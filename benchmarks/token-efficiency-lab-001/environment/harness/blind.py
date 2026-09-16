"""Blind evaluation.

The Quality Judge scores before seeing cost, and never sees which treatment produced an
output. This is not a courtesy — the conflict of interest is declared in the frozen
methodology: two candidates are simultaneously Lab subjects and ATK integration candidates, and
a judge who can see which is which is not a judge.

Enforcement is machine-checked, not procedural. `assert_blind` walks the packet recursively and
fails if any forbidden key or any candidate name appears anywhere in it, at any depth, in a key
or in a value. A protocol that relies on the judge not looking is not a protocol.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import string
from dataclasses import dataclass

# Anything in this list identifies the treatment, its cost, or how much ATK wants it to win.
FORBIDDEN_KEYS = frozenset(
    {
        "condition",
        "treatment",
        "treatment_name",
        "candidate",
        "candidate_name",
        "candidate_commit_sha",
        "cost",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "cached_tokens",
        "tool_schema_tokens",
        "tool_result_tokens",
        "token_source",
        "pricing_snapshot_id",
        "model",
        "model_pair",
        "model_version",
        "provider",
        "stars",
        "popularity",
        "repository",
        "repo",
        "atk_integration_interest",
        "integration_interest",
        "retries",
        "escalations",
        "latency_ms",
    }
)

LABELS = list(string.ascii_uppercase)


class BlindError(RuntimeError):
    pass


@dataclass(frozen=True)
class JudgePacket:
    """Everything the Quality Judge is allowed to see, and nothing else."""

    packet_id: str
    task_id: str
    workload: str
    blind_treatment_id: str
    model_output: str
    required_evidence: list
    answer_key: dict
    quality_metric: str
    failure_condition: str

    def to_dict(self) -> dict:
        return {
            "packet_id": self.packet_id,
            "task_id": self.task_id,
            "workload": self.workload,
            "blind_treatment_id": self.blind_treatment_id,
            "model_output": self.model_output,
            "required_evidence": self.required_evidence,
            "answer_key": self.answer_key,
            "quality_metric": self.quality_metric,
            "failure_condition": self.failure_condition,
        }


class BlindMapping:
    """Held by the Benchmark Runner. Never shipped to the Quality Judge.

    Labels are assigned by sorting on HMAC-style digests of (salt, condition), so the label
    order carries no information about the condition order. Without the salt, "Treatment A" is
    not guessable; with it, un-blinding is exact and repeatable.
    """

    def __init__(self, salt: str) -> None:
        if not salt or len(salt) < 16:
            raise BlindError("blind salt must be at least 16 characters")
        self._salt = salt
        self._label_of: dict[str, str] = {}

    @staticmethod
    def _digest(salt: str, condition: str) -> str:
        return hashlib.sha256(f"{salt}|{condition}".encode()).hexdigest()

    def assign(self, conditions: list[str]) -> dict[str, str]:
        unique = sorted(set(conditions))
        if len(unique) > len(LABELS):
            raise BlindError(f"cannot blind {len(unique)} conditions with {len(LABELS)} labels")
        ordered = sorted(unique, key=lambda c: self._digest(self._salt, c))
        self._label_of = {c: f"Treatment {LABELS[i]}" for i, c in enumerate(ordered)}
        return dict(self._label_of)

    def label(self, condition: str) -> str:
        if condition not in self._label_of:
            raise BlindError(f"condition {condition!r} was never assigned a blind label")
        return self._label_of[condition]

    def unblind(self, scored_packets: list[dict], scoring_complete: bool) -> dict[str, str]:
        """Reverse the mapping. Refuses while scoring is still open."""
        if not scoring_complete:
            raise BlindError(
                "refusing to un-blind: the Quality Judge has not finished scoring. "
                "Un-blinding early destroys the only property this protocol provides."
            )
        unscored = [p.get("packet_id") for p in scored_packets if p.get("quality_score") is None]
        if unscored:
            raise BlindError(
                f"refusing to un-blind: {len(unscored)} packet(s) are still unscored: "
                + ", ".join(str(u) for u in unscored[:5])
            )
        return {label: cond for cond, label in self._label_of.items()}

    def save(self, path: pathlib.Path) -> None:
        pathlib.Path(path).write_text(
            json.dumps(
                {
                    "note": "RUNNER ONLY. Must never be placed on the Quality Judge's path.",
                    "salt_sha256": hashlib.sha256(self._salt.encode()).hexdigest(),
                    "label_of_condition": self._label_of,
                },
                indent=2,
            )
            + "\n"
        )


def _walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield path + "/" + str(k), k, v
            yield from _walk(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")


def assert_blind(packet: dict, candidate_names: list[str]) -> None:
    """Fail loudly if anything identifying leaked into a judge packet.

    Checks keys at every depth, and scans every string value for candidate names. Called on
    every packet before it is written to the judge's path.
    """
    for full_path, key, _value in _walk(packet):
        if key in FORBIDDEN_KEYS:
            raise BlindError(
                f"blind violation: forbidden key {key!r} present at {full_path}. "
                "The Quality Judge may not see treatment identity or cost."
            )
    blob = json.dumps(packet).lower()
    for name in candidate_names:
        needle = name.lower()
        if needle and needle in blob:
            raise BlindError(
                f"blind violation: candidate name {name!r} appears in the packet body. "
                "Scrub it from the model output before the packet reaches the judge."
            )


def build_packet(
    run_record: dict,
    model_output: str,
    task: dict,
    answer_key: dict,
    mapping: BlindMapping,
    candidate_names: list[str],
) -> JudgePacket:
    label = mapping.label(run_record["condition"])
    packet = JudgePacket(
        packet_id=hashlib.sha256(
            f"{run_record['run_id']}|{run_record['task_id']}".encode()
        ).hexdigest()[:16],
        task_id=run_record["task_id"],
        workload=run_record["workload"],
        blind_treatment_id=label,
        model_output=model_output,
        required_evidence=task.get("required_evidence", []),
        answer_key=answer_key,
        quality_metric=task["quality_metric"],
        failure_condition=task["failure_condition"],
    )
    assert_blind(packet.to_dict(), candidate_names)
    return packet

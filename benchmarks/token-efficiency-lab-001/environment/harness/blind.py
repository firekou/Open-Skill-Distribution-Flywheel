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

from . import METHODOLOGY_VERSION
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
        # Added for NEW-06. These reached the judge through `required_evidence`, which the walk
        # used to skip. There is now ONE list and both gates read it.
        "treatment_name",
        "candidate_commit_sha",
        "model_version",
        "cache_state",
        "run_id",
        "container_digest",
        "egress_destinations",
        "image_content_sha256",
        "pricing_snapshot_id",
    }
)

LABELS = list(string.ascii_uppercase)

# Every condition the frozen 100-run allocation can produce (methodology v1.0.0 section 5),
# plus the two guardrail run kinds. Labels are assigned over THIS list, never over whatever
# happens to be in the batch at hand - see BlindMapping.assign.
CANONICAL_CONDITIONS = (
    "C0", "C1", "C2", "C3", "C4", "C5", "C2+C4", "C3+C4", "CALIB", "CACHE",
)


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
    required_evidence: dict | list
    answer_key: dict
    quality_metric: str
    failure_condition: str
    methodology_version: str = METHODOLOGY_VERSION

    def to_dict(self) -> dict:
        return {
            "methodology_version": self.methodology_version,
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
        """Assign labels over the CANONICAL condition set, not over this batch.

        Labelling only the conditions present in a batch makes a label batch-scoped: the
        Reproduction Agent measured `C0 = Treatment B` in the full 10-run plan and
        `C0 = Treatment A` in a 2-run subset **with the same salt**. A partial reproduction —
        which is the whole point of the Reproduction seat, since it repeats the strongest
        results rather than everything — would then disagree on `blind_treatment_id` while
        being entirely correct, and the disagreement would look like an invalidation.

        Labelling the canonical set makes a label a property of (salt, condition) alone, exactly
        as BLIND_EVALUATION_PROTOCOL.md says it is. Unused labels simply never appear.
        """
        unknown = sorted(set(conditions) - set(CANONICAL_CONDITIONS))
        if unknown:
            raise BlindError(
                f"condition(s) {unknown} are not in the canonical set. The 100-run allocation is "
                "frozen (methodology v1.0.0 section 5); a new condition is a methodology change, "
                "not a runner argument."
            )
        if len(CANONICAL_CONDITIONS) > len(LABELS):
            raise BlindError(
                f"cannot blind {len(CANONICAL_CONDITIONS)} conditions with {len(LABELS)} labels"
            )
        ordered = sorted(CANONICAL_CONDITIONS, key=lambda c: self._digest(self._salt, c))
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


# Fields that are FROZEN TASK-SET CONTENT: authored before any run, by seats that never saw
# candidate identity, and hashed into the task set. The judge is supposed to read them in full.
#
# The forbidden-KEY scan is skipped inside these subtrees. The reason is empirical: the first
# run of this checker against the real task set failed a packet because answer key D-002 mirrors
# an offline tool's argument schema, one of whose arguments is named `repository`. That is a
# synthetic repo name in a fixture, not a candidate identity, and failing on it adds no safety
# while blocking a legitimate packet (EVIDENCE_LEDGER E027).
#
# The candidate-NAME scan still covers the whole packet, including these subtrees. A name is the
# real leak vector; a key called `repo` in a frozen fixture is not.
# NOTE: `required_evidence` is NOT here, and that is the fix for NEW-06.
#
# It was listed as "frozen task-set content", but it is the one packet field that is
# **run-produced** — so it is precisely where run metadata would leak. With it excluded from the
# walk, `required_evidence.treatment_name`, `.candidate_commit_sha`, `.model_version` and
# `.cache_state` all passed both blind gates. A blind guarantee whose own assertion skips the
# field most likely to break it is the RT-02 shape: a check that can be off without anyone
# noticing.
FROZEN_CONTENT_FIELDS = frozenset(
    {"answer_key", "quality_metric", "failure_condition"}
)


def assert_blind(packet: dict, candidate_names: list[str]) -> None:
    """Fail loudly if anything identifying leaked into a judge packet.

    Checks keys at every depth outside the frozen task-set content, and scans every string value
    in the WHOLE packet for candidate names. Called on every packet before it is written to the
    judge's path.
    """
    for field in FROZEN_CONTENT_FIELDS & set(packet):
        if field in FORBIDDEN_KEYS:
            raise BlindError(
                f"{field!r} is both frozen content and a forbidden key; the two lists disagree"
            )
    scannable = {k: v for k, v in packet.items() if k not in FROZEN_CONTENT_FIELDS}
    for full_path, key, _value in _walk(scannable):
        if key in FORBIDDEN_KEYS:
            raise BlindError(
                f"blind violation: forbidden key {key!r} present at {full_path}. "
                "The Quality Judge may not see treatment identity or cost."
            )
    for key in packet:
        if key in FORBIDDEN_KEYS:
            raise BlindError(
                f"blind violation: forbidden key {key!r} present at the packet top level. "
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


def assert_evidence_sufficient(task: dict, required_evidence) -> None:
    """RT-01 / RT-13 — refuse the packet BEFORE it reaches the judge.

    v1.0.0 read `task.get("required_evidence", [])`, no task file carried that key, and every
    packet shipped an empty list. Ten of seventeen byte-perfect answers failed at score 0.0 and
    the cause was invisible from the score. Worse, an empty container passes a type check, so an
    empty `shifts`/`roster` silently disarmed workload E's zero-tolerance criteria and let an
    ineligible assignment score `task_success: true` (RT-02).

    So the check is on CONTENT, at packet-build time, and it raises. A judge that receives a
    packet has evidence; a judge that would have received an empty one gets nothing at all.
    """
    from .evidence import EvidenceError, required_fields, validate

    if not isinstance(required_evidence, dict):
        raise BlindError(
            f"required_evidence must be a mapping produced by harness.evidence, got "
            f"{type(required_evidence).__name__}. An empty list is how v1.0.0 shipped 17 "
            "unscoreable packets."
        )
    try:
        validate(required_evidence, task)
    except EvidenceError as exc:
        raise BlindError(str(exc)) from exc

    if task["workload"] == "E":
        turns = required_evidence.get("turns") or []
        expected = task["input"].get("turn_count") or task.get("turn_count")
        if expected and len(turns) != int(expected):
            raise BlindError(
                f"workload E packet carries {len(turns)} turns but the task declares {expected}. "
                "A truncated transcript hides every violation after the cut."
            )
    del required_fields


def build_packet(
    run_record: dict,
    model_output: str,
    task: dict,
    answer_key: dict,
    mapping: BlindMapping,
    candidate_names: list[str],
    required_evidence: dict | None = None,
    methodology_version: str | None = None,
) -> JudgePacket:
    label = mapping.label(run_record["condition"])
    evidence = required_evidence if required_evidence is not None else task.get("required_evidence")
    assert_evidence_sufficient(task, evidence)
    packet = JudgePacket(
        packet_id=hashlib.sha256(
            f"{run_record['run_id']}|{run_record['task_id']}".encode()
        ).hexdigest()[:16],
        task_id=run_record["task_id"],
        workload=run_record["workload"],
        blind_treatment_id=label,
        model_output=model_output,
        required_evidence=evidence,
        answer_key=answer_key,
        quality_metric=task["quality_metric"],
        failure_condition=task["failure_condition"],
        # v1.1.0 section 13: the scorer refuses a packet whose version it cannot resolve rather
        # than scoring it under a guess. Silent cross-version scoring is how a v1.0.0 relative
        # floor would survive into a v1.1.0 result.
        methodology_version=(methodology_version
                             or run_record.get("methodology_version")
                             or task.get("methodology_version")
                             or METHODOLOGY_VERSION),
    )
    assert_blind(packet.to_dict(), candidate_names)
    return packet

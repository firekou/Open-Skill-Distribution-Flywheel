"""Run harness.

Executes one task under one condition, accumulates provider-reported usage, writes a schema-valid
run record, preserves raw evidence, and emits a blind judge packet.

The harness never scores. It builds the packet and hands it over. The Quality Judge scores from
the packet alone and returns a number, and only then does anything un-blind. Keeping the scorer
out of this file is the enforcement: code that cannot see a score cannot be tempted to weight it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

from .attest import dependency_manifest_hash, image_content_hash
from .blind import BlindMapping, build_packet
from .meter import TokenMeter
from .pricing import PricingSnapshot
from .providers import ReplayProvider
from .record import sha256_text, write_raw_evidence, write_record

CANDIDATE_NAMES = [
    "tokentab", "headroom", "rtk", "paritok", "lean-ctx", "leanctx",
    "entroly", "api-relay-audit", "NadirClaw", "nadir",
]


class RunError(RuntimeError):
    pass


def load_task(task_root: pathlib.Path, task_id: str) -> dict:
    workload = task_id.split("-")[0]
    path = pathlib.Path(task_root) / "tasks" / workload / f"{task_id}.json"
    if not path.exists():
        raise RunError(f"task {task_id} not found at {path}")
    return json.loads(path.read_text())


def load_answer_key(task_root: pathlib.Path, task: dict) -> dict:
    ref = task.get("answer_key_reference")
    if not ref:
        raise RunError(f"task {task['task_id']} carries no answer_key_reference")
    path = pathlib.Path(task_root) / ref
    if not path.exists():
        raise RunError(
            f"answer key {ref} does not exist. A task cannot be scored against a key that was "
            "never built; the run is recorded as a failure, not scored optimistically."
        )
    return json.loads(path.read_text())


def hash_tree(root: pathlib.Path, patterns=("*.json", "*.md", "*.py", "*.txt", "*.csv")) -> str:
    """Stable hash over a directory tree: relative path plus content, sorted."""
    root = pathlib.Path(root)
    h = hashlib.sha256()
    files = sorted(
        (p for pat in patterns for p in root.rglob(pat) if p.is_file()),
        key=lambda p: str(p.relative_to(root)),
    )
    for p in files:
        h.update(str(p.relative_to(root)).encode())
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def run_one(
    *,
    task_id: str,
    condition: str,
    repetition: int,
    task_root: pathlib.Path,
    fixture: pathlib.Path,
    snapshot: PricingSnapshot,
    evidence_root: pathlib.Path,
    mapping: BlindMapping,
    run_class: str,
    environment_id: str,
    container_digest: str | None,
    task_set_hash: str,
    answer_key_hash: str,
    run_id: str | None = None,
    reproduces_run_id: str | None = None,
) -> tuple[dict, dict]:
    if run_class not in ("benchmark", "pilot", "calibration", "reproduction", "dry_run"):
        raise RunError(f"unknown run_class {run_class!r}")

    task = load_task(task_root, task_id)
    answer_key = load_answer_key(task_root, task)
    provider = ReplayProvider(fixture)

    if provider.synthetic and run_class in ("benchmark", "pilot"):
        raise RunError(
            f"refusing to record a {run_class} run from a synthetic replay fixture. There is no "
            "model in the loop, so the result would describe the harness, not the intervention."
        )

    meter = TokenMeter(snapshot)
    started = time.time()
    raw_calls, outputs = [], []
    for usage, raw in provider.run_task(task_id):
        meter.record(usage)
        raw_calls.append(raw)
        if raw.get("output_text"):
            outputs.append(raw["output_text"])
    elapsed_ms = int((time.time() - started) * 1000)

    totals = meter.totals()
    warning = meter.cross_provider_guard()
    model_output = "\n".join(outputs)

    rid = run_id or f"{run_class}-{task_id}-{condition}-r{repetition}"
    evidence_path = write_raw_evidence(
        rid,
        {
            "run_id": rid,
            "task_id": task_id,
            "condition": condition,
            "run_class": run_class,
            "fixture_sha256": hashlib.sha256(pathlib.Path(fixture).read_bytes()).hexdigest(),
            "calls": raw_calls,
            "model_output": model_output,
            "cross_provider_warning": warning,
            # NOTE: no timestamp here, deliberately. `written_at` lives in MANIFEST.json, which
            # is not itself hashed. Putting it inside raw.json and then hashing raw.json made the
            # evidence hash differ on every run by construction, so the manifest could detect
            # tampering within a run but could never answer "is this the same evidence as the
            # original" - which is the one question a reproduction needs it to answer.
            # Found by the Reproduction Agent (WOULD-INVALIDATE 6).
        },
        evidence_root,
    )

    record = {
        "run_id": rid,
        "task_id": task_id,
        "condition": condition,
        "workload": task["workload"],
        "repetition": repetition,
        "run_class": run_class,
        "model": ",".join(totals.models),
        "provider": ",".join(totals.providers),
        "model_version": raw_calls[0]["model_version"],
        "model_calls": totals.model_calls,
        "tool_calls": sum(int(c.get("tool_calls", 0)) for c in raw_calls),
        "input_tokens": totals.input_tokens,
        "output_tokens": totals.output_tokens,
        "total_tokens": totals.total_tokens,
        "token_source": "provider_usage_field",
        "cost": round(totals.cost, 10),
        "pricing_snapshot_id": snapshot.snapshot_id,
        "latency_ms": elapsed_ms,
        "retries": totals.retries,
        "escalations": totals.escalations,
        "cache_state": totals.cache_state,
        # Filled in after the Quality Judge returns. Never guessed here.
        "task_success": False,
        "quality_score": 0.0,
        "quality_judged_before_cost": True,
        "environment_id": environment_id,
        # Operator-supplied. Recorded because a verifier needs it to pull the image, but it is
        # an assertion, not a measurement - see harness/attest.py.
        "container_digest": container_digest,
        # Self-derived inside the running container. A flag cannot forge these.
        "image_content_sha256": image_content_hash(),
        "dependency_manifest_sha256": dependency_manifest_hash(),
        "prompt_hash": sha256_text(json.dumps(task["input"], sort_keys=True)),
        "config_hash": sha256_text(f"{condition}|{snapshot.snapshot_id}|{task_set_hash}"),
        "task_version": "1.0.0",
        "task_set_hash": task_set_hash,
        "answer_key_hash": answer_key_hash,
        "blind_treatment_id": mapping.label(condition),
        "reproduces_run_id": reproduces_run_id,
        "raw_evidence_path": evidence_path,
        "methodology_version": "1.0.0",
        "notes": warning,
    }
    if condition.startswith("C4"):
        record["model_pair"] = " -> ".join(totals.models)

    packet = build_packet(record, model_output, task, answer_key, mapping, CANDIDATE_NAMES)
    return record, packet.to_dict()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lab 001 run harness")
    ap.add_argument("--task-root", required=True)
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--run-class", default="dry_run")
    ap.add_argument("--plan", required=True, help="JSON list of {task_id, condition, repetition}")
    ap.add_argument("--environment-id", default="lab001-env-2026-09-16")
    ap.add_argument("--container-digest", default=None)
    ap.add_argument("--blind-salt", required=True)
    args = ap.parse_args(argv)

    task_root = pathlib.Path(args.task_root)
    out = pathlib.Path(args.out)
    snapshot = PricingSnapshot(pathlib.Path(args.snapshot))
    plan = json.loads(pathlib.Path(args.plan).read_text())

    mapping = BlindMapping(args.blind_salt)
    mapping.assign([p["condition"] for p in plan])
    (out / "runner_only").mkdir(parents=True, exist_ok=True)
    mapping.save(out / "runner_only" / "BLIND_MAPPING.json")

    task_set_hash = hash_tree(task_root / "tasks")
    answer_key_hash = hash_tree(task_root / "answer_keys")

    records, packets, failures = [], [], []
    for item in plan:
        try:
            rec, pkt = run_one(
                task_id=item["task_id"],
                condition=item["condition"],
                repetition=item.get("repetition", 1),
                task_root=task_root,
                fixture=pathlib.Path(args.fixture),
                snapshot=snapshot,
                evidence_root=out / "raw",
                mapping=mapping,
                run_class=args.run_class,
                environment_id=args.environment_id,
                container_digest=args.container_digest,
                task_set_hash=task_set_hash,
                answer_key_hash=answer_key_hash,
            )
            write_record(rec, out / "records")
            records.append(rec)
            packets.append(pkt)
        except Exception as exc:  # noqa: BLE001
            # A failed run is RECORDED, not dropped. A harness that silently skips what it
            # cannot do reports a success rate it did not earn.
            failures.append(
                {"task_id": item["task_id"], "condition": item["condition"],
                 "error": f"{type(exc).__name__}: {exc}"}
            )

    (out / "judge_packets").mkdir(parents=True, exist_ok=True)
    for pkt in packets:
        (out / "judge_packets" / f"{pkt['packet_id']}.json").write_text(
            json.dumps(pkt, indent=2, ensure_ascii=False) + "\n"
        )

    summary = {
        "run_class": args.run_class,
        "planned": len(plan),
        "completed": len(records),
        "failed": len(failures),
        "failures": failures,
        "task_set_hash": task_set_hash,
        "answer_key_hash": answer_key_hash,
        "pricing_snapshot_id": snapshot.snapshot_id,
        "container_digest": args.container_digest,
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }
    (out / "RUN_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

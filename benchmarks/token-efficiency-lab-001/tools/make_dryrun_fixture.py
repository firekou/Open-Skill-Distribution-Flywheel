#!/usr/bin/env python3
"""Generate a deterministic replay fixture for a harness DRY RUN.

This is NOT a benchmark, a pilot, or a model. It produces provider-shaped `usage` blocks from a
seeded PRNG so that the run harness can be exercised end to end with no network, no credential
and no cost. Its only purpose is to answer "does the plumbing work".

Everything it emits is marked `synthetic: true`, and `harness/runner.py` refuses to write a
`benchmark` or `pilot` record from a synthetic fixture. The safety is in the code path, not in
this docstring.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random

# One cheap and one mid-tier model from the pricing snapshot, so escalation and cross-provider
# handling are both exercised. These names must exist in the snapshot or pricing fails loudly.
CHEAP = ("openai", "gpt-5-mini")
MID = ("openai", "gpt-5")


def seeded(task_id: str, condition: str, salt: str) -> random.Random:
    """Deterministic per (task, condition). The same inputs always give the same fixture."""
    h = hashlib.sha256(f"{salt}|{task_id}|{condition}".encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def make_calls(task: dict, condition: str, salt: str) -> list[dict]:
    rng = seeded(task["task_id"], condition, salt)
    workload = task["workload"]

    # Rough shapes per workload, so the dry run exercises different call patterns. These are
    # invented. They are not predictions about how any real workload behaves.
    base_input = {"A": 24000, "B": 48000, "C": 18000, "D": 14000, "E": 11000}[workload]
    turns = {"A": 3, "B": 1, "C": 4, "D": 2, "E": 6}[workload]

    provider, model = CHEAP
    calls = []
    for turn in range(turns):
        # C3 compaction shrinks later turns; C2 filtering shrinks tool results. Modelled crudely
        # ONLY so different conditions produce different plumbing paths, never as a claim.
        factor = 1.0
        if condition in ("C2", "C2+C4") and turn > 0:
            factor *= 0.7
        if condition in ("C3", "C3+C4") and turn > 1:
            factor *= 0.5
        inp = int(base_input * factor * rng.uniform(0.95, 1.05)) + turn * 900
        out = int(rng.uniform(300, 1200))
        cached = int(inp * 0.4) if turn > 0 else 0
        calls.append(
            {
                "task_id": task["task_id"],
                "provider": provider,
                "model": model,
                "model_version": f"{model}-2026-09",
                "accepted": True,
                "role": "primary",
                "cache_state": "warm" if turn > 0 else "cold",
                "latency_ms": int(rng.uniform(400, 2500)),
                "tool_calls": rng.randint(0, 4) if workload in ("A", "C", "D") else 0,
                "usage": {"input_tokens": inp, "output_tokens": out, "cached_tokens": cached},
                "output_text": (
                    f"[SYNTHETIC DRY-RUN OUTPUT] task={task['task_id']} turn={turn}. "
                    "No model produced this text. It exists so the harness has something to "
                    "carry through to a judge packet."
                ),
            }
        )

    # Every call in a run must share a cache state or the run is void by methodology section 9.
    state = calls[0]["cache_state"]
    for c in calls:
        c["cache_state"] = state

    # C4 routes to the mid tier on the last call, exercising escalation attribution.
    if condition.startswith("C4") or condition.endswith("C4"):
        p, m = MID
        calls[-1].update({"provider": p, "model": m, "model_version": f"{m}-2026-09",
                          "role": "escalation"})
    return calls


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-root", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--salt", default="lab001-dryrun-2026-09-16")
    args = ap.parse_args()

    task_root = pathlib.Path(args.task_root)
    plan = json.loads(pathlib.Path(args.plan).read_text())

    calls = []
    for item in plan:
        wl = item["task_id"].split("-")[0]
        task = json.loads((task_root / "tasks" / wl / f"{item['task_id']}.json").read_text())
        calls.extend(make_calls(task, item["condition"], args.salt))

    fixture = {
        "fixture_version": "1.0.0",
        "synthetic": True,
        "salt": args.salt,
        "purpose": "harness dry run - plumbing verification only",
        "hard_caveat": (
            "NO MODEL PRODUCED ANY OF THIS. Every usage block is generated from a seeded PRNG. "
            "Nothing derived from this fixture is a benchmark result, a pilot result, or "
            "evidence for or against any hypothesis. runner.py refuses to write a benchmark or "
            "pilot record from it."
        ),
        "calls": calls,
    }
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(calls)} calls across {len(plan)} planned runs -> {out}")
    print("sha256:", hashlib.sha256(out.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

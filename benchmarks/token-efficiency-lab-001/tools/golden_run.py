#!/usr/bin/env python3
"""Golden end-to-end run — all 17 tasks, a legitimate answer, the whole chain.

The Answer Key Builder already checks that an ideal answer scores 1.0 when handed straight to
`judge.score_packet`. That is necessary and it is not sufficient: it skips the runner, the
Evidence Producer, the packet builder, the blind check, finalize and the aggregator — which is
exactly where RT-01, RT-02, RT-08 and RT-13 lived. Feeding a key back to a scorer and calling the
chain verified is the specific claim this file exists to stop anyone making.

So: build a legitimate answer from each key, push it through the **real** pipeline with real
corpus-derived evidence, a real tool audit and complete turns, and require **17 of 17 PASS**.
A single FAIL_QUALITY or INVALID here means a correct answer cannot get through the machinery,
which is a harness defect whatever the scorer says in isolation.
"""
from __future__ import annotations

import argparse
import json
import pathlib

# Provenance, not answer. Everything else in a key is what a correct reply contains.
KEY_META = {"task_id", "derived_by", "derivation_method", "derivation_script",
            "derivation_diagnostics", "notes", "contested_families", "required_tools",
            "tool_calls_made_by_this_derivation", "citation_support"}


def ideal_answer(key: dict) -> dict:
    """The reply a perfect run would emit, reconstructed from the key.

    Two keys store their payload in a different shape from the reply, both for good reasons, and
    both have to be unwrapped here rather than papered over:

    * **workload D** nests the answer under `answer`, beside the contested families and the tool
      calls its derivation made - none of which a reply contains.
    * **B-001** nests its 36 contract terms under `contract_terms` beside four provenance fields
      (this is UG-32), while the reply is a flat object of exactly those 36 keys. The first run
      of this file scored B-001 `more_than_one_required_key_missing` for precisely that reason,
      which is the check doing its job.
    """
    if "answer" in key and isinstance(key["answer"], dict):
        return key["answer"]
    payload = {k: v for k, v in key.items() if k not in KEY_META}
    if set(payload) - {"as_of_date"} == {"contract_terms"}:
        return dict(payload["contract_terms"])
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--condition", default="C0")
    ap.add_argument("--run-class", default="dry_run")
    args = ap.parse_args()

    root = pathlib.Path(args.task_root)
    out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)

    plan, calls, audit, seq = [], [], [], 0
    for wl in "ABCDE":
        for tp in sorted((root / "tasks" / wl).glob("*.json")):
            task = json.loads(tp.read_text())
            tid = task["task_id"]
            key = json.loads((root / task["answer_key_reference"]).read_text())
            answer = json.dumps(ideal_answer(key), ensure_ascii=False)
            # Must match harness.runner's own id: f"{run_class}-{task_id}-{condition}-r{rep}".
            # The Evidence Producer filters the audit by run id and refuses a run with no
            # entries of its own, so a prefix mismatch here fails every A and D attempt - which
            # is what it did on the first try, correctly.
            rid = f"{args.run_class}-{tid}-{args.condition}-r1"
            plan.append({"task_id": tid, "condition": args.condition, "repetition": 1})

            turns = int(task["input"].get("turn_count") or 1) if wl == "E" else 1
            for n in range(turns):
                last = n == turns - 1
                calls.append({
                    "task_id": tid, "provider": "lab", "model": "replay-synthetic",
                    "model_version": "golden", "accepted": True, "role": "primary",
                    "cache_state": "cold", "latency_ms": 1, "tool_calls": 0,
                    "turn": n + 1,
                    "usage": {"input_tokens": 1000, "output_tokens": 100, "cached_tokens": 0},
                    # Only the final turn carries the answer; the earlier ones are the
                    # transcript workload E's violation classes are scored over.
                    "output_text": answer if last else f"[golden turn {n+1}] acknowledged.",
                })

            if wl in ("A", "D"):
                for cp in (task["input"].get("corpus_paths") or ["corpora/"])[:2]:
                    seq += 1
                    audit.append({"seq": seq, "run_id": rid, "mode": "read", "tool": "fs.read",
                                  "family": "corpus", "arguments": {"path": cp}})
                for t in (key.get("required_tools") or [])[:4]:
                    seq += 1
                    audit.append({"seq": seq, "run_id": rid, "mode": "call", "tool": t,
                                  "family": "required", "arguments": {}})
                if not key.get("required_tools"):
                    seq += 1
                    audit.append({"seq": seq, "run_id": rid, "mode": "call",
                                  "tool": "catalog.list_tools", "family": "meta", "arguments": {}})

    (out / "PLAN.json").write_text(json.dumps(plan, indent=2) + "\n")
    (out / "FIXTURE.json").write_text(json.dumps({
        "fixture_version": "golden-1.1.0", "synthetic": True,
        "purpose": "a legitimate answer for every task, pushed through the real pipeline",
        "hard_caveat": ("The answers are reconstructed from the frozen answer keys. This measures "
                        "the MACHINERY - whether a correct answer can get through it - and says "
                        "nothing about any model, any intervention, or any hypothesis."),
        "calls": calls,
    }, ensure_ascii=False, indent=2) + "\n")
    (out / "TOOL_AUDIT.jsonl").write_text(
        "\n".join(json.dumps(a, sort_keys=True) for a in audit) + "\n")

    from collections import Counter
    cells = Counter((p["task_id"][0], p["condition"]) for p in plan)
    (out / "CELL_PLAN.json").write_text(json.dumps(
        [{"workload": w, "condition": c, "planned_attempts": n}
         for (w, c), n in sorted(cells.items())], indent=2) + "\n")

    print(f"{len(plan)} tasks, {len(calls)} calls, {len(audit)} audit entries -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
import sys

sys.path.insert(
    0, str(pathlib.Path(__file__).resolve().parent.parent / "environment"))

from harness import corpus_reader as cr  # noqa: E402

# Provenance, not answer. Everything else in a key is what a correct reply contains.
def _first_file(root: pathlib.Path, corpus_path: str) -> str:
    """One concrete file under a declared corpus path, so the reader has something to open."""
    target = root / corpus_path
    if target.is_file():
        return corpus_path
    for p in sorted(target.rglob("*")):
        if p.is_file():
            return str(p.relative_to(root).as_posix())
    raise SystemExit(f"{corpus_path} contains no file to read")


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

    audit_file = out / "TOOL_AUDIT.jsonl"
    audit_file.write_text("")          # the reader appends; start from empty
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
            # R3-01: the dry-run plan carried no attempt_id, so the records it produced could
            # not be identity-checked and the documented aggregate step reported the cell
            # unverified. The synthetic fixture gets its OWN plan and its own ids - the
            # production run plan's 270 attempts are not a denominator for a 17-task dry run.
            plan.append({"task_id": tid, "condition": args.condition, "repetition": 1,
                         "attempt_id": f"{tid}-{args.condition}-r1"})

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
                # NEW-03: these entries used to be FABRICATED here - `{"tool": "fs.read"}` with
                # no reader behind it - so the lab's own proof harness forged the evidence it was
                # meant to check, and the fact that nothing in the lab could produce a workload-A
                # corpus read stayed invisible. They now come from the real audited reader
                # (`harness/corpus_reader.py`), which reads the file and writes the entry in the
                # same call, so an entry cannot exist for a file that was not read.
                for cp in (task["input"].get("corpus_paths") or ["corpora/"])[:2]:
                    cr.read(_first_file(root, cp), task_root=root,
                            allowed=task["input"].get("corpus_paths"),
                            run_id=rid, audit_path=audit_file)
                # Tool calls still come from the tool server's own format. They are marked
                # synthetic so nothing mistakes them for a real invocation.
                for t in (key.get("required_tools") or ["catalog.list_tools"])[:4]:
                    audit.append({"run_id": rid, "mode": "call", "tool": t,
                                  "family": "required", "arguments": {}, "synthetic": True})

    (out / "PLAN.json").write_text(json.dumps(plan, indent=2) + "\n")
    (out / "FIXTURE.json").write_text(json.dumps({
        "fixture_version": "golden-1.1.0", "synthetic": True,
        "purpose": "a legitimate answer for every task, pushed through the real pipeline",
        "hard_caveat": ("The answers are reconstructed from the frozen answer keys. This measures "
                        "the MACHINERY - whether a correct answer can get through it - and says "
                        "nothing about any model, any intervention, or any hypothesis."),
        "calls": calls,
    }, ensure_ascii=False, indent=2) + "\n")
    # Append the tool-call entries after the reader's, renumbering `seq` continuously.
    existing = [l for l in audit_file.read_text().splitlines() if l.strip()]
    lines = list(existing)
    for i, a in enumerate(audit, start=len(existing) + 1):
        lines.append(json.dumps(dict(a, seq=i), sort_keys=True))
    audit_file.write_text("\n".join(lines) + "\n")

    from collections import Counter
    cells = Counter((p["task_id"][0], p["condition"]) for p in plan)
    cell_list = [{"workload": w, "condition": c, "planned_attempts": n}
                 for (w, c), n in sorted(cells.items())]
    (out / "CELL_PLAN.json").write_text(json.dumps(cell_list, indent=2) + "\n")

    # A run plan for THIS fixture, in the shape `harness.aggregate --run-plan` reads: it carries
    # the denominators and the planned attempt identities from one source, which is the whole
    # point of R2-01. One run per (workload, condition) here, because the dry run does one
    # repetition of every task.
    runs = {}
    for item in plan:
        wl = item["task_id"][0]
        rid = f"{wl}-{item['condition']}-r{item['repetition']}"
        runs.setdefault(rid, {"run_id": rid, "workload": wl, "condition": item["condition"],
                              "repetition": item["repetition"], "task_attempts": []})
        runs[rid]["task_attempts"].append(
            {"task_id": item["task_id"], "attempt_id": item["attempt_id"],
             "session": "independent"})
    (out / "RUN_PLAN.json").write_text(json.dumps({
        "run_plan_version": "dry-run fixture, not the frozen v1.1.0 plan",
        "methodology_version": "1.1.0",
        "status": "SYNTHETIC - for the documented dry run only",
        "note": ("This is the 17-task golden fixture's own plan. It must never be confused with "
                 "RUN_PLAN_v1.1.0.json, whose 270 attempts are the real experiment's "
                 "denominators."),
        "cells": cell_list,
        "runs": [runs[k] for k in sorted(runs)],
    }, indent=2) + "\n")

    print(f"{len(plan)} tasks, {len(calls)} calls, {len(audit)} audit entries -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

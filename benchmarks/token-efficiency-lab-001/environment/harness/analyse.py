"""Descriptive analysis entry point — R4-01 / R4-07.

R4-01 found that `cost_per_successful_task` (quantity 9, the headline metric), `select_strongest`
(§7.7) and `pair_attempts` (§7.1/§7.3) were reachable from **no command at all**. Only tests
called them, so every repair made to them across rounds 1–3 was unreachable in practice — the
same defect as R3-01, one layer up.

The first response to that was to leave the whole analysis layer unbuilt because the methodology
is unratified. The fourth review judged that half right, and it was: **CR-002 decides how many
attempts to run, not whether reading records, checking cost completeness and reporting pairing
diagnostics may exist.**

So this module computes everything that does not need a ruling, and **refuses, loudly and by
name, everything that does**:

| Computed here | Refused here |
|---|---|
| per-cell PASS / FAIL_QUALITY / INVALID / missing counts | deltas versus baseline |
| total cost, and whether cost is complete | rankings, "strongest" selection |
| cost per successful task, when every attempt is priced | non-inferiority conclusions |
| paired / unpaired attempt lists, with the reason for each | any "saving" or "quality was not sacrificed" claim |

The refusals are **not** a silent omission: every blocked output appears in `decisions_required`
with the decision it waits on. A reader who wants a delta finds out why there isn't one.

**Nothing here licenses a result.** It describes records that already exist.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib

from .aggregate import (INVALID, PASS, FAIL_QUALITY, AggregateError, PlannedAttempts,
                        build_cells, load_attempts, pair_attempts)

# Every conclusion this module will not draw, and the decision each waits on. A blocked output is
# named here rather than omitted, because an absent number reads as "not interesting" and a named
# refusal reads as "nobody has ruled on this yet".
BLOCKED_OUTPUTS = {
    "cost_delta_vs_baseline": (
        "CR-002 has not been ratified, so the run plan this would summarise is not the agreed "
        "design. A delta computed over a design nobody approved is a number about nothing."),
    "condition_ranking": (
        "§7.7 selection ranks by delta; see above. §7.6 (the INVALID re-run rule) is also "
        "unratified, and it decides which attempts are even in the denominator."),
    "strongest_conditions": (
        "§7.7. Same dependency, and the ranking would drive which cells get reproduced."),
    "non_inferiority": (
        "no margin has been set. A margin is a business judgement and cannot be inferred from "
        "the data it is meant to judge."),
    "savings_claim": (
        "requires all of the above, plus a ratified pricing lineup. Three pricing rows are "
        "BLOCKED and the model selection does not exist."),
}


class AnalysisError(RuntimeError):
    pass


def _cost_summary(cell) -> dict:
    """Cost, and an explicit statement of whether it can be believed.

    A missing cost is never read as zero (ADV-C). Here the refusal is reported rather than
    raised, because the point of this command is to say what CAN and CANNOT be computed from a
    record set, not to stop at the first gap.
    """
    unpriced = [a.get("attempt_id") or a.get("run_id")
                for a in cell.attempts if a.get("cost") is None]
    priced = [float(a["cost"]) for a in cell.attempts if a.get("cost") is not None]
    passes = cell.counts[PASS]
    out = {
        "attempts_priced": len(priced),
        "attempts_unpriced": len(unpriced),
        "unpriced_attempts": unpriced[:10],
        "cost_total_of_priced_attempts": round(sum(priced), 6) if priced else 0.0,
    }
    if unpriced:
        out["cost_per_successful_task"] = None
        out["cost_status"] = "BLOCKED"
        out["cost_blocked_reason"] = (
            f"{len(unpriced)} attempt(s) carry no cost. An unpriced attempt is not a free "
            "attempt; treating it as $0 makes the least-measured cell look like the cheapest.")
        return out
    if passes == 0:
        out["cost_per_successful_task"] = None
        out["cost_status"] = "NO_FINITE_VALUE"
        out["cost_blocked_reason"] = (
            "the cell has no passing attempt, so cost per successful task is infinite. That is "
            "the honest reading, not a gap to be filled or averaged away.")
        return out
    out["cost_per_successful_task"] = round(sum(priced) / passes, 6)
    out["cost_status"] = "COMPUTED"
    out["cost_definition"] = (
        "total cost of EVERY attempt in the cell, including failures, divided by PASSING "
        "attempts only (quantity 9). A failed attempt still cost money.")
    return out


def _pairing(cells: list, baseline_condition: str) -> dict:
    """Which treatment attempts can be compared with a baseline attempt, and which cannot."""
    by_key = {(c.workload, c.condition): c for c in cells}
    report = {}
    for (wl, cond), cell in sorted(by_key.items()):
        if cond == baseline_condition:
            continue
        base = by_key.get((wl, baseline_condition))
        if base is None:
            report[f"{wl}/{cond}"] = {
                "pairs": 0, "unpairable": [f"no {baseline_condition} cell exists for {wl}"],
                "comparable": False}
            continue
        pairs, unpaired = pair_attempts(cell.attempts, base.attempts)
        report[f"{wl}/{cond}"] = {
            "pairs": len(pairs),
            "treatment_attempts": len(cell.attempts),
            "unpairable": unpaired[:10],
            "unpairable_count": len(unpaired),
            # Comparability is a fact about the records. It is NOT permission to compare.
            "comparable": not unpaired and len(pairs) == len(cell.attempts),
            "note": ("every attempt pairs on (task_id, task_version, repetition) AND cache "
                     "state. Cold and warm are never paired."),
        }
    return report


def analyse(records_dir: pathlib.Path, run_plan: dict, plan_source: str,
            baseline_condition: str = "C0") -> dict:
    registry = PlannedAttempts.from_run_plan(run_plan, source=plan_source)
    attempts = load_attempts(pathlib.Path(records_dir))
    cells = build_cells(attempts, run_plan["cells"], registry=registry)

    cell_reports, reportable = [], True
    for c in cells:
        v = c.verdict()
        entry = {
            "workload": c.workload, "condition": c.condition,
            "planned": c.planned, "recorded": len(c.attempts),
            "missing": max(0, c.planned - len(c.attempts)),
            "counts": v["counts"],
            "cell_verdict": v["cell_verdict"],
            "identity_verified": v["identity_verified"],
            "build_consistent": v.get("build_consistent", True),
            "reasons": v["reasons"],
            "cost": _cost_summary(c),
        }
        if v["cell_verdict"] != "PASS":
            reportable = False
        cell_reports.append(entry)

    return {
        "level": "descriptive only",
        "plan_hash": registry.plan_hash,
        "plan_source": registry.source,
        "plan_declares": registry.declared,
        "baseline_condition": baseline_condition,
        "cells": cell_reports,
        "pairing": _pairing(cells, baseline_condition),
        "all_cells_reportable": reportable,
        "decisions_required": [
            {"output": k, "waits_on": v} for k, v in sorted(BLOCKED_OUTPUTS.items())],
        "what_this_is_not": (
            "This is a description of records that exist. It contains NO delta, NO ranking, NO "
            "non-inferiority conclusion and NO savings claim, because each of those depends on a "
            "ruling nobody has made - see decisions_required. The absence of those numbers is "
            "the result, not an omission."),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="descriptive analysis of run records; refuses unratified conclusions")
    ap.add_argument("--records", required=True)
    ap.add_argument("--run-plan", required=True,
                    help="the run plan: denominators AND planned attempt identities")
    ap.add_argument("--baseline-condition", default="C0")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    run_plan = json.loads(pathlib.Path(a.run_plan).read_text())
    try:
        rep = analyse(pathlib.Path(a.records), run_plan, a.run_plan, a.baseline_condition)
    except AggregateError as exc:
        # An integrity failure is not a small number in a table. Nothing descriptive is printed,
        # because a description of a record set that does not hold together is misinformation.
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}, indent=2))
        return 2
    text = json.dumps(rep, indent=2)
    print(text)
    if a.out:
        pathlib.Path(a.out).write_text(text + "\n")
    return 0 if rep["all_cells_reportable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

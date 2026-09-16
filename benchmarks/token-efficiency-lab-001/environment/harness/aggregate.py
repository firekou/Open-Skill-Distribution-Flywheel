"""Cell and aggregate level — CR-001-B.

v1.0.0 §6 said "≥ 95% task success" for D and "≥ 95% completion" for E without saying whether
either is evaluated per attempt or per cell. Read one way, D gets thresholded twice: once per
packet by the judge and again per cell here. v1.1.0 §6.1 fixes the levels:

    attempt  -> Quality Judge      one execution of one task under one condition
    cell     -> THIS MODULE        one (workload, condition, repetition-set)
    aggregate-> THIS MODULE        across cells, always stated explicitly

**The judge never sees a cell threshold and this module never re-scores an attempt.** Each
threshold is applied at exactly one level.

The denominator is **planned** attempts, never completed ones. Removing failures from the
denominator is the most common way a benchmark reports a success rate it did not earn, and it
usually happens by accident: you iterate over the records you have.
"""
from __future__ import annotations

import json
import math
import pathlib
from collections import defaultdict
from dataclasses import dataclass, field

PASS, FAIL_QUALITY, INVALID = "PASS", "FAIL_QUALITY", "INVALID"
OUTCOMES = (PASS, FAIL_QUALITY, INVALID)

# v1.1.0 §6: D's 0.95 is a CELL success rate. No other workload has a cell-level threshold.
CELL_SUCCESS_THRESHOLD = {"D": 0.95}


class AggregateError(RuntimeError):
    pass


@dataclass
class Cell:
    workload: str
    condition: str
    planned: int
    attempts: list = field(default_factory=list)

    @property
    def counts(self) -> dict:
        c = {o: 0 for o in OUTCOMES}
        for a in self.attempts:
            c[a["outcome"]] += 1
        return c

    @property
    def success_rate(self) -> float:
        """Passing attempts ÷ PLANNED attempts. Never ÷ completed."""
        return self.counts[PASS] / self.planned if self.planned else 0.0

    @property
    def threshold(self) -> float | None:
        return CELL_SUCCESS_THRESHOLD.get(self.workload)

    def verdict(self) -> dict:
        c = self.counts
        recorded = len(self.attempts)
        reasons = []
        ok = True

        if recorded < self.planned:
            ok = False
            reasons.append(
                f"{self.planned - recorded} planned attempt(s) produced no record at all; they "
                "stay in the denominator")
        if c[INVALID]:
            ok = False
            reasons.append(f"{c[INVALID]} attempt(s) INVALID - measured nothing, not a failure to measure")
        if c[FAIL_QUALITY]:
            ok = False
            reasons.append(f"{c[FAIL_QUALITY]} attempt(s) failed quality or breached zero tolerance")

        thr = self.threshold
        if thr is not None:
            # Worked example from v1.1.0 §6.1: denominator 3 means 3/3. 2/3 = 0.667 does not pass.
            if self.success_rate + 1e-12 < thr:
                ok = False
                reasons.append(
                    f"cell success rate {self.success_rate:.3f} < {thr} "
                    f"({c[PASS]}/{self.planned} planned)")
        return {
            "workload": self.workload,
            "condition": self.condition,
            "planned": self.planned,
            "recorded": recorded,
            "counts": c,
            "success_rate": round(self.success_rate, 4),
            "threshold": thr,
            "cell_verdict": "PASS" if ok else "FAIL",
            "reasons": reasons,
            "rate_claim_warning": (
                f"{c[PASS]}/{self.planned} passed. This does NOT mean the true success rate is "
                f"at or above {thr}; {self.planned} observations cannot support that claim."
            ) if thr is not None and ok else None,
        }


def load_attempts(records_dir: pathlib.Path) -> list[dict]:
    out = []
    for p in sorted(pathlib.Path(records_dir).glob("*.json")):
        r = json.loads(p.read_text())
        if "outcome" not in r:
            raise AggregateError(
                f"{p.name} has no `outcome`. Under v1.1.0 section 6.2 an attempt is PASS, "
                "FAIL_QUALITY or INVALID; a record without one cannot be counted, and guessing "
                "it from task_success would silently turn 'we could not measure it' into "
                "'it failed'.")
        if r["outcome"] not in OUTCOMES:
            raise AggregateError(f"{p.name} has unknown outcome {r['outcome']!r}")
        out.append(r)
    return out


def build_cells(attempts: list[dict], plan: list[dict]) -> list[Cell]:
    """`plan` supplies the PLANNED denominator. Attempts never define it."""
    planned = defaultdict(int)
    for item in plan:
        planned[(item["workload"], item["condition"])] += item.get("planned_attempts", 1)
    cells = {k: Cell(workload=k[0], condition=k[1], planned=v) for k, v in planned.items()}
    orphans = []
    for a in attempts:
        key = (a["workload"], a["condition"])
        if key not in cells:
            orphans.append(a.get("run_id", "?"))
            continue
        cells[key].attempts.append(a)
    if orphans:
        raise AggregateError(
            f"{len(orphans)} attempt(s) belong to no planned cell: {orphans[:5]}. An unplanned "
            "attempt cannot be counted without changing a denominator after the fact.")
    return [cells[k] for k in sorted(cells)]


def cost_per_successful_task(cell: Cell) -> float:
    """Quantity 9. Numerator: EVERY attempt's cost, including failures. Denominator: PASS only.

    An attempt that is cheap and fails still cost money. A cell with no passes costs infinity per
    successful task, and that is the honest number, not a gap in a table.
    """
    total = sum(float(a.get("cost", 0.0)) for a in cell.attempts)
    passes = cell.counts[PASS]
    return total / passes if passes else math.inf


def pair_attempts(treatment: list[dict], baseline: list[dict]) -> tuple[list[tuple], list[str]]:
    """v1.1.0 §7.1/§7.3 — pair on (task_id, task_version, repetition) AND cache state.

    Returns (pairs, unpairable_reasons). An unpaired attempt is NOT silently dropped: an
    unpaired comparison of cell means is not reportable, so what could not be paired has to be
    visible.
    """
    def key(a):
        return (a["task_id"], a.get("task_version"), a["repetition"])
    base = {key(a): a for a in baseline}
    pairs, unpaired = [], []
    for t in treatment:
        b = base.get(key(t))
        if b is None:
            unpaired.append(f"{t.get('run_id')}: no C0 attempt for {key(t)}")
            continue
        if t.get("cache_state") != b.get("cache_state"):
            unpaired.append(
                f"{t.get('run_id')}: cache state {t.get('cache_state')} vs baseline "
                f"{b.get('cache_state')} - cold and warm are never compared")
            continue
        pairs.append((t, b))
    return pairs, unpaired


def select_strongest(cells: list[Cell], deltas: dict) -> dict:
    """v1.1.0 §7.7 — pre-registered, deterministic, no discretion.

    `deltas` maps (workload, condition) to the cost-per-successful-task improvement versus paired
    C0. Eligibility is decided BEFORE size: a cell with any FAIL_QUALITY or INVALID attempt is
    ineligible however large its saving. That ordering is the point — the biggest saving in a
    benchmark is usually the run that quietly broke.
    """
    SINGLE = {"C1", "C2", "C3", "C4", "C5"}
    eligible, rejected = [], []
    for c in cells:
        key = (c.workload, c.condition)
        if c.condition not in SINGLE:
            rejected.append((key, "not a single-intervention condition")); continue
        cc = c.counts
        if cc[FAIL_QUALITY] or cc[INVALID]:
            rejected.append((key, f"{cc[FAIL_QUALITY]} FAIL_QUALITY / {cc[INVALID]} INVALID")); continue
        if key not in deltas:
            rejected.append((key, "no paired delta computed")); continue
        eligible.append((key, c))

    def sort_key(item):
        key, c = item
        return (-deltas[key], -c.counts[PASS], c.condition)
    eligible.sort(key=sort_key)
    chosen = [k for k, _ in eligible[:2]]

    return {
        "chosen": chosen,
        "eligible": [k for k, _ in eligible],
        "rejected": rejected,
        "shortfall": None if len(chosen) == 2 else (
            f"only {len(chosen)} eligible cell(s). Reproduce those and record the shortfall as a "
            "failed cell with its reason. Do NOT substitute an ineligible cell and do NOT relax "
            "eligibility to reach two."),
        "tie_break": "delta, then passing attempts, then condition number - deterministic",
    }


def report(cells: list[Cell]) -> dict:
    verdicts = [c.verdict() for c in cells]
    totals = {o: sum(v["counts"][o] for v in verdicts) for o in OUTCOMES}
    planned = sum(v["planned"] for v in verdicts)
    return {
        "level": "cell",
        "cells": verdicts,
        "cells_passed": sum(1 for v in verdicts if v["cell_verdict"] == "PASS"),
        "cells_failed": sum(1 for v in verdicts if v["cell_verdict"] == "FAIL"),
        "attempts_planned": planned,
        "attempt_outcomes": totals,
        "attempts_unrecorded": planned - sum(totals.values()),
        "denominator_note": (
            "Every rate above divides by PLANNED attempts. FAIL_QUALITY and INVALID both stay in "
            "the denominator, and an attempt that produced no record at all stays in it too."
        ),
    }


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="cell-level aggregation")
    ap.add_argument("--records", required=True)
    ap.add_argument("--plan", required=True, help="JSON list of {workload, condition, planned_attempts}")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    attempts = load_attempts(pathlib.Path(a.records))
    plan = json.loads(pathlib.Path(a.plan).read_text())
    rep = report(build_cells(attempts, plan))
    text = json.dumps(rep, indent=2)
    print(text)
    if a.out:
        pathlib.Path(a.out).write_text(text + "\n")
    return 0 if rep["cells_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

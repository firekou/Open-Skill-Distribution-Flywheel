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

import hashlib
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
    # R3-02: this used to be `expected: frozenset | None` - the id SET only, with
    # `identity_verified` defined as `expected is not None`. Holding a set of legal ids is not
    # having checked anything: twelve records carrying twelve legal ids while all claiming
    # task D-001 repetition 1 passed at 12/12 with `identity_verified: True`, and were selected.
    # And because the Cell keeps references to the caller's dicts, a record could be validated by
    # `build_cells` and then edited, and `verdict()` still reported the stale answer.
    #
    # The cell now holds the PLAN, not a set, and re-verifies every attempt inside `verdict()` -
    # where the rate is computed, and at the moment the number is produced. Validation at the
    # entrance plus a trusted flag at the exit is the defect this file has now shipped twice.
    plan: "PlannedAttempts | None" = None

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

    @property
    def expected(self) -> frozenset | None:
        """The planned attempt ids for this cell, read from the plan every time."""
        if self.plan is None:
            return None
        return frozenset(self.plan.cell_ids(self.workload, self.condition))

    @property
    def identity_mismatches(self) -> list:
        """Re-check every attempt against the plan AT REPORT TIME (R3-02).

        Not a cached flag, not a promise made by whoever built this cell. If the record was
        edited after `build_cells` accepted it, this sees the edit.
        """
        if self.plan is None:
            return []
        return [m for m in (self.plan.mismatch(a) for a in self.attempts) if m]

    @property
    def pending_adjudication(self) -> list:
        """Attempts holding a possible violation nobody has ruled on yet.

        ADV-D: the scorer records prose mentions that structural detection cannot decide, and the
        methodology says such an attempt is adjudicated BEFORE its cell is reported. Nothing
        enforced the "before". A PASS carrying an undecided possible violation flowed through
        finalize into a PASS cell, so the guarantee existed only in the prose that described it.
        """
        return [a.get("run_id", "?") for a in self.attempts if a.get("pending_adjudication")]

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
        # ADV-A, second line: build_cells refuses duplicates at load, but a Cell can also be
        # constructed directly (tests, notebooks, any future caller), and then the numerator is
        # again "however many records you hold". The rate is computed HERE, so the check belongs
        # here too - a defence that only guards one entrance is not a defence.
        idents = [attempt_identity(a) for a in self.attempts]
        if len(set(idents)) != len(idents):
            ok = False
            dupes = sorted({i for i in idents if idents.count(i) > 1})
            reasons.append(
                f"{len(idents) - len(set(idents))} duplicate attempt record(s) {dupes[:3]}: one "
                "attempt counted more than once inflates the numerator against a fixed planned "
                "denominator")
        # R2-02: `build_cells` refused over-count at load, but a Cell built directly still
        # reported 4 records against 3 planned as success_rate 1.3333 / PASS, and
        # select_strongest then chose it. The first ADV-A fix put the duplicate check here and
        # left the over-count check at the entrance - so the check that catches DISTINCT
        # over-count never ran where the rate is computed. A rate above 1.0 is arithmetic
        # telling you the record set is wrong; it is never clipped to 100%.
        if recorded > self.planned:
            ok = False
            reasons.append(
                f"{recorded} records for {self.planned} planned attempt(s): success rate "
                f"{self.success_rate:.4f} exceeds 1.0, which is not a result but a broken "
                "record set")
        # R2-01: identity must come from the frozen plan, not from what the record calls itself.
        mismatched = self.identity_mismatches
        if mismatched:
            ok = False
            reasons.append(
                f"{len(mismatched)} attempt(s) do not match the planned attempt they claim: "
                f"{mismatched[:3]}. Carrying a legal attempt id is not the same as being that "
                "attempt")
        if self.expected is None:
            ok = False
            reasons.append(
                "attempt identity was never checked against a frozen plan. Without the plan's "
                "own attempt id set, twelve re-runs of one task are indistinguishable from "
                "twelve planned attempts of twelve different tasks, and both read as 12/12")
        else:
            observed = {a.get("attempt_id") for a in self.attempts}
            missing = sorted(self.expected - observed)
            unexpected = sorted(observed - self.expected)
            if missing:
                ok = False
                reasons.append(
                    f"{len(missing)} planned attempt(s) absent from this cell: {missing[:5]}. "
                    "A re-run of another task does not substitute for them")
            if unexpected:
                ok = False
                reasons.append(
                    f"{len(unexpected)} record(s) claim an attempt this cell did not plan: "
                    f"{unexpected[:5]}")
        pending = self.pending_adjudication
        if pending:
            ok = False
            reasons.append(
                f"{len(pending)} attempt(s) await Red Team adjudication of a possible constraint "
                f"violation ({pending[:3]}); the cell is not reportable until each is ruled on. "
                "This is NOT a quality failure - the ruling may well be 'no violation' - it is a "
                "result that is not yet allowed to be published")

        thr = self.threshold
        if thr is not None:
            # v1.1.0 §6.1: the denominator is the run plan's planned_attempts for THIS cell -
            # 12 for a D cell (4 tasks x 3 repetitions), not 3. The document's worked example
            # said 3, which was the repetition count left over from before CR-002 made the
            # attempt the unit; it has been corrected. This code always read the plan.
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
            # R3-02: this was `self.expected is not None` - "somebody handed me a set" reported
            # as "the identities were checked". It now means the fields were compared, here, now.
            "identity_verified": self.plan is not None and not mismatched,
            "pending_adjudication": pending,
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


class PlannedAttempts:
    """The frozen run plan expanded into the exact set of attempts that may be counted.

    R2-01: `attempt_identity` alone was not identity. Its fallback keyed on `run_id`, which
    changes on every retry, so twelve records of the SAME task at the SAME repetition, differing
    only in `run_id`, filled a 12-attempt D cell and reported **12/12, 1.0, PASS** - eleven
    planned attempts of other tasks silently replaced by re-runs of one. And `attempt_id` was
    believed because the record asserted it, so twelve invented ids did the same. Neither needs
    anyone to act in bad faith: a retry loop, a renamed import or a re-sampled task does it.

    A denominator from the plan and a numerator from self-reported identity is not a check. The
    plan must supply BOTH: these ids, these tasks, these repetitions, and no others.
    """

    __slots__ = ("by_id", "by_cell", "plan_hash", "source")

    def __init__(self, by_id: dict, plan_hash: str, source: str) -> None:
        self.by_id = by_id
        self.by_cell: dict = defaultdict(set)
        for aid, exp in by_id.items():
            self.by_cell[(exp["workload"], exp["condition"])].add(aid)
        self.plan_hash = plan_hash
        self.source = source

    @classmethod
    def from_run_plan(cls, run_plan: dict, source: str = "RUN_PLAN") -> "PlannedAttempts":
        """Expand `runs[].task_attempts[]`. The plan already carries an `attempt_id` per attempt."""
        by_id = {}
        for run in run_plan.get("runs", []):
            for ta in run.get("task_attempts", []):
                aid = ta.get("attempt_id")
                if not aid:
                    raise AggregateError(
                        f"run {run.get('run_id')!r} has a task attempt with no attempt_id; the "
                        "plan cannot anchor an identity it does not name")
                if aid in by_id:
                    raise AggregateError(f"run plan issues attempt_id {aid!r} twice")
                by_id[aid] = {
                    "workload": run["workload"], "condition": run["condition"],
                    "repetition": run["repetition"], "task_id": ta["task_id"],
                    "planned_run_id": run["run_id"],
                }
        plan_hash = hashlib.sha256(
            json.dumps(by_id, sort_keys=True).encode()).hexdigest()
        return cls(by_id, plan_hash, source)

    @classmethod
    def from_ids(cls, spec: dict, source: str = "synthetic") -> "PlannedAttempts":
        """`{attempt_id: {workload, condition, repetition, task_id}}` — for tests and fixtures."""
        plan_hash = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
        return cls(dict(spec), plan_hash, source)

    def cell_ids(self, workload: str, condition: str) -> set:
        return set(self.by_cell.get((workload, condition), ()))

    def mismatch(self, a: dict) -> str | None:
        """Does this record match the planned attempt it claims to be?"""
        aid = a.get("attempt_id")
        exp = self.by_id.get(aid)
        if exp is None:
            return f"attempt_id {aid!r} is not in the frozen plan"
        for field in ("workload", "condition", "task_id", "repetition"):
            if a.get(field) != exp[field]:
                return (f"{aid}: record says {field}={a.get(field)!r}, plan says "
                        f"{exp[field]!r}. A retry may keep the planned attempt's id only if it "
                        "is the same planned attempt")
        return None


def attempt_identity(a: dict) -> tuple:
    """Which planned attempt this record IS.

    ADV-A: the denominator was planned, but the NUMERATOR was "however many records you happen to
    hold". Copy one passing record three times into a planned-3 cell and it reported 3/3 PASS;
    copy it four times and it reported 4/3 = 1.3333 and still PASS. Duplicated files, a re-run
    left beside its original, or an import run twice all become fresh successes. A planned
    denominator is worth nothing if the numerator can be inflated by copying.

    `attempt_id` is the run plan's own identity for a planned attempt and is preferred. The
    (run_id, task_id, repetition) triple is the fallback for records written before the plan
    carried one.
    """
    if a.get("attempt_id"):
        return ("attempt_id", a["attempt_id"])
    return ("triple", a.get("run_id"), a.get("task_id"), a.get("repetition"))


def build_cells(attempts: list[dict], plan: list[dict],
                registry: "PlannedAttempts | None" = None) -> list[Cell]:
    """`plan` supplies the PLANNED denominator. Attempts never define it.

    Every attempt must be a DISTINCT planned attempt of a planned cell. Duplicates and
    over-count are refused here rather than corrected, because either one means the record set
    does not describe the run that was planned, and silently de-duplicating would hide that.
    """
    planned = defaultdict(int)
    for item in plan:
        planned[(item["workload"], item["condition"])] += item.get("planned_attempts", 1)
    cells = {k: Cell(workload=k[0], condition=k[1], planned=v, plan=registry)
             for k, v in planned.items()}
    if registry:
        for k, c in cells.items():
            if c.expected is None or len(c.expected) != c.planned:
                raise AggregateError(
                    f"{k[0]}/{k[1]}: the plan's denominator says {c.planned} attempts but the "
                    f"plan enumerates {len(c.expected)} attempt ids. The plan disagrees with "
                    "itself and no rate computed from it means anything.")
    orphans = []
    seen: dict[tuple, str] = {}
    duplicates, mismatches = [], []
    for a in attempts:
        key = (a["workload"], a["condition"])
        if key not in cells:
            orphans.append(a.get("run_id", "?"))
            continue
        if registry:
            bad = registry.mismatch(a)
            if bad:
                mismatches.append(bad)
                continue
        ident = attempt_identity(a)
        if ident in seen:
            duplicates.append(f"{ident} appears again (first seen as {seen[ident]})")
            continue
        seen[ident] = a.get("run_id", "?")
        cells[key].attempts.append(a)
    if orphans:
        raise AggregateError(
            f"{len(orphans)} attempt(s) belong to no planned cell: {orphans[:5]}. An unplanned "
            "attempt cannot be counted without changing a denominator after the fact.")
    if mismatches:
        raise AggregateError(
            f"{len(mismatches)} record(s) do not match the planned attempt they claim: "
            + "; ".join(mismatches[:5]) + ". An attempt id is issued by the plan, not asserted "
            "by the record that wants to be counted.")
    if duplicates:
        raise AggregateError(
            f"{len(duplicates)} duplicate attempt record(s): {duplicates[:5]}. Two records for "
            "one planned attempt cannot both be counted; one success copied twice is not two "
            "successes. Remove the duplicate or give the re-run its own planned attempt.")
    over = [f"{c.workload}/{c.condition}: {len(c.attempts)} records for {c.planned} planned"
            for c in cells.values() if len(c.attempts) > c.planned]
    if over:
        raise AggregateError(
            "more records than planned attempts: " + "; ".join(over[:5]) +
            ". A success rate above 1.0 is arithmetic telling you the record set is wrong.")
    return [cells[k] for k in sorted(cells)]


def cost_per_successful_task(cell: Cell) -> float:
    """Quantity 9. Numerator: EVERY attempt's cost, including failures. Denominator: PASS only.

    An attempt that is cheap and fails still cost money. A cell with no passes costs infinity per
    successful task, and that is the honest number, not a gap in a table.

    ADV-C: this used to read `a.get("cost", 0.0)`, so an attempt whose cost was missing was
    counted as an attempt that cost nothing, and the cheapest-looking cell in a table could be
    the one whose costs failed to record. The pricing entrance already refuses an undeclared
    rate; the ANALYSIS exit refused nothing. A missing cost stops the economic number rather
    than lowering it.
    """
    missing = [a.get("run_id", "?") for a in cell.attempts if a.get("cost") is None]
    if missing:
        raise AggregateError(
            f"{len(missing)} attempt(s) in {cell.workload}/{cell.condition} carry no cost: "
            f"{missing[:5]}. Treating an unpriced attempt as $0 makes an unmeasured cell look "
            "like the cheapest one. Price it or report the cell as unpriceable.")
    total = sum(float(a["cost"]) for a in cell.attempts)
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


def select_strongest(cells: list[Cell], deltas: dict, variances: dict | None = None) -> dict:
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
        # ADV-B: eligibility used to be a scan of the records that HAPPENED TO EXIST - any
        # FAIL_QUALITY or INVALID among them. A cell with 1 of 3 planned attempts recorded, all
        # passing, has no failure to find, so the same module that called it FAIL by verdict
        # handed it back as a winner to reproduce. The missing attempts were the failure. The
        # cell's own verdict is the single authority, so the two answers cannot disagree again.
        v = c.verdict()
        if not v["identity_verified"]:
            # R2-02: a directly-constructed, plan-unverified cell was selectable as a winner.
            rejected.append((key, "attempt identity not verified against the frozen plan")); continue
        v = c.verdict()
        if v["cell_verdict"] != "PASS":
            rejected.append((key, "cell verdict FAIL: " + "; ".join(v["reasons"])[:200])); continue
        if key not in deltas:
            rejected.append((key, "no paired delta computed")); continue
        eligible.append((key, c))

    def sort_key(item):
        key, c = item
        # v1.1.0 section 7.7 step 4 orders ties by delta, then passing attempts, then SMALLER
        # VARIANCE, then condition. `variances` was absent from this key entirely, so the
        # published rule and the implementation disagreed on any tie. Absent variance sorts last
        # among equals rather than silently counting as zero (which would win every tie).
        var = (variances or {}).get(key)
        return (-deltas[key], -c.counts[PASS], math.inf if var is None else var, c.condition)
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
        "tie_break": (
            "v1.1.0 section 7.7 step 4: delta, then passing attempts, then smaller variance, "
            "then condition number - deterministic"),
        "variance_supplied": sorted((variances or {}).keys()),
    }


def report(cells: list[Cell]) -> dict:
    verdicts = [c.verdict() for c in cells]
    totals = {o: sum(v["counts"][o] for v in verdicts) for o in OUTCOMES}
    planned = sum(v["planned"] for v in verdicts)
    return {
        "level": "cell",
        "cells": verdicts,
        "cells_passed": sum(1 for v in verdicts if v["cell_verdict"] == "PASS"),
        "cells_identity_unverified": [
            (v["workload"], v["condition"]) for v in verdicts if not v["identity_verified"]],
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
    """R3-01: the registry was added as an OPTIONAL argument and this entry point never built one.

    So the documented command in RUNBOOK section 8 produced `identity_verified: false` and
    `cell_verdict: FAIL` on a set of twelve entirely legitimate records, and exited 1. The
    library call was fixed and the only way anyone actually runs it was not. A defence that the
    real command line cannot reach is not deployed.

    The denominator and the identities now come from **one** source: the run plan. `--run-plan`
    supplies both. `--plan` (the bare cell list) is kept for the older fixtures, and is refused
    unless a registry is supplied alongside it, rather than silently producing a cell nobody
    checked.
    """
    import argparse
    ap = argparse.ArgumentParser(description="cell-level aggregation")
    ap.add_argument("--records", required=True)
    ap.add_argument("--run-plan", default=None,
                    help="the frozen run plan. Supplies BOTH the planned denominators and the "
                         "planned attempt identities. This is the normal way to run it.")
    ap.add_argument("--plan", default=None,
                    help="JSON list of {workload, condition, planned_attempts}. Legacy shape: "
                         "denominators only, so --registry is required with it.")
    ap.add_argument("--registry", default=None,
                    help="a run plan to take attempt identities from, when --plan supplies the "
                         "denominators separately.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    if not a.run_plan and not a.plan:
        ap.error("one of --run-plan or --plan is required")
    if a.run_plan and a.plan:
        ap.error("--run-plan already carries the denominators; do not also pass --plan")

    if a.run_plan:
        run_plan = json.loads(pathlib.Path(a.run_plan).read_text())
        registry = PlannedAttempts.from_run_plan(run_plan, source=a.run_plan)
        plan = run_plan["cells"]
    else:
        if not a.registry:
            ap.error(
                "--plan gives planned counts but no attempt identities, and a cell whose "
                "identities were never checked is not reportable (R2-01). Pass --run-plan, or "
                "--registry alongside --plan.")
        registry = PlannedAttempts.from_run_plan(
            json.loads(pathlib.Path(a.registry).read_text()), source=a.registry)
        plan = json.loads(pathlib.Path(a.plan).read_text())

    attempts = load_attempts(pathlib.Path(a.records))
    rep = report(build_cells(attempts, plan, registry=registry))
    rep["plan_hash"] = registry.plan_hash
    rep["plan_source"] = registry.source
    text = json.dumps(rep, indent=2)
    print(text)
    if a.out:
        pathlib.Path(a.out).write_text(text + "\n")
    return 0 if rep["cells_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

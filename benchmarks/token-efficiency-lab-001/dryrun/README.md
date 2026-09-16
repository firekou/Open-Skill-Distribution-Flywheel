# Harness dry run — NOT a Calibration Pilot

**This directory does not contain benchmark results. It does not contain pilot results.**

## Why it exists

The Phase F Calibration Pilot has four preconditions: LG3 PASS, task set frozen, answer key
frozen, **and meter calibration PASS**. Meter calibration is **FAIL — not executed as
specified**, because no benchmark credential exists and therefore no provider-native usage field
can be obtained (`reports/LAB_001_METER_CALIBRATION_RESULT.md`). The gate does not open, and no
Pilot run was executed.

But the round's stated purpose is to *verify whether the benchmark infrastructure itself is
trustworthy*. Leaving the harness entirely unexercised would answer that question with a shrug.
So the harness is run end to end against a **replay fixture generated from a seeded PRNG**, with
no model, no provider, no credential and no cost.

## What this is and is not

| | |
|---|---|
| **Is** | A test of the plumbing: does a run produce a schema-valid record, complete raw evidence, a verifiable manifest, a correctly blinded judge packet, a recorded failure when a task is missing, a determinable cache state, the right pricing snapshot, and an identical result on a second execution |
| **Is not** | Any statement about token optimisation, about any candidate, about H1–H4, or about what a real run would cost |

Every record here carries `run_class: "dry_run"`. `harness/runner.py` **refuses** to write a
record with `run_class` of `benchmark` or `pilot` from a synthetic fixture — the guard is in the
code path, not in this README:

> refusing to record a *pilot* run from a synthetic replay fixture. There is no model in the
> loop, so the result would describe the harness, not the intervention.

## The plan

Ten runs across all five workloads and six condition shapes (`C0`, `C1`, `C2`, `C3`, `C4`,
`C2+C4`), chosen to exercise different code paths — cold and warm cache, escalation, the
cross-provider guard, and the combined-condition record shape. Ten mirrors the Pilot's size so
the shape of a real pilot is what gets tested.

## Reading these files

Nothing in `records/` may be quoted, charted, summarised or compared. The token counts are from
a pseudo-random number generator seeded on the task id. They are arbitrary by construction.

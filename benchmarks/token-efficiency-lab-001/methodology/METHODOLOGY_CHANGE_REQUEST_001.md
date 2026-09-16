# Methodology Change Request 001

**Raised:** 2026-09-16 · **Against:** `METHODOLOGY_v1.0.0.md` (FROZEN)
**Raised by:** coordinating seat, on findings from four independent seats
**Status:** **OPEN — awaiting Editor-in-Chief review. Nothing has been changed.**

The frozen methodology has not been edited and will not be. This document requests a review and
proposes `METHODOLOGY_v1.1.0.md` as a **new file**, per the immutability clause. Every run
already executed stays attributed to v1.0.0.

None of these were visible when v1.0.0 was frozen. All three surfaced when a task set, a scorer
and a harness were actually built against it.

---

## CR-001-A — §6 quality floors for workloads A and C are relative to a baseline that the judge
cannot see

**Severity: BLOCKING for LG4.** Affects 7 of 17 tasks (A×4, C×3).

§6 states the floors as *"≥ 95% of baseline's correct set"* (A) and *"≥ 90% of baseline's
covered facts"* (C). Two independent seats hit this without conferring: the Task Set Designer
recorded it as its third-least-certain decision, and the Quality Judge recorded it as UG-02, the
largest of its 33 gaps.

Two separate problems:

**1. It is unscoreable under the blind protocol.** Computing a baseline median requires knowing
which runs are C0. Knowing which runs are C0 *is* knowing the treatment. The Quality Judge's
adopted workaround — the Runner injects a `baseline_reference_quality` value, defaulting to 1.0
when absent — is conservative in the right direction (it withholds passes, never grants them),
but it forces a **two-pass scoring order that the blind protocol does not describe**:
`quality_score` is final on pass 1, while `task_success` for those 7 tasks stays provisional
until C0 completes and the scorer re-runs.

**2. It contains a perverse incentive.** If baseline quality turns out low, the bar moves down
with it, and a weak treatment passes a floor that a strong baseline would have failed. The floor
is anchored to the thing being compared against rather than to the task.

**What a fix must satisfy:** either (a) an absolute floor per workload, fixed before any run and
independent of baseline quality, or (b) the relative floor retained with the two-pass procedure
written into the methodology, including the ordering constraint (all C0 cells complete and are
scored before any relative `task_success` is determined) and an explicit statement that a low
baseline does not lower the bar. **Neither seat substituted a floor on its own** — that would
have been a methodology change by the wrong seat.

## CR-001-B — §6 does not distinguish per-task from aggregate thresholds

**Severity: MAJOR.** Affects workload D.

§6 reads *"≥ 95% task success, zero wrong-tool invocations"* for D and *"≥ 95% completion,
zero constraint violations"* for E. The Quality Judge read D's threshold as a **cell-level
aggregate over repetitions** (the Runner's job) and E's as **per-task** (the judge's job) — a
defensible reading, and the wording supports either.

Read the other way, D would be thresholded twice: once per packet by the judge and once per cell
by the runner. With 3 repetitions per cell, a run that succeeds on 2 of 3 is a 67% cell; applying
a 95% bar per packet as well makes the criterion strictly harsher than intended, and nothing in
the text says which is meant.

**What a fix must satisfy:** state, per workload, whether each threshold is evaluated per packet
or per cell, and name the seat that evaluates it.

## CR-001-C — §11 requires a pricing snapshot but not a *complete* one, while §9 requires cache
state on every record

**Severity: BLOCKING for any cached run.** Evidence E026.

§9 requires `cache_state` on every run record and allocates 6 cold-cache verification runs. §8
and `METER_CALIBRATION_v1.0.0.md` quantity 3 require cached tokens to be *"reported separately,
never folded into input"* and quantity 8 to price them *"at the cached rate"*. §11 requires every
record to carry a `pricing_snapshot_id`.

Nothing requires the snapshot to actually contain a cached rate. **It does not: 12 of the 15
rates in `PS-2026-09-15` have none** — every OpenAI model and every Anthropic model. Only
DeepSeek's two carry one.

The meter behaves correctly: it **refuses** to price such a call rather than folding cached
tokens in at the full input rate, which would overstate cost by up to 5.41× on the fixture's
cache-heavy case. But the consequence is that **any warm-cache run on an OpenAI or Anthropic
model cannot be priced today**, which removes most of C2 and C3 in long sessions.

**What a fix must satisfy:** a snapshot-completeness requirement — a run may not execute against
a snapshot that cannot price every quantity its `cache_state` implies. This is close to a §11
clarification rather than a change of substance, but it is still the methodology's to state.

**Note:** completing the snapshot is a fetch from the vendor pricing pages, not a judgement, and
would resolve the immediate blocker without any methodology change. The methodology change is
what stops it recurring.

---

## What is NOT being requested

- **No change to the research question, H1–H4, workloads A–E, conditions C0–C5, the 100-run
  allocation, the zero-tolerance criteria, the C4 tier-adjacent design, the cache-control
  requirement, the reproduction plan, or the conflict-of-interest declaration.** Guardrails 4, 5
  and 6 forbid touching the conditions and the allocation, and nothing found this round gives any
  reason to.
- **No relaxation of any floor.** CR-001-A asks for a floor that can be computed and cannot drift
  downward. If the Editor-in-Chief prefers absolute floors, they should be set at or above what
  §6 intends, not below.
- **No change on the strength of a result.** No result exists. Nothing here was found by looking
  at an outcome and wishing the rule were different; all three were found by building the
  machinery and watching it fail closed.

## Consequence if this is declined

CR-001-A and CR-001-C are blocking as written. Declining CR-001-A means LG4 runs with
`task_success` provisional for 7 of 17 tasks until C0 completes, and with the perverse incentive
live. Declining CR-001-C means either no cached runs on OpenAI or Anthropic models, or completing
the pricing snapshot by hand each time without a rule requiring it.

CR-001-B is not blocking: the Quality Judge's reading is recorded in `SCORING_SPEC.md` §9 and can
simply be ratified.

# Lab 001 — Methodology v1.1.0 Review

**Round:** Prompt 3.5 benchmark repair · **Source commit:** `a8ca352dc64e792864f351f7775e2b21681b6390`
**Branch:** `claude/atk-open-skill-distribution-96e4vv` — **not merged to main**
**Covers:** the methodology changes, the experimental unit, the 100-run mapping, and the
comparison and statistical limits that follow from them.

---

## 1. What was changed, and what the change actually costs

Three clauses changed. The review that produced them is
`methodology/METHODOLOGY_CHANGE_REVIEW_001.md`; this section records the consequences rather than
repeating the adjudication.

| CR | Clause | Change | Honest description |
|---|---|---|---|
| **A** | §6 | Quality floors: baseline-relative → answer-key-absolute | **Semantic.** The threshold now means something different. Calling this a wording fix would be the easiest lie available in this round |
| **B** | §6.1–6.2 | Attempt / cell / aggregate defined once; `INVALID` becomes a third outcome | Clarification, but with enforcement that changes results |
| **C** | §11 | Pricing snapshots must be complete, checked by a blocking preflight | Widened beyond the request |

### Why CR-001-A is not cosmetic

Under v1.0.0, A-001's **zero-work blanket answer** — reply "all functions", read nothing — scores
**0.6667**, and at a C0 median of 0.70 it returned `task_success: true`. The floor moved down to
meet it. Under v1.1.0 the same answer fails at any baseline, because there is no baseline term.

That is a real change in what the benchmark accepts, in the direction of strictness. **No floor
was lowered.** The numbers are v1.0.0's numbers with the baseline term removed.

### What passing an absolute floor does not mean

It means the attempt reached the **minimum acceptable quality**. It does **not** mean quality
matched C0, and v1.1.0 §6.0 forbids reporting it that way. Quality delta and success-rate delta
are computed after un-blinding and reported as **descriptive** numbers. A non-inferiority
claim — any form of "quality was not sacrificed" — needs a margin and a method approved in
advance. **That approval does not exist** (open item **A-a**), so no such claim may be made,
including by implication.

---

## 2. The experimental unit — the question v1.0.0 never answered

v1.0.0 §5 allocates 100 runs as workload × condition × repetitions. It never says what a run
**is**. That was invisible while no task set existed. With 17 tasks it decides the size of the
experiment.

| Reading | Result |
|---|---|
| A run = one task attempt | **Impossible.** C0 has 15 runs for 17 tasks; some task gets no baseline |
| A run = one (workload, condition, repetition) unit, attempting every task in that workload | **Fits exactly** |

v1.1.0 §5.1 adopts the second. It is not a preference — it is the only reading the arithmetic
permits.

> **A run is an aggregation unit. A task attempt is the unit of execution and of quality
> scoring.** Every task attempt is its own independent agent session.

The session rule matters most for workload E: running its three scenarios inside one session
would contaminate the context-accumulation measurement E exists to make.

### 2.1 The mapping, in full

| Condition | Workloads | Runs | Task attempts |
|---|---|--:|--:|
| C0 | A, B, C, D, E | 15 | 51 |
| C1 | A, D | 6 | 24 |
| C2 | A, B, C, D | 12 | 42 |
| C3 | B, E | 6 | 18 |
| C4 | A, B, C, D, E | 15 | 51 |
| C5 | A, B, D | 9 | 33 |
| C2+C4 | A, B, D | 9 | 33 |
| C3+C4 | B, E | 6 | 18 |
| **Experimental** | | **78** | **270** |
| Reproduction | | 10 | per §7.7 selection |
| Cache control | | 6 | — |
| Meter calibration | | 6 | — |
| **Total** | | **100** | |

**78 + 22 = 100.** The allocation is untouched: no cell added, removed, renamed or re-weighted,
no task dropped, no repetition count changed. Machine-readable form:
`benchmarks/token-efficiency-lab-001/RUN_PLAN_v1.1.0.json`, which enumerates all 78 runs and all
270 attempts explicitly rather than leaving them to be inferred.

### 2.2 What it costs, stated rather than buried

**270 task attempts, a mean of 3.46 per run.** Every prior cost figure in this repository assumed
one attempt per run, so:

| | Prior | Revised |
|---|---|---|
| Cost | $51–94 | **≈ $177–325** |
| Execution time | 8–16 h | scales similarly |

This is why **`METHODOLOGY_CHANGE_REQUEST_002`** exists. The allocation genuinely did not change,
but a 3.46× multiplier that appears only as an inference from a definition should be ruled on
before it is spent. The change request costs four alternatives, including the cheap one (a single
designated task per workload, ~117 attempts) and says plainly what that one costs in measurement
quality.

**The run-plan-mapping freeze gate is PENDING, not PASS.**

### 2.3 Two arithmetic traps, explicitly avoided

- **Three repetitions of a workload are not three repetitions of each task**, and the two are not
  interchangeable. The run plan enumerates attempts individually so the distinction cannot be
  blurred.
- **Three outputs of one task are not three independent task samples.** They are three
  repetitions of one measurement. The run plan carries `repetition` per attempt, and the
  aggregator groups by cell, never by attempt count.

---

## 3. Comparison design

v1.0.0 had no comparison design. v1.1.0 §7 adds one; it is new, not a restatement.

| Element | Rule |
|---|---|
| **Pairing** | Every treatment attempt pairs with the C0 attempt of the **same task id, task-set version and repetition index**. Unpaired comparison of cell means is not reportable |
| **Order** | Within a repetition index, all C0 attempts for a task complete before any treatment attempt for it. Order recorded per attempt |
| **Cache pairing** | Cold is compared only with cold. A run whose cache state cannot be determined is `INVALID`, not "probably cold" |
| **Denominator** | **Planned** attempts, never completed ones |
| **Combined conditions** | `C2+C4` and `C3+C4` run only after both singles report |
| **Retry budget** | Proposed: at most one re-run per planned attempt, `INVALID` only, both records retained. **Needs ratification (B-a)** |

### 3.1 "The two strongest single results"

v1.0.0 §10 required reproducing them and never said how to pick them. §7.7 makes it
pre-registered and deterministic:

1. Single-intervention conditions only. Combined conditions are ineligible.
2. Rank by cost-per-successful-task improvement versus paired C0, at cell level.
3. **A cell containing any `FAIL_QUALITY` or `INVALID` attempt is ineligible, however large its
   saving.** Eligibility is decided before size — the largest saving in a benchmark is usually
   the run that quietly broke.
4. Ties: more passing attempts, then smaller variance, then lower condition number.
5. Fewer than two eligible: reproduce what is eligible and record the shortfall as a failed cell.
   **Do not substitute an ineligible cell. Do not relax eligibility to reach two.**

Verified in `harness/aggregate.py`: given a fixture where the two largest deltas are a combined
condition (0.95) and a cell with one quality failure (0.90), the selector rejects both and
chooses the third and fourth largest.

---

## 4. Statistical limits

**Three repetitions per cell supports descriptive comparison and nothing else.**

| Permitted | Prohibited |
|---|---|
| Per-cell cost, tokens, quality, success rate | Significance testing |
| Paired per-attempt deltas | Non-inferiority claims |
| Cost per successful task | Superiority rankings |
| Descriptive ranges | "X% cheaper at equal quality" |

**"3 of 3 passed" is not "a ≥95% success rate".** Three observations cannot support that claim,
and `aggregate.py` attaches that sentence to every passing D cell so the claim cannot be made by
accident downstream.

Any inferential claim requires a design this methodology does not contain. Producing one is a new
change request, not an analysis choice made after seeing the numbers.

---

## 5. Failure taxonomy, and why it has three values

v1.0.0 had `task_success: true | false`. Two values cannot distinguish **"the intervention
produced a worse answer"** from **"we could not measure this attempt at all"**, and collapsing
them is not neutral: it turns an unmeasured run into evidence against the treatment, or — more
often — lets a run with missing evidence disappear from a success rate.

| Outcome | Success | In denominator |
|---|---|---|
| `PASS` | yes | yes |
| `FAIL_QUALITY` | no | yes |
| `INVALID` / `UNSCORABLE` | no | **yes** |

`INVALID` is not deleted, not folded into a savings average at zero cost, and not replaced by an
automatic re-run. A re-run is a new record; the original stands. Enforced in `record.py`
(a record without an outcome is refused), `finalize.py` (a score that declares no outcome is
refused rather than inferred from `task_success`) and `aggregate.py` (a planned attempt with no
record at all still counts against the denominator).

---

## 6. Open decisions

| id | Question | Blocks freeze | Blocks publication |
|---|---|---|---|
| **CR-002** | Ratify the run-plan unit and its 3.46× cost consequence | **yes** (gate PENDING) | — |
| **A-a** | Non-inferiority margin and statistical method | no | **yes — any quality-parity claim** |
| **B-a** | Retry budget | no | no |
| **C-a** | Which models and API plans the run plan uses | no | **yes — pricing cannot complete without it** |

None of these can be settled by this seat: three are budget or business decisions and one is a
statistical commitment that must be made before the numbers exist, not after.

---

## 7. What this review does not establish

- **v1.1.0 is a DRAFT.** No independent reviewer has signed it off. The Editor-in-Chief approved
  the revision *direction*; a draft that follows an approved direction is still a draft.
- **No run has executed under it.** Every claim here is about text, arithmetic and code paths.
- **It says nothing about H1–H4.** The methodology describes how they would be tested. Nothing was
  tested.
- **A complete methodology is not a complete benchmark.** Pricing, credentials, provider-native
  calibration, candidate runtime status and the task set each gate separately.

# Methodology Change Review 001

**Reviews:** `METHODOLOGY_CHANGE_REQUEST_001.md`
**Reviewed at:** source commit `a8ca352dc64e792864f351f7775e2b21681b6390`
**Review date:** 2026-09-16 · **Reviewing seat:** methodology-reviewer
**Authority:** Editor-in-Chief approved the revision *direction* (Prompt 3.5 §3). This document
records the adjudication and the exact clause text that follows from it.
**Status of the outcome:** `METHODOLOGY_v1.1.0.md` is **DRAFT / REVIEW_PENDING**. Approval of a
direction is not approval of a deliverable.

> **`METHODOLOGY_v1.0.0.md` is not edited by this review and never will be.** Its sha256 is
> `c1810b0481d1442937771c124c7c30668490470f00dcf71098bdf139ee7089bc`, unchanged, re-verified at
> the start and the end of this round. Every run executed under it stays attributed to it.

---

## CR-001-A — quality floors

### Original clause (v1.0.0 §6, verbatim)

| Workload | Quality floor as frozen |
|---|---|
| A | "≥ 95% of baseline's correct set, **zero fabricated symbols**" |
| B | "≥ 97% exact-match on a pre-built answer key" |
| C | "100% traceable, ≥ 90% of baseline's covered facts" |
| D | "≥ 95% task success, zero wrong-tool invocations" |
| E | "≥ 95% completion, **zero constraint violations from forgotten context**" |

### Root cause

Two of the five floors (A and C) are defined **relative to the baseline condition's own result**.
That couples the acceptance criterion to a quantity produced by the experiment, which creates two
independent failures.

1. **It is unscoreable under the blind protocol.** Computing a baseline median requires knowing
   which attempts are C0. Knowing which attempts are C0 *is* knowing the treatment. The blind
   protocol exists to prevent exactly that.
2. **The bar moves with the baseline.** A weak C0 lowers the threshold a treatment must clear.
   The floor is anchored to the comparison rather than to the task.

### Evidence

- `RED_TEAM_REVIEW.md` RT-05, measured: at a C0 median of **0.70**, A-001's zero-work blanket
  answer — which scores **0.6667** without reading the corpus at all — returns
  `task_success: true`. A-003 has the same cliff at a C0 median ≤ 0.638.
- `SCORING_SPEC.md` §9 **UG-02**, reached independently by the Quality Judge: it had to adopt a
  `baseline_reference_quality` injection defaulting to 1.0, which forces a two-pass scoring order
  the blind protocol does not describe.
- `DESIGN_NOTES.md` §7 item 3, reached independently by the Task Set Designer.

Three seats that did not confer found the same defect. That is the strongest signal available
here short of running the thing.

### Ruling — **UPHELD. Adopt absolute, answer-key-anchored floors.**

This is **not a wording correction.** Moving from baseline-relative to answer-key-absolute
**changes what the threshold means**, and v1.1.0 says so in its own text. A run that passes an
absolute floor has cleared a minimum acceptable quality; it has **not** thereby been shown equal
to C0.

### Revised clause (v1.1.0 §6)

Per **complete task attempt**, evaluated by the Quality Judge from the blind packet alone:

| Workload | v1.1.0 floor | Zero-tolerance (unchanged from v1.0.0) |
|---|---|---|
| A | `quality_score ≥ 0.95` computed against the **full** answer key | zero fabricated symbols |
| B | `quality_score ≥ 0.97` | no fabricated record id |
| C | `coverage ≥ 0.90` **and** `traceability = 1.00` | traceability is itself zero-tolerance |
| D | correct tool **and** correct answer for this attempt | zero wrong-tool invocations |
| E | `completion ≥ 0.95` | zero constraint violations across **every turn that occurred** |

D's "≥ 95% task success" is **not** an attempt-level threshold; it is a cell success rate owned
by the aggregator (see CR-001-B).

### Prohibitions added by this ruling

1. **No floor may be lowered to make a task pass.** The numbers above are the v1.0.0 numbers with
   the baseline term removed, not softened numbers.
2. **`baseline_reference_quality` may not determine `task_success` under v1.1.0.** No default
   baseline, no hidden second scoring pass, no re-score branch. The v1.0.0 code path may remain
   for replaying v1.0.0 records, but it must be **version-gated**, and a packet whose methodology
   version is missing or incompatible must be **refused**, not scored under a guess.
3. **Passing an absolute floor may not be reported as "quality equal to C0".** Quality delta,
   success-rate delta and paired comparison remain, computed after un-blinding. Any
   non-inferiority claim requires a pre-approved margin and statistical method; without one,
   only descriptive numbers may be reported, and "no quality was sacrificed" may not be written.

### Acceptance tests

| # | Test | Expected |
|---|---|---|
| A-1 | Score A-001's blanket answer with no baseline supplied | `quality_score ≈ 0.6667`, `task_success: false` |
| A-2 | Same packet with a simulated C0 median of 1.00 | identical result |
| A-3 | Same packet with a simulated C0 median of 0.70 | identical result — **this is the case that passed under v1.0.0** |
| A-4 | Any packet scored twice with different external C0 results | byte-identical score both times |
| A-5 | A v1.1.0 packet carrying `baseline_reference_quality` | field ignored; recorded in `detail.ignored_packet_keys` |
| A-6 | A packet with a missing or unrecognised methodology version | **refused**, not scored |

### Affected files

`methodology/METHODOLOGY_v1.1.0.md` · `environment/harness/judge.py` ·
`tasks/TASK_SET_v1.1.0/SCORING_SPEC.md` · `tasks/TASK_SET_v1.1.0/tasks/{A,C}/*.json` ·
`environment/harness/runner.py` (stops needing to inject a baseline) ·
`BLIND_EVALUATION_PROTOCOL.md` (the two-pass description is no longer needed).

### Responsible seats

Methodology Reviewer (clause) · Quality Judge (scorer + tests) · Task Set Designer (task text) ·
Task Red Team (verification).

### Still open for decision

**A-a.** The non-inferiority margin and statistical method for any later "quality did not drop"
claim. Not needed to freeze; needed before any result is published. Recorded so it cannot be
invented after the numbers are in.

---

## CR-001-B — attempt, cell and aggregate

### Original clause (v1.0.0 §6, verbatim)

> "≥ 95% task success, zero wrong-tool invocations" (D) · "≥ 95% completion, zero constraint
> violations from forgotten context" (E)

### Root cause

Neither threshold says whether it is evaluated **per attempt** or **per cell**. The Quality Judge
read D as a cell-level aggregate and E as per-attempt — defensible, and the text supports either.
Read the other way, D is thresholded twice: once per packet by the judge and again per cell by
the runner.

### Evidence

`SCORING_SPEC.md` §9 cross-cutting notes, self-declared by the Quality Judge before anyone asked.

### Ruling — **UPHELD.**

### Revised clause (v1.1.0 §6.1) — three levels, named once and used everywhere

| Level | Unit | Numerator / denominator | Owning seat |
|---|---|---|---|
| **Attempt** | one complete execution of one task under one condition | the task's own metric over the full answer key | **Quality Judge** |
| **Cell** | one (workload, condition, repetition-set) group | attempts passing the floor ÷ attempts **planned** for the cell | **Runner / Aggregator** |
| **Aggregate** | across cells | stated explicitly wherever it appears | **Aggregator** |

**D's 95% is a cell success rate.** With a denominator of 3 planned attempts, **3/3 is required;
2/3 = 0.667 does not pass.** The same threshold is applied **once**, at the cell level, never
again at the attempt level.

**3/3 does not mean "the true success rate is ≥ 95%".** It means three of three passed. Three
observations cannot support a 95% rate claim, and no report may say otherwise.

### Failure taxonomy (v1.1.0 §6.2) — three outcomes, never two

| Outcome | Meaning | Counts as success | In the denominator |
|---|---|---|---|
| `PASS` | scored and met the floor | yes | yes |
| `FAIL_QUALITY` | scored and missed the floor, or breached zero tolerance | no | yes |
| `INVALID` / `UNSCORABLE` | could not be scored — missing evidence, tool-chain failure, unpriceable usage | **no** | **yes** |

Rules that follow, all of them prohibitions on things that would flatter a result:

- A confirmed zero-tolerance violation fails its cell **outright**. Mean quality may not absorb it.
- `INVALID` is **not** silently deleted, **not** folded into a savings average at zero cost, and
  **not** replaced by an automatic re-run. A re-run is a new record; the original stands.
- Both `FAIL_QUALITY` and `INVALID` stay in the denominator. Removing failures from the
  denominator is the most common way a benchmark reports a success rate it did not earn.

### Acceptance tests

| # | Test | Expected |
|---|---|---|
| B-1 | A D cell with 3 planned attempts, 2 passing | cell `FAIL`, rate 0.667 |
| B-2 | A D cell with 3 of 3 passing | cell `PASS`, and the report must not read "≥95% success rate" |
| B-3 | One attempt `INVALID`, two `PASS` | rate 0.667, `INVALID` visible, cell `FAIL` |
| B-4 | An attempt with a zero-tolerance breach and quality 1.00 | attempt fails; cell fails |
| B-5 | Attempt-level threshold applied to D anywhere in the pipeline | must not exist — asserted by test |

### Affected files

`METHODOLOGY_v1.1.0.md` §6.1–6.2 · task schema (`level` per metric) · `judge.py` (attempt only) ·
`runner.py` / new aggregator (cell) · `run_record_schema.json` (`outcome` enum) · every report.

### Responsible seats

Methodology Reviewer · Quality Judge (attempt) · Runner/Aggregator (cell) · Red Team.

### Still open for decision

**B-a.** The retry budget: how many `INVALID` attempts a cell may re-run before the cell itself is
declared failed. Proposed in v1.1.0 §7.6 as **at most one re-run per planned attempt, both
records retained**; needs ratification.

---

## CR-001-C — pricing completeness

### Original clause (v1.0.0 §11, verbatim)

> "Every run record carries `pricing_snapshot_id`. Token counts are physical; prices move."

### Root cause

§11 requires a snapshot. It does not require the snapshot to be able to **price the quantities
§9 forces every record to report**. §9 requires `cache_state` on every record and allocates 6
cold-cache runs; `METER_CALIBRATION_v1.0.0.md` quantity 3 requires cached tokens priced at the
cached rate and never folded into input.

### Evidence

**E026, measured.** 12 of the 15 rates in `PS-2026-09-15` carry no cached input rate — every
OpenAI model and every Anthropic model. Only DeepSeek's two do. The meter **refused** to price a
cached call rather than folding cached tokens in at the full input rate, which on the calibration
fixture's cache-heavy case would have overstated cost by **5.41×**. Correct behaviour; the
consequence is that no warm-cache run on those providers can be priced today, which removes most
of C2 and C3 in long sessions.

### Ruling — **UPHELD, and the scope is wider than the request stated.**

The request asked for a completeness requirement. Review adds three things it did not ask for,
because the same defect class produces them:

1. Completeness must be checked against **what the provider can actually return**, including
   automatic caching, **not** against what the run plan declares as cold or warm. A run plan that
   says "cold" does not stop a provider serving a cache hit.
2. Token **inclusion relationships** must be declared per provider, so cached and reasoning
   tokens are not double-counted against a total that already contains them.
3. Retries, failed calls, escalation targets and any extra calls made by a compression or routing
   intervention must all be priced. The cost of an intervention includes the calls the
   intervention itself makes.

### Revised clause (v1.1.0 §11)

- A new snapshot with a **new ID**. `PS-2026-09-15` is not overwritten, amended or re-dated.
- Per model actually used, and per API plan actually used, the snapshot records: official vendor
  source URL, retrieval date, currency, billing unit, and rates for **standard input, output,
  cache read, cache write, cache TTL tiers where the vendor has them, and any other applicable
  fee**.
- A billing dimension the vendor does not have is recorded as **`not_applicable` with the
  evidence for that claim**. **A missing rate is never recorded as zero.**
- A machine-readable **preflight** runs before execution and **blocks** if any applicable rate is
  absent for any model in the run plan.
- If real usage returns a billable quantity the snapshot does not cover, the run is marked
  **`unpriceable`**, its evidence is retained, and the harness does **not** estimate the price.
- Where an external source or credential is unavailable, the affected row is recorded
  **`BLOCKED`** with what is missing. **No price is invented**, and no plaintext credential is
  requested or displayed.

**Fixing the snapshot does not constitute provider-native meter calibration.** They are different
gates and one does not imply the other.

### Acceptance tests

| # | Test | Expected |
|---|---|---|
| C-1 | Preflight against a model with no cache-read rate | **BLOCK**, naming model and dimension |
| C-2 | Preflight against a fully specified model | PASS |
| C-3 | A `not_applicable` row with no evidence | **BLOCK** |
| C-4 | Usage returning a quantity the snapshot lacks | record `unpriceable`, no estimate |
| C-5 | Cached tokens included in the provider's input total | counted once |
| C-6 | Retry, escalation and intervention-issued calls | all present in total cost |

### Affected files

`METHODOLOGY_v1.1.0.md` §11 · new `evidence/PRICING_SNAPSHOT_<new-id>.{md,json}` ·
`environment/harness/pricing.py` · new `environment/harness/pricing_preflight.py` ·
`METER_CALIBRATION_v1.1.0.md` (quantity inclusion rules).

### Responsible seats

Methodology Reviewer · Harness/Evidence Producer · Coordinator (sourcing).

### Still open for decision

**C-a.** Which models and which API plans the LG4 run plan will actually use. The snapshot cannot
be completed for models nobody has chosen, and choosing them is not this seat's call.

---

## Summary

| CR | Ruling | Blocks freeze | Blocks Pilot |
|---|---|---|---|
| **CR-001-A** | UPHELD — absolute floors, semantics change acknowledged | Closed by v1.1.0 §6 | no |
| **CR-001-B** | UPHELD — three levels, three outcomes | Closed by v1.1.0 §6.1–6.2 | no |
| **CR-001-C** | UPHELD and widened | Closed by v1.1.0 §11 + preflight | **yes, until a complete snapshot exists** |

Three items remain open for the Editor-in-Chief: **A-a** (non-inferiority margin), **B-a** (retry
budget), **C-a** (model and plan selection). None blocks the production of a freeze candidate.
**A-a and C-a both block publication of any cost claim.**

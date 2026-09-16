# Token Efficiency Lab 001 — Methodology v1.1.0

**Status:** **DRAFT / REVIEW_PENDING** · **NOT FROZEN** · **NOT APPROVED FOR EXECUTION**
**Supersedes:** nothing yet. `METHODOLOGY_v1.0.0.md` remains the only frozen methodology.
**Derives from:** `METHODOLOGY_v1.0.0.md` (sha256 `c1810b04…89bc`, unmodified) as amended by
`METHODOLOGY_CHANGE_REVIEW_001.md`
**Drafted:** 2026-09-16 · **Drafting seat:** methodology-reviewer

> **v1.0.0 is not edited, replaced or retired by this file.** It is a separate file and it stays
> frozen. Every run executed under v1.0.0 remains attributed to v1.0.0 forever. This document
> becomes usable only when an independent reviewer signs it off; until then no run may cite it.

## What changed, and what deliberately did not

**Changed — three clauses, all from `METHODOLOGY_CHANGE_REVIEW_001`:**

| § | Change | Kind |
|---|---|---|
| **6** | Quality floors move from baseline-relative to **answer-key-absolute** | **Semantic. Not a wording fix.** |
| **6.1–6.2** | **Attempt / cell / aggregate** are defined once and used everywhere; `INVALID` becomes a third outcome | Clarification with teeth |
| **11** | Pricing snapshots must be **complete**, checked by a blocking preflight | Widened from the request |

**Added — clauses v1.0.0 did not have:**

§5.1 run-plan mapping (what a "run" is) · §7 comparison design · §12.1 evidence contract ·
§13 versioning and refusal.

**Deliberately unchanged, and not open for change here:** the research question · H1–H4 ·
workloads A–E · conditions C0–C5 · the 100-run allocation · the C4 tier-adjacent design · cache
control · the independent reproduction requirement · the conflict-of-interest declaration · every
zero-tolerance criterion.

---

## 1. Research question — unchanged

**Where do Agents waste tokens, and which interventions reduce total task cost without
materially reducing task success?**

## 2. Hypotheses H1–H4 — unchanged

| ID | Hypothesis | Pre-registered direction |
|---|---|---|
| **H1** | Large MCP/tool schemas create measurable fixed context overhead | Overhead grows with tool count; deferred exposure or a code-execution pattern reduces it |
| **H2** | Raw intermediate tool results create avoidable variable overhead | Filtering/compression reduces total tokens at an acceptable quality cost |
| **H3** | Model misrouting creates hidden cost via overpowered selection or retry/escalation | A complexity-aware route beats always-frontier on cost at equal quality |
| **H4** | Context accumulation creates avoidable repeated-token cost | Compaction/clearing reduces tokens in long sessions |

Lab hypotheses, distinct from the strategic H001–H010. **Not ATK claims** until TESTED and
VERIFIED. Pre-registered null results are publishable.

## 3. Workloads A–E — unchanged

| ID | Workload | Why it is in the set |
|---|---|---|
| **A** | Repository / code analysis | Many tool calls, large file payloads |
| **B** | Long-document extraction | Single large context, low tool count |
| **C** | Multi-source research | Many small results, high aggregation |
| **D** | MCP-heavy multi-tool task | Maximum schema overhead — the H1 probe |
| **E** | Long multi-turn agent workflow | Context accumulation — the H4 probe |

## 4. Conditions C0–C5 — unchanged

| ID | Condition | Tests |
|---|---|---|
| **C0** | Baseline, no intervention | — |
| **C1** | Deferred/reduced tool-schema exposure (code-execution pattern) | H1 |
| **C2** | Tool-result filtering / compression | H2 |
| **C3** | Context compaction / clearing | H4 |
| **C4** | Routing by task complexity, tier-adjacent pairs (§8) | H3 |
| **C5** | Third-party optimisation tool, only after LG2 pass | H2 |

## 5. 100-run allocation — unchanged, and it is unchanged

| Condition | Workloads | Reps | Runs |
|---|---|--:|--:|
| C0 baseline | A, B, C, D, E | 3 | **15** |
| C1 schema deferral | A, D | 3 | **6** |
| C2 result filtering | A, B, C, D | 3 | **12** |
| C3 compaction | B, E | 3 | **6** |
| C4 routing | A, B, C, D, E | 3 | **15** |
| C5 third-party tool | A, B, D | 3 | **9** |
| C2+C4 combined | A, B, D | 3 | **9** |
| C3+C4 combined | B, E | 3 | **6** |
| Reproduction | 2 strongest single results | 5 | **10** |
| Cache-state control | cold-cache verification | — | **6** |
| Meter calibration | meter vs provider `usage` | — | **6** |
| | | | **100** |

**Freeze rule, unchanged:** a cell that cannot execute is recorded as a **failed cell with a
reason** — never silently reallocated, never replaced with a substitute.

## 5.1 Run-plan mapping — **NEW, and it needs ratification**

v1.0.0 never defined what a "run" is. The task set has 17 tasks; the matrix counts
workload × condition × repetition. Those two facts do not reconcile on their own, and the
reconciliation has a material cost consequence, so it is written down rather than assumed.

**Definition adopted here:**

> **A run is one (workload, condition, repetition) unit.** Within a run, **every task in that
> workload is attempted**, each as its own independent agent session.
> A run is an aggregation unit. A **task attempt** is the unit of execution and of quality
> scoring.

This is the only reading that fits 17 tasks into the frozen allocation without touching it. The
alternative — run = attempt — cannot work: a single C0 cell would have 15 runs for 17 tasks.

### What that means arithmetically

| Condition | Workloads | Runs | **Task attempts** |
|---|---|--:|--:|
| C0 | A, B, C, D, E | 15 | 51 |
| C1 | A, D | 6 | 24 |
| C2 | A, B, C, D | 12 | 42 |
| C3 | B, E | 6 | 18 |
| C4 | A, B, C, D, E | 15 | 51 |
| C5 | A, B, D | 9 | 33 |
| C2+C4 | A, B, D | 9 | 33 |
| C3+C4 | B, E | 6 | 18 |
| **Experimental subtotal** | | **78** | **270** |
| Reproduction / cache / meter | | 22 | see §10, §9, §12 |
| **Total** | | **100** | |

**The allocation is unchanged. 78 + 22 = 100.** No cell was added, removed, renamed or
re-weighted, and no task was dropped to make the numbers work.

### The consequence, stated plainly

**270 task attempts, not 100.** A mean of **3.46 attempts per run**. Any cost estimate that
assumed one attempt per run is low by that factor: the previous **$51–94** becomes roughly
**$177–325** on the same assumptions.

Each task in a workload is a **separate agent session**. Workload E in particular must not run
its three scenarios inside one session — that would contaminate the context-accumulation
measurement E exists to make.

> **RATIFICATION REQUIRED.** The definition is forced by the arithmetic, but the 3.46× cost
> consequence is material and the Editor-in-Chief has not seen it. Raised as
> **`METHODOLOGY_CHANGE_REQUEST_002`**. The freeze-readiness gate for run-plan mapping is
> **PENDING**, not PASS, until that is ruled on.

### Comparability constraint

Every condition compares **the same task ids, the same task-set version, the same corpora and
the same configuration**. The only permitted difference between a treatment attempt and its
baseline attempt is the **registered intervention**. Selecting a subset of tasks per condition,
renaming runs, or dropping a task to resolve an inconsistency is prohibited.

## 6. Quality floors — **CHANGED: absolute, per attempt**

Evaluated per **complete task attempt** by the Quality Judge, from the blind packet alone,
against the **full** answer key.

| Workload | Floor | Zero-tolerance |
|---|---|---|
| **A** | `quality_score ≥ 0.95` | **zero fabricated symbols** |
| **B** | `quality_score ≥ 0.97` | no fabricated record id |
| **C** | `coverage ≥ 0.90` **and** `traceability = 1.00` | traceability is itself zero-tolerance |
| **D** | correct tool **and** correct answer for this attempt | **zero wrong-tool invocations** |
| **E** | `completion ≥ 0.95` | **zero constraint violations across every turn that occurred** |

**D's "≥ 95% task success" from v1.0.0 §6 is a cell success rate** (§6.1), not an attempt
threshold. It is applied once, at the cell level.

**Any zero-tolerance criterion fails the attempt outright regardless of the percentage**, and
fails its cell. Mean quality may not absorb it.

### 6.0 What passing a floor does and does not mean

Passing an absolute floor means the attempt reached **the minimum acceptable quality**. It does
**not** mean quality equals C0, and no report may say so.

Quality delta, success-rate delta and paired comparison are computed **after un-blinding** and
reported as **descriptive** numbers. A non-inferiority claim — "quality was not sacrificed" —
requires a margin and a statistical method **approved in advance**. Without that approval, the
claim may not be made in any form, including by implication.

**Lower cost with unacceptable quality is a failed optimisation, not a trade-off.**

### 6.0.1 Prohibitions carried from the change review

1. No floor may be lowered to make a task pass.
2. **`baseline_reference_quality` may not determine `task_success` under v1.1.0.** No default
   baseline, no hidden second pass, no re-score branch. The v1.0.0 path may exist only for
   replaying v1.0.0 records and must be version-gated.
3. A packet whose methodology version is absent or unrecognised is **refused**, not scored
   under a guess (§13).

### 6.1 Attempt, cell, aggregate — **NEW**

| Level | Unit | Numerator ÷ denominator | Owning seat |
|---|---|---|---|
| **Attempt** | one execution of one task under one condition | the task's metric over the full answer key | **Quality Judge** |
| **Cell** | one (workload, condition, repetition-set) | attempts passing the floor ÷ attempts **planned** | **Runner / Aggregator** |
| **Aggregate** | across cells | stated explicitly at every use | **Aggregator** |

Every metric in every task file, scorer, run record and report carries its level. **A threshold
is applied at exactly one level.**

**D, worked:** planned denominator 3 ⇒ **3/3 required**; 2/3 = 0.667 fails the cell. And **3/3
does not mean the true success rate is ≥ 95%** — three observations cannot support that claim.

### 6.2 Outcome taxonomy — **NEW: three outcomes, never two**

| Outcome | Meaning | Success | In denominator |
|---|---|---|---|
| `PASS` | scored, met the floor, no zero-tolerance breach | yes | yes |
| `FAIL_QUALITY` | scored, missed the floor or breached zero tolerance | no | yes |
| `INVALID` / `UNSCORABLE` | could not be scored: missing or empty required evidence, tool-chain failure, unpriceable usage, undeterminable cache state | **no** | **yes** |

- `INVALID` is **not** deleted, **not** folded into a savings average at zero cost, and **not**
  replaced by an automatic re-run. A re-run is a **new record**; the original stands.
- Both failure kinds stay in the denominator. Removing failures from the denominator is the most
  common way a benchmark reports a success rate it did not earn.
- `INVALID` and `FAIL_QUALITY` are reported separately. "It failed" and "we could not measure it"
  are different findings.

## 7. Comparison design — **NEW**

### 7.1 Pairing
Every treatment attempt pairs with the C0 attempt of the **same task id, task-set version and
repetition index**. Comparison is **paired at the attempt level**; unpaired comparison of cell
means is not reportable.

### 7.2 Execution order
Within a repetition index, all C0 attempts execute **before** any treatment attempt for the same
task. The order is recorded per attempt. Interventions are never interleaved inside one session.

### 7.3 Cache pairing
A treatment attempt is compared only with a C0 attempt in the **same cache state**. Cold and warm
are never mixed in one comparison. A run whose cache state cannot be determined is `INVALID`
(§6.2) — not "probably cold".

### 7.4 Failure denominator
Success rates use **planned** attempts as the denominator (§6.1). Never completed attempts.

### 7.5 Combined conditions
`C2+C4` and `C3+C4` execute **only after both single conditions have reported**. A combined cell
whose singles did not report is a failed cell with that reason.

### 7.6 Retry budget — **needs ratification (CR-001-B item B-a)**
Proposed: **at most one re-run per planned attempt, and only for `INVALID`**, never for
`FAIL_QUALITY`. Both records are retained and both appear in the evidence. A cell needing more
is a failed cell.

### 7.7 "The two strongest single results" (§10 reproduction)
Selection is **pre-registered before any result is read**:

1. Eligible: single-intervention conditions only (C1, C2, C3, C4, C5). Combined conditions are
   not eligible.
2. Rank by **cost per successful task** improvement versus paired C0, computed at the cell level.
3. A cell with any `FAIL_QUALITY` or `INVALID` attempt is **not eligible**, however large its
   saving.
4. **Tie:** break by the larger number of passing attempts; then by the smaller variance; then by
   the lower condition number. Deterministic, no discretion.
5. **Fewer than two eligible cells:** reproduce however many are eligible and record the shortfall
   as a failed cell with its reason. **Do not substitute an ineligible cell, and do not relax
   eligibility to reach two.**

### 7.8 Statistical limits
With 3 repetitions per cell, the design supports **descriptive comparison only**. No superiority
ranking, no non-inferiority claim, and no significance language may be published from it. Any
inferential claim requires a pre-approved design that this document does not contain.

## 8. C4 tier-adjacent routing — unchanged

Verified pricing shows tier-adjacent models differ by ~11×, while cheapest-vs-pro-tier reaches
257×. Pairing across five tiers measures a real number that **systematically overstates**
production routing, which steps one tier.

| C4 pair | Rationale |
|---|---|
| Primary: mid-tier frontier ↔ next cheaper general-purpose tier | The realistic production decision |
| Secondary (≤ 1 cell): cheapest ↔ pro-tier | Bounds the maximum; reported **as a bound, not the result** |

**The concrete pairs are not yet chosen, and the lineup they were reasoned about has moved.**
`PS-2026-09-16` confirms that all eight OpenAI models in `PS-2026-09-15` still exist at unchanged
prices, but **none of them is a flagship model any more** — the current flagship line is
`gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`. "Tier-adjacent" has to be decided
against the lineup that will actually be used, which is open decision **C-a**. A pair must also
satisfy §12.0.1: if it spans a tokenizer boundary, no token delta from it is reportable.

Every C4 attempt records the exact model pair and `pricing_snapshot_id`. No C4 result is
reportable as a saving without both (Decision Ledger D011).

## 9. Cache control — unchanged, with §6.2 applied

6 dedicated cold-cache verification runs. Cached and uncached attempts are **never silently
mixed**. Every record carries `cache_state`. A run whose cache state cannot be determined is
**`INVALID`** (v1.0.0 said "void"; §6.2 gives that a name and a denominator).

**Automatic provider-side caching counts.** A run plan that declares "cold" does not stop a
provider serving a cache hit; the record reports what the provider reported.

## 10. Reproduction plan — unchanged, with §7.7 applied

10 runs, 5 repetitions each of the two strongest single-intervention results, executed by the
**Reproduction Agent**, which may not reproduce its own original run (`SEAT_REGISTRY.json`
invariant I10). Selection, ties and shortfall follow §7.7.

## 11. Pricing — **CHANGED: completeness is required and enforced**

### 11.1 Snapshot identity
Every attempt carries `pricing_snapshot_id`. A new snapshot gets a **new ID**;
`PS-2026-09-15` is never overwritten, amended or re-dated.

### 11.2 Required content
Per model **and per API plan actually used**: official vendor source URL · retrieval date ·
currency · billing unit · and rates for **standard input, output, cache read, cache write, cache
TTL tiers where the vendor has them, and any other applicable fee**.

A dimension the vendor does not have is recorded `not_applicable` **with the evidence for that
claim**. **A missing rate is never recorded as zero.**

### 11.3 Blocking preflight
A machine-readable completeness check runs **before execution** and **blocks** if any applicable
rate is missing for any model in the run plan. Completeness is judged against **what the provider
API can actually return as billable**, including automatic caching — not against what the run
plan declares.

### 11.4 Unpriceable usage
If real usage returns a billable quantity the snapshot does not cover, the attempt is marked
**`unpriceable`**, evidence is retained, and **the harness does not estimate**.

### 11.5 Token inclusion
The snapshot declares, per provider, whether cached and reasoning tokens are **included in** or
**additional to** the reported totals, so nothing is double-counted.

### 11.6 Cost completeness
Total cost includes **retries, failed calls, escalation targets, and any extra calls the
intervention itself makes**. An intervention's cost includes the cost of running it.

### 11.7 Blocked sources
Where a source or credential is unavailable, the row is recorded **`BLOCKED`** with what is
missing. **No price is invented.** No plaintext credential is requested or displayed.

### 11.8 Separation from calibration
**A complete pricing snapshot is not provider-native meter calibration.** Different gates.
Neither implies the other.

## 12. Meter — unchanged in substance

The provider-native `usage` field is ground truth. **`bytes / 4` and every uncalibrated estimator
are PROHIBITED as benchmark ground truth.** Full specification:
`METER_CALIBRATION_v1.1.0.md`, which restates v1.0.0's nine quantities and adds §11.5's
inclusion rules.

6 dedicated calibration runs compare the ATK Token Meter against the provider `usage` field.
**An offline accumulator check is a different question and is not a substitute.** Where a
provider's accounting cannot be compared like-for-like with another's, that is recorded, and
cross-provider token deltas from it are **not reportable** — only cost and cost per successful
task, and only with the pairing and the snapshot id stated.

### 12.0.1 The comparability bar also applies WITHIN a provider

Verified from Anthropic's own documentation while building `PS-2026-09-16`:

> *"Claude 4.7 and later models and Claude Mythos Preview use a newer tokenizer… This tokenizer
> produces approximately 30% more tokens for the same text… Claude Sonnet 4.6 and earlier models
> use the previous tokenizer."*

So a token-count delta measured across that boundary — Haiku 4.5 against Opus 5 or Sonnet 5, for
instance — carries **roughly 30% that has nothing to do with any intervention**. v1.0.0's rule
barred cross-*provider* token deltas; that was too narrow. **A token delta is reportable only
between models sharing a tokenizer.** Cost and cost per successful task remain reportable across
the boundary, because the unit there is money.

Each model in the pricing snapshot records its tokenizer generation, and any C4 pair spanning a
tokenizer boundary must state it wherever a token figure from that pair appears.

### 12.0.2 Token inclusion is a per-provider fact, not arithmetic

Also found while building `PS-2026-09-16`, and it had already produced a bug in the harness:
providers disagree about whether cached tokens sit **inside** the reported input total or
**beside** it. OpenAI and DeepSeek report them as **included**; Anthropic reports them as
**additional** — its pricing page carries an example with `input_tokens: 105` against
`cache_read_input_tokens: 7123`.

The meter previously treated `cached > input` as an error, encoding one convention as if it were
arithmetic. On a cache-heavy Anthropic attempt that either raises or, if an adapter folds the
fields to avoid raising, misprices by the size of the cache — **21% of the example call above**.

The convention is therefore **declared per model in the snapshot with the vendor sentence as
evidence**, and the meter applies the declaration. **An undeclared model is refused**, because a
default is a wrong answer for whichever half of the providers it does not match.

### 12.1 Evidence contract — **NEW**

Every scored attempt carries evidence that is **produced by the harness, never asserted by the
agent under test**:

| Evidence | Source | Rule |
|---|---|---|
| Static facts (valid symbols, catalogs, rosters) | derived from the **frozen corpus** at the frozen hash | never from the model's output |
| Tool calls | the **runner's own audit log** | never from the model's self-report |
| Turns | captured by the runner | `len(turns)` must equal the turn count; a short or reordered transcript is `INVALID` |
| Corpus integrity | hash before and after, or a read-only mount | a modified corpus fails the attempt |

**Required evidence that is missing, empty, wrongly typed, or from the wrong run is `INVALID`,
never a pass.** Emptiness is a content check, not a type check: `{}` and `[]` fail closed.

Evidence must be **treatment-neutral**: it may not leak the candidate name, the routed model, the
condition, or any usage figure into the judge's packet. The answer key is **never** mounted for
the agent under test.

## 13. Versioning and refusal — **NEW**

Every task file, answer key, scoring spec, packet and run record carries its methodology version.
The scorer and the runner **refuse** a packet or record whose version is absent, unrecognised, or
incompatible with the rules they implement. Silent cross-version scoring is prohibited: it is how
a v1.0.0 relative floor would survive into a v1.1.0 result.

## 14. Evidence manifest — unchanged, extended

Recorded per attempt: repository URL · exact commit SHA (never a branch) · ATK branch ·
dependency/environment manifest · container digest **and the self-derived image content hash** ·
task set version + hash · **answer key hash** · **scorer hash** · **config hash** ·
prompt/config hash · model/provider/version · `pricing_snapshot_id` · raw run id + path ·
result commit · reproduction instructions.

`task_set_hash`, `answer_key_hash`, `scorer_hash` and `config_hash` are **distinct**. No hash may
be computed over a manifest that contains itself.

## Declared stop conditions — unchanged, extended

Execution halts and the failure is **recorded, not improvised around**, if: benchmark credentials
are unavailable · token accounting is incomparable across conditions · the environment cannot be
pinned by digest · a candidate fails security review · quality cannot be measured for a workload ·
cache state cannot be determined · provider pricing changes mid-run without a snapshot boundary ·
**the pricing preflight blocks** · **required evidence is missing or empty** · **a packet's
methodology version cannot be resolved**.

## Conflict of interest — unchanged

`rtk` and `headroom` are both Lab subjects and ATK integration candidates. Mitigations, all
pre-registered: quality floors fixed before results; the Quality Judge scores before seeing cost
and never sees candidate identity; the Reproduction Agent is independent of the original run; the
Red Team owns LG8 and may not have authored the work. **A result favourable to an ATK integration
candidate is the one most in need of reproduction, not the one most ready to publish.**

## Immutability of this file, once signed off

Same rule as v1.0.0: no result may change it. A necessary change creates
`METHODOLOGY_v1.2.0.md` as a **new file**. Never overwrite, never edit in place.

**Until an independent reviewer signs this off, it is a draft and no run may cite it.**

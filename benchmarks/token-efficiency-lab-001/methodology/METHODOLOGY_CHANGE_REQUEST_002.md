# Methodology Change Request 002 — run-plan unit and its cost consequence

**Raised:** 2026-09-16 · **Against:** `METHODOLOGY_v1.0.0.md` §5 · **By:** methodology-reviewer
**Status:** **OPEN — awaiting Editor-in-Chief ratification.**
**Blocks:** the run-plan-mapping freeze gate (recorded **PENDING**, not PASS).
**Does NOT block:** producing the rest of the freeze candidate.

## What is missing from the frozen text

§5 allocates 100 runs as workload × condition × repetitions. **It never says what a run is.**
That was invisible while no task set existed. With 17 tasks it is unavoidable, because the two
readings give different experiments and different bills.

| Reading | Consequence |
|---|---|
| **A run = one task attempt** | **Impossible.** C0 has 15 runs for 17 tasks. Some task gets no baseline. |
| **A run = one (workload, condition, repetition) unit, attempting every task in that workload** | Fits exactly. 78 experimental + 22 guardrail = **100**, allocation untouched |

The arithmetic rules out the first reading. It does **not** by itself select the second.

**Correction (external adversarial review, 2026-09-17).** This request previously said "the
arithmetic decides that", and that was an overstatement of what arithmetic can do. Arithmetic
establishes only that a run is not a single task attempt. Reading 2 additionally assumes *every
task, in every applicable condition, three times* — full factorial coverage. That is a **design
choice**, and there are cheaper designs that also fit 100 runs (see option 5 below). §5.1 adopts
reading 2 because it is the strongest design, not because it is the only one that fits.

The choice of research unit therefore **is** on the table, and is the Editor-in-Chief's to make.

## What this request is actually asking

**Ratify the cost consequence, which the Editor-in-Chief has not seen.**

| Condition | Runs | Task attempts |
|---|--:|--:|
| C0 | 15 | 51 |
| C1 | 6 | 24 |
| C2 | 12 | 42 |
| C3 | 6 | 18 |
| C4 | 15 | 51 |
| C5 | 9 | 33 |
| C2+C4 | 9 | 33 |
| C3+C4 | 6 | 18 |
| **Experimental** | **78** | **270** |
| Reproduction / cache / meter | 22 | **not expanded — see correction below** |
| **Total** | **100** | |

**270 task attempts across the 78 experimental runs, a mean of 3.46 attempts per experimental
run.**

**Correction (external adversarial review, 2026-09-17). The previous version of this paragraph
multiplied the whole budget by 3.46, and that figure does not carry. Four things were wrong:**

1. **3.46 is an experimental-subset ratio, not a project ratio.** 270 ÷ 78 uses only the
   experimental runs. The other **22 guardrail runs** (reproduction, cache control, meter
   calibration) were never expanded into attempts at all, yet $51–94 covered all 100 runs. A
   subset's ratio was applied to the whole.
2. **270 is not the project's total attempts.** It is the experimental total. The project total
   is 270 + (however many attempts the 22 guardrail runs expand to), and that number has not
   been computed. If reproduction expands into a workload suite it rises further.
3. **An attempt-count multiplier is not a dollar multiplier.** Cost depends on context length,
   per-workload call volume, model price, cache state, retries and intervention overhead, none
   of which is uniform across attempts. Workload E accumulates context across 16 turns; a B
   attempt does not. Multiplying attempts to get dollars assumes every attempt costs the same,
   and they demonstrably do not.
4. **8–16 hours does not scale by the same factor either.** Wall time depends on parallelism,
   rate limits, the multi-turn dependencies in D and E, and human review time.

**As a counter-example only, not a new quote:** if the 22 guardrail runs stayed at one attempt
each and every attempt cost the same, the ratio would be (270 + 22) ÷ 100 = **2.92**, not 3.46.
That is not a better estimate — it rests on the same false uniformity assumption. It is here to
show that 3.46 is not forced by the counts.

**What is actually established:** the experimental workload is **270 task attempts**, up from an
implied 78 under the old reading. **The dollar and wall-time consequences are NOT established**
and must not be quoted. Producing them needs a per-workload, per-condition estimate of calls,
context length and price — which is work item 1 below, and is a precondition for ratifying any
option here on cost grounds.

## Why it is being raised rather than absorbed

The allocation is genuinely unchanged — no cell added, removed, renamed or re-weighted, no task
dropped. But a **3.46× increase in task attempts** that appears only as an inference from a
definition is exactly the kind of thing that should be ruled on before it is spent, not
discovered in an invoice. (The earlier wording called this a cost multiplier. It is an attempt
multiplier; see the correction above.)

## Alternatives

**All counts below are EXPERIMENTAL TASK ATTEMPTS on one consistent basis.** The earlier version
of this table mixed bases — 270 and 180 were experimental attempts while ~117 and 100 silently
included guardrails — so the columns could not be compared with each other. Corrected after
external review. Guardrail runs are listed separately because they are the same 22 under every
option.

| # | Option | Experimental attempts | Guardrails | What it costs you |
|---|---|--:|--:|---|
| **1** | **Ratify as proposed.** Every task, every applicable condition, 3 repetitions | **270** | 22 runs | The most expensive. Buys full coverage and within-workload variance |
| 2 | One **designated task per workload** per run; others only under C0 | **~117** | 22 runs | **Drops the within-workload variance the repetitions exist to measure.** The designated task silently becomes the workload |
| 3 | Reduce repetitions from 3 to 2, keep full task coverage | **180** | 22 runs | **Changes the frozen allocation** — needs its own change request. 2 repetitions supports even less than 3 |
| 4 | Keep 100 attempts, **shrink the task set** | **100** | 22 runs | Discards tasks four seats built and attacked. Not recommended |
| **5** | **Staged: full task coverage, single interventions only, 1 repetition first** | **73**, then decide | 22 runs | **Cheapest that keeps the whole task set.** Added after external review — it was missing, and its absence made option 1 look better than it was |

### Option 5 in full — added after external review

The original table offered only "run everything" or "throw away tasks", and argued against
shrinking on the grounds that four seats had built and attacked the task set. **That was a sunk
cost argument, and it should not have been in a decision document.** Keeping the task set and
paying for every attempt in this round are two different things; the tasks stay in the repository
either way.

**Stage 1 — 73 experimental attempts.** Drop the two combined conditions (219 attempts), then run
each task once per applicable condition instead of three times: 219 ÷ 3 = **73**. All 17 tasks,
C0 and every applicable single intervention. Guardrails unchanged.

**What stage 1 can and cannot deliver.** It can answer: does the harness execute end to end
against a real provider, do the interventions produce a measurable token difference in the
expected direction, and what does an attempt actually cost. It **cannot** support
non-inferiority, a stable ranking, or any variance claim — **one observation per cell has no
variance at all**, and §7.8's limits bind harder, not less.

**Stage 2 is pre-registered, not chosen afterwards.** The rule for adding repetitions, combined
conditions or a confirmatory run is written down **before** stage 1 executes. Data that has been
looked at may not be pooled into a result claimed as independent confirmation; a confirmatory
stage uses fresh attempts.

Two further designs exist and are also cheaper than option 1: a fixed-budget **incomplete block**
design pairing conditions within workloads, and **one prioritised hypothesis** run properly with
the remaining tasks kept as offline regression. Both need the same pre-registered sampling and
stopping rules. The choice is not binary.

## Recommendation

**Option 5, then option 1 if stage 1 justifies it** — changed from option 1 after external review.

Option 1 remains the strongest design and the right end state. What changed is the claim that it
had to be bought in one purchase: with the dollar figures withdrawn as unestablished, ratifying
the most expensive option on an unquantified budget is not a decision this document can support.
Stage 1 produces the per-attempt cost measurement that would make option 1's price knowable, and
it does so without discarding a single task.

If stage 1 is not acceptable, option 1 is the honest full-coverage choice; option 2 is the
fallback if the budget will not carry it, and its cost is measurement quality, which must be
stated in any result derived from it.

## Work items before any option can be ratified on cost

1. **Per-workload, per-condition cost model.** Expected calls, context length, cache state and
   price per attempt, so an attempt count can become a dollar range. **Blocked** on the three
   BLOCKED pricing rows.
2. **Expand the 22 guardrail runs into attempts.** They are one third of the run budget and have
   never been counted in attempts.
3. **Re-derive the wall-time estimate** from parallelism and rate limits rather than by scaling
   the old one.

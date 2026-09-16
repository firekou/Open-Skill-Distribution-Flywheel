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

Only the second reading works, so `METHODOLOGY_v1.1.0.md` §5.1 adopts it. This request is not
asking which reading to take; the arithmetic decides that.

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
| Reproduction / cache / meter | 22 | per §9, §10, §12 |
| **Total** | **100** | |

**270 task attempts, a mean of 3.46 per run.** Every previous cost figure in this repository
assumed one attempt per run. On the same assumptions **$51–94 becomes roughly $177–325**, and the
8–16 hour execution estimate scales similarly.

## Why it is being raised rather than absorbed

The allocation is genuinely unchanged — no cell added, removed, renamed or re-weighted, no task
dropped. But a 3.46× cost multiplier that appears only as an inference from a definition is
exactly the kind of thing that should be ruled on before it is spent, not discovered in an
invoice.

## Alternatives, with their costs

| # | Option | Runs | Attempts | What it costs you |
|---|---|--:|--:|---|
| **1** | **Ratify as proposed.** Full coverage: every task in every applicable condition | 100 | 270 | ~3.46× the earlier estimate |
| 2 | One **designated task per workload** per run; the others run only under C0 | 100 | ~117 | Cheapest, and it **drops the within-workload variance** the repetitions exist to measure. The designated task becomes the workload |
| 3 | Reduce repetitions from 3 to 2 and keep full task coverage | ~52+22 | 180 | **Changes the frozen allocation** — needs its own change request, and 2 repetitions supports even less than 3 |
| 4 | Keep 100 attempts and **shrink the task set** to fit | 100 | 100 | Discards tasks that four seats built and attacked. Not recommended |

**Recommendation: option 1.** It is the only one that preserves both the frozen allocation and
full task coverage. Option 2 is the honest fallback if the budget will not carry it, and its cost
is measurement quality, which should be stated in any result derived from it.

## What is NOT being requested

No change to the allocation, the conditions, the workloads, the repetition count, the
zero-tolerance criteria, or any floor. No task is selected, renamed or dropped. If the ruling is
that the budget cannot carry option 1, the answer is a further change request — **not a quiet
re-scoping**.

## Consequence of no ruling

The run-plan-mapping gate stays **PENDING**. A freeze candidate can still be produced and
reviewed; it cannot be declared execution-ready, because the size of the experiment it authorises
would be unratified.

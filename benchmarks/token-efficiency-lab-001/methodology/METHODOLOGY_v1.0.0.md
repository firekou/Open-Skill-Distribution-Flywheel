# Token Efficiency Lab 001 — Methodology v1.0.0 (FROZEN)

**Status:** **FROZEN**
**Version:** `1.0.0`
**Frozen at:** 2026-09-16
**Authority:** Editor-in-Chief / ChatGPT review, LG1 granted
**Gate owner:** `methodology-reviewer` (`agents/SEAT_REGISTRY.json`, LG1)

> **This document is immutable.** No result, at any stage, may change it. If a change becomes
> necessary, create `METHODOLOGY_v1.1.0.md` (or v2.0.0) as a **new file**. Never overwrite,
> never edit in place. The superseding version must state what changed and why, and any run
> executed under v1.0.0 remains attributed to v1.0.0.

---

## 1. Research question — FROZEN

**Where do Agents waste tokens, and which interventions reduce total task cost without
materially reducing task success?**

## 2. Hypotheses H1–H4 — FROZEN

| ID | Hypothesis | Pre-registered direction |
|---|---|---|
| **H1** | Large MCP/tool schemas create measurable fixed context overhead | Overhead grows with tool count; deferred exposure or a code-execution pattern reduces it |
| **H2** | Raw intermediate tool results create avoidable variable overhead | Filtering/compression reduces total tokens at an acceptable quality cost |
| **H3** | Model misrouting creates hidden cost via overpowered selection or retry/escalation | A complexity-aware route beats always-frontier on cost at equal quality |
| **H4** | Context accumulation creates avoidable repeated-token cost | Compaction/clearing reduces tokens in long sessions |

These are Lab hypotheses, distinct from the strategic hypotheses H001–H010. They are **not ATK
claims** until TESTED and VERIFIED. **Pre-registered null results are publishable.**

## 3. Workloads A–E — FROZEN

| ID | Workload | Why it is in the set |
|---|---|---|
| **A** | Repository / code analysis | Many tool calls, large file payloads |
| **B** | Long-document extraction | Single large context, low tool count |
| **C** | Multi-source research | Many small results, high aggregation |
| **D** | MCP-heavy multi-tool task | Maximum schema overhead — the H1 probe |
| **E** | Long multi-turn agent workflow | Context accumulation — the H4 probe |

## 4. Conditions C0–C5 — FROZEN

| ID | Condition | Tests |
|---|---|---|
| **C0** | Baseline, no intervention | — |
| **C1** | Deferred/reduced tool-schema exposure (code-execution pattern) | H1 |
| **C2** | Tool-result filtering / compression | H2 |
| **C3** | Context compaction / clearing | H4 |
| **C4** | Routing by task complexity, **tier-adjacent pairs** (§7) | H3 |
| **C5** | Third-party optimisation tool, **only after LG2 pass** | H2 |

## 5. 100-run matrix — FROZEN

| Condition | Workloads | Reps | Runs | Applicability reasoning |
|---|---|--:|--:|---|
| C0 baseline | A, B, C, D, E | 3 | **15** | Every workload needs its own baseline |
| C1 schema deferral | A, D | 3 | **6** | Only A and D carry enough tools for schema overhead to exist |
| C2 result filtering | A, B, C, D | 3 | **12** | E's cost is accumulation, not result size |
| C3 compaction | B, E | 3 | **6** | Only long-context workloads accumulate |
| C4 routing | A, B, C, D, E | 3 | **15** | Routing applies everywhere |
| C5 third-party tool | A, B, D | 3 | **9** | Where the LG2-passed tools claim to operate |
| | | | **63** | |
| C2+C4 combined | A, B, D | 3 | **9** | Only after both singles report |
| C3+C4 combined | B, E | 3 | **6** | Only after both singles report |
| | | | **78** | |
| Reproduction | 2 strongest single results | 5 | **10** | LG6 — independent repeat by a different seat |
| Cache-state control | Cold-cache verification | — | **6** | Guardrail (§9) |
| Meter calibration | Meter vs provider `usage` | — | **6** | Guardrail (§8) |
| | | | **100** | |

**Freeze rule:** this allocation is immutable. A cell that cannot execute is recorded as a
**failed cell with a reason** — never silently reallocated, never replaced with a substitute.

## 6. Quality floors — FROZEN, pre-registered

| Workload | Success criterion | Quality floor | Scored by |
|---|---|---|---|
| A | Named functions/symbols correctly identified | ≥ 95% of baseline's correct set, **zero fabricated symbols** | Quality Judge |
| B | Required fields extracted | ≥ 97% exact-match on a pre-built answer key | Quality Judge |
| C | Claims traceable to a retrieved source | 100% traceable, ≥ 90% of baseline's covered facts | Quality Judge |
| D | Correct tool selected and correct final answer | ≥ 95% task success, zero wrong-tool invocations | Quality Judge |
| E | Task completed, earlier-turn constraints honoured | ≥ 95% completion, **zero constraint violations from forgotten context** | Quality Judge |

Any zero-tolerance criterion fails the cell outright regardless of percentages. **The Quality
Judge scores before seeing cost.** Lower tokens with unacceptable quality is a **failed
optimisation**, not a trade-off.

## 7. C4 tier-adjacent routing design — FROZEN

Verified pricing (`PS-2026-09-15`) shows the gap between **tier-adjacent** models is ~11×,
while cheapest-vs-pro-tier reaches 257×. Pairing across five tiers would measure a real number
that **systematically overstates** production routing, which steps one tier.

| C4 pair | Rationale |
|---|---|
| Primary: mid-tier frontier ↔ next cheaper general-purpose tier | The realistic production decision |
| Secondary (≤ 1 cell): cheapest ↔ pro-tier | Bounds the maximum; reported **as a bound, not the result** |

Every C4 run record carries the exact model pair and `pricing_snapshot_id`. No C4 result may be
reported as a saving without both (Decision Ledger D011).

## 8. Meter calibration — FROZEN

6 dedicated runs compare the ATK Token Meter against the provider-native `usage` field.

**`bytes / 4` and any other uncalibrated estimator are PROHIBITED as benchmark ground truth.**
Full specification: `methodology/METER_CALIBRATION_v1.0.0.md`.

If a provider's token accounting cannot be compared like-for-like with another's, that must be
recorded explicitly, and cross-provider deltas from it are not reportable.

## 9. Cache control — FROZEN

6 dedicated cold-cache verification runs. **Cached and uncached runs must never be silently
mixed.** Every run record carries `cache_state`. A run whose cache state cannot be determined
is void, not "probably cold".

## 10. Reproduction plan — FROZEN

10 runs, 5 repetitions each of the 2 strongest single-intervention results, executed by the
**Reproduction Agent**, which may not reproduce its own original run (`SEAT_REGISTRY.json`
invariant I10). Tolerance and procedure: `reproduction/` at execution time.

## 11. Pricing snapshot requirement — FROZEN

Every run record carries `pricing_snapshot_id`. Token counts are physical; prices move. A later
price change must not retroactively alter a measured result. Active snapshot: **`PS-2026-09-15`**
(`evidence/PRICING_SNAPSHOT_2026-09-15.md`).

## 12. Evidence manifest — FROZEN

Recorded per experiment:

repository URL · exact commit SHA (never a branch) · ATK branch · dependency/environment
manifest · container digest · task set version + hash · prompt/config hash · model/provider/
version · `pricing_snapshot_id` · raw run id + path · result commit · reproduction instructions.

---

## Declared stop conditions — FROZEN

Execution halts and the failure is **recorded, not improvised around**, if: benchmark
credentials are unavailable; token accounting is incomparable across conditions; the
environment cannot be pinned by digest; a candidate fails security review; quality cannot be
measured for a workload; cache state cannot be determined; or provider pricing changes
mid-run without a snapshot boundary.

## Conflict of interest — FROZEN

`rtk` and `headroom` are both Lab subjects and ATK integration candidates. Mitigations, all
pre-registered: quality floors fixed before results; Quality Judge scores before seeing cost;
Reproduction Agent independent of the original run; Red Team owns LG8 and may not have authored
the work. **A result favourable to an ATK integration candidate is the one most in need of
reproduction, not the one most ready to publish.**

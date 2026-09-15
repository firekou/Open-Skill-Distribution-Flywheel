# ATK Execution Status

**Date:** 2026-09-15 · **Branch:** `main` · **Updated:** after Phase D
**Position: mandatory review stop. Lab 001 execution not started.**

---

## ⚠️ Blocker to resolve before any gate answer is unambiguous

**RESOLVED by review decision 2026-09-15.** Doctrine gates are now **DG0–DG10**; Lab gates are
**LG0–LG9**. Bare `G4` is no longer written anywhere. The collision below is kept as the record
of why the namespaces exist.

**Previously: two different gate systems were both labelled G0–G9/G10.**

| Source | Sequence |
|---|---|
| `EXECUTION_DOCTRINE.md` (now **DG**) | G0 Question → G1 Hypothesis → G2 Signal → G3 Research+counterevidence → G4 Test Design → G5 Execution → G6 Verification → G7 Decision → G8 Distribution → G9 Demand Feedback → G10 Productization |
| `workflows/TOKEN_EFFICIENCY_LAB_001_TEAM.md` (now **LG**) | G0 claim → G1 methodology frozen → G2 repo/security → G3 environment → G4 execution complete → G5 quality floor → G6 reproduction → G7 Verify state → G8 Red Team → G9 publish |

They are not the same ladder. "G4" means *Test Design* in one and *Execution complete* in the other.
`reports/TOKEN_EFFICIENCY_LAB_001_PRECHECK.md` §8 uses the **Lab** set.

**Renaming was approved and applied 2026-09-15.** Both source files now carry an explicit
namespace rule.

---

## 1. Current gate

| Ladder | Position |
|---|---|
| **Doctrine** | **DG4 Test Design — COMPLETE.** DG5 Execution is **blocked** by the mandatory review stop. |
| **Lab 001** | **LG0 claim registered — COMPLETE.** **LG1 methodology freeze requested, NOT granted.** |

Both ladders are waiting on the **same single event**: Editor-in-Chief / ChatGPT review.

---

## 2. Completed — and independently checkable

| Work | Artifact | Check |
|---|---|---|
| Phase A — roles as contracts | `agents/SEAT_REGISTRY.json`, 71 seat files, `tools/validate_seats.py` | `python3 tools/validate_seats.py` → 71 seats, 10 departments, 14 invariants pass |
| Phase B — S3 Top 30 | `reports/TOP30_R3.md` | 10 Talk / 10 Run / 10 Integrate, each with an evidence state |
| Phase C — Lab precheck | `reports/TOKEN_EFFICIENCY_LAB_001_PRECHECK.md` | 100-run matrix sums to 100; quality floors pre-registered |
| Candidate version pinning | `benchmarks/token-efficiency-lab-001/environment/PINS.txt` | 8 candidates pinned to exact commit SHAs |
| Discovery registry | `registry/materials.json` | 188 materials, 6 categories, schema validates |
| Prior research | `RESEARCH_REPORT.md`, `reports/BENCHMARK_R2_00{1,2}.md` | — |

**Highest-value verified output so far:** primary-source reads that **corrected two of ATK's own
published figures** (`TOP30_R3.md` §1), and the discovery that `rtk`'s savings accounting is
disputed in 14 of its own issues.

---

## 3. Planned but NOT verified — the honest gap

Written as a document ≠ done. Every row below exists **only as a specification**.

| Area | Written | Actually verified |
|---|---|---|
| Lab 001 hypotheses H1–H4 | 4 hypotheses | **0 runs. Nothing TESTED.** |
| Lab directory layout | 8 dirs in precheck §5 | **1 of 8 exists** (`environment/` only) |
| Security review | Full scope, 8 candidates, risk-ranked | **NOT PERFORMED** (LG2 open) |
| Quality floors | 5 workloads, zero-tolerance criteria | Defined, **never applied** |
| 100-run matrix | Allocated cell by cell | **Never executed** |
| Agent organization | 71 seat contracts, invariants enforced | **No seat has executed a real task.** Instantiated, unexercised |
| Magazine | 10 desks, 8 formats specified | **0 articles, 0 content packages published** |
| Demand Sensor | `DEMAND_SENSOR_SPEC.md` | **No instrumentation, no data, no tracking IDs issued** |
| ATK Verify | Standard + 5 states | **Nothing in the repo is above OBSERVED** |
| Content Package schema | Named in growth plan §15 | **Not created** |
| H003 / H004 / H005 | Hypotheses stated | **No test designed for any of them** |

> ~~The ~100× model price gap~~ **RESOLVED 2026-09-15.** Verified from primary pricing pages and
> **corrected: 11.4× like-for-like**, not ~100×. See E007/E015 and
> `benchmarks/token-efficiency-lab-001/evidence/PRICING_SNAPSHOT_2026-09-15.md`.

---

## 4. In progress

**Nothing is mid-execution.** Phase D completed 2026-09-15; everything else is blocked at the
review stop.

| Ledger | Data rows | State |
|---|--:|---|
| `ledgers/HYPOTHESIS_LEDGER.md` | 10 | Populated by GPT. **Confidence column unchanged by Claude** |
| `ledgers/EVIDENCE_LEDGER.md` | **14** | ✅ Populated from Phases A/B/C |
| `ledgers/DECISION_LEDGER.md` | **10** | ✅ Populated — **2 marked STRATEGIC BET** |

Evidence and decisions from Phases A–C are now traceable. Two decisions (D007 Measurement &
Trust priority, D008 strategic-conflict rejections) carry no demand data and are labelled bets
rather than findings.

## 5. Hypothesis confidence — as recorded, unchanged

Read from `ledgers/HYPOTHESIS_LEDGER.md`. **Not modified.** Confidence changes require an
evidence-backed proposal and Editor-in-Chief approval.

| ID | Hypothesis | Confidence | Status |
|---|---|---|---|
| H001 | Agent scale increases demand for Measurement / Attribution / Trust | **H1 Signal** | ACTIVE |
| H002 | Token Cost is a strong wedge into Agent Resource Intelligence | **H1 Signal** | ACTIVE |
| H003 | Technical Intelligence Magazine as low-CAC distribution/trust engine | **H0 Idea** | ACTIVE |
| H004 | Agent-native organization increases verified output per human hour | **H0 Idea** | ACTIVE |
| H005 | Verification gains value as AI generation gets cheaper | **H0 Idea** | ACTIVE |
| H006 | Agent Unit Economics becomes a management discipline | **H0 Idea** | WATCH |
| H007 | Cost per successful task beats raw token price | **H0 Idea** | WATCH |
| H008 | Quality-adjusted routing beats cheapest routing | **H0 Idea** | WATCH |
| H009 | Machine-readable Trust Receipts useful in enterprise Agent ops | **H0 Idea** | WATCH |
| H010 | Human + Agent demand signals beat editorial intuition | **H0 Idea** | WATCH |

**Note for the review, not a change:** Phases B/C produced evidence bearing on H001, H002 and
H005 — including **counterevidence** against H002 (platform vendors commoditising routing). None
of it is in the Evidence Ledger yet, so **no confidence proposal can be justified until Phase D
runs.** This is stated as a sequencing fact, not as a request to upgrade anything.

---

## 6. Last step GPT requested

`CLAUDE_EXECUTION_START.md` defines **Phase A → B → C → D → mandatory review stop**.

| Phase | State |
|---|---|
| A Operating system | ✅ complete |
| B S3 Top 30 | ✅ complete |
| C Lab 001 precheck | ✅ complete |
| **D Ledgers** | ❌ **not started** |
| Mandatory review stop + seven Forward-Motion questions | ⏸ cannot be entered until D is complete |

---

## 7. The single most reasonable next gate

**The mandatory review stop — now.** All four phases in `CLAUDE_EXECUTION_START.md` are
complete. The seven Forward-Motion answers are below.

The review decides **LG1 methodology freeze: grant or refuse.** Nothing further proceeds
without it.

**Explicitly NOT next:** Lab 001 execution (LG2 security review onward).

## Open items for the Editor-in-Chief

1. **Disambiguate the two G0–G9 gate namespaces** (top of this document). Claude flagged, did not change.
2. ~~Resolve the ~100× price gap~~ — **DONE 2026-09-15.** Corrected to 11.4× like-for-like.
3. **Confirm Phase D is authorised to proceed** before the review stop, or say the stop happens now without it.


---

## Seven Forward-Motion answers (`EXECUTION_DOCTRINE.md`)

### 1. What uncertainty was reduced?

Three things moved from assumption to observation:

- **What the two market leaders actually claim.** ATK had been working from secondary
  paraphrases. Both primary sources are materially more careful (E001, E002).
- **Whether the biggest token tool's numbers are trusted.** They are disputed by its own users,
  14 times, with a >10,000× over-count repro (E003).
- **Whether two candidate Scout components are usable.** One conditionally, one not (E009, E010).

### 2. Which hypothesis changed confidence?

**None — Claude may not change confidence.** One upgrade is *proposed*: **H005 H0 → H1 Signal**.
Three explicit non-upgrades are recorded, including for both ACTIVE hypotheses. See
`ledgers/HYPOTHESIS_LEDGER.md`.

### 3. What new evidence was produced?

14 evidence entries. 9 OBSERVED, 4 REPORTED, 1 recorded as a LIMITATION. **Nothing is TESTED or
above** — no third-party code was executed.

### 4. What failed or contradicted us?

- **ATK published two inflated figures** by trusting search summaries instead of reading files
  one HTTP request away. The failure occurred in the repository that defines the evidence ladder.
- **Counterevidence against both ACTIVE hypotheses.** E008 against H001 (every measurement/trust
  project is small); E005 against H002 (platform vendors reported to give routing away free).
- **A query failure recorded as a failure** (E013): two searches of `headroom`'s issues returned
  nothing despite 643 open issues. That is not a clean bill of health.
- **Three operations blocked by environment policy**: repository settings write, branch
  deletion, and the GitHub commits API. SHAs were obtained via `git ls-remote` instead.

### 5. What decision is now justified?

10 decisions recorded. 8 evidence-backed; **2 labelled STRATEGIC BET** (D007, D008) because they
rest on reasoning rather than demand data.

**D010 is now closed** — the price gap was verified and corrected. **D011 is new**: state the
price gap as a range with its pairing, never as a single multiple.

### 6. What is the single next gate?

**LG1 — methodology freeze.** Grant or refuse. If refused, name the condition, allocation or
quality floor to change now, while changing it is still free; after LG1 a change voids the runs.

### 7. What requires Editor-in-Chief / ChatGPT review?

1. **LG1 grant or refusal** — the blocking decision
2. **H005 H0→H1 proposal**, and the three non-upgrades
3. **Two STRATEGIC BETs (D007, D008)** — both concern ATK's core commercial premise and neither
   has demand data
4. **The duplicate G0–G9 gate namespaces** — flagged, not changed
5. **E005 is REPORTED and load-bearing** — if platform vendors genuinely commoditise routing,
   H002's wedge narrows. Worth one hour of reading vendor documentation before the next cycle

# ATK Execution Status

**Date:** 2026-09-15 · **Branch:** `main` @ `3bd10a2` · **Purpose:** position confirmation only
**Nothing was executed, changed or re-planned to produce this document.**

---

## ⚠️ Blocker to resolve before any gate answer is unambiguous

**Two different gate systems are both labelled G0–G9/G10.**

| Source | Sequence |
|---|---|
| `EXECUTION_DOCTRINE.md` | G0 Question → G1 Hypothesis → G2 Signal → G3 Research+counterevidence → G4 Test Design → G5 Execution → G6 Verification → G7 Decision → G8 Distribution → G9 Demand Feedback → G10 Productization |
| `workflows/TOKEN_EFFICIENCY_LAB_001_TEAM.md` | G0 claim → G1 methodology frozen → G2 repo/security → G3 environment → G4 execution complete → G5 quality floor → G6 reproduction → G7 Verify state → G8 Red Team → G9 publish |

They are not the same ladder. "G4" means *Test Design* in one and *Execution complete* in the other.
`reports/TOKEN_EFFICIENCY_LAB_001_PRECHECK.md` §8 uses the **Lab** set.

This document writes **DG0–DG10** (doctrine) and **LG0–LG9** (lab) to stay unambiguous.
**Renaming them in the source files is an Editor-in-Chief decision, not a Claude one** — flagged, not changed.

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

> The single most load-bearing unverified item remains the **~100× model price gap**
> (`TOP30_R3.md` T10). It underpins the routing economics argument and is still REPORTED.

---

## 4. In progress

**Strictly: nothing is mid-execution.** Every started item is either complete or blocked at the
review stop.

**One assigned-but-unstarted item:** `CLAUDE_EXECUTION_START.md` **Phase D — Ledgers**.

| Ledger | Data rows | State |
|---|--:|---|
| `ledgers/HYPOTHESIS_LEDGER.md` | 10 | Populated by GPT (H001–H010) |
| `ledgers/EVIDENCE_LEDGER.md` | **0** | **Empty** |
| `ledgers/DECISION_LEDGER.md` | **0** | **Empty** |

Phases A, B and C produced evidence and decisions that were **never recorded in the ledgers**.
That is the gap between what the repo has done and what the repo can prove it has done.

---

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

**Complete Phase D, then enter the mandatory review stop.**

Phase D is the only remaining **unblocked** work in the entire plan. Everything else is
gated behind a review that the doctrine says cannot happen until the ledgers are maintained and
the seven Forward-Motion questions are answered.

It is also not busywork: Phases A–C generated evidence and decisions that currently exist only
inside reports. Until they are in the Evidence and Decision Ledgers, they are **not traceable**,
and the doctrine's own rule — *"a decision without traceable evidence must be marked STRATEGIC
BET"* — means ATK cannot presently distinguish which of its decisions are evidence-backed.

**Explicitly NOT the next gate:** Lab 001 execution (LG2 security review onward). It stays
blocked until the Editor-in-Chief grants LG1.

### Order

1. **Phase D** — populate the Evidence and Decision Ledgers from A/B/C; prepare, but do not
   apply, evidence-backed confidence proposals for H001 / H002 / H005
2. **Answer the seven Forward-Motion questions**
3. **STOP** for Editor-in-Chief / ChatGPT review
4. Review decides: **LG1 methodology freeze — grant or refuse**

---

## Open items for the Editor-in-Chief

1. **Disambiguate the two G0–G9 gate namespaces** (top of this document). Claude flagged, did not change.
2. **Resolve the ~100× price gap** (`TOP30_R3.md` §6 item 1, ~10 min) before approving any benchmark spend.
3. **Confirm Phase D is authorised to proceed** before the review stop, or say the stop happens now without it.

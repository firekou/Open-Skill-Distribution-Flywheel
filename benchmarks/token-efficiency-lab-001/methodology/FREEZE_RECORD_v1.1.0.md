# Freeze Record — Methodology v1.1.0

| | |
|---|---|
| **Gate** | LG1 (v1.1.0) |
| **Status** | **NOT FROZEN — DRAFT / REVIEW_PENDING** |
| **Version** | 1.1.0 |
| **Drafted** | 2026-09-16 |
| **Drafting seat** | `methodology-reviewer` |
| **Source commit** | `a8ca352dc64e792864f351f7775e2b21681b6390` |
| **Methodology SHA-256** | `f4327ca9ce7b61c88fd84c54e3eb3f91a564d986b38c567c8c58311e4a9c3436` |
| **Meter calibration SHA-256** | `726d193b8e24cc4825c151e41bef09dd0027988efce33bfa069bcafc71298113` |
| **Independent sign-off** | **NONE. Pending.** |
| **Freeze commit SHA** | **not assigned — nothing has been frozen** |

## This record exists to say NO

A freeze record whose only job is to record a freeze will, sooner or later, record one that did
not happen. This one records the opposite.

**v1.1.0 is not frozen.** The Editor-in-Chief approved the *revision direction* in Prompt 3.5
§3. That is not approval of this deliverable, and the two must not be conflated. Approval of a
direction plus a draft that follows it is still a draft.

## What is required before this may read FROZEN

| # | Requirement | Status |
|---|---|---|
| 1 | Independent Methodology Reviewer sign-off on the actual text | **PENDING** |
| 2 | `CR-002` ratified — the run-plan unit and its 3.46× cost consequence | **PENDING** |
| 3 | `TASK_SET_v1.1.0` frozen, with RT-01–RT-13 closed and re-verified | see `LAB_001_FREEZE_READINESS_V1_1.md` |
| 4 | A complete pricing snapshot, or an explicit ruling that a `BLOCKED` snapshot may be frozen alongside | **PENDING** |
| 5 | Red Team replay against the repaired artefacts, by a seat that did not author them | see the freeze-readiness report |
| 6 | Independent semantic verification of all 17 tasks | see the freeze-readiness report |

**Freeze and Pilot are decided separately.** Even a frozen v1.1.0 does not start a Pilot: that
additionally needs the new environment verified, a complete price list, credentials,
provider-native meter calibration, applicable candidate runtime and security status, and an
independent launch decision. **LG4 remains NO GO.**

## v1.0.0 is untouched

| | |
|---|---|
| `METHODOLOGY_v1.0.0.md` | `c1810b0481d1442937771c124c7c30668490470f00dcf71098bdf139ee7089bc` |
| `METER_CALIBRATION_v1.0.0.md` | `3ed9dac60aa537f3e37503cec2c6eb91c4abebcb746658369f534ac2e21a98aa` |

Both re-verified at the start and the end of this round. **v1.1.0 does not supersede, replace or
retire v1.0.0**, and no run executed under v1.0.0 is re-attributed. The original
`FREEZE_RECORD.md` and `METHODOLOGY_LOCK.json` are untouched and remain the record of the v1.0.0
freeze.

## Verification

```bash
cd benchmarks/token-efficiency-lab-001/methodology
sha256sum METHODOLOGY_v1.0.0.md METHODOLOGY_v1.1.0.md \
          METER_CALIBRATION_v1.0.0.md METER_CALIBRATION_v1.1.0.md
# v1.0.0  c1810b0481d1442937771c124c7c30668490470f00dcf71098bdf139ee7089bc
# v1.1.0  f4327ca9ce7b61c88fd84c54e3eb3f91a564d986b38c567c8c58311e4a9c3436
```

Any mismatch on a v1.0.0 line means the frozen document was altered and every run under it is
void. A mismatch on a v1.1.0 line means the draft moved after this record was written, which
invalidates any review already performed against it.

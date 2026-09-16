# Freeze Record — Methodology v1.1.0

| | |
|---|---|
| **Gate** | LG1 (v1.1.0) |
| **Status** | **NOT FROZEN — DRAFT / REVIEW_PENDING** |
| **Version** | 1.1.0 |
| **Drafted** | 2026-09-16 |
| **Drafting seat** | `methodology-reviewer` |
| **Source commit** | `a8ca352dc64e792864f351f7775e2b21681b6390` |
| **Methodology SHA-256** | `f4e5b65e204dd0a31cc3d04a639d5542c7aa49523d374da5f51bc0330e490774` |
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
# v1.1.0  f4e5b65e204dd0a31cc3d04a639d5542c7aa49523d374da5f51bc0330e490774
```

Any mismatch on a v1.0.0 line means the frozen document was altered and every run under it is
void. A mismatch on a v1.1.0 line means the draft moved after this record was written, which
invalidates any review already performed against it.

## Drafting amendments

This draft was amended three times while being drafted, each from a source read during the round,
each recorded in `METHODOLOGY_LOCK_v1.1.0.json`:

| Clause | Amendment | Source |
|---|---|---|
| **12.0.1** | The token-comparability bar extended to apply **within** a provider, after Anthropic's docs were found to state that Claude 4.7 and later use a tokenizer producing ~30% more tokens for the same text | `docs.claude.com/en/docs/about-claude/pricing` |
| **12.0.2** | Token inclusion declared per provider. The harness previously encoded the OpenAI/DeepSeek convention as arithmetic and would have raised or mispriced **every cache-heavy Anthropic attempt** — 21% of the vendor's own example call | same |
| **8** | Recorded that the C4 tier-adjacent pairs were reasoned about against an OpenAI lineup that has since moved; choosing the pairs is open decision **C-a** | `PRICING_SNAPSHOT_PS-2026-09-16.json` |

A draft is amended in place while it is a draft — that is what a draft is for, and hiding the
amendments would make the review harder rather than cleaner. **Once signed off, any further change
requires a new version file.** Any review performed against the earlier hash
`f4327ca9…` must be redone.

## Task-set binding (the outer record, not a self-reference)

The manifest lists artefacts and never hashes itself. **This record binds the manifest digest to
the commit**, which is the direction that avoids a circular attestation.

| | |
|---|---|
| `tasks/TASK_SET_v1.1.0/MANIFEST.json` digest | `b08d4f1fe9d4f6aacabae0c064b3aa1a664d5c3a0321391f348c9ee6b26811eb` |
| `task_set_hash` | `4954ee84cb61bc56d271ae45df4478312147373d486e58524a92126805184ea0` |
| `answer_key_hash` | `57ec5d50f82c0ec453a75d1c64c6a581d9ce884ef2c1d2a9cec738e86c0a252d` |
| `answer_key_scripts_hash` | `839b95af67db206b5e4d1ed7246e231c0875b5bad5d2a938ed91df08e4fe8d2f` |
| `scoring_spec_hash` | `887dcf10726ad2e23efb7449bc3d799b5922c3064474625dc8266d7583b09ac6` |
| `scorer_hash` | `e558aac2901e3970c1ac91bcf79e3ab10970153eb6cf2ce0734fcd956e5713bb` |
| `config_hash` (schema + harness modules) | `d2b324176db469b44f44e7e72a5b9eb269c47c49e949f68dda28c3ff9d13f152` |
| Files covered | 194, **unclaimed: none** |
| Artifact commit | recorded by the commit that carries this file; see `git log` |

**Still not frozen.** These hashes exist so a later freeze has something to bind, and so a
reviewer can tell whether anything moved between review and freeze. Recording a hash is not
freezing a set.

Verify:

```bash
python3 environment/harness/manifest.py verify \
  --task-set tasks/TASK_SET_v1.1.0 --env environment \
  --manifest tasks/TASK_SET_v1.1.0/MANIFEST.json
```

Exit 0 means every covered file matches, **and** the manifest's own recorded group hashes agree
with the files it lists — a doctored manifest used to pass this check and no longer does.

# PR #1 — Executor response to the fourth adversarial review

**PR:** https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/1 (draft, not merged)
**Branch:** `claude/atk-open-skill-distribution-96e4vv`
**Commit submitted for review:** `37a1dc155acb60494b2427252382c190a508a1b4`
**Reviewed code was:** `6d59acd39bd62f64b539b106f603e91876171e94`
**Review package was:** `401ea9a702b9dd061978aa868bc72d321435b936`

**Status of every fix below: `IMPLEMENTED_PENDING_REVIEW`.** Nothing here is marked verified or
closed. Only an independent reviewer can do that, and only against this exact head.

**Freeze and LG4 remain NO GO.** This response does not change the benchmark's BLOCKED state.

---

## Execution environment

| | |
|---|---|
| Python | 3.11.15 (the repository's target), host, **not** the LG3 container |
| `jsonschema` | 4.26.0, installed from the repository's vendored wheelhouse. **The real record validator ran in every command below. No stub anywhere in this table.** |
| Docker | **not used.** No image was rebuilt, so no image digest binds this code |
| Models | **none contacted.** No credential, no spend, no live provider |

**Both this response and the R4 review ran on host Python rather than the pinned container. Neither
of us has verified this code under LG3 conditions.**

---

## Findings

### R4-02 — integrity manifest stale, and scoped to exclude the code that produces results

| | |
|---|---|
| **Reproduced** | Yes, twice over |
| **Root cause** | Two distinct defects sharing one row. (a) The committed `MANIFEST.json` had not been regenerated after `run_record_schema.json` and `judge.py` changed. (b) `CONFIG_FILES` was a **hand-maintained list** that never included `aggregate.py`, `finalize.py` or `runner.py` — every module between a scored packet and a published cell. A hand-maintained list of what to protect goes stale the first time someone adds a file, and nothing says so |
| **Observed on `6d59acd`** | committed manifest `verify → ok=false` (`config`: `run_record_schema.json`; `scorer`: `harness/judge.py`). Fresh manifest over a modified `aggregate.py` with `select_strongest` overridden to return a fixed winner → **`ok=true`** |
| **Fix** | `environment/harness/manifest.py`: the `execution` group is **discovered** from `harness/*.py`, with three exclusions named with reasons (`test_harness.py`, `test_judge.py`, `blind_smoke.py`). The "nothing unclaimed" rule the task set had now also covers the environment. `MANIFEST.json` regenerated |
| **Positive control** | untouched tree → `ok=true`; committed manifest verifies against the committed code |
| **Negative controls** | modified `aggregate.py` → `ok=false`, `execution.modified = ['harness/aggregate.py']`. A **new** `harness/*.py` → `ok=false`, `execution.added = [...]` |
| **Boundary check beyond the reported case** | coverage asserted for `aggregate.py`, `finalize.py`, `runner.py`, `judge.py`, `analyse.py`; execution group is **17 files** |
| **Not verified** | that the excluded three genuinely cannot affect a scored run — argued from their roles, not proven by execution |

### R4-03 — the documented dry-run path was broken by this branch's own change

| | |
|---|---|
| **Reproduced** | Yes |
| **Root cause** | R3-01 made `attempt_id` mandatory in the runner. `dryrun/PLAN.json` is a **committed input** and was never updated, so the documented path failed before executing anything. Only the separately generated golden fixture still worked — which is exactly why "the documented commands work" was too broad a claim |
| **Observed on `6d59acd`** | 10 plan items, **10 without `attempt_id`**; no `dryrun/RUN_PLAN.json`; runner exit 1 |
| **Fix** | `dryrun/PLAN.json` carries ids; `tools/make_dryrun_fixture.py` refuses a plan without them and writes `dryrun/RUN_PLAN.json`; `RUNBOOK.md` documents **both** paths and their expected exit codes |
| **Positive control** | the documented chain now runs: runner 10/10 → judge → finalize 10 → aggregate |
| **Expected-failure control** | aggregate exits **1**, and that is correct: the dry-run fixture's outputs are synthetic, so the attempts genuinely fail quality. This path proves the plumbing executes, not that anything scores well. The RUNBOOK now says so |
| **Not verified** | the containerised form of these commands. Host only |

### R4-04 — methodology lock document hash stale

| | |
|---|---|
| **Reproduced** | Yes — `METHODOLOGY_CHANGE_REQUEST_002.md` differed from the hash the lock recorded |
| **Root cause** | The document was edited in the round-1 response (the cost withdrawal) and the lock's `documents` map was not updated with it |
| **Fix** | Hashes refreshed, and **enforced**: `tools/delivery_check.py` exits 1 on any drift |
| **Control** | check passes now; it failed before the refresh |

### R4-05 — records from different builds aggregate into a clean pass

| | |
|---|---|
| **Reproduced** | Yes, both parts |
| **Root cause** | `PlannedAttempts.mismatch` compared four **identity** fields — which planned attempt a record claims to be — and nothing compared the **build** that produced it. Separately, `plan_hash` covered only the attempt layout, so it was an attempt-layout fingerprint being reported as a plan fingerprint |
| **Observed on `6d59acd`** | one record rewritten to `methodology_version` 1.0.0, `task_version` 1.0.0 and foreign task-set/scorer hashes passed the **real schema** and the **real CLI**: exit 0, 5 cells passed, `identity_unverified: []`. Changing the plan's own `methodology_version` and `task_set_version` left `plan_hash` **byte-identical** |
| **Fix** | `aggregate.py`: attempts in a cell must agree on `methodology_version`, `task_version`, `task_set_hash`, `answer_key_hash`, `scorer_hash`, and must match what the plan declares. `plan_hash` now covers the declared versions |
| **Classification** | reported as **BUILD INCONSISTENT — explicitly not a quality failure.** Nothing about the candidate failed; the record set cannot be interpreted. Reported in its own field, and such a cell cannot be selected |
| **Positive control** | genuine records → exit 0, 5 cells passed, `build_inconsistent: []` |
| **Negative control** | mixed build → exit 1, `cells_build_inconsistent: [['A','C0']]` |
| **Boundary check beyond the reported case** | five build fields, not just the two the probe altered; absence of a field is itself a failure; plan-declared version mismatch is a separate check |
| **Not verified** | whether `answer_key_hash` and `task_set_hash` are populated correctly by every run class. Asserted from the runner's code, not exercised per class |

### R4-06 — score provenance absent, so the guard had never run

| | |
|---|---|
| **Reproduced** | Yes |
| **Root cause** | `finalize` compared `scorer_hash` and methodology version **only when both sides carried them**, and the judge wrote neither. **0 of 17 real scores had `scorer_hash`.** "Absent means fine" is the same shape as the missing-cost defect: the safe-looking default is the one that lets an unbound result through. **This is the fourth consecutive round of "a guard whose input nothing produces"** (R3-01 CLI, R4-01 analysis functions, now this) |
| **Observed on `6d59acd`** | 17 scores, **0** with `scorer_hash`. A record given `scorer_hash = "f"*64` finalized 17 records and kept the wrong hash. A score with `detail.methodology_version` removed also finalized 17 |
| **Fix** | `judge.py` derives `scorer_hash` **from its own source** (`scorer_identity()`), and stamps `methodology_version` and `packet_digest` on every score. `finalize.py` **requires** all three and compares them unconditionally; `scored_packet_digest` travels into the record so the binding stays auditable afterwards |
| **Positive control** | golden chain: 17 scores, **17 with full provenance**; record `scorer_hash` equals score `scorer_hash`; finalize 17 |
| **Negative controls** | missing provenance → refused, nothing written. Record naming a different scorer → refused. Score missing methodology version → refused |
| **Not verified** | that `packet_digest` is stable across platforms — it hashes a `sort_keys` JSON dump, which is deterministic, but this was not tested on a second platform |

### R4-01 — analysis entry point (my earlier reason was half a reason)

The review's judgement — *"理由只成立一半"* — is accepted. **CR-002 decides how many attempts to
run. It does not decide whether reading records, checking cost completeness and reporting pairing
diagnostics may exist.** I extended a real constraint over work it did not cover.

`environment/harness/analyse.py`, `python3 -m harness.analyse --records DIR --run-plan PLAN`:

| Computed | Refused by name, with the decision it waits on |
|---|---|
| per-cell PASS / FAIL_QUALITY / INVALID / **missing** counts | `cost_delta_vs_baseline` — CR-002 unratified |
| total cost of priced attempts | `condition_ranking` — §7.7; §7.6 decides the denominator |
| **cost per successful task**, when every attempt is priced | `strongest_conditions` — §7.7 |
| paired / unpaired lists, each with its reason | `non_inferiority` — no margin set |
| | `savings_claim` — all the above, plus a pricing lineup that does not exist |

Every refusal appears in `decisions_required`. An absent number reads as "not interesting"; a
named refusal reads as "nobody has ruled on this yet".

| Control | Result |
|---|---|
| Positive: fully priced golden cells | exit 0, `cost_status: COMPUTED` |
| Negative: one unpriced attempt | `cost_status: BLOCKED`, value `null` — **never 0** |
| Negative: no passing attempt | `NO_FINITE_VALUE` |
| Negative: substituted identity | **exit 2, whole description refused** — a description of a record set that does not hold together is misinformation |
| Assertion | no `delta`, `ranking`, `non_inferiority_result` or `saving` key appears anywhere in the output |

---

## Same-class sweep

R4-01 and R4-06 both came from asking *"which documented command reaches this?"*. I extended it and
it is **still not exhaustive**: `pricing_preflight.check`, `evidence.compare_corpus_hashes` and
`assert_treatment_neutral` have **not** been checked for reachability. Listing them as unchecked
rather than implying coverage.

New, added this round: `tools/delivery_check.py` verifies the **committed** manifest, lock,
run-plan self-consistency and dry-run plan. `--refresh` is a separate deliberate action, because
**rebuilding an artefact and finding it matches proves only that the builder is deterministic**,
which was never in doubt. It caught its own first drift: adding `analyse.py` broke the manifest and
the check blocked until it was regenerated.

---

## The "7 of 7 tests failed" claim, corrected

The review's classification is accepted in full. The previous claim was literally true and weaker
than it sounded: **5 failures, 2 errors** (`TypeError`: the old `Cell` has no `plan=`), and **2 of
the 5 stopped at CLI argument parsing** before reaching data-validation logic. An interface change
that turns a test red is not the same strength of evidence as a behavioural regression.

**This round, classified up front:**

```
349 tests pass (was 326). 23 new.
The 23 against 6d59acd:  11 failures · 10 errors · 2 pass
```

- **The 10 errors are not behavioural evidence** — import failures and `TypeError`s from modules and
  keyword arguments that do not exist on `6d59acd` (`analyse`, `plan=`, `scorer_identity`).
- **The 2 that pass:** `test_a_record_naming_a_different_scorer_is_refused` passes because the old
  conditional check *did* fire when the fixture supplies both hashes — a weaker reason than it
  passes for now, and **not** evidence R4-06 was already closed, since 0 of 17 real scores carried
  the field. `test_a_substituted_identity_refuses_the_whole_description` covers the new `analyse`
  entry point reaching a refusal that already existed from R2-01.

**The 17-task positive control and the semantic negative control are retained** (E-002 turn 8
violation with a byte-perfect final answer → `FAIL_QUALITY`, `zero_tolerance:constraint_violation`).

---

## Both documented paths, executed

| Path | runner | judge | finalize | aggregate | analyse |
|---|---|---|---|---|---|
| Golden fixture | 17/17 | 17 scored, **17 with provenance** | 17 | **exit 0** — 5 cells, `identity_unverified: []`, `build_inconsistent: []` | **exit 0** |
| Committed dry run | 10/10 | scored | 10 | **exit 1 — the expected result** (synthetic outputs fail quality) | — |

`tools/delivery_check.py` → **exit 0** on all four checks.
Machine-readable before/after table: `reviews/evidence/r4/replay_results.json`.

---

## Engineering done vs decisions still owed

**Engineering, done here, none of it pushed back to the owner:** R4-01 through R4-06, the delivery
check, and the documented-path repair. The review was right that I had previously handed back work
that was already authorised; that is not repeated.

**Decisions, not mine, untouched:** CR-002 (research design; the dollar figure remains withdrawn as
unestablished), §7.6 (INVALID re-run rule), RT-04 and RT-10 (both departed from the instruction
without approval; **RT-10 raises the pass rate**), and the independent methodology review.

---

## What this is not

Everything above is a **replay of known-correct answers through the pipeline**. Workload D's tool
audit is script-assembled and flagged synthetic, workload E's intermediate turns are placeholder
text, the corpus reader reads only the first declared file, and **no model has been contacted at
any point**. No token saving has been measured and no cost figure exists.

**A passing synthetic chain is not evidence of real model quality, of a saving, or of readiness to
Freeze.**

Every fix here is `AUTHOR_TESTED` by the seat that wrote the defects. **Nothing on this branch is
independently verified against the current code**, and the two prior independent reviews are of
commits that no longer describe it.

# Response to the fourth adversarial review — `6d59acd`

**Review received:** 2026-09-18 · **Reviewed code:** `6d59acd` · **Review package:** `401ea9a`
**Reviewer verdict:** REQUEST CHANGES, stay in Draft, Freeze and LG4 NO GO.
**Responding seat:** the coordinating seat. Same seat, fourth round.

---

## The short version

**All six findings reproduced. All six are fixed. R4-01 is now built. The verdict is accepted.**

Two of the six are the recurring shape for a fourth consecutive round:

- **R4-06** — `finalize` compared a score's `scorer_hash` with the record's **only when both
  carried one**, and the judge never wrote one. **0 of 17 real scores had the field.** A guard
  whose input nothing produces is not a guard. That is R3-01 and R4-01 again, one stage further
  along, and I had listed this exact suspicion in the round-4 package as *"conditional checks"*
  without checking whether the field was ever produced at all.
- **R4-02** — the integrity manifest excluded `aggregate.py`, `finalize.py` and `runner.py`: every
  module between a scored packet and a published cell. A fresh manifest over a modified
  `aggregate.py`, with `select_strongest` overridden to return a fixed winner, verified **ok**.

The reviewer also rejected my framing in two places, and was right both times. Those are §4.

---

## 1. Findings, reproduced before anything changed

| # | Finding | Reproduced | Observed on `6d59acd` |
|---|---|---|---|
| **R4-02** | Manifest stale **and** under-scoped | **Yes** | committed manifest `verify → ok=false` (`run_record_schema.json`, `judge.py`); fresh manifest over a modified `aggregate.py` → **ok=true** |
| **R4-03** | Documented dry run broken | **Yes** | `dryrun/PLAN.json`: 10 items, **10 without `attempt_id`**; no `dryrun/RUN_PLAN.json`; runner exits 1 before executing anything |
| **R4-04** | Lock hash stale | **Yes** | `METHODOLOGY_CHANGE_REQUEST_002.md` differs from the hash the lock records |
| **R4-05** | Mixed builds pass | **Yes** | one record rewritten to methodology 1.0.0 + foreign task-set/scorer hashes → real CLI **exit 0, 5 cells passed**; `plan_hash` **byte-identical** after changing the plan's own versions |
| **R4-06** | Score provenance absent | **Yes** | **0 of 17** scores carried `scorer_hash`; a record with a wrong scorer hash finalized 17 records and kept it |
| **R4-01** | Analysis layer unreachable | **Yes** (self-found in round 4) | no command reached `cost_per_successful_task`, `select_strongest`, `pair_attempts` |

---

## 2. What changed

| # | Fix |
|---|---|
| **R4-06** | The judge derives `scorer_hash` **from its own source**, and stamps `methodology_version` and `packet_digest` on every score. `finalize` now **requires** all three — absent is a refusal, not a pass — and compares them unconditionally. The digest travels into the record as `scored_packet_digest` so the binding stays auditable afterwards |
| **R4-02** | The execution group is **discovered**, not listed: every `harness/*.py` except three named exclusions with reasons. A hand-maintained list of what to protect goes stale the first time someone adds a file and nothing says so. The same "nothing unclaimed" rule the task set had now applies to the environment. Committed manifest regenerated |
| **R4-05** | Records in a cell must agree on `methodology_version`, `task_version`, `task_set_hash`, `answer_key_hash`, `scorer_hash`, and must match what the plan declares. A mismatch is reported as **BUILD INCONSISTENT — explicitly not a quality failure**, because nothing about the candidate failed; the record set cannot be interpreted. `plan_hash` now covers the versions the plan declares |
| **R4-03** | `dryrun/PLAN.json` carries attempt ids; `make_dryrun_fixture.py` refuses a plan without them and writes `dryrun/RUN_PLAN.json`. RUNBOOK documents **both** paths and their expected exit codes |
| **R4-04** | Lock document hashes refreshed |
| **R4-01** | **`python3 -m harness.analyse` exists** — see §3 |
| *new* | **`tools/delivery_check.py`** verifies the *committed* manifest, lock, run-plan self-consistency and dry-run plan, and exits 1 on drift. `--refresh` is a separate, deliberate action, because rebuilding an artefact and finding it matches proves only that the builder is deterministic |

---

## 3. R4-01 — the reviewer was right that my reason was half a reason

I declined to build the analysis layer because §7 is unratified. The reviewer's judgement — *"理由只成立一半"* — is correct. **CR-002 decides how many attempts to run. It does not decide whether reading records, checking cost completeness and reporting pairing diagnostics may exist.** I extended a real constraint over work it did not cover.

`harness/analyse.py` computes what needs no ruling and refuses what does, by name:

| Computed | Refused, and why |
|---|---|
| per-cell PASS / FAIL_QUALITY / INVALID / **missing** counts | `cost_delta_vs_baseline` — CR-002 unratified |
| total cost of priced attempts | `condition_ranking` — §7.7, and §7.6 decides the denominator |
| **cost per successful task**, when every attempt is priced | `strongest_conditions` — §7.7 |
| paired / unpaired lists with a reason for each | `non_inferiority` — no margin has been set |
| | `savings_claim` — all of the above, plus a pricing lineup that does not exist |

Every refusal appears in `decisions_required` with the decision it waits on. **An absent number reads as "not interesting"; a named refusal reads as "nobody has ruled on this yet".**

Cost is never silently zero: unpriced attempts give `cost_status: BLOCKED`, a cell with no passes gives `NO_FINITE_VALUE`, and a substituted identity **refuses the whole description** (exit 2) rather than describing a record set that does not hold together.

---

## 4. Two framings the reviewer rejected, and I accept both

### "7 of 7 new tests fail on the old commit" was literally true and weaker than it sounded

The reviewer's classification: 5 failures, 2 errors (`TypeError`: the old `Cell` has no `plan=`), and **2 of the 5 stopped at CLI argument parsing before reaching any data-validation logic**. An interface change that turns a test red is not the same strength of evidence as a behavioural regression, and presenting one count hid the difference. **Accepted.** This round's classification is stated up front, below.

### "6 → 3 → 2" is not a credibility curve

The reviewer: each round's scope and intensity differ, so the count is not a trend. **Accepted, and I was leaning on it.** I used the falling number as the honest-sounding way to summarise four rounds; it implied convergence that the evidence does not support. This round found **six**. Dropped.

---

## 5. This round's test evidence, classified up front

```
349 tests pass (was 326). 23 new.

The 23 against 6d59acd:  11 failures · 10 errors · 2 pass
```

**The 10 errors are not behavioural evidence** — they are import failures and `TypeError`s from modules and keyword arguments that do not exist on `6d59acd` (`analyse`, `plan=`, `scorer_identity`). They are reported as errors, not counted as proof.

**The 2 that pass, and why:**

- `test_a_record_naming_a_different_scorer_is_refused` — the old conditional check *did* fire, because this fixture supplies both hashes. It passes for a weaker reason than it does now, and is **not** evidence that R4-06 was already closed: 0 of 17 real scores carried the field at all.
- `test_a_substituted_identity_refuses_the_whole_description` — identity refusal already existed from R2-01; the test covers the new `analyse` entry point reaching it.

**Both documented paths were executed with the real `jsonschema` validator. No stub anywhere:**

| Path | runner | judge | finalize | aggregate | analyse |
|---|---|---|---|---|---|
| Golden fixture | 17/17 | 17 scored, **17 with provenance** | 17 | **exit 0**, 5 cells, no unverified, no build inconsistency | **exit 0** |
| Committed dry run | 10/10 | scored | 10 | **exit 1 — expected**: the fixture's outputs are synthetic, so attempts genuinely fail quality | — |

`tools/delivery_check.py` → **exit 0** on all four checks. It caught its own first drift: adding `analyse.py` broke the manifest, and the check blocked until it was regenerated deliberately.

---

## 6. What I have not done

- **No independent re-test.** Every fix is `AUTHOR_TESTED`, same seat, same day.
- **No container rebuild, no image digest.** The reviewer ran on host CPython 3.12 with jsonschema 4.23 in an isolated directory, not the repo's 3.11 container. **Neither of us has verified this code under LG3 conditions.**
- **The reachability sweep is still not exhaustive.** R4-01 and R4-06 both came from it, and I have not finished it for `pricing_preflight.check`, `evidence.compare_corpus_hashes` or `assert_treatment_neutral`.
- **No model contacted, no cost measured, no live provider.** Unchanged.
- **The methodology decisions are untouched** — CR-002, §7.6, RT-04, RT-10, the independent methodology review. They are not mine.

---

## 7. What this still does not mean

The tool now runs both documented paths end to end, refuses substituted identities, refuses mixed builds, refuses unprovenanced scores, protects its own execution code, and can produce a descriptive cost figure while blocking every conclusion that waits on a ruling.

**None of that is a measurement.** It is a replay of known-correct answers: workload D's tool audit is script-assembled, E's intermediate turns are placeholders, and no model has been contacted at any point. The reviewer's own words are the right ending — *"不要藉本輪工程驗收自動批准任何商業節省或品質不劣性主張"*.

**Verdict unchanged: NOT FIT TO FREEZE. LG4 NO GO. Stay in Draft.**

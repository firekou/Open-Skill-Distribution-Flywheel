# Response to the third adversarial review — `4e6584b`

**Review received:** 2026-09-17 · **Reviewed commit:** `4e6584b6a90dc21067e298ac482d100221ca13a3`
**Reviewer verdict:** REQUEST CHANGES, stay in Draft, Freeze and LG4 NO GO.
**Responding seat:** the coordinating seat. Same seat, third round.

---

## The short version

**Both P1 findings reproduced. Both are fixed. And looking for them I found a third defect the
reviewer did not, which was worse than either.**

The reviewer's judgement — that "three P1s all fixed" could not be accepted as a complete close —
was correct, and for a reason I should state plainly:

> **Three rounds. Three times the same mistake: the check went in at one entrance, and the exit
> was left trusting a flag.**

- **Round 1** put the duplicate check in `build_cells`.
- **Round 2** found `Cell.verdict()` unguarded. I fixed it, and wrote *"a defence that only
  guards one entrance is not a defence."*
- **Round 3** found that `identity_verified` was defined as `expected is not None` — the cell
  held a **set of legal ids** and reported the identities as checked without ever comparing a
  field. Twelve records carrying twelve legal ids while all claiming `D-001` repetition 1 passed
  at **12/12, `identity_verified: true`**, and were selected as a winner.

I wrote the principle in round 2 and violated it in the same file in round 3.

---

## 1. Findings, reproduced before anything changed

| # | Finding | Reproduced? | Observed on `4e6584b` |
|---|---|---|---|
| **R3-01** | The documented CLI never built a registry | **Yes** | Twelve **entirely legitimate** records → `exit 1`, `cell_verdict FAIL`, `identity_verified false` |
| **R3-02a** | `Cell` treats "has an id set" as "identity checked" | **Yes** | legal ids + wrong task/repetition → **12/12 PASS**, `identity_verified: true`, **selected** |
| **R3-02b** | Records mutated after validation | **Yes** | edit the dict after `build_cells` accepted it → still **PASS**, still selected |
| **R3-03** | *(found here, not by the reviewer)* | **Yes** | see below |

### R3-03 — the one nobody was looking for, and the worst of the three

`run_record_schema.json` has `additionalProperties: false`. Neither `pending_adjudication`
(added in **round 1**) nor `attempt_id` (added in **round 3**) was in it.

**Round 1's ADV-D fix would have made `finalize` reject every record in the real chain**, with
`Additional properties are not allowed ('pending_adjudication' was unexpected)`. Proven against
the shipped `4e6584b` schema, in `LAB_001_ADVERSARIAL_REPLAY_R3_RESULT.json`.

It survived two rounds of external review and two of my own test suites because:

1. `jsonschema` was not installed in this environment, so `record.validate` never ran; and
2. **my finalize tests stubbed the validator** — the same isolation both reviewers correctly
   flagged as a limitation, which I treated as an acceptable caveat instead of as a gap to close.

I reported a fix as working while the validator that would have rejected it was switched off.
That is the same error as the original version mis-stamp: **evidence that was green because
something was not actually running.** Third occurrence of that shape too.

---

## 2. What changed

### R3-02 — the cell holds the plan, and re-verifies at report time

`Cell.expected: frozenset` is gone. The cell now holds `plan: PlannedAttempts` and
`verdict()` re-checks **every attempt's workload, condition, task and repetition against it, at
the moment the rate is computed.** `identity_verified` now means *the fields were compared, here,
now* — not *somebody handed me a set*.

That also closes R3-02b for free: because verification happens at report time rather than at
build time, a record edited after `build_cells` accepted it is caught when the number is
produced.

### R3-01 — the command line, and the whole chain behind it

- `harness.aggregate` gains **`--run-plan`**, which supplies the denominators **and** the
  identities from one source. The report echoes `plan_hash` and `plan_source`.
- The legacy `--plan` (counts only) now **declines with exit 2 unless `--registry` is given**. It
  does not print a report. A refusal to measure must not look like a measurement result.
- **`runner.py` now writes `attempt_id`** — it wrote none at all, so no record it produced could
  ever have been checked — and refuses a plan whose items lack one. Planned identity
  (`attempt_id`, issued by the plan) and execution identity (`run_id`, new on every retry) are
  separate fields, so **a retry replaces a sample instead of adding one**.
- `tools/golden_run.py` emits its **own** `RUN_PLAN.json` for the 17-task fixture, and the
  RUNBOOK says explicitly not to aggregate dry-run records against the production plan's 270.
- `run_record_schema.json` accepts both fields, with a description of what each means.

---

## 3. Evidence — stronger this round, and here is exactly why

`jsonschema` was installed into this environment (it was already in the vendored wheelhouse; it
had simply never been installed here). **The whole documented chain then ran end to end with the
real record validator, for the first time in any round:**

```
runner    17/17 completed, 0 failed
judge     17 packets, 17 passed, 0 zero-tolerance breaches
finalize  17 finalized, pending_adjudication []
aggregate exit 0 — 5 cells passed, 0 failed, cells_identity_unverified []
          plan_hash a4fc427c3136…
packets   Counter({'1.1.0': 17})
```

```
326 tests pass (was 319). 7 new R3 tests. All 7 fail on 4e6584b.
```

Round 2 could not show its tests failing on the reviewed commit. **Round 3 can**, and the CLI
tests are real `subprocess` positive and negative controls, as the reviewer asked for.

**What this still is not.** It is a replay of known-correct answers through the pipeline. Workload
D's tool audit is script-assembled, E's intermediate turns are placeholders, and no model has been
contacted. It shows the documented commands work on data that is supposed to pass, and refuse
data that is supposed to fail. It shows nothing about real agent behaviour.

---

## 4. What I did not do

- **No independent re-test.** Every round-3 fix is `AUTHOR_TESTED`, same seat, same day.
- **No container rebuild**, so no image digest binds this code. Gate 13 stays INVALIDATED.
- **No binding of source commit / scorer hash / image digest into the records** as a set, which
  the reviewer lists as step 4. `plan_hash` is now recorded; the rest is not.
- The reviewer's remaining items — methodology review, CR-002, §7.6, RT-04/RT-10 — are
  **untouched decisions**, not work I can close.

---

## 5. Three rounds, counted honestly

| Round | Defects found by an outsider | Found by me first |
|---|---|---|
| 1 | 6 | 0 |
| 2 | 3 (two were incomplete round-1 fixes) | 0 |
| 3 | 2 (both incomplete round-2 fixes) | **1 — R3-03, and it was the worst one** |

**Twelve executable defects across three rounds.** Eleven found by someone else.

Two things changed this round that are worth more than the fix count: the first end-to-end run
with validation actually enabled, and the first defect I found before the reviewer did. Both came
from the same decision — **stop stubbing the thing that was inconvenient and turn it on.**

That is a real improvement and it is not a case for freezing. The outside defect-discovery rate
has gone 6 → 3 → 2 and has not reached zero, and each round has shown my fixes to be locally
correct while leaving the class open. Until an independent seat re-tests at the current head, the
only honest reading of a green suite from this seat is that **it is green.**

**Verdict unchanged: NOT FIT TO FREEZE. LG4 NO GO. Stay in Draft.**

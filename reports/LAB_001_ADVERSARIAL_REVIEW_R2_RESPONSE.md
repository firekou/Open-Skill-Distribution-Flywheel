# Response to the second adversarial review — `59293e8`

**Review received:** 2026-09-17 · **Reviewed commit:** `59293e8278f8cbef5781b6a6bb3b0def2ed3a880`
**Reviewer verdict:** REQUEST CHANGES, stay in Draft, Freeze and LG4 NO GO.
**Responding seat:** the coordinating seat — again, the seat that wrote the defects.

---

## The short version

**All three P1 findings reproduced. All three are fixed. The verdict is accepted in full.**

The finding that matters is not any individual bug. It is this: **two of the three are the same
defects round 1 closed, surviving in a place the round-1 fix did not reach.**

Round 1's own fix comment said, about putting the duplicate check in `Cell.verdict()` as well as
at the entrance:

> *"a defence that only guards one entrance is not a defence"*

And then I left the **over-count** check at that one entrance. A directly-constructed cell with
four distinct records against three planned still reported **success_rate 1.3333, PASS**, and
`select_strongest` still chose it. I wrote the principle and did not apply it one line away.

The same pattern in R2-01: I added `attempt_identity()` to stop a record being counted twice, and
took the identity **from the record**. Twelve retries of one task, differing only in `run_id`,
filled a twelve-attempt cell and reported **12/12, PASS** — eleven planned attempts of other
tasks silently replaced. A planned denominator with a self-reported numerator is not a check.

**Round 1 fixed the examples. Round 2 shows I had not fixed the class.**

---

## 1. Findings, reproduced before anything was changed

| # | Finding | Reproduced? | Observed on `59293e8` |
|---|---|---|---|
| **R2-01** | Changing `run_id` substitutes for missing tasks | **Yes** | 12 records of `D-001` rep 1, ids `retry-0…11` → **12/12, 1.0, PASS** |
| **R2-01b** | Invented `attempt_id` believed | **Yes** | 12 self-asserted ids → **12/12, 1.0, PASS** |
| **R2-02** | Direct `Cell` accepts 133% and is selectable | **Yes** | `recorded 4 / planned 3`, `success_rate 1.3333`, **PASS**, `chosen [('D','C1')]` |
| **R2-03** | `finalize` not whole-batch | **Yes** | second record's outcome rejected **after** the first was rewritten |
| **R2-04** | Withdrawals never reached the decision surfaces | **Yes** | freeze-readiness verdict, gate 5, gate 19 and the PR body all still carried withdrawn text |

---

## 2. What changed

### R2-01 — identity now comes from the plan, not from the record

`PlannedAttempts` expands the frozen run plan into the **270 attempt ids it actually authorises**,
each bound to its workload, condition, repetition and task. `build_cells` takes the registry and
refuses any record whose `attempt_id` is not in it, or which holds a real id while claiming a
different task or repetition. `Cell` carries the `expected` id set and compares it: **missing**
planned attempts and **unexpected** records are each a named failure reason.

Execution identity and planned identity are now separate. A retry may reuse a planned attempt's
id **only if it is that same planned attempt**; it can never add a sample.

**A cell whose identity was never checked against a plan is not reportable** — `verdict()` fails
it and `select_strongest` refuses it. Unverified is a finding, not a default.

### R2-02 — the over-count check moved to where the rate is computed

`Cell.verdict()` now fails any cell with more records than planned, and **reports the rate above
1.0 rather than clipping it to 100%**. A rate above 1.0 is arithmetic telling you the record set
is broken; hiding it would destroy the only signal.

### R2-03 — and the word "atomic" is withdrawn

`finalize` now resolves **every** record in memory — field updates, outcome resolution, schema
validation — and writes nothing unless all of them pass. Writes go through temp + rename, so no
single file is ever torn.

**It is still not a multi-file transaction, and the code and the report now say so.** A crash
between renames leaves some records finalized. Making that genuinely all-or-nothing needs a new
batch directory and a publish marker — a change to how records are stored, not to this function.
The guarantee is stated exactly, in the returned `write_guarantee` field: *whole-batch validation
before any write, and no torn file.*

The reviewer's precise demand — "若只保證驗證前置，應精確描述，撤回泛稱 atomic" — is what was done.

### R2-04 — the withdrawals reached the decision surfaces

| Surface | Was | Now |
|---|---|---|
| Freeze-readiness **verdict** | "a complete candidate, pending two independent reviews and one ruling" | withdrawn in place, with five outstanding items |
| Gate 5 | PASS, RT-01–RT-13 closed | **PARTIAL** — RT-04 and RT-10 are unapproved DEVIATIONs |
| Gate 19 | PASS, "finalize made atomic" | **REOPENED**, the atomic claim marked false |
| Gate 21 | — | round-2 fixes, author-tested only |
| PR body | 3.46×, $177–325, complete candidate | rewritten |

**A withdrawal that does not reach the document a decision is made from has not been made.**
Round 1 corrected the response document and left the decision surfaces alone.

---

## 3. Tests, and an honest limit on this round's evidence

```
319 tests pass (was 307). 12 new round-2 regression tests.
```

**Round 1 could say "9 of 12 fail on `62a16a4`". Round 2 cannot make the equivalent claim.** The
new tests import `PlannedAttempts`, which does not exist on `59293e8`, so against that commit the
module fails to import rather than the assertions failing.

The before-column is therefore the **probe reproduction** — the reviewer's inputs run against the
pre-fix code, recorded in `LAB_001_ADVERSARIAL_REPLAY_R2_RESULT.json`. That is weaker evidence
than round 1's, and it is not being presented as equivalent.

The finalize probe stubs schema validation, because `jsonschema` is not installed here — the same
isolation the reviewer declared for theirs. It establishes the **ordering** of validation and
writes. It does **not** establish end-to-end schema acceptance, and is not cited as doing so.

### The controls

A fix that rejects everything is not a fix. The genuine twelve-attempt D/C1 cell, built from the
plan's own ids, still passes at 1.0 with `identity_verified: true`; eleven of twelve fails and
names the absent attempt.

---

## 4. What I did not do

- **No independent re-test.** Every round-2 fix is `AUTHOR_TESTED`, same seat, same day.
- **No rebuild**, no golden-chain re-run, no container binding of source commit / scorer hash /
  image digest. The reviewer lists these as next steps and they remain open.
- **No live model, no token measurement, no approved budget or margin.**

---

## 5. The thing to take from two rounds, not from either one

| Round | Executable defects found by an outsider | Found by me first |
|---|---|---|
| 1 | 6 | 0 |
| 2 | 3 (two of them incomplete round-1 fixes) | 0 |

**Nine executable defects in two rounds, none of which I found myself, and the second round shows
my repairs can be locally correct and still leave the class open.** The test count went 294 → 306
→ 319 and every one of those greens was true at the time.

The right conclusion is not "the instrument is nearly ready". It is that **the rate at which an
outside party finds real defects here has not yet fallen**, and until it does, no green suite
from this seat should move anything.

**Verdict unchanged, and now for stronger reasons: NOT FIT TO FREEZE. LG4 NO GO. Stay in Draft.**

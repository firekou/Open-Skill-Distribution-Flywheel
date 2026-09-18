# Review package for round 4 — pinned at `6d59acd`

**PR:** https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/1 (draft, **not merged**)
**Head:** `6d59acd` · **Base:** `main` at `a8ca352` · **Branch:** `claude/atk-open-skill-distribution-96e4vv`
**Prior reviewed commits:** `205c1b4` → `62a16a4` (R1) → `59293e8` (R2) → `4e6584b` (R3) → **`6d59acd`**

**Verdict unchanged: NOT FIT TO FREEZE. LG4 NO GO. Stay in Draft.**

---

## 0. Read this first: the pattern, not the fix count

Three rounds of external review. **Twelve executable defects. Eleven found by someone else.**
Every round found the previous round's repairs locally correct and the defect class still open:

| Round | Where the check went in | What the next round found unguarded |
|---|---|---|
| 1 | `build_cells` | `Cell.verdict()` — a directly built cell |
| 2 | `Cell.verdict()`, with the note *"a defence that only guards one entrance is not a defence"* | `identity_verified` meant `expected is not None` — a **flag**, not a comparison |
| 3 | `Cell` holds the plan and re-verifies at report time | **see §2 — I found the next one myself, and it is the same shape again** |

**The recurring failure is not a bug type. It is that I fix the reported example and leave the
class open, then report the class closed.** Round 4 should assume that is still true and look for
where it is true now.

---

## 1. What changed since `4e6584b`

| ID | Defect on `4e6584b` | Fix |
|---|---|---|
| **R3-01** | The documented RUNBOOK command **failed twelve entirely legitimate records** (`exit 1`, `identity_verified false`) because the CLI never built a registry | `--run-plan` supplies denominators *and* identities from one source, echoes `plan_hash`. Legacy `--plan` **declines with exit 2** unless `--registry` is given, and prints no report. `runner.py` now writes `attempt_id` (it wrote none at all) and refuses a plan without one |
| **R3-02a** | Legal ids + wrong task/repetition → **12/12 PASS**, `identity_verified: true`, selected | `Cell` holds `PlannedAttempts` and re-verifies workload/condition/task/repetition **inside `verdict()`** |
| **R3-02b** | A record edited *after* `build_cells` accepted it still reported PASS | Closed by the same change — verification happens when the number is produced, not when the cell is built |
| **R3-03** | **Self-found.** `run_record_schema.json` is `additionalProperties: false` and contained neither `pending_adjudication` (round 1) nor `attempt_id`. **Round 1's fix would have made `finalize` reject every record in the real chain.** It survived two external reviews because `jsonschema` was not installed and my finalize tests stubbed the validator | Both fields added to the schema |

### Evidence

`jsonschema` installed from the vendored wheelhouse. **The documented chain then ran end to end
with the real record validator for the first time in any round:**

```
runner    17/17 completed, 0 failed
judge     17 packets, 17 passed, 0 zero-tolerance breaches
finalize  17 finalized, pending_adjudication []
aggregate exit 0 — 5 cells passed, cells_identity_unverified []
          plan_hash a4fc427c3136…
packets   Counter({'1.1.0': 17})

326 tests pass. 7 new R3 tests, ALL 7 fail on 4e6584b,
including subprocess positive AND negative controls on the real CLI.
```

Round 2 could not show its tests failing on the reviewed commit. Round 3 can.

---

## 2. R4-01 — found while preparing this package, **not fixed**, and it is R3-01's shape again

R3-01 was "the defence exists but no command reaches it." I ran that same reachability check
across the rest of the module. Result:

**`cost_per_successful_task`, `select_strongest` and `pair_attempts` are reachable from no
documented command and no CLI at all. They are called only by tests.**

- `cost_per_successful_task` is **quantity 9 — the benchmark's headline metric**, the one the
  whole exercise exists to produce. `meter.py` names it in a docstring. `RUNBOOK.md` has no
  command that computes it.
- `select_strongest` implements **§7.7**, which decides which cells get reproduced.
- `pair_attempts` implements **§7.1/§7.3** pairing, without which no comparison is valid.

`harness.aggregate --run-plan` stops at cell verdicts. **So every fix made to those three
functions across rounds 1–3 — the missing-cost refusal, the failed-cell rejection, the
cold/warm pairing refusal — is currently unreachable in practice, exactly like the registry was
before R3-01.**

**Why it is not fixed here.** Building that command means fixing how deltas are computed and how
treatment and baseline records are supplied — that is §7 of a methodology which is **unratified**
and has an open change request (CR-002) and an unratified §7.6. Building it now would bake in
design decisions the Editor-in-Chief has not made, which is the defect RT-04 and RT-10 already
represent. It is recorded as **gate 24, NOT BUILT** rather than half-built.

**It does mean the analysis half of this harness has never been executed by anyone.**

---

## 3. What is claimed, and what is not

**Claimed:** the documented commands accept data that should pass and refuse data that should
fail, at the cell level, with the real schema validator running.

**Not claimed, and must not be read in:**

- **This is a replay of known-correct answers.** Workload D's tool audit is script-assembled and
  flagged `synthetic`; workload E's intermediate turns are placeholder text; the corpus reader
  reads only the first declared file. It shows nothing about real agent behaviour.
- **No model has been contacted at any point.** `LiveProvider.run_task()` raises
  `NotImplementedError`; `runner.py` always builds a `ReplayProvider`. That is unbuilt code, not
  a credential blocker (gate 20).
- **No container rebuild**, so no image digest binds this code. Gate 13 stays INVALIDATED.
- **Every fix is `AUTHOR_TESTED`** by the seat that wrote the defects. Nothing on this branch is
  independently verified against the current code. The R1 Red Team reviewed `205c1b4`; the
  Reproduction Agent reproduced a pre-fix image. **Neither transfers.**
- **No token saving has been measured. No cost figure exists.** The previously quoted 3.46× /
  $177–325 is **withdrawn** — it applied an experimental-subset attempt ratio to a whole-project
  budget, never expanded the 22 guardrail runs, and treated attempt counts as dollars.
- **No hypothesis confidence raised.** H011 stays at H0 Idea.

---

## 4. Where to attack this — including what I have not checked

The first three are my own suspicions, not safe ones:

1. **Finish the reachability sweep I started.** R3-01 and R4-01 are the same defect found twice.
   Every guarantee in this repo should be checked against *"which documented command reaches
   it?"* — `manifest.verify`, `pricing_preflight.check`, `evidence.compare_corpus_hashes`,
   `assert_treatment_neutral`. I have not done this systematically.
2. **`PlannedAttempts.mismatch` compares four fields** — workload, condition, task_id,
   repetition. It does **not** compare `task_version`, `task_set_hash`, `scorer_hash` or
   `methodology_version`. A record from a different task-set build, holding a legal attempt id,
   would pass identity. I believe this is a real hole and have not closed it.
3. **`finalize`'s cross-checks are conditional.** The `methodology_version` and `scorer_hash`
   comparisons only fire when *both* sides carry the field. A score missing `scorer_hash` passes
   silently. That is the same "absent means fine" shape as the missing-cost defect.
4. **The R3-03 class.** One closed schema hid two fields for two rounds. Are there other
   validators that are off, stubbed, or never installed in the path anyone runs? My finalize
   tests still stub the validator in the ordering test.
5. **The controls, not the refusals.** Every round I add negative tests. A fix that rejects
   everything would also pass those. Check the positive controls are real — particularly that the
   genuine 12-attempt cell, and the 17-task chain, pass for the right reasons.

---

## 5. Decisions still outstanding — none are mine

| # | Decision | Status |
|---|---|---|
| 1 | **CR-002** — the research design. Option 5 (73 experimental attempts, staged, pre-registered) vs option 1 (270). **No dollar figure exists** | PENDING |
| 2 | **§7.6** — the INVALID re-run rule, marked "needs ratification" in the methodology and omitted from an earlier "one ruling outstanding" claim | PENDING |
| 3 | **RT-04** — a seat ruled that a low-authority source stating the correct value is not a valid citation. The instruction said the opposite. **Approve or reverse** | PENDING |
| 4 | **RT-10** — a seat re-weighted `count` immediately instead of reviewing it separately. **It raises the pass rate** (B-002: 0.95 fail → 0.9945 pass). **Approve or reverse** | PENDING |
| 5 | **Independent methodology review** of `METHODOLOGY_v1.1.0` — drafted by the seat that adjudicated the change request | PENDING |
| 6 | **Independent re-test at `6d59acd`** — not at any earlier commit | PENDING |

---

## 6. Files, pinned at `6d59acd`

| What | Path |
|---|---|
| Round 3 response (point by point) | `reports/LAB_001_ADVERSARIAL_REVIEW_R3_RESPONSE.md` |
| Round 3 probe evidence | `reports/LAB_001_ADVERSARIAL_REPLAY_R3_RESULT.json` |
| Rounds 1 and 2 | `reports/LAB_001_ADVERSARIAL_REVIEW_{,R2_}RESPONSE.md` |
| Gate table | `reports/LAB_001_FREEZE_READINESS_V1_1.md` |
| Aggregator | `benchmarks/token-efficiency-lab-001/environment/harness/aggregate.py` |
| Runner | `…/harness/runner.py` · Finalize `…/harness/finalize.py` |
| Record schema | `…/environment/run_record_schema.json` |
| Tests | `…/harness/test_harness.py` (326 with `test_judge.py`) |
| RUNBOOK | `benchmarks/token-efficiency-lab-001/RUNBOOK.md` |
| Run plan | `benchmarks/token-efficiency-lab-001/RUN_PLAN_v1.1.0.json` |

Pin any link as
`https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/6d59acd/<path>`.

---

## 7. The honest summary

The instrument is better than it was three rounds ago and **it has still measured nothing**. The
outside defect-discovery rate has gone **6 → 3 → 2** and has not reached zero. Each round has
shown my repairs locally correct while leaving the class open, and round 4 already has one
confirmed open instance (**R4-01**) before it starts.

Two things improved this round, and both came from the same decision — **stop stubbing the
inconvenient check and turn it on**: the first end-to-end run with validation actually enabled,
and the first defect found here before the reviewer found it.

Neither is a case for freezing. Until an independent seat re-tests at `6d59acd`, the only honest
reading of a green suite from this seat is that **it is green**.

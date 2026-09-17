# Lab 001 — Freeze Readiness, v1.1.0

**Round:** Prompt 3.5 benchmark repair · **Source commit:** `a8ca352dc64e792864f351f7775e2b21681b6390`
**Branch:** `claude/atk-open-skill-distribution-96e4vv` — **not merged to main**
**Decision this report supports:** whether `METHODOLOGY_v1.1.0` and `TASK_SET_v1.1.0` are a
**freeze candidate**. It does **not** authorise a Pilot; those are decided separately.

> **LG4 remains NO GO.** Nothing in this round changes that, and nothing in it was meant to.

---

## Gate table

| # | Gate | Status | Evidence | Owner |
|---|---|---|---|---|
| 1 | v1.0.0 originals unmodified | **PASS** | `METHODOLOGY_v1.0.0.md` still `c1810b04…89bc`, `METER_CALIBRATION_v1.0.0.md` still `3ed9dac6…a98aa`; `TASK_SET_v1.0.0` 155/155 manifest entries OK; `git diff a8ca352..HEAD` over all v1.0.0 paths is empty | coordinator |
| 2 | CR-001-A, B, C adjudicated and executable | **PASS** | `METHODOLOGY_CHANGE_REVIEW_001.md`; acceptance tests A-1…A-6 and B-1…B-5 implemented | methodology-reviewer |
| 3 | `METHODOLOGY_v1.1.0` written and internally consistent | ~~PASS (as a DRAFT)~~ **PASS only after correction** | `75676732…fcc1`; **six** drafting amendments. External review found §6.1 contradicted the run plan's denominator (3 vs 12) and §7.7 named a variance tie-break the code omitted — so "internally consistent" was false at `62a16a4`. Both corrected | methodology-reviewer |
| 4 | Independent methodology sign-off | **PENDING** | nobody outside the drafting seat has reviewed the text | **Editor-in-Chief** |
| 5 | RT-01 – RT-13 closed | ~~PASS~~ **PARTIAL** | 11 of 13 closed with a named proof. **RT-04 and RT-10 are reclassified DEVIATION — ruled by a seat, against the instruction, never approved** (R2-04: this row still read PASS after they were reclassified elsewhere). RT-10 raises the pass rate | four seats |
| 6 | RT-14 – RT-21 dispositioned | **PASS** | 7 closed, 1 retained with its consequence written into DESIGN_NOTES | Designer / Judge |
| 7 | UG-01 – UG-33 dispositioned | **PASS** | 26 closed with clause + test; 7 retained with an argument each; the two that could hide a violation are made visible rather than waived | Quality Judge |
| 8 | 17 tasks independently semantically verified | **PASS** | `INDEPENDENT_VERIFICATION.md`: 17 of 17 agree, every value re-derived by different methods, nothing sampled | independent verifier |
| 9 | Answer keys mechanically re-derivable | **PASS** | 17/17 reproduce byte-identically from committed scripts | Answer Key Builder |
| 10 | Blind evaluation and evidence contract complete | **PASS** | salt custody written; evidence produced by a named seat; packet sufficiency asserted before the judge sees anything; 240 judge tests | Judge + harness |
| 11 | Scoring-integrity manifest | **PASS** | separate task-set / answer-key / scorer / config hashes, no self-reference, **zero unclaimed files**; modified, added and deleted all caught | harness |
| 12 | Golden end-to-end run | ~~PASS~~ **SUPERSEDED — re-test required** | The 17/17 was produced under the **wrong rulebook** (records stamped 1.0.0). At the declared version the same run gave **11/17**. Superseded again on 2026-09-17: six scoring and aggregation defects found by external review, now fixed, have **not** been re-tested end to end. **This row is not evidence of anything until a fresh golden run is executed and independently reproduced.** | harness |
| 13 | Environment rebuilt and reproducible | ~~PASS~~ **INVALIDATED — image is stale** | `sha256:04d7fac698f8…fa68` was built **before** the version fix, the six ADV fixes and the task-set corrections. It reproduces exactly, and it reproduces the wrong code. A new image must be built and independently reproduced; the old digest may not be cited as current readiness | harness |
| 19 | Defects from external adversarial review round 1 | ~~PASS~~ **REOPENED, then closed again in round 2** | Six closed with 12 tests, 9 failing on `62a16a4`. **Round 2 reopened two of them**: duplicate refusal did not stop *distinct* over-count at the cell, and identity was still self-reported. This row also claimed *"finalize made atomic"*, which was **false** — only the missing-score check had been hoisted | harness |
| 21 | Defects from external adversarial review round 2 | **PASS (author-tested only)** | R2-01 identity bound to a frozen `PlannedAttempts` registry (270 ids); R2-02 over-count and identity-unverified cells refused at the cell and barred from selection; R2-03 whole-batch validation before any write, temp+rename per file, and **the word "atomic" withdrawn** — it is not a multi-file transaction. 12 new tests; **319 green**. **Same seat, no independent verification.** The round-2 tests cannot be shown failing on `59293e8` (they import a class that does not exist there); the before-column is the probe reproduction in `LAB_001_ADVERSARIAL_REPLAY_R2_RESULT.json`, which is weaker evidence than round 1's and is not claimed as equivalent | harness |
| 20 | Live provider execution path | **NOT BUILT** | `providers.LiveProvider.run_task()` raises `NotImplementedError`; `runner.py` constructs `ReplayProvider` unconditionally. This is **a build task, not a credential blocker** — issuing a credential and choosing a model would still not produce a runnable agent loop | harness |
| 14 | 100-run mapping without contradiction | **PENDING** | `RUN_PLAN_v1.1.0.json` enumerates all 78 runs and 270 attempts; allocation untouched — but the **research design is unratified** (`CR-002`). The 3.46× figure is an **attempt** multiplier for the experimental subset; **the dollar consequence is withdrawn as unestablished** | **Editor-in-Chief** |
| 14b | §7.6 INVALID re-run rule ratified | **PENDING** | §7.6 is marked "needs ratification" in the methodology itself. It was **omitted** from the review package's "one ruling outstanding" claim; there are at least **two** | **Editor-in-Chief** |
| 15 | Pricing readiness | **BLOCKED** | `PS-2026-09-16` prices 30 entries with cache rates; **3 rows BLOCKED**; and the model/plan selection that decides completeness does not exist (open item **C-a**) | Editor-in-Chief + harness |
| 16 | Provider-native meter calibration | **BLOCKED** | no benchmark credential exists. An accumulator check is not calibration | **Editor-in-Chief** |
| 17 | Independent Red Team replay | **DONE — verdict NOT FIT TO FREEZE, then remediated** | `RED_TEAM_REVIEW.md`: 3 BLOCKING, 4 MAJOR, 5 MINOR. All three blockers closed and the acceptance criterion met; **the replay has not been re-run against the remediation** | Task Red Team |
| 18 | Independent reproduction of the new environment | **DONE — image and run both reproduce exactly** | `LAB_001_REPAIR_REPRODUCTION_RESULT.md`: 15 findings, 9 remediated here. It reproduced the run perfectly and independently found that the run reproduced **the wrong rulebook** | Reproduction Agent |

---

## How to read a superseded row

**Rows 12 and 13 are struck through on purpose.** An earlier version of this table left them as
plain **PASS** and explained their invalidation in an addendum further down. External review
pointed out that anything reading the table — a person skimming, or a script — still takes a
PASS from the row, and the correction only exists for whoever reads to the bottom. **The active
status line is now the correction.** A superseded gate carries no credit anywhere in this
document.

## What "BLOCKED" means here, and what it does not

Gates 15 and 16 are **BLOCKED on things outside this round's authority**: a credential nobody has
issued, and a model selection nobody has made. That is recorded as BLOCKED rather than dressed up
as complete.

It does **not** follow that the whole candidate is unusable. A methodology and a task set can be
frozen while pricing is blocked — what cannot happen is a **Pilot**, and what must not happen is
a claim that the stack is execution-ready. Prompt 3.5 §9 anticipates exactly this: submit the
complete methodology and task-set candidate, list pricing readiness as BLOCKED, and do not
represent the whole as runnable.

---

## The three findings this round that most justify its existence

Recorded together because each would have produced a **wrong published number**, not a failed run.

**1. A task that was unpassable in every condition.** C-002's answer key carried a prose `note`
inside `citation_support`, and the scorer absorbed every string there into the governing set. A
108-character English sentence became a mandatory, uncitable source; the key's own perfect answer
scored traceability **0.72** with a zero-tolerance breach. Every C-002 attempt would have failed
and been reported as a quality failure of whatever intervention happened to be running. Reading
did not find it — round-tripping the key through the live scorer did.

**2. A task that rewarded discarding 86% of its input.** B-002's required evidence all sat in the
last 13% of the document, so a compaction condition scored identically to baseline at a fraction
of the tokens. That is a **false positive for H2 and H4 manufactured by the corpus layout**. Now
measured closed: last-15% reading went 1.0000 → 0.0000, and — the half that matters equally —
content-selective retrieval still scores 1.0000 at 5.2% of the bytes, so the fix does not force
full-document reading and bias the measurement the other way.

**3. A meter that mispriced an entire provider.** `cached_tokens > input_tokens` was treated as an
error, encoding the OpenAI/DeepSeek convention as arithmetic. Anthropic reports cache reads as
**additional** — its own example has `input_tokens: 105` against `cache_read_input_tokens: 7123`.
Every cache-heavy Anthropic attempt would have raised, or been mispriced by 21% of that call.

None was found by review. All three were found by **running the thing**.

---

## Two gaps in this round's own process

Stated because a readiness report that only lists gates is easy to pass.

- **Gate 4 has no independent reviewer.** The methodology was drafted by the seat that adjudicated
  the change request. Separation held everywhere else — the Designer never saw candidate
  identity, the Judge never saw cost, the Key Builder never read the Designer's notes, the
  verifier never opened the derivation scripts — but **it did not hold for the methodology text
  itself.** That gate is PENDING for a real reason, not a formality.
- **Nothing here has been executed against a model.** Every claim is about text, arithmetic and
  code paths. The stack is better tested than it was; it remains untested against the only thing
  it exists to measure.


---

## Red Team and Reproduction — what they changed

Both seats ran after the gate table above was drafted, and both independently found the same
defect, which invalidated gate 12's evidence.

### The verdict that matters

The Red Team's words: **"NOT fit to freeze. The repair is good; the delivery is broken."**

It verified a great deal — RT-03 closed with both halves confirmed against the delivered key
(*"the best work in the round"*), the E evidence contract failing closed, the tool families now
real decoys, `manifest.py` catching all five tamper classes, four findings closed by rulings
written into the task text, 17 of 17 keys reproducing. And then: **none of the version-gated half
of that work reached a real run**, because `runner.py` stamped the wrong methodology version.

The Reproduction Agent, measuring separately, reached the same place from the other side: the run
reproduces *exactly* — every record field identical across two runs, zero packet differences, zero
score differences — and it reproduces **the wrong rulebook**.

### What has been done about it

All three BLOCKING findings and nine of the reproduction's fifteen are closed, and the Red Team's
own acceptance criterion is met:

| | Result |
|---|---|
| Golden run at the declared version | **17/17 PASS**, `Counter({'1.1.0': 17})` |
| E-002 with a violation at turn 8, final answer byte-perfect | **fails**, `zero_tolerance:constraint_violation` |
| Image | `sha256:81f8bfc61822…` reproduces twice from a pruned store, LG3 8/8 |
| Tests | 240 judge + 54 harness, including **eight seam tests** covering runner → packet → judge |
| `MANIFEST.json` | committed, zero unclaimed files, a doctored manifest now caught |

### The gate this does not clear

**Gate 17 is not re-satisfied by remediation.** The Red Team found the defects; it has not
re-tested the fixes. A repair verified only by the seat that wrote it is the exact shape of the
problem this round was called in to fix — and this coordinating seat wrote most of these fixes.

**The same applies to gate 4.** The methodology was drafted by the seat that adjudicated the
change request.

So: separation of duties held for the task set, the keys, the scorer and the semantic
verification. It did **not** hold for the methodology text, and it does not hold for this
remediation. Both are PENDING for a real reason.

---

# Verdict

## **NOT FIT TO FREEZE.** The instrument still had reproducible scoring and aggregation defects in two consecutive external reviews.

> **R2-04.** This section previously read *"a complete candidate, pending two independent reviews
> and one ruling… Everything a reviewer needs exists and is internally consistent."* Those words
> were withdrawn in `LAB_001_ADVERSARIAL_REVIEW_RESPONSE.md` **and left standing here**, in the
> document a decision is actually made from. A withdrawal that does not reach the decision
> surface has not been made. Corrected 2026-09-17 after the second review.

**Two rounds of external adversarial review, ten executable defects, all reproduced, all fixed.**
The second round found that two of the first round's fixes were incomplete in exactly the way the
first round's own commentary warned about — identity that the record asserts about itself, and a
check placed at one entrance while the arithmetic happens somewhere else.

| # | What is needed | From whom |
|---|---|---|
| 1 | **Independent re-test of the remediation** at the current head — not at `205c1b4`, `62a16a4` or `59293e8` | an executor who wrote none of it |
| 2 | **Independent methodology review** of `METHODOLOGY_v1.1.0` | Editor-in-Chief or a reviewing seat |
| 3 | **CR-002 ratified** — the run-plan unit and the research design. The 3.46× figure is an **attempt** multiplier; the dollar consequence is **withdrawn as unestablished** | Editor-in-Chief |
| 4 | **§7.6 ratified** — the INVALID re-run rule, omitted from the earlier "one ruling" claim | Editor-in-Chief |
| 5 | **RT-04 and RT-10 approved or reversed** — both departed from the instruction without being put up for approval; RT-10 raises the pass rate | Editor-in-Chief |

Pricing (gate 15) and provider-native calibration (gate 16) remain **BLOCKED** on a model
selection nobody has made and a credential nobody has issued. The live execution path (gate 20)
is **NOT BUILT** — that one is engineering work, not a blocker anyone can unblock by deciding
something.

**LG4 remains NO GO**, and would remain NO GO even if the freeze were granted tomorrow.

## The honest summary of this round

The stack is substantially better than it was and **still has not measured anything**. Two
external reviews in two days each found live defects by executing code, and the second found that
some of the first round's repairs were incomplete. **The outside defect-discovery rate has gone
6 → 3 → 2 and has not reached zero**, and that — not the test count — is the signal about
whether this instrument is ready. Its three most consequential findings — a task that was unpassable in every condition, a task that rewarded
discarding 86% of its input, and a scoring pipeline that applied the wrong rulebook to every run —
were all invisible to review and visible only to execution. Two of the three were in work this
coordinating seat did itself and was confident about.

That is the result worth carrying forward, and it is a result about the instrument, not about the
market or about token optimisation. Nothing here has spoken to a model.

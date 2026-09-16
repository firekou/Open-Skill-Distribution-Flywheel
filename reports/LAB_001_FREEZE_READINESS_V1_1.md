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
| 3 | `METHODOLOGY_v1.1.0` written and internally consistent | **PASS (as a DRAFT)** | `f4e5b65e…0774`; three drafting amendments recorded in the lock | methodology-reviewer |
| 4 | Independent methodology sign-off | **PENDING** | nobody outside the drafting seat has reviewed the text | **Editor-in-Chief** |
| 5 | RT-01 – RT-13 closed | **PASS** | closure matrix in `LAB_001_BENCHMARK_REPAIR_REPORT.md`, each row naming its proof | four seats |
| 6 | RT-14 – RT-21 dispositioned | **PASS** | 7 closed, 1 retained with its consequence written into DESIGN_NOTES | Designer / Judge |
| 7 | UG-01 – UG-33 dispositioned | **PASS** | 26 closed with clause + test; 7 retained with an argument each; the two that could hide a violation are made visible rather than waived | Quality Judge |
| 8 | 17 tasks independently semantically verified | **PASS** | `INDEPENDENT_VERIFICATION.md`: 17 of 17 agree, every value re-derived by different methods, nothing sampled | independent verifier |
| 9 | Answer keys mechanically re-derivable | **PASS** | 17/17 reproduce byte-identically from committed scripts | Answer Key Builder |
| 10 | Blind evaluation and evidence contract complete | **PASS** | salt custody written; evidence produced by a named seat; packet sufficiency asserted before the judge sees anything; 240 judge tests | Judge + harness |
| 11 | Scoring-integrity manifest | **PASS** | separate task-set / answer-key / scorer / config hashes, no self-reference, **zero unclaimed files**; modified, added and deleted all caught | harness |
| 12 | Golden end-to-end run | **PASS** | 17 of 17 correct answers pass the whole chain with real evidence, a real audit and complete turns | harness |
| 13 | Environment rebuilt and reproducible | **PASS** | `sha256:04d7fac698f8…fa68`, 13 layers, reproduces from a fully pruned store; LG3 8/8 with a working negative control | harness |
| 14 | 100-run mapping without contradiction | **PENDING** | `RUN_PLAN_v1.1.0.json` enumerates all 78 runs and 270 attempts; allocation untouched — but the **3.46× cost consequence is unratified** (`CR-002`) | **Editor-in-Chief** |
| 15 | Pricing readiness | **BLOCKED** | `PS-2026-09-16` prices 30 entries with cache rates; **3 rows BLOCKED**; and the model/plan selection that decides completeness does not exist (open item **C-a**) | Editor-in-Chief + harness |
| 16 | Provider-native meter calibration | **BLOCKED** | no benchmark credential exists. An accumulator check is not calibration | **Editor-in-Chief** |
| 17 | Independent Red Team replay | **DONE — verdict NOT FIT TO FREEZE, then remediated** | `RED_TEAM_REVIEW.md`: 3 BLOCKING, 4 MAJOR, 5 MINOR. All three blockers closed and the acceptance criterion met; **the replay has not been re-run against the remediation** | Task Red Team |
| 18 | Independent reproduction of the new environment | **DONE — image and run both reproduce exactly** | `LAB_001_REPAIR_REPRODUCTION_RESULT.md`: 15 findings, 9 remediated here. It reproduced the run perfectly and independently found that the run reproduced **the wrong rulebook** | Reproduction Agent |

---

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

## **NOT FIT TO FREEZE — a complete candidate, pending two independent reviews and one ruling**

Everything a reviewer needs exists and is internally consistent. What is missing cannot be
supplied by the seats that built it:

| # | What is needed | From whom |
|---|---|---|
| 1 | **Red Team re-test of the remediation** — the acceptance criterion is met, but by the seat that wrote the fixes | Task Red Team |
| 2 | **Independent methodology review** of `METHODOLOGY_v1.1.0` | Editor-in-Chief or a reviewing seat |
| 3 | **CR-002 ratified** — the run-plan unit and its 3.46× cost consequence | Editor-in-Chief |

Pricing (gate 15) and provider-native calibration (gate 16) remain **BLOCKED** on a model
selection nobody has made and a credential nobody has issued. Per Prompt 3.5 §9 that does not
block a freeze candidate; it blocks representing the stack as execution-ready, and it blocks the
Pilot outright.

**LG4 remains NO GO**, and would remain NO GO even if the freeze were granted tomorrow.

## The honest summary of this round

The stack is substantially better than it was and **still has not measured anything**. Its three
most consequential findings — a task that was unpassable in every condition, a task that rewarded
discarding 86% of its input, and a scoring pipeline that applied the wrong rulebook to every run —
were all invisible to review and visible only to execution. Two of the three were in work this
coordinating seat did itself and was confident about.

That is the result worth carrying forward, and it is a result about the instrument, not about the
market or about token optimisation. Nothing here has spoken to a model.

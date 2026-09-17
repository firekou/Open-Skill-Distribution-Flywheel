# Review Package — Benchmark Repair & Methodology v1.1.0

**For:** Editor-in-Chief review
**PR:** https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/1 (draft, **not merged**)
**Branch:** `claude/atk-open-skill-distribution-96e4vv` · **Head:** `205c1b4`
**Base:** `main` at `a8ca352dc64e792864f351f7775e2b21681b6390` — the commit you last read
**Size:** 13 commits, 283 files, +39,833 / −530 at `205c1b4`; the adversarial-review fixes add further commits on the same branch

**This document is self-contained.** Every number quoted here is reproducible from the branch,
and the file path is given so you can check any of it. You do not need to read the repository to
review the decisions.

---

> ## Status: revised 2026-09-17 after external adversarial review
>
> An external reviewer ran executable counterexamples against this branch and found **six live
> defects** plus four claims that had to be withdrawn. **Every one reproduced.** They are fixed,
> and `reports/LAB_001_ADVERSARIAL_REVIEW_RESPONSE.md` is the point-by-point record.
>
> **Nothing in this document is independently verified against the fixed code.** §5 explains what
> each seat's isolation does and does not license.

---

## 0. The one thing to read first

The round's headline evidence **was wrong, and an independent seat caught it.**

I reported "17 of 17 correct answers pass the whole chain" as proof the repaired harness worked.
It was true. It was also **not evidence of what I cited it for.**

`runner.py` stamped the literal `"1.0.0"` as the methodology version on every record and packet.
`judge.py` gates the entire v1.1.0 repair on that field across ~14 branches. So every real run was
scored under the **old** rulebook: absolute floors, both `count` rulings, C citation symmetry, the
corpus-integrity gate and turn completeness never executed.

**The 17/17 was caused by the defect.** The more permissive rules were selected. Forced to the
declared version, the same run gave **11/17**.

The Red Team demonstrated the consequence end to end: a zero-tolerance violation injected at
E-002 turn 8, final answer byte-perfect, run through the documented commands → **PASS**, while the
packet's own evidence held the violating text.

Two seats found this independently. Neither wrote the code. **I did**, and I was confident about
it. That is the most important fact in this package, and §5 is where it bears on what you decide.

---

## 1. Verdict

> ## NOT FIT TO FREEZE. LG4 remains NO GO.
> ## The instrument still had reproducible scoring and aggregation defects, and the reasons are worse than this document first said.

**This verdict was rewritten on 2026-09-17 after external adversarial review.** The previous
wording was:

> ~~"a complete candidate, pending two independent reviews and one ruling. Everything a reviewer
> needs exists and is internally consistent. What is missing cannot be supplied by the seats that
> built it."~~

**That was wrong, and it was wrong in the flattering direction.** It framed the gap as missing
signatures. The reviewer found six live defects by running code, not by reading it: a version
conflict that still downgraded a violation to PASS, success counts inflatable by copying a file,
a cell that failed its own verdict and was still selected as a winner to reproduce, a missing
cost read as $0, an unruled violation published as a clean PASS, and a "refusing" finalize that
wrote records before it refused.

### Four claims formally withdrawn

| Withdrawn claim | Why |
|---|---|
| "A complete and **internally consistent** candidate" | §6.1's worked example contradicted the run plan's own denominator (3 vs 12); §7.7's published tie-break named a variance term the code did not have |
| "The cross-version scoring problem is **closed**" | Moving the literal into one constant reduced the chance of mistyping it. The downgrade needed only one stale field to disagree, and `resolve_methodology_version` took the first parsable candidate and never compared the rest. **Now** closed, with a test |
| "Total cost is **3.46×**" | An experimental-subset ratio applied to a whole-project budget, with 22 runs never expanded and attempt counts treated as dollars |
| "What remains is **external review and user decisions**" | What remained was also six executable defects, two unratified rulings, one unbuilt live provider, and an unratified §7.6 — **two** rulings outstanding, not one |

### What is true after the repair

All six defects are fixed, with **12 regression tests, 9 of which fail on `62a16a4`** and pass
here; 306 tests green. **That is `AUTHOR_TESTED`, not verified** — written by the seat that wrote
the defects, which is precisely the pattern this round exists to distrust. The reviewer's closing
point stands: even a fully green instrument would only show that the tool obeys its registered
rules, not that the rules can show quality parity or a commercial saving.

---

## 2. What was asked, and what was done

| Instruction | Outcome |
|---|---|
| Preserve v1.0.0 originals | **Verified by hash.** `METHODOLOGY_v1.0.0.md` still `c1810b04…89bc`; `METER_CALIBRATION_v1.0.0.md` still `3ed9dac6…a98aa`; `TASK_SET_v1.0.0` 155/155; `git diff a8ca352..HEAD` over every v1.0.0 path is **empty**. New versions are new files; `PS-2026-09-15` keeps its id |
| Review CR-001-A/B/C | All three **UPHELD**. C **widened** beyond the request |
| Build v1.1.0 | `METHODOLOGY_v1.1.0.md`, **DRAFT / REVIEW_PENDING**, never marked FROZEN |
| Repair RT-01 – RT-21 | 13 closed with a named proof, 7 dispositioned, 1 retained with its consequence recorded |
| Handle UG-01 – UG-33 | 26 closed, 7 retained with an argument each |
| Independent Red Team | Done. Verdict: **NOT FIT TO FREEZE**, 3 BLOCKING / 4 MAJOR / 5 MINOR |
| Independent reproduction | Done. 15 findings; image and run both reproduce exactly |
| Independent semantic verification of 17 tasks | Done. **17/17 agree, zero value disagreements**, every value re-derived by different methods |
| 100-run mapping | Produced — and it raised **CR-002**, because the definition costs 3.46× |
| Do not run a Pilot, buy a licence, or claim savings | None happened |

---

## 3. The three change-request rulings

### CR-001-A — absolute quality floors. **UPHELD.**

The v1.0.0 floors for workloads A and C were relative to the baseline's own result. Two failures,
not one: a blind judge cannot compute a baseline median without learning the treatment, **and the
bar moves down with a weak baseline**.

Measured: at a C0 median of **0.70**, A-001's zero-work blanket answer — reply "all functions",
read nothing — scores **0.6667** and returned `task_success: true`.

v1.1.0 floors: A ≥ 0.95 · B ≥ 0.97 · C coverage ≥ 0.90 **and** traceability = 1.00 · D correct
tool and answer per attempt · E completion ≥ 0.95. **No floor was lowered** — these are the
v1.0.0 numbers with the baseline term removed.

The text states plainly that this **changes what the threshold means**, and that passing an
absolute floor is *minimum acceptable quality*, **not** "equal to C0".

*Found independently by three seats that never conferred.*

### CR-001-B — attempt / cell / aggregate. **UPHELD.**

Each threshold now applies at exactly one level. D's 95% is a **cell** rate: with 3 planned
attempts, **3/3 is required**. And 3/3 does not mean the true rate is ≥95% — three observations
cannot support that, and the aggregator attaches that sentence to every passing D cell so the
claim cannot be made downstream by accident.

A third outcome, **`INVALID`**, separates *"the intervention produced a worse answer"* from
*"we could not measure this attempt"*. Both stay in the denominator. An `INVALID` is not deleted,
not folded into a savings average at zero cost, and not replaced by an automatic re-run.

### CR-001-C — pricing completeness. **UPHELD and widened.**

The request asked for a completeness rule. Review added three things it did not ask for, because
the same defect class produces them: completeness judged against **what a provider can actually
return** (including automatic caching) rather than what the plan declares; **per-provider token
inclusion**; and **full cost attribution** including retries, escalations and the calls an
intervention itself makes.

Enforced by a blocking preflight. A missing rate is **never zero**; `not_applicable` requires the
vendor sentence as evidence; unpriceable usage is recorded and **never estimated**.

---

## 4. CR-002 — raised, not absorbed. **This is decision #1 for you.**

The frozen §5 allocates 100 runs and **never says what a run is.** Invisible while no task set
existed; decisive with 17 tasks.

| Reading | Result |
|---|---|
| A run = one task attempt | **Impossible** — C0 has 15 runs for 17 tasks |
| A run = one (workload, condition, repetition) unit attempting every task in that workload | **Fits exactly** |

78 experimental + 22 guardrail = **100 runs. Allocation untouched.** But **270 task attempts**, a
mean of **3.46 per run**.

**Every prior cost figure assumed one attempt per run.** So **$51–94 becomes ≈ $177–325**, and the
8–16 hour estimate scales with it.

Four options are costed in `methodology/METHODOLOGY_CHANGE_REQUEST_002.md`:

| # | Option | Attempts | What it costs you |
|---|---|--:|---|
| **1** | Ratify as proposed — full coverage | 270 | ~3.46× the earlier estimate |
| 2 | One designated task per workload; others C0 only | ~117 | Cheapest, but **drops the within-workload variance the repetitions exist to measure** |
| 3 | 3 → 2 repetitions, full coverage | 180 | **Changes the frozen allocation** — needs its own change request |
| 4 | Shrink the task set to 100 attempts | 100 | Discards tasks four seats built and attacked. Not recommended |

**Recommendation: option 1.** Option 2 is the honest fallback if the budget will not carry it, and
its cost is measurement quality, which must then be stated in any result derived from it.

The run-plan-mapping gate is **PENDING**, not PASS, until this is ruled on.

---

## 5. What separation of duties caught — and where it did not hold

Six seats, deliberately isolated. **Every one of them found something the others could not.**

**Corrected 2026-09-17.** The table below previously carried only *Isolation* and *Found*, and
every repaired item was marked **CLOSED**. External review pointed out that one word was doing
two different jobs: "I fixed it and tested it" and "somebody else confirmed it" both read as
CLOSED. They are now separated, and a third column names **what each seat's isolation does and
does not license**. Nothing in this table is independently verified.

| Seat | Isolation — and its limit | Found | Strongest status it can confer |
|---|---|---|---|
| Task Set Designer | Never saw candidate identity. **Did not verify its own rebuild** | Rebuilt B-002; wrote four ambiguities out of the task text | AUTHOR_TESTED |
| Answer Key Builder | Never read the designer's notes | **C-002 was unpassable in every condition** | AUTHOR_TESTED |
| Quality Judge | Never saw cost or candidate identity. **Blind to cost ≠ blind to its own implementation** — it scored code it wrote | 33 underspecified metrics; its own per-field citation rule was a no-op | AUTHOR_TESTED |
| Semantic Verifier | Never opened the derivation scripts. Licenses the **answer values**, says nothing about scorer or runner | C-001's source mapping was under-determined | INDEPENDENTLY_VERIFIED — *for answer values only* |
| Task Red Team | Authored none of it. **Reviewed `205c1b4`, i.e. pre-remediation** | **The version mis-stamp** | INDEPENDENTLY_VERIFIED — *of the pre-fix state only* |
| Reproduction Agent | Reproduced nobody's own run. **Reproduced the OLD image and OLD chain** | Same defect from the other side, plus 14 more | INDEPENDENTLY_VERIFIED — *of the pre-fix state only* |
| **Coordinator / integration author** | **None. Not previously listed at all** | Wrote the remediation for every blocker above | **AUTHOR_FIXED — cannot confer more** |

**The row that was missing is the one that matters.** The seat that wrote the critical fixes was
not in the six-seat table, and its work was recorded as CLOSED alongside genuinely independent
findings. The three-status vocabulary now in use:

| Status | Meaning |
|---|---|
| `AUTHOR_FIXED` | changed by the seat that wrote the defect; no test binding it |
| `AUTHOR_TESTED` | that seat wrote a test that fails before and passes after |
| `INDEPENDENTLY_VERIFIED` | a seat that wrote neither the code nor the test confirmed it, **at a named commit** |

**Every ADV fix from the 2026-09-17 review is `AUTHOR_TESTED`. Nothing in this branch is
`INDEPENDENTLY_VERIFIED` against the post-fix code.** Two isolations that cannot substitute for
each other: "the judge never saw cost" is blind evaluation, not independence from its own
implementation; "the verifier never read the derivation scripts" licenses the answer values, not
the scorer.

### Where it did NOT hold, and this is decision #2 and #3

1. **The methodology was drafted by the seat that adjudicated the change request.** No independent
   reviewer has read `METHODOLOGY_v1.1.0.md`.
2. **The remediation was written by the coordinating seat.** The Red Team found the three
   blockers; **it has not re-tested the fixes.** Its acceptance criterion is met — by the person
   who wrote them.
3. **Both independent reviews are of a commit that no longer exists as current.** The Red Team
   reviewed pre-remediation code; the Reproduction Agent reproduced the pre-remediation image.
   Neither has seen the version fix, the six ADV fixes, or the corrected task set. **An
   independent review of an old commit does not transfer to a new one.**

A repair verified only by its author is the exact shape of the problem this round was called in to
fix. Both gates are PENDING for that reason, not as a formality.

---

## 6. Three findings that would each have produced a wrong published number

Not failed runs — **wrong numbers that looked right.**

**1. A task that was unpassable in every condition.** C-002's answer key carried a prose `note`
string inside `citation_support`, and the scorer absorbed every string there into the set of
required citations. A 108-character English sentence became a **mandatory, uncitable source**. The
key's own perfect answer scored traceability **0.72** with a zero-tolerance breach. Every C-002
attempt would have failed and been reported as a quality failure of whatever intervention was
running. *Reading found nothing; round-tripping the key through the live scorer found it.*

**2. A task that rewarded discarding 86% of its input.** B-002's required evidence all sat in the
last 13% of a 147 KB document, so a compaction condition scored identically to baseline at a
fraction of the tokens — **a false H2/H4 positive manufactured by corpus layout.** The document
was rebuilt, and both halves measured:

| Strategy | v1.0.0 | v1.1.0 |
|---|--:|--:|
| Last 15% only | 1.0000 pass | **0.0000 fail** |
| Ends-only compaction | 1.0000 pass | **0.0000 fail** |
| Fixed truncation, first 50% | 0.0000 | 0.2421 |
| **Content-selective retrieval** | 1.0000 | **1.0000 at 5.2% of bytes** |

The last row matters as much as the first: the fix punishes truncation **without** forcing
full-document reading, which would have biased the measurement the other way.

**3. A meter that mispriced an entire provider.** `cached_tokens > input_tokens` was treated as an
error — encoding the OpenAI/DeepSeek convention as if it were arithmetic. Anthropic reports cache
reads as **additional** to input; its own example has `input_tokens: 105` against
`cache_read_input_tokens: 7123`. Every cache-heavy Anthropic attempt would have raised, or been
"fixed" by folding the fields and mispricing by **21%** of that call.

**None was found by review. All three were found by running the thing.**

---

## 7. Where to attack this

Please be adversarial about these specifically.

1. **Is "17/17 PASS" trustworthy now, or is it green for a new reason?** That is exactly how it
   failed last time. The acceptance criterion is: 17/17 **with every packet resolving
   `methodology_version 1.1.0`**, and a violation injected at E-002 turn 8 must fail. Both hold —
   but verified by the seat that wrote the fix.
2. **Four changes raise the pass rate**, all declared, none undeclared, no floor moved:
   B-002 `count` 0.9500 fail → 0.9945 pass · A's count penalty 0.05 → 0.02 (a genuine A-001 miss
   0.9420 → 0.9720) · C's count penalty removed (an omitted record 0.8875 → 0.9375) · an extra key
   in a D reply 0.0 → 1.0. **Is the net direction acceptable?** An earlier draft of the repair
   report claimed one of these was "the single change most in need of a second opinion" and that
   "workload C is now strictly harder". The Red Team measured both claims false; both are
   withdrawn in the committed report.
3. **Is the absolute-floor change too strict, too lax, or right?** It is a semantic change. It
   makes A-001's zero-work answer fail at any baseline, which is the intent — but check the other
   floors against the tasks as they now stand.
4. **Two task-text rulings were made by a seat, not by you**, both quantified in the task text:
   a wrong `count` is not equivalent to a 3%-wrong extraction (RT-10), and a low-authority file
   stating the correct value is **not** a valid citation (RT-04). Both are reversible.
5. **The retained UG items.** 7 of 33 are kept as limitations. The two that could in principle
   hide a zero-tolerance violation are **not** waived: every prose mention that did not fire is
   recorded per turn and flagged for adjudication before its cell may be reported. Is that
   sufficient, or should they block?

---

## 8. What is BLOCKED, and on what

| Gate | Status | Blocked on |
|---|---|---|
| Pricing completeness | **BLOCKED** | Which models and API plans the run plan will use — a decision nobody has made. 3 rows also genuinely unreadable from the vendor page and reported **BLOCKED** rather than trimmed away to reach a PASS |
| Provider-native meter calibration | **BLOCKED** | A lab-scoped, spend-limited benchmark credential. **An offline accumulator check is not calibration**, and the report says so |

Per your §9, neither blocks a freeze *candidate*. Both block representing the stack as
execution-ready, and both block the Pilot outright.

Two vendor findings worth your attention:

- **All eight OpenAI models in the old snapshot still exist at unchanged prices, but none is a
  flagship any more.** The C4 tier-adjacent pairs were reasoned about against a lineup that has
  moved.
- **Anthropic states that Claude 4.7 and later use a tokenizer producing ~30% more tokens for the
  same text.** So token deltas are not comparable across that boundary — **within** one provider.
  v1.0.0 barred only cross-*provider* token deltas; that was too narrow. Cost stays comparable.

---

## 9. What is actually yours to decide — corrected 2026-09-17

The previous version of this section put **five** items to you. External review found that only
two were genuinely yours; two were work already authorised that was being handed back, and one
had effectively been decided already and was presented as an open question.

### Genuinely yours

| # | Decision | What you are choosing | What I recommend |
|---|---|---|---|
| **1** | **CR-002 — the research design** | Full factorial (270 experimental attempts) vs staged (73, then decide) vs the three cheaper designs | **Option 5, then option 1 if stage 1 justifies it.** Changed from "option 1" — with the dollar figures withdrawn, ratifying the most expensive design on an unquantified budget is not supportable. Stage 1 keeps every task and produces the per-attempt cost that would make option 1 pricable |
| **2** | **The non-inferiority margin** — how much quality loss is acceptable | A business judgement. Nobody else can set it | Must be fixed **before** any number exists. Until it is, only descriptive figures may be published and "quality was not sacrificed" may not be written in any form. **The statistical method and sample requirement are mine to propose, not yours to invent — see below** |
| **3** | **Spend and commercial representativeness** for the model lineup | Which vendors and plans represent the buying decision you care about, and the ceiling | The **technical shortlist is mine**, and its absence was my gap, not a question |

### Not yours — already authorised, and being done rather than asked about

| # | Item | Why it was wrong to ask |
|---|---|---|
| **4** | ~~"Assign an independent seat to re-test the remediation"~~ | Prompt 3.5 already authorises it. Scheduling an independent seat is coordination work, which is my job. It comes back to you **only** if no independent executor can be obtained — and then as a named resource blocker, not an open question |
| **5** | ~~"Assign an independent methodology reviewer"~~ | Same. The technical review can be prepared and run here; what is genuinely yours is the **policy choice and the formal sign-off**, not the assignment |

### Newly yours, because a seat decided them without asking

| # | Item | What happened |
|---|---|---|
| **6** | **RT-04** — low-authority sources | The instruction said a low-authority source genuinely supporting a correct claim must not fail on source type alone. The seat ruled the opposite and marked it CLOSED. **Approve or reverse** |
| **7** | **RT-10** — `count` re-weighting | The instruction said keep the rule by default and review alternatives separately. The seat re-weighted immediately. **It raises the pass rate** (B-002: 0.95 fail → 0.9945 pass). **Approve or reverse** |
| **8** | **§7.6** — the INVALID re-run rule | Marked "needs ratification" in the methodology and omitted from the earlier "one ruling outstanding" claim |

### What I owe you before decision 1 or 2 can be answered

Neither is answerable as a bare question, and presenting them as such pushed my work to you:

1. **A per-workload, per-condition cost model** — calls, context length, cache state, price per
   attempt. Turns an attempt count into a dollar range. Partly **BLOCKED** on the three BLOCKED
   pricing rows, and buildable for the rest.
2. **A candidate model/plan shortlist with comparable pairings**, re-derived against the current
   lineup, not spanning the Anthropic tokenizer boundary if a token delta is to be reported.
3. **A statistical proposal for the non-inferiority test** — the design, the sample size each
   candidate margin needs, and plainly whether this run plan can support the margin at all.
   **Under option 5 stage 1 it cannot: one observation per cell has no variance.** You should be
   choosing a margin against a method that tells you what it costs, not in a vacuum.

---

## 10. What this round did not do

No benchmark run · no pilot · no candidate executed · **no model contacted at any point** · no
licence purchased · no candidate substituted (NadirClaw's cells remain `FAILED / LICENSE`) · no
hypothesis confidence raised · no product built · nothing marked VERIFIED or REPRODUCED · not
merged to `main`.

### And one thing it did not build, which was not disclosed as a build task

**The live execution path does not exist.** `providers.LiveProvider.run_task()` raises
`NotImplementedError` and `runner.py` constructs a `ReplayProvider` unconditionally. Every
`PASS` in this branch is a replay of a known-correct answer through the scoring chain.

This matters because it was filed under "blocked on a credential". **It is not.** Issue the
credential, choose the model, unblock all three pricing rows, and there would still be no agent
loop to run a task with. That is engineering work nobody has scheduled, and presenting the gap as
purely a resourcing and adjudication problem understated what stands between this branch and a
first real attempt. Recorded as gate 20, **NOT BUILT** (external adversarial review, 2026-09-17).

A new hypothesis **H011** was recorded at **H0 Idea** — that ATK's value may develop
Measurement → Verification → Quality-adjusted Economics → Routing — together with a long list of
what it is *not* supported by. Finding 44 defects in one's own instrument is evidence about the
instrument. It says nothing about market demand, willingness to pay, competitive advantage, or
ATK's ability to deliver savings. **If a good repair round were market evidence, every well-run
lab would be a business.**

---

## 11. Honest summary

The stack is substantially better than it was and **has still not measured anything**.

Its three most consequential findings were all invisible to review and visible only to execution.
**Two of the three were in work the coordinating seat did itself and was confident about.**

The pattern from the previous round held and generalised: *two halves built by different seats,
each correct in isolation.* What was new is that **the integration proof itself was one of the
halves** — a test that runs the whole chain is not a seam test unless something asserts which
rules the chain applied.

---

## Appendix — where to find things

| | |
|---|---|
| Adjudication of CR-001-A/B/C | `benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_CHANGE_REVIEW_001.md` |
| The v1.1.0 draft | `…/methodology/METHODOLOGY_v1.1.0.md` (`75676732…fcc1`; was `f4e5b65e…0774` at `62a16a4`) |
| CR-002 with four costed options | `…/methodology/METHODOLOGY_CHANGE_REQUEST_002.md` |
| RT/UG closure matrix + Red Team addendum | `reports/LAB_001_BENCHMARK_REPAIR_REPORT.md` |
| Methodology, unit, 100-run mapping, statistical limits | `reports/LAB_001_METHODOLOGY_V1_1_REVIEW.md` |
| Gate table and verdict | `reports/LAB_001_FREEZE_READINESS_V1_1.md` |
| Red Team replay (21 originals + 12 new) | `…/tasks/TASK_SET_v1.1.0/RED_TEAM_REVIEW.md` |
| Independent semantic verification of 17 tasks | `…/tasks/TASK_SET_v1.1.0/INDEPENDENT_VERIFICATION.md` |
| Independent reproduction, 15 findings | `reports/LAB_001_REPAIR_REPRODUCTION_RESULT.md` |
| B-002 shortcut probe numbers | `…/tasks/TASK_SET_v1.1.0/SHORTCUT_PROBE_RESULTS.md` |
| Every command from a clean checkout | `…/RUNBOOK.md` |
| New pricing snapshot, 30 entries | `…/evidence/PRICING_SNAPSHOT_PS-2026-09-16.{json,md}` |
| All 78 runs and 270 attempts enumerated | `…/RUN_PLAN_v1.1.0.json` |
| Evidence / Decision / Hypothesis ledgers | `ledgers/` — E043, E044, D029, H011 are this round's |

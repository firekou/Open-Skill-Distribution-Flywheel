# Response to the external adversarial review of `62a16a4`

**Review received:** 2026-09-17 · **Reviewed commit:** `62a16a43fc70477f48aab1a2c779cbc4204a6d08`
**Responding seat:** the coordinating seat — **the seat that wrote most of the defects below.**
That is worth stating first: this is a self-assessment of an external critique, which is the
weakest possible standing for the words "fixed" and "closed".

---

## The short version

**Every executable finding reproduced. I accept all of them. None is disputed.**

The review found six defects by running code, and its central charge is correct: the previous
report described the remaining work as *signatures and budget*, when in fact the instrument still
mis-scored, over-counted, mis-selected, mis-priced and published unruled results.

**It also caught me repeating the exact error the round was convened to fix.** The version
mis-stamp was the round's headline finding. I fixed the symptom — one constant instead of a
literal — and wrote that the class of defect was closed. It was not: `resolve_methodology_version`
took the first parsable version field and never compared the others, so one stale field still
downgraded a violation to PASS. **I declared a root cause closed while the root cause was a
one-field disagreement away from firing again.**

---

## 1. Findings, reproduced

I re-ran every executable case before changing anything. Results on `62a16a4`:

| # | Finding | Reproduced? | Observed on `62a16a4` |
|---|---|---|---|
| **ADV-A** | Duplicated records manufacture successes | **Yes** | One PASS copied 3× → `3/3 PASS`. Copied 4× → `success_rate 1.3333`, still `PASS` |
| **ADV-B** | A failed cell is selected as a winner | **Yes** | 1 of 3 planned recorded → `verdict FAIL`, `select_strongest` → `[('D','C1')]` |
| **ADV-C** | Missing cost reads as zero | **Yes** | `cost_per_successful_task` → `0.0` |
| **ADV-D** | Unadjudicated violation published as PASS | **Yes** | attempt `PASS` with `unadjudicated_mentions` non-empty; cell `PASS` |
| **ADV-E** | Live provider not implemented | **Yes** (static) | `LiveProvider.run_task()` raises `NotImplementedError`; `runner.py` always builds `ReplayProvider` |
| **ADV-F** | Methodology internally inconsistent | **Yes** (static) | §6.1 worked example says D denominator 3; run plan says 12. §7.7 names a variance tie-break the sort key omits. §7.6 pending, never disclosed |
| **ADV-G** | `finalize` writes before it refuses | **Yes** (static) | the `missing` check ran *after* the write loop |
| **ADV-05** | Version conflict still downgrades | **Yes** | top-level `1.0.0` + key/evidence `1.1.0` → **PASS**, 1 turn checked. Declared `1.1.0` → `FAIL_QUALITY` |

The reviewer flagged ADV-G as read-only because `jsonschema` was missing locally. **It is
confirmed here**: the refusal genuinely ran after the writes.

---

## 2. What changed

All fixes are in `environment/harness/`. **Each has a regression test that fails on `62a16a4`.**

| Finding | Fix | Test |
|---|---|---|
| ADV-A | `attempt_identity()`; `build_cells` refuses duplicates and over-count; `Cell.verdict()` refuses duplicates **again**, because the rate is computed there and a defence guarding one entrance is not a defence | 4 tests, incl. one proving a *distinct* full cell still passes |
| ADV-B | `select_strongest` reads the cell's **own verdict** instead of re-scanning records. The two answers can no longer disagree | 1 |
| ADV-C | `cost_per_successful_task` raises on any attempt with no cost. An unpriced cell is unpriceable, not free | 1 |
| ADV-D | `pending_adjudication` lifted from `detail` to the top level of the score, carried through `finalize`, **gated** in `Cell.verdict()` | 1 |
| ADV-F | §6.1 corrected to 12; §7.7's variance term added to the sort key (absent variance sorts last, never as zero) | 1 |
| ADV-G | `finalize` resolves the whole batch first and writes only if every record has a matching score; **also** now refuses a score whose methodology version or scorer hash disagrees with the record | covered by existing finalize tests |
| ADV-05 | `resolve_methodology_version` collects **every** version field and refuses on disagreement, classified **INVALID** — not measured under any rulebook | 4 |

```
Ran 306 tests — OK          (was 294; +12 regression tests)
New tests against 62a16a4:   9 of 12 FAIL
The 3 that pass are deliberate controls: a distinct full cell must still
pass, a real violation must still fail, agreeing versions must still score.
```

**A fix with no test that fails beforehand is a claim, not a repair.** That is the standard I
failed to meet on the version defect, so it is the standard applied here.

---

## 3. Claims withdrawn

| Claim | Where | Status |
|---|---|---|
| "A complete and internally consistent candidate" | review package §1 | **WITHDRAWN** — §6.1 and §7.7 each contradicted the implementation |
| "The cross-version scoring problem is closed" | repair report NEW-01 | **WITHDRAWN**, then made true with a test |
| "Total cost is 3.46× ($177–325)" | CR-002, methodology §5.1, run plan, lock, freeze record | **WITHDRAWN** — no dollar figure is available |
| "What remains is external review and user decisions" | review package §1 | **WITHDRAWN** |
| "RT-04 / RT-10 CLOSED (ruled)" | repair report | **Reclassified DEVIATION — not approved** |

### On 3.46 specifically

The reviewer's arithmetic is right and mine was wrong. 270 ÷ 78 is an **experimental-subset**
ratio; it was applied to a budget covering **all 100 runs**; the 22 guardrail runs were never
expanded into attempts; and an attempt multiplier is not a dollar multiplier, because an E
attempt accumulating 16 turns of context does not cost what a B attempt costs.

**Established:** the experimental workload is 270 task attempts.
**Not established:** any dollar or wall-time figure. CR-002 now says so and lists the work needed.

I have not adopted the reviewer's 2.92 as a replacement, and they did not offer it as one — it
rests on the same false uniformity assumption. **The honest output is a withdrawal, not a
different number.**

### On the missing cheaper option

CR-002 offered "run everything" or "throw tasks away", and argued against shrinking because four
seats had built the task set. **That is a sunk-cost argument and it should not have been in a
decision document.** Keeping the task set and paying for every attempt this round are separate
questions. **Option 5** (full task coverage, single interventions, one repetition — **73**
experimental attempts, staged with pre-registered rules for what follows) is now in CR-002, and
the recommendation has changed to it. Two further designs are named.

---

## 4. Findings I am recording rather than fixing

| Finding | Why not fixed here |
|---|---|
| **ADV-E — live provider** | Real engineering, and the round is explicitly barred from live execution. **Filed as gate 20, NOT BUILT.** The correction is that it was described as blocked on a credential when it is unbuilt code: credential plus model plus pricing still yields no agent loop |
| **Golden run is synthetic** | Accepted in full. The reviewer is right that D's audit is script-assembled and marked `synthetic: True`, that E's intermediate turns are placeholders, and that the reader reads only the first declared file. It supports "known answers traverse the pipeline" — **not** "real agent tool-use and multi-turn behaviour are verified". Gate 12 is now **SUPERSEDED** |
| **RT-04, RT-10, §7.6** | Not mine to rule on. Reclassified as open decisions §9 items 6–8 |

---

## 5. What I did *not* verify

- **No independent re-test.** Every fix is `AUTHOR_TESTED` — same seat, same day.
- **No rebuild.** The container digest in gate 13 predates all of this and is **INVALIDATED**.
- **No re-run of the full golden chain** against the fixed code.
- **No re-derivation of the 17 answer values.** Untouched here; their independent verification
  still stands, and it only ever licensed the values.

---

## 6. Where the reviewer and I differ — and it is not a defence

None of the six defects is disputed. One framing point is worth stating precisely.

The review says the earlier report "omitted" that the old `golden_run.py` fabricated corpus-read
audit entries. **The substance is right and the omission is real** — the review package's §0
carried only the version mis-stamp, and a reader of that section alone would not learn it. It was
disclosed as NEW-03 in the detailed repair report. **A disclosure buried one document deeper than
the finding it belongs with is a weak disclosure**, and the fix is to raise it, not to argue
about where it was already written. Gate 12's status now carries it.

---

## 7. What this still does not mean

Six defects closed with tests is a better instrument. It is **not**:

- evidence that the benchmark measures what it claims;
- evidence for H1–H4, or for any hypothesis in the ledger;
- grounds to raise any confidence level;
- a reason to freeze, pilot, or quote a saving.

The reviewer's closing line is the right one to end on: even if every gate passed, that would
show the tool obeys its own registered rules. **Whether those rules can demonstrate quality
parity or a commercial saving is a separate question, and no work in this branch has touched it.**

**Verdict unchanged: NOT FIT TO FREEZE. LG4 NO GO.**

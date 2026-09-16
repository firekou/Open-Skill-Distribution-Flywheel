# Lab 001 — Benchmark Repair Report

**Round:** Prompt 3.5 · **Source commit:** `a8ca352dc64e792864f351f7775e2b21681b6390`
**Branch:** `claude/atk-open-skill-distribution-96e4vv` — **not merged to main**
**Scope:** closure matrix for RT-01–RT-21 and UG-01–UG-33

> **Nothing here is a benchmark result.** No model was called, no candidate executed, no pilot
> run performed. Every entry below is about the machinery.

---

## How to read the status column

| Status | Meaning |
|---|---|
| **CLOSED** | Repaired, and a test or measurement distinguishes correct from incorrect behaviour |
| **CLOSED (ruled)** | Settled by a written ruling in the task text or methodology, with the effect quantified |
| **RETAINED** | Deliberately kept as a limitation, with an argument for why it cannot hide a defect |
| **OPEN** | Not fixed. Named, with what it blocks |

A finding marked CLOSED without a test that would fail against the old code is not closed. Every
CLOSED row below names its proof.

---

## RT-01 – RT-13

| id | sev | status | what was done | proof |
|---|---|---|---|---|
| **RT-01** | BLOCKING | **CLOSED** | `required_evidence` has an owner: `harness-evidence-producer` (`harness/evidence.py`). Static facts derive from the frozen corpus (`ast` parse, frozen CSVs); dynamic facts from the runner's audit. **Never from the model's output.** Empty fails closed; cross-run audit entries are filtered out; an unattributable entry is refused; evidence is machine-checked treatment-neutral | End-to-end dry run: 10/10 attempts carry real evidence — 394 valid symbols for A, 18 and 16 turns for E, tool calls for A and D, corpus hashes for all. Previously **10 of 17 byte-perfect answers failed at score 0.0** |
| **RT-02** | BLOCKING | **CLOSED** | Fail-closed on **content**, not type. Empty `shifts`/`roster`/`catalog_part_ids` now yield `INVALID`. `part_id_pattern` removed and replaced by a scanner derived from the frozen id lists, so no configuration can disarm a check | A breaching **and** a legitimate case for every violation class per E task (E-001 V1–V6, E-002 V1–V5, E-003 V1–V6), plus a test that five spellings of the old regex — including the anchored `^KP-\d{4}$` that used to disarm V1/V3 — all give one identical verdict |
| **RT-03** | BLOCKING | **CLOSED** | The workload-B document was **rebuilt**, not rearranged: one appendix became four per-quarter registers at 22/40/60/80%, a superseding amendments layer at 95%, correction notices at 98%, precedence at 2%, and 48 per-incident narratives in between. One amendment *withdraws* an incident that would otherwise be in the answer | Shortcut probe, each strategy at its ceiling: **last 15% only 1.0000 → 0.0000**; ends-only compaction **1.0000 → 0.0000**; 50% truncation 0.0000 → 0.2421; **content-selective retrieval 1.0000 → 1.0000 at 5.2% of bytes** |
| **RT-04** | BLOCKING | **CLOSED (ruled)** | A three-part rule in all three C prompts separating **(a) source authority, (b) whether the value is correct, (c) whether the citation supports the claim**, plus a per-task claim-to-source mapping and a conflict-precedence rule. Ruled in advance: a low-authority file stating the correct value is **not** a valid citation. Made symmetric — `traceability = supported / (total + missing)`, so incomplete citation now costs | Judge implements the symmetric rule; the ruling is in the task text, where two judges read the same words |
| **RT-05** | MAJOR | **CLOSED** via CR-001-A | Absolute floors replace baseline-relative ones. Handled as a methodology change, not a seat-level edit | `TestAcceptanceCR001A` A-1…A-6. **A-3** asserts the blanket 0.6667 answer fails at any baseline **and** that v1.0.0 still passes it at a C0 median of 0.70 — the defect preserved as a test |
| **RT-06** | MAJOR | **CLOSED** | `procurement_policy.md` P1 names the four rounding points and declares every per-vendor apportionment intermediate; P4 makes freight one component total summed from full-precision products | `1197.39` is no longer defensible — the two readings cannot coexist, rather than the key picking one |
| **RT-07** | MAJOR | **CLOSED** | `amendments_in_force_on_as_of_date` given a fixed `Amendment No. n` form and exempted from N4; new rule **N4a** fixes the extent of `governing_law` and `jurisdiction_city` to the bare name | N4 and the prompt's own example no longer contradict. Previously each reading alone scored 0.9722 and passed, **both together 0.9444 and failed** |
| **RT-08** | MAJOR | **CLOSED** | Evaluated, not declared away. All 17 tasks name `corpus_hashes_before`/`corpus_hashes_after`; the harness hashes before and after every attempt and a difference fails it. A-001's corpus-read guard uses `corpus_access_log`, built from the runner's audit | `test_a_modified_corpus_fails_every_workload_not_only_d`, `test_a001_answer_produced_without_reading_the_corpus_fails`, plus a test that v1.0.0 did **not** evaluate it outside D |
| **RT-09** | MAJOR | **CLOSED** | The undeclared 0.05 `count` penalty removed from workload C. The task text is authoritative and states no penalty | `test_RT09_workload_c_count_changes_nothing_under_v1_1_0` beside `test_RT09_v1_0_0_still_reproduces_the_0_95` |
| **RT-10** | MAJOR | **CLOSED (ruled)** | The **Designer** ruled, not the judge: a wrong `count` is **not** equivalent to a 3%-wrong extraction. In B it is one comparable cell; in A it subtracts 0.02; in C nothing. Floor unchanged at 0.97 | Effect quantified in the task text: a perfect-but-wrong-count B-002 answer goes 0.95 (fail) → 0.9945 (pass). **This raises the pass rate and is flagged as the change to be most suspicious of** |
| **RT-11** | MAJOR | **CLOSED** | Eight non-competing tools moved out of contested families; `calendar.get_calendar_period` **added** so `calendar-period-resolution` is a real two-member decoy rather than a family of one. 84 → 85 tools, 25 → 28 families | Every remaining contested member called live and confirmed to return a plausible competing payload. All four D answers and `required_tools` sets **unchanged** |
| **RT-12** | MAJOR | **CLOSED** | `harness/manifest.py`: separate `task_set_hash`, `answer_key_hash`, `answer_key_scripts_hash`, `scoring_spec_hash`, `scorer_hash`, `config_hash` over disjoint groups, no self-reference, and it walks the filesystem so additions and deletions are caught | Verified against all four cases the v1.0.0 manifest missed: a **modified answer key**, an **added** key, a **deleted** task, a **modified scorer**. The old manifest covered 155 files and **not one answer key** |
| **RT-13** | MAJOR | **CLOSED** | Turn counts frozen in the scorer so no packet can shrink the requirement; the packet builder asserts `len(turns) == turn_count`; harness-captured turns preferred over the agent's own | `test_a_byte_perfect_runbook_without_turns_cannot_score_1_0` beside `test_v1_0_0_still_replays_the_old_verdict` (1.0 / pass). Truncated, reordered and duplicated transcripts all rejected — and this fired for real during the dry run, on a 6-turn fixture against a declared 18 |

## RT-14 – RT-21 — every one with a disposition

| id | sev | status | disposition |
|---|---|---|---|
| **RT-14** | MINOR | **CLOSED** | The "about 0.5 F1" claim in A-001's notes and DESIGN_NOTES §2 corrected to the measured **0.6667**. It mattered because A-001's floor used to be relative |
| **RT-15** | MINOR | **CLOSED** | E-002's self-contradicting metric ("5 comparable cells … counts as 6 - use 6") rewritten to "6 comparable cells". Judge implements 6 |
| **RT-16** | MINOR | **CLOSED (ruled)** | C-003's `contradicted_by` settled on the **literal** reading, which includes `registry_export_2032-02.csv`. One sentence, in the task |
| **RT-17** | MINOR | **CLOSED** | `retryable`, `TransientError`, `ConfigError`, `instrumented` and `deprecated` defined. **0 of 75 modules now fail to import, was 36.** All four A answers byte-identical; function count 394 → 397, all additions under `util/` |
| **RT-18** | MINOR | **CLOSED** | SCORING_SPEC §8 states the real count: **228** |
| **RT-19** | MINOR | **CLOSED** | Both dead instruction branches removed by *generalising* the rule rather than deleting the branch. They cost tokens to reason about, which is itself a cost term in a token-efficiency benchmark |
| **RT-20** | MINOR | **RETAINED, with the consequence written down** | Every D decoy still announces itself twice. Kept deliberately — but DESIGN_NOTES §5 now records that a D wrong-tool failure is evidence about **schema visibility** (the H1 question) and nothing else, so the result cannot be over-read |
| **RT-21** | MINOR | **CLOSED** | `seq` is now continuous across processes, seeded from the lines already in the file. Fixed together with a gap neither seat could see alone: **the server wrote no `run_id`**, so the Evidence Producer would have refused every real audit entry as unattributable |

## The two findings that were not on anyone's list

Both surfaced only because two halves built by different seats were wired together.

| | Finding | Why it matters |
|---|---|---|
| **1** | **The tool server wrote no `run_id`.** The Evidence Producer refuses unattributable entries; the server produced nothing else | Each half looked correct in isolation. A shared audit log would have made every workload-A and workload-D attempt `INVALID` |
| **2** | **`meter.py` treated `cached_tokens > input_tokens` as an error**, encoding the OpenAI/DeepSeek convention as arithmetic | It is wrong for Anthropic, where cache reads are **additional** to input — the vendor's own example has `input_tokens: 105` against `cache_read_input_tokens: 7123`. Every cache-heavy Anthropic attempt would have raised, or been "fixed" by folding the fields and mispricing by **21%** of that call. Token inclusion is now declared per model in the snapshot with the vendor sentence as evidence, and an undeclared model is refused |

## UG-01 – UG-33

**26 closed, 7 retained.** Full per-item detail with clause and test references is in
`tasks/TASK_SET_v1.1.0/SCORING_SPEC.md` §9. Ownership split: 16 were task-text defects fixed by
the Designer, the rest were scorer-side.

### The seven retained, and why none can hide a defect

| id | Retained rule | Why it is safe |
|---|---|---|
| **UG-01** | Lenient extraction of a JSON answer from surrounding prose or a code fence | Errs toward **accepting** a legitimate answer. A strict rule would fail correct runs for formatting |
| **UG-04** | A non-string entry in a symbol list counts as a fabrication | Harsh, and harsh in the safe direction |
| **UG-15** | Tier-name spelling normalised | Cannot change which tier is meant |
| **UG-18** | Five calls to one wrong tool count as five invocations | Only affects a count that is already zero-tolerance at one |
| **UG-23** | "Timestamp" defined as a token carrying both a date and a time of day | A bare date is not a timestamp; the narrower reading could only fail correct answers |
| **UG-22** | "Named as a step to be performed" is not mechanically decidable from prose | **Not waved through** — see below |
| **UG-24** | "Naming the vendor in prose is not a violation" needs a mechanical separator | **Not waved through** — see below |

**UG-22 and UG-24 are the only two that could in principle let a zero-tolerance violation go
undetected**, so they are not closed as limitations. Instead every prose mention of a scoped
service or an excluded vendor that did **not** fire a violation is recorded per turn in
`detail.unadjudicated_mentions`. An attempt carrying a non-empty list is **flagged for Red Team
adjudication before its cell may be reported**, and a confirmed violation re-enters through
`precomputed_violations` by **union**, never replacement. A miss is therefore visible and
recoverable rather than silent.

---

## Changes a reviewer should push back on if they disagree

Recorded because a repair round that only lists wins is not a report.

1. **RT-10 raises the pass rate.** No floor was lowered and no task weakened, but a
   perfect-but-wrong-count B-002 answer moves from fail to pass. The effect is quantified inside
   the task text. This is the single change most in need of a second opinion.
2. **Workload C is now strictly harder.** Incomplete `sources` used to be free. That is the price
   of removing an asymmetry that penalised only broad retrieval; the lever for easing C is the
   coverage floor, not the rule.
3. **Two judge-adopted rules were overruled by the Designer**, explicitly: UG-19 (an extra key in
   a D reply is no longer fatal — D measures tool selection, so an extra key is a confound) and
   UG-27 (the turn-16 `max_shifts` override is stated in the task rather than read from evidence
   that could go missing and take a violation class with it — the RT-02 failure mode).
4. **`probe_b002.py` is committed** and contains an extractor, in tension with the no-ground-truth
   rule for the task-set directory. The corpus generator is still not committed and the results
   file reports only aggregates.
5. **B-002 grew from 147 KB to 161 KB.** No v1.0.0 run may ever be pooled with a v1.1.0 run.
6. **`MANIFEST.sha256` was deleted** from v1.1.0 rather than left stale, and replaced by the wider
   `manifest.py`. Restorable in one command if the Reviewer prefers both.

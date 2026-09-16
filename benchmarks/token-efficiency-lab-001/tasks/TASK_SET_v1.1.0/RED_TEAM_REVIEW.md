# RED_TEAM_REVIEW.md — Task Set v1.1.0

**Seat:** Task Red Team · **Date:** 2026-09-16 · **Branch:** `claude/atk-open-skill-distribution-96e4vv`
**Under review:** the v1.0.0 → v1.1.0 repair claimed in `reports/LAB_001_BENCHMARK_REPAIR_REPORT.md`
**Replay list:** `tasks/TASK_SET_v1.0.0/RED_TEAM_REVIEW.md` §2, RT-01…RT-21
**Binding authority:** `methodology/METHODOLOGY_v1.1.0.md`

This seat authored none of the material under review and fixed nothing. Everything below that
says "demonstrated" was executed. Working tree verified clean at the end of the review
(`git status --porcelain` → empty); all tampering was done in
`/tmp/.../scratchpad/rt/sandbox`, a copy.

---

## 0. The one thing to read if you read nothing else

`environment/harness/runner.py:193` writes

```python
"methodology_version": "1.0.0",
```

into every run record, and line 239 passes that same string to `blind.build_packet`. The judge's
version gate (`judge.py:2663`) therefore resolves **1.0.0** for every packet the real harness
produces, and `judge.py` routes to the v1.0.0 rulebook at all thirteen `_mv` branch points.

**Every packet built by the shipped pipeline is scored under v1.0.0.** Demonstrated:

```
$ python3 tools/golden_run.py --task-root tasks/TASK_SET_v1.1.0 --out $S/golden
$ docker run ... atk-lab001:v11 python3 -m harness.runner --task-root /lab/tasks ... --out /lab/g/out
$ python3 -c "import json; print(json.load(open('judge_packets/01b1a7042162de6c.json'))['methodology_version'])"
1.0.0
```

and in the scores, `detail.floor_basis` for A-003 comes back
`"absolute_fallback_baseline_unavailable"` — the v1.0.0 relative-floor code path, named in
`judge.py:1090`, not the v1.1.0 `"absolute_answer_key_methodology_v1.1.0_s6"` path.

Consequences, each demonstrated below: the absolute floors (RT-05) are not applied, the C
citation symmetry (RT-04) is not applied, the C count-penalty removal (RT-09) is not applied,
the B `count` ruling (RT-10) is not applied, the corpus-read guard and the D fixtures
prohibition (RT-08) are not applied, the turn-completeness assertion (RT-13) is not applied,
and **workload E's entire constraint-violation scan runs against `model_output` instead of the
harness-captured transcript**, so four of the five repaired E violation classes cannot fire.

The 17/17 golden PASS is real, and it is evidence about the v1.0.0 scorer.

`SCORING_SPEC.md` §1.1 carries an "Open handoff" note saying `blind.build_packet` does not set
`methodology_version` "so every packet it builds today is refused". That note is now stale and
describes the wrong symptom: `build_packet` defaults to `1.1.0` (`blind.py:306`), but `runner.py`
overrides the default with `1.0.0`. Nothing is refused. Everything is silently downgraded.

---

## 1. Replay table — RT-01 … RT-21 against v1.1.0

"Shipped path" = a packet as `harness.runner` actually writes it (`methodology_version 1.0.0`).
"v1.1.0 path" = the same packet with the version corrected by hand.

| id | v1.1.0 status | command / result |
|---|---|---|
| **RT-01** | **STILL OPEN** (new form) | Golden packets from the real runner, re-scored with `methodology_version` forced to `1.1.0`: **11 PASS, 5 INVALID, 1 FAIL_QUALITY.** B-002 `required_evidence_missing:document_incident_ids`, B-003 `…document_req_ids`, C-001 `…corpus_files`, C-002 `…corpus_files,document_award_ids`, C-003 `…corpus_files,registry_plugin_ids`, A-001 `answered_without_reading_the_corpus`. `grep -n "document_incident_ids\|corpus_files\|registry_plugin_ids\|document_award_ids\|document_req_ids" environment/harness/evidence.py` → **no match**: the Evidence Producer never produces any of the five fields `judge.EVIDENCE_CONTRACT` (judge.py:2456-2477) and `SCORING_SPEC` §4.1 require. Identical defect class to v1.0.0's, at 6 of 17 instead of 10 of 17. See **NEW-02**, **NEW-03**, **NEW-04**. |
| **RT-02** | **CLOSED — verified** (scorer) | `E-003` with `{"shifts":{},"roster":{}}` and with `[]`/`[]` → `INVALID required_evidence_empty:shifts,roster` at **both** versions; fields absent → `required_evidence_missing`. `E-001` with `catalog_part_ids: []`, `halberd_part_ids: []` → `INVALID`. Five spellings of `part_id_pattern` (`^KP-\d{4}$`, `KP-\d{4}`, `\bKP-\d{4}\b`, `ZZZ`, `""`) → **one identical verdict**, and the key is listed in `detail.ignored_packet_keys` under v1.1.0. The original attack (empty evidence + ineligible `PR-007`→`SH-105` ⇒ pass) is dead. *But* the criterion it protects is inert in the shipped path — see RT-13 and NEW-01. |
| **RT-03** | **CLOSED — verified, both halves** | See §3. Verified independently of `probe_b002.py`'s self-reference, against the **delivered** `answer_keys/B-002.json`. |
| **RT-04** | **CLOSED — verified on the v1.1.0 path; STILL OPEN on the shipped path** | v1.1.0: one extra `forum_thread_4111.md` ⇒ `zero_tolerance:workload_C_100_percent_traceable`; **one governing source omitted ⇒ the same failure** (symmetry works); every record cites only its first source ⇒ fail. Shipped path (`1.0.0`): extra citation still fails, but **"one governing source omitted" and "every record cites only its first source" both PASS at 1.0000** — v1.0.0's one-directional metric, the exact RT-04 asymmetry, is still live. The *ruling* (task text (a)/(b)/(c) + claim-to-source mapping) is genuinely in all three C prompts and is unambiguous. |
| **RT-05** | **STILL OPEN** | Reproduced exactly, on a packet built by the real v1.1.0 runner. A-001 blanket answer (all 126 module-level functions in `api/`+`plugins/`+`cli/`) scores **0.6667** (TP 63, FP 63, FN 0). With `required_evidence.baseline_reference_quality` set to **0.70** ⇒ `task_success: true`, `outcome: PASS`. At 0.60 ⇒ PASS. At 0.71, 1.00, and absent ⇒ FAIL. Only with `methodology_version` forced to `1.1.0` does the absolute floor bite. The CR-001-A repair is correct and unreachable. |
| **RT-06** | **CLOSED — verified (ruled)** | `corpora/workflow_e/procurement_policy.md` P1 now names four rounding points and states that "a per-vendor, per-region, per-line or per-category apportionment of freight or of contingency is an intermediate value: it is not a line, it is not a component total, and it is not rounded"; P4 makes freight one component total summed from full-precision per-vendor products. Key carries `freight_eur: "1197.38"`. `1197.39` is no longer a defensible reading — the two readings cannot coexist. |
| **RT-07** | **CLOSED — verified (ruled)** | Scoring is unchanged (`AMENDMENT` casing alone 0.9722 pass; `the laws of England and Wales` alone 0.9722 pass; **both together 0.9444 fail**) — but the readings are no longer defensible. The prompt now fixes `amendments_in_force_on_as_of_date` to `Amendment No. n` "whatever capitalisation the document's own heading uses", N4 explicitly exempts it, and **N4a** fixes `governing_law`/`jurisdiction_city` to the bare name. Closed by ruling, exactly as a fix of this kind has to be. |
| **RT-08** | **PARTIAL** | *Corpus-integrity half: closed and verified end to end.* A modified `corpus_hashes_after` ⇒ `FAIL_QUALITY corpus_modified` for A, B, C, D **and** E on the v1.1.0 path; and independently of the version, `runner.py:222` fails the attempt and `finalize.py:70` refuses to let the judge overturn it, and `aggregate.py` counts on `outcome`. *A-001 read-guard half: broken in both directions* — see **NEW-04**. |
| **RT-09** | **CLOSED on the v1.1.0 path; STILL OPEN on the shipped path** | Shipped path: perfect C-001 with `count` off by one ⇒ **0.9500**, the undeclared penalty, reproduced. v1.1.0 path ⇒ 1.0000. `COUNT_RULE_V11` (judge.py) sets C-001/2/3 to `("none", 0.0)`; `count_rule` (judge.py:840) returns the flat 0.05 whenever `_mv != 1.1.0`. |
| **RT-10** | **CLOSED (ruled) on the v1.1.0 path; STILL OPEN on the shipped path** | See §4. 0.95 → 0.9945 reproduced exactly; no floor moved; three further loosenings found beside it. |
| **RT-11** | **CLOSED — could not reproduce the original attack** | `metrics.get_error_budget_raw` no longer exists in `corpora/mcp_toolset/tools.json` (85 tools, 28 families). `metrics.get_slo` → family `slo-reference`, `tickets.get_queue` → `queue-reference`, `calendar.get_month_boundaries` → `calendar-arithmetic`, none contested for their task. Demonstrated on D-004 at both versions: `+ metrics.get_error_budget` ⇒ `zero_tolerance:wrong_tool_invocation`; `+ tickets.get_ticket_sla` ⇒ breach; `+ metrics.get_slo`, `+ calendar.get_month_boundaries`, `+ tickets.get_queue`, `+ catalog.list_tools` ⇒ **PASS 1.0000**. D-003's new `calendar.get_calendar_period` is a real second member and fires. Contested families and `required_tools` unchanged from v1.0.0. |
| **RT-12** | **CLOSED in code — verified; the artefact is missing** | In a sandbox copy: `manifest.py build` then five tamper cases, each `manifest.py verify` exiting **1** and naming the group — modified corpus (`task_set.modified`), modified `answer_keys/A-001.json` (`answer_key.modified`), modified `harness/judge.py` (`scorer.modified`), **added** `answer_keys/Z-999.json` (`answer_key.added`), **deleted** `tasks/A/A-004.json` (`task_set.deleted`); restored ⇒ exit 0, `ok: true`. **But `tasks/TASK_SET_v1.1.0/MANIFEST.json` does not exist in the repository** and `MANIFEST.sha256` was deleted, so the frozen task set currently ships with no integrity manifest at all. See **NEW-05**. |
| **RT-13** | **CLOSED at the producer — verified; STILL OPEN at the scorer, demonstrated end to end** | Producer (`evidence.assert_turns_complete`): 16 turns accepted; 15 turns, final-only, reversed, duplicated-last, `[]` and `None` all refused with a specific message. Scorer on the v1.1.0 path: deleted middle turn / final-reply-only / `turns` absent / `turns` empty / reversed / duplicated ⇒ `INVALID evidence_incomplete:turns`; `'just'` at turn 8 with turns supplied ⇒ `zero_tolerance:constraint_violation`. **Shipped path: all six of those PASS.** See §2 item 9 for the end-to-end demonstration. |
| **RT-14** | **CLOSED — verified** | `tasks/A/A-001.json` `notes` and `DESIGN_NOTES.md` §2 both now state **0.6667** and say the v1.0.0 figure "was wrong by 17 points". |
| **RT-15** | **CLOSED — verified** | `grep -c "counts as 6 - use 6" tasks/E/E-002.json` → 0. The metric reads "6 comparable cells". |
| **RT-16** | **CLOSED — verified (ruled)** | C-003's prompt now says `contradicted_by` is "a fact about the corpus and not about authority: EVERY file of ANY tier … including the registry export itself for a plugin whose registry row an erratum has corrected." One sentence, in the task. |
| **RT-17** | **CLOSED — verified** | Imported every module under `corpora/repo_ledgerline/ledgerline/`: **51 modules, 0 import failures.** `ast` count of module-level functions = **397**, matching `valid_symbols` in the produced evidence. |
| **RT-18** | **CLOSED — verified** | `python3 -m unittest test_judge` → `Ran 240 tests … OK`; `SCORING_SPEC.md` §8 says 240. |
| **RT-19** | **CLOSED — verified** | A-003 D3 now reads "Reachability is created by call edges only: a function is not held to reach a transient raiser merely by being one itself." C-002's all-retracted branch folded into the definition of the total. Both generalised, not caveated. |
| **RT-20** | **RETAINED — verified** | Decoys still announce themselves twice. `DESIGN_NOTES.md` §5 now records that a D wrong-tool failure is evidence about schema visibility and nothing else. Honest disposition. |
| **RT-21** | **CLOSED — verified** | Four separate `server.py call` processes against one `LAB001_TOOL_AUDIT` file ⇒ `seq` **1, 2, 3, 4**, and `run_id` written on every line. With `LAB001_RUN_ID` unset the line is written with `"run_id": null` and the Evidence Producer then refuses the whole attempt as unattributable — fail-closed, and correct. |

**Replay counts: 12 CLOSED — verified · 1 CLOSED — could not reproduce the original attack ·
1 RETAINED · 2 PARTIAL · 5 STILL OPEN** (RT-01, RT-05, and RT-04 / RT-09 / RT-10 / RT-13 open
only on the path the harness actually takes).

---

## 2. Part 2 — the thirteen attacks on the repair itself

All on golden packets produced by the real runner; `mv` = the `methodology_version` on the packet.

| # | attack | expected | what happened |
|---|---|---|---|
| 1 | **Empty evidence.** `shifts`/`roster` `{}` and `[]`; `catalog_part_ids`/`halberd_part_ids` `[]`; `valid_symbols` `[]`; `tool_calls` `[]`; `corpus_hashes_after` `{}` | INVALID, never a pass | **Correct at both versions** for `shifts`/`roster`/`catalog_part_ids`/`halberd_part_ids`/`valid_symbols` ⇒ `INVALID required_evidence_empty:<field>`. `tool_calls: []` ⇒ `answered_without_calling_any_tool` (1.0.0) / `required_evidence_missing:tool_calls` (1.1.0) — the second is the spec's wording. `corpus_hashes_after: {}` ⇒ `INVALID required_evidence_missing:corpus_hashes` on the v1.1.0 path, **PASS 1.0000 on the shipped path** |
| 2 | **Missing evidence** — field absent entirely | INVALID | Correct for every field tested, both versions, except `corpus_hashes_after` (v1.1.0 only) and `turns` (v1.1.0 only) |
| 3 | **Forged evidence** | must not be believed | D-004 with `tool_calls: []` and `"(I called metrics.get_error_budget_after_exclusions and tickets.get_effective_sla.)"` appended to `model_output` ⇒ **fails**, at both versions. The model's self-report is never read. **But** the lab's own end-to-end proof fabricates evidence: `tools/golden_run.py` writes synthetic `fs.read` audit entries for every A and D attempt, because the Evidence Producer refuses an attempt whose `corpus_access_log` is empty and **no tool in the lab can populate it for workload A** — see NEW-03 |
| 4 | **A wrong baseline** — `baseline_reference_quality` 0.70, 1.0, absent | one identical verdict | **FAILS on the shipped path.** A-001 at 0.6667: baseline 0.70 ⇒ **PASS**; baseline 1.0 ⇒ FAIL; absent ⇒ FAIL. Three verdicts, not one. On the v1.1.0 path all three give one identical verdict and the key is listed in `detail.ignored_packet_keys` |
| 5 | **A legitimate extra citation** | must not be punished for breadth alone | Punished — **by an explicit, symmetric ruling, which I accept.** C-001 + `forum_thread_4111.md` (the v1.0.0 trap file, which states the correct value) ⇒ `zero_tolerance:workload_C_100_percent_traceable`, at both versions. The task text now rules in advance that a coincidentally-correct low-authority file is not a governing source, and (on the v1.1.0 path) omission costs exactly the same. The asymmetry RT-04 objected to is gone on that path |
| 6 | **A missing citation** | must fail | v1.1.0 path: one record with `sources: []` ⇒ fail; one of two governing sources omitted ⇒ fail; every record cites only its first source ⇒ fail. **Shipped path: the last two PASS at 1.0000** |
| 7 | **Tail truncation** — last 15% of B-002 only | must fail | **0.0000, `below_quality_floor`.** Verified against the delivered key, not the probe's self-reference. See §3 |
| 8 | **A wrong tool** | decoy fails, exploration does not | Both correct — see RT-11. One gap: a call whose `family` label is not one of the frozen contested names is ignored, so a mislabelled entry disarms the criterion (**NEW-08**) |
| 9 | **A deleted middle turn**, and a final-reply-only transcript | INVALID | v1.1.0 path: both ⇒ `INVALID evidence_incomplete:turns`. **Shipped path: both PASS 1.0000.** End-to-end demonstration: I patched the golden fixture so E-002's turn 8 reads `"kestrel-search is just in wave 3."` (a V2 violation) and E-003's turn 14 proposes ineligible `PR-007` for `SH-105`, leaving both final answers byte-perfect, and ran the **exact RUNBOOK chain** — runner, `judge.py`, `finalize`. Result: **16 passed, 1 zero-tolerance breach.** E-003 breached (its JSON leaked into `model_output`); **E-002 PASSED**, with `detail.turns_source: "model_output"`, `detail.turns_seen: 1`, `constraint_violations: 0` — while the packet's own `required_evidence.turns` contained all 16 turns including `{"turn": 8, "text": "kestrel-search is just in wave 3."}`. The harness captured the violation correctly and the scorer never looked at it |
| 10 | **Corpus / key / scorer modification, plus an added and a deleted file** | all six caught | **All six caught**, exit 1 each, correct group and filename. See RT-12. The manifest itself is not committed |
| 11 | **A missing rate** — `pricing_preflight.py` against a model with no cache-read rate | BLOCK, exit 1 | Correct in all three shapes: `cache_read` key removed ⇒ `"cache_read is applicable but has no rate. A missing rate is never zero"`, exit **1**; `cache_read: null` ⇒ same, exit 1; model absent from the snapshot ⇒ `"the run plan uses this model and the snapshot does not price it"`, exit 1 |
| 12 | **Un-blinding by field injection** | refused or inert | Top level: `condition`, `cost`, `model`, `candidate`, `input_tokens` ⇒ listed in `detail.ignored_packet_keys`, verdict byte-identical to clean, and `blind.assert_blind` **refuses** the packet. Nested inside `required_evidence`: `assert_blind` **does not scan it at all** (`required_evidence` is in `FROZEN_CONTENT_FIELDS`), and `evidence.assert_treatment_neutral`'s key list is a strict subset of `FORBIDDEN_KEYS`, so `required_evidence.treatment_name`, `.candidate_commit_sha`, `.model_version` and `.cache_state` pass **both** gates. No scoring impact today. **NEW-06** |
| 13 | **Cross-run audit contamination** | refused | Correct and strict. Another attempt's entries ⇒ filtered by `run_id`; another task's entries ⇒ filtered; **any** entry with no `run_id` or `run_id: null` ⇒ the whole attempt refused as unattributable; an audit with no entry for this run ⇒ refused ("'No calls were logged' and 'the log is not this run's' are different"); empty audit ⇒ refused |

---

## 3. RT-03 — both halves verified

The Designer's claim is that reading only the last 15% of B-002's document went 1.0000 → 0.0000
while content-selective retrieval still scores 1.0000 at 5.2% of the bytes. **Both halves hold,
and the second half holds against the delivered answer key, which is what the probe itself says
it cannot check.**

`shortcut_probe/probe_b002.py` reports its quality figures relative to *its own extractor's*
full-document output, and says so (§5, "The reference row is the answer this probe's own
extractor produces"). That is a circular basis, so I checked it externally.

**Structure, measured directly** (`re.finditer(r'^#{1,3} ', doc)`, 161,323 characters):

| evidence | offset | share |
|---|--:|--:|
| §1.4 Precedence of figures | 3,234 | 2.00% |
| Q1 register | 35,384 | 21.93% |
| Q2 register | 64,716 | 40.12% |
| Q3 register | 96,671 | 59.92% |
| Q4 register | 129,849 | 80.49% |
| Appendix A — Register Amendments | 153,732 | 95.29% |
| Appendix B — Correction Notices | 157,425 | 97.58% |

The last 15% begins at byte 137,124, inside §6.3. It contains **no register at all**.

**Half one — the shortcut is dead.** Every strategy's best-case answer, scored through the real
`judge.score_packet` against `answer_keys/B-002.json`:

| strategy | share | records | `quality_score` | verdict |
|---|--:|--:|--:|---|
| full document | 100% | 26 | **1.0000** | PASS |
| **last 15% only** | 15.0% | **0** | **0.0000** | **`below_quality_floor`** |
| first section only | 3.6% | 0 | 0.0000 | fail |
| first 32,768 bytes | 20.3% | 0 | 0.0000 | fail |
| first 50% | 50.0% | 8 | 0.2434 | fail |
| **head 10% + tail 15%** | 25.0% | **0** | **0.0000** | **fail** |
| **content-selective retrieval** | **5.2%** | 26 | **1.0000** | **PASS** |

**Half two — effective retrieval still wins, and I checked it the hard way.** I compared each
strategy's extracted record set, field by field, against the 26 records in the delivered
`answer_keys/B-002.json`:

```
full document (reference)                     recs=26  matches_delivered_key=True
content-selective retrieval                   recs=26  matches_delivered_key=True
last 15% of bytes only                        recs=0   matches_delivered_key=False
head 10% + tail 15%                           recs=0   matches_delivered_key=False
fixed truncation: first 50% of bytes          recs=8   matches_delivered_key=False
```

A structure-selective reader that keeps §1.4, the register tables, the amendment tables and the
correction-notice paragraphs reproduces the **committed key exactly** on **8,464 of 161,323
characters**. The fix has not over-corrected into forcing full-document reading: it costs a
position-based filter everything and costs a content-based one nothing.

**Verdict: RT-03 CLOSED — verified, both halves.** This is the best piece of work in the repair.
The informative row is the 50% truncation: 8 confident records where the key has 26, including
one the amendments withdraw — a complete, confident and wrong answer rather than a visible
refusal, which is what this workload exists to catch.

One caveat the Designer already states and I confirm: this measures *sufficiency of evidence*,
not model behaviour. 5.2% is the floor of what a competent selector needs, not a prediction.

---

## 4. RT-10 — the ruling, and what else moved with it

**The ruling reproduces exactly.** Perfect B-002 answer, `count = 25`:

* shipped path (`mv 1.0.0`): **0.9500**, `below_quality_floor`, FAIL — the v1.0.0 defect, intact
* v1.1.0 path: **0.9945**, PASS

`count = 0` and `count = 999` behave identically, so it is the inconsistency and not the
magnitude that is scored — correct for a self-consistency check. One genuinely wrong extraction
cell scores 0.9945 as well, which is the point of the ruling: a bookkeeping slip and a one-cell
error now cost the same, instead of the slip costing twenty times more.

**No floor moved.** `FLOOR_A = 0.95`, `FLOOR_B = 0.97`, `FLOOR_C_COVERAGE = 0.90`,
`FLOOR_C_TRACEABILITY = 1.0`, `FLOOR_E_COMPLETION = 0.95` — identical to
`METHODOLOGY_v1.0.0.md` §6 and to `TASK_SET_v1.0.0/SCORING_SPEC.md`. Verified by reading both.

**But RT-10 is not the only loosening.** I scored a battery of perturbations of every golden
answer at both versions and diffed the verdicts. Four changes flip a fail to a pass:

| task | perturbation | v1.0.0 | v1.1.0 | cause | declared? |
|---|---|--:|--:|---|---|
| **B-002** | `count` off by one | 0.9500 **fail** | 0.9945 **pass** | RT-10 ruling | yes, prominently |
| **A-001** | one true member dropped, `count` left stale | 0.9420 **fail** | 0.9720 **pass** | A's count penalty 0.05 → **0.02** | in the task text; one clause of the repair report |
| **C-001** | one whole record dropped | 0.8875 **fail** | 0.9375 **pass** | RT-09, C count penalty removed | yes (as a correctness fix) |
| **D-001…4** | one extra top-level key in the reply | 0.0000 **fail** | 1.0000 **pass** | UG-19 reversed | yes |

All four are stated in the frozen task text, so none of them is a silent softening, and each has
a defensible rationale. Two observations the repair report should carry:

1. It names RT-10 as "the single change most in need of a second opinion". There are **four**
   pass-rate-raising changes, not one, and the A-workload one (0.05 → 0.02) is the least visible.
2. It states "**Workload C is now strictly harder.**" That is true of citation and **false of
   coverage**: removing the count penalty moves a C-001 answer that omits an entire record from
   0.8875 (fail) to 0.9375 (pass). The net direction for C depends on which error a run makes.

**Verdict: RT-10 CLOSED (ruled) on the v1.1.0 path, with the effect quantified honestly and no
floor moved — and nothing loosened that is not written into the task text.** On the shipped path
the ruling is not applied at all and the 0.95 cliff is still there.

---

## 5. New findings

| id | sev | where | what is wrong | how demonstrated | a fix must satisfy |
|---|---|---|---|---|---|
| **NEW-01** | **BLOCKING** | `environment/harness/runner.py:187,193,239`; `environment/harness/selfcheck.py:166` | The runner stamps `task_version` and `methodology_version` as the literal string `"1.0.0"` on every record and every packet. `judge.py`'s version gate then routes the whole v1.1.0 repair to the v1.0.0 rulebook: absolute floors (RT-05), C citation symmetry (RT-04), C count-penalty removal (RT-09), the B `count` ruling (RT-10), the corpus-integrity and corpus-read gate (RT-08), turn completeness (RT-13) and the entire `_evidence_gate` are all `_mv == V1_1_0`-guarded and never run. `METHODOLOGY_v1.1.0` §6.0.1(2) and §13 prohibit exactly this. | Golden packets from the real runner carry `"methodology_version": "1.0.0"`; A-003's score carries `floor_basis: "absolute_fallback_baseline_unavailable"`. Every "STILL OPEN on the shipped path" row in §1 is this one bug. Most sharply: the RUNBOOK chain run end to end on a fixture with a V2 violation at E-002 turn 8 ⇒ **PASS**, while `required_evidence.turns[7]` contains the violating text | The runner must stamp the version of the rules it was built to run, and it must be derived from one declared source rather than a literal. A test must build a packet through `blind.build_packet` from a `harness.runner` record and assert the resolved version — no test does today (**NEW-07**). The fix is not complete until the golden run passes **under the v1.1.0 rules**, which today it does not (**NEW-02**) |
| **NEW-02** | **BLOCKING** | `environment/harness/evidence.py` vs `judge.EVIDENCE_CONTRACT` (judge.py:2456) and `SCORING_SPEC.md` §4.1 | The Evidence Producer produces none of `document_incident_ids`, `document_req_ids`, `corpus_files`, `document_award_ids`, `registry_plugin_ids`. The v1.1.0 judge requires all five, at minimum 1. `SCORING_SPEC` §4.1 asserts `required_evidence` "is produced by `environment/harness/evidence.py`" and then lists five fields it does not produce. Consequence: under the rules the task set declares, B-002, B-003, C-001, C-002 and C-003 are **structurally unscorable**, and workload B's "no fabricated record id" zero-tolerance criterion can never be evaluated | Golden packets re-scored at `mv 1.1.0`: 5 `INVALID required_evidence_missing:<field>`, all five byte-perfect answers. `grep` over `evidence.py` for each field name → no match | A producer for each of the five, derived from the frozen corpus at the frozen hash, plus one test that scores **all 17 byte-perfect golden answers at `methodology_version 1.1.0`** and requires 17 PASS. Until that test exists the RT-01 failure mode is not closed, only moved |
| **NEW-03** | **BLOCKING** | `evidence.REQUIRED_BY_WORKLOAD["A"]`, `evidence.validate`; `corpora/mcp_toolset/tools.json`; `RUNBOOK.md` §8b | Workload A requires `tool_calls` and `corpus_access_log` non-empty, and **nothing in the lab can produce either for a workload-A attempt**: `tools.json` has no `fs.*` or file-read tool, and `corpora/mcp_toolset/server.py` is the only writer of `LAB001_TOOL_AUDIT`. A real A attempt therefore raises `EvidenceError` in the producer and is recorded `INVALID` by `runner.py:216`. The RUNBOOK §8b says "Workloads A and D score a zero-tolerance criterion from the server-written audit log" — for A there is no server. The only reason this is invisible is that `tools/golden_run.py` **fabricates** two `fs.read` audit entries per A and D attempt | `ev.produce` on D-004 with a clean two-entry audit of the two required tools ⇒ `EvidenceError: required_evidence_empty:corpus_access_log`. `tools.json` contains zero tools matching `fs.` or `read`. `golden_run.py` lines writing `{"tool": "fs.read", "family": "corpus"}` into `TOOL_AUDIT.jsonl` | A named, real mechanism that records a workload-A corpus read (an audited read tool, or a harness-side FUSE/strace/open-hook), or the A-workload evidence requirement must be dropped and A-001's anti-shortcut `failure_condition` declared unevaluated in `SCORING_SPEC` §9. What is not acceptable is an evidence field that only the lab's own proof harness can fill |
| **NEW-04** | **MAJOR** | `evidence.access_log_from_audit` vs `judge._evidence_gate` step 4 (judge.py:2614-2645); `README.md` line 105 | The producer emits `corpus_access_log` as `list[dict]` (`{"path":…, "tool":…, "seq":…}`); the judge reads it as `list[str]` (`[p for p in log if isinstance(p, str) and directory in p]`). `README.md` and `SCORING_SPEC` §4.1 both say `[path]`, so the producer is the deviant. **Two opposite failures from one mismatch:** A-001's corpus-read guard never sees a hit and fails every legitimate run; D's fixtures-read prohibition never sees a hit and **fails open** | At `mv 1.1.0`: golden A-001 with the producer's own log ⇒ `FAIL_QUALITY answered_without_reading_the_corpus`; the same packet with `["corpora/repo_ledgerline/…py"]` ⇒ PASS. D-001 with `[{"path":"corpora/mcp_toolset/fixtures/rota.json",…}]` ⇒ **PASS 1.0000**; the same path as a bare string ⇒ `fixtures_read_tool_selection_unmeasurable` | One declared shape, asserted on both sides, with a test that feeds the **producer's actual output** to the judge. A reader that accepts either shape is acceptable; two seats each believing the other's shape is not. A D run that reads `corpora/mcp_toolset/fixtures/` gets the answers for free, so this half is a correctness hole, not only a plumbing one |
| **NEW-05** | **MAJOR** | `tasks/TASK_SET_v1.1.0/` | `MANIFEST.json` is not in the repository and `MANIFEST.sha256` was deleted. RT-12's repair is real code with no artefact: `manifest.py verify` against the frozen set raises `FileNotFoundError` and exits 1. Nothing binds the corpora, the 19 answer keys, `SCORING_SPEC.md` or `judge.py` to any digest today, which is the state RT-12 was raised about. Separately, `manifest.py build` reports `unclaimed_files: ["INDEPENDENT_VERIFICATION.md"]` — a file inside the frozen set that no hash group covers | `python3 environment/harness/manifest.py verify --task-set tasks/TASK_SET_v1.1.0 --env environment --manifest tasks/TASK_SET_v1.1.0/MANIFEST.json` → traceback, exit 1. The same command in a sandbox copy, after `build`, → exit 0 and catches all five tamper classes | `MANIFEST.json` committed, built from the exact tree that is frozen, before any run; every file inside the task-set directory in a group or explicitly excluded by a rule; and the freeze record binding `manifest_digest` to the commit |
| **NEW-06** | **MAJOR** | `blind.assert_blind` + `blind.FROZEN_CONTENT_FIELDS`; `evidence.TREATMENT_LEAKING_KEYS` | `assert_blind` excludes `required_evidence` from its forbidden-key walk by listing it as "frozen task-set content" — but `required_evidence` is the one packet field that is *run-produced*, so it is exactly where run metadata would leak. The compensating check, `evidence.assert_treatment_neutral`, uses a key list that is a strict subset of `FORBIDDEN_KEYS`, and only runs on evidence built by `evidence.produce` | `required_evidence.treatment_name`, `.candidate_commit_sha`, `.model_version` and `.cache_state` all **pass both gates**. `.condition` passes `assert_blind` and is caught only by `assert_treatment_neutral` | One forbidden-key list, used by both, walked over the whole packet including `required_evidence`. A blind guarantee whose own assertion does not cover the field most likely to break it is the RT-02 shape: a check that can be off without anyone noticing |
| **NEW-07** | **MAJOR** | `environment/harness/test_judge.py`; `tools/golden_run.py` | 240 tests, none of which calls `blind.build_packet` or exercises a `harness.runner` record, so no test covers the runner → packet → judge seam. The single integration proof, `golden_run.py`, returns 17/17 PASS **because** the mis-stamped version selects the more permissive rulebook — a green integration test whose greenness is caused by the defect it should catch | `grep -n "build_packet" environment/harness/test_judge.py` → no match. Golden run 17/17 at the stamped version; 11/17 at the declared version | At least one test that runs the RUNBOOK chain end to end and asserts, for all 17 tasks, the resolved methodology version, `outcome == PASS`, and that `detail.floor_basis` is the absolute one. The repair round's own best insight — "two halves built by different seats were wired together" — was not generalised into a seam test |
| **NEW-08** | MINOR | `judge._score_d` | Wrong-tool classification uses the packet's own `family` string and compares it to the frozen list of contested family *names*. There is no frozen tool→family map, so a call whose `family` does not match a contested name is silently counted "extraneous" and ignored. This contradicts judge.py's own comment (lines 200-207): "Held here rather than read from `required_evidence` so that the scoring basis for a zero-tolerance criterion cannot be narrowed by whatever built the packet" | D-004 + `metrics.get_error_budget` labelled `"family": "totally-made-up-family"` ⇒ **PASS 1.0000**. Not exploitable by the agent under test today, because `server.py:72` takes `family` from `tools.json` | Either resolve the tool name against a frozen name→family table in `judge.py` and record any disagreement with the packet, or delete the comment. Low risk, but it is the difference between a criterion that is defended and one that happens to be correct |
| **NEW-09** | MINOR | `reports/LAB_001_BENCHMARK_REPAIR_REPORT.md` | Two claims do not survive measurement: "RT-10 … the single change most in need of a second opinion" (there are four pass-rate-raising changes; see §4) and "Workload C is now strictly harder" (false for coverage — an omitted record moves 0.8875 fail → 0.9375 pass) | §4 table | A repair report that quantifies its loosenings should quantify all of them and should not claim a net direction it has not measured |
| **NEW-10** | MINOR | `dryrun/out/` | The committed dry-run artefacts are stale v1.0.0-era output: 10 packets with `methodology_version: null`, scores carrying `spec_version 1.0.0` and reasons like `unparseable_output`, sitting under a RUNBOOK that tells a reader to reproduce them against `TASK_SET_v1.1.0` | `Counter` over `dryrun/out/judge_packets/*.json` → `{None: 10}`; `dryrun/out/judge_scores/*.json` → `spec_version 1.0.0`, 0/10 passing | Regenerate or delete. A reproducer following the RUNBOOK will not reproduce them and cannot tell whether that is the point |
| **NEW-11** | MINOR | `evidence.validate` vs `SCORING_SPEC.md` §4.1 | The spec says `corpus_access_log` carries **no minimum** and that its emptiness "is read as a fact about the run, never as a violation and never as missing evidence". `evidence.validate` applies the blanket non-empty rule to it for all of A and D | `ev.produce` on a clean D-004 audit ⇒ `required_evidence_empty:corpus_access_log` | One rule. This is the proximate cause of NEW-03's invisibility |
| **NEW-12** | MINOR | `SCORING_SPEC.md` §1.1 "Open handoff" | The note says `build_packet` sets no `methodology_version` "so every packet it builds today is refused". `blind.py:306` defaults to `1.1.0`; `runner.py:239` overrides it with `1.0.0`. The handoff was taken, incorrectly, and the note now points a reader away from the live defect | Read both files | Update or remove. A stale open-item note is worse than none: it tells the next reviewer the seam has a known, benign symptom |

**Counts: 3 BLOCKING · 4 MAJOR · 5 MINOR.**

---

## 6. Verdict

### NOT fit to freeze. The repair is good; the delivery is broken.

I want to be precise about what I am and am not saying, because most of this stack is better
than what it replaced.

**What is genuinely fixed, and verified here:** B-002's corpus (RT-03) is the best work in the
round — rebuilt rather than rearranged, with both halves of the claim independently confirmed
against the delivered key, including the half that matters for over-correction. The E evidence
contract (RT-02) fails closed on content at the scorer and the producer refuses a short,
reordered or duplicated transcript with a specific message (RT-13). The tool families (RT-11)
are now real decoys and exploration is no longer punished. `manifest.py` catches all five
tamper classes including an added and a deleted file (RT-12). The audit log carries `run_id`
and a continuous `seq`, and refuses an unattributable entry (RT-21, and the run-id gap the
repair round found on its own). Four findings were closed by rulings written into the task
text where two judges read the same words (RT-04, RT-06, RT-07, RT-16), which is the only way
findings of that shape can be closed. The pricing preflight blocks correctly. Cross-run
contamination is refused strictly. Seventeen of seventeen keys reproduce.

**Why it cannot freeze anyway:** none of the version-gated half of that work reaches a real run.
`runner.py` stamps `1.0.0`, so the shipped pipeline scores every attempt under the rulebook the
lab has just spent a round replacing. I demonstrated this end to end, through the exact RUNBOOK
commands, on a run whose transcript contained a zero-tolerance constraint violation that the
Evidence Producer captured correctly and the scorer never read. That is not a theoretical
exposure; it is the v1.0.0 failure mode, reproduced, inside v1.1.0.

And when the version *is* corrected, the golden run does not pass: 11 of 17, because the
Evidence Producer and the judge's evidence contract were written to two different lists. That is
RT-01 again — the same class, the same cause (a field with a named consumer and no named
producer), at six tasks instead of ten. Workload A is worse than that: the evidence it requires
has no producer that could exist, and the only artefact that supplies it is the lab's own proof
harness, fabricating it.

**Three things must change before freeze:**

1. **NEW-01** — the runner must stamp the version of the rules it runs, and a test must assert
   it through `build_packet`.
2. **NEW-02 / NEW-03 / NEW-04** — the Evidence Producer and the judge must agree on one field
   list and one field shape, workload A's evidence must have a real producer or the requirement
   must be withdrawn and declared, and the D fixtures-read prohibition must stop failing open.
3. **NEW-05** — `MANIFEST.json` must exist, cover every file that can change a score, and be
   built from the tree that is actually frozen.

The acceptance test for all three is one sentence: **`golden_run.py` must give 17/17 PASS with
every packet resolving `methodology_version 1.1.0`, and the run that today passes with a
violation at E-002 turn 8 must fail.** Today the first gives 11/17 and the second passes.

**Before results are read, not necessarily before freeze:** NEW-06 and NEW-07. NEW-07 is the
one I would push hardest on culturally: this round's own best finding was that two halves built
by different seats were wired together and neither was wrong alone. Three of my four MAJOR/
BLOCKING findings are that same shape, and the reason they survived is that all 240 tests build
their packets by hand.

**The MINOR findings belong in the next revision and should not hold anything.**

I found no wrong answer key, no ambiguous ruling that survived the round, no floor that moved,
no silent softening outside the task text, and no way to make a wrong answer pass the chain
*other than* through NEW-01. Fix the delivery and this is a task set I would sign.

---

## 7. What I did NOT check

Read this before treating anything above as a sign-off.

* **I did not re-derive any answer key.** I compared the probe's B-002 extraction against the
  delivered key and I used the golden answers as ground truth everywhere else. The Independent
  Semantic Verifier's document (`INDEPENDENT_VERIFICATION.md`, committed during this review)
  claims 17/17 agreement by a second method; I did not audit that claim, and my work would not
  have caught a key that is wrong in a way both the key and the golden answer share.
* **I did not run any task against a real model.** Every score above is a constructed answer or
  a replayed fixture. The 0.6667 cliff, the 5.2% retrieval ceiling and the perturbation table
  are all constructions.
* **I did not read the B or C corpora in full,** only B-002's section structure by byte offset
  and C-001's citation rule and key. I did not verify that any corpus file states what the key
  says it states.
* **I did not audit the cost side.** `meter.py`, `pricing.py`, `calibrate.py`,
  `METER_CALIBRATION_v1.1.0.md`, the tokenizer-boundary rule (§12.0.1) and the cache-inclusion
  rule (§12.0.2) were out of scope except for `pricing_preflight.py`, which I exercised only
  for missing rates. The Anthropic cache-accounting fix the repair round claims is untested here.
* **I did not verify the container build reproduces.** I used the supplied `atk-lab001:v11`
  and did not rebuild from `environment/build.sh`, did not check `image_content_sha256`, and
  did not run the LG3 self-check or its network negative control.
* **I did not test the aggregator or the cell arithmetic** beyond reading that it keys on
  `outcome`. D's 95% cell rule, the `INVALID` denominator treatment and quantity 9 are unexercised.
* **I did not exercise the blind salt custody path,** the un-blinding procedure, or whether
  blind labels are stable across subsets — only `assert_blind`'s key and name scans.
* **I did not exhaustively fuzz `judge.py`.** Roughly 150 constructed packets. `score_packet`
  never raised and never returned `judge_internal_error`, but that is a sample.
* **I did not check workload E's V6 classes, E-002's V1/V3/V4/V5 individually, or E-001's V2/
  V4/V5/V6.** I verified the delivery mechanism (turns) and two violation instances. The repair
  report claims a breaching and a legitimate case for every class; I did not replay that matrix.
* **The task set moved under me.** `INDEPENDENT_VERIFICATION.md` appeared and commit `3781886`
  ("C-001 source mapping made unambiguous") landed during this review; `answer_key_hash` changed
  between my first and second golden runs. My §1 results were re-confirmed after that commit,
  but nothing here is a statement about a frozen tree, because the tree was not frozen.

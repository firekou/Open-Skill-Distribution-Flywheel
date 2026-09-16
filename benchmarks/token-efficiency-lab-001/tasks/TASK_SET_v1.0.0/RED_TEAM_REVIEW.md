# RED_TEAM_REVIEW.md — Task Set v1.0.0

**Seat:** Task Red Team (LG8) · **Date:** 2026-09-16
**Under review:** `tasks/TASK_SET_v1.0.0/` (Task Set Designer), `answer_keys/` (Answer Key
Builder), `SCORING_SPEC.md` + `environment/harness/judge.py` (Quality Judge)
**Binding authority:** `methodology/METHODOLOGY_v1.0.0.md` (FROZEN, not editable by this seat)

This seat may reject but may not author replacements. Nothing under `tasks/`, `corpora/`,
`answer_keys/`, `SCORING_SPEC.md` or `judge.py` was modified. Verified: `sha256sum -c
MANIFEST.sha256` → 155/155 OK **after** this review, identical to before.

---

## 0. What was actually executed

Everything below that says "demonstrated" was run. Work was done in a scratch directory; no
artefact was left in the task set except this file.

| Action | Result |
|---|---|
| `derive_{A,B,C,D,E}.py --write` into a scratch copy of the task set, diffed against the committed keys | **17/17 byte-identical.** The keys are exactly what the scripts produce. |
| `sha256sum -c MANIFEST.sha256` | 155/155 OK |
| `python3 -m unittest test_judge` | 100 tests, OK (`SCORING_SPEC.md` §8 says 81 — doc drift) |
| Workload D tool server, `call` mode and `mcp` stdio mode, `LAB001_TOOL_AUDIT` set | Both work; audit JSONL written by the server; required tools reproduce every keyed D answer |
| ~60 adversarial packets scored through `judge.score_packet` | Results tabulated below |
| Byte-offset analysis of the three workload-B documents | See RT-03 |

---

## 1. Verdicts

### Q1 — Is any task biased toward a particular kind of optimisation tool?

**Verdict: YES. Two tasks are biased, one severely, and the bias points the same way in both:
toward aggressive context reduction.** The designer's isolation posture (DESIGN_NOTES §0) is
credible and I found no evidence of candidate-shaped design. The bias that exists is
*accidental*, arising from corpus layout and from a one-directional scoring rule — which is
exactly the failure mode the question anticipates.

* **B-002 (BLOCKING, RT-03).** Everything B-002 needs lives in the last 13% of its document.
  Appendix A starts at byte 127,608 and Appendix B at byte 131,705 of 146,666 — 4 KB apart, not
  the "~120 KB" claimed in both `DESIGN_NOTES.md` §3 and B-002's own `notes`. The preceding
  86% is quarterly narrative that the task *forbids* using. A C2/C3 condition that discards the
  first 86% of the document scores **identically to C0 at a fraction of the tokens**. That is a
  large, clean, entirely artefactual "saving with no quality cost" — pre-registered H2 and H4
  both read it as confirmation.
* **C-001 (BLOCKING, RT-04).** Traceability is zero-tolerance and penalises citing *more*, never
  citing *less*: an incomplete `sources` list is free (demonstrated: citing 1 of N key sources
  scores 1.0 / pass), while one extra citation is an outright failure. Two of the sixteen flags
  have a forum thread that states the **correct** `introduced_in`, which the task's own citation
  rule expressly permits citing — and citing it fails the task (demonstrated). A run that reads
  16 of 50 files therefore strictly dominates a run that reads 50.
* **D (MAJOR, RT-11).** The H1 probe's zero-tolerance criterion keys on *family membership*, not
  on "returns a competing answer". `metrics.get_slo`, `calendar.get_month_boundaries` and
  `tickets.get_queue` return nothing that competes with the task question, yet one call to any
  of them is an outright failure. Exploration propensity is precisely what C1 (deferred schema)
  changes, so an intervention-correlated behaviour is converted into a quality failure. The
  designer pre-declared this (DESIGN_NOTES §7.2) and mitigated it with free `catalog.*`; the
  mitigation is real but does not cover the three tools above.
* **Counter-balancing, and worth keeping:** C-003's `contradicted_by` genuinely requires a full
  50-file sweep and punishes filtering; B-001 and B-003 require the whole document; A-004
  requires function-body imports that a truncating reader loses. The set is not uniformly
  biased — B-002 and C-001 are the outliers.

### Q2 — Is any task too easy?

**Verdict: ONE task has a live corpus-free shortcut (A-001), and it only bites because of the
relative floor. The other sixteen are robust.**

Measured scores for the cheapest plausible strategy:

| Task | Cheap strategy | quality_score | Passes? |
|---|---|--:|---|
| A-001 | emit all 126 functions in `api/`+`plugins/`+`cli/` (`grep -rn '^def '`, no graph) | **0.6667** | **Yes, if C0 median ≤ 0.70** |
| A-001 | first 63 alphabetically | 0.5556 | No |
| A-002 | empty list / naive `grep -w` over the tree | 0.0 | No |
| A-003 | every `@retryable` function, ignore reachability | 0.6061 | Only if C0 median ≤ 0.638 |
| A-003 | every `@retryable` + `@retryable_v2` | 0.5263 | No |
| B-001/2/3 | any guess | ≪ 0.97 | No |
| C-001/2/3 | any guess | traceability < 1.0 | No |
| D-001…4 | answer without tools | `tool_calls` empty ⇒ outright failure | No |
| E-001 | refuse to substitute, empty BOM | 0.1667 | No |

Two aggravating facts about A-001:

1. The blanket answer scores **0.6667**, not the "~0.5 F1" asserted in `DESIGN_NOTES.md` §2 and
   in A-001's own `notes` (TP=63, FP=63, FN=0 ⇒ P=0.5, R=1.0, F1=0.667). The designer's
   safety margin is 17 points smaller than believed.
2. A-001 `failure_condition` (4) — *"the answer is produced without reading the corpus (empty
   tool-call record)"* — **is not implemented anywhere**, is not among `required_evidence`'s
   fields (SCORING_SPEC §4), and is not declared as a gap in SCORING_SPEC §9. The single guard
   against this shortcut does not exist.

Demonstrated end-to-end: with `baseline_reference_quality = 0.70`, the blanket A-001 answer
returns `task_success = true`.

### Q3 — Can any task be scored unstably?

**Verdict: YES, in four places — but `judge.py` is, on the whole, unusually disciplined.** I
found no free-text field, no unordered comparison, no undefined float comparison (D-004's `4.4`
survives a float-derived `44.6 − 40.2 = 4.399999999999999` under the 1e-9 tolerance), and the
parse/extraction path is deterministic. The instability is elsewhere:

1. **RT-02 (BLOCKING) — the workload-E zero-tolerance criterion fails OPEN.** `SCORING_SPEC` §2
   promises fail-closed. It holds for *absent* evidence but not for *present-but-empty*
   evidence. Demonstrated:
   * E-003 with `{"shifts": {}, "roster": {}}`: a reply assigning ineligible `PR-007` to
     `SH-105` scores `task_success = true`, `zero_tolerance_breached = false`, no warning.
     With the real CSVs it correctly fails.
   * E-001 with `catalog_part_ids: []`, `halberd_part_ids: []`: the exact case SCORING_SPEC §7
     says the suite exists to protect (perfect final BOM, excluded-vendor part proposed at turn
     7) scores **1.0 / pass**. With real lists it fails.
   * E-001 `part_id_pattern`: the prose-turn detector is a Runner-supplied regex used with
     `finditer`. `^KP-\d{4}$` — an entirely plausible value, and the only one a schema-minded
     Runner would write — matches nothing and silently disarms V1/V3 in prose. `KP-\d{4}`
     fires correctly. Demonstrated: same output, same key, opposite verdict.
2. **RT-09 (MAJOR) — the judge applies a penalty the frozen task text does not state.** C-001,
   C-002 and C-003 each define `quality_score = coverage` with **no `count` penalty**.
   `SCORING_SPEC` §5 adds "Then the 0.05 `count` penalty" and `judge.py` implements it.
   Demonstrated: a perfect C-001 answer with `count` off by one scores **0.95** where the frozen
   metric says 1.0. SCORING_SPEC's own rule ("where this document disagrees with a frozen task
   file, the task wins") makes this a defect, and it is not in the §9 UG table.
3. **RT-08 (MAJOR) — outright-failure conditions that are never evaluated.** *"any corpus file
   is modified"* / *"the run edits the source document"* / *"the run edits the corpus"* appears
   in the `failure_condition` of all 13 A, B, C and E tasks. `judge.py` reads `corpus_modified`
   **only for workload D**. SCORING_SPEC §9 does not declare this. An optimisation that
   pre-processes or rewrites a corpus file on disk — a plausible compression strategy — is an
   outright failure by the frozen text and scores clean.
4. **RT-13 (MAJOR) — UG-28 in practice.** With only the final reply shipped, E-002's V1, V2, V4
   and V5 cannot fire. Demonstrated: byte-perfect runbook plus *"kestrel-search is just in wave
   3"* at turn 8 scores 1.0 / **pass** when turns are omitted, and correctly fails when they are
   supplied. The Quality Judge flagged this (UG-28) and recommended the harness assert it;
   nothing does.

Where two competent judges *would* now agree: the UG table is thorough and the frozen
per-task tables in `judge.py` (contested families, cell lists) mean a packet cannot narrow a
zero-tolerance basis. Credit where due.

### Q4 — Is any answer key ambiguous or wrong?

**Verdict: no key is WRONG. Three are ambiguous in ways that change pass/fail, and the builder
found all three itself. I found one it missed.**

Mechanical reproduction: **17/17 byte-identical** from the committed scripts. The D keys were
re-verified against live tool calls (`rota.get_effective_oncall` → `m.okonjo`, tier 2;
`metrics.get_error_budget_after_exclusions` → `remaining_minutes: 4.4`;
`tickets.get_ticket` → 09:12→15:02 = 350 min, −95 stopped = 255 > 240 ⇒ breach). All match.

Confirmed from `BUILDER_NOTES.md`, with measurements:

| Builder's defect | My measurement | Still live? |
|---|---|---|
| #1 C-002 "unscoreable under a literal grader" | **Closed.** `judge.py`'s `per_award` handling makes a perfect C-002 score 1.0 / pass; citing bulletins only also passes. | No |
| #2 C-001 forum thread states a correct value | **Live and fatal.** Demonstrated outright failure. See RT-04. | **Yes** |
| #3 E-001 freight rounding | **Live.** Per-vendor rounding (`1197.39 / 73703.04 / 3703.04`) scores **0.9444** < 0.95 ⇒ fail, for an otherwise perfect, policy-compliant answer. See RT-06. | **Yes** |
| #4 C-003 `contradicted_by` fork | **Live but not fatal.** The alternate reading scores 0.9375, still above the 0.90 floor. Costs 6.25 points of the primary measurement between two defensible readings. | Yes (MINOR) |
| #5/#7 B-001 `AMENDMENT` casing + `governing_law` | **Live and jointly fatal.** Each alone → 0.9722 (pass). **Both together → 0.9444 ⇒ fail.** Both readings are literally mandated by the task's own rule N4. See RT-07. | **Yes** |
| #9 D `required_tools` semantics | Resolved by `judge.py`: minimal-and-permitted (a superset inside a contested family fails; a subset is fine). Consistent with the task text. | No |
| #10 B-002 "~120 KB" claim | **Confirmed and escalated** — it is not merely a wrong note, it is a benchmark bias. See RT-03. | **Yes** |

**What the builder missed:** its own warning that UG-11 couples traceability to coverage
("a wrong value in workload C fails the task twice") is **overstated**. Demonstrated on C-003: a
record with a wrong `min_kestrel_version` still scores traceability 1.0, because the
record-level `"*"` support set absorbs the key's `sources` and another field in the record is
correct. The coupling only bites when *every* scored field of a record is wrong. Worth
recording so nobody "fixes" a problem that is not there.

**Answer-key integrity gap (RT-12, MAJOR):** `MANIFEST.sha256` covers `tasks/` and `corpora/`
only. It does **not** cover `answer_keys/*.json`, `answer_keys/scripts/*.py`, `SCORING_SPEC.md`,
`DESIGN_NOTES.md` or `README.md` — verified by diffing the manifest against the tree. The
scoring ground truth is unhashed. Methodology §12 requires "task set version + hash" in the
evidence manifest; as it stands, a key can change after freeze and the manifest still reports
155/155 OK.

### Q5 — Are the quality floors executable?

**Verdict: NO for 7 of 17 tasks, and the perverse incentive is real and measurable.**

**Which determinations cannot be computed until C0 runs.** Exactly the seven whose
`task_success` is stated relative to a baseline C0 median:

| Task | Floor | Computable at judge time? |
|---|---|---|
| A-001, A-002, A-003, A-004 | `quality_score ≥ 0.95 × C0 median` | **No** |
| C-001, C-002, C-003 | `coverage ≥ 0.90 × C0 median` | **No** |
| B-001, B-002, B-003 | `≥ 0.97` absolute | Yes |
| D-001…D-004 | binary | Yes |
| E-001, E-002, E-003 | `completion ≥ 0.95` absolute | Yes |

A blind judge cannot compute a batch median over C0 without knowing which packets are C0, which
is knowing the treatment. `judge.py` handles this correctly: the Runner injects
`required_evidence.baseline_reference_quality` (a bare float, treatment-neutral); absent, the
baseline is assumed 1.0, `floor_basis = "absolute_fallback_baseline_unavailable"` and
`relative_floor_pending = true`. `quality_score` is final on the first pass; only `task_success`
is provisional.

**What that implies for run ordering.** The 100-run matrix (§5) does not describe this
dependency, and `BLIND_EVALUATION_PROTOCOL.md` does not either. Concretely:

1. All 15 C0 runs must complete and be scored **before** any A or C `task_success` is final.
2. Every A and C packet must be scored **twice** — once at collection, once after C0 closes —
   and the second pass must use the same `judge.py` build for the result to be attributable.
3. The C0 median is a **per-task** quantity over 3 repetitions. A median of three is a single
   middle value; one anomalous C0 run moves the floor for every downstream cell of that task.
4. Because §5's freeze rule forbids reallocation, a failed C0 cell leaves the relative floor for
   that task permanently underdetermined. There is no stated fallback. This is a declared stop
   condition ("quality cannot be measured for a workload") waiting to happen.

**Is it a perverse incentive? Yes — demonstrated, not argued.** Floor moves with the baseline:

| C0 median for A-001 | Floor | Blanket zero-work answer (0.6667) |
|--:|--:|---|
| 1.00 | 0.950 | fail |
| 0.90 | 0.855 | fail |
| 0.80 | 0.760 | fail |
| 0.71 | 0.6745 | fail |
| **0.70** | **0.665** | **PASS** |
| 0.60 | 0.570 | PASS |

If C0 turns out mediocre on A-001 — plausible for a 63-member reverse transitive closure — an
intervention that reads nothing passes the frozen quality floor. A-003 has the same shape at a
C0 median ≤ 0.638. The direction is strictly wrong: the worse the baseline, the easier it is for
a token-cutting intervention to claim "quality held".

**This cannot be fixed here.** §6's wording "≥ 95% of baseline's correct set" is frozen and
immutable. Replacing it with an absolute floor, or adding a floor-of-the-floor (e.g.
`max(0.95 × C0_median, X)`), **requires a `METHODOLOGY_CHANGE_REQUEST` and a
`METHODOLOGY_v1.1.0.md` as a new file.** No seat in this lab may edit v1.0.0 to do it, and this
seat does not propose editing it. What the Lab *can* do under v1.0.0 without a change request is
report the C0 medians and the resulting floors as first-class published numbers, so a reader can
see when a pass was granted by a low bar. That is a reporting decision, not a methodology
change. The Task Set Designer pre-registered this concern (DESIGN_NOTES §7.3) and was right to
escalate rather than improvise.

---

## 2. Findings

Severity: **BLOCKING** = must change before freeze · MAJOR = must change before results are
read · MINOR = record and fix in v1.1.0.

| id | sev | where | what is wrong | how demonstrated | a fix must satisfy |
|---|---|---|---|---|---|
| **RT-01** | **BLOCKING** | `environment/harness/blind.py` `build_packet`; all 17 task files | `required_evidence` is sourced from `task.get("required_evidence", [])` and **no task file has that key**, so every packet built by the harness carries `required_evidence: []`. `judge.py` requires it for A (`valid_symbols`), D (`tool_calls`), E-001 (`catalog_part_ids`,`halberd_part_ids`) and E-003 (`shifts`,`roster`). Nothing in the lab produces it. | Scored all 17 **byte-perfect** answers with `required_evidence: []`: **10 of 17 fail** — A-001…4 `required_evidence_missing:valid_symbols`, D-001…4 `required_evidence_missing:tool_calls` (score 0.0), E-001 `…:catalog_part_ids,halberd_part_ids`, E-003 `…:shifts,roster`. | A named owner and a deterministic producer for `required_evidence`, derived from the frozen corpus, per task; and a pre-judge assertion (extend `assert_blind` or add a sibling) that fails loudly when a workload's required evidence is missing **or empty**, before packets reach the judge. It must be treatment-neutral. |
| **RT-02** | **BLOCKING** | `judge.py` `_e001_violations`, `_e003_violations` | The workload-E §6 zero-tolerance criterion **fails open** on present-but-empty evidence, contradicting `SCORING_SPEC` §2. `_e003_violations` does `if not s or not p: continue`; `_e001_violations` does `if catalog and …` / `p in halberd`. Empty containers pass the type check and silently disable V1–V5. Separately, `part_id_pattern` is a Runner-supplied regex used with `finditer`; the plausible anchored form `^KP-\d{4}$` matches nothing and disarms prose-turn V1/V3. | E-003 with `{"shifts":{},"roster":{}}`: ineligible `PR-007`→`SH-105` at turn 14 with a perfect final answer ⇒ **pass**, `zero_tolerance_breached: false`. With real CSVs ⇒ correct zero-tolerance failure. E-001 with empty lists: SCORING_SPEC §7's own protected case ⇒ **1.0 / pass**. With real lists ⇒ correct failure. `^KP-\d{4}$` vs `KP-\d{4}`: same packet, opposite verdict. | Fail-closed on *content*, not type: an empty `shifts`/`roster`/`catalog_part_ids`/`halberd_part_ids` must produce `required_evidence_missing:<field>`, never a pass. `part_id_pattern` must be specified (anchoring, `search` vs `fullmatch`) or removed in favour of an id list. A test must assert that each of V1–V6, per E task, fails a packet that breaches it and that no configuration can make it silently not fire. |
| **RT-03** | **BLOCKING** | `tasks/B/B-002.json` `notes`; `DESIGN_NOTES.md` §3; `corpora/docs_b/KESTREL_RELIABILITY_2031.md` | The claimed long-range-retrieval difficulty does not exist, and its absence biases the primary measurement. Everything the task needs (§1.4 precedence + Appendix A + Appendix B) is ~22 KB of a 147 KB document; Appendix A and B are 4 KB apart, both in the final 13%. The preceding 86% is narrative the task forbids using. A compaction/filtering condition that drops it loses nothing and saves most of the tokens. | Byte offsets: Appendix A at 127,608, Appendix B at 131,705, file length 146,666 (`grep`/`re.finditer` over the document). `BUILDER_NOTES.md` §B-002 independently found the same thing. | Either the corpus must place the corrections far from the register with payload-bearing content in between, or B-002 must stop being counted as evidence for H2/H4 and its `notes` and `DESIGN_NOTES.md` §3 must be corrected. A fix is only complete when a run that reads the last 15% of the document scores materially below one that reads it all. |
| **RT-04** | **BLOCKING** | `tasks/C/C-001.json` citation rule vs `judge.py` `_citation_support`; `answer_keys/C-001.json` | The task says *"Cite a file only if that file actually states the value you are reporting"*. `forum_thread_4111.md` states the correct `introduced_in` for `adaptive_shard_split`, and `forum_thread_4106.md` for `opportunistic_gc` — the key records this itself under `non_authoritative_files_stating_the_same_introduced_in`. Citing them is literally compliant and is scored as a **zero-tolerance traceability breach**. The metric's parenthetical says the key "lists, per value, the set of files that state it"; the key deliberately lists a curated subset, so the key contradicts the metric. Direction of harm is not neutral: it penalises broad retrieval only. | Perfect C-001 + `forum_thread_4111.md` added to one `sources` list ⇒ `quality_score 1.0`, `task_success false`, `zero_tolerance:workload_C_100_percent_traceable`. Citing only 1 of N key sources ⇒ 1.0 / pass (incompleteness is free). 2 of 16 flags carry the trap. | One sentence in the task, not in the judge, deciding whether a low-authority file that states the correct value is a valid citation — and the key's `citation_support` must then *be* the set the metric says it is. Whichever way it is ruled, the rule must be symmetric: if breadth can fail, incompleteness must cost something, or the metric must stop being one-directional. |
| **RT-05** | MAJOR | `methodology` §6 (frozen) via A-001…4, C-001…3 | Relative floors are uncomputable until C0 completes, force a two-pass scoring order the run matrix does not describe, and move *down* with a weak baseline. | Table in §Q5 above: at a C0 median of 0.70, the zero-work A-001 blanket answer (0.6667) returns `task_success: true`. | **Needs a `METHODOLOGY_CHANGE_REQUEST`** to add a floor-of-the-floor or an absolute floor; no seat may edit v1.0.0. Absent that: the run matrix must state the C0→A/C ordering dependency explicitly, the protocol must describe the re-score pass, and every published A/C pass must carry the C0 median and the derived floor beside it. |
| **RT-06** | MAJOR | `tasks/E/E-001.json`; `corpora/workflow_e/procurement_policy.md` P1/P4 | The freight rounding order is not determined by the task. Round-once gives `1197.38`; round-per-vendor gives `1197.39`. Monetary values compare as exact strings, so three of nine scalar cells flip. | Per-vendor rounding scored **0.9444** vs the 0.95 floor ⇒ `below_quality_floor`, for an otherwise perfect and policy-compliant answer. Confirms `BUILDER_NOTES` E-001 #1. | The policy or the task must state where rounding happens (per vendor, per line, once on the total). A fix is complete when both readings cannot coexist — not when the key picks one. E-001 is a C3 cell; a coin-flip failure here is noise injected straight into the H4 measurement. |
| **RT-07** | MAJOR | `tasks/B/B-001.json` N4 vs its own prompt example; `answer_keys/B-001.json` | Two fields have two readings each, both mandated by the task's own rules: `amendments_in_force_on_as_of_date` (document prints `AMENDMENT No. 1`, N4 says verbatim, the prompt's example says `Amendment No. 1`) and `governing_law` (`England and Wales` vs the verbatim `the laws of England and Wales`). The 0.97 floor tolerates exactly one. | Each alone ⇒ 0.9722 / pass. **Both together ⇒ 0.9444 / fail.** Confirms `BUILDER_NOTES` B-001 #1 and #2. | The task text must make one reading unambiguous for each field (e.g. N4 exempting this field, and naming the clause span for `governing_law`). Not fixable in the key: both readings are currently correct. |
| **RT-08** | MAJOR | `judge.py`; `SCORING_SPEC.md` §9 (omission) | Outright-failure conditions in the frozen task text that the judge never evaluates: *"any corpus file is modified"* / *"the run edits the source document"* / *"the run edits the corpus"* (all 13 A, B, C, E tasks — `corpus_modified` is read for **D only**), and A-001's *"the answer is produced without reading the corpus (empty tool-call record)"*. Neither is declared as a gap in SCORING_SPEC §9. | `grep -n "corpus_modified" judge.py` → one site, inside `_score_d`. No tool-call or corpus-read evidence exists for A anywhere in SCORING_SPEC §4 or `judge.py`. | Either the evidence fields exist and the judge evaluates them for A, B, C and E, or SCORING_SPEC §9 declares them unevaluated and the run record carries the check instead. Silently unenforced is the one option that is not acceptable — a corpus-rewriting optimisation currently scores clean, and A-001's only anti-shortcut guard does not exist. |
| **RT-09** | MAJOR | `SCORING_SPEC.md` §5 and `judge.py` `_score_c` vs `tasks/C/C-00{1,2,3}.json` | The judge applies the 0.05 `count` penalty to workload C. All three C `quality_metric`s define `quality_score = coverage` and state no such penalty. SCORING_SPEC's own precedence rule makes the task text authoritative; the divergence is not in the §9 UG table. | Perfect C-001 with `count` off by one ⇒ **0.95**, where the frozen metric gives 1.0. | Either remove the penalty for C, or record it in §9 as a declared deviation with a rationale. Two judges reading only the frozen task files get 1.0 and disagree with the harness by 5 points — that is the definition of an unstable metric. |
| **RT-10** | MAJOR | `judge.py` §3.5 + the 0.97 B floor (UG-10, self-declared) | The `count` penalty is applied before the floor test, so an otherwise **perfect** B-002 answer with a wrong `count` scores 0.95 and fails the workload-B floor outright. | Demonstrated: perfect `incidents`, `count = 25` ⇒ 0.95, `below_quality_floor`. | The task must say whether a bookkeeping slip is equivalent to a 3%-wrong extraction. The Quality Judge flagged this as "almost certainly not what the designer intended" and is right; it needs a ruling from the Designer, not a judge-side softening. |
| **RT-11** | MAJOR | `tasks/D/D-003.json`, `D-004.json`; `corpora/mcp_toolset/tools.json` | The zero-tolerance criterion keys on family membership, but three contested-family tools do not return a competing answer: `metrics.get_slo` (an SLO target, not an error budget), `calendar.get_month_boundaries` and `calendar.get_iso_week` (no fiscal answer at all), `tickets.get_queue` (a queue definition). The prompt defines a family as siblings that "look interchangeable"; these are not. One diligence call ⇒ outright failure. | Demonstrated: perfect D-004 + one `metrics.get_error_budget_raw` call ⇒ `zero_tolerance:wrong_tool_invocation`, score 0.0. Same mechanism applies to `metrics.get_slo`. Family listing taken from `tools.json`. | Either the contested-family lists are narrowed to the genuine decoy siblings, or the non-competing tools move to uncontested families. A fix is complete when every tool inside a contested family returns a plausible *answer to the task's question*, as `DESIGN_NOTES.md` §5 claims they all do. |
| **RT-12** | MAJOR | `MANIFEST.sha256`; `README.md` §Integrity | The manifest covers `tasks/` and `corpora/` only. `answer_keys/*.json` (17 files, the scoring ground truth), `answer_keys/scripts/*.py`, `SCORING_SPEC.md`, `DESIGN_NOTES.md` and `README.md` are unhashed. A key can change post-freeze and `sha256sum -c` still reports 155/155 OK. | `comm -23` of the file tree against the manifest's path column: 25 files on disk, none in the manifest. | The frozen hash must cover every file whose content can change a score. Note `README.md` says `config_hash` is the sha256 of `MANIFEST.sha256` itself, so extending the manifest changes `config_hash` — that has to happen **before** any run is executed, not after. |
| **RT-13** | MAJOR | `BLIND_EVALUATION_PROTOCOL.md` / Runner contract (UG-28, self-declared) | If the Runner ships only the final reply, four of five E-002 violation classes and most of E-001's and E-003's cannot fire. Nothing asserts that turns are supplied. | Demonstrated: byte-perfect E-002 runbook with *"just"* at turn 8 ⇒ **1.0 / pass** when `turns` is omitted; correctly fails when supplied. | The packet builder must assert `len(turns) == turn_count` for workload E and fail the packet otherwise. The Quality Judge recommended exactly this; it is still a recommendation. |
| RT-14 | MINOR | `tasks/A/A-001.json` `notes`; `DESIGN_NOTES.md` §2 | Both claim the blanket "all"/"none" answer scores "about 0.5 F1". It scores **0.6667** (P=0.5, R=1.0). The stated safety margin is 17 points too generous, which matters because A-001's floor is relative (RT-05). | Scored directly. | Correct the note, or re-scope so the claim is true. |
| RT-15 | MINOR | `tasks/E/E-002.json` `quality_metric` (UG-21) | The frozen metric contradicts itself: "5 comparable cells per key step (step_id, action, service, wave, owner_team, start_utc counts as 6 - use 6)". | Read directly; `judge.py` uses 6 and scores a perfect answer 1.0. | A frozen scoring rule must not contain a self-contradiction, even a self-resolving one. v1.1.0. |
| RT-16 | MINOR | `tasks/C/C-003.json` `contradicted_by` vs its own `expected_behavior` | Literal reading includes `registry_export_2032-02.csv` for the two erratum-corrected plugins; `expected_behavior` implies blog/forum only. The key uses the literal reading and records the other. | Alternate reading scores coverage **0.9375** (passes the 0.90 floor). Affects `kp-csv-bridge` and `kp-fx-lookup`. | One sentence settling it. Not fatal, but it moves the primary measurement by 6.25 points for reasons unrelated to run quality. |
| RT-17 | MINOR | `corpora/repo_ledgerline/ledgerline/util/retry.py` | Fifteen modules do `from ledgerline.util.retry import retryable`; `retry.py` does not define it. The corpus is not importable. `retryable_v2` *is* defined elsewhere, which makes the asymmetry actively misleading for A-003. | Confirmed via the AST pass; matches `BUILDER_NOTES` A #1. No key changes. | Define it, or state in R-rules that the corpus is not executable. A run that "corrects" itself toward `retryable_v2` loses A-003 entirely. |
| RT-18 | MINOR | `SCORING_SPEC.md` §8 | Says "81 tests"; the suite runs 100. | `python3 -m unittest test_judge` → `Ran 100 tests`. | Doc accuracy. |
| RT-19 | MINOR | `tasks/A/A-003.json` D3; `tasks/C/C-002.json` | Two instruction branches are dead in this corpus: no retry-decorated function is itself a `TransientError` raiser (D3's self-inclusion half), and no project has all its awards retracted. | `BUILDER_NOTES` A #4 and C-002 #2; confirmed against the derived keys. | Harmless, but it is instruction surface a run spends tokens reasoning about — which is itself a cost term in a token-efficiency benchmark. |
| RT-20 | MINOR | `corpora/mcp_toolset/` | Every D decoy announces itself twice: in its `description` ("Reflects the published rotation only") **and** in its response payload (`"note": "Template value. Approved overrides … are NOT applied."`). Tool selection measures "did you read one sentence", not judgement. | `tools.json` inspection + live `rota.get_nominal_shift` call. | Not a defect — but it means a D wrong-tool failure is evidence about schema *visibility* (the H1 question) and nothing else. Report it that way. |
| RT-21 | MINOR | `corpora/mcp_toolset/server.py` audit writer | `seq` restarts at 1 for each `server.py call` process, so the JSONL carries no global ordering when the Runner invokes one process per call. | Three sequential `call` invocations all logged `"seq": 1`. | No scoring impact (wrong-tool counting is order-free). Fix if any later analysis wants call order. |

**Counts: 4 BLOCKING · 9 MAJOR · 8 MINOR.**

---

## 3. Overall verdict

### NOT fit to freeze — but it is close, and the work is good.

I want to be explicit that this is not a reflexive block. The three seats produced work of
unusually high quality: 17/17 answer keys reproduce byte-identically from committed scripts, all
155 manifest entries verify, 100 judge tests pass, the tool server is deterministic and its
answers match the keys, `judge.py` fails closed almost everywhere and its §9 gap table is the
most honest artefact in the lab. Fifteen of the seventeen tasks are genuinely hard, genuinely
tool-neutral and genuinely resistant to the cheap strategy. Both the Designer and the Builder
pre-declared their own worst problems rather than hiding them, which is why this review could
spend its time confirming and measuring rather than discovering.

The block is narrow. **Four things must change before freeze:**

1. **RT-01 — `required_evidence` must have an owner and a producer.** Today the harness builds
   packets carrying `required_evidence: []`, and 10 of 17 perfect answers fail. Nothing can be
   run until this exists. It is nobody's declared deliverable, which is why it fell through.
2. **RT-02 — the workload-E zero-tolerance criterion must fail closed on empty evidence and on
   an unusable `part_id_pattern`.** As it stands, a plausible Runner configuration silently
   turns off the §6 criterion for E-001 and E-003 and reports `zero_tolerance_breached: false`.
   A zero-tolerance criterion that can be switched off without anyone noticing is worse than no
   criterion, because it produces a confident pass.
3. **RT-03 — B-002 must stop rewarding the discarding of 86% of its document,** or must stop
   counting toward H2/H4. This is the single finding most likely to produce a *wrong published
   result* rather than a failed measurement.
4. **RT-04 — C-001 must rule on whether a low-authority file that states the correct value is a
   valid citation,** and the key's `citation_support` must then match the metric's own
   description of it. Until then C-001 fails compliant runs on a zero-tolerance criterion, in a
   direction that systematically favours narrower retrieval.

**Before any result is read** (not necessarily before freeze): RT-05 through RT-13. RT-05 in
particular needs a decision at LG5 — and if the Lab wants an absolute floor under the relative
ones, that is a **`METHODOLOGY_CHANGE_REQUEST` and a new `METHODOLOGY_v1.1.0.md`**, never an
edit to v1.0.0. This seat does not propose editing it.

**Fit to freeze after the four BLOCKING items are closed and re-verified**, with RT-05's
ordering dependency written into the run plan. The MINOR findings belong in a `TASK_SET_v1.1.0`
and should not hold the freeze.

---

## 4. What I did NOT check

Read this before treating anything above as a sign-off.

* **I did not verify the corpora against their prompts by hand.** I confirmed the derivation
  scripts reproduce the committed keys byte-for-byte, and I spot-checked the D answers through
  live tool calls. I did **not** independently re-derive A, B, C or E ground truth by a second
  method. If a derivation script and its task statement share a misreading, I would not have
  caught it — the reproduction check is circular by construction.
* **I did not run any task against a real model.** Every "cheap strategy" score above is a
  constructed answer scored through `judge.py`, not an observed run. Real baselines may be far
  above or below the thresholds in §Q5; the 0.70 figure is an illustration of where the cliff
  is, not a prediction.
* **I did not read the workload-B or workload-C corpora in full.** B findings rest on byte
  offsets, section structure and the derivation scripts. I did not verify that every one of
  B-001's 36 keyed values is the value the document states, beyond the two the builder flagged.
* **I did not audit the cost/metering side at all** — `meter.py`, `pricing.py`, `calibrate.py`,
  `ENVIRONMENT_LOCK.json`, the wheelhouse, the Dockerfile, the pricing snapshot, meter
  calibration (§8) and cache control (§9) are outside this review. A quality task set says
  nothing about whether the token numbers are trustworthy.
* **I did not review `BLIND_EVALUATION_PROTOCOL.md` as a whole,** only `blind.py`'s
  `build_packet` and `assert_blind` where they bear on `required_evidence` and on packet shape.
  I did not test the un-blinding path, the salt handling, or whether the treatment labels
  actually stay hidden across a full run.
* **I did not check the seat registry invariants,** the LG2 security review, candidate identity,
  or `PINS.txt`. I took the Designer's isolation claim (DESIGN_NOTES §0) at its word; I found
  no evidence contradicting it, but I did not attempt to verify it.
* **I did not exhaustively fuzz `judge.py`.** I ran roughly sixty hand-built adversarial
  packets chosen to probe the metrics I distrusted most. `score_packet` never raised and never
  returned `judge_internal_error` in any of them, but that is a sample, not a proof of totality.
* **I did not test workload E's multi-turn delivery contract end-to-end,** because no harness
  currently delivers it. RT-13 is inferred from `judge.py`'s behaviour on packets I constructed,
  not observed from a real 18-turn run.
* **I did not evaluate whether the 17 tasks are collectively sufficient** to answer H1–H4. My
  scope was whether each task is sound, not whether the set has the statistical power the
  100-run matrix assumes. Three repetitions per cell against binary `task_success` is a
  question for the Methodology Reviewer, not for me.

# Lab 001 — Scoring Specification v1.1.0

**Status:** DRAFT, tracking `METHODOLOGY_v1.1.0.md` (itself DRAFT / REVIEW_PENDING)
**Owner:** Quality Judge seat · **Binds:** every packet scored under methodology v1.1.0
**Implements:** `methodology/METHODOLOGY_v1.1.0.md` §6 (absolute floors), §6.1 (attempt / cell /
aggregate), §6.2 (the three-outcome taxonomy), §12.1 (evidence contract), §13 (versioning and
refusal), and the `quality_metric` / `failure_condition` of each of the 17 tasks in
`tasks/TASK_SET_v1.1.0/tasks/`
**Executable form:** `environment/harness/judge.py` · **Tests:** `environment/harness/test_judge.py`
**Supersedes:** `tasks/TASK_SET_v1.0.0/SCORING_SPEC.md`, which is **not edited** and remains the
normative document for any packet that declares methodology v1.0.0.

This document is the normative scoring procedure. `judge.py` is its implementation: where the two
disagree, this document states the intent and the module has the bug. Where **this document**
disagrees with a v1.1.0 task file or with the methodology, those win and this document is the
defect report. Nothing here modifies a task, a corpus or an answer key.

**What is new in v1.1.0, in one paragraph.** Quality floors are absolute and answer-key-anchored;
no baseline may reach `task_success` (§3.7). Every result carries an `outcome` of exactly `PASS`,
`FAIL_QUALITY` or `INVALID`, and "we could not measure it" is never reported as either a pass or a
quality failure (§2.1). A packet whose methodology version is absent or unrecognised is refused
(§1.1). Required evidence is checked for **content**, so `{}` and `[]` fail closed (§4). The
`count` field is scored three different ways, each ruled in the task text, and the flat 0.05
penalty is gone (§3.5). Corpus integrity and the corpus-read condition are evaluated for every
workload, not for D alone (§4.2). Workload E's transcript must be complete or the attempt is
`INVALID` (§4.3). Workload C's citation rule is symmetric: an uncited governing source now costs
(§5, workload C).

---

## 1. Scope and contract

The Quality Judge scores **blind judge packets**. A v1.1.0 packet carries exactly these ten keys:

```
packet_id  task_id  workload  blind_treatment_id  model_output
required_evidence  answer_key  quality_metric  failure_condition  methodology_version
```

`methodology_version` is the tenth and it is new. It is treatment-neutral — it names the rulebook,
not the condition — and without it the packet cannot be scored at all.

`score_packet(packet: dict) -> dict` returns at least:

| field | type | meaning |
|---|---|---|
| `packet_id` | string | echoed from the packet |
| `quality_score` | float in [0,1] | the workload's quality number, 4 dp. **0.0 whenever `outcome` is `INVALID`** |
| `task_success` | boolean | `outcome == "PASS"`; the **attempt** met its floor and breached nothing |
| `outcome` | `PASS` / `FAIL_QUALITY` / `INVALID` | methodology §6.2 |
| `failure_reason` | string or null | why; null only when `PASS` |
| `zero_tolerance_breached` | boolean | a criterion that fails the attempt whatever the score |
| `detail` | object | every intermediate number, so the result is auditable and re-derivable. `detail.level` is always `"attempt"` |

**Level.** Everything this module produces is **attempt-level** (methodology §6.1). It computes no
cell success rate and applies no cell threshold — D's 95% least of all. That number is the
Runner/Aggregator's, applied once, at the cell level, over `outcome` values. `detail.level` says so
on every result, and `test_B5_the_d_attempt_threshold_0_95_exists_nowhere_in_the_judge` asserts the
constant does not appear in the workload-D path at all.

**Isolation.** The scorer copies the allowed keys into a fresh mapping and reads only that copy. A
packet that leaks a token count, a cost, a model name or a condition label cannot change a score;
the leaked key names are listed in `detail.ignored_packet_keys` with `detail.blind_warning` set.
The same list also carries the evidence fields this version deliberately does **not** read (§4.4).

**Determinism.** No clock, no randomness, no network, no filesystem read during scoring, no
iteration over an unordered structure without sorting. The same packet always scores the same.
Standard library only.

**Totality.** `score_packet` never raises. Every failure mode produces a score, not a traceback.
The single `except` around dispatch is a contract backstop; if it fires the result is
`judge_internal_error`, which is `INVALID`.

### 1.1 Version gate and refusal (methodology §13)

The version is resolved, in order, from `packet.methodology_version`,
`answer_key.methodology_version`, `required_evidence.methodology_version`. A leading `v` is
accepted; nothing else is normalised.

| Situation | Result |
|---|---|
| resolves to `1.1.0` | scored under this document |
| resolves to `1.0.0` | scored under `TASK_SET_v1.0.0/SCORING_SPEC.md`, unchanged, for **replay of v1.0.0 records** |
| absent | `INVALID`, `methodology_version_absent`, `quality_score = 0.0` |
| present but not one of the two | `INVALID`, `methodology_version_unsupported` |

Refusal is not a quality judgement: a byte-perfect answer in an unversioned packet is refused too.
There is no default and no guess, because a guess is exactly how a v1.0.0 relative floor would
survive into a v1.1.0 result.

> **Open handoff — Harness/Evidence Producer.** `blind.build_packet` does not currently set
> `methodology_version` on the packet it constructs, so every packet it builds today is refused.
> Any one of the three sources above satisfies the gate. This is a one-line change in a file this
> seat does not own; it is named here so it cannot fall between seats the way RT-01 did.

### 1.2 What is version-gated and what is not

Two different kinds of change came out of the Red Team review, and they are treated differently.

* **Rules that changed** — floors, the `count` rule, the citation rule, D's extra-key rule, the
  corpus and transcript conditions — apply **only** to v1.1.0 packets. A v1.0.0 record replays to
  the number it originally scored.
* **Fail-open defects** — an empty container passing a type check (RT-02), a packet-supplied regex
  able to disarm a check — are repaired on **both** paths. v1.0.0's own §2 already required
  fail-closed behaviour; making the module do what its spec said is a defect repair, not a version
  change, and it can only ever withhold a pass, never grant one.

---

## 2. Zero tolerance

Methodology v1.1.0 §6 fixes the same zero-tolerance criteria v1.0.0 did:

| Workload | Criterion |
|---|---|
| A | zero fabricated symbols |
| B | no fabricated record id |
| C | traceability = 1.00 |
| D | zero wrong-tool invocations |
| E | zero constraint violations across every turn that occurred |

Implemented literally: a breach sets `task_success = false`, `zero_tolerance_breached = true`,
`outcome = FAIL_QUALITY`, and **`quality_score` is still reported at its true value**. A
fabrication on an otherwise perfect answer is `quality_score ≈ 1.0, outcome FAIL_QUALITY`. Zeroing
it would hide the shape of the failure. `detail.zero_tolerance` lists each breached criterion, its
source and its instances.

Several tasks add outright-failure conditions §6 does not name — a fabricated `incident_id`, an
undersized A-004 component, a cited file that does not exist, reading `fixtures/`, a modified
corpus, an answer produced without reading the corpus. Those of the *fabrication* kind also set
`zero_tolerance_breached`; the structural ones fail the attempt with
`zero_tolerance_breached = false`, so the two can be told apart in aggregate.

**Fail-closed.** A zero-tolerance criterion that cannot be *verified* from the packet never passes.
It is `INVALID`, not a failure of the run — see §2.1.

**A confirmed breach outranks missing evidence.** If the scorer found a violation, that is a
finding and it is reported as `FAIL_QUALITY`, even when some other evidence field is absent.

### 2.1 The three outcomes (methodology §6.2)

| Outcome | Meaning | `task_success` | `quality_score` |
|---|---|---|---|
| `PASS` | scored, met the floor, breached nothing | true | the real number |
| `FAIL_QUALITY` | scored, missed the floor or breached zero tolerance | false | the real number |
| `INVALID` | could not be scored: missing, empty, wrongly typed or wrong-run evidence; an unusable answer key; an incomplete transcript; a refused version | false | **0.0**, with the number that had been computed retained in `detail.unverified_quality_score` |

`INVALID` reasons are recognised by prefix: `required_evidence_missing:`,
`required_evidence_empty:`, `evidence_incomplete:`, `evidence_from_wrong_run`,
`answer_key_unavailable`, `packet_unreadable`, `judge_internal_error`, `unknown_task_id`,
`unknown_workload`, `methodology_version_absent`, `methodology_version_unsupported`. Everything
else that is not a pass is `FAIL_QUALITY`.

**Why `INVALID` carries no quality score.** An attempt whose evidence could not be verified has no
quality number that means anything, and reporting one invites an aggregator to average it. 0.0 can
never flatter a result; the computed value stays in `detail` so the failure is still auditable.
`INVALID` must not be deleted, folded into a savings average, or replaced by an automatic re-run,
and it stays in the cell denominator — all of which is the Aggregator's obligation, not this
module's.

---

## 3. Common procedures

### 3.1 Extracting the answer object

`model_output` is the reply text. Extraction is attempted in this fixed order and recorded in
`detail.parse_mode`: `strict` (the whole stripped reply parses) · `fence_stripped` (one markdown
fence) · `embedded_object` (the first **balanced** `{…}` span, string- and escape-aware) ·
`unparseable` / `empty`. Modes 2 and 3 set `detail.format_strict = false` and do **not** fail the
task (§9 UG-01).

### 3.2 Malformed output

| Situation | quality_score | outcome | failure_reason |
|---|--:|---|---|
| `model_output` empty, whitespace-only or null | 0.0 | FAIL_QUALITY | `empty_output` |
| no balanced JSON object recoverable | 0.0 | FAIL_QUALITY | `unparseable_output` |
| unbalanced `{` (truncation signature) | 0.0 | FAIL_QUALITY | `unparseable_output`, `detail.truncation_suspected` |
| a declared required key absent | 0.0 | FAIL_QUALITY | `missing_required_keys` |
| a required key present but wrongly typed | 0.0 | FAIL_QUALITY | `required_key_wrong_type` |
| `answer_key` absent, empty or wrongly shaped | 0.0 | **INVALID** | `answer_key_unavailable` |
| packet file unreadable (CLI) | 0.0 | **INVALID** | `packet_unreadable` |

An unusable answer key is a failure of the measurement, not of the run: that row moved from
"strict" to `INVALID` in v1.1.0.

### 3.3 Cell comparison

Type class must match (`number`, `string`, `boolean`, `array`, `object`, `null` are distinct, so
`"30"` never equals `30` and `true` never equals `1`); numbers compare within `1e-9` except where a
task states a tolerance; strings compare case-sensitively after stripping; `null` is a value and an
**absent** key does not match `null`; arrays compare element-wise and **ordered** by default,
sorted only where the task says so (C-002 `awards_*`, C-003 `contradicted_by`). Every string on
both sides is stripped before comparison, as all 17 v1.1.0 metrics now require (UG-30).

### 3.4 Record matching

Where a metric matches records on an id: `matched_cells` counts only cells of key records with a
reported counterpart; a key record with no counterpart contributes `ncells` and 0 matches; a
reported record whose id is not in the key **adds `ncells` to the denominator**; a reported record
that is not an object, or whose id is not a string, is an extra record. **Duplicate ids:** the
first in emitted order is scored, each later duplicate is an extra record (UG-09, now stated in
every task).

### 3.5 The `count` field — three rules, each ruled in the task text

v1.0.0 subtracted a flat 0.05 everywhere, including from workload C, whose metrics never asked for
it (RT-09), and including before a 0.97 floor, so a perfect B extraction with a bookkeeping slip
failed outright (RT-10). The v1.1.0 task text rules all of it:

| Task | Rule | Where it is ruled |
|---|---|---|
| A-001…A-004 | subtract **0.02**, report `count_consistent: false` | each A metric, "This replaces v1.0.0's 0.05" |
| B-002, B-003 | **one ordinary comparable cell**: denominator `7·|K| + 1` / `4·|K| + 1` | each B metric, "RULING (closes RT-10)" |
| B-001 | no `count` field exists | — |
| C-001…C-003 | **no effect at all** on coverage, on traceability or on pass/fail; reported as `count_consistent` | each C metric |

The judge resolves the rule from the packet's own `quality_metric` text first and from a frozen
transcription table second, records which in `detail.count_rule_basis`, and records any
disagreement in `detail.count_rule_task_text_disagrees_with_frozen_table`. The task text wins. A
test scores the real v1.1.0 task files through both routes and fails if they ever diverge, so a
later Designer ruling cannot drift away from the scorer unnoticed.

### 3.6 Rounding

Scores round to 4 dp, half away from zero. Floor comparisons use the rounded score against the
rounded floor with a `1e-9` slack.

### 3.7 Floors — absolute, and nothing else reaches them

| Workload | Floor, per attempt, against the full answer key |
|---|---|
| A | `quality_score ≥ 0.95` |
| B | `quality_score ≥ 0.97` |
| C | `coverage ≥ 0.90` **and** `traceability = 1.00` |
| D | correct tool **and** correct answer for this attempt (binary) |
| E | `completion ≥ 0.95` |

`detail.floor_basis` is `absolute_answer_key_methodology_v1.1.0_s6` and
`detail.baseline_influenced_task_success` is `false`, always. Under v1.1.0 the scorer does not read
`baseline_reference_quality`: there is no default baseline, no second pass and no re-score branch.
If a packet carries one it is listed in `detail.ignored_packet_keys` as
`required_evidence.baseline_reference_quality`. Scoring the same packet with seven different
baselines produces byte-identical results.

The v1.0.0 relative path — `multiplier × the injected C0 median`, falling back to a baseline of
1.0 — still exists and is reachable **only** from a packet that declares methodology 1.0.0.

**Passing a floor means the attempt reached the minimum acceptable quality. It does not mean
quality equals C0**, and no report may say so (methodology §6.0).

---

## 4. `required_evidence` — what the packet must carry

`required_evidence` is produced by `environment/harness/evidence.py` and is
**treatment-neutral**: static facts come from the frozen corpus, dynamic facts from the runner's
own audit, never from the model's self-report. None of it identifies a treatment.

**Emptiness is a content check, not a type check.** `{}` and `[]` are missing evidence, not
evidence. Missing or empty required evidence is `INVALID` with
`required_evidence_missing:<field>` or `required_evidence_empty:<field>` — never a pass, and never
a quality failure.

### 4.1 The fields

| Scope | Field | Type | Minimum | Purpose |
|---|---|---|--:|---|
| all | `corpus_hashes_before` (alias `corpus_hashes`) | {path: sha256} | 1 | corpus integrity, §4.2 |
| all | `corpus_hashes_after` | {path: sha256} | 1 | corpus integrity, §4.2 |
| A | `valid_symbols` | [string] | 1 | defines "not fabricated" |
| A-001, D-* | `corpus_access_log` (aliases `file_access_log`, `files_opened`) | [path] | — | §4.2 |
| B-002 / B-003 | `document_incident_ids` / `document_req_ids` | [string] | 1 | fabricated-record check |
| C | `corpus_files` | [string] | 1 | "this file exists" check |
| C-002 / C-003 | `document_award_ids` / `registry_plugin_ids` | [string] | 1 | fabricated-identifier check |
| D | `tool_calls` | [{`tool`,`family`}] | 1 | the zero-tolerance basis |
| E | `turns` | [{turn, text}] | complete | §4.3 |
| E-001 | `catalog_part_ids`, `halberd_part_ids` | [string] | 1, 1 | V1 / V3 |
| E-003 | `shifts`, `roster` | {id: {…}} | 1, 1 | V1–V5 |
| E | `precomputed_violations` | [{turn, code, subject}] | 0 | unioned in, never replacing |

The minima are **this task set's contract**, not a blanket rule: `parts_catalog.csv` holds 24
parts, 4 of them Halberd Manufacturing's; `shifts.csv` holds 12 shifts and `staff_roster.csv` 16
people. None of those sets can legitimately be empty, so an empty one is a broken evidence
producer. Where a set *may* legitimately be empty it carries a minimum of 0 and its emptiness is
read as a fact about the run, never as a violation and never as missing evidence:
`precomputed_violations`, and `corpus_access_log` for A-001 (§4.2).

The answer key additionally carries, beyond the expected payload: **D** `required_tools` — a
**permission** list, not a checklist (UG-17, ruled in each D metric); **C** `citation_support` —
the **governing sources** per record (§5, workload C).

### 4.2 Corpus integrity and the corpus-read condition (RT-08)

Thirteen A/B/C/E tasks and all four D tasks carry "any corpus file is modified" (or its
task-specific wording) as an outright failure. v1.0.0 read `corpus_modified` for **D only** and
declared the gap nowhere; a corpus-rewriting optimisation scored clean. v1.1.0 evaluates it for
every workload, from the evidence the task text now specifies:

* **modified** when a path present in **both** hash maps has different hashes, or when a path in
  `corpus_hashes_before` is **absent** from `corpus_hashes_after` ⇒ `corpus_modified`,
  `FAIL_QUALITY`;
* either map absent, wrongly typed or **empty** ⇒ `required_evidence_missing:corpus_hashes`,
  `INVALID`;
* scoped per workload — A `repo_ledgerline`, B `docs_b`, C `research_c`, D `mcp_toolset`,
  E `workflow_e` — so a change in another task's corpus is not this attempt's failure. If no path
  in the map names the task's directory at all, every path is in scope, so a harness that ships
  already-relative paths is not silently read as "nothing to check".

**A-001's corpus-read condition**, which had no implementation at all in v1.0.0: a CORPUS READ is
an entry in `corpus_access_log` resolving inside `corpora/repo_ledgerline/`. No such entry ⇒
`answered_without_reading_the_corpus`, `FAIL_QUALITY` — the list being *present and empty* is the
finding. `corpus_access_log` **absent** ⇒ `required_evidence_missing:corpus_access_log`, `INVALID`.

**D's fixture-read condition** moves to the same field: any entry resolving inside
`corpora/mcp_toolset/fixtures/` ⇒ `fixtures_read_tool_selection_unmeasurable`. Absent **or empty**
⇒ `required_evidence_missing:corpus_access_log`, per D's own wording.

> **Open handoff — Harness/Evidence Producer.** `evidence.py` today produces `corpus_hashes` (the
> start-of-run map) but neither `corpus_hashes_after` nor `corpus_access_log`. Both are named in
> all 17 v1.1.0 task texts. Until they are produced, every v1.1.0 attempt is `INVALID` — which is
> the correct fail-closed behaviour and is exactly why it is written here rather than worked
> around.

### 4.3 Workload E: the transcript must be complete (RT-13)

A reply that was never shipped cannot be shown to be clean. Under v1.0.0 a byte-perfect E-002
runbook with a violation at turn 8 scored **1.0 / pass** when `turns` was omitted.

* The **turn count is frozen in the scorer** — E-001 18, E-002 16, E-003 20, transcribed from the
  task files' `input.turn_count` — so omitting or shrinking a packet's `turn_count` cannot shrink
  the requirement. A packet that disagrees has the disagreement recorded and the frozen value used.
* The covered turn set is `{turn numbers in turns} ∪ {final turn}` and must equal `1…N`. Turn
  numbers must be ascending and unique.
* Short, truncated, reordered or duplicated ⇒ `evidence_incomplete:turns`, `INVALID`.
* When `required_evidence.turns` is supplied it **is** the transcript (methodology §12.1: turns are
  captured by the runner, never asserted by the agent). `model_output` still carries the final
  answer that completion is scored against. `detail.turns_source` records which was used.

`blind.assert_evidence_sufficient` makes the same assertion at packet-build time. Both exist on
purpose: the builder stops a bad packet being written, the judge stops a bad packet being scored.

### 4.4 Evidence this version deliberately does not read

Each of these could silently go missing and take a check with it. Each is listed in
`detail.ignored_packet_keys` when present.

| Field | Why not |
|---|---|
| `baseline_reference_quality` | methodology §6.0.1(2): it may not determine `task_success` |
| `part_id_pattern` | RT-02: a runner-supplied regex used with `finditer`; the plausible anchored form `^KP-\d{4}$` matched nothing and disarmed E-001 V1/V3. Replaced by a pattern **derived from the frozen id lists** (§6) |
| `additional_on_leave`, `max_shifts_overrides` | UG-27: E-003's two mid-conversation changes are fixed by the conversation and frozen in the task text — "nothing is read from `required_evidence` for V5" |
| `fixture_reads` | superseded by `corpus_access_log` (§4.2) |
| `corpus_modified` | superseded by the hash pair (§4.2) |

### 4.5 Wrong-run evidence

If `required_evidence.packet_id` or `required_evidence.task_id` is present and disagrees with the
packet's own, the result is `evidence_from_wrong_run`, `INVALID`. Evidence from another run is not
this attempt's evidence.

---

## 5. Per-workload procedure

### Workload A — repository / code analysis

**A-001…A-003** — set F1 over the single list field. De-duplicate the reported list (not an
error); `TP/FP/FN` over stripped strings; `quality_score = 2TP/(2TP+FP+FN)`; subtract 0.02 if
`count` disagrees with the de-duplicated length; any reported entry not in `valid_symbols` —
including any non-string entry — is a fabricated symbol and one is a zero-tolerance breach;
`task_success` = `quality_score ≥ 0.95` **and** zero fabrications. `valid_symbols` absent **or
empty** ⇒ `required_evidence_missing:valid_symbols`, `INVALID` — never "no fabrications found",
and never "every symbol is fabricated".

**A-004** — components as sets of frozensets, members and components de-duplicated; a reported
component matches only on exact equality; `component_count` compares against the **emitted** outer
length and disagreement subtracts 0.02; a fabricated member is a zero-tolerance breach; a component
with fewer than two members is an outright failure with `zero_tolerance_breached = false`.

**A-001 only** additionally fails outright when the corpus was never read (§4.2).

### Workload B — long-document extraction

**B-001** — field-level exact match over the 36 keys of `contract_terms`; extra keys ignored and
listed in `detail.extra_fields`; `quality_score = matched / 36`; floor 0.97, i.e. at most one
mismatched field.

**B-002 / B-003** — record matching on `incident_id` (7 cells) / `req_id` (4 cells), **plus one
cell for `count`**; any reported id not in `document_*_ids` is a fabricated record ⇒ outright
failure with `zero_tolerance_breached = true`; floor 0.97. The identifier evidence is mandatory and
non-empty: without it the fabrication check is unverifiable and the attempt is `INVALID`.

### Workload C — multi-source research

`quality_score = coverage`. `count` changes nothing (§3.5).

**Coverage** — record matching (§3.4): C-001 on `flag` (3 cells), C-002 on `project` (4 cells,
`awards_*` as sorted lists), C-003 on `plugin_id` (4 cells, `contradicted_by` as a sorted list).
An absent key of a record mismatches that cell even where the key's value is `null` (UG-14).

**Traceability — the v1.1.0 citation rule (RT-04).** The key supplies, per record, the set of
**governing sources**; that set *is* the set the metric describes, with no curated subset.

```
traceability = supported_citations / (total_citations + missing_citations)
```

* `total_citations` — the number of **distinct** file names in each reported record's `sources`.
* a cited file is **supported** iff it is in that record's governing set, which is built entirely
  from the key. The governing set is **per field, over the values the record actually reported**:
  the union of `citation_support[field]` for every scored field the reported record contains. A
  field the run did not report grants nothing and owes nothing. The **id field is excluded** — it
  is how the record is matched, not a value claimed from a source.
* the **record-level set is a fallback, not an addition**. It applies only to a key that gives no
  per-field breakdown at all (v1.0.0's C-002 `{"per_award": {…}}` shape), and it is the key
  record's own `sources` plus the file names in any non-per-field part of the blob. Adding it *on
  top of* a per-field breakdown is what made the breakdown a no-op: a citation then counted as
  supported if it governed *any* field of the record, including one the run never reported, and a
  run that reported a subset of fields owed citations for fields it had made no claim about.
  `detail.citation_support_basis` records which rule each record was scored under.
* **`citation_support` is parsed structurally, not by collecting every string it contains.** A
  governing source is a **file name**; a value that is not shaped like one is rejected and listed
  in `detail.citation_support_rejected_strings`, never promoted into a requirement. This is not
  hygiene. The v1.0.0 C-002 key carried a prose `note` inside `citation_support`; absorbed as a
  string it became a mandatory, uncitable governing source, and that key's **own perfect answer**
  scored traceability **0.72** with **7 missing citations** and a zero-tolerance breach — every
  C-002 attempt, in every condition, would have failed outright. `TestDeliveredCKeysRoundTrip`
  scores each shipped workload-C key against its own payload so a key that makes its task
  unpassable is caught by the suite rather than by the run.
* `missing_citations` — every governing source of a reported value that is **absent** from the
  record's `sources`. An empty `sources` list contributes one missing citation per governing
  source, and never fewer than one.
* a citation in a record whose id is not in the key is unsupported.
* a cited file not in `corpus_files` is unsupported **and** an outright failure
  (`cited_file_absent_from_corpus`).
* a key that carries no governing-source data at all ⇒
  `required_evidence_missing:citation_support`, `INVALID`. Traceability is the workload-C
  zero-tolerance criterion; an answer key that cannot support it makes the attempt unscorable, not
  failed.

This is the symmetry RT-04 demanded: under v1.0.0 breadth could fail an attempt and incompleteness
was free, which penalised broad retrieval only. Now citing a non-governing file lowers
traceability through the numerator and failing to cite a governing one raises the denominator.

> **Dependency — Answer Key Builder.** The key's `citation_support` must be a **per-field map**
> whose per-field lists are *exactly* the governing sources of that field. A file listed under a
> field it does not govern forces a correct run to cite it; a governing file omitted makes a
> correct citation unsupported. The metric says this explicitly ("with no curated subset and no
> separate list of coincidentally-correct files"); it is repeated here because the scorer cannot
> tell a wrong governing set from a right one. What the scorer *can* now tell is that a value is
> not a file name at all, and it rejects those rather than requiring them.

`task_success` = `traceability == 1.0` **and** `coverage ≥ 0.90` **and** no fabricated identifier.

### Workload D — MCP-heavy multi-tool

Binary by construction; both components always reported.

**Tool selection**, evaluated first because it is the zero-tolerance one. For each object in
`tool_calls`: `family == "meta"` is never counted; a `family` in this task's **contested families**
whose `tool` is not in `answer_key.required_tools` is a wrong-tool invocation, counted per call;
any other family is an extraneous call with no effect. The contested families are **frozen in
`judge.py`**, transcribed from the task files, so the basis of a zero-tolerance criterion cannot be
narrowed by whatever built the packet; a packet that disagrees has the disagreement recorded and
ignored.

`tool_calls` absent **or empty** ⇒ `required_evidence_missing:tool_calls`, `INVALID`. An empty
audit is indistinguishable from a run that called nothing, so it is never read as "no wrong tools
were called". (Under v1.0.0 an empty list was `answered_without_calling_any_tool`, a quality
failure; the v1.1.0 metric rules it unevaluable instead.)

**Answer correctness** — every required field must be present and match. **Extra keys are ignored**
and listed in `detail.extra_fields` (UG-19, reversed by the v1.1.0 task ruling: discarding a
correct D answer because the reply also carried `"confidence"` destroyed a D observation for a
reason unrelated to tool selection, and reply verbosity is a plausible treatment-correlated
artefact). A **missing** required key remains an outright failure.
`D-004.remaining_error_budget_minutes` compares with an absolute tolerance of `1e-6` (UG-20).

`quality_score = 1.0` iff `answer_correct` and `wrong_tool_invocations == 0`, else `0.0`.
Independently outright-failing: any wrong-tool invocation, a fixture read, a modified corpus, an
unparseable reply.

**§6's "≥ 95% task success" for D is a cell success rate.** It is not applied here, anywhere.

### Workload E — long multi-turn workflow

Transcript per §4.3. Completion:

* **E-001** — `bom` matched on `part_id`, 5 cells per row, plus the 9 scalars at one cell each.
* **E-002** — `steps` matched **positionally**, **6** cells per step, plus `step_count` and
  `total_duration_minutes`. Six, not five: the v1.1.0 metric removes v1.0.0's self-contradiction
  (RT-15 / UG-21).
* **E-003** — `assignments` matched on `shift_id`, 2 cells, plus `unfilled_count`.

**Constraint violations**, over every supplied reply and the final answer, instance key
`(turn, code, subject)` as the v1.1.0 metrics now define it (UG-26). `precomputed_violations` are
unioned in and never replace the scorer's own.

E-001: `V1` part id not in the catalogue · `V2` a monetary field (the six scalars plus each row's
`unit_price_eur` / `line_total_eur`, and no others) that is not a string matching
`^[0-9]+\.[0-9]{2}$` · `V3` an excluded-vendor **part id** at or after turn 3 · `V4` `bom` not
sorted ascending · `V5` fewer rows than the key, or a `qty` below the key's · `V6` `within_cap`
true where the key says false, or `amount_over_cap_eur` `"0.00"` where the key says otherwise.

E-002: `V1` `kestrel-vault` as a step's service at or after turn 3 · `V2` whole-word
`simply`/`just` at or after turn 4 · `V3` a `step_id` not of the form `MIG-nnn`, or a gap, repeat
or start other than `MIG-001` · `V4` `kestrel-mailer` as a step's service at or after turn 9 ·
`V5` a timestamp at or after turn 6 not matching `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`.

E-003: `V1` certification mismatch · `V2` site mismatch · `V3` a person whose roster `status` is
`on_leave`, **or PR-014 at or after turn 12** · `V4` a night shift filled by someone not
night-qualified · `V5` more shifts than `max_shifts` as it stands at that turn, **PR-016's being 3
from turn 16 onward and in the final answer** · `V6` a `reason_if_unfilled` outside the four
permitted strings, or a filled shift breaching V1–V5, or a `shift_id`/person id **not in the frozen
corpus** in a structured assignment.

V3's turn-12 change and V5's turn-16 change are **frozen in `judge.py` from the task text**, not
read from evidence (UG-27). An evidence field that can go missing takes its check with it.

**Fail-closed on content.** E-001's V1/V3 need a non-empty `catalog_part_ids` and
`halberd_part_ids`; E-003's V1–V5 need a non-empty `shifts` and `roster`. Empty ⇒
`required_evidence_empty:<fields>`, `INVALID`. With no tables at all the scorer also does **not**
invent an "unknown entity" violation — that would be the mirror image of the fail-open bug.

---

## 6. Detection rules for prose-scoped constraints

| Constraint | Mechanical rule |
|---|---|
| E-001 V1/V3, prose part ids | The prose scanner is a regex **derived from the frozen `catalog_part_ids` ∪ `halberd_part_ids`**: every digit run generalised, everything else literal (`KP-1010` → `KP-\d{4}`), unanchored and word-bounded by construction. A packet cannot supply, anchor, break or empty it, and a token of a catalogued shape that is not in the catalogue fires V1. |
| E-001 V3, vendor in prose | Keys on excluded-vendor **part ids**, never the vendor name: "Halberd Manufacturing is excluded, so I am not proposing their appliance" fires nothing. Every such prose mention is recorded in `detail.unadjudicated_mentions` (§9 UG-24). |
| E-002 V1/V4 | Structural: the service appears as `service` in an object that also carries `step_id`/`action`/`wave`/`start_utc`, or as a token on a line containing a `MIG-nnn` identifier. Turn 13's correct answer — "no step references kestrel-vault" — fires nothing, and is recorded in `detail.unadjudicated_mentions`. |
| E-002 V5 | A timestamp is a token carrying **both** a date and a time of day. A bare `2032-05-10` is not a timestamp. |
| E-003 per-turn assignments | Pairs are taken from JSON objects carrying both `shift_id` and a person id. Only when a reply contains no such object does the scorer fall back to one `SH-nnn` and one `PR-nnn` on the same line; in that fallback an id absent from the corpus fires nothing, because prose may legitimately name one. |

---

## 7. Worked interaction: a high score that fails

| Workload | Answer | quality_score | outcome |
|---|---|--:|---|
| A-001 | all 5 key symbols **plus one invented name** | 0.9091 | `FAIL_QUALITY` — `zero_tolerance:fabricated_symbol` |
| A-001 | the blanket answer, at a C0 median of 0.70 | 0.6667 | `FAIL_QUALITY` — **passed under v1.0.0**, fails here |
| B-002 | both key incidents perfect **plus one invented `INC-…`** | 0.6667 | `FAIL_QUALITY` — fabricated record id |
| C-001 | every value correct, one governing source not cited | 1.0 | `FAIL_QUALITY` — traceability < 1.0 |
| D-001 | all fields correct, one contested sibling called "only to look" | 0.0 | `FAIL_QUALITY` — wrong-tool invocation |
| D-001 | all fields correct, `tool_calls: []` | 0.0 | **`INVALID`** — not "no wrong tools were called" |
| E-002 | runbook byte-perfect, turn 8 said "just" | 1.0 | `FAIL_QUALITY` — V2 at turn 8 |
| E-002 | runbook byte-perfect, `turns` omitted | 0.0 | **`INVALID`** — **passed 1.0 under v1.0.0** |
| E-003 | perfect final answer, `{"shifts":{},"roster":{}}` | 0.0 | **`INVALID`** — **passed under v1.0.0 with an ineligible assignment at turn 14** |

A scorer that averaged these away would pass every other test in `test_judge.py`.

---

## 8. Running it

```bash
cd environment/harness
python3 -m unittest test_judge              # 240 tests
python3 judge.py --packets judge_packets/ --scores judge_scores/
```

**240 tests.** (v1.0.0's §8 said "81" when the suite ran 100 — RT-18. The number above is the
number the suite reports; if they ever differ again, the suite is right.) 100 of them are v1.0.0
replay cases, unchanged and still passing, which is what makes the v1.1.0 cases regression tests
rather than restatements: several score the **same packet** under both versions and assert that
the two disagree.

The CLI writes one `<packet_id>.json` per packet plus `_SUMMARY.json`, which carries
`outcome_counts` and `level: "attempt"` and states that cell success rates are the Aggregator's. A
packet file that will not parse is scored `packet_unreadable` / `INVALID`, not skipped.

### 8.1 Acceptance tests from `METHODOLOGY_CHANGE_REVIEW_001`

| # | Test | Where |
|---|---|---|
| A-1 | blanket answer, no baseline ⇒ 0.6667, fail | `TestAcceptanceCR001A.test_A1_…` |
| A-2 | same packet, C0 median 1.00 ⇒ identical | `…test_A2_…` |
| A-3 | same packet, C0 median 0.70 ⇒ identical, **and v1.0.0 still passes it** | `…test_A3_…` |
| A-4 | scored twice with different external C0 ⇒ byte-identical | `…test_A4_…` (both) |
| A-5 | `baseline_reference_quality` ignored, recorded | `…test_A5_…` |
| A-6 | missing/unrecognised version ⇒ refused | `…test_A6_…`, `TestVersionGate` |
| B-1 | D cell, 2 of 3 passing | `TestAcceptanceCR001B.test_B1_…` — **attempt outcomes only; the cell verdict is the Aggregator's** |
| B-2 | D cell, 3 of 3 passing, no "≥95%" claim | `…test_B2_…` — asserts the judge emits no rate |
| B-3 | one `INVALID`, two `PASS`, all three distinguishable | `…test_B3_…` |
| B-4 | zero-tolerance breach at quality 1.00 ⇒ attempt fails | `…test_B4_…` |
| B-5 | no attempt-level 0.95 for D anywhere | `…test_B5_…` (source assertion + behaviour) |

**B-1, B-2 and B-3 are cell-level and the cell is not this seat's unit.** What is implemented here
is the attempt-level contract a cell is computed *from*: three attempts yielding
`PASS / PASS / FAIL_QUALITY` and `PASS / FAIL_QUALITY / INVALID` respectively, each distinguishable
by `outcome`, none carrying a rate. The arithmetic the tests name — 2 passing ÷ **3 planned** =
0.667, which fails a cell requiring 3/3 — belongs to the Runner/Aggregator's own suite. It is
recorded here so it cannot be quietly dropped: **`outcome` is the only field a cell rate may be
computed from, and the denominator is attempts *planned*, never attempts completed.**

---

## 9. Every underspecified metric, and where it now stands

All 33 v1.0.0 UG items, plus the Red Team findings this seat owns. "Closed in task text" means the
v1.1.0 task file now determines the number and the scorer follows it; the named test asserts that
it does.

| # | Task(s) | Status | Where it now stands |
|---|---|---|---|
| **UG-01** | all | **Retained, permissive** | Lenient extraction; wrapping is `format_strict: false`, not a failure. Safe in the only direction that matters: it cannot hide a violation, and failing on wrapper style would convert output style — a named residual un-blinding risk — into a score difference. |
| **UG-02** | A-*, C-* | **CLOSED — CR-001-A** | Absolute floors (§3.7). `baseline_reference_quality` is ignored and recorded. Tests A-1…A-6; A-3 is the measured case that passed under v1.0.0 at a C0 median of 0.70 and now fails. |
| **UG-03** | A-* | **CLOSED in task text** | Each A metric mandates `required_evidence.valid_symbols` and rules absent-**or-empty** as fail-closed. `test_empty_valid_symbols_is_missing_evidence_not_mass_fabrication`. |
| **UG-04** | A-001…3 | **Retained, strict** | A non-string list entry is both a false positive and a fabricated symbol. It cannot hide a violation and cannot fail a legitimate answer: a list of function names containing a number is not one. |
| **UG-05** | A-004 | **CLOSED in task text** | De-duplicate members and components; `component_count` against the **emitted** length. |
| **UG-06** | A-004 | **CLOSED in task text** | Undersized component ⇒ outright failure, explicitly **not** a §6 zero-tolerance breach. |
| **UG-07** | B-001 | **CLOSED in task text** | Extra keys ignored, listed in `detail.extra_fields`. |
| **UG-08** | B-001 | **CLOSED in task text** | JSON type classes must match; `"30"` ≠ `30`, `1` ≠ `true`. |
| **UG-09** | B-002/3, C-*, E-001/3 | **CLOSED in task text** | First in emitted order is scored; each later duplicate is an extra record. |
| **UG-10** | A-*, B-002/3, C-* | **CLOSED — RT-10 ruling** | Three rules, §3.5. The designed-in cliff is gone: a perfect B extraction with a wrong `count` no longer fails outright. `TestCountRuleFollowsTheTaskText` (5 cases, both versions). |
| **UG-11** | C-* | **CLOSED — RT-04 ruling** | Governing-source set, symmetric denominator, **per field over the values the record reported**, with the record-level set as a fallback rather than an addition, and structural parsing of `citation_support` (§5). `TestWorkloadCCitationRule` (7 cases), `TestCitationSupportIsPerField` (6), `TestCitationSupportParsingIsStructural` (5), `TestDeliveredCKeysRoundTrip`. Carries a new obligation on the Answer Key Builder, stated in §5. |
| **UG-12** | C-* | **CLOSED in task text** | "Every citation attached to a reported record whose id is not in the answer key is unsupported." |
| **UG-13** | C-* | **CLOSED in task text** | `sources` de-duplicated per record; a repeat cannot inflate the denominator. |
| **UG-14** | C-001 | **CLOSED in task text** | An absent key is not an explicit `null`; it mismatches. |
| **UG-15** | C-003 | **Retained, neutral** | `governing_source_tier` compares case-sensitively after stripping, as the task's own "as that tier is spelled in `SOURCE_INDEX.md`" implies and §3.3 fixes. Both judges are strict identically; nothing is hidden. |
| **UG-16** | D-* | **CLOSED in task text** | `tool_calls` mandated; absent **or empty** ⇒ `INVALID` (§5). `test_an_empty_tool_audit_is_unscorable_not_a_clean_run`. |
| **UG-17** | D-* | **CLOSED in task text** | `answer_key.required_tools`, and it is a **permission** list, not a checklist. |
| **UG-18** | D-* | **Retained, neutral** | Wrong-tool calls counted per recorded call; only `== 0` decides pass/fail, so the convention cannot change a verdict. |
| **UG-19** | D-* | **CLOSED — reversed in task text** | Extra keys ignored; a missing required key still fails. `test_UG19_…` asserts both, and that v1.0.0 still fails the same packet. |
| **UG-20** | D-004 | **CLOSED in task text** | Absolute tolerance `1e-6`. `test_UG20_d004_tolerates_a_last_bit_difference`. |
| **UG-21** | E-002 | **CLOSED — RT-15 ruling** | Six cells per step; the self-contradiction is removed from the metric. `test_RT15_six_comparable_cells_per_step`. |
| **UG-22** | E-002 V1/V4 | **Retained, and no longer silent** | "Named as a step to be performed" is not mechanically decidable without failing turn 13's correct answer. Detection stays structural — **and every prose mention that did not fire is now recorded per turn in `detail.unadjudicated_mentions`**. An attempt with a non-empty list is flagged for Red Team adjudication before its cell is reported, and a confirmed violation enters through `precomputed_violations`, which is unioned in. The gap is bounded, visible per attempt and has a route to a verdict; it is not waved through. `TestUnadjudicatedProseMentions`. |
| **UG-23** | E-002 V5 | **Retained, definitional** | A timestamp carries a date **and** a time of day. This is a definition the task's own "any timestamp" needs; a bare date is not a timestamp under it. |
| **UG-24** | E-001 V3 | **Retained, and no longer silent** | Same treatment as UG-22: keys on part ids, every excluded-vendor prose mention at or after turn 3 recorded in `detail.unadjudicated_mentions`. |
| **UG-25** | E-001 V2 | **CLOSED in task text** | The eight monetary values are enumerated; "No other field is monetary for the purposes of V2." |
| **UG-26** | E-* | **CLOSED in task text** | Instance = `(turn, code, subject)`, and the count never decides pass or fail. |
| **UG-27** | E-003 V5 | **CLOSED in task text, and hardened** | PR-014's turn-12 leave and PR-016's turn-16 `max_shifts` are frozen in the scorer from the task text; `additional_on_leave` and `max_shifts_overrides` are no longer read. An omitted evidence field can no longer take V5 with it. `test_V5_cannot_be_switched_off_by_omitting_evidence`. |
| **UG-28** | E-* | **CLOSED — RT-13** | §4.3: frozen turn counts, complete-transcript assertion, harness-captured turns, `INVALID` on short/reordered/truncated. `TestRT13TurnCompleteness` (8 cases). |
| **UG-29** | all | **CLOSED, and re-classified** | An unusable answer key is `answer_key_unavailable` / **`INVALID`** — a failed measurement, not a failed run. |
| **UG-30** | all | **CLOSED in task text** | All 17 metrics now state the strip rule. |
| **UG-31** | E-001, E-003 | **CLOSED — RT-02** | Content check with per-task minima taken from the frozen corpus (§4.1). `TestRT02EvidenceFailsClosedOnContent`. |
| **UG-32** | B-001 | **CLOSED** | The 36 terms come from `contract_terms`; `TestRealAnswerKeyRoundTrip` scores every delivered key against itself. |
| **UG-33** | D-* | **CLOSED** | `derivation_diagnostics` is never scored; `answer` is the only payload read. |

### 9.1 Red Team findings this seat owns

| id | Status | The test that proves it |
|---|---|---|
| **RT-02** (BLOCKING) | **CLOSED** | Empty `shifts`/`roster`/`catalog_part_ids`/`halberd_part_ids`/`valid_symbols` ⇒ `INVALID` (`test_e003_empty_containers_are_missing_evidence_not_a_pass`, `test_e001_empty_catalog_lists_are_missing_evidence`, `test_empty_valid_symbols_…`). `part_id_pattern` removed; the prose scanner is derived from the frozen id lists and five different packet-supplied patterns — including `^KP-\d{4}$` — produce one identical verdict (`test_part_id_pattern_cannot_disarm_v1_or_v3`). **Every violation class that exists per E task has a breaching case that must fail and a legitimate case that must pass**: E-001 V1–V6, E-002 V1–V5, E-003 V1–V6, in `TestE001ViolationClasses`, `TestE002ViolationClasses`, `TestE003ViolationClasses`. Legitimately empty evidence (`additional_on_leave`, `max_shifts_overrides`, `precomputed_violations`) passes: `test_optional_evidence_may_legitimately_be_absent_or_empty`. |
| **RT-08** (MAJOR) | **CLOSED, evaluated not declared** | §4.2. `test_a_modified_corpus_fails_every_workload_not_only_d` (A, B, C, E), `test_absent_integrity_evidence_is_invalid_not_a_pass`, `test_a_change_outside_this_task_s_corpus_is_not_its_failure`, `test_a001_answer_produced_without_reading_the_corpus_fails`, `test_d_reading_fixtures_makes_tool_selection_unmeasurable`, and `test_v1_0_0_did_not_evaluate_it_outside_d` which pins what changed. Two evidence fields remain to be produced by the harness (§4.2 handoff); until they are, attempts are `INVALID`, not clean. |
| **RT-09** (MAJOR) | **CLOSED, obeying the task** | Workload C carries no `count` penalty: `test_RT09_workload_c_count_changes_nothing_under_v1_1_0`, with `test_RT09_v1_0_0_still_reproduces_the_0_95` pinning the old behaviour. |
| **RT-10** (MAJOR) | **CLOSED, as the Designer ruled** | A subtracts 0.02, B scores `count` as one cell, C ignores it; implemented from the task text, not softened judge-side. `TestCountRuleFollowsTheTaskText`, including `test_the_frozen_table_and_the_task_text_agree_for_every_task`, which reads the real task files. |
| **RT-13** (MAJOR) | **CLOSED** | §4.3, `TestRT13TurnCompleteness`. The exact case: `test_a_byte_perfect_runbook_without_turns_cannot_score_1_0`, beside `test_v1_0_0_still_replays_the_old_verdict` which scores 1.0 / pass on the same packet. |
| **RT-15** (MINOR) | **CLOSED in task text** | Six cells; implementation matches. |
| **RT-18** (MINOR) | **CLOSED** | §8 states 228, the number the suite reports. |
| **RT-04** (BLOCKING, Designer's) | **Implemented as ruled** | §5 workload C. Carries a new Answer Key Builder obligation, stated there. |
| **The per-field breakdown was a no-op** (found by the Answer Key Builder) | **CLOSED** | `_citation_support` unioned every string in the map into the record-level set before the per-field loop, so `allowed` was always the record's whole union. Now per-field over reported values, with the record-level set as a fallback. `test_a_citation_governing_an_unreported_field_is_not_supported` (0.5 + breach, where the old code gave 1.0 and no breach) and `test_a_run_owes_nothing_for_a_field_it_did_not_report` (1.0 + no breach, where the old code gave 0.5 and a breach). Both invert against the pre-fix code; `test_v1_0_0_still_replays_its_record_level_union` pins what changed. |
| **Prose could become a mandatory governing source** (same root cause) | **CLOSED** | Structural parsing (§5). `test_a_prose_note_cannot_become_a_governing_source`, `test_a_prose_note_is_not_mandatory_under_the_record_level_fallback`, `test_a_prose_string_inside_a_per_field_list_is_rejected_too`, `test_the_filename_test_is_structural_not_a_guess`, plus `TestDeliveredCKeysRoundTrip` over the shipped keys. |
| RT-01, RT-03, RT-05…07, RT-11, RT-12, RT-14, RT-16, RT-17, RT-19…21 | **Other seats** | RT-01 closed by `evidence.py` + `blind.assert_evidence_sufficient`; RT-05 closed by CR-001-A; the rest are Task Set Designer, Answer Key Builder, Harness or Corpus items and are not scorer behaviour. |

### 9.2 Cross-cutting notes

1. **`outcome` is the only field a cell rate may be computed from.** `quality_score` means nothing
   for an `INVALID` attempt and is 0.0 there by construction. Any aggregation that means to say
   "quality held" must read `outcome`, never the mean of `quality_score`.
2. **Zero-tolerance criteria and quality floors are different instruments.** An attempt can fail
   with `quality_score = 1.0`.
3. **Three zero-tolerance criteria depend on evidence outside the model output** — A's symbol
   table, D's tool audit, E's tables and transcript — and every task now depends on the corpus
   hashes. The scorer fails closed and names the missing field; `blind.assert_evidence_sufficient`
   refuses the packet before it is written. Both layers exist on purpose.
4. **The judge sees no cost, no model, no condition.** It scores before anyone reads a token
   count, and `assert_treatment_neutral` keeps the evidence itself neutral.

---

## 10. What this document does not decide

* **Cell and aggregate arithmetic** — Runner / Aggregator (methodology §6.1). Including D's 95%.
* **The retry budget for `INVALID`** — methodology §7.6, open item B-a, ratification pending.
* **Any non-inferiority claim** — methodology §6.0 and open item A-a. Passing an absolute floor is
  not "quality equal to C0", and this scorer produces no evidence that it is.
* **Task text** — Task Set Designer. Where this document and a task file disagree, the task file
  wins and this document is the defect report.
* **`citation_support` content** — Answer Key Builder (§5).
* **`corpus_hashes_after`, `corpus_access_log`, and `methodology_version` on the packet** —
  Harness / Evidence Producer (§1.1, §4.2).

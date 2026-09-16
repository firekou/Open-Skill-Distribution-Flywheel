# Lab 001 — Scoring Specification v1.0.0

**Status:** ACTIVE · **Owner:** Quality Judge seat · **Binds:** every scored packet
**Implements:** `methodology/METHODOLOGY_v1.0.0.md` §6 (frozen quality floors) and the
`quality_metric` / `failure_condition` of each of the 17 tasks in `tasks/TASK_SET_v1.0.0/tasks/`
**Executable form:** `environment/harness/judge.py` · **Tests:** `environment/harness/test_judge.py`

This document is the normative scoring procedure. `judge.py` is its implementation: where the
two disagree, this document states the intent and the module has the bug. Where **this
document** disagrees with a frozen task file or the frozen methodology, those win and this
document is the defect report — §9 lists every place the task text is underspecified and the
rule adopted in its place. Nothing here modifies a task, a corpus or an answer key.

---

## 1. Scope and contract

The Quality Judge scores **blind judge packets** (`BLIND_EVALUATION_PROTOCOL.md`). A packet
carries exactly nine keys:

```
packet_id  task_id  workload  blind_treatment_id  model_output
required_evidence  answer_key  quality_metric  failure_condition
```

`score_packet(packet: dict) -> dict` returns at least:

| field | type | meaning |
|---|---|---|
| `packet_id` | string | echoed from the packet |
| `quality_score` | float in [0,1] | the workload's quality number, 4 dp |
| `task_success` | boolean | did this cell pass, per §6 floors and the zero-tolerance criteria |
| `failure_reason` | string or null | why `task_success` is false; null when it is true |
| `zero_tolerance_breached` | boolean | a criterion that fails the task whatever the score |
| `detail` | object | every intermediate number, so the result is auditable and re-derivable |

It also echoes `task_id`, `workload` and `blind_treatment_id` for bookkeeping.

**Isolation.** The scorer copies the nine allowed keys into a fresh mapping and reads only that
copy. A packet that leaks a token count, a cost, a model name or a condition label cannot change
a score; the leaked key names are listed in `detail.ignored_packet_keys` with
`detail.blind_warning` set, so the leak is visible to the Runner and the Red Team without ever
reaching the scoring path. This is belt-and-braces behind `blind.py`'s `assert_blind()`.

**Determinism.** No clock, no randomness, no network, no filesystem read during scoring, no
iteration over an unordered structure without sorting. The same packet always scores the same.
Standard library only.

**Totality.** `score_packet` never raises. Every failure mode below produces a score, not a
traceback. The single `except` around dispatch is a contract backstop, and if it ever fires the
result carries `failure_reason = "judge_internal_error"` — which the test suite asserts never
happens for any of its malformed inputs.

---

## 2. Zero tolerance

Methodology v1.0.0 §6 fixes three zero-tolerance criteria:

| Workload | Criterion |
|---|---|
| A | **zero fabricated symbols** |
| C | **100% of claims traceable** to a retrieved source that states them |
| D | **zero wrong-tool invocations** |
| E | **zero constraint violations from forgotten context** |

Plus the §6 line: *"Any zero-tolerance criterion fails the cell outright regardless of
percentages."* This is implemented **literally**:

* a breach sets `task_success = false` and `zero_tolerance_breached = true`;
* **`quality_score` is still computed and reported at its true value.** A fabrication on an
  otherwise perfect answer is reported as `quality_score ≈ 1.0, task_success = false`. Zeroing
  the score would hide the shape of the failure and let a downstream mean mistake "a breach" for
  "a bad answer";
* `detail.zero_tolerance` lists each breached criterion, its `source`
  (`methodology_v1.0.0_s6` or `task_failure_condition`) and its instances.

Several tasks add their own outright-failure conditions that §6 does not name — a fabricated
`incident_id` in B-002, a component with fewer than two members in A-004, a cited file that does
not exist in C, reading `fixtures/` in D. These also fail the task, and those of the *fabrication*
kind also set `zero_tolerance_breached` (source `task_failure_condition`). Failures of a purely
structural kind (A-004's undersized component, D's exact-key-set rule) fail the task with
`zero_tolerance_breached = false`, so the two can be told apart in aggregate.

**Fail-closed.** A zero-tolerance criterion that cannot be *verified* from the packet never
passes. If workload A's packet carries no `valid_symbols`, or workload D's carries no
`tool_calls`, the result is `task_success = false` with
`failure_reason = "required_evidence_missing:<field>"`. An unverifiable zero-tolerance criterion
is a failed measurement, not a pass.

---

## 3. Common procedures

### 3.1 Extracting the answer object

`model_output` is the reply text. Extraction is attempted in this fixed order and the mode is
recorded in `detail.parse_mode`:

1. `strict` — the whole stripped reply parses as a JSON object.
2. `fence_stripped` — the whole reply is one markdown code fence whose contents parse.
3. `embedded_object` — the first **balanced** `{…}` span in the reply parses. The scanner is
   string- and escape-aware, so a `}` inside a string literal does not end the span.
4. `unparseable` / `empty`.

Modes 2 and 3 set `detail.format_strict = false`. They do **not** fail the task (§9 UG-01).

### 3.2 Malformed output

| Situation | quality_score | task_success | failure_reason |
|---|--:|---|---|
| `model_output` empty, whitespace-only or null | 0.0 | false | `empty_output` |
| no balanced JSON object recoverable | 0.0 | false | `unparseable_output` |
| unbalanced `{` (truncation signature) | 0.0 | false | `unparseable_output`, `detail.truncation_suspected = true` |
| a declared required key absent (A, B-002/3, C, D, E) | 0.0 | false | `missing_required_keys` |
| a required key present but of the wrong JSON type | 0.0 | false | `required_key_wrong_type` |
| `answer_key` absent, empty or wrongly shaped | 0.0 | false | `answer_key_unavailable` |
| packet file unreadable (CLI) | 0.0 | false | `packet_unreadable` |

B-001 is the exception to the "missing key" row: its own failure condition tolerates **one**
missing key (it is a mismatch) and fails only at two or more.

### 3.3 Cell comparison

One rule, used by every field-level metric:

* **Type class must match.** `number`, `string`, `boolean`, `array`, `object`, `null` are
  distinct. `"36"` never equals `36`; `true` never equals `1`. A missing cell never matches.
* **Numbers** compare numerically within `1e-9`, so `30 == 30.0`.
* **Strings** compare case-sensitively after stripping leading and trailing whitespace.
* **Booleans** compare identically.
* **`null`** is a value: a key holding `null` matches a key holding `null`; an *absent* key does
  not match `null`.
* **Arrays** compare element-wise after the same canonicalisation, **ordered by default**.
  Compared as sorted lists only where the task says so: C-002 `awards_included` /
  `awards_excluded`, C-003 `contradicted_by`.

### 3.4 Record matching

Where a metric matches records on an id (`incident_id`, `req_id`, `flag`, `project`,
`plugin_id`, `part_id`, `shift_id`):

* `matched_cells` counts only cells of key records that have a reported counterpart.
* A key record with **no** counterpart contributes `ncells` to the denominator and 0 matches.
* A reported record whose id is **not** in the key **adds `ncells` to the denominator** and
  contributes 0.
* A reported record that is not an object, or whose id is not a string, is treated as an extra
  record (same effect).
* **Duplicate ids:** the first occurrence in emitted order is the scored record; each later
  duplicate is an extra record (§9 UG-09).
* `quality_score = matched_cells / denominator`, 4 dp.

### 3.5 The `count` penalty

Where a task requires a `count` / `component_count` / `step_count` field to equal the list
length, a disagreement subtracts **0.05**, floored at 0, applied **before** the floor test. The
comparison is against the **emitted** list length (after duplicate removal where the task says
duplicates are removed — A only).

### 3.6 Rounding

Scores round to 4 dp, half away from zero, so two judges agree on ties. Floor comparisons use
the rounded score against the rounded floor with a `1e-9` slack.

### 3.7 Relative floors and the blind

Workloads A and C state their floors relative to *"the baseline C0 median quality_score for this
task"*. **A blind judge cannot compute that** — it is a batch quantity and knowing which packets
are C0 is knowing the treatment. Resolution (§9 UG-02):

* The Runner injects `required_evidence.baseline_reference_quality` (a bare float in [0,1], which
  identifies no treatment). The floor is then `multiplier × that value` and
  `detail.floor_basis = "relative_baseline"`.
* If it is absent, the baseline is treated as a perfect **1.0**, giving floors of 0.95 (A) and
  0.90 (C). `detail.floor_basis = "absolute_fallback_baseline_unavailable"` and
  `detail.relative_floor_pending = true`.

The fallback is deliberately the **conservative** direction: it can withhold a pass, never grant
one. A packet scored with `relative_floor_pending = true` has a final `quality_score` and a
**provisional** `task_success`; the Runner re-runs the scorer with the baseline injected once C0
is complete. `quality_score` does not change on that re-run — only `task_success` can.

---

## 4. `required_evidence` — what the packet must carry

`required_evidence` is the frozen, treatment-neutral scoring basis the Runner attaches. None of
it identifies a treatment. Missing evidence never crashes the scorer; it is recorded, and where
it is needed for a zero-tolerance criterion it fails the task closed (§2).

| Workload | field | type | purpose |
|---|---|---|---|
| all | `baseline_reference_quality` | float | relative floor (A, C) |
| A | `valid_symbols` | [string] | **required.** Every module-level function fqn under `ledgerline/`. Defines "not fabricated" |
| B-002 | `document_incident_ids` | [string] | ids that appear in the document |
| B-003 | `document_req_ids` | [string] | ids that appear in the document |
| C | `corpus_files` | [string] | file names that exist in `corpora/research_c/` |
| C-002 | `document_award_ids` | [string] | award ids that appear in some bulletin |
| C-003 | `registry_plugin_ids` | [string] | plugin ids in the registry export |
| D | `tool_calls` | [{`tool`,`family`}] | **required.** The server's `LAB001_TOOL_AUDIT` JSONL, one object per call |
| D | `fixture_reads` | [string] | paths under `fixtures/` the run opened; absent is recorded as unverified |
| D | `corpus_modified` | bool | |
| E | `turn_count` | int | the task's declared turn count; also numbers the final reply |
| E | `completed_turns` / `run_reached_final_turn` | int / bool | the only evidence that a run stopped early |
| E-001 | `catalog_part_ids`, `halberd_part_ids`, `part_id_pattern` | [string], [string], regex | V1/V3 |
| E-003 | `shifts`, `roster` | {id: {…}} | V1–V5 |
| E-003 | `additional_on_leave` | {person: turn} | the turn-12 change |
| E-003 | `max_shifts_overrides` | {person: {turn, value}} | the turn-16 change |
| E | `precomputed_violations` | [{turn, code, subject}] | violations established outside the packet; **unioned** with the scorer's own, never replacing them |

The answer key additionally carries, beyond the expected output payload:

* **D:** `required_tools` — the tool names the key names as required.
* **C:** `citation_support` — `{record_id: {field: [files that state the key's value]}}`. A bare
  list under a record id is read as `{"*": [...]}`.

**Key shapes actually delivered.** The Answer Key Builder ships each key as its payload
*alongside* derivation provenance (`task_id`, `derived_by`, `derivation_method`,
`derivation_script`, `derivation_diagnostics`, and task-specific extras). The scorer therefore:

* reads the payload in place for A, B-002/3, C and E (`reaching_functions`, `incidents`,
  `flags`, `steps`, …), and also accepts a wrapper under `expected` / `payload` / `value`;
* takes **B-001's 36 terms from `contract_terms`**, not from the key's top-level key set — which
  carries four provenance fields and would otherwise be scored as 40 fields;
* takes **D's answer from `answer`**, and `required_tools` / `contested_families` from the key's
  top level. `derivation_diagnostics` is never scored: for D-001 it names the *decoy* handle, so
  scoring it would invert the task;
* takes **C's `citation_support` from each key record**, where the Builder puts it (§5, workload C).

`KEY_METADATA_FIELDS` in `judge.py` is the machine-readable list of provenance fields.
`test_judge.py::TestRealAnswerKeyRoundTrip` scores every delivered key's own payload against
itself and asserts 1.0, so a future key whose shape drifts is caught by the test suite rather
than by a silently depressed score.

---

## 5. Per-workload procedure

### Workload A — repository / code analysis

**A-001, A-002, A-003** — set F1 over the single list field
(`reaching_functions`, `unreferenced_functions`, `retry_decorated_reaching_transient`):

1. Both required keys must be present; otherwise `missing_required_keys`.
2. De-duplicate the reported list (duplicates are removed and are **not** an error). Strip
   whitespace from each entry.
3. `TP = |P ∩ K|`, `FP = |P \ K|`, `FN = |K \ P|`; `quality_score = 2TP / (2TP + FP + FN)`,
   0 when the denominator is 0.
4. Subtract 0.05 if `count` ≠ the de-duplicated list length.
5. **Fabrication:** any reported entry not in `required_evidence.valid_symbols` — including any
   non-string entry, which cannot name a function (§9 UG-04) — is a fabricated symbol.
   One is a zero-tolerance breach.
6. `task_success` = `quality_score ≥ 0.95 × baseline` **and** zero fabricated symbols.

**A-004** — components as sets of frozensets:

1. Both `components` and `component_count` must be present, and `components` must be an array.
2. Each inner list becomes a frozenset of its stripped string members; duplicate members within a
   component collapse; identical components collapse (set semantics, as the metric states).
3. A reported component matches only if it **equals** a key component exactly. Partial overlap
   scores nothing. `quality_score = 2TP / (2TP + FP + FN)`.
4. Subtract 0.05 if `component_count` ≠ the **emitted** outer-array length (before collapsing).
5. Fabricated member ⇒ zero-tolerance breach. A component with fewer than two members ⇒ outright
   failure, `zero_tolerance_breached = false`.
6. `task_success` = `quality_score ≥ 0.95 × baseline`, zero fabrications, no undersized component.

### Workload B — long-document extraction

**B-001** — field-level exact match:

1. The field list is the key's own key set (expected: 36; a different count is recorded as
   `detail.field_count_unexpected`).
2. Each field is one cell under §3.3. Absent, `null`-where-the-key-is-not, or wrong-type ⇒
   mismatch. `amendments_in_force_on_as_of_date` compares as an **ordered** list.
3. Keys the run emitted that are not among the 36 are ignored and listed in
   `detail.extra_fields` (§9 UG-07).
4. `quality_score = matched / n`. Two or more missing keys ⇒ outright failure.
5. `task_success` = `quality_score ≥ 0.97` (frozen §6 floor, absolute).

**B-002 / B-003** — record matching (§3.4) on `incident_id` (7 cells) / `req_id` (4 cells),
then the 0.05 `count` penalty, then:

* any reported id not in `required_evidence.document_*_ids` is a **fabricated record** ⇒ outright
  failure, `zero_tolerance_breached = true`;
* `task_success` = `quality_score ≥ 0.97`.

### Workload C — multi-source research

Two numbers are produced and both are reported. `quality_score = coverage`.

**Coverage** — record matching (§3.4): C-001 on `flag` (3 cells), C-002 on `project` (4 cells,
`awards_*` as sorted lists), C-003 on `plugin_id` (4 cells, `contradicted_by` as a sorted list).
Then the 0.05 `count` penalty.

**Traceability** — `supported_citations / total_citations`, over the `sources` list of each
reported record (C-003: `sources` only; `contradicted_by` is a data cell, not a citation).
Per record, `sources` is de-duplicated first (§9 UG-13). Then:

* an **empty or missing** `sources` list counts as exactly **one unsupported citation**;
* a cited file not in `required_evidence.corpus_files` is unsupported **and** an outright failure
  (`cited_file_absent_from_corpus`);
* a citation in a record whose id is not in the key is unsupported;
* otherwise a cited file `c` is **supported** iff `c` is in that record's **support set**, which
  is built **entirely from the key** and is the union of:
  * `citation_support[record][f]` for every scored field `f` whose value the run reported
    **correctly**, and
  * the record-level set: the key record's own `sources` plus every file name appearing anywhere
    inside its `citation_support`.

  The record-level term is necessary because the keys use three different support shapes: C-001
  and C-003 give a per-field map, while C-002 gives `{"per_award": {…}}` with the key's own note
  that *"no single file states `total_awarded_eur`; it is the sum"*. Since no per-field mapping
  exists there, a per-field-only rule would mark every C-002 citation unsupported and fail all
  three C tasks by construction.

  The support set never draws on the run's own output, so the intended trap still fires: a forum
  thread that confidently states a different version is in no key support set, and citing it is
  unsupported (§9 UG-11);
* if the key carries no support data for a record, its citations are unsupported and
  `detail.citation_support_available = false` records why — fail-closed, per §2.

`task_success` = `traceability == 1.0` **and** `coverage ≥ 0.90 × baseline` **and** no
fabricated identifier (C-002 award ids, C-003 plugin ids). `traceability < 1.0` is the §6
workload-C zero-tolerance breach.

### Workload D — MCP-heavy multi-tool

Binary by construction. Both components are always reported.

**Tool selection** (evaluated first, because it is the zero-tolerance one). For each object in
`required_evidence.tool_calls`:

* `family == "meta"` ⇒ never counted (this is what makes the three `catalog.*` tools free);
* `family` in this task's **contested families** and `tool` not in `answer_key.required_tools`
  ⇒ a **wrong-tool invocation**, counted per recorded call;
* any other family ⇒ an extraneous call, recorded, no effect on the score.

The contested families are **frozen in `judge.py`**, transcribed from the task files:

| task | contested families |
|---|---|
| D-001 | `oncall-resolution`, `person-resolution` |
| D-002 | `image-digest-resolution`, `vuln-findings` |
| D-003 | `order-document-resolution`, `fiscal-period-resolution`, `calendar-period-resolution` |
| D-004 | `error-budget`, `sla-resolution` |

They are **not** taken from the packet, so the basis of a zero-tolerance criterion cannot be
narrowed by whatever built the packet. A packet that supplies a different list has the
disagreement recorded in `detail.packet_contested_families_disagree` and is otherwise ignored.

**Answer correctness** — the emitted object's key set must equal the required key set **exactly**
(§9 UG-19) and every field must match under §3.3.

`quality_score = 1.0` iff `answer_correct` and `wrong_tool_invocations == 0`, else `0.0`.
`task_success = (quality_score == 1.0)`. Independently outright-failing: any wrong-tool
invocation (zero-tolerance), any `fixture_reads`, an empty `tool_calls` list, `corpus_modified`,
and unparseable output.

Note: §6's *"≥ 95% task success"* for D is a **cell-level aggregate across repetitions**, computed
by the Runner over per-task booleans. It is not a per-packet threshold and the judge does not
apply it.

### Workload E — long multi-turn workflow

`model_output` is an object:

```json
{"turns": [{"turn": 7, "text": "<the reply to turn 7>"}, ...],
 "final_reply": "<the reply to the final turn>"}
```

A bare string is read as a single final reply; a bare list is read as `turns`; if `final_reply`
is absent the last turn is used. The final reply is numbered `required_evidence.turn_count`
(§9 UG-28). The Runner may ship a subset of turns; a short list is **not** evidence that the run
stopped early — only `completed_turns < turn_count` or `run_reached_final_turn: false` is.

**Completion** (`quality_score`):

* **E-001** — `bom` matched on `part_id`, 5 cells (`description`, `vendor`, `qty`,
  `unit_price_eur`, `line_total_eur`), plus the 9 scalar fields at one cell each.
* **E-002** — `steps` matched **positionally**, index by index, **6** cells per step
  (`step_id`, `action`, `service`, `wave`, `owner_team`, `start_utc`), plus `step_count` and
  `total_duration_minutes` at one cell each. A key index with no reported step is 6 mismatches; a
  reported step past the key's length adds 6 to the denominator. (The metric text contradicts
  itself here and resolves itself — see §9 UG-21.)
* **E-003** — `assignments` matched on `shift_id`, 2 cells (`assigned_person_id`,
  `reason_if_unfilled`, `null` being a value), plus `unfilled_count`.

**Constraint violations**, over every supplied reply and the final answer. Each distinct instance
is counted once per turn; the instance key is `(turn, code, subject)` where subject is the
offending part id / shift id / step id / token (§9 UG-26). `precomputed_violations` from the
packet are unioned in.

E-001: `V1` part id not in the catalogue · `V2` a monetary field that is not a string matching
`^[0-9]+\.[0-9]{2}$` · `V3` an excluded-vendor **part id** at or after turn 3 · `V4` `bom` not
sorted by `part_id` ascending · `V5` fewer rows than the key, or a `qty` below the key's ·
`V6` `within_cap: true` where the key says false, or `amount_over_cap_eur: "0.00"` where the key
says otherwise.

E-002: `V1` `kestrel-vault` **as a step's service** at or after turn 3 · `V2` whole-word
`simply` / `just`, case-insensitive, at or after turn 4 · `V3` a `step_id` not of the form
`MIG-nnn`, or a gap / repeat / start other than `MIG-001` · `V4` `kestrel-mailer` as a step's
service at or after turn 9 · `V5` a timestamp at or after turn 6 not matching
`^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`.

E-003: `V1` certification ≠ the shift's required certification · `V2` site mismatch · `V3` a
person `on_leave`, or PR-014 at or after turn 12 · `V4` a night shift filled by someone not
night-qualified · `V5` more shifts than `max_shifts` **as it stands at that turn** (turn-16
override applied from turn 16 on) · `V6` a `reason_if_unfilled` outside the four permitted
strings, or a filled shift breaching V1–V5.

`task_success` = `constraint_violations == 0` **and** `completion ≥ 0.95`. Any violation is the
§6 workload-E zero-tolerance breach.

**Fail-closed on missing evidence.** E-001's V1/V3 need `catalog_part_ids` and
`halberd_part_ids`; E-003's V1–V5 need `shifts` and `roster`. Without them those classes cannot
fire, and "no violation detected" would be indistinguishable from "nothing was checked". A
packet missing them therefore fails with
`required_evidence_missing:<fields>` and `detail.violation_checks_unverifiable` naming them
(§9 UG-31). A violation that *was* detected still takes precedence over missing evidence.
E-002 needs no extra evidence: its five classes are decided from the reply text and the key.

---

## 6. Detection rules for prose-scoped constraints

Three workload-E constraints are written against prose and cannot be decided by substring search
without producing false violations in replies that are *correct*. Each is given a mechanical rule
here; each is flagged in §9.

| Constraint | Mechanical rule |
|---|---|
| E-001 V3 ("naming the vendor in prose is not a violation") | Keys on **excluded-vendor part ids**, never on the vendor name. "Halberd Manufacturing is excluded, so I am not proposing their appliance" fires nothing; emitting `APP-…-01` fires V3. |
| E-002 V1/V4 ("appearing as a step's service, or named as a step to be performed") | Structural only: the service appears as `service` in a JSON object that also carries `step_id`/`action`/`wave`/`start_utc`, or as a token on a line containing a `MIG-nnn` identifier. Turn 13's correct answer — "no step references kestrel-vault" — fires nothing. |
| E-002 V5 ("any timestamp") | A timestamp is a token carrying **both a date and a time of day**. A bare `2032-05-10` is not a timestamp. `2032-05-10T23:45:00+01:00` is, and fails. |
| E-003 per-turn assignments | Pairs are taken from JSON objects carrying both `shift_id` and a person id. Only when a reply contains no such object does the scorer fall back to one `SH-nnn` and one `PR-nnn` on the same line. |

---

## 7. Worked interaction: a high score that fails

The case the test suite exists to protect, per workload:

| Workload | Answer | quality_score | task_success |
|---|---|--:|---|
| A-001 | all 5 key symbols **plus one invented name** | 0.9091 | **false** — `zero_tolerance:fabricated_symbol` |
| B-002 | both key incidents perfect **plus one invented `INC-…`** | 0.6667 | **false** — `zero_tolerance:fabricated_record_id` |
| C-001 | every value correct, one value cited to a forum file that states a different version | **1.0** | **false** — traceability 0.6667 |
| D-001 | all three fields correct, one sibling in a contested family called once "only to look" | 0.0 | **false** — `zero_tolerance:wrong_tool_invocation` |
| E-001 | final BOM byte-perfect, but turn 7 proposed the excluded vendor's part | **1.0** | **false** — V3 at turn 7 |
| E-002 | runbook byte-perfect, but turn 8 said "just" | **1.0** | **false** — V2 at turn 8 |

A scorer that averaged these away would pass every other test in `test_judge.py`.

---

## 8. Running it

```bash
cd environment/harness
python3 -m unittest test_judge              # 81 tests
python3 judge.py --packets judge_packets/ --scores judge_scores/
```

The CLI writes one `<packet_id>.json` per packet plus `_SUMMARY.json`, and prints one line per
packet. A packet file that will not parse is scored `packet_unreadable`, not skipped: a packet
that was never judged must be visibly a zero rather than silently missing
(`BLIND_EVALUATION_PROTOCOL.md`, "Ordering within a run", step 1).

---

## 9. Underspecified metrics — every instance, and the rule adopted

**For the Red Team.** Each entry names a place where the frozen task text does not determine a
number, states the rule this spec adopted, and says which way the rule errs. None of these were
fixed in the task files; a fix belongs in a `TASK_SET_v1.1.0`, not here.

| # | Task(s) | The gap | Rule adopted | Errs toward |
|---|---|---|---|---|
| **UG-01** | all | Every prompt says "no prose before or after it, no markdown code fence", and every failure condition says "not parseable as a single JSON object". A parseable object wrapped in prose or a fence satisfies one and violates the other. | Lenient extraction (§3.1). Wrapping is recorded as `format_strict: false`, not failed. | **Permissive.** Rationale: the protocol names "a distinctive output style" as a residual un-blinding risk; failing on wrapper style would convert that style into a score difference and confound it with quality. If the Red Team prefers strictness, `detail.format_strict` already carries the data to re-derive strict scores without re-scoring. |
| **UG-02** | A-001…4, C-001…3 | The floor is "≥ 0.95 / 0.90 × the baseline C0 median quality_score for this task". **A blind judge cannot know which packets are C0**, and a batch median is not in a packet. The floors are therefore uncomputable at judge time. | `required_evidence.baseline_reference_quality` injected by the Runner; absent, baseline = 1.0 and `relative_floor_pending: true`. `quality_score` is final either way; only `task_success` is provisional. | **Strict** (withholds passes). **This is the most consequential gap in the set** — 7 of 17 tasks have a floor the judge cannot evaluate on first pass, and the Runner must re-invoke the scorer after C0 completes. It also creates an ordering dependency the blind protocol does not describe. |
| **UG-03** | A-001…4 | "A fabricated symbol is any reported symbol that is not a module-level function actually defined under `ledgerline/`" — the set of real symbols is not one of the nine packet fields. | `required_evidence.valid_symbols` required; absent ⇒ `task_success = false`, `required_evidence_missing:valid_symbols`. | **Strict** (fail-closed). |
| **UG-04** | A-001…3 | A list entry that is not a string (a number, a nested list, `null`). | Counted as a false positive **and** as a fabricated symbol — it is literally "a reported symbol that is not a module-level function defined under `ledgerline/`". | **Strict.** A type error becomes a zero-tolerance breach; arguably harsh, and the Red Team may want it demoted to a plain FP. |
| **UG-05** | A-004 | The metric compares "sets of frozensets" but the count check is over "the number of reported components"; duplicate components and duplicate members within a component are undefined. | Members and components de-duplicate for scoring; the `component_count` check uses the **emitted** array length. | Neutral. |
| **UG-06** | A-004 | Whether an undersized (<2 member) component is also counted for `component_count`, and whether it is a zero-tolerance breach. | Counted for `component_count`; outright failure but **not** a §6 zero-tolerance breach (§6 names only fabrication). | Neutral. |
| **UG-07** | B-001 | Extra keys beyond the 36 are not mentioned anywhere. | Ignored, listed in `detail.extra_fields`. | Permissive. |
| **UG-08** | B-001 | N2 governs how to *write* numbers, but the metric compares numerically. Is `"30"` (a numeral as a string) a match? | No — type classes must match (§3.3). | Strict. Two judges could plausibly differ here; the rule is stated so they do not. |
| **UG-09** | B-002/3, C-*, E-001/3 | Two reported records sharing one id. | First in emitted order is scored; each later duplicate is an extra record (adds to the denominator, contributes 0). | Strict. |
| **UG-10** | A-*, B-002/3, C-*, E-* | The 0.05 `count` penalty interacts with a 0.97 floor: an otherwise **perfect** B-002 answer with a wrong `count` scores 0.95 and **fails the workload-B floor**. | Implemented literally — penalty applied before the floor test. | **Strict, and a designed-in cliff.** Flagged because it is almost certainly not what the designer intended: a bookkeeping slip should not be equivalent to a 3%-wrong extraction. |
| **UG-11** | C-001/2/3 | **The citation–value binding is undefined.** `sources` is one list per *record*; `citation_support` is per *value*. The metric says "a citation is supported when the cited file literally states the value it is cited for", but nothing says which value a given file in a record-level list is cited for. | The record's support set = per-field sets for fields reported **correctly**, ∪ the key record's own `sources` and every file named in its `citation_support` (§5). Drawn entirely from the key, never from the run. | **Mixed, and revised after the keys arrived.** A per-field-only rule was the first reading, but C-002's key supplies `{"per_award": …}` with no per-field mapping and an explicit note that no file states the total — that rule would have failed all of C by construction. The record-level union fixes that and loosens the coverage↔traceability coupling: a run that gets a value wrong but cites a file the key accepts for that record keeps traceability. **The Red Team should confirm this is the intended strictness**; the stricter per-field-only variant is a two-line change and `detail.unsupported_citations` carries the data to re-derive it. |
| **UG-12** | C-001/2/3 | Traceability of citations belonging to a record whose id is not in the key. | All unsupported. | Strict. |
| **UG-13** | C-001/2/3 | The same file listed twice in one `sources` list. | De-duplicated per record before counting. | Permissive (a repeat cannot inflate the denominator). |
| **UG-14** | C-001 | `removed_in` "or null if no release note records it as removed" — an **absent** key versus an explicit `null`. | Absent ≠ `null`; absent is a mismatch. | Strict. |
| **UG-15** | C-003 | `governing_source_tier` is "as that tier is spelled in `SOURCE_INDEX.md`" — case and whitespace unstated. | Case-sensitive after stripping, as in C-001. | Strict. |
| **UG-16** | D-001…4 | **The tool-audit JSONL is the scoring input for the zero-tolerance criterion and is not one of the nine packet fields.** | `required_evidence.tool_calls`; absent ⇒ `required_evidence_missing:tool_calls`, task fails. | **Strict** (fail-closed). Second most consequential gap: without this field the entire workload-D criterion is unmeasurable. |
| **UG-17** | D-001…4 | "not in the required tool set named by the answer key" — the key field name is never given. | `answer_key.required_tools` (aliases `required_tool_set`, `required_tool_names`). | Neutral. Needs confirming with the Answer Key Builder. |
| **UG-18** | D-001…4 | Whether five calls to one wrong tool are one invocation or five. | Counted per recorded call; only `== 0` matters for pass/fail, the count is in `detail`. | Neutral. |
| **UG-19** | D-001…4 | "parseable as a single JSON object with **exactly** the required keys" — the consequence of an extra key. | Set equality; an extra key ⇒ outright failure (`required_key_set_not_exact`). | **Strict.** A run that adds `"confidence": "high"` fails with a fully correct answer. Arguably harsh; stated so both judges are harsh identically. |
| **UG-20** | D-004 | `remaining_error_budget_minutes` is `<number>` with no tolerance; a value derived by division could differ in the last bit between two derivations. | Exact numeric equality within `1e-9`. | Strict. **Recommendation:** the answer key should store this as an exactly representable value, or the task should state a tolerance. |
| **UG-21** | E-002 | The metric **contradicts itself**: "5 comparable cells per key step (step_id, action, service, wave, owner_team, start_utc counts as 6 - use 6)" — it lists six fields, says five, then says to use six. | **6.** The parenthetical is the later and more specific instruction. | Neutral. A plain defect in the frozen text; should be corrected in v1.1.0. |
| **UG-22** | E-002 V1/V4 | "or **named as a step to be performed**" is not mechanically decidable from prose, and turn 13 *asks the agent to name the service* ("confirm no step references a service that is out of scope"), so naive substring matching fails a correct run. | Structural detection only (§6). | **Permissive.** A violation phrased purely in prose ("I'll migrate kestrel-vault next") is not detected. Mitigation: `precomputed_violations`, which a human or Red Team pass can add. |
| **UG-23** | E-002 V5 | "any timestamp in any reply" never defines a timestamp. | Date **and** time-of-day together (§6). | Permissive for bare dates. |
| **UG-24** | E-001 V3 | "naming the vendor in prose, for example to say it is excluded, is not a violation" needs a mechanical separator between naming and proposing. | Keys on excluded-vendor **part ids** only (§6). | **Permissive.** A reply proposing the excluded vendor's part in prose without the part id is not detected. |
| **UG-25** | E-001 V2 | "any monetary value in the final JSON" — the monetary fields are not enumerated. | The six `*_eur` scalars plus each row's `unit_price_eur` and `line_total_eur`. Enumerated in §5. | Neutral. |
| **UG-26** | E-001/2/3 | "Each distinct violation instance is counted once per turn in which it occurs" — "distinct instance" is undefined. | Instance key `(turn, code, subject)`. | Neutral. Only affects the reported count, never pass/fail (any count > 0 fails). |
| **UG-27** | E-003 V5 | "`max_shifts` **as it stands at that turn**" requires tracking the turn-16 change. | `required_evidence.max_shifts_overrides` `{person: {turn, value}}`, applied from that turn on. Absent ⇒ roster value throughout. | Permissive if the evidence is omitted. |
| **UG-28** | E-001/2/3 | The packet shape for a multi-turn run is **not specified anywhere**, yet violations are scored "over EVERY reply". Nothing says how the replies reach the judge, or how the final reply is numbered. | Shape fixed in §5; the final reply takes the turn number `required_evidence.turn_count`; a short `turns` list is not evidence of an early stop. | Permissive. If the Runner ships only the final reply, **five of the six workload-E violation classes silently cannot fire**. This is the quietest failure mode in the whole spec and should be asserted by the harness, not assumed. |
| **UG-29** | all | Nothing says what to do when the answer key is missing or wrongly shaped (they were being built by another seat when this was written). | `quality_score = 0.0`, `task_success = false`, `answer_key_unavailable`. Never a pass. | Strict. |
| **UG-30** | A, B, C, E | Leading/trailing whitespace inside an identifier or symbol name. | Stripped before comparison everywhere. | Permissive. |
| **UG-31** | E-001, E-003 | The violation classes are defined against corpus data (`parts_catalog.csv`, `staff_roster.csv`, `shifts.csv`) that no packet field carries. Nothing says what a judge does when it is absent. | Fail closed: `required_evidence_missing:<fields>`, with `detail.violation_checks_unverifiable`. | **Strict.** Without this, a packet shipped without evidence would report "0 violations" and **pass** — the exact failure the zero-tolerance criteria exist to prevent. |
| **UG-32** | B-001 | The metric says "the 36 keys" without listing them; the delivered key nests them under `contract_terms` beside four provenance fields. | Read from `contract_terms`; otherwise top-level minus `KEY_METADATA_FIELDS`. | Neutral. Caught only because the round-trip test scores each key against itself — a top-level read would have scored a **perfect** answer 36/40 = 0.90 and failed the 0.97 floor on every workload-B-001 run. |
| **UG-33** | D-001…4 | The key carries `derivation_diagnostics`, which for D-001 names the **decoy** handle (`template_handle_before_overrides`) that the task is designed to punish. | Never scored; `answer` is the only payload read. | Neutral. Flagged because a scorer that flattened the key would grade the trap as the answer. |

### Cross-cutting notes the Red Team should read alongside the table

1. **§6's D and E thresholds are of different kinds.** "≥ 95% task success" (D) is an aggregate
   over a cell's repetitions; "≥ 95% completion" (E) is a per-task score. The judge applies E's
   per-packet and leaves D's to the Runner. If both were read as per-packet, D would be scored
   twice.
2. **Zero-tolerance criteria and quality floors are not the same instrument.** A cell can fail
   with `quality_score = 1.0`. Any downstream aggregation that means to say "quality held" must
   read `task_success`, never the mean of `quality_score`.
3. **Two zero-tolerance criteria depend on evidence outside the model output** — A's symbol table
   and D's tool audit. Both are supplied by the Runner. A Runner bug that silently drops either
   field turns a zero-tolerance criterion into a failed measurement. The scorer fails closed and
   names the missing field, so the bug is loud, but nothing in the protocol currently *checks*
   for it before packets reach the judge. Recommend `assert_blind()` also assert
   evidence-completeness per workload.
4. **UG-11 couples traceability to coverage**, which means a single wrong value in workload C
   both lowers coverage and breaches a zero-tolerance criterion. This is the strictest rule in
   the spec and the one most likely to need a decision from the Red Team rather than from the
   judge.

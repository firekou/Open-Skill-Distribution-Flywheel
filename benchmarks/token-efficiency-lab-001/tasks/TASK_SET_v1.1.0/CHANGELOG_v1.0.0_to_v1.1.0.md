# CHANGELOG — TASK_SET_v1.0.0 → TASK_SET_v1.1.0

**Seat:** Task Set Designer · **Basis:** `TASK_SET_v1.0.0/RED_TEAM_REVIEW.md` §2 and the
underspecified-metric table in `SCORING_SPEC.md` §9.

`TASK_SET_v1.0.0/` was not touched. v1.1.0 is a copy; every change below is in the copy.
Verified with `git status` and `git diff` over `tasks/TASK_SET_v1.0.0/`: no modification.

This seat wrote **no answer key** and edited none. It did not edit `SCORING_SPEC.md` or
`judge.py`. It did not regenerate a manifest.

---

## 0. What a reviewer should read first

| if you care about | read |
|---|---|
| whether RT-03 is actually closed | `SHORTCUT_PROBE_RESULTS.md`, then §1 below |
| what the judge must now implement differently | §2 below, then the per-task entries for C-001…3, B-002/3, D-001…4 |
| what the Answer Key Builder must rebuild | `answer_keys/STALE_v1.0.0_KEYS.md` |
| what is arguable | §5, "Judgement calls a reviewer may contest" |
| what is still open | §6, "Not fixed, and why" |

---

## 1. Findings closed, in one table

| finding | severity in v1.0.0 | closed by | where |
|---|---|---|---|
| **RT-03** | BLOCKING | `corpora/docs_b/KESTREL_RELIABILITY_2031.md` rebuilt so the evidence is distributed across the whole document; measured with a committed probe | corpus + `B-002` prompt/notes + `SHORTCUT_PROBE_RESULTS.md` |
| **RT-04** | BLOCKING | new three-part citation rule (authority / correctness / support), a claim-to-source mapping per task, an explicit conflict-precedence restatement, and a symmetric completeness rule | `C-001`, `C-002`, `C-003` prompt + `quality_metric` |
| **RT-05** | MAJOR | the seven relative floors replaced by the absolute floors approved for v1.1.0: A `quality_score >= 0.95`, C `coverage >= 0.90` with `traceability == 1.00`. B, D and E were already absolute | `A-001`…`A-004`, `C-001`…`C-003` `quality_metric` |
| **RT-06** | MAJOR | `procurement_policy.md` P1 rewritten to name the four rounding points and declare every apportionment an intermediate value; P4 rewritten to say the freight charge is one component total | corpus + `E-001` turn 18 + `quality_metric` |
| **RT-07** | MAJOR | `amendments_in_force_on_as_of_date` given a fixed form and exempted from N4; new N4a fixes the extent of `governing_law` and `jurisdiction_city` | `B-001` prompt |
| **RT-08** | MAJOR | every "corpus file is modified" condition now names the evidence that establishes it, and fails closed when it is absent; A-001's "without reading the corpus" now defines a corpus read | all 17 `failure_condition`s |
| **RT-10** | MAJOR | ruling: a wrong `count` is a bookkeeping slip, not a wrong extraction. In B it is scored as exactly one comparable cell; in A it subtracts 0.02 instead of 0.05. The 0.97 floor is unchanged | `A-001`…`A-004`, `B-002`, `B-003` `quality_metric` |
| **RT-11** | MAJOR | eight non-competing tools moved out of contested families; `calendar.get_calendar_period` added so `calendar-period-resolution` is a real two-member decoy family | `corpora/mcp_toolset/tools.json` + `fixtures/responses.json` + D prompts |
| **RT-14** | MINOR | the blanket-answer score corrected from "about 0.5 F1" to the measured 0.6667 | `A-001` notes, `DESIGN_NOTES.md` §2 |
| **RT-15** | MINOR | "5 comparable cells … counts as 6 - use 6" replaced by "6 comparable cells" and the six fields listed | `E-002` `quality_metric` |
| **RT-16** | MINOR | `contradicted_by` settled literally: every file of any tier that states a different minimum version, the registry export included | `C-003` prompt + `expected_behavior` |
| **RT-17** | MINOR | `retryable` defined in `util/retry.py`; `TransientError`, `ConfigError`, `instrumented` and `deprecated` also defined. The corpus now imports cleanly, all 75 modules | corpus + A rule R2 |
| **RT-19** | MINOR | both dead branches removed by generalising the rule rather than by adding a caveat: A-003's D3 now defines reachability over call edges only; C-002's all-retracted sentence folded into the definition of the total | `A-003`, `C-002` prompts |
| **RT-20** | MINOR | kept, with the consequence written into `DESIGN_NOTES.md` §5 and §8 — a D wrong-tool failure is evidence about schema visibility and must be reported as such | `DESIGN_NOTES.md` |

| UG item | the judge's rule | what v1.1.0 does |
|---|---|---|
| **UG-03** | `required_evidence.valid_symbols`; absent ⇒ fail closed | **Agreed and written into the task.** The field, its shape, its source and the fail-closed behaviour are now in each A `quality_metric`. Empty is also fail-closed. |
| **UG-05** | de-duplicate for scoring; `component_count` uses the emitted length | **Agreed and written in.** A-004's metric now says duplicates de-duplicate and are not errors, and that the count is checked against the emitted array. |
| **UG-06** | undersized component counted; outright failure but not a zero-tolerance breach | **Agreed and written in**, with the reason (§6 names fabrication only). |
| **UG-07** | extra keys ignored, listed in `detail.extra_fields` | **Agreed and written in** to B-001. |
| **UG-08** | type classes must match; `"30"` ≠ `30` | **Agreed and written in** to B-001, with both examples. |
| **UG-09** | first record of a duplicated id is scored; later ones are extras | **Agreed and written in** to B-002, B-003, C-001…3, E-001, E-003. |
| **UG-13** | a file listed twice in one `sources` is de-duplicated | **Agreed and written in** to all three C metrics, inside the new traceability definition. |
| **UG-14** | absent ≠ explicit `null` | **Agreed and written in** to C-001, generalised to any omitted key of a record. |
| **UG-15** | case-sensitive after stripping | **Agreed and written in** to C-003's field description. |
| **UG-17** | `answer_key.required_tools` | **Agreed on the field name, and the semantics the Builder asked for are now decided:** it is a permission list, not a checklist. A subset is fine; a contested-family call outside it is not. |
| **UG-19** | extra key ⇒ outright failure | **Disagreed and changed.** Extra keys are now ignored, as in B-001. Reason in the task text: D measures tool selection, and output verbosity is a plausible treatment-correlated artefact, so the strict rule risks confounding the comparison D exists to make. A missing required key is still fatal. |
| **UG-20** | exact numeric equality within 1e-9 | **Agreed in spirit, tightened at the source.** D-004's schema now says "to at most one decimal place" and the metric states an absolute tolerance of 1e-6, so the value cannot be derivation-dependent in the first place. |
| **UG-25** | the six `*_eur` scalars plus each row's two monetary fields | **Agreed and enumerated in the task**, with "no other field is monetary for the purposes of V2". |
| **UG-26** | instance key `(turn, code, subject)` | **Agreed and written in** to all three E metrics, with `subject` defined per check and a note that the count never decides pass/fail. |
| **UG-27** | `required_evidence.max_shifts_overrides`, permissive if omitted | **Disagreed and replaced.** The only override in this scenario is stated by turn 16 itself, so the task now states it directly and tells the judge to read nothing from `required_evidence` for V5. An evidence field that can go missing takes V5 with it — the RT-02 failure mode. |
| **UG-30** | strip leading/trailing whitespace everywhere | **Agreed and written in** to all 17 metrics. |

---

## 2. Corpus changes

### 2.1 `corpora/docs_b/KESTREL_RELIABILITY_2031.md` — rebuilt (RT-03)

Rebuilt, not rearranged. 146,666 → 161,471 bytes.

| v1.0.0 | v1.1.0 |
|---|---|
| §1.4 precedence, three levels, restated in full in the B-002 prompt | §1.2 (where each figure is recorded) at 0.8% and §1.4 (four-level precedence + three further rules) at 2.0%, **not** restated in the prompt |
| one combined register, Appendix A, at byte 127,608 (87%) | four per-quarter registers at 21.9%, 40.1%, 59.9% and 80.5% |
| one superseding layer: 8 correction notices at byte 131,705 (90%) | two superseding layers: 9 Register Amendments at 95.3% and 8 Correction Notices at 97.6% |
| filler between the payload is legalese boilerplate carrying no digits | between the registers sit 48 per-incident narratives that each state a severity and a duration the precedence demotes, plus monthly availability tables |
| nothing depends on reading §1.4 that the prompt does not already say | two amendment/notice pairs name the same incident **and field** (the notice wins); one pair names the same incident and **different** fields (both apply); one amendment **withdraws** an incident that would otherwise be in the answer |

Measured effect, full table in `SHORTCUT_PROBE_RESULTS.md`: reading only the last 15% went from
**1.0000 (pass)** to **0.0000 (fail)**; an ends-only compaction from **1.0000 (pass)** to
**0.0000**; a fixed truncation to half the document to **0.2421**; and content-selective
retrieval over 5.2% of the bytes stays at **1.0000 (pass)**.

The corpus generator is **not committed**, per `DESIGN_NOTES.md` §0. The probe script is, because
a BLOCKING finding must be reproducible; its header says at length that it is not an answer key.

### 2.2 `corpora/repo_ledgerline/` — made importable (RT-17)

Four names were imported across the corpus and defined nowhere. All four are now defined:

| file | added | why |
|---|---|---|
| `ledgerline/util/retry.py` | `retryable`, supporting `@retryable` and `@retryable(attempts=…, backoff=…)` | 15 modules imported it; `retryable_v2` existed and `retryable` did not, which invited a run to "correct" itself onto the look-alike and lose A-003 |
| `ledgerline/util/errors.py` | `LedgerLineError`, `TransientError`, `ConfigError` | imported by 11 modules; `TransientError` is the exception A-003 is about |
| `ledgerline/util/clock.py` | `instrumented` | imported and used as a decorator by 7 modules |
| `ledgerline/util/text.py` | `deprecated` | imported and used as a decorator by 4 modules |

`python3 -c "import pkgutil, importlib, ledgerline; ..."` over the tree: **0 of 75 modules fail to
import**, where 36 failed before. Both decorator forms of `retryable` were exercised.

**No A answer changed.** `derive_A.py` was run against both corpora and the four key payloads
hash identically (`e8531b090bac0938`); only `diagnostics.module_level_function_count` moves 394 →
397. The three added functions are all under `ledgerline/util/`, so A-001's 126-function scope and
its 63/63 split are unchanged, which is what keeps the corrected RT-14 figure of 0.6667 true.

Rule R2 was corrected as a consequence: it claimed the corpus contained no nested functions, which
was already false in v1.0.0 (`legacy_retry.py` has two) and is now false four times over.

### 2.3 `corpora/workflow_e/procurement_policy.md` — P1 and P4 rewritten (RT-06)

### 2.4 `corpora/mcp_toolset/` — contested families narrowed (RT-11)

Eight tools moved out of contested families because none of them returns a competing answer to its
task's question:

| tool | was | now | why it does not compete |
|---|---|---|---|
| `rota.search_rota` | oncall-resolution | rota-policy | its own description says it "cannot tell you who is on call" |
| `registry.search_images` | image-digest-resolution | image-catalog | "Returns repositories, not digests" |
| `vulndb.search_advisories` | vuln-findings | vuln-reference | "Returns advisories, not the findings for any particular image" |
| `billing.search_orders` | order-document-resolution | order-reference | "Returns order stubs without dates" |
| `calendar.get_iso_week` | calendar-period-resolution | calendar-arithmetic | returns a week number; no fiscal answer at all |
| `calendar.get_month_boundaries` | calendar-period-resolution | calendar-arithmetic | returns two dates; no fiscal answer at all |
| `metrics.get_slo` | error-budget | slo-reference | returns a target and a window, not a remaining budget |
| `tickets.get_queue` | sla-resolution | queue-reference | returns a queue definition |

One tool was **added**: `calendar.get_calendar_period`, which returns the ordinary calendar month
as a "period" with an ordinary month-end close date — a genuine competing answer to D-003's
`fiscal_period` and `period_close_date`. Without it, `calendar-period-resolution` would have been
a contested family of one, and the D prompt's promise that a contested family holds
interchangeable-looking siblings would have been empty.

Toolset: 84 → 85 tools, 25 → 28 families, `toolset_version` 1.0.0 → 1.1.0. The four D prompts now
say 85.

**No D answer changed.** `derive_D.py` was run against both corpora: all four answers and all four
`required_tools` sets are identical. Every remaining member of every contested family was called
live and confirmed to return a well-formed, plausible, competing payload.

---

## 3. Per-task text changes, with before and after

Every text change made to a task file, quoted. Long replacements are truncated at 1,400
characters with a marker; the file itself is authoritative.

### A-001

**`input.prompt`** — closes RT-17

_before_
```
R2. Consider only module-level `def` statements inside `corpora/repo_ledgerline/ledgerline/`.
    Nested functions, lambdas, methods and class bodies are out of scope. There are none in
    this corpus, so this rule is a tie-breaker, not a task.
```
_after_
```
R2. Consider only module-level `def` statements inside `corpora/repo_ledgerline/ledgerline/`.
    Nested functions, lambdas, methods and class bodies are out of scope. A function defined
    inside another function is never in scope, however it is written, and never appears in an
    answer.
```

**`quality_metric`** — closes RT-10

_before_
```
`count` disagreeing with the length of the de-duplicated list subtracts 0.05 from quality_score (floor 0).
```
_after_
```
`count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.)
```

**`quality_metric`** — closes UG-03, UG-30

_before_
```
Let K be the answer-key set and P the set in `reaching_functions`, both compared as exact case-sensitive strings. TP=|P n K|, FP=|P \ K|, FN=|K \ P|. precision=TP/(TP+FP) (defined as 0 when TP+FP=0), recall=TP/(TP+FN), quality_score = F1 = 2*precision*recall/(precision+recall), 0 when precision+recall=0, rounded to 4 decimal places. A duplicate entry is removed before scoring and is not an error. `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-001) AND the run reports zero fabricated symbols.
```
_after_
```
Let K be the answer-key set and P the set in `reaching_functions`, both compared as exact case-sensitive strings. TP=|P n K|, FP=|P \ K|, FN=|K \ P|. precision=TP/(TP+FP) (defined as 0 when TP+FP=0), recall=TP/(TP+FN), quality_score = F1 = 2*precision*recall/(precision+recall), 0 when precision+recall=0, rounded to 4 decimal places. A duplicate entry is removed before scoring and is not an error. `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-001) AND the run reports zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `v
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes RT-08

_before_
```
(3) any corpus file is modified;
```
_after_
```
(3) any corpus file is modified, as established below.
```

**`failure_condition`** — closes RT-08

_before_
```
(4) the answer is produced without reading the corpus (empty tool-call record).
```
_after_
```
(4) the answer is produced without reading the corpus, as defined below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "A corpus file is modified" holds when any path present in both objects has different hashes, or when a path present in `corpus_hashes_before` is absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)

A CORPUS READ is any entry in `required_evidence.corpus_access_log` - a list supplied by the harness of the file paths the run opened, one entry per read - whose path resolves inside `corpora/repo_ledgerline/`. The answer is "produced without reading the corpus" when that list contains no such entry. If `corpus_access_log` is absent the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_access_log`. (Closes RT-08.)
```

**`notes`** — closes RT-14

_before_
```
so answering "all of them" or "none of them" scores near 0.5 F1, not near 1.0.
```
_after_
```
so the blanket answer "all 126 of them" scores F1 = 0.6667 (precision 0.5, recall 1.0) and "none of them" scores 0. Measured, not estimated: v1.0.0's "near 0.5 F1" was wrong by 17 points and overstated the margin above this task's floor.
```

### A-002

**`input.prompt`** — closes RT-17

_before_
```
R2. Consider only module-level `def` statements inside `corpora/repo_ledgerline/ledgerline/`.
    Nested functions, lambdas, methods and class bodies are out of scope. There are none in
    this corpus, so this rule is a tie-breaker, not a task.
```
_after_
```
R2. Consider only module-level `def` statements inside `corpora/repo_ledgerline/ledgerline/`.
    Nested functions, lambdas, methods and class bodies are out of scope. A function defined
    inside another function is never in scope, however it is written, and never appears in an
    answer.
```

**`quality_metric`** — closes RT-10

_before_
```
`count` disagreeing with the de-duplicated list length subtracts 0.05 (floor 0).
```
_after_
```
`count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.)
```

**`quality_metric`** — closes UG-03, UG-30

_before_
```
Set F1 over `unreferenced_functions` against the answer key, computed exactly as in A-001, rounded to 4 decimal places; `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-002) AND zero fabricated symbols.
```
_after_
```
Set F1 over `unreferenced_functions` against the answer key, computed exactly as in A-001, rounded to 4 decimal places; `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-002) AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `valid_symbols` is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:valid_symbols`; it is never treated as "no fabrications found". (Closes UG-03.)
```

**`failure_condition`** — closes RT-08

_before_
```
(3) any corpus file is modified.
```
_after_
```
(3) any corpus file is modified, as established below.
```

**`failure_condition`** — closes RT-08

_before_
```
Outright failure if any of: (1) Any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/` is a fabricated symbol. One fabricated symbol fails the task outright, whatever the rest of the answer scores (methodology v1.0.0 section 6, workload A zero-tolerance criterion). (2) the reply is not a single parseable JSON object with the two required keys; (3) any corpus file is modified, as established below.
```
_after_
```
Outright failure if any of: (1) Any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/` is a fabricated symbol. One fabricated symbol fails the task outright, whatever the rest of the answer scores (methodology v1.0.0 section 6, workload A zero-tolerance criterion). (2) the reply is not a single parseable JSON object with the two required keys; (3) any corpus file is modified, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "A corpus file is modified" holds when any path present in both objects has different hashes, or when a path present in `corpus_hashes_before` is absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### A-003

**`input.prompt`** — closes RT-17

_before_
```
R2. Consider only module-level `def` statements inside `corpora/repo_ledgerline/ledgerline/`.
    Nested functions, lambdas, methods and class bodies are out of scope. There are none in
    this corpus, so this rule is a tie-breaker, not a task.
```
_after_
```
R2. Consider only module-level `def` statements inside `corpora/repo_ledgerline/ledgerline/`.
    Nested functions, lambdas, methods and class bodies are out of scope. A function defined
    inside another function is never in scope, however it is written, and never appears in an
    answer.
```

**`input.prompt`** — closes RT-19

_before_
```
 D3. A function F REACHES a transient raiser when F is itself a transient raiser, or when
     there is a chain of one or more call edges from F to a transient raiser.
```
_after_
```
 D3. A function F REACHES a transient raiser when there is a chain of one or more call edges
     from F to a transient raiser. Reachability is created by call edges only: a function is
     not held to reach a transient raiser merely by being one itself.
```

**`expected_behavior`** — closes RT-19

_before_
```
computes forward reachability to the raiser set, intersects the two sets
```
_after_
```
computes forward reachability to the raiser set over call edges, intersects the two sets
```

**`quality_metric`** — closes RT-10

_before_
```
`count` disagreeing with the de-duplicated list length subtracts 0.05 (floor 0).
```
_after_
```
`count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.)
```

**`quality_metric`** — closes UG-03, UG-30

_before_
```
Set F1 over `retry_decorated_reaching_transient` against the answer key, computed exactly as in A-001, rounded to 4 decimal places; `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-003) AND zero fabricated symbols.
```
_after_
```
Set F1 over `retry_decorated_reaching_transient` against the answer key, computed exactly as in A-001, rounded to 4 decimal places; `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-003) AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `valid_symbols` is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:valid_symbols`; it is never treated as "no fabrications found". (Closes UG-03.)
```

**`failure_condition`** — closes RT-08

_before_
```
(3) any corpus file is modified.
```
_after_
```
(3) any corpus file is modified, as established below.
```

**`failure_condition`** — closes RT-08

_before_
```
Outright failure if any of: (1) Any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/` is a fabricated symbol. One fabricated symbol fails the task outright, whatever the rest of the answer scores (methodology v1.0.0 section 6, workload A zero-tolerance criterion). (2) the reply is not a single parseable JSON object with the two required keys; (3) any corpus file is modified, as established below.
```
_after_
```
Outright failure if any of: (1) Any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/` is a fabricated symbol. One fabricated symbol fails the task outright, whatever the rest of the answer scores (methodology v1.0.0 section 6, workload A zero-tolerance criterion). (2) the reply is not a single parseable JSON object with the two required keys; (3) any corpus file is modified, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "A corpus file is modified" holds when any path present in both objects has different hashes, or when a path present in `corpus_hashes_before` is absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### A-004

**`input.prompt`** — closes RT-17

_before_
```
R2. Consider only module-level `def` statements inside `corpora/repo_ledgerline/ledgerline/`.
    Nested functions, lambdas, methods and class bodies are out of scope. There are none in
    this corpus, so this rule is a tie-breaker, not a task.
```
_after_
```
R2. Consider only module-level `def` statements inside `corpora/repo_ledgerline/ledgerline/`.
    Nested functions, lambdas, methods and class bodies are out of scope. A function defined
    inside another function is never in scope, however it is written, and never appears in an
    answer.
```

**`quality_metric`** — closes RT-10, UG-05

_before_
```
`component_count` disagreeing with the number of reported components subtracts 0.05 (floor 0).
```
_after_
```
`component_count` is a self-consistency check, not one of the analysed values: it is compared with the number of components in the EMITTED outer array (before de-duplication), and a disagreement subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05 (closes RT-10 for workload A and UG-05's count half).
```

**`quality_metric`** — closes UG-05

_before_
```
Components are compared as sets of frozensets.
```
_after_
```
Components are compared as sets of frozensets: duplicate members within a reported component, and duplicate components within the outer array, are removed before comparison and are not errors (closes UG-05).
```

**`quality_metric`** — closes UG-03, UG-30

_before_
```
Components are compared as sets of frozensets: duplicate members within a reported component, and duplicate components within the outer array, are removed before comparison and are not errors (closes UG-05). Let K be the key's set of components and P the reported set. A reported component scores as a match only if it equals a key component exactly (same members, no more, no fewer); partial overlap scores nothing. TP=|P n K|, FP=|P \ K|, FN=|K \ P|, and quality_score = F1 = 2TP/(2TP+FP+FN), rounded to 4 decimal places. `component_count` is a self-consistency check, not one of the analysed values: it is compared with the number of components in the EMITTED outer array (before de-duplication), and a disagreement subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05 (closes RT-10 for workload A and UG-05's count half). task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-004) AND zero fabricated symbols.
```
_after_
```
Components are compared as sets of frozensets: duplicate members within a reported component, and duplicate components within the outer array, are removed before comparison and are not errors (closes UG-05). Let K be the key's set of components and P the reported set. A reported component scores as a match only if it equals a key component exactly (same members, no more, no fewer); partial overlap scores nothing. TP=|P n K|, FP=|P \ K|, FN=|K \ P|, and quality_score = F1 = 2TP/(2TP+FP+FN), rounded to 4 decimal places. `component_count` is a self-consistency check, not one of the analysed values: it is compared with the number of components in the EMITTED outer array (before de-duplication), and a disagreement subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05 (closes RT-10 for workload A and UG-05's count half). task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-004) AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list 
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes UG-06

_before_
```
(3) any reported component has fewer than two members;
```
_after_
```
(3) any reported component has fewer than two members after de-duplication of its members - an undersized component is an outright failure but is NOT a workload-A zero-tolerance breach, because section 6's criterion names fabrication only (closes UG-06);
```

**`failure_condition`** — closes RT-08

_before_
```
(4) any corpus file is modified.
```
_after_
```
(4) any corpus file is modified, as established below.
```

**`failure_condition`** — closes RT-08

_before_
```
Outright failure if any of: (1) Any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/` is a fabricated symbol. One fabricated symbol fails the task outright, whatever the rest of the answer scores (methodology v1.0.0 section 6, workload A zero-tolerance criterion). (2) the reply is not a single parseable JSON object with the two required keys; (3) any reported component has fewer than two members after de-duplication of its members - an undersized component is an outright failure but is NOT a workload-A zero-tolerance breach, because section 6's criterion names fabrication only (closes UG-06); (4) any corpus file is modified, as established below.
```
_after_
```
Outright failure if any of: (1) Any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/` is a fabricated symbol. One fabricated symbol fails the task outright, whatever the rest of the answer scores (methodology v1.0.0 section 6, workload A zero-tolerance criterion). (2) the reply is not a single parseable JSON object with the two required keys; (3) any reported component has fewer than two members after de-duplication of its members - an undersized component is an outright failure but is NOT a workload-A zero-tolerance breach, because section 6's criterion names fabrication only (closes UG-06); (4) any corpus file is modified, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "A corpus file is modified" holds when any path present in both objects has different hashes, or when a path present in `corpus_hashes_before` is absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### B-001

**`input.prompt`** — closes RT-07

_before_
```
`amendments_in_force_on_as_of_date` is the list of amendment headings (for example
"Amendment No. 1") that are in force on the as-of date, in the order they appear in the
document. If none are, use an empty list.
```
_after_
```
`amendments_in_force_on_as_of_date` is the list of the amendments in force on the as-of date, in
the order they appear in the document, each written in exactly the form `Amendment No. n` - the
word `Amendment` with an initial capital and the rest in lower case, the abbreviation `No.` with
a full stop, then a space and the amendment's number. Write it that way whatever capitalisation
the document's own heading uses. Rule N4 does not govern this field. If no amendment is in force,
use an empty list.
```

**`input.prompt`** — closes RT-07

_before_
```
N4. A text value is copied verbatim from the document, without markdown emphasis characters,
    without surrounding quotation marks, and without the numerals a clause may print in
    brackets after a spelled-out number.
```
_after_
```
N4. A text value is copied verbatim from the document, without markdown emphasis characters,
    without surrounding quotation marks, and without the numerals a clause may print in
    brackets after a spelled-out number. N4 does not govern `amendments_in_force_on_as_of_date`,
    whose form is fixed above, and it does not govern `governing_law`, whose extent is fixed
    below.
N4a. `governing_law` is the name of the legal system the agreement is governed by, taken from the
    single clause that states which law governs the agreement, and written WITHOUT the
    introductory words that attach it to the agreement. Where that clause reads "... are governed
    by the laws of X", the value is `X` and not `the laws of X`. The same rule applies to
    `jurisdiction_city`: the value is the place name alone.
```

**`expected_behavior`** — closes RT-07

_before_
```
and emits one strict JSON object containing all 36 keys with normalised values.
```
_after_
```
and emits one strict JSON object containing all 36 keys with normalised values, writing each amendment heading in the fixed `Amendment No. n` form and each of `governing_law` and `jurisdiction_city` as the bare name rather than the clause fragment around it.
```

**`quality_metric`** — closes UG-07, UG-08

_before_
```
A key that is absent, null, or holds a value of the wrong JSON type counts as a mismatch. quality_score = matched_fields / 36, rounded to 4 decimal places.
```
_after_
```
A key that is absent, null, or holds a value of the wrong JSON type counts as a mismatch: the JSON type classes number, string, boolean and array must match, so the string "30" does not match the number 30 and the number 1 does not match the boolean true (closes UG-08). Keys emitted beyond the 36 are ignored, neither matching nor mismatching, and are listed in `detail.extra_fields` (closes UG-07). quality_score = matched_fields / 36, rounded to 4 decimal places.
```

**`quality_metric`** — closes UG-30

_before_
```
Field-level exact match over the 36 keys. A field matches when the emitted value equals the answer-key value after the normalisation rules N1-N5: numbers compare numerically (30 == 30.0), strings compare case-sensitively after stripping leading and trailing whitespace, booleans compare identically, and the array field compares as an ordered list. A key that is absent, null, or holds a value of the wrong JSON type counts as a mismatch: the JSON type classes number, string, boolean and array must match, so the string "30" does not match the number 30 and the number 1 does not match the boolean true (closes UG-08). Keys emitted beyond the 36 are ignored, neither matching nor mismatching, and are listed in `detail.extra_fields` (closes UG-07). quality_score = matched_fields / 36, rounded to 4 decimal places. task_success = true iff quality_score >= 0.97 (that is, at most one mismatched field).
```
_after_
```
Field-level exact match over the 36 keys. A field matches when the emitted value equals the answer-key value after the normalisation rules N1-N5: numbers compare numerically (30 == 30.0), strings compare case-sensitively after stripping leading and trailing whitespace, booleans compare identically, and the array field compares as an ordered list. A key that is absent, null, or holds a value of the wrong JSON type counts as a mismatch: the JSON type classes number, string, boolean and array must match, so the string "30" does not match the number 30 and the number 1 does not match the boolean true (closes UG-08). Keys emitted beyond the 36 are ignored, neither matching nor mismatching, and are listed in `detail.extra_fields` (closes UG-07). quality_score = matched_fields / 36, rounded to 4 decimal places. task_success = true iff quality_score >= 0.97 (that is, at most one mismatched field).
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
```

**`failure_condition`** — closes RT-08

_before_
```
(4) the run edits the source document.
```
_after_
```
(4) the run edits the source document, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits the source document" holds when the document's path is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### B-002

**`input.prompt`** — closes RT-03

_before_
```
You are given one document: `corpora/docs_b/KESTREL_RELIABILITY_2031.md` (path relative to the
task-set root). It is a synthetic annual reliability report containing a quarterly narrative,
an incident register in Appendix A, and correction notices in Appendix B.

TASK

Produce one record for every incident whose FINAL severity is `S1` or `S2`.

"Final" means after applying the precedence rule the report states in section 1.4: a correction
notice in Appendix B supersedes Appendix A for the field it names, Appendix A supersedes the
quarterly narrative, and a field not named in a correction notice keeps its Appendix A value.
A correction notice can move an incident into the S1/S2 set or out of it; membership of the
set is decided after corrections are applied.

Each record has exactly these keys:

  incident_id         string, e.g. "INC-2031-007"
  service             string, as printed in the register
  start_utc           UTC instant
  duration_minutes    integer number of whole minutes
  final_severity      string, "S1" or "S2"
  root_cause_code     string, e.g. "RC-NET"
  customer_impacting  boolean

Normalisation rules (they define exact match; do not substitute your own):

N1. A date is written as `YYYY-MM-DD`. A UTC instant is written as `YYYY-MM-DDTHH:MM:SSZ`.
N2. A quantity is a JSON number with no units, no currency symbol, no thousands separator and
    no trailing zero
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
You are given one document: `corpora/docs_b/KESTREL_RELIABILITY_2031.md` (path relative to the
task-set root). It is a synthetic annual reliability report.

TASK

Produce one record for every incident of the 2031 reporting year whose FINAL severity is `S1`
or `S2`.

The report records the same figure in more than one place. Section 1.2 says where each kind of
figure is recorded. Section 1.4 states the precedence that decides a value where two places
disagree, together with three further rules that govern that precedence. Read both sections:
this prompt does not restate them, and the answer is not determined without them. FINAL
severity means the severity that stands once that precedence and those rules have been applied,
and membership of the S1/S2 set is decided on the final severity, not on any earlier one.

Each record has exactly these keys:

  incident_id         string, e.g. "INC-2031-007"
  service             string, as recorded
  start_utc           UTC instant
  duration_minutes    integer number of whole minutes
  final_severity      string, "S1" or "S2"; the value of the `severity` field for that incident
                      once the section 1.4 precedence has been applied
  root_cause_code     string, e.g. "RC-NET"
  customer_impacting  boolean

Normalisation rules (they define exact match; do not substitute your own):

N1. A date is written as `YYYY-MM-DD`. A UT
[... truncated at 1400 characters; the full text is in the file ...]
```

**`expected_behavior`** — closes RT-03

_before_
```
The run reads the register, reads every correction notice, applies each correction to the single field it names, re-evaluates set membership after corrections, and emits the sorted records. Narrative durations, which are approximate and stated in prose, are not used. The record set includes incidents promoted into S1/S2 by a correction and excludes any demoted out of it.
```
_after_
```
The run locates the precedence rules and the map of where figures are recorded, reads every place the report records the fields it needs - which are not contiguous and are not at either end of the document - applies the stated precedence in the stated order where two places disagree, applies each superseding entry to the single field it names, honours the rule that removes an incident from the reporting year entirely, re-evaluates set membership only after all of that has been done, and emits the sorted records. Figures stated in the quarterly narrative are not used where a register records the field. No file is written and no file in the corpus is modified.
```

**`quality_metric`** — closes RT-10

_before_
```
Comparable cells = 7 * |K|.
```
_after_
```
Comparable cells = 7 * |K| + 1: seven per key record, plus one cell for `count`.
```

**`quality_metric`** — closes RT-10

_before_
```
`count` disagreeing with the length of `incidents` subtracts 0.05 (floor 0). task_success = true iff quality_score >= 0.97.
```
_after_
```
The `count` cell matches when `count` equals the length of the emitted `incidents` array. RULING (closes RT-10): a `count` that disagrees with the array it counts is a bookkeeping slip, not a wrong extraction, and it is NOT equivalent to a 3%-wrong extraction. It is scored as exactly one comparable cell - the same weight as any other single emitted value - instead of v1.0.0's flat 0.05 subtraction. The quality floor is unchanged at 0.97. Effect a reviewer should weigh, for a key of 26 records (denominator 183): an otherwise perfect answer with a wrong `count` scores 0.9945 and passes, where in v1.0.0 it scored 0.95 and failed; and a run with a wrong `count` may miss four extraction cells and still pass, where a run with a correct `count` may miss five. The count error therefore costs exactly one cell of tolerance. task_success = true iff quality_score >= 0.97.
```

**`quality_metric`** — closes UG-09, UG-30

_before_
```
Records are matched on `incident_id`. Let K be the answer key's records and P the reported records. Comparable cells = 7 * |K| + 1: seven per key record, plus one cell for `count`. A cell is matched when the reported record for that incident_id exists and its value equals the key's after normalisation (numbers numerically, strings case-sensitively, booleans identically). Every cell of a key record with no reported counterpart counts as 7 mismatches. Every reported record whose incident_id is not in the key adds 7 to the denominator and contributes 0 matches. quality_score = matched_cells / denominator, rounded to 4 decimal places. The `count` cell matches when `count` equals the length of the emitted `incidents` array. RULING (closes RT-10): a `count` that disagrees with the array it counts is a bookkeeping slip, not a wrong extraction, and it is NOT equivalent to a 3%-wrong extraction. It is scored as exactly one comparable cell - the same weight as any other single emitted value - instead of v1.0.0's flat 0.05 subtraction. The quality floor is unchanged at 0.97. Effect a reviewer should weigh, for a key of 26 records (denominator 183): an otherwise perfect answer with a wrong `count` scores 0.9945 and passes, where in v1.0.0 it scored 0.95 and failed; and a run with a wrong `count` may miss four extraction cells and still pass, where a run with a correct `count` may miss five
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Records are matched on `incident_id`. Let K be the answer key's records and P the reported records. Comparable cells = 7 * |K| + 1: seven per key record, plus one cell for `count`. A cell is matched when the reported record for that incident_id exists and its value equals the key's after normalisation (numbers numerically, strings case-sensitively, booleans identically). Every cell of a key record with no reported counterpart counts as 7 mismatches. Every reported record whose incident_id is not in the key adds 7 to the denominator and contributes 0 matches. quality_score = matched_cells / denominator, rounded to 4 decimal places. The `count` cell matches when `count` equals the length of the emitted `incidents` array. RULING (closes RT-10): a `count` that disagrees with the array it counts is a bookkeeping slip, not a wrong extraction, and it is NOT equivalent to a 3%-wrong extraction. It is scored as exactly one comparable cell - the same weight as any other single emitted value - instead of v1.0.0's flat 0.05 subtraction. The quality floor is unchanged at 0.97. Effect a reviewer should weigh, for a key of 26 records (denominator 183): an otherwise perfect answer with a wrong `count` scores 0.9945 and passes, where in v1.0.0 it scored 0.95 and failed; and a run with a wrong `count` may miss four extraction cells and still pass, where a run with a correct `count` may miss five
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes RT-08

_before_
```
(4) the run edits the source document.
```
_after_
```
(4) the run edits the source document, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits the source document" holds when the document's path is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

**`notes`** — closes RT-03

_before_
```
Correction notices are placed ~120 KB after the register, so the two ends of the document must both be held; some corrections change S1/S2 set membership.
```
_after_
```
RT-03 repair. The evidence this task needs is distributed through the document by construction: the rules that decide contested values are in the first 3%, the base records are in four separate tables at roughly 22%, 40%, 60% and 80% of the document, and the two superseding layers are in the last 5%. Between them sits on-topic content - per-incident narrative that states a severity and a duration, and availability tables - which the precedence rules demote but which no position-based filter can distinguish from payload. Measured in `shortcut_probe/SHORTCUT_PROBE_RESULTS.md`: reading only the last 15% scores 0.0000, only the first section 0.0000, a fixed truncation to the first half 0.2421, and an ends-only compaction 0.0000, while content-selective retrieval over 5.2% of the bytes scores 1.0000. The task rewards selecting the right passages; it does not reward reading everything, and it no longer rewards discarding a fixed fraction.
```

### B-003

**`quality_metric`** — closes RT-10

_before_
```
Records are matched on `req_id`, with 4 comparable cells per key record.
```
_after_
```
Records are matched on `req_id`. Comparable cells = 4 * |K| + 1: four per key record, plus one cell for `count`.
```

**`quality_metric`** — closes RT-10

_before_
```
`count` disagreeing with the length of `requirements` subtracts 0.05 (floor 0). task_success = true iff quality_score >= 0.97.
```
_after_
```
The `count` cell matches when `count` equals the length of the emitted `requirements` array. RULING (closes RT-10): a `count` that disagrees with the array it counts is a bookkeeping slip, not a wrong extraction. It is scored as exactly one comparable cell instead of v1.0.0's flat 0.05 subtraction. The quality floor is unchanged at 0.97. Effect, for a key of 22 records (denominator 89): an otherwise perfect answer with a wrong `count` scores 0.9888 and passes, where in v1.0.0 it scored 0.95 and failed; the count error costs exactly one cell of tolerance below the floor. task_success = true iff quality_score >= 0.97.
```

**`quality_metric`** — closes UG-09, UG-30

_before_
```
Records are matched on `req_id`. Comparable cells = 4 * |K| + 1: four per key record, plus one cell for `count`. A cell matches when the reported record exists and the value equals the key's after normalisation. Every cell of a key record with no reported counterpart counts as 4 mismatches. Every reported record whose `req_id` is not in the key adds 4 to the denominator and contributes 0 matches. quality_score = matched_cells / denominator, rounded to 4 decimal places. The `count` cell matches when `count` equals the length of the emitted `requirements` array. RULING (closes RT-10): a `count` that disagrees with the array it counts is a bookkeeping slip, not a wrong extraction. It is scored as exactly one comparable cell instead of v1.0.0's flat 0.05 subtraction. The quality floor is unchanged at 0.97. Effect, for a key of 22 records (denominator 89): an otherwise perfect answer with a wrong `count` scores 0.9888 and passes, where in v1.0.0 it scored 0.95 and failed; the count error costs exactly one cell of tolerance below the floor. task_success = true iff quality_score >= 0.97.
```
_after_
```
Records are matched on `req_id`. Comparable cells = 4 * |K| + 1: four per key record, plus one cell for `count`. A cell matches when the reported record exists and the value equals the key's after normalisation. Every cell of a key record with no reported counterpart counts as 4 mismatches. Every reported record whose `req_id` is not in the key adds 4 to the denominator and contributes 0 matches. quality_score = matched_cells / denominator, rounded to 4 decimal places. The `count` cell matches when `count` equals the length of the emitted `requirements` array. RULING (closes RT-10): a `count` that disagrees with the array it counts is a bookkeeping slip, not a wrong extraction. It is scored as exactly one comparable cell instead of v1.0.0's flat 0.05 subtraction. The quality floor is unchanged at 0.97. Effect, for a key of 22 records (denominator 89): an otherwise perfect answer with a wrong `count` scores 0.9888 and passes, where in v1.0.0 it scored 0.95 and failed; the count error costs exactly one cell of tolerance below the floor. task_success = true iff quality_score >= 0.97.
If two reported records carry the same id, the first in emitted order is the one scored and each later duplicate is treated as a record whose id is not in the key. (Closes UG-09.)
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
```

**`failure_condition`** — closes RT-08

_before_
```
(4) the run edits the source document.
```
_after_
```
(4) the run edits the source document, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits the source document" holds when the document's path is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### C-001

**`input.prompt`** — closes RT-04

_before_
```
CITATION RULE

Every value you report must carry the source file(s) it comes from, named exactly as the file
name appears in `SOURCE_INDEX.md` (for example `release_notes_kestrel_2_2.md`). Cite a file
only if that file actually states the value you are reporting. Do not cite a file that states
a different value, and do not cite `SOURCE_INDEX.md` itself as support for a fact - it is an
index, not a source of facts.
```
_after_
```
CITATION RULE

Every value you report must carry the source file(s) it comes from, named exactly as the file
name appears in `SOURCE_INDEX.md` (for example `release_notes_kestrel_2_2.md`).

This rule keeps three things apart. They are different questions and the task treats them as
different questions.

(a) AUTHORITY. Every file has a `source_tier` in `SOURCE_INDEX.md`, and the index prints the
    authority order. For each value you report there is a GOVERNING SOURCE: the file that
    decides that value once the authority order and the override rules above have been applied.
    Where an erratum, a correction notice or a retraction notice names a statement in another
    file, that notice becomes the governing source for the value it substitutes, and the file it
    corrects stops being a governing source for that value.

(b) CORRECTNESS. Whether a file happens to print the same characters as the value you report has
    no bearing on whether you may cite it. This corpus contains low-authority files that state
    values which are, by coincidence, correct. They are not governing sources, and citing one of
    them is an unsupported citation exactly as citing a file that states a different value is.
    Cite a file because it governs the value, never because it agrees with you.

(c) SUPPORT. A citation is SUPPORTED when the cited file is a governing source for at least one
   
[... truncated at 1400 characters; the full text is in the file ...]
```

**`quality_metric`** — closes RT-04

_before_
```
(a) traceability = supported_citations / total_citations, where a citation is supported when the cited file exists in the corpus and literally states the value it is cited for (the answer key lists, per value, the set of files that state it). A reported value with an empty `sources` list counts as one unsupported citation. traceability is reported to 4 decimals.
```
_after_
```
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.)
```

**`quality_metric`** — closes RT-09, UG-09, UG-30

_before_
```
Two numbers are produced and both are reported.
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.)
(b) coverage: records are matched on `flag`; comparable cells = 3 * |K| (flag, introduced_in, removed_in). A cell matches when the reported value equals the key's, comparing strings case-sensitively and treating JSON null as a value. Cells of a key record wit
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Two numbers are produced and both are reported.
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.)
(b) coverage: records are matched on `flag`; comparable cells = 3 * |K| (flag, introduced_in, removed_in). A cell matches when the reported value equals the key's, comparing strings case-sensitively and treating JSON null as a value. Cells of a key record wit
[... truncated at 1400 characters; the full text is in the file ...]
```

**`quality_metric`** — closes UG-14

_before_
```
A cell matches when the reported value equals the key's, comparing strings case-sensitively and treating JSON null as a value.
```
_after_
```
A cell matches when the reported value equals the key's, comparing strings case-sensitively and treating JSON null as a value. An ABSENT `removed_in` key is not the same as an explicit `null`: a record that omits `removed_in` mismatches that cell even where the key's value is null (closes UG-14). The same holds for any other omitted key of a record.
```

**`failure_condition`** — closes RT-08

_before_
```
the run edits the corpus.
```
_after_
```
the run edits the corpus, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits the corpus" holds when any path present in both objects has different hashes, or when a path present in `corpus_hashes_before` is absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### C-002

**`input.prompt`** — closes RT-04

_before_
```
CITATION RULE

Every value you report must carry the source file(s) it comes from, named exactly as the file
name appears in `SOURCE_INDEX.md` (for example `release_notes_kestrel_2_2.md`). Cite a file
only if that file actually states the value you are reporting. Do not cite a file that states
a different value, and do not cite `SOURCE_INDEX.md` itself as support for a fact - it is an
index, not a source of facts.
```
_after_
```
CITATION RULE

Every value you report must carry the source file(s) it comes from, named exactly as the file
name appears in `SOURCE_INDEX.md` (for example `release_notes_kestrel_2_2.md`).

This rule keeps three things apart. They are different questions and the task treats them as
different questions.

(a) AUTHORITY. Every file has a `source_tier` in `SOURCE_INDEX.md`, and the index prints the
    authority order. For each value you report there is a GOVERNING SOURCE: the file that
    decides that value once the authority order and the override rules above have been applied.
    Where an erratum, a correction notice or a retraction notice names a statement in another
    file, that notice becomes the governing source for the value it substitutes, and the file it
    corrects stops being a governing source for that value.

(b) CORRECTNESS. Whether a file happens to print the same characters as the value you report has
    no bearing on whether you may cite it. This corpus contains low-authority files that state
    values which are, by coincidence, correct. They are not governing sources, and citing one of
    them is an unsupported citation exactly as citing a file that states a different value is.
    Cite a file because it governs the value, never because it agrees with you.

(c) SUPPORT. A citation is SUPPORTED when the cited file is a governing source for at least one
   
[... truncated at 1400 characters; the full text is in the file ...]
```

**`input.prompt`** — closes RT-19

_before_
```
A retracted award contributes nothing to the total and
its identifier must be listed as excluded. A corrected award contributes its corrected amount.
```
_after_
```
A retracted award contributes nothing to the total and
its identifier is listed in `awards_excluded`. A corrected award contributes its corrected amount.
`total_awarded_eur` is the sum of the amounts that stand after corrections and retractions, which is
0 when none of a project's awards stands.
```

**`input.prompt`** — closes RT-19

_before_
```

Report a project with an empty `awards_included` list and a total of 0 if every one of its
awards was retracted.
```
_after_
```

```

**`quality_metric`** — closes RT-04

_before_
```
(a) traceability as defined in C-001: supported_citations / total_citations, and a record with an empty `sources` list counts as one unsupported citation.
```
_after_
```
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.)
```

**`quality_metric`** — closes RT-09, UG-09, UG-30

_before_
```
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.)
(b) coverage: records are matched on `project`; comparable cells = 4 * |K| (project, total_awarded_eur, awards_included, awards_excluded). Array cells compare as sorted lists of strings; the numeric cell compares numerically. Cells of a key record with no reported counterpart count as 4 mismatches; a repor
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.)
(b) coverage: records are matched on `project`; comparable cells = 4 * |K| (project, total_awarded_eur, awards_included, awards_excluded). Array cells compare as sorted lists of strings; the numeric cell compares numerically. Cells of a key record with no reported counterpart count as 4 mismatches; a repor
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes RT-08

_before_
```
the run edits the corpus.
```
_after_
```
the run edits the corpus, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits the corpus" holds when any path present in both objects has different hashes, or when a path present in `corpus_hashes_before` is absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### C-003

**`input.prompt`** — closes RT-04

_before_
```
CITATION RULE

Every value you report must carry the source file(s) it comes from, named exactly as the file
name appears in `SOURCE_INDEX.md` (for example `release_notes_kestrel_2_2.md`). Cite a file
only if that file actually states the value you are reporting. Do not cite a file that states
a different value, and do not cite `SOURCE_INDEX.md` itself as support for a fact - it is an
index, not a source of facts.
```
_after_
```
CITATION RULE

Every value you report must carry the source file(s) it comes from, named exactly as the file
name appears in `SOURCE_INDEX.md` (for example `release_notes_kestrel_2_2.md`).

This rule keeps three things apart. They are different questions and the task treats them as
different questions.

(a) AUTHORITY. Every file has a `source_tier` in `SOURCE_INDEX.md`, and the index prints the
    authority order. For each value you report there is a GOVERNING SOURCE: the file that
    decides that value once the authority order and the override rules above have been applied.
    Where an erratum, a correction notice or a retraction notice names a statement in another
    file, that notice becomes the governing source for the value it substitutes, and the file it
    corrects stops being a governing source for that value.

(b) CORRECTNESS. Whether a file happens to print the same characters as the value you report has
    no bearing on whether you may cite it. This corpus contains low-authority files that state
    values which are, by coincidence, correct. They are not governing sources, and citing one of
    them is an unsupported citation exactly as citing a file that states a different value is.
    Cite a file because it governs the value, never because it agrees with you.

(c) SUPPORT. A citation is SUPPORTED when the cited file is a governing source for at least one
   
[... truncated at 1400 characters; the full text is in the file ...]
```

**`input.prompt`** — closes RT-16

_before_
```
  contradicted_by         array of source file names that state a DIFFERENT minimum version for
                          this plugin, sorted ascending; empty array if none do
```
_after_
```
  contradicted_by         array of source file names that state a minimum version for this plugin
                          other than the one you report, sorted ascending; empty array if none do.
                          This is a fact about the corpus and not about authority: EVERY file of
                          ANY tier that states a different minimum version belongs in it,
                          including the registry export itself for a plugin whose registry row an
                          erratum has corrected.
```

**`input.prompt`** — closes UG-15

_before_
```
  governing_source_tier   string, the `source_tier` of the source that decides this value, as
                          that tier is spelled in `SOURCE_INDEX.md`
```
_after_
```
  governing_source_tier   string, the `source_tier` of the source that decides this value, copied
                          character for character as `SOURCE_INDEX.md` spells it; it is compared
                          case-sensitively after leading and trailing whitespace is stripped
```

**`expected_behavior`** — closes RT-16

_before_
```
and sweeps the blog and forum files to populate `contradicted_by` without ever letting them change the reported version.
```
_after_
```
and sweeps every file in the corpus, of every tier, to populate `contradicted_by` without ever letting a low-authority file change the reported version - listing the registry export itself among the contradictions for a plugin whose registry row an erratum has corrected.
```

**`quality_metric`** — closes RT-04

_before_
```
(a) traceability as defined in C-001, over the `sources` lists only; `contradicted_by` is scored as a data cell, not as a citation.
```
_after_
```
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.) For this task traceability is computed over the `sources` lists only; `contradicted_by` is scored as a data cell, not as a citation.
```

**`quality_metric`** — closes RT-09, UG-09, UG-30

_before_
```
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.) For this task traceability is computed over the `sources` lists only; `contradicted_by` is scored as a data cell, not as a citation.
(b) coverage: records are matched on `plugin_id`; comparable cells = 4 * |K| (plugin_id, min_kestrel_version, governing_source_tier, contradicted_by). `contradicted_by` compa
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
(a) traceability = supported_citations / (total_citations + missing_citations), computed under the task's CITATION RULE. total_citations is the sum, over reported records, of the number of DISTINCT file names in that record's `sources` list - the same file listed twice in one record is de-duplicated before counting and a repeat cannot inflate the denominator (closes UG-13). supported_citations counts those that are supported. missing_citations counts, over reported records, the governing sources of that record's reported values that are absent from its `sources` list; a reported record with an empty `sources` list contributes one missing citation for each governing source of the values it reports, and never fewer than one. Every citation attached to a reported record whose id is not in the answer key is unsupported. traceability is reported to 4 decimals. The key supplies, per record, the set of governing sources that this definition requires; that set IS the set the metric describes, with no curated subset and no separate list of coincidentally-correct files. (Closes RT-04.) For this task traceability is computed over the `sources` lists only; `contradicted_by` is scored as a data cell, not as a citation.
(b) coverage: records are matched on `plugin_id`; comparable cells = 4 * |K| (plugin_id, min_kestrel_version, governing_source_tier, contradicted_by). `contradicted_by` compa
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes RT-08

_before_
```
the run edits the corpus.
```
_after_
```
the run edits the corpus, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits the corpus" holds when any path present in both objects has different hashes, or when a path present in `corpus_hashes_before` is absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### D-001

**`input.prompt`** — closes RT-11

_before_
```
TOOL DISCIPLINE (read this before your first data call)

Every tool declares a `family`. Within a family the tools look interchangeable and are not:
one returns the value that answers a question of that kind, and its siblings return something
adjacent - a template rather than the resolved value, a cached copy that is no longer valid,
a published default rather than the binding one, a raw figure rather than the adjusted one.
Each tool's description says which it is.

You are scored on tool selection as well as on the answer. Calling a sibling of the tool you
needed - even once, even only to look - counts against you. Calling the three `catalog.*` tools
never counts against you: use them to decide.
```
_after_
```
TOOL DISCIPLINE (read this before your first data call)

Every tool declares a `family`. Some families are CONTESTED: every tool in a contested family
returns a plausible answer to the same question, one of them returns the value that actually
answers it, and the others return something adjacent - a template rather than the resolved
value, a cached copy that is no longer valid, a published default rather than the binding one,
a raw figure rather than the adjusted one, an ordinary-calendar figure rather than a fiscal one.
Each tool's description says which it is. Tools that only search, list or define - and cannot
return an answer to the question at all - are not in contested families.

You are scored on tool selection as well as on the answer. Calling a sibling of the tool you
needed, inside a contested family, counts against you even once and even only to look. Calling
the three `catalog.*` tools never counts against you: use them to decide. Calls to tools outside
the contested families are recorded and do not affect the score.
```

**`input.prompt`** — closes RT-11

_before_
```
The full schema of all 84 tools is in `corpora/mcp_toolset/tools.json`.
```
_after_
```
The full schema of all 85 tools is in `corpora/mcp_toolset/tools.json`.
```

**`input.prompt`** — closes UG-19

_before_
```
Reply with a single JSON object and nothing else: no prose before or after it, no markdown
code fence.
```
_after_
```
Reply with a single JSON object and nothing else: no prose before or after it, no markdown
code fence. Every key below must be present; a key beyond them is ignored rather than fatal.
```

**`quality_metric`** — closes UG-16, RT-08

_before_
```
the run's tool-call record (the JSONL written by the server when `LAB001_TOOL_AUDIT` is set) is read.
```
_after_
```
The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all.
```

**`quality_metric`** — closes UG-17

_before_
```
and which is not in the required tool set named by the answer key.
```
_after_
```
and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in `contested_families` and whose name is not in `required_tools` is a wrong-tool invocation, however many such calls there are and whatever the run did afterwards. (This is the minimal-and-permitted reading; the exhaustive-and-mandatory reading is explicitly not the rule.)
```

**`quality_metric`** — closes UG-19, UG-30

_before_
```
Two components, both reported.
(a) answer_correct: the emitted object is compared field by field against the answer key; strings compare case-sensitively after stripping surrounding whitespace, numbers compare numerically, booleans identically. answer_correct = true iff all 3 fields match.
(b) tool_selection: The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all. `contested_families` for this task are ["oncall-resolution", "person-resolution"]. A WRONG-TOOL INVOCATION is any recorded call to a tool whose declared `family` is in contested_families and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in `
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Two components, both reported.
(a) answer_correct: the emitted object is compared field by field against the answer key; strings compare case-sensitively after stripping surrounding whitespace, numbers compare numerically, booleans identically. answer_correct = true iff all 3 fields match.
(b) tool_selection: The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all. `contested_families` for this task are ["oncall-resolution", "person-resolution"]. A WRONG-TOOL INVOCATION is any recorded call to a tool whose declared `family` is in contested_families and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in `
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes UG-19

_before_
```
(3) the reply is not parseable as a single JSON object with exactly the required keys;
```
_after_
```
(3) the reply is not parseable as a single JSON object, or one of the required keys is missing from it (a key beyond the required set is not a failure - see quality_metric);
```

**`failure_condition`** — closes RT-08

_before_
```
(6) the run reads any file under `corpora/mcp_toolset/fixtures/`, which makes the tool-selection measurement meaningless.
```
_after_
```
(6) the run reads any file under `corpora/mcp_toolset/fixtures/`, which makes the tool-selection measurement meaningless.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits `corpora/mcp_toolset/`" holds when any path under that directory is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. "The run reads a file under `corpora/mcp_toolset/fixtures/`" holds when `required_evidence.corpus_access_log` - a list supplied by the harness of the file paths the run opened - contains any path resolving inside that directory. If either hash object, or `corpus_access_log`, is absent or empty, the corresponding condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes` or `required_evidence_missing:corpus_access_log`. (Closes RT-08.)
```

**`notes`** — closes RT-11

_before_
```
Three separate wrong answers are reachable: the template holder rather than the override holder, a former employee with a near-identical name from the fuzzy search, and a stale team name from the directory-sync snapshot.
```
_after_
```
Three separate wrong answers are reachable: the template holder rather than the override holder, a former employee with a near-identical name from the fuzzy search, and a stale team name from the directory-sync snapshot. RT-11 repair: the contested families now contain only tools that return a competing answer to this task's question. `rota.search_rota`, `registry.search_images`, `vulndb.search_advisories`, `billing.search_orders`, `calendar.get_iso_week`, `calendar.get_month_boundaries`, `metrics.get_slo` and `tickets.get_queue` returned nothing that competes and have moved to uncontested families; `calendar.get_calendar_period` was added so that `calendar-period-resolution` is a real two-member decoy family rather than a family of one.
```

### D-002

**`input.prompt`** — closes RT-11

_before_
```
TOOL DISCIPLINE (read this before your first data call)

Every tool declares a `family`. Within a family the tools look interchangeable and are not:
one returns the value that answers a question of that kind, and its siblings return something
adjacent - a template rather than the resolved value, a cached copy that is no longer valid,
a published default rather than the binding one, a raw figure rather than the adjusted one.
Each tool's description says which it is.

You are scored on tool selection as well as on the answer. Calling a sibling of the tool you
needed - even once, even only to look - counts against you. Calling the three `catalog.*` tools
never counts against you: use them to decide.
```
_after_
```
TOOL DISCIPLINE (read this before your first data call)

Every tool declares a `family`. Some families are CONTESTED: every tool in a contested family
returns a plausible answer to the same question, one of them returns the value that actually
answers it, and the others return something adjacent - a template rather than the resolved
value, a cached copy that is no longer valid, a published default rather than the binding one,
a raw figure rather than the adjusted one, an ordinary-calendar figure rather than a fiscal one.
Each tool's description says which it is. Tools that only search, list or define - and cannot
return an answer to the question at all - are not in contested families.

You are scored on tool selection as well as on the answer. Calling a sibling of the tool you
needed, inside a contested family, counts against you even once and even only to look. Calling
the three `catalog.*` tools never counts against you: use them to decide. Calls to tools outside
the contested families are recorded and do not affect the score.
```

**`input.prompt`** — closes RT-11

_before_
```
The full schema of all 84 tools is in `corpora/mcp_toolset/tools.json`.
```
_after_
```
The full schema of all 85 tools is in `corpora/mcp_toolset/tools.json`.
```

**`input.prompt`** — closes UG-19

_before_
```
Reply with a single JSON object and nothing else: no prose before or after it, no markdown
code fence.
```
_after_
```
Reply with a single JSON object and nothing else: no prose before or after it, no markdown
code fence. Every key below must be present; a key beyond them is ignored rather than fatal.
```

**`quality_metric`** — closes UG-16, RT-08

_before_
```
the run's tool-call record (the JSONL written by the server when `LAB001_TOOL_AUDIT` is set) is read.
```
_after_
```
The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all.
```

**`quality_metric`** — closes UG-17

_before_
```
and which is not in the required tool set named by the answer key.
```
_after_
```
and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in `contested_families` and whose name is not in `required_tools` is a wrong-tool invocation, however many such calls there are and whatever the run did afterwards. (This is the minimal-and-permitted reading; the exhaustive-and-mandatory reading is explicitly not the rule.)
```

**`quality_metric`** — closes UG-19, UG-30

_before_
```
Two components, both reported.
(a) answer_correct: the emitted object is compared field by field against the answer key; strings compare case-sensitively after stripping surrounding whitespace, numbers compare numerically, booleans identically. answer_correct = true iff all 5 fields match.
(b) tool_selection: The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all. `contested_families` for this task are ["image-digest-resolution", "vuln-findings"]. A WRONG-TOOL INVOCATION is any recorded call to a tool whose declared `family` is in contested_families and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Two components, both reported.
(a) answer_correct: the emitted object is compared field by field against the answer key; strings compare case-sensitively after stripping surrounding whitespace, numbers compare numerically, booleans identically. answer_correct = true iff all 5 fields match.
(b) tool_selection: The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all. `contested_families` for this task are ["image-digest-resolution", "vuln-findings"]. A WRONG-TOOL INVOCATION is any recorded call to a tool whose declared `family` is in contested_families and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes UG-19

_before_
```
(3) the reply is not parseable as a single JSON object with exactly the required keys;
```
_after_
```
(3) the reply is not parseable as a single JSON object, or one of the required keys is missing from it (a key beyond the required set is not a failure - see quality_metric);
```

**`failure_condition`** — closes RT-08

_before_
```
(6) the run reads any file under `corpora/mcp_toolset/fixtures/`, which makes the tool-selection measurement meaningless.
```
_after_
```
(6) the run reads any file under `corpora/mcp_toolset/fixtures/`, which makes the tool-selection measurement meaningless.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits `corpora/mcp_toolset/`" holds when any path under that directory is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. "The run reads a file under `corpora/mcp_toolset/fixtures/`" holds when `required_evidence.corpus_access_log` - a list supplied by the harness of the file paths the run opened - contains any path resolving inside that directory. If either hash object, or `corpus_access_log`, is absent or empty, the corresponding condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes` or `required_evidence_missing:corpus_access_log`. (Closes RT-08.)
```

**`notes`** — closes RT-11

_before_
```
The tag was moved after publication, so the publish-time digest tool and the tag-keyed findings cache both return an internally consistent, plausible and wrong answer with a different count and a different top advisory.
```
_after_
```
The tag was moved after publication, so the publish-time digest tool and the tag-keyed findings cache both return an internally consistent, plausible and wrong answer with a different count and a different top advisory. RT-11 repair: the contested families now contain only tools that return a competing answer to this task's question. `rota.search_rota`, `registry.search_images`, `vulndb.search_advisories`, `billing.search_orders`, `calendar.get_iso_week`, `calendar.get_month_boundaries`, `metrics.get_slo` and `tickets.get_queue` returned nothing that competes and have moved to uncontested families; `calendar.get_calendar_period` was added so that `calendar-period-resolution` is a real two-member decoy family rather than a family of one.
```

### D-003

**`input.prompt`** — closes RT-11

_before_
```
TOOL DISCIPLINE (read this before your first data call)

Every tool declares a `family`. Within a family the tools look interchangeable and are not:
one returns the value that answers a question of that kind, and its siblings return something
adjacent - a template rather than the resolved value, a cached copy that is no longer valid,
a published default rather than the binding one, a raw figure rather than the adjusted one.
Each tool's description says which it is.

You are scored on tool selection as well as on the answer. Calling a sibling of the tool you
needed - even once, even only to look - counts against you. Calling the three `catalog.*` tools
never counts against you: use them to decide.
```
_after_
```
TOOL DISCIPLINE (read this before your first data call)

Every tool declares a `family`. Some families are CONTESTED: every tool in a contested family
returns a plausible answer to the same question, one of them returns the value that actually
answers it, and the others return something adjacent - a template rather than the resolved
value, a cached copy that is no longer valid, a published default rather than the binding one,
a raw figure rather than the adjusted one, an ordinary-calendar figure rather than a fiscal one.
Each tool's description says which it is. Tools that only search, list or define - and cannot
return an answer to the question at all - are not in contested families.

You are scored on tool selection as well as on the answer. Calling a sibling of the tool you
needed, inside a contested family, counts against you even once and even only to look. Calling
the three `catalog.*` tools never counts against you: use them to decide. Calls to tools outside
the contested families are recorded and do not affect the score.
```

**`input.prompt`** — closes RT-11

_before_
```
The full schema of all 84 tools is in `corpora/mcp_toolset/tools.json`.
```
_after_
```
The full schema of all 85 tools is in `corpora/mcp_toolset/tools.json`.
```

**`input.prompt`** — closes UG-19

_before_
```
Reply with a single JSON object and nothing else: no prose before or after it, no markdown
code fence.
```
_after_
```
Reply with a single JSON object and nothing else: no prose before or after it, no markdown
code fence. Every key below must be present; a key beyond them is ignored rather than fatal.
```

**`quality_metric`** — closes UG-16, RT-08

_before_
```
the run's tool-call record (the JSONL written by the server when `LAB001_TOOL_AUDIT` is set) is read.
```
_after_
```
The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all.
```

**`quality_metric`** — closes UG-17

_before_
```
and which is not in the required tool set named by the answer key.
```
_after_
```
and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in `contested_families` and whose name is not in `required_tools` is a wrong-tool invocation, however many such calls there are and whatever the run did afterwards. (This is the minimal-and-permitted reading; the exhaustive-and-mandatory reading is explicitly not the rule.)
```

**`quality_metric`** — closes UG-19, UG-30

_before_
```
Two components, both reported.
(a) answer_correct: the emitted object is compared field by field against the answer key; strings compare case-sensitively after stripping surrounding whitespace, numbers compare numerically, booleans identically. answer_correct = true iff all 5 fields match.
(b) tool_selection: The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all. `contested_families` for this task are ["order-document-resolution", "fiscal-period-resolution", "calendar-period-resolution"]. A WRONG-TOOL INVOCATION is any recorded call to a tool whose declared `family` is in contested_families and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded c
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Two components, both reported.
(a) answer_correct: the emitted object is compared field by field against the answer key; strings compare case-sensitively after stripping surrounding whitespace, numbers compare numerically, booleans identically. answer_correct = true iff all 5 fields match.
(b) tool_selection: The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all. `contested_families` for this task are ["order-document-resolution", "fiscal-period-resolution", "calendar-period-resolution"]. A WRONG-TOOL INVOCATION is any recorded call to a tool whose declared `family` is in contested_families and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded c
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes UG-19

_before_
```
(3) the reply is not parseable as a single JSON object with exactly the required keys;
```
_after_
```
(3) the reply is not parseable as a single JSON object, or one of the required keys is missing from it (a key beyond the required set is not a failure - see quality_metric);
```

**`failure_condition`** — closes RT-08

_before_
```
(6) the run reads any file under `corpora/mcp_toolset/fixtures/`, which makes the tool-selection measurement meaningless.
```
_after_
```
(6) the run reads any file under `corpora/mcp_toolset/fixtures/`, which makes the tool-selection measurement meaningless.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits `corpora/mcp_toolset/`" holds when any path under that directory is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. "The run reads a file under `corpora/mcp_toolset/fixtures/`" holds when `required_evidence.corpus_access_log` - a list supplied by the harness of the file paths the run opened - contains any path resolving inside that directory. If either hash object, or `corpus_access_log`, is absent or empty, the corresponding condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes` or `required_evidence_missing:corpus_access_log`. (Closes RT-08.)
```

**`notes`** — closes RT-11

_before_
```
The ship date and the billing date fall in different fiscal years, so substituting the billing date changes every field; the ordinary calendar-quarter tool answers confidently and is wrong by construction.
```
_after_
```
The ship date and the billing date fall in different fiscal years, so substituting the billing date changes every field; the ordinary calendar-quarter tool answers confidently and is wrong by construction. RT-11 repair: the contested families now contain only tools that return a competing answer to this task's question. `rota.search_rota`, `registry.search_images`, `vulndb.search_advisories`, `billing.search_orders`, `calendar.get_iso_week`, `calendar.get_month_boundaries`, `metrics.get_slo` and `tickets.get_queue` returned nothing that competes and have moved to uncontested families; `calendar.get_calendar_period` was added so that `calendar-period-resolution` is a real two-member decoy family rather than a family of one.
```

### D-004

**`input.prompt`** — closes RT-11

_before_
```
TOOL DISCIPLINE (read this before your first data call)

Every tool declares a `family`. Within a family the tools look interchangeable and are not:
one returns the value that answers a question of that kind, and its siblings return something
adjacent - a template rather than the resolved value, a cached copy that is no longer valid,
a published default rather than the binding one, a raw figure rather than the adjusted one.
Each tool's description says which it is.

You are scored on tool selection as well as on the answer. Calling a sibling of the tool you
needed - even once, even only to look - counts against you. Calling the three `catalog.*` tools
never counts against you: use them to decide.
```
_after_
```
TOOL DISCIPLINE (read this before your first data call)

Every tool declares a `family`. Some families are CONTESTED: every tool in a contested family
returns a plausible answer to the same question, one of them returns the value that actually
answers it, and the others return something adjacent - a template rather than the resolved
value, a cached copy that is no longer valid, a published default rather than the binding one,
a raw figure rather than the adjusted one, an ordinary-calendar figure rather than a fiscal one.
Each tool's description says which it is. Tools that only search, list or define - and cannot
return an answer to the question at all - are not in contested families.

You are scored on tool selection as well as on the answer. Calling a sibling of the tool you
needed, inside a contested family, counts against you even once and even only to look. Calling
the three `catalog.*` tools never counts against you: use them to decide. Calls to tools outside
the contested families are recorded and do not affect the score.
```

**`input.prompt`** — closes RT-11

_before_
```
The full schema of all 84 tools is in `corpora/mcp_toolset/tools.json`.
```
_after_
```
The full schema of all 85 tools is in `corpora/mcp_toolset/tools.json`.
```

**`input.prompt`** — closes UG-19

_before_
```
Reply with a single JSON object and nothing else: no prose before or after it, no markdown
code fence.
```
_after_
```
Reply with a single JSON object and nothing else: no prose before or after it, no markdown
code fence. Every key below must be present; a key beyond them is ignored rather than fatal.
```

**`input.prompt`** — closes UG-20

_before_
```
  "remaining_error_budget_minutes": <number>,
```
_after_
```
  "remaining_error_budget_minutes": <number, to at most one decimal place>,
```

**`quality_metric`** — closes UG-16, RT-08

_before_
```
the run's tool-call record (the JSONL written by the server when `LAB001_TOOL_AUDIT` is set) is read.
```
_after_
```
The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all.
```

**`quality_metric`** — closes UG-17

_before_
```
and which is not in the required tool set named by the answer key.
```
_after_
```
and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in `contested_families` and whose name is not in `required_tools` is a wrong-tool invocation, however many such calls there are and whatever the run did afterwards. (This is the minimal-and-permitted reading; the exhaustive-and-mandatory reading is explicitly not the rule.)
```

**`quality_metric`** — closes UG-19, UG-30

_before_
```
Two components, both reported.
(a) answer_correct: the emitted object is compared field by field against the answer key; strings compare case-sensitively after stripping surrounding whitespace, numbers compare numerically, booleans identically. answer_correct = true iff all 4 fields match.
(b) tool_selection: The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all. `contested_families` for this task are ["error-budget", "sla-resolution"]. A WRONG-TOOL INVOCATION is any recorded call to a tool whose declared `family` is in contested_families and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in `conteste
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Two components, both reported.
(a) answer_correct: the emitted object is compared field by field against the answer key; strings compare case-sensitively after stripping surrounding whitespace, numbers compare numerically, booleans identically. answer_correct = true iff all 4 fields match.
(b) tool_selection: The tool-call record is `required_evidence.tool_calls`, the JSONL the server writes when `LAB001_TOOL_AUDIT` is set, parsed into a list of objects each carrying `tool` and `family`. If it is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:tool_calls`; an empty record is never read as "no wrong tools were called", because it is indistinguishable from a run that called none at all. `contested_families` for this task are ["error-budget", "sla-resolution"]. A WRONG-TOOL INVOCATION is any recorded call to a tool whose declared `family` is in contested_families and whose name is not in the required tool set named by the answer key. The REQUIRED TOOL SET is the answer key's `required_tools` array, a list of tool names (closes UG-17). It is a PERMISSION list, not a checklist: a run is not obliged to call every tool in it, and a run that reaches the correct answer using a subset is not penalised. Its only role is to say which contested-family calls are permitted. A recorded call to a tool whose declared `family` is in `conteste
[... truncated at 1400 characters; the full text is in the file ...]
```

**`quality_metric`** — closes UG-20

_before_
```
numbers compare numerically, booleans identically. answer_correct = true iff all 4 fields match.
```
_after_
```
numbers compare numerically, booleans identically. `remaining_error_budget_minutes` is compared numerically with an absolute tolerance of 1e-6 and is to be reported to at most one decimal place, so a value reached by division cannot differ from the key in its last bit (closes UG-20). answer_correct = true iff all 4 fields match.
```

**`failure_condition`** — closes UG-19

_before_
```
(3) the reply is not parseable as a single JSON object with exactly the required keys;
```
_after_
```
(3) the reply is not parseable as a single JSON object, or one of the required keys is missing from it (a key beyond the required set is not a failure - see quality_metric);
```

**`failure_condition`** — closes RT-08

_before_
```
(6) the run reads any file under `corpora/mcp_toolset/fixtures/`, which makes the tool-selection measurement meaningless.
```
_after_
```
(6) the run reads any file under `corpora/mcp_toolset/fixtures/`, which makes the tool-selection measurement meaningless.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits `corpora/mcp_toolset/`" holds when any path under that directory is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. "The run reads a file under `corpora/mcp_toolset/fixtures/`" holds when `required_evidence.corpus_access_log` - a list supplied by the harness of the file paths the run opened - contains any path resolving inside that directory. If either hash object, or `corpus_access_log`, is absent or empty, the corresponding condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes` or `required_evidence_missing:corpus_access_log`. (Closes RT-08.)
```

**`notes`** — closes RT-11

_before_
```
Both decoys flip an output: the raw error budget is negative where the reported one is positive, and the queue-default target turns a breach into a pass.
```
_after_
```
Both decoys flip an output: the raw error budget is negative where the reported one is positive, and the queue-default target turns a breach into a pass. RT-11 repair: the contested families now contain only tools that return a competing answer to this task's question. `rota.search_rota`, `registry.search_images`, `vulndb.search_advisories`, `billing.search_orders`, `calendar.get_iso_week`, `calendar.get_month_boundaries`, `metrics.get_slo` and `tickets.get_queue` returned nothing that competes and have moved to uncontested families; `calendar.get_calendar_period` was added so that `calendar-period-resolution` is a real two-member decoy family rather than a family of one.
```

### E-001

**`text`** — closes BUILDER_NOTES E-001 #3

_before_
```
Start the bill of materials. We need 4 edge appliances, 2U form factor.
```
_after_
```
Start the bill of materials. We need 4 edge appliances, 2U form factor. Standing instruction for the whole job: where the catalogue entry that most obviously matches what I ask for is not one we are allowed to buy, substitute the nearest catalogue entry that is allowed and still meets the stated specification, put that entry in the bill of materials, and tell me what you substituted and why. Do not stop and ask.
```

**`text`** — closes RT-06

_before_
```
Apply the policy in
`procurement_policy.md` for the contingency base, the freight rate and the approval
threshold.
```
_after_
```
Apply the policy in
`procurement_policy.md` for the contingency base, the freight rate, the approval
threshold and, in P1, for exactly where rounding happens.
```

**`expected_behavior`** — closes BUILDER_NOTES E-001 #3

_before_
```
substitutes an eligible part when the obvious catalogue entry belongs to the excluded vendor,
```
_after_
```
substitutes an eligible part when the obvious catalogue entry belongs to the excluded vendor, as turn 7's standing instruction directs, and says what it substituted,
```

**`quality_metric`** — closes UG-25

_before_
```
  V2 any monetary value in the final JSON that is not a string matching ^[0-9]+\.[0-9]{2}$;
```
_after_
```
  V2 any monetary value in the final JSON that is not a string matching ^[0-9]+\.[0-9]{2}$. The
     monetary values of the final JSON are exactly these and no others (closes UG-25): the six
     scalars `hardware_subtotal_eur`, `service_subtotal_eur`, `freight_eur`, `contingency_eur`,
     `grand_total_eur` and `amount_over_cap_eur`, plus `unit_price_eur` and `line_total_eur` on
     every row of `bom`. No other field is monetary for the purposes of V2;
```

**`quality_metric`** — closes UG-26

_before_
```
  Each distinct violation instance is counted once per turn in which it occurs.
```
_after_
```
  A DISTINCT VIOLATION INSTANCE is identified by the triple (turn, code, subject), where code is V1..V6 and subject is the single entity the check names - the part id, the field name, the service, the step_id, the person id or the shift id, as the check's own wording fixes it. Two breaches of the same code in the same turn about the same subject are one instance; the same code in the same turn about two subjects is two. The count never decides pass or fail - any count above zero fails - so this rule fixes only the reported number. (Closes UG-26.)
```

**`quality_metric`** — closes RT-06, UG-09, UG-30

_before_
```
Two components, both reported.
(a) completion: the final JSON is compared field by field against the answer key. The `bom` array is matched on part_id with 5 comparable cells per key row (description, vendor, qty, unit_price_eur, line_total_eur); a key row with no reported counterpart counts as 5 mismatches, a reported row whose part_id is not in the key adds 5 to the denominator and contributes 0. The 9 scalar fields are each one cell. Monetary strings compare as exact strings; integers and booleans compare identically. completion = matched_cells / denominator, 4 decimals.
(b) constraint_violations, counted over EVERY reply in the run, not only the final one:
  V1 any part_id that does not appear verbatim in `parts_catalog.csv`;
  V2 any monetary value in the final JSON that is not a string matching ^[0-9]+\.[0-9]{2}$. The
     monetary values of the final JSON are exactly these and no others (closes UG-25): the six
     scalars `hardware_subtotal_eur`, `service_subtotal_eur`, `freight_eur`, `contingency_eur`,
     `grand_total_eur` and `amount_over_cap_eur`, plus `unit_price_eur` and `line_total_eur` on
     every row of `bom`. No other field is monetary for the purposes of V2;
  V3 any part_id whose vendor in `parts_catalog.csv` is Halberd Manufacturing appearing as a proposed or accepted bill-of-materials line in any reply at or after turn 3 (naming the vendor in prose, for
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Two components, both reported.
(a) completion: the final JSON is compared field by field against the answer key. The `bom` array is matched on part_id with 5 comparable cells per key row (description, vendor, qty, unit_price_eur, line_total_eur); a key row with no reported counterpart counts as 5 mismatches, a reported row whose part_id is not in the key adds 5 to the denominator and contributes 0. The 9 scalar fields are each one cell. Monetary strings compare as exact strings; integers and booleans compare identically. completion = matched_cells / denominator, 4 decimals.
(b) constraint_violations, counted over EVERY reply in the run, not only the final one:
  V1 any part_id that does not appear verbatim in `parts_catalog.csv`;
  V2 any monetary value in the final JSON that is not a string matching ^[0-9]+\.[0-9]{2}$. The
     monetary values of the final JSON are exactly these and no others (closes UG-25): the six
     scalars `hardware_subtotal_eur`, `service_subtotal_eur`, `freight_eur`, `contingency_eur`,
     `grand_total_eur` and `amount_over_cap_eur`, plus `unit_price_eur` and `line_total_eur` on
     every row of `bom`. No other field is monetary for the purposes of V2;
  V3 any part_id whose vendor in `parts_catalog.csv` is Halberd Manufacturing appearing as a proposed or accepted bill-of-materials line in any reply at or after turn 3 (naming the vendor in prose, for
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes RT-08

_before_
```
(4) the run edits any file in `corpora/workflow_e/`.
```
_after_
```
(4) the run edits any file in `corpora/workflow_e/`, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits any file in `corpora/workflow_e/`" holds when any path under that directory is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### E-002

**`quality_metric`** — closes RT-15

_before_
```
with 5 comparable cells per key step (step_id, action, service, wave, owner_team, start_utc counts as 6 - use 6).
```
_after_
```
with 6 comparable cells per key step: `step_id`, `action`, `service`, `wave`, `owner_team` and `start_utc`. (v1.0.0 said "5", then listed six fields, then said to use six. Six is correct and the contradiction is removed. Closes RT-15 / UG-21.)
```

**`quality_metric`** — closes UG-26

_before_
```
  Each distinct violation instance is counted once per turn in which it occurs.
```
_after_
```
  A DISTINCT VIOLATION INSTANCE is identified by the triple (turn, code, subject), where code is V1..V6 and subject is the single entity the check names - the part id, the field name, the service, the step_id, the person id or the shift id, as the check's own wording fixes it. Two breaches of the same code in the same turn about the same subject are one instance; the same code in the same turn about two subjects is two. The count never decides pass or fail - any count above zero fails - so this rule fixes only the reported number. (Closes UG-26.)
```

**`quality_metric`** — closes UG-30

_before_
```
Two components, both reported.
(a) completion: the `steps` array is matched positionally, index by index, with 6 comparable cells per key step: `step_id`, `action`, `service`, `wave`, `owner_team` and `start_utc`. (v1.0.0 said "5", then listed six fields, then said to use six. Six is correct and the contradiction is removed. Closes RT-15 / UG-21.) A key index with no reported step counts as 6 mismatches; a reported step beyond the key's length adds 6 to the denominator and contributes 0. `step_count` and `total_duration_minutes` are one cell each. completion = matched_cells / denominator, 4 decimals.
(b) constraint_violations, counted over EVERY reply in the run:
  V1 the token `kestrel-vault` appearing as a step's `service`, or named as a step to be      performed, in any reply at or after turn 3;
  V2 the word `simply` or the word `just`, case-insensitive, whole word, appearing in any      reply at or after turn 4;
  V3 a step_id that is not of the form MIG-nnn with three digits, or a step_id sequence      with a gap, a repeat or a start other than MIG-001, in the final answer;
  V4 `kestrel-mailer` appearing as a step's service in any reply at or after turn 9;
  V5 any timestamp in any reply at or after turn 6 that is not RFC 3339 UTC ending in Z.
  A DISTINCT VIOLATION INSTANCE is identified by the triple (turn, code, subject), where code is V1..V6 and subject is the single
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Two components, both reported.
(a) completion: the `steps` array is matched positionally, index by index, with 6 comparable cells per key step: `step_id`, `action`, `service`, `wave`, `owner_team` and `start_utc`. (v1.0.0 said "5", then listed six fields, then said to use six. Six is correct and the contradiction is removed. Closes RT-15 / UG-21.) A key index with no reported step counts as 6 mismatches; a reported step beyond the key's length adds 6 to the denominator and contributes 0. `step_count` and `total_duration_minutes` are one cell each. completion = matched_cells / denominator, 4 decimals.
(b) constraint_violations, counted over EVERY reply in the run:
  V1 the token `kestrel-vault` appearing as a step's `service`, or named as a step to be      performed, in any reply at or after turn 3;
  V2 the word `simply` or the word `just`, case-insensitive, whole word, appearing in any      reply at or after turn 4;
  V3 a step_id that is not of the form MIG-nnn with three digits, or a step_id sequence      with a gap, a repeat or a start other than MIG-001, in the final answer;
  V4 `kestrel-mailer` appearing as a step's service in any reply at or after turn 9;
  V5 any timestamp in any reply at or after turn 6 that is not RFC 3339 UTC ending in Z.
  A DISTINCT VIOLATION INSTANCE is identified by the triple (turn, code, subject), where code is V1..V6 and subject is the single
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes RT-08

_before_
```
(4) the run edits any file in `corpora/workflow_e/`.
```
_after_
```
(4) the run edits any file in `corpora/workflow_e/`, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits any file in `corpora/workflow_e/`" holds when any path under that directory is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

### E-003

**`quality_metric`** — closes UG-27

_before_
```
  V5 a person assigned to more shifts than their `max_shifts` as it stands at that turn;
```
_after_
```
  V5 a person assigned to more shifts than their `max_shifts` as it stands at that turn. "As it
     stands at that turn" means the `max_shifts` value in `staff_roster.csv` for every person and
     every turn, with one exception fixed by the conversation itself: from turn 16 onward, and in
     the final answer, PR-016's `max_shifts` is 3, because turn 16 raises it. No other override
     exists in this scenario and the judge is not to look for one; nothing is read from
     `required_evidence` for V5. (Closes UG-27, and replaces the scoring spec's
     `max_shifts_overrides` evidence field, which could silently go missing and take V5 with it.);
```

**`quality_metric`** — closes UG-26

_before_
```
  Each distinct violation instance is counted once per turn in which it occurs.
```
_after_
```
  A DISTINCT VIOLATION INSTANCE is identified by the triple (turn, code, subject), where code is V1..V6 and subject is the single entity the check names - the part id, the field name, the service, the step_id, the person id or the shift id, as the check's own wording fixes it. Two breaches of the same code in the same turn about the same subject are one instance; the same code in the same turn about two subjects is two. The count never decides pass or fail - any count above zero fails - so this rule fixes only the reported number. (Closes UG-26.)
```

**`quality_metric`** — closes UG-09, UG-30

_before_
```
Two components, both reported.
(a) completion: `assignments` is matched on shift_id with 2 comparable cells per key row (assigned_person_id, reason_if_unfilled), JSON null being a value. A key shift_id with no reported row counts as 2 mismatches; a reported shift_id not in the key adds 2 to the denominator and contributes 0. `unfilled_count` is one cell. completion = matched_cells / denominator, 4 decimals.
(b) constraint_violations, counted over EVERY reply in the run:
  V1 an assignment whose person's `certification` differs from the shift's      `required_certification`;
  V2 an assignment whose person's `site_id` differs from the shift's `site_id`;
  V3 an assignment of a person whose roster `status` is `on_leave`, or of PR-014 in any      reply at or after turn 12;
  V4 an assignment to a `night` shift of a person whose `night_qualified` is `no`;
  V5 a person assigned to more shifts than their `max_shifts` as it stands at that turn. "As it
     stands at that turn" means the `max_shifts` value in `staff_roster.csv` for every person and
     every turn, with one exception fixed by the conversation itself: from turn 16 onward, and in
     the final answer, PR-016's `max_shifts` is 3, because turn 16 raises it. No other override
     exists in this scenario and the judge is not to look for one; nothing is read from
     `required_evidence` for V5. (Closes UG-27, and replaces
[... truncated at 1400 characters; the full text is in the file ...]
```
_after_
```
Two components, both reported.
(a) completion: `assignments` is matched on shift_id with 2 comparable cells per key row (assigned_person_id, reason_if_unfilled), JSON null being a value. A key shift_id with no reported row counts as 2 mismatches; a reported shift_id not in the key adds 2 to the denominator and contributes 0. `unfilled_count` is one cell. completion = matched_cells / denominator, 4 decimals.
(b) constraint_violations, counted over EVERY reply in the run:
  V1 an assignment whose person's `certification` differs from the shift's      `required_certification`;
  V2 an assignment whose person's `site_id` differs from the shift's `site_id`;
  V3 an assignment of a person whose roster `status` is `on_leave`, or of PR-014 in any      reply at or after turn 12;
  V4 an assignment to a `night` shift of a person whose `night_qualified` is `no`;
  V5 a person assigned to more shifts than their `max_shifts` as it stands at that turn. "As it
     stands at that turn" means the `max_shifts` value in `staff_roster.csv` for every person and
     every turn, with one exception fixed by the conversation itself: from turn 16 onward, and in
     the final answer, PR-016's `max_shifts` is 3, because turn 16 raises it. No other override
     exists in this scenario and the judge is not to look for one; nothing is read from
     `required_evidence` for V5. (Closes UG-27, and replaces
[... truncated at 1400 characters; the full text is in the file ...]
```

**`failure_condition`** — closes RT-08

_before_
```
(4) the run edits any file in `corpora/workflow_e/`.
```
_after_
```
(4) the run edits any file in `corpora/workflow_e/`, as established below.

Corpus integrity is established from `required_evidence.corpus_hashes_before` and `required_evidence.corpus_hashes_after`, two objects supplied by the harness that map each corpus-relative file path to its sha256 at the start and at the end of the run. "The run edits any file in `corpora/workflow_e/`" holds when any path under that directory is present in both objects with different hashes, or is present in `corpus_hashes_before` and absent from `corpus_hashes_after`. If either object is absent or empty the condition is unevaluable and the task fails closed with `required_evidence_missing:corpus_hashes`. (Closes RT-08.)
```

---

## 4. What this obliges the Quality Judge and the Answer Key Builder to do

`SCORING_SPEC.md` in this directory is the v1.0.0 spec, **carried over unmodified** because this
seat does not own it. Its own precedence rule — "where this document disagrees with a frozen task
file, the task wins" — now bites in several places. The judge seat should read these as
requirements, not suggestions:

1. **Workload C traceability changed shape.** It is no longer `supported / total`. It is
   `supported / (total + missing)`, where `missing` counts governing sources omitted from a
   record's `sources`. Citing too narrowly now costs what citing too broadly costs. The key must
   supply, per record, the set of **governing sources** — and that set *is* the set the metric
   describes. The v1.0.0 pattern of a curated `sources` list plus a separate
   `non_authoritative_files_stating_the_same_introduced_in` list is exactly the divergence RT-04
   objected to and must not be reproduced.
2. **Workload C's `count` is explicitly not a comparable cell** and must not carry the 0.05
   penalty `judge.py` applies today (RT-09, from the task-text side: the three C metrics said no
   penalty, and now they say so in words).
3. **Workload B's `count` is one comparable cell**, added to numerator and denominator. The
   denominator is `7·|K| + 1` for B-002 and `4·|K| + 1` for B-003.
4. **Workload A's count penalty is 0.02, not 0.05.**
5. **`required_tools` is a permission list.** A subset is fine. A contested-family call outside it
   is a wrong-tool invocation.
6. **An extra key in a D reply is no longer fatal.** A missing required key still is.
7. **E-003 V5 reads nothing from `required_evidence`.** The turn-16 override is stated in the task.
8. **The seven relative floors are gone.** A's `task_success` is `quality_score >= 0.95` and C's
   is `coverage >= 0.90 AND traceability == 1.00`, both absolute. `judge.py`'s
   `baseline_reference_quality` injection, `floor_basis` and `relative_floor_pending` are no
   longer needed for any task in this set, and the C0-before-A/C scoring order they forced is
   no longer a dependency of the run plan.
9. **Every task now names corpus-hash evidence** (`corpus_hashes_before`, `corpus_hashes_after`)
   and A-001 and D additionally name `corpus_access_log`. All fail closed on absence **or
   emptiness**. This is new required evidence for 17 tasks; it is the same fail-closed discipline
   RT-01 and RT-02 asked for, and it is now the task text's requirement rather than the spec's
   silence.

---

## 5. Judgement calls a reviewer may reasonably contest

Each of these is a decision, not a deduction. They are listed so they can be overruled cheaply.

1. **RT-04 was ruled against breadth, not for it.** A low-authority file that states the correct
   value is **not** a valid citation. The alternative — "any file that literally states the value
   is supported" — would have been kinder to broad retrieval, but it would have made
   `governing_source_tier` and the whole authority order decorative, and it would have let a run
   cite a forum thread for a value the forum thread is wrong about elsewhere. The asymmetry the
   Red Team objected to is removed by the completeness rule instead: breadth and narrowness now
   cost the same. **This makes workload C strictly harder than v1.0.0**, because an incomplete
   `sources` list used to be free. If the Lab wants C easier, the lever is the coverage floor, not
   the citation rule.
2. **RT-10 was ruled in the direction that raises the pass rate**, which is the direction a
   designer should be most suspicious of. The B-002 effect is stated in the task text so a reviewer
   can weigh it: a perfect answer with a wrong `count` goes from 0.95 (fail) to 0.9945 (pass), and
   a wrong `count` now costs exactly one cell of tolerance below the unchanged 0.97 floor. The
   floor was not moved and no task was weakened. If a reviewer thinks a bookkeeping slip *should*
   be fatal, the change is one sentence.
3. **UG-19 was overruled.** An extra key in a D reply no longer fails the task. This is more
   permissive than the judge's rule and than the D prompt's word "exactly", which was changed to
   match. The argument is confound control, not leniency; it is written in the task text.
4. **UG-27 was overruled in the opposite direction** — the task now states the turn-16 override
   itself rather than depending on a `required_evidence` field. This is more robust but it hard-
   codes a person id and a value into the metric, which will not survive a regenerated corpus.
5. **The v1.0.0 `MANIFEST.sha256` was deleted from this task set rather than left in place.** It
   covered a different tree, it never covered `answer_keys/` (RT-12), and `README.md` defined
   `config_hash` as its sha256. Leaving a manifest that fails to verify is a worse hazard than
   having none while the coordinator builds the wider one. A reviewer who would rather have kept
   the stale file can restore it from v1.0.0 in one command.
6. **`shortcut_probe/probe_b002.py` is committed**, and it contains an extractor that can produce
   a B-002 answer. That is in tension with `DESIGN_NOTES.md` §0's rule that no ground truth lives
   in this directory. The trade was made deliberately: RT-03 is BLOCKING and its repair is
   worthless if it cannot be re-measured. Mitigations: the corpus **generator** is still not
   committed, the results file reports only aggregate scores, and the script's header states that
   the Answer Key Builder must derive B-002 independently and that the script is wrong if they
   disagree.
7. **Two changes were made that are not on the Red Team's list**, both from `BUILDER_NOTES.md`,
   both because they cause a correct run to score near zero for a reason unrelated to quality:
   * **E-001 turn 7** now carries a standing instruction authorising substitution and requiring the
     agent to say what it substituted. Without it, a run that refuses to substitute and asks the
     user — good behaviour under turn 3 — scores about 0 on the BOM. The hard part (remembering
     turn 3 across eleven turns, and finding the eligible part) is untouched.
   * **B-002's output key** `final_severity` is now tied in words to the register's `severity`
     field, which the v1.0.0 notices named inconsistently.
8. **`directory.get_person_by_email` was kept in the contested `person-resolution` family** even
   though it returns the *correct* person record. It competes (it is an alternative resolution
   path) and so satisfies RT-11's criterion, and D-001 never hands the run an email address, so it
   is not a natural path. A reviewer who thinks "correct answer, failed task" is unacceptable in
   principle should move it to an uncontested family.
9. **The B-002 document grew from 147 KB to 161 KB.** Workload B's cost measurement is per task and
   per condition, so this does not affect any comparison within B-002, but it does move B-002's
   absolute token cost relative to v1.0.0 runs. No v1.0.0 run should be pooled with a v1.1.0 run.

---

## 6. Not fixed, and why

| finding | status | why not here |
|---|---|---|
| **RT-01** — `required_evidence` has no producer | **Open, and now larger.** | Every v1.1.0 task names corpus-hash evidence on top of what v1.0.0 already needed, so the field's owner now has more to produce. Naming it in the task text is the part a Task Set Designer can do; building it is the harness owner's. Nothing can be run until it exists. |
| **RT-02** — workload E fails open on empty evidence | Open. | `judge.py` is another seat's. The task text now fails closed on *empty* as well as absent for every field it names, and E-003 V5 was removed from `required_evidence` entirely so one of the three affected checks can no longer be silently disarmed. `part_id_pattern` is still the spec's to specify or delete. |
| **RT-05** — relative floors move down with a weak baseline | **Closed in the task text.** | The absolute floors approved for v1.1.0 are now written into the seven affected `quality_metric`s, together with the reason. What remains open is not this seat's: `methodology/METHODOLOGY_v1.0.0.md` §6 still says "≥95% of baseline's correct set", and a frozen methodology can only be changed by a `METHODOLOGY_CHANGE_REQUEST` and a new version file. Until that lands, the task text and the methodology disagree, and the task text is the one the judge reads. |
| **RT-09** — judge applies a `count` penalty to C that the task text denies | Half closed. | The task text now says in words that `count` is not a comparable cell and does not change coverage. Removing the penalty from `judge.py` is the judge seat's. |
| **RT-12** — manifest does not cover `answer_keys/` | Not this seat's. | The coordinator builds the wider manifest. The stale one was removed rather than left to mislead. |
| **RT-13** — nothing asserts that E turns are delivered | Open. | A harness assertion, not a task file. The E `protocol` block already states the contract. |
| **RT-18** — `SCORING_SPEC.md` says 81 tests, the suite runs 100 | Not this seat's. | `SCORING_SPEC.md` is owned elsewhere. |
| **RT-21** — audit `seq` restarts per process | Not this seat's. | `server.py`'s audit writer belongs to the environment seat, and it has no scoring impact. |
| **UG-01, 02, 04, 10, 11, 12, 16, 18, 21–24, 28, 29, 31–33** | Not assigned to this seat. | Several are now partly addressed as a side effect — UG-11's citation binding is superseded by the new C rule, UG-16's evidence field is named in the D metric, UG-21 is RT-15 and is closed — but the spec entries themselves are the judge's to update. |

### One thing that was checked and found not to need fixing

The Builder's warning that UG-11 "couples traceability to coverage, so a wrong value in workload C
fails the task twice" was **overstated** in v1.0.0, and the new rule does not reintroduce it: under
§(c) a citation is supported when the cited file governs *at least one* value of the record, so a
record with one wrong field keeps its traceability as long as another field is right and cited.
Nobody should "fix" a problem that is not there.

---

## 7. Addendum — the absolute quality floors (RT-05)

Applied after §3 was written, so the before/after quotes for it are collected here.
The floors are the ones approved for v1.1.0: A `quality_score >= 0.95` with zero fabricated
symbols; B `>= 0.97`; C `coverage >= 0.90` **and** `traceability == 1.00`; D per attempt,
correct tool and correct answer with zero wrong-tool invocations; E `completion >= 0.95` with
zero constraint violations. B, D and E were already absolute in v1.0.0 and did not change.
No floor was lowered: A's effective bar rises whenever the C0 median would have come in below
1.0, and C's likewise.

**A-001 `quality_metric`** — closes RT-05 / v1.1.0 absolute floor

_before_
```
task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-001) AND 
```
_after_
```
task_success = true iff quality_score >= 0.95 AND 
```

**A-001 `quality_metric`** — closes RT-05

_before_
```
Let K be the answer-key set and P the set in `reaching_functions`, both compared as exact case-sensitive strings. TP=|P n K|, FP=|P \ K|, FN=|K \ P|. precision=TP/(TP+FP) (defined as 0 when TP+FP=0), recall=TP/(TP+FN), quality_score = F1 = 2*precision*recall/(precision+recall), 0 when precision+recall=0, rounded to 4 decimal places. A duplicate entry is removed before scoring and is not an error. `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 AND the run reports zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `valid_symbols` is absent or empty the criterion 
[... truncated ...]
```
_after_
```
Let K be the answer-key set and P the set in `reaching_functions`, both compared as exact case-sensitive strings. TP=|P n K|, FP=|P \ K|, FN=|K \ P|. precision=TP/(TP+FP) (defined as 0 when TP+FP=0), recall=TP/(TP+FN), quality_score = F1 = 2*precision*recall/(precision+recall), 0 when precision+recall=0, rounded to 4 decimal places. A duplicate entry is removed before scoring and is not an error. `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 AND the run reports zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `valid_symbols` is absent or empty the criterion 
[... truncated ...]
```

**A-002 `quality_metric`** — closes RT-05 / v1.1.0 absolute floor

_before_
```
task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-002) AND 
```
_after_
```
task_success = true iff quality_score >= 0.95 AND 
```

**A-002 `quality_metric`** — closes RT-05

_before_
```
Set F1 over `unreferenced_functions` against the answer key, computed exactly as in A-001, rounded to 4 decimal places; `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `valid_symbols` is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:valid_symbols`; it is never treated as "no fabrications found". (Closes UG-03.)
```
_after_
```
Set F1 over `unreferenced_functions` against the answer key, computed exactly as in A-001, rounded to 4 decimal places; `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `valid_symbols` is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:valid_symbols`; it is never treated as "no fabrications found". (Closes UG-03.)
The floor is ABSOLUTE and is evaluated against the full answer key. It replaces v1.0.0's `0.95 x (baseline C0 median quality_score for this tas
[... truncated ...]
```

**A-003 `quality_metric`** — closes RT-05 / v1.1.0 absolute floor

_before_
```
task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-003) AND 
```
_after_
```
task_success = true iff quality_score >= 0.95 AND 
```

**A-003 `quality_metric`** — closes RT-05

_before_
```
Set F1 over `retry_decorated_reaching_transient` against the answer key, computed exactly as in A-001, rounded to 4 decimal places; `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `valid_symbols` is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:valid_symbols`; it is never treated as "no fabrications found". (Closes UG-03.)
```
_after_
```
Set F1 over `retry_decorated_reaching_transient` against the answer key, computed exactly as in A-001, rounded to 4 decimal places; `count` is a self-consistency check on the emitted list, not one of the analysed values. A `count` that disagrees with the length of the de-duplicated list subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05: a bookkeeping slip is not equivalent to a wrong analysis, but it is not free either. (Closes RT-10 for workload A.) task_success = true iff quality_score >= 0.95 AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the harness from the frozen corpus. If `valid_symbols` is absent or empty the criterion is unevaluable and the task fails closed with `required_evidence_missing:valid_symbols`; it is never treated as "no fabrications found". (Closes UG-03.)
The floor is ABSOLUTE and is evaluated against the full answer key. It replaces v1.0.0's `0.95 x (baseline C0 median quality_score 
[... truncated ...]
```

**A-004 `quality_metric`** — closes RT-05 / v1.1.0 absolute floor

_before_
```
task_success = true iff quality_score >= 0.95 * (baseline C0 median quality_score for A-004) AND 
```
_after_
```
task_success = true iff quality_score >= 0.95 AND 
```

**A-004 `quality_metric`** — closes RT-05

_before_
```
Components are compared as sets of frozensets: duplicate members within a reported component, and duplicate components within the outer array, are removed before comparison and are not errors (closes UG-05). Let K be the key's set of components and P the reported set. A reported component scores as a match only if it equals a key component exactly (same members, no more, no fewer); partial overlap scores nothing. TP=|P n K|, FP=|P \ K|, FN=|K \ P|, and quality_score = F1 = 2TP/(2TP+FP+FN), rounded to 4 decimal places. `component_count` is a self-consistency check, not one of the analysed values: it is compared with the number of components in the EMITTED outer array (before de-duplication), and a disagreement subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05 (closes RT-10 for workload A and UG-05's count half). task_success = true iff quality_score >= 0.95 AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the 
[... truncated ...]
```
_after_
```
Components are compared as sets of frozensets: duplicate members within a reported component, and duplicate components within the outer array, are removed before comparison and are not errors (closes UG-05). Let K be the key's set of components and P the reported set. A reported component scores as a match only if it equals a key component exactly (same members, no more, no fewer); partial overlap scores nothing. TP=|P n K|, FP=|P \ K|, FN=|K \ P|, and quality_score = F1 = 2TP/(2TP+FP+FN), rounded to 4 decimal places. `component_count` is a self-consistency check, not one of the analysed values: it is compared with the number of components in the EMITTED outer array (before de-duplication), and a disagreement subtracts 0.02 from quality_score (floor 0) and is reported separately as `count_consistent: false`. This replaces v1.0.0's 0.05 (closes RT-10 for workload A and UG-05's count half). task_success = true iff quality_score >= 0.95 AND zero fabricated symbols.
Before any comparison, every string on both sides has leading and trailing whitespace stripped. (Closes UG-30.)
Fabricated symbols. A fabricated symbol is any reported symbol that is not a module-level function actually defined under `corpora/repo_ledgerline/ledgerline/`. The set of symbols that do exist is supplied to the judge as `required_evidence.valid_symbols`, a list of fully qualified dotted names derived by the 
[... truncated ...]
```

**C-001 `quality_metric`** — closes RT-05 / v1.1.0 absolute floor

_before_
```
task_success = true iff traceability == 1.0 AND coverage >= 0.90 * (baseline C0 median coverage for C-001).
```
_after_
```
task_success = true iff traceability == 1.0 AND coverage >= 0.90. Both floors are ABSOLUTE. The coverage floor replaces v1.0.0's `0.90 x (baseline C0 median coverage for this task)` for the reasons given in RT-05: a blind judge cannot compute a batch median, the relative form forced a two-pass scoring order that the run matrix does not describe, and it moved down with a weak baseline. traceability was already absolute at 1.00 and is unchanged.
```

**C-002 `quality_metric`** — closes RT-05 / v1.1.0 absolute floor

_before_
```
task_success = true iff traceability == 1.0 AND coverage >= 0.90 * (baseline C0 median coverage for C-002).
```
_after_
```
task_success = true iff traceability == 1.0 AND coverage >= 0.90. Both floors are ABSOLUTE. The coverage floor replaces v1.0.0's `0.90 x (baseline C0 median coverage for this task)` for the reasons given in RT-05: a blind judge cannot compute a batch median, the relative form forced a two-pass scoring order that the run matrix does not describe, and it moved down with a weak baseline. traceability was already absolute at 1.00 and is unchanged.
```

**C-003 `quality_metric`** — closes RT-05 / v1.1.0 absolute floor

_before_
```
task_success = true iff traceability == 1.0 AND coverage >= 0.90 * (baseline C0 median coverage for C-003).
```
_after_
```
task_success = true iff traceability == 1.0 AND coverage >= 0.90. Both floors are ABSOLUTE. The coverage floor replaces v1.0.0's `0.90 x (baseline C0 median coverage for this task)` for the reasons given in RT-05: a blind judge cannot compute a batch median, the relative form forced a two-pass scoring order that the run matrix does not describe, and it moved down with a weak baseline. traceability was already absolute at 1.00 and is unchanged.
```


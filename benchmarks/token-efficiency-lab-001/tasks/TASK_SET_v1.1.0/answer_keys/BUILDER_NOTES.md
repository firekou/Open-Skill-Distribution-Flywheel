# BUILDER_NOTES.md — ATK Token Efficiency Lab 001, answer keys

Seat: **Answer Key Builder**. Scope: all 17 tasks (A×4, B×3, C×3, D×4, E×3).

Every key in this directory was derived **against the frozen task set whose manifest is
`MANIFEST.sha256`, sha256 `9bc84e9f1307175a3d83f111ded05aa03eb15acd18baca0571e0fe36de0e3105`**.
All 155 manifest entries were verified to match on disk before the keys were written, and
verified again afterwards (155/155 OK), so nothing under `tasks/` or `corpora/` was modified by
this seat. `DESIGN_NOTES.md` was not read; every key was derived independently from the task
statement and the corpus.

## How to re-derive

```
python3 answer_keys/scripts/derive_A.py --write     # A-001..A-004
python3 answer_keys/scripts/derive_B.py --write     # B-001..B-003
python3 answer_keys/scripts/derive_C.py --write     # C-001..C-003
python3 answer_keys/scripts/derive_D.py --write     # D-001..D-004
python3 answer_keys/scripts/derive_E.py --write     # E-001..E-003
```

Without `--write` each script prints the same payloads to stdout. All five are offline,
deterministic and read only from `corpora/`. Verification performed: all 17 keys were written,
their sha256 recorded, all five scripts re-run, and every file came back **byte-identical**
(17/17). Every key file parses as JSON and carries `task_id`, `derived_by`,
`derivation_method` and `derivation_script`.

`derive_D.py` obtains its values by calling the task's own offline MCP server
(`python3 corpora/mcp_toolset/server.py call <tool> '<json>'`). It never reads
`corpora/mcp_toolset/fixtures/` and never scrapes `server.py`, so it also demonstrates that the
`required_tools` set named in each D key is sufficient to answer the task. It strips
`LAB001_TOOL_AUDIT` from the environment so it can never contaminate a run's audit file.

---

# Per-task derivation and confidence

## A-001 … A-004 — call-graph analysis over `repo_ledgerline`

**Method.** `derive_A.py` parses every `.py` file under `ledgerline/` with Python's `ast`
module (never `tests/`, per R3). Module-level `FunctionDef`s are the node set; a call edge is a
`ast.Call` whose `func` is an `ast.Name` naming one of those functions, found anywhere inside a
function body. Using the AST rather than text search makes R5 (comments / docstrings / string
literals are not code) true *by construction* rather than by filtering, and makes R6 (the
`getattr` dispatch table in `dynamic.py`) fall out for free — those are string constants, not
calls.

Checks the script performs and that passed:

* 394 module-level functions; **no duplicate short names**, so R4's "names are globally unique"
  holds and a bare name resolves to exactly one definition.
* **No self-recursive functions**, so the A-002 question "does a self-call count as a reference
  to yourself?" never arises.
* **No `Name` load of a function name that is neither a call callee nor an import** — so U1's
  narrow definition of a reference (callee or import only) and a broader one (any code-level
  mention) give the *same* answer here. This was the ambiguity I most expected to bite; it does
  not.

Results: A-001 63 reaching functions (out of exactly 126 functions in `api/`+`plugins/`+`cli/`
— a 63/63 split, so a blanket guess scores ~0.5 F1 as the task notes claim); A-002 11
unreferenced functions; A-003 10 functions; A-004 4 components.

**Confidence: high** for all four. These are mechanical questions with a mechanical answer and
the rules R1–R8 are unusually tight.

### Ambiguities / defects (A)

1. **`retryable` does not exist. (Defect, low scoring impact, real corpus bug.)**
   Fifteen modules do `from ledgerline.util.retry import retryable`, but
   `ledgerline/util/retry.py` **does not define `retryable`**. The corpus is not importable.
   It does not change any key (D1 is satisfied by the import statement naming the module, and
   `retryable` is not itself a module-level function so it cannot appear in an answer), but a
   run that tries to *execute* the corpus, or that reasons "this import must be wrong, so the
   decorator must be `retryable_v2`", will go astray. `retryable_v2` *is* defined
   (`plugins/legacy_retry.py`), which makes the asymmetry more misleading, not less.

2. **A-002 U1 does not say what to do with a bare-name mention that is neither a call nor an
   import** (e.g. `handler = some_func`). Moot in this corpus — there are none — but the rule
   is under-specified and would bite if the corpus were regenerated with a callback passed by
   reference.

3. **A-002 `__all__` and `dynamic.py`.** `ledgerline/dynamic.py` has
   `__all__ = ["dispatch", "DISPATCH"]`, which makes `dispatch` referenced under U2. Correct,
   but note that U2 rescues a function whose *only* mention is a string in an `__all__` list,
   while R5 says strings are not code. The two rules point opposite ways and only the explicit
   U2 carve-out resolves it. A careful reader gets this right; a fast one may not.

4. **A-003 D3 "F is itself a transient raiser" is untested.** No retry-decorated function is
   itself a `raise TransientError` site in this corpus, so the self-inclusion half of D3 does
   no work and a run that ignores it scores identically. Not a defect in the key, but the trap
   the task thinks it is setting is not armed.

---

## B-001 — MSA as in effect on 2031-11-30

**Method.** `derive_B.py` pulls each value with a regex anchored on the exact clause, Schedule B
paragraph or amendment sub-clause that states it (`grab()` asserts the pattern matches exactly
once, so a corpus change breaks the script instead of silently changing the key). It then
applies the document's own ORDER OF PRECEDENCE: Schedule C is parsed **and discarded** (the
script asserts Schedule C says it is subordinate), Schedule B supplies the service levels, and
Amendments 1 (2031-03-01) and 2 (2031-09-15) are applied while Amendment 3 (2032-01-01) is not.

Key values that the traps turn on: `payment_terms_days` 45 (Amd 1, not the body's 30, and not
coincidentally Schedule C's 45), `audit_notice_business_days` 20 (Amd 1),
`liability_cap_percent_of_charges` 150 (Amd 2), `availability_target_percent` 99.95 (Amd 2),
`p1_restoration_hours` 3 (Amd 2), `subprocessor_objection_days` 21 (Amd 2),
`termination_for_convenience_notice_days` **180** (body — *not* Schedule C's 90 and *not*
Amd 3's 90, which happen to agree with each other and disagree with the right answer),
`liability_cap_absolute_eur` 2000000, `renewal_term_months` 12, `non_renewal_notice_days` 90.

**Confidence: high on 33 of 36 fields, medium on 3.** The three soft ones are below.

### Ambiguities / defects (B-001), worst first

1. **`amendments_in_force_on_as_of_date` — the document and the prompt disagree on spelling.
   (High impact: the metric compares strings case-sensitively, and this is 1 of 36 fields, i.e.
   exactly the one field a run is allowed to miss before it drops under the 0.97 floor.)**
   The document headings are `## AMENDMENT No. 1` (upper case). The prompt's example is
   `"Amendment No. 1"`, and N4 says text is "copied verbatim from the document". A run that
   obeys N4 emits `AMENDMENT No. 1`; a run that follows the prompt's example emits
   `Amendment No. 1`. **I keyed the prompt's spelling** (`"Amendment No. 1"`,
   `"Amendment No. 2"`), because the prompt gives it as the expected form for this specific
   field, but this is a coin-flip that should be fixed in the task text, not in the key.

2. **`governing_law` — how much of the clause is "the value"?** Clause 24.1 reads "governed by
   the laws of England and Wales". I keyed `"England and Wales"`. `"the laws of England and
   Wales"` is a defensible verbatim copy. The field name argues for mine; N4's "verbatim"
   argues for the other. 1 of 36 fields.

3. **`price_increase_frequency_per_twelve_months` and `audit_frequency_per_twelve_months` are
   not printed as numerals.** The document says "**once** in any twelve month period" (5.3 and
   13.1). N5 only covers "spelled out … and repeated as a numeral in brackets"; here there is no
   bracketed numeral, so the value `1` is an inference, not an extraction. Both keyed as `1`.
   Low risk (no competent reader says anything else) but the normalisation rules do not
   actually cover the case.

4. **Minor: `annual_price_increase_cap_percent` is printed `3.0%`.** N2 says "no trailing
   zeroes beyond what the document prints", which argues for `3.0`; the metric says numbers
   compare numerically, so `3` also passes. Keyed as `3.0`. No impact under the stated metric,
   but a strict string comparator would break.

---

## B-002 — incident register as corrected

**Method.** Parse the 48-row Appendix A table; parse all 8 Appendix B notices with a regex
capturing `(incident, field, old value, new value)`; **assert each stated old value against the
register before overwriting it** (all 8 matched — the notices are internally consistent with the
register); then select records whose post-correction severity is S1 or S2. The quarterly
narrative is never read, per the precedence rule in §1.4. Result: **24 records**.

Membership changes: CN-010 promotes INC-2031-010 (S4→S1) *in*; CN-041 promotes INC-2031-041
(S4→S1) *in*; CN-034 demotes INC-2031-034 (S2→S3) *out*. CN-021 (S3→S4) changes nothing about
membership. That is the "three corrections change set membership" the task claims. Non-severity
corrections that land inside the reported set: CN-003 flips INC-2031-003 `customer_impacting`
to `false`, CN-028 changes INC-2031-028 `root_cause_code` to `RC-SW`. CN-015 and CN-046 touch
incidents that are not in the S1/S2 set and are therefore invisible in the answer.

**Confidence: high.**

### Ambiguities / defects (B-002)

1. **The notices name a field that the register does not have.** Appendix A's column is
   `severity`; the correction notices say "the value recorded in Appendix A for
   `final_severity`". The task's output key is `final_severity`, so the intent is obvious, but
   strictly there is no `final_severity` column in Appendix A for a notice to correct. Cosmetic.

2. **The task note is factually wrong about the corpus.** It says the correction notices are
   "placed ~120 KB after the register". The whole document is 147 KB and Appendix B
   *immediately follows* Appendix A (lines 367 and 420 of 462). The long-range-retrieval
   difficulty the note claims is not present: both ends of the document are adjacent. This does
   not affect the key but it does mean B-002 is easier than the design intends, which matters
   if anyone calibrates a baseline against that claim.

---

## B-003 — MUST requirements after errata

**Method.** Parse every `**SDX-REQ-nnnn** An implementation …` line; section number from the
enclosing `## n.` heading; constrained field from the backticked identifier; level from the
modal verb with **longest match first**, so "must not" is never read as "must". Then apply §10:
`Withdrawn` drops the requirement, a corrected level replaces the body level and sets
`level_source: "errata"`, `Clarified` leaves the body level and `level_source: "body"`.

96 requirements in the body, 17 errata entries (3 clarified, 3 withdrawn, 11 relevelled).
Result: **22 MUST requirements**, of which 3 come from the errata (SDX-REQ-0040, -0070, -0073).

Confirmation that the task's own note is accurate: ignoring the errata entirely also yields 22
requirements, differing in exactly six members (body-only adds -0001, -0008, -0082; misses
-0040, -0070, -0073). The script asserts every errata `req_id` exists in the body.

**Confidence: high.**

### Ambiguities / defects (B-003)

1. **The body never prints the keywords.** §1 declares "The key words MUST, MUST NOT, SHOULD…",
   but every requirement is written in lower case prose ("An implementation must populate…").
   Mapping lower-case modal verbs onto the declared levels is obvious but is nowhere stated.
   Low risk.

2. **`level_source` for a `Clarified` entry.** The task says `"errata"` only "if this
   requirement's level comes from an errata entry that gave a corrected level". A clarified
   entry gives no corrected level, so `"body"`. Keyed that way. The three clarified requirements
   (-0022, -0029, -0042, -0074) are not all MUST, so the blast radius is small, but a run that
   reads "the errata mentions it, so the source is errata" loses a cell.

---

## C-001 — Kestrel feature-flag lifecycle

**Method.** Parse the `## Feature flags` list of every official release note for added/removed
entries; apply the three errata (ERR-001 `opportunistic_gc` 2.0→2.2, ERR-002
`nested_span_export` 1.0→1.2, ERR-003 `parallel_compaction` 1.0→2.1). Result: **16 flags**, 8
with a removal release and 8 with `removed_in: null`.

Each key record carries `sources` (the authoritative files), plus a `citation_support` block
giving, per value, the files that literally state it, plus
`non_authoritative_files_stating_the_same_introduced_in` — see ambiguity 2.

**Confidence: high on the data; medium on the citation sets**, for the reasons below.

### Ambiguities / defects (C-001), worst first

1. **`sources` is per record, but traceability is defined per value. (High impact — traceability
   must be exactly 1.0 or the task fails outright.)** The output schema gives one `sources` list
   per flag, while the metric says "a citation is supported when the cited file … states the
   value it is cited for (the answer key lists, per value, the set of files that state it)".
   For a flag with `removed_in: null` there is *no* file that states the null, and for a flag
   with both values the cited files split between them. The only workable reading is "each
   cited file must state at least one of this record's values", and the key's
   `citation_support` block is written so a grader can implement either reading. **This needs
   a ruling from whoever writes the judge, not from me.**

2. **A forum thread can state the right answer. (High impact, same reason.)**
   `forum_thread_4106.md` says `opportunistic_gc` "landed in 2.2" and `forum_thread_4111.md`
   says `adaptive_shard_split` "landed in 2.2" — both are the correct introduced_in. Under the
   metric's literal words ("the cited file … states the value it is cited for") citing them is
   *supported*; under the task's framing (forum threads "are wrong", low authority) citing them
   is clearly not intended. I keyed `sources` to the authoritative files only and recorded the
   coincidentally-correct low-authority files separately. A run that cites one of them is
   either fine or instantly failed depending on the grader's reading. **Rule this explicitly.**

3. **An erratum-corrected flag has two files stating its (now) correct release.** For
   `opportunistic_gc`, both `erratum_ERR-001.md` and `release_notes_kestrel_2_2.md` state 2.2;
   the same for the other two corrected flags. Citing only one of the pair should be fine
   (nothing requires completeness of citations), but the metric never says whether an
   *incomplete* citation set costs anything. Under the literal formula it does not.

---

## C-002 — Meridian Infrastructure Fund award totals

**Method.** Parse the award table in all eight bulletins (24 awards, GA-0001…GA-0024), apply
the three correction notices (asserting the stated original amount against the bulletin first —
all three matched) and the two retraction notices, then sum per project. Result: **7 projects**.

| project | total_eur | excluded |
|---|---|---|
| Project Halyard | 621500 | — |
| Project Ironwood | 574000 | GA-0008 |
| Project Junction | 472000 | — |
| Project Kilnwork | 880500 | — |
| Project Lodestar | 358000 | GA-0017 |
| Project Marrowbone | 807000 | — |
| Project Nettleford | 386000 | — |

**Confidence: high on the arithmetic; the citation half of this task is broken — see below.**

### Ambiguities / defects (C-002), worst first

1. **No file states `total_awarded_eur`, so under the literal traceability definition every
   possible run fails C-002. (Severity: highest in the whole set.)** traceability is
   `supported_citations / total_citations`, where "supported" means the cited file "literally
   states the value it is cited for", and traceability must equal 1.0 or the task fails
   outright. `total_awarded_eur` is a *sum*; it appears in no bulletin and in no notice. Under
   a literal grader, any citation attached to a project record is unsupported for that field,
   traceability < 1.0, outright failure — for a perfect answer. The key therefore records
   `sources` as "every bulletin publishing one of this project's awards, plus every notice that
   changed one of them", and a `citation_support.per_award` block naming, per award, the file
   that states its standing amount. **The judge must be told that a record-level citation is
   supported when it states any constituent award amount or status; otherwise C-002 is
   unscoreable.**

2. **The "empty `awards_included`, total 0" branch is dead.** The prompt specifies behaviour
   for a project whose awards were all retracted; no such project exists (Ironwood and Lodestar
   each lose one award of three or four). Harmless, but it is untested instruction text that a
   run may waste reasoning on.

3. **Notices identify bulletins by number, not by file name.** CORR-001 says "bulletin
   BUL-2031-07", the file is `bulletin_bul_2031_07.md`, and the citation rule demands file
   names "exactly as the file name appears in SOURCE_INDEX.md". The mapping is obvious but the
   corpus never states it outside `SOURCE_INDEX.md`, which the same rule forbids citing as a
   source of facts.

---

## C-003 — plugin minimum Kestrel versions

**Method.** Read `registry_export_2032-02.csv` (8 plugins), override `kp-csv-bridge` → 0.9
(ERR-004) and `kp-fx-lookup` → 2.3 (ERR-005), then sweep every file for a statement of a
different minimum version to build `contradicted_by`. `governing_source_tier` is `erratum` for
the two corrected plugins and `registry_export` for the other six.

**Confidence: high on `min_kestrel_version` and `governing_source_tier`; the `contradicted_by`
cell is a genuine fork — see below.**

### Ambiguities / defects (C-003), worst first

1. **Does `contradicted_by` include the registry export itself? (High impact: it changes 2 of
   8 records, i.e. up to 0.0625 of coverage, and coverage is the quality score.)** The task
   says `contradicted_by` is "an array of source file names that state a DIFFERENT minimum
   version for this plugin". For `kp-csv-bridge` the reported version is 0.9 and
   `registry_export_2032-02.csv` states 3.0 — literally a different version, so it belongs.
   The task's `expected_behavior` instead says the run "sweeps the blog and forum files to
   populate `contradicted_by`", which implies only low-authority files. **I keyed the literal
   reading** (registry export included for `kp-csv-bridge` and `kp-fx-lookup`) and recorded the
   other reading in each record as
   `contradicted_by_alternate_reading_low_authority_only`. Two competent readers produce
   different keys here; the task text needs one sentence to settle it.

2. **`sources` for the two erratum-corrected plugins.** Only the erratum states the corrected
   version, so `sources` is a single-element list. A run that also cites the registry export
   (which states the *wrong* version) fails traceability outright. Correct per the citation
   rule, but worth flagging as the sharpest edge in workload C: the obvious "cite your
   sources, all of them" instinct is fatal here.

---

## D-001 … D-004 — tool selection under sibling pressure

**Method.** `derive_D.py` calls the offline server directly. Each key records
`contested_families`, the `required_tools` a correct run must use, the exact calls the
derivation made (all of which are either the required tools or tools in uncontested families),
the answer, and diagnostics naming the decoy value that the sibling tool would have returned.
The script asserts that it made no contested-family call outside `required_tools`.

| task | required tools | answer |
|---|---|---|
| D-001 | `rota.get_effective_oncall`, `directory.get_person_by_handle` | Adaeze M. Okonjo / Billing Platform / tier 2 |
| D-002 | `registry.resolve_digest_pinned`, `vulndb.get_image_findings_by_digest` | `sha256:bd7745e1…1d33` / 3 / KSA-2032-0117 / debian-12 / 2.9.4-3 |
| D-003 | `billing.get_invoice`, `fiscal.convert_calendar_to_fiscal` | 2032-01-03 / FY2032 / Q4 / 12 / 2032-02-06 |
| D-004 | `metrics.get_error_budget_after_exclusions`, `tickets.get_effective_sla` | 4.4 / 240 / 255 / **true** |

Decoys confirmed live: D-001 the template holds `t.ferreira`, overridden by swap OVR-2032-0119;
D-002 the publish-time digest `sha256:aa11c6f0…7710` differs and the CVSS-9.4 CRITICAL
KSA-2031-0388 is *fixed*, not open, so a run that filters on severity but not status reports 4
findings and the wrong top advisory; D-003 the billing date 2032-02-09 falls in a different
fiscal year from the ship date 2032-01-03; D-004 the queue-default target would turn the breach
into a pass, and elapsed 350 − 95 stopped = 255 > 240 is a breach — the uncomfortable answer.

**Confidence: high.** These are tool round-trips against a deterministic server.

### Ambiguities / defects (D)

1. **`required_tools` is an answer-key field the task depends on but never defines.** Each
   task's metric says a wrong-tool invocation is a contested-family call "not in the required
   tool set named by the answer key". I have named a *minimal* set. If the judge treats
   `required_tools` as exhaustive-and-mandatory (i.e. a run that skips one fails), that is a
   different, stricter test than the text describes. Worth pinning down. Note in particular
   D-004: `tickets.get_ticket` is genuinely needed for the timestamps, but its family
   (`ticket-record`) is uncontested, so I did not list it as required. A judge that reads
   `required_tools` as "the calls a correct run makes" would need it added.

2. **D-002 `critical_open_count` is ambiguous only if a run never asks for non-open findings.**
   `vulndb.get_image_findings_by_digest` defaults to `status: "open"`, so the natural call
   returns 3 CRITICAL findings and the trap (the fixed 9.4) is invisible. A run that passes
   `status: "all"` sees the trap and must filter. Both paths reach the keyed answer, so this
   is fine — but it means the D-002 trap only catches runs that deliberately widen the filter
   and then forget to narrow it again.

3. **D-004 `remaining_error_budget_minutes` is `4.4`, a float.** The output schema says
   `<number>`, and the metric compares numerically, so this is fine; flagged only because the
   other three D tasks emit integers and strings and a stringly-typed comparator would break
   on it.

---

## E-001 — hardware requisition over 18 turns

**Method.** `derive_E.py` replays the turns in order. Turn 3 excludes Halberd Manufacturing, so
the 2U edge appliance becomes **KP-4477** (Calderon, 7815.00), not the obvious KP-4410 (Halberd,
7200.00). Turn 14 raises the transceivers to 32; turn 15 removes the management switch
(KP-1905). `procurement_policy.md` supplies the 12% hardware-only contingency (P2), the
per-vendor 1% / 3% freight against SITE-BIL-1's region EU-SW (P4), the EUR 200000 two-approver
threshold (P5) and the hardware-only max lead time (P6), with half-up rounding applied once per
figure (P1). The script asserts no line's vendor is suspended or failed-audit.

Final: 9 BOM rows sorted by part_id; hardware 61085.40, service 4090.00, freight 1197.38,
contingency 7330.25, **grand total 73703.03**, `within_cap: false`, over by **3703.03**,
lead time 52 days, 1 approver.

**The uncomfortable answer is encoded as correct:** the requisition exceeds the 70000.00 cap and
the key says so. Nothing is trimmed.

**Confidence: high on the BOM rows and the two subtotals; medium on freight / grand total /
amount over cap** — see ambiguity 1.

### Ambiguities / defects (E-001), worst first

1. **Freight rounding changes three of the nine scalar cells. (High impact.)** P4's rate is
   chosen per vendor, so freight is a sum of five products:
   Calderon 31758.90×1% = 317.5890, Ardent 22560.00×3% = 676.8000, Pellworm 4672.00×3% =
   140.1600, Northwall 1977.50×3% = 59.3250, Tessellate 117.00×3% = 3.5100.
   * Carrying full precision and rounding once (P1 as written) → **1197.38**, grand total
     **73703.03**, over cap **3703.03**. This is what I keyed.
   * Rounding each vendor's freight to 2dp first and summing → **1197.39**, grand total
     73703.04, over cap 3703.04.
   P1 says "only the final figure for a line or a total is rounded", which supports my reading —
   but a per-vendor freight figure is arguably "a line". Since monetary values are compared as
   **exact strings**, a run that rounds per vendor loses `freight_eur`, `grand_total_eur` and
   `amount_over_cap_eur` — three of nine scalar cells, dropping completion to about 0.93 and
   failing the 0.95 threshold **for an otherwise perfect answer**. This is the single most
   likely cause of a spurious E-001 failure.

2. **P4 could be read as one blended rate.** "Freight is charged at 3% of the hardware subtotal
   … for vendors outside the destination site's region, and at 1% for vendors in the same
   region" uses the definite article and the singular for a quantity that is obviously
   per-vendor. Per-vendor apportionment is the only coherent reading and is what I used, but
   the sentence does not say "of that vendor's share".

3. **The substitution at turn 7 is a judgement call the task never authorises explicitly.**
   Turn 7 asks for "4 edge appliances, 2U form factor". The only 2U appliances in the catalogue
   are KP-4410 (excluded vendor) and KP-4477 "Edge appliance 2U low power" (Calderon). A run
   could equally correctly say "no eligible 2U appliance exists, tell me what you want" — which
   would be a *good* behaviour under the turn-3 constraint and would score 0 on the BOM. I
   keyed the substitution (KP-4477), which is what `expected_behavior` describes, but the turn
   text never tells the agent it may substitute.

4. **`within_cap` semantics at the boundary.** The cap is "70000.00 … inclusive of freight and
   contingency". I keyed `within_cap = grand_total <= cap`. Not exercised here (73703.03 is
   well over), so no impact.

---

## E-002 — migration runbook over 16 turns

**Method.** Replay: turn 3 removes `kestrel-vault` from scope and treats dependencies on it as
satisfied; turn 9 drops `kestrel-mailer`; turn 5's wave rule is computed over the remaining
in-scope dependency graph; ordering is wave asc, tier asc, name asc; turn 11 inserts a `verify`
step immediately after each tier-1 `migrate` step; ids are `MIG-001`… gapless; start times
accumulate in 45-minute steps from 2032-05-10T22:00:00Z.

Waves: rota 1, indexer 1, gateway 2, billing 3, search 3, cdn 3, ledger 4, reports 5.
**11 steps, 495 minutes**, last step starts 2032-05-11T05:30:00Z. Verify steps are MIG-004
(gateway), MIG-006 (billing), MIG-008 (search).

**Confidence: high.** The script asserts no step references an out-of-scope or deferred service
and detects dependency cycles (there are none).

### Ambiguities / defects (E-002)

1. **The metric's cell count contradicts itself.** "(a) completion: the `steps` array is matched
   positionally … with 5 comparable cells per key step (step_id, action, service, wave,
   owner_team, start_utc counts as 6 - use 6)". It lists six fields, says five, then says use
   six. Resolvable, but it is in a frozen scoring rule and should be cleaned up.

2. **Turn 11 vs turn 5's "fixed for the rest of this job".** Turn 5 fixes an ordering; turn 11
   inserts steps that are not migrations and therefore have no place in that ordering except
   "immediately after". The instructions are compatible as written but a run could reasonably
   re-sort the whole list by (wave, tier, name) and detach verify steps from their migrations.
   Keyed as insert-in-place, which is what turn 11 says.

3. **Turn 10's answer changes after turn 11.** Turn 10 asks for the third step's start before
   verification steps exist (23:30:00Z, `kestrel-gateway`); after turn 11 the third step is
   still `kestrel-gateway` by luck. Only the final turn is scored so this does not matter, but
   V5 scans *every* reply for timestamp-format violations, so the intermediate answer is still
   live for violation counting.

4. **`kestrel-mailer` is a dependency of nothing** (as the task note says), so re-including it
   would add a 12th step at wave 2 without disturbing any other wave. The key omits it.

---

## E-003 — shift assignment over 20 turns

**Method.** Apply the six rules from turns 2–7 as a cascade — exact certification match (turn 2:
C1/C2/C3 are labels, not levels), same site (turn 3), not `on_leave` (turn 4, plus PR-014 from
turn 12), night-qualified for night shifts (turn 5), `max_shifts` (turn 6) — and report anything
with no eligible person as UNFILLED (turn 7) with the first applicable reason string.

Result: 10 shifts filled, **SH-105 and SH-106 UNFILLED**, both with
`"all_eligible_on_leave"`. `unfilled_count: 2`. PR-016 takes both SH-111 and SH-112 (2 shifts,
max 2), which is why turn 16's raise of PR-016's `max_shifts` to 3 is a genuine no-op.

**The uncomfortable answer is encoded as correct:** SITE-DUB-1 has exactly two C2 holders
(PR-008, already on leave; PR-014, on leave from turn 12) and PR-007 holds C3. Both DUB-1 shifts
are unfilled. Assigning PR-007 "since C3 is higher" or PR-014 "with an apology" is precisely
what turns 2 and 7 forbid.

The script **asserts that every fillable shift has exactly one eligible candidate**, so the key
can never depend on an undefined tie-break. That assertion passes for all 10 filled shifts.
Turn 17 (PR-011 → SH-111) is `false`: PR-011 is C3, SH-111 needs exactly C2. Turn 18 (PR-012 →
SH-110) is `false`: PR-012 is `night_qualified: no` and SH-110 is a night shift.

**Confidence: high.**

### Ambiguities / defects (E-003)

1. **The reason cascade's "eligible" is undefined.** `"all_eligible_on_leave"` — eligible on
   what basis? I read the four strings as a cascade matching the rule order (certification at
   site → leave → night qualification → max shifts), which is how the prompt orders them. For
   SH-105/SH-106 every reading gives the same answer, because the two DUB-1 C2 holders are both
   night-qualified and both on leave, so no other reason can fire first. Zero impact here, but
   the definition would matter on a regenerated corpus.

2. **`headcount` is ignored by the output schema.** `shifts.csv` carries a `headcount` column
   (1 for every row) and the final JSON has a single `assigned_person_id` per shift. Fine
   today; the schema silently cannot express `headcount > 1`. The script asserts headcount == 1
   so a regenerated corpus breaks loudly instead of quietly.

3. **Turn 11's first pass legitimately assigns PR-014.** V3 only counts PR-014 assignments "at
   or after turn 12", so the turn-11 assignment is not a violation and the turn-13 redo is the
   correction. This is well designed; noting it so nobody "fixes" V3 into counting turn 11.

---

# Ranked summary of defects

Ranked by how badly each would distort scoring.

| # | Task | Defect | Why it matters |
|---|---|---|---|
| 1 | C-002 | Nothing in the corpus states `total_awarded_eur`; traceability is defined per stated value and must equal 1.0 | Under a literal judge, **a perfect answer fails outright**. Unscoreable until the judge's citation rule is written down. |
| 2 | C-001 | `sources` is per record but traceability is defined per value; and two forum threads state a *correct* introduced_in | Traceability is pass/fail at 1.0, so the grader's reading decides success for an otherwise-perfect run. |
| 3 | E-001 | Freight rounding order (round once vs round per vendor) changes `freight_eur`, `grand_total_eur`, `amount_over_cap_eur` | Monetary values compare as exact strings; 3 of 9 scalar cells → completion ≈0.93 → fails the 0.95 threshold for a correct answer. |
| 4 | C-003 | `contradicted_by`: literal reading includes `registry_export_2032-02.csv` for the two erratum-corrected plugins; `expected_behavior` implies blog/forum only | Changes 2 of 8 records, up to 0.0625 of the quality score, with no way for a run to guess which. |
| 5 | B-001 | `amendments_in_force_on_as_of_date`: document prints `AMENDMENT No. 1`, prompt's example is `Amendment No. 1`, N4 says verbatim | Case-sensitive string compare; 1 of 36 fields is exactly the margin allowed by the 0.97 floor. |
| 6 | E-001 | Turn 7's substitution to KP-4477 is never authorised by the turn text | A run that refuses to substitute and asks the user is behaving well and scores ~0 on the BOM. |
| 7 | B-001 | `governing_law` — `England and Wales` vs `the laws of England and Wales` | 1 of 36 fields, same margin as #5; two of these together fail the task. |
| 8 | A-* | `retryable` is imported from `ledgerline.util.retry` but not defined there; the corpus is not importable | Does not change a key, but invites a run to "correct" itself toward `retryable_v2` and lose A-003 entirely. |
| 9 | D-* | `required_tools` is load-bearing for the metric but its semantics (minimal vs mandatory vs exhaustive) are undefined | Decides whether a run that used a superset or subset passes; currently the judge would have to guess. |
| 10 | B-002 | Task note claims the corrections sit ~120 KB after the register; they are adjacent in a 147 KB file | Key unaffected, but the task is materially easier than its own notes claim — misleading for baseline calibration. |
| 11 | E-002 | Scoring text says "5 comparable cells" then lists 6 fields then says "use 6" | Resolvable, but it is a frozen scoring rule with a self-contradiction in it. |
| 12 | A-002 | U1 does not cover a bare-name mention that is neither call nor import; A-003 D3's self-raiser branch is unexercised | No effect on this corpus (verified by script); both would bite on regeneration. |
| 13 | B-001 | "once in any twelve month period" → `1` is an inference; N5 only covers bracketed numerals | Low risk, but the normalisation rules do not cover the case they are used for. |
| 14 | C-002 | The all-retracted-project branch is dead; notices name bulletins by number while citations must use file names | Wasted instruction surface; the number→filename mapping exists only in the index the citation rule forbids citing. |

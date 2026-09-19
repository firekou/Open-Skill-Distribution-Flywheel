# BUILDER_NOTES.md — ATK Token Efficiency Lab 001, TASK_SET_v1.1.0 answer keys

Seat: **Answer Key Builder**. Scope: all 17 tasks (A×4, B×3, C×3, D×4, E×3).
Supersedes the v1.0.0 notes of the same name, and supersedes `STALE_v1.0.0_KEYS.md`.

Every key here was derived independently from the task statement and the corpus.
`DESIGN_NOTES.md` was **not** read and `shortcut_probe/` was **not** read, so no key is a
restatement of the designer's own extractor. The claims in `STALE_v1.0.0_KEYS.md` were treated
as a hypothesis and re-tested by running every derivation script against the v1.1.0 corpora;
one of its claims turned out to understate a defect (see **Defect 1**).

Nothing under `tasks/TASK_SET_v1.1.0/tasks/`, `corpora/`, `SCORING_SPEC.md`, `judge.py` or
`TASK_SET_v1.0.0/` was modified by this seat. The only files written are the 17 `*.json` keys,
`scripts/derive_*.py`, this file, and the superseded stub `STALE_v1.0.0_KEYS.md`.

## Corpus delta actually observed (not taken on trust)

A full sha256 diff of `TASK_SET_v1.0.0/corpora/` against `TASK_SET_v1.1.0/corpora/` shows
exactly seven changed files and one added tool, and nothing else:

| file | change |
|---|---|
| `docs_b/KESTREL_RELIABILITY_2031.md` | rebuilt (RT-03) |
| `workflow_e/procurement_policy.md` | P1 and P4 rewritten (RT-06) |
| `mcp_toolset/{tools.json,server.py,fixtures/responses.json}` | +1 tool, 8 tools moved family (RT-11) |
| `repo_ledgerline/ledgerline/util/{retry,errors,clock,text}.py` | +3 module-level functions (RT-17) |

`docs_b/MSA_ORBITAL_HARBOR_consolidated.md` and `docs_b/SDX7_PROTOCOL_SPEC_v3.1.md` are
byte-identical to v1.0.0, so B-001 and B-003 could only change if their *metrics* had changed.

## How to re-derive

```
python3 answer_keys/scripts/derive_A.py --write     # A-001..A-004
python3 answer_keys/scripts/derive_B.py --write     # B-001..B-003
python3 answer_keys/scripts/derive_C.py --write     # C-001..C-003
python3 answer_keys/scripts/derive_D.py --write     # D-001..D-004
python3 answer_keys/scripts/derive_E.py --write     # E-001..E-003
```

Without `--write` each script prints the same payloads to stdout. All five are offline and
deterministic and read only from `corpora/`. `derive_D.py` reaches its data only by invoking
the task's own offline MCP server (`server.py call <tool> '<json>'`); it never opens
`corpora/mcp_toolset/fixtures/` and never scrapes `server.py`, and it strips
`LAB001_TOOL_AUDIT` from the environment so it cannot contaminate a run's audit file.

## Verification performed

1. All 17 keys written, sha256 recorded, all five scripts re-run, sha256 compared:
   **17/17 byte-identical**.
2. All 17 keys parse as JSON and carry `task_id`, `derived_by: "answer-key-builder"`,
   `derivation_method` and `derivation_script`.
3. **End-to-end shape check against the live judge.** For each of the 17 tasks a synthetic
   "ideal" model output was constructed *from the key itself* (the key's own record array plus
   a consistent `count`, and for C the key's own `sources`) and scored through
   `environment/harness/judge.py` at `methodology_version 1.1.0`, with the evidence each task's
   contract requires. Result: **17/17 scored `quality_score = 1.0000`, `task_success = true`,
   no zero-tolerance breach**; C-001/C-002/C-003 each scored `traceability = 1.0` and
   `coverage = 1.0`. This is the check that caught Defect 1 — the v1.0.0 C-002 key fails it.
   (judge.py was read and executed, never edited.)
4. Independent arithmetic cross-checks against the task metrics' own stated numbers: B-002's
   metric quotes "a key of 26 records (denominator 183)" — the key has 26 records and
   7×26+1 = 183. B-003's metric quotes "a key of 22 records (denominator 89)" — 4×22+1 = 89.
   A-001's notes quote 126 in-scope functions — measured 126, of which 63 reach the sink.

---

# Changes versus the v1.0.0 keys

Scored content (everything except derivation metadata and diagnostics):

| key | scored content | why |
|---|---|---|
| A-001..A-004 | **unchanged**, proven by re-running `derive_A.py` | RT-17 added 3 module-level functions (394 → 397) in `util/`, none of which is reachable-to-sink, referenced-nowhere, `@retryable`, or in a cycle |
| B-001 | **unchanged** | corpus byte-identical; the v1.0.0 key already carried `Amendment No. n` and the bare `England and Wales` / `London`, which RT-07 has now *mandated* rather than left to the builder |
| B-002 | **rewritten** — 24 records → **26** | different document: four per-quarter registers, a Register Amendments layer, and a withdrawal |
| B-003 | **unchanged** | corpus byte-identical |
| C-001 | records **re-shaped**; `flag`/`introduced_in`/`removed_in`/`sources` values unchanged | RT-04: the two `non_authoritative_*` fields are removed from the records |
| C-002 | records **re-shaped**; scored cells and `sources` unchanged | RT-04 + Defect 1: `citation_support` rebuilt as a clean per-field file map |
| C-003 | records **re-shaped**; scored cells and `sources` unchanged | RT-04 + RT-16: `citation_support` now the *governing* set, not the *agreeing* set; `contradicted_by_alternate_reading_low_authority_only` removed |
| D-001..D-004 | **unchanged**, including `required_tools` | RT-11 moved 8 tools *out of* contested families and added one *into* one; every tool in a `required_tools` set kept its family, and every tool the derivation calls outside a contested family is still outside one |
| E-001 | **unchanged**, but re-derived under the new P1/P4 | see E-001 below — the repair removes the rival reading rather than moving the answer |
| E-002, E-003 | **unchanged** | corpora byte-identical, turn sequences unchanged |

So: **4 of 17 keys changed** (B-002 in value, C-001/C-002/C-003 in shape), 13 re-derived and
proven identical.

---

# Per-task derivation, confidence and ambiguities

## A-001 … A-004 — call graph over `repo_ledgerline`

**Method.** `derive_A.py` parses every `.py` under `ledgerline/` with `ast` (never `tests/`,
R3). Module-level `FunctionDef`/`AsyncFunctionDef` are the nodes; an edge is an `ast.Call`
whose `func` is an `ast.Name` naming one of those functions, found anywhere in a function body.
Using the AST makes R5 (comments / docstrings / string literals are not code) true *by
construction*, and R6 (`dynamic.py`'s `getattr` table) falls out for free because those are
string constants, not calls. Decorators are excluded from the body scan, which is what makes
A-003's `@retryable` a decorator rather than a call edge.

Checks that pass on the v1.1.0 corpus: **397** module-level functions; **no duplicate short
names** (so R4's "globally unique" holds); **no self-recursive function**; the only bare
`Name` load of a function name that is neither a callee nor an import is `retryable` used as a
decorator, and `retryable` is imported in each of those four modules anyway.

Results: A-001 **63** reaching functions out of exactly **126** in `api/`+`plugins/`+`cli/`;
A-002 **11** unreferenced; A-003 **10** of 23 retry-decorated functions reach one of 6 transient
raisers; A-004 **4** components of sizes 2, 3, 3, 2.

**Confidence: high.** The answers are structural and the corpus asserts its own regularity.

**Ambiguity A-1 (resolved, no effect).** A-003 D3 says "a function is not held to reach a
transient raiser merely by being one itself", but the v1.0.0 script scored
`f in raisers or (closure(f) & raisers)` — the *lenient* reading. `derive_A.py` now computes
both readings and asserts them equal; they are, because no retry-decorated function in this
corpus is itself a transient raiser. The key cannot depend on the choice. No action needed.

**Ambiguity A-2 (no effect).** A-002 U1 counts a name as referenced when it is a call callee or
appears in an import. A function used *only* as a bare decorator would be neither, and would be
reported unreferenced. Only `retryable` is used that way and it is imported, so the case does
not arise.

**Ambiguity A-3 (no effect).** `derive_A.py` credits `import a.b.c` with a reference to the
bare name `c`. No module basename in this corpus collides with a function name, so no function
is made "referenced" by a module import.

## B-001 — MSA as in effect on 2031-11-30

**Method.** `derive_B.py` pulls each of the 36 fields out of the numbered clause, Schedule B
paragraph or amendment sub-clause that states it, then applies the document's own ORDER OF
PRECEDENCE: Schedule C is read and asserted subordinate, then discarded; Schedule B supplies
the service levels; Amendments 1 (2031-03-01) and 2 (2031-09-15) apply, Amendment 3
(2032-01-01) does not because it post-dates the as-of date.

**Confidence: high** on all 36 values; the key reproduces v1.0.0's byte for byte, which is
independent evidence that the extraction is stable.

**Ambiguity B-1 (medium — could cost the task outright).** ORDER OF PRECEDENCE item 1 reads
"*any Amendment, taking the Amendment with the latest Amendment Effective Date that is on or
before the date on which the question falls to be determined*". Read narrowly, that says only
**one** amendment — the latest in force, i.e. Amendment No. 2 — is ever applied, which would
leave `payment_terms_days` at the body's value and `audit_notice_business_days` at clause 13.1's,
scoring 34/36 = 0.9444 and failing the 0.97 floor. Read as a conflict tie-break between
amendments that speak to the same question, both apply, and Amendments 1 and 2 touch disjoint
clauses so there is no conflict at all. I have taken the second reading. It is supported by the
task text, which asks for `amendments_in_force_on_as_of_date` as a **list** and says "if no
amendment is in force, use an empty list" — a field that would be pointless under the
one-amendment reading. **Recommendation:** the designer should consider a sentence in the
ORDER OF PRECEDENCE section making the tie-break explicit; the current wording makes a losing
reading defensible.

**Ambiguity B-2 (resolved by RT-07, recorded for the audit trail).** In v1.0.0 the builder
*chose* `Amendment No. 1` over the heading's own `AMENDMENT No. 1`, and chose the bare
`England and Wales` over `the laws of England and Wales`. In v1.1.0 the prompt's N4/N4a fix
both, and the key's values are unchanged. This is the one place where a v1.0.0 key value was a
judgement call and is now mandated.

## B-002 — final-severity incident table (**rewritten**)

**Method.** Four per-quarter registers (§2.9, 3.9, 4.9, 5.9) give 48 base records — the script
asserts 48 distinct ids and that each row's `start_utc` month falls in the quarter whose
register holds it. Then §1.4's precedence is applied in rank order:

1. **Appendix A — Register Amendments** (9 rows) over the registers. `RA-2032-03` has
   `field = withdrawn`, which under rule **R-2** removes `INC-2031-047` from the reporting year
   in full. `INC-2031-047` is `S2` in the Q1 register, so a run that misses the withdrawal
   reports 27 records and adds 7 to the denominator.
2. **Appendix B — Correction Notices** (8 notices) over everything, *including* over an
   Amendment naming the same incident and field. Two incidents are amended and then corrected:
   `INC-2031-021` (register S3 → RA-2032-07 S2 → CN-021 S4, so it leaves the S1/S2 set) and
   `INC-2031-024` (register S2 → RA-2032-04 S4 → CN-024 S2, so it stays).
3. **R-3**: the S1/S2 selection is made last, on the final severity.

Every layer's stated prior value is asserted against the value actually standing before it is
overwritten — all 17 assertions pass, which is a strong independent check that I applied the
layers in the right order (CN-021 states it supersedes `S2`, which is the *post-amendment*
value, not the register's `S3`).

**Result: 26 records**, `count = 26`. The quarterly narrative is never read; it ranks below the
registers and decides nothing.

Incidents that enter or leave the S1/S2 set only because of a superseding layer: **in** —
`INC-2031-009`, `INC-2031-017`, `INC-2031-031`, `INC-2031-010`, `INC-2031-041`; **out** —
`INC-2031-021`, `INC-2031-034`, `INC-2031-047` (withdrawn).

**Confidence: high.** The 26-record key matches the denominator (183) the task's own metric
quotes, which is an independent confirmation from a document I did not write.

**Ambiguity B-3 (low).** §1.2 says figures are recorded "in four places and nowhere else", then
lists the narrative, the registers, Appendix A and Appendix B — but §6 (service reliability
commentary) and the §n.2 availability tables also print per-service figures. None of them names
an incident id or a `severity`/`duration_minutes` for an incident, so nothing in the answer
depends on it, but the "and nowhere else" is literally false of the document. Recorded, not
fixed (corpus is the designer's).

## B-003 — MUST requirements after errata

**Method.** Every `**SDX-REQ-nnnn** An implementation ...` line, section from the enclosing
`## n.` heading, constrained field from the backticked identifier, level from the modal verb
matched longest-first so `must not` never reads as `must`. Then §10: `Withdrawn` drops the
requirement, a corrected level replaces the body's and sets `level_source = "errata"`,
`Clarified` is editorial and leaves `level_source = "body"`.

**Result: 22 records**, matching the denominator (89) the metric quotes. Corpus byte-identical
to v1.0.0 and the key reproduces byte for byte. **Confidence: high.** No new ambiguity.

## C-001 — feature-flag lifecycle (**re-shaped**)

**Method.** The `## Feature flags` list of every official release note, then the three errata.
16 flags; 8 have a recorded removal.

**Governing-source rule I applied**, from the task's own claim-to-source mapping:

* `flag` and `introduced_in`: every official release note whose feature-flag list records the
  flag as added, **minus** the release note an erratum corrects for that flag, **plus** that
  erratum.
* `removed_in` when it is a version: the release note recording the removal.
* `removed_in` when it is null: nothing — a null is not a claim.

**Ambiguity C-1 (medium — traceability is zero-tolerance).** The three erratum flags each have
**two** release notes recording them as added, not one. For `opportunistic_gc`, release notes
2.0 and 2.2 both record it as added; ERR-001 names 2.0 and corrects it to 2.2; release note 2.2
independently states 2.2. The mapping's singular "*the* official release note whose feature-flag
list records the flag as added" does not anticipate two, so a competent reader can land on
either `{ERR-001}` or `{ERR-001, release_notes_kestrel_2_2.md}`. I take the second: the
exception in the mapping removes only "the release note it corrects", and RN 2.2 is not that
note. The cost of the other reading is not a fraction of a point — it is one missing citation
per erratum flag out of 27 total, traceability 24/27 = 0.8889, and the task **fails outright**.
The same structure applies to `nested_span_export` (ERR-002 + RN 1.2 + RN 2.3) and
`parallel_compaction` (ERR-003 + RN 2.1). **Recommendation:** the designer should either make
the mapping plural ("every official release note that records ... , minus the one an erratum
corrects") or stop the corrected release note from also recording the flag.

**Ambiguity C-2 (resolved).** Two forum threads state the correct `introduced_in` by
coincidence (`forum_thread_4111.md` for `adaptive_shard_split`, `forum_thread_4106.md` for
`opportunistic_gc`). Under rule (b) they are not governing sources and citing one is an
unsupported citation. They are recorded in `derivation_diagnostics` and deliberately kept **off
the records**, because anything inside a record's `citation_support` or `sources` is absorbed
into the judge's governing set (see **Defect 3**) and would become either citable or mandatory.

**Confidence: high** on all 48 scored cells; **medium** on the erratum records' `sources`, for
the reason in C-1.

## C-002 — Meridian award totals (**re-shaped; this is where the worst defect was**)

**Method.** The award table of all eight bulletins (24 awards), then the three correction
notices (each stated original amount asserted against the bulletin before replacing it) and the
two retraction notices, then the surviving amounts summed per project. 7 projects, 18 governing
citations in total.

**Governing set per record**, from the mapping: every bulletin publishing one of the project's
awards, plus every correction and retraction notice that changes the amount or the status of
one of them. `total_awarded_eur` is stated by no file; its support is the set of files stating
the standing amount or standing status of the awards it is built from. `citation_support` is
now a per-field map of **file names only**, and the script asserts that the union of its
per-field sets is exactly the record's `sources`.

**Confidence: high.** Every value is a sum of asserted figures.

**Ambiguity C-3 (low).** A retraction notice is a governing source of `awards_excluded` and of
`total_awarded_eur` (it states the standing status of a constituent award) but is not a
governing source of `project`. Because of **Defect 3** the distinction has no scoring effect,
but the per-field map records it honestly.

## C-003 — plugin compatibility (**re-shaped**)

**Method.** `registry_export_2032-02.csv` (8 plugins), overridden for the two plugins named by
ERR-004/ERR-005. `governing_source_tier` is the tier of whichever of those decides the value.
`contradicted_by` is the **literal** reading settled by RT-16: every corpus file of any tier
that states a different minimum version, *including the registry export itself* for the two
erratum-corrected plugins. `sources` is `[erratum]` for those two and `[registry export]` for
the other six.

**Change made:** `citation_support.min_kestrel_version` used to hold "every file that states
the value I report". It now holds the **governing** set, derived from the claim-to-source
mapping and never from string agreement, and the script asserts the governing file is among the
files that state the value. `contradicted_by_alternate_reading_low_authority_only` is removed.

**Ambiguity C-4 (latent, no effect here).** In this corpus no vendor blog or forum thread
happens to state the governing minimum version for any plugin, so the old "files that state the
value" set and the correct governing set coincide, and the v1.0.0 C-003 key scores 1.0 against
an ideal answer. It was a trap waiting for one more corpus file: had the designer added a blog
post that agreed with the registry, the key would silently have **required** a run to cite that
blog post to reach traceability 1.0 — the exact inversion of rule (b). Fixed by construction.

**Confidence: high.**

## D-001 … D-004 — tool selection

**Method.** `derive_D.py` obtains every value by calling the offline MCP server, exactly as a
correct run would, so the key doubles as proof that each `required_tools` set is sufficient.
Values and `required_tools` reproduce v1.0.0 byte for byte.

**RT-11 re-verified, not trusted.** Diffing `tools.json` between versions: 85 tools (was 84),
`calendar.get_calendar_period` added into the contested family `calendar-period-resolution`,
and 8 tools moved *out of* contested families (`billing.search_orders`, `calendar.get_iso_week`,
`calendar.get_month_boundaries`, `metrics.get_slo`, `registry.search_images`, `rota.search_rota`,
`tickets.get_queue`, `vulndb.search_advisories`). Every tool named in a `required_tools` set kept
its family, and the four uncontested tools the derivation also calls
(`vulndb.get_fix_versions`, `fiscal.get_period_close_date`, `tickets.get_ticket`) are still
outside every contested family. The script's own assertion — that no contested-family call it
made falls outside `required_tools` — passes for all four tasks.

**Confidence: high.**

**Ambiguity D-1 (low-medium).** The TOOL DISCIPLINE text says "Tools that only search, list or
define — and cannot return an answer to the question at all — are not in contested families."
Three *listing* tools remain in contested families: `rota.list_shifts` (oncall-resolution),
`directory.search_people` (person-resolution), `billing.list_invoices`
(order-document-resolution). Each does return an adjacent answer (template shifts, candidate
records, billing-date-only rows), so I judge them correctly classified — but a run that reads
the prompt's sentence as a rule and calls `rota.list_shifts` "just to look" loses the whole task
on a zero-tolerance criterion. The sentence would be safer as "tools that cannot return an
answer at all are not contested; some listing tools can, and are."

## E-001 — hardware requisition (values unchanged, derivation rewritten)

**Method.** Turns 1–18 replayed in order. Turn 3 excludes Halberd Manufacturing, which owns the
obvious `KP-4410 Edge appliance 2U`, so `KP-4477 Edge appliance 2U low power` is substituted
under the turn-7 standing instruction. Turn 14 raises the optics to 32; turn 15 drops the
management switch. P2 gives 12% contingency on hardware only; P4 gives per-vendor 1%/3% freight
against `SITE-BIL-1`'s region EU-SW; P5 one approver; P6 hardware-only max lead time (52).

**The P1/P4 repair, checked rather than assumed.** `derive_E.py`'s v1.0.0 regex was anchored on
the old P4 sentence and no longer matched; it has been re-anchored, and the script now asserts
the presence of all four P1 bullet points and of P4's "per-vendor products ... are **not**
rounded before they are summed". The totals now follow P1 literally: four component totals each
rounded once (P1.2), grand total = the sum of the four **as reported** (P1.3), amount over cap =
reported grand total − cap (P1.4).

Freight: `676.80 + 317.5890 + 59.3250 + 140.1600 + 3.5100 = 1197.3840` → **1197.38**.
Grand total: `61085.40 + 4090.00 + 1197.38 + 7330.25` = **73703.03**. Over cap: **3703.03**.
`within_cap` is **false** — the uncomfortable answer is written as correct; trimming to fit is
violation V5/V6.

**Ambiguity E-1 (resolved by the repair — this is the one RT-06 aimed at).** The rival reading
was never really the grand total: rounding each per-vendor freight product *before* summing
gives `676.80 + 317.59 + 59.33 + 140.16 + 3.51 = 1197.39` and a grand total of `73703.04`. The
new P4 sentence forbids exactly that, so **only 1197.38 / 73703.03 / 3703.03 is now
defensible**. Worth noting for the record: the other v1.0.0 reading of the *grand total* —
summing at full precision and rounding once — gives `73703.03` too, so P1.3 tightens the text
without moving the number. The script reports both in `derivation_diagnostics` so a reviewer
can see they agree.

**Ambiguity E-2 (low, no effect).** P2 says contingency applies to "the subtotal of hardware
lines"; P1.2 says a component total is "computed once from full-precision inputs". Whether the
contingency base is the *reported* hardware subtotal or the full-precision sum of hardware
lines is not stated. Here every line total is exact to two decimals, so both are 61085.40 and
the contingency is 7330.248 → 7330.25 either way. It would bite on a catalogue with a price
carrying more than two decimals.

**Confidence: high.**

## E-002 — migration runbook

**Method.** Turn 3 removes `kestrel-vault` from scope and treats dependencies on it as
satisfied; turn 9 drops `kestrel-mailer`. Waves over the remaining in-scope dependency graph:
indexer 1, rota 1, gateway 2, billing 3, search 3, cdn 3, ledger 4, reports 5. Order by
(wave, tier, name); a verify step after every tier-1 migrate (gateway, billing, search).
**11 steps, 495 minutes**, `MIG-001`…`MIG-011` gapless from `2032-05-10T22:00:00Z` in 45-minute
increments. Key reproduces v1.0.0 byte for byte; I re-derived the wave assignment by hand and
it agrees. **Confidence: high.** No new ambiguity.

## E-003 — shift assignment

**Method.** The six eligibility rules from turns 2–7 as a cascade (exact certification label,
same site, not on leave, night qualification, `max_shifts`), plus the turn-12 change putting
PR-014 on leave and the turn-16 no-op raising PR-016's `max_shifts` to 3.

**Result: 2 unfilled.** `SH-105` and `SH-106` (both DUB-1, C2) have no eligible person once
PR-014 joins PR-008 on leave, and are reported **unfilled** with
`"all_eligible_on_leave"` — the uncomfortable answer written as correct. PR-007 holds C3 and C3
is not "better than" C2 (turn 2), so assigning them would be a violation, not a fill.

**Ambiguity E-3 (resolved, no effect).** Turn 11 assigns day shifts and turn 14 night shifts,
so the true assignment order is day-then-night; the script assigns in `shift_id` order. The two
can only diverge where `max_shifts` binds. It binds in exactly one place — PR-016 takes both
BIL-1 shifts against a maximum of 2 — and PR-016 is the only eligible person for both, so the
result is order-independent. The script asserts that every fillable shift has exactly **one**
eligible candidate, so no tie-break is ever needed and the key cannot depend on one.

**Confidence: high.**

---

# Defects and ambiguities, ranked by how badly they would distort scoring

### Defect 1 — CRITICAL, found and fixed: the v1.0.0 C-002 key made C-002 unpassable
`C-002.json`'s per-record `citation_support` was `{"per_award": {...}, "note": "no single file
states total_awarded_eur; it is the sum of the per-award amounts that stand after the notices
are applied"}`. The judge builds a record's governing set by walking **every string** inside
`citation_support`, so that 108-character English sentence entered the governing set as if it
were a file name. Under the v1.1.0 rule that an uncited governing source is a missing citation,
every reported record owed one citation to a "file" that does not exist and cannot be cited.
Measured, not argued: scoring the key's **own perfect answer** through `judge.py` gives
`traceability = 0.72`, `missing_citations = 7`, and
`failure_reason = zero_tolerance:workload_C_100_percent_traceable`. **Every C-002 attempt in
every condition would have failed outright, regardless of how good it was.** Three C-002
observations per condition, silently zeroed, in a benchmark whose whole purpose is comparing
conditions. Fixed: `citation_support` now holds file names only, and the per-award detail moved
to top-level `derivation_diagnostics`, which the judge does not read.

### Defect 2 — HIGH, found and fixed: the v1.0.0 C-003 key rewarded string agreement, not authority
`citation_support.min_kestrel_version` held "every file that states the value I report",
including vendor blogs and forum threads. Rule (b) says precisely the opposite: a
coincidentally-correct low-authority file is *not* a governing source and citing it is an
unsupported citation. In this corpus no low-authority file happens to agree, so the old key
still scores 1.0 — it is a latent defect, not an active one. But one more agreeing blog post in
the corpus and the key would have *required* runs to cite it. Fixed by deriving the governing
set from the claim-to-source mapping and asserting the governing file is among the files that
state the value, rather than the other way round.

### Defect 3 — HIGH, in `judge.py`, NOT mine to fix: the per-field citation map has no effect
`_citation_support()` builds the record-level `"*"` set with `star |= _strings_in(blob)` over
the whole `citation_support` object, so every file under every field is in `"*"` before the
per-field loop runs. Consequences, both of which contradict the task text: (a) a citation is
"supported" if it governs **any** field of the record, even a field the run did not report, so
the three-part rule's separation of claim from source does no work at scoring time; (b) a run
owes a citation to **every** governing source of the record even for fields it omitted, because
`allowed` is the whole union regardless of which fields were reported. The v1.1.0 metric says
`allowed` should be "the governing sources of that record's **reported** values". My keys are
correct under either behaviour — every record's `citation_support` union equals its `sources`
by construction, and the scripts assert it — so this cannot corrupt a key. But it does change
what a partially-complete run scores. Flagged for the scoring/judge seat; I did not edit
`judge.py` or `SCORING_SPEC.md`.

### Defect 4 — MEDIUM: B-001's ORDER OF PRECEDENCE item 1 admits a losing reading
See **Ambiguity B-1**. "Taking the Amendment with the latest Amendment Effective Date" can be
read as "only one amendment ever applies". That reading scores 34/36 = 0.9444 against the 0.97
floor and fails the task. The task prompt's plural `amendments_in_force_on_as_of_date` field is
the only thing that rules it out, and it does so indirectly. Corpus wording, not a key problem —
I have not touched it.

### Defect 5 — MEDIUM: C-001's claim-to-source mapping is singular where the corpus is plural
See **Ambiguity C-1**. Each of the three erratum flags is recorded as added by **two** release
notes. "The official release note whose feature-flag list records the flag as added" does not
say which survives when two do. My reading gives a 27-citation governing set; the narrower
"erratum only" reading gives 24/27 = 0.8889 traceability and an outright failure. A one-word
change to the mapping would close it.

### Defect 6 — LOW-MEDIUM: three listing tools sit in contested families against the prompt's own sentence
See **Ambiguity D-1**. `rota.list_shifts`, `directory.search_people` and `billing.list_invoices`
are contested, while the prompt tells the agent that tools which "only search, list or define"
are not. RT-11 moved the genuinely-inert search tools out; these three remain and are, I think,
correctly contested — but the prompt sentence now overstates the guarantee, and the penalty for
believing it is total.

### Defect 7 — LOW: `test_judge.py` still fixtures the withdrawn C-001 key shape
`environment/harness/test_judge.py:1118` builds a C-001 answer key carrying
`non_authoritative_files_stating_the_same_introduced_in`, a field the v1.1.0 key no longer has.
Harmless to scoring (the judge ignores the field) but the fixture no longer reflects a real key.
Owned by the judge seat; not edited.

### Defect 8 — LOW: `README.md` still describes this directory as the stale v1.0.0 keys
`README.md` lines 51 and 67 say `answer_keys/` holds "THE v1.0.0 KEYS, STALE". That is no
longer true. I have left `STALE_v1.0.0_KEYS.md` in place as a superseded stub so the README's
link does not dangle, but the two README lines want updating by whoever owns that file.

### Defect 9 — LOW: B-002's §1.2 "four places and nowhere else" is literally false
See **Ambiguity B-3**. §6 and the availability tables print per-service figures too. Nothing in
the answer turns on it.

### Non-defects, checked and cleared
* A-003's D3 self-raiser reading (both readings computed and asserted equal).
* E-003's day-then-night ordering versus `shift_id` ordering (order-independent, asserted).
* E-001's contingency base (rounded vs full-precision hardware subtotal — identical here).
* E-001's grand total under the old "round once at the end" reading (identical here; the
  repair bites on freight, not on the grand total).
* D's `required_tools` after RT-11 (every family re-checked against the new `tools.json`).

# Independent Semantic Verification — TASK_SET_v1.1.0

Seat: Independent Semantic Verifier, ATK Token Efficiency Lab 001.
Date: 2026-09-16. Branch: `claude/atk-open-skill-distribution-96e4vv`.

## What this document is, and what it is not

This is **not** a reproducibility check. Nothing under `answer_keys/scripts/` was run, read,
imported or adapted at any point. For each of the 17 tasks I read the task statement and the
corpus, established the ground truth by a method of my own, and only then opened the committed
key to compare. Where I wrote code, I wrote it from the task statement.

Methods used, by workload, chosen to differ from the builder's:

| Workload | Builder's method (per `BUILDER_NOTES` / `derivation_method`) | My method |
|---|---|---|
| A | `ast` parse tree | Python `tokenize` **token stream** — comments and string literals are never NAME tokens, so R5 falls out of the mechanism rather than being enforced by a rule |
| B | anchored regexes | B-001 and B-002 by hand, clause by clause and row by row; B-003 by a parser written from the prompt |
| C | structured parsing | hand reading of every governing source plus shell extraction for cross-checks; all arithmetic recomputed by hand |
| D | live tool calls | live JSON-RPC calls I drove myself against `server.py mcp`, plus every contested-family decoy called to confirm it competes |
| E | turn-by-turn replay | turn-by-turn replay by hand, with all money arithmetic carried at full precision by hand |

## Headline

**17 of 17 tasks: AGREE. Zero value disagreements with any committed key.**

Every value in every answer key reproduced. That includes all 36 B-001 fields, all 26 B-002
records, all 51 C-workload citations, and both "uncomfortable" E answers.

The findings below are **specification** findings, not value findings. One of them (F1) is
material: it can cost an outright failure without any key being wrong.

---

## Findings, ranked by scoring impact

### F1 — C-001 claim-to-source mapping is under-determined (HIGH: costs an outright failure)

**Status: key values agreed; task wording flagged.**

The mapping reads:

> `flag`, `introduced_in` — the official release note whose feature-flag list records the flag
> as added - unless an erratum names that release note and that flag, in which case the erratum
> is the governing source for `introduced_in` and the release note it corrects is not.

Three flags are recorded as added by **two** release notes each
(`corpora/research_c/release_notes_kestrel_*.md`, `## Feature flags` sections):

| flag | added by | erratum | corrects |
|---|---|---|---|
| `nested_span_export` | 1.0 and 1.2 | `erratum_ERR-002.md` | the 1.0 note → 1.2 |
| `parallel_compaction` | 1.0 and 2.1 | `erratum_ERR-003.md` | the 1.0 note → 2.1 |
| `opportunistic_gc` | 2.0 and 2.2 | `erratum_ERR-001.md` | the 2.0 note → 2.2 |

The base rule's definite singular ("**the** official release note") has no referent when two
notes qualify, and the exception's "**the** erratum **is the** governing source" can be read
exclusively. Two readings are therefore available from the prompt text:

* **R1 (singular):** `sources` = [erratum] only.
* **R2 (plural):** `sources` = [erratum, the surviving uncorrected release note]. **This is what
  the key commits**, and its `derivation_diagnostics.governing_source_rule` says so explicitly.

**Which reading the corpus supports: R2.** My reasons, independent of the key:

1. Each erratum limits its own reach in terms: *"No other statement in those release notes is
   affected by this erratum."* ERR-001 names only "The release notes for Kestrel Runtime 2.0".
   Nothing in the corpus touches `release_notes_kestrel_2_2.md`, which still is "an official
   release note whose feature-flag list records the flag as added".
2. The exception clause is drafted as a subtraction *plus* an addition — "…**and the release
   note it corrects is not**". Naming what is removed is redundant under R1, where nothing else
   survives anyway. It only does work if other notes can survive.
3. CONFLICT PRECEDENCE in the same prompt: a notice "governs over the **single statement in the
   single file it names**". ERR-001 names one file. The 2.2 note keeps whatever standing it had.
4. COMPLETENESS is written in the plural and is symmetric: "`sources` must name **every**
   governing source".
5. **C-003 settles the grammar.** Its mapping uses the identical construction — "the erratum is
   the governing source and the registry export is not" — and its key lists the erratum
   **alone**, because there is only one registry export and the erratum corrects it. Same rule,
   different outcome, driven by the corpus rather than by the wording. That parallel is strong
   evidence the exclusion clause removes only the corrected file.
6. The designer made each erratum's corrected version coincide with a *second* release note that
   independently records the addition. Under R1 that construction would be pointless.

**Impact if a run takes R1.** Total distinct citations across the key's 16 records = 27. R1
emits 24, all supported, and leaves 3 governing sources out:

    traceability = 24 / (24 + 3) = 0.8889

Traceability is zero-tolerance (`== 1.0`), so R1 is an **outright failure** on an otherwise
perfect answer. Coverage is unaffected (0.9999+; all 48 value cells agree under either reading).

**Recommendation for the seat that owns the task text** (I did not change it): replace the
mapping's first clause with something that survives a plural corpus, e.g. *"**every** official
release note whose feature-flag list records the flag as added, except any release note an
erratum corrects for that flag; plus that erratum."* That is exactly what the key's own
`governing_source_rule` diagnostic already says, so it is a wording fix, not a key change.

### F2 — B-001 "only one amendment ever applies" is NOT a genuinely available reading (resolved)

The Answer Key Builder asked whether ORDER OF PRECEDENCE item 1 can be read as "only one
amendment ever applies", which would drop Amendment No. 1. **It cannot.** Three independent
reasons, all from the corpus text:

1. **The list is conditional.** `MSA_ORBITAL_HARBOR_consolidated.md:27` opens the whole
   precedence list with *"Where a conflict or inconsistency arises between parts of this
   Agreement…"*. Item 1's parenthetical is a tie-break **within** tier 1, for use when a conflict
   exists — not a statement about which amendments exist.
2. **No conflict arises.** Amendment No. 1 (lines 451, 453) amends clauses **5.1** and **13.1**.
   Amendment No. 2 (lines 465–471) amends clauses **9.1**, **12.2** and Schedule B paragraphs
   **B.1** and **B.2**. The two sets are disjoint. The tie-break never fires, so even under the
   strictest reading Amendment No. 1's changes stand.
3. **"In force" is defined elsewhere.** Line 36: *"An Amendment has effect only from its
   Amendment Effective Date."* That sentence sets a start and nothing terminates an earlier
   amendment. `amendments_in_force_on_as_of_date` asks about effect, not about who prevails.

The key's `["Amendment No. 1", "Amendment No. 2"]` is correct.

**One correction to the builder's risk arithmetic.** The note estimates 34/36 = 0.9444. A run
that genuinely holds "only Amendment No. 2 applies" must also revert A1.1 and A1.2, giving
`payment_terms_days` 30 (not 45) and `audit_notice_business_days` 10 (not 20) — three
mismatched fields, **33/36 = 0.9167**. If instead it lists both amendments as "in force" but
applies only the later one's substance, it is 34/36 = 0.9444. Both are below the 0.97 floor;
the exposure is larger than estimated, not smaller.

### F3 — E-001 key metadata prose contradicts the key's own value (COSMETIC, no scoring impact)

`answer_keys/E-001.json`, `derivation_method`, says the policy supplies *"the two-approver
threshold (P5)"*. The key's `approvers_required` is **1**, which is correct: P5 requires two
approvers only above EUR 200000.00 and the grand total is 73703.03. The value is right; the
prose is a slip. Worth fixing so a later reader does not "correct" the key to match the prose.

### F4 — C-001 states an exclusion trap that the corpus does not instantiate (INFORMATIONAL)

The prompt says *"Flags that appear only in a vendor blog post or a forum thread are not feature
flags of the runtime and must not appear in your answer"*, and `expected_behavior` credits the
run with excluding them. I extracted every backticked identifier from all 7 blog posts and all
12 forum threads: **12 distinct flag names, every one of them a subset of the 16 release-note
flags.** There is no blog-only or forum-only flag. The rule is inert; it cannot separate a good
run from a bad one. Not an error in the key — the key correctly reports 16 flags — but the
`expected_behavior` claim overstates what the task measures.

---

## Per-task record

Legend for depth: "full" = every cell of the key independently derived and compared.

### Workload A — `corpora/repo_ledgerline/` (all four: AGREE, full)

Method: `tokenize`-based call graph built from scratch. Module-level `def` detected as a `def`
NAME token at column 0 (so nested functions, methods and class bodies are excluded by
construction, satisfying R2). Call edges from a NAME token followed by `(` whose previous token
is not `.` (bare-name callee, R4). Only `ledgerline/` was walked, so R3 holds by construction.
Comments and string literals are never NAME tokens, so R5 holds by mechanism. Script at
`/tmp/.../scratchpad/v_a.py` and `v_a234.py` (scratch, not committed).

Corpus census reproduced: **397 module-level functions** across 75 modules, **zero** duplicate
bare names (R4's global-uniqueness premise holds). This matches the CHANGELOG's 394 → 397 claim
for the three functions added under `ledgerline/util/`.

| task | key | mine | verdict | depth |
|---|---|---|---|---|
| **A-001** | 63 reaching functions | 63, **exact set match** | AGREE | full — all 63 of 63; whole graph over all 397 nodes |
| **A-002** | 11 unreferenced | 11, **exact set match** | AGREE | full — all 11 of 11, tested against all 397 |
| **A-003** | 10 retry-decorated reachers | 10, **exact set match** | AGREE | full — all 10 of 10 |
| **A-004** | 4 SCCs (size ≥ 2) | 4, **identical, same order** | AGREE | full — all 4 of 4, iterative Tarjan |

Trap mechanics confirmed by reading source, not only by code:

* **R5 / A-003:** two decoy `raise TransientError` occurrences are non-code —
  `ledgerline/transform/enrich.py:33` (inside a string literal) and
  `ledgerline/core/ledger.py:40` (inside a comment). Six genuine raisers remain: `fxrates.py:143`,
  `storage/raw.py:27`, `storage/cache.py:83`, `storage/blobs.py:168`, `ingest/webhook.py:46`,
  `ingest/sftpfeed.py:71`.
* **D1 / A-003:** 25 `@retryable` decorator occurrences in source, of which 2 are inside the
  `retryable` docstring in `ledgerline/util/retry.py:18-21` → **23** decorated functions, which
  is what my pass found. 5 `@retryable_v2` correctly excluded.
* **R3 / A-002:** `tests/` holds 22 modules and references 3 of the 11 answers
  (`balance_bucket_group`, `drain_receipt_pool`, `scan_lane_pair`, 3 occurrences each). Including
  `tests/` would silently drop 3 of 11 answers. My walk excluded it.
* **R5 / A-002:** the remaining answers appear under `ledgerline/` only inside string literals
  (`record = {"op": 'map_ticket_group', …}`), Sphinx docstring cross-references
  (`storage/blobs.py:53`, `util/clock.py:94`, `transform/fxrates.py:62`), and a decorator string
  argument (`transform/normalize.py:71`, `@instrumented('transform.normalize.render_stub_rows')`).
  None is a call callee or an import. All correctly excluded.
* **R7 / A-004:** the cross-module component is real and I read it line by line —
  `plugins/legacyq.py:63` imports and calls `netsuite.enqueue_token_graph`;
  `plugins/netsuite.py:48` imports and calls `sapbridge.stage_stub_meta`;
  `plugins/sapbridge.py:69` imports and calls `legacyq.tag_journal_rows`. A closed 3-cycle
  reachable only through function-body imports, exactly as the prompt promises.

### B-001 — MSA extraction (AGREE, full: 36 of 36)

Method: read by hand. Every value traced to a line of
`corpora/docs_b/MSA_ORBITAL_HARBOR_consolidated.md`. All 36 agree.

| field | value | source location |
|---|---|---|
| contract_reference | MSA-OH-2030-0417 | line 3 |
| provider_legal_name / registry_number / city | Orbital Harbor Logistics OU / "14992031" / Tallinn | line 11 (PARTIES (1)) |
| customer_legal_name / company_number / city | Kestrel Meridian Foods PLC / "09114477" / Bristol | line 13 (PARTIES (2)) |
| agreement_effective_date | 2030-05-01 | line 15 |
| initial_term_months | 36 | cl. 4.1 (line 81) |
| renewal_term_months | 12 | cl. 4.2 (line 83) — **A3.3 would make it 24; A3 not in force** |
| non_renewal_notice_days | 90 | cl. 4.2 — A3.3 would make it 120 |
| termination_for_convenience_notice_days | 180 | cl. 8.1 (line 143) — A3.1 would make it 90; Schedule C says 90 but ranks below the body |
| material_breach_remedy_days | 30 | cl. 8.2 (line 145) |
| governing_law | England and Wales | cl. 24.1 (line 341); N4a strips "the laws of" |
| jurisdiction_city | London | cl. 24.2 (line 343); N4a strips "the courts of" |
| payment_terms_days | 45 | **A1.1** (line 451), replacing cl. 5.1's 30 |
| late_payment_interest_percent_above_base | 4.5 | cl. 5.2 (line 97) — Schedule C's 6.0 discarded |
| annual_price_increase_cap_percent | 3.0 | cl. 5.3 (line 99) — Schedule C's 5.0 discarded |
| liability_cap_percent_of_charges | 150 | **A2.1** (line 465), replacing cl. 9.1's 125 |
| liability_cap_absolute_eur | 2000000 | cl. 9.2 (line 161) — A3.2's 3,000,000 not in force |
| cyber_insurance_minimum_eur | 5000000 | cl. 10.1 (line 175) |
| availability_target_percent | 99.95 | **A2.4** (line 471), amending B.1's 99.90 (line 377) |
| p1_acknowledgement_minutes | 15 | B.2 (line 379); A2.2 says acknowledgement unchanged |
| p1_restoration_hours | 3 | **A2.2** (line 467), replacing B.2's 4 |
| service_credit_percent_band_1 / _2 / _3 | 5 / 10 / 20 | Schedule B credit table, lines 385–387 |
| price_increase_frequency_per_twelve_months | 1 | cl. 5.3, "once in any twelve month period" |
| personal_data_retention_days | 730 | cl. 12.1 (line 201) |
| subprocessor_objection_days | 21 | **A2.3** (line 469), replacing cl. 12.2's 14 |
| audit_notice_business_days | 20 | **A1.2** (line 453), replacing cl. 13.1's 10 |
| audit_frequency_per_twelve_months | 1 | cl. 13.1 (line 219) |
| amendment_1/2/3_effective_date | 2031-03-01 / 2031-09-15 / 2032-01-01 | lines 449, 463, 481 |
| amendments_in_force_on_as_of_date | ["Amendment No. 1", "Amendment No. 2"] | lines 447+449, 461+463; No. 3 post-dates 2031-11-30 |

Also checked: exactly **one** clause states governing law (`grep 'laws of|governed by'` → line 341
only), so N4a's "the single clause" premise holds; Schedules A and D contain **no** numbered
paragraphs, so they hold no decoy values.

### B-002 — Kestrel reliability extraction (AGREE, full: 26 records × 7 fields + count)

Method: read all four registers, both appendices and §1.4 by hand, built the 48-row table, applied
amendments then notices, then selected. Independent of any script.

Census reproduced: **48 register rows** (Q1 11 / Q2 9 / Q3 13 / Q4 15), **no duplicate
incident_id** across registers, 9 Appendix A amendments, 8 Appendix B notices, 47 after
withdrawal, **26** selected. All 26 records match the key on all 7 fields.

The three things I was asked to verify myself:

1. **Withdrawal (R-2).** `RA-2032-03` (line 726) sets `field = withdrawn` for **INC-2031-047**,
   whose Q1 register row (line 204) is `S2 / RC-HUM / yes`. Under R-2 it is not an incident of
   2031 at all. Without the withdrawal it would have been selected. Correctly absent from the key.
2. **INC-2031-021 — amended then corrected on the same field.** Q3 register (line 480): `S3`.
   `RA-2032-07` (line 730): severity S3 → S2. `CN-021` (line 771): severity "standing as S2"
   → **S4**. Notice wins → final S4 → **excluded**. Correct.
3. **INC-2031-024 — amended then corrected on the same field, opposite direction.** Q2 register
   (line 334): `S2`. `RA-2032-04` (line 727): severity S2 → S4. `CN-024` (line 773): severity
   "standing as S4" → **S2**. Notice wins → final S2 → **included**. Correct.

Also verified, and worth recording because they are the same shape:

* **INC-2031-028 — two layers on *different* fields**, so both apply: `RA-2032-08`
  `customer_impacting` yes→no, and `CN-028` `root_cause_code` RC-EXT→RC-SW. Key has both. Correct.
* **INC-2031-034** falls *out* of the set (`CN-034`: S2 → S3), and **INC-2031-010**, **-031**,
  **-041**, **-017** fall *in* (S4 → S1). R-3 ("selection happens last") is what makes these right.
* Every layer's stated prior value is consistent with what actually stands before it: e.g.
  `RA-2032-06` asserts `was 88` and the Q3 row reads 88; `CN-024` asserts "standing as S4" and
  `RA-2032-04` had just set S4. No layer asserts a value that was not standing.
* **The narrative is never needed.** Nothing I used came from §§2.4/3.4/4.4/5.4.

### B-003 — SDX7 MUST requirements (AGREE, full: 22 of 22)

Method: a parser written from the prompt (`/tmp/.../scratchpad/v_b003.py`), not from the builder's.

Census reproduced: **96** body requirements across sections 2–9 (22 MUST, 22 SHOULD, 22 MAY,
17 SHOULD NOT, 13 MUST NOT); **17** errata entries (10 corrected level, 4 Clarified, 3 Withdrawn);
**22** final MUST. Exact list match with the key, all four fields per record.

Coverage of my parse verified, not assumed: `grep -c` gives 96 lines of the form
`^\*\*SDX-REQ-\d+\*\* `, and 96 of them match my pattern — **no requirement line was skipped**.
Only one other `SDX-REQ` mention exists in the file (§1 prose, line 7). `MUST NOT` is correctly
kept out (13 body + `SDX-REQ-0010` promoted to MUST NOT by errata).

### C-001 — feature-flag lifecycle (AGREE on all values and all 27 citations; see **F1**)

Method: read every `## Feature flags` section of all 11 release notes and all 5 errata by hand.

* **16 flags**, matching the key. All 16 `introduced_in` and all 16 `removed_in` values agree
  (8 removals recorded, 8 nulls).
* **Citations: all 27 distinct file names across the 16 records agree** with the key under the
  plural reading. The three erratum records carry {erratum + surviving release note}; the
  `nested_span_export` record additionally carries `release_notes_kestrel_2_3.md` for its removal.
* I confirmed no blog or forum file is cited anywhere in the key (correctness rule (b)), and that
  the two "coincidentally correct" files the key records in diagnostics
  (`forum_thread_4111.md` for `adaptive_shard_split`, `forum_thread_4106.md` for
  `opportunistic_gc`) are indeed absent from every `sources` list.
* See **F1** for the wording risk, and **F4** for the inert exclusion rule.

### C-002 — Meridian award totals (AGREE, full: 7 records, 24 awards, all arithmetic)

Method: read all 8 bulletins, 3 correction notices and 2 retraction notices; summed by hand.

Census: 24 award rows, `GA-0001`…`GA-0024`, one row each. Cross-checked by counting every
`GA-####` mention corpus-wide: exactly the 3 corrected and 2 retracted ids appear more than once.

All seven totals recomputed by hand and matched: Halyard 621500 (GA-0001 corrected 76000 → 88500
by `correction_CORR-002.md`), Ironwood 574000 (GA-0008 retracted, −204000, by
`retraction_RETR-001.md`), Junction 472000 (GA-0009 158000 → 143000, `CORR-003`), Kilnwork 880500,
Lodestar 358000 (GA-0017 retracted by `RETR-002`; GA-0019 139000 → 124000 by `CORR-001`),
Marrowbone 807000, Nettleford 386000. `awards_included` / `awards_excluded` match for all seven.

**All 7 `sources` sets agree** with the mapping ("every bulletin publishing one of that project's
awards, plus every correction and retraction notice that changes one"): 3+3+3+2+4+2+1 = 18
citations, each independently checked against which bulletin actually carries each award id.

The key's finer-grained `citation_support` is internally consistent with rule (c): e.g. for
Junction, `bulletin_bul_2031_03.md` is excluded from `total_awarded_eur` support (GA-0009's
standing amount now comes from `CORR-003`) but retained under `awards_included`, so it remains
a supported citation for the record. The metric reads `sources`, and `sources` is right.

### C-003 — plugin compatibility (AGREE, full: 8 records × 4 cells)

Method: read the registry export and both registry errata; extracted every blog/forum statement.

All 8 `min_kestrel_version`, all 8 `governing_source_tier`, and — the fiddly part — **all 8
`contradicted_by` arrays** reproduced exactly, including the RT-16 rule that the registry export
itself belongs in the array for the two erratum-corrected plugins:

* `kp-csv-bridge`: erratum 0.9; contradicted by blog_01 (2.1), forum_4102 (3.1), forum_4103 (1.0),
  forum_4107 (3.1) and **registry_export_2032-02.csv (3.0)** — 5 entries.
* `kp-fx-lookup`: erratum 2.3; contradicted by blog_02 (1.1), blog_04 (3.0) and **the registry
  export (2.2)** — 3 entries.
* The other six: registry-governed, contradicted only by blog/forum statements (2, 1, 2, 4, 1, 3).

I checked the reading that only "definitely needs X or newer" states a minimum — the trailing
"we tried Y" figure is not a stated minimum — which is what makes `forum_thread_4107`
("needs 3.1 … we tried 3.1") a single contradiction rather than two.

`sources` for all 8 agree (6 × registry export, 2 × the naming erratum). Note that C-003's
mapping, which is grammatically identical to C-001's, is applied here **exclusively** — and
correctly so, because the single registry export *is* the corrected file. See F1 reason 5.

### D-001 … D-004 (all four: AGREE, full on every answer field)

Method: I drove `python3 corpora/mcp_toolset/server.py mcp` myself over JSON-RPC
(`/tmp/.../scratchpad/v_d.py`, `v_d2.py`, `v_d3.py`) and computed the answers from the raw
payloads. Toolset census reproduced three ways: `tools.json` `tool_count` = 85, actual array = 85,
and a live `tools/list` = 85; 28 families; all four D prompts say "85 tools".

| task | field | my value | key |
|---|---|---|---|
| D-001 | engineer_full_name / team / escalation_tier | Adaeze M. Okonjo / Billing Platform / 2 | same |
| D-002 | digest | `sha256:bd7745e1…41d33` | same |
| D-002 | critical_open_count | **3** (KSA-2032-0117 9.8, KSA-2031-0442 9.3, KSA-2032-0094 9.1; KSA-2031-0388 at 9.4 excluded, `status: fixed`) | same |
| D-002 | highest_cvss_advisory_id / distribution / fixed_version | KSA-2032-0117 / debian-12 / 2.9.4-3 | same |
| D-003 | ship_date / fiscal_year / quarter / period / close | 2032-01-03 / FY2032 / Q4 / 12 / 2032-02-06 | same |
| D-004 | remaining_error_budget_minutes | 4.4 | same |
| D-004 | target / measured / breached | 240 / **255** (09:12→15:02 = 350, less 95 stopped) / true | same |

`required_tools` designation independently justified: I called **every** competing member of every
contested family and confirmed each returns a well-formed, different, plausible answer —
`rota.get_nominal_shift` → t.ferreira (pre-override); `registry.get_tag_digest` →
`sha256:aa11c6f0…` (publish-time digest); `vulndb.get_image_findings_by_tag` → a stale cache keyed
to that old digest, with KSA-2031-0388 at a different CVSS; `metrics.get_error_budget` → −58.6
(raw, pre-exclusion); `tickets.get_ticket_sla` → 480 (queue default, which would flip
`sla_breached` to false); `billing.list_invoices` → billing_date only, no ship_date;
`calendar.get_calendar_quarter` → Q1; and the RT-11 addition **`calendar.get_calendar_period` →
period 1, close_date 2032-02-03**, a genuine competitor to fiscal period 12 / close 2032-02-06.
RT-11's justification for adding that tool holds.

Minor, not a defect: `vulndb.get_image_findings_by_tag` rejects a `status` argument
(`unknown_argument`). Its declared schema has no `status` property and sets
`additionalProperties: false`, so the server is enforcing its own schema correctly.

### E-001 — requisition (AGREE, full: 9 BOM rows × 5 cells + 9 scalars)

Method: replayed turns 1–18 by hand against the four corpus files; all money arithmetic done at
full precision by hand and only then rounded per P1.

All nine rows agree (part_id, description, vendor, qty, unit_price, line_total), sorted ascending.
The turn-3 substitution is right: the obvious 2U edge appliance is **KP-4410** at 7200.00, vendor
**Halberd Manufacturing**, which turn 3 excludes and which P3 independently bars
(`vendors.csv:2`, `audit_result: failed`); the nearest allowed 2U entry is **KP-4477** at 7815.00
from Calderon Metalworks. Turn-14 (24 → 32 optics) and turn-15 (drop KP-1905) both land on the
final table.

My arithmetic, reproduced independently:

* hardware_subtotal = 427.50 + 71.40 + 1977.50 + 4672.00 + 117.00 + 22560.00 + 31260.00 =
  **61085.40** (KP-6001 and KP-6042 excluded as service lines — `uom = day`, or `rohs = n/a`, P2)
* service_subtotal = 2640.00 + 1450.00 = **4090.00**
* contingency = 61085.40 × 0.12 = 7330.248 → **7330.25** (one rounding, P1.2)
* freight: destination SITE-BIL-1 is **EU-SW** (`sites.csv:7`). Calderon is EU-SW → 1%:
  31758.90 × 0.01 = 317.589. Ardent EU-C → 676.80; Pellworm EU-N → 140.16; Northwall EU-NW →
  59.325; Tessellate EU-NW → 3.51. Sum of **unrounded** products = 1197.384 → **1197.38**
  (one rounding, P4 + P1.2)
* grand_total = 61085.40 + 4090.00 + 1197.38 + 7330.25 = **73703.03** (components as reported, P1.3)
* **within_cap = false**, amount_over_cap = 73703.03 − 70000.00 = **3703.03** (P1.4)
* lead time = max over hardware lines = **52** (KP-4477); approvers = **1** (73703.03 ≤ 200000, P5)

**The uncomfortable answer is keyed correctly.** The key reports the breach rather than trimming;
no line is dropped and no qty reduced, which is what V5 exists to catch. See F3 for the prose slip.

### E-002 — migration runbook (AGREE, full: 11 steps × 6 cells + 2 scalars)

Method: computed waves and ordering by hand from `services.csv`.

Waves recomputed independently, after removing `kestrel-vault` (turn 3) and `kestrel-mailer`
(turn 9) and treating vault dependencies as satisfied: rota 1, indexer 1 (its only dependency was
vault), gateway 2, billing 3, cdn 3, search 3 (max of indexer 1 and gateway 2), ledger 4,
reports 5. Identical to the key.

Ordering by (wave, tier, name) reproduced: indexer, rota | gateway | billing, search, cdn |
ledger | reports. Verification steps inserted after each **in-scope** tier-1 service — gateway,
billing, search (vault is tier 1 but out of scope, correctly not verified) — giving MIG-001…
MIG-011 with no gap. Owner teams all match `services.csv`. Start times at 45-minute spacing from
2032-05-10T22:00:00Z reproduced step by step through the midnight rollover to
**2032-05-11T05:30:00Z**. step_count 11, total_duration 495.

The key's diagnostic that the turn-10 answer (third step = 2032-05-10T23:30:00Z, before
verification steps exist) differs from the final MIG-003 position is consistent with my replay.

### E-003 — shift assignment (AGREE, full: 12 shifts × 2 cells + unfilled_count)

Method: eligibility computed by hand for all 16 roster people against all 12 shifts.

All 12 assignments match. I confirmed **every shift has exactly one eligible person**, so the key
is uniquely determined and not one of several defensible answers.

**The uncomfortable answers are keyed correctly:**

* **SH-105 and SH-106 (SITE-DUB-1, both require C2) are UNFILLED.** The only C2 people at that
  site are PR-008 (`status: on_leave` in the roster) and PR-014 (put on leave by turn 12). PR-007
  is at the site and available but holds **C3**, which turn 2 says does not qualify. The key
  assigns nobody rather than bending a rule — exactly what turn 7 demands and what V1/V3 catch.
* **Reason string.** `all_eligible_on_leave` is right, not
  `no_person_with_required_certification_at_site`: C2 people *do* exist at SITE-DUB-1, they are
  merely on leave, so the second reason in the stated order is the first that applies. For SH-106
  the night rule never gets a turn, because both C2 candidates are night-qualified.
* **unfilled_count = 2.** Correct.
* **Turn 16 is a genuine no-op**, as the notes claim: PR-016 takes SH-111 and SH-112, which is 2
  shifts against an original `max_shifts` of 2. Raising it to 3 changes nothing.
* Turn-17 and turn-18 probes independently confirmed: PR-011 cannot cover SH-111 (C3 ≠ C2);
  PR-012 cannot cover SH-110 (`night_qualified: no`, and SH-110 is a night shift).

---

## How much of each task I actually verified

| task | verified | of | proportion |
|---|---|---|---|
| A-001 | 63 symbols | 63 | 100% (graph over all 397 functions) |
| A-002 | 11 symbols | 11 | 100% (tested against all 397) |
| A-003 | 10 symbols | 10 | 100% (+ all 23 decorations, all 6 raisers) |
| A-004 | 4 components | 4 | 100% (+ read the cross-module cycle line by line) |
| B-001 | 36 fields | 36 | 100%, each with a line citation |
| B-002 | 26 records × 7 + count = 183 cells | 183 | 100% (from all 48 rows, 9 amendments, 8 notices) |
| B-003 | 22 requirements | 22 | 100% (from all 96 body reqs + 17 errata) |
| C-001 | 16 records × 3 = 48 value cells, **27 citations** | 48 + 27 | 100% |
| C-002 | 7 records × 4 = 28 value cells, **18 citations**, 24 awards | 28 + 18 | 100% |
| C-003 | 8 records × 4 = 32 value cells, **8 citations** | 32 + 8 | 100% |
| D-001 | 3 answer fields + 2 required tools + 2 decoys called | 3 | 100% |
| D-002 | 5 answer fields + 2 required tools + 2 decoys called | 5 | 100% |
| D-003 | 5 answer fields + 2 required tools + 3 decoys called | 5 | 100% |
| D-004 | 4 answer fields + 2 required tools + 2 decoys called | 4 | 100% |
| E-001 | 9 rows × 5 + 9 scalars = 54 cells | 54 | 100%, arithmetic redone at full precision |
| E-002 | 11 steps × 6 + 2 = 68 cells | 68 | 100% |
| E-003 | 12 shifts × 2 + 1 = 25 cells | 25 | 100% |

Every committed answer-key value in the task set was independently re-derived. Nothing was
sampled or spot-checked in lieu of full derivation.

---

## What I did NOT check — do not over-read this sign-off

1. **`judge.py` and `SCORING_SPEC.md` implementation.** I did not read `judge.py`, did not run its
   test suite, and did not confirm that the scorer implements the per-task `quality_metric` text.
   My only check there was a targeted grep confirming no live task file still carries a v1.0.0
   relative floor. **A key can be right and still be scored wrongly; that is a different seat.**
2. **The derivation scripts under `answer_keys/scripts/`.** Deliberately never opened. I therefore
   cannot say whether they are correct *as programs* — only that their committed outputs are the
   right answers. A script that gets the right answer by the wrong route would pass my check.
3. **`SHORTCUT_PROBE_RESULTS.md`.** The measured figures (0.2421 for first-half truncation,
   1.0000 for content-selective retrieval over 5.2% of bytes, the three 0.0000 results) were not
   reproduced. `shortcut_probe/probe_b002.py` was not run.
4. **The v1.0.0 → v1.1.0 invariance claims.** I confirmed the *current* A and D keys are correct,
   and I reproduced the corpus/toolset census figures the CHANGELOG cites (397 functions, 85 tools,
   28 families). I did **not** diff against `TASK_SET_v1.0.0/`, which is immutable and out of
   bounds for this seat, so I cannot confirm the payload hash `e8531b090bac0938` or that the four D
   `required_tools` sets are byte-identical to v1.0.0's. My statement is the stronger one that
   matters for the run: **the v1.1.0 keys are right**, whatever v1.0.0 held.
5. **`required_evidence` plumbing.** Every failure condition depends on the harness supplying
   `corpus_hashes_before`/`_after` and (for A) `valid_symbols`. I confirmed the task text defines
   them and fails closed without them; I did **not** confirm the harness actually produces them.
6. **E intermediate turns.** Only each scenario's final state is scored for content, and that is
   what I verified, together with the per-turn logic that produces it. I did not simulate an agent,
   so I have not exercised the V-code scanners against real intermediate replies.
7. **Token-efficiency and cost claims** anywhere in the task set. Out of scope for this seat.
8. **`DESIGN_NOTES.md`, `README.md`, `BUILDER_NOTES.md`, `STALE_v1.0.0_KEYS.md`** were not audited
   for internal consistency beyond the specific CHANGELOG claims named above.

## Constraints observed

No task, corpus, answer key, derivation script, `SCORING_SPEC.md` or `judge.py` was modified.
Nothing under `TASK_SET_v1.0.0/` was touched. Nothing was committed to git. All generated code and
intermediate output went to the session scratch directory. This file is the only thing I wrote.

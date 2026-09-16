# SUPERSEDED — this directory now holds the v1.1.0 answer keys

**This file is kept only so that links to it do not dangle. Its previous contents — a list of
ways the copied v1.0.0 keys were stale — have been resolved. Read
[`BUILDER_NOTES.md`](BUILDER_NOTES.md) instead.**

All 17 `*.json` keys and all five scripts under `scripts/` have been re-derived by the Answer
Key Builder against `TASK_SET_v1.1.0/corpora/` and against each task's v1.1.0
`quality_metric` and `failure_condition`. Each key is produced mechanically by the script named
in its own `derivation_script` field, and all 17 were verified to reproduce byte-identically on
a second run. An "ideal" answer built from each key was scored through
`environment/harness/judge.py` at methodology version 1.1.0: 17/17 score 1.0000 with
`task_success = true`.

Disposition of every row of the previous version of this file:

| the previous claim | what actually happened |
|---|---|
| `B-002.json` is wrong; `derive_B.py` asserts against the new document | **Confirmed and rebuilt.** `b002()` was rewritten for the four per-quarter registers, the Appendix A Register Amendments layer (including the `withdrawn` amendment that removes `INC-2031-047`) and the Appendix B Correction Notices layer. 24 records → **26**. |
| `derive_E.py` fails; the v1.0.0 freight figures are now the only defensible reading | **Confirmed.** The P4 regex was re-anchored and the totals re-derived under P1.1–P1.4. The values `1197.38 / 73703.03 / 3703.03` stand and are now the only defensible ones; the rival reading (rounding each per-vendor freight product before summing) gives 1197.39 / 73703.04 and is forbidden by the new P4. |
| The three C keys need a governing-source set that *is* the set the metric describes | **Done, and it uncovered more than a shape problem.** The `non_authoritative_*` fields are gone from C-001, `citation_support` is a clean per-field map of file names in all three, and C-003's support set is now derived from authority rather than from string agreement. The old C-002 key made C-002 **unpassable** — see Defect 1 in `BUILDER_NOTES.md`. |
| `C-003.json`'s `contradicted_by_alternate_reading_low_authority_only` is dead | **Removed.** The literal reading is the only one recorded. |
| The four D answers and `required_tools` are unchanged | **Verified, not assumed.** `tools.json` was diffed between versions; every tool in a `required_tools` set kept its family and every uncontested tool the derivation calls is still uncontested. All four D keys reproduce byte for byte. |
| The four A answer sets are unchanged; only the function count moves 394 → 397 | **Verified.** All four A keys reproduce byte for byte; the count is 397. |
| `B-001`'s two fields are now mandated rather than chosen | **Confirmed.** The v1.0.0 values already matched what N4/N4a now require, so the key is unchanged. |
| Every `count` rule changed but no key value changes | **Confirmed.** Independently cross-checked against the metrics' own arithmetic: B-002 26 records → denominator 183, B-003 22 records → denominator 89. |
| `MANIFEST.sha256` was removed rather than regenerated | Unchanged; the coordinator owns the wider manifest. This seat wrote no manifest. |

Two residual defects in this directory's *inputs* — not in the keys — are recorded in
`BUILDER_NOTES.md` as Defects 4 and 5: B-001's ORDER OF PRECEDENCE item 1 and C-001's singular
claim-to-source mapping each admit a reading that fails the task outright.

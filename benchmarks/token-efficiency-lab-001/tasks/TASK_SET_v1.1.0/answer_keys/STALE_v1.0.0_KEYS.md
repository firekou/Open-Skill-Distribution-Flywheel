# STALE — these are the v1.0.0 answer keys, not the v1.1.0 keys

**Do not score a v1.1.0 run with anything in this directory.**

Every `*.json` key here and every script under `scripts/` was copied unchanged from
`TASK_SET_v1.0.0/` when this task set was branched, so that the Answer Key Builder has the
v1.0.0 derivations to work from. The Task Set Designer wrote no key and edited none.

They are stale for v1.1.0 in at least these ways, and possibly others:

| what changed in v1.1.0 | consequence for this directory |
|---|---|
| `corpora/docs_b/KESTREL_RELIABILITY_2031.md` was rebuilt (RT-03) | `B-002.json` is wrong. `derive_B.py` **fails with an assertion** against the new document. |
| `corpora/workflow_e/procurement_policy.md` P1 and P4 were rewritten (RT-06) | `derive_E.py` **fails**: its regex is anchored on the old P4 sentence. `E-001.json`'s freight figures need re-deriving, though the v1.0.0 key's `1197.38 / 73703.03 / 3703.03` is now the only defensible reading. |
| The workload-C citation rule was replaced (RT-04) | `C-001.json`, `C-002.json` and `C-003.json` need a `governing_sources` set per record that *is* the set the metric describes — not a curated subset plus a separate `non_authoritative_files_stating_the_same_introduced_in` list. |
| `contradicted_by` was settled literally (RT-16) | `C-003.json`'s `contradicted_by_alternate_reading_low_authority_only` field is now dead; the literal reading is the rule. |
| `corpora/mcp_toolset/` gained a tool and moved eight tools between families (RT-11) | The four D answers and `required_tools` sets are **unchanged** — verified by running `derive_D.py` against both corpora — but `contested_families` now denote different tool sets. |
| `ledgerline/util/retry.py`, `util/errors.py`, `util/clock.py`, `util/text.py` gained definitions (RT-17) | The four A answer sets are **unchanged** — verified by running `derive_A.py` against both corpora; only `module_level_function_count` moves from 394 to 397. |
| `B-001` fixed the spelling of `amendments_in_force_on_as_of_date` and the extent of `governing_law` (RT-07) | `B-001.json`'s values for those two fields are now mandated by the task text rather than chosen by the builder: `Amendment No. n` and the bare jurisdiction name. |
| Every `count` rule changed (RT-10) | No key value changes; the metric that consumes them does. |

`MANIFEST.sha256` was **removed** from this task set rather than regenerated: the coordinator
builds the wider manifest, and the v1.0.0 manifest neither covered this directory (RT-12) nor
matched the v1.1.0 tree.

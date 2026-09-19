# First-issue samples

Three topics. Each has a human article and a machine learning package that **share the same
`claim_id`s, sources and evidence states**. `tools/test_packages.py` `t_17` fails if they drift, and
if the machine version drops a limitation the human version carries.

| Sample | Topic | Depth |
|---|---|---|
| `S001-approval-boundaries` | What may an Agent decide for the company | **full demonstration** |
| `S002-cost-per-successful-task` | What one successful task really costs | concise |
| `S003-expiry-and-revocation` | How an Agent learns its knowledge expired | concise |

All three are `status: draft`. **None is published.** `human_responsible` is `null` on all six
packages because no human publishing owner has been assigned — that is the honest value, not a gap
in the data, and `t_19` locks it.

Every `test_case` carries `"executed": false`. **A written test is not a passed test.**

## Sources

S001 cites the MCP tools specification at two versions (read verbatim) and the A2A specification
(obtained only as a summarised rendering, therefore capped at `REPORTED` — rule `P13`).
S002 and S003 cite this repository's own evidence ledger and readiness review at commit `a8ca352`.

**No claim in any sample rests on a measurement of a third-party tool.** ATK has executed no
third-party candidate code, and nothing here says otherwise.

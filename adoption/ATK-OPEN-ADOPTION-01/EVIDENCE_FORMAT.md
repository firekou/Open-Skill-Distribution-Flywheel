# Adoption evidence format (A5)

One JSON file per trial attempt in `records/`, checked by `validate_records.py`
(stdlib, offline). Schema: [adoption-record.schema.json](adoption-record.schema.json).
This is a file format, not a tracking system: nothing here collects data from anyone. Records are
written by us from what an operator chose to tell us, or by the operator themselves.

## The one rule that matters: who ran it, and how they got there

| `source_class` | what it proves | what it does **not** prove |
|---|---|---|
| `INTERNAL_AGENT_TEST` | our own agent can follow the docs | anything about outside use — even in a new session, another model, or starting from an unknown URL |
| `EXTERNAL_INVITED_AGENT` | an agent controlled by an outside developer used it after a direct invite | that anyone would find it on their own |
| `EXTERNAL_DISCOVERED_AGENT` | an outside agent found it via a recorded search or directory entry and used it | anything about agents that did not find it |
| `EXTERNAL_INVITED_HUMAN` / `EXTERNAL_DISCOVERED_HUMAN` | same, operated by a person directly | — |
| `UNVERIFIED` | nothing yet | — use this whenever who controlled the agent is not observable |

`discovery_route` is separate: `INTERNAL`, `DIRECT_INVITE`, `PUBLIC_DISCOVERY`,
`DIRECTORY_DISCOVERY`, `UNKNOWN`.

`validate_records.py` runs two blocking layers. The **schema layer** applies the schema itself —
`required`, `additionalProperties`, `type`, `enum`, `const`, `pattern`, `items`, `minItems`,
`minimum`, `anyOf` — as a small stdlib subset, so a bad date format, an empty `commands`, a
negative duration or `operator_external: 1` in place of `true` is rejected, not just a missing
field. The **semantic layer** then enforces what a schema cannot:

1. `EXTERNAL_*` needs `operator_external: true` **and** `operator_evidence` (for example, the
   operator's own public issue comment). Missing either → the record must be `UNVERIFIED`.
2. `INTERNAL_AGENT_TEST` must be `operator_external: false` and route `INTERNAL`.
3. `PUBLIC_DISCOVERY` / `DIRECTORY_DISCOVERY` need `discovery_detail`: the exact query or
   directory entry, the result position, and why it was chosen.

## What counts as adoption

A completed record with `success: true` means: **found or received → obtained → ran → completed
the stated task**. Clones, stars, page views, crawler hits and "I read it" are not adoption and do
not get a record. A trial that ended in `NO_BENEFIT`, `NEEDLE_LOST` or `STOPPED_BY_POLICY` still
gets a record — those are results.

## Fields

| field | notes |
|---|---|
| `record_id` | `INT-…` for ours, `EXT-…` for outside, `DISC-…` for discovery trials |
| `agent_runtime` | agent name and version, OS, Python — as reported |
| `code_sha`, `headroom_version` | full 40-char SHA; the version actually installed |
| `date_utc`, `duration_minutes` | `duration_minutes` may be `"unknown"` |
| `task` | what they were asked to do, in one line |
| `input_md5` | the synthetic log's md5, or `"own-payload-not-shared"` |
| `commands` | as run; never including a key |
| `exit_code`, `result`, `success_criterion`, `success` | `result` enum is in the schema |
| `human_help` | `"none"`, or what help, from whom |
| `usage_cost` | `"0 (offline)"`, provider usage figures, or `"unknown"` — **never** `0` for unknown |
| `blockers` | where it got stuck, as error classes |
| `reuse_intent` | `yes` / `no` / `maybe` / `unknown` |
| `public_scope` | `public`, `summary-only`, `private` — what the operator agreed we may publish |
| `evidence_urls` | public links (their issue comment, a gist) or paths in this repo |

## Never record

An API key or any part of one, a real log or real log lines, needle text from a real payload, a
raw provider error body, a full session transcript, personal data beyond a public handle the
person used themselves. If an operator sends any of these, do not commit it; write the record from
what can be shared and note that the rest was withheld.

## Current ledger (2026-09-22)

| class | records |
|---|--:|
| `INTERNAL_AGENT_TEST` | see `records/INT-*` |
| `EXTERNAL_INVITED_AGENT` | **0** |
| `EXTERNAL_DISCOVERED_AGENT` | **0** |
| external human, either route | **0** |
| public discovery trials run | **0** (protocol in [TRIAL_TASK.md](TRIAL_TASK.md); T0 has not occurred) |

`test_fixtures/` holds five records that must fail and one that must pass; they are the
negative controls for the validator, not real trials.

# Discoverability baseline — fixed queries for a repeatable re-test

## What happened to the first run's raw log

The 2026-09-18 search trial reported **0/3** across three problem statements and 16 queries. **The
verbatim query log was not preserved** — only the isolated agent's summary of it survives, in
`reviews/ATK_AGENT_DISCOVERY_EXECUTOR_RESPONSE.md` §4. That summary lists the queries it used, but
it is the agent's own account, written after the fact, not a captured transcript.

**Consequence, stated plainly:** the original 16 queries **cannot be re-run as the same set**, and
any later claim of "we re-ran the same queries" would be false. The earlier round said the
re-test would use "the same set"; that was wrong and is withdrawn here.

This file is therefore a **new baseline, established 2026-09-18, not yet executed**. The 0/3
result stands as a recorded observation from the earlier trial; it is not the T0 of this baseline.

## The baseline

**Not yet run. No result is recorded below, and no cell is pre-filled with 0 or PASS.**

**T0 definition.** T0 is the date the new root-README entry and the GitHub About description /
topics are **actually public on `main`**. All of that is currently on a Draft branch with the
About change unapplied, so **T0 has not occurred**. No clock is running and nothing is scheduled.
The comparison run is T0 + 14 days, executed by a human or agent at that time.

**Method.** A clean agent with web search only, no repository name, no brand name, no URL, no
hint that this project exists. One run per query, top results recorded with URLs.

| # | Problem | Query (verbatim, to be issued exactly as written) |
|---|---|---|
| Q1 | P1 | `local proxy compress LLM context deploy logs preserve error line coding agent` |
| Q2 | P1 | `prompt compression proxy measured token savings reproducible evidence open source` |
| Q3 | P1 | `compress log before sending to LLM keep the failure line benchmark not marketing` |
| Q4 | P2 | `token compression in front of OpenAI-compatible gateway per-request no code changes` |
| Q5 | P2 | `compression proxy non-OpenAI gateway worked example real measured numbers` |
| Q6 | P2 | `headroom proxy x-headroom-base-url custom upstream gateway example` |
| Q7 | P3 | `machine-readable registry verified AI tools version licence install command cost dated evidence` |
| Q8 | P3 | `curated index AI agent skills with proof someone actually ran it reproducible` |
| Q9 | P3 | `registry of agent tools recording cost and dated verification record` |

**Recorded per query:** date and time (UTC), search tool and model, the query as issued, the top
ten result URLs, whether this repository appeared and at what rank, and whether the agent selected
it. A query that returns nothing relevant is recorded as such, not as a failure of the tool.

## Interpretation rules, agreed in advance

These are fixed now so the result cannot be read generously later.

1. **Nine queries are a diagnostic, not a discovery rate.** No percentage may be derived.
2. **Appearing in results proves visibility only.** It is not adoption, not use, and not revenue.
3. **A change in result does not establish a cause.** The earlier 0/3 was attributed in part to
   the project naming a metaphor rather than a problem. That remains a **hypothesis**. Competing
   explanations that this baseline cannot separate: the asset was on an unmerged Draft branch with
   no navigation to it; the repository had not been crawled since the content was added; ordinary
   ranking volatility; and the crowdedness of P1/P2 (eight to ten established competitors each).
4. **A null result at T0+14 is a real result** and is reported as one, not re-run until it moves.

## Separate ledgers — never merged into one number

| Ledger | Meaning | Status as of 2026-09-18 |
|---|---|---|
| Given-the-URL adoption | Someone handed the entry point can complete the task | Passed once, by an isolated agent inside our own session. **Not a third party.** |
| Natural search discovery | Found without being given the name or URL | **0/3** on the earlier trial. This baseline not yet run |
| Third-party use | A person or agent outside this project ran it | **None recorded** |
| ATK referral | Traffic or usage reaching ATK through this asset | **None recorded, and not measurable** — this asset contains no tracking of any kind |

# Trial tasks (A3): three separate tests, never merged into one number

All three use the same asset and the same success definition:
**found or received → obtained → ran → completed the task.** A trial that stops for a valid
reason (no benefit, needle lost, policy) is recorded as that result; it is not re-worded into a
success, and a failed discovery query is not swapped for an easier one until something is found.

The task in every case is the offline trial in
[AGENT_QUICKSTART.md](../../integrations/headroom-atk/AGENT_QUICKSTART.md) §4–§5 at code SHA
`304af885193245da7186cb6b9ab247ec2494bd86`. Records go in `records/` per
[EVIDENCE_FORMAT.md](EVIDENCE_FORMAT.md).

## 1. DIRECT_INVITE — can someone who is handed the link use it?

- Given: the pinned link to `AGENT_QUICKSTART.md` (and the manifest), the task text in
  [INVITATIONS.md](INVITATIONS.md) §2, nothing else.
- Run by: an outside developer's own agent (target class `EXTERNAL_INVITED_AGENT`), or our own
  agent in a fresh session (`INTERNAL_AGENT_TEST`, which does not count toward M2).
- Pass: exit 0 on the synthetic log, reported with the §7 fields. A stop at exit 1/3/4 with the
  correct reading of the table is a **documentation pass** and an **adoption non-result**; record
  both.
- Record: every place the agent had to guess or ask for help (`human_help`, `blockers`). Those are
  the inputs to M3.

## 2. PUBLIC_DISCOVERY — would anyone find it without being told?

Protocol (fixed before any run so the result cannot be read generously later):

- Given: **only** a real problem statement. No brand (ATK, AI Token King, headroom), no
  repository name, no URL, no hint that a specific asset exists.
- Tool: a clean agent session with ordinary web search; record the search tool and model.
- Problem statements, issued verbatim:
  - P1: "My coding agent reads 100 KB deploy logs into the model context. I want to shrink what is
    sent without losing the one failed-migration line. Is there a tool I can check first, offline,
    on my own log?"
  - P2: "I run an OpenAI-compatible gateway that is not OpenAI. How do I put a prompt compression
    proxy in front of it, per request, without code changes, and verify it kept the error line?"
- The agent chooses its own queries. Record every query as issued, the top ten result URLs, whether
  this repository appears and at what rank, and whether the agent selected it and why.
- Result classes: `NOT_FOUND`, `FOUND_NOT_SELECTED`, `SELECTED_NOT_RUN`, `RUN_COMPLETED` (only the
  last is a discovery success, and only when the agent's operator is outside this project does it
  count as `EXTERNAL_DISCOVERED_AGENT`).
- Timing: this reuses the rules in `integrations/headroom-atk/evidence/SEARCH_BASELINE.md` @
  `304af885`. **T0 is the day the asset is reachable from `main` and the About/topics are
  applied** — neither has happened. Run once at T0 and once at T0+14 days. Before T0 a run
  measures a Draft branch and is labelled as such.
- A null result is recorded as a null result.

Our own agent running this protocol is an **internal discovery test**, whatever session, model or
starting point it uses.

## 3. DIRECTORY_DISCOVERY — does a listing lead anyone to it?

Only applies once the asset is actually listed somewhere (none today; candidates and their current
rules in [DISTRIBUTION_CHANNELS.md](DISTRIBUTION_CHANNELS.md)). For each listing: record the
directory, the entry URL, the date listed, and for each trial the search the agent ran inside that
directory and the position of our entry. A listing is not a result; a run that started from the
listing is.

## Status on 2026-09-22

| test | runs | classification |
|---|--:|---|
| DIRECT_INVITE | 2 by us (executor run and a fresh subagent session) | `INTERNAL_AGENT_TEST` only |
| PUBLIC_DISCOVERY | 0 | not run; T0 has not occurred |
| DIRECTORY_DISCOVERY | 0 | not listed anywhere |
| external use of any kind | 0 | — |

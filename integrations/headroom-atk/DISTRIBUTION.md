# Sharing draft and distribution list — 待發布 (NOT PUBLISHED)

**Status: nothing in this file has been posted, submitted, or sent.** No account was used, no
upstream project was contacted, no directory was submitted to. Publication needs separate owner
authorisation. This file is the prepared material and the checklist, which is what the work
package asked for — it is not evidence of distribution.

Channel doctrine reused from [CONTENT_DISTRIBUTION.md](../../CONTENT_DISTRIBUTION.md); not
reinvented here. This asset lands on its Beat 2 ("we ran it, here is what broke") and Beat 5
("real before/after numbers"), which that document requires to carry real measurements — it does.

---

## Draft 1 — short post (X / Threads)

> We put a local compression proxy in front of an LLM gateway and measured it on a 1,200-line
> deploy log with one FATAL line buried at index 947.
>
> 40,589 → 25,525 prompt tokens. 37.1% fewer. Both paths returned the same migration name and the
> same SQLSTATE.
>
> The part nobody posts: on a "summarise in five bullets" prompt, the FATAL line was missed by
> **both** the compressed and the uncompressed path. Wrong instrument for the job, not a
> compression failure — but it is the result.
>
> Three things that will trip you up, and an offline check that needs no API key:
> [link]

## Draft 2 — the gotcha post (the one with actual reuse value)

> Spent an hour on this so you do not have to. Putting `headroom` in front of a non-OpenAI
> OpenAI-compatible gateway:
>
> 1. Setting `OPENAI_BASE_URL` does NOT route the proxy to your gateway. It resolves the provider
>    itself, so your gateway key goes to OpenAI and you get `Incorrect API key provided` — which
>    looks like a gateway problem and is not.
> 2. Use `x-headroom-base-url`, and give it the base **without** `/v1`. It appends the path. With
>    `/v1` you get a 404 from a URL containing `/v1/v1/`.
> 3. Pointing it at a localhost test stub fails *silently*: its SSRF guard refuses private
>    addresses and falls back to its own provider resolution, so you see failure (1) again and
>    blame the wrong thing. `HEADROOM_ALLOWED_BASE_URLS` allowlists it.
>
> Working example + an offline verification script: [link]

## Draft 3 — README (the canonical asset, already written)

[`integrations/headroom-atk/README.md`](README.md) — this is the destination every other draft
links to. It is written to be followed by someone who was given nothing else.

---

## Distribution list — every entry is 待發布

| # | Entry point | Who sees it | Links to | How we would verify it was actually indexed / used | Authorisation needed |
|---|---|---|---|---|---|
| 1 | This repository (`integrations/headroom-atk/`) | anyone with the repo URL; agents given the path | itself | GitHub traffic on the path; clones | none — **done**, this is the only completed item |
| 2 | `registry/materials.json` `_adoption` record | an agent reading the machine index | the README | fetch the raw JSON and confirm `_adoption` present | none — **done** |
| 3 | Repository README index entry | a human landing on the repo root | the README | visible in the root README | small edit, not yet made |
| 4 | Repo topics / description keywords (e.g. `token-optimization`, `llm-proxy`) | GitHub search | the repo | search GitHub for the topic and find the repo | owner (repo settings) |
| 5 | An upstream issue or discussion on `headroomlabs-ai/headroom` sharing the three gotchas | headroom's own users and maintainers | the README | the thread exists; reactions; whether a maintainer folds it into their docs | **owner authorisation required — this is contacting a third party** |
| 6 | X / Threads / LinkedIn posts (drafts 1–2) | developer audience | the README | referral traffic; replies | owner; account access |
| 7 | External tool directories / awesome-lists | people browsing curated lists | the repo | our entry appears in their list | owner; each has its own submission rules to follow |
| 8 | `llms.txt` at the repo root | agents that look for one | the registry + README | **cannot be verified** — no client is known to guarantee it is read. Listed as preparation, never as discoverability | none, but see caveat |

**Caveat carried from the work package, restated because it is the easiest thing to get wrong:**
publishing JSON, Markdown, `llms.txt` or an MCP endpoint is a *delivery format*. None of them
causes a search service to index the asset or an agent to find it. Items 1–2 are done and are the
only ones that are. Everything else is prepared and waiting.

## What would make item 4–7 worth doing

Right now the asset has zero recorded external use. Posting first and measuring later is how a
project convinces itself it distributed something. The order that produces evidence is: make the
entry point followable by a stranger (done, and trialled), then place it, then measure whether
anyone arrived.

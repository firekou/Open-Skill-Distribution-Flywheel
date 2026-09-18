# Verification record — ATK provider seam

**Updated:** 2026-09-18 (round 2, after the PR #4 review of `f2a2188`)
**Scope:** `integrations/atk-provider/`
**Status: local behaviour VERIFIED by the author. ATK connectivity VERIFIED BY THE REVIEWER, not
by this repository.**

## The official endpoint — and who established it

The first version of this file recorded that `api.aitokenking.com` did not resolve and concluded
the ATK path was unverified. **That hostname was wrong**: it was missing both `.tw` and `/api`.

**The PR #4 reviewer found the official entry point and tested it. I did not.** Attribution
matters here, so it is stated before the table:

| | |
|---|---|
| **Tested by** | the PR #4 reviewer, with their own credential |
| **Not tested by** | this repository. **No ATK credential exists in this environment**, and nothing here has ever called ATK |
| Source | <https://aitokenking.com.tw/assets/docs/zh-Hant/index.html#mcp-server> |

| Purpose | Official entry point | Evidence |
|---|---|---|
| OpenAI-compatible base URL | `https://api.aitokenking.com.tw/api/v1` | **TESTED (reviewer)** |
| Model list | `GET /api/v1/models` | **TESTED (reviewer)** — HTTP 200, 52 models |
| Chat completions | `POST /api/v1/chat/completions` | **TESTED (reviewer)** — one call through **this repository's `atk_provider.py`**, changing only the environment: `model=claude-sonnet-4.6`, `MAX_RETRIES=1`, no fallback, `max_tokens=16`. Sent "Reply with OK only." → returned `OK`, usage 12 in / 4 out. **No USD cost reported, which does not mean free** |
| MCP | `https://api.aitokenking.com.tw/mcp`, header `X-Aitokenking-Api-Key` | **OBSERVED in the official docs only.** No MCP handshake has been performed by anyone on this PR |

**What that one live call establishes:** the single-text path works against the real service, and
this adapter speaks it correctly. **What it does not establish:** MCP, other models, other
providers, streaming, tool calls, billing behaviour, or anything about cost.

## Variable naming

The official docs use `AITOKENKING_API_KEY`; `ATK_ROUTING_INTEGRATION.md` §3 uses `ATK_API_KEY`.
**`ATK_API_KEY` is the documented name here, and `AITOKENKING_API_KEY` is accepted as an alias**
so a reader can paste either without knowing this history. Mapping stated in `.env.example` and
`README.md`; regression test `test_the_official_key_name_is_accepted_as_an_alias`.

## Review findings from `f2a2188` — all three closed

Each was reproduced before being changed, and each fix has a **runtime** regression test. The
reviewer's instruction was explicit: *do not let "no `sk-` in the source" stand in for a runtime
test*. So every credential case configures a real canary value, has a real server echo it, and
asserts on what a human would actually see.

### P4-01 — a rejecting server could leak the key (was REPRODUCED, now closed)

`_post` put the first 400 characters of the error body into the exception, under a comment
reasoning that keys travel in headers so bodies are safe. **That inference was wrong.** A server
answering `401 {"error": "invalid credential <key>"}` put the key into text the example prints
to stderr. Reproduced: `CANARY in str(exc)` → `True`.

**Fix:** the body is **withheld by default**; the message carries status and provider only.
`ATK_INCLUDE_ERROR_BODY=1` opts in for debugging, and **redaction still applies on that path**.
Every known `*_API_KEY` value is also redacted from the aggregated fallback error, and from the
URL in an unreachable-host error, since some gateways carry credentials in a query string.

Tests: rejecting server · opt-in body · aggregated fallback · unreachable host with the key in
the URL · `--show-payload` never prints the key or an `Authorization` header.

**Honest limit:** redaction only removes values it knows. A proxy that re-encodes or truncates a
key can still defeat it — which is why withholding, not redaction, is the default.

### P4-02 — a 200 with no text counted as success (was REPRODUCED, now closed)

`content: null` returned `Completion(text=None)`; the example printed `None` and exited 0. For a
summarising asset that is a failure reported as a success. Reproduced: `c.text is None` → `True`.

**Fix:** a non-empty string is required. `null`, whitespace-only, and wrong-typed content all
raise, and the message names `finish_reason` so the reader learns *why* it was empty. Same rule
for empty Anthropic `content` blocks. **Control:** genuine text still succeeds.

### P4-03 — Quick Start did not match the implementation (was OBSERVED, now closed)

1. `.env.example` carried the wrong base URL and the README only said "fill in key/model", so
   following it could not work. **Fixed** to the official URL, with the model-list command.
2. The README claimed `--dry-run` printed "the exact request" while the code printed 300-char
   excerpts. **Fixed both ways**: the default is now labelled a **PREVIEW**, and `--show-payload`
   prints the **complete JSON body**. Headers are never printed.

## What was verified, and how

All tests run against a **real HTTP server on localhost** — a real socket, a real request, a real
parse. What is synthetic is the *provider*, not the transport. URL construction, headers, JSON
body, status handling, retries and fallback are genuinely exercised.

```
$ python3 -m unittest test_atk_provider
Ran 25 tests — OK
```

Against the reviewed commit `f2a2188`, the 11 new PR #4 tests give **10 failures /
1 error**, and the single pass is the deliberate control (`test_real_text_still_succeeds`) — a fix that rejected everything would be its own
defect.

| Contract property (`ATK_ROUTING_INTEGRATION.md` §1) | Evidence |
|---|---|
| **Transparent** — the user sees which provider served each request | `Completion.provider` asserted; the example prints it on every run |
| **Replaceable** — switching takes one config change and works | The same call reaches two different servers with two different keys, by env alone. Both servers assert what they received |
| **Documented** — switching *away* is explained prominently | `README.md` § "Switching away from ATK" |
| **Optional** — runs end to end with ATK fully removed | Asserted with every `ATK_*` variable absent |

| Promised behaviour | Evidence |
|---|---|
| No hardcoded key, URL or model (§3 rule 4) | Source scanned for `aitokenking`, `sk-`, `api.openai.com`, `api.anthropic.com` — none present |
| Incomplete config fails **before** a request is sent | Asserted the server received **zero** calls |
| An unknown `PROVIDER` is refused, not defaulted | `ConfigError`, "Refusing to guess" |
| 4xx not retried | 1 call for `MAX_RETRIES=3` |
| 5xx retried, then falls back | 2 calls to the failing host, then served by the fallback |
| Unconfigured fallback skipped, not retried | Chain `qwen,openai` → served by `openai` |
| Final error names every provider tried | Contains both `atk` and `qwen: not configured` |
| Malformed response reported clearly | Names `choices[0].message.content` |
| Anthropic uses its own wire format | `POST /v1/messages`, `x-api-key`, `system` in its own field |
| Unreported cost stays `None` | Asserted `cost_usd is None`, never `0.0` |

### End-to-end, the example script itself

Run as a subprocess against a local OpenAI-compatible server, once per provider:

```
PROVIDER=atk     exit=0   served by atk / local-test · 412 in, 37 out · cost not reported
PROVIDER=openai  exit=0   served by openai / local-test · 412 in, 37 out · cost not reported
```

Identical output, identical code, different provider — configuration alone.

```
$ python3 example_summarise_tool_output.py --dry-run --file build.log
PROVIDER=atk
provider not configured: PROVIDER=atk needs ATK_API_KEY, ATK_BASE_URL, ATK_MODEL. ...
input 1100 chars -> prompt 1443 chars
```

## Not verified, and not claimed

- **Anything about ATK, by this repository.** The one live call on record is the reviewer's,
  with their credential. **I have not run against ATK and do not claim to have.**
- **MCP.** Endpoint and header come from the official docs. No handshake performed.
- **Other models, other providers.** 52 models are listed; one was called, once, by the reviewer.
- **Any cost or token saving.** This code moves requests. It does not compress, cache or
  optimise, and **nothing here may be cited as evidence of a saving.** The one live call reported
  no USD cost, which is not the same as free.
- **Latency, throughput, concurrency, billing.** Not measured.
- **Streaming, tool calls, batching.** Not implemented; a tool-only reply now fails loudly.
- **`TOKEN_BUDGET_PER_RUN` / `COST_BUDGET_USD_PER_RUN`.** Named in the contract, **not
  implemented**. Recorded as an open gap rather than silently ignored.
- **Integration with any registry candidate.** This is a standalone example. headroom, rtk and
  open-code-review are **not** wired in, and the claim that every integration must first have a
  common adapter is **not evidenced** — ATK's native MCP and OpenAI-compatible config may be
  enough for some assets.

## What would close the remaining gap

1. **A credential in the executor's environment**, so the author can reproduce the reviewer's
   live call rather than citing it. (Items 1 and 2 of the previous version are now **done** —
   by the reviewer.)
2. An MCP handshake against `https://api.aitokenking.com.tw/mcp`, to move that row from OBSERVED
   to TESTED.
3. One real integration with a registry candidate, which is the next asset and not this one.

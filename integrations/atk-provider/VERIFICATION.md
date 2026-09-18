# Verification record — ATK provider seam

**Updated:** 2026-09-18 (round 2, after the PR #4 review of `f2a2188`)
**Scope:** `integrations/atk-provider/`
**Status: every fix below is `IMPLEMENTED_PENDING_REVIEW`.**
**Live ATK verification: DONE by the executor on 2026-09-18 — see "Round 4" immediately below.**

**Only an independent reviewer marks a finding CLOSED** (`reviews/README.md`). An earlier version
of this file wrote "all three closed" about my own work, which was not mine to write. The one
exception is noted per-row: **P4-02 was marked closed by the R2 reviewer**, not by me.

## The official endpoint — and who established it

The first version of this file recorded that `api.aitokenking.com` did not resolve and concluded
the ATK path was unverified. **That hostname was wrong**: it was missing both `.tw` and `/api`.

**The PR #4 reviewer found the official entry point and tested it. I did not.** Attribution
matters here, so it is stated before the table — including whose credential it was:

| | |
|---|---|
| **Tested by** | the PR #4 reviewer, using **a credential the owner supplied and authorised for a minimal test** — corrected 2026-09-18 (P4-R2-03.4). It is not the reviewer's own account, and an earlier version of this file said it was |
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

## Review findings from `f2a2188` — status per finding

Each was reproduced before being changed, and each fix has a **runtime** regression test. The
reviewer's instruction was explicit: *do not let "no `sk-` in the source" stand in for a runtime
test*. So every credential case configures a real canary value, has a real server echo it, and
asserts on what a human would actually see.

### P4-01 — a rejecting server could leak the key (REPRODUCED → **partially fixed, then REOPENED as P4-R2-01**)

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

**Honest limit:** redaction only removes values it knows. A proxy that re-encodes a key can still
defeat it — which is why withholding, not redaction, is the default.

**This was not enough, and the R2 reviewer showed why.** See P4-R2-01 below: *this code itself*
truncated the body to 400 characters **before** redacting, so a key straddling the cut left its
prefix behind, and my test passed because it only checked for the whole key.

### P4-02 — a 200 with no text counted as success (REPRODUCED → **CLOSED by the R2 reviewer**)

`content: null` returned `Completion(text=None)`; the example printed `None` and exited 0. For a
summarising asset that is a failure reported as a success. Reproduced: `c.text is None` → `True`.

**Fix:** a non-empty string is required. `null`, whitespace-only, and wrong-typed content all
raise, and the message names `finish_reason` so the reader learns *why* it was empty. Same rule
for empty Anthropic `content` blocks. **Control:** genuine text still succeeds.

### P4-03 — Quick Start did not match the implementation (OBSERVED → **partly verified; the full-payload part REOPENED as P4-R2-02**)

1. `.env.example` carried the wrong base URL and the README only said "fill in key/model", so
   following it could not work. **Fixed** to the official URL, with the model-list command.
2. The README claimed `--dry-run` printed "the exact request" while the code printed 300-char
   excerpts. **Fixed both ways**: the default is now labelled a **PREVIEW**, and `--show-payload`
   prints the **complete JSON body**. Headers are never printed.

## Round 4 — LIVE, by the executor, on this head

**2026-09-18. The owner supplied a credential directly, and the live gap that had been open
since the first version of this file is now closed by me rather than cited from someone else.**

Environment only. **The key was never written to any file, never committed, and is not in this
repository.** It is now exposed in a chat transcript and **should be rotated.**

| Check | Result |
|---|---|
| DNS | `api.aitokenking.com.tw` → `47.239.51.250` |
| `GET /api/v1/models` | **HTTP 200, 52 models** — e.g. `claude-sonnet-4.6`, `claude-sonnet-5`, `gemini-3.1-pro-preview`, `gpt-5.6-terra` |
| Minimal chat through `atk_provider.py` | `"Reply with OK only."` → **`OK`**, 12 in / 4 out, `cost_usd` **`None`** |
| **The documented Quick Start, end to end** | `python3 example_summarise_tool_output.py --file sample-build.log` → a correct five-point summary naming `src/main.c:42` and `util.c:88`, **892 in / 115 out**, served by `atk / claude-sonnet-4.6` |

**This is the first time anything in this repository has been run against ATK by its author.**
It reproduces the reviewer's earlier result exactly (12 in / 4 out on the same probe), and
extends it: the **full documented path** works, not just a one-token probe.

**Still true, and not changed by this:** `cost_usd` is **not reported**, which is not the same as
free. **No saving or quality claim is made or evidenced.** No MCP handshake has been performed.
No other provider has been called live. Latency, throughput and billing are unmeasured.

The earlier rows in this file that read "no request has reached ATK" describe the state before
this round and are left as written.

## Round 3 — findings from the R2 review of `b3bd4e5`

### P4-R2-01 (P1, blocking) — the truncation was mine, not a proxy's

`_post` did `decode(...)[:400]` and *then* `redact(...)`. A 41-character key straddling the cut
could not be matched, so its prefix survived. **My own defence created the leak**, and
`test_the_opt_in_body_is_still_redacted` passed anyway because it asserted only that the *full*
key was absent.

Reviewer's replay on `b3bd4e5`: `client_truncation_leaks_prefix= True`.

**Fix:** redact the whole decoded body, **then** truncate what is already safe.
After: `client_truncation_leaks_prefix= False`.

**Tests now assert no 8-character run of the key survives**, for a key before the boundary,
straddling it, after it, and repeated. Plus a control that an ordinary error is still
diagnosable — redaction must not turn every failure into "something went wrong".

### P4-R2-02 (P2) — the preview was a second implementation

`--show-payload` built an OpenAI-shaped body itself. `AnthropicProvider` hoists `system` to a
top-level field and adds `max_tokens`, so the "complete request body" was wrong for that path.

Reviewer's replay on `b3bd4e5`:
`preview_keys= ['messages','model']` vs `wire_keys= ['max_tokens','messages','model','system']`.

**Fix:** `build_payload()` on each adapter is the single source, used by both `complete()` and
the preview. A test asserts preview == the body the local server actually received, for both
wire formats. With no provider configured it **declines** rather than guessing.
After: `anthropic_preview_matches_wire= True`.

### P4-R2-03 (P2) — documentation and status

All six sub-items addressed: closure authority (above), stale PR body, README ordering
(`.env` loaded *before* `curl`, alias caveat stated as Python-side only), a committed
`sample-build.log` so the Quick Start needs no file of your own, credential attribution,
test arithmetic (below), and the MCP block relabelled as conceptual with the `${VAR}`
expansion caveat.

### The test arithmetic, corrected

An earlier version said "10 failures / 1 error, 2 pass" for 11 tests — which does not add up, as
the reviewer noted. Measured against the real `f2a2188` source:

```
Ran 11 tests — FAILED (failures=12, errors=1)
```

**11 test methods: 10 fail, 1 passes** (the deliberate control). `unittest` prints `failures=12`
because one method uses `subTest` over four sub-cases and reports each separately. The earlier
"2 pass" was simply wrong.

## What was verified, and how

All tests run against a **real HTTP server on localhost** — a real socket, a real request, a real
parse. What is synthetic is the *provider*, not the transport. URL construction, headers, JSON
body, status handling, retries and fallback are genuinely exercised.

```
$ python3 -m unittest test_atk_provider
Ran 33 tests — OK
```

Against `f2a2188`, the 11 PR #4 test methods give **10 failing, 1 passing** — the pass being the
deliberate control (`test_real_text_still_succeeds`) — a fix that rejected everything would be its own
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

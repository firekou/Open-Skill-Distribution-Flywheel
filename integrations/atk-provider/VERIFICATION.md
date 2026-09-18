# Verification record — ATK provider seam

**Date:** 2026-09-18 · **Scope:** `integrations/atk-provider/`
**Status: VERIFIED OFFLINE. NOT verified against ATK.**

## The headline gap, stated first

**No request in this record has ever reached ATK.** Two independent reasons:

1. **No ATK credential exists in the build environment.** `ATK_API_KEY` is unset, and none was
   requested or created.
2. **`api.aitokenking.com` does not resolve from the build environment.**

```
$ python3 -c "import socket; print(socket.gethostbyname('api.aitokenking.com'))"
socket.gaierror: [Errno -5] No address associated with hostname

$ curl -sS --max-time 15 https://api.aitokenking.com/v1/models
curl: (56) CONNECT tunnel failed, response 502

# control, same network, same moment:
$ python3 -c "import socket; print(socket.gethostbyname('api.openai.com'))"
172.66.0.243
```

`api.openai.com` resolves from the same shell, so this is **not** a blanket network block. It
may be egress policy on this host, or the hostname in the contract document may be wrong or not
yet live. **This record does not decide which**, and the value in `.env.example` is carried over
from `ATK_ROUTING_INTEGRATION.md` §3 and is marked there as unverified.

**Therefore `ATK_BASE_URL`, a real `ATK_MODEL` id, and ATK's response shape are all UNVERIFIED.**
The adapter assumes ATK is OpenAI-compatible because the contract document says so. If it is not,
the ATK path breaks and every other provider keeps working.

## What was verified, and how

All tests run against a **real HTTP server on localhost** — a real socket, a real request, a real
parse. What is synthetic is the *provider*, not the transport. URL construction, headers, JSON
body, status handling, retries and fallback are genuinely exercised.

```
$ python3 -m unittest test_atk_provider
Ran 14 tests — OK
```

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

- **Any ATK behaviour at all.** See above.
- **Any real provider.** No request has gone to OpenAI, Anthropic or anyone else. The wire
  formats follow published API shapes; that they match today's live APIs is **untested here**.
- **Any cost or token saving.** This code moves requests. It does not compress, cache or
  optimise, and **nothing in this asset may be cited as evidence of a saving.**
- **Latency, throughput, concurrency.** Not measured.
- **Streaming, tool calls, batching.** Not implemented.
- **`TOKEN_BUDGET_PER_RUN` / `COST_BUDGET_USD_PER_RUN`.** Named in the contract, **not
  implemented**. A caller setting them today gets no enforcement. Recorded as an open gap rather
  than silently ignored.

## What would close the live gap

1. Confirm the real ATK base URL and one valid model id.
2. One credential with a small budget.
3. Re-run `example_summarise_tool_output.py` against it and append the transcript here.

Until then this is **a verified client with an unverified counterparty.**

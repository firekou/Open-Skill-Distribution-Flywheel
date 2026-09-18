# Headroom + ATK: cut a 100 KB deploy log before it reaches the model

**Verified 2026-09-18** against live ATK. Two measurements below, kept apart on purpose: a live
run whose token counts came from ATK, and an offline check anyone can re-run right now with no
key and no cost. Raw output in `evidence/`.

| | |
|---|---|
| **Problem** | An agent reads a 1,200-line deploy log. You pay for every token of it, and the one line you need is buried at line 947 |
| **Tool** | [headroom](https://github.com/headroomlabs-ai/headroom) `0.37.0` · Apache-2.0 · `pip install "headroom-ai[proxy]"` · compression runs locally, no content leaves your machine |
| **ATK integration** | **Configuration only.** No fork, no adapter, no SDK. |
| **Live measurement** | **40,589 → 25,525 prompt tokens (37.1% fewer)**, and both paths still returned the exact migration name and SQLSTATE |
| **Offline measurement** | **111,357 → 94,578 characters (15.1% fewer)** reaching the upstream, needle intact — reproducible without a key |

## The whole integration

```bash
pip install "headroom-ai[proxy]"
headroom proxy --port 8787 --no-http2
```

Then send requests to the proxy and name ATK as the upstream **per request**:

```bash
curl -sS http://127.0.0.1:8787/v1/chat/completions \
  -H "Authorization: Bearer $ATK_API_KEY" \
  -H "Content-Type: application/json" \
  -H "x-headroom-base-url: https://api.aitokenking.com.tw/api" \
  -d '{"model":"claude-sonnet-4.6","messages":[{"role":"user","content":"..."}]}'
```

That is the entire integration. **Two config values, no code.**

### The three things that will trip you up

**1. Setting `OPENAI_BASE_URL` for the proxy does NOT route it to ATK.** This is the mistake worth
writing down, because it fails in a way that looks like an ATK problem and is not:

```
{"error":{"message":"Incorrect API key provided: sk-xxxxx***…xxxx.
  You can find your API key at https://platform.openai.com/account/api-keys."}}
```

Headroom resolves the provider itself (it uses LiteLLM internally), so your ATK key went to
**OpenAI**, which correctly rejected it. (The key fragment above is masked here; OpenAI
 echoes real prefix and suffix characters of whatever key you sent, so do not paste that error
 anywhere public verbatim.) Use the `x-headroom-base-url` header.

**2. The header takes the base WITHOUT `/v1`.** Headroom appends `/v1/chat/completions`. Give it
`https://api.aitokenking.com.tw/api/v1` and ATK answers:

```
{"code":404,"message":"接口不存在: /api/v1/v1/chat/completions"}
```

Correct value: `https://api.aitokenking.com.tw/api`

**3. A loopback or private-network upstream is refused *silently*.** headroom 0.37.0 checks the
client-named base URL against an SSRF guard (its CVE-2026-77775 fix). If the host resolves to
loopback, RFC1918 or link-local space it **falls back to the provider it resolved itself** — so
you get the same misleading OpenAI 401 as in gotcha 1.

The source contains a warning string, `ignoring unsafe x-headroom-base-url override`, but we
measured that **it is not printed at default verbosity** — 0 occurrences in the proxy's combined
stdout/stderr across a run that triggered the fallback. Grepping for it to diagnose will find
nothing. The fallback really is silent.

It affects you only when pointing at something internal, such as a test stub: allowlist it with
`HEADROOM_ALLOWED_BASE_URLS=http://127.0.0.1:PORT`. A public host like ATK needs nothing.
`local_check.py` sets it, and fails loudly if the override is ignored anyway.

## Measurement 1 — live, against ATK

One 1,200-line deploy log, same model (`claude-sonnet-4.6`), same prompt, same moment. A single
`FATAL` line at index 947 carries the answer. Token counts are **ATK's own `usage` field**, not an
estimate. Raw responses: `evidence/ab_summary.json`, `evidence/ab_needle.json`.

### Task A — summarise the log

| Path | prompt tokens | |
|---|--:|---|
| Direct to ATK | 40,572 | |
| Via headroom | 29,781 | **26.6% fewer** |

**Neither summary mentioned the FATAL line.** That is not a compression failure — the *direct*
path missed it too. A "five bullet summary" of 1,200 lines is simply the wrong instrument for
finding one unique event, with or without compression. Recorded because it is the result.

### Task B — ask the actual question

*"Did any database migration fail? Give the migration name and the exact SQLSTATE code."*

| Path | prompt tokens | migration name | SQLSTATE | |
|---|--:|:---:|:---:|---|
| Direct to ATK | 40,589 | ✅ `0042_add_tenant_id` | ✅ `42701` | |
| Via headroom | 25,525 | ✅ `0042_add_tenant_id` | ✅ `42701` | **37.1% fewer** |

**The compressed path answered identically at 63% of the prompt cost.**

## Measurement 2 — offline, reproducible by anyone

`local_check.py` starts the proxy and a stub upstream on localhost, sends the same needle prompt
both ways, and measures **the body the upstream actually receives**. No key, no model call, no
cost. Output committed at `evidence/local_check.txt`:

```
log        : deploy.log — 1200 lines, 111262 bytes
direct     : 111357 chars reached the upstream
via proxy  :  94578 chars reached the upstream  (15.1% fewer)
needle '0042_add_tenant_id': present after compression
needle '42701': present after compression
PASS
```

The same file also records the **negative control** — the same records as JSON lines, where the
reduction is exactly 0.0%. Read *Will this help your logs?* below before adopting.

**15.1% here versus 37.1% above is not a contradiction and not a correction of either number.**
They are different metrics (characters on the wire vs. ATK-counted prompt tokens) on different
bytes (see *What was not preserved*). The offline figure is the conservative one and the only one
you can check without spending anything.

## What these numbers are not

- **One workload, one model, two calls.** Not a benchmark. See *Will this help your logs?* below —
  the honest answer for a large class of logs is "not at all".
- **No cost figure.** ATK reported `cost_usd: null` on every call. Fewer tokens is not
  automatically less money, and this asset makes **no saving claim in currency**.
- **No quality benchmark.** Two prompts, one needle. Headroom publishes its own quality
  benchmarks; those are theirs, not reproduced here.
- **A partial honest failure:** in task A, the needle was lost by **both** paths.
- **What was not preserved:** the live run's `deploy.log` was generated in a scratch directory and
  not kept. `make_log.py` in this directory is a deterministic reconstruction of that generator —
  same shape, same 1,200 lines, same needle at index 947, but **not the same bytes** (it emits
  111,262 bytes; the live run's log was ~101 KB). So `ab_test.py` re-run today will produce its
  own token counts close to, but not identical to, the table above. Stated rather than papered
  over; the offline check exists because it *is* exactly reproducible.

## Will this help YOUR logs? Often the answer is no — check before adopting

**How it actually saves.** We diffed the body our stub upstream received against the body we sent.
headroom is doing **shared-prefix factoring across lines**: it hoists the repeated part of the
timestamp into a header line and rewrites every line relative to it —

```
2026-09-18T11
00:00Z WARN  auth-svc    connection pool at 90%, queue depth 3
00:01Z ERROR cache-warm  request failed: connection reset by peer after 3 attempts
```

**It drops no lines** (1,200 in, 1,200 out). That is exactly why the needle always survives — and
also exactly why the saving comes only from textual redundancy, not from any judgement about what
matters.

**So the saving collapses to zero when the redundancy is not there.** Measured on this machine,
same date, same proxy:

| payload | reduction | needle |
|---|--:|:--|
| Plain-text deploy log, uniform timestamp prefix (the sample here) | **15.1%** | survived |
| The *same records* re-emitted as JSON lines | **0.0%** — byte-for-byte pass-through | survived |
| Those same JSON records flattened back to plain text | **27.3%** | survived |

**Structured JSON logging is extremely common for server logs.** If that is what your agent reads,
this tool will do nothing for you. It will not corrupt anything — in every zero-compression case
it passed the payload through unmodified — but you would be adding a process for no benefit.

**So check your own log first. One command, no key, about a minute:**

```bash
python3 local_check.py --log /path/to/your.log --needle "the line that must survive"
```

`--needle` is repeatable. **Exit 0** = it shrank and every needle survived. **Exit 3** = it did not
shrink at all; nothing lost, nothing gained, do not bother. **Exit 1** = a needle was lost; do not
adopt for that payload.

**One thing we did not test:** the proxy's own banner reports `Code-Aware: NOT INSTALLED (pip
install headroom-ai[code])`. There is an optional extra we never installed, and every number on
this page was measured without it. It may change results for code-shaped payloads; we do not know.

## Reproduce it

```bash
pip install "headroom-ai[proxy]"
python3 make_log.py > deploy.log      # deterministic; md5 0ad9194a489136baa931881b78374cf7
python3 local_check.py                # offline, no key, no cost — takes ~1 min
```

`local_check.py` and `ab_test.py` look for `deploy.log` **next to the script**, not in your current
directory, so `python3 path/to/local_check.py` works from anywhere. Python 3.11 is what we ran;
both scripts are stdlib-only apart from headroom itself.

To repeat the live measurement (**this spends real tokens**):

```bash
headroom proxy --port 8787 --no-http2 &
ATK_API_KEY=sk-... python3 ab_test.py
```

`ab_test.py` refuses to run without `ATK_API_KEY` and substitutes no mock. Pass the key in the
environment only — never on the command line, never in a file in this repo.

## There is a second, official route we did NOT test

While checking how discoverable this asset is, an independent search turned up something that
belongs here: **LiteLLM ships an official Headroom guardrail** —
<https://docs.litellm.ai/docs/proxy/headroom>. Verified at the source on 2026-09-18: the guardrail
is named `headroom-compression`, configured with `guardrail: headroom` / `mode: pre_call` /
`api_base`, enabled per request with `"guardrails": ["headroom-compression"]` (or
`litellm_metadata.guardrails` in Anthropic format), with `x-headroom-bypass: true` as a
per-request opt-out.

If you already run LiteLLM as your gateway, that is probably the route you want, and it gives you
a bypass header this one does not. **We did not test it and it carries no measured numbers on the
LiteLLM page** — stated so the choice is yours rather than ours. What is measured here is the
direct route: your client to `headroom proxy`, `x-headroom-base-url` naming the upstream.

## Why the numbers here are taken at the upstream, not from the proxy

The same search surfaced a documented case of a compression proxy whose own savings dashboard
reported a large reduction while it actually sent *more* to the upstream than the uncompressed
request. We have not reproduced that case and are not repeating the accusation as fact — but it
is the reason both measurements here are taken **outside** the proxy: the live numbers are ATK's
`usage` field, and the offline numbers are the bytes a stub upstream actually received.
**No number on this page comes from headroom's own reporting.**

## Switching away, and removing ATK

The `x-headroom-base-url` header names the upstream **per request**. Point it at any
OpenAI-compatible endpoint — another provider, a gateway, a local server — and nothing else
changes. Drop the header and headroom routes by its own provider resolution. Stop the proxy and
your client talks to the provider directly.

**ATK is one value in one header here.** That is as replaceable as an integration gets.

## Licence and attribution

headroom is **Apache-2.0** (`headroomlabs-ai/headroom`). **No headroom code is copied into this
repository** — this directory contains only configuration, a test harness and measurements.
Install it from PyPI. Its own docs: <https://docs.headroomlabs.ai/docs>.

## Files

| File | |
|---|---|
| `make_log.py` | deterministic log generator (stdlib only) |
| `local_check.py` | offline verification **and preflight for your own log** (`--log`, `--needle`): proxy routing, compression, needle survival — no key |
| `ab_test.py` | the live A/B against ATK — needs `ATK_API_KEY` |
| `evidence/ab_summary.json`, `evidence/ab_needle.json` | raw ATK responses from the live run |
| `evidence/local_check.txt` | output of the offline check, with versions and log md5 |

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
loopback, RFC1918 or link-local space it logs `ignoring unsafe x-headroom-base-url override` and
**falls back to the provider it resolved itself** — so you get the same misleading OpenAI 401 as
in gotcha 1. It affects you only when pointing at something internal, such as a test stub:
allowlist it with `HEADROOM_ALLOWED_BASE_URLS=http://127.0.0.1:PORT`. A public host like ATK needs
nothing. `local_check.py` does exactly this, and fails loudly if the override is ignored.

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
log        : 1200 lines, 111262 bytes
direct     : 111357 chars reached the upstream
via proxy  :  94578 chars reached the upstream  (15.1% fewer)
needle '0042_add_tenant_id': present after compression
needle '42701': present after compression
PASS
```

**15.1% here versus 37.1% above is not a contradiction and not a correction of either number.**
They are different metrics (characters on the wire vs. ATK-counted prompt tokens) on different
bytes (see *What was not preserved*). The offline figure is the conservative one and the only one
you can check without spending anything.

## What these numbers are not

- **One workload, one model, two calls.** Not a benchmark. Your logs compress differently; a log
  of near-identical lines compresses far better than prose.
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

## Reproduce it

```bash
pip install "headroom-ai[proxy]"
python3 make_log.py > deploy.log      # deterministic; md5 0ad9194a489136baa931881b78374cf7
python3 local_check.py                # offline, no key, no cost — takes ~1 min
```

To repeat the live measurement (**this spends real tokens**):

```bash
headroom proxy --port 8787 --no-http2 &
ATK_API_KEY=sk-... python3 ab_test.py
```

`ab_test.py` refuses to run without `ATK_API_KEY` and substitutes no mock. Pass the key in the
environment only — never on the command line, never in a file in this repo.

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
| `local_check.py` | offline verification: proxy routing, compression, needle survival — no key |
| `ab_test.py` | the live A/B against ATK — needs `ATK_API_KEY` |
| `evidence/ab_summary.json`, `evidence/ab_needle.json` | raw ATK responses from the live run |
| `evidence/local_check.txt` | output of the offline check, with versions and log md5 |

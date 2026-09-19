# Headroom + ATK: cut a 100 KB deploy log before it reaches the model

**Verified 2026-09-18** against live ATK. Two measurements below, kept apart on purpose: a live
run whose token counts came from ATK, and an offline check anyone can re-run right now with no
key and no cost. Raw output in `evidence/`.

| | |
|---|---|
| **Problem** | An agent reads a 1,200-line deploy log. You pay for every token of it, and the one line you need is buried at line 947 |
| **Tool** | [headroom](https://github.com/headroomlabs-ai/headroom) · Apache-2.0 · `pip install "headroom-ai[proxy]==0.37.0"` · compression runs locally, no content leaves your machine |
| **ATK integration** | **Configuration only.** No fork, no adapter, no SDK. |
| **Live measurement** | **40,589 → 25,525 prompt tokens (37.1% fewer)**, and both paths still returned the exact migration name and SQLSTATE |
| **Offline measurement** | **111,357 → 94,578 characters (15.1% fewer)** reaching the upstream, needle intact — reproducible without a key |

## The whole integration

```bash
pip install "headroom-ai[proxy]==0.37.0"    # the version every number here was measured on
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

**3. A loopback or private-network upstream is refused, and the explanation is in a log file you
would not think to open.** headroom 0.37.0 checks the client-named base URL against an SSRF guard
(its CVE-2026-77775 fix). If the host resolves to loopback, RFC1918 or link-local space it drops
your override and **falls back to the provider it resolved itself** — so you get the same
misleading OpenAI 401 as in gotcha 1.

It does log the reason. Measured on 2026-09-19, on a run that triggered the fallback:

| where you would look | occurrences of `ignoring unsafe` |
|---|--:|
| the proxy's stdout / stderr | 0 |
| the file you passed to `--log-file` | 0 |
| `~/.headroom/logs/proxy.log` | **3** |

`_setup_file_logging` attaches a rotating file handler to the `headroom` logger and sets
`propagate = False`, so the record goes to that file and nowhere else; `--log-file` is a separate
request/response stream. **Check `~/.headroom/logs/proxy.log` — that is where the answer is.**

> **Correction.** An earlier version of this page said the fallback was "silent" and that the
> warning "is not printed", based on finding 0 occurrences in the two places above. That was
> wrong: we had not looked in the third place. The claim is withdrawn and replaced by the table.

It affects you only when pointing at something internal, such as a test stub: allowlist it with
`HEADROOM_ALLOWED_BASE_URLS=http://127.0.0.1:PORT`. A public host like ATK needs nothing.
`local_check.py` sets it, and fails loudly if the override is ignored anyway.

## Measurement 1 — live, against ATK

One 1,200-line deploy log, same model (`claude-sonnet-4.6`), same prompt, same moment. A single
`FATAL` line at index 947 carries the answer. Token counts are **ATK's own `usage` field**, not an
estimate. Recorded excerpts — the `usage` block and the answer text only, not the full HTTP
response: `evidence/ab_summary.json`, `evidence/ab_needle.json`.

### Task A — summarise the log

| Path | prompt tokens | |
|---|--:|---|
| Direct to ATK | 40,572 | |
| Via headroom | 29,781 | **26.6% fewer** |

**Neither summary mentioned the FATAL line.** The *direct* path missed it too, so the compression
is not the whole explanation — but "both failed" does not prove compression cost nothing here
either, and we cannot separate the two from one pair of calls. What we can say: on this prompt,
asking for five bullets did not surface the line on either path, and asking the specific question
surfaced it on both. Recorded because it is the result.

### Task B — ask the actual question

*"Did any database migration fail? Give the migration name and the exact SQLSTATE code."*

| Path | prompt tokens | migration name | SQLSTATE | |
|---|--:|:---:|:---:|---|
| Direct to ATK | 40,589 | ✅ `0042_add_tenant_id` | ✅ `42701` | |
| Via headroom | 25,525 | ✅ `0042_add_tenant_id` | ✅ `42701` | **37.1% fewer** |

**The compressed path answered identically on 63% of the prompt tokens** — tokens, not cost. We
have no currency figure (see below), so "cost" was the wrong word and is withdrawn.

**Scope of this table:** one log, one model, one prompt, one moment, on 2026-09-18. It is a
recorded historical case, not a result this round re-measured and not a guarantee for any other
payload. The exact input file was not preserved (see *What was not preserved*), so it cannot be
re-run identically even by us.

## Measurement 2 — offline, reproducible by anyone

`local_check.py` starts the proxy and a stub upstream on localhost, sends the same needle prompt
both ways, and measures **the body the upstream actually receives**. No key, no model call, no
cost. Output committed at `evidence/local_check.txt`:

```
log        : deploy.log — 1200 lines, 111262 bytes
direct     : 111357 chars reached the upstream
via proxy  : 94578 chars reached the upstream  (15.1% fewer)
needle #1 (18 chars): present after the proxy
needle #2 (5 chars): present after the proxy
PASS: 16779 fewer characters (15.1%) and every needle survived
exit=0
```

(Copied verbatim from `evidence/local_check.txt`. Note what it does **not** contain: the needle
text. Needles are reported by position and length — that is the point of the next section.)

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

**It dropped no lines in the cases we ran** (1,200 in, 1,200 out; the needle survived in all six
payloads we tested, including the ones where nothing was compressed). That is consistent with the
saving coming from textual redundancy rather than from any judgement about what matters — but six
payloads on one version is not a guarantee that a needle always survives, and we do not claim one.
`local_check.py` exists precisely so you check your own payload instead of trusting that.

**So the saving collapses to zero when the redundancy is not there.** Measured on this machine,
same date, same proxy:

| payload | reduction | needle |
|---|--:|:--|
| Plain-text deploy log, uniform timestamp prefix (the sample here) | **15.1%** | survived |
| The *same records* re-emitted as JSON lines | **0.0%** — byte-for-byte pass-through | survived |
| Those same JSON records flattened back to plain text | **27.3%** | survived |

**Structured JSON logging is extremely common for server logs.** On the JSON payload *we* tested,
headroom 0.37.0 returned it unmodified — no benefit, and no damage either. We tested one JSON
shape, so treat this as "check yours first", not as "JSON never compresses". Run the preflight
below; that is the whole point of it.

**So check your own log first. One command, no key, about a minute:**

```bash
python3 local_check.py --log /path/to/your.log --needle "the line that must survive"
```

`--needle` is repeatable, and the output names needles by position, not content, so it is safe to
paste into a bug report.

| exit | meaning |
|--:|---|
| **0** | it shrank and every needle survived |
| **3** | no size benefit. Three different cases, and the message says which: returned unchanged; rewritten but the same length (content changed — check that is acceptable to you); or **larger than the original** |
| **1** | a needle was lost. Do not adopt for that payload |
| **2** | misuse — no needle given, an empty needle, or a needle that is not in the log to begin with |

Only the first case under exit 3 is "nothing happened". A same-length rewrite changed your payload,
and an inflated one sent more upstream than sending it directly.

**One thing we did not test:** the proxy's own banner reports `Code-Aware: NOT INSTALLED (pip
install headroom-ai[code])`. There is an optional extra we never installed, and every number on
this page was measured without it. It may change results for code-shaped payloads; we do not know.

## Reproduce it

**This asset is not on `main` yet.** It lives on the branch below, in an open Draft pull request.
Check that branch out explicitly; a default `git clone` will not contain these files.

```bash
git clone https://github.com/firekou/Open-Skill-Distribution-Flywheel
cd Open-Skill-Distribution-Flywheel
git checkout claude/atk-headroom-adoption          # NOT on main yet — PR #5, Draft

python3 -m venv .venv && . .venv/bin/activate      # Python 3.11 is what we ran
pip install "headroom-ai[proxy]==0.37.0"

cd integrations/headroom-atk                       # run from this directory
python3 make_log.py > deploy.log                   # deterministic; md5 0ad9194a489136baa931881b78374cf7
python3 local_check.py                             # offline, no key, no cost — about a minute
python3 test_local_check.py                        # 29 unit tests, also offline
```

`local_check.py` and `ab_test.py` resolve `deploy.log` **next to the script**, not in your current
directory, so an absolute `python3 /path/to/local_check.py` also works — but `make_log.py` writes
wherever your shell is, which is why the `cd` above is not optional. Apart from headroom itself
both scripts are stdlib-only.

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

## Found a problem, or used it?

Open an issue: <https://github.com/firekou/Open-Skill-Distribution-Flywheel/issues>. Bugs in
headroom itself belong upstream at <https://github.com/headroomlabs-ai/headroom/issues>.

There is **no telemetry here** — nothing phones home, nothing is logged, nothing observes you. So
an issue is the only way we would ever know this helped or failed.

`local_check.py` output is written to be pasteable: it prints sizes, exit status, the log's file
name and needles identified by position and length — **never the needle text and never your log**.
(`--show-needles` turns that off for your own terminal; do not use it for output you intend to
share.) If you would rather not paste even that, this is all we need:

```
headroom version:
OS / Python:
payload shape:      plain text | JSON lines | mixed | other
size:               <lines>, <bytes>
local_check exit:   0 | 1 | 2 | 3
reduction:          <percent>
used ATK?           yes | no | other upstream
```

**Never paste an API key or a real log line.**

**Third-party reports to date: none.**

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
| `evidence/ab_summary.json`, `evidence/ab_needle.json` | `usage` and answer-text excerpts from the live run — not full HTTP responses |
| `test_local_check.py` | 29 offline unit tests: the adoption verdict, output privacy, and the error body never being shown |
| `evidence/local_check.txt` | output of the offline check, with versions and log md5 |
| `evidence/pr5-r2/controls.txt` | positive and negative controls for the two defects fixed in review round 1 |
| `evidence/pr5-r3/controls.txt` | controls for review round 2: the partial-echo leak, output privacy, and the withdrawn logging root cause |
| `evidence/pr5-r4/controls.txt` | controls for review round 3: the document/evidence mismatches, and misuse paths returning exit 2 |
| `evidence/SEARCH_BASELINE.md` | the fixed queries for a discoverability re-test, and why the first run cannot be repeated |
| `offering/` | free and paid service samples, unit economics — the paid one is an **unapproved draft** |
| `upstream/HEADROOM_FEEDBACK_DRAFT.md` | three gotchas written up for the headroom maintainers, with duplicate check — **not sent** |
| `DISTRIBUTION.md` | sharing drafts, distribution list, proposed About/topics — **nothing published** |

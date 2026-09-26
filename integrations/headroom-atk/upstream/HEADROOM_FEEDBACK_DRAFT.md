# Upstream feedback for `headroomlabs-ai/headroom` — DRAFT, 待核准、未送出

> **Status: NOT SENT.** No issue, discussion, comment or PR has been opened on the upstream
> repository. Sending any of this needs separate owner authorisation. Nothing below has been
> communicated to the headroom maintainers.

**Version these were found on:** `headroom-ai` **0.37.0**, installed from PyPI on 2026-09-18.
At time of writing 0.37.0 is the **latest** published release (PyPI upload 2026-08-27T21:50:58),
so none of this is a stale-version report. Python 3.11.15, Linux.

**Duplicate check performed 2026-09-18** by searching the upstream issue tracker for
`x-headroom-base-url`, `OPENAI_BASE_URL`, and `unsafe upstream / loopback / SSRF / "ignoring
unsafe"`. Findings, and how they change what is proposed below:

| Existing issue | State | Effect on our items |
|---|---|---|
| [#1503](https://github.com/headroomlabs-ai/headroom/issues/1503) "Dedicated OpenAI handlers ignore `x-headroom-base-url` (breaks OpenAI-compatible gateways like LiteLLM/CPA/vLLM)" | Closed | **This is the parent of items 1 and 2.** The mechanism it asks for exists in 0.37.0 (`_resolve_openai_upstream_base`). Item 1 is now a documentation gap, not a bug. Item 2 is a behaviour the issue explicitly did **not** cover. |
| [#3346](https://github.com/headroomlabs-ai/headroom/issues/3346) "Different `x-headroom-base-url` gateways share semantic cached responses" | Open | Different defect (cache keying). Unrelated to these three. |
| [#3336](https://github.com/headroomlabs-ai/headroom/issues/3336) connectivity probe routed to the default vendor, asks for a vendor pin / fail-closed option | Open | **Adjacent to item 3** — same underlying discomfort with silent default-vendor routing. Item 3 should be posted as a comment on #3336 rather than as a new issue, unless a maintainer prefers otherwise. |
| [#3280](https://github.com/headroomlabs-ai/headroom/issues/3280) SSRF via Vertex location path | Closed | The guard item 3 concerns is *working as designed*; item 3 is about its diagnosability, not its correctness. |

**Recommended disposition:** items 1 and 2 as **one documentation issue** (or a docs PR), and item 3
as a **comment on #3336**. That is two touches on the tracker, not three new issues.

---

## Item 1 — `OPENAI_BASE_URL` does not redirect the proxy's own upstream (documentation)

**Not a bug.** Recorded because it costs an hour and produces an error that points at the wrong
party.

**Expected (by the user):** exporting `OPENAI_BASE_URL` before `headroom proxy` makes the proxy
forward to that gateway.
**Actual:** the proxy resolves the provider itself, so a request with a non-OpenAI key is sent to
`api.openai.com`, which returns

```
401 {"error":{"message":"Incorrect API key provided: <your key, partly echoed> ...
     You can find your API key at https://platform.openai.com/account/api-keys."}}
```

The failure names OpenAI, so the natural conclusion is "my gateway is broken" or "my key is
invalid", when in fact the request never reached the gateway. **It also echoes part of the
credential back to the user's terminal**, which matters for anyone who then pastes the error into
a bug report.

**Minimal reproduction, no secret required:**

```bash
pip install "headroom-ai[proxy]==0.37.0"
OPENAI_BASE_URL=https://your-gateway.example/api headroom proxy --port 8787 --no-http2 &
curl -sS http://127.0.0.1:8787/v1/chat/completions \
  -H "Authorization: Bearer not-a-real-key" -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}'
# -> 401 from api.openai.com, not from your-gateway.example
```

**Suggestion:** one line in the proxy docs — *"`OPENAI_BASE_URL` configures clients, not the
proxy's upstream. To name a non-OpenAI upstream, send `x-headroom-base-url` per request."* The
correct answer already exists (#1503); only the signpost is missing.

---

## Item 2 — `x-headroom-base-url` silently accepts a value ending in `/v1` and produces `/v1/v1/…`

**Explicitly outside the scope of #1503**, which noted the header is expected to carry the base
without `/v1` but documented no guidance and added no validation.

`_resolve_openai_upstream_base` (`headroom/proxy/handlers/openai.py`, ~line 369) preserves the
path component of the supplied URL, then the handler appends `/v1/chat/completions`. A user who
copies their gateway's advertised OpenAI-compatible endpoint — which conventionally *does* end in
`/v1`, because that is what every SDK's `base_url` takes — gets a doubled segment:

```
x-headroom-base-url: https://gateway.example/api/v1
  -> POST https://gateway.example/api/v1/v1/chat/completions
  -> 404 from the gateway
```

**Expected:** either the same value that works as an SDK `base_url`, or a clear error.
**Actual:** a 404 from the gateway, which again reads as the gateway's fault.

This is a sharp edge rather than a defect: the header's contract is "origin plus optional
sub-path", while the value users have to hand is "SDK base URL". Those differ by exactly `/v1`.

**Suggestion, in preference order:**
1. Document the contract next to the header, with one wrong and one right example.
2. And/or log a warning when the supplied path already ends in `/v1` while the handler is about to
   append `/v1` — cheap, and catches the whole class.

We are **not** proposing that headroom strip `/v1` automatically: a gateway legitimately served
from a `/v1` sub-path would break. Documentation and a warning are the safe fixes.

---

## Item 3 — a refused upstream is diagnosable only in a log file nobody is looking at

**Correction first.** An earlier version of this draft claimed the warning "reaches nothing"
because the root logger has no handlers. **That was wrong on both counts and is withdrawn.**
Python's `logging.lastResort` writes WARNING to stderr even with no handlers configured, so the
premise was invalid; and re-checking empirically showed the message is not lost at all.

**What actually happens** (measured on 0.37.0, 2026-09-19). When `x-headroom-base-url` names a
host resolving to loopback / RFC1918 / link-local, `is_safe_upstream_url` refuses it (the
CVE-2026-77775 guard, working as intended), the override is dropped, and the request proceeds to
the **self-resolved provider**. The client therefore sees a 401 from OpenAI and has no signal that
its upstream was rejected rather than its key. The warning that would explain this goes to a third
location:

| destination | occurrences of `ignoring unsafe` |
|---|--:|
| proxy stdout + stderr | 0 |
| `--log-file <path>` | 0 |
| `~/.headroom/logs/proxy.log` | **3** |

```
2026-09-19 06:45:04,348 - headroom.proxy - WARNING - ignoring unsafe x-headroom-base-url override: 'http://127.0.0.1:47779'
```

**Mechanism, from the source rather than inferred.** `_setup_file_logging`
(`headroom/proxy/helpers.py`, ~1552) attaches a `RotatingFileHandler` to the `"headroom"` logger
pointing at `~/.headroom/logs/proxy.log`, and sets `headroom_logger.propagate = False` — with the
stated intent of avoiding duplicate writes when `wrap.py` redirects stderr to the same file. Both
consequences follow: `lastResort` never fires, because the chain does have a handler; and the
record never reaches root, so it is absent from stderr. `--log-file` is a separate
request/response log and does not receive it either.

**So this is not a logging bug.** The diagnostic exists and is correct. The gap is that the two
places an operator looks — the terminal, and the log file they explicitly passed on the command
line — are the two places it is not, and nothing in the 401 points at the third.

**Minimal reproduction, no secret required:**

```bash
headroom proxy --port 8787 --no-http2 --log-file /tmp/hr.log &
curl -sS http://127.0.0.1:8787/v1/chat/completions \
  -H "Authorization: Bearer not-a-real-key" -H "Content-Type: application/json" \
  -H "x-headroom-base-url: http://127.0.0.1:9999" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}'
# -> 401 from api.openai.com; nothing listening on :9999 is ever contacted
grep -c "ignoring unsafe" /tmp/hr.log                      # 0
grep -c "ignoring unsafe" ~/.headroom/logs/proxy.log       # >0
```

**Suggestion, in preference order:**
1. Surface the refusal on the response — a header such as
   `x-headroom-upstream-override: rejected` — so the caller can tell a security refusal from an
   authentication failure without reading any log.
2. Name `HEADROOM_ALLOWED_BASE_URLS` in the warning text, since a local stub or an on-prem gateway
   is exactly the case that hits this.
3. Document that `headroom` logger output goes to `~/.headroom/logs/proxy.log` and that
   `--log-file` is a different stream. That alone would have saved this round.
4. Consider fail-closed rather than falling back to the default vendor — the same request already
   made in **#3336**, and the reason this belongs there.

**What we are not claiming.** We did not test whether other `headroom.proxy` warnings behave the
same way, only this path. We did not test with an operator-supplied logging configuration, which
may change the destination. We tested 0.37.0 only.

## Tone and disclosure

If sent, these go as ordinary technical feedback with reproductions. ATK appears only where it is
needed to describe a reproduction — the same behaviour occurs with any OpenAI-compatible gateway,
and the reproductions above deliberately use `your-gateway.example` and a local stub instead. This
is not a promotional channel and must not be used as one.

**Reminder for whoever sends these:** the reproductions contain no credential. Do not paste a real
error body into the issue — per item 1, the provider echoes part of the key back.

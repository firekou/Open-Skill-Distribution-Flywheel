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

## Item 3 — a refused upstream falls back with no diagnostic reaching any handler

**This is the one we would most like a maintainer's view on**, and the one with a concrete root
cause rather than a documentation gap.

**Behaviour.** When `x-headroom-base-url` names a host resolving to loopback / RFC1918 /
link-local, `is_safe_upstream_url` correctly refuses it (the CVE-2026-77775 guard). The handler
then returns `None` and the request proceeds to the **self-resolved provider** — so the user sees
the same misleading OpenAI 401 as in item 1, and has no way to tell "my upstream was rejected"
apart from "my key is wrong".

The code does try to say so:

```python
logger.warning("ignoring unsafe x-headroom-base-url override: %r", raw_base_url)
```

**But that message reaches nothing.** Measured on 0.37.0:

| where | occurrences of `ignoring unsafe` |
|---|--:|
| proxy stdout + stderr | **0** |
| `--log-file` output | **0** |

**Root cause (this is the actionable part):** `logging.getLogger("headroom.proxy")` is at
`NOTSET`, inheriting effective level `WARNING`, and `isEnabledFor(WARNING)` is `True` — so the
record *is* created. The root logger, however, has **no handlers attached** in the proxy process,
so the record is discarded. The warning is not suppressed by level; it is emitted into nowhere.
Anyone who reads the source and greps their logs for that exact string — which is the obvious
debugging move — finds nothing and concludes the branch was never taken.

**Minimal reproduction, no secret required:**

```bash
# a stub that records what it receives, on 127.0.0.1
headroom proxy --port 8787 --no-http2 --log-file /tmp/hr.log &
curl -sS http://127.0.0.1:8787/v1/chat/completions \
  -H "Authorization: Bearer not-a-real-key" -H "Content-Type: application/json" \
  -H "x-headroom-base-url: http://127.0.0.1:9999" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}'
# -> 401 from api.openai.com; the stub on :9999 is never contacted
grep -c "ignoring unsafe" /tmp/hr.log   # -> 0
```

The workaround, once you know it exists, is `HEADROOM_ALLOWED_BASE_URLS`, which the code comment
names but which is easy to miss when the log line you are grepping for never appears.

**Impact.** Correctness is fine — the guard is doing its job, and we are not asking for it to be
relaxed. The cost is diagnostic: a security refusal is indistinguishable from an authentication
failure, and it is attributed to the wrong service.

**Suggestion, in preference order:**
1. Make the refusal observable — attach a handler so `headroom.proxy` warnings reach stderr and
   `--log-file`, or surface the refusal on the response (a header such as
   `x-headroom-upstream-override: rejected`).
2. Mention `HEADROOM_ALLOWED_BASE_URLS` in the message and in the docs, since local stubs and
   on-prem gateways are exactly the case that hits this.
3. Consider fail-closed as an option rather than falling back to the default vendor — which is
   the same request already made in **#3336**, and the reason we would post this there.

**What we are not claiming.** We did not test whether other `headroom.proxy` warnings are also
discarded; we observed this one path. We did not test any version other than 0.37.0, and we did
not test with an operator-supplied logging configuration, which may well attach handlers.

---

## Tone and disclosure

If sent, these go as ordinary technical feedback with reproductions. ATK appears only where it is
needed to describe a reproduction — the same behaviour occurs with any OpenAI-compatible gateway,
and the reproductions above deliberately use `your-gateway.example` and a local stub instead. This
is not a promotional channel and must not be used as one.

**Reminder for whoever sends these:** the reproductions contain no credential. Do not paste a real
error body into the issue — per item 1, the provider echoes part of the key back.

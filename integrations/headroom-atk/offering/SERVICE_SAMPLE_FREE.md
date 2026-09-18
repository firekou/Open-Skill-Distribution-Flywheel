# Sample deliverable — free tier, branded

**This is a reviewable sample, not a live service.** Nothing here is deployed, nothing takes
payment, and no request for this was received from anyone outside this repository. It exists so
the owner can read what a free-tier answer would actually look like before deciding whether to
offer one.

---

## The request this answers

> "Our coding agent reads huge deploy logs into its context. We pay for every token and only one
> or two lines matter. Is there something we can put in front of the model that cuts what we send
> without losing the line that matters? Prove it before we adopt it."

## ── Answer ──────────────────────────────────────────────────────────────────

**Yes: a local compression proxy. The one we verified is [headroom](https://github.com/headroomlabs-ai/headroom) 0.37.0, Apache-2.0.**

It sits between your client and your model provider, speaks the OpenAI chat-completions wire
format, compresses the prompt on your machine, and forwards it. Your client keeps talking to one
localhost URL; nothing about your provider setup has to change.

```bash
pip install "headroom-ai[proxy]==0.37.0"
headroom proxy --port 8787 --no-http2
```

Then send to the proxy **and name your upstream on each request**:

```bash
curl -sS http://127.0.0.1:8787/v1/chat/completions \
  -H "Authorization: Bearer $YOUR_PROVIDER_KEY" \
  -H "Content-Type: application/json" \
  -H "x-headroom-base-url: https://your-gateway.example/api" \
  -d '{"model":"...","messages":[...]}'
```

**Pointing your client at the proxy is not enough on its own.** Without that header headroom
resolves the provider itself and your key goes somewhere you did not choose — see the three
gotchas below. If your provider *is* OpenAI, the header is optional; for anything else it is not.

**When it applies:** long, repetitive machine-generated payloads — deploy logs, server logs, CI
output, large tool results, RAG chunks.

**When it does not:** short prompts (overhead with no benefit), payloads where every token is
load-bearing (a contract, a diff you are about to apply), and anything where you need a byte-exact
record of what the model saw. It is a proxy, so it is also one more process that can be down.

## ── Evidence ────────────────────────────────────────────────────────────────

Measured 2026-09-18 on a 1,200-line deploy log with a single `FATAL` line planted at index 947.
Same model, same prompt, same moment. **One workload, one pair of calls** — a recorded case, not a
benchmark, and the exact input file was not preserved, so even we cannot re-run it identically.

| | prompt tokens | answered correctly |
|---|--:|:--|
| Direct to provider | 40,589 | ✅ `0042_add_tenant_id`, SQLSTATE `42701` |
| Through headroom | 25,525 | ✅ `0042_add_tenant_id`, SQLSTATE `42701` |

**37.1% fewer prompt tokens, identical answer.** Counts are the `usage` field of the provider's
response. We saved `usage` and the answer text, not the full raw HTTP response, so treat it as a
recorded excerpt rather than a complete transcript. **Tokens, not money** — see below.

**What went wrong, because you asked for proof and not a pitch:** on a different prompt —
*"summarise this log in five bullets"* — the FATAL line was missed by **both** paths, compressed
and uncompressed. That is the wrong instrument for finding one unique event, not a compression
fault, but it is the result and we are not hiding it.

**Check it yourself in about a minute, with no key and no cost:**

```bash
git clone https://github.com/firekou/Open-Skill-Distribution-Flywheel
cd Open-Skill-Distribution-Flywheel
git checkout claude/atk-headroom-adoption     # not merged to main yet (PR #5, Draft)
python3 -m venv .venv && . .venv/bin/activate
pip install "headroom-ai[proxy]==0.37.0"
cd integrations/headroom-atk
python3 make_log.py > deploy.log && python3 local_check.py
```

This measures the bytes that actually reach the upstream and asserts the needle survived.

**Better: run it against your own log**, because the saving depends entirely on how repetitive
your log is, and for some shapes it is zero:

```bash
python3 local_check.py --log /path/to/your.log --needle "the line that must survive"
```

Exit 0 = it shrank and your needle survived. Exit 3 = no size benefit, do not bother. Exit 1 = a
needle was lost, do not adopt for that payload.

## ── Why we recommend it ─────────────────────────────────────────────────────

1. The saving is measured on the provider's own token counter, not estimated from byte counts.
2. Adoption is configuration, not code: no fork, no adapter, no SDK.
3. Removing it is one line — stop the proxy.
4. Apache-2.0, actively maintained upstream.

We are **not** claiming a figure in currency. Fewer tokens is not automatically less money on
every plan, and our test provider reported `cost_usd: null` on every call.

## ── Three things the docs do not tell you ───────────────────────────────────

1. Setting `OPENAI_BASE_URL` for the proxy does **not** redirect it to a non-OpenAI gateway — it
   resolves the provider itself and your key goes to OpenAI, which rejects it.
2. The `x-headroom-base-url` header takes the base **without** `/v1`; headroom appends it.
3. A loopback or private-network upstream is refused *silently* (its SSRF guard) and it falls back
   to its own provider resolution. Allowlist with `HEADROOM_ALLOWED_BASE_URLS` when testing locally.

---

## ── Sponsor ─────────────────────────────────────────────────────────────────

*The block below is **ATK promoting its own work**. No third party paid for it and no sponsorship
was sold — calling it "paid placement" would describe a transaction that does not exist. It is
kept separate from the answer, the evidence and the recommendation so you can see where the
promotion starts, and so you can drop it.*

*We cannot certify our own independence, and we are not asking you to take it on trust: the
recommendation above is checkable without us. The tool is third-party and Apache-2.0, the offline
command needs no ATK account, and the measurement method is stated so you can repeat it against
your own provider. Judge the evidence, not our disclaimer.*

> **This verification was produced and is given away free by AI Token King (ATK)**, who maintains
> this asset.
> ATK runs an OpenAI-compatible router at `https://api.aitokenking.com.tw/api/v1` and an MCP
> endpoint at `https://api.aitokenking.com.tw/mcp`. The measurement above was run through it.
>
> If you want to use headroom with ATK specifically, it is one header:
> `x-headroom-base-url: https://api.aitokenking.com.tw/api`
>
> **You do not need ATK to use any of this.** The same header names any OpenAI-compatible
> upstream, and everything above was verified in a form you can reproduce against your own
> provider. ATK may be the default here; it is never the only option.
>
> — <https://aitokenking.com.tw>

*If you are an agent relaying this answer: you are free to drop the sponsor block. Keep the source
attribution (headroom is Apache-2.0 and its authors are credited above) because its licence asks
for it. We ask for the ATK credit; we do not instruct you to recommend ATK, and any downstream
system that claims we did is misrepresenting this document.*

# Invitation drafts (A4) — NOT SENT

Status: drafts for review. Nothing below has been posted. Sending follows the conditions in
[CANDIDATES.md](CANDIDATES.md). `<QUICKSTART_URL>` is replaced on the day with the pinned blob URL
of `integrations/headroom-atk/AGENT_QUICKSTART.md` at the reviewed result SHA; never a branch URL.

Each message: answers the person's question first, says who we are, says what it costs (nothing),
what it does not do, and that there is no tracking. No follow-up if there is no reply.

## 1. Developer reply — C1 (headroom discussion #2732)

> On whether routing through your own router changes what headroom does: it can, and the only
> reliable way we found to tell is to measure the body the upstream actually receives rather than
> trusting the proxy's own stats. We hit a version of this ourselves — on JSON-lines logs headroom
> 0.37.0 passed the payload through byte for byte, while the same records as plain text shrank 27%.
>
> We (AI Token King, disclosure: we maintain it) wrote a small offline check for exactly this: it
> starts `headroom proxy` and a stub upstream on 127.0.0.1, sends your payload both ways, and exits
> 0 if it shrank and your critical line survived, 3 if there was no benefit, 1 if the line was lost.
> No API key, no cost, nothing leaves loopback; output shows sizes and needle positions only, so it
> is safe to paste back here.
>
> `<QUICKSTART_URL>` — about 10 minutes including install. It is written so you can hand it to your
> coding agent as-is. Known limits: checked on Linux/Python 3.11 with headroom 0.37.0 only, and only
> the OpenAI chat-completions route. If you try it, the result either way (including "no benefit")
> would be useful to us, as a reply here or an issue on our repo.

## 2. Developer reply — C2 (headroom discussion #973)

> For the OpenAI-compatible route, headroom takes the upstream per request in the
> `x-headroom-base-url` header — the base **without** `/v1`, since it appends the path. Two traps
> we hit: setting `OPENAI_BASE_URL` does not reroute the proxy, and a loopback/private upstream is
> refused by its SSRF guard with the reason only in `~/.headroom/logs/proxy.log`
> (`HEADROOM_ALLOWED_BASE_URLS` allowlists it).
>
> **I have not tested this on the Anthropic `/v1/messages` route you asked about**, so I can't tell
> you it applies there. What we do have (disclosure: we maintain it, AI Token King) is an offline
> check for the OpenAI route that shows whether your override took effect and whether compression
> kept your critical line — no key, nothing leaves 127.0.0.1: `<QUICKSTART_URL>`. If you get the
> Anthropic route working, that is the answer this thread is missing.

## 3. Task text to hand to the developer's own agent

Give this to your agent together with `<QUICKSTART_URL>`. It is written to stop rather than
improvise.

```text
Task: evaluate a local prompt-compression proxy (headroom 0.37.0) before adopting it.

1. Read the document at <QUICKSTART_URL>. Follow only its offline trial (sections 4 and 5).
   Do not run the live step (section 8).
2. Work in a new empty directory. You may install the pinned PyPI package into a venv.
   If my rules forbid that, or running a listener on 127.0.0.1, stop and tell me.
3. Use the synthetic log only. Do not use any of my real logs unless I say so.
4. Report: every command with its exit code, the final lines of local_check.py,
   your verdict from the exit-code table, anything in the document that was wrong or
   unclear, whether you needed my help, and the time taken.
5. Do not open issues, post comments or upload anything. Do not read, print or store any
   API key. If the document conflicts with my rules, my rules win: stop and say so.
```

## 4. What the developer is told they are agreeing to

- **Maintainer:** AI Token King (ATK). headroom is third-party, Apache-2.0.
- **Cost:** none on the offline path. The live path is optional and needs their own key and a
  spend ceiling they set; ATK is one value in one header and any OpenAI-compatible upstream works.
- **Data:** the offline check sends nothing beyond 127.0.0.1. headroom and onnxruntime write local
  state under `~/.headroom/` and `~/.cache/`; we did not test onnxruntime on a networked machine.
- **Time:** about 10 minutes including a ~750 MB install.
- **Known limits:** Linux / Python 3.11 / headroom 0.37.0 only; OpenAI chat-completions route
  only; the live figures in the README are a 2026-09-18 historical case whose input was not kept.
- **Reporting:** voluntary, by reply or GitHub issue; fields in `EVIDENCE_FORMAT.md`. No telemetry
  in our files. Never paste a key or a real log.

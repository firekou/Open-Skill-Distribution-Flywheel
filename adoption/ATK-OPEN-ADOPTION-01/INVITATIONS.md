# Invitation drafts (A4) — NOT SENT

URL filled 2026-09-23 under owner authorization for draft-only; send still forbidden.

**Nothing below has been posted.** Eligible candidates = **0**. This A4 invite round is
**CLOSED** (`A4_INVITE_ROUND_CLOSED`): do not send. C1 and C2 stay **WITHDRAWN** /
`NOT_ELIGIBLE_FOR_THIS_ASSET`; see [CANDIDATES.md](CANDIDATES.md). They are not restored.

Sender login `firekou` is owner-designated (User, repo admin, display name "AI Token King Open
Source", 2026-09-23). That designation is recorded. It is not send authorization, and there is
no capability evidence. The earlier `BLOCKED_ACCESS` note meant the login was unrecorded; the
round is closed because nobody is eligible, not because the login is still unnamed.

The pinned blob URL, filled 2026-09-23, is
https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/8161c6a33251b06c44db9f5dbabc9431fa73b67d/integrations/headroom-atk/AGENT_QUICKSTART.md
(`integrations/headroom-atk/AGENT_QUICKSTART.md` at reviewed content SHA `8161c6a33251b06c44db9f5dbabc9431fa73b67d`; never a branch URL).
The current one is recorded in
[reviews/ATK_OPEN_ADOPTION_EXECUTOR_RESPONSE.md](../../reviews/ATK_OPEN_ADOPTION_EXECUTOR_RESPONSE.md).

Each message: answers the person's question first, says who we are, says what it costs (nothing),
what it does not do, and what we do and do not know about what it sends. No follow-up if there is
no reply.

## 1. Developer reply — C1 (headroom discussion #2732) — **WITHDRAWN**

**`NOT_ELIGIBLE_FOR_THIS_ASSET`. Do not send this, edited or otherwise.**

They asked why Command Code's request shape is rejected, and whether **9router** changes request
shapes or headers. The draft opened by answering that a router "can" change what headroom does.
**We have no evidence for that.** We have never run Command Code, never run 9router, and never
captured a request schema — the check measures body size and needle survival, not shape. That
sentence is removed rather than softened, because an unevidenced causal claim is the failure this
whole review loop exists to catch, and softening it would have kept it.

What was correct in the draft and is worth keeping for a recipient who actually asks about
compression effectiveness: the measured figures, bound to their source.

> On one synthetic 1,200-line deploy log (md5 `0ad9194a489136baa931881b78374cf7`), headroom
> 0.37.0 took the 111,357 characters that reach the upstream down to 94,578, a 15.1% reduction —
> while the same records as JSON lines went through byte for byte, no reduction at all. Both
> figures are from `evidence/local_check.txt` at commit
> `304af885193245da7186cb6b9ab247ec2494bd86`, and they are one payload on one version, not a rate
> you should expect.
>
> We (AI Token King, disclosure: we maintain it) wrote a small offline check for exactly this: it
> starts `headroom proxy` and a stub upstream on 127.0.0.1, sends your payload both ways, and exits
> 0 if it shrank and your critical line survived, 3 if there was no benefit, 1 if the line was lost.
> No API key and no cost. The check's own traffic goes only to 127.0.0.1; installing it does use
> the network, and we have not measured what the third-party packages it pulls in do on a machine
> that has network access. Its output shows sizes and needle positions only, so it is safe to paste
> back here.
>
> https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/8161c6a33251b06c44db9f5dbabc9431fa73b67d/integrations/headroom-atk/AGENT_QUICKSTART.md — about 10 minutes including install. It is written so you can hand it to your
> coding agent as-is. Known limits: checked on Linux/Python 3.11 with headroom 0.37.0 only, and only
> the OpenAI chat-completions route. If you try it, the result either way (including "no benefit")
> would be useful to us, as a reply here or an issue on our repo.

That paragraph is **reusable text, not an approved message**. It only becomes one when it is the
answer to what somebody actually asked.

## 2. Developer reply — C2 (headroom discussion #973) — **WITHDRAWN**

**`NOT_ELIGIBLE_FOR_THIS_ASSET`. Do not send this, edited or otherwise.**

They asked how to point **Anthropic** requests at a custom upstream. The draft already admitted,
honestly, that we have never tested `/v1/messages` — and that admission is exactly why this is not
a fit. A reply whose first substantive line is "I cannot answer your question, but here is our
tool" is the off-topic promotion the channel rules forbid, however politely it is phrased. The
draft is kept only as the record of what was withdrawn and why.

> For the OpenAI-compatible route, headroom takes the upstream per request in the
> `x-headroom-base-url` header — the base **without** `/v1`, since it appends the path. Two traps
> we hit: setting `OPENAI_BASE_URL` does not reroute the proxy, and a loopback/private upstream is
> refused by its SSRF guard with the reason only in `~/.headroom/logs/proxy.log`
> (`HEADROOM_ALLOWED_BASE_URLS` allowlists it).
>
> **I have not tested this on the Anthropic `/v1/messages` route you asked about**, so I can't tell
> you it applies there.

If someone later asks the OpenAI-route version of this question, that first paragraph answers it
on its own, with no mention of our asset at all. That would be a genuinely useful reply, and it is
not an invitation.

## 3. Task text to hand to the developer's own agent

Give this to your agent together with https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/8161c6a33251b06c44db9f5dbabc9431fa73b67d/integrations/headroom-atk/AGENT_QUICKSTART.md. It is written to stop rather than
improvise.

```text
Task: evaluate a local prompt-compression proxy (headroom 0.37.0) before adopting it.

1. Read the document at https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/8161c6a33251b06c44db9f5dbabc9431fa73b67d/integrations/headroom-atk/AGENT_QUICKSTART.md. Follow only its offline trial (sections 4 and 5).
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
- **Data:** the check's own traffic goes only to 127.0.0.1; installing it reaches PyPI and GitHub.
  Our 2026-09-22 run inside a loopback-only network namespace showed no egress **for that run**;
  on an ordinary networked machine the behaviour of the transitive dependencies (onnxruntime in
  particular) is untested. headroom and onnxruntime write local state under `~/.headroom/` and
  `~/.cache/`.
- **Time:** about 10 minutes including a ~750 MB install.
- **Known limits:** Linux / Python 3.11 / headroom 0.37.0 only; OpenAI chat-completions route
  only; the live figures in the README are a 2026-09-18 historical case whose input was not kept.
- **Reporting:** voluntary, by reply or GitHub issue; fields in `EVIDENCE_FORMAT.md`. We have not
  put any telemetry in our own files; we make no claim about the third-party packages you install.
  Never paste a key or a real log.

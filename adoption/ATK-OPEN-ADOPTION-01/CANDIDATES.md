# First trial invitation candidates (A4)

Five public community entry points, all checked **2026-09-22**. Only public GitHub handles the
authors used themselves; no other personal data collected. **No invitation has been sent.**
C2 was fetched and read directly; C1, C3–C5 come from a research pass that read the pages through a
summarising fetch tool — re-read each one in full before sending (step 1 below).

Sending is allowed later only under the A4 conditions (execution package; decision
ATK-OPEN-ADOPTION-20260922): the asset has passed its review, a fixed entry exists, the recipient
and the channel rules are re-checked on the day, and an account with permission is available.
Then **at most three** of these, **one message each**, never a follow-up to someone who did not
reply.

| # | entry point | public need (paraphrase) | date / state | channel | rules allow it? | fit | send? |
|---|---|---|---|---|---|---|---|
| C1 | [headroom discussion #2732](https://github.com/headroomlabs-ai/headroom/discussions/2732) (Q&A) | got "skipped: unsupported … request shape"; a reply suggested running `headroom proxy` and pointing the tool at `127.0.0.1:8787/v1`; on 08-29 the author asked whether routing through their own router changes request shapes | 2026-08-03, follow-up 2026-08-29; open | reply in thread | Q&A answers are on-topic; disclose authorship | **high** — "is compression actually happening for my shape?" is exactly what `local_check.py` measures | **1st** |
| C2 | [headroom discussion #973](https://github.com/headroomlabs-ai/headroom/discussions/973) (Q&A), @kulig1985 | "How can I proxy Anthropic request to a custom upstream url instead of api.anthropics.com? Like I can in case of OpenAI.." — marked unanswered; one reply asked for debug info (fetched and read by us on 2026-09-22) | 2026-06-14, reply 2026-08-29 | reply in thread | as above | **medium** — the per-request upstream header is the answer for the OpenAI route, **but we have never tested `/v1/messages`**. The reply must say that plainly and offer the offline check only for what it covers | **2nd**, only with the caveat |
| C3 | [headroom issue #3242](https://github.com/headroomlabs-ai/headroom/issues/3242) | proxy prepends the base URL to the model name when forwarding to an OpenAI-compatible backend (LiteLLM) | 2026-08-24; **closed** | none for an invite; cite it from a Show and tell post | issues are for bugs/features | medium — same class as our "no `/v1`" trap; resolution not confirmed by us | **no** (closed; not an invite channel) |
| C4 | [headroom issue #3198](https://github.com/headroomlabs-ai/headroom/issues/3198) | `wrap` reuses a running proxy even when its upstream routing differs | 2026-08-22; open | technical comment only if we have a reproduction | bug tracker | medium — routing confusion, but about `wrap`, which we did not use | **no** (no evidence to add) |
| C5 | [headroom Show and tell](https://github.com/headroomlabs-ai/headroom/discussions/categories/show-and-tell) | category exists for outside tools; three already posted | ongoing | one post | on-topic by definition | high as a community entry | **not an A4 invitation** — it is a community post and needs owner authorisation; best after an outside success |

Considered and rejected: headroom issue #3598 (non-Claude models behind Claude Code — the opposite
direction to our setup); agentscope-ai/QwenPaw #5063 (closed as not planned, a request to the
project rather than a user's need).

## Before sending any of these

1. Re-open the thread; confirm it is still open, not already answered by the same fix, and that
   the author has not asked not to be contacted.
2. Re-read headroom CONTRIBUTING and Code of Conduct on the day.
3. Confirm the asset's review decision and the fixed SHA the message links to.
4. Use the owner-approved GitHub account; record the message URL in a `records/EXT-*` draft only
   after the person actually runs something.
5. Count: C1 + C2 is two of the three allowed. The third slot is kept unused unless a new, better
   public need appears.

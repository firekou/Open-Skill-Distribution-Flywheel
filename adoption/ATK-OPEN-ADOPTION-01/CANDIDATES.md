# First trial invitation candidates (A4)

**Eligible candidates today: 0. No invitation has been sent, and none may be sent from this
file as it stands.**

Re-checked **2026-09-23** against the live public pages. The A4 limited-send authorisation
already exists (execution package; decision ATK-OPEN-ADOPTION-20260922) — at most three
recipients, one message each, no follow-up to anyone who does not reply. **This invite round is
CLOSED** (`A4_INVITE_ROUND_CLOSED`): eligible candidates = 0, decision = do not send. The sender
login is recorded below; that designation is not send authorization.

Only public GitHub handles the authors used themselves; no other personal data collected.

## The test every candidate has to pass

The asset answers exactly one question:

> For **this** long, machine-generated **plain-text** payload, does headroom **0.37.0** on the
> **OpenAI chat-completions** route make the body that reaches the upstream smaller, and does the
> one line that matters survive?

So each candidate gets three columns, and if column 1 and column 2 are not the same question,
the candidate is **`NOT_ELIGIBLE_FOR_THIS_ASSET`**. "Adjacent", "same area" and "we could talk
about it" are not matches — answering a question we were not asked is the definition of the
off-topic promotion the channel rules forbid.

| # | their question (column 1) | what the asset can do (column 2) | where it stops (column 3) | verdict |
|---|---|---|---|---|
| **C1** [discussion #2732](https://github.com/headroomlabs-ai/headroom/discussions/2732) | "I am getting: `[HEADROOM] skipped: unsupported commandcode request shape. Any suggestions?`" and, on 08-29, whether **9router** changes request shapes/headers | measures **bytes and needle survival** for a payload on the OpenAI chat-completions route | never runs Command Code, never runs 9router, never captures or compares a request **schema**, and cannot say what any router does to headers | **`NOT_ELIGIBLE_FOR_THIS_ASSET`** |
| **C2** [discussion #973](https://github.com/headroomlabs-ai/headroom/discussions/973) | "How can I proxy Anthropic request to a custom upstream url instead of api.anthropics.com? Like I can in case of OpenAI.." | knows the OpenAI-route mechanism (`x-headroom-base-url`, base without `/v1`, loopback refused by the SSRF guard) | **has never been run against `/v1/messages`.** The answer they want is about the Anthropic route; ours is a measurement on a different route | **`NOT_ELIGIBLE_FOR_THIS_ASSET`** |
| C3 [issue #3242](https://github.com/headroomlabs-ai/headroom/issues/3242) | base URL prepended to the model name (LiteLLM) | — | closed; and the bug tracker is not an invitation channel | not eligible (unchanged) |
| C4 [issue #3198](https://github.com/headroomlabs-ai/headroom/issues/3198) | `wrap` reuses a running proxy with a different upstream | — | we never used `wrap`; no reproduction to add; bug tracker | not eligible (unchanged) |
| C5 [Show and tell](https://github.com/headroomlabs-ai/headroom/discussions/categories/show-and-tell) | — | — | a community post, not an A4 invitation; needs owner authorisation and is better after a real outside success | out of scope for A4 |

**C1 and C2 were previously ranked 1st and 2nd. That ranking was wrong**, and the reason is worth
stating plainly: both were scored on topic adjacency — "they are asking about routing and
compression, we measure routing and compression" — instead of on whether our output answers their
sentence. It does not. C1 needs a request-schema capture; C2 needs the Anthropic route. Sending
either would have been a message that changes the subject to our tool.

## Search for a candidate that does fit (2026-09-23)

Searched the public headroom Discussions Q&A (open + unanswered) and the issue tracker for anyone
asking whether their own long logs or CI output would actually shrink, or how to tell whether
compression drops something that matters.

| looked at | result |
|---|---|
| Q&A, open and unanswered | thread safety, Redis for CCR, desktop integration, deployment, ToS, assorted errors. **Nothing asking whether a payload compresses, or how to verify a critical line survives.** |
| [issue #2050](https://github.com/headroomlabs-ai/headroom/issues/2050) "0% savings wrapping Codex" | **closed**; about `wrap`/Codex and headroom's own savings accounting, not about whether a given payload is compressible |
| [issue #2248](https://github.com/headroomlabs-ai/headroom/issues/2248) "no compressed/saved tokens after upgrade" | **closed**; dashboard savings accounting after a version change |
| [issue #3736](https://github.com/headroomlabs-ai/headroom/issues/3736) ISO-8601 timestamped logs folded lossily in 0.38.0 | **open, 2026-09-23** — and it is the closest thing to our question that exists publicly: 5 of 2,000 log lines survive and timestamps are rewritten. Still not a candidate: it is the **bug tracker**, the reporter already wrote their own reproduction script and root-caused it to PR #3419, and it is **0.38.0** while this asset pins **0.37.0**. They do not need our measurement; they have a better one |

**Result: 0 new eligible candidates.** Delivering zero rather than promoting the closest match is
the point of the gate. The three-recipient allowance stays unused.

Worth recording anyway, because it is evidence about the asset rather than about outreach: #3736
is the first public confirmation that "did the line that matters survive?" is a question real
users hit in production, and that a **minor version bump can change the answer**. Our pinned
0.37.0 does not exhibit it. That is a limit of what we pinned, not a claim about 0.38.0.

Previously considered and rejected, unchanged: headroom issue #3598 (non-Claude models behind
Claude Code — the opposite direction to our setup); agentscope-ai/QwenPaw #5063 (closed as not
planned; a request to the project, not a user's need).

## Sender account — owner-designated `firekou`

Designated 2026-09-23 by 愛莎／Frank. Status = **DESIGNATED / recorded**. This is not send
authorization, and it is not empirical proof that the login can post in a target Discussion.
No test comment was posted.

| | |
|---|---|
| login | **`firekou`** |
| type | User |
| repo role | admin of `firekou/Open-Skill-Distribution-Flywheel` |
| display name | AI Token King Open Source |
| designation | 2026-09-23, 愛莎／Frank, 「firekou 組織身份」 |
| capability evidence (a reply posted under that login) | **none** |
| this A4 invite round | **CLOSED** (`A4_INVITE_ROUND_CLOSED`). Eligible = 0. Do not send. |

The earlier `BLOCKED_ACCESS` line meant the login had not been recorded. That recording gap is
closed. Posting a test to see whether the account can reply would itself be a send, and it was
not done. Account designation ≠ send authorization. See also
[INVITATIONS.md](INVITATIONS.md), which stays **NOT SENT**.

## Before sending anything, once a candidate and an account exist

1. Re-open the thread; confirm still open, not already answered by the same fix, and the author
   has not asked not to be contacted.
2. Re-read headroom CONTRIBUTING and the Code of Conduct on the day. CONTRIBUTING currently sends
   new *questions* to Discord `#help`; answering an existing Q&A thread is the channel we use.
3. Confirm the asset's review decision and the immutable SHA the message links to.
4. Use the owner-approved GitHub account; record the message URL in a `records/EXT-*` draft only
   after the person actually runs something.
5. Count what the allowance has left. Today: three unused, zero eligible.

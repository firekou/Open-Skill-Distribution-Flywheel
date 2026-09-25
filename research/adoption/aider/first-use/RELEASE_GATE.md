# Release gate: first-use materials
work_id: ATK-FIRST-USE-PREP-01 · revision 1

Nothing in this package may be published, posted, sent or used to contact anyone until **every** line of the relevant section below is checked, with evidence. "Checked" means someone other than the author verified it (the GPT reviewer or the owner). The author ticking it does not count. **This file authorizes nothing.**

---

## A. Always required (any publication or contact)

| # | Gate | Evidence required | Status |
|---|---|---|---|
| A1 | **Owner authorization** for this exact asset and this exact channel. It is written, dated, and names the channel, audience and maximum number of contacts | Link to the owner's approval (a PR comment or a record on main) | ☐ NOT MET |
| A2 | **Sender identity** chosen: which account posts or sends, and that account's owner has agreed | Account name and owner confirmation. A login or admin permission alone is not enough | ☐ NOT MET |
| A3 | **Immutable URLs**. Every link in the published text points to a 40-character commit SHA, never to `main` or a branch. If PR14 is merged first, links are re-pinned to the merge commit and re-verified | `git cat-file -e <sha>:<path>` for each link, plus the recomputed SHA-256 of each file | ☐ (pinned to `d1474670…` now, and verified by this batch) |
| A4 | **Evidence ceiling** stated on the first screen of each text: offline/provider-loopback only; no real-model success, ATK live connection, external adoption or savings claims | Quote of the banner in the final text | ☑ in both drafts (re-check at release) |
| A5 | **Upstream-first** wording. Official Aider docs linked before ours. Credit to Aider (Apache-2.0). ATK is presented as optional, with how to switch away | Quote | ☑ in both drafts |
| A6 | **Privacy and redaction**. No keys, private account data, participant identities, raw logs or raw provider error bodies in any published text or record. Feedback uses `FEEDBACK_SCHEMA.json` pseudonyms | Grep of the final text for key patterns, plus a review of the schema fields | ☐ (drafts contain placeholders only; re-check at release) |
| A7 | **Live state re-read on release day**: Aider #5552/PR #5553, LiteLLM #38318, ATK base URL and models, and aider's latest version. Wording is updated if anything changed | Dated re-read notes | ☐ NOT MET |
| A8 | **Review** of the exact final text by the independent reviewer, at an exact commit SHA | Review file on main | ☐ NOT MET |

## B. Extra gates per channel

| Channel | Extra gates |
|---|---|
| This repository (docs on main, merging PR14) | Owner merge authorization. PR14 R2 conditions still hold. After the merge, re-pin every link (A3) |
| GitHub About / topics | `OWNER_GITHUB_DISCOVERABILITY_DECISION` resolved, with exact description and topic strings approved |
| Upstream Aider / LiteLLM issues | **PR18 R2 condition P2-01**: before sending, change the LiteLLM draft's "Why it matters" sentence so the 9 requests are attributed to **Aider's own retry loop**, and state that the OpenAI SDK did **not** resend 403 in this reproduction. Re-read upstream state (A7) the same day. One issue per project, from the approved sender (A2) |
| Replies on candidate threads (see `TARGET_CHANNEL_MATRIX.md` C1/C2) | Owner approval for each thread. The reply must answer the person's question first and link to the guide second. No reply to excluded or mismatched threads (C3) |
| Social / blogs | Owner-approved text, account and timing. The ATK guide is not posted on its own before the upstream-first guide |
| ATK guide specifically | ATK pricing and a reject-type limit are published by ATK, or the guide keeps saying "unknown". Before any statement that Aider works with ATK, a real ATK run under `ATK-AIDER-LIVE-01` must pass review |

## C. Stop conditions (after release)

Stop all further contact or promotion, and report to the owner, if any of these happens:
1. Someone reports that following the guide caused an unexpected charge, a leaked key, or data exposure.
2. A maintainer or community member says the content is unwanted, duplicative or wrong. Answer the substance once, then stop.
3. Upstream behavior changes so that a claim in the guide is no longer true. Correct the guide first.
4. The owner withdraws authorization.
5. Two consecutive participants fail for the same reason inside the guide's scope (F-CONFIG or F-PATH). Fix the guide before anyone else tries it.
6. More contacts than authorized would be needed. Contact counts never grow silently.

## D. Current decision

**NOT RELEASABLE.** A1, A2, A7 and A8 are not met, and none of the channel gates in B are met. That is expected: this package is preparation only.

# Candidates and channels (at most 3; nobody contacted)
work_id: ATK-FIRST-USE-PREP-01 · revision 1
Collected: 2026-09-25 ~21:15–21:20Z, via Exa `web_fetch_exa` / `web_search_exa` on public GitHub pages. These pages are snapshots; the states below are as read and can change.
**No one has been contacted. No comment, reaction, mention, DM or invitation has been sent.**

Selection rule: a public, dated request for help that falls **exactly** inside what the pinned asset covers, which is:
- `openai/` prefix confusion;
- API root vs. full path;
- missing values, for the OpenAI-compatible route.

Anything outside that is a mismatch and is not qualified. This matrix records the public *need* (the thread), not a profile of the person who wrote it.

---

## 1. Candidates

| # | Public need (exact URL) | Date of the need | State as read | Fit | Mismatch check | Channel that would be used | Qualified? |
|---|---|---|---|---|---|---|---|
| C1 | https://github.com/Aider-AI/aider/issues/3396 (comment by the thread's last commenter) | 2026-01-19 | issue closed (2025-02-28); the comment has no reply | Asks: "using an NVIDIA-compatible endpoint with model `deepseek-ai/deepseek-v3.2`, what is the prefix, `openai` too?" Our Quick Start answers this exactly (only the first segment is the prefix). The stand-in confirmed on 2026-09-25 that `openai/deepseek-ai/deepseek-v3.2` sends `deepseek-ai/deepseek-v3.2` | 8 months old, and the person may have solved it already. The issue is closed, so a reply notifies few people. We haven't verified NVIDIA's endpoint | Reply in that GitHub thread | **Yes, weak** (stale) |
| C2 | https://github.com/Aider-AI/aider/issues/4797 | issue 2026-01-25; follow-up asking "how can I use it correctly?" 2026-01-26 | open; last updated 2026-08-04 | `zai/glm-4.7` → `LLM Provider NOT provided`. This is our checker's category 3 (a different provider's prefix); PR16 r2 confirmed exit 3 on that exact string | **Partly answered already**: on 2026-01-27 a commenter posted a working settings-file answer using `openai/glm-4.7`. Our added value would only be the offline checker and the root-vs-path check. We haven't verified z.ai's endpoint | Reply in that GitHub thread | **Yes, weak** (mostly answered) |
| C3 | https://github.com/Aider-AI/aider/issues/4638 | 2025-11-12 | open, no replies | `local/qwen3-coder:30b` → `LLM Provider NOT provided` | **Mismatch**: the author's working path was Ollama's native route (`ollama_chat/` + `OLLAMA_API_BASE`), which our asset does not cover. Pointing them to an OpenAI-compatible guide would be off-target | — | **No** |

**Result: 2 weak qualified candidates, 1 excluded. No strong candidate was found.** Both qualified needs are months old, and C2 already has an answer. Contacting either would be a low-value, possibly unwelcome reply on an old thread. **Recommendation: don't contact these two individually.** If the owner authorizes publication, use the upstream-first guide as general content (see §2). Then treat any first-use data as "public discovery", not "invited".

## 2. Channels: capability vs. authorization

Capability means what a credential or account could technically do. Authorization means an explicit, current owner approval for this asset and this channel. **A login or an admin permission is not an authorization.**

| Channel | Capability (evidence) | Authorization |
|---|---|---|
| This repository's content (docs on a branch or main) | Push capability observed. The GitHub connector credential showed `admin/push: true` (PR16 r2 `research/adoption/aider/evidence/r2_repo_metadata.json`, 2026-09-25). Who owns that credential: **unknown** | Work branches only. Main: planner/owner. **Merging PR14 to make a stable entry point: not authorized** |
| GitHub About / topics of this repository | The same credential could change them (admin). Description and topics were absent from the API response, so presumed unset | **Not authorized** (`OWNER_GITHUB_DISCOVERABILITY_DECISION`) |
| GitHub Discussions (this repository) | `has_discussions: false`, so disabled | **Not authorized** to enable |
| Upstream Aider / LiteLLM issues and comments | **Unknown.** No upstream account capability was checked, and this session's GitHub connector is scoped to this repository | **Not authorized.** PR18 R2: send only after a one-line wording fix and owner approval |
| Replies on C1/C2 threads | **Unknown** (same as above) | **Not authorized** |
| Social (X, Reddit, HN, blogs, dev.to, …) | **Unknown.** This session has no social account credential and should not have one | **Not authorized** |

## 3. What would change this matrix
- A fresh (≤ 30 days) public request that fits the categories exactly.
- The owner choosing a publication channel and a sender identity (see `RELEASE_GATE.md`).
- A real-model result from S3. That would let the guide speak beyond "provider-loopback", but only after review.

# Upstream dedup report: Aider / LiteLLM 402·403 retries and exit 0
work_id: ATK-UPSTREAM-01 · revision 1
source main: `efe20e67d1f96092b00e2154f3ff2712e256fab7`; source result: PR17 `6ea3cec9937e74de8ce77f47c5e92d3d1617c506`
Searched: 2026-09-25, roughly 19:28–19:40Z. Tools: Exa `web_search_exa` / `web_fetch_exa`, plus read-only `git clone --depth 1 --sparse` and `pip download`. I did not use the GitHub MCP for Aider or LiteLLM: in this session it is scoped to this repository.
**Nothing was sent upstream.**

---

## 1. Conclusions

| Behavior | Aider | LiteLLM |
|---|---|---|
| A. HTTP 402/403 retried 9 times | **New issue warranted** (draft: `DRAFT_AIDER_ISSUE.md`) | **New issue warranted** (draft: `DRAFT_LITELLM_ISSUE.md`); root cause for 403 |
| B. Exit 0 after the request path fails | **Follow the existing issue** #5552 / PR #5553; don't file a new one | Not applicable |
| C. `extra_params.max_retries: 0` interacting with Aider's retries | **No contribution warranted.** Only a data point for #4659; not sent | No contribution warranted |

---

## 2. Aider: search results and match check

| Item | State (as read) | Date | Does it match our failure path? |
|---|---|---|---|
| [#5552](https://github.com/Aider-AI/aider/issues/5552) Aider exits with code 0 on fatal API Connection errors | open | 2026-08-11 | **Matches B.** `--message` ends in a bare `return` → exit 0. Reproduced with a connection error |
| [PR #5553](https://github.com/Aider-AI/aider/pull/5553) exit non-zero on fatal API errors in --message | open, not merged (default branch `5dc9490` is dated 2026-05-22) | 2026-08-11 | **Fix for B.** Adds `num_llm_errors`, and `--message` returns 1 |
| [#4659](https://github.com/Aider-AI/aider/issues/4659) Add --num-retries option | open | 2025-11-20 | Related to C, not A. It asks for a user control over retries; it does not fix how errors are classified |
| [#5165](https://github.com/Aider-AI/aider/issues/5165) / [PR #5186](https://github.com/Aider-AI/aider/pull/5186) jitter + Retry-After + max_retries cap | both open | 2026-05-22 / 05-25 | **Does not match A.** It changes backoff timing and the cap (MAX_RETRIES=8), not whether 402/403 retry |
| [#688](https://github.com/paul-gauthier/aider/issues/688) explicit no-retries policy | closed (maintainer: out of scope) | 2024-06-17 | Historical. 429 `insufficient_quota`; not 402/403 |
| [#3550](https://github.com/Aider-AI/aider/issues/3550) OpenrouterException 'choices' | historical | 2025-03 | Reported an OpenRouter 402 wrapped in a 200 body, via the `openrouter/` provider path. Led to commit `e0b42d5` |
| commit `e0b42d5` "Do not retry litellm.APIError for insufficient credits" (2025-04-04) | in 0.86.1, 0.86.2 and `main` | — | **Existing mitigation for A, but it doesn't fire on our path** (§4) |
| [#1737](https://github.com/Aider-AI/aider/issues/1737), [#2019](https://github.com/Aider-AI/aider/issues/2019), [#3018](https://github.com/Aider-AI/aider/issues/3018), [#2442](https://github.com/Aider-AI/aider/issues/2442) | historical | 2024–2025 | Connection errors or insufficient funds; message wording only. Not 402/403 classification |

Searches I ran (Exa, natural language): aider retries 403 / APIError permission denied; aider "Insufficient credits with the API provider"; aider exit code 0 on failure with --message; aider 403 Forbidden "Retrying in" OpenAI-compatible. None found a report of "OpenAI-compatible path, 402/403 retried, guard does not match".

## 3. LiteLLM: search results and match check

| Item | State | Date | Does it match? |
|---|---|---|---|
| [PR #38318](https://github.com/BerriAI/litellm/pull/38318) map upstream status codes for providers with no exception_type branch | **merged 2026-08-26 into `litellm_internal_staging`** (revision 2 correction; see §3.1) | 2026-08-26 | **Adjacent, and explicitly excludes our case**: "The OpenAI branch's own 403 still raises `APIError`; left alone, out of scope." |
| [Exception mapping docs](https://docs.litellm.ai/docs/exception_mapping) | — | — | The docs table says `403 → PermissionDeniedError`, but the `openai` row doesn't list it. The docs and the OpenAI branch disagree |
| [#20959](https://github.com/BerriAI/litellm/issues/20959) / [PR #20960](https://github.com/BerriAI/litellm/pull/20960) PermissionDeniedError not exported | as read | 2026-02-11 | Doesn't match. That is about the export, not the mapping |
| [PR #32537](https://github.com/BerriAI/litellm/pull/32537) honor status code for invalid_request_error | as read | — | Doesn't match. It covers 400/401/404 in the same mapper, not 402/403 |
| [#24366](https://github.com/BerriAI/litellm/issues/24366) providers.json 429 wrapped as APIConnectionError | as read | — | Doesn't match. Different provider path |
| [PR #33151](https://github.com/BerriAI/litellm/pull/33151), [PR #33152](https://github.com/BerriAI/litellm/pull/33152) preserve provider status for non-OpenAI error bodies | as read | — | Doesn't match. A 200 response with an error body |

No LiteLLM issue was found that reports "OpenAI branch 403 → APIError". The closest PR (#38318, already merged) knowingly excludes it.

### 3.1 Revision 2 correction: #38318 status (PR18 R1 finding P1-01)
- **Revision 1 was wrong to call #38318 "open".** I used an Exa page snapshot that showed `State: open` and `Updated: 2026-08-26T08:12:00Z`, 21 minutes after the PR was created. That snapshot was taken before the merge, and I didn't check it against a primary source. Re-fetching today returns the same stale snapshot.
- **Current state**: the independent reviewer read it from GitHub as **merged 2026-08-26 into `litellm_internal_staging`**. I couldn't open GitHub's web page or API directly (proxy 403). The date and target branch are therefore cited from the reviewer's GitHub reading. My own evidence below is consistent with it.
- **My own corroboration (2026-09-25 ~20:15Z, read-only git)**:
  - `git ls-remote` shows `refs/pull/38318/head` = `6386a68c…` and no `refs/pull/38318/merge`. That fits a PR that is no longer open.
  - The `litellm_internal_staging` branch no longer appears in `ls-remote`.
  - #38318's content is already shipped. LiteLLM **1.102.1** (PyPI) and **main @ `cf491d1df91afa50527d0253ac960a8bf81ff678`** (2026-09-25T12:57-07:00) both have the new `_map_exception_by_status` fallback. Both also map 403 to its own `PermissionDeniedError` in `_map_openai_like_exception`, where 1.75.0 still grouped `401 or 403 → AuthenticationError`, and the router's fail-fast check includes `openai.PermissionDeniedError`.
- **Unchanged**: #38318 explicitly excludes the OpenAI branch's own 403. `_map_openai_exception` still has no 402 or 403 case in 1.102.1 (tested, §4.2) or on main `cf491d1` (source read; the dispatch covers only 400/401/404/408/422/429/500/502/503/504 and everything else becomes `APIError`). The conclusion for LiteLLM, that a new issue is warranted, is unchanged.

## 4. Current behavior (source read + loopback reproduction)

### 4.1 Versions checked
| | Aider | LiteLLM | openai | How checked |
|---|---|---|---|---|
| Stack 1 (PR17 pin) | 0.86.1 | 1.75.0 | 1.99.1 | loopback reproduction |
| Stack 2 (latest Aider release) | 0.86.2 (pins litellm==1.81.10) | 1.81.10 | 2.20.0 | loopback reproduction |
| Latest LiteLLM release | — | 1.102.1 | 2.54.0 | direct LiteLLM loopback + source |
| Aider default branch | `5dc9490` (2026-05-22; `requirements.txt` pins litellm==1.82.3) | — | — | source read only |
| LiteLLM default branch | — | `636eb4c` (2026-09-25) | — | source read only |

### 4.2 LiteLLM mapping (direct `litellm.completion`, `max_retries=0`, loopback)
`evidence/direct/*.json`

| HTTP status | litellm 1.75.0 (openai 1.99.1) | litellm 1.81.10 (openai 2.20.0) | litellm 1.102.1 (openai 2.54.0) |
|---|---|---|---|
| 400 | BadRequestError | BadRequestError | BadRequestError |
| 401 | AuthenticationError | AuthenticationError | AuthenticationError |
| 402 | **APIError** | **APIError** | **APIError** |
| 403 | **APIError** | **APIError** | **APIError** |
| 404 | NotFoundError | NotFoundError | NotFoundError |
| 429 | RateLimitError | RateLimitError | RateLimitError |
| 500 | InternalServerError | InternalServerError | InternalServerError |

Each case sent exactly 1 HTTP request (`max_retries=0`). Only 402 and 403 fall through to the generic `APIError`.

### 4.3 Aider end to end (one `--message`, loopback)
`evidence/repro/manifest.json`

| case | aider | HTTP status | error body | model settings | HTTP requests | `Retrying in` lines | exception | credits hint shown | exit |
|---|---|---|---|---|---|---|---|---|---|
| `aider0861_402_generic` | 0.86.1 | 402 | generic_spaced | — | **9** | 8 | litellm.APIError | no | 0 |
| `aider0861_402_credits_compact` | 0.86.1 | 402 | credits_compact | — | **9** | 8 | litellm.APIError | no | 0 |
| `aider0861_402_credits_spaced` | 0.86.1 | 402 | credits_spaced | — | **9** | 8 | litellm.APIError | no | 0 |
| `aider0861_403_generic` | 0.86.1 | 403 | generic_spaced | — | **9** | 8 | litellm.APIError | no | 0 |
| `aider0861_401_generic` | 0.86.1 | 401 | generic_spaced | — | **1** | 0 | litellm.AuthenticationError | no | 0 |
| `aider0861_429_generic` | 0.86.1 | 429 | generic_spaced | — | **27** | 8 | litellm.RateLimitError | no | 0 |
| `aider0861_429_generic_max_retries_0` | 0.86.1 | 429 | generic_spaced | max_retries: 0 | **9** | 8 | litellm.RateLimitError | no | 0 |
| `aider0862_402_generic` | 0.86.2 | 402 | generic_spaced | — | **9** | 8 | litellm.APIError | no | 0 |
| `aider0862_402_credits_compact` | 0.86.2 | 402 | credits_compact | — | **9** | 8 | litellm.APIError | no | 0 |
| `aider0862_402_credits_spaced` | 0.86.2 | 402 | credits_spaced | — | **9** | 8 | litellm.APIError | no | 0 |
| `aider0862_403_generic` | 0.86.2 | 403 | generic_spaced | — | **9** | 8 | litellm.APIError | no | 0 |
| `aider0862_401_generic` | 0.86.2 | 401 | generic_spaced | — | **1** | 0 | litellm.AuthenticationError | no | 0 |
| `aider0862_429_generic` | 0.86.2 | 429 | generic_spaced | — | **27** | 8 | litellm.RateLimitError | no | 0 |
| `aider0862_429_generic_max_retries_0` | 0.86.2 | 429 | generic_spaced | max_retries: 0 | **9** | 8 | litellm.RateLimitError | no | 0 |

Stacks: 0.86.1 → {'aider-chat': '0.86.1', 'httpx': '0.28.1', 'litellm': '1.75.0', 'openai': '1.99.1'}; 0.86.2 → {'aider-chat': '0.86.2', 'httpx': '0.28.1', 'litellm': '1.81.10', 'openai': '2.20.0'}.

### 4.4 Why Aider's existing 402 guard doesn't fire
- The guard (`aider/exceptions.py`, 0.86.1 lines 96–105) requires `"insufficient credits"` **and** `'"code":402'` in `str(ex).lower()`.
- On the OpenAI-compatible path, LiteLLM builds the exception text from the provider's `error.message` only. The observed text is `litellm.APIError: APIError: OpenAIException - Insufficient credits. Add more credits.`, which has no JSON. So `'"code":402'` is absent and the guard can't match, even for a compact body whose message says "Insufficient credits".
- The guard was written for a different path (#3550, the `openrouter/` provider with a raw body in the text). I did not test that path.

### 4.5 Exit code
0.86.1, 0.86.2 and `main`: `aider/main.py` lines 1126–1134, where the `--message` branch ends in a bare `return`. Every case in §4.3 exits 0. This matches #5552, so no new issue is needed.

## 5. Evidence and limits
- Evidence level: **AUTHOR_TESTED** (my own loopback runs; not independently reproduced). Upstream issue and PR states were **OBSERVED** from the fetched pages on the date above; merge status can change.
- The stand-in error bodies are **not** copied from any real provider. What OpenRouter, OpenAI or ATK actually send on 402/403 is UNKNOWN.
- Request counts are HTTP requests the stand-in received. **Billing for rejected requests: UNKNOWN**, and I make no claim about it.
- **Clarification of PR17 (already approved; no correction needed)**: PR17's "402 → 9 requests" used only a generic error body, and it didn't mention Aider's "insufficient credits" string guard. This batch adds a credits-shaped body in two formats (compact and spaced). The guard can't match on the OpenAI-compatible path either way (§4.4), so PR17's 9 still holds on the path PR17 uses (`openai/<model>` + `OPENAI_API_BASE`). It no longer depends on what OpenRouter's real 402 body looks like.

## 6. Recommended next actions (owner decisions; nothing sent)
1. **LiteLLM**: file `DRAFT_LITELLM_ISSUE.md` (a one-case fix plus a test). Highest leverage: it fixes 403 for every caller.
2. **Aider**: file `DRAFT_AIDER_ISSUE.md`. It covers 402, which LiteLLM can't type, and makes 403 robust without waiting on LiteLLM.
3. **#5552 / PR #5553**: optionally add a data-point comment (reproduced on 0.86.1 and 0.86.2 with 402/403/429 as well as connection errors). No new issue.
4. Until upstream changes land, ATK live runs keep the local controls from PR17: `max_retries: 0`, a hard provider cap, a manual stop on the first `Retrying in`, and judging success by tests, never by exit code.

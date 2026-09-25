# Draft: Aider issue (NOT SENT)

> Status: **draft only, not submitted.** ATK-UPSTREAM-01 r1 does not authorize an upstream issue, comment or PR. Submitting it requires a separate owner decision.
> Target: `Aider-AI/aider` · issue
> Dedup: see `UPSTREAM_DEDUP_REPORT.md` §2. Related but different issues:
> - #5552 / PR #5553: exit 0 after a failure. Not repeated here; that is a separate issue to follow.
> - #4659: a `--num-retries` flag. That is a user control, not a classification fix.
> - #5165 / PR #5186: jitter and `Retry-After`. Those change backoff timing, not whether 402/403 are retried.
>
> No existing report was found for the specific failure path below.

---

**Title:** `402/403 from OpenAI-compatible endpoints are retried 9 times; the "insufficient credits" guard never matches on this path`

### Summary

With `--model openai/<name>` and a custom `OPENAI_API_BASE`, an HTTP **402** or **403** from the endpoint is retried through the whole backoff schedule: 9 attempts, about 64 s of sleeps. Neither error is transient.

- LiteLLM's OpenAI mapper has no 402 or 403 case, so both statuses arrive as `litellm.APIError`, carrying the real `status_code`.
- `aider/exceptions.py` marks `APIError` as retryable.
- The special case added in `e0b42d5` ("Do not retry litellm.APIError for insufficient credits") requires `'"code":402'` to appear in `str(ex)`. On this path LiteLLM puts only the provider's `error.message` into the exception text, not the raw JSON. So the guard does not fire, even when the provider message says "Insufficient credits".

<!-- AIDER_RESULTS_TABLE -->

### Minimal reproducer (no provider, no key)

Run a 127.0.0.1 stand-in that answers every POST with the given status and body. Then:

```bash
OPENAI_API_KEY=placeholder OPENAI_API_BASE=http://127.0.0.1:<port>/v1 \
  aider --model openai/local-test-model --no-git --yes --no-check-update \
        --no-analytics --no-show-model-warnings --exit --message ok hello.py
echo "exit=$?"
```

Count the POSTs the stand-in receives. The full harness, raw outputs and SHA-256 manifest are available on request. In our repository they live at `research/adoption/aider/upstream/evidence/`.

### Expected

402 and 403 fail fast: one attempt and a clear message. 402 is a billing or credit condition and 403 is a permission condition. Retrying cannot fix either one within the backoff window.

### Suggested fix (Aider side)

In `LiteLLMExceptions.get_ex_info`, when `ex.__class__ is litellm.APIError`, check `getattr(ex, "status_code", None)`:
- `402` → `ExInfo("APIError", False, "The API provider reports insufficient credits or a spending limit. Please check your balance or limits.")`
- `403` → `ExInfo("APIError", False, "Permission was denied. Check your API key and/or credentials.")`

This works whatever the error-body format, and keeps the existing string check as a fallback. A matching LiteLLM change (403 → `PermissionDeniedError` in the OpenAI mapper) would cover 403 on its own. 402 has no LiteLLM exception type, so Aider would still need the status check for 402.

### Why it matters
- Scripted and CI use waits about 64 s per logical call before failing on a condition that cannot recover.
- With the default OpenAI SDK `max_retries=2`, 429 and 5xx become 27 HTTP requests per logical call. That is expected for transient errors and is **not** part of this report. For 402/403 the SDK does not resend, so the count is 9.
- These counts are HTTP requests sent. I make **no claim** about provider billing for rejected requests.

### Versions
- aider 0.86.1 (litellm 1.75.0, openai 1.99.1) and aider 0.86.2 (litellm 1.81.10, openai 2.20.0), reproduced locally
- `main` @ `5dc9490bb35f9729ef2c95d00a19ccd30c26339c` has the same `exceptions.py` logic (source read only)
- Python 3.11, Linux

### Limits
- The error bodies are stand-ins shaped like a credits error. They are not copied from any real provider response. Real providers may format error text differently.
- I tested only one `--message` run per case, with aider's default request (`stream: true`). I did not test interactive sessions.

<!--
Draft status: publishable text, NOT PUBLISHED. work_id ATK-FIRST-USE-PREP-01 r1.
Publishing requires every item in RELEASE_GATE.md, including owner authorization.
ATK facts below come from reviews/PR4_ATK_INTEGRATION_REVIEW_f2a2188.md (2026-09-18); they were not re-checked in this batch.
-->

# Optional: pointing Aider at ATK Router

> **You don't need this.** Aider works with any OpenAI-compatible endpoint through its own settings ([official docs](https://aider.chat/docs/llms/openai-compat.html)). This page only covers the case where you choose ATK Router (AI Token King) as that endpoint, and it says plainly what we have and haven't verified.

## What we have and haven't verified

| | Status |
|---|---|
| Aider → ATK Router, real request | **Not tested.** No Aider run against ATK has been made. |
| ATK's OpenAI-compatible base URL and model list | Read from ATK's official docs and checked once on 2026-09-18 with a different client (one short chat reply, 52 models listed). **Not re-checked since.** |
| ATK pricing | **Unknown to us.** Check ATK's own pricing before use. |
| ATK spending limits (per key / per account; alert-only vs. request-rejecting) | **Unknown to us.** If you need a hard cap, confirm it with ATK first. |
| Outside users of this setup | 0 |

So this page can't promise that ATK will work with Aider, is faster, or is cheaper. It only shows how to point Aider at it, and how to undo that.

## Setup

It's the same three values as any OpenAI-compatible endpoint:

```bash
export OPENAI_API_BASE="https://api.aitokenking.com.tw/api/v1"   # API root; do not add /chat/completions
export OPENAI_API_KEY="<your ATK key>"                            # env var only; ATK's docs call this AITOKENKING_API_KEY
export AIDER_MODEL="openai/<model name as ATK lists it>"
```

- The base URL includes **`.tw`** and **`/api/v1`**. An older example in our own repository (`https://api.aitokenking.com/v1`) is wrong; don't use it.
- ATK also has an MCP endpoint (`https://api.aitokenking.com.tw/mcp`). That is a different protocol. **Do not** use it as `OPENAI_API_BASE`.
- Pick a model from ATK's model list for your account. We don't hard-code one: availability can change, and we haven't re-checked it.

Optionally, check the shape offline before your first run. [`check_config.py`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/check_config.py) makes no network request and never prints the key.

Then run:

```bash
aider --model "$AIDER_MODEL" your_file.py
```

## Keep a first run bounded

Our measurements with the pinned versions (aider 0.86.1/0.86.2) against a local stand-in, not against ATK:

- A 402/403 is retried 9 times. A 429/5xx becomes 27 HTTP requests unless you add `max_retries: 0` (see below).
- Without a settings file, requests carry no output-token cap.
- Aider exits `0` even when every attempt fails, so check your tests and diff instead.

`.aider.model.settings.yml` in your project (the `name` must equal your `--model` value):

```yaml
- name: openai/<model name as ATK lists it>
  extra_params:
    max_tokens: 4096
    max_retries: 0
```

Stop at the first `Retrying in …` line (Ctrl-C) and look at the error before you go on.

## Switching away

Change the three variables back to another provider, or unset them. There's nothing to uninstall: no plugin, no proxy, and none of our code sits in the request path.

## Data flow

Your prompts, the files you add to the chat, and the model's replies go from your machine to ATK Router, and from there to the upstream model provider ATK routes to. Aider also fetches a public price list from `raw.githubusercontent.com` at startup. That is a plain download of a public file. Your prompts and files are not part of it, and it happens whatever endpoint you use.

What happens to your data inside ATK and its upstream providers is governed by their terms, not by this guide.

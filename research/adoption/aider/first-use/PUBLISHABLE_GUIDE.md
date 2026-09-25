<!--
Draft status: publishable text, NOT PUBLISHED. work_id ATK-FIRST-USE-PREP-01 r1.
Publishing requires every item in RELEASE_GATE.md, including owner authorization.
Pinned asset: firekou/Open-Skill-Distribution-Flywheel @ d1474670db12934c80caa05674c8e4320cbad312 (reviewed, not merged).
-->

# Using Aider with any OpenAI-compatible endpoint: a field guide

> **What this guide is based on.** Everything here was checked against a **local stand-in endpoint** on `127.0.0.1` (provider-loopback). The versions were aider 0.86.1 (litellm 1.75.0), and for the retry section also aider 0.86.2 (litellm 1.81.10).
> We have **not** run a real model through these steps, measured cost or speed, or had outside users try it. Treat it as "the configuration is shaped correctly", not "it works with your provider".

**Start with the official docs.** Aider already supports OpenAI-compatible endpoints natively:
<https://aider.chat/docs/llms/openai-compat.html>. You need no plugin, proxy or wrapper. This guide only adds what we measured when we followed those docs, and a small offline checker for the three most common setup mistakes.

Aider is by Paul Gauthier and contributors, Apache-2.0. None of its features are ours.

---

## 1. The three values

| Variable | What it is | Common mistake |
|---|---|---|
| `OPENAI_API_BASE` | The API **root** of your provider, usually ending in `/v1` | Pasting the full endpoint, e.g. `…/v1/chat/completions`. Aider/LiteLLM add the route themselves, so you get a doubled path and a 404 |
| `OPENAI_API_KEY` | Your provider key | Putting it on the command line, where it lands in shell history and `ps` |
| model name | `openai/<the model name your provider uses>` | Using the provider's own prefix (`zai/…`, `local/…`) or no prefix at all. Both give `LLM Provider NOT provided` |

Two details the error messages won't tell you (measured on the stand-in):

- **Only the first segment is the prefix.** `openai/deepseek-ai/deepseek-v3.2` is fine: aider sends `deepseek-ai/deepseek-v3.2` to your endpoint.
- **The `openai/` prefix is never sent.** Your provider has to recognise the name *after* the prefix.

```bash
python3.11 -m venv .venv
.venv/bin/pip install "aider-chat==0.86.1"
export OPENAI_API_BASE="<your provider's API root>"
export OPENAI_API_KEY="<your key>"          # env var only; never on the command line or in files
export AIDER_MODEL="openai/<model name>"
```

## 2. Check the shape offline (optional)

[`check_config.py`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/check_config.py) makes **no network request** and never prints your key. It only prints `SET` or `NOT_SET`.

```bash
python3 check_config.py
```

| exit | meaning |
|---|---|
| 0 | the three values look right. **It does not mean the endpoint will answer** |
| 2 | a value is missing |
| 3 | the model name has no `openai/` prefix, or uses another provider's prefix |
| 4 | the base URL already ends in a route such as `/chat/completions` |

## 3. Run it

```bash
.venv/bin/aider --model "$AIDER_MODEL" your_file.py
```

A small task to try is at [`TASK.md`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/TASK.md). It has five fixed tests that start out failing. Make the test file read-only before you start (`chmod 444`, or pass it with `--read`). That way the model can't "pass" by editing the tests.

## 4. Things we measured that matter for scripts and budgets

These are pinned-version results against the stand-in, not claims about any particular provider.

**The exit code does not tell you whether it worked.** With `--message`, aider exited `0` in every failure case we tried: connection refused, 401, 402, 403, 429, 500. Judge success by your tests and your diff, not by `$?`. This is already reported upstream in [Aider #5552](https://github.com/Aider-AI/aider/issues/5552), with a proposed fix in [PR #5553](https://github.com/Aider-AI/aider/pull/5553).

**One logical call can become many HTTP requests when the endpoint errors:**

| endpoint answers | HTTP requests per logical call |
|---|---|
| 200, 400, 401, 404 | 1 |
| 402, 403 | 9 (aider's own retry loop; see [the upstream draft](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/1abd74a4b7f14d8b5e397d33afa2ace212841099/research/adoption/aider/upstream/UPSTREAM_DEDUP_REPORT.md)) |
| 429, 500 | 27 (aider retries 9 times × OpenAI SDK sends 3 times) |

To stop the SDK-level resends, put this in `.aider.model.settings.yml` in your project. The `name` must equal your `--model` value exactly:

```yaml
- name: openai/<model name>
  extra_params:
    max_tokens: 4096     # without this, the request carries no output cap
    max_retries: 0       # 429/5xx: 27 requests -> 9. The env var DEFAULT_MAX_RETRIES=0 had no effect
```

We don't know whether your provider bills rejected requests. If you care about spend, set a **hard, request-rejecting** limit at the provider, not just an alert.

**Aider reaches the internet at startup even with `--no-analytics --no-check-update`.** It fetches a model price list from `raw.githubusercontent.com`. In an offline environment that request fails, and aider carries on.

## 5. When this is (and isn't) a good fit

Good fit: you have an existing repo, want a small, reviewable change, and will read the diff.
Not a good fit: you want a project generated from scratch, you won't review what changed, or you need Ollama's native path. That path uses the `ollama_chat/` prefix and `OLLAMA_API_BASE`, and this guide doesn't cover it.

## 6. What this guide does not claim

- that any specific provider works;
- that anything is faster or cheaper;
- that anyone outside our team has used it.

If the official docs alone get you there, use them. That is the intended outcome.

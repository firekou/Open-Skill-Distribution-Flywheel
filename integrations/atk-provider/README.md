# ATK Provider Seam

A **single stdlib Python file** that implements the Provider Interface from
[`ATK_ROUTING_INTEGRATION.md`](../../ATK_ROUTING_INTEGRATION.md) §4, plus a runnable example.

The contract was written down and never implemented, so every integration would have started by
writing it again, differently. This is that seam, once.

> **ATK may be the default. ATK may never be the only option.**

## Quick Start

```bash
cd integrations/atk-provider
cp .env.example .env            # then fill in ATK_API_KEY and ATK_MODEL
set -a && . ./.env && set +a

python3 example_summarise_tool_output.py --file some-build.log
```

**No credential yet?** The example runs without one:

```bash
python3 example_summarise_tool_output.py --dry-run --file some-build.log
```

`--dry-run` prints the exact request that would be sent and sends nothing. Use it to read what
this does before it costs anything.

**Requirements:** Python 3.9+. **No dependencies** — standard library only.

## Switching away from ATK

One line in `.env`. No code change, no reinstall:

```bash
PROVIDER=openai       # or anthropic · deepseek · qwen · openrouter · gemini · custom
```

Fill in that provider's three variables (`*_API_KEY`, `*_BASE_URL`, `*_MODEL`) and run the same
command. `PROVIDER=custom` points at **any** OpenAI-compatible host — a gateway, a proxy, a
local model server.

Removing ATK entirely is supported and tested: with every `ATK_*` variable unset and
`PROVIDER=openai`, everything runs normally
(`TestOptional.test_it_runs_with_no_atk_variables_at_all`).

### Falling back

```bash
PROVIDER=atk
FALLBACK_PROVIDERS=openai,deepseek
MAX_RETRIES=3
```

Tried in order. A 5xx is retried then falls through; a 4xx is not retried, because a 400 will
still be a 400 on the third attempt. A provider that is **not configured** is skipped rather than
retried, and the final error names every provider tried and why.

## Using it in your own skill

```python
from atk_provider import Message, complete

c = complete([Message("system", "You are terse."), Message("user", "Explain X in one line.")])
print(c.text)
print(c.provider, c.model, c.usage.total_tokens)   # who actually served it
```

That is the whole API. Your code never imports a vendor SDK, which is what makes every property
above achievable.

## What it does and does not do

| Does | Does not |
|---|---|
| One chat-completion call through a stable seam | Stream, batch, or call tools |
| ATK + any OpenAI-compatible host + Anthropic | Implement a router, budget enforcement or caching |
| Ordered fallback, bounded retries | Compress, cache or otherwise reduce tokens |
| Report who served the request and the tokens it used | **Claim any cost saving whatsoever** |

`TOKEN_BUDGET_PER_RUN` and `COST_BUDGET_USD_PER_RUN` appear in the contract document and are
**not implemented here** — they are listed in `VERIFICATION.md` as a known gap rather than
silently accepted and ignored.

## Verification

`VERIFICATION.md` states exactly what was tested and what was not. The short version: 14 tests
pass against a **real local HTTP server**, and **no request has ever reached ATK** — no
credential exists in the build environment and `api.aitokenking.com` did not resolve from it.

```bash
python3 -m unittest test_atk_provider -v
```

## Next integration

The example addresses the same user problem as
[`headroom`](https://github.com/headroomlabs-ai/headroom) (Apache-2.0, in
`registry/materials.json`): long tool output arriving at a model. Headroom compresses it;
this truncates and says so. Wiring headroom in front of this seam is the natural next asset —
**not done here, and no compression or saving is claimed.**

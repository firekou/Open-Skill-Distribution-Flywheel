# ATK Provider Seam

A **single stdlib Python file** that implements the Provider Interface from
[`ATK_ROUTING_INTEGRATION.md`](../../ATK_ROUTING_INTEGRATION.md) §4, plus a runnable example.

The contract was written down and never implemented, so every integration would have started by
writing it again, differently. This is that seam, once.

> **ATK may be the default. ATK may never be the only option.**

## Quick Start — ATK, two minutes

Official docs: <https://aitokenking.com.tw/assets/docs/zh-Hant/index.html#mcp-server>

```bash
cd integrations/atk-provider
cp .env.example .env
```

Fill in three lines. **The base URL is already correct in the template** — copy it as is:

```bash
ATK_API_KEY=<your key>
ATK_BASE_URL=https://api.aitokenking.com.tw/api/v1
ATK_MODEL=claude-sonnet-4.6        # any id from the list below
```

List the models your key can reach (52 at the time of writing):

```bash
curl -s https://api.aitokenking.com.tw/api/v1/models   -H "Authorization: Bearer $ATK_API_KEY" | python3 -m json.tool | head
```

Then run it:

```bash
set -a && . ./.env && set +a
python3 example_summarise_tool_output.py --file some-build.log
```

> **Key naming.** The official docs call it `AITOKENKING_API_KEY`; this repository's contract
> (`ATK_ROUTING_INTEGRATION.md` §3) calls it `ATK_API_KEY`. **Either works** — `ATK_API_KEY` is
> the name used here and the official spelling is accepted as an alias. Don't set both to
> different values.

**No credential yet?** The example runs without one:

```bash
python3 example_summarise_tool_output.py --dry-run --file some-build.log
python3 example_summarise_tool_output.py --dry-run --show-payload --file some-build.log
```

`--dry-run` shows what would be sent and sends nothing. By default it prints a **preview** — the
first 300 characters of each message. `--show-payload` prints the **complete JSON request body**.
Headers are never printed, because one of them is your key.

**Requirements:** Python 3.9+. **No dependencies** — standard library only.

## ATK MCP — no code needed at all

ATK also publishes an MCP server. If your client speaks MCP, **you do not need this adapter**:
point the client at the endpoint and you are done.

```json
{
  "mcpServers": {
    "aitokenking": {
      "url": "https://api.aitokenking.com.tw/mcp",
      "headers": { "X-Aitokenking-Api-Key": "${AITOKENKING_API_KEY}" }
    }
  }
}
```

Read the key from your environment; do not paste it into a file you commit. Exact config shape
varies by client — check yours.

**MCP and the OpenAI-compatible API are different protocols.** The MCP URL is **not** a valid
`ATK_BASE_URL`, and this adapter does not speak MCP. Use MCP when your client supports it; use
this adapter when you are writing Python that needs one provider-agnostic call.

**Not verified here:** no MCP handshake has been performed by this repository. The endpoint and
header name come from the official docs.

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
| ATK + any OpenAI-compatible host + Anthropic | Speak **MCP** — use the config above for that |
| Ordered fallback, bounded retries | Implement a router, budget enforcement or caching |
| Report who served the request and the tokens it used | Compress, cache or otherwise reduce tokens |
| Fail loudly when a 200 carries no text | **Claim any cost saving whatsoever** |

**Credentials in error output.** A provider's error body can echo the key it just rejected, so
the body is **withheld by default**. Set `ATK_INCLUDE_ERROR_BODY=1` to include it while
debugging; known key values are redacted either way, but redaction only catches values it knows.
Treat any error text you paste elsewhere as potentially sensitive.

`TOKEN_BUDGET_PER_RUN` and `COST_BUDGET_USD_PER_RUN` appear in the contract document and are
**not implemented here** — they are listed in `VERIFICATION.md` as a known gap rather than
silently accepted and ignored.

## Verification

`VERIFICATION.md` states exactly what was tested and what was not. The short version: the local
tests pass against a **real local HTTP server**, and **a reviewer — not this repository — made
the one live ATK call on record**, using their own credential. Nothing here was run against ATK
by its author.

```bash
python3 -m unittest test_atk_provider -v
```

## Honest status of this asset

This is a **standalone example**, not yet an integration with any tool from
`registry/materials.json`. The reviewer's point stands: *"every integration must first write a
common adapter"* is a claim this delivery does not evidence, and ATK's own native MCP and
OpenAI-compatible configuration may be all some assets ever need. Use this when you are writing
Python and want one call that survives changing providers.

## Next integration

The example addresses the same user problem as
[`headroom`](https://github.com/headroomlabs-ai/headroom) (Apache-2.0, in
`registry/materials.json`): long tool output arriving at a model. Headroom compresses it;
this truncates and says so. Wiring headroom in front of this seam is the natural next asset —
**not done here, and no compression or saving is claimed.**

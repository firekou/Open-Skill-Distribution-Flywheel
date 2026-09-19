# ATK Provider Seam

A **single stdlib Python file** that implements the Provider Interface from
[`ATK_ROUTING_INTEGRATION.md`](../../ATK_ROUTING_INTEGRATION.md) §4, plus a runnable example.

The contract was written down and never implemented. **This is not a prerequisite for every
integration** — ATK's native MCP and OpenAI-compatible configuration may be all some assets ever
need (see "Honest status" below). It is for the case where you are writing Python and want one
call that survives changing providers.

> **ATK may be the default. ATK may never be the only option.**

## Quick Start — ATK, two minutes

Official docs: <https://aitokenking.com.tw/assets/docs/zh-Hant/index.html#mcp-server>

```bash
cd integrations/atk-provider
cp .env.example .env
```

Fill in two lines in `.env` (**the base URL is already correct — leave it**):

```bash
ATK_API_KEY=<your key>
ATK_MODEL=claude-sonnet-4.6
```

Load it, **then** list the models your key can reach:

```bash
set -a && . ./.env && set +a          # load FIRST: the curl below needs $ATK_API_KEY

curl -s "$ATK_BASE_URL/models" -H "Authorization: Bearer $ATK_API_KEY" \
  | python3 -m json.tool | head
```

Run it against the sample log in this directory — no file of your own needed:

```bash
python3 example_summarise_tool_output.py --file sample-build.log
```

> **Key naming.** The official docs call it `AITOKENKING_API_KEY`; this repository's contract
> (`ATK_ROUTING_INTEGRATION.md` §3) calls it `ATK_API_KEY`. **For this Python code either works** —
> `ATK_API_KEY` is the name used here and the official spelling is accepted as an alias.
>
> **The alias is Python-side only.** The `curl` above reads `$ATK_API_KEY` from your shell, so if
> your `.env` uses `AITOKENKING_API_KEY`, either set `ATK_API_KEY` too or substitute it in the
> command. Don't set both to different values.

**No credential yet?** The example runs without one:

```bash
python3 example_summarise_tool_output.py --dry-run --file sample-build.log
python3 example_summarise_tool_output.py --dry-run --show-payload --file sample-build.log
```

`--dry-run` shows what would be sent and sends nothing. By default it prints a **preview** — the
first 300 characters of each message. `--show-payload` prints the **complete JSON request body,
built by the adapter that would send it** (so the Anthropic shape differs from the OpenAI one —
that is real, not a display quirk). It needs a configured provider, and declines rather than
guessing if there is none. Headers are never printed, because one of them is your key.

**Requirements:** Python 3.9+. **No dependencies** — standard library only.

## ATK MCP — no code needed at all

ATK also publishes an MCP server. If your client speaks MCP, **you do not need this adapter**:
point the client at the endpoint and you are done.

```
endpoint: https://api.aitokenking.com.tw/mcp
header:   X-Aitokenking-Api-Key: <your key>
```

**This is a conceptual example, not a config file you can paste.** MCP client configuration
differs between clients, and **`${VAR}` expansion inside a config file is a per-client feature,
not part of MCP** — several clients will pass that string through literally and send it as your
key. Check your own client's documentation for how it injects headers from the environment (some
support an explicit env-to-header mapping), and read the key from the environment rather than
writing it into a file you commit.

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
the one live ATK call on record**, using **a credential the owner supplied and authorised for a
minimal test** (not the reviewer's own account). **That live call was made against commit
`f2a2188`**, and is not promoted to any later head. Nothing here has been run against ATK by its
author.

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

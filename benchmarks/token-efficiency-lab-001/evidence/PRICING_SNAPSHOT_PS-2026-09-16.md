# Pricing Snapshot — PS-2026-09-16

**Snapshot ID:** `PS-2026-09-16`
**Captured:** 2026-09-16
**Methodology:** v1.1.0 §11
**Machine-readable form:** `evidence/PRICING_SNAPSHOT_PS-2026-09-16.json`
**Supersedes:** `PS-2026-09-15` — which is **not** overwritten, amended or re-dated (§11.1). It
remains on disk unchanged.

**Currency:** USD · **Billing unit:** USD per 1,000,000 tokens

## Method

Every vendor pricing page was fetched directly with `curl -sSL` over the session's egress proxy on
**2026-09-16**, the HTML tags were stripped, and the numbers were read out of the resulting text.
The pages are JS-heavy; where a number is only rendered client-side, that is stated explicitly
below and the rate is either taken from the page's own shipped data (with the provenance noted) or
recorded `BLOCKED`.

**No price in this snapshot was recalled, estimated, or carried across from `PS-2026-09-15`.** The
single carried-over row is `lab/replay-synthetic`, which is labelled in the JSON as
`synthetic_not_a_vendor_rate: true` and is not a price anyone pays.

Rules applied, per §11.2 and §11.7:

- A missing rate is **never** `0`.
- A dimension the vendor genuinely does not bill is `not_applicable` **with the quoted source text**.
- A rate that could not be read is `"BLOCKED"`, with what is missing and the URL that was tried.

## Preflight verdicts

Run against `environment/harness/pricing_preflight.py` on 2026-09-16.

| Model list | Verdict |
|---|---|
| The 13 models a Lab 001 run plan would plausibly name (4 OpenAI flagship, `gpt-5`, `gpt-5-mini`, 4 Anthropic, 2 DeepSeek, `lab/replay-synthetic`) | **PASS** — 0 blocks, 0 warnings |
| All 30 entries in this snapshot | **BLOCK** — 3 blocks, all `cache_read` on OpenAI pro-tier models (see Limitations L‑2) |
| `PS-2026-09-15`, for contrast, on just `gpt-5, gpt-5-mini, claude-opus-5, deepseek-v4-pro` | **BLOCK** — 4 blocks |

A PASS here is a completeness statement only. It is **not** provider-native meter calibration —
different gate, neither implies the other (§11.8).

---

## Anthropic — `https://docs.claude.com/en/docs/about-claude/pricing`

Read directly on 2026-09-16. The page carries a full table with base input, 5m cache writes, 1h
cache writes, cache hits/refreshes, and output.

**Plan:** Claude API (first-party) · standard service tier (not Batch API, not Fast mode) ·
`inference_geo=global` (default) · full 1M context at standard pricing.

| Model | Base input | 5m cache write | 1h cache write | Cache hit / refresh | Output |
|---|--:|--:|--:|--:|--:|
| Claude Fable 5.1 | 10.00 | 12.50 | 20.00 | **0.25** | 50.00 |
| Claude Opus 5 | 5.00 | 6.25 | 10.00 | **0.50** | 25.00 |
| Claude Sonnet 5 | 2.00 | 2.50 | 4.00 | **0.20** | 10.00 |
| Claude Haiku 4.5 | 1.00 | 1.25 | 2.00 | **0.10** | 5.00 |

The cache-hit column is the one `PS-2026-09-15` was missing for all four models. It was on the
page the whole time.

**Two entries per model, not one.** The TTL tier is priced *through* the cache-write rate
(`5-minute cache write | 1.25x base input price`, `1-hour cache write | 2x base input price`), so
each model appears twice with a distinct key — `anthropic/claude-opus-5` (5-minute, the documented
default) and `anthropic/claude-opus-5@1h-cache`. Flattening the two into one row is exactly the
mistake that lost the cache rates last time.

`anthropic/claude-opus-5@fast-mode` is a third entry (input 10.00 / output 50.00). Its cache rates
are **applied multipliers**, not cells read verbatim — see Limitations L‑3.

**Excluded dimensions**

- `cache_ttl` → `not_applicable`. The multiplier table prices the TTL inside the write rate; with
  the tier fixed in `plan`, no residual TTL charge exists.
- `other_fees` → `not_applicable`, **scoped**: *"Client-side tools are priced the same as any other
  Claude API request, although server-side tools can incur additional charges based on their
  specific usage."* Lab 001 workloads A–E use a locally hosted MCP toolset
  (`tasks/TASK_SET_v1.0.0/corpora/mcp_toolset/server.py`), i.e. client-side. Anthropic server-side
  tools *are* separately billed on the same page ($10 per 1,000 web searches; $0.05/hour/container
  beyond 1,550 free hours) and an attempt that enables one is **not** priced by this entry and is
  `unpriceable` under §11.4.

**Token inclusion**

- `cached_tokens_in_input` = **additional**. *"total_input_tokens = cache_read_input_tokens +
  cache_creation_input_tokens + input_tokens"* and *"Important: input_tokens does NOT represent all
  input tokens — only the portion after your last cache breakpoint."*
- `reasoning_tokens_in_output` = **included**. *"monitor the usage.output_tokens_details.thinking_tokens
  field in the response, which reports how many of the billed output tokens were internal reasoning."*
- `reports_total` = **not_applicable**. The Messages API reports no total; the caching FAQ hands the
  caller a formula to compute one, and every published usage block on the pricing page carries only
  the parts.

---

## OpenAI — `https://platform.openai.com/docs/pricing`

Read directly on 2026-09-16. OpenAI prices by **service tier** (Standard, Batch, Flex, Fast mode)
**and by context length** (Short context, Long context), with four token columns per tier:
Input | Cached input | Cache writes | Output.

### Flagship line (Standard tier) — read from the server-rendered table

| Model | Short: Input | Cached in | Cache write | Output | Long: Input | Cached in | Cache write | Output |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| gpt-6-astra | 10.00 | 1.00 | 12.50 | 50.00 | 20.00 | 2.00 | 25.00 | 75.00 |
| gpt-5.6-sol | 4.00 | 0.40 | 5.00 | 20.00 | 8.00 | 0.80 | 10.00 | 30.00 |
| gpt-5.6-terra | 2.00 | 0.20 | 2.50 | 12.00 | 4.00 | 0.40 | 5.00 | 18.00 |
| gpt-5.6-luna | 0.20 | 0.02 | 0.25 | 1.20 | 0.40 | 0.04 | 0.50 | 1.80 |

Short and long context are **separate entries** (`openai/gpt-6-astra` and
`openai/gpt-6-astra@long-context`), not one flattened row.

### Legacy "All models" listing (Standard tier, short context)

| Model | Input | Cached input | Cache writes | Output |
|---|--:|--:|--:|--:|
| gpt-5.5 (<272K context length) | 5.00 | 0.50 | n/a | 30.00 |
| gpt-5.5-pro (<272K context length) | 30.00 | **BLOCKED** | n/a | 180.00 |
| gpt-5.1 | 1.25 | 0.125 | n/a | 10.00 |
| gpt-5 | 1.25 | 0.125 | n/a | 10.00 |
| gpt-5-mini | 0.25 | 0.025 | n/a | 2.00 |
| gpt-5-nano | 0.05 | 0.005 | n/a | 0.40 |
| gpt-5-pro | 15.00 | **BLOCKED** | n/a | 120.00 |
| o1-pro | 150.00 | **BLOCKED** | n/a | 600.00 |

`cache_writes` is `not_applicable` for every row above, on the vendor's own statement. The prompt
caching guide's *Summary of model differences* table, columns
`GPT-5.6 and later | GPT-5.5 and GPT-5.5 Pro | Other earlier models`, reads:
**"Cache write charge | 1.25× the uncached input-token rate | No additional cache-write charge |
No additional cache-write charge"**. That is a statement that the dimension is not billed, not an
absence of information — so it is `not_applicable` with evidence, not `BLOCKED`, and certainly not `0`.

**Excluded dimensions (all OpenAI entries)**

- `cache_ttl` → `not_applicable`: *"Prompt caching pricing varies by model. See API pricing for
  current cached-input and cache-write rates. Cache-write pricing is not an additive fee: input
  tokens use the uncached-input, cached-input, or cache-write rate."* plus *"reusing the prefix
  refreshes its lifetime without another cache-write charge."*
- `other_fees` → `not_applicable`, **scoped**: *"Responses API, Chat Completions API, Realtime API,
  Batch API, and Assistants API are not priced separately. Tokens are billed at the chosen model's
  input and output rates."* Scoped to requests using **no** built-in/server-side tools; built-in
  tools are separately billed on the same page and an attempt that enables one is `unpriceable`.

**Token inclusion**

- `cached_tokens_in_input` = **included**. The vendor's own cost formula:
  `ordinary_input_tokens = input_tokens - cached_tokens - cache_write_tokens`, and *"Cache-write
  pricing is not an additive fee: input tokens use the uncached-input, cached-input, or cache-write
  rate."* Pricing all of `input_tokens` at the uncached rate **and then** adding `cached_tokens`
  again would double-count by exactly the cached portion.
- `reasoning_tokens_in_output` = **included**. *"While reasoning tokens are not visible via the API,
  they still occupy space in the model's context window and are billed as output tokens."* The
  published usage block shows `output_tokens: 1186` with `output_tokens_details.reasoning_tokens: 1024`.
- `reports_total` = **included**. The published usage object carries `"total_tokens": 1261` against
  `input_tokens: 75` and `output_tokens: 1186` — 75 + 1186 = 1261.

---

## DeepSeek — `https://api-docs.deepseek.com/quick_start/pricing`

Read directly on 2026-09-16. DeepSeek publishes **four** input prices per model — cache-hit and
cache-miss, each in a peak and an off-peak window — plus two output prices.

Peak = 01:00–04:00 and 06:00–10:00 UTC, Mon–Fri. *"Off-peak rates are half of the peak rates."*

| Model (version) | Window | Input, cache miss | Input, cache hit | Output |
|---|---|--:|--:|--:|
| deepseek-v4-pro (DeepSeek-V4-Pro-0813) | off-peak | 0.66 | 0.022 | 1.98 |
| deepseek-v4-pro | peak | 1.32 | 0.044 | 3.96 |
| deepseek-flash (DeepSeek-V4.1-Flash) | off-peak | 0.15 | 0.003 | 0.60 |
| deepseek-flash | peak | 0.30 | 0.006 | 1.20 |

Peak and off-peak are **separate entries** (`deepseek/deepseek-v4-pro` and
`deepseek/deepseek-v4-pro@peak`). `rates.input` is the **cache-miss** price: DeepSeek splits every
input token into a hit or a miss, so the miss price *is* the uncached input price. An attempt that
crosses the boundary is priced wrong by a single entry and must be split or recorded as crossing it.

**Excluded dimensions**

- `cache_write` → `not_applicable`: *"We will bill based on the total number of input and output
  tokens by the model."* / *"The expense = number of tokens × price."* / *"prompt_tokens … It equals
  prompt_cache_hit_tokens + prompt_cache_miss_tokens."* Every input token is billed exactly once, as
  a hit or as a miss, so the tokens that populate the cache are billed at the cache-miss rate and
  there is no separate write charge to record. Caching is *"enabled by default for all users."*
- `cache_ttl` → `not_applicable`: *"Cache construction takes seconds. Once the cache is no longer in
  use, it will be automatically cleared, usually within a few hours to a few days."* There is no
  caller-selectable TTL tier and no TTL row in the price table.
- `other_fees` → `not_applicable`: *"The expense = number of tokens × price."*

**Token inclusion**

- `cached_tokens_in_input` = **included**. *"prompt_tokens integer required Number of tokens in the
  prompt. It equals prompt_cache_hit_tokens + prompt_cache_miss_tokens."*
- `reasoning_tokens_in_output` = **BLOCKED** — see Limitations L‑4.
- `reports_total` = **included**. *"total_tokens integer required Total number of tokens used in the
  request (prompt + completion)."*

---

## `lab/replay-synthetic` — not a model

Carried forward unchanged from `PS-2026-09-15` (input 1.00 / output 5.00 / cache read 0.10) and
flagged `synthetic_not_a_vendor_rate: true`. It exists so that offline harness dry-runs price
deterministically. **Any figure produced under it is plumbing verification, never a benchmark
result.** Its `not_applicable` evidence quotes the harness source, not a vendor page, because there
is no vendor and no account is billed.

---

## Findings

### F‑1 — The old snapshot's OpenAI models still exist, but none of them is a flagship model any more

The OpenAI flagship line on 2026-09-16 is **`gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`,
`gpt-5.6-luna`**. Not one of the eight models `PS-2026-09-15` recorded appears there.

**All eight are still on the page**, in the collapsed "All models" section:

| Old-snapshot model | Still listed? |
|---|---|
| `gpt-5.5-pro` (as `gpt-5.5-pro (<272K context length)`) | yes |
| `gpt-5-pro` | yes |
| `gpt-5.5` (as `gpt-5.5 (<272K context length)`) | yes |
| `gpt-5` | yes |
| `gpt-5.1` | yes |
| `gpt-5-mini` | yes |
| `gpt-5-nano` | yes |
| `o1-pro` | yes |

**None removed, none renamed, and no price has moved** — every input and output rate in
`PS-2026-09-15` still matches the page today. What `PS-2026-09-15` got wrong was **completeness, not
the numbers**: it omitted the cached-input column that was there all along, for OpenAI and for
Anthropic alike.

Two consequences worth recording. First, a run plan naming `gpt-5` or `gpt-5-mini` is still
priceable, but it is no longer pricing a current-generation model. Second, the C4 tier-adjacent
pairs in §8 were chosen against a lineup that has since moved; whether the intended "mid-tier
frontier ↔ next cheaper general-purpose tier" pairing still lands on the models §8 had in mind is a
question for whoever ratifies the run plan, not something this snapshot can settle.

### F‑2 — Anthropic token counts are NOT comparable across Claude model generations

Confirmed verbatim on the Anthropic pricing page:

> **"Claude 4.7 and later models and Claude Mythos Preview use a newer tokenizer that contributes to
> their improved performance on a wide range of tasks. This tokenizer produces approximately 30% more
> tokens for the same text. The exact increase depends on the content and workload shape. Claude
> Sonnet 4.6 and earlier models use the previous tokenizer."**

Of the models in this snapshot:

- **Newer tokenizer (4.7+):** `claude-fable-5-1`, `claude-opus-5`, `claude-sonnet-5`
- **Previous tokenizer (4.6 and earlier):** `claude-haiku-4-5`

**Why this matters to the lab.** §5.1's comparability constraint requires that the only permitted
difference between a treatment attempt and its baseline attempt is the registered intervention. A
C4 pair that puts **Claude Haiku 4.5 against Claude Opus 5 or Claude Sonnet 5** violates that for
**token counts**: the same text yields roughly 30% more tokens on one side of the pair for reasons
that have nothing whatsoever to do with the intervention. A measured "token saving" across that
boundary is partly a tokenizer artefact.

§12 already forbids reporting cross-provider token deltas where accounting is not like-for-like.
This finding extends that prohibition **within Anthropic**, across the 4.6/4.7 tokenizer boundary.
**Cost and cost-per-successful-task remain reportable** (the per-token rates are real and the
tokenizer difference is already inside the bill). **A token-count delta across that boundary is
not.**

### F‑3 — The meter's disjointness check encodes one provider's convention

`environment/harness/meter.py` raises `MeterError` when `cached_tokens > input_tokens`, with the
message *"the provider is not reporting these as disjoint"*. That check encodes the OpenAI/DeepSeek
convention, where cached tokens sit **inside** `input_tokens`. It is wrong for Anthropic, where
`total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens` and a
cache-heavy call legitimately reports `cache_read_input_tokens` far larger than `input_tokens` —
the pricing page's own example has `input_tokens: 105` against `cache_read_input_tokens: 7123`.

An Anthropic attempt with a large cached prefix would therefore either raise `MeterError` or, if an
adapter folds the fields together to avoid it, be mispriced. The per-model `token_inclusion` block
in this snapshot records the difference per provider; the meter must **read** it rather than assume
a single convention. Raised here as an evidence finding, **not fixed** — the meter is not this
seat's file to change.

---

## Limitations

Every `BLOCKED` row, and what would unblock it.

### L‑1 — The OpenAI short/long context threshold could not be read *(not a BLOCKED rate)*

The pricing tables are grouped under "Short context" and "Long context" column headers, but the
numeric token threshold is delivered only in a JS tooltip that is not server-rendered. The
**rates** for both tiers were read and are recorded; **which tier a given request falls into**
cannot be determined from what was read. The one exception is the legacy rows that carry the
threshold in the model name itself (`gpt-5.5 (<272K context length)`).

**Consequence:** a run that may straddle the threshold cannot be assigned to the right entry from
this snapshot alone.
**Unblocked by:** the threshold published in server-readable text, or a vendor statement of the
token boundary per model.

### L‑2 — `cache_read` is **BLOCKED** for three OpenAI pro-tier models

`openai/gpt-5.5-pro`, `openai/gpt-5-pro`, `openai/o1-pro`.

The page ships **no cached-input value** for these rows — the cell is empty / `-`. An empty cell is
not a price. And no OpenAI page read on 2026-09-16 states that prompt caching is unavailable or
unbilled for these models: the *Summary of model differences* table covers "GPT-5.6 and later",
"GPT-5.5 and GPT-5.5 Pro" and "Other earlier models" for the **write** charge, but says only
"Model-dependent cached-input rate" for the **read** charge, and the pro rows carry no such rate.

"We could not find it" and "it does not exist" are different statements, so these are `BLOCKED` —
not `not_applicable`, and emphatically not `0`. **These three rows are the entire reason the
all-30-entry preflight returns BLOCK.** They were not trimmed from the snapshot to manufacture a
PASS; they are reported.

**URLs tried:** `https://platform.openai.com/docs/pricing`,
`https://platform.openai.com/docs/guides/prompt-caching`.
**Unblocked by:** a cached-input rate for these models published on the pricing page, **or** a
vendor sentence stating that prompt caching does not apply to them.
**Workaround if a run needs them:** none from this snapshot. Under §11.4 any attempt on these models
that returns `cached_tokens > 0` is `unpriceable`, and the harness must not estimate.

### L‑3 — Anthropic Fast mode cache rates are applied multipliers, not read cells

`anthropic/claude-opus-5@fast-mode` carries `cache_read: 1.00` and `cache_write: 12.50`. The page
publishes **only input and output** for Fast mode. These two numbers are the page's own documented
multipliers applied to the Fast mode base input rate — *"Fast mode pricing stacks with other pricing
modifiers: Prompt caching multipliers apply on top of fast mode pricing"*, with *"Cache read (hit) |
0.1x base input price"* and *"5-minute cache write | 1.25x base input price"*, giving
0.1 × $10 = $1.00 and 1.25 × $10 = $12.50.

They are arithmetic on quoted rules rather than cells read verbatim, and are flagged
`derived_rate_note` in the JSON. **Lower confidence than every standard-tier row.**
**Unblocked by:** an explicit Fast mode cache-rate table on the vendor page.

### L‑4 — DeepSeek `reasoning_tokens_in_output` is **BLOCKED**

DeepSeek publishes `reasoning_tokens` nested under `completion_tokens_details` — *"reasoning_tokens
integer Tokens generated by the model for reasoning"* — but states nowhere that was read on
2026-09-16 whether those tokens are counted **inside** `completion_tokens` or are **additional** to
it, nor at what rate they are billed. The Thinking Mode guide describes `reasoning_content`
behaviour and says nothing about billing.

The field nesting *suggests* inclusion. That is an inference, not a vendor statement, so it is not
recorded as fact. Guessing here would misstate DeepSeek output cost by the whole reasoning portion,
which on a thinking-mode run is most of the completion.

**URLs tried:** `https://api-docs.deepseek.com/api/create-chat-completion`,
`https://api-docs.deepseek.com/guides/thinking_mode`,
`https://api-docs.deepseek.com/quick_start/token_usage`.
**Unblocked by:** a DeepSeek sentence stating whether reasoning tokens are included in
`completion_tokens` and at what rate they are billed.

> **Note on preflight coverage.** `pricing_preflight.py` checks only that each of the three
> `token_inclusion` keys is *present*; it does not reject a `"BLOCKED"` value the way it rejects a
> `"BLOCKED"` rate. So L‑4 does **not** surface as a preflight block. It is recorded here because a
> gate that cannot see a gap is not the same thing as there being no gap.

### L‑5 — Legacy OpenAI rows come from the page's shipped data, not from rendered cells

The four flagship rows are server-rendered and were read as table cells. The legacy "All models"
rows are collapsed behind an expander and are **not** server-rendered; their numbers were taken from
the pricing data the page itself ships for those rows. That data is the vendor's own and, for the
four flagship models, matches the rendered **short-context** cells exactly (e.g. gpt-6-astra
10 / 1 / 12.5 / 50), which is why the legacy rows are recorded as short-context standard-tier rates.

The **long-context** cells for legacy rows are computed client-side by
`/_astro/pricing.BUoGAsc4.js`, which the egress proxy returns **403** for. Those rates were not read
and are **not** recorded. A legacy-model run above the context threshold is not priced by this
snapshot.

### L‑6 — Plans deliberately not priced here

Recorded so that nobody reads a silence as a zero:

- **Anthropic:** Batch API (*"a 50% discount on both input and output tokens"*) and the
  `inference_geo: "us"` 1.1× data-residency multiplier. Both are different plans; neither is priced
  by these entries.
- **OpenAI:** Batch, Flex and Fast mode tiers, all published on the page, all omitted here because
  no Lab 001 condition currently declares them. Also the 10% regional-processing uplift.
- **Both:** server-side / built-in tool fees, scoped out of `other_fees` with the quoted evidence
  above. An attempt that enables one is `unpriceable` under §11.4.
- **All vendors:** these are list rates. Negotiated enterprise rates are not visible and are not
  recorded.

Adding any of these is a **new snapshot with a new ID**, never an edit to this one (§11.1).

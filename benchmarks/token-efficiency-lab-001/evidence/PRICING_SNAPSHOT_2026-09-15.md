# Pricing Snapshot — 2026-09-15

**Snapshot ID:** `PS-2026-09-15`
**Method:** primary vendor pricing pages read directly. **OBSERVED.**
**Purpose:** evidence for E007; required `pricing_snapshot_id` for Lab 001 runs.

Token counts are physical; prices move. Every Lab run references this snapshot by ID so a
later price change cannot retroactively alter a measured result.

## OpenAI — `developers.openai.com/api/docs/pricing`

| Model | Input $/1M | Output $/1M |
|---|--:|--:|
| o1-pro | 150.00 | 600.00 |
| **gpt-5.5-pro** (<272K ctx) | **30.00** | **180.00** |
| gpt-5-pro | 15.00 | 120.00 |
| gpt-5.5 (<272K ctx) | 5.00 | 30.00 |
| gpt-5 | 1.25 | 10.00 |
| gpt-5.1 | 1.25 | 10.00 |
| gpt-5-mini | 0.25 | 2.00 |
| gpt-5-nano | 0.05 | 0.40 |

## DeepSeek — `api-docs.deepseek.com/quick_start/pricing`

DeepSeek publishes **four** input prices per model: cache-hit / cache-miss × peak / off-peak.
Peak = 01:00–04:00 and 06:00–10:00 UTC, Mon–Fri. Off-peak rates are half of peak.

| Model | Input cache-hit (off/peak) | Input cache-miss (off/peak) | Output (off/peak) |
|---|--:|--:|--:|
| **deepseek-v4-pro** | 0.022 / 0.044 | **0.66 / 1.32** | **1.98 / 3.96** |
| deepseek-flash | 0.003 / 0.006 | 0.15 / 0.30 | 0.60 / 1.20 |

## Anthropic — Claude API first-party rates

| Model | Input $/1M | Output $/1M |
|---|--:|--:|
| Claude Fable 5.1 | 10.00 | 50.00 |
| Claude Opus 5 | 5.00 | 25.00 |
| Claude Sonnet 5 | 2.00 | 10.00 |
| Claude Haiku 4.5 | 1.00 | 5.00 |

*Anthropic figures from the bundled `claude-api` reference (cached 2026-06-24), not re-fetched
from the pricing page this run. Lower confidence than the two above; refresh before any
Anthropic-specific cost claim.*

## Limitations

1. Anthropic row is from a cached reference, not a live page read.
2. Batch, priority, cached-input and volume tiers are not fully enumerated.
3. Context-length tiers exist (the GPT-5.5 rows are the <272K tier) and change prices above
   that threshold.
4. Prices are list rates; negotiated enterprise rates are not visible.

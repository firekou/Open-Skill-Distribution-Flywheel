# Meter Calibration Design v1.0.0 (FROZEN)

**Bound to:** `METHODOLOGY_v1.0.0.md` §8 · **Status: FROZEN** · **Gate: LG5 depends on this**

## Prohibition

**`bytes / 4`, character counts, and any other uncalibrated estimator are PROHIBITED as
benchmark ground truth.**

This is not theoretical. `rtk-ai/rtk`'s own README states it ships no tokenizer and estimates
`bytes / 4`, and its issue tracker carries 14 reports disputing the resulting figures — one
repro at **>10,000×** (Evidence Ledger E001, E003). An uncalibrated meter does not produce a
noisy number; it produces a number with no defined relationship to the thing being measured.

## Ground truth

**The provider-native `usage` field is ground truth.** The ATK Token Meter is validated against
it and is never a substitute for it.

Every run record carries `token_source ∈ {provider_usage_field, atk_meter}`. A run whose
`token_source` is `atk_meter` **without a passing calibration for that provider** is void.

## The nine quantities — definitions frozen before measurement

| # | Quantity | Definition | Source of truth |
|---|---|---|---|
| 1 | Input tokens | Provider's reported prompt tokens for the request | `usage` field |
| 2 | Output tokens | Provider's reported completion tokens | `usage` field |
| 3 | Cached tokens | Tokens served from a provider cache, **reported separately, never folded into input** | `usage` cache field |
| 4 | Tool-schema tokens | Tokens attributable to tool definitions. **Measured by difference**: identical request with and without the tool block | Two calls, differenced |
| 5 | Tool-result tokens | Tokens attributable to tool results entering context | Differenced per turn |
| 6 | Retry tokens | Tokens spent on attempts that did not produce the accepted answer. **Counted, never discarded** | Sum over attempts |
| 7 | Escalation tokens | Tokens spent on the model escalated *to*, recorded separately from the original attempt | Per-call attribution |
| 8 | Total cost | Σ(tokens × rate) using `pricing_snapshot_id`, with cached tokens at the cached rate | Snapshot + usage |
| 9 | **Cost per successful task** | Total cost of **every** attempt ÷ tasks that passed the quality floor | Derived |

Quantity 9 is the headline. A run that is cheap per call and fails the floor costs infinity per
successful task, and reporting only per-call cost would hide that.

## Calibration procedure — 6 runs (frozen matrix §5)

1. For each provider in the matrix, issue identical requests and record both the provider
   `usage` field and the ATK Token Meter.
2. Compute per-quantity relative error.
3. **Acceptance: |relative error| ≤ 1% on input, output and total tokens.**
4. A provider failing acceptance is recorded as **not meter-comparable**. Its runs may still
   execute using the provider `usage` field directly, but **no ATK-meter-derived delta may be
   reported for it.**

## Cross-provider comparability — recorded, not assumed

Different providers tokenize differently. The same text is not the same token count across
providers, and no calibration fixes that.

**Rule:** cross-provider token deltas are **not reportable** as efficiency findings. Only
**within-provider, within-tokenizer** deltas are. Cross-provider comparison is permitted on
**cost** and on **cost per successful task**, where the unit is money, not tokens — and must
state both the pairing and `pricing_snapshot_id` (Decision Ledger D011).

Where a provider's accounting cannot be compared like-for-like, that is recorded in the run
record and repeated in any result derived from it. **It is a finding, not a footnote.**

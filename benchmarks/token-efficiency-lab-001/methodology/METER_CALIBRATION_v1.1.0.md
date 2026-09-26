# Meter Calibration Design v1.1.0

**Status:** **DRAFT / REVIEW_PENDING** · bound to `METHODOLOGY_v1.1.0.md` §12 · Gate: LG5
**Derives from:** `METER_CALIBRATION_v1.0.0.md` (sha256 `3ed9dac6…a98aa`, **unmodified**)

> v1.0.0 is not edited. This is a new file. Everything in v1.0.0 that is not listed under
> "What changed" below is carried forward **unchanged in substance**.

## What changed from v1.0.0

| # | Change | Why |
|---|---|---|
| 1 | **Token inclusion relationships are declared per provider** | Cached and reasoning tokens were double-countable against a total that already contained them |
| 2 | **Cost completeness** is explicit: retries, failed calls, escalation targets and intervention-issued calls all count | An intervention's cost includes the cost of running it |
| 3 | **An offline accumulator check is named as a separate result** and may not be reported as calibration | The 2026-09-16 round produced exactly this confusion and had to resolve it |
| 4 | **Automatic provider-side caching** counts toward completeness | A run plan that says "cold" does not stop a provider serving a cache hit |

## Prohibition — unchanged

**`bytes / 4`, character counts, and any other uncalibrated estimator are PROHIBITED as benchmark
ground truth.**

Measured, not asserted: on the v1.0.0 calibration fixture the `bytes/4` error ranged from
**13.6%** (English prose) to **61.0%** (minified JSON) and **changed sign**. No calibration factor
corrects an estimator whose error depends on the input. *(Those magnitudes are against a
synthetic fixture and describe no real provider; only the structural claim carries.)*

## Ground truth — unchanged

**The provider-native `usage` field is ground truth.** The ATK Token Meter is validated against
it and is never a substitute for it. Every record carries
`token_source ∈ {provider_usage_field, atk_meter}`. A record whose `token_source` is `atk_meter`
without a passing calibration for that provider is **`INVALID`** (v1.1.0 §6.2).

## The nine quantities — unchanged definitions

| # | Quantity | Definition | Source |
|---|---|---|---|
| 1 | Input tokens | provider's reported prompt tokens | `usage` |
| 2 | Output tokens | provider's reported completion tokens | `usage` |
| 3 | Cached tokens | served from a provider cache, **reported separately, never folded into input** | `usage` cache field |
| 4 | Tool-schema tokens | **measured by difference**: identical request with and without the tool block | two calls |
| 5 | Tool-result tokens | differenced per turn | two calls |
| 6 | Retry tokens | attempts that did not produce the accepted answer. **Counted, never discarded** | sum over attempts |
| 7 | Escalation tokens | the model escalated *to*, recorded separately | per-call |
| 8 | Total cost | Σ(tokens × rate) under `pricing_snapshot_id`, cached at the cached rate | snapshot + usage |
| 9 | **Cost per successful task** | total cost of **every** attempt ÷ attempts passing the floor | derived |

Quantity 9 is the headline. An attempt that is cheap per call and fails the floor costs infinity
per successful task, and reporting only per-call cost would hide that. Under v1.1.0 §6.2 the
denominator counts `PASS` only, while the numerator includes `FAIL_QUALITY` and `INVALID`
attempts — **the cost of failure is real cost**.

## 1. NEW — token inclusion, declared per provider

Before any run, the snapshot declares for each provider, with the vendor page as evidence:

| Declaration | Values |
|---|---|
| Are cached tokens **included in** the reported input total, or **additional to** it? | `included` / `additional` |
| Are reasoning tokens **included in** the reported output total, or **additional**? | `included` / `additional` / `not_applicable` |
| Does the provider report a `total` that already sums the parts? | `yes` / `no` |

The meter applies the declaration. **An undeclared provider is a blocking preflight failure**, not
a default. Guessing produces a number that is wrong by exactly the size of the cached portion —
which, on a cache-heavy run, is most of it.

## 2. NEW — cost completeness

Total cost for an attempt includes **every** call the attempt caused:

- the accepted call,
- **retries and failed calls**,
- the **model escalated to**, priced at its own rate,
- **calls the intervention itself issues** — a compression pass, a routing classifier, a
  summariser. An intervention that spends tokens to save tokens is measured net, not gross.

An intervention whose own calls are not instrumented cannot be measured and its cells are
`INVALID`.

## 3. Calibration procedure — unchanged, with the separation made explicit

1. For each provider in the run plan, issue identical requests and record **both** the provider
   `usage` field and the ATK Token Meter.
2. Compute per-quantity relative error.
3. **Acceptance: |relative error| ≤ 1% on input, output and total tokens.**
4. A provider failing acceptance is recorded **not meter-comparable**. Its runs may still execute
   using the provider `usage` field directly, but **no ATK-meter-derived delta is reportable**.

### 3.1 NEW — what an offline accumulator check is, and is not

An offline check over recorded or synthetic `usage` blocks tests **ATK's arithmetic**: retry
tokens counted rather than discarded, cached tokens kept separate, escalation attributed to the
right model, each call priced at its own rate. That is a real and checkable property and it is
worth testing.

**It is not calibration.** It says nothing about whether ATK's figures match what a provider
reported, because no provider was involved. A round that reports an accumulator PASS as
"calibration passed" has reported a result it does not have.

**Calibration requires live provider calls and therefore a benchmark credential.** Where none
exists, calibration is **BLOCKED** — a declared stop condition — and the Pilot gate stays shut.

## 4. Cross-provider comparability — unchanged

Different providers tokenize differently. The same text is not the same token count across
providers and no calibration fixes that.

**Rule:** cross-provider **token** deltas are **not reportable** as efficiency findings. Only
within-provider, within-tokenizer deltas are. Cross-provider comparison is permitted on **cost**
and **cost per successful task**, where the unit is money — and must state both the pairing and
`pricing_snapshot_id` (Decision Ledger D011).

Where a provider's accounting cannot be compared like-for-like, that is recorded in the run
record and repeated in any result derived from it. **It is a finding, not a footnote.**

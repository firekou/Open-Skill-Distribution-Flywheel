# Lab 001 — Meter Calibration Result (Phase E)

**Date:** 2026-09-16 · **Spec:** `methodology/METER_CALIBRATION_v1.0.0.md` (FROZEN)
**Acceptance:** |relative error| ≤ 1% on input, output and total tokens

# Verdict: **FAIL — not executed as specified**

The accumulator passed every case. The comparison the spec actually requires was never run,
because it cannot be run without a benchmark credential. Those are two different results and
collapsing them into one "PASS" would be the most consequential dishonesty available in this
round.

---

## Two questions, only one of them answerable here

`METER_CALIBRATION_v1.0.0.md` defines calibration as comparing **the ATK Token Meter against the
provider-native `usage` field**, over 6 dedicated runs. That is question 2 below. Question 1 is a
prerequisite that is easy to mistake for the whole thing.

| | Question | Answerable offline? | Result |
|---|---|---|---|
| **1** | Is ATK's accumulator arithmetically correct over a set of usage blocks? | **Yes** — arithmetic does not care where the numbers came from | **PASS**, 6/6 cases, 72 quantities |
| **2** | Do the numbers ATK reads match what a real provider reported and charged? | **No** — requires issuing real requests | **BLOCKED** |

**Phase E as specified is question 2.** It was not performed.

---

## Question 1 — accumulator: PASS

Run inside the locked container, `--network none`.

| Case | What it is adversarial against | Result |
|---|---|---|
| **CAL-001** | Nothing — the control. One accepted call, no cache, no retry | PASS |
| **CAL-002** | A meter that records only the accepted call: it would report 9,800 input tokens instead of 28,200 — a **65% undercount**, and it would look entirely plausible | PASS |
| **CAL-003** | A meter that prices all 40,000 input tokens at the uncached rate: $0.028182 instead of $0.005214, a **5.41× overstatement** | PASS |
| **CAL-004** | A meter applying one run-level rate: it would price all 22,600 input tokens at whichever model it picked, and would hide that the escalation is where the money went | PASS |
| **CAL-005** | Any meter that handles retry, cache and escalation correctly in isolation but loses one when they interact | PASS |
| **CAL-006** | Reporting "8,000 vs 8,000 input tokens, identical efficiency" across two different tokenizers — the numbers match and the comparison is meaningless | PASS |

**6/6 cases, 12 quantities each, 72 checks, zero mismatches.**

Every expected value was computed by explicit arithmetic in the fixture generator, **not by
running the meter**. The fixture carries `cost_working` showing the per-call arithmetic so a
reviewer can check it by hand. A fixture whose expectations came from the meter would prove only
that the meter agrees with itself.

Fixture: `environment/calibration/FIXTURE_v1.0.0.json`,
sha256 `c5ae60a194a8ffa95be2b7638d023fc76b61ea2b7e50c8f868789ebc17f93f5b`.

### What question 1 establishes

The meter counts retry tokens instead of discarding them (quantity 6). It keeps cached tokens
separate and prices them at the cached rate instead of folding them into input (quantity 3). It
attributes escalation tokens to the model escalated **to** and prices every call at that call's
own rate (quantity 7). It fires the cross-provider guard when a run spans tokenizers (quantity
comparability). And `CallUsage` **refuses construction** for any `token_source` other than
`provider_usage_field`, so an estimated count cannot enter the run path at all.

### What question 1 does not establish

That the meter has ever been right about a real provider. It has never spoken to one.

---

## Question 2 — provider-native comparison: BLOCKED

```
PROVIDER-NATIVE COMPARISON: BLOCKED
no benchmark credential is available (LAB001_BENCHMARK_API_KEY is unset), so no
provider-native usage field can be obtained for any request.
```

This is a **declared stop condition** in the frozen methodology — *"benchmark credentials are
unavailable"* — and the instruction attached to it is to record the failure, not improvise
around it.

The harness enforces the surrounding guardrail too. `harness/providers.py` will read exactly one
credential, `LAB001_BENCHMARK_API_KEY`, provisioned for this lab. If that is absent but an
ambient production key is present, it **raises rather than falling back**:

> refusing to run: … is present in the environment, but these are production credentials and
> guardrail 10 forbids their use. Provision a lab-scoped, spend-limited key as
> `LAB001_BENCHMARK_API_KEY` instead.

No credential was sought, read, or echoed at any point in this round.

### What it will take to answer question 2

A benchmark-scoped key with a hard spend cap, and the 6 calibration runs from the frozen matrix.
Cost is negligible — these are small identical requests, well under a dollar. **Provisioning the
credential is an Editor-in-Chief decision, not a technical obstacle.**

---

## The prohibited estimator, measured rather than asserted

`bytes / 4` is prohibited as benchmark ground truth. The prohibition has until now rested on
citing `rtk`'s issue tracker. The fixture measures it directly:

| Sample | Content kind | `bytes/4` | Fixture's count | Error |
|---|---|--:|--:|--:|
| EST-001 | English prose | 450 | 396 | 13.6% |
| EST-002 | Python source | 502 | 720 | 30.3% |
| EST-003 | Minified JSON | 390 | 1,000 | **61.0%** |
| EST-004 | CJK text | 660 | 880 | 25.0% |
| EST-005 | Base64 blob | 440 | 760 | 42.1% |

The shape matters more than the magnitudes: the error is **not a constant offset**. It swings
from 13.6% to 61.0% depending on what the content is, and it changes sign. A calibration factor
cannot fix an estimator whose error depends on the input. A benchmark that used it would report
differences between conditions that are artefacts of content type.

**Hard caveat, stated because this table is the most quotable thing in this document:** the
"fixture's count" column is **assumed, not provider-reported**. These numbers characterise the
estimator against the fixture's own tokenizer assumptions. **They say nothing about OpenAI,
Anthropic or DeepSeek and must never be quoted as if they did.** The finding here is structural —
that the error is content-dependent — not numerical.

`bytes_over_four()` exists only in `harness/calibrate.py`, is imported by nothing in the run
path, and could not be used as a token source even if it were, because `CallUsage` rejects it.

---

## Consequence for the Pilot gate

The Phase F gate requires **LG3 PASS · Task Set frozen · Answer Key frozen · Meter Calibration
PASS**, all four.

Meter Calibration is **FAIL**. The gate does not open. No Calibration Pilot run was executed.

## Evidence produced

| | |
|---|---|
| ATK accumulator correctness over adversarial usage patterns | **TESTED** — real code, really executed, 72 checks |
| ATK meter agreement with any real provider | **not established at any level** |
| `bytes/4` error is content-dependent | **TESTED against a synthetic fixture only**; not evidence about any provider |

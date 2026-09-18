# Unit economics — what is measured, and what is not

Per the work package: **contribution per unit = service revenue actually received − variable cost
of delivering that unit.** Company profit additionally subtracts fixed cost. Impressions and page
reads are not booked as revenue.

**Headline: revenue to date is 0, units delivered to date are 0, so contribution per unit is
undefined — not zero, undefined.** The table below is the cost structure a first unit would have,
with each line marked measured or unmeasured. It is a model to be filled in, not a result.

## Revenue lines, kept separate so nothing is double counted

| Line | To date | Note |
|---|--:|---|
| A. Paid service revenue received | **0** | No price set, no payment path exists |
| B. ATK routing gross margin from traffic this asset sends | **unknown** | Not attributable: the asset does not tag requests, and our test calls returned `cost_usd: null`, so we cannot compute margin even on our own usage |
| C. Brand exposure | **not revenue** | Recorded as reach if it ever occurs; never booked as income |

A and B must never be added together for the same request. A is what the buyer pays us for the
engagement; B is what ATK earns on tokens the buyer would have spent anyway. Reporting one number
covering both would be counting the same customer twice.

## Variable cost of one paid engagement

| Line | Status | What it would take to measure |
|---|---|---|
| Model tokens for the A/B runs | **partially measured** — our own run used ~81k prompt tokens for one workload's two tasks × two paths | Multiply by the buyer's prompt count; convert at their rate card |
| Model cost in currency | **unmeasured** | Our provider reported `cost_usd: null`. Needs a plan with per-call cost reporting, or the rate card applied manually |
| Search / retrieval | **≈0** | No paid search used |
| Compute | **≈0 marginal** | headroom runs locally; the proxy is a laptop process |
| Payment processing | **unmeasured** | No processor chosen. Typically a percentage plus a fixed fee per transaction |
| Human/agent delivery time | **unmeasured** | The dominant cost. This asset took one working session to produce, but that was the first of its kind; a repeat engagement is the number that matters and we have not run one |
| Rework | **unmeasured, and known to be non-trivial** | This deliverable needed several correction rounds. An engagement priced on the first-attempt cost would lose money |

## What this says right now

1. **The largest cost line is delivery labour and it is unmeasured.** Any price set today would be
   a guess, which is why none is set.
2. **The free tier's cost is real but small and non-recurring**: one verification, published once,
   reusable by everyone. That is the tier the evidence currently supports.
3. **Rework is the risk to contribution**, not model tokens. Model tokens for one engagement are
   small next to the time spent getting the measurement right and defensible.
4. **Nothing here justifies scaling supply.** With zero external requests, adding agents or roles
   increases cost with no revenue line to offset it.

## The first number worth getting

Not a price — a demand signal. One person outside this repository asking for the paid version, or
one recorded external use of the free version. Until then, every figure in this document except
"0" is a placeholder, and marked as one.

# Sample deliverable — paid tier

**This is a reviewable sample, not a live service.** No price is set here, no payment path exists,
no account can be charged, and nobody has bought this. Setting a price is an owner decision and is
deliberately left blank rather than invented.

The free sample (`SERVICE_SAMPLE_FREE.md`) answers *"does this class of tool work, and can I check
that claim myself."* That question is answered once and given away. This tier exists only if
someone needs the part that cannot be answered once for everybody.

## What the extra money buys, stated as a difference

| | Free | Paid |
|---|---|---|
| The recommendation | one verified tool, one workload we chose | the shortlist for **your** workload, with the ones we rejected and why |
| The measurement | our log, our prompt, our provider | **your** log sample and **your** prompts, against **your** provider and plan |
| The number | % prompt tokens on our test | tokens *and* the currency figure on your actual rate card, with the break-even volume |
| Quality risk | one needle, one prompt | your retrieval cases run both ways, with a list of what compression loses on your data |
| Integration | a README you follow | a working configuration in your stack, with the rollback step |
| Freshness | the date on the page | re-verification on a stated cadence, and a notice when the upstream breaks the integration |
| Failure | you are on your own | a named contact, a fix or a refund |

**The honest one-line version: the free tier proves the category works; the paid tier tells you
whether it works on your data, and what it is worth in your currency.**

## Scope of one engagement

1. You send a representative payload sample and 5–10 prompts you actually run.
2. We run each both ways against the provider and plan you actually use.
3. You get: token and currency deltas per prompt, the break-even volume, the cases where
   compression changed the answer, the configuration, and the removal procedure.
4. If the measured saving on your data does not clear the threshold agreed before we start, the
   engagement is refunded. We do not get paid for finding out it does not help you.

**Not included:** running your production traffic, holding your credentials, or any ongoing
service. This is a one-off measurement engagement with a deliverable, not a subscription.

## Pricing unit — deliberately unfilled

The unit is **one engagement as scoped above**, not per-seat and not per-token. A recurring
re-verification would be a separate, smaller unit.

| | |
|---|---|
| Price | **not set** — owner decision, no figure invented here |
| Payment | **no path exists.** No account, no processor, no x402/AP2 integration. Nothing here can take money |
| Refund trigger | measured saving below the pre-agreed threshold |
| Authorisation | must come from the paying organisation, not from an agent acting on its own |

## What must be true before this is worth offering at all

Listed as unproven, because they are:

1. Someone outside this repository asks for it. **Zero such requests to date.**
2. The variable cost of delivering it is below any price a buyer would accept
   (see `UNIT_ECONOMICS.md` — several cost lines are currently unmeasured).
3. The free tier is actually being found and used. **No external usage recorded to date.**

Offering a paid tier before (1) and (3) is building a shop before checking the street has people
on it. This sample exists to be reviewed, not to be launched.

## Conflict-of-interest rule this sample commits to

The paid engagement measures whether a tool helps **you**. It is paid for by the buyer, never by
the tool's vendor, and a "no, this will not save you enough" result is a delivered result that
still gets paid for — otherwise the measurement is worthless. Sponsorship, where it exists, is
labelled and kept out of the recommendation, exactly as in the free sample.

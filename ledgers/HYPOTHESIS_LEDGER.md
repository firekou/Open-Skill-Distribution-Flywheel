# ATK Hypothesis Ledger

| ID | Hypothesis | Type | Confidence | Next validation/falsification | Status |
|---|---|---|---|---|---|
| H001 | Agent scale increases demand for Measurement / Attribution / Trust | Market | H1 Signal | Demand + counterevidence research, then willingness-to-pay test | ACTIVE |
| H002 | Token Cost is a strong wedge into Agent Resource Intelligence | Product | H1 Signal | Compare with reliability, security, budget control, attribution and routing | ACTIVE |
| H003 | Technical Intelligence Magazine can be a low-CAC ATK distribution/trust engine | Distribution | H0 Idea | Instrument content IDs and downstream actions | ACTIVE |
| H004 | Agent-native organization increases verified output per human hour | Operating Model | H0 Idea | Measure AI cost, review time, rework and verified output | ACTIVE |
| H005 | Verification gains value as AI generation becomes cheaper | Market/Product | **H1 Signal** | Compare verified vs unverified asset behavior | ACTIVE |
| H006 | Agent Unit Economics becomes a management discipline | Market | H0 Idea | Research vocabulary, tooling and buying behavior | WATCH |
| H007 | Cost per successful task beats raw token price for many decisions | Product | H0 Idea | Benchmark + decision-use testing | WATCH |
| H008 | Quality-adjusted routing beats cheapest routing | Product | H0 Idea | Routing benchmark | WATCH |
| H009 | Machine-readable Trust Receipts become useful in enterprise Agent operations | Product | H0 Idea | Use-case research | WATCH |
| H010 | Human + Agent demand signals predict priorities better than editorial intuition | Operating Model | H0 Idea | Compare predicted and observed performance | WATCH |
| H011 | ATK's value may develop in the order **Measurement → Verification → Quality-adjusted Economics → Routing**, each layer being the precondition for the next | Market/Product | **H0 Idea** | Customer evidence: who pays for measurement before they pay for routing, and in what order. **Not** more internal benchmark work | ACTIVE |

Confidence: H0 Idea; H1 Signal; H2 Supported; H3 Tested; H4 Validated; H5 Commercially Proven.


---

## Review decisions applied — 2026-09-15

**Editor-in-Chief / ChatGPT review, 2026-09-15.**

- **H005 H0 Idea → H1 Signal — APPROVED and applied above.** Rationale: multiple cases show a
  material gap between secondary reporting and primary source, including ATK's own incorrect
  savings figure. Sufficient for Signal; **not** sufficient for H2 Supported.
- **H001, H002, H003, H004, H006–H010 — maintained at current levels.** No change applied.

**New this cycle, not yet reflected in any confidence level:** E007 was upgraded to OBSERVED and
its figures corrected. Per the review guardrails, a successful price-gap verification **does not**
establish H002, and price gap is **not** willingness-to-pay evidence. H002 stays at H1 Signal.

---

## Pending confidence proposals — Phase D, 2026-09-15 (superseded by the decisions above)

**The Confidence column above is unchanged.** Claude may not alter strategic confidence.
These are proposals for Editor-in-Chief decision, with the evidence and the counterevidence.

| ID | Current | Proposed | Evidence for | Evidence against | Claude's recommendation |
|---|---|---|---|---|---|
| **H001** | H1 Signal | **H1 Signal — no change** | E003: users of the largest token tool independently file issues demanding accurate savings measurement, and upvote each other. E006: academic work independently frames routing as a trust problem | **E008: every measurement/trust project is small** — 202 to 3,199 stars against 80,473 for pure cost reduction | **Do not upgrade.** The supporting and opposing evidence are of comparable weight. E003 is 14 issues from a complainer-biased sample; E008 is consistent with either an underserved market or no market. Upgrading here would be the convenient answer, not the supported one |
| **H002** | H1 Signal | **H1 Signal — no change, but flagged** | E014: token cost is the fastest-growing category found | **E005: platform vendors reported to give routing away free** — material counterevidence, currently only REPORTED | **Do not upgrade, and raise E005 to OBSERVED before the next review.** If Cloudflare and Vercel genuinely commoditise the layer, H002's wedge narrows and the strategy changes. That is worth one hour of reading vendor docs |
| **H005** | H0 Idea | **H1 Signal** | E001 + E002: both market-leading projects' primary claims were materially more careful than their secondary coverage. E004: **ATK itself published two inflated figures** by trusting a paraphrase, then caught it only by reading the source | Sample is three cases, one of them ATK. No evidence anyone *pays* for verification | **Upgrade to H1 Signal.** H1 requires a signal, not proof. Three independent instances of "the primary source was more careful than the report of it" is a signal that verification has value. It is nowhere near H2 |
| **H004** | H0 Idea | **H0 Idea — no change** | E012: 71-seat organization instantiated, 14 separation-of-duties invariants machine-enforced | **No seat has executed a real task.** The organization is built and unexercised | **Do not upgrade.** Building an org says nothing about output per human hour. H004 needs a measured cycle, not a registry |

**Net: one proposed upgrade (H005 H0→H1), three explicit non-upgrades.**

H003, H006–H010 unchanged: no evidence was gathered this cycle that bears on them.

### Why so few upgrades

The doctrine requires active counterevidence search for important hypotheses. This cycle found
counterevidence against both ACTIVE hypotheses — E008 against H001, E005 against H002 — and it
is as strong as the supporting evidence. Recording that honestly is the point of the ledger.

**The fastest way to move H001 is not more research.** It is a willingness-to-pay or usage test
(D007). Desk research has reached its limit on this question.


---

## H011 — added 2026-09-16, and what it is NOT supported by

The 2026-09-16 repair round found a long list of measurement and verification defects in **ATK's
own benchmark**: a task that was unpassable in every condition, a task that rewarded discarding
86% of its document, evidence that was specified but produced by nothing, a zero-tolerance
criterion that failed open on an empty container, a scorer whose per-field rule was a no-op, and
a meter that mispriced an entire provider's caching convention.

That is a genuine observation, and it is an observation about **one team's own machinery**. It
supports a narrow claim: *building a benchmark whose numbers can be trusted is materially harder
than it looks, and a verification process catches things reading does not.*

**It does not support any of these, and none may be written anywhere:**

- that a market exists for measurement or verification,
- that any customer would pay for it, or how much,
- that ATK has an advantage at it,
- that ATK can deliver credible savings — **nothing has been measured yet**,
- any upgrade to H001–H010, or to the Lab's H1–H4.

**A repair round that goes well is evidence about the repair, not about the market.** If finding
44 defects in one's own instrument were market evidence, every well-run lab would be a business.

### What would actually move H011

External, and none of it is desk research: which layer a customer buys **first**; whether anyone
pays for measurement while routing is free (E005 established that routing, gateway and provider
aggregation are commoditized to zero at two major vendors, while measurement, attribution and
governance are metered — a vendor price list is what a vendor charges, not what a market pays);
and whether a verified figure changes a purchasing decision.

H011 is recorded at **H0 Idea** and stays there until customer evidence exists. This round did
not build any product and must not be read as having started one.

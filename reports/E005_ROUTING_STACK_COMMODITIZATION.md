# E005 — Which layer of the AI routing stack is being commoditized?

**Date:** 2026-09-16 · **Evidence state: REPORTED → OBSERVED**
**Method:** Cloudflare and Vercel **primary vendor documentation read directly.**

> The review asked for the layer answer, not the free/paid answer. That framing turned out to
> matter: the original claim is **confirmed for one layer and contradicted for four others.**

---

## 1. What the primary sources say

### Cloudflare AI Gateway — `developers.cloudflare.com/ai-gateway/reference/pricing/`

| Item | Published position |
|---|---|
| Gateway + routing | **Free** |
| Dashboard analytics, caching, rate limiting | **Free on all plans** |
| Provider token markup | **None** — *"Inference pricing from providers is passed through with no markup"* |
| Logs | Free, but **storage is metered**: Workers Free **100,000 logs total across all gateways**; Workers Paid **10,000,000 logs per gateway** |
| Logpush (export to your own store) | **Workers Paid only** — 10 million/month, then **+$0.05/million** |
| Guardrails | **Billed as Workers AI token inference** |
| Unified Billing | **5% fee on all credits purchased** |

### Vercel AI Gateway — `vercel.com/docs/ai-gateway/pricing`

| Item | Published position |
|---|---|
| Token markup / platform fee | **"AI Gateway charges no markup and no platform fee on tokens."** |
| BYOK | **"With BYOK, there is no markup or fee from AI Gateway."** |
| Free tier | A **subset** of models, lower per-model rate limits |
| **Custom Reporting** (tags, user IDs, quota entity IDs → **attribution**) | **$0.075 / 1,000 writes** + **$5 / 1,000 queries** |
| **Provider allowlist** (governance) | **$0.10 / 1,000 successful requests**, Pro + Enterprise only |
| **Zero Data Retention** (compliance) | **$0.10 / 1,000 requests** team-wide, Pro + Enterprise only |
| **Trace Drains** (observability export) | **$0.05 / 1,000 traces + $0.50 / GB egress**, Pro + Enterprise only |
| Budgets | Available (team / project / key / member) |

---

## 2. The layer answer

| Layer | Cloudflare | Vercel | Commoditized? |
|---|---|---|---|
| **Routing** | Free | Free, zero markup | **YES — to zero** |
| **Gateway** | Free | Free | **YES — to zero** |
| **Provider aggregation** | Free | Free, incl. BYOK | **YES — to zero** |
| **Observability (dashboard)** | Free | Included | **YES — basic tier** |
| **Observability (export)** | Logpush: paid plan, +$0.05/M | Trace Drains: $0.05/1k + $0.50/GB | **NO — metered** |
| **Measurement (log retention)** | 100k free → 10M paid tier | — | **NO — metered** |
| **Attribution** | — | Custom Reporting: $0.075/1k writes, **$5/1k queries** | **NO — explicitly metered** |
| **Budget control** | — | Budgets available | **Partially free** |
| **Governance** | Guardrails billed as inference | Allowlist $0.10/1k; ZDR $0.10/1k | **NO — metered** |
| **Verification** | Not offered | Not offered | **NEITHER VENDOR PROVIDES IT** |

### The finding in one line

**Routing has been commoditized to zero. Measurement, attribution, governance and export have
not — and the companies doing the commoditizing are the ones metering those layers.**

Vercel charges **$5 per 1,000 queries** to ask its own system what a request cost and who
incurred it. That is the clearest single data point in this run: the layer ATK's thesis targets
is the layer a commoditizer chose to keep priced.

---

## 3. What this does to E005 as originally written

| Original | Verdict |
|---|---|
| "Cloudflare AI Gateway free on every plan, 24 providers, OpenAI/Anthropic-compatible endpoint" | **CONFIRMED** for routing, gateway and basic analytics |
| "Vercel ~45 providers BYOK no markup" | **CONFIRMED**, in the vendor's own words |
| The inference drawn from it — *"platform vendors are commoditising the layer ATK sells, so H002's wedge narrows"* | **NOT SUPPORTED.** They commoditized routing. They did not commoditize measurement, attribution, governance or export |

The original evidence was correct; **the inference built on it was too broad.** It read
"routing is free" as "the stack is free". The stack is not free above the routing layer.

---

## 4. What this does NOT establish

Stated explicitly, because the guardrails require it and because the temptation runs the other
way:

1. **This does not establish H002.** Showing that vendors meter measurement is not the same as
   showing customers will pay ATK for it. **H002 stays at H1 Signal.**
2. **This is not willingness-to-pay evidence.** A vendor's price list shows what a vendor
   charges, not what a market pays. Two companies pricing a layer is weak positive evidence at
   best, and both have distribution ATK does not.
3. **"Routing is free" does not mean ATK has no commercial value** — and equally, "measurement
   is metered" does not mean ATK has one. Both inferences are unearned.
4. **Verification being absent from both vendors is ambiguous.** It reads as an opening; it
   reads equally as a feature nobody has asked for. Same unresolved question as `RESEARCH_REPORT`
   §6.2. **Only a usage or willingness-to-pay test settles it** (Decision Ledger D007).

## 5. Limitations

- Two vendors. Kong, Portkey, LiteLLM, Bedrock and Vertex were not read this run.
- Published list prices only; enterprise agreements are not visible.
- Pricing pages change. This is a **2026-09-16 snapshot**.
- Cloudflare's page did not specify budget enforcement or audit features either way; absence
  from a pricing page is not evidence of absence in the product.

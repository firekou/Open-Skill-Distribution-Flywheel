# AI Agent Tooling & LLM Routing — Market Research Report

**Prepared for:** AI Token King (ATK) · **Date:** 2026-09-15
**Evidence base:** 188 catalogued materials · **Status:** Draft for external review

---

## 0. How to review this document

This report is written to be **attacked**, not agreed with. It is self-contained: no
knowledge of the source repository is needed.

Every claim carries a confidence label:

| Label | Meaning |
|---|---|
| **[OBSERVED]** | Measured directly from a primary API or read from a primary source page |
| **[REPORTED]** | Stated by a secondary source (search summary, blog, vendor copy) — **not independently confirmed** |
| **[INFERENCE]** | My reasoning on top of the above. This is where the report is most likely to be wrong |

**The most useful review would focus on §6 (Where this argument is weakest).** Those are the
load-bearing assumptions I could not verify. Attacking §5 (the strategic argument) is more
valuable than correcting §3 (the data), because the data is mechanically reproducible and the
argument is not.

Known bias to account for: this research was commissioned by a company that sells LLM token
routing. A finding that routing is defensible is the convenient answer. §6.2 and §6.7 are
where that bias would most plausibly have distorted the conclusions.

---

## 1. The question

ATK operates an LLM routing and token service. It proposes an open-source distribution
strategy: find useful AI tooling, improve and maintain it, redistribute it, and let ATK
routing be the default path underneath.

**The question this research answers:** what is actually happening in AI agent tooling right
now, and does that landscape support or undermine that strategy?

---

## 2. Method

Two sweeps, both on 2026-09-15.

| Run | Framing | Sources | Result |
|---|---|---|---|
| Sweep 1 | "What can we fork?" | GitHub repository search | 68 candidates |
| Sweep 2 | "What should we understand?" | GitHub + engineering blogs + arXiv + Hugging Face + Hacker News + community + curated indexes | 188 materials |

**Instruments.** GitHub repository search API (metrics and licence metadata), direct file
reads from `raw.githubusercontent.com` (licence texts), and web search across engineering
blogs, arXiv and community sources.

**Scoring.** Each material scored /100 on six axes. Three axes — technical utility, ATK
relevance, content potential — were assigned by review. Three — momentum, experimentability,
source credibility — are derived by fixed published rules from snapshot metrics, so the long
tail is not given precision it has not earned. All totals are recomputed by a validator that
fails on mismatch.

**What was not done, and it matters:**

- **Nothing was executed.** No tool was installed, run, or benchmarked. Every efficiency
  claim in this report is a claim someone else made.
- **No source code was read.** Repository assessment is from metadata, descriptions and
  documentation only.
- **Star counts are a snapshot.** They move, and they are an imperfect adoption proxy (§6.4).

---

## 3. What the evidence base contains

**188 materials** — 164 code repositories, 24 non-repository (engineering posts, papers,
community signals, curated indexes).

| Category | Count | | Licence | Count |
|---|--:|---|---|--:|
| Routing / gateways | 42 | | MIT | 52 |
| Agent skills | 37 | | Unresolved | 79 |
| Token optimisation | 28 | | Apache-2.0 | 23 |
| MCP ecosystem | 28 | | Editorial (n/a) | 24 |
| Agent frameworks | 28 | | | |
| Agent-to-agent | 25 | | Apache-2.0 / MIT mixed | 2 |
| | | | AGPL-3.0 | 3 |
| | | | Restrictive (BUSL / ELv2 / CC-NC-ND) | 3 |
| | | | No licence at all | 2 |

52 materials score ≥80.

**Verification split of the 24 non-repository materials: 5 read from the primary source, 19
from search summaries.** The 19 are flagged individually. Several of the most quotable figures
in this report sit in that group.

---

## 4. Findings

### F1 — Token cost is the dominant growth theme in developer AI tooling **[OBSERVED]**

Two projects created in January 2026 each passed 70,000 GitHub stars within eight months:

| Project | Stars | Created | Licence | What it does |
|---|--:|---|---|---|
| `rtk-ai/rtk` | 80,473 | 2026-01-22 | Apache-2.0 | CLI proxy; cuts up to 90% of **bash output**, which its README states is explicitly not a 90% bill cut |
| `headroomlabs-ai/headroom` | 72,266 | 2026-01-07 | Apache-2.0 | Compresses tool output, logs and RAG chunks; own scenario table reports **21–57%** |

Neither is a model, a framework, or an agent. Both are **cost-reduction plumbing**. Around
them sit 26 more token-optimisation projects, and the theme has independent community
validation (a Hacker News launch thread for one of them).

The framing that recurs across these projects: *agentic products make dozens to hundreds of
model calls per task, so a cheap per-token price still produces an expensive per-task bill.*
Star counts of this size, this fast, indicate the pain is widely felt.

### F2 — Platform vendors are giving the routing layer away **[REPORTED]**

| Vendor | Offering |
|---|---|
| **Cloudflare AI Gateway** | Managed AI routing and observability proxy, **free on every Cloudflare plan** — analytics, caching, rate limiting at no charge. 24 native providers. Universal REST endpoint (May 2026) accepting OpenAI and Anthropic request formats. |
| **Cloudflare Agents Week** (Aug 2026) | 20+ launches in two weeks: agent wallet with verifiable identity, Identity-Aware AI Gateway, persistent Agent Memory, DeepSeek models with ~1M-token context on edge compute. |
| **Cloudflare + OpenAI Agent Cloud** (Apr 2026) | Enterprise agent runtime, GPT-5.4 and Codex in a unified catalogue. |
| **Vercel AI Gateway** | Hundreds of models across ~45 providers, one key, **BYOK with no markup**. |

This is the finding that most changes ATK's strategic picture, and it is **[REPORTED]** — it
comes from search summaries and vendor documentation pages, not from hands-on testing. §6.1
says what would confirm it.

### F3 — Licence restrictiveness tracks competitive proximity to ATK **[OBSERVED]**

Eight materials carry a licence that constrains ATK's proposed redistribution model. The
deliberately restrictive ones cluster in exactly the categories closest to ATK's own business:

| Project | Licence | Effect |
|---|---|---|
| `ThinkWatchProject/ThinkWatch` | **BUSL-1.1** | Self-describes as *not* open source. Free production use capped at **10M tokens and 10k MCP calls per month**, then paid. Converts to GPL-2.0-or-later in 2030. |
| `mksglu/context-mode` | **Elastic-2.0** | Fork and redistribute permitted; offering it as a **hosted service** is not. |
| `theopenco/llmgateway` | **AGPL-3.0** + commercial `ee/` tier | Two independent blocks. |
| `calesthio/OpenMontage` | **AGPL-3.0** | Network copyleft. |
| `hesreallyhim/awesome-claude-code` | **CC BY-NC-ND 4.0** | No commercial use, no derivatives. |

Meanwhile permissive licences (MIT, Apache-2.0) dominate the agent-skills category.

The ThinkWatch case is the sharpest: **its licence thresholds are denominated in tokens and
MCP calls** — the same units ATK's business is measured in. Anyone operating at ATK's scale
crosses them by design.

A correction worth recording: an earlier pass assumed non-standard licences would mostly be
clerical variations of standard ones. Six were read in full; **two were permissive, four were
deliberately restrictive.** An unusual licence usually means the author chose one on purpose.

### F4 — The best available technique is an Anthropic engineering post, not a product **[OBSERVED]**

[*Code execution with MCP: building more efficient AI agents*](https://www.anthropic.com/engineering/code-execution-with-mcp)
(Anthropic, Nov 2025 — read from source).

Agents connected to many MCP servers pay twice: every tool definition is loaded into context
upfront, and every intermediate tool result passes back through the model. Anthropic's worked
example puts a two-hour meeting transcript at **~50,000 extra tokens from intermediate results
alone**. Having the agent write code that calls tools, rather than calling each tool directly,
removes both costs.

It is a technique rather than a product, so it can be tested, measured, taught and built on
with **no licensing question at all**. Anthropic's context-engineering cookbook (Mar 2026)
covers memory, compaction and tool clearing and is runnable as-is.

### F5 — Academic work independently frames routing as a trust problem **[REPORTED]**

Six 2026 arXiv papers on routing and cascades appear in the evidence base. Two matter here:

- [*Cluster, Route, Escalate: Cascaded Framework for Cost-Aware LLM Serving*](https://arxiv.org/abs/2606.27457)
  — cluster queries to the cheapest adequate model, escalate on a quality estimate; reported
  to retain **97–99% of the strongest model's accuracy**. This is the academic form of what
  commercial routers claim to do.
- [*Model Routing as a Trust Problem: Route Receipts for Adaptive AI Systems*](https://arxiv.org/pdf/2605.01710)
  — frames routing as a **trust** problem and proposes verifiable receipts recording which
  model actually served a request and why.

Also observed: a **51M-parameter router model** (`Supra-Router-51M`) on Hugging Face — small
enough to run in-process, which makes routing decisions nearly free.

### F6 — Framing the search as "what can we fork?" caused a category-sized blind spot **[OBSERVED]**

Same researcher, same tools, same day, different question:

| | Sweep 1 ("what can we fork?") | Sweep 2 ("what should we understand?") |
|---|--:|--:|
| Materials found | 68 | 188 |
| Token-optimisation materials | **2** | **28** |
| `rtk` (80k stars) found? | **No** | Yes |
| `headroom` (72k stars) found? | **No** | Yes |

Sweep 1 missed the two largest projects in the fastest-growing category, because a fork-first
filter discards anything that is not a viable fork target *before* asking whether it is
important. **Forkability and importance are weakly correlated**, and filtering on the first
destroys visibility into the second.

---

## 5. The strategic argument

Stated as a chain so each link can be attacked separately.

> **L1** Agentic workloads make per-task token cost the thing developers actually feel. **[OBSERVED — F1]**
>
> **L2** That pain is large enough to drive 70k+ stars in eight months for pure cost plumbing. **[OBSERVED — F1]**
>
> **L3** The price spread between cheap and frontier models is wide enough that routing captures real value. **[OBSERVED — verified 2026-09-15. The spread is real but smaller than ATK claimed: 11.4× like-for-like, not ~100×. See §6.1]**
>
> **L4** But platform vendors now give routing away free, bundled with distribution ATK cannot match. **[REPORTED — F2]**
>
> **L5** Therefore ATK cannot differentiate on price or provider count. **[INFERENCE from L4]**
>
> **L6** The gap those free gateways leave is measurement: cost attribution, model-choice transparency, auditability. Vendor documentation describes them as proxies with analytics, not audit systems; one is reported to lack guardrails and semantic cache entirely. **[REPORTED + INFERENCE]**
>
> **L7** Academic work independently arrives at the same framing — routing as a trust problem requiring verifiable receipts. **[REPORTED — F5]**
>
> **L8** Therefore ATK's defensible position is trust and measurement, not price. **[INFERENCE]**

**The economic argument for L8:** a free gateway has no incentive to prove what it did with
your request. Its business is the platform it is attached to. A paid routing layer's entire
value proposition is that the customer can verify what they bought. That asymmetry is
structural, not a feature gap a competitor closes in a quarter.

**The argument against L8, which I cannot currently refute:** every project sitting in that
gap is tiny.

| Project | Stars |
|---|--:|
| `liaohch3/claude-tap` (agent traffic inspection) | 3,199 |
| `crwdla/tokentab` (per-model cost accounting) | 1,136 |
| `toby-bridges/api-relay-audit` (LLM proxy security audit) | 836 |
| `RelayPlane/proxy` (run cost metering, kills runaways) | 202 |

Against 80,473 for a tool that just makes things cheaper.

**Two readings fit this data equally well.** Either measurement is an underserved opportunity,
or developers do not currently pay for it. **This research cannot distinguish between them**,
and the distinction decides whether the strategy is sound. §7 proposes how to find out.

---

## 6. Where this argument is weakest

Ranked by how much damage each would do if wrong.

### 6.1 ~~The ~100× price gap is unverified~~ — RESOLVED 2026-09-15, and it was wrong

**Verified from primary vendor pricing pages.** Snapshot:
`benchmarks/token-efficiency-lab-001/evidence/PRICING_SNAPSHOT_2026-09-15.md`.

The frontier half of the claim was right: **gpt-5.5-pro is $30 in / $180 out**. The cheap half
was not: **no DeepSeek price of $0.44 exists.** deepseek-v4-pro cache-miss is $0.66/$1.32 input
and $1.98/$3.96 output. The nearest real figure to $0.44 is **$0.044 — the cache-*hit* peak
input rate**, an order of magnitude out, which suggests the original comparison set a cache-hit
price against a cache-miss price.

**Computed gaps, all cache-miss, blended 3:1 input:output:**

| Comparison | Gap |
|---|--:|
| **gpt-5.5 vs deepseek-v4-pro — like-for-like tiers** | **11.4×** |
| gpt-5.5 vs deepseek-flash | 42.9× |
| gpt-5.5-**pro** vs deepseek-v4-pro | 68.2× |
| gpt-5.5-**pro** vs deepseek-flash | 257.1× |
| flash peak *input* vs gpt-5.5-pro *input* | exactly 100× |

**The finding is not "the gap is smaller".** It is that **a single price-gap multiple is
meaningless without its pairing.** DeepSeek publishes four input prices per model (cache
hit/miss × peak/off-peak); OpenAI prices by context tier; Anthropic's own range spans 10×
internally. Almost any multiple between 11× and 300× can be produced honestly by choosing
different, defensible endpoints.

Routing still captures real value — **but tier-adjacent routing, the common case, is worth
~10×, not ~100×.** Any ATK material must state the pairing (Decision Ledger D011).### 6.2 "Measurement is defensible" has no demand evidence

§5 argues it from supply-side observations (vendor gaps, academic framing) and my own
reasoning. **There is no evidence anyone pays for it.** The star counts weakly suggest the
opposite. This is also precisely where the commissioning bias noted in §0 would show up — it
is the conclusion most favourable to ATK, and the one with the thinnest support.

### 6.3 Zero measurements were taken — and two figures here were wrong

Every efficiency figure quoted is a claim by the party that benefits from it. **None was
reproduced.** A report that repeats vendor benchmarks without testing them is marketing with
footnotes.

> **Correction, 2026-09-15.** An earlier version of this report quoted `rtk` as claiming
> "60–90% token reduction" and `headroom` as claiming "60–95% fewer tokens". Both came from
> search-engine summaries. Both READMEs were subsequently read directly and **neither project
> claims what this report said it claimed**: `rtk` cuts up to 90% of *bash output* and
> explicitly says that is not a 90% bill reduction, while `headroom`'s own scenario table
> reports 21–57%. The primary sources are markedly more careful than the coverage of them.
> Full detail: `reports/TOP30_R3.md` §1.
>
> This is the exact failure the evidence ladder exists to prevent, committed in the document
> that defines the ladder. It is recorded rather than quietly patched.

### 6.4 Stars are a weak adoption proxy

Growth of 70,000 stars in eight months is unusual enough to warrant suspicion. Stars measure
attention, not use, and are gameable. The finding "token cost is the dominant theme" would
survive some star inflation; the specific ranking of projects would not.

### 6.5 Sampling bias toward English-language GitHub

Search ran mostly against English topic tags. The Chinese ecosystem is visible in the results
but under-sampled relative to its real size, and X, Reddit and YouTube were reached only
through third-party write-ups rather than their own surfaces.

### 6.6 Scoring is uncalibrated

The /100 scores rank materials sensibly against each other but are calibrated against nothing,
because there are no outcomes yet. Treat them as ordering, not measurement.

### 6.7 ATK's own product was never examined

This report analyses the market ATK operates in **without ever verifying ATK's routing works,
is reliable, or does the things the strategy assumes**. If ATK's routing cannot produce a
verifiable record of which model served a request, then L8 recommends a position ATK cannot
currently occupy. An external reviewer cannot check this; ATK can, and should, before acting
on §5.

---

## 7. What would settle the open questions

In order of value per hour spent.

| # | Action | Resolves | Cost |
|---|---|---|---|
| 1 | Read the three provider pricing pages | §6.1 — the load-bearing number | ~10 min |
| 2 | Run Anthropic's context-engineering cookbook, record measured token deltas | §6.3 — first real number | ~half a day |
| 3 | Deploy Cloudflare AI Gateway and Vercel AI Gateway; list concretely what they do not do | §6.1 of F2, and L6 | ~1 day |
| 4 | Run `toby-bridges/api-relay-audit` against ATK's own routing | §6.7 | ~half a day |
| 5 | Ship a minimal cost-attribution receipt and see if anyone uses it | §6.2 — the demand question | ~1 week |

Item 5 is the only one that tests the central thesis. Items 1–4 make the rest of the report
trustworthy; item 5 decides whether the strategy is right.

---

## 8. Summary for a reviewer

**What I am confident about:** token cost is the dominant growth theme in developer AI tooling
(F1), licence restrictiveness tracks competitive proximity (F3), and framing a search around
forkability destroys visibility into importance (F6). These are measured, reproducible, and
would survive most challenges.

**What I believe but cannot prove:** that platform vendors commoditising routing pushes ATK
out of price competition and into measurement and trust (§5, L4–L8). The supply-side evidence
is consistent and triangulates from three directions. The demand-side evidence does not exist.

**What I would most like challenged:** §5 L5 → L8. Specifically — is "developers will pay for
verifiable routing" a real market, or is it the comfortable conclusion for a company that
sells routing? §6.2 is my own best argument against my own conclusion, and I do not think it
is resolved.

---

## Appendix — reproduction

| Artefact | Contents |
|---|---|
| `registry/materials.json` | All 188 materials with scores, licences, verification flags |
| `reports/BENCHMARK_R2_001.md` | Sweep 2, GitHub phase — 164 materials, four ranked lists |
| `reports/BENCHMARK_R2_002.md` | Sweep 2, non-GitHub phase — the other four source classes |
| `reports/CANDIDATE_REGISTRY.md` | Sweep 1 — 68 candidates, fork-first framing |
| `LICENSE_REVIEW.md` | Licence gate procedure and per-licence rulings |
| `tools/build_materials.py` | Scoring and action routing — the derivation rules |
| `tools/score.py` | Validator; fails on any score/licence inconsistency |

```bash
python3 tools/build_materials.py    # rebuild the registry
python3 tools/score.py              # validate every score and licence invariant
```

All repository metrics are a 2026-09-15 snapshot from the GitHub repository search API.
Licences were confirmed against GitHub licence metadata; the six that GitHub could not
identify were fetched and read in full.

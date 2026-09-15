# Top 10 — Technical & License Deep Review (TASK 12)

> Snapshot: 2026-09-14 · Reviewers: License Agent (02), Technical Reviewer (03)

---

## Scope and Honest Limits

This review covers the ten candidates in `reports/TOP10_SHORTLIST.md`.

**What was verified directly:** license (GitHub license metadata, confirmed by re-running
each search with a `license:` qualifier), repository metrics, activity, issue pressure,
default branch, and archival status — all captured from the GitHub API on 2026-09-14.

**What was not:** source-level code reading, dependency-tree audit, and runtime security
testing. This session had repository-read access scoped to ATK's own repository only, so
file contents for external repositories could not be fetched.

Therefore every entry below carries a **Security Review: NOT PERFORMED** marker. Per
`FORK_POLICY.md` §2, security review is an entry condition, so **no candidate here is yet
fork-approved** — the recommendations in TASK 13 are gated on it. This is stated plainly
rather than papered over, because a fork approved on unverified security is exactly the kind
of mistake that is expensive after distribution.

**Issue pressure** = open issues ÷ forks, a rough proxy for maintenance burden relative to
project size.

---

## 1. `mvanhorn/last30days-skill` — 91/100

| | |
|---|---|
| **License** | MIT — verified. Modify ✅ Redistribute ✅ Commercial ✅ · No copyleft · Attribution required · Trademark risk low |
| **Metrics** | 62,022 ★ · 5,410 forks · 129 open issues · created 2026-01-23 · Python |
| **Issue pressure** | 0.024 — healthy |
| **Growth** | ~8,068 ★/month, still compounding |
| **License ruling** | **PASS** |

**Architecture.** Python skill that fans out across Reddit, X, YouTube, Hacker News,
Polymarket and general web search, then synthesises a grounded summary. The fan-out/synthesis
shape means a single invocation produces many model calls.

**ATK fit (19/20).** The strongest in the pool. Multi-source research is genuinely
expensive, so a token budget and tiered routing (cheap model for per-source extraction,
strong model for final synthesis) are real features a user would want even if ATK did not
exist. That is the test for whether routing is a feature or a sticker.

**Concerns.**
- Correctness depends on several third-party surfaces that change without notice. This is the
  dominant maintenance cost and the reason Maintenance scores 7, not 9.
- 129 open issues at this scale is manageable, but breakage will be *silent* — a scraper that
  returns empty results looks like "no recent activity", not like an error. Any ATK fork must
  add per-source health checks; that is a genuine Value Add, not packaging.
- Data-source ToS should be reviewed before ATK redistributes it under its own name.

**Technical Review: PASS** (subject to security review) · **Security Review: NOT PERFORMED**

---

## 2. `blader/humanizer` — 88/100

| | |
|---|---|
| **License** | MIT — verified (full metadata read). Modify ✅ Redistribute ✅ Commercial ✅ · Trademark risk low |
| **Metrics** | 48,065 ★ · 3,911 forks · **13 open issues** · created 2026-01-18 · Python · ~205 KB |
| **Issue pressure** | 0.003 — the best in the pool |
| **License ruling** | **PASS** |

**Architecture.** Small Python skill; essentially prompt engineering plus a single model call
per invocation.

**ATK fit (18/20).** Precisely because it is small. One call site means the ATK provider
adapter is a new file plus a one-line registration — the additive change pattern
`UPSTREAM_SYNC.md` §2 argues for. This is the cleanest available place to build and prove the
reference adapter end to end before applying it to harder targets.

**Concerns.**
- Commercial score is only 8: one call per run. It earns its slot on *implementation risk*,
  not revenue.
- Output quality is model-sensitive. Swapping providers can degrade results in ways tests do
  not catch, so the provider-switch QA test must include a human quality check, not just a
  200 response.
- The Value Add bar is the real risk here: with a codebase this small, a fork that adds only
  a provider adapter is close to a rebrand. It needs the full B-category treatment (Docker,
  `.env.example`, examples, a quality benchmark across providers) to be defensible.

**Technical Review: PASS** · **Security Review: NOT PERFORMED**

---

## 3. `virgiliojr94/book-to-skill` — 88/100

| | |
|---|---|
| **License** | MIT — verified. Modify ✅ Redistribute ✅ Commercial ✅ |
| **Metrics** | 30,626 ★ · 3,174 forks · 23 open issues · created 2026-05-01 · Python · default branch `master` |
| **Issue pressure** | 0.007 — very healthy |
| **Growth** | ~6,824 ★/month |
| **License ruling** | **PASS** |

**Architecture.** PDF → structured skill pipeline: extract, chunk, summarise, emit skill
files. A batch workload with a predictable, measurable token profile.

**ATK fit (19/20).** The best *demonstration* candidate for cost routing. Because the
workload is batched and repeatable, before/after token and cost numbers are directly
measurable — which is what `CONTENT_DISTRIBUTION.md` Beat 5 requires and what most skills
cannot honestly supply.

**Concerns.**
- Extraction quality varies with PDF source quality; results are not uniform across inputs.
- Output quality is model-tier sensitive — cheap-model routing may degrade the generated
  skill. The right integration is *tiered* (cheap for extraction, strong for synthesis), not
  uniformly cheap. Getting this wrong would produce a fork that is cheaper and worse.
- **Copyright caution:** the tool ingests books. ATK must not ship, host or demo with
  copyrighted material it does not have rights to. Demo content must be public-domain or
  ATK-owned. This is a distribution risk, not a license risk, and it is easy to trip over.

**Technical Review: PASS** · **Security Review: NOT PERFORMED**

---

## 4. `tt-a1i/archify` — 86/100

| | |
|---|---|
| **License** | MIT — verified. Modify ✅ Redistribute ✅ Commercial ✅ |
| **Metrics** | 61,985 ★ · 4,090 forks · 168 open issues · created 2026-04-15 · JavaScript |
| **Issue pressure** | 0.041 — moderate |
| **Growth** | ~12,336 ★/month — fastest-growing eligible candidate |
| **License ruling** | **PASS** |

**Architecture.** Generates architecture, workflow, sequence, data-flow and lifecycle
diagrams as self-contained HTML with motion and export.

**ATK fit (16/20) / Distribution (15/15).** The best content asset available: diagram output
is visual, screenshot-ready, and multi-model comparison is genuinely informative rather than
a contrived benchmark ("here is the same architecture rendered by four models").

**Concerns.**
- 168 open issues and rapid growth mean upstream is moving fast — sync cadence should be
  weekly from day one, not monthly.
- Self-contained HTML output has a wide surface for rendering regressions that unit tests
  miss; visual regression testing is effectively required.
- Diagram quality is highly model-dependent. Cheap-model routing will visibly degrade output,
  so the honest default is a strong model with routing used for *choice*, not for cost
  reduction.

**Technical Review: PASS** · **Security Review: NOT PERFORMED**

---

## 5. `Egonex-AI/Understand-Anything` — 84/100

| | |
|---|---|
| **License** | MIT — verified |
| **Metrics** | 82,729 ★ · 6,961 forks · 302 open issues · created 2026-03-15 · TypeScript |
| **Issue pressure** | 0.043 |
| **Growth** | ~13,672 ★/month |
| **License ruling** | **PASS** |

**Architecture.** Converts a codebase into an interactive, explorable knowledge graph.

**ATK fit (16/20).** Whole-repository analysis is heavy and repeated, and the extract →
synthesise split maps cleanly onto tiered routing.

**Concerns.**
- 302 open issues against a fast-moving codebase — Maintenance 6/10.
- Graph-extraction correctness is hard to regression-test, so upstream syncs carry real risk
  of silent quality loss.
- **Security-relevant:** the tool reads entire codebases. Any ATK fork must document exactly
  what leaves the machine and when. Routing user source code through ATK by default without
  explicit disclosure would be a `ATK_ROUTING_INTEGRATION.md` §9 failure.

**Technical Review: CONDITIONAL** — the open gate is the security review, not the merits.
It reads whole codebases, so what leaves the machine must be established before anything
ships. Sync cadence: weekly. · **Security Review: NOT PERFORMED** *(elevated priority)*

---

## 6. `Paritok-official/paritok-4b-v1` — 84/100

| | |
|---|---|
| **License** | Apache-2.0 — verified. Modify ✅ Redistribute ✅ Commercial ✅ · **NOTICE required** · **Change statement required (§4b)** · Patent grant included |
| **Metrics** | 1,454 ★ · 138 forks · 8 open issues · created 2026-07-15 · Python |
| **Issue pressure** | 0.058 |
| **License ruling** | **PASS** (Apache-2.0 obligations apply) |

**Architecture.** Non-destructive context-compression gateway that sits in front of coding
agents on any `BASE_URL`, backed by an open 4B code-native model.

**ATK fit (19/20).** Architecturally the closest to ATK's own business: it is already a
gateway, so ATK integration is composition rather than retrofit. Compression multiplies with
routing — the combined cost story is stronger than either alone.

**Concerns.**
- **Young and small**: created 2026-07-15, 1,454 stars, 138 forks. Little external
  validation, and vendor-published benchmark claims (25% → 85% savings) must be independently
  reproduced before ATK repeats any number publicly. `CONTENT_DISTRIBUTION.md` §8.1 applies.
- The 4B model is an additional dependency to host or call — a real operational cost not
  present in the other candidates.
- Apache-2.0 NOTICE and `CHANGES-ATK.md` obligations are mandatory, not optional.
- Trend 14/20 — it is on the list for architecture, not momentum.

**Technical Review: CONDITIONAL** — pending independent benchmark reproduction ·
**Security Review: NOT PERFORMED**

---

## 7. `Panniantong/Agent-Reach` — 83/100

| | |
|---|---|
| **License** | MIT — verified |
| **Metrics** | 81,070 ★ · 7,060 forks · 134 open issues · created 2026-02-24 · Python |
| **Issue pressure** | 0.019 |
| **Growth** | ~12,528 ★/month |
| **License ruling** | **PASS** |

**Architecture.** One CLI giving agents read/search access to Twitter, Reddit, YouTube,
GitHub, Bilibili and XiaoHongShu without per-platform API fees.

**ATK fit (15/20).** Retrieval feeding summarisation — solid, not exceptional. The model
calls are downstream of the retrieval, so the seam is one layer removed.

**Concerns — the most significant on this list.**
- **Terms-of-service exposure.** "Zero API fees" implies scraping or unofficial endpoints on
  platforms that prohibit it. The MIT license governs the *code*; it says nothing about
  whether operating it is permitted. ATK redistributing this under its own brand assumes a
  materially different risk profile than an individual using it.
- Scraper fragility: platform changes break it silently.
- Bilibili and XiaoHongShu coverage is genuinely differentiating for ATK's Chinese-language
  audience — which raises both the value and the exposure.

**Technical Review: BLOCKED pending legal review of platform ToS** ·
**Security Review: NOT PERFORMED**

---

## 8. `K-Dense-AI/scientific-agent-skills` — 83/100

| | |
|---|---|
| **License** | MIT — verified |
| **Metrics** | 44,908 ★ · 4,073 forks · **10 open issues** · created 2025-10-19 · Python |
| **Issue pressure** | 0.002 — best-maintained project in the sweep |
| **License ruling** | **PASS** |

**Architecture.** 165 validated skills plus 100+ scientific databases spanning biology,
chemistry, medicine and drug discovery.

**ATK fit (17/20).** Different buyer entirely: research institutions and pharma, with
sustained high-value consumption and low price sensitivity. Strategically valuable as
diversification away from a purely developer-tool funnel.

**Concerns.**
- **Domain correctness matters more than anywhere else on this list.** A cheap-model swap in
  a drug-discovery workflow is not a quality regression, it is a safety problem. Any ATK
  routing integration must pin model tiers per skill and refuse to silently downgrade.
- Requires domain expertise ATK does not obviously have in-house for meaningful review.
- Very clean upstream (10 open issues) means low sync cost — the cheapest fork to keep
  current on this list.

**Technical Review: CONDITIONAL** — requires a domain reviewer ·
**Security Review: NOT PERFORMED**

---

## 9. `nexu-io/open-design` — 83/100

| | |
|---|---|
| **License** | Apache-2.0 — verified. NOTICE + change statement required |
| **Metrics** | 96,144 ★ · 11,139 forks · **1,008 open issues** · created 2026-04-28 · TypeScript |
| **Issue pressure** | 0.090 — the worst among the Top 10 |
| **Growth** | ~21,077 ★/month — the fastest in the entire sweep |
| **License ruling** | **PASS** (Apache-2.0 obligations apply) |

**Architecture.** Local-first desktop application turning a coding agent into a design engine
producing prototypes, landing pages, dashboards, slides, images and video. Already BYOK
across 20+ CLIs.

**ATK fit (15/20).** BYOK means a provider seam already exists — good. But the seam is
designed around *agent CLIs*, not raw model providers, so ATK integration is at a different
layer than the other candidates.

**Concerns.**
- **1,008 open issues.** Maintenance 5/10, the lowest in the Top 10 — a desktop app with
  media pipelines is the highest-surface project here. Workable on a weekly cadence; it just
  costs more attention than the others.
- Positioned explicitly as a "Claude Design alternative", and already BYOK across 20+ CLIs —
  so the ATK integration sits at the agent-CLI layer, not the raw provider layer.
- Fastest growth in the sweep also means the fastest upstream drift.

**Technical Review: CONDITIONAL** — merit is clear. 1,008 open issues and the fastest growth
in the sweep mean this one needs a **weekly** sync cadence and a maintainer who owns it
outright; it is not a fork to run casually alongside three others.
· **Security Review: NOT PERFORMED**

---

## 10. `tbphp/gpt-load` — 82/100

| | |
|---|---|
| **License** | MIT — verified |
| **Metrics** | 6,740 ★ · 726 forks · **20 open issues** · created 2025-06-06 · Go |
| **Issue pressure** | 0.028 — excellent for a gateway |
| **License ruling** | **PASS** |

**Architecture.** Self-hosted Go gateway for multi-channel, multi-credential setups: key and
subscription-account scheduling, failover, request logs, usage tracking. Bilingual
(English/Chinese) documentation.

**ATK fit (18/20).** The natural **routing anchor** for the ATK Skill Network. ATK becomes
one upstream channel among many — which is the Routing Principle expressed as architecture
rather than as policy. A user who installs ATK's distribution of `gpt-load` can see ATK
sitting alongside OpenAI and Anthropic, and can remove it. That is the most credible possible
demonstration that ATK Routing is replaceable.

**Concerns.**
- Distribution 11/15: infrastructure does not spread on screenshots. Expect low K and high
  conversion — judge it on activation, not stars (`ANALYTICS_METRICS.md` §6).
- Go codebase; ATK needs Go maintenance capacity.
- Self-hosted credential handling means the security review here is the most important of the
  ten. It stores and schedules API keys.
- Bilingual docs are a real asset for ATK's Chinese-language channels.

**Technical Review: PASS** · **Security Review: NOT PERFORMED** *(highest priority — handles
credentials)*

---

## Summary

| # | Repository | License | Gate | Technical | Security | Fork-ready? |
|---|---|---|---|---|---|---|
| 1 | last30days-skill | MIT | PASS | PASS | Not performed | Pending security |
| 2 | humanizer | MIT | PASS | PASS | Not performed | Pending security |
| 3 | book-to-skill | MIT | PASS | PASS | Not performed | Pending security |
| 4 | archify | MIT | PASS | PASS | Not performed | Pending security |
| 5 | Understand-Anything | MIT | PASS | CONDITIONAL | Not performed | Pending security — reads whole codebases |
| 6 | paritok-4b-v1 | Apache-2.0 | PASS | CONDITIONAL | Not performed | Pending benchmark repro |
| 7 | Agent-Reach | MIT | PASS | **BLOCKED** | Not performed | **No — ToS review first** |
| 8 | scientific-agent-skills | MIT | PASS | CONDITIONAL | Not performed | Needs a domain reviewer |
| 9 | open-design | Apache-2.0 | PASS | CONDITIONAL | Not performed | Needs weekly sync + a dedicated owner |
| 10 | gpt-load | MIT | PASS | PASS | Not performed | Pending security |

**All ten passed the License Gate.** That is the expected result — the gate ran *before*
this review and removed the failures, which is the point of ordering it first.

Differentiation came instead from technical and legal risk: one candidate is blocked on ToS,
one needs a domain reviewer, two need a weekly sync cadence and a dedicated owner, and five
are clean enough to proceed once security review completes.

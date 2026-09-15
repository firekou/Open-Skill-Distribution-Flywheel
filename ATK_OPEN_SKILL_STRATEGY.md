# ATK Open Skill Distribution Strategy

> AI Token King — Open Skill Distribution Flywheel
> Version 1.0 · Owner: ATK Distribution · Last updated: 2026-09-14

---

## 1. Strategic Intent

AI Token King does not attempt to control external open-source projects, and does not
depend on other projects accepting ATK pull requests.

The core strategy is:

> **Find AI Skills, Agents, MCP servers, Routing layers, Workflows and developer tools that
> the market has already validated. Where the license allows it, fork, maintain, improve and
> integrate them — then redistribute through GitHub and social assets ATK controls.**

The resulting loop:

```
Discover → Fork → Improve → Integrate → Publish → Distribute → Use → Feedback → Update
```

ATK's competitive advantage is not inventing every tool. It is:

| Advantage | What it means operationally |
|---|---|
| Find good tools | A repeatable Discovery + Scoring pipeline, not ad-hoc bookmarking |
| Maintain good tools | Upstream sync discipline so forks do not rot |
| Lower the barrier | One-command install, Docker, `.env.example`, working examples |
| Provide Routing | A transparent, replaceable provider layer with ATK as the default |
| Keep updating | Weekly operating loop with measurable output |
| Own Distribution | GitHub + social as an acquisition layer, not a billboard |

---

## 2. Core Assumptions

ATK holds two assets that amplify each other.

### Asset A — GitHub technical assets

ATK maintains an **Open Skill Group** spanning:

AI Skills · Agent Skills · MCP Servers · MCP Clients · Agent-to-Agent · Routing ·
Model Gateway · Media Skills · Developer Skills · Enterprise Skills · Automation Skills ·
Agent Infrastructure

### Asset B — Social distribution

Threads, X, LinkedIn, YouTube and technical articles. **Established:** 3–5 accounts already
produce **300,000–500,000 impressions per month**. This is an operating channel ATK runs
today, not a projection.

That impression volume should *not* be pointed directly at ATK product pages. The
higher-converting path is developer-first:

```
Social Content
      ↓
Useful Skill / GitHub Repository
      ↓
README / Demo / Tutorial
      ↓
Developer actually uses the Skill
      ↓
Developer encounters ATK Routing
      ↓
ATK API / MCP / Token consumption
```

> **What this means for Phase 1:** the top of the funnel is already built and running. The
> unknown is not whether ATK can generate reach — it can — but what the reach converts at
> once it points into GitHub repositories instead of product pages. That is what
> `ANALYTICS_METRICS.md` instruments.

---

## 3. The Flywheel

### Stage 1 — Discover

Continuously scan for fast-growing GitHub repositories, MCP servers, Skills, Agent
frameworks, AI SDKs, Workflows, Prompt tools, Automation and Routing projects.

Priority signals:

1. Star growth rate (not absolute stars)
2. Fork growth rate
3. Recent, sustained commit activity
4. Active community discussion
5. Solves a real working problem
6. Can combine with ATK API / MCP / Routing
7. License permits fork, modification and redistribution

Signals 1–6 make a repository *interesting*. Signal 7 makes it *usable*. A repository that
fails signal 7 never enters the pipeline regardless of how well it scores elsewhere.

### Stage 2 → 8

| Stage | Gate | Artifact |
|---|---|---|
| Discover | Growth signal present | `registry/skill_registry.json` entry |
| Score | `skill_score` ≥ 80 (Priority A) | `SKILL_SCORING.md` result |
| License Gate | Redistribution + commercial use permitted | `LICENSE_REVIEW.md` record |
| Technical Review | Architecture, security, dependencies pass | Review note |
| Fork | Value-add plan committed in writing | `FORK_POLICY.md` checklist |
| Integrate | ATK Router adapter + fallback + token tracking | `ATK_ROUTING_INTEGRATION.md` |
| QA | Install / build / API / routing / security / regression | QA report |
| Distribute | 5–20 content assets produced | `CONTENT_DISTRIBUTION.md` |
| Measure | Funnel instrumented end to end | `ANALYTICS_METRICS.md` |

---

## 4. Anti-Goal: No Fork Graveyard

A large number of forks with no improvement has no value — it has negative value, because
it burns the developer trust the whole strategy depends on.

**Every ATK fork must ship at least one committed Value Add before it is published.**
See `FORK_POLICY.md` for the enforced checklist. The positioning is never:

> ~~"We copied this project."~~

It is:

> **"ATK maintains a production-ready distribution of this project, with multi-model
> routing and additional integrations."**

And that claim must be *true at publish time*, not aspirational.

---

## 5. Routing Integration Principle

ATK Routing is the commercial layer of this strategy. It must never be smuggled in by
locking a provider.

```
Skill
  ↓
Provider Interface      ← stable, documented seam
  ↓
Router
  ↓
ATK Router (default)    ← replaceable
  ↓
OpenAI / Anthropic / Gemini / DeepSeek / Qwen / others
```

Four non-negotiable properties: **Transparent · Replaceable · Documented · Optional.**

ATK may be the Quick Start default. It may not be the only path. Full rules and the
reference adapter contract: `ATK_ROUTING_INTEGRATION.md`.

---

## 6. Repository Group Architecture

Not one giant repository — an **ATK Skill Network**:

```
aitokenking
├── awesome-ai-skills      Discovery. Curated external projects worth using.
├── atk-agent-skills       ATK-reviewed, forked, improved Agent Skills
├── atk-mcp-skills         ATK-maintained MCP servers/clients
├── atk-media-skills       Image / audio / video skills
├── atk-developer-skills   Dev-workflow skills
├── atk-enterprise-skills  Compliance, reporting, internal ops
├── atk-routing            Provider abstraction, model/token/cost routing, fallback
├── atk-agent-stack        Reference end-to-end agent stack
└── atk-examples           Runnable demos
```

`awesome-ai-skills` is deliberately *not* a fork target — it is the honest curation surface
that earns the right to distribute. It links to upstream projects, including ones ATK never
forks.

---

## 7. Phasing

| Phase | Window | Target |
|---|---|---|
| Phase 1 | 30 days | Registry, scoring, license gate, fork SOP, upstream sync, router adapter, README + content templates, analytics. 10 Priority-A candidates identified. **3–5 production-ready forks shipped.** |
| Phase 2 | 60 days | 20–30 ATK-maintained projects. Category repos live. GitHub topic cluster forming. |
| Phase 3 | 90 days | Measure traffic → clone → activation → token consumption per skill. Retire the bottom performers. Concentrate on the top 20%. Publish the **ATK Recommended Stack**. |

Phase 1 explicitly does **not** pursue scale. Ten genuinely good skills × ten content
assets each = 100 content assets. That is enough surface to learn which skills actually
convert before spending maintenance budget on thirty more.

---

## 8. North Star

Not followers. Not stars.

> **MAAPP — Monthly Active ATK-Powered Projects**
>
> The number of distinct projects that, in a given month, actually executed work through
> ATK Routing / API / MCP.

Stars measure attention. MAAPP measures dependency. Only the second one compounds.

---

## 9. Agent Architecture

| # | Agent | Responsibility | Primary artifact |
|---|---|---|---|
| 01 | Trend Scout | Scan GitHub, Hugging Face, YouTube, Reddit, X, MCP registries | Candidate rows |
| 02 | License Agent | License, copyright, NOTICE, commercial use, modification, redistribution | `LICENSE_REVIEW.md` record |
| 03 | Technical Reviewer | Architecture, code quality, security, maintenance, dependencies, ATK compatibility | Review note |
| 04 | Fork Agent | Fork, branch, ATK modification, documentation | Fork branch |
| 05 | Integration Agent | ATK API / MCP / Router, fallback, token tracking | Adapter PR |
| 06 | QA Agent | Install, build, API, routing, security, regression | QA report |
| 07 | Upstream Agent | Upstream commits, releases, breaking changes, security fixes | Sync record |
| 08 | Content Agent | Threads, X, LinkedIn, blog, tutorial, video script | Content assets |
| 09 | Analytics Agent | Traffic, stars, forks, clones, signup, activation, token usage | Weekly funnel report |

**Hard rule:** Agents 04 and 05 cannot run until Agents 02 and 03 have both returned a
pass for that repository. This is enforced by the registry `decision` field, not by
convention.

---

## 10. Weekly Operating Loop

| Day | Activity | Output |
|---|---|---|
| Monday | Trend Scout | 20–50 candidates |
| Tuesday | Score | Top 5 selected |
| Wednesday | License + Technical Review | Pass/fail per candidate |
| Thursday | Fork + Integration | 1–3 forks in progress |
| Friday | QA + Release | Tagged release |
| Weekend | Content distribution | 5–20 assets |
| Following week | Analysis | Traffic → Usage → Conversion |

---

## 11. The Real Moat

What this strategy builds is not a pile of forks. It is the **ATK Distribution Network**:

```
Open Source → Discovery → ATK Curation → Fork + Improvement → ATK Routing
   → GitHub Distribution → Social Distribution → Developer Adoption
   → Usage Data → Better Curation → More Distribution
```

> Useful Tools create Traffic.
> Traffic creates Developers.
> Developers create Usage.
> Usage creates Token Demand.
> Token Demand strengthens ATK Routing.

ATK does not need to control the AI open-source ecosystem. It needs to become the layer
developers routinely pass through when they find a good AI Skill, Agent, MCP or Routing
tool.

---

## 12. Document Map

| Document | Purpose |
|---|---|
| `ATK_OPEN_SKILL_STRATEGY.md` | This document — strategy of record |
| `SKILL_SCORING.md` | The 100-point `skill_score` rubric |
| `LICENSE_REVIEW.md` | License Gate procedure and per-license rulings |
| `FORK_POLICY.md` | When to fork, required value-add, branch model |
| `UPSTREAM_SYNC.md` | Keeping forks alive against upstream drift |
| `ATK_ROUTING_INTEGRATION.md` | Provider interface contract and adapter spec |
| `CONTENT_DISTRIBUTION.md` | 1 repo → 5–20 content assets |
| `ANALYTICS_METRICS.md` | Funnel, metrics, MAAPP definition |
| `registry/skill_registry.json` | Machine-readable candidate registry |
| `reports/` | TASK 10–13 outputs: candidates, Top 10, deep review, fork recommendations |
| `templates/` | README, content and `.env` templates |
| `tools/score.py` | Reproducible scoring over the registry |

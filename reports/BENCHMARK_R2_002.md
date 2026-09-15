# Benchmark Run R2-002 — Mining the Four Unmined Source Classes

> Run ID `R2-002` · Snapshot **2026-09-15** · Scoring: `TREND_SCORING.md`
> Fixes the weakest metric of R2-001: source diversity. **No repository was forked.**

---

## What changed

R2-001 mined GitHub only — four of the six `DISCOVERY_ENGINE.md` source classes went untouched. This run adds **24 non-repository materials** across all four.

| Source class | R2-001 | R2-002 |
|---|---|---|
| 1. Primary code (GitHub) | ✅ 164 | ✅ 164 |
| 2. Protocol / registry | ✅ via GitHub | ✅ via GitHub |
| 3. Model/platform engineering | ❌ none | ✅ Anthropic, Cloudflare, Vercel, OpenAI, DeepSeek |
| 4. Research / model hubs | ❌ none | ✅ 6 arXiv papers, Hugging Face router + LCLM |
| 5. Community signal | ❌ none | ✅ Hacker News, developer community, YouTube |
| 6. Curated discovery | ⚠️ partial | ✅ 3 curated indexes incl. an automated HF feed |

**Registry total: 188 materials** (164 repositories + 24 non-repository). 52 Priority A.

| Source type | Count |
|---|--:|
| code_repository | 164 |
| paper | 6 |
| engineering_blog | 4 |
| engineering_docs | 4 |
| curated_index | 3 |
| news | 3 |
| community_signal | 2 |
| model_hub | 1 |
| video_channel | 1 |

### Verification status — read this before quoting anything

Of the 24 new materials, **6 were retrieved from the primary source** and **18 come from search-engine summaries only**.

Every item carries a `_verification` field. `"search"` means the underlying claim is **not independently confirmed**. Several of the most quotable numbers in this run are in that category — the ~100× price gap, the 40–85% routing savings, the 2.37M YouTube view count. They are useful as hypotheses to test. **They are not facts ATK may publish.**

---

## The finding that matters most

### The routing layer is being commoditised by platform companies, not by open source

R2-001 flagged small free-aggregation projects as ATK's price competition. That read was **too small**. The real pressure is this:

| Who | What they give away |
|---|---|
| **Cloudflare AI Gateway** | Managed AI routing and observability proxy, **free on every Cloudflare plan** — analytics, caching and rate limiting at no charge. 24 native providers. A universal REST endpoint added May 2026 speaks both OpenAI and Anthropic request formats. |
| **Cloudflare Agents Week (Aug 2026)** | 20+ launches in two weeks: agent wallet and verifiable identity, Identity-Aware AI Gateway, persistent Agent Memory, DeepSeek models with ~1M-token context on Workers AI. |
| **Cloudflare + OpenAI Agent Cloud (Apr 2026)** | Enterprise agent runtime with GPT-5.4 and Codex in a unified model catalogue. |
| **Vercel AI Gateway** | Hundreds of models across ~45 providers, one key, **BYOK with no markup**. |

A dozen small OSS aggregators are a nuisance. Two platform companies with default distribution into millions of developer projects, giving the same layer away as a feature of something else, is a different problem entirely. **ATK cannot win on price or on provider count.** Both are already zero-cost commodities from vendors with better reach.

### Where the gap actually is

The same sources name what these gateways do *not* do. Vercel's is described as having **no guardrails and no semantic cache**. Cloudflare's is a proxy with analytics, not a cost-attribution or audit system.

And the research independently points at the same opening. [*Model Routing as a Trust Problem: Route Receipts for Adaptive AI Systems*](https://arxiv.org/pdf/2605.01710) (arXiv 2605.01710, May 2026) frames routing as a **trust** problem and proposes verifiable route receipts — a cryptographic record of which model actually served a request and why.

That is the same conclusion R2-001 reached from repository data, now supported from two independent directions. **Measurement, attribution and auditability is the position price competition cannot erase** — because a free gateway has no incentive to prove what it did with your request, and a paid one does.

The projects sitting in that gap are all still small: `claude-tap` (3.2k★), `api-relay-audit` (836★), `RelayPlane/proxy` (202★), `tokentab` (1.1k★). That is either an opportunity or a warning that the market does not value it yet. R2-003 should find out which.

---

## Best primary-source technique found

[**Code execution with MCP: building more efficient AI agents**](https://www.anthropic.com/engineering/code-execution-with-mcp) — Anthropic engineering, Nov 2025. Retrieved from the primary source.

The argument: agents connected to many MCP servers pay twice. Every tool definition is loaded into context upfront, and every intermediate tool result passes through the model. Anthropic's example puts a 2-hour meeting transcript at ~50,000 extra tokens from intermediate results alone. Having the agent **write code that calls tools**, instead of calling each tool directly, removes both costs.

This is the most actionable thing in the run: it is a technique, not a product, so ATK can test it, measure it, teach it and build routing around it without any licence question at all. Anthropic's context-engineering cookbook (Mar 2026) is runnable and covers memory, compaction and tool clearing — a ready-made experiment.

---

## 1. What should ATK talk about?

Refreshed across all 188 materials. Non-repository items now rank here too — a technique or a market fact is often better content than a tool.

| Material | Type | _★/mo or date | Score | Angle |
|---|---|--:|---|---|
| [`calesthio/OpenMontage`](https://github.com/calesthio/OpenMontage) | code repository | 10568 | **88** | Agentic video production: 12 pipelines, 100+ tools, 700+ skill and… |
| [`tt-a1i/archify`](https://github.com/tt-a1i/archify) | code repository | 12332 | **88** | Generates architecture, workflow, sequence, data-flow and lifecycle… |
| [`nexu-io/open-design`](https://github.com/nexu-io/open-design) | code repository | 20904 | **86** | Local-first design surface turning a coding agent into a… |
| [`koala73/worldmonitor`](https://github.com/koala73/worldmonitor) | code repository | 10516 | **81** | Real-time global intelligence dashboard |
| [Show HN: Headroom - reversible context compression (~60%…](https://news.ycombinator.com/item?id=46628278) | community signal | 2026 | **84** | Independent HN validation of the headroom project already in the… |
| [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) | code repository | 7951 | **83** | 38 editorial diagram types rendered as self-contained HTML + SVG |
| [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) | code repository | 3877 | **79** | Generates presentation slides on the web using a coding agent's… |
| [YouTube: Claude Code tutorial demand is enormous](https://developereducators.com/best/claude-code/) | video channel | 2026 | **67** | The most-watched Claude Code tutorial reportedly sits near 2.37M… |
| [`headroomlabs-ai/headroom`](https://github.com/headroomlabs-ai/headroom) | code repository | 8764 | **91** | Compresses tool output, logs, files and RAG chunks before they reach… |
| [`mvanhorn/last30days-skill`](https://github.com/mvanhorn/last30days-skill) | code repository | 8034 | **91** | Researches a topic across Reddit, X, YouTube, HN, Polymarket and the… |
| [`rtk-ai/rtk`](https://github.com/rtk-ai/rtk) | code repository | 10380 | **87** | CLI proxy that cuts up to 90% of the BASH OUTPUT an agent reads |
| [DeepSeek open-sources its agent harness under MIT](https://thenewstack.io/deepseek-harness-open-source-plugins/) | news | 2026-08-13 | **87** | Model adapter, tool registry and agent loop are all swappable… |
| [`Egonex-AI/Understand-Anything`](https://github.com/Egonex-AI/Understand-Anything) | code repository | 13686 | **86** | Turns a codebase into an interactive, queryable knowledge graph |
| [`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach) | code repository | 12157 | **86** | Gives an agent read/search access to Twitter, Reddit, YouTube… |
| [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | code repository | 13438 | **85** | Design intelligence for building professional UI/UX across platforms |

## 2. What should ATK test?

Cheap to stand up, and produces a number ATK can publish once measured.

| Material | Category | _Exp | _ATK | Score | What it measures |
|---|---|--:|--:|---|---|
| [`Paritok-official/paritok-4b-v1`](https://github.com/Paritok-official/paritok-4b-v1) | token-optimization | 10 | 19 | **81** | Non-destructive compression gateway backed by an open 4B… |
| [`NadirRouter/NadirClaw`](https://github.com/NadirRouter/NadirClaw) | routing | 10 | 19 | **76** | Prompt-complexity router: cheap/local models for simple… |
| [`yvgude/lean-ctx`](https://github.com/yvgude/lean-ctx) | token-optimization | 10 | 18 | **79** | Rust context-intelligence layer for coding agents |
| [`tbphp/gpt-load`](https://github.com/tbphp/gpt-load) | routing | 10 | 18 | **79** | Self-hosted AI gateway for multi-channel, multi-credential… |
| [`juyterman1000/entroly`](https://github.com/juyterman1000/entroly) | token-optimization | 10 | 18 | **75** | Reversible, byte-exact recoverable context compression with an… |
| [`kittors/CliRelay`](https://github.com/kittors/CliRelay) | routing | 10 | 18 | **75** | Self-hosted gateway for coding CLIs with multi-tenant console… |
| [`caidaoli/ccLoad`](https://github.com/caidaoli/ccLoad) | routing | 10 | 18 | **70** | Go gateway with smart routing, auto failover, exponential… |
| [`crwdla/tokentab`](https://github.com/crwdla/tokentab) | token-optimization | 10 | 17 | **80** | Reads Claude Code/Codex/Gemini session logs and computes cost… |
| [`jgravelle/jcodemunch-mcp`](https://github.com/jgravelle/jcodemunch-mcp) | token-optimization | 10 | 16 | **78** | Symbol-level GitHub code retrieval over tree-sitter AST; claims… |
| [`alexgreensh/token-optimizer`](https://github.com/alexgreensh/token-optimizer) | token-optimization | 10 | 16 | **77** | Finds 'ghost tokens', survives compaction, tracks context… |
| [`Tura-AI/tura`](https://github.com/Tura-AI/tura) | token-optimization | 10 | 16 | **71** | Rust agent builder targeting 80% less token use with better… |
| [`ojuschugh1/sqz`](https://github.com/ojuschugh1/sqz) | token-optimization | 10 | 16 | **70** | Rust context compressor for LLM cost reduction |

## 3. What is suitable for ATK integration?

Companion adapter or deep integration — not a fork. Licence-gated, so licence is shown.

| Material | _ATK fit | Licence | Score | Shape |
|---|--:|---|---|---|
| [`ENTERPILOT/GoModel`](https://github.com/ENTERPILOT/GoModel) | 20 | MIT | **74** | Go AI gateway with unified OpenAI- and Anthropic-compatible… |
| [`headroomlabs-ai/headroom`](https://github.com/headroomlabs-ai/headroom) | 19 | Apache-2.0 | **91** | Compresses tool output, logs, files and RAG chunks before they… |
| [`mvanhorn/last30days-skill`](https://github.com/mvanhorn/last30days-skill) | 19 | MIT | **91** | Researches a topic across Reddit, X, YouTube, HN, Polymarket… |
| [`rtk-ai/rtk`](https://github.com/rtk-ai/rtk) | 19 | Apache-2.0 | **87** | CLI proxy that cuts up to 90% of the BASH OUTPUT an agent reads |
| [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) | 19 | MIT | **87** | Turns a technical book PDF into a usable Claude Code skill |
| [`Paritok-official/paritok-4b-v1`](https://github.com/Paritok-official/paritok-4b-v1) | 19 | Apache-2.0 | **81** | Non-destructive compression gateway backed by an open 4B… |
| [`RelayPlane/proxy`](https://github.com/RelayPlane/proxy) | 19 | MIT | **70** | Local-first proxy that meters what every agent run costs and… |
| [`blader/humanizer`](https://github.com/blader/humanizer) | 18 | MIT | **87** | Removes tells of AI-generated writing from text |
| [`yvgude/lean-ctx`](https://github.com/yvgude/lean-ctx) | 18 | Apache-2.0 | **79** | Rust context-intelligence layer for coding agents |
| [`tbphp/gpt-load`](https://github.com/tbphp/gpt-load) | 18 | MIT | **79** | Self-hosted AI gateway for multi-channel, multi-credential… |
| [`maximhq/bifrost`](https://github.com/maximhq/bifrost) | 18 | Apache-2.0 | **77** | High-performance Go AI gateway with adaptive load balancing and… |
| [`juyterman1000/entroly`](https://github.com/juyterman1000/entroly) | 18 | Apache-2.0 | **75** | Reversible, byte-exact recoverable context compression with an… |

## 4. What is suitable for fork / redistribution?

The only list where the full `LICENSE_REVIEW.md` + `FORK_POLICY.md` gate applies. Verified permissive licences only. **Nothing was forked.**

| Material | Licence | _ATK fit | Score | Note |
|---|---|--:|---|---|
| [`headroomlabs-ai/headroom`](https://github.com/headroomlabs-ai/headroom) | Apache-2.0 | 19 | **91** | Compresses tool output, logs, files and RAG chunks before… |
| [`mvanhorn/last30days-skill`](https://github.com/mvanhorn/last30days-skill) | MIT | 19 | **91** | Researches a topic across Reddit, X, YouTube, HN… |
| [`rtk-ai/rtk`](https://github.com/rtk-ai/rtk) | Apache-2.0 | 19 | **87** | CLI proxy that cuts up to 90% of the BASH OUTPUT an agent… |
| [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) | MIT | 19 | **87** | Turns a technical book PDF into a usable Claude Code skill |
| [`Paritok-official/paritok-4b-v1`](https://github.com/Paritok-official/paritok-4b-v1) | Apache-2.0 | 19 | **81** | Non-destructive compression gateway backed by an open 4B… |
| [`blader/humanizer`](https://github.com/blader/humanizer) | MIT | 18 | **87** | Removes tells of AI-generated writing from text |
| [`yvgude/lean-ctx`](https://github.com/yvgude/lean-ctx) | Apache-2.0 | 18 | **79** | Rust context-intelligence layer for coding agents |
| [`tbphp/gpt-load`](https://github.com/tbphp/gpt-load) | MIT | 18 | **79** | Self-hosted AI gateway for multi-channel… |
| [`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills) | MIT | 17 | **87** | 165 validated scientific skills plus 100+ scientific… |
| [`crwdla/tokentab`](https://github.com/crwdla/tokentab) | MIT | 17 | **80** | Reads Claude Code/Codex/Gemini session logs and computes… |
| [`Portkey-AI/gateway`](https://github.com/Portkey-AI/gateway) | MIT | 17 | **79** | AI gateway with guardrails routing to 1,600+ LLMs |
| [`tt-a1i/archify`](https://github.com/tt-a1i/archify) | MIT | 16 | **88** | Generates architecture, workflow, sequence, data-flow and… |

---

## New discovery inputs worth automating

| Index | Why |
|---|---|
| [`agents-radar`](https://github.com/duanyytop/agents-radar) | Bot-maintained repos that post Hugging Face trending models as dated GitHub issues. **Already an automated feed** — the Discovery Engine can consume it directly instead of scraping Hugging Face. |
| [`awesome-llm-token-optimization`](https://github.com/pleasedodisturb/awesome-llm-token-optimization) | Curated token-cost strategies, tools and papers. |
| [`Awesome-Routing-LLMs`](https://github.com/MilkThink-Lab/Awesome-Routing-LLMs) | Curated index of the routing research paradigm. |

Wiring these three into the Monday scout replaces most of the manual searching this run required.

## Honest limits

- **18 of 24 new materials are search-summary only.** Their claims are unconfirmed. The cheapest fix is fetching the primary pages directly — `raw.githubusercontent.com` and normal HTTPS both work from this environment.
- **Still nothing executed.** No experiment from list 2 has been run, so every savings figure in this registry — vendor or community — remains unverified.
- **X and Reddit were reached only through secondary write-ups**, not their own surfaces. Same for YouTube: view counts come from an aggregator page, not from YouTube.
- **Pricing was the load-bearing assumption and has since been verified.** The ~100× gap quoted in this run was corrected on 2026-09-15 from primary vendor pricing pages: like-for-like it is **11.4×**. See `PRICING_SNAPSHOT_2026-09-15.md` and Evidence Ledger E007/E015.

## R2-003

1. ~~Confirm the price gap from provider pricing pages~~ — **done 2026-09-15, corrected to 11.4×**
2. Run the Anthropic context-engineering cookbook and record measured token deltas
3. Run `api-relay-audit` against ATK's own routing
4. Stand up Cloudflare AI Gateway and Vercel AI Gateway and document, concretely, what ATK does that they do not
5. Wire the three curated indexes into the weekly scout

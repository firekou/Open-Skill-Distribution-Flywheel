# Benchmark Run R2-001 — First Discovery Sweep

> Run ID `R2-001` · Snapshot **2026-09-15** · Scoring: `TREND_SCORING.md`
> Runbook: `DISCOVERY_PIPELINE.md` · Architecture: `ARCHITECTURE_R2.md`
> **No repository was forked during this run**, as the runbook requires.
>
> **Superseded for registry counts by [`BENCHMARK_R2_002.md`](./BENCHMARK_R2_002.md)**, which adds the four source classes this run left unmined. The findings below still stand; the totals describe R2-001 only.

---

## Phase 0 — Permission Preflight

Recorded before mining, per the runbook. A missing permission is a limit on *this executor*, never a negative finding about a candidate.

| Capability | Status | Effect on this run |
|---|---|---|
| GitHub repository search (MCP tool) | ✅ Available | Primary mining path |
| GitHub search REST API (direct) | ❌ Blocked by proxy | Had to route all search through the MCP tool |
| `raw.githubusercontent.com` file reads | ✅ Available | **Licence texts and READMEs readable for any public repo** |
| GitHub contents API for external repos | ❌ 403 | Cannot enumerate trees; single-file reads via raw only |
| Repository settings writes | ❌ Blocked by policy | Unrelated to discovery |
| Web search (WebSearch / Exa) | ✅ Available | Not needed this run — GitHub yielded enough breadth |

**Consequence:** every item here is sourced from primary code repositories. Hacker News, Reddit, X, YouTube and Hugging Face — source classes 3–5 in `DISCOVERY_ENGINE.md` — were **not mined in this run**. Source diversity is therefore the weakest metric of R2-001 and the first thing to fix in R2-002.

---

## Result

| | Target | Actual |
|---|---|---|
| Raw candidates | 120 | **164** |
| — agent-skill | 20 | 36 ✅ |
| — routing | 20 | 30 ✅ |
| — mcp | 20 | 27 ✅ |
| — a2a | 20 | 25 ✅ |
| — agent-framework | 20 | 25 ✅ |
| — token-optimization | 20 | 21 ✅ |
| Priority A (≥80) | — | 38 |
| Priority B (65–79) | — | 105 |
| Watch (50–64) | — | 20 |
| Licence unresolved | — | 79 (48%) |

> **Licence is a flag, not a gate.** Per `ARCHITECTURE_R2.md`, an unresolved licence constrains redistribution only. All 79 unresolved items remain valid research and content material.

### Scoring honesty

`technical_utility`, `atk_relevance` and `content_potential` were **assigned by review**. `momentum`, `experimentability` and `source_credibility` are **derived by fixed public rules** in `tools/build_materials.py` from snapshot metrics. The split is deliberate: hand-scoring 164 items on six axes would have produced numbers with more precision than judgement behind them. Every derived value is reproducible from the registry.

---

## 1. What should ATK talk about?

Ranked by content potential, then momentum. These are content assets first — several are not forkable and do not need to be.

| Material | Stars | ★/mo | Licence | Score | Content angle |
|---|--:|--:|---|--:|---|
| [`calesthio/OpenMontage`](https://github.com/calesthio/OpenMontage) | 59,020 | 10,568 | AGPL-3.0 | **88** | Agentic video production: 12 pipelines, 100+ tools, 700+ skill and knowledge files |
| [`tt-a1i/archify`](https://github.com/tt-a1i/archify) | 61,985 | 12,332 | MIT | **88** | Generates architecture, workflow, sequence, data-flow and lifecycle diagrams as self-contained  |
| [`nexu-io/open-design`](https://github.com/nexu-io/open-design) | 96,144 | 20,904 | Apache-2.0 | **86** | Local-first design surface turning a coding agent into a prototype/landing-page/slide/image/vid |
| [`koala73/worldmonitor`](https://github.com/koala73/worldmonitor) | 86,368 | 10,516 | unresolved | **81** | Real-time global intelligence dashboard |
| [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) | 39,705 | 7,951 | MIT | **83** | 38 editorial diagram types rendered as self-contained HTML + SVG |
| [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) | 29,294 | 3,877 | MIT | **79** | Generates presentation slides on the web using a coding agent's frontend skills |
| [`headroomlabs-ai/headroom`](https://github.com/headroomlabs-ai/headroom) | 72,266 | 8,764 | Apache-2.0 | **91** | Compresses tool output, logs, files and RAG chunks before they reach the model |
| [`mvanhorn/last30days-skill`](https://github.com/mvanhorn/last30days-skill) | 62,022 | 8,034 | MIT | **91** | Researches a topic across Reddit, X, YouTube, HN, Polymarket and the web, then synthesises a gr |
| [`rtk-ai/rtk`](https://github.com/rtk-ai/rtk) | 80,473 | 10,380 | Apache-2.0 | **87** | CLI proxy cutting LLM token use 60-90% on common dev commands |
| [`Egonex-AI/Understand-Anything`](https://github.com/Egonex-AI/Understand-Anything) | 82,729 | 13,686 | MIT | **86** | Turns a codebase into an interactive, queryable knowledge graph |
| [`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach) | 81,070 | 12,157 | MIT | **86** | Gives an agent read/search access to Twitter, Reddit, YouTube, GitHub, Bilibili and XiaoHongShu |
| [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 127,581 | 13,438 | MIT | **85** | Design intelligence for building professional UI/UX across platforms |
| [`Leonxlnx/taste-skill`](https://github.com/Leonxlnx/taste-skill) | 87,095 | 12,746 | MIT | **83** | Steers agent output away from generic, boring generations |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | 94,287 | 13,538 | MIT | **82** | Production-grade engineering skills for AI coding agents |
| [`blader/humanizer`](https://github.com/blader/humanizer) | 48,065 | 6,096 | MIT | **87** | Removes tells of AI-generated writing from text |
| [`HKUDS/nanobot`](https://github.com/HKUDS/nanobot) | 48,179 | 6,489 | unresolved | **82** | Ultra-light self-hosted personal agent framework with WebUI, tools, memory, MCP and multi-agent |
| [`coreyhaines31/marketingskills`](https://github.com/coreyhaines31/marketingskills) | 50,207 | 6,289 | MIT | **80** | Marketing skills for agents: CRO, copywriting, SEO, analytics and growth engineering |
| [`pascalorg/editor`](https://github.com/pascalorg/editor) | 23,938 | 2,182 | MIT | **78** | 3D architectural editor with CLI and MCP tools |
| [`bytedance/UI-TARS-desktop`](https://github.com/bytedance/UI-TARS-desktop) | 38,995 | 1,965 | unresolved | **81** | ByteDance multimodal agent stack for GUI and computer use |
| [`internet-court/internet-court-skill`](https://github.com/internet-court/internet-court-skill) | 5,722 | 1,914 | unresolved | **76** | Trust layer for agent-to-agent commerce: mandates, delegated permissions, x402 payments, escrow |

**The story this list is telling.** The single strongest content theme in the whole sweep is **token cost**. `rtk-ai/rtk` (80k stars, 60–90% token reduction) and `headroomlabs-ai/headroom` (72k stars) were both created in January 2026 and both crossed 70k stars inside eight months. Neither appeared in the R1 sweep at all, because R1 searched for things to fork rather than things to understand. That gap is the clearest argument for the R2 architecture.

## 2. What should ATK test?

Ranked by how cheaply it can be stood up, then by how much ATK learns from the result. Everything here produces a number ATK can publish.

| Material | Category | Exp /10 | ATK fit | Score | What the test would measure |
|---|---|--:|--:|--:|---|
| [`Paritok-official/paritok-4b-v1`](https://github.com/Paritok-official/paritok-4b-v1) | token-optimization | 10 | 19 | **81** | Non-destructive compression gateway backed by an open 4B code-native model |
| [`NadirRouter/NadirClaw`](https://github.com/NadirRouter/NadirClaw) | routing | 10 | 19 | **76** | Prompt-complexity router: cheap/local models for simple prompts, premium for c |
| [`tbphp/gpt-load`](https://github.com/tbphp/gpt-load) | routing | 10 | 18 | **79** | Self-hosted AI gateway for multi-channel, multi-credential setups with schedul |
| [`yvgude/lean-ctx`](https://github.com/yvgude/lean-ctx) | token-optimization | 10 | 18 | **79** | Rust context-intelligence layer for coding agents |
| [`juyterman1000/entroly`](https://github.com/juyterman1000/entroly) | token-optimization | 10 | 18 | **75** | Reversible, byte-exact recoverable context compression with an auditable recei |
| [`kittors/CliRelay`](https://github.com/kittors/CliRelay) | routing | 10 | 18 | **75** | Self-hosted gateway for coding CLIs with multi-tenant console, request logs an |
| [`caidaoli/ccLoad`](https://github.com/caidaoli/ccLoad) | routing | 10 | 18 | **70** | Go gateway with smart routing, auto failover, exponential cooldown and soft-er |
| [`crwdla/tokentab`](https://github.com/crwdla/tokentab) | token-optimization | 10 | 17 | **80** | Reads Claude Code/Codex/Gemini session logs and computes cost by model, projec |
| [`jgravelle/jcodemunch-mcp`](https://github.com/jgravelle/jcodemunch-mcp) | token-optimization | 10 | 16 | **78** | Symbol-level GitHub code retrieval over tree-sitter AST; claims 95%+ token cut |
| [`alexgreensh/token-optimizer`](https://github.com/alexgreensh/token-optimizer) | token-optimization | 10 | 16 | **77** | Finds 'ghost tokens', survives compaction, tracks context quality decay |
| [`Tura-AI/tura`](https://github.com/Tura-AI/tura) | token-optimization | 10 | 16 | **71** | Rust agent builder targeting 80% less token use with better results |
| [`edouard-claude/snip`](https://github.com/edouard-claude/snip) | token-optimization | 10 | 16 | **70** | Go CLI proxy, declarative YAML filters, positioned as an rtk alternative |
| [`ThinkWatchProject/ThinkWatch`](https://github.com/ThinkWatchProject/ThinkWatch) | routing | 10 | 16 | **70** | Enterprise AI bastion host for secure AI API and MCP access with RBAC, audit l |
| [`Nya-Foundation/NyaProxy`](https://github.com/Nya-Foundation/NyaProxy) | routing | 10 | 16 | **69** | Central manager for API access across OpenAI, Gemini and Anthropic with load b |
| [`ojuschugh1/sqz`](https://github.com/ojuschugh1/sqz) | token-optimization | 10 | 16 | **70** | Rust context compressor for LLM cost reduction |

**Run this one first, even though it is not top of the table.** [`toby-bridges/api-relay-audit`](https://github.com/toby-bridges/api-relay-audit) (836★, experimentability 9, ATK fit 19) sits just below the cut because fifteen items scored a perfect 10 on ease of setup. It is still the single highest-value experiment available, and the ranking simply does not capture why: it is a security auditor for LLM proxies — prompt injection, model substitution, tool-call rewriting, SSE anomalies, error leakage. **ATK operates an LLM proxy.**

Running it against ATK's own routing is a real security exercise, and publishing the result is the kind of trust signal a cost claim can never buy. Nothing else in this sweep doubles as self-audit and content. Treat the table as the cheap-and-useful list, and this as the one that matters most.

## 3. What is suitable for ATK integration?

Ranked by ATK relevance. Integration here means a **companion adapter or deep integration** — not a fork. Licence constrains this list, so it is shown.

| Material | ATK fit /20 | Licence | Score | Integration shape |
|---|--:|---|--:|---|
| [`ENTERPILOT/GoModel`](https://github.com/ENTERPILOT/GoModel) | 20 | MIT | **74** | Go AI gateway with unified OpenAI- and Anthropic-compatible API, routing, fail |
| [`headroomlabs-ai/headroom`](https://github.com/headroomlabs-ai/headroom) | 19 | Apache-2.0 | **91** | Compresses tool output, logs, files and RAG chunks before they reach the model |
| [`mvanhorn/last30days-skill`](https://github.com/mvanhorn/last30days-skill) | 19 | MIT | **91** | Researches a topic across Reddit, X, YouTube, HN, Polymarket and the web, then |
| [`rtk-ai/rtk`](https://github.com/rtk-ai/rtk) | 19 | Apache-2.0 | **87** | CLI proxy cutting LLM token use 60-90% on common dev commands |
| [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) | 19 | MIT | **87** | Turns a technical book PDF into a usable Claude Code skill |
| [`Paritok-official/paritok-4b-v1`](https://github.com/Paritok-official/paritok-4b-v1) | 19 | Apache-2.0 | **81** | Non-destructive compression gateway backed by an open 4B code-native model |
| [`RelayPlane/proxy`](https://github.com/RelayPlane/proxy) | 19 | MIT | **70** | Local-first proxy that meters what every agent run costs and kills runaways be |
| [`blader/humanizer`](https://github.com/blader/humanizer) | 18 | MIT | **87** | Removes tells of AI-generated writing from text |
| [`yvgude/lean-ctx`](https://github.com/yvgude/lean-ctx) | 18 | Apache-2.0 | **79** | Rust context-intelligence layer for coding agents |
| [`tbphp/gpt-load`](https://github.com/tbphp/gpt-load) | 18 | MIT | **79** | Self-hosted AI gateway for multi-channel, multi-credential setups with schedul |
| [`maximhq/bifrost`](https://github.com/maximhq/bifrost) | 18 | Apache-2.0 | **77** | High-performance Go AI gateway with adaptive load balancing and cluster mode |
| [`juyterman1000/entroly`](https://github.com/juyterman1000/entroly) | 18 | Apache-2.0 | **75** | Reversible, byte-exact recoverable context compression with an auditable recei |
| [`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills) | 17 | MIT | **87** | 165 validated scientific skills plus 100+ scientific databases for biology, ch |
| [`crwdla/tokentab`](https://github.com/crwdla/tokentab) | 17 | MIT | **80** | Reads Claude Code/Codex/Gemini session logs and computes cost by model, projec |
| [`Portkey-AI/gateway`](https://github.com/Portkey-AI/gateway) | 17 | MIT | **79** | AI gateway with guardrails routing to 1,600+ LLMs |

A second tier scores just as high on ATK relevance but has an **unresolved licence**, so it can be researched and tested but not yet adapted:

| Material | ATK fit /20 | Score | Why it matters |
|---|--:|--:|---|
| [`lidge-jun/opencodex`](https://github.com/lidge-jun/opencodex) | 18 | **85** | Universal provider proxy letting Codex CLI/App/SDK and Claude Code run on any  |
| [`liaohch3/claude-tap`](https://github.com/liaohch3/claude-tap) | 19 | **82** | Intercepts and inspects coding-agent API traffic across 9 agents in a local tr |
| [`wang2122/sprix-sage-router`](https://github.com/wang2122/sprix-sage-router) | 18 | **81** | State-aware SELF/COLLABORATE/HANDOFF routing for A2A agent networks |
| [`iflytek/skillhub`](https://github.com/iflytek/skillhub) | 18 | **80** | Self-hosted enterprise agent-skill registry with versioning, RBAC and audit lo |
| [`assafelovic/gpt-researcher`](https://github.com/assafelovic/gpt-researcher) | 18 | **80** | Autonomous deep-research agent across any LLM provider |
| [`toby-bridges/api-relay-audit`](https://github.com/toby-bridges/api-relay-audit) | 19 | **78** | Security audit for AI API relays and LLM proxies: prompt injection, model subs |
| [`esengine/DeepSeek-Reasonix`](https://github.com/esengine/DeepSeek-Reasonix) | 18 | **77** | DeepSeek-native terminal coding agent engineered around prefix-cache stability |
| [`NadirRouter/NadirClaw`](https://github.com/NadirRouter/NadirClaw) | 19 | **76** | Prompt-complexity router: cheap/local models for simple prompts, premium for c |

## 4. What is suitable for fork / redistribution?

The **only** list where the full `LICENSE_REVIEW.md` + `FORK_POLICY.md` gate applies. Everything here has a verified permissive licence. **Nothing was forked.**

| Material | Licence | ATK fit | Score | Note |
|---|---|--:|--:|---|
| [`headroomlabs-ai/headroom`](https://github.com/headroomlabs-ai/headroom) | Apache-2.0 | 19 | **91** | Compresses tool output, logs, files and RAG chunks before they reach the mo |
| [`mvanhorn/last30days-skill`](https://github.com/mvanhorn/last30days-skill) | MIT | 19 | **91** | Researches a topic across Reddit, X, YouTube, HN, Polymarket and the web, t |
| [`rtk-ai/rtk`](https://github.com/rtk-ai/rtk) | Apache-2.0 | 19 | **87** | CLI proxy cutting LLM token use 60-90% on common dev commands |
| [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) | MIT | 19 | **87** | Turns a technical book PDF into a usable Claude Code skill |
| [`Paritok-official/paritok-4b-v1`](https://github.com/Paritok-official/paritok-4b-v1) | Apache-2.0 | 19 | **81** | Non-destructive compression gateway backed by an open 4B code-native model |
| [`blader/humanizer`](https://github.com/blader/humanizer) | MIT | 18 | **87** | Removes tells of AI-generated writing from text |
| [`yvgude/lean-ctx`](https://github.com/yvgude/lean-ctx) | Apache-2.0 | 18 | **79** | Rust context-intelligence layer for coding agents |
| [`tbphp/gpt-load`](https://github.com/tbphp/gpt-load) | MIT | 18 | **79** | Self-hosted AI gateway for multi-channel, multi-credential setups with sche |
| [`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills) | MIT | 17 | **87** | 165 validated scientific skills plus 100+ scientific databases for biology, |
| [`crwdla/tokentab`](https://github.com/crwdla/tokentab) | MIT | 17 | **80** | Reads Claude Code/Codex/Gemini session logs and computes cost by model, pro |
| [`Portkey-AI/gateway`](https://github.com/Portkey-AI/gateway) | MIT | 17 | **79** | AI gateway with guardrails routing to 1,600+ LLMs |
| [`tt-a1i/archify`](https://github.com/tt-a1i/archify) | MIT | 16 | **88** | Generates architecture, workflow, sequence, data-flow and lifecycle diagram |
| [`Egonex-AI/Understand-Anything`](https://github.com/Egonex-AI/Understand-Anything) | MIT | 16 | **86** | Turns a codebase into an interactive, queryable knowledge graph |
| [`alibaba/open-code-review`](https://github.com/alibaba/open-code-review) | Apache-2.0 | 16 | **84** | Hybrid deterministic-pipeline plus LLM code review with line-level comments |
| [`Graphify-Labs/graphify`](https://github.com/Graphify-Labs/graphify) | Apache-2.0 | 16 | **83** | Turns a codebase plus docs, SQL schemas, configs and PDFs into a queryable  |

This list is deliberately the shortest of the four. Under R1 every candidate was judged as a fork target and most failed. Under R2 the same projects are useful in three other lanes, and forking is what is left over after the cheaper options are exhausted — which is the correct order.

---

## What the benchmark actually proved

**The mine is real.** 164 qualified materials from one run against a 120 target, with all six required categories above floor, and **38 scoring Priority A**. The R1 architecture produced 68 candidates of which 21 were Priority A and only 4 were actionable, because every item had to survive a fork gate before it counted as anything.

**Three findings worth acting on:**

1. **R1 had a blind spot the size of the category.** Token optimisation is the fastest-growing space in the sweep and R1 found two items in it. R2 found 21, including two projects above 70k stars. Searching for fork targets systematically missed the thing ATK most needs to talk about.

2. **The market is competing on cost, hard.** Of the routing and token materials, a large share sell on price — free aggregation (`OmniRoute`, `openrelay`, `9router`), subscription arbitrage (`dario`), or raw reduction (`rtk`, `headroom`, `snip`, `lowfat`). ATK cannot differentiate on price against free. The defensible position visible in this data is **measurement and trust**: cost attribution, drift tracking, auditability — which is exactly where `claude-tap`, `api-relay-audit`, `RelayPlane/proxy` and `tokentab` sit, and they are all small.

3. **Licence resolution is now the bottleneck, not discovery.** 79 of 164 materials have an unresolved licence. That blocks nothing in lanes A and B — but it does mean list 4 is much shorter than it should be. Resolving licences for the top 20 ATK-relevant items is a ~20-minute job with the `raw.githubusercontent.com` access this run confirmed works.

## Honest limits of this run

- **Source diversity is poor.** GitHub only. No Hacker News, Reddit, X, YouTube or Hugging Face. Four of six source classes in `DISCOVERY_ENGINE.md` went unmined.
- **Nothing was executed.** Phase 4 "read primary documentation/code" was done from repository metadata and descriptions, not from running anything. Every claim a project makes about its own savings (`rtk` 60–90%, `headroom` 60–95%, `NadirClaw` 40–70%) is **unverified vendor copy** and must not be repeated by ATK until list 2 is executed.
- **Scores are a first pass.** They rank sensibly against each other; they are not calibrated against outcomes, because there are no outcomes yet.

## Next run (R2-002)

1. Mine the four unmined source classes — that is where the diversity metric improves
2. Resolve licences for the top 20 ATK-relevant materials via raw file reads
3. Execute the top 3 experiments from list 2 and record **measured** numbers
4. Run `api-relay-audit` against ATK's own routing

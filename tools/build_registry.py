#!/usr/bin/env python3
"""Build registry/skill_registry.json from the verified candidate table.

All metrics are a point-in-time snapshot taken from the GitHub repository search API
on SNAPSHOT_DATE. Scores follow SKILL_SCORING.md v1.0; totals are computed, never typed.
"""
import json
import pathlib
from datetime import date

SNAPSHOT_DATE = "2026-09-15"
SCORING_MODEL = "SKILL_SCORING.md v1.0"

# License rulings verified 2026-09-14 via the GitHub repository search `license:` qualifier.
# "UNVERIFIED" means the automated filter did not resolve it -> blocked per LICENSE_REVIEW.md
LICENSES = {
    "MIT":        dict(spdx="MIT", copyleft="none", commercial_use=True, modification=True,
                       redistribution=True, attribution_required=True, notice_required=False,
                       trademark_risk="low", ruling="PASS", verified=True),
    "Apache-2.0": dict(spdx="Apache-2.0", copyleft="none", commercial_use=True, modification=True,
                       redistribution=True, attribution_required=True, notice_required=True,
                       trademark_risk="medium", ruling="PASS", verified=True),
    "AGPL-3.0":   dict(spdx="AGPL-3.0", copyleft="network", commercial_use=True, modification=True,
                       redistribution=True, attribution_required=True, notice_required=True,
                       trademark_risk="low", ruling="ESCALATE", verified=True),
    "Other":      dict(spdx="NOASSERTION", copyleft="unknown", commercial_use=None, modification=None,
                       redistribution=None, attribution_required=True, notice_required=None,
                       trademark_risk="unknown", ruling="ESCALATE", verified=True),
    "None":       dict(spdx="NONE", copyleft="n/a", commercial_use=False, modification=False,
                       redistribution=False, attribution_required=True, notice_required=False,
                       trademark_risk="unknown", ruling="FAIL", verified=True),
    "UNVERIFIED": dict(spdx=None, copyleft="unknown", commercial_use=None, modification=None,
                       redistribution=None, attribution_required=True, notice_required=None,
                       trademark_risk="unknown", ruling="UNVERIFIED", verified=False),
}

# repo, author, category, created, stars, forks, open_issues, license,
# (utility, trend, atk_fit, distribution, maintenance, commercial),
# use_case, atk_relevance, risk
C = [
 ("mvanhorn/last30days-skill","mvanhorn","research","2026-01-23",62022,5410,129,"MIT",(23,18,19,14,7,10),
  "Researches a topic across Reddit, X, YouTube, HN, Polymarket and the web, then synthesises a grounded summary.",
  "Highest token burn per invocation in the pool: a multi-source research loop is many model calls. Routing plus a per-run token budget is a genuine feature, not a sticker.",
  "Depends on several third-party surfaces that change without notice; 129 open issues. Scraper breakage is the dominant maintenance cost."),
 ("blader/humanizer","blader","media-skills","2026-01-18",48065,3911,13,"MIT",(21,17,18,14,10,8),
  "Removes tells of AI-generated writing from text.",
  "Essentially one model call per invocation with a clean prompt seam - the cheapest possible place to demonstrate a correct ATK provider adapter end to end.",
  "Low. ~205 KB source, 13 open issues. Main risk is prompt-quality regression when swapping models, which is exactly what the provider-switch QA test catches."),
 ("virgiliojr94/book-to-skill","virgiliojr94","developer-skills","2026-05-01",30626,3174,23,"MIT",(21,17,19,13,8,10),
  "Turns a technical book PDF into a usable Claude Code skill.",
  "Long-document ingestion is a large, batchable token workload where cost routing is the headline benefit and the savings are directly measurable.",
  "PDF extraction quality varies by source; output quality is model-sensitive, so provider switching must be validated per model tier."),
 ("tt-a1i/archify","tt-a1i","media-skills","2026-04-15",61985,4090,168,"MIT",(22,18,16,15,7,8),
  "Generates architecture, workflow, sequence, data-flow and lifecycle diagrams as self-contained HTML.",
  "Diagram generation is model-quality sensitive and visually demonstrable - the strongest social-content asset in the pool, and a natural multi-model comparison.",
  "168 open issues; self-contained HTML output has a broad surface for rendering regressions."),
 ("Egonex-AI/Understand-Anything","Egonex-AI","developer-skills","2026-03-15",82729,6961,302,"MIT",(21,18,16,14,6,9),
  "Turns a codebase into an interactive, queryable knowledge graph.",
  "Whole-repository analysis is a heavy, repeated token workload; tiered routing (cheap model for extraction, strong model for synthesis) is a real cost lever.",
  "302 open issues and a fast-moving codebase; graph extraction correctness is hard to regression-test."),
 ("Paritok-official/paritok-4b-v1","Paritok-official","routing","2026-07-15",1454,138,8,"Apache-2.0",(20,14,19,13,8,10),
  "Non-destructive context compression gateway for coding agents; drop-in for any BASE_URL agent.",
  "Directly amplifies ATK's cost narrative: compression plus routing compounds. Sits at exactly the layer ATK sells.",
  "Young project (created 2026-07), small contributor base, and its own 4B model is an extra dependency to host or call."),
 ("Panniantong/Agent-Reach","Panniantong","automation-skills","2026-02-24",81070,7060,134,"MIT",(22,18,15,14,6,8),
  "Gives an agent read/search access to Twitter, Reddit, YouTube, GitHub, Bilibili and XiaoHongShu via one CLI.",
  "High-volume retrieval feeding model calls; strong pairing with ATK routing for summarisation workloads.",
  "Scraping-based access to platforms that actively change; ToS exposure on several sources needs legal review before redistribution."),
 ("K-Dense-AI/scientific-agent-skills","K-Dense-AI","enterprise-skills","2025-10-19",44908,4073,10,"MIT",(22,15,17,12,8,9),
  "165 validated scientific skills plus 100+ scientific databases for biology, chemistry, medicine and drug discovery.",
  "Enterprise/research buyers with sustained, high-value token consumption and low price sensitivity.",
  "Domain correctness matters far more than in general skills; a wrong model swap has real consequences. Only 10 open issues suggests strong maintenance."),
 ("nexu-io/open-design","nexu-io","media-skills","2026-04-28",96144,11139,1008,"Apache-2.0",(21,18,15,15,5,9),
  "Local-first design surface turning a coding agent into a prototype/landing-page/slide/image/video engine.",
  "Already BYOK-oriented, so a provider seam exists. Media generation is token-heavy and highly visual for content.",
  "1008 open issues and a desktop app surface - the highest maintenance cost among Priority A candidates."),
 ("tbphp/gpt-load","tbphp","routing","2025-06-06",6740,726,20,"MIT",(21,15,18,11,8,9),
  "Self-hosted AI gateway for multi-channel, multi-credential setups with scheduling, failover, logs and usage.",
  "The natural routing anchor: ATK becomes one upstream channel among many, which is the Routing Principle expressed as architecture.",
  "Low. Only 20 open issues against 726 forks is the healthiest issue hygiene in the routing category."),
 ("cathrynlavery/diagram-design","cathrynlavery","media-skills","2026-04-16",39705,2522,44,"MIT",(20,17,14,15,9,7),
  "38 editorial diagram types rendered as self-contained HTML + SVG.",
  "Visual output, small surface, easy provider seam. Excellent content asset; moderate token consumption.",
  "Low. Small codebase, 44 open issues."),
 ("nextlevelbuilder/ui-ux-pro-max-skill","nextlevelbuilder","developer-skills","2025-11-30",127581,13619,85,"MIT",(21,16,15,14,7,8),
  "Design intelligence for building professional UI/UX across platforms.",
  "High-volume generation workload with visual output; good routing demo surface.",
  "85 open issues at very large scale; design-quality regressions are subjective and hard to test."),
 ("Leonxlnx/taste-skill","Leonxlnx","developer-skills","2026-02-19",87095,5936,66,"MIT",(19,18,15,14,8,7),
  "Steers agent output away from generic, boring generations.",
  "Prompt-layer skill with a clean model seam; quality is strongly model-dependent, making multi-model comparison genuinely informative.",
  "Value is subjective and hard to benchmark, which makes the Beat-5 cost story weaker than for research skills."),
 ("alibaba/open-code-review","alibaba","developer-skills","2026-05-18",25280,1845,160,"Apache-2.0",(21,17,16,12,6,9),
  "Hybrid deterministic-pipeline plus LLM code review with line-level comments and a multi-language ruleset.",
  "Already OpenAI- and Anthropic-compatible, so the provider seam exists. Per-PR review is recurring token consumption.",
  "Vendor-led project; direction set by Alibaba. Apache-2.0 NOTICE and trademark handling need care."),
 ("ENTERPILOT/GoModel","ENTERPILOT","routing","2025-12-05",1155,100,72,"MIT",(20,13,20,11,7,10),
  "Go AI gateway/control plane with a unified OpenAI- and Anthropic-compatible API, routing, failover and cost tracking.",
  "Highest ATK Fit in the pool - it is the routing layer, so ATK integration is adding a provider rather than retrofitting a seam.",
  "Small community (1.1k stars, 100 forks) means little external validation; 72 open issues is high relative to size."),
 ("OthmanAdi/planning-with-files","OthmanAdi","agent-skills","2026-01-03",26885,2237,8,"MIT",(22,16,14,13,9,6),
  "Crash-proof file-based planning and session recovery for long-running agents.",
  "No direct model call site - it is a file/prompt protocol. ATK value is indirect (longer sessions consume more tokens).",
  "Low. 8 open issues. Main risk is that the ATK value-add is weak enough to read as a rebrand."),
 ("zarazhangrui/frontend-slides","zarazhangrui","media-skills","2026-01-28",29294,2314,68,"MIT",(19,17,14,15,8,7),
  "Generates presentation slides on the web using a coding agent's frontend skills.",
  "Visual, shareable output; moderate token consumption per deck.",
  "Low-moderate. Output quality varies by model."),
 ("addyosmani/agent-skills","addyosmani","developer-skills","2026-02-15",94287,10028,119,"MIT",(21,18,12,14,8,5),
  "Production-grade engineering skills for AI coding agents.",
  "A skill collection rather than a runtime - no single call site for routing.",
  "Well-maintained collection with no call site - little technical surface for ATK to add to."),
 ("DietrichGebert/ponytail","DietrichGebert","developer-skills","2026-06-12",138230,7418,266,"MIT",(18,19,11,13,9,4),
  "Steers agents toward minimal, YAGNI-style code.",
  "Prompt-layer only; reduces token consumption by design, which works against the commercial dimension.",
  "Fastest-growing candidate but the thinnest ATK insertion point."),
 ("wshobson/agents","wshobson","agent-skills","2025-07-24",39648,4223,5,"MIT",(20,15,12,13,9,5),
  "Multi-harness agentic plugin marketplace across Claude Code, Codex, Cursor, Copilot and others.",
  "Marketplace/aggregator - ATK is better placed as a listed entry than as a fork.",
  "A marketplace listing reaches its users directly; a fork of it would not."),
 ("titanwings/distilly","titanwings","agent-skills","2026-03-30",24716,2145,37,"MIT",(18,16,13,13,8,6),
  "Distils how a person works into reusable skills for any agent.",
  "Skill-generation is a moderate token workload with a usable seam.",
  "Moderate; non-default branch (dot-skill) complicates fork tracking."),
 ("JimLiu/baoyu-skills","JimLiu","agent-skills","2026-01-13",25895,2867,15,"MIT",(17,16,12,12,8,5),
  "A widely-used personal collection of agent skills.",
  "Collection, not a runtime.",
  "A skill collection with no runtime: nothing for a router adapter to attach to."),
 ("KKKKhazix/khazix-skills","KKKKhazix","agent-skills","2026-04-06",20661,2200,49,"MIT",(16,16,12,12,8,5),
  "Chinese-language agent skill collection covering goal definition, analysis and writing.",
  "Strong fit with ATK's Chinese-language social channels.",
  "Collection, not a runtime. Strong fit with ATK Chinese-language channels for content."),
 ("phuryn/pm-skills","phuryn","enterprise-skills","2026-03-01",26312,2806,41,"MIT",(17,16,11,12,8,5),
  "100+ product-management skills from discovery through growth.",
  "Non-developer audience; weaker fit with a developer-first funnel.",
  "Low technical risk, low strategic fit."),
 ("alirezarezvani/claude-skills","alirezarezvani","agent-skills","2025-10-19",25949,3655,17,"MIT",(17,14,11,12,8,5),
  "380 skills, 30+ agents and 70+ commands across many coding agents.",
  "Collection, not a runtime.",
  "Breadth over depth; high surface, low differentiation."),
 ("sickn33/agentic-awesome-skills","sickn33","discovery","2026-01-14",46406,6761,2,"MIT",(14,17,10,12,8,4),
  "Agent-first control plane over a 2,115-skill catalogue, with CLI, local MCP and plugins.",
  "Catalogue/control plane - closer to a competitor of awesome-ai-skills than a fork target.",
  "Directly overlaps ATK's own discovery repo."),
 ("agentskills/agentskills","agentskills","standard","2025-12-16",25324,1899,76,"Apache-2.0",(18,16,9,11,8,3),
  "Specification and documentation for the Agent Skills standard.",
  "A standard to conform to, never to fork.",
  "Forking a specification fragments it and would damage ATK's standing."),
 ("googleworkspace/cli","googleworkspace","automation-skills","2026-03-02",30992,1832,133,"Apache-2.0",(21,17,10,12,7,4),
  "Google Workspace CLI across Drive, Gmail, Calendar, Sheets, Docs and Admin, with agent skills.",
  "Vendor tool with no model call site.",
  "Vendor-controlled; trademark risk high. Do not fork."),
 ("topoteretes/cognee","topoteretes","agent-infrastructure","2023-08-16",30681,3027,494,"Apache-2.0",(21,11,15,11,6,8),
  "Self-hosted knowledge-graph memory platform for agents.",
  "Memory pipelines embed and summarise continuously - real token consumption.",
  "494 open issues; mature project with its own commercial direction."),
 ("oraios/serena","oraios","mcp","2025-03-23",29320,1988,178,"MIT",(23,14,13,12,6,7),
  "Semantic retrieval and editing MCP toolkit - an IDE layer for agents.",
  "Reduces tokens by design; strong utility, weak commercial alignment.",
  "Language-server dependencies make the maintenance surface wide."),
 ("DeusData/codebase-memory-mcp","DeusData","mcp","2026-02-24",43233,3522,582,"MIT",(21,18,13,12,5,7),
  "Indexes codebases into a persistent knowledge graph; 158 languages, single static binary.",
  "Token-reducing by design; useful to ATK users but not a routing surface.",
  "582 open issues; C codebase raises the security-review bar."),
 ("Portkey-AI/gateway","Portkey-AI","routing","2023-08-23",12987,1300,265,"MIT",(23,13,17,11,5,9),
  "AI gateway with guardrails routing to 1,600+ LLMs.",
  "ATK could be added as a provider plugin - but upstream contribution beats forking here.",
  "Vendor-led with a commercial product behind it; forking invites direct competitive response."),
 ("maximhq/bifrost","maximhq","routing","2025-03-19",8069,1214,995,"Apache-2.0",(22,15,18,11,4,9),
  "High-performance Go AI gateway with adaptive load balancing and cluster mode.",
  "Strong architectural fit for ATK routing.",
  "995 open issues and a non-standard default branch (dev) - the weakest maintenance profile among serious gateways."),
 ("katanemo/plano","katanemo","routing","2024-07-09",7049,484,140,"Apache-2.0",(21,12,17,11,6,8),
  "Rust proxy and data plane for agentic apps with smart LLM routing and guardrails.",
  "Routing-native; ATK fits as an upstream target.",
  "Rust plus Envoy raises the maintenance bar; vendor-led."),
 ("BerriAI/litellm","BerriAI","routing","2023-07-27",58721,11430,5054,"MIT",(25,13,16,10,2,9),
  "The most widely adopted LLM gateway; 100+ APIs in OpenAI format.",
  "ATK should ship an upstream provider PR, not a fork. Being a first-class LiteLLM provider is worth more than an ATK fork nobody installs.",
  "5,054 open issues and an enormous surface - forking is not maintainable at ATK's Phase 1 capacity."),
 ("coaidev/coai","coaidev","routing","2023-07-17",9311,1226,39,"Apache-2.0",(19,10,14,10,6,8),
  "Multi-tenant LLM gateway with built-in admin and billing across 200+ models.",
  "Billing-adjacent; overlaps ATK's own product surface.",
  "Strategic overlap with ATK's commercial layer."),
 ("APIParkLab/APIPark","APIParkLab","routing","2024-08-12",1815,245,53,"Apache-2.0",(18,9,14,9,6,7),
  "Cloud-native AI and API gateway with LLM API management and a developer portal.",
  "Enterprise gateway; moderate fit.",
  "Slow growth; enterprise sales motion rather than developer adoption."),
 ("Fast-Editor/Lynkr","Fast-Editor","routing","2025-12-03",550,61,5,"Apache-2.0",(16,11,17,9,8,7),
  "CLI HTTP proxy for Claude Code interactions with prompt caching and multi-provider support.",
  "Small, clean routing surface - easy to integrate.",
  "Very small community; limited distribution value."),
 ("Kong/kong","Kong","routing","2014-11-17",44137,5210,200,"Apache-2.0",(22,9,13,9,4,7),
  "Mature API and AI gateway.",
  "Enterprise infrastructure; ATK fits as a plugin, never as a fork.",
  "Enormous, mature, vendor-led. Fork is out of the question."),
 ("diegosouzapw/OmniRoute","diegosouzapw","routing","2026-02-13",66084,9268,766,"MIT",(20,19,3,13,4,2),
  "Free AI gateway aggregating 352 providers and 1200+ models with quota-aware fallback.",
  "STRATEGIC CONFLICT: its core value is free provider aggregation, which directly displaces paid routing.",
  "Veto per SKILL_SCORING.md 4.4. 766 open issues; non-standard default branch. Track for competitive intelligence only."),
 ("decolua/9router","decolua","routing","2026-01-05",28738,5269,2101,"MIT",(18,18,3,12,2,2),
  "Routes coding agents to free Claude/GPT/Gemini across 40+ providers.",
  "STRATEGIC CONFLICT: explicitly positions free access against paid token consumption.",
  "Veto per SKILL_SCORING.md 4.4. 2,101 open issues is the worst backlog in the pool."),
 ("router-for-me/CLIProxyAPI","router-for-me","routing","2025-07-01",51751,7835,639,"MIT",(19,16,3,11,5,2),
  "Wraps coding-agent subscriptions as OpenAI/Gemini/Claude-compatible API services.",
  "STRATEGIC CONFLICT: converts subscriptions into API access, displacing metered token spend. ToS exposure on the wrapped services.",
  "Veto per SKILL_SCORING.md 4.4, plus material ToS risk for a redistributor."),
 ("upstash/context7","upstash","mcp","2025-03-26",62012,2992,61,"MIT",(23,15,9,12,7,4),
  "Up-to-date code documentation for LLMs and AI code editors.",
  "Token-reducing; excellent utility but no routing surface.",
  "Vendor-led; license not verified by the automated gate."),
 ("ChromeDevTools/chrome-devtools-mcp","ChromeDevTools","mcp","2025-09-11",51935,3647,106,"Apache-2.0",(22,16,9,12,7,5),
  "Chrome DevTools exposed to coding agents over MCP.",
  "Tooling layer, no model call site.",
  "Vendor-controlled (Google); trademark risk high. License not verified."),
 ("github/github-mcp-server","github","mcp","2025-03-04",32926,4965,320,"MIT",(22,13,8,10,7,4),
  "GitHub's official MCP server.",
  "Official vendor server - conform, do not fork.",
  "Trademark risk high; license not verified."),
 ("modelcontextprotocol/servers","modelcontextprotocol","mcp","2024-11-19",90324,11632,522,"Other",(22,12,10,11,5,4),
  "The reference collection of MCP servers.",
  "Reference implementation - contribute upstream instead.",
  "Forking the reference collection fragments the ecosystem."),
 ("modelcontextprotocol/registry","modelcontextprotocol","mcp","2025-02-05",7247,989,165,"Other",(17,13,8,9,7,2),
  "Community registry service for MCP servers.",
  "ATK should publish into it, not fork it.",
  "Ecosystem infrastructure."),
 ("czlonkowski/n8n-mcp","czlonkowski","mcp","2025-06-07",22884,3641,67,"MIT",(20,13,11,11,7,6),
  "MCP server that builds n8n workflows for coding agents.",
  "Workflow generation consumes tokens; moderate fit.",
  "Tightly coupled to n8n's evolving schema. License not verified."),
 ("mobile-next/mobile-mcp","mobile-next","mcp","2025-03-28",6689,582,43,"Apache-2.0",(19,12,10,12,7,5),
  "MCP server for mobile automation across iOS, Android, emulators and real devices.",
  "Device automation with vision-model calls; moderate consumption.",
  "Device-farm dependencies. License not verified."),
 ("getsentry/XcodeBuildMCP","getsentry","mcp","2025-03-09",6383,318,24,"MIT",(19,12,9,11,7,5),
  "MCP server and CLI for iOS and macOS project work.",
  "Narrow platform audience.",
  "Vendor-led; license not verified."),
 ("zcaceres/markdownify-mcp","zcaceres","mcp","2024-12-18",2990,253,29,"MIT",(18,9,12,11,9,5),
  "Converts almost anything to Markdown over MCP.",
  "Preprocessing for token-heavy pipelines; small and clean.",
  "Low maintenance but modest growth. License not verified."),
 ("brightdata/brightdata-mcp","brightdata","mcp","2025-04-15",2641,327,40,"MIT",(18,11,13,11,7,7),
  "All-in-one public web access over MCP.",
  "Feeds retrieval-heavy pipelines.",
  "Commercial vendor with paid quotas; license not verified."),
 ("anthropics/skills","anthropics","agent-skills","2025-09-22",176286,20867,1232,"None",(22,17,12,13,9,5),
  "The public reference repository for Agent Skills.",
  "Reference material to conform to, not a fork target.",
  "BLOCKED: did not resolve to MIT or Apache-2.0 under the automated gate despite its scale. Manual review required. Trademark risk high."),
 ("Graphify-Labs/graphify","Graphify-Labs","developer-skills","2026-04-03",116685,11393,1342,"Apache-2.0",(22,18,16,13,5,9),
  "Turns a codebase plus docs, SQL schemas, configs and PDFs into a queryable knowledge graph.",
  "Heavy multi-document ingestion - strong routing and cost-tiering fit.",
  "BLOCKED on licence. 1,342 open issues; non-standard default branch (v8)."),
 ("calesthio/OpenMontage","calesthio","media-skills","2026-03-29",59020,7403,320,"AGPL-3.0",(21,18,17,15,4,10),
  "Agentic video production: 12 pipelines, 100+ tools, 700+ skill and knowledge files.",
  "Media generation is the highest-value token workload available and the best visual content source.",
  "BLOCKED on licence. Very large surface (700+ files), heavy external tool dependencies (ffmpeg, image and TTS models)."),
 ("mksglu/context-mode","mksglu","agent-infrastructure","2026-02-23",22813,1650,245,"Other",(21,18,17,12,5,9),
  "Context-window optimisation with tool-output sandboxing, session memory and routing enforcement across 17 platforms.",
  "Explicitly a routing-enforcement layer - a direct architectural fit for ATK.",
  "BLOCKED on licence. 245 open issues."),
 ("thedotmack/claude-mem","thedotmack","agent-infrastructure","2025-08-31",93860,8259,183,"Apache-2.0",(21,16,13,12,6,6),
  "Persistent cross-session context capture and compression for agents.",
  "Compression pipelines call models continuously.",
  "BLOCKED on licence."),
 ("coreyhaines31/marketingskills","coreyhaines31","enterprise-skills","2026-01-15",50207,7606,112,"MIT",(19,17,14,14,7,7),
  "Marketing skills for agents: CRO, copywriting, SEO, analytics and growth engineering.",
  "Directly useful to ATK's own content engine - dogfooding value on top of distribution value.",
  "BLOCKED on licence."),
 ("kepano/obsidian-skills","kepano","developer-skills","2026-01-02",48315,3443,72,"MIT",(20,17,12,13,8,5),
  "Agent skills for Obsidian CLI and open formats.",
  "Note-processing workloads; moderate consumption.",
  "Licence now confirmed MIT. Note-processing workloads; moderate token consumption."),
 ("mukul975/Anthropic-Cybersecurity-Skills","mukul975","enterprise-skills","2026-02-25",32771,3956,46,"Apache-2.0",(20,17,15,13,7,8),
  "817 cybersecurity skills mapped to MITRE ATT&CK, NIST CSF 2.0, ATLAS and D3FEND.",
  "Enterprise security buyers; sustained high-value consumption.",
  "BLOCKED on licence: the repository description claims Apache-2.0 but prose is not verification. Security-domain content needs its own review."),
 ("theopenco/llmgateway","theopenco","routing","2025-04-12",1633,183,68,"Other",(19,13,17,10,7,8),
  "Unified API to route, manage and analyse LLM requests across providers.",
  "Routing-native; good architectural fit.",
  "BLOCKED on licence - resolved as neither MIT, Apache-2.0 nor AGPL-3.0 under the automated gate."),
 ("ThinkWatchProject/ThinkWatch","ThinkWatchProject","routing","2026-04-02",813,21,0,"Other",(18,12,16,9,8,7),
  "Enterprise AI bastion host for secure AI API and MCP access with RBAC, audit logs and cost tracking.",
  "Enterprise governance layer around routing.",
  "BLOCKED on licence. Only 21 forks - minimal external validation."),
 ("bestruirui/octopus","bestruirui","routing","2025-11-18",2625,427,19,"AGPL-3.0",(18,14,15,10,8,7),
  "Personal LLM API aggregation gateway.",
  "Reasonable routing fit on the merits.",
  "ESCALATE: AGPL-3.0 network copyleft. Hosting a modified version as a service obliges ATK to publish complete corresponding source. Blocked for Phase 1."),
 ("ComposioHQ/awesome-claude-skills","ComposioHQ","discovery","2025-10-17",75025,8670,1453,"None",(9,16,8,13,6,3),
  "Curated list of Claude Skills and tooling.",
  "Discovery reference for awesome-ai-skills; link to it, do not fork it.",
  "Awesome-list: Utility capped at 10 per SKILL_SCORING.md 2. Licence unverified."),
 ("hesreallyhim/awesome-claude-code","hesreallyhim","discovery","2025-04-19",54026,4708,1046,"Other",(9,14,7,13,5,2),
  "Curated Claude Code resources, skills, agents and tooling.",
  "Discovery reference only.",
  "Awesome-list. Licence unverified."),
 ("VoltAgent/awesome-agent-skills","VoltAgent","discovery","2025-10-28",34310,3636,12,"MIT",(9,15,7,12,8,2),
  "1000+ agent skills from official teams and the community.",
  "Best single discovery input for the Trend Scout agent.",
  "Awesome-list; no fork value, high reference value."),
 ("VoltAgent/awesome-openclaw-skills","VoltAgent","discovery","2026-01-25",52562,5026,0,"MIT",(8,17,7,12,8,2),
  "5,400+ skills filtered from the OpenClaw Skills Registry.",
  "Discovery input.",
  "Awesome-list."),
 ("github/awesome-copilot","github","discovery","2025-06-11",39000,4940,45,"MIT",(10,13,7,11,8,2),
  "Community instructions, agents, skills and configurations for GitHub Copilot.",
  "Discovery input; vendor-run.",
  "Awesome-list; trademark risk high."),
]

def months_between(iso, ref):
    a = date.fromisoformat(iso); b = date.fromisoformat(ref)
    return max((b - a).days / 30.44, 0.5)

def priority(total):
    if total >= 80: return "A"
    if total >= 65: return "B"
    if total >= 50: return "Watchlist"
    return "Ignore"

DIMS = ("utility", "trend", "atk_fit", "distribution", "maintenance", "commercial")
MAX = dict(utility=25, trend=20, atk_fit=20, distribution=15, maintenance=10, commercial=10)

candidates = []
for (repo, author, cat, created, stars, forks, issues, lic, dims,
     use_case, atk_rel, risk) in C:
    score = dict(zip(DIMS, dims))
    for k, v in score.items():
        assert 0 <= v <= MAX[k], f"{repo}: {k}={v} exceeds max {MAX[k]}"
    total = sum(dims)
    prio = priority(total)
    lic_block = dict(LICENSES[lic])
    lic_block["verified_at"] = SNAPSHOT_DATE if lic_block["verified"] else None
    lic_block["method"] = "github-license-metadata" if lic_block["verified"] else "unresolved"

    gate_ok = lic_block["ruling"] == "PASS"
    conflict = "STRATEGIC CONFLICT" in atk_rel
    if conflict:
        decision, blocked_by = "reject", "strategic-conflict-veto"
    elif not gate_ok:
        decision, blocked_by = "blocked", "license-gate"
    elif prio == "A":
        decision, blocked_by = "review", None
    elif prio == "B":
        decision, blocked_by = "watch", None
    else:
        decision, blocked_by = "watch", None

    spm = round(stars / months_between(created, SNAPSHOT_DATE))
    candidates.append({
        "id": repo.split("/")[1].lower(),
        "repository": repo,
        "original_author": author,
        "original_url": f"https://github.com/{repo}",
        "category": cat,
        "license": lic_block,
        "metrics": {
            "stars": stars, "forks": forks, "open_issues": issues,
            "created_at": created, "snapshot_at": SNAPSHOT_DATE,
            "stars_per_month": spm,
            "issue_pressure": round(issues / forks, 3) if forks else None,
        },
        "growth_signal": f"~{spm:,} stars/month since {created}",
        "use_case": use_case,
        "atk_relevance": atk_rel,
        "integration_difficulty": None,
        "distribution_potential": None,
        "maintenance_cost": None,
        "risk": risk,
        "score": {**score, "total": total},
        "priority": prio,
        "decision": decision,
        "blocked_by": blocked_by,
        "upstream": {
            "upstream_repository": repo, "upstream_branch": None,
            "last_sync": None, "atk_changes": [], "conflict_status": "not-forked",
        },
    })

# Derive the three qualitative bands from their numeric dimensions so they cannot drift.
def band(v, hi, lo, labels):
    return labels[0] if v >= hi else (labels[1] if v >= lo else labels[2])

for c in candidates:
    s = c["score"]
    c["integration_difficulty"] = band(s["atk_fit"], 17, 13, ["low", "medium", "high"])
    c["distribution_potential"] = band(s["distribution"], 13, 10, ["high", "medium", "low"])
    c["maintenance_cost"] = band(s["maintenance"], 9, 7, ["low", "medium", "high"])

candidates.sort(key=lambda c: (-c["score"]["total"], -c["score"]["atk_fit"]))

registry = {
    "schema_version": "1.0.0",
    "generated_at": SNAPSHOT_DATE,
    "scoring_model": SCORING_MODEL,
    "snapshot_note": (
        "All metrics are a point-in-time snapshot from the GitHub repository search API on "
        + SNAPSHOT_DATE + ". Star and issue counts move; re-run tools/build_registry.py to refresh."
    ),
    "license_note": (
        "Licenses resolved against GitHub license metadata in two passes (2026-09-14, 2026-09-15). "
        "ruling=PASS may be forked. ruling=ESCALATE means either network copyleft (AGPL) or a "
        "non-standard license GitHub could not identify - a human must read it. ruling=FAIL means "
        "no license file exists, which in copyright terms is all-rights-reserved, not public domain."
    ),
    "counts": {
        "total": len(candidates),
        "priority_a": sum(1 for c in candidates if c["priority"] == "A"),
        "priority_b": sum(1 for c in candidates if c["priority"] == "B"),
        "watchlist": sum(1 for c in candidates if c["priority"] == "Watchlist"),
        "license_pass": sum(1 for c in candidates if c["license"]["ruling"] == "PASS"),
        "license_escalate": sum(1 for c in candidates if c["license"]["ruling"] == "ESCALATE"),
        "license_fail": sum(1 for c in candidates if c["license"]["ruling"] == "FAIL"),
        "license_unverified": sum(1 for c in candidates if not c["license"]["verified"]),
        "rejected_strategic": sum(1 for c in candidates if c["decision"] == "reject"),
    },
    "candidates": candidates,
    "forks": [],
}

out = pathlib.Path(__file__).resolve().parent.parent / "registry" / "skill_registry.json"
out.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out} ({len(candidates)} candidates)")
print("counts:", json.dumps(registry["counts"], indent=None))

"""Raw material table for Benchmark Run R2-001 (2026-09-15).

Metrics captured from the GitHub repository search API on 2026-09-15.
Columns: repo, stars, forks, issues, created, category, license,
         technical_utility(25), atk_relevance(20), content_potential(15), note

technical_utility / atk_relevance / content_potential are assigned by review.
momentum, experimentability and source_credibility are DERIVED by stated rule in
build_materials.py so the tail of the list is not given fake precision.

license: "?" means not resolved in this run. Per ARCHITECTURE_R2 this does NOT
reduce the score and does NOT block discovery - it only constrains redistribution.
"""

# ── Token optimization / cost ──────────────────────────────────────────────
TOKEN_OPT = [
 ("rtk-ai/rtk",80473,5108,1621,"2026-01-22","token-optimization","Apache-2.0",23,19,14,
  "CLI proxy that cuts up to 90% of the BASH OUTPUT an agent reads. Its README states this is explicitly NOT a 90% bill reduction, and that token counts are estimated as bytes/4 with no tokenizer shipped, so percentages are reliable but absolute numbers are approximate. 14 open issues dispute the savings dashboard; one repro reports a >10,000x over-count."),
 ("headroomlabs-ai/headroom",72266,5531,643,"2026-01-07","token-optimization","Apache-2.0",23,19,14,
  "Compresses tool output, logs, files and RAG chunks before they reach the model. Its own scenario table reports 21-57% (90% only on highly repetitive payloads), measured with the provider tokenizer, with published quality benchmarks (SQuAD v2 97% at 19% compression, BFCL 97% at 32%) and a seeded offline reproduction command."),
 ("yvgude/lean-ctx",3788,346,7,"2026-03-23","token-optimization","Apache-2.0",20,18,12,
  "Rust context-intelligence layer for coding agents."),
 ("jgravelle/jcodemunch-mcp",2686,367,0,"2026-02-09","token-optimization","?",20,16,13,
  "Symbol-level GitHub code retrieval over tree-sitter AST; claims 95%+ token cut on code exploration."),
 ("cytostack/openwolf",2323,209,55,"2026-03-15","token-optimization","?",19,15,12,
  "Portable project memory plus token accounting measured from harness transcripts. Local only, no telemetry."),
 ("alexgreensh/token-optimizer",2284,175,1,"2026-02-26","token-optimization","?",19,16,13,
  "Finds 'ghost tokens', survives compaction, tracks context quality decay."),
 ("Paritok-official/paritok-4b-v1",1454,138,8,"2026-07-15","token-optimization","Apache-2.0",20,19,13,
  "Non-destructive compression gateway backed by an open 4B code-native model."),
 ("crwdla/tokentab",1136,213,1,"2026-09-07","token-optimization","MIT",18,17,12,
  "Reads Claude Code/Codex/Gemini session logs and computes cost by model, project and day."),
 ("lucasrosati/claude-code-memory-setup",981,89,5,"2026-04-12","token-optimization","MIT",17,14,13,
  "Obsidian + knowledge-graph memory setup claiming up to 71.5x fewer tokens per session."),
 ("Tura-AI/tura",633,34,2,"2026-07-06","token-optimization","?",18,16,11,
  "Rust agent builder targeting 80% less token use with better results."),
 ("ojuschugh1/sqz",624,43,4,"2026-04-12","token-optimization","?",17,16,11,
  "Rust context compressor for LLM cost reduction."),
 ("agentic-os-org/ANOLISA",613,104,97,"2026-03-30","token-optimization","Apache-2.0",17,15,11,
  "Agentic OS with runtime, security, observability and tokenless response compression."),
 ("nadimtuhin/claude-token-optimizer",579,73,8,"2025-11-10","token-optimization","MIT",14,13,10,
  "Token usage optimiser for Claude API calls."),
 ("zdk/lowfat",573,17,2,"2026-04-09","token-optimization","Apache-2.0",17,15,12,
  "Strips noise from command output to save tokens. Small, sharp, Rust."),
 ("gglucass/headroom-desktop",552,58,4,"2026-03-30","token-optimization","MIT",16,14,13,
  "Menu-bar app cutting Claude Code and Codex token cost by ~50%."),
 ("ooples/token-optimizer-mcp",529,64,2,"2025-10-11","token-optimization","MIT",17,16,11,
  "Measures token savings per agent and shares a live local knowledge graph across 16 CLI clients."),
 ("GMaN1911/claude-cognitive",451,39,1,"2025-12-30","token-optimization","MIT",16,13,10,
  "Working memory and multi-instance coordination for Claude Code."),
 ("edouard-claude/snip",445,43,3,"2026-02-20","token-optimization","MIT",18,16,12,
  "Go CLI proxy, declarative YAML filters, positioned as an rtk alternative."),
 ("juyterman1000/entroly",443,67,1,"2026-03-07","token-optimization","Apache-2.0",20,18,13,
  "Reversible, byte-exact recoverable context compression with an auditable receipt per reduction."),
 ("ratel-ai/ratel",436,21,15,"2025-11-12","token-optimization","MIT",19,17,12,
  "Context engineering with BM25 + semantic retrieval and progressive disclosure. No vector DB."),
 ("IyadhKhalfallah/clauditor",428,42,22,"2026-04-02","token-optimization","MIT",16,14,12,
  "Auto-rotates oversized Claude Code sessions to stop quota burn."),
]

# ── A2A / agent interoperability ───────────────────────────────────────────
A2A = [
 ("a2aproject/A2A",25779,2609,252,"2025-03-25","a2a","?",23,16,13,
  "The Agent2Agent open protocol for interoperability between opaque agentic applications. Linux Foundation."),
 ("GetBindu/Bindu",9823,442,157,"2025-03-16","a2a","?",20,17,12,
  "Identity, communication and payments layer for AI agents."),
 ("EvoMap/evolver",9080,845,23,"2026-02-01","a2a","?",19,15,13,
  "Self-evolving engine for agents with auditable genes, capsules and events."),
 ("google/adk-go",8793,1007,238,"2025-05-05","a2a","?",22,14,11,
  "Google's code-first Go toolkit for building, evaluating and deploying agents."),
 ("internet-court/internet-court-skill",5722,106,26,"2026-06-16","a2a","?",19,17,14,
  "Trust layer for agent-to-agent commerce: mandates, delegated permissions, x402 payments, escrow, disputes."),
 ("ag2ai/ag2",4927,718,27,"2024-11-11","a2a","?",21,14,11,
  "AG2, formerly AutoGen. Open-source AgentOS."),
 ("SolaceLabs/solace-agent-mesh",4926,276,99,"2025-01-10","a2a","?",20,14,10,
  "Event-driven framework for orchestrating multi-agent systems."),
 ("panaversity/learn-agentic-ai",4368,1011,59,"2024-06-12","a2a","?",16,11,12,
  "Teaching repo for agentic AI with Dapr, MCP, A2A and Kubernetes."),
 ("archestra-ai/archestra",4279,1199,44,"2025-07-15","a2a","?",20,17,11,
  "Enterprise AI platform with guardrails, MCP registry, gateway and orchestrator."),
 ("evalstate/fast-agent",3919,444,29,"2025-01-18","a2a","?",21,16,12,
  "Build and evaluate agents with strong Skills/MCP/ACP/A2A support."),
 ("Atmosphere/atmosphere",3812,761,10,"2010-06-30","a2a","?",19,15,10,
  "Portable JVM agent runtime; one agent class runs on 12 backends behind one SPI. Speaks MCP, A2A and AG-UI."),
 ("wang2122/sprix-sage-router",3689,187,2,"2026-08-18","a2a","?",18,18,12,
  "State-aware SELF/COLLABORATE/HANDOFF routing for A2A agent networks."),
 ("a2aproject/a2a-python",2141,495,81,"2025-05-09","a2a","?",20,15,10,
  "Official Python SDK for the A2A protocol."),
 ("trpc-group/trpc-agent-go",1791,308,129,"2025-05-14","a2a","?",20,15,10,
  "Tencent Go agent framework with graph workflows, memory, A2A, AG-UI, MCP and observability."),
 ("a2aproject/a2a-samples",1765,754,314,"2025-05-27","a2a","?",16,12,11,
  "Official A2A protocol samples."),
 ("mozilla-ai/any-agent",1200,96,30,"2025-03-25","a2a","?",20,16,12,
  "One interface to use and evaluate different agent frameworks. Mozilla AI."),
 ("agentlas-ai/Agentlas-OS",1111,103,1,"2026-06-04","a2a","?",18,15,11,
  "Specialist agents in a hub, temporary orchestrator per task. Local-first, any model."),
 ("Azure-Samples/AI-Gateway",987,513,85,"2024-04-03","a2a","?",17,16,11,
  "Microsoft labs for AI models, MCP servers and agents behind an AI gateway."),
 ("agentic-community/mcp-gateway-registry",917,236,115,"2025-05-29","a2a","?",19,18,11,
  "Enterprise MCP gateway and registry with OAuth, dynamic tool discovery and governed access."),
 ("nuwax-ai/nuwax",887,182,16,"2025-07-09","a2a","?",18,16,10,
  "Enterprise agent platform with model proxy, memory, knowledge base and plugin ecosystem."),
 ("agentscope-ai/agentscope-runtime",865,167,72,"2025-08-14","a2a","?",19,14,10,
  "Production runtime with tool sandboxing, agent-as-a-service APIs and observability."),
 ("w8123/EnterpriseAgentFramework",725,58,3,"2026-04-02","a2a","?",17,15,10,
  "Chinese-language enterprise agent platform bringing AI into existing OA/ERP/CRM systems."),
 ("ai-boost/awesome-a2a",686,158,107,"2025-04-10","a2a","?",9,10,11,
  "Curated A2A agents, tools, servers and clients. Discovery input."),
 ("lofcz/LLMTornado",641,115,14,"2023-10-08","a2a","?",18,16,10,
  ".NET agent library with 30+ built-in connectors."),
 ("diegosouzapw/OmniRoute",66431,9314,695,"2026-02-13","a2a","MIT",20,8,13,
  "Free gateway aggregating 352 providers with MCP/A2A. Strategically competitive with paid routing."),
]

# ── Agent frameworks / runtimes ────────────────────────────────────────────
FRAMEWORK = [
 ("HKUDS/nanobot",48179,8515,780,"2026-02-01","agent-framework","?",21,15,14,
  "Ultra-light self-hosted personal agent framework with WebUI, tools, memory, MCP and multi-agent workflows."),
 ("666ghj/BettaFish",42219,7616,5,"2024-07-01","agent-framework","?",19,13,13,
  "Chinese multi-agent public-opinion analysis assistant, built from scratch with no framework."),
 ("esengine/DeepSeek-Reasonix",35557,2399,1893,"2026-04-21","agent-framework","?",20,18,13,
  "DeepSeek-native terminal coding agent engineered around prefix-cache stability."),
 ("deepset-ai/haystack",26513,3138,142,"2019-11-14","agent-framework","?",22,15,10,
  "Mature orchestration framework with explicit control over retrieval, routing, memory and generation."),
 ("NirDiamant/agents-towards-production",21459,2848,4,"2025-06-16","agent-framework","?",18,12,14,
  "Code-first tutorials for production-grade agents. Strong content reference."),
 ("pydantic/pydantic-ai",19953,2716,884,"2024-06-21","agent-framework","?",23,16,12,
  "Typed Python agent framework covering every model behind one interface."),
 ("RightNow-AI/openfang",18183,2292,120,"2026-02-24","agent-framework","?",20,15,13,
  "Open-source agent operating system in Rust."),
 ("eigent-ai/eigent",15286,1825,245,"2025-07-29","agent-framework","?",19,15,13,
  "Open-source Cowork desktop; local alternative to hosted multi-agent desktops."),
 ("microsoft/agent-framework",13532,2323,609,"2025-04-28","agent-framework","?",22,14,11,
  "Microsoft framework for building and deploying agents and multi-agent workflows in Python and .NET."),
 ("aden-hive/hive",11044,5663,1354,"2026-01-12","agent-framework","?",18,14,11,
  "Multi-agent harness for production AI with human-in-the-loop."),
 ("omnigent-ai/omnigent",9962,1563,1360,"2026-06-11","agent-framework","?",20,18,12,
  "Meta-harness: swap Claude Code / Codex / Cursor / Pi without rewriting; policies and sandboxing."),
 ("MiroMindAI/MiroThinker",8399,646,2,"2025-08-07","agent-framework","?",21,15,12,
  "Deep research agent tuned for complex research and prediction benchmarks."),
 ("Upsonic/Upsonic",7955,744,33,"2024-05-26","agent-framework","?",19,15,10,
  "Python framework for autonomous agents with reliability focus."),
 ("strands-agents/harness-sdk",7253,1140,756,"2025-05-14","agent-framework","?",21,16,11,
  "AWS-backed SDK for building an agent harness end to end. Any model, any cloud."),
 ("open-multi-agent/open-multi-agent",6926,2431,4,"2026-03-31","agent-framework","?",19,16,11,
  "Self-hosted TypeScript runtime with durable approvals and verifiable run records."),
 ("crestalnetwork/intentkit",6511,711,97,"2024-12-09","agent-framework","?",17,13,10,
  "Self-hosted cloud agent cluster managing a collaborative agent team."),
 ("microsoft/agent-governance-toolkit",6265,1115,191,"2026-03-02","agent-framework","?",20,14,13,
  "Policy enforcement, zero-trust identity, sandboxing; covers the OWASP Agentic Top 10."),
 ("rllm-org/rllm",5824,617,164,"2025-01-26","agent-framework","?",20,11,10,
  "Reinforcement learning for LLMs and agents."),
 ("agentscope-ai/agentscope-java",5619,1367,880,"2025-09-23","agent-framework","?",18,13,9,
  "Alibaba Java framework for distributed long-running agents."),
 ("iflytek/skillhub",5110,836,44,"2026-03-11","agent-framework","?",19,18,12,
  "Self-hosted enterprise agent-skill registry with versioning, RBAC and audit logs."),
 ("didilili/ai-agents-from-zero",4646,642,56,"2026-01-29","agent-framework","?",16,12,14,
  "Chinese-language systematic agent curriculum. Content and SEO reference for ATK's Chinese channels."),
 ("TencentCloudADP/youtu-agent",4611,481,75,"2025-08-21","agent-framework","?",19,15,11,
  "Tencent agent framework tuned to deliver with open-source models."),
 ("kungfu-systems/kungfu",4513,1288,92,"2017-11-15","agent-framework","?",17,14,10,
  "Keeps the same unit of work moving across Codex, Claude, OpenCode and custom surfaces."),
]

# ── MCP ecosystem ──────────────────────────────────────────────────────────
MCP = [
 ("n8n-io/n8n",204366,60686,1157,"2019-06-22","mcp","?",23,14,12,
  "Fair-code workflow automation with native AI and 400+ integrations; MCP client and server."),
 ("google-gemini/gemini-cli",107001,14583,843,"2025-04-17","mcp","?",22,13,12,
  "Google's open-source terminal agent. MCP client and server."),
 ("modelcontextprotocol/servers",90341,11632,524,"2024-11-19","mcp","Apache-2.0+MIT",22,12,11,
  "The reference collection of MCP servers. Contribute upstream, never fork."),
 ("koala73/worldmonitor",86368,13104,320,"2026-01-08","mcp","?",18,13,15,
  "Real-time global intelligence dashboard. Exceptional visual content asset."),
 ("D4Vinci/Scrapling",81075,8189,6,"2024-10-13","mcp","?",22,16,12,
  "Adaptive web-scraping framework with an MCP server. Only 6 open issues at 81k stars."),
 ("upstash/context7",62049,2995,66,"2025-03-26","mcp","MIT",23,13,12,
  "Up-to-date code documentation for LLMs and AI editors. Token-reducing by design."),
 ("ChromeDevTools/chrome-devtools-mcp",52036,3658,103,"2025-09-11","mcp","Apache-2.0",22,13,13,
  "Chrome DevTools exposed to coding agents. Google-run; conform, do not fork."),
 ("DeusData/codebase-memory-mcp",43332,3533,581,"2026-02-24","mcp","MIT",21,15,12,
  "Codebase knowledge graph, 158 languages, single static binary, 99% fewer tokens."),
 ("bytedance/UI-TARS-desktop",38995,3944,445,"2025-01-19","mcp","?",21,15,14,
  "ByteDance multimodal agent stack for GUI and computer use. Highly demonstrable."),
 ("github/github-mcp-server",32947,4969,319,"2025-03-04","mcp","MIT",22,12,11,
  "GitHub's official MCP server."),
 ("assafelovic/gpt-researcher",29461,4007,96,"2023-05-12","mcp","?",22,18,13,
  "Autonomous deep-research agent across any LLM provider. Heavy token workload with a provider seam."),
 ("oraios/serena",29377,1991,181,"2025-03-23","mcp","MIT",23,13,12,
  "Semantic retrieval and editing MCP toolkit - an IDE layer for agents."),
 ("activepieces/activepieces",24464,4192,591,"2022-12-03","mcp","?",20,14,11,
  "AI workflow automation with ~400 MCP servers."),
 ("modelcontextprotocol/python-sdk",24305,3925,418,"2024-09-24","mcp","?",22,14,10,
  "Official Python SDK for MCP."),
 ("pascalorg/editor",23938,2969,22,"2025-10-16","mcp","MIT",19,13,14,
  "3D architectural editor with CLI and MCP tools. Very strong visual content."),
 ("mksglu/context-mode",23003,1659,244,"2026-02-23","mcp","Elastic-2.0",21,17,12,
  "Context-window optimisation, tool-output sandboxing and routing enforcement across 17 platforms."),
 ("czlonkowski/n8n-mcp",22886,3642,67,"2025-06-07","mcp","MIT",20,14,11,
  "MCP server that builds n8n workflows for coding agents."),
 ("1Panel-dev/MaxKB",22799,3148,22,"2023-09-14","mcp","?",19,14,10,
  "Enterprise agent platform, Chinese-market strong."),
 ("modelscope/FunASR",20344,2030,33,"2022-11-24","mcp","?",21,13,12,
  "Alibaba speech-recognition toolkit with OpenAI-compatible and MCP serving."),
 ("Evil0ctal/Douyin_TikTok_Download_API",20125,2788,0,"2021-11-07","mcp","?",18,13,12,
  "Douyin/TikTok scraper and API with MCP. ToS exposure; relevant to ATK Chinese-language content."),
 ("microsoft/mcp-for-beginners",17217,5600,9,"2025-04-04","mcp","?",17,11,13,
  "Microsoft MCP curriculum across six languages. Strong tutorial reference."),
 ("triggerdotdev/trigger.dev",16283,1455,342,"2022-11-30","mcp","?",20,15,11,
  "Durable agent and workflow execution with MCP server."),
 ("modelcontextprotocol/registry",7248,988,166,"2025-02-05","mcp","Apache-2.0+MIT",17,14,9,
  "Community MCP registry. ATK should publish into it."),
 ("mobile-next/mobile-mcp",6693,584,43,"2025-03-28","mcp","Apache-2.0",19,12,13,
  "MCP server for iOS/Android automation on emulators and real devices."),
 ("getsentry/XcodeBuildMCP",6384,319,24,"2025-03-09","mcp","MIT",19,11,10,
  "MCP server and CLI for iOS/macOS project work."),
 ("zcaceres/markdownify-mcp",2990,253,29,"2024-12-18","mcp","MIT",18,14,11,
  "Converts almost anything to Markdown over MCP. Useful preprocessing for token-heavy pipelines."),
 ("brightdata/brightdata-mcp",2641,327,40,"2025-04-15","mcp","MIT",18,14,11,
  "All-in-one public web access over MCP. Commercial vendor with paid quotas."),
]


# ── Routing / gateways (top-up to meet the 20-per-category benchmark floor) ──
ROUTING = [
 ("NadirRouter/NadirClaw",651,76,0,"2026-02-11","routing","?",20,19,13,
  "Prompt-complexity router: cheap/local models for simple prompts, premium for complex. Drop-in OpenAI-compatible proxy claiming 40-70% cost savings. Self-hosted."),
 ("Nya-Foundation/NyaProxy",984,17,0,"2025-04-13","routing","?",18,16,10,
  "Central manager for API access across OpenAI, Gemini and Anthropic with load balancing and rate limiting. Zero open issues."),
 ("xing61/zzz-api",986,82,1,"2023-04-12","routing","?",15,14,11,
  "Chinese-market enterprise API proxy for OpenAI, Claude and Gemini without foreign payment cards."),
 ("ENTERPILOT/GoModel",1155,100,72,"2025-12-05","routing","MIT",20,20,11,
  "Go AI gateway with unified OpenAI- and Anthropic-compatible API, routing, failover and cost tracking."),
 ("Fast-Editor/Lynkr",550,61,5,"2025-12-03","routing","Apache-2.0",16,17,9,
  "CLI HTTP proxy for coding-agent traffic with prompt caching and multi-provider support."),
 ("lidge-jun/opencodex",14724,1107,158,"2026-06-18","routing","?",21,18,13,
  "Universal provider proxy letting Codex CLI/App/SDK and Claude Code run on any model."),
 ("liaohch3/claude-tap",3199,278,34,"2026-02-15","routing","?",21,19,14,
  "Intercepts and inspects coding-agent API traffic across 9 agents in a local trace viewer. The observability piece ATK's routing story is missing."),
 ("romgX/openrelay",2303,321,0,"2026-03-07","routing","?",17,8,12,
  "Hundreds of free AI model quotas, one-click local access. Strategically competitive with paid routing."),
 ("kittors/CliRelay",1003,120,9,"2026-02-27","routing","?",19,18,11,
  "Self-hosted gateway for coding CLIs with multi-tenant console, request logs and spend quotas."),
 ("toby-bridges/api-relay-audit",836,80,26,"2026-03-30","routing","?",21,19,14,
  "Security audit for AI API relays and LLM proxies: prompt injection, model substitution, tool-call rewriting, SSE anomalies, error leakage."),
 ("askalf/dario",532,65,8,"2026-04-08","routing","?",18,9,13,
  "Routes subscription plans into API-shaped endpoints at subscription pricing. Directly displaces per-token billing."),
 ("mozilla-ai/otari",463,52,182,"2026-04-02","routing","?",19,18,11,
  "Mozilla self-hosted OpenAI-compatible gateway for 40+ providers with virtual keys, budgets and usage tracking."),
 ("caidaoli/ccLoad",413,72,2,"2025-09-08","routing","?",19,18,11,
  "Go gateway with smart routing, auto failover, exponential cooldown and soft-error detection."),
 ("starbaser/ccproxy",347,31,9,"2025-07-29","routing","?",18,18,12,
  "Hook any Claude Code request or response and apply custom model-routing logic."),
 ("thushan/olla",299,44,33,"2025-05-23","routing","?",18,16,10,
  "Lightweight Go proxy and load balancer across local and remote inference backends."),
 ("ferro-labs/ai-gateway",256,35,68,"2026-02-25","routing","?",19,18,11,
  "Go-native gateway for 30+ LLMs with caching, guardrails, A/B testing and cost controls."),
 ("RelayPlane/proxy",202,33,5,"2026-02-03","routing","MIT",19,19,13,
  "Local-first proxy that meters what every agent run costs and kills runaways before they drain a budget. MIT."),
]


# ── Adoption records ───────────────────────────────────────────────────────
# A material earns an entry here only after someone installed it, ran it and
# wrote down what happened. Keyed by the material id build_materials.py derives
# from the repo name. An id here that matches no material is a build error, not
# a silent no-op — see the assertion in build_materials.py.
#
# `verified_on` / `evidence` are claims about work actually done in this repo.
# Do not add a record for a tool that has not been run.
ADOPTION = {
 "headroom": {
   "problem_solved": "An agent that reads a large log, file or tool output pays for every token "
                     "of it, and the one line that answers the question is a small fraction of "
                     "that. headroom compresses the payload locally before it is sent.",
   "entry_point": "integrations/headroom-atk/README.md",
   "version_verified": "0.37.0",
   "license": "Apache-2.0",
   "install": 'pip install "headroom-ai[proxy]"',
   "example": "python3 integrations/headroom-atk/make_log.py > deploy.log && "
              "python3 integrations/headroom-atk/local_check.py",
   "io": "in: an OpenAI-compatible /v1/chat/completions request on localhost. "
         "out: the same request, prompt compressed, forwarded to the upstream you name; "
         "the upstream's response is returned unchanged.",
   "atk_config": "Two values, no code: run `headroom proxy --port 8787 --no-http2`, then send "
                 "requests to it with header "
                 "`x-headroom-base-url: https://api.aitokenking.com.tw/api` (no /v1 suffix) and "
                 "`Authorization: Bearer $ATK_API_KEY`.",
   "alternative_provider": "The same header names any OpenAI-compatible upstream per request "
                           "(another provider, a gateway, a local server). Drop the header and "
                           "headroom routes by its own provider resolution. Nothing else changes, "
                           "so ATK is replaceable here without touching code.",
   "cost_and_permissions": "headroom itself is free and runs locally; no content leaves the "
                           "machine to compress it. Model calls through it cost whatever the "
                           "upstream charges. Needs no credential of its own — it forwards the "
                           "Authorization header it is given. Binds to 127.0.0.1 by default and "
                           "refuses client-named upstreams that resolve to private/loopback space.",
   "verified_on": "2026-09-18",
   "evidence": [
     "integrations/headroom-atk/evidence/ab_needle.json",
     "integrations/headroom-atk/evidence/ab_summary.json",
     "integrations/headroom-atk/evidence/local_check.txt",
   ],
   "measured": "Live against ATK: 40,589 -> 25,525 prompt tokens (37.1% fewer) on a needle "
               "question, same answer both paths, counts from ATK's own usage field. Offline and "
               "reproducible without a key: 111,357 -> 94,578 characters reaching the upstream "
               "(15.1% fewer), needle intact. Different metrics on different bytes; both recorded.",
   "does_not_apply_to": "Measured limit, not a guess: headroom saves by factoring text repeated "
                        "across lines. The same 1,200 records as JSON lines compress by exactly "
                        "0.0% (byte-for-byte pass-through); flattened to plain text they compress "
                        "27.3%. If your agent reads JSON-structured logs this tool does nothing "
                        "for you. It also does not apply to short prompts, to payloads where "
                        "every token is load-bearing, or where you need a byte-exact record of "
                        "what the model saw. Check yours first: "
                        "`python3 local_check.py --log YOUR.log --needle 'the line that matters'` "
                        "(exit 3 means no benefit).",
   "known_failure": "On a 'summarise in five bullets' prompt the FATAL line was missed by BOTH "
                    "the compressed and the direct path — the wrong instrument for finding one "
                    "unique event, not a compression fault. Recorded because it is the result.",
   "maintenance": "Active upstream at snapshot 2026-09-15: ~8,764 stars/month since 2026-01-07, "
                  "643 open issues. Version pinned in this record is the one actually run.",
   # Attribution travels with the machine-readable record, not only with the
   # prose page, so a client that reads the index alone still carries it.
   # `upstream_attribution` is required by the tool's own Apache-2.0 licence.
   # `verified_by` is a credit we ask for, never a condition of use.
   "upstream_attribution": "headroom, (c) headroomlabs-ai, Apache-2.0, "
                           "https://github.com/headroomlabs-ai/headroom. No headroom code is "
                           "redistributed here; install it from PyPI.",
   "verified_by": "AI Token King (ATK), https://aitokenking.com.tw — measurement run through "
                  "https://api.aitokenking.com.tw/api/v1. ATK is not required to use this tool; "
                  "the same configuration names any OpenAI-compatible upstream.",
   "status": "verified_working",
 },
}

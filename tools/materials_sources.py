"""Non-repository materials for Benchmark Run R2-002 (2026-09-15).

Covers the four DISCOVERY_ENGINE.md source classes that R2-001 left unmined:
  class 3 primary engineering · class 4 research/model hubs
  class 5 community signal    · class 6 curated discovery indexes

VERIFICATION HONESTY
--------------------
`verified` marks how the item was obtained:
  "primary"  - the primary page/abstract itself was retrieved
  "search"   - obtained from a search-engine summary; the underlying claim is
               NOT independently confirmed and must not be quoted as fact by ATK
Per DISCOVERY_ENGINE.md "separate verified facts from hypotheses".

Columns: id, title, url, source_type, category, published, verified,
         tu(25), momentum(20), atk(20), content(15), exp(10), cred(10), note
"""

SOURCES = [
 # ── class 3: primary engineering ─────────────────────────────────────────
 ("cf-ai-gateway","Cloudflare AI Gateway","https://developers.cloudflare.com/ai-gateway/",
  "engineering_docs","routing","2026-05","search",
  23,18,20,14,9,10,
  "Managed AI routing and observability proxy, FREE on every Cloudflare plan, with analytics, "
  "caching and rate limiting at no charge. Routes to 24 native providers; a universal REST "
  "endpoint added May 2026 speaks OpenAI and Anthropic request formats. THE most significant "
  "competitive fact in this run: a platform company with enormous distribution is giving away "
  "the layer ATK sells."),
 ("cf-agents-week","Cloudflare Agents Week 2026 (20+ launches)",
  "https://shattered.io/cloudflare-agents-week-ai-wallet-2026/","news","routing","2026-08","search",
  21,19,19,14,6,8,
  "Cloudflare shipped 20+ agent products in two weeks of August 2026: Cloudflare Wallet giving an "
  "agent verifiable identity and spending power, an Identity-Aware AI Gateway, a persistent Agent "
  "Memory service, and DeepSeek models with ~1M-token context on Workers AI."),
 ("cf-openai-agent-cloud","Cloudflare and OpenAI launch Agent Cloud for enterprises",
  "https://www.forbes.com/sites/janakirammsv/2026/04/16/cloudflare-and-openai-launch-agent-cloud-for-enterprises/",
  "news","routing","2026-04","search",
  20,17,18,13,4,8,
  "Agent Cloud integrates OpenAI GPT-5.4 and Codex alongside open-source models through a unified "
  "catalogue built on Cloudflare's Replicate acquisition."),
 ("vercel-ai-gateway","Vercel AI Gateway","https://vercel.com/ai-gateway",
  "engineering_docs","routing","2026","search",
  21,16,19,12,8,10,
  "Hundreds of models across ~45 providers behind one endpoint and one key, BYOK with NO MARKUP. "
  "No native guardrails and no semantic cache - the two gaps a differentiated router could fill."),
 ("anthropic-code-exec-mcp","Code execution with MCP: building more efficient AI agents",
  "https://www.anthropic.com/engineering/code-execution-with-mcp",
  "engineering_blog","token-optimization","2025-11-04","primary",
  24,14,19,14,8,10,
  "Loading every tool definition upfront and passing intermediate results through context is the "
  "dominant hidden token cost in MCP-heavy agents. Having the agent write code to call tools "
  "instead cuts both. The single most actionable primary-source technique found in this run."),
 ("anthropic-context-eng","Effective context engineering for AI agents",
  "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents",
  "engineering_blog","token-optimization","2025-09-29","primary",
  23,13,18,14,7,10,
  "Anthropic's reference treatment of context as a managed budget rather than a container."),
 ("anthropic-harness-design","Harness design for long-running application development",
  "https://www.anthropic.com/engineering/harness-design-long-running-apps",
  "engineering_blog","agent-framework","2026-03-24","primary",
  23,16,17,13,6,10,
  "Primary-source harness design guidance for long-running agents."),
 ("anthropic-compaction-cookbook","Context engineering: memory, compaction and tool clearing",
  "https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools",
  "engineering_docs","token-optimization","2026-03-20","primary",
  22,16,18,13,9,10,
  "Runnable cookbook covering memory, compaction and tool clearing - directly testable."),
 ("anthropic-writing-tools","Writing effective tools for AI agents",
  "https://www.anthropic.com/engineering/writing-tools-for-agents",
  "engineering_blog","mcp","2025-09-11","primary",
  22,12,15,13,7,10,
  "How tool design itself drives token consumption and agent reliability."),
 ("deepseek-harness-launch","DeepSeek open-sources its agent harness under MIT",
  "https://thenewstack.io/deepseek-harness-open-source-plugins/","news","agent-framework","2026-08-13","search",
  21,20,16,14,7,9,
  "Model adapter, tool registry and agent loop are all swappable plugins; four runtime modes. "
  "Reportedly passed 33,000 stars within hours of release. The plugin seam is where an ATK "
  "provider would attach."),

 # ── class 4: research / model hubs ───────────────────────────────────────
 ("supra-router-51m","Supra-Router-51M (Hugging Face)","https://huggingface.co/models?search=Supra-Router",
  "model_hub","routing","2026","search",
  22,17,20,13,8,8,
  "A 51M-parameter router model for selecting the optimal LLM path in a multi-model setup. A "
  "router small enough to run in-process is the cheapest possible form of cost routing."),
 ("arxiv-cluster-route-escalate","Cluster, Route, Escalate: Cascaded Framework for Cost-Aware LLM Serving",
  "https://arxiv.org/abs/2606.27457","paper","routing","2026-06","search",
  23,16,19,13,5,9,
  "Two-stage cascade: cluster queries to the cheapest adequate model, then escalate on a quality "
  "estimate. Reported to retain 97-99% of the strongest model's accuracy. This is the academic "
  "form of exactly what ATK routing claims to do."),
 ("arxiv-route-receipts","Model Routing as a Trust Problem: Route Receipts for Adaptive AI Systems",
  "https://arxiv.org/pdf/2605.01710","paper","routing","2026-05","search",
  22,15,20,14,4,9,
  "Frames routing as a TRUST problem and proposes verifiable route receipts. Independent academic "
  "support for the measurement-and-trust position, which is the one differentiator price "
  "competition cannot erase."),
 ("arxiv-escalation-worth-it","Is Escalation Worth It? A Decision-Theoretic Characterization of LLM Cascades",
  "https://arxiv.org/pdf/2605.06350","paper","routing","2026-05","search",
  21,14,17,11,4,9,
  "When escalating to a stronger model actually pays, using confidence, token probabilities and "
  "self-consistency signals."),
 ("arxiv-routing-cascades-choice","Routing, Cascades, and User Choice for LLMs",
  "https://arxiv.org/pdf/2602.09902","paper","routing","2026-02","search",
  20,13,17,11,4,9,
  "Survey-style treatment of ensemble, cascade and direct-routing strategies."),
 ("arxiv-graph-context-compression","Training-free LLM Context Compression with Hybrid Graph Priors",
  "https://arxiv.org/pdf/2604.23277","paper","token-optimization","2026-04","search",
  21,14,17,11,5,9,
  "Training-free context compression - no fine-tuning required, so cheap to trial."),
 ("hf-lclm","Latent Context Language Models as long-horizon agent backbones",
  "https://huggingface.co/papers?q=Latent+Context+Language+Models","paper","token-optimization","2026","search",
  21,15,16,11,4,8,
  "Agent skims a compressed long context and adaptively expands only the relevant segments."),

 # ── class 5: community signal ────────────────────────────────────────────
 ("hn-headroom","Show HN: Headroom - reversible context compression (~60% cost reduction)",
  "https://news.ycombinator.com/item?id=46628278","community_signal","token-optimization","2026","search",
  18,18,18,15,8,7,
  "Independent HN validation of the headroom project already in the registry. The framing that "
  "landed: by turn 10 teams pay for 100k+ tokens on every call, and truncation, summarisation and "
  "bigger windows each have a fundamental tradeoff."),
 ("price-gap-100x","~100x price gap between cheapest usable and frontier models",
  "https://www.digitalapplied.com/blog/llm-model-routing-2026-cost-quality-optimization-engineering-guide",
  "community_signal","routing","2026","search",
  20,17,20,15,3,6,
  "DeepSeek V4 around $0.44/M tokens against GPT-5.5-pro at $30/$180. UNVERIFIED pricing from a "
  "secondary source - but if even roughly right, the arbitrage a router captures is ~100x, and "
  "that spread IS the routing business."),
 ("routing-savings-range","Reported routing savings cluster at 40-85%",
  "https://www.ayautomate.com/blog/open-source-llm-orchestration-tools","community_signal","routing","2026","search",
  17,15,18,14,3,5,
  "Multiple secondary sources report 40-85% bill reduction from a tuned routing layer. UNVERIFIED "
  "and self-reported; useful as a hypothesis to test, never as a number to publish."),
 ("yt-claude-code-tutorials","YouTube: Claude Code tutorial demand is enormous",
  "https://developereducators.com/best/claude-code/","video_channel","agent-skill","2026","search",
  14,16,15,15,2,5,
  "The most-watched Claude Code tutorial reportedly sits near 2.37M views (Nick Saraev). Cole "
  "Medin, Fireship and LangChain's channel are the recurring names for production agent content. "
  "Confirms YouTube demand for exactly the tutorials ATK plans to make."),

 # ── class 6: curated discovery indexes ───────────────────────────────────
 ("awesome-llm-token-optimization","awesome-llm-token-optimization",
  "https://github.com/pleasedodisturb/awesome-llm-token-optimization","curated_index","token-optimization","2026","search",
  12,14,16,12,3,6,
  "Curated strategies, tools, papers and resources for cutting LLM token cost. Feed it to the "
  "Trend Scout; do not fork it."),
 ("awesome-routing-llms","Awesome-Routing-LLMs (MilkThink-Lab)",
  "https://github.com/MilkThink-Lab/Awesome-Routing-LLMs","curated_index","routing","2026","search",
  12,13,16,11,3,6,
  "Curated index of the Routing-LLMs research paradigm. Best single input for keeping the routing "
  "literature current."),
 ("agents-radar","agents-radar (automated Hugging Face trending digest)",
  "https://github.com/duanyytop/agents-radar","curated_index","agent-framework","2026","search",
  13,16,15,10,7,5,
  "Bot-maintained repos that post Hugging Face trending models as dated GitHub issues. An "
  "already-automated feed the Discovery Engine can consume directly instead of scraping HF."),
]

# Discovery Engine

## Objective
Continuously answer: **What useful AI technology should ATK talk about, test, teach, adapt or integrate next?**

## Source classes
1. Primary code: GitHub/GitLab repositories, releases, issues, changelogs.
2. Protocol/registry: MCP Registry, protocol specifications, A2A ecosystems.
3. Model/platform engineering: OpenAI, Anthropic, Google, Microsoft, AWS, Cloudflare, Vercel, ByteDance/BytePlus, Alibaba/Qwen, Tencent, Baidu, DeepSeek and other relevant primary engineering sources.
4. Research/model hubs: Hugging Face, papers and official demos.
5. Community signal: Hacker News, Reddit technical communities, X technical accounts, YouTube developer channels.
6. Curated discovery: awesome lists and skill registries. These are discovery inputs, not automatic fork targets.

## Required discovery categories
mcp, a2a, agent-framework, agent-skill, ai-sdk, routing, model-gateway, context, memory, tool-use, browser-agent, coding-agent, multimodal, workflow, eval, observability, identity, payment, token-optimization, cost-optimization, rag, computer-use, multi-agent, security.

## Pipeline
Collect → Normalize → Deduplicate → Verify source → Extract technical value → Score → Assign actions → Material Card → Content/Experiment/Integration lane.

## Failure isolation
A failure in one lane must not stop other lanes.
- Cannot read full repository: keep signal as pending verification; do not fabricate.
- License unclear: block redistribution only.
- Security scan unavailable: block executable integration only.
- GitHub write permission unavailable: generate report locally/in branch; discovery continues.
- API/rate limit: checkpoint progress and resume later.
- One source unavailable: continue other sources.

## Output requirement
Every accepted item must answer:
- What is it?
- What problem does it solve?
- Why now?
- What is technically interesting?
- Who benefits?
- ATK routing/token/MCP/A2A relevance?
- What can we test?
- What can we publish?
- What are the rights/usage constraints?

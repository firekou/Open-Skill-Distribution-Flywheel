# ATK Technical Growth System — Execution Plan

**Status:** Approved direction for Claude execution  
**Date:** 2026-09-15  
**North Star:** Build a high-output technical intelligence and verification system that continuously discovers real Agent demand, verifies useful techniques, turns evidence into reusable technical assets, distributes them through ATK-owned channels, and feeds response back into the next discovery cycle.

## 1. Strategic correction
ATK is not building a content farm and is not primarily building a fork farm. ATK is building a **technical growth system for the Agent economy**.

The flywheel is:
**Research → Proof → Content → Distribution → GitHub → ATK → Usage Signal → Next Research**

We serve both human developers and machine-level Agent needs: lower token cost, better context, reliable routing, usable tools, MCP/A2A interoperability, observability, security, identity, memory and repeatable skills.

## 2. Scout, in plain language
A **Scout is an automated technical researcher that goes out every day and finds what is getting hot.**

Instead of a person manually opening GitHub, YouTube, X, Reddit, Hacker News, Hugging Face and engineering blogs one by one, the Scout:
1. searches recent technical material;
2. records observable popularity/growth signals;
3. removes duplicates and noise;
4. brings strong candidates into the ATK registry;
5. explains why each may matter;
6. never treats popularity as proof of technical correctness.

Agent-Reach and last30days-skill may help implement parts of this collection layer. Inspect and test them before treating them as infrastructure.

## 3. Two demand systems
### Human market demand
Views, stars, saves, reposts, comments, clicks, GitHub visits, installs, signups, API activation.

### Agent demand
Repeated tool calls, token spend, context pressure, routing decisions, retries, failure modes, latency, MCP usage, skill invocation, model escalation, cache misses.

ATK's strongest opportunities sit where both intersect.

## 4. Measurement & Trust research program
Measurement & Trust is now a **high-priority strategic hypothesis**. Research why high-attention token/cost tools grow and which trust functions are necessities.

Investigate:
1. Cost visibility: what did this task cost?
2. Attribution: which agent, project, customer, workflow and model created the cost?
3. Routing transparency: which model served the request and why?
4. Quality evidence: did the cheaper route still succeed?
5. Budget control: can runaway spend be stopped?
6. Auditability: can a route/cost decision be reproduced?
7. Integrity: was the requested model used; were prompts/tool calls modified?
8. Policy: which agent may spend how much and call which tools/models?
9. Billing: can usage become reliable per-team/per-client billing?
10. Trust receipt: can an important run leave a machine-readable receipt?

Do not infer users from stars. For high-growth projects investigate issues, releases, contributors, forks, discussions, installation/use evidence, community references and exact pain language.

## 5. ATK Verify evidence ladder
**REPORTED** → another source says it.  
**OBSERVED** → ATK directly read a primary source or measured an observable fact.  
**TESTED** → ATK executed the technique under a documented test.  
**VERIFIED** → the test passed predefined acceptance criteria and evidence was saved.  
**REPRODUCED** → the result was independently repeated within defined tolerance.

Every benchmark evidence package records environment, versions/commit SHA, task dataset, baseline, treatment, repetitions, token accounting, latency, cost, success/quality criteria, raw outputs, limitations and reproduction command.

## 6. Agent 真正燒 Token 的四個地方
This becomes the first recurring editorial + experiment series.

### Waste 1: Tool definitions and MCP schema overhead
Agents may load many tool definitions before using them. Measure token overhead at 5/20/50/100 tools and test deferred discovery/code execution.

### Waste 2: Tool results and intermediate data
Logs, transcripts, JSON, search results and files can pass through model context when only a small answer is needed. Measure filtering/compression/code-execution reductions and quality impact.

### Waste 3: Wrong-model routing
Simple tasks may hit expensive frontier models; hard tasks may hit cheap models then retry/escalate. Measure cheapest model meeting the quality threshold and the cost of bad routing.

### Waste 4: Context accumulation, memory and repeated information
Long sessions repeatedly carry old conversation, duplicated files, stale results and unnecessary memory. Test compaction, caching, retrieval-on-demand and clearing.

Every theme must output: research note, reproducible test, raw evidence, ATK Verify result, GitHub asset, article, social variants and optional Skill/Adapter/Router integration.

## 7. Token Efficiency Lab 001 — How Agents Waste Tokens
Goal: produce the first **ATK Token Efficiency Benchmark** based on ATK measurements.

Compare where applicable:
- baseline workflow
- MCP/code-execution reduction
- tool-result filtering/compression
- context compression/compaction
- routing strategy
- selected tools such as Headroom/RTK after review

Workloads:
- code/repository analysis
- long-document extraction
- multi-tool research
- MCP-heavy workflow
- repeated multi-turn agent task

Target **100 completed runs across predefined conditions**. Do not create meaningless repetitions just to hit 100.

Measure every run: input/output/total tokens, tool overhead, model, model calls, tool calls, retries, escalations, latency, cost, task success, quality and failure reason.

No savings claim becomes VERIFIED unless treatment meets a predefined success/quality floor.

## 8. ATK Technical Magazine
ATK behaves like a high-output technical magazine backed by evidence.

Recurring desks:
MCP; A2A; Agent Skills; Agent Frameworks; Token Efficiency; Routing; Context/Memory; Security; Identity/Payments; Observability/Measurement; Coding/Computer-use Agents.

One material can become a **Content Package**:
- technical research card
- ATK Verify status
- long article
- GitHub note/demo
- 3–5 Threads/X posts
- LinkedIn angle
- short-video brief
- benchmark/diagram where justified
- integration hypothesis

High output comes from reuse of verified research, not lower evidence quality.

## 9. Popularity as a marketing expansion factor
Scout should prioritise already-validated attention.

Example filters:
- published/meaningfully updated within 30 days
- YouTube >10,000 views in 30 days, with growth velocity
- unusually fast GitHub star/fork growth
- repeated references across independent communities
- strong discussion/save/repost signals
- primary-source launch/release momentum

Popularity means **investigate first**, not copy and not technically verified.

Store published_at, observed_at, views, stars, forks, growth_velocity, cross_source_mentions, source_quality and evidence_state.

## 10. Social accounts become demand sensors
Every distributed package receives topic/category and tracking IDs.

Track impressions/views, engagement, saves, shares, comments, outbound clicks, GitHub visits, benchmark/repo actions, ATK visits and attributable API/registration conversion.

Aggregate by category over rolling 7/30/90 days. Do not use raw views alone. Build Demand Signal from attention + high-intent actions + technical usage.

If A2A repeatedly produces stronger saves/GitHub follow-through than MCP, increase A2A discovery. If Token Efficiency gets fewer views but more benchmark usage/API activation, it can rank higher commercially.

The social network is a market sensor that tells the next Scout what to search more deeply.

## 11. Three ATK insertion levels
### Level 0 — Pure Value
ATK branding/source attribution may be present, but no forced product pitch. Goal: usefulness, trust and reach.

### Level 1 — Contextual ATK
Naturally explain where the technique touches ATK: token reduction before routing, model choice, MCP cost, audit, multi-model access.

### Level 2 — ATK Native
ATK actually implements: Adapter, Benchmark, Skill, Router integration, Verify report or machine-readable receipt.

Preserve upstream attribution and never disguise third-party work as ATK's own.

## 12. Top 10 / 10 / 10 operating model
From the registry select, overlap allowed:
- **10 Worth Talking About** → Content Packages.
- **10 Worth Running** → ATK Verify experiments.
- **10 Worth Integrating** → integration briefs, then adapters/skills after review.

The registry may keep growing, but execution capacity goes to the Top 30.

## 13. S3–S6 execution
### S3 — Verify Top 30
1. Freeze current 188-material snapshot.
2. Select 10 Talk / 10 Run / 10 Integrate.
3. Replace search-summary claims with primary evidence.
4. Investigate why high-growth items grew.
5. Assign ATK Verify states.
6. Produce reports/TOP30_R3.md.

Exit: every Top 30 item has a primary-source dossier or explicit unverified status.

### S4 — Token Efficiency Lab 001
1. Lock methodology.
2. Build workload and baseline.
3. Security-review executable candidates.
4. Run 100 completed executions across predefined conditions.
5. Save raw results.
6. Analyse savings only when quality floor passes.
7. Independently repeat key result.
8. Publish Benchmark 001.

Exit: at least one VERIFIED result; REPRODUCED preferred.

### S5 — Research-to-Distribution Factory
1. Define Content Package schema.
2. Convert Top 10 Talk materials.
3. Generate channel-specific drafts from one evidence package.
4. Preserve source/evidence labels.
5. Attach category/tracking IDs.
6. Prepare editorial schedule.

Exit: ten complete content packages.

### S6 — Demand Sensor & Feedback
1. Collect 7/30/90-day performance.
2. Aggregate by category.
3. Separate attention from high-intent actions.
4. Add Agent Demand signals where ATK telemetry appropriately permits.
5. Feed results into discovery priority.
6. Produce monthly ATK_TECHNICAL_DEMAND_REPORT.

Exit: next Scout cycle is driven partly by observed human + Agent demand.

## 14. Claude execution rules
Claude must distinguish facts, reports, tests and inference; never convert stars/views into users; never publish vendor savings as ATK-verified; preserve attribution; isolate discovery failures from integration failures; avoid automatic forking; review executable third-party code; record benchmark configurations; make outputs reproducible; and report when a required measurement cannot be obtained.

Optimise for **verified reusable assets and measurable distribution learning**, not document count.

## 15. Immediate Action Items
1. Create reports/TOP30_R3.md.
2. Deep-review demand behind fastest-growing token/cost projects.
3. Evaluate last30days-skill and Agent-Reach as Scout components.
4. Build Token Efficiency Lab 001 methodology before execution.
5. Define ATK Verify metadata.
6. Define Content Package schema.
7. Define Demand Sensor schema.
8. After S3 review, begin S4. Do not wait for 500 materials.

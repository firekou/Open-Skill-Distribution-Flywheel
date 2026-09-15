# Discovery Pipeline Runbook

## Phase 0 — Permission preflight
Check which external sources and repository scopes the executor can actually read. Record limitations. Do not interpret a missing permission as a negative finding about a candidate.

## Phase 1 — Mine
Search each target domain. Aim for breadth across MCP, A2A, frameworks, skills, routing and token optimization first, then the wider category list.

## Phase 2 — Normalize
Canonical URL, owner, project, category, source type, dates and observable signals.

## Phase 3 — Deduplicate
Merge repeated mentions into one material record while preserving all source signals.

## Phase 4 — Understand
Read primary documentation/code when accessible. Separate verified facts from hypotheses.

## Phase 5 — Score
Apply TREND_SCORING.md. License does not veto this score.

## Phase 6 — Route
Choose any combination of research/content/tutorial/experiment/link/adapter/fork/deep integration.

## Phase 7 — Gate only what needs gating
Research/content: provenance and copyright discipline.
Experiment: security/sandbox constraints as needed.
Adapter: interface and license boundary review.
Fork/redistribution: full LICENSE_REVIEW + FORK_POLICY.
Deep integration: full technical/security/commercial review.

## Phase 8 — Produce
Top material cards, content briefs, experiment briefs and integration candidates.

## First benchmark run
Collect at least 20 candidates in each:
MCP, A2A, Agent Framework, Agent Skill, Routing, Token Optimization.
Target = 120 raw candidates before deduplication.

Return four ranked lists:
1. What should ATK talk about?
2. What should ATK test?
3. What is suitable for ATK integration?
4. What is suitable for fork/redistribution?

Do not automatically fork anything during the benchmark.

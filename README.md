> **Agent 執行入口：[治理規範](governance/OPERATING_RULES.md)。** 任務、已決策事項與自動化狀態依該入口讀取。GOV-01 已授權有限自動治理導入；目前只有規範與離線檢查，尚未啟動背景 executor/reviewer。歷史 Lab／全面暫停治理文字不作當前排程。

# ATK Token Intelligence Magazine / Open Skill Distribution Flywheel

> **Current goal:** A practical collection of verified tools and skills that external agents can discover, understand and adopt to solve real tasks, with transparent and optional ATK integration.
>
> We continuously discover useful tools, verify their practical use, prepare usable assets, and distribute them through accessible entry points. External discovery and adoption remain goals to prove, not outcomes implied by publishing this repository.

**Try it:** [Aider + any OpenAI-compatible endpoint, first run](integrations/aider-atk/delivery/README.md). Rehearsed offline from a clean clone; no real model or outside user has completed it yet.

以下雜誌、Lab 與組織文件保留為歷史與參考；目前任務以頁首最新目標及 reviews/STATUS.md 為準。

## Start here

| Document | Purpose |
|---|---|
| [`EXECUTION_DOCTRINE.md`](./EXECUTION_DOCTRINE.md) | Governing principle: 大膽假設，小心求證; Hypothesis → Evidence → Decision → Execution |
| [`MAGAZINE_MASTER_PLAN.md`](./MAGAZINE_MASTER_PLAN.md) | Full ATK Token Intelligence Magazine structure |
| [`MAGAZINE_DESK_SPEC.md`](./MAGAZINE_DESK_SPEC.md) | Ten permanent technical desks and their scope |
| [`ATK_TECHNICAL_GROWTH_PLAN.md`](./ATK_TECHNICAL_GROWTH_PLAN.md) | Research-to-distribution and technical growth plan |
| [`ATK_VERIFY_STANDARD.md`](./ATK_VERIFY_STANDARD.md) | REPORTED → OBSERVED → TESTED → VERIFIED → REPRODUCED |
| [`DEMAND_SENSOR_SPEC.md`](./DEMAND_SENSOR_SPEC.md) | Human + Agent demand sensing |
| [`organization/ORGANIZATION_V1.md`](./organization/ORGANIZATION_V1.md) | Agent-native magazine organization |
| [`agents/AGENT_SPECS_V1.md`](./agents/AGENT_SPECS_V1.md) | Agent role contracts |
| [`skills/AGENT_SKILL_CONTRACT.md`](./skills/AGENT_SKILL_CONTRACT.md) | Standard skill contract |
| [`workflows/MAGAZINE_PRODUCTION_V1.md`](./workflows/MAGAZINE_PRODUCTION_V1.md) | Magazine production workflow |
| [`CLAUDE_EXECUTION_START.md`](./CLAUDE_EXECUTION_START.md) | Claude execution entrypoint and mandatory review stop |

## Three ledgers

| Ledger | Purpose |
|---|---|
| [`ledgers/HYPOTHESIS_LEDGER.md`](./ledgers/HYPOTHESIS_LEDGER.md) | H001–H010 hypotheses and confidence |
| [`ledgers/EVIDENCE_LEDGER.md`](./ledgers/EVIDENCE_LEDGER.md) | Traceable evidence and verification state |
| [`ledgers/DECISION_LEDGER.md`](./ledgers/DECISION_LEDGER.md) | Decisions linked back to hypotheses and evidence |

## Operating loop

**Signal → Intelligence → Research → Lab → Verify → Benchmark → Magazine → Distribution → Demand → Decision → Engineering → ATK**

Commercial exploration:

**Media → Intelligence → Measurement → Execution**

The repository must not optimize for file count, autonomous activity, forks or article volume. It must optimize for:

**less uncertainty + stronger evidence + better decisions + reusable verified assets + measurable demand + validated product learning.**

## Magazine desks

1. Token Intelligence
2. Agent Intelligence
3. MCP Intelligence
4. A2A Intelligence
5. Routing Intelligence
6. Skill Intelligence
7. Framework Intelligence
8. Context & Memory
9. Trust & Security
10. Agent Economy

## Editorial formats

SIGNAL · EXPLAINED · ATK VERIFY · ATK LAB · TOP PICKS · BENCHMARK · DEEP DIVE · BUILD

## Top 30 operating model

Each cycle produces three overlapping lists:
- 10 Worth Talking About
- 10 Worth Running
- 10 Worth Integrating

Discovery can continue in the background, but execution capacity goes to the highest-value items.

## Current Lab

[`benchmarks/TOKEN_EFFICIENCY_LAB_001.md`](./benchmarks/TOKEN_EFFICIENCY_LAB_001.md)

Research question: **Where do Agents waste tokens, and which interventions reduce total task cost without materially reducing task success?**

The Lab team and GitHub evidence workflow are defined in [`workflows/TOKEN_EFFICIENCY_LAB_001_TEAM.md`](./workflows/TOKEN_EFFICIENCY_LAB_001_TEAM.md).

## Discovery architecture

The R2 discovery-first architecture remains valid and now serves the Magazine Intelligence layer.

| Document | Purpose |
|---|---|
| [`ARCHITECTURE_R2.md`](./ARCHITECTURE_R2.md) | Discovery-first architecture |
| [`DISCOVERY_ENGINE.md`](./DISCOVERY_ENGINE.md) | Technical-material mining engine |
| [`DISCOVERY_PIPELINE.md`](./DISCOVERY_PIPELINE.md) | Discovery runbook |
| [`TREND_SCORING.md`](./TREND_SCORING.md) | Material opportunity scoring |
| [`registry/SOURCE_REGISTRY.json`](./registry/SOURCE_REGISTRY.json) | Signal sources |
| [`registry/MATERIAL_SCHEMA.json`](./registry/MATERIAL_SCHEMA.json) | Material schema |
| [`registry/materials.json`](./registry/materials.json) | Current material registry |

**Critical rule:** License Gate is a redistribution gate, not a discovery gate.

## Existing integration and redistribution framework

These documents remain active for the Engineering / Integration lane:

| Document | Purpose |
|---|---|
| [`ATK_OPEN_SKILL_STRATEGY.md`](./ATK_OPEN_SKILL_STRATEGY.md) | Original open skill strategy |
| [`SKILL_SCORING.md`](./SKILL_SCORING.md) | Skill scoring |
| [`LICENSE_REVIEW.md`](./LICENSE_REVIEW.md) | License review |
| [`FORK_POLICY.md`](./FORK_POLICY.md) | Fork policy |
| [`UPSTREAM_SYNC.md`](./UPSTREAM_SYNC.md) | Upstream sync |
| [`ATK_ROUTING_INTEGRATION.md`](./ATK_ROUTING_INTEGRATION.md) | Routing integration |
| [`CONTENT_DISTRIBUTION.md`](./CONTENT_DISTRIBUTION.md) | Content distribution |
| [`ANALYTICS_METRICS.md`](./ANALYTICS_METRICS.md) | Analytics metrics |

## Research reports

Current evidence base includes R2 discovery runs and the market research report. New Claude execution should continue from current work rather than restarting prior research.

## Governing rule for Claude and all Agents

Every major execution must answer the seven Forward-Motion questions in `EXECUTION_DOCTRINE.md`. If the work cannot show what uncertainty was reduced, what evidence was produced, what decision is now justified, and what the next gate is, it is not considered complete.

## License

MIT for ATK-authored repository material unless otherwise stated. Third-party project licenses remain with their respective authors.

## 外部實證與遞迴改善實驗準則

所有後續實驗依 [共用實驗準則](EXPERIMENT_GUIDELINE.md)、[本專案接合](EXPERIMENT_APPLICATION.md) 與 [實驗工作單](EXPERIMENT_TEMPLATE.md) 規劃與留證。優先縮短有效外部回饋時間；大量探索後獨立確認，再找反例界定局部成功。100／1,000 次為有限批次搜尋規模，不是成功保證或解除既有權限。文件採用不代表自動執行已啟動。

## GPT／Claude 接力與運作方法

依 [共用運作方法](AGENT_OPERATING_METHOD.md)、[專案接合](AGENT_METHOD_APPLICATION.md)、[交接手冊](AGENT_HANDOFF_RUNBOOK.md) 與 [工作模板](AGENT_TASK_TEMPLATE.md) 續作；雲端接線依 [導入驗收包](AGENT_CLOUD_ADOPTION_PLAN.md)。版本 AGENT-HANDOFF-001 / 1.0.0。此次只採用文件，不代表 runtime 已啟用，原治理入口及授權維持。

> **負責人最新目標補充：[外部 Agent 發現、採用與解題驗收](reviews/ATK_AGENT_DISCOVERY_AND_ADOPTION.md)。** PR #4 的小交付結案不代表整體目標達成。下一個工作包是一個真實工具的可發現入口、可跟做接入與任務驗證，回覆於 `reviews/ATK_AGENT_DISCOVERY_EXECUTOR_RESPONSE.md`；下方舊「下一步／停止」只適用原交付，不得據此停止整體主線。

> **2026-09-18 目標與排程校正，優先閱讀：[ATK 主線校正](reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md)。**
> 現行主線為有用 AI 工具／skill 的技術分享、可運行資產、透明可選的 ATK Router 接入與實際採用。Benchmark 全面修復、Freeze 與新治理框架 PoC 暫停，不再作為上述交付的前置條件。歷史缺陷仍未關閉，暫停不代表通過。
> 下一工作包：從既有清單挑三個候選，先完成一個最小接入與分享包；Claude 回覆於 `reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md`。下文與此衝突的工作順序與「下一步」均為歷史，不得據此自動續跑。

# ATK Token Intelligence Magazine / Open Skill Distribution Flywheel

> **Current goal:** A practical collection of verified tools and skills that external agents can discover, understand and adopt to solve real tasks, with transparent and optional ATK integration.
>
> We continuously discover useful tools, verify their practical use, prepare usable assets, and distribute them through accessible entry points. External discovery and adoption remain goals to prove, not outcomes implied by publishing this repository.

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

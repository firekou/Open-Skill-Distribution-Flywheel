> **規劃、執行與 review 的共同前置規則：[ATK 目標對齊與防偏航 skill](.claude/skills/atk-goal-alignment/SKILL.md)。** 每轮先確認工作如何服務最新用戶目標，再決定必要測試與停止點。小修正沿用既有目標摘要，不另開治理或批准流程。

> **2026-09-18 目標與排程校正，優先閱讀：[ATK 主線校正](reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md)。**
> 現行主線為有用 AI 工具／skill 的技術分享、可運行資產、透明可選的 ATK Router 接入與實際採用。Benchmark 全面修復、Freeze 與新治理框架 PoC 暫停，不再作為上述交付的前置條件。歷史缺陷仍未關閉，暫停不代表通過。
> 下一工作包：從既有清單挑三個候選，先完成一個最小接入與分享包；Claude 回覆於 `reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md`。下文與此衝突的工作順序與「下一步」均為歷史，不得據此自動續跑。

# Claude Execution Start

## Read order
Read these governing files before new execution:
1. `EXECUTION_DOCTRINE.md`
2. `MAGAZINE_MASTER_PLAN.md`
3. `MAGAZINE_DESK_SPEC.md`
4. `ATK_TECHNICAL_GROWTH_PLAN.md`
5. `ATK_VERIFY_STANDARD.md`
6. `DEMAND_SENSOR_SPEC.md`
7. `organization/ORGANIZATION_V1.md`
8. `agents/AGENT_SPECS_V1.md`
9. `agents/SEAT_REGISTRY.json`
10. `skills/AGENT_SKILL_CONTRACT.md`
11. `workflows/MAGAZINE_PRODUCTION_V1.md`
12. `benchmarks/TOKEN_EFFICIENCY_LAB_001.md`
13. `workflows/TOKEN_EFFICIENCY_LAB_001_TEAM.md`
14. `ledgers/HYPOTHESIS_LEDGER.md`
15. `ledgers/EVIDENCE_LEDGER.md`
16. `ledgers/DECISION_LEDGER.md`

## Phase A — Operating system
Instantiate roles as contracts, not personas. Preserve separation of duties. Do not restart completed work.

## Phase B — S3 Top 30
Create/update `reports/TOP30_R3.md` with:
- 10 Worth Talking About
- 10 Worth Running
- 10 Worth Integrating

Overlap is allowed. Use primary evidence where possible. Deep-review the demand behind the strongest token/cost/measurement projects. Do not equate stars with users. Search for counterevidence.

Evaluate `last30days-skill` and `Agent-Reach` as possible Scout components. Do not execute unreviewed third-party code.

Map relevant evidence to H001–H005 and update the Evidence Ledger. If a hypothesis confidence level should change, propose the change with evidence; do not silently modify strategic confidence.

## Phase C — Token Efficiency Lab 001 precheck
Do NOT launch an uncontrolled 100-run benchmark.

First freeze and document:
- hypotheses
- workloads/tasks
- baseline
- treatment conditions
- repetition allocation
- success/quality thresholds
- token/cost accounting
- environment/version plan
- repository/commit pinning
- candidate repository inspection
- security review
- raw evidence schema
- GitHub evidence manifest
- reproduction plan

Write `reports/TOKEN_EFFICIENCY_LAB_001_PRECHECK.md`.

## Phase D — Ledgers
Maintain:
- `ledgers/HYPOTHESIS_LEDGER.md`
- `ledgers/EVIDENCE_LEDGER.md`
- `ledgers/DECISION_LEDGER.md`

Every major research or experiment output must state which hypothesis it informs and what decision it could change.

## Mandatory review stop
After S3 + Lab 001 precheck, STOP before the full benchmark.

At the stop, answer the seven Forward-Motion questions from `EXECUTION_DOCTRINE.md`:
1. What uncertainty was reduced?
2. Which hypothesis changed confidence?
3. What new evidence was produced?
4. What failed or contradicted us?
5. What decision is now justified?
6. What is the single next gate?
7. What requires ChatGPT / Editor-in-Chief review?

Do not continue to the full benchmark until that review occurs.

## Optimization target
Optimize for **less uncertainty, stronger evidence, better decisions, verified reusable assets and measurable demand**. Do not optimize for autonomous activity, file count, report count or fork count.

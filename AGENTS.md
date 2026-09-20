# Repository agent instructions

唯一現行治理入口：[governance/OPERATING_RULES.md](governance/OPERATING_RULES.md)。

開始規劃、執行或 review 前，依該檔讀取 decisions.json 與 state.json，再查 live PR head。已決策事項不重問，失效入口不續跑。
套用 [.claude/skills/atk-goal-alignment/SKILL.md](.claude/skills/atk-goal-alignment/SKILL.md) 與 [.claude/skills/executive-review-gate/SKILL.md](.claude/skills/executive-review-gate/SKILL.md)。

目前治理導入按 GOV-01 有限授權進行；主線仍是實用工具分享、可選 ATK 接入與外部採用。
治理實作與產品 PR 分開；治理規範完成不等於自動化已啟動。歷史 benchmark 不自動恢復。
文檔與review可依既有授權寫main，實作在分支送Draft PR。不得自行merge、對外發送或新增未授權支出。

## GPT／Claude 接力與運作方法

依 [共用運作方法](AGENT_OPERATING_METHOD.md)、[專案接合](AGENT_METHOD_APPLICATION.md)、[交接手冊](AGENT_HANDOFF_RUNBOOK.md) 與 [工作模板](AGENT_TASK_TEMPLATE.md) 續作；雲端接線依 [導入驗收包](AGENT_CLOUD_ADOPTION_PLAN.md)。版本 AGENT-HANDOFF-001 / 1.0.0。此次只採用文件，不代表 runtime 已啟用，原治理入口及授權維持。

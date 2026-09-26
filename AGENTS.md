# Repository agent instructions

唯一現行治理入口：[governance/OPERATING_RULES.md](governance/OPERATING_RULES.md)。

開始規劃、執行或 review 前，依該檔讀取 decisions.json 與 state.json，再查 live PR head。已決策事項不重問，失效入口不續跑。
套用 [.claude/skills/atk-goal-alignment/SKILL.md](.claude/skills/atk-goal-alignment/SKILL.md) 與 [.claude/skills/executive-review-gate/SKILL.md](.claude/skills/executive-review-gate/SKILL.md)。
每一次執行動作向負責人回報時，所有 agent（GPT、Claude 及其他）一律使用 [.claude/skills/execution-report/SKILL.md](.claude/skills/execution-report/SKILL.md) 的四節格式：1 執行者、2 小目標進度、3 目標藍圖對齊、4 本次執行的意義；缺一節即未完成回報。此格式與既有送審、PR、executor response 格式並存，不取代它們。
- **填寫範本、本 repo 目標藍圖一句話與階段表、自動自查**：見 [REPORT_FORMAT.md](REPORT_FORMAT.md)；送出前執行 `python3 check_report_format.py <回報檔>`，不通過不得送出。（2026-09-26 補充，REPORT-FORMAT-20260926）

使命依 GOAL-02：幫助他人透過我們的 AI 基礎完成真實工作，並持續成熟上游 routing、intelligence、skill 與治理。具體規劃及 review 判準見唯一治理入口的「使命與定位」。實用工具分享、可選 ATK 接入與外部採用仍是落地路徑；目前導入範圍依 GOV-01 與 GOV-PLAN-02。
治理實作與產品 PR 分開；治理規範完成不等於自動化已啟動。歷史 benchmark 不自動恢復。
文檔與review可依既有授權寫main，實作在分支送Draft PR。不得自行merge、對外發送或新增未授權支出。

## GPT／Claude 接力與運作方法

依 [共用運作方法](AGENT_OPERATING_METHOD.md)、[專案接合](AGENT_METHOD_APPLICATION.md)、[交接手冊](AGENT_HANDOFF_RUNBOOK.md) 與 [工作模板](AGENT_TASK_TEMPLATE.md) 續作；雲端接線依 [導入驗收包](AGENT_CLOUD_ADOPTION_PLAN.md)。版本 AGENT-HANDOFF-001 / 1.0.0。此次只採用文件，不代表 runtime 已啟用，原治理入口及授權維持。

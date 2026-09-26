# Repository agent instructions

## ★ 固定回報格式（強制，最優先）

每一次執行完動作的回報，一律依 [REPORT_FORMAT.md](REPORT_FORMAT.md) 的四項固定格式：
**1. 執行者／2. 小目標進度／3. 目標藍圖對齊／4. 本次執行的意義**。
四項不可改名、調換、合併或省略；第 3 項每次都要照抄本 repo 的目標藍圖一句話。其他既有回報格式放進第 2 項或附件，不得取代這四項。送出前用 `python3 check_report_format.py <回報檔>` 自查。（Frank 2026-09-26 核定，REPORT-FORMAT-20260926）

唯一現行治理入口：[governance/OPERATING_RULES.md](governance/OPERATING_RULES.md)。

開始規劃、執行或 review 前，依該檔讀取 decisions.json 與 state.json，再查 live PR head。已決策事項不重問，失效入口不續跑。
套用 [.claude/skills/atk-goal-alignment/SKILL.md](.claude/skills/atk-goal-alignment/SKILL.md) 與 [.claude/skills/executive-review-gate/SKILL.md](.claude/skills/executive-review-gate/SKILL.md)。

使命依 GOAL-02：幫助他人透過我們的 AI 基礎完成真實工作，並持續成熟上游 routing、intelligence、skill 與治理。具體規劃及 review 判準見唯一治理入口的「使命與定位」。實用工具分享、可選 ATK 接入與外部採用仍是落地路徑；目前導入範圍依 GOV-01 與 GOV-PLAN-02。
治理實作與產品 PR 分開；治理規範完成不等於自動化已啟動。歷史 benchmark 不自動恢復。
文檔與review可依既有授權寫main，實作在分支送Draft PR。不得自行merge、對外發送或新增未授權支出。

## GPT／Claude 接力與運作方法

依 [共用運作方法](AGENT_OPERATING_METHOD.md)、[專案接合](AGENT_METHOD_APPLICATION.md)、[交接手冊](AGENT_HANDOFF_RUNBOOK.md) 與 [工作模板](AGENT_TASK_TEMPLATE.md) 續作；雲端接線依 [導入驗收包](AGENT_CLOUD_ADOPTION_PLAN.md)。版本 AGENT-HANDOFF-001 / 1.0.0。此次只採用文件，不代表 runtime 已啟用，原治理入口及授權維持。

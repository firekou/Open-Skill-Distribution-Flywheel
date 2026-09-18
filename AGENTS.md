# Repository agent instructions

## 目標對齊

在本 repository 規劃、派工、續作、review 或新增依賴前，讀取並套用 [.claude/skills/atk-goal-alignment/SKILL.md](.claude/skills/atk-goal-alignment/SKILL.md)。Codex 與其他讀取 AGENTS.md 的 agent 也使用這一份規則，不維護平行副本。

先檢查工作是否服務使用者最新目標，再做技術驗收。當前主線為有用 AI 工具與 skill 的分享、可運行技術資產、透明可選的 ATK Router 接入及實際採用。詳見 [方向校正](reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md)。

使用者最新明確指示優先。暫停中的 benchmark 或治理工具試點不得因舊工作檔而自動恢復；暫停不代表歷史缺陷已修復。

## 執行與交接

沿用 [reviews/README.md](reviews/README.md) 與 [Claude 執行入口](CLAUDE_EXECUTION_START.md)。技術驗收使用 [.claude/skills/executive-review-gate/SKILL.md](.claude/skills/executive-review-gate/SKILL.md)。一般範圍內工作不新增批准流程。

把交接、修復回覆與 review 留在 repository，不要求負責人搬運檔案。Skill 與 review 判定本身不授權 merge、部署或支出。

## 外部 Agent 採用目標

必讀 [外部 Agent 發現、採用與解題驗收](reviews/ATK_AGENT_DISCOVERY_AND_ADOPTION.md)。每次交付都分辨「已公開」「能被找到」「能採用」「解決任務」「外部實際使用」；不能互相代替。小 PR 結案後指出下一個未驗證目標並繼續主線，不無限重驗已解問題，也不把停止點誤作整體專案停止。下一工作包與回覆位置以該文件為準。

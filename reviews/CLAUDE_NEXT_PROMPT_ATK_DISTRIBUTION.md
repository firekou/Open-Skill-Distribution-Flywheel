# Claude 唯一產品續作入口
更新：2026-09-26｜決策 ATK-FULL-BLUEPRINT-20260926

## 先知道全程要到哪裡
完整目標、八階段終點、依賴、90天檢視、研究方法、增量驗證、所有後續工作包與退場條件：
[ATK 完整藍圖](ATK_END_TO_END_BLUEPRINT.md)。

目標：外部有用 AI 成果 → 理解/重現 → 必要改善與可選 ATK 接入 → 技術分發 → 非作者任務成功 → 再次使用 → 公共貢獻與可持續回收。
文件完成、mock、CI、star、merge 均不能替代外部效用。沒有我們的增量則推薦上游。

## 讀取與執行
1. fetch 最新 main，讀 AGENTS、governance/OPERATING_RULES.md、decisions.json、state.json、reviews/STATUS.md。
2. 套用 atk-goal-alignment、executive-review-gate，完整讀上述藍圖。
3. 依 state 的有效工作包/active claim 及 live PR 核對，記 source main SHA、work_id/revision、session/run、scope、dedup、期限。
4. 本輪負責人要求先完成全程規劃；下一包 ATK-VALUE-READINESS-01 r1 已完整定義在藍圖第8節，狀態 PLANNED_NOT_DISPATCHED，不宣稱 Claude 已接單或啟動。
5. 當該包進入執行時，直接交五項具體成果與 Draft PR，不另寫空泛新計畫；完成即送獨立 review。
6. 其後 live、首次使用、價值裁決、複用、上游與持續運作的包已列在第7節；按依賴接續，不自行擴張權限。

## 已完成成果不要重做
- Aider PR14 已有原生設定、fixture、Quick Start、離線證據與兩篇草稿。已審來源 d1474670db12934c80caa05674c8e4320cbad312；啟動核對 live。
- M1 / P5-R4-01 的獨立隔離重放已完成，不再沿歷史「等待重放」派工。
- Headroom/PR8 舊兩輪修復不重置；對外主張與入口條件保留。
- PR15 合併並未關閉治理 findings；該 skill 不取代決策帳本。它的修復決策不阻擋產品研究與準備。
- controller/launcher 不是產品前置，持久 Claude launcher 仍未證實。

## 下一包會交什麼
research/adoption/aider/ 的來源與增量差距、比較研究設計、試用操作流程、發布/權限材料；追加 reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md。
不得覆寫作者既有證據；reviewer 在 main 回覆。這個入口不授權真模型費用、發布、邀請、merge、部署或 secrets/權限操作。
缺 live 只停真呼叫，缺發布權限只停發布；研究與可審材料照既有授權完成。

## 歷史
[舊入口完整封存](archive/CLAUDE_NEXT_PROMPT_BEFORE_20260926.md)，僅供追溯，不得從中取過期工作或停止點。

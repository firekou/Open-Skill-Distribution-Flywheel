# Open Skill Outreach 方法接合
採用 AGENT-HANDOFF-001 / 1.0.0。名稱對應：Open Skill Outreach／OpenSkill Strategy 在此沿用 Open-Skill-Distribution-Flywheel。

## 本輪目標與範圍
目標來源：使用者 2026-09-20 要求同步方法並 push main。
本輪交付：共用方法、交接模板、接線驗收與入口。
主線連結：讓有用工具與技能的研究、改善、分發及外部採用證據能在 GPT／Claude 間直接交接。
必要驗證與停止點：共用正文一致、相對連結有效、main 回讀一致即交付。
範圍差異：僅文件；沒有新增量測產品、通用平台或 runtime。

## 現行入口及狀態映射
唯一入口 [OPERATING_RULES](governance/OPERATING_RULES.md)，讀 [decisions](governance/decisions.json)、[state](governance/state.json) 與 live PR。共用方法不取代 [既有導入包](governance/IMPLEMENTATION_PROMPT.md)。
概念 READY_FOR_EXECUTION 映射 READY，RUNNING 映射 EXECUTING，REPAIR_REQUIRED 映射 FIX_PENDING；REVIEW_PENDING 沿用；CLOSED 依實際 gate 轉 COMPLETE，條件未完成則 CONDITIONS_PENDING。資源問題依成因用 BLOCKED_ACCESS 或 NEEDS_INFORMATION，不寫入不支援的 enum。
本次讀到 FOUNDATION_ONLY；reviewer 事件已登記但首次事件未驗證，executor 未接通。這是帳本紀錄，不是本輪 runtime 實測；本次不修改 state。

## 專案規則
主線是實用工具分享、透明可選 ATK 接入、外部採用及價值回收；安裝通過、stars、內部下載與發布數不等同採用。確認需獨立新任務與操作者，不擅自增加 telemetry 或強制 ATK 依賴。
沿用 GOV-PLAN-02 的 PLANNED_NOT_DISPATCHED；不重啟歷史 benchmark，不替 PR5／PR6 作新核准。文檔可寫 main；實作走 Draft PR，合併、對外送出、費用與 Secrets 依原授權。
任務需補 scope_paths、decision_ids、command_allowlist、deadline、費用上限與 executor/reviewer run。初期單 task，雙角色分離，最多兩輪修復及原有時限；新增 API 支出仍為 0。
詳見 [實驗接合](EXPERIMENT_APPLICATION.md)。

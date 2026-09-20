# 共用訂閱雲端接力導入工作包

版本：AGENT-HANDOFF-001 / 1.0.0。專案階段及授權依 [專案接合](AGENT_METHOD_APPLICATION.md)。

狀態：PLANNED_NOT_DISPATCHED。本次使用者要求建立規劃與運作方法；此工作包尚未啟動 Routine、修改 Secrets 或派送實驗。現行可運作模式依各 repo 帳本，不假設已有排程或 executor。

## 目標與範圍

每個 repo 先選一個已授權的小型內部文件任務，證明電腦關機後仍可 GPT 規劃 → Claude 執行 → GitHub 結果 → GPT 檢核 → 有限修正。成功後再評估跨 repository 採用。

固定 main 與精確工作版本，不依賴平台默認分支。成果用任務工作分支及 PR，不讓 worker 直接改 main 的治理政策。此接線試點不發布產品、不做外部觸達、不部署 production、不進行交易，也不重跑已結案任務。

## 分批落地

| 批次 | Owner | 交付與退出條件 |
|---|---|---|
| C0 能力盤點 | GPT planner | 核對帳號的 Routines、GitHub App、ChatGPT 事件及目前排程；每項記可用、不可用或未知與證據 |
| C1 接線設計 | Claude executor | 依 AGENT_HANDOFF_RUNBOOK 補最小適配層設計或 draft PR；明確持久狀態、原子領取、去重與對帳；GPT review |
| C2 帳號接線 | 有權限操作者 | 建立單 repo、單任務 Routine 與 reviewer 事件；確認使用訂閱且無付費 fallback，記錄設定 ID，Secret 值不上庫 |
| C3 真實往返 | Claude executor → GPT reviewer | 在有限測試任務上完成下列驗收及該 repo 更嚴格的自主運作門檻並保存 session、commit、事件與 review 證據 |
| C4 採用 | GPT planner | 真實通過才更新 decisions runtime；未通過保留手動 Claude 入口，列出精確缺口 |

C0/C1 可先完成不依賴帳號設定的部分。C2 的既有權限直接使用；需要帳號擁有者登入或平台未提供功能時，提出具體缺項，不把所有準備留給使用者。

## 兩條 Claude 接線路徑

A. 優先 Routines：設定 repository、可信工作 prompt、PR labeled 與 ready-claude 篩選；session 重新讀 main 任務。回程使用 ready-gpt 加完成留言，ChatGPT 重新核對狀態後 review。

B. Routines 不可用時，官方 claude-code-action 支援訂閱 OAuth。由帳號擁有者透過 claude setup-token 取得憑證並安全存入 CLAUDE_CODE_OAUTH_TOKEN；workflow 使用 claude_code_oauth_token 輸入，不配置 anthropic_api_key。Actions 執行資源的費用與訂閱額度分開。這是備案設計，不在本次提交啟用。

兩條只選一條派同一任務，不能雙重消耗。不得繞過既有 Copilot 管理員政策。GPT 回程事件不可用時，若已有可用治理續作排程則沿用，否則記為人工交接；記錄延遲，不能稱已事件化。

## C3 驗收矩陣

| 情境 | 預期結果與證據 |
|---|---|
| 正常完整往返，使用者不搬運報告 | 雲端 run → 成果 commit → GPT review；紀錄各步時間與 task_id |
| 刻意一項不符合條件 | GPT 提出 finding，Claude 限定修復，GPT 核對新 head；修復最多兩輪 |
| 重複事件 | 同 task/revision 只一個有效 worker，重複事件有忽略紀錄 |
| 舊版本事件晚到 | 不覆寫新工作，不審錯 commit |
| 配額不足或中途失聯 | RESOURCE_BLOCKED，保留待辦；先查 session 結果再恢復，無付費 fallback |
| 事件漏失 | 對帳發現待辦並補派一次，不重做已有成果 |
| 未授權來源或一般留言 | 不執行；不因 prompt 文字取得額外權限 |
| 完成後再次收到同一事件 | 不重跑已結案批次 |

故障可先用離線 fixtures 驗證；mock 與真實平台行為分列。至少正常往返及修正往返需要真實 session 證據。CI 綠燈只能證明其測過的部分。

## 操作與恢復

啟動後記錄事件 ID、設定 ID、run ID、處理時間及用量；所有值不得包含憑證。停用新 trigger 即退回本 repo 既有可用的人工交接模式，保留全部成果與待辦。先確認沒有在途 session 再人工續作。

完成本 repo 全部自主門檻並獨立覆核後，才更新原治理帳本的 runtime，附 reviewer 證據。未驗證前保持 PLANNED_NOT_ENABLED，不把規劃完成、程式完成、單向啟動或綠燈寫成自主營運成功。

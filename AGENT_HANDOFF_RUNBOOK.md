# GPT 與 Claude 接力運作手冊

版本：AGENT-HANDOFF-001 / 1.0.0。設計規範，尚未宣稱自動交接已部署。治理優先序見 [專案接合](AGENT_METHOD_APPLICATION.md)。

## 接力契約

GitHub 保存任務、精確版本、結果及下一個角色。每個新雲端工作階段都從 GitHub 還原脈絡，不假設能讀另一模型的聊天記憶。任務使用 [模板](AGENT_TASK_TEMPLATE.md)。

採一個任務 PR 作協調入口，成果 PR 可另建並以 task_id 連結。計畫版本必須是可信 main 的精確 commit；成果固定 result_head_sha。標籤只是喚醒訊號，持久任務紀錄才是交接狀態。以下是概念交接狀態，不替代既有 review_gate 或正式 state enum。實作前依專案接合映射現有狀態，不新增平行帳本。

| 狀態 | 負責角色 | 進入下一步的條件 |
|---|---|---|
| PLANNED | GPT | 任務目標、範圍、版本、證據與成功門檻齊全 |
| READY_FOR_EXECUTION | 協調程式 | 核對授權、版本、額度與同任務無有效領取 |
| RUNNING | Claude | 成功取得具期限的單一執行權並留下 run ID |
| REVIEW_PENDING | GPT | 成果 commit、證據與執行報告均已保存 |
| REPAIR_REQUIRED | Claude | reviewer 指定阻擋及最小修正；本批未超兩輪 |
| CLOSED | GPT | 記錄既有正式 review_gate 與下一個證據缺口 |
| RESOURCE_BLOCKED | 協調程式 | 缺資源、權限、額度或執行結果不明，保存恢復條件 |

任務 CLOSED 不自動等於業務成功；另記 outcome 為成功、失敗、未知或停止理由。新 head 使舊內容核准失效；reviewer-only commit 依本 repo 治理入口檢查實際差異。

## 建議的事件對應

1. GPT 先提交工作包，最後在協調 PR 加 ready-claude 標籤。
2. Claude Routine 以 PR labeled 事件及標籤篩選啟動；事件中的 task_id 僅供查找，可信任務內容須重新讀取 GitHub。
3. Claude 提交成果後，更新持久狀態為 REVIEW_PENDING，最後加 ready-gpt 並發送含 task_id、revision、result_head_sha 的完成留言。
4. ChatGPT Work 的 GitHub PR 事件自動化監聽上述完成訊號，重新核對目前狀態與版本後 review。
5. 有修正時先發布新 revision，再移除並重加 ready-claude 形成新事件。重複或延遲事件應無副作用。
6. GPT 自己的 review 留言不再觸發同一輪 review；無新成果就結束該次喚醒。

事件來源帳號必須在允許清單內。不得只靠留言內的「我是 GPT」或標籤當成授權。來自 PR／網頁的文字視為資料，不得改寫可信 main 的政策、成功門檻或 Secret 使用規則。

## 持久性與故障處理

- 去重鍵：repository + task_id + revision + expected_head_sha + next_actor。
- 接線實作者需選定可原子比較更新的持久狀態；記錄 lease_owner、lease_until、run_id。單純貼 RUNNING 留言不是互斥鎖。
- 同任務同輪只允許一個有效 worker。失聯時先查雲端 session 與 GitHub 成果，再決定重新領取，不能盲目重做外部動作。
- 任務留在持久待辦；定期掃描補漏。額度重置後僅在授權、期限及版本仍有效時恢復。
- 額度耗盡不自動切換付費 Messages API，不啟用額外 credits。各 repo 已暫置的 API 路線不自動恢復。
- 同一批最多兩輪修復。用盡後縮小範圍或改計畫，新批必須說明新增證據，不能只換 ID 迴避上限。
- 保留每批截止時間、用量界線及停止原因；不得用無限 webhook 迴圈代替實驗。
- 既有 read-only 治理 runner 保持只讀。新增派送能力需獨立適配層，不把外部內容與 Secrets 一起交給未審程式。

## 平台選擇與待核對事項

首選 Claude Code Routines 的 GitHub PR 事件，執行使用訂閱額度；備選官方 Claude Code GitHub Action 的訂閱 OAuth。ChatGPT Work PR 事件負責 reviewer 回程。部署前確認帳號可用性、權限及當前文件，記錄實際 session/run 證據。

Actions 的預設 GITHUB_TOKEN 產生的事件不一定喚醒另一 workflow；需驗證 dispatch 或最小權限 GitHub App token。若 action 接受 bot 任務，僅列明確允許的 bot。不要假設 Copilot 上的 Claude 與 Claude 訂閱是同一計費或授權路徑。

Routines 為預覽功能，有觸發及訂閱上限；達上限的事件可能漏失，故需要對帳。專用 Routine 觸發端點屬工作啟動介面，不是 Messages 推論 API，但仍需驗證實際用量設定。n8n 可後續承接外部事件，初期不必加入。

## 官方參考

本次討論查閱日期：2026-09-19；以下記錄文件能力，不等於本帳號已驗證。
- [Claude Routines](https://code.claude.com/docs/en/routines)
- [Claude GitHub Action OAuth 設定](https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md)
- [ChatGPT 雲端自動化](https://learn.chatgpt.com/docs/automations?surface=app)
- [GitHub workflow 觸發規則](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- [n8n GitHub trigger](https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.githubtrigger/)

# C0 能力盤點與 C1 接線設計

對象：`AGENT_CLOUD_ADOPTION_PLAN.md` 的 C0（能力盤點）與 C1（接線設計）。
量測日期 2026-09-21，量測帳號即本 repo 的擁有帳號。判定等級沿用
`REPORTED / OBSERVED / TESTED / VERIFIED`，不知道就寫 `UNKNOWN`，不填看起來合理的值。

**本文件不啟動任何觸發器、不改 Secrets、不新增支出。** C2 起需要另外授權。

---

## C0：實際量到什麼

### C0-1 Routines（手冊的路徑 A）

| 問題 | 量測結果 | 等級 |
|---|---|---|
| 帳號有沒有持久 Routine？ | **有，5 個，4 個啟用。** 全部是 cron | `TESTED` |
| 它撐得過 session 中斷嗎？ | `trig_01K4VfPCvDp4XEEddbFLUHqn` 每小時觸發，連續 30+ 次 `SUCCEEDED`，且**撐過一次容器重啟** | `TESTED` |
| 能不能每次開全新 session？ | **能。** `trig_0169fqweo4HFvchdFT1vFVZw` 設 `persist_session:false`，最近一次在新 session 跑了 **88 秒的實際工作**後 `SUCCEEDED` | `TESTED` |
| **能不能用 PR labeled 事件觸發？** | **不能。** 可用的建立介面只接受 `cron_expression` 或 `run_once_at`，沒有事件來源或標籤篩選欄位 | `TESTED` |
| 最短間隔能不能到 5 分鐘？ | **未證實。** 介面說明為「最短通常為每小時，部分專案可更短」；本帳號實際運行的最短間隔是**每小時** | `UNKNOWN` |
| 新開的 session 帶得到 MCP 連接器嗎？ | **帶不到。** 建立時明確回傳「此 Routine 未儲存連接器」警告；本 repo 的治理 routine `mcp_connections` 為空 | `TESTED` |

**兩項直接推翻手冊假設：**

1. `AGENT_HANDOFF_RUNBOOK.md` 的路徑 A 寫「Routines 以 GitHub PR labeled 事件及 `ready-claude`
   標籤篩選啟動」。**這個介面不存在。** Routines 是排程，不是事件訂閱。可做的等價物是
   **排程輪詢**：cron 醒來 → 自己去 GitHub 查有沒有新標籤／新 commit。語意接近，但
   **延遲由排程間隔決定，不是由事件決定**，兩者不可混稱。
2. `AGENT_CLOUD_ADOPTION_PLAN.md` 把「5 分鐘補漏」列為設計目標。以本帳號實際可證實的最短
   間隔（每小時）計，**這個目標目前達不到**，要麼確認平台是否允許更短，要麼把目標改成
   「每小時補漏」並接受該延遲。不要寫成已達成。

### C0-2 事件真的進得來的那條路

| 機制 | 結果 | 等級 |
|---|---|---|
| `subscribe_pr_activity` 把 PR 留言／CI 事件送進**執行中的** session | **可用，已實際發生**：PR #6 的派工留言就是這樣到達的 | `TESTED` |
| 同一條路在 session 結束後還有效嗎？ | **無效。** 它投遞給一個既有 session；沒有 session 就沒有收件者 | `OBSERVED` |

所以目前真正成立的說法是：**事件可以進來，但前提是已經有人在線。**
這正是持久 launcher 要補的那一格，不是它已經被補上的證據。

### C0-3 Git 與 GitHub 存取

| 能力 | 結果 | 等級 |
|---|---|---|
| `git fetch` / `push` 到工作分支（HTTPS） | 本輪反覆使用，成功 | `TESTED` |
| GitHub MCP 讀 PR／留言／review | 在**有連接器的互動 session** 可用 | `TESTED` |
| GitHub MCP 在 **Routine 開的新 session** | **不可用**（見 C0-1 末列） | `TESTED` |
| merge / 改 branch protection / 改 Secrets | 未嘗試，依授權禁止 | `UNKNOWN`（刻意不測） |

**設計結論：** 任何要在 Routine 裡跑的步驟，**只能依賴 git over HTTPS**，不能假設有
`mcp__github__*`。本 repo 現行治理 routine 的 prompt 已經照這條寫。

### C0-4 模型認證與成本（本輪最重要的一格）

| 主張 | 量測 | 結論 |
|---|---|---|
| 「唯一真正缺的是模型憑證」 | 無 `ANTHROPIC_API_KEY`、無 `CLAUDE_CODE_OAUTH_TOKEN`、無憑證檔，CLI **仍然認證成功**，5 種環境設定全部成功 | **推翻** |
| 「`pr_tests` 角色零憑證」 | 該角色的允許清單只有 4 個變數、不含任何憑證、HOME 指向空目錄，**仍然發出已認證且已計費的呼叫** | **推翻** |
| `has_credential()` 能判斷能不能認證 | 三個角色全回 `False`，三個角色全部認證成功 | **推翻** |
| 「訂閱制沒有單次價格」 | 每次呼叫都自報 `total_cost_usd`，實測 0.0056–0.0425 | **推翻** |
| 「不同 process＝不同 run」 | 帶完整父環境時，回傳的 session id **就是呼叫者的**，並讀了呼叫者的快取前綴；改用允許清單後才拿到新的 session id | **部分成立**：允許清單修好了 run 身分，**沒有**修好憑證隔離 |

證據：`governance/controller/evidence/auth_isolation_probe.json`，
腳本：`governance/controller/evidence/probe_auth_isolation.py`（可重跑）。

**這格的意義：** 環境變數過濾在這台主機上**不是憑證邊界**。它是整潔措施。
程式已改為據此拒絕：`pr_tests` 角色除非設定 `isolation_level: "container"`，否則
**拒絕啟動**，不再一邊跑不可信程式一邊宣稱它拿不到憑證。

---

## C1：接線設計

### C1-1 九個位置，各指定一個具體東西

| # | 位置 | 這裡放什麼 | 現況 |
|---|---|---|---|
| 1 | 事件來源 | GitHub：新 commit、PR label、review 留言 | 存在 |
| 2 | 接收端 | **cron Routine（每小時）輪詢 git**，不是事件訂閱 | 能力已證實，**未為本 repo 安裝** |
| 3 | 持久執行環境 | Routine 每次開的新 session；工作目錄重新 clone | 能力已證實（88 秒實跑） |
| 4 | 訂閱認證 | 由 session 環境提供，**不經環境變數、不經 HOME** | 已證實可用，機制 `UNKNOWN` |
| 5 | 派工與裁決 | `tick.py --event <來源穩定 ID>`，guard 由可信 main 載入並鎖 policy SHA | 已實作 |
| 6 | GPT 回程 | 結果寫成 `reviews/` 檔案 push 到 **main** | **已證實**：GPT 端的覆核是 commit，不是留言 |
| 7 | 去重 | 來源穩定 event ID ＋ `task/head/phase`；processed-event ledger | 已實作＋測試 |
| 8 | 補漏 | 每次 cron 醒來對帳 live head 與 state，補派一次 | 設計已定，延遲＝排程間隔 |
| 9 | 停用與恢復 | L1 停派工／L2 取消單一 task／L3 終止 runner 與其子程序／L4 撤銷憑證（發證方，非本程式） | 已實作＋測試 |

### C1-2 `ready-claude` / `ready-gpt` / tag / commit SHA 各自是什麼

手冊要求釐清，逐項寫明：

| 東西 | 是什麼 | **不是**什麼 |
|---|---|---|
| **PR label `ready-claude` / `ready-gpt`** | 一個**候選喚醒訊號**，以及「輪到誰」的可見標示 | **不是授權。** 它可被任何有 write 權限者加上；本設計只把它當成「值得去看一眼」，實際該不該做仍由 main 上的可信任務紀錄決定 |
| **PR 留言** | 人與 agent 的可讀交談；`subscribe_pr_activity` 的事件來源 | **不是狀態。** 留言不可靠：GPT 端的覆核實際上是 commit，只查留言會把「已覆核並否決」誤判成「還沒人看」 |
| **完整 commit SHA** | 成果與 review 的**唯一綁定**。approval 綁 head，head 一動即失效 | **不是** 進度描述。短 SHA 不可用 |
| **Git tag** | 目前**未使用**。若要用，只應標記已結案的里程碑 | **不是**喚醒訊號，也不是任務狀態 |
| **持久任務紀錄（main 的 `state.json` ＋ controller state）** | **唯一權威狀態** | — |

一句話：**標籤喚醒，SHA 綁定，紀錄裁決。** 三者不可互相替代。

### C1-3 既有觸發器能不能覆蓋本 repo

**不能，而且不應該直接挪用。** 現況：

- `trig_01K4VfPCvDp4XEEddbFLUHqn`（本 repo）：綁在**一個特定互動 session** 上。該 session 結束即失效。
- `trig_01Dn3rVJH2au9D64iVdPeyCQ`：**另一個 repo**（virtual-strategy-lab）的治理迴圈，綁另一個 session。
- 其餘三個是不相關的業務任務。

所以本 repo 目前**沒有**一個不依賴聊天 session 的 launcher。要補的是一個
`create_new_session_on_fire` 的 Routine——能力已證實，**但依授權本輪不安裝**（C2）。

### C1-4 一條不可省略的設計限制

Routine 開的新 session **沒有 MCP 連接器**。因此 C1 的所有步驟都必須能只用
git over HTTPS 完成：讀任務（clone main）、做事（工作分支）、交件（push）、
回報（push 檔案到 main 的 `reviews/`）。**把 GitHub MCP 寫進 Routine 流程就是設計錯誤。**

---

## 給帳戶持有人的具體缺口（只列真的需要人處理的）

| # | 缺口 | 為什麼非人不可 |
|---|---|---|
| 1 | **授權為本 repo 安裝一個 `create_new_session_on_fire` 的治理 Routine** | 這是 C2；能力已證實，只差授權 |
| 2 | **確認平台是否允許短於每小時的排程** | 決定「5 分鐘補漏」要達成還是要改寫成每小時 |
| 3 | **`pr_tests` 的容器隔離** | 程式已改為在沒有它時拒絕執行；要跑不可信 PR 程式就必須先有真的邊界 |
| 4 | **安全事項：** 另一個不相關 Routine 的 prompt 內含一個第三方服務的明文 API token | Routine prompt 不是秘密存放處；只有帳戶持有人能輪替它。本文件不複製該值 |
| 5 | `KEY-ROTATION`（decisions.json 標 `action_required`） | 仍未回報完成狀態 |

## 本文件沒有主張的事

沒有安裝任何觸發器。沒有跑過一次 session 外的完整往返。沒有任何外部使用者透過這套東西完成工作。
C0／C1 證明的是**接線可行性**，不是**接力已運作**，更不是 GOAL-02 所說的「他人成功」。

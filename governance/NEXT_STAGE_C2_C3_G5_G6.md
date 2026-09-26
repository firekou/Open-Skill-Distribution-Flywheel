# 下一階段可直接執行的工作：C2、C3、G5、G6

每項寫到「照著做就能做完」的粒度：操作順序、責任角色、所需權限、驗收證據、停止條件。
**本文件不執行其中任何一項。** C2 起需要負責人另外授權。

排序依據：**C2 是其餘三項的共同前提**。沒有一個不依賴聊天 session 的 launcher，
C3／G5／G6 全部只能在有人在線時成立，而那正是要驗掉的假設。

---

## C2 帳號接線（先做這個）

**角色：** 帳戶持有人（唯一能建立 Routine 的人）。Claude 只能提供設定內容與驗證腳本。
**所需權限：** 建立 Routine；本 repo 的 push 權限已具備。

| 步驟 | 動作 | 產出 |
|---|---|---|
| C2-1 | 建立一個 Routine：`create_new_session_on_fire: true`（**不要綁既有 session**），cron 每小時 | Routine ID |
| C2-2 | prompt 只用 git over HTTPS（見 `CLOUD_HANDOFF_WIRING.md` C1-4）；**不得假設有 GitHub MCP** | prompt 文字入庫 |
| C2-3 | prompt 內**不得**含任何 token（現有某個不相關 Routine 已踩到這條） | — |
| C2-4 | 讓它空跑兩次，只讀不寫 | 兩筆 `last_run: SUCCEEDED` ＋ 兩個**不同**的 session ID |

**驗收證據：** Routine ID、兩次 `fired_at`／`finished_at`、兩個相異 session ID，
且**本輪互動 session 全程未參與**。
**停止條件：** 若兩次觸發拿到同一個 session ID，表示它其實綁在既有 session 上 → 停，回 C1 重新設計。

---

## C3 真實往返

**角色：** Claude executor（Routine 內）→ GPT reviewer。
**前提：** C2 通過。

| 情境 | 要證明什麼 | 證據 |
|---|---|---|
| C3-1 正常往返 | 使用者不搬運任何檔案 | 事件 ID、task ID、各 run ID、完整 SHA、各步時間 |
| C3-2 刻意不符合 | GPT 提 finding → Claude 限定修復 → GPT 核新 head | 兩個 head、finding 逐項處置 |
| C3-3 重複事件 | 同 task/revision 只有一個有效 worker | 忽略紀錄（ledger） |
| C3-4 舊版本事件晚到 | 不覆寫新工作、不審錯 commit | 拒收紀錄 ＋ 被保護的 head |
| C3-5 額度不足／中途失聯 | 記 `RESOURCE_BLOCKED` 保留待辦，**無付費 fallback** | 狀態轉移紀錄 |
| C3-6 事件漏失 | 對帳補派**一次**，不重做已有成果 | 對帳紀錄 |

**停止條件（任一成立即停並回報，不繞過）：**
需要人工搬檔 · 出現付費 fallback · 同一 finding 無新證據重複兩輪 · 修復超過兩輪。

---

## G5 單任務真實試行

**角色：** Claude executor → 獨立 reviewer。**前提：** G4 通過 ＋ 真實試行授權。

1. 選一個**無秘密、無對外發布**的治理文件小任務，寫明 `scope_paths` 與客觀驗收，指定隔離分支。
2. 同一個初始觸發之後：controller 派 executor 產 commit → 派**獨立** reviewer → 有真實 finding 才修 → 結案。
3. **不得為了展示修復而讓 reviewer 虛構缺陷**；負控制留在離線 replay。

**必須保存：** 初始 event ID、task ID、各 run ID、完整 SHA、policy SHA、起訖時間、
認證類型、**每次呼叫的 `total_cost_usd`**（CLI 本來就回傳，不記是選擇不是限制）、
review 決定、修復輪數。

**只有**真實 CLI 解析、認證、分支推送、review 回填**全部成功**才標 `MANUAL_RUN_VERIFIED`。
只單獨跑一次模型不算閉環。

**G5 的前置阻擋（本輪實測後新增）：** reviewer 的獨立性目前只做到
**不同 session ID ＋ 不同工作區**。同模型、同帳號、同憑證來源。
送 G5 前必須先裁定「獨立 reviewer」的定義（見下方 D3），否則做完也不能宣稱獨立。

---

## G6 持久觸發與營運驗收

**角色：** Claude／Operator。**前提：** G5 通過 ＋ 觸發部署授權。

| 要證明 | 怎麼證 |
|---|---|
| 不依賴既有聊天 session | 原互動 session 結束後，新事件仍被處理 |
| 事件來源→接收→排隊→執行→回填各有可核對 ID | 五段 ID 串得起來 |
| 重送事件不重跑 | ledger 命中紀錄 |
| 途中改 head 廢止舊 review | 拒收紀錄 |
| 停止與恢復 | L1–L3 實跑；L4 明記屬發證方 |
| 補漏延遲 | **照實記錄實際間隔**；每小時就寫每小時，不寫 5 分鐘 |

**先決事項：** `AGENT_CLOUD_ADOPTION_PLAN.md` 寫的「5 分鐘補漏」以本帳號可證實的能力
**達不到**。C2-2 之前必須先裁定：確認平台可否更短，或把目標改寫為每小時。

---

## 需要裁定才能往下的四件事

| ID | 事項 | 不裁定的後果 |
|---|---|---|
| **D1** | **G2／G3 掛在哪條分支。** 目前 PR #6（`claude/atk-governance-controller`）與 PR #7（`claude/friendly-knuth-i9zfp7`）各有一份 G1 | 兩份互相分歧的 executor response 與能力表，單一事實來源失效 |
| **D2** | 是否授權為本 repo 安裝 `create_new_session_on_fire` 的 Routine（C2） | C3／G5／G6 全部卡住 |
| **D3** | 「獨立 reviewer」的定義。同帳號、同模型、同憑證來源，只有 session 與工作區不同，算不算獨立 | G5 做完也不能宣稱獨立，等於白做 |
| **D4** | 每次呼叫的 `total_cost_usd` 是否納入 run 紀錄與上限 | 次數上限擋得住失控迴圈，擋不住每次都很貴 |

D1 依 `IMPLEMENTATION_PROMPT.md`「治理修復沿用 PR #6 的治理分支」，**本輪已照此執行**；
PR #7 的實測結論已併入本分支並獨立重現。是否關閉 PR #7 由 Planner 決定，executor 不自行處置。

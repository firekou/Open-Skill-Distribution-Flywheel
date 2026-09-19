# G1 能力表：治理自動化實際具備什麼

版本 1，2026-09-19。執行者：Claude（executor）。
依 [`governance/IMPLEMENTATION_PROMPT.md`](IMPLEMENTATION_PROMPT.md) 的 **G1**，處理
[`reviews/PR6_R1_READINESS_REVIEW_c04ef465.md`](../reviews/PR6_R1_READINESS_REVIEW_c04ef465.md)
的 `GOV-R1-01`～`GOV-R1-04`。

政策來源：[`governance/OPERATING_RULES.md`](OPERATING_RULES.md)。決策來源：[`decisions.json`](decisions.json)。
本檔**不是** review，也**不**變更任何授權。

> **G1 要修的不是「缺什麼」，是「我們怎麼講我們有什麼」。**
> 上一輪把「這個容器沒有憑證檔」寫成了「唯一缺口是憑證」。前者是觀測，後者是結論，
> 而那個結論這次被實測推翻了。

## 0. 本輪為什麼開始執行

`decisions.json` 的 `GOV-PLAN-02` 把治理導入定為 `PLANNED_NOT_DISPATCHED`，並寫明
「未來收到明確啟動指示後」才執行 G1–G3。負責人於本輪明確指示依既有工作計畫**執行下去**，
這構成該啟動指示。

範圍限制照舊：本輪**不**掛 live webhook、**不**開 live dispatch、**不**合併、**不**對外發送、
**不**新增未授權支出。`automation.status` 維持 `FOUNDATION_ONLY`，由 planner 依證據決定是否更動。

## 1. 能力表

判定詞只有四個（沿用 `OPERATING_RULES` 的證據詞彙）：
**REPORTED**（他人自報）／**OBSERVED**（直接看到）／**TESTED**（有紀錄但本輪未重跑）／
**VERIFIED**（本輪獨立取得可核對結果）。「不知道」一律寫 `UNKNOWN`，不寫 0、不寫「只缺 X」。

| # | 能力 | provider | 生命週期 | 等級 | 證據 | 限制與缺口 |
|---|---|---|---|---|---|---|
| 1 | 事件來源 | GitHub PR／commit webhook | 隨 repo | **OBSERVED** | 本輪以 API 讀到 live PR 列表與 head（PR#6 head 仍為 `c04ef465…`，Draft、未合併） | 讀得到事件**不等於**有東西會被事件喚醒。PR#6 沒有任何接收端訂閱 |
| 2 | 接收服務 | Anthropic 帳號的 routines（排程／webhook） | 帳號層級、持久 | **VERIFIED（存在）** | 本輪讀取帳號 routines：3 個（2 啟用、1 停用），含 `0 1 */6 * *` 與 `0 1 * * 1` 兩個 cron，且有實際 `last_fired_at` 與 `SUCCEEDED` 結果 | 那三個都屬**其他專案**。治理導入本身沒有任何 routine |
| 3 | 持久 launcher（本 session 結束後仍能喚起 Claude） | 同上（`create_trigger`，可綁持久 session 或每次開新 session） | 持久 | **VERIFIED（能力存在）**／**未為治理導入安裝** | 同上；另有 `persist_session: true` 的實例 | ⚠️ **這一列推翻了上一輪的預設。** 正確說法不是「沒有持久 launcher」，是「有，但沒有為這件事裝，而且本輪依授權不裝」 |
| 4 | 執行主機 | Anthropic cloud 環境（4 個 active） | 帳號層級 | **VERIFIED（存在）** | 本輪列出 4 個 `kind=anthropic_cloud`、`state=active` | 這是模型執行環境，**不是**隔離的不可信程式沙箱。`GOV-R1-03` 要的容器隔離仍未接上 |
| 5 | 模型認證（executor 側） | 由 session 環境提供，**不是**由環境變數或家目錄憑證檔提供 | 單次 session | **VERIFIED** | [`evidence/G1-claude-cli-auth-probe-2026-09-19.json`](evidence/G1-claude-cli-auth-probe-2026-09-19.json)：`claude -p` 在**沒有**模型 API 環境變數、**沒有**家目錄憑證檔的情況下回傳 `PONG`、`is_error=false`、exit 0 | ⚠️ 見 §2 的 `GOV-R1-01`。同一次呼叫回報 `total_cost_usd = 0.0415`，且 `session_id` 與父 session 相同 |
| 6 | reviewer 身分（獨立 run） | — | — | **UNKNOWN／未達成** | 本輪沒有任何獨立 reviewer run | 由 executor session 內 spawn 出來的 subprocess **共用同一個 session_id**（證據同上），因此它不是獨立來源。「不同程序」不等於「不同 run」 |
| 7 | GitHub 讀寫 | MCP GitHub 工具 + 環境內的寫入憑證 | session | **VERIFIED** | 本輪已讀 live PR、並推送工作分支 | 🔴 寫入憑證與 executor 同環境；不可信 PR 測試環境的隔離未建立（`GOV-R1-03` 未關閉） |
| 8 | 狀態磁碟 / task store | ① repo 內 `state.json`（摘要）② PR#6 的 controller `state_dir`（repo 外） | ①隨 git ②隨磁碟 | **REPORTED（②）／OBSERVED（①）** | ① 本輪讀取；② 本輪**未執行** controller，未產生任何 state | `state.json` 是檔案，沒有 compare-and-swap；它是摘要不是權威。G3 的跨程序鎖與租約仍待驗 |
| 9 | 取消與恢復 | routine 的 `enabled` 開關、controller 的 `stop_file`、任務終態 | — | **OBSERVED（介面存在）** | ACTIVATION.md 記載 `touch $stop_file` → 下一個 tick 回 exit 30 | 本輪**未實測**。而且「停止派工」「取消當前程序」「終止子程序」「撤銷外部 token」是四件不同的事，目前只有第一件有現成開關 |

## 2. 四項 finding 的處置

### `GOV-R1-01` — 「只缺模型憑證」這個結論已被實測推翻

**原文主張（PR#6 `ACTIVATION.md`）：** 「The one thing genuinely missing: a model credential
in whatever process runs the runners.」並說明本容器沒有 API key 與憑證檔。

**本輪實測：** 在一個**同樣沒有**模型 API 環境變數、**同樣沒有**家目錄憑證檔的容器裡，
`claude -p --output-format json` 成功回應、`is_error=false`、exit 0。

**所以那句話錯在哪：** 它把「憑證不在我找的那兩個位置」講成「沒有憑證」。
實際上認證由 session 環境提供。**「檔案不存在」與「無法認證」是兩件事，而它們在 `ls` 的輸出上長得一模一樣。**

**替代說法（建議寫回 ACTIVATION.md）：**

> 本容器內 `claude -p` 可以認證（2026-09-19 實測），而且不是透過 API key 或憑證檔——
> 認證來自執行它的 session 環境。因此「換個地方跑就會認證」與「這裡不能跑」都不成立；
> **正確的問題是「哪一種執行主機會帶著可用的認證」，那要逐主機測，不能從本機的檔案清單推論。**

**仍然缺的是什麼（這才是 `GOV-R1-01` 要的分列）：** 見 §1 表格第 1、3、6、8、9 列。
最關鍵的一列是**第 6 列 reviewer 獨立性**，不是憑證。

### `GOV-R1-02` — 啟動入口的矛盾已在 ACTIVATION.md 內解掉，但別處還沒

`ACTIVATION.md` 現行版本已經寫對：「`controller.py` 自己的 CLI 仍拒絕 `mode != replay`；
`tick.py` 才是支援兩種模式的入口」。

**仍需同步的位置：** PR#6 的 `reviews/GOVERNANCE_EXECUTOR_RESPONSE.md` §4「啟用 live dispatch
必須修改程式」與 PR body。**預設禁用不等於不存在可啟動路徑**，兩種說法在操作者眼中差很多：
一個要他改程式，一個要他改設定。

### `GOV-R1-03` — 隔離邊界仍未成立，而且本輪又多一個證據

`runners.py` 對 subprocess 的 `env_passthrough_only` 預設為 `None`，live 範本未設該欄位；
容器隔離 ACTIVATION.md 自己也承認未接上。**本輪新增一項**：

> 從 executor session 內 spawn 的 `claude -p`，回傳的 `session_id` **與父 session 相同**，
> 並讀取了 31,908 個 cache token。

**後果：** 「executor 與 reviewer 用不同 subprocess」**不構成**角色隔離。
不同 run ID、不同工作區、不同權限，這三件事都要分別成立，而目前一件都沒有實測成立。

### `GOV-R1-04` — 次數與費用必須分開，而「訂閱所以沒有單次價格」與觀測不符

`ACTIVATION.md` 現行版本寫：「There is no per-call price to approve… What runs out is usage
and time, not dollars.」

**本輪實測：** 同一次 `claude -p` 呼叫，CLI **自己**回報 `total_cost_usd = 0.0415356`。

**正確的分列（建議寫回）：**

| 控制項 | 管什麼 | 現況 |
|---|---|---|
| `run_budget` | **次數**（一次 runner 呼叫 = 1），在派工前預留 | 預設 8，PR#6 已實作並測過 |
| `max_attempts` | 修復輪數 | 2 |
| `timeout_seconds` | 時間 | 2700 |
| **金額** | **每次呼叫的實際成本** | **CLI 會回報，因此可以記帳；目前沒有任何地方記它** |
| **授權** | 允許花多少 | `decisions.json` 現為「新增自動 API 支出上限 0」 |

**「訂閱」是計費方式，不是成本為零。** 次數上限擋得住失控迴圈，擋不住「每次都很貴」。
建議 G2 把 `total_cost_usd` 寫進 run 紀錄——它已經在回傳裡，不記它是選擇不是限制。

## 3. 本輪沒有做的事

* 沒有執行 `controller.py` 或 `tick.py`，沒有開任何 live dispatch。
* 沒有建立、修改或停用任何 routine／trigger。
* 沒有合併、沒有對外發送、沒有修改帳戶權限或 secrets。
* 沒有修改 `decisions.json`、`state.json` 或 `OPERATING_RULES.md`——那是 planner 的寫入範圍，
  本檔只提供建議（見 executor response）。
* **沒有把 G1 的結論寫成「已通過」。** G1 的驗收人是 reviewer，不是 executor。

## 4. 下一步（唯一）

把本檔與 executor response 交給**獨立 reviewer**，對本分支確切 head 取證。
G2／G3 需要修改 PR#6 分支上的 controller 程式，而本 session 被指定推送的是另一條分支——
見 executor response 的 `G1-D1`。

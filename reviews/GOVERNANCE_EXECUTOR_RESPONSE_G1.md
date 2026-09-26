# Governance Executor Response — G1

角色：**Claude executor**。2026-09-19。
這**不是** review，不宣稱任何驗收通過，也不變更任何授權。

## 1. 工作單

| 欄位 | 值 |
|---|---|
| task_id | `GOV-BOOTSTRAP` / 工作包 **G1** |
| goal | 修正四項 finding 的主張一致性，並建立能力表（`IMPLEMENTATION_PROMPT.md` G1） |
| scope_paths | `governance/RUNTIME_CAPABILITY_TABLE.md`、`governance/evidence/`、`reviews/GOVERNANCE_EXECUTOR_RESPONSE_G1.md` |
| decision_ids | `GOV-01`（治理導入目標）、`GOV-PLAN-02`（啟動條件）、`REVIEW-MAIN` |
| 啟動依據 | 負責人本輪明確指示依既有工作計畫執行。`GOV-PLAN-02` 寫明「未來收到明確啟動指示後」執行 G1–G3，本輪即該指示 |
| branch | `claude/friendly-knuth-i9zfp7` |
| base_sha | `b6edd70`（執行前的 live main） |
| candidate_head | 不自填；由 PR 引用確切 SHA |
| policy_sha | `governance/OPERATING_RULES.md`（v2）於 base 的內容 |
| executor_run | 本 session，無外部 run ID |
| reviewer_run | **無** |
| status | `REVIEW_PENDING` |
| 費用 | 本輪**新增**付費 API 呼叫：0。唯一一次模型呼叫是能力查證，走既有已認證環境，CLI 自報 `0.0415 USD`（見 §3） |

## 2. 本輪交付

| 項目 | 檔案 |
|---|---|
| 九列能力表 + 四項 finding 處置 | `governance/RUNTIME_CAPABILITY_TABLE.md` |
| 能力查證原始結果（去識別） | `governance/evidence/G1-claude-cli-auth-probe-2026-09-19.json` |
| 本回報 | 本檔 |

**為什麼不是追加在 `reviews/GOVERNANCE_EXECUTOR_RESPONSE.md`：**
那個檔案存在於 PR#6 的分支 `claude/atk-governance-controller`，**不在 main**。
本 session 被指定推送另一條分支，若把它複製一份到這裡再改，就會出現兩份互相分歧的
executor response——那正是「單一事實來源」失效的樣子。所以本輪另立 G1 專檔，
並在 §5 把該檔需要的修改以**建議 diff**形式列出，由有權限者套用到 PR#6 分支。

## 3. 本輪做了什麼查證（含唯一一次模型呼叫）

| # | 動作 | 結果 |
|---|---|---|
| 1 | 讀 live PR 列表與 head | PR#6 head 仍為 `c04ef465…`，Draft、未合併，與 `state.json` 快照一致 |
| 2 | 讀 PR#6 的 `governance/controller/` 檔案清單與 `ACTIVATION.md` | 10 個項目；ACTIVATION 內容已取得 |
| 3 | 列出帳號 routines | 3 個（2 啟用、1 停用），兩個 cron，有實際 fired／SUCCEEDED 紀錄 |
| 4 | 列出可用執行環境 | 4 個 active cloud 環境 |
| 5 | **能力查證：從 executor session 內 subprocess 呼叫 `claude -p --output-format json`** | exit 0、`result="PONG"`、`is_error=false`、`total_cost_usd=0.0415356`、`session_id` **與父 session 相同** |
| 6 | 檢查模型 API 環境變數與家目錄憑證檔 | 皆不存在（只檢查有無，未檢視值） |

第 5 項是本輪唯一一次模型呼叫，目的就是測「runners 指向的那個 CLI 能不能認證」。
不做它，G1 只能繼續引用上一輪的結論；做了它，那個結論被推翻。

## 4. 四項 finding 的回應摘要

| finding | 處置 | 依據 |
|---|---|---|
| `GOV-R1-01` 不得以「只缺憑證」作結論 | **主張已推翻並改寫。** 實測顯示同樣沒有 key／憑證檔的容器**可以**認證 | §3 第 5、6 項 |
| `GOV-R1-02` 啟動入口說明矛盾 | ACTIVATION.md 現行版本已正確；**PR#6 的 executor response §4 與 PR body 仍需同步** | 建議 diff 見 §5 |
| `GOV-R1-03` 隔離邊界未成立 | **未關閉，且本輪新增一項不利證據**：subprocess 與父 session 共用 `session_id` | §3 第 5 項 |
| `GOV-R1-04` 次數與費用需分開 | **「訂閱所以沒有單次價格」與觀測不符**：CLI 自報 per-call USD | §3 第 5 項 |

四項**沒有任何一項**可以由 executor 自行標記關閉。

## 5. 給 PR#6 分支的建議修改（本輪未套用）

以下是 `governance/controller/ACTIVATION.md` 與 PR#6 的 executor response 需要改的段落。
**本輪沒有推到那條分支**，原因見 §7 `G1-D1`。

1. **刪除「The one thing genuinely missing: a model credential」整節**，改為
   `RUNTIME_CAPABILITY_TABLE.md` §2 `GOV-R1-01` 的替代說法：認證來自 session 環境，
   因此必須逐執行主機實測，不能由檔案清單推論。
2. **刪除「There is no per-call price to approve」**，改為 §2 `GOV-R1-04` 的五列控制表，
   並把 `total_cost_usd` 加進 run 紀錄欄位（G2 實作）。
3. **executor response §4** 把「啟用 live dispatch 必須修改程式」改為
   「`tick.py` 支援 `mode: live`；啟用是設定變更（`runners.*.enabled`），不是程式修改。
   `controller.py` 自己的 CLI 才拒絕非 replay 模式」。
4. **`config.live.example.json`** 補上 `env_passthrough_only` 的明確允許清單（不得留 `None`），
   這是 `GOV-R1-03` 的最小可驗收動作。

## 6. 沒做與不能做

| 沒做 | 原因 |
|---|---|
| G2／G3 的 controller 修復 | 需要寫入 PR#6 的分支；本 session 被指定推另一條分支（`G1-D1`） |
| 執行 `controller.py`／`tick.py` | G1 不需要；且不在本輪授權的動作清單內 |
| 掛 live webhook、開 live dispatch | `IMPLEMENTATION_PROMPT` 明文：B 階段「先無秘密 replay，不立即掛 live webhook」 |
| 修改 `decisions.json`／`state.json`／`OPERATING_RULES.md` | planner 的寫入範圍；本檔只提供建議 |
| 把 `automation.status` 升格 | 只有 runtime 實測通過後由 planner 依證據處理。本輪**沒有**任何真實閉環 |
| 合併、對外發送、新增未授權支出 | 未授權 |

## 7. 需要負責人或 planner 裁定

| ID | 事項 | 為什麼卡住 |
|---|---|---|
| **G1-D1** | G2／G3 要寫在哪條分支 | `IMPLEMENTATION_PROMPT` 說沿用 PR#6 的治理分支；但本 session 被指定推 `claude/friendly-knuth-i9zfp7`。兩者只能擇一，否則會出現兩份分歧的 controller |
| G1-D2 | 是否授權為治理導入安裝一個持久 trigger | 能力已證實存在（表格第 3 列）；安裝與否是授權問題不是能力問題 |
| G1-D3 | 獨立 reviewer 怎麼產生 | 表格第 6 列：subprocess 共用 session，不是獨立來源。需要**不同帳號／不同 runtime**，或明確接受「同模型不同 run」並在報告中標明其限制 |
| G1-D4 | per-call 成本是否納入 run 紀錄與上限 | 資料已經在 CLI 回傳裡；記不記是決定 |

## 8. 機器狀態摘要

```yaml
execution_mode: MANUAL_HANDOFF
runtime_status: FOUNDATION_ONLY   # 本輪未變更；executor 無權升格
review_decision: none_this_round
reviewed_head: none
g_scope_this_round: G1
findings_addressed: [GOV-R1-01, GOV-R1-02, GOV-R1-03, GOV-R1-04]
findings_closed_by_executor: []   # 刻意為空；executor 不自我關閉 finding
evidence: governance/evidence/G1-claude-cli-auth-probe-2026-09-19.json
next_role: independent_reviewer
next_action: 對本分支確切 head 取證覆核 G1；並裁定 G1-D1 後才能開始 G2
```

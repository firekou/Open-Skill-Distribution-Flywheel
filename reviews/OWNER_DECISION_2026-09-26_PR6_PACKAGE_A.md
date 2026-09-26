# 負責人授權紀錄：PR6 controller 包 A（第三輪限定修復，2026-09-26）

- **記錄者**：Claude executor，session `session_01RFeCsTYkVywjHvXk7od7Ab`
- **本檔的定位**：只是紀錄，不是 executor 自己給自己的授權。

## 來由

2026-09-26 負責人在 Claude Code 對話裡重新下達治理導入指示，內容是「完成最小自動執行與獨立 review 交接實作；使用獨立治理工作分支，建立 Draft PR」。

executor 讀取最新治理入口後，發現與已記錄的狀態衝突：
- state.json rev 55 的 `GOV-BOOTSTRAP` 為 BLOCKED；
- PR6 R4 已用完兩輪修復（2/2）；
- `no_parallel_controller: true`；
- 包 A 為 `BACKLOG_NOT_DISPATCHED`；
- R4 的 retry gate 要求「新的明確授權、最小範圍、可驗證的隔離環境」，重啟 controller 才能繼續。

executor 因此沒有照指令另開分支，而是先用選項題問負責人。

## 逐字紀錄

**題目**：這份指令要求的 controller（自動交接器）其實已在 PR6 做完並達 REPLAY_VERIFIED（我剛重跑：146 測試全過、整輪重放到結案）。但 GPT 第 4 輪覆核擋下 4 項，兩輪修復上限已用完，治理紀錄寫明「不開第三輪、不另建第二份 controller」。你這次的指令是否等於授權重啟？

**負責人答案**：**授權包 A（建議）**，說明文字為：在既有 PR6 分支修 GPT 指出的 3 項純程式問題＋2 項次要問題，全部離線、附正負對照，送 GPT 覆核。不建新 controller。完成後仍不是 ACTIVE：還缺隔離環境（包 B）與真實啟動授權。

## 授權範圍

- **分支**：沿用 `claude/atk-governance-controller`（PR #6）。不建第二份 controller，也不開新的治理 PR。
- **修正項目（包 A）**：
  - `GOV-R2-02`：租約失效後仍可能啟動 executor；
  - `GOV-R2-03`：不相干的分支移動被當成本工作成果；
  - `GOV-R2-05`：期限過後仍可能 Popen；
  - `P2-ISOLATION-BASELINE`：隔離探測缺少未包裝的對照組；
  - `P2-ATOMIC-SPEND-INTENT-TASK`：spend、intent 與 task 寫入不是同一筆交易。
- **不在範圍內**：
  - `GOV-R1-03`（包 B）：仍等可驗證的隔離後端。本 session 的環境有 docker CLI，但 daemon 沒有啟動，**不算已具備**。
- **修復輪次**：這是負責人明示授權的第三輪，只限上述五項。未來若還要再修，必須再取得授權；不以改名規避上限。
- **不授權**：
  - 真實 executor／reviewer 模型呼叫；
  - 安裝觸發器或 webhook；
  - 新增付費；
  - merge、部署；
  - 修改 secrets、權限或可信政策；
  - 把狀態標為 ACTIVE。
- **驗收**：由 GPT 在新的精確 SHA 上獨立覆核。executor 不自評 CLOSED 或 APPROVED。

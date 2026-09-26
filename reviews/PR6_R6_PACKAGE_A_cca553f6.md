# PR6 R6：Package A 精確 head 獨立覆核

## 1. 執行者

- 誰執行：Claude 在既有 session `session_01RFeCsTYkVywjHvXk7od7Ab` 實作並提交 Package A；GPT／Codex 以不同 reviewer run 對 GitHub live PR、精確 head、來源碼、測試、mutation、replay 與事件去重做獨立覆核。
- 經過哪些 agent（依順序）：Claude executor → GPT／Codex independent reviewer。
- 人類參與：負責人明確授權既有 PR #6 分支的第三輪限定 Package A；本次覆核期間無人類執行測試、合併、部署或憑證操作。

## 2. 小目標進度

- 這次往哪個小目標前進：判定 PR #6 精確 head `cca553f6291d14a7abbb6ef8c42d377a127fd9f6` 是否在負責人限定的 Package A 範圍內，真正關閉 R4 的三項程式阻擋與兩項 P2 缺口。
- 屬於哪一個小目標階段：治理基礎的離線可靠性修復；它支援藍圖各階段的可追查交接，但不是產品採用階段本身。
- 有沒有前進：有 —— 證據：19/19 Package A 聚焦測試通過、8/8 Package A mutants 被攔截、replay 到 `COMPLETE / REPLAY_VERIFIED`、tick 首次 exit 10 且同 event 重送 exit 20；R4 的 `GOV-R2-02`、`GOV-R2-03`、`GOV-R2-05`、`P2-ISOLATION-BASELINE`、`P2-ATOMIC-SPEND-INTENT-TASK` 在此精確 head 關閉。
- 遇到的困難：完整 165-test suite 在 reviewer runtime 出現 2 個既有 process-group 測試失敗、1 個 isolation 測試 skip；相同兩個 failure 在舊 reviewed head `25457fbd...` 也重現，單獨重跑其中一個負控制可通過，另一個在測試函式進入被測 kill 邏輯前即因 shell child 啟動競態失敗。`mutate_g123.py` 因同一 baseline 不綠而無法在本 runtime 重現作者的 50/51 結果；不得把作者報告升格為獨立通過。
- 卡在哪裡、需要誰做什麼決策：Package B `GOV-R1-03` 仍卡在不存在的合格隔離後端。需要負責人日後提供或授權一個能獨立證明未信任來源、認證、網路、檔案與工具權限隔離的 runtime，才可開 Package B；目前不得啟動真實 executor/reviewer 閉環。
- 缺乏什麼資訊：缺 Package B 的 backend identity、隔離政策、可重放正負控制與獨立 run evidence；也沒有真實 Claude persistent launcher 或 end-to-end controller run。
- 覆核結論：`APPROVED_WITH_CONDITIONS`，只針對已授權的 Package A。PR #6 整體仍為 `BLOCKED / FOUNDATION_ONLY`，不得 merge、deploy、安裝 launcher、使用 secrets、付費或標為 ACTIVE。
- 是否進入下一個小目標：有條件。Package A 到此停止，不派第四輪同類修復；下一治理小目標是 `GOV-PR6-PACKAGE-B-ISOLATION-EVIDENCE`，驗收為五項隔離性質皆有 working baseline、wrapped negative control、backend/policy/run ID、exact SHA 與退出碼，停止點是任一性質未知或失敗即維持 fail-closed。
- 下一階段或修復包是否已上傳 GitHub：Package A 的 owner authorization、submission、executor response 與本 review 均已上傳 main；Package B 沒有新增執行包，原因是未獲 Package B 授權且沒有可用隔離環境，不能用留言擴張權限。既有 `reviews/CONTROLLER_MINIMAL_PACKAGE_PROPOSAL.md` 與 `PR6_R5_SCOPE_REDUCTION_7de3043.md` 已記錄其驗收方向。
- 執行端交接狀態：Package A 已交付並完成獨立覆核；work id `GOV-PR6-R2`、revision `3`、source head `25457fbd2ff02a900d55538eb4e2fa0893663c31`、result head `cca553f6291d14a7abbb6ef8c42d377a127fd9f6`、dedup key `firekou/Open-Skill-Distribution-Flywheel:6:GOV-PR6-R2:3:25457fbd2ff02a900d55538eb4e2fa0893663c31:package-a`。Package B 為 `WAITING_QUALIFYING_ISOLATION_BACKEND`，未派工；下一 checkpoint `GOV_PR6_PACKAGE_B_QUALIFYING_RUNTIME_OR_OWNER_AUTHORIZATION`。

### 驗收矩陣

| Finding | 獨立判定 | 證據 | 剩餘界線 |
|---|---|---|---|
| GOV-R2-02 lease-loss launch gate | CLOSED for Package A | 每 run 單調 cancellation token；lease monitor 先設 token；dispatch/clone/checkout/work-order/launch 前與 Popen 後檢查；4 個新測試及 mutants 通過 | 不代表有合格隔離 runtime |
| GOV-R2-03 effect attribution | CLOSED for Package A | `ATK-Work-Receipt: <task>/<intent>` 綁定 work order；無 receipt 的 head 與 branch move fail closed；5 個新測試含真 git history 通過 | 真實 CLI 是否遵守 trailer 仍未知；不遵守時停止而非誤放行 |
| GOV-R2-05 absolute deadline | CLOSED for Package A | Popen 前重算 absolute deadline；剩餘少於 1 秒拒絕；3 個正負控制通過 | 未執行真實模型程序 |
| P2-ISOLATION-BASELINE | CLOSED for Package A | production probe 先跑 unwrapped baseline；baseline 失敗回 `None`；4 個控制通過 | GOV-R1-03 的完整隔離性質仍未滿足 |
| P2-ATOMIC-SPEND-INTENT-TASK | CLOSED for Package A | spend 與 task open-intent 同一 lease-fenced CAS；round deadline owner+generation fenced；3 個控制通過 | controller 仍未獲 live 啟動授權 |
| GOV-R1-03 | OPEN / BLOCKING real loop | 現有環境沒有可證明完整五項性質的 backend | Package B 等 runtime 與明確授權 |

### 精確 head 與獨立重放

- Live PR：Draft、open、unmerged、mergeable；base `main`，head `cca553f6291d14a7abbb6ef8c42d377a127fd9f6`。PR body 仍指向舊 head，不作授權或覆核來源。
- Exact-head GitHub checks：workflow runs 0、commit statuses 0、PR reviews 0。GitHub mergeable 不等於治理批准。
- Diff：相對 R4 程式 head `25457fbd...` 共 1 個 Package A code commit；17 paths（包含先前已審的 scope proposal 與 append-only executor response），controller code、tests、evidence 與限定文件相符；`git diff --check` 及 `py_compile` 通過。
- `python3 governance/controller/test_controller.py <5 classes>`：19 tests，exit 0。
- `python3 governance/controller/evidence/mutate_package_a.py`：5 個原版 class PASS，8/8 mutants caught，exit 0。
- `python3 governance/controller/replay.py`：`COMPLETE / REPLAY_VERIFIED`，exit 0，無模型與網路。
- `tick.py --drive`：完整走到 COMPLETE，exit 10；同一 source event redelivery 為 duplicate，exit 20。
- 完整 suite：165 tests，2 failures、1 skip；在舊 head `25457fbd...` 為 146 tests、相同兩個 failures、1 skip。因此列為既有 portability/flakiness 殘餘風險，不把它偽裝為 165/165 的 reviewer 結果，也不視為 Package A regression。

## 3. 目標藍圖對齊

- 現在的目標藍圖：讓別人借助我們的 AI 基礎（選模型與工具、判斷與修正、可重用的 skill）完成他想做的工作，並在別人的成功中累積我們自己的能力。
- 目前處在藍圖哪一個階段：產品主線在第 4 階段「技術分享與分發」，PR #22 等負責人 merge 與 post-merge pin；本次 controller 是跨階段治理基礎，不得冒充第 5 階段實際採用。
- 這次有沒有遵照藍圖：是 —— 理由：只修復會讓交接重複執行、接受錯誤成果或在失租／過期後啟動 child 的最小可靠性缺口，且沒有讓治理 runtime 阻塞產品分發主線。
- 距離藍圖方向：前進 —— 理由：交接器的五項離線可靠性缺口已從待修變成精確 head 可重放的通過；但沒有新增非作者使用、再次使用、採用或經濟成果證據，所以只算治理基礎前進，不算產品採用前進。

## 4. 本次執行的意義

這次確認 Package A 不只是文件聲稱修好，而是失去租約、期限耗盡、別人推了同一分支、探測本來就失敗，以及扣額與意圖分裂這五種情況，現在都有可重放的攔截證據。負責人因此可以把這五項從 Package A 待修清單移除，但仍不能把 PR #6 當成可上線 controller；真正缺的是隔離環境與持久 executor 接線。

產品藍圖不必等待 Package B：PR #22 的發布入口仍依它自己的 owner merge gate 往前。治理這條線則停在 `FOUNDATION_ONLY`，直到有合格 runtime 與新授權，避免再派一個在現有環境注定無法驗收的工作包。

### Machine-readable decision

```yaml
decision: APPROVED_WITH_CONDITIONS
approval_scope: "PR6 Package A only"
reviewed_base: "25457fbd2ff02a900d55538eb4e2fa0893663c31"
reviewed_head: "cca553f6291d14a7abbb6ef8c42d377a127fd9f6"
policy_sha: "38ee2303fd4c702af6d583a00dd9ed6f871ce54f"
highest_evidence:
  github_state: VERIFIED
  source_review: VERIFIED
  package_a_runtime: INDEPENDENTLY_TESTED_OFFLINE
  full_suite: PARTIAL_PLATFORM_FLAKY
  real_model_runtime: NOT_VERIFIED
closed_findings:
  - GOV-R2-02
  - GOV-R2-03
  - GOV-R2-05
  - P2-ISOLATION-BASELINE
  - P2-ATOMIC-SPEND-INTENT-TASK
blocking_findings:
  - GOV-R1-03
conditions:
  - "PR6 remains BLOCKED / FOUNDATION_ONLY overall."
  - "No merge, deployment, launcher installation, credential use, paid call or ACTIVE promotion."
  - "Do not dispatch Package B without a qualifying runtime and explicit authorization."
  - "Treat 165/165 and mutate_g123 50/51 as author-reported on this reviewer runtime; the independent full-suite baseline is flaky."
next_checkpoint: "GOV_PR6_PACKAGE_B_QUALIFYING_RUNTIME_OR_OWNER_AUTHORIZATION"
```

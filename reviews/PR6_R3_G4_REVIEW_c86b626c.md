# PR6 R3 G4 覆核 c86b626c

## 給負責人的兩分鐘簡報

**整體目標：** 用可靠交接支援 ATK 工具接入、分發與採用，不把治理當成產品交付的無限前置工程。
**本輪處理：** 接管時發現新交付，獨立閱讀 c86b626c 的 controller/runner/store/tick 與版本差異。
**目前進度：** 上輪問題有實作改善，G4 仍 BLOCKED。
**本輪成果：** OBSERVED 續租、派工前預留、事件與狀態原子提交、工作單輸出已接上部分路徑；VERIFIED GitHub compare 無其後 controller 程式差異。
**還有什麼風險：** 隔離後端只被探測但未用來跑工作；deadline 未真正限制程序；intent 恢復與可信政策載入順序仍有缺口。
**需要負責人決定：** 無。沿既有有限修復包交接，無新增費用或部署。
**下一步與停止點：** 完成本文件列出的原 finding 殘餘修復並附隔離測試，再送同批獨立 reviewer；兩輪上限不因換 ID 重置。
**審查結論：** BLOCKED。

## 審查定位

- repo: firekou/Open-Skill-Distribution-Flywheel / PR6，Draft、open、未合併。
- reviewed_base: 86421c903563a16ca888a4aed10bd614e223ca0e
- reviewed_head: c86b626c8666b563e9e10413c5a967a4f94328cb
- observed_live_head: a21fa1e21f4f361bd7df2d379c2711bd3ac28c7b
- observed PR base: a4d664568ecda1025c43a0f4bfae7b1771e28a78
- 作者指定 policy: 38ee2303fd4c702af6d583a00dd9ed6f871ce54f
- Reviewer：GPT/Codex，2026-09-21；未修改受審實作。
- 來源：上述精確 head 的 controller.py、runners.py、store.py、tick.py；main 的 GOVERNANCE_G4_RESUBMISSION_c86b626c；PR body、comments、GitHub compare。
- code head → live head：8 commits，7 個文件／review 證據檔案差異，沒有 controller 程式差異；main 規劃與 state 仍須獨立按可信入口讀取。
- live head status API 回 statuses=[]；PR-triggered workflow API 回 workflow_runs=[]。這不證明所有類型 checks 都不存在，也不是 CI 通過。
- repo 的 REVIEW-MAIN 優先於通用 skill 的分支存放預設；review 與帳本仍寫 main，避免改動受審 head。

## Finding 處置與最小修復包

| 原 finding | 獨立可觀察改善 | 本輪判定 |
|---|---|---|
| GOV-R2-01 | render_command 改為具名 placeholder 替換，JSON 不再直接 str.format | PARTIAL；CLI envelope 仍未接 |
| GOV-R2-02 | invocation UUID、renew thread、成功回傳後 holds_lease | PARTIAL；失租終止與原子 fencing 未完成 |
| GOV-R2-03 | dispatch 前 record_intent；成功路徑 commit_event_and_task | OPEN；恢復不讀 open intents |
| GOV-R2-04 | policy SHA 比對；clone 外工作單檔 | OPEN；驗證前 import guard、dirty checkout、同 UID 檔案邊界 |
| GOV-R2-05 | add_spend 移至派工前；保存 round_deadline | OPEN；deadline 只送提示、不限制 runtime |
| GOV-R1-03 | 宣告 container 時 probe 後端 | OPEN；實際 Popen 仍在宿主 |

以下均為 P1、OBSERVED 原始碼路徑判定；沒有將靜態閱讀寫成動態重現。

### 1. GOV-R1-03：探測隔離工具可用，不等於在隔離工具內執行

_require_isolation 可保存 _container_backend，但 run 的 Popen 直接執行 cmd，沒有使用選定的 backend 包裝或建立隔離。宿主上只要 probe 成功，就放行原本要求隔離的角色，實際工作仍在宿主 cwd/env 執行。

**修復：** 後端必須承載真正 runner，約束來源唯讀、寫入位置、網路及宿主憑證可達性；尚未接通就拒絕 live 隔離角色。
**驗證：** 讓 probe 可用、實際命令嘗試讀合成宿主秘密／寫來源／觸達禁止路徑，必須在真正 runner 邊界被拒絕；禁止用真實模型呼叫探針。

### 2. GOV-R2-05：round_deadline 尚未被強制

_order 的 elapsed 仍是本 step 的 elapsed；deadline_seconds 使用 max(1, remaining)，過期仍變成 1。SubprocessRunner.run 只是將 deadline_seconds 代入提示，實際 limit 仍直接取 config.timeout_seconds；communicate(timeout=limit) 未取剩餘時間最小值，clone 也先行消耗時間。送審摘要「runner 取較小值」與實作不符。

**修復：** 過期先拒派工；使用持久 absolute deadline，在 clone、checkout、啟動前、等待期間重新計算剩餘值。實際超時參數取剩餘期限與角色上限較小值。
**驗證：** 剩餘 0 秒不得啟動；剩餘短於 runner timeout 時確實提早終止；跨 step／重啟不重設。用無模型 stub 及虛擬時鐘。

### 3. GOV-R2-03：寫了 intent，恢復仍未使用

step 在取得租約後直接依 status 派工，沒有查 open_intents 或 reconciliation。發生副作用後 crash、尚未保存结果的任務可再次派工。drive 仍從 event/0 開始，遇 duplicate NOOP 即停，部分完成後的同源事件重送不能續行。RunnerError 一律關 intent 也未区分外部副作用是否未知。

**修復：** 派工前檢查未決 intent，核對結果後才續行；未知結果保留可恢復狀態。完整定義部分完成的 drive 重送，不能換事件 ID 盲重跑。
**驗證：** 在外部結果後、本地保存前 crash，重新打開 Store／Controller，證明不重派且能恢復；包含失敗結果未知及 drive 部分完成。

### 4. GOV-R2-04：policy guard 先 import，之後才驗證

tick.build 第一行便 load_guard，執行模組頂層；live 分支的 SHA 驗證在後面，第二次 load_guard 亦先於 guard 路徑邊界檢查。rev-parse HEAD 不查 dirty/untracked guard。clone 外的 chmod 0400 工作單仍由同 UID 擁有，可 chmod 或刪除重建，不能宣稱 PR 程式「無法改寫」。

**修復：** 所有驗證先於第一次 import，確保實際 guard blob 對應釘住的政策版本，拒絕 dirty/錯路徑，統一路徑解析。可信工作單交由真正唯讀掛載或隔離權限交付，不以檔案位置／mode 代替隔離。
**驗證：** 帶頂層 sentinel 的錯誤 guard，在 SHA/路徑/dirty 驗證失敗時 sentinel 永遠不執行；從非 repo cwd 測相對路徑；runner 無法改寫工作單。

### 5. GOV-R2-02：成功路徑 fence 與 state commit 仍分離

renew thread 的失敗只記入 failures，沒有即時取消 runner；等 runner 返回才讀。_fence 為獨立 read，後續 commit_event_and_task 不檢查 lease owner/期限；租約若在二者間轉移，舊 worker 可使用新 revision 更新 task。finally release 在其他 owner 接手後亦可拋例外，掩蓋原先 NOOP。

**修復：** 持有者／租約 generation／期限驗證與結果提交放同一持久交易；失租後取消工作並阻止後續副作用，保留未知 intent。release 不應解除別人租約或掩蓋主要結果。
**驗證：** 兩程序跨 TTL、在 fence→commit 間接管、失租但 stub 尚未退出；舊 worker 不能推進狀態。不是只調大 TTL。

### 6. GOV-R2-01：範本字串修復不等於 CLI 契約完成

parse_verdict 仍直接要求 stdout 根物件含 new_head 或 review，沒有 CLI result envelope 的拆解。作者亦明示沒有真實 CLI 契約端到端驗證。

**修復：** 依可查驗的 CLI 輸出定義 adapter，使用去敏的真實格式 fixture／無模型 stub；缺實際格式證據就明列，不猜 schema。
**驗證：** shipped template → adapter → stdout envelope → verdict 的完整無模型路徑，兩角色及 error/unknown output 負控制。

## 證據、範圍與停止條件

本次獨立取得精確 SHA 原始碼與 GitHub 比較結果，沒有 import 或執行 PR 模組。前一輪 reviewer 隔離不可用的限制未解除，本輪未重跑 108 tests、34 mutations、replay 或付費探針；這些仍是作者 REPORTED，不是本 reviewer VERIFIED。沒有新 capability 證據，不反覆跑同一隔離失敗檢查。

本 review 接續原 blocking findings，不另開平台建設、benchmark 或產品功能。PR5 933446ab 無新成果，本輪不重做其 review；仍需另一獨立隔離 reviewer 的既有重放。產品主線不以 PR6 完整 ACTIVE 為前提。

本批 R2 finding 的第一次修復已送回，本次是限定的第二次修復交接。若再回來仍缺相同邊界證據，不更名重開無限輪次；Planner 縮小可交付範圍並保留未完成 runtime。不能將重複 self-test 當獨立驗收。

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: 86421c903563a16ca888a4aed10bd614e223ca0e
  reviewed_head: c86b626c8666b563e9e10413c5a967a4f94328cb
  observed_live_head: a21fa1e21f4f361bd7df2d379c2711bd3ac28c7b
  highest_evidence: VERIFIED
  independent_runtime_verified: false
  blocking_findings: [GOV-R2-01, GOV-R2-02, GOV-R2-03, GOV-R2-04, GOV-R2-05, GOV-R1-03]
  conditions: []
  owner_decisions: []
  next_checkpoint: 同批第二次限定修復及隔離證據，精確新 SHA 送獨立覆核
  invalidates_when: [reviewed content changes, evidence changes or fails]
```

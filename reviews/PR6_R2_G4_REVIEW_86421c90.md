# PR6 G4 獨立 review — 86421c90

## 給負責人的兩分鐘簡報

**整體目標：** 讓使用者透過可靠的 AI 基礎完成工作，逐步成熟 routing、intelligence、skill 與治理。
**本輪處理：** 獨立讀取 G1–G3 與 C0/C1 交付，核對精確程式版本、可信政策及實際接線。
**目前進度：** 完整 executor response 已收到；本輪 G4 結論為 BLOCKED，runtime 維持 FOUNDATION_ONLY。
**本輪成果：** 已核對送審版本，並以純資料操作 REPRODUCED 兩個 live 命令範本的 KeyError；VERIFIED controller 沒有呼叫已新增的續租及 intent API。
**還有什麼風險：** runner 尚不能依範本啟動；長任務／崩潰恢復可能重複工作或遺失進度；權限隔離及用量上限尚未達標。
**需要負責人決定：** 目前修復規劃無。持久觸發器、實際模型試行及新增支出仍依各階段既有授權處理。
**下一步與停止點：** Claude 依 IMPLEMENTATION_PROMPT 的本輪補充修復與補證，提交新 SHA；Reviewer 完成必要隔離驗證後再判 G4。不安裝排程、不合併。
**審查結論：** BLOCKED。

## 身分與範圍

- Repository：firekou/Open-Skill-Distribution-Flywheel；PR #6，Draft，未合併。
- 前次審查比較基準：c04ef465d000968b86065e7608a8c92761458c6d。
- 本輪程式 head：86421c903563a16ca888a4aed10bd614e223ca0e。
- 指定可信政策：d92d082bfcee7002d737e2c3ee2914d2b1fa804c。
- 讀取時 PR base main：bc2acbdc4143f12c1c5660dd2bc8c1e0b1ba6015。
- 讀取時 live head：75976be1db636ef72d76206b387583fb3cc03443。
- code head → live head 的 GitHub compare：ahead 2；淨差異只有 reviews/GOVERNANCE_G4_SUBMISSION_86421c90.md，沒有程式差異。此核對不把 code head 當永遠有效的 live head。
- Reviewer：本次 GPT/Codex review session，2026-09-21；未修改受審實作。本次只寫 main 的 review、規劃與摘要。
- 範圍：controller、store、runner、tick、live/replay 範本、相關測試原始碼、response §10、CLOUD_HANDOFF_WIRING、NEXT_STAGE_C2_C3_G5_G6。
- 排除：PR5 產品驗收、實際認證探針、模型呼叫、正式 runtime、持久 trigger 與外部採用。

## 驗收表

| 驗收 | 結果 | 證據等級／來源 | 缺口 |
|---|---|---|---|
| 精確送審定位 | 已核對 | VERIFIED：GitHub PR metadata 與 compare | 後續新程式 SHA 需重新 review |
| live adapter 可依範本啟動 | 不通過 | REPRODUCED：下列 reviewer 純資料檢查 | R2-01 |
| 長任務互斥與續租 | 不通過 | OBSERVED 原始碼；VERIFIED AST 無續租呼叫 | R2-02；未獨立做並行 runtime |
| crash／事件恢復 | 不通過 | OBSERVED 狀態提交順序；VERIFIED 無 intent 呼叫 | R2-03；未獨立 crash injection |
| 工作單與 policy 綁定 | 不通過 | OBSERVED live build、範本、runner 邊界 | R2-04 |
| run 與整輪時間上限 | 不通過 | OBSERVED 失敗分支與 step 計時 | R2-05 |
| 不可信 code 與 reviewer 權限隔離 | 未達標 | OBSERVED 宣告式 isolation_level；作者明示尚未接線 | GOV-R1-03 維持 OPEN |
| 92 tests／26 mutants | 未獨立重跑 | REPORTED：response §10.4；已讀測試原始碼 | 不以測試數取代實際接線驗證 |
| C0/C1 | 可保留為盤點／設計草案 | OBSERVED 文件；跨 session／平台能力為作者報告 | 下列接線修訂，尚非驗收通過 |
| G5/G6／外部使用者成功 | 未驗證 | OBSERVED 作者未完成的明示 | 不升 MANUAL_RUN_VERIFIED 或 ACTIVE |

## Blocking findings

### GOV-R2-01 — P1：live 範本在模型啟動前就失敗

**證據：** runners.py:399 以 Python str.format 展開每個 command 元素。config.live.example.json 內 executor 與 reviewer 指示含未跳脫的 JSON 大括號。將精確版本 JSON 當資料載入，只執行相同標準函式展開，即分別得到 KeyError: '"new_head"' 與 KeyError: '"review"'。沒有執行 PR code 或模型。

**影響：** 範本即使補齊能力並啟用也無法派工；這個例外並非 RunnerError，不走預期的結構化失敗回報。

**修復：** 修正命令生成方式，讓 JSON 常值安全保留；把錯誤轉成可追查的設定失敗。完成真實 CLI output envelope → 內層 verdict 的明確契約，不只讓 stub 回傳裸 JSON。範本 reviewer 目前也沒有取得 controller 預期的完整 reviewer identity。

**驗證：** 直接載入 shipped live template，使用不呼叫模型的 stub 跑完整 SubprocessRunner.run。覆蓋兩個角色、實際輸出包裝、無效 JSON、非零退出、完整 SHA 與 reviewer identity 綁定。不能另造一份不含原範本問題的測試設定就聲稱完成。

### GOV-R2-02 — P1：續租 API 未接到 controller，租約無法保證長任務互斥

**證據：** Controller.step:281 acquire 後同步呼叫 runner；整個 controller 沒有 renew 或 holds_lease 呼叫。範本 lease_seconds=900，而單 runner timeout=1200，尚未包含 clone。Store.acquire 只對「不同 owner 的未過期租約」拒絕；相同 config.controller_identity 的另一 tick 可再次取得同一 task。新增測試只證明 Store.renew 能延長期限，未證明 controller 會續租。

**影響：** 不同 worker 在租約到期後，或使用相同靜態 identity 的兩個 invocation，可能對同一 task 同時啟動工作。這是原始碼路徑判定，並非本 reviewer 已完成並行動態重現。

**修復：** 為每次 worker invocation 配置唯一身分；續租／有效持有檢查接入 runner 生命週期，失租時停止或 fence 舊 worker 的後續提交。避免只把 TTL 調大而保留相同 owner 可重入的漏洞。

**驗證：** 隔離環境兩個真實程序、相同啟動設定、同 task，不同事件；stub 持續超過原 TTL。證明只有一次有效 dispatch、失租者不能提交，並覆蓋崩潰後可恢復。

### GOV-R2-03 — P1：intent 未使用，事件與狀態分開保存留下崩潰窗口

**證據：** controller 沒有 record_intent／open_intents／close_intent 呼叫。executor 外部工作完成後才 add_spend，再 mark_processed:359，最後 set_task:360。review 路徑亦先 mark_processed:407 再更新結果。若在 mark_processed 後中止，重送事件會直接 NOOP，但 state 尚未推進；若在副作用後、本地保存前中止，沒有 durable intent 可供先查證。原始碼註解聲稱這個順序會重新執行，與 dedup 分支相反。drive 每次由 event/0 開始且遇 NOOP 即停，也缺少部分成功後的續行策略。

**影響：** 交接卡住、重複模型工作或無法判定外部推送是否已完成。

**修復：** 真正接上 dispatch intent 與結果 reconciliation；event 消耗和 task transition 原子保存。未知副作用先對外部結果查證；設計 drive/tick 重送及補漏的持久恢復點，不能靠換 event ID 盲重跑。

**驗證：** 在 dispatch 前後、push 後、本地結果保存前、event 與 transition 邊界做 crash injection。重啟及重送後既不漏進度也不重做未知副作用。測 Store API 自身不足以結案。

### GOV-R2-04 — P1：可信 policy 與工作單欄位停留在記憶體，未完成 live 交付契約

**證據：** tick.build 只 load_guard(config.guard_path)，沒有驗證 checkout 的 policy SHA；controller.policy_sha() 沒被 live build 使用，範本沒有 policy_sha，Controller 退回 "unrecorded"。就算填入 config.policy_sha，目前也未驗證它與實際載入檔案相符。runner.run 只將 prompt_file/head 代入 command，沒有傳遞已組裝的 goal、scope、acceptance、decision_ids、run_identity、deadline 等工作單。相對 prompt_file 在 PR clone 下讀取，不能充當可信派工契約。

**影響：** 記錄欄位存在不等於實際 runner 受相同契約約束；policy 版本與 reviewer binding 不可驗證。

**修復：** live 模式從可信且已驗證的政策 checkout 載入並釘住完整 SHA，dirty／錯配 fail closed；以 PR 無法改寫的工作單檔或標準輸入交付完整契約，明確區分待審 PR 資料與可信指令。scope/command 欄位哪些由平台強制、哪些僅指示必須明示。

**驗證：** 從 shipped tick/live 入口搭配 stub，檢查 runner 實際收到的工作單；錯配 policy、PR 修改同名 prompt、偽造 reviewer identity 必須拒收。不能只測 _order 字典有 key。

### GOV-R2-05 — P1：失敗呼叫不計 run，整輪時計每個 step 重置

**證據：** executor/reviewer 的 add_spend 位於成功回傳之後；RunnerError 分支先返回，已啟動但失敗／逾時的工作不計入 run。_order 的 cost+1 只是本次 guard 的數值，沒有持久 reservation。step:274 每次重設 started，不能證明範本宣稱的整輪 2700 秒限制。

**影響：** run_budget 無法涵蓋已消耗的失敗工作，崩潰亦可遺失用量；多步總耗時可超過宣告的整輪限額。

**修復：** 派工前持久預留，保存 started/unknown/completed 狀態；已開始或結果未知的工作不能當作零消耗。區分 run 次數、provider 回報用量／估算、實際帳單、額外 API 支出授權。保存跨步驟及重啟有效的 round deadline，runner 取剩餘期限與自身上限的較小值。

**驗證：** stub 啟動後失敗、逾時、crash，以及跨多個 step／重啟的虛擬時鐘；不因失敗重置 cap 或 deadline。

### GOV-R1-03 — P1／既有 OPEN：權限隔離仍未完成

**證據：** 作者已明示 process_env 不是邊界；新增 container 字串只表示操作者宣告，沒有建立或驗證容器。executor 與 reviewer 仍可在相同主機讀取共同 HOME／宿主能力；拒傳 GITHUB_TOKEN 不證明 reviewer 無其他寫入途徑。

**影響：** 不可信 PR code 與憑證的隔離、reviewer 權限独立，尚不能作為 G2 通過的依據。

**修復及驗證：** 接上最小可用隔離後端，或持續拒絕所需邊界尚不存在的 live 角色；使用合成秘密、唯讀來源、無寫入憑證、拒絕未授權網路／宿主認證路徑的負控制驗證。不要為驗證「拿不到憑證」再發真實模型呼叫。不要求為本修復另建大型平台。

## C0/C1、D1–D4 與範圍判定

- D1：既有 IMPLEMENTATION_PROMPT 已指定 PR6。沿用 PR6 修復，不需負責人重選分支；本 review 不關閉 PR7，保留其證據。
- D3：現行規範已允許同一模型，但要求不同 run/session、隔離工作區與權限。不能只以不同名字／session 滿足，也不得宣稱模型來源獨立。
- D4：記錄 provider 回傳的用量／total_cost_usd 不需另立商業決策；它本身不證明帳戶真的新增扣款。8 次、約 0.13 USD 是作者所報 probe 指標，未獨立核對帳單；不推論新增支出已獲批准，也不推論必定實扣。
- D2：C2 的持久觸發安裝屬後續階段，不能以文件已寫好推導已獲授權。本輪先完成具體設定、停用／取消／回退與驗收計畫，無需讓這項未啟動工作阻塞 G2/G3 修復。
- 能力主張限縮到「作者當時看見的帳號／工具介面」；尚未獨立證實所有 Routines 均無事件觸發或平台全域最短間隔為一小時。保留 5 分鐘補漏目標及實際能力缺口，不能自行改成每小時已達標。
- git 可以交接版本化檔案，但不能憑 git fetch 推導已取得 GitHub labels/comments。為事件資料及結果各指定真正讀寫端。
- Executor 結果寫允許分支；受限回填者傳遞結果，Planner/Reviewer 依授權寫 main。不能讓雲端 executor 直接寫 main 政策來解決交接。
- runtime durable store 是 task/lease/event 的權威；main state.json 是治理摘要，不建兩個同等權威。
- G5 單次手動啟動閉環不以 C2 常駐 trigger 為必要條件。G6／C3 session 外交接才需持久接線。故意失敗測試留離線 fixture，真實 review 不捏造 finding。
- 使命對齊：本次修復減少重複算力、遺失工作與人工搬運，服務上游可靠性；尚無外部使用者成功證據，市場回饋仍是待驗證假設。

## 實際檢查及限制

可重放 reviewer 檢查：[static_checks.py](evidence/pr6-r2/static_checks.py)、[結果](evidence/pr6-r2/static_results.json)。
命令：python static_checks.py <精確 SHA 檔案所在根目錄>。此脚本只用 ast.parse、json.loads 與標準字串展開，沒有 import／執行受審 Python 模組。

本環境隔離探測：
- unshare --user --map-root-user --net true → exit 1，write failed /proc/self/uid_map: Operation not permitted。
- bwrap --unshare-all … /usr/bin/true → exit 1，loopback: Failed to create NETLINK_ROUTE socket: Operation not permitted。
- Docker/Podman 不存在。

依 OPERATING_RULES 的第三方 code 隔離條件，未執行 PR tests/replay/mutation；未執行會呼叫模型的 probe_auth_isolation.py。這不影響已重現的範本錯誤與可直接查驗的接線缺口，但不能把它寫成完整獨立 runtime 驗收。

修復後仍需：隔離 reviewer 重放上述 controller 邊界、實際 CLI 契約、G5 認證／推送／回填閉環、G6 session 外事件驗收。只有所需檢查完成才能升格；不因檢查數增加而延長無关範圍。

## Gate

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: c04ef465d000968b86065e7608a8c92761458c6d
  reviewed_head: 86421c903563a16ca888a4aed10bd614e223ca0e
  observed_live_head: 75976be1db636ef72d76206b387583fb3cc03443
  policy_sha: d92d082bfcee7002d737e2c3ee2914d2b1fa804c
  highest_evidence: REPRODUCED
  independent_runtime_verified: false
  blocking_findings: [GOV-R2-01, GOV-R2-02, GOV-R2-03, GOV-R2-04, GOV-R2-05, GOV-R1-03]
  conditions: []
  owner_decisions: []
  next_checkpoint: Claude 提交以上修復、隔離測試證據與新完整 SHA，再做 G4
  runtime_status: FOUNDATION_ONLY
  invalidates_when:
    - reviewed scope changes
    - reviewed head changes
    - required evidence changes or fails
```

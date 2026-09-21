# PR #6 治理導入準備度審查與後續規劃

## 給負責人的兩分鐘簡報

**整體目標：** 讓 ATK 工具分發的執行、獨立審查與修復能可靠交接，減少負責人搬運訊息。
**本輪處理：** 檢查 Claude 完整交付報告、接單診斷、啟動文件與 runner 邊界；本輪依使用者最新指示只做 review 與規劃。
**目前進度：** PR #6 已交付 controller 原型與測試紀錄，等待獨立程式驗收；真實自動閉環未驗證。
**本輪成果：** OBSERVED：確認報告存在，辨識啟動方案的證據缺口及文件矛盾。
**還有什麼風險：** 把既有 session 收到事件誤當持久啟動；憑證及 PR 程式隔離不完整；訂閱認證與呼叫上限被誤當費用限制已驗證。
**需要負責人決定：** 無。既有 1A／2A／3A 不重問。此次不要求登入或提供金鑰。
**下一步與停止點：** 先按下方清單完善導入設計與證據契約，再做另行授權的實作／啟動驗收。此文件不是派工事件。
**審查結論：** NEEDS_INFORMATION。

## 審查身分與範圍

- Repository: firekou/Open-Skill-Distribution-Flywheel
- PR: https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/6
- Base: 204a7fe8d43a39962bb4beb313b7538484d433cb
- Head: c04ef465d000968b86065e7608a8c92761458c6d
- Reviewer: ChatGPT，2026-09-19。
- 本輪重新查 live PR，仍為以上 head、Draft、未合併。
- 範圍：報告完整性、導入邏輯、啟動前提與靜態邊界；不是完整 controller 程式驗收。
- 未重跑測試、未執行 runner、未啟動或變更排程、未喚起 Claude、未合併。
- 最新使用者已明確要求「繼續完成 AI 治理的規劃，不是直接執行」。此限制優先於舊 IMPLEMENTATION_PROMPT 的自動續作描述。自動化或 executor 讀到本檔不得據此啟動修復或真實執行。

## 方向對齊

目標來源：使用者要求收到完整報告後判別，並完成治理規劃。
本輪交付：可審查的準備度結論與分階段驗收設計。
主線連結：避免 ATK 分發任務因失效 session、重複派工與錯誤批准而停滯。
必要驗證與停止點：確認交付存在、把已觀察與未驗證能力分開、明列最小缺口後結束本輪。
範圍差異：不恢復 benchmark，不新增大型治理平台，不擴至 50～100 Agent。

## 已讀證據

以下路徑除明示 main 外均綁定上述 head：

- reviews/GOVERNANCE_EXECUTOR_RESPONSE.md
- governance/controller/ACTIVATION.md
- governance/controller/config.live.example.json
- governance/controller/runners.py
- governance/controller/tick.py
- governance/controller/evidence/tests.txt
- main: AGENTS.md、governance/OPERATING_RULES.md、decisions.json、state.json、IMPLEMENTATION_PROMPT.md，以及目標對齊與 executive-review-gate skills。
- Claude 接單診斷：https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/6#issuecomment-5742640203

| 驗收項目 | 狀態 | 證據等級 | 證據及缺口 |
|---|---|---|---|
| 完整交付報告 | 已提供 | OBSERVED | 有實作清單、命令、測試紀錄、限制與啟動方案；內容仍有矛盾 |
| 測試替身閉環 | 作者自報完成 | TESTED | 已讀 tests.txt 的 26／28 條歷次紀錄；未獨立重跑，未把 PR body 的 30 條視為本輪驗證值 |
| 真實 executor/reviewer adapter | 有程式 | OBSERVED | runners.py 存在；真實認證、輸出解析、提交與 review 尚未端到端驗證 |
| 持久事件到 runner | 證據不足 | REPORTED | main 僅記錄 PR5 reviewer 事件註冊、首事件未驗；不證明它能呼叫 tick 或覆蓋 PR6 |
| Claude 接單 | 有回覆 | OBSERVED | 回覆自述為既有 session 的 webhook 訂閱，並非新 GitHub Agent；平台機制未另行獨立驗證 |
| 真實閉環及重啟恢復 | 尚未證明 | REPORTED | 報告承認此 controller 未跑真實 AI 回合 |
| 正式啟動權限 | 本輪不啟動 | OBSERVED | 最新使用者限制為 review 與規劃 |

## Findings 與最小收斂範圍

### GOV-R1-01 / P1：不能以「只缺模型憑證」作為啟動結論

**後果：** 可能在 session 結束後失去交接，卻誤報持續治理已運作。
**證據：** executor response §8 與 ACTIVATION 稱唯一缺口是憑證；接單診斷則說 session 結束後相同留言不會啟動任何東西。main state 的 reviewer trigger 僅涵蓋 PR5，且首事件未驗。
**所需規劃修正：** 分列事件接收、持久 launcher、執行環境、模型認證、controller 呼叫、review 回填，各自記錄提供者、存續條件與證據狀態。不要求使用者重選已批准方向。
**未來驗收：** 在原互動 session 不參與的條件下，保留 event ID、觸發時間、task、run/session ID、head 與回填結果；證明 runtime 重啟後仍可接新事件。未實測前標 UNKNOWN 或 PENDING。

### GOV-R1-02 / P2：啟動入口說明互相矛盾

**後果：** 操作者會誤判啟動需要改程式還是只改設定。
**證據：** response §4 稱啟用 live dispatch 必須修改程式；tick.py 的 build 已有 live 分支，ACTIVATION 也說 tick 支援 live、controller 自身 CLI 才拒絕。
**所需規劃修正：** 以 tick 為唯一擬定運行入口，清楚列 enabled、mode、認證、政策來源與外部呼叫者條件；同步報告、範本與 PR body。預設禁用不等於不存在可啟動路徑。
**未來驗收：** 用無模型測試替身檢查禁用與錯誤配置；真實執行另行驗收。

### GOV-R1-03 / P1：獨立 clone 尚未形成憑證與不可信程式的隔離邊界

**後果：** 待審程式可能接觸父程序的憑證；不同工作目錄不足以履行規範的權限隔離。
**證據：** runners.py 對 subprocess 使用 env_passthrough_only 預設 None；live 範本未配置該欄位。ACTIVATION 明列容器隔離未接上。未觀察到真實外洩，本 finding 不宣稱已發生事故。
**所需規劃修正：** 定義可信 orchestrator、模型 runner、不帶秘密的 PR 測試環境及分支寫入者的權限表。明訂環境變數允許清單、GitHub 寫入 token 的持有者、政策唯讀來源與 reviewer 的獨立 run 身分。
**未來驗收：** 使用合成秘密與無網路隔離測試確認不可信測試程序讀不到；驗 reviewer 無法使用 executor 的寫入權限。未接妥前不開 live。

### GOV-R1-04 / P2：次數限制與費用授權需要分開記錄

**後果：** 呼叫次數上限可能被當成任何認證方式都不會新增費用的證據。
**證據：** ACTIVATION 一概稱訂閱無 per-call 價格；範本同時列 API key 或 OAuth。接單診斷稱跨入口額度是否共用未知。run_budget 是次數，不能單獨證明認證與計費路徑。
**所需規劃修正：** 保留已批准訂閱方向與 run_budget，不重問泛泛的預算問題；把實際認證入口、是否容許額外計費、次數及時間限制分欄。未驗證的認證不得自行切換為新增 API 支出。
**未來驗收：** 在選定 runtime 確認認證方式及額度狀態，只記有無與類型，不記秘密。

## 後續治理規劃：完成條件與責任

| 階段 | 負責角色 | 必要交付 | 過關條件 |
|---|---|---|---|
| 1. 導入設計收斂 | Planner | 統一能力表、入口、權限及狀態來源 | 上述四項矛盾均有一致處置，不把假設寫成已運作 |
| 2. 原型獨立驗收 | Reviewer | 精確 SHA 的離線重放與必要負控制 | 既有驗收要求得到獨立證據；不任意擴張測試範圍 |
| 3. 有限真實驗證 | Executor + 獨立 Reviewer，待啟動授權 | 一個 task 的真實 execute/review/必要修復紀錄 | 不靠負責人搬檔、批准綁定 head、權限及限制有效 |
| 4. 持續運作驗收 | Controller/operator，待啟動授權 | session 外的觸發、重啟與停機證據 | 真實閉環及持久觸發全部成立才可 ACTIVE |

### 觸發與檢查頻率的設計要求

- 首選新提交／review 完成事件，僅在新 task/head/phase 時派相應工作。
- 使用者要求的 5 分鐘可作補漏檢查目標，不能寫成現已配置。需在選定平台確認支援與延遲，再落實。
- 事件去重使用來源的穩定 event ID；補漏按 live head 與已處理狀態核對，不能每 5 分鐘重跑完整 AI review。
- 無新版本不呼叫模型；最多一項 task 串行推進。兩輪修復、超時與停止条件沿用可信規範。
- 持久狀態存於待審 commit 之外；main 的 state.json 只作帶時間與來源的摘要。已審 head 應留在 review 紀錄，不因「不存 live 快照」而刪除審查綁定。
- 停止設計需分開「阻止下一次派工」與「取消正在執行的程序」。現有 STOP 文件只證明前者的意圖，不能寫成即時終止所有程序。

## 尚未執行的驗證與殘餘風險

本輪沒有重跑 replay、完整單元測試、並行租約、崩潰恢復或真實 CLI。沒有對整份程式宣告安全或正確。後續獨立驗收應特別確認長任務期間的租約、穩定事件 ID、runner 輸出契約與取消行为，但此處未重現，不能記成已證實程式缺陷。

不把前述資訊缺口升格為任意平台重建。先針對這個單 task controller 收斂；也不因本 review 要求合併 PR5。

## Final gate

```yaml
review_gate:
  decision: NEEDS_INFORMATION
  reviewed_base: "204a7fe8d43a39962bb4beb313b7538484d433cb"
  reviewed_head: "c04ef465d000968b86065e7608a8c92761458c6d"
  review_scope: "report consistency and activation readiness; not full code acceptance"
  highest_evidence: OBSERVED
  blocking_findings:
    - GOV-R1-01
    - GOV-R1-03
  conditions:
    - reconcile activation entrypoint
    - establish authentication and usage boundary
    - independent replay acceptance
    - persistent real handoff evidence before ACTIVE
  owner_decisions: []
  dispatch_authorized_by_this_review: false
  next_checkpoint: "consistent activation design and separately reviewed replay evidence"
  invalidates_when:
    - reviewed scope changes
    - reviewed head changes
    - required evidence changes or fails
```

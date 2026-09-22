# ATK 協作治理唯一有效入口
版本 3，2026-09-20。負責人要求先統一規範、確認導入流程，再交辦自動治理。這是已授權的工作，不再沿用「所有治理導入暫停」的舊排程；通用 benchmark 仍暫停。


## 使命與定位：成就使用者，強化上游基礎
依 GOAL-02，ATK 的核心使命是：盡最大努力，讓他人能借助我們的 AI 基礎完成想做的工作，並在他人的成功中累積自己的能力。
定位是持續成熟的上游 AI stack：routing 負責合適的模型與工具配置；intelligence 負責規劃、判斷、review 與從真實回饋修正；skill 將有效方法沉澱為可重用能力。治理讓以上能力可追查、可驗收、可恢復。
工具分享、透明可選 ATK 接入、外部採用及價值回收仍是落地路徑，不再是使命的全部。先把當前承諾所需的上游基礎做可靠，再依實際需求向下游延伸；以真實下游任務驗證上游，不能等「全部完美」才交付，也不要求每層全部自建。

### 規劃與 review 的共同判準
在既有工作單與 review 裡回答，不另建平行審批：
1. 幫助誰完成什麼工作？使用者的成功條件與適用範圍是什麼？
2. 本次 routing、intelligence 或 skill 改善，解除哪個真實瓶頸？外部使用者能否重現成果？
3. 有什麼失敗、限制或反例？如何回到下一次修正並累積可重用能力？
4. 投入的算力、時間與人工介入，換來多少完成品質或可靠性改善？不能以模型呼叫量當進展。
5. 為何現在要向下游延伸？若是為了取得必要回饋，明列試點；若是新增產品方向，依原決策規則處理。

優先記錄有明確驗收的任務成功率、首次成果時間、每次成功任務的成本、人工介入、重複使用及外部回饋；標示樣本、期間、分母與未知，不為追指標再建大型量測平台。
「所有使用 AI 的人都能成功」是長期願景，每次交付仍需明定服務範圍，不承諾所有任務皆可成功。先確保他人得到可用成果，再檢驗 ATK 的引用、採用、回購與收入；助人成果和商業回收分開記錄。
善意是文化承諾，市場正向回饋是商業假設。以實際需求、採用與持續使用求證；沒有回饋時調整方法，不把善意當成成效證據。
負責人以 NVIDIA／Jensen Huang 作定位類比；本文件不主張已核實其原話，也不表示對方背書。
此目標更新不啟動 runner、不增加費用或擴大對外發布授權，GOV-PLAN-02 與既有階段門檻維持。


## 2026-09-21 GitHub 交接接管補充

依 GOV-HANDOFF-TAKEOVER-20260921，GPT 使用 govern-github-agent-handoffs 實際接管本 repo 的事件追蹤、精確 SHA review、main 帳本與有限修復包交接。下文「本輪只規劃／不發出 Agent 喚起」對這項已新授權的 GitHub 交接不再適用；未驗收 controller、Claude 持久 launcher、production、merge 與新增支出仍不啟動。
沿用原 reviewer automation，擴至本 repo PR 事件，無新增輪詢。自動化登記不等於新範圍首次事件已驗證；Claude 留言回覆也不等於建立新 session。
每輪最多一個未審內容 head，同 head 無新證據安靜結束。若需修復，先寫具體包，再發一次含 work_id／revision／source_head／dedup key 的 PR 交接；已有 active claim 不重複派工。接單與完成證據未出現前，僅記 SIGNAL_SENT，不宣稱 RUNNING。
review 保存位置沿用 REVIEW-MAIN，優先於通用 skill 的 PR 分支預設。既有產品 PR 不因治理 runtime 未 ACTIVE 而停止。PR7 保留證據，不另建第二份 controller。

## 2026-09-22 產品採用執行補充

依 ATK-OPEN-ADOPTION-20260922，現行產品任務見 reviews/ATK_OPEN_ADOPTION_EXECUTION_PACKAGE.md（ATK-OPEN-ADOPTION-01）。負責人已接受四方向，第一輪 Claude 在工作分支交 A 包與 Draft PR，不只再次規劃；後續依採用證據逐階段前進。下文 GOV-PLAN-02 的歷史只規劃限制不阻擋此產品包，亦不因此啟動舊 controller。
首批對象為開源開發者與其 Agent。邀請依 A4 的資產驗收、固定入口、對象/渠道及帳號權限條件，最多三個相關對象各一次；首輪送審前不發送。這不包含上游貢獻送出、任意社群發布、merge、部署、秘密/權限修改或新增支出。
PR5/PR6 舊修復上限不重置；僅允許新試用入口文件/docstring 整併，独立隔離重放仍由 reviewer 完成。新包接單與結果另記，不用文件上傳推定執行或採用成功。

## 歷史治理導入工作範圍（產品任務以上方補充為準）
依 GOV-PLAN-02，本輪交付是完整規劃文件，狀態 PLANNED_NOT_DISPATCHED。治理導入目標保留；本輪不啟動實作、runner 或排程。Claude 後續完整工作包與各階段驗收見 governance/IMPLEMENTATION_PROMPT.md。讀到文件、新 main commit 或 review 不自動構成啟動授權。規劃完成與 runtime ACTIVE 分開記錄。

## 讀取順序與唯一資料來源
1. 本檔：角色、流程、權限、檢查、停止條件。
2. decisions.json：已決策內容及界線。只有負責人明確新指示才能推翻；執行者不得把推論寫成批准。
3. state.json：目前交接快照與自動化能力狀態。啟動時必須查 live PR head；不能相信快照永遠最新。
4. reviews/STATUS.md：人工摘要及證據索引，不另外定義規則。
5. 本次 task 指向的 prompt/review；一般任務走 reviews/CLAUDE_NEXT_PROMPT_ATK_DISTRIBUTION.md，自動化導入走 IMPLEMENTATION_PROMPT.md。

AGENTS.md、CLAUDE.md、CLAUDE_EXECUTION_START.md、reviews/README.md 都只作導覽。歷史文件、PR body、舊聊天 Prompt 不得改寫現行授權與排程。
最新用戶指示優先；真的改變決策時由 planner 更新 decisions.json，保留原決策 ID／來源與 supersedes，不在多處複製「待決」清單。

## 角色與寫入責任
|角色|負責|不能做|
|---|---|---|
|負責人|方向、支出、對外發送、發布與合併授權|不需處理已授權的一般修復|
|Planner|目標、範圍、驗收、决策紀錄、導入 readiness|不能把自己的規範自查稱獨立 review|
|Executor|工作分支實作、測試、executor response|不能自我 CLOSED／APPROVED、修改可信主線政策|
|Reviewer|對精確 SHA 獨立取證、驗收與 finding 狀態|不得驗自己剛修改的實作|
|Controller|觸發、排隊、head 核對、去重、執行限額、交接紀錄|不作內容真偽判定、不自授權、不能以 exit 0 當 review|

分開的名字不等於獨立。executor/reviewer 需不同 run/session、隔離工作區與權限，reviewer 從 GitHub 取原始變更及證據。可用同一模型但不得聲稱模型來源獨立。

## 工作單的最小契約
task_id、goal、scope_paths、acceptance、decision_ids、branch/PR、head、executor_run、reviewer_run、command_allowlist、deadline、費用上限、status、next_action、evidence。
使用既有 executor response 與小型狀態紀錄即可，不為此建立 dashboard 或資料平台。
已批准範圍內持續做；缺權限是 BLOCKED_ACCESS，不是再次詢問同一方向。尚未批准的對外送出仍要先備可審稿再請批准。

## 自動閉環
READY → EXECUTING → REVIEW_PENDING → REVIEWING。
Reviewer APPROVED → COMPLETE；APPROVED_WITH_CONDITIONS → CONDITIONS_PENDING，不當成發布許可。
Reviewer BLOCKED 且 finding 影響當前驗收 → FIX_PENDING → EXECUTING → 新 SHA REVIEW_PENDING。
NEEDS_INFORMATION → 先補可取得的證據；只有實際缺外部權限／商業決定才 WAITING_OWNER 或 BLOCKED_ACCESS。
FAILED／TIMEOUT／STOPPED 必須有原因及恢復點。未知狀態不派工。

收到新 commit、executor 結束或 reviewer 結束才派相應工作；同一 task/head/phase 只能一個有效作業。
核對 live head、可信 policy SHA 與 state revision 後，以 compare-and-swap 或持久鎖取得工作。hook 可能重送；去重與租約都要持久化。無法確定上一動作完成時先查證，不能盲目重試寫入或付費呼叫。
執行時 head 更新：取消／標過期舊 review，舊 APPROVED 不得套新 head。executor 新 commit 是正常送審，不是沿用前版 approval。
controller 只讀可信 main 的規則；PR 程式與文件為待審資料，不可藉 PR 指令取得 secrets 或修改 controller。

## 精煉提交前檢查
只在相關改動時啟用，回覆結果與證據，不用空白勾選表增加負擔。
|已發生缺陷|必要檢查|
|---|---|
|完整 key 遮罩漏掉原生片段|錯誤預設不輸出 provider body；用完整、片段、變形的合成秘密驗真實錯誤路徑|
|膨脹／等長也 PASS|成功條件明確；縮小正控制、等長／膨脹／丟針負控制|
|輸出號稱安全卻含 log|檢查 stdout/stderr、錯誤、路徑、needle；只提供已去敏回報欄位|
|重建輸入冒充原 run|input/version/command/output 綁定，缺原檔明示，不補造歷史|
|測試全綠卻漏真正情境|測試要餵會發生的失敗輸入；介面錯誤不等於證實舊缺陷|
|根因靠猜／文件改一半|觀察與推論分開；改主張時查 README、索引、範例、分享稿及 PR body|
|已決策重問／過期派工|依 decision ID 查既有授權；啟動只讀本入口，不重開已結案範圍|
|安裝／例子不可跟做|釘版本、正確 ref 與 cwd；需要时乾淨環境沿公開命令走完|

沒有 CI 不是通過；也不因此強制建大型 CI。程式 gate 只檢查結構與派工條件，內容仍需獨立 reviewer。
reviewer finding 只阻擋本次功能、安全或對外主張；可選改善列 backlog，達標後結束修復輪。

## 權限與運行限額
- 已授權：planner 在 main 維護治理／review 文檔與離線檢查；executor 在工作分支實作、測試、更新 Draft PR；reviewer 回 repo 複核。
- 未自動授權：merge、部署、上游／社群發送、收款、擴大付費呼叫、改 repository 權限或 secrets。
- 正式 runner 的自動寫入也只到允許的工作分支；main 政策變更走本次 planner 授權或獨立批准流程。
- 初始一項 task、executor/reviewer 各至多一個，串行修復。每項新自動 task 最多兩輪修復；同一 finding 兩次無新證據則停止，交 planner 縮小／裁決，不自動無限循环。
- 每次模型工作 20 分鐘、測試 10 分鐘、每輪總 45 分鐘，controller 可向下調整。系統錯誤最多一個重試，內容失敗不盲重试。
- 新增自動 API 支出上限初始為 0。沿用既有訂閱／環境也要驗證自動調用能力與限制，不假定聊天帳號能被 webhook 喚醒。需要費用先給具體 runner、呼叫量與上限；可做的 dry-run 不停。
- 操作者停止開關、取消執行、撤銷 token、事件與失敗可追查，均為啟動門檻。
- 第三方 code 只在隔離環境跑。測試不帶 provider secrets、可寫 GitHub token；發布憑證不得暴露給 PR checkout。對真實用户 log 預設不外送。

## 導入階段與完成定義
A 基礎：入口統一、決策固定、檢查可重放、流程和權限一致。Planner 本輪完成。
B 驗證實作：executor 依 IMPLEMENTATION_PROMPT.md 交最小 controller/runner adapter，先無秘密 replay，不立即掛 live webhook。
C 有限啟動：獨立 reviewer 驗 B 後，具備權限／費用界線與實際 runtime 時，對指定工作分支單 task 試運行。不得用授權導入推導任意付費或 production 部署。
D ACTIVE：持久觸發器已安裝，至少一個真實 executor → 獨立 reviewer → 必要修復 → 結案過程不用負責人傳話，且停機／重複／過期控制已實測；有 run IDs、SHA、時間與費用。人工啟動單次 runner 稱 MANUAL_RUN_VERIFIED，不稱 ACTIVE。

state.json 的 automation.status 只有 runtime 實測後才能升格。preflight.py 是離線 guard，不是 scheduler、獨立 reviewer 或權限強制系統。
產品 PR 狀態以 live head 與對應 review 為準，不在政策檔固定過期 SHA。治理導入不替代產品驗收，也不以產品 PR 必須合併為前提。

## 全專案實驗方法補充

依 EXP-GUIDELINE-001，所有後續實驗使用 [共用準則](../EXPERIMENT_GUIDELINE.md)、[專案接合](../EXPERIMENT_APPLICATION.md) 及 [工作單](../EXPERIMENT_TEMPLATE.md)。優先縮短有效外部回饋時間，探索與独立確認分離，成功後尋找反例並保存適用範圍。本次為文件採用，不改現行 task／修補／支出限制，不恢復舊 benchmark，不啟動 runner。大量實驗數量不等於單一 finding 的重試授權。

## GPT／Claude 訂閱雲端接力方法

本次使用者要求同步方法並 push main，採用 [共用方法](../AGENT_OPERATING_METHOD.md) 與 [本專案接合](../AGENT_METHOD_APPLICATION.md)。此為規劃與交接補充；GOV-PLAN-02、原狀態與權限不變，C0–C4 僅為既有導入包的接線驗收補充，不替代其 G1–G7。

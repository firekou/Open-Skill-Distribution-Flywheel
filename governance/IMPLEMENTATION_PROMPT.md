# Claude AI 治理導入工作包
版本 2，2026-09-19。取代本檔舊版派工順序。

## 使用方式與目前授權
這是 Planner 依負責人要求完成的全程執行規劃。負責人本輪要求把所有要交給 Claude 的工作寫進 repository；本輪不啟動實作、runner 或排程。
文件狀態：PLANNED_NOT_DISPATCHED。讀到本檔、main 更新或 review 事件本身不代表啟動授權。未來收到明確啟動指示後，按以下依賴與 gate 執行，不需重新詢問既有 1A／2A／3A。
本檔是治理工作的唯一派工明細；OPERATING_RULES 是唯一政策來源；decisions.json 是決策來源；review 是證據來源。舊聊天中「挑三個候選」不適用本治理任務。

## 本輪使命更新（GOAL-02）
2026-09-20 負責人更新：以幫助他人完成工作成果為核心，持續成熟上游 routing、intelligence、skill 與治理，在他人成功中強化 ATK。完整判準以 OPERATING_RULES 的「使命與定位」為準，不另複製政策。
G1 能力表須說明各項能力解決的使用者瓶頸；G2～G4 驗證可靠性；G5～G6 的治理文件試行僅證明接力能力，不冒稱已證明外部使用者成功；G7 再用真實工具任務驗證他人能否完成工作。由外部失敗與成功回饋形成下一輪 skill／routing／review 改進。
既有 G1～G7 及支出、啟動門檻不變。最大努力不等於無上限呼叫模型；投入算力需對應成果或可檢驗的改善假設。市場回饋另行求證，不以善意或自我 review 代替外部證據。

## 目標與完成定義
讓一項 ATK 實用工具交付能由事件帶動執行、独立 review、必要修復與結案，過程不需負責人搬運 Prompt。保留透明可選 ATK 接入、分享及採用主線，不恢復通用 benchmark，不默認付費量測產品。
完整治理導入必須同時具備：政策一致、精確 SHA 驗收、持久狀態與事件、權限隔離、使用上限、取消與恢復、真實閉環及可查證紀錄。文件或測試替身完成不等於 ACTIVE。

## 啟動後先讀
1. AGENTS.md → governance/OPERATING_RULES.md
2. governance/decisions.json、governance/state.json
3. .claude/skills/atk-goal-alignment/SKILL.md、.claude/skills/executive-review-gate/SKILL.md
4. reviews/PR6_R1_READINESS_REVIEW_c04ef465.md
5. PR #6 最新 head、完整 executor response 與後續 review；以 live 資訊取代快照，不沿用過期 approval。

已審報告基準為 c04ef465d000968b86065e7608a8c92761458c6d。這是歷史 review 綁定，不是永遠有效的 live head。

## 角色與執行邊界
Planner 維護政策、方向與驗收；Claude 作 executor；Reviewer 用不同 run、隔離工作區及權限獨立取證；Controller 只排程及驗證派工契約。不得用自己撰寫的修復自我批准。
治理修復沿用 PR #6 的治理分支，若該 PR 已關閉則先讀結案證據，再建立單一後續治理分支；不混入 PR5 產品程式。
Executor 可提交分支及 Draft PR、追加回報；可信 main 政策修改先提供建議 diff，由 Planner 處理。不得合併、發布、部署正式 webhook、修改帳戶權限或 secrets、發上游訊息、新增未授權費用。
缺外部能力只阻擋依賴它的工作，先完成可離線交付；無新證據不得反覆詢問同一決策。

## 工作順序與責任
| 工作包 | 執行者 | 依賴 | 完成輸出 | 驗收者 |
|---|---|---|---|---|
| G1 入口與證據一致 | Claude | 收到實作啟動指示 | 修正報告與 activation 文件 | Reviewer |
| G2 權限與 runner 契約 | Claude | G1 的能力盤點 | runner 修復、預設禁用範本、針對性測試 | Reviewer |
| G3 狀態與事件可靠性 | Claude | G2 介面確定 | controller 修復、重放與失敗證據 | Reviewer |
| G4 獨立原型驗收 | Reviewer | G1～G3 同一 head 送審 | 精確 SHA review | Reviewer，非 executor |
| G5 單任務真實試行 | Claude/Reviewer | G4 通過及真實啟動範圍可用且獲授權 | 真實 run、review、必要修復紀錄 | Reviewer |
| G6 持久觸發與維運驗收 | Claude/Operator | G5 通過及觸發部署授權 | session 外的事件、重啟、停機紀錄 | Reviewer |
| G7 回到 ATK 交付 | Planner/Claude | G6 或明確標示的有限人工模式 | 交付、採用與治理成效分開回報 | Reviewer |

G1～G3 是第一個有限工作包，可一次修復後送審，不要求每個小步驟各開 PR。G5／G6 是後續條件式工作，不因 G4 通過自動取得部署或費用授權。

## G1：修正四項 review 與建立能力表
處理 GOV-R1-01～04，不把「收到事件」當成「已建立持久 launcher」，不再寫「只缺憑證」。
更新既有 GOVERNANCE_EXECUTOR_RESPONSE、ACTIVATION、config.live.example 與 PR body，消除以下矛盾：
- tick 支援 live；controller 自身 CLI 的限制不能說成整個專案無 live 入口。
- 已有訂閱不證明新行程已認證，不推導 API key 不會新增費用。
- PR5 reviewer 觸發註冊不證明 PR6 或 controller 已接通。
- 不同 clone 不代表不可信程式與秘密已隔離。
能力表至少含：事件來源、接收服務、持久 launcher、執行主機、模型認證方式、reviewer 身分、GitHub 讀寫、狀態磁碟、取消與恢復。每列填 provider、生命週期、OBSERVED/REPORTED/TESTED/VERIFIED、證據連結、限制及缺口。
只讀現有工具及能力，不為盤點啟動模型。若必須選型，最多比較兩條能補實際缺口的路徑，以官方資料確認能力；先驗既有入口，不因框架知名而重建平台。
驗收：四项主張一致，所有未知明列，沒有把 planner 自查升格獨立批准。

## G2：隔離與真實 runner 介面
- Controller 從可信政策 checkout 載入 guard，鎖定 policy SHA；PR 無法改政策來源。
- Runner 使用最小環境允許清單；executor 與 reviewer 分開 run ID、工作區與權限。不要預設繼承全部父程序環境。
- 不可信 PR 測試置於無 provider secrets、無 GitHub 寫入 token 的隔離環境。模型認證只給需要它的可信 runner，寫入由受限發布步驟完成，不把 token 交給 PR 測試。
- GitHub 寫入只到批准的工作分支；reviewer 的證據回填與 executor 的寫入角色分開。記錄平台能強制的限制及僅靠約定的限制。
- 以無模型的 stub executable 驗證真實 adapter 的 command 格式、CLI 輸出包裝與 JSON 解析、錯誤碼、stdout/stderr、超時、缺認證、無效 SHA、缺 review evidence。不能只測 FakeExecutor 而聲稱驗過 SubprocessRunner。
- 檢查新 commit 是否真實存在並位於指定分支，不能接受 runner 自報 new_head 即算完成；review 必須綁定當前實際 SHA。
- 模型每次上限 20 分鐘、測試 10 分鐘、總輪次 45 分鐘，範本不可放寬可信規範。一次 runner 算一個 run；run 上限初始不高於 8，額外 API 支出仍為 0，禁止自動改走付費 fallback。
驗收：合成秘密與負控制證明限制有效；錯誤預設不回顯 provider body、原始 log 或秘密。預設 live 禁用，未認證只回 BLOCKED_ACCESS，不假成功。

## G3：事件、持久狀態、取消及恢復
- 狀態放在被審 commit 之外，main state 是摘要。保留歷史 reviewed_head；live head 在派工與接受 review 時重新查。
- 工作單至少含 task_id、goal、scope_paths、acceptance、decision_ids、PR/branch、head、policy_sha、phase、run_id、command_allowlist、deadline、run/時間/費用限制、evidence。
- 事件使用來源穩定 event ID，補漏使用 task/head/phase 去重；不得由每次都變動的 state revision 假冒同一來源事件。
- 以跨程序鎖/CAS、租約及必要續租防止長任務被第二 worker 接走。以同時程序與跨租約時長的 stub 工作驗證，不只循序呼叫。
- 寫入前記錄 intent，寫入後記錄結果；崩潰發生在外部副作用與本地保存之間時，恢復先向 GitHub 查證，不盲目重做推送或模型呼叫。
- APPROVED_WITH_CONDITIONS → CONDITIONS_PENDING；NEEDS_INFORMATION → 證據待補；只有對當前 head 的有效 APPROVED 可 COMPLETE。COMPLETE 不等於 merged/deployed。
- 區分不再派工、取消當前程序、終止子程序與撤銷外部 token。保留恢復點；取消後不得留背景模型繼續跑。
- 系統錯誤最多一次受控重試，未知副作用先查證；內容失敗不盲重試。最多兩輪修復，同一 finding 無新證據反覆兩次交 Planner。
驗收：重複事件、真實並行、途中換 head、自審、過期 approval、重啟、停止與限額均有相應正負控制；既有已通過項只在相關程式改動或具體風險時重驗。

## G4：獨立驗收契約
Executor 提交完整新 SHA，將 G1～G3 的命令、結果及不足寫入 reviews/GOVERNANCE_EXECUTOR_RESPONSE.md；證據放 governance/controller/evidence/，保留必要原始結果並去敏。
Reviewer 從 GitHub 精確 SHA 另取工作區，不修改受審實作；重跑必要離線檢查，區分作者結果與獨立結果，判 APPROVED / APPROVED_WITH_CONDITIONS / NEEDS_INFORMATION / BLOCKED。
重放必須一次啟動走完 execute → review BLOCKED → fix 新 head → review APPROVED → COMPLETE；測試替身清楚標示。
達標後可將原型驗收記 REPLAY_VERIFIED。不需為了更多測試一直延長審查。
回報 review 必須含逐項 finding 處置、證據、殘餘風險與下一個 gate。Reviewer finding 需要修復才回 G2/G3，不擴大無關產品工作。

## G5：有限真實試行的具體工作
此階段只在允許真實試行的授權及能力已具備時啟動，不要求重選治理方向。
選擇一個無秘密、無外部發布的治理文件小任務，列明 scope_paths 與客觀驗收，指定隔離分支。不得直接用真實客戶 log。
同一初始觸發後，由 controller 啟動 executor 產出 commit、啟動獨立 reviewer、若有真實 finding 則修復後再審、最後結案。不要為了展示修復故意讓 reviewer 虛構缺陷；負控制留離線 replay。
保存：初始 event ID、task ID、各 run ID、完整 SHA、policy SHA、開始結束時間、認證類型與已知用量、review 決定、修復次數、結果連結。
真實 CLI 解析、認證、分支推送及 review 回填均成功才標 MANUAL_RUN_VERIFIED；若只單獨跑一次模型，不算閉環。
若缺認證或額度，完成準備資料並列精確缺口；不要求在對話貼 key，不使用已暴露 key，不新增未授權 API 呼叫。

## G6：持久觸發與營運驗收
- 事件優先：新提交、executor 完成、review 完成時推進相應 phase。
- 5 分鐘為補漏目標，僅讀狀態與 live head。選定平台須確認支援、延遲與限制；達不到則報實際限制，不假裝已設。無新版本不啟動模型。
- 持久 launcher 不依賴既有聊天 session；事件來源、接收、排隊、執行與回填須各有可核對 ID。
- 模擬原互動 session 不參與及 worker 重啟後的新事件，證明不用負責人傳話仍能完成。
- 證明重送事件不重跑、途中改 head 廢止舊 review、停止當前工作與禁止下一次派工、恢復後不重複副作用。
- 設計並交付啟動、停用、取消、回退與紀錄保存 runbook；回退停服務和寫入，不刪稽核紀錄。
僅 G4、G5 與持久觸發驗收全部通過後，Planner 才依證據更新 ACTIVE。此狀態不代表允許擴張 Agent 數量或對外發布。

## G7：回到主線的營運衡量
首個治理閉環完成後，用已批准的 headroom 工具交付作下一個任務候選，重新查該產品 PR 的 live review，不沿用舊 SHA。
分開記：
1. 治理：交接成功率、重複派工、過期批准拒收、人工介入、耗時、用量、失敗恢復。
2. 產品：可用工具交付、外部使用、品牌引用、導流、付費實收。
沒有外部紀錄就填 0 或未知，不以測試數及 Agent 數冒充採用。
10／25／50／100 個工作單元是後续容量里程碑，待單 task 可靠性與真實需求成立再規劃，不在本包實作。

## 回報與檔案交接
沿用 reviews/GOVERNANCE_EXECUTOR_RESPONSE.md，追加本輪，不刪原始失敗與歷史證據。每次回報：
- task、完整 head、policy SHA、作用中的 decision IDs；
- 修改路徑、G1～G7 本輪涵蓋範圍；
- 每條 review finding 的回應與命令／結果；
- 真正運作的能力、待驗證能力、具體 BLOCKED_ACCESS；
- 下一位角色及唯一 next_action。
機器狀態摘要至少包含 execution_mode、runtime_status、review_decision、reviewed_head、evidence、next_action；規劃準備狀態不得覆蓋 runtime status。
技術交接留 repo；只把真正缺少的人工作業與商業決定交負責人。文件讀到、留言送出及 executor 自報都不算驗收完成。

## Planner 本版自查
已核對：入口指向本檔；四項 finding 分別對應 G1/G2；執行依賴與獨立驗收分開；次數、時間與新增費用分開；持久觸發與既有 session 分開；停止派工與取消程序分開；有缺存取時仍有可交付項；G5/G6 不由 review 自動推導授權。
這是規劃自查，不是對自己計畫的獨立批准，也不宣告 PR6 程式通過。

## 新交付送審與後續規劃更新
每次送審提供 repo、PR、完整 head、executor response 路徑、本輪 G 編號及 finding 對應。這些資料寫入既有 response，由 reviewer 直接讀取，不要求負責人搬運全文。
Reviewer 先查 live head；同 SHA 且無新證據時只記錄查核，不冒稱新一輪修復通過。若新成果在其他 repo 或分支，先定位並讀其現行指示，再判斷依賴，不把另一個 worker 的成功當成本 controller ACTIVE。
程式變更按差異及既有未完成驗收進行獨立測試；只有文件更新則核對主張與所引用原始證據。完成後將結果綁定精確 SHA，更新 state 與本入口的下一個 G 工作，不自動擴大。
最近一次交付定位查核：reviews/GOVERNANCE_SUBMISSION_CHECK_c04ef465.md。該次仍取得舊 head，未取得新的治理送審版本；此紀錄不表示 executor 在其他環境沒有工作。

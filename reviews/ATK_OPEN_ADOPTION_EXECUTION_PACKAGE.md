# Claude 執行工作包：開源開發者與 Agent 採用
日期：2026-09-22
work_id: ATK-OPEN-ADOPTION-01
revision: 1
decision_id: ATK-OPEN-ADOPTION-20260922
狀態：READY_FOR_EXECUTOR，尚未取得本包接單證據

## 目標與最新決策
負責人已接受四個方向依序推進：Routing 接入範例、可重用 Skill、既有 Framework 整合貢獻、任務狀態與記憶接入。第一批使用者定位為開源社群開發者，優先爭取由外部開發者操作的 Agent 試用。
使命：讓他人透過我們的基礎完成真實工作，在採用與回饋中成熟上游能力。ATK 為透明可選配置，不要求綁定帳號才能完成離線任務。
本包是實際可執行的分階段交付，不只回覆計畫。第一輪完成 A 包送審；後續按里程碑門檻接續，不四線同時開發。

## 啟動與責任
Claude 是 executor；GPT 是 planner / independent reviewer。
先 fetch main，讀 AGENTS.md、governance/OPERATING_RULES.md、decisions.json、state.json、reviews/STATUS.md、兩個 repo skills（atk-goal-alignment、executive-review-gate），再讀本包與 PR5 R9。
重新查所有相關 live PR、工作編號、active claim、完整 head、diff 及最新 review；有相同 active claim 不重派。
已知來源：PR5 的 304af885193245da7186cb6b9ab247ec2494bd86；此為規劃基準，啟動時核對，不把舊批准套用新 head。
接單回報：work_id、revision、policy SHA、source head、branch、session/run、scope、claim deadline、dedup key。
dedup key 格式：repo:work_id:stage:revision:source_head:executor。
claim deadline 為接單起 24 小時，逾時先查成果，不盲重啟；原每模型工作 20 分鐘、測試 10 分鐘、每輪 45 分鐘界線保留，超時保存 checkpoint。
未使用的模型額度、API、雲端與對外費用上限仍為 0；既有訂閱也不可假定可自動喚起。

## 當前基礎，不重做
Headroom 案例、Quick Start、兩篇分享稿與上游備稿已存在，先盤點與引用。
PR5 狀態 NEEDS_INFORMATION：P5-R4-01 等獨立隔離重放，作者不得自我关闭或再補同類自跑證據冒充 reviewer。
原 ATK-PR5-R7-LIVE-GUARD 已完成兩輪，不重啟第三輪。本包新增外部採用交付；不得藉新名稱續修舊程式。
PR6 controller 保持 FOUNDATION_ONLY；治理 ACTIVE 不是本包的依賴。
R9 的文件 backlog 本次可隨新試用入口做限定文件整併：free sample 改指向唯一 TRY_IT、安全旗標/版本說明同步、成功嘗試次數文案更正。只改文件及 docstring，不修改舊實作邏輯；舊 review 繼續保留。

## A 包：現在直接完成的第一輪交付
範圍：
- integrations/headroom-atk/ 的 README、TRY_IT、DISTRIBUTION、offering/SERVICE_SAMPLE_FREE.md 與 ab_test.py 的 docstring
- integrations/headroom-atk/AGENT_QUICKSTART.md
- integrations/headroom-atk/agent-manifest.json
- adoption/ATK-OPEN-ADOPTION-01/ 的試用任務、邀請稿、候選表、證據格式與後續規劃
- reviews/ATK_OPEN_ADOPTION_EXECUTOR_RESPONSE.md
沿用已有同功能檔案可不新增，說明映射即可。

A1. 統一試用入口
整理一條最短操作路徑：固定版本取得範例、建立合成 log、執行離線檢查、解讀結果、選擇是否進入 live。
發布前文件修正限上述範圍。保留所有未知與歷史資料限制。不要複製多份會漂移的 live 命令。
驗收：所有入口能追到同一版本與命令；失敗/無效/無收益有明確退出方式；缺 key 的離線流程仍成立。
独立隔離環境不可用時，照實標示 runtime pending，同時完成 A2-A5。

A2. 給 Agent 的最小使用契約
交付 AGENT_QUICKSTART 與可解析 manifest，字段至少包含：
asset_id、version/source SHA、用途、適用/不適用情境、license 與依賴 license、runtime/依賴版本、安裝步驟、輸入輸出、成功/失敗條件、外網與檔案寫入需求、離線費用、live 前置条件、可選 ATK/provider 配置、證據連結、回報入口。
這是本專案格式，不宣稱任何未驗證通用標準或自動相容所有 Agent。
Agent 必須能知道何時不應使用工具；不指示忽略自身政策，不要求上傳 key、客戶 log 或完整 session。
驗收：JSON 可解析；命令與版本對齊；一個乾淨 Agent session 僅按任務與文件就能走到成功或明確停止。若由我們啟動，標 INTERNAL_AGENT_TEST。

A3. 公開可發現與試用設計
沿用現有 GitHub 索引與分享稿，補問題導向描述、適用條件、原始檔固定版本連結。
評估 GitHub 專案社群、合適的 Agent/Skill 目錄與 Hugging Face 等候選管道的當前官方規則；記錄查核日期、允許內容類型、帳號需求、實際搜尋方式。沒有適合的 artifact 類型就不硬塞 model/dataset 分類。
本包不替其他 repo 建重複雜誌發行或付款服務。
準備兩種測試：
1. DIRECT_INVITE：直接給固定網址，驗能否用。
2. PUBLIC_DISCOVERY：只給真實問題，不給品牌、repo、特定 URL 或暗示詞，保存查詢、結果位置與選用原因。
目錄已知入口另記 DIRECTORY_DISCOVERY。未被找到也是結果，不換題直到成功後冒稱原測試成功。
完整成功必須是發現/取得/執行/完成任務；爬取、Star、頁面閱讀不算採用。

A4. 第一批邀請準備
查找最多 5 個有實際相關需求的開源開發者或社群入口，優先曾討論部署 log、模型上下文或工具整合的人/專案。
每筆附公開證據、需求匹配、可使用的合規聯絡管道、是否允許試用招募；不大量蒐集個資、不群發、不重複邀請。
準備英文開發者短邀請與「請你的 Agent 試用」任務稿；說明 ATK 維護、免費離線路徑、可選 provider、時間估計、已知限制、如何回報。
用戶已明確選擇邀請方向。資產通過相應驗收、有可用固定入口、接收者身份與管道規則核對完成、具帳號權限後，可執行最多 3 次單次精準試用邀請；不需重問選人類或 Agent 的方向。
這是試用邀請的有限授權，不是大量推銷、正式上游 code PR、merge、部署、付費或廣泛社群發布授權。條件不具備先交可審候選與稿件，不把沒送出寫成已邀請。
Agent 邀請以其開發者/operator 控制的正常入口進行，不假設陌生 Agent 可被任意喚起。
本輪 A 包送審前不發邀請。

A5. 證據與里程碑規劃
建立最小回報表/JSON schema，不建追蹤平台或秘密遙測。
字段：來源分類、operator 是否外部、agent/runtime、版本 SHA、日期、任務、合成輸入 hash、命令、exit/result、成功判準、必要人工協助、時間、usage/費用若未知填 unknown、卡點、再用意願、可公開範圍、證據 URL。
將下列 M1-M5 的工作、依賴、產物與 gate 寫成可直接接續的工作單。

## 後續方向與里程碑
| 階段 | 具體工作 | 成功與停止條件 |
|---|---|---|
| M1 Routing 資產就緒 | 完成 A 包，獨立 reviewer 在合格環境重放最小任務及必要安全控制；準備固定版本入口與發布清單 | 一份可跟做資產通過所需驗收；只剩發布權限時交具體成果，不擴建 routing engine |
| M2 外部開源開發者/Agent 採用 | 發有限精準邀請並取得實際使用結果；優先請對方自己的 Agent 操作 | 至少 1 位非作者開發者或其 Agent 完成指定任務；公開發現另外驗證，不用受邀替代 |
| M3 可重用 Skill | 從 M2 成功與卡點抽出選用、配置、驗證、診斷 skill；草稿可先備，但實證前不稱 proven | 第二個獨立環境能照 skill 完成；至少一個不適用/失敗案例被正確拒絕。skill 建立遵守當地 skill-creator 與 git 保存規範 |
| M4 Framework 整合貢獻 | 比較 LiteLLM、PydanticAI、Vercel AI SDK、Microsoft Agent Framework 現行官方能力與 issue；選一個需求具體、改動最少的目標 | 一份小型範例/文件/修正通過本地獨立驗收；先查重，備完整 upstream 提案；正式送出依 3A 授權，不將草稿當已接受 |
| M5 狀態/記憶接入 | 以「任務中斷後另個 Agent 接續」盤點 TiDB 與現有儲存替代；需要時才加入向量/branch | 先交一頁選型與任務契約；確有需求且前階段有成果後做一個薄整合 PoC，驗重啟、隔離、重複操作及結果一致性；不搬遷 production |

M4 不預先指定贏家，不自建 SDK 取代原生配置。每次最多一個框架目標。
M5 的四個參考來源（需按實作當時重新查核可用版本、帳號能力與產品限制）：
- https://www.pingcap.com/case-study/manus-agentic-ai-database-tidb/
- https://www.pingcap.com/case-study/kimi-2-6-agent-hosting-platform-tidb-cloud/
- https://www.pingcap.com/case-study/dify-consolidates-massive-database-containers-into-one-unified-system-with-tidb/
- https://www.pingcap.com/blog/what-makes-a-database-for-ai-agents-different/
案例是供應商公開描述，不是本專案驗收；不得將一秒建立、分支或租戶隔離直接寫成我們已具備。
M3-M5 每階段一次小交付送審，沿原 task 保留回饋，不自行展開多框架/多資料庫試點。

## Agent 採用的證據分級
- INTERNAL_AGENT_TEST：我們操作的 Agent；只證明內部可用性。
- EXTERNAL_INVITED_AGENT：外部開發者控制的 Agent，收到直接邀請後使用；是外部受邀採用。
- EXTERNAL_DISCOVERED_AGENT：外部 Agent 由記錄中的公開搜尋/目錄發現並成功使用；來源仍細分。
- 可觀察的外部身份/控制者及操作證據不足時：UNVERIFIED，不推測為外部。
- 我們自己的 Agent 即使在新 session、不同模型、未知 URL 下找到工具，也只是內部發現測試。
這些是證據分類，不是每一項都必須通過才能開始交付。第一成果以外部受邀成功為目標，公開發現持續另驗。

## 分支、驗收與交接
A 包從最新可信 main 建立 claude/atk-open-adoption-01 分支及 Draft PR。PR5 未合併的資產用 pinned source 引用。
如需上述文件修正，建立以 PR5 精確 head 為基準的文件 delta 並明列依賴；不複製整個舊實作進 main、不私自合併 PR5。優先保持新 PR 只含 adoption 產物與明確文件差異。
送審時回報完整 result SHA、diff scope、policy SHA、來源 PR5 SHA、commands/exit/results、已驗證/未知、來源與日期，以及本包工作编号。
成果報告寫 reviews/ATK_OPEN_ADOPTION_EXECUTOR_RESPONSE.md；保留原作者證據，不自行 APPROVED。
GPT reviewer 每輪一個精確內容 head，main 記帳；每階段最多兩輪限定修復，同缺陷達上限改縮小範圍，不用新 work_id 繞過。
沒有資源/憑證仍完成 A 包其他產物；獨立重放不可用交回 reviewer，不讓 executor 自證獨立。
M1 後 M2 邀請 gate 滿足即可依本包有限授權續作；正式 release/merge/部署/帳號註冊等需明確既有授權或具體成果後再處理。
本輪停止點：A 包實際檔案 + Draft PR + executor response 已提交。不要只提交一份重述此包的計畫。

## Non-goals
不恢復通用 benchmark、Freeze、Omnigent/AGT/OMA 試點；不重建 controller、不新增 polling/付費 API fallback；不開第三輪 PR5 舊程式修復；不建立付款服務或大規模量測平台；不無限增加候選；不碰金鑰、權限或真實客戶資料；不自行 merge、部署、上游送出或新增支出。

## 給負責人的回報
只報：交付什麼、誰能用、已實測什麼、外部採用屬哪一類、還差哪一個最小 checkpoint，以及確實需帳戶持有人處理的缺口。不要要求搬運 Prompt、報告或 SHA。

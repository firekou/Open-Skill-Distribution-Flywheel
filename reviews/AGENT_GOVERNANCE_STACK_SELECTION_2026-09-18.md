# AI 規劃、執行與獨立審查：協作架構選型

日期：2026-09-18。狀態：選型建議，尚未安裝、跑付費模型或完成整合驗證。

## 給負責人的結論

建議採用三層結構：Omnigent 做調度，你已有的 executive-review-gate 與 reviews/ 做審查契約，GitHub 檢查與分支規則做交付門檻。先增加一個外部 runtime，不要同時裝多套主管系統。Microsoft Agent Governance Toolkit 排第二階段，只試 Claude Code 外掛；不先裝完整企業治理套件。

這是目前最符合你「保留 Claude 執行、GPT 規劃與獨立複核，減少人工傳話」的候選，不是經過本地對照測試後的全球最佳排名。Omnigent 的 README 明列 Alpha，AGT 明列 Public Preview，推薦的是有限試點。

真正值得升級的能力：任務有持久身分、能自動交接、審查綁定版本、作者無法自行宣告驗收、失敗有有限重試與停止點。增加 agent 人數本身不構成治理。

## 先查了你已有的哪些資料

1. 已完整讀取 ATK_SOURCE_COLLABORATION_GITHUB_GITLAB_AI_SDK_TARGET_LIST_2026-09-02.md。它原先是對外技術貢獻清單，LiteLLM、PydanticAI、Vercel AI SDK 的排序不能直接當內部工作流採購排序。
2. 掃描 Open-Skill-Distribution-Flywheel 的 registry/materials.json，並用 main 上檔案核對 Omnigent 收錄。現有資料已包含 Omnigent、Kungfu、Open Multi-Agent、Microsoft Agent Governance Toolkit、Microsoft Agent Framework。
3. 查閱候選上游目前 README 與可讀的外掛文件，確認功能、安裝入口與成熟度。未另行擴張成全網排行榜。

你自己的資料入口：[現有 registry](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/main/registry/materials.json)。其中 Star 是 2026-09-15 的歷史快照，不是本次即時核驗值，也不是安全或品質認證。

## 優先順序與各自負責的事

| 優先 | 採用項目 | 用在你這裡 | 安裝或匯入 | 判斷 |
|---|---|---|---|---|
| 1 | Omnigent，從 Polly 範例改造 | 統一調度 Claude Code 與 Codex，組織執行與跨模型 review | Omnigent runtime、兩個 coding CLI、Polly 範例配置 | 最貼合現況；先單 repository 試點 |
| 同步保留 | executive-review-gate 與 reviews/ | 定義驗收、證據等級、停止點，留下交接紀錄 | 將既有規則載入每個角色的指令；不是再購買一套 AI | 已有資產，先補自動驗證，不重寫成另一套治理語言 |
| 同步補強 | GitHub required checks 與分支規則 | 真正攔住缺證據、過期審查與未通過的交付 | workflow、可信 reviewer 身分及 repository 設定 | 規則須在 agent 外部執行 |
| 第二階段 | Microsoft AGT 的 Claude Code 外掛 | 在工具呼叫前檢查動作、載入政策與留紀錄 | agt-governance plugin | 可補 Claude 執行端；不覆蓋所有 agent 與工具 |
| 備選 | Open Multi-Agent（OMA） | 若未來要開發自己的可恢復任務與審批服務 | TypeScript runtime | 是另一條 runtime 路線，不與 Omnigent 同時當總調度 |

### 1. Omnigent：先試這個

上游支援將多種 coding harness 放進共同調度層。Polly 是主管範例：拆任務、用 worktree 隔離工作、將 diff 交給不同供應商 reviewer。這與你目前模式最接近。Debby 的雙模型辯論可作企劃輔助，但不能代替驗收。

來源：[Omnigent README 與 Quick start](https://github.com/omnigent-ai/omnigent/blob/main/README.md)。原始 README 的徽章標示 Alpha。

工程端安裝入口，這些命令本次尚未執行：

```bash
uv tool install omnigent
omnigent setup
```

需要 Python 3.12+、Git；coding CLI 路徑需要 Node.js 22+，原生終端 wrapper 需要 tmux。Linux 隔離另需 bubblewrap。應先選定並鎖定測試版本；上列為官方未釘版本的入門語法。

從上游取得相容版本的 examples/polly/ 後，官方啟動方式為：

```bash
omnigent run examples/polly/
```

這個相對路徑來自上游 checkout，不能假設安裝 Python 套件後你的專案就自動出現它。實作時先讀實際範例設定與指定工作目錄的方式，再改造成專案內的配置。本次未取得 Polly 內部配置，因此沒有假造可直接 import 的 YAML。

不要把目前聊天視窗視為可直接匯入的執行程序。需要在工作機或持續運作的 host 上配置可呼叫的 CLI／API agent，另將已核准規格、review 檔與決策紀錄交給它。工具接入、憑證、計費與使用權須依實際安裝環境確認。

### 2. Microsoft AGT：只先考慮 Claude 外掛

官方目前提供 Claude Code plugin 安裝入口：

```text
/plugin marketplace add microsoft/agent-governance-toolkit
/plugin install agt-governance@agent-governance-toolkit
```

此命令在 Claude Code 中使用。外掛文件明列 SessionStart、UserPromptSubmit、PreToolUse hooks，以及政策檢查 MCP 工具。它適合試「這個動作是否允許」，不負責判斷研究結論是否正確。

來源：[官方安裝说明](https://github.com/microsoft/agent-governance-toolkit)、[外掛實際範圍](https://github.com/microsoft/agent-governance-toolkit/blob/main/agent-governance-claude-code/README.md)、[marketplace manifest](https://github.com/microsoft/agent-governance-toolkit/blob/main/.claude-plugin/marketplace.json)。

限制必須保留：不是所有 Claude 介面的通用保護，也不會自動限制 Codex；工具已執行後，不能保證再攔掉輸出。文件也承認其未加密鑰的 hash chain 無法阻止有完整寫入權者重寫紀錄。因此不要把它說成不可竄改的真相來源。

先用 Omnigent 本身的政策功能與 GitHub 權限完成最低需求；只有可重現的治理缺口再引入 AGT。兩套政策同時存在時，要測試 allow／deny／ask 衝突、timeout，以及外掛未載入時是否被識別，不能假設保護自動相加。

### 3. OMA：有價值，但目前留作替代路線

OMA 文件列出持久審批、checkpoint、可離線驗證的 journal，以及驗證角色／依賴順序的 governance floor。若未來做 ATK 自己的任務服務，這些機制比聊天紀錄更容易形成機器可驗證契約。

但這是 TypeScript runtime，需要工程接入模型、工具與排程；不能把目前 Claude 對話 import 後就自動運行。

```bash
npm create oma-app@latest my-oma
# 或加入既有 TypeScript backend
npm install @open-multi-agent/core
```

```typescript
import { FileStore, OpenMultiAgent } from '@open-multi-agent/core'
```

官方 starter 可使用合成回應跑示範，不能當真實模型協作已驗證。journal 能檢查內容來源，不等於檔案從未被重寫。來源：[OMA 官方文件](https://github.com/open-multi-agent/open-multi-agent)。

## 其他收錄專案為什麼沒有排前面

| 專案 | 適用情境 | 本輪不優先原因 |
|---|---|---|
| Kungfu | 跨不同 agent 保留同一份工作與恢復狀態 | 功能貼合，但上游標 Alpha；與 Omnigent 的交接職責重疊，先保留成對照候選 |
| Microsoft Agent Framework | 自建 Python／.NET 多 agent 工作流、checkpoint、人工介入與 telemetry | 能力完整，但需要程式化重建流程；現階段接續既有 coding agents 的成本較重要 |
| CrewAI | 自建角色型 research／writer／reviewer 流程 | 已在既有清單，仍需寫 integration；命名 reviewer 不等於具備獨立驗收權限 |
| PydanticAI | 型別化輸出與工具契約 | 適合未來把 review 結果轉 schema，不是直接管理現有兩個 coding agent 的首選 |
| LiteLLM／Vercel AI SDK | 模型接入、路由或應用開發 | 解決的是另一層問題，不能替代工作交接與審查治理 |

前兩項現況來源：[Kungfu](https://github.com/kungfu-systems/kungfu)、[Microsoft Agent Framework](https://github.com/microsoft/agent-framework)。其他項目依先前完整清單定位，本輪未做安裝比較。

## 建議架構：保留模型分工，補上外部狀態與證據

規劃者先交付可驗收規格。調度器以 task_id 建立工作，交給 Claude 在隔離工作目錄執行。獨立 reviewer 讀原始規格、實際 diff 與證據，不只讀執行者摘要。程式化門檻綁定精確版本。通過後更新負責人簡報；需要修復則自動回到執行者。

這是建議實作契約，不是宣稱任何套件預設全部做到：

| 要保存的欄位 | 意義 |
|---|---|
| task_id、attempt_id | 同一工作、不同嘗試要能分辨 |
| spec_commit、code_commit、reviewed_commit | 防止拿舊審查批准新程式 |
| executor_identity、reviewer_identity | 記錄誰寫、誰驗，不以角色名稱冒充隔離 |
| evidence_paths、evidence_hashes | 定位實际測試與輸出；hash 本身不是可信來源認證 |
| decision、blocking_findings、next_actor | 讓調度程式知道下一步，不從自然語言猜 PASS |
| retry_count、deadline、budget_limit、actual_usage | 控制輪數與成本；拿不到成本就記 unknown，不能記 0 |

規劃與 reviewer 可以使用同一供應商，但要有分離的工作脈絡。執行者不得持有最終審查 gate 的寫入權；驗證機制與結果發送身分應與執行者分開。單一憑證給三個 agent，只有提示詞不同，仍不是權限隔離。

GitHub 可要求指定檢查、dismiss stale approvals，以及最近一次 push 由其他人批准；也能限制檢查狀態的來源 App。需實際設定後才有保護，寫進 Markdown 不會自動生效。來源：[GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)。

## 交給 Claude 的最小試點規格

1. 先讀 reviews/README.md、STATUS.md 與 executive-review-gate。此次僅進行協作工具試點，不解除 benchmark 原有 BLOCKED。
2. 建立隔離試點分支，記錄 Omnigent 與範例的實際版本。不要一次加入 AGT、OMA、其他記憶系統或多層 router。
3. 先接一個 executor、一個獨立 reviewer、一個調度角色；先串行跑通，再談平行加速。
4. 將 review 的檔案路徑與機器可讀狀態接入調度。是否能自動追蹤 GitHub 變動、觸發角色與回寫紀錄，必須實測；缺少的 bridge 明列為工程工作。
5. 設定有限重試、timeout、去重與停止條件。初始可設最多兩次自動修復；達上限先產出阻塞包，主管判斷技術原因，只有商業決定才交負責人。
6. 未有可用的模型用量授權與預算配置時，只做離線測試，不假設聊天訂閱等於任意 API 預算。
7. 回覆 reviews/AGENT_GOVERNANCE_POC_RESPONSE.md，記錄精確 commit、實際命令、證據、已知限制及回退方式。不要自行改成正式採用。

## 六個驗收情境與停止點

| 情境 | 必須看見的結果 |
|---|---|
| 合法小任務 | 完成規劃、執行、獨立 review 與狀態更新，無需負責人傳話 |
| 故意加入可辨識缺陷 | Reviewer 能拒絕，工作退回 executor |
| 審查後再改 code commit | 舊審查不再授權新版本 |
| 中途中止再啟動 | 工作可恢復或明確失敗，不重複提交或重複外部動作 |
| 相同交接事件重送 | 不重複派工、不重複付費執行 |
| 超出輪數或缺必要證據 | 停止並列明原因，不無限辯論，也不靠摘要判成功 |

六項通過，再在第二個 repository 驗證可移植性；只有出現具體權限控制缺口才試 AGT。有無省 Token、是否提高品質是後續測量問題，本次選型不預先承諾。

## 本次證據界線

已做：讀取自有清單、registry、現有協作規則；查上游功能與安裝文件，讀 AGT plugin 的 manifest 與限制。

未做：安裝任何候選、執行其測試、驗證 Polly 內部設定、驗證 agent 間自動調度、量測品質／延遲／成本、啟用分支保護或付費資源。因此不能稱為部署完成或安全驗收完成。

此檔可供 Claude 在 repository 中直接讀取並準備試點。既有 benchmark 的修復回合與本工具選型是不同工作，請保持證據和 gate 分開。

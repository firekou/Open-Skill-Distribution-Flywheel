> 2026-09-24 最新排序校正：先交外部價值證據與增量差距裁決（EXTERNAL_VALUE_EVIDENCE_AND_INCREMENTAL_GAP），再決定是否需要評估工具。stars／引用是線索，需追查第三方實證、使用效果與上游需求；不得把方法建設當成新增社會價值。詳見研究文件末節。

## 最新補充：外部貢獻先行（2026-09-24）
先讀 [AI 研究室外部貢獻與方法](../research/AI_LAB_EXTERNAL_CONTRIBUTIONS_2026-09-24.md)，依 LAB-EXTERNAL-CONTRIBUTIONS-20260924 更新研究待辦。先看別人已做到什麼、如何評估、開放與維護情況，再重現與判斷值得引入的差距；沒有新增價值就直接採用原作。研究不等待產品公開發現授權。文件中的 LAB-EXTERNAL-METHOD-01 尚未派送／接單，不能視為 active claim 或已實測；任何實作仍依有效工作包與分支流程。保留既有任務兩輪上限與權限邊界。

# Claude 現行產品交接入口

## 2026-09-24：依可確認成果續作

先讀可信 main 的 governance/OPERATING_RULES.md、decisions.json、state.json、reviews/STATUS.md，以及 [成果與信心準則](../governance/OUTCOME_CONFIDENCE.md)。每輪先說明如何推進有用工具／skill、可選 ATK Router／API／MCP、技術分發與實際採用。

main revision 24 已記錄：M1／P5-R4-01 由 PR10 完成獨立隔離重放；不要重跑舊等待指令。PR8 R4 對 9ab2cbb09f44a94a0e52d8e8c4d6bbb9de2d6b34 僅接受 closure record，仍有公開入口、sender 證據與 issue #3736 措辭條件。啟動時重新查 live head 與最新 review，不能沿用舊批准。

本次新增的是交付準則，不是新 repair packet。既有修復已達 2/2，不開第三輪、不重做三候選篩選或已完成的 Headroom 範例。下一 checkpoint 維持 state.json 的 OWNER_GITHUB_DISCOVERABILITY_DECISION。無依賴且已授權的工作直接完成到可用小交付與必要驗證，不只寫下一份計畫，也不把本文件視為額外部署／發布／費用授權。

後續有效工作包須指定：誰使用、完成什麼真實任務、成功條件、最小成果、證據取得方法及停止點。執行結果在既有工作包指定的 executor response 追加；distribution 任務使用 ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md，adoption 任務沿用 ATK_OPEN_ADOPTION_EXECUTOR_RESPONSE.md，不重複另建帳本。每次記錄新增成果、固定 SHA、重播方法、效果及未知，向負責人提供可親自確認的連結。內部測試與外部採用分開，不用 mock 或歷史 live 紀錄冒充本輪成功。

---

## 以下為歷史快照，停止點已由上方入口與最新 main 帳本取代

## 2026-09-23：PR8 A package 條件修正已覆核

當前工作仍是 [完整執行包](ATK_OPEN_ADOPTION_EXECUTION_PACKAGE.md) 的 `ATK-OPEN-ADOPTION-01`。revision 2 已由 Claude session `session_01RFeCsTYkVywjHvXk7od7Ab` 交付；[R2 獨立覆核](PR8_R2_CONDITIONS_8161c6a3.md) 對內容 SHA `8161c6a33251b06c44db9f5dbabc9431fa73b67d` 判定 **APPROVED_WITH_CONDITIONS**，A-R1-01 至 A-R1-05 均已關閉。

**不要再接或重做 revision 2，也不要因本入口建立第二輪修復。** live/result head `b76fc7ba08deade6733f140d3a37aadfd201d51c` 在 content head 後只追加 executor response 與 controls。非阻擋的 `EVIDENCE_FORMAT.md` 四／五 fixture 字詞列 merge／發布前 editorial backlog，不是新的自動派工。

下一 checkpoint 只有 M1／P5-R4-01：由獨立 reviewer 在無 secrets、無外網、唯讀來源、無 GitHub write token 的合格環境綁定 PR5 `304af885193245da7186cb6b9ab247ec2494bd86` 重放。這不是 Claude 作者工作；不得以同 session 自測替代，也不重派舊 PR5 修復。完成前不發邀請、不套用 PR5 patch。其他無依賴的採用準備可繼續，不等待 controller ACTIVE。

沒有 merge、部署、上游送出、settings/secrets/權限變更或新增費用授權。

---

## 以下全為歷史紀錄，不得作現行派工指令

## 2026-09-21 負責人最新續作：兩條線收斂與 ATK 接入需求

目標來源：負責人要求直接往下規劃，並確認最小 ATK 案例需要 token 或 MCP、是否已提供。
本輪交付：沿用 Headroom + ATK，讓需要分析部署 log 的使用者能先確認壓縮後關鍵資訊仍在，再選擇 ATK 取得答案。
主線連結：既有可用資產 → 精確版本獨立驗收 → 可跟做入口與分享草稿 → 真實採用。
必要驗證與停止點：只補既有缺口；完成本工作包送審，沒有新內容不重審。
範圍差異：不重新挑三工具、不建立 adapter 或 MCP、不把 controller ACTIVE 當成產品前置條件。

### A. 治理線：保留必要交接，停止框架擴建
核對 PR6 最新 head、R4 與 R5 scope reduction。此次觀察 head 為 7de3043938b4179f5011f82927aaeecc5b82cbd1，controller 審查仍綁 25457fbd2ff02a900d55538eb4e2fa0893663c31、BLOCKED。
沿用 GitHub 工作單、精確 SHA、獨立 reviewer 與既有事件路徑。包 A 保留 backlog，包 B 等待合格隔離後端；本次一般續作不解讀為重置兩輪上限或開第三輪 controller 修復。
下一個治理成果是明確的隔離後端能力證據與可執行驗收條件；沒有合格環境就如實記錄缺口，不安裝平台、不增加 launcher 或輪詢。不得讓這項依賴阻塞 B 線可離線完成部分。

### B. ATK 產品線：既有 Headroom 案例完成驗收與採用準備
本輪查核 PR5 仍為 Draft，head e8a15d7d2c012007a69ca69c7e4630c33147c4a6。啟動時重新查 live head。
1. Reviewer：依 PR5_R6_REVIEW_933446ab.md，在合格隔離環境重放既有 pr5-r5 證據包，限定 P5-R4-01 與直接回歸。作者不再補同類自跑證據替代獨立驗收。缺隔離環境維持 NEEDS_INFORMATION。
2. Executor：先核對既有 README、DISTRIBUTION、分享稿與 evidence，已有成果不重寫。只修影響首次使用的缺口，保留歷史數據限制。所有說明分清「本機壓縮」與「live 呼叫會將處理後內容送至 ATK」，不可暗示 live 路徑資料完全不外送。
3. 在既有交付目錄補齊一份最小試用步驟：用合成部署 log，提問失敗 migration 名稱與 SQLSTATE；先離線確認關鍵資訊保留，再於權限和費用已明確時做 live。保存輸入 checksum、版本、prompt、實際模型、答案、usage、時間和錯誤類型，不保存秘密或客戶 log。
4. 已有 2026-09-18 live 記錄只能作歷史案例，原 live 輸入未保存，不得用重建資料冒充重放。新的成功數據另立紀錄，沒有新數據不宣稱重測。
5. 採用驗收：至少一位非作者使用者按 Quick Start 完成任務，記錄版本、結果、卡點與協助次數；人工直給、目錄發現、公開搜尋分開。目前外部使用仍無證據，不把準備稿或內部測試當採用。
6. 兩篇分享草稿及入口已存在，沿用並校正即可。準備具體可審稿；外部邀請、上游或社群發送、合併與發布依原授權界線，未取得授權前不送出。

### 憑證與接入盤點（只記 metadata，不讀取或輸出秘密）
- 此案例是 API 配置接入，不需要 MCP server 或 MCP token。
- PR5 README 記錄曾使用 ATK live API；這證明作者曾取得可用憑證，不證明此刻仍可用或 reviewer 可取得。
- 本次 GPT 環境 ATK_API_KEY、ATK_BASE_URL、ATK_MODEL 均未設定；未檢查其他 runtime 的秘密值，也未做模型呼叫。
- KEY-ROTATION 仍為 action_required，輪替狀態未知。不得找回或重用舊金鑰，不請負責人在聊天貼新 key。
- 歷史已用設定：Headroom x-headroom-base-url 為 https://api.aitokenking.com.tw/api（此 header 不帶 /v1）；模型 claude-sonnet-4.6。這是歷史實測設定，不保證當前帳號模型仍可用。根目錄舊 integration contract 的不同示例 URL 不能直接替換此案例。
- 新 live run 真正需要：執行環境安全注入的有效 ATK_API_KEY、核實的端點與可用 model，以及明確的測試呼叫/費用上限。缺 key 不影響規劃、文件和離線驗收。
- Executor 先回報現有 runtime 是否已有新 key（僅 SET/NOT_SET）、輪替確認是否存在、是否有使用授權。只有確實沒有才請帳戶持有人配置；不要求再次搬運既有憑證。
- live 提案預設單一合成任務、direct/proxy 各一次、零自動重試；先依實際模型限制設定輸入及輸出上限並提出費用上限。尚未批准的付費呼叫保持 0，不以「有 key」推定支出授權。

### Repository 交付
沿用產品分支與 Draft PR；不與 PR6 混合。把本輪差異、精確 SHA、已驗證與未知、試用步驟及剩餘配置缺口寫入 reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md（若分支已有則追加）。
GPT review 寫 main。技術交接留 repository，無須負責人搬運報告。
本補充是規劃工作包，沒有宣稱新模型呼叫、獨立 runtime 驗收或外部採用已完成。

---

# 現行產品交接：PR5 等待獨立隔離驗證

2026-09-21 接管更新：先讀可信 main 的治理入口、decisions、state 與 reviews/STATUS.md，啟動時核對 live head。
最新 review 為 reviews/PR5_R6_REVIEW_933446ab.md，綁定 933446ab230e6fb8b41d79b596ef3c19b721fb7a，NEEDS_INFORMATION。P5-R4-01 作者已修復並送證，剩下獨立隔離 reviewer 重放既有 reviews/evidence/pr5-r5/README.md 的證據，不再要求作者重複同類自跑證據。
1A／2A／3A、免費技術資產、可選 ATK 接入、分發及採用主線維持；已有 headroom 小交付，不因舊三候選 prompt 重新造工具。治理 PR6 不作本產品驗收的額外前置門檻；通用 benchmark、Freeze 與框架試點不重開。
新內容才重審；無新 head/證據安靜結束。通過後做既有入口發布準備與搜尋／採用驗證，對外送出、merge、部署遵守原授權。
GitHub 交接已由 govern-github-agent-handoffs 接管。reviewer 事件登記涵蓋本 repo；Claude 新 session 持久 launcher 未驗證。報告與摘要仍寫 main。下列內容保留為歷史，不再重派。

## 歷史 R4 工作單

# 現行產品任務：PR #5 完成一項 R4 條件

先讀可信 main 的 governance/OPERATING_RULES.md、decisions.json、state.json，核對 live PR #5。
1A／2A／3A 已批准，勿重問。既定 headroom 交付、免費品牌與上游備稿範圍不變。

最新獨立 review：reviews/PR5_R4_REVIEW_d1930e4.md，綁定 d1930e4696f11cfb3cdae2f59d1b3692b68ee127，APPROVED_WITH_CONDITIONS。
Executor 只修 P5-R4-01：parse_args 不得回顯任何未知 raw token，包含被誤當旗標的 dash 開頭 needle。最小方案是固定錯誤提示加 --help 指引。依 review 的普通值、dash 值、equals、合法參數正控制驗收；同步受影響文件與實際測試數，提交新 SHA。
若 live head 已改，先比對差異與是否已有新 review，不套用過期通過。

Reviewer 下一份 PR5_R4_CONFIRM_<short-sha>.md，只確認此條件及直接回歸；達標結束修復輪。不重开benchmark，不再挑三工具或造adapter。
產品交付通過後，下一步是入口發布準備及搜尋／採用驗證；合併、發布、About/topics、上游送出仍遵守既有界線。

本輪已註冊PR5新commit事件GPT review，首次事件尚未驗證；沒有遠端Claude launcher。報告與記帳寫main，不在被審分支追加observed_head補寫commit。GOV-BOOTSTRAP勿重複建立同一reviewer觸發器，也不得稱完整閉環ACTIVE。

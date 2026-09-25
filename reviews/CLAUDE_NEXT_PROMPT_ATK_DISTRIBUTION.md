# Claude 完整執行 Prompt：ATK 從外部成果到實際採用
版本 2.0｜2026-09-26｜單一執行入口
Repository：https://github.com/firekou/Open-Skill-Distribution-Flywheel
負責人本輪指示：把整個執行計畫、目標與所有階段細節整合為完整 Prompt，交給 Claude 執行。
全程藍圖：[ATK_END_TO_END_BLUEPRINT.md](ATK_END_TO_END_BLUEPRINT.md)。

## 1. 你的責任與最終交付
你是 Claude executor。直接執行可做的工作、產生可驗收成果，不再只回覆新計畫。GPT 負責獨立 review；你不可自行宣告 APPROVED。
目標：找到外部有用 AI 工具與 skill → 理解原作與真實需求 → 必要改善及可選 ATK Router/API/MCP 接入 → 技術分享與分發 → 非作者完成真實任務 → 再次使用 → 開源貢獻及可持續回收。

最終必須能用證據回答：
1. 哪些非作者完成了什麼任務，成功條件、失敗和樣本分母是什麼？
2. 原作已提供什麼？我們額外減少多少設定、排錯、學習或支持負擔？
3. ATK 真實接入是否完成，與直接用原作相比的限制和成本是什麼？
4. 外部是否再次使用、重現或引用我們的成果？是否有可核對的上游回應？
5. 維護、provider 和支持成本是否可負擔？應保留、改善、直接推薦原作或退出？

文件數、stars、mock、CI、merge、模型呼叫數都不能代替上述答案。缺證據記未知；没有增量則推薦原作，不硬造 adapter。

## 2. 啟動程序與當前起點
先 fetch 最新 main，依序讀 AGENTS.md、governance/OPERATING_RULES.md、governance/decisions.json、governance/state.json、reviews/STATUS.md，套用 atk-goal-alignment 與 executive-review-gate，完整讀全程藍圖與本 Prompt。
查 live PR base/head、diff、comments、最新 main review、executor response，不能依舊 PR body 判定目前版本。

目前可核對的起點：
- 三候選 Aider/Continue/Open WebUI 已比較，Aider 已選定，不重做選題。
- PR14 固定資產 d1474670db12934c80caa05674c8e4320cbad312 已有原生設定、最小任務、Quick Start、離線檢查器、兩篇技術草稿。R2 三項條件已關閉。真模型和外部採用未驗證。
- PR16 head 57fa50900035cb6eef316504b065cf98a8b4fee0，ATK-VALUE-READINESS-01 r1 為 BLOCKED。先完成下節 revision 2；不要重建 PR14。
- 本 Prompt 整合全程，不重置任何修復輪次，不替代現行精確 head review。
- PR15 的治理問題只限制該 skill 的權威使用，不阻擋無依賴產品工作。controller/持久 launcher 不是產品前置。

若 live 已有較新成果，先沿最新 review 續作，不套用過期修正；相同 work_id 有 active claim 就續用該工作，不另開平行分支。

## 3. 現在立即執行：PR16 revision 2
work_id: ATK-VALUE-READINESS-01
revision: 2
branch: claude/atk-value-readiness-01
source_head: 57fa50900035cb6eef316504b065cf98a8b4fee0
dedup_key: firekou/Open-Skill-Distribution-Flywheel:16:ATK-VALUE-READINESS-01:2:57fa50900035cb6eef316504b065cf98a8b4fee0:executor
repair_round: 1/2
review: reviews/PR16_R1_VALUE_READINESS_57fa5090.md

只修改 PR16 原有九個路徑；可在 research/adoption/aider/evidence/ 補 manifest/raw metadata。保留既有原始證據，追加修正版與 supersedes 對照，不覆寫舊觀測。PR14 檔案不改。
四個具體工作：
1. SOURCE_AND_GAP.md 完整納入 Aider #4027 本文、相關留言、版本及原回報者 v0.86.1 無法重現後關閉的事實。把它標成歷史案例。查當前與檢查器功能相符的需求，保存查詢、時間、範圍、結果與排除理由；找不到就記 0，不把歷史缺陷變成現行需求。
2. STUDY_PROTOCOL.md 不再用不同人的 A/B/A 來回答材料效果。若只做 1–3 人探索，明定只判可行性及卡點；若要比較增量，提供兩個固定、等難度任務，配置 AB/BA 順序、能力背景、學習效應、支援介入、品質底線與逐人配對資料。新任務可放同研究 evidence 目錄，不改 PR14 評分測試。探索樣本不宣稱普遍或統計顯著改善。最低有用差異須事前有理由，不能事後挑指標。
3. 各 base-path 與 retry case 補去敏 manifest：case_id、完整安全命令/config、版本、fixture hash、server-ready、起迄 UTC、exit、stdout/stderr 與 SHA256、觀察和限制。原紀錄沒有的欄位不得回填猜值；在原授權離線範圍可重跑，不能重跑就將主張降為 REPORTED。相同 JSON 不能獨自證明三次不同執行。
4. RELEASE_AND_ACCESS_PACKET.md 與 TRIAL_RUNBOOK.md 將 provider key/project 硬費用上限改為待核實能力；未選定 provider 不預設存在。區分警報與真正拒絕後續請求的硬限制，列不能證明上限就不執行 live 的 gate。GitHub/session 權限沒有 API 證據就寫 unknown。

交付五份文件的一致修正、證據索引與 executor response 追加，提交同一 Draft PR。逐項回覆 P1-01 至 P1-04 的證據，不自行關閉 reviewer findings。交 reviewer 後停止本批，不自行進入真呼叫。

## 4. 各階段的詳細執行與終點

### S0 全程對齊
輸入：本 Prompt、藍圖、可信 main 帳本和 live PR。
工作：建立每階段的已完成/可執行/待 review/缺條件清單，對照既有成果；把每個缺口連到下列固定 work_id。
產物：executor response 的全程進度表、依賴、下一可執行項。
驗收：沒有把規劃寫成已運行、沒有舊入口重跑。這是啟動步驟，不另開一個只寫計畫的 PR。

### S1 外部研究與價值差距
當前併入 readiness 修正，不重選 Aider。後續候選每批最多三個深讀、一個實作。
工作：讀官方 code/docs/release、完整 issue 討論、第三方正反使用報告及 GitHub/GitLab 下游使用。記作者、固定版本、日期、license、code/weights/data/eval recipe 開放程度、維護與回饋路徑。
追查引用與 stars 背後是否真的使用、重現、比較或只是關注；未知就寫未知。
比較原作、替代方案、我們的增量假說與反證。裁決只選：直接用原作、改善文件、薄接入、小修正、不採用。
終點：可追溯需求與選擇理由；沒有現行需求時交需求探索，不造需求。

### S2 可用技術資產
既有 ATK-AIDER-FIRST-USE-01/PR14 已完成離線範圍，不重建。
必要後續修正須有受影響主張與單獨允許範圍。
資產要求：固定來源、可跟做安裝、原生 provider 設定、可選 ATK 與退出切換、最小真實任務、不可任意修改的評分測試、常見錯誤、兩篇完整技術草稿。
草稿一說原作價值、實際操作、失敗及心得；草稿二說可選 ATK 設定、資料流、費用和限制。不拿上游功能算我們貢獻。
驗收：精確 SHA 獨立 review；離線協定與真實模型分開。沒有接點必要性就不加 SDK/MCP server。

### S3 真實接入：ATK-AIDER-LIVE-01
前置：readiness 修正通過、固定資產、指定且已授權 endpoint/model/runtime、可用安全注入方式、明確呼叫/token/總費用上限與授權紀錄。
先備：live 執行命令、受保護測試 hash、輸入、成功條件、主呼叫/helper/retry 盤點、價格來源與日期、預估最大成本、停止方式。驗證 LiteLLM 等底層重試，不能拿 Aider 的 9 次推論當完整費用保證。
真呼叫：先做最小連通與一個固定任務，在既定總上限內執行；禁止自動無限重試。測試結果加人工語意核對才判成功。失敗也保存，不追加未授權嘗試。
產物：integrations/aider-atk/evidence/live/ 的去敏輸入/輸出、命令、版本、起迄、exit、請求數、usage/實付可取得部分、測試與失敗原因。
終點：指定端點的一次真實任務可核對。缺 access/budget 只停真呼叫，其他準備照做。不得要求把 key 貼聊天或 commit。

### S4 發現與首次使用：ATK-FIRST-USE-01
先備：固定 SHA 入口、兩篇可直接發布的完整文案、適合對象、渠道、帳號能力、授權範圍、回饋表與去識別方式。
若尚無 live 結果，內容明標只驗離線；不能宣稱 ATK 真接入或模型任務成功。
公開發送/邀請必須有該資產及渠道的有效授權，舊 Headroom A4 額度不能搬來。About/topics、merge、社群發文都不由本 Prompt 自動批准。
在獲准範圍內逐一進行，第一批規劃最多三位匹配非作者，0 名也如實結束；不能為數量亂邀請。
每人記：來源方式（人工直給/受邀/公開發現）、同意、環境、首次成果時間、任務通過、錯誤、支援分鐘、成本、放棄原因、再用意願。內部 Agent 演練另列。
產物：research/adoption/aider/results/，保留全分母及失敗。
終點：至少取得可判讀的首次使用或不使用原因；沒有使用不能寫採用成功。

### S5 增量價值：ATK-VALUE-DECISION-01
前置：已固定的研究設計及相應真實資料。
工作：按 protocol 比較官方直用與我們指引；相同模型/provider、等難度任務、保留順序和協助差異。沒有可比資料就只做個案敘述。
品質不得退步；列首次成功時間、錯誤、額外學習、支援、費用及維護攤提。資料不足不算 0 成本。
另查不同日期再次完成任務的證據，意願與實際再用分開。
產物：research/adoption/aider/value-review.md，逐項標資料/推論/未知，列反例。
终點：保留、改善、直接推薦上游或停止的一個裁決；不能從小樣本推廣到所有開發者。GPT 獨立覆核後才把價值主張放進對外文案。

### S6 複用與公共貢獻
ATK-REUSE-02：第一場景外部價值成立後，依真需求選一個第二場景，先定路徑/來源/驗收再實作。只抽出已證實可重用方法；優先沿用，不建通用平台。
ATK-UPSTREAM-01：可提早唯讀查重和備稿。檢查上游 release、issues/PR、貢獻規範與 license；準備最小重現、版本、反例、預期/實際、修正或文件 diff、驗證。放 research/upstream/。
送上游需另外有效授權；投稿、維護者接受、第三方使用分開記錄。
終點：第二場景重用證據，或一份能被維護者審閱的具體贡献。上游已有功能就推薦既有做法，不重造。

### S7 持續運作、回收與退出：ATK-SUSTAIN-01
前置：一個完整且有起迄日期的觀察窗口。
工作：去識別記活躍任務專案、首次成功、跨日/跨週再用、失敗、支援工時、維護變更、可歸因實收與 provider/其他變動成本。
淨工時改善 = 基線工時 - 使用後工時 - 額外學習/接入/維護攤提。
經濟結果 = 可歸因實收 - provider 成本 - 其他變動成本 - 明示假設的支援成本。無資料記未知，不虛構時薪。
產物：research/adoption/portfolio-review.md，包括維護負責角色、來源版本、受影響回歸、擴張/維持/縮減/退出裁決。
退出保留歷史證據、替代方案、遷移步驟和原因。連續兩個有界批次沒有新需求/效果，交取捨裁決，不能換 work_id 無限修復。
終點：能回答是否值得繼續投入，以及誰在實際受益。

## 5. 時程、交接與自動接續規則
90 天是探索管理窗口，不是成果保證或新增額度；T0 為該階段實際前置具備之日。
- 0–7 日：readiness 與真實接入準備。
- 8–30 日：第一條入口到非作者成功路徑；規劃最多三位探索，至少一位成功為目標。
- 31–60 日：規劃累積五個外部專案、兩個不同日期再用。
- 61–90 日：規劃十個月活任務專案、三個跨週再用，完成成本和維護裁決。
數量不是邀請授權，不為湊數略過品質，也不新增 polling。

每次開工先在既有 GitHub conversation 登記：
work_id、revision、source main SHA、source asset/head、session/run、scope、dedup key、絕對 UTC deadline。
PR16 沿用既有 dedup；後續格式 repo:work_id:revision:source_sha:executor。單批 45 分鐘工作窗口、claim 起 24 小時期限；不夠就交 partial、精確缺口及可恢復步驟，不偽報完成。
每批只一個主要 work_id。成果 commit/ Draft PR、executor response 齊就交 GPT；不得自己批准自己的實作。
GPT 通過後，重新核對依賴，續作下一個已定義且在授權範圍內的包；不要求負責人重新給方向。某階段缺權限只停該動作，完成無依賴準備。不得趁等 review 更改同一受審 head。
每包最多兩輪必要修復，舊輪次不重置；耗盡時交縮小或停止建議。
不假設 comment/label 會啟動 Claude。訊號、接單、成果 SHA、獨立驗收各自有證據才提升狀態；本 Prompt 不批准新 launcher、付費 fallback 或排程。

## 6. 交付格式與治理邊界
實作在工作分支，送 Draft PR，不自行 merge。review/planner 文件由 GPT 依 REVIEW-MAIN 寫 main。
reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md 追加，保留原紀錄。每批含：
- 本工作如何幫誰完成何種真實任務。
- work/revision、source/result SHA、session/run、dedup、期限。
- 變更路徑、五階段證據分類 REPORTED/OBSERVED/TESTED/VERIFIED/REPRODUCED；自己的測試不能稱獨立重現。
- 實際命令、exit、版本、時間、輸出雜湊、通過/失敗及未測原因。
- findings 對照與證據，findings_closed_by_executor 保持空，交 reviewer 判斷。
- 全程階段進度、下一 work_id、已備妥材料、真正缺的授權或能力。
- 只向負責人報新增成果、實際效果、重大風險及具體待決材料，不要求搬運報告。

Non-goals：不重啟通用 benchmark/Freeze/Omnigent/AGT/OMA；不新增平台、controller、無限候選搜尋；不以 mock 代替真成功；不自行部署、發布、邀請、送上游、修改 secrets/權限或新增未授權支出。
負責人此次授權整合與執行規劃不等於解除上述外部動作界線。真正需決定時，先備妥固定資產、文案、對象/渠道、端點/model/成本/停止方式，再把單一具體決策交回。

現在開始：讀 live state，承接 PR16 revision 2 四項修正並完成交付，不重做已驗收離線資產。

## 歷史
本版取代本入口先前 PLANNED_NOT_DISPATCHED 的過期起點；全程藍圖中的 r1 契約保留作歷史，現行執行以 main 帳本、最新 review 與本版為準。
[舊入口封存](archive/CLAUDE_NEXT_PROMPT_BEFORE_20260926.md)僅供追溯。

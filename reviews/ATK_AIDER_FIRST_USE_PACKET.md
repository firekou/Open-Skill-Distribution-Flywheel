# ATK-AIDER-FIRST-USE-01：原生設定與首次任務交付
revision: 1
date: 2026-09-24
role: Claude executor；GPT planner/reviewer（不得批准自己的實作）
source main: 251f9755ed5c1b4fd260b23b622e8ba5fad278eb
upstream source: Aider-AI/aider@5dc9490bb35f9729ef2c95d00a19ccd30c26339c
branch: claude/atk-aider-first-use-01
dedup_key: firekou/Open-Skill-Distribution-Flywheel:ATK-AIDER-FIRST-USE-01:1:251f9755ed5c1b4fd260b23b622e8ba5fad278eb:executor
claim期限：訊號時間起24小時；接單時寫絕對UTC期限。單次工作45分鐘上限（模型工作20、測試10，其餘交付）；逾時交部分成果與精確缺口。
最多兩輪修復；舊PR4/5/6/8的修復計數完全獨立，不能借此重修它們。
預算：新增API費用0，無live provider呼叫。
此新交付承接負責人要求繼續延展搜尋與規劃，以及既有工作分支小交付指示。與舊採用邀請包無依賴。

## 目的與選擇
讀 research/ATK_THREE_TOOL_VALUE_REVIEW_2026-09-24.md。幫開源開發者用Aider完成一個小型程式修改；採原生API配置，ATK可替換。不是重造adapter、重現整個外部遷移案例或比較模型排行榜。
外部第一手使用報告支撑選題；我們的時間改善仍是假說，先交可跟做資產，不宣稱效果。

## 開工與接單
fetch main並讀AGENTS、OPERATING_RULES、decisions、state、本包及指定skills。檢查同work_id既有分支/PR/comments/active claim，若已有有效接單或成果不得重開。先回覆session/run、work_id、revision、source head、dedup、UTC期限與scope，再從固定main開新分支。
source是研究報告commit；本包與可信治理讀開工最新main，記錄policy SHA。若同work_id範圍已更新，停舊revision而不是自行推定。

## 交付範圍與順序
僅可改 integrations/aider-atk/** 及 reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md（追加本work_id）。
1. 來源與安裝：SOURCE.md記source SHA、LICENSE、Python與相依版本、官方配置依據。優先固定release；本次指定source含dev版本，只能如實標示source pin，不能自稱穩定版。若改用release，先給與指定source的相關差異理由，不悄悄追latest。
2. Quick Start：Linux/Python3.11單一路徑；原生OPENAI_API_BASE/OPENAI_API_KEY與openai/model。base、model須由使用者環境提供，缺值先停止；不硬填歷史ATK endpoint作新live證據。秘密只進環境，不進檔案、CLI參數、log。Windows/macOS標本輪未測。
3. 最小任務：sample/import_contacts.py、固定tests、TASK.md。任務及五種情境按研究報告；baseline固定失敗及預期行為要可查。禁止executor把参考修正版或假回應當成Aider實際成果；測試不得由受測Aider修改。保留原檔與diff。
4. 配置與診斷：先文檔/設定即可；只有明確缺口才加小型本地檢查器，不轉送請求、不建立新HTTP client或gateway。區分缺base/model/key、模型prefix、API root與/chat/completions錯填；不猜URL、不列印key片段。
5. 驗證：無秘密隔離環境核對CLI/配置。若用local假server，保存實際請求路徑與模型欄位（移除auth），證據標OFFLINE_PROTOCOL_ONLY。關閉可選analytics/update不等於證明無外連，隔離設定與觀察另列。--dry-run不當成不收費保證。查清helper model、重試、repo map、test/commit等額外動作；不能控制呼叫上限則live維持不啟用。
6. EVIDENCE.md：命令、exit、原始輸出、來源和input雜湊、實際環境、失敗；clean install/CLI/協定/真模型/外部使用五欄分開。
7. 兩篇完整繁中草稿：AIDER_WHAT_WE_LEARNED.md 說外部原作與具體適用情境；ATK_OPTIONAL_SETUP_DRAFT.md 說可選設定、實測範圍與未知。引用原作、不得將歷史案例成本當新價格，不寫尚無證據的省費或效果。未發布。
8. 在新分支提交，開Draft PR，追加executor response，回報content/result SHA及成果連結，停止。不要只交第二份計畫。

## 本輪驗收
- 可按固定來源建立環境；若隔離/依賴下載限制，交已完成文件、fixture與限制原文，不假稱已跑。
- 五種任務情境與baseline真實結果可重跑；無live時不要求模型完成測試。
- 配置忠於上游，沒有多餘adapter與ATK綁定，未帶入PR4/5修補。
- 所有成功主張綁命令/證據；假server只證協定，本地測試只證fixture/檢查器。
- 兩篇完整草稿＋Quick Start＋來源歸因＋Draft PR；缺live不能阻擋以上交付。
Reviewer另取精確SHA確認範圍、重放受影響檢查、保留未驗證，review寫main。

## 後續效果與價值驗證（規劃，不包含本輪付費／發送授權）
第二階段：確認安全注入的新憑證、端點、model與明確呼叫/費用上限後，跑原生設定與我們引導的同任務比較。算入helper/retry與安裝排錯時間，保存失敗。無充分權限只停live，不停文件交付。
第三階段：找真正要修改既有程式且願意試用的外部使用者，資產通過及發送授權成立後才邀請；不要將研究引用者自動當邀請對象。首批最多3位探索，不做統計普遍主張。
記：首次成功時間、配置錯誤、協助次數、任務測試結果、人工review工時、實付費用、是否重用。
配對任務順序要平衡，降低熟悉效應；報每位結果與分母。
增量裁決：若原生配置同樣容易、我們沒有可觀察改善，就推薦官方文檔；若只在特定情境有改善，限定範圍。不為證明ATK而挑最好模型或刪失敗。
第四階段：有可重現缺陷才備upstream issue/PR草稿並查重；未授權不送。原生設定足夠時，不向上游塞ATK廣告PR。

## 明確排除
不merge、部署、讀/改secret、送上游、邀請、付費呼叫；不新增polling/controller/eval平台；不要求人搬運報告；不宣稱訊號等於Claude已啟動。無需負責人再選三候選或批准相同規劃。

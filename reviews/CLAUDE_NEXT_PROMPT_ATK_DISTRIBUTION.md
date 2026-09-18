> **負責人最新目標補充：[外部 Agent 發現、採用與解題驗收](ATK_AGENT_DISCOVERY_AND_ADOPTION.md)。** PR #4 的小交付結案不代表整體目標達成。下一個工作包是一個真實工具的可發現入口、可跟做接入與任務驗證，回覆於 `reviews/ATK_AGENT_DISCOVERY_EXECUTOR_RESPONSE.md`；下方舊「下一步／停止」只適用原交付，不得據此停止整體主線。

# Claude 執行 Prompt：方向校正與第一個 ATK 接入交付

你是 ATK 的執行者。請在以下 repository 接續工作：
https://github.com/firekou/Open-Skill-Distribution-Flywheel

本輪目標：完成一次方向校正，接著交付第一個服務 ATK 技術分發與 Router 接入的小成果。不要只回覆計畫或更新文件就停止。

一、先同步最新指示
fetch 最新 main，記錄起始 commit，保留現有工作，避免覆蓋其他人的變更。閱讀：
1. AGENTS.md
2. .claude/skills/atk-goal-alignment/SKILL.md
3. reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md
4. reviews/README.md、reviews/STATUS.md
5. ATK_OPEN_SKILL_STRATEGY.md、ATK_ROUTING_INTEGRATION.md
6. .claude/skills/executive-review-gate/SKILL.md

若你在旧分支，不得因該分支缺少上述新規則而繼續舊排程。以負責人最新明確指示為準，歷史計畫只作背景。

二、理解這次修正
我們的主線是：
找到有用 AI 工具／skill → 整理與改善 → 透明可選的 ATK 接入 → 技術分享與分發 → 實際使用與回饋。

先前偏航，是把 benchmark 修復、可信量測與治理架構建設逐漸當成產品中心。現在已校正：
- 通用 benchmark 全面修復、Freeze 與正式執行暫停，不作為工具分享或接入交付的前提。
- Measurement & Trust 保留為研究假設，不代表已決定開發量測產品。
- Omnigent、AGT、OMA 的優先導入試點暫停。沒有具體交付瓶頸，不增加管理系統。
- 保留必要功能、安全、授權與來源檢查；不宣稱未驗證的省錢或品質效果。
- 暫停不等於缺陷已修好。歷史 OPEN finding 保留，不自行標 CLOSED、APPROVED 或合併 benchmark PR。

三、先更新當前工作狀態
核對工作分支、待辦與執行入口，修正仍要求「先完成 benchmark 才能往下做」的有效指令，保留歷史與更新理由。
把已完成、暫停、未驗證、下一步分開記錄。不重寫所有歷史文件，也不新增一套方法論。

四、直接開始第一個小交付
先讀現有 registry/materials.json 與整合候選資料，確認是否已有可復用成果，不重做全網搜尋。

挑三個候選，每個簡短說明：
- 幫哪種使用者解決什麼問題。
- 現成專案與來源。
- 模型呼叫點及 ATK 可接入的位置。
- 最小交付、必要驗證與維護負擔。
- 使用者如何從技術內容走到實際使用。

你自行選其中一個接點最清楚、修改最少、授權適合的候選開始做，不把一般技術選擇推回給負責人。優先原生 provider 設定、可運行範例或薄 adapter；只有必要時才 fork，不另外重造 Router。

本輪交付：
1. 一個最小可運行範例或 ATK 接入。
2. Quick Start、環境變數範例及切換其他 provider 的說明。
3. 與承諾功能相符的驗證紀錄及已知限制。
4. 兩篇指向該資產的繁體中文技術分享草稿。

確認實際 ATK endpoint、model ID 與支援能力，不把舊文件示意值當成已驗證服務。不要提交真實 key。
若缺憑證，完成離線可做的實作、測試與文件，明列 live 驗證缺口；不把 mock 通過稱為 ATK 真實連線成功。
未另有授權，不購買資源、發送上游訊息或發布社群草稿。

五、每輪先確認方向
在既有交接文件寫五行即可：
目標來源、本輪交付、與主線的連結、必要驗證與停止點、是否增加範圍。

若發現新問題，先判斷是否阻擋本輪交付；不相關的列待辦。不能為了避免偏航而略過必要品質檢查，也不能為了嚴謹而無限擴大測試。規格、實作、實測、外部採用必須分開。

六、提交與交接
在獨立工作分支提交本輪變更，依既有授權推送並建立或更新 Draft PR；不要合併。
回覆寫入：
reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md

記錄候選取捨、實際交付路徑、精確 commit、測試命令與輸出、限制、PR 連結及下一 reviewer 要驗什麼。狀態先標待獨立 review。
後續技術溝通直接透過 repository 檔案，不要求負責人搬運文件；沒有實際觸發機制就不要宣稱已喚醒 reviewer。

完成上述小交付並送審，或遇到無法解決的必要外部阻擋且其餘可做工作已完成，就是本輪停止點。不要自動擴張到第二套框架或整個產品平台。

最後給負責人的回報只需說：
這次做了什麼、怎麼推進 ATK 原始目標、哪些已驗證、還卡什麼、下一停止點，以及是否需要其決定。沒有真正的商業決定就寫「無」。

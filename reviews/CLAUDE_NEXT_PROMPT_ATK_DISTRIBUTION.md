# Claude 下一輪執行 Prompt：PR #5 修復、單一工具採用與免費品牌分發

## 已確認決策與目標

2026-09-18，負責人明確選擇 **1A／2A／3A**：
1. 集中 headroom 一個工具，修復既有問題，補乾淨安裝、根目錄入口與問題導向描述，驗證可找到、可使用。不擴充另外兩個工具。
2. 先做免費實用資產、明示 ATK 品牌與可選接入，觀察使用及導流。付費樣本保留未批准草稿，不將量測服務升格成產品方向。
3. 準備 headroom 上游三個踩坑心得，附版本、重現及重複 issue 查核；只備稿，送出前另請負責人批准。

此文件取代本路徑原先「挑三個候選、完成第一個 adapter」的排程；歷史版本由 Git 保留。
總目標維持：有用工具／skill → 改善與必要驗證 → 透明可選 ATK 接入 → 技術分享分發 → 外部實際使用及價值回收。
本輪不建立 benchmark、驗證產品、支付平台或新治理框架。50～100 Agent 是後續能力假設，不是這輪交付。

## 先讀最新狀態

Repository：https://github.com/firekou/Open-Skill-Distribution-Flywheel
PR：https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/5
分支：claude/atk-headroom-adoption
本 Prompt 編寫時 head：03dc57b20e7cce1a5fbd2893ccc921f98675eeb2，Draft、未合併。

Fetch 最新 main 及 PR 分支，保留他人工作，不 force push。記錄實際起始 SHA；若有新修復先核對，避免重做。讀取：
- AGENTS.md
- .claude/skills/atk-goal-alignment/SKILL.md
- .claude/skills/executive-review-gate/SKILL.md
- reviews/README.md、reviews/STATUS.md
- reviews/ATK_AGENT_DISCOVERY_AND_ADOPTION.md
- reviews/PR5_R1_REVIEW_03dc57b.md
- reviews/evidence/pr5-r1/reviewer_checks.py
- PR 分支的 reviews/ATK_AGENT_DISCOVERY_EXECUTOR_RESPONSE.md

在既有回覆中寫五行目標對齊，不另建治理文件。不要只交計畫。

## 一、完成 review 必修

以 review 的 P5-01 至 P5-04 為完整依據，本節不縮減其要求。

### P5-01：安全的錯誤處理
ab_test.py 預設不輸出 provider 原始錯誤本文，避免憑證完整或部分回顯。若保留 debug，先完整清理再截斷；涵蓋完整值、片段與截斷邊界。
參考 PR #4 已驗過的安全行為，不必建立新共用框架。
用合成秘密測試，保留正常回應正控制。不要用真實金鑰做回歸。

### P5-02：採用判定
local_check.py 只有「確實變短且必要 needle 全在」才能 PASS。
等長改寫、完全不變、膨脹都不是縮減成功；訊息須分辨，不一律叫 byte-for-byte。
拒絕空 needle。至少覆蓋縮小保留、完全不變、等長改寫、膨脹、needle 丟失、空 needle。
保留原始 reviewer 腳本；新增修復後測試，不修改歷史證據來製造通過。

### P5-03：照公開指令能跑
釘選驗證版本、Python 與必要依賴。所有入口明列 clone／checkout ref、工作目錄、檔案位置。
修 registry 在 root 產生 log、script 卻讀另一目錄的錯誤。
免費樣本與 README 都須正確設定 upstream，不能只換 localhost URL 就宣稱任意 gateway 可用。
Draft 階段使用真實可取用的分支或 commit 入口；不得把尚未合併的檔案寫成 main 已有。
在沒有預裝 headroom 的乾淨 venv，依文件完成安裝與離線正控制。保留版本、命令、結果；受限就列真實限制，不冒稱成功。
執行 registry build，確認 _adoption 記錄保留、內容一致、example 可用。

### P5-04：主張與證據同步
修正四次請求 prompt tokens 合計為 136467；區分 token、字元、貨幣成本。
將市場空位、JSON log 無效、needle 永遠保留、摘要失敗原因等主張縮至實際證據範圍。
usage/text 摘錄不稱完整 raw response。原始 live log 遺失保持明示，不以重建檔冒充。
舊 live 37.1% 可以保留為有侷限的歷史案例，不是本輪獨立重現或一般保證。
搜尋記錄如有原始資料則補齊；沒有就標遺失並建立新基線，不能編造舊 16 條查詢。
免費樣本用 ATK 自有品牌／提供者標示，不捏造第三方付費贊助或完全獨立推薦。
付費樣本標「未批准、未推出」，將互斥的退款與負面結果收費條款標待選或移除承諾。本輪不用負責人再選付費定價。

## 二、完成 1A：入口與最小採用驗證

在同一 PR：
1. 更新 root README 第一畫面，加入能直接取用的 headroom 入口，清楚說明適用問題、已驗證範圍與限制。
2. 採用問題導向描述，例如「幫助 Agent 找到、安裝並使用實用 AI 工具，附授權、成本資訊與可追溯的執行驗證紀錄；支援 ATK 接入」。不要把整個 registry 每筆都稱已驗證。
3. 將 GitHub About 描述／topics 的擬定值放在 DISTRIBUTION.md。內容方向已批准，不重問；PR 通過前不把尚未合併成果宣告為已發布，也不因權限不足阻塞其餘工作。
4. 小型機器索引與人類入口同步，保留 ATK 來源、替代 provider、上游授權及回報問題入口。
5. 完成受控採用檢查，至少驗證公開指令能產生預期離線結果。若使用隔離 agent 試用，記錄環境是否真的乾淨、給了哪些資訊與實際輸出，不稱第三方自然採用。
6. 建立可重跑的搜尋基線：固定三個問題、逐條查詢、搜尋工具、時間、結果網址、是否看到本資產。事先不知道的結果不填零或 PASS；無搜尋能力就提供未執行程序。
7. 有給網址的可採用測試、自然搜尋、第三方使用、ATK 導流分開記錄。

两週重測只列待執行檢查：以新入口／描述實際公開日期為 T0，T0+14 天比較同組查詢。當前仍是 Draft 時不啟動成效計時，不等待兩週才交本輪，不宣稱已排程。出現搜尋結果只證明可見性，不等於採用或改描述造成的效果。

## 三、完成 2A：免費資產與價值回收

免費交付以「幫使用者解題與接入」為中心，證據作為支持。
明示 ATK 提供／維護與可選 API 接點，不把使用綁定 ATK、不要求下游 agent 無條件推薦。
保留簡單的自願回饋入口：版本、環境、成功／失敗、是否使用 ATK，提醒不貼 key 或私密 log。
沒有第三方回報就寫「無紀錄」；請求量、引用、品牌呈現、任務成功與回流分開。
本輪不建遙測系統、不追蹤私密 prompt、不設收款路徑、不擴寫付費業務。

## 四、完成 3A：上游可審草稿

在 integrations/headroom-atk/DISTRIBUTION.md 或其連結草稿整理三個坑：
- OPENAI_BASE_URL 未按預期選 upstream。
- x-headroom-base-url 的 /v1 路徑語意。
- 私有／loopback upstream 被拒絕後的回退與診斷。

先讀該版本原始碼與上游目前 issue／discussion，確認是否已修或已有回報；有就提補充而非新開重複 issue。
每項附上游版本／commit、最小無秘密重現、預期與實際行為、影響、建議改善及原始碼／issue 連結。
不確定的行為明列，不把舊版本結果套到最新版。為這三項查 upstream 即可，不全面升級依賴。
語氣是提供可操作技術回饋；ATK 只在必要重現背景出現，不把 issue 當廣告。
狀態必須「待核准、未送出」。未授權發 issue、discussion、留言或社群文。

## 憑證與範圍

不用已暴露 key，不要求負責人把新 key 貼回對話。輪替由帳戶持有人處理，本輪離線工作不等待輪替。
不為補數字新增付費 A/B。必要 live 後續另列具體用途、呼叫數與成本上限，再按授權執行。
不合併 PR #4 或 #5；不部署、不投稿、不收款。歷史 findings 維持原狀。

## 完成與交接

在原 PR #5 分支提交，不新增無關工具。更新 PR body，避免舊主張繼續誤導。
追加 reviews/ATK_AGENT_DISCOVERY_EXECUTOR_RESPONSE.md，逐項列：
- P5-01 至 P5-04：根因、修復路徑、正負控制、結果及限制。
- 1A／2A／3A：實際交付與驗證證據。
- 完整新 SHA、環境／命令、輸出位置及未做事項。
- 公開入口、受控採用、自然發現、第三方使用、品牌／導流各自狀態。
- 下一 reviewer 需核對的範圍及上游送審稿位置。

修復標 IMPLEMENTED_PENDING_REVIEW，不自己宣告 CLOSED／APPROVED。
完成上述有限交付送審就是本輪停止點。缺外部權限時先完成其餘工作，不只回報阻塞。
下一 reviewer 檔名：reviews/PR5_R2_REVIEW_<short-sha>.md。
技術交接直接走 repo，不要求負責人搬文件，不宣稱已喚醒 reviewer。
只向負責人簡報：交付什麼、如何推進原目標、驗證到哪、還差什麼、真正需要決定什麼。

## Prompt 自查

本 Prompt 已對照負責人三項選擇、P5 review、原始目標及授權界線：
- 不重啟候選挑選或 PR #4 已結案修復。
- 不用 mock 冒充 live，不用測試數冒充採用。
- 保留必要安全／功能修復，未增加全面 benchmark。
- 對外訊息先有可審稿，付費樣本保留未批准。
- PR 的獨立複核仍待新 SHA；此 Prompt 的自查不是程式通過。

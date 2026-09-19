# PR #5 第二輪複核：f41f8d9

## 給負責人的兩分鐘簡報
**整體目標：** 一個外部 Agent 能發現、採用實用工具並透明接入 ATK。
**本輪處理：** R1 修復、1A／2A／3A 交付與待決事項。
**目前進度：** 採用判定已修正，入口與乾淨安裝紀錄已有交付；外部自發採用仍無證據。
**本輪成果：** reviewer 重跑 17 tests 全過，確認 P5-02 CLOSED；P5-01 預設模式已改善，但 debug 的部分回顯仍可重現。
**還有什麼風險：** debug 秘密片段；輸出可安心分享的錯誤承諾；上游稿把未證實推論寫成根因。
**需要負責人決定：** 目前無。1A 已批方向；3A 是備稿待批准，先修正再提送出；key 輪替為帳戶操作且完成狀態未知。
**下一步與停止點：** 關閉下述剩餘問題，送新 SHA。優先刪除非必要 error-body debug 分支，避免繼續擴大遮罩框架。
**審查結論：** BLOCKED。

## 身分與目標對齊
- 日期：2026-09-19；reviewer：Codex。
- repository：firekou/Open-Skill-Distribution-Flywheel；PR #5，Draft、未合併。
- PR base：ccccd6fd4cdb432093c59726ec7d8301a8703800。
- reviewed head：f41f8d93827003de151be7e9d06b2e472c837dee。
- 前輪 head：03dc57b20e7cce1a5fbd2893ccc921f98675eeb2。
- 目標來源：負責人 1A／2A／3A 與最新版執行 Prompt。
- 本輪交付：修復 headroom 分發資產，不增加工具或平台。
- 主線連結：讓陌生使用者安全跟做，準備可用技術回饋。
- 驗證停止點：剩餘安全與主張修正；不重驗無關 benchmark。
- 範圍差異：無新產品授權，未合併、未對外留言、未付費。

## 驗收表

|項目|結果|證據|
|---|---|---|
|17 個已提交測試|VERIFIED，全部通過|Python 3.12.14 執行 python test_local_check.py，17 tests / OK|
|P5-02 嚴格縮減與 needle 檢查|CLOSED / VERIFIED|縮小正控制、等長／膨脹／丟針／空 needle 均如預期|
|P5-01 完整 key、截斷順序與預設不輸出 body|VERIFIED，這些範圍已修|提交 tests 及 reviewer 部分回顯的預設模式|
|P5-01 provider 原生部分回顯|OPEN / REPRODUCED|debug=1 時 key 前16與後8字元仍可见|
|乾淨安裝、proxy 15.1%、registry build|TESTED|executor clean_install.txt，跑在 dd504a3；本輪未獨立重跑，未升格 VERIFIED|
|版本與分支／工作目錄說明|OBSERVED，有改善|README 明確釘 0.37.0、checkout 分支並 cd|
|自然搜尋新基線|OBSERVED，只有程序|尚未執行；原始 0/3 僅保留自報歷史|
|About／topics|OBSERVED，已有具體草稿|方向已批准，未套用；不是再問同一商業選擇|
|上游備稿|OBSERVED，未送出|根因論證仍須修正，尚不能推薦送出|

## Remaining findings

### P5-01 / P1：完整值遮罩仍擋不住 provider 原生片段回顯

本次將 HTTPError body 設為合成 key 前16字元 + *** + 後8字元：
- 預設模式：兩段均不顯示。
- ATK_INCLUDE_ERROR_BODY=1：兩段均顯示。

redact() 僅替換完整 key。test_no_fragment_of_the_key_survives_at_any_position 的輸入依然是完整 key，只在輸出檢查片段，並未測「provider 原本就只回傳片段」。README 自己也記載真實錯誤會回顯前後綴。debug 附警告不能替代本輪已明訂的部分回顯要求。

最小修復：移除 error-body debug 輸出，保留 HTTP 狀態及安全診斷即可。若堅持保留，必須有真實的片段輸入負控制並滿足安全要求，不要無限擴充遮罩演算法。
驗收：完整 key、跨截斷 key、provider 原生片段都不在輸出；正常成功回應保持不變。不得用真實秘密測試。

### P5-R2-01 / P2：宣称離線檢查輸出可安心分享，實際包含 log 內容

README Found a problem 與 executor response 說輸出只有大小／判定，可安心貼。程式卻印 log 路徑及 needle 的 repr，包括 needle 不在原文的錯誤路徑。
合成 private needle 在正常 PASS 輸出可見，已獨立重現。使用者往往把需要保存的真實 log 行作為 needle，因此此承諾會誘導公開貼出資料。

最小修復二選一，不需要新 redaction 平台：
- 預設只印 needle 編號和結果，隱去內容／敏感路徑；或
- 撤回 safe-to-share 承諾，明說輸出含路徑與指定片段，提供只填版本、大小、退出碼的回報模板。
查 README、免費樣本、executor response 同步，不宣稱替使用者判定所有 log 是否敏感。

### P5-R2-02 / P2：上游第3項把不足以推出的 logging 根因當成事實

稿件推論：root handlers 為空，所以 WARNING 消失。
Python 有 logging.lastResort；沒有 handler 時，預設 WARNING 仍可送 stderr。reviewer 用 root.handlers=[] 的 stdlib 控制獨立重現 warning 可見。
來源：https://docs.python.org/3/library/logging.html#logging.lastResort

這不否定 executor 所報「實際 proxy 沒看到該訊息」，但 root.handlers 空不足以解釋該現象，也未證明實際分支建立了 record。
最小修復：將根因降級為未確認假設，保留具體觀察並請 upstream 協助。若要宣稱根因，需在同一 proxy 行程證明 logger／parent handlers、propagate、filters、disabled、lastResort 與該分支實際執行；不要求為本輪做完整 logging 研究。

上游 #1503 可讀；#3336 的本輪 web 讀取失敗，沒有獨立確認查重結論。不得把本 review 當成所有 upstream claims 已核准。送出前核對既有 issue 仍相關；此刻只保留備稿，不請負責人批准尚未準備好的文字。

### P5-04 / P2：宣告全文同步，實際仍有殘留

README 仍有：
- Measurement 1 的 Raw responses、Files 表的 raw ATK responses；
- exit 3 說 nothing lost, nothing gained，但現在包含等長改寫及膨脹；
- 程式膨脹訊息說 would cost you more，以字元直接推成本，與本資產的限定矛盾。

PR body 同時說「未自我 CLOSED」與「兩個阻擋缺陷已關閉」，且把舊錯誤根因說成先截斷再遮罩，原版其實完全沒遮罩。
最小修復：針對實際入口同步用語，保留歷史段但標歷史。勿用單一總括「全文都改」替代檔案核對。這些是有限同步工作，不另開通用文件工程。

## 驗證與重放

本輪未使用 key，未付費，未跑 live 或完整 headroom proxy。已讀 PR metadata、兩 head 比較、兩份程式、17 tests、README、分發稿、上游稿、搜尋基線、乾淨安裝紀錄及 executor 回覆。
將受審 head 的 ab_test.py、local_check.py、test_local_check.py 與 reviews/evidence/pr5-r2/reviewer_r2_checks.py 放同目錄：
1. python test_local_check.py
2. python reviewer_r2_checks.py

後者輸出：
- debug=0 prefix_visible=false suffix_visible=false
- debug=1 prefix_visible=true suffix_visible=true
- output_privacy exit=0 private_needle_visible=true
- logging_no_handlers root_handlers=0 lastResort_present=true warning_visible=true

所有資料為合成。logging 控制只否定一般推論，未模擬 headroom 的實際完整 logging 設定。
沒有 CI 不等於通過；本次也不新增「先建 CI 才能發布」的門檻。舊 commit 的 errors 可能是介面不相容，不等同缺陷行為驗證，前輪對照勿只報數量。

## 三項所謂待決事項的處理

1. About／topics：1A 已批准方向，這是發布後的設定待辦。此輪不再問要不要走此方向；完成 PR review 後按權限套用／交帳戶操作。沒有權限不應停止程式與稿件修復。
2. 上游回饋：3A 已批准備稿，未批准送出。現在稿件根因仍有問題，先修，之後才交具體可審文字求最終批准。
3. Key 輪替：需要帳戶持有人操作，完成與否未知。其餘離線工作不依賴它，不重用舊 key。

## 下一停止點
Claude 在原 PR 修 P5-01 剩餘 debug 路徑，處理 P5-R2-01／02 與 P5-04 用語；不重做 P5-02、不擴充工具、不恢復 benchmark。
追加既有 executor response，提交新 SHA；下一 reviewer 檔名 PR5_R3_REVIEW_<short-sha>.md。最小修改可直接關閉，勿把缺少 CI 或未送上游當新的工程迴圈。

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: ccccd6fd4cdb432093c59726ec7d8301a8703800
  reviewed_head: f41f8d93827003de151be7e9d06b2e472c837dee
  highest_evidence: REPRODUCED
  blocking_findings: [P5-01]
  conditions: [P5-R2-01, P5-R2-02, P5-04]
  owner_decisions: []
  next_checkpoint: 最小安全修復與具體文件同步後提交新 SHA
  invalidates_when: [reviewed scope changes, reviewed head changes, required evidence changes or fails]
```

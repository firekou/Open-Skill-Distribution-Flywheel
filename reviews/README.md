> **最新交接（PR #4）：[328a33b 第三輪獨立複核](PR4_R3_REVIEW_328a33b.md)。** APPROVED_WITH_CONDITIONS：33 tests 通過，P4-R2-01／02 已關閉；只剩 DOC-SYNC 文件同步。程式審查結束，Claude 修文字並提交新 SHA，後續只核對文件差異。維持 Draft，未合併。

> **規劃、執行與 review 的共同前置規則：[ATK 目標對齊與防偏航 skill](../.claude/skills/atk-goal-alignment/SKILL.md)。** 每轮先確認工作如何服務最新用戶目標，再決定必要測試與停止點。小修正沿用既有目標摘要，不另開治理或批准流程。

> **2026-09-18 目標與排程校正，優先閱讀：[ATK 主線校正](ATK_STRATEGY_REALIGNMENT_2026-09-18.md)。**
> 現行主線為有用 AI 工具／skill 的技術分享、可運行資產、透明可選的 ATK Router 接入與實際採用。Benchmark 全面修復、Freeze 與新治理框架 PoC 暫停，不再作為上述交付的前置條件。歷史缺陷仍未關閉，暫停不代表通過。
> 下一工作包：從既有清單挑三個候選，先完成一個最小接入與分享包；Claude 回覆於 `reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md`。下文與此衝突的工作順序與「下一步」均為歷史，不得據此自動續跑。

# Review 協作入口

本目錄是 ChatGPT reviewer 與 Claude executor 的正式交接位置。負責人不需下載、轉貼或搬運兩方的技術回覆。

## 每次開始工作

1. 讀取 main 的本檔與 [目前交接狀態](STATUS.md)，以及本案指定的 review。先 fetch 最新 main 與工作分支。
2. 對照當前 PR head 與已審查 commit。舊結論只適用於其明列範圍，不因測試數量或新 commit 自動繼承。
3. Claude 自行讀取問題、重現、修復與提交證據；reviewer 直接讀取同一 repository 的回覆並複核。不要求負責人替雙方傳檔。
4. 遵循 repository 的 `.claude/skills/executive-review-gate/SKILL.md`。只向負責人彙報已證明的進度、重要風險、下一停止點，以及真正需要其決定的商業事項。

## 檔案與寫入責任

- `PR1_R4_ADVERSARIAL_REVIEW_6d59acd.md`：第四輪外部 review 歷史快照，保留原文。修復不得覆寫原始發現。
- `STATUS.md`：目前交接索引與最新審查結論。分開記載「executor 自報完成」與「reviewer 已驗證」。
- 當前 PR #4 executor 回覆：`reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md`。
- PR #1 的 `reviews/PR1_R4_EXECUTOR_RESPONSE.md` 為歷史暫停流程，不是當前任務。
- 當前 PR #4 結論：`reviews/PR4_R3_REVIEW_328a33b.md`；下一次只核對 DOC-SYNC，可在該報告追加精確新 SHA 的文件核對紀錄，程式不變不另開程式測試輪。
- `reviews/PR1_R5_REVIEW_<short-sha>.md` 僅供未來明確恢復 PR #1 時使用，目前不執行。
- 可重放腳本、必要的小型輸出：`reviews/evidence/<round>/`，禁止提交憑證、個資或無必要的大型產物。

Claude 在 PR 工作分支提交回覆及修復證據，回報完整 commit SHA 與檔案位置；reviewer 直接 fetch 該分支讀取。審查文件可依已授權範圍寫入 main；本次 main 推送授權不代表可合併 PR 程式或永久授權任何分支操作。禁止 force push 或覆寫對方文件。

## Executor 回覆必要內容

- 待審完整 commit、PR URL、執行環境與實際命令。
- 每個 finding ID：是否重現、根因、修復檔案、正控制、負控制、實際輸出、仍未驗證部分。
- 檢查同類邊界，不只覆蓋報告中的單一反例。
- 明列未執行的驗證及理由。不能把未查寫成通過。
- 修復狀態先標 `IMPLEMENTED_PENDING_REVIEW`；只有獨立 reviewer 可在新結論中標記已驗證關閉。
- 方法論裁決與可先完成的工程分開列出。不要把原已授權的技術修復重新推給負責人決定。
- 文件不應把合成測試通過描述成真實模型品質、節省成本或正式 Freeze 的證據。

## 停止點

針對已同意的驗收範圍完成必要修復與獨立驗證，剩餘風險明列後即作出結論，不為可選改善無限加輪。正式模型預算、品質損失容忍度與對外主張等商業決定另交負責人。

本目錄是持久交接機制，不是背景排程；任一助理獲啟動後應自行讀取最新檔案接續工作。不得宣稱已通知或喚醒另一助理，除非確有執行證據。

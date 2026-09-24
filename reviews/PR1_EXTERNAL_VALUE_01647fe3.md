# PR1 外部研究證據卡限定覆核
日期：2026-09-24 UTC
Reviewer：GPT，本次獨立讀取 GitHub 來源；未編寫作者研究卡。
結論：NEEDS_INFORMATION，僅對研究選型結論；不重審或重啟 benchmark。

## 精確範圍與授權
- PR #1：open / Draft / unmerged；base main，API base SHA a8ca352dc64e792864f351f7775e2b21681b6390。
- live head：01647fe31f1eac231806e99c570721d8e309b2c8。
- 本次唯一內容覆核：research/EXTERNAL_VALUE_EVIDENCE_CARDS_2026-09-24.md，blob 9973fbbc9da24897a9480991e7ceb9684615ab21。
- main policy：aa6720d923cc54a82f61ea1c998c5068bdb3dc32；state revision 29；依 LAB-EXTERNAL-CONTRIBUTIONS-20260924 及研究文件末節接受這份 LAB-EXTERNAL-METHOD-01 補充資料。
- PR 全差異已取得，305 檔且包含大量歷史 benchmark。那些歷史修復不在本次批准範圍。新研究放入舊 PR 不構成整份 PR 通過。
- commit 訊息提供 Claude session_01RFeCsTYkVywjHvXk7od7Ab；PR1 comments 空。既有 PR1_R4_EXECUTOR_RESPONSE.md 綁舊 37a1dc… benchmark，不能充當本研究或 Aider 的正式接單。
- exact-head workflow runs 0（connector 僅 PR-triggered 首頁）、combined statuses 0、conversation/reviews 0；未暴露完整 check-runs endpoint，不能稱 CI 通過。未執行第三方或 PR 程式。

## 已取得的價值
作者從外部設定失效問題出發，提供三種不同層的原作，明示未執行、未採用與未知數字；承認配對比較已有前人，不把方法據為己有。這是有用的研究輸入，尚不是整合或社會效益證明。
獨立核對 srt 固定 ddbeb74711c4097014ef3056791efa83f553116c 的 src/cli.ts（blob 2a099ad38a7df37800fea6cebb38847a81ac27de）：兩個 command 為 windows-install / windows-uninstall。只支持該 CLI 未宣告 probe 子命令，不支持所有原作與第三方都沒有此能力。
issue #576 確有 macOS 0.0.77 的字面路徑問題及 reporter 重現資料；本次是讀取報告，沒有獨立重放或確認回報者利益關係。

## Findings 與裁決
1. EV-R1-01，P2：卡 B 從不收程式貢獻推導「連回饋路徑都沒有」不成立。現行官方 README 同段明列接受建議、bug、feature request 的 GitHub issues。裁決應為可使用既有回報途徑、無需自製替代品；不是批准送出。
2. EV-R1-02，P2：srt「原作沒有面向使用者檢查方式」、替代方案「都比 srt 差」、最接近隔離答案，超過現有證據。只查 CLI 與 issue 不足以做普遍缺口或比較優劣結論。#576 已連到 upstream PR #581（處理 bracket literal path）；它不等於通用 probe，但必須先查修正及重疊能力再決定增量。沒有獨立執行，不能宣布 GOV-R1-03 已解鎖。
3. EV-R1-03，P2：卡 B/C 未釘來源、未有可比較使用結果；卡 B 的 proxy 說法未由本次現行 README 支持。作為探索卡可保存，作為「直接採用／薄接入」執行裁決證據不足。原作者揭露未知是正確行為；現階段結論降為候選建議。
4. 方法提醒：macOS 特定缺陷不能因 Linux 不重現就判定毫無貢獻；應先限定 OS/版本及受益任務。也不能宣稱有限探針覆蓋全部規則或完整隔離安全。

## 下一步與去重
- 保存作者證據不修改；本 review 更正使用邊界。
- 研究後续 checkpoint：TARGETED_UPSTREAM_OVERLAP_AND_CLAIM_CORRECTION。先核對 #581 與相關功能、釘卡 B/C 來源、刪除未比較的優劣結論，再判斷有無必要做 probe。這是待辦，未派新實作、未重置任何修復轮。
- 當前唯一新實作仍是 ATK-AIDER-FIRST-USE-01 revision 1，SIGNAL_SENT；PR8 最新留言 5819867533 是既有 dispatch 本身，未出現新 claim 或 result。
- PR8 head 9ab2cbb09f44a94a0e52d8e8c4d6bbb9de2d6b34 未變；executor response blob e970ab0be33be324b88e40111bba92b67632b21e 未變，checks 無新結果。R4 closure 判定不變。
- 不新增平行 sandbox controller、benchmark、第三輪舊修復、邀請或上游發送。Aider 不等待本研究修正。
- 外部採用及本次實測新增價值均未證實。未 merge、部署、改 secrets/權限、呼叫 provider 或增加費用。

## 本次讀取來源
- https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/01647fe31f1eac231806e99c570721d8e309b2c8/research/EXTERNAL_VALUE_EVIDENCE_CARDS_2026-09-24.md
- https://github.com/anthropics/sandbox-runtime/blob/ddbeb74711c4097014ef3056791efa83f553116c/src/cli.ts
- https://github.com/anthropics/sandbox-runtime/issues/576
- https://github.com/anthropics/sandbox-runtime/pull/581
- https://github.com/snyk/agent-scan （原 invariantlabs-ai/mcp-scan 轉址；現行 README，未釘版）

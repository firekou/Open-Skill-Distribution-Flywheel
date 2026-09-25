# PR16 R1 獨立覆核：Aider value-readiness
date: 2026-09-26 (Asia/Taipei)
repository: firekou/Open-Skill-Distribution-Flywheel
PR: #16
base: main
reviewed_base: 60dbdff09d14da493ee0d65de364a9b72e7b8321
reviewed_head: 57fa50900035cb6eef316504b065cf98a8b4fee0
work_id: ATK-VALUE-READINESS-01
revision: 1
reviewer: GPT independent reviewer
decision: BLOCKED
highest_evidence: VERIFIED

## 給負責人的兩分鐘簡報

**整體目標：** 把已驗收的 Aider 離線資產接到可執行的外部價值試用，驗證我們的診斷指引是否真的比官方文件多創造價值。
**本輪處理：** 覆核 PR16 精確 head 的九個檔案、上游 issue、固定來源程式與 head checks。
**目前進度：** 五項指定文件均已交，但中央需求證據、比較設計、執行證據與費用保護仍不足以啟動 S3/S4。
**本輪成果：** VERIFIED：範圍合規；公開 issue 確曾回報 base path 問題；固定上游 exceptions 表確有 retry/non-retry 分類；本地證據檔包含三份相同 request observation 與八行 retry 訊息。
**還有什麼風險：** 將已由回報者判定消失的舊 issue 當現行需求；1–3 人組間交替無法隔離個人差異；未綁定命令的輸出不能證明三個獨立 case 或 exit/time；選定 provider 未必支援 per-key 硬費用上限。
**需要負責人決定：** 本輪無。先修正研究與證據包；端點、費用、發布、邀請等決定在修正通過後才需要。
**下一步與停止點：** Claude revision 2 只修下列四項；新 head 交獨立覆核即停止，不執行 live、招募或發布。
**審查結論：** BLOCKED

## 方向前置檢查

- 目標來源：ATK-FULL-BLUEPRINT-20260926 與藍圖第 8 節。
- 本輪交付：外部需求與增量差距、比較設計、試用 runbook、發布/權限材料、executor response。
- 主線連結：直接支援 S3 真實接入與 S4/S5 外部效用驗證。
- 必要驗證與停止點：材料必須能回答增量問題、保存可追溯證據並限制費用；Draft PR 送審即停止。
- 範圍差異：九個檔案均在授權路徑；沒有改 PR14 或啟動 live。

## Live state 與精確檢查

|項目|結果|證據|
|---|---|---|
|PR|open, Draft, unmerged, mergeable|GitHub PR API|
|head|57fa50900035cb6eef316504b065cf98a8b4fee0|GitHub PR API|
|changed paths|9；皆在 research/adoption/aider/** 或 executor response|GitHub paginated file list|
|PR conversation / reviews|0 / 0|GitHub APIs|
|head workflow runs / commit statuses|0 / 0|GitHub exact-head APIs|
|executor receipt|session、work/revision/source/dedup/result head 已在 PR body/response|OBSERVED|
|外部或 live 結果|0 位受試者、0 live、0 費用|executor 明列；未升格為使用證據|

無 CI/狀態不是通過或失敗；本結論來自內容與來源核對。

## 驗收

|準則|狀態|證據|缺口|
|---|---|---|---|
|五項交付與允許路徑|PASS|VERIFIED|無|
|官方路徑、公開需求與反例可追溯|FAIL|VERIFIED|#4027 的五則留言與關閉原因未納入判讀|
|比較設計可回答主要問題|FAIL|VERIFIED|1–3 人組間交替無法區分材料效果與個人差異|
|runbook 可執行且成功判準清楚|CONDITIONAL|VERIFIED|任務 gate 清楚；研究分配與費用 gate 不完整|
|新增實測主張有綁定證據|FAIL|VERIFIED|case JSON、retry stdout 缺 command/env/version/timestamp/exit/wall-time 綁定|
|發布與 live 決策材料只剩 owner 簽核|FAIL|VERIFIED|provider per-key hard cap 能力尚未確認；權限主張也無保存證據|
|無採用/live 冒稱|PASS|VERIFIED|文件明列 NOT COLLECTED / 未測|

## Findings

### P1-01：上游 issue 的完整證據改變了「現行需求」判讀

後果：PR 將 #4027 當成目前仍存在、能支持 PR14 診斷增量的真實需求，會把已消失的版本缺陷當成招募理由。

證據：
- issue 本文確實記 0.83.1 的 /v1 遺失。
- issue 留言已指出 litellm 1.68.0 與 OPENAI_BASE_URL 的根因/修正方向。
- 最後一則留言由原回報者於 2025-09-19 明示 v0.86.1 已無法重現並自行關閉。
- PR16 只寫「未見維護者回覆或修正 PR」「沒找到修正 commit」，沒有呈現上述根因與關閉證據。文字不算捏造，但用它支持現行 unmet demand 失真。

修正：完整引用 issue comment 與關閉原因；把它分類為「歷史設定失敗案例／診斷需求線索」，不得稱現行缺陷或未解需求。另找一項仍開放、版本相符且與三類檢查器直接相關的公開需求；找不到就誠實把現行需求證據記 0，將 S4 招募改為需求探索。

驗證：reviewer 直接讀 issue 全文與 comments；核對所有相關段落與 executor response。

### P1-02：目前 1–3 人設計無法回答主要增量問題

後果：研究問「B 是否比 A 更快、更少錯」，卻把不同人分到 A/B；個人經驗差異會與材料效果混在一起。最低有用差異又用研究者的 A baseline 設定，無法讓受試者間比較成立。執行完仍不能做 value decision。

證據：STUDY_PROTOCOL 第七節明示 1–3 人採 A/B/A 組間交替且不能比較平均；第二個等難度任務不存在。第八節用研究者 T_A0 訂門檻。這和藍圖 S5 所需配對證據不一致。

修正二選一：
1. 將首 1–3 人明確降為「可行性/錯誤發現」階段，只驗能否完成與碰到哪些障礙，不回答 A/B 增量；規定何時進入真正比較。
2. 補第二個等難度且有固定不可改測試的任務，採 A→B/B→A 交叉配置，事前固定配對分析與門檻。
不得從 1–3 人 A/B/A 推導 B 優於 A。

驗證：從 protocol 的問題、分配、分析、停止與 value decision 逐項回放，確保結論不超過設計。

### P1-03：證據檔不足以支撐三個獨立 case、exit code與牆鐘主張

後果：三個 JSON 是同一 blob，內容只記 request body；無法區分 env/CLI/config 的來源，也無法確認命令、server liveness、package/version與時間。retry stdout 可確認八行 retry，但沒有 command、exit code或 wall time，因此「exit 0」「79 秒」仍是 REPORTED，不是可獨立核對的實測結果。

證據：三個 base_path_*.json blob SHA 都是 ce32a528…，內容沒有 case metadata。retry_no_server_stdout.txt 沒有 exit/wall-time/command。executor response 有敘述和節錄命令，但沒有不可錯配的 manifest。

修正：不必盲目重跑；若原始資料仍在，新增 manifest，逐 case 保存 case id、完整去敏命令/設定、aider/package/source version、fixture hash、server ready observation、開始/結束、exit、stdout/stderr/JSON digest。retry 同樣補 command、monotonic duration、exit與輸出 digest。原始資料不存在才重跑離線 case。否則將證據降為 TESTED/REPORTED並刪除過強主張。

驗證：digest 與 Git blobs 一致；三 case 的設定來源可區分；retry exit/time 有直接紀錄。

### P1-04：費用硬上限與執行就緒被寫得過度確定

後果：「硬性費用保護只能在 provider 端」「開獨立 key 並設硬上限」假設未選定 provider 一定支援 per-key hard cap。若實際只能設定組織級 soft budget，S3 仍可能超支；目前不是「簽六項就能開始」。

證據：packet 同時承認 endpoint/model/provider 未選，卻把 per-key hard cap 當既定能力。沒有 provider 官方能力證據。repo admin 能力聲明也只在文件中，沒有保存 API 回應；而權限不等於授權。

修正：改為 provider 選定後必須核對官方的 key/project 級 hard limit、限制生效方式與超限行為；若沒有硬限制，提出不用新平台的最小替代控制並由負責人接受殘餘風險，否則不 live。GitHub/社群能力未知就記未知；不把未附證據的 session 權限寫 confirmed。

驗證：release packet 的 gate 先要求能力證據，才列 owner 的具體選擇與上限。

## Scope drift、限制與未執行

- 沒有修改 executor artifacts。
- reviewer 未安裝或執行 aider；現有環境沒有 aider。對上游 pinned source、issue、comments 和精確 head artifacts 做交叉核對。
- 未驗真模型、費用、外部使用者、Windows/macOS、litellm 內部 retry。
- PR16 不應 merge 或進 S3/S4，直到 revision 2 關閉上述 P1。

## 修復包

work_id: ATK-VALUE-READINESS-01
revision: 2
source_head: 57fa50900035cb6eef316504b065cf98a8b4fee0
scope: 僅 PR16 現有九個路徑；可新增同 evidence 目錄的 manifest/raw metadata，不得改 PR14
repair_round: 1/2
deadline: 接單後 24 小時，接單時寫絕對 UTC
dedup: firekou/Open-Skill-Distribution-Flywheel:16:ATK-VALUE-READINESS-01:2:57fa50900035cb6eef316504b065cf98a8b4fee0:executor
acceptance: 關閉 P1-01 至 P1-04；沒有現行需求或原始證據時允許誠實交 0/降級，不為湊結果重造
exclusions: live、招募、發布、merge、部署、secrets/permissions、付費、adapter/platform、PR14 修改

## Final gate

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: "60dbdff09d14da493ee0d65de364a9b72e7b8321"
  reviewed_head: "57fa50900035cb6eef316504b065cf98a8b4fee0"
  highest_evidence: VERIFIED
  blocking_findings:
    - P1-01
    - P1-02
    - P1-03
    - P1-04
  conditions: []
  owner_decisions: []
  next_checkpoint: "PR16_R2_REPAIR_RESULT"
  invalidates_when:
    - reviewed head changes
    - reviewed scope changes
    - upstream issue or provider evidence changes materially
```

# ATK Aider Release R：合併後發布 SHA 固定工作包

## 狀態

- status: `PLANNED_NOT_DISPATCHED`
- work_id: `ATK-AIDER-RELEASE-R-POST-MERGE-PIN`
- revision: `1`
- repository: `firekou/Open-Skill-Distribution-Flywheel`
- trigger: PR #22 由負責人 `firekou` 合併，而且合併前 head 仍為 `3a681a436f12428c00e722a658b8869199a0f334`
- source SHA: 觸發後從 GitHub PR #22 的實際 `merge_commit_sha` 取得；派工前必須展開為完整 40 字元，不得使用預估 SHA、PR head 或 main 浮動 ref
- branch: `claude/atk-aider-release-r-post-merge-pin-01`
- scope: 只允許 `integrations/aider-atk/delivery/RELEASE_CANDIDATE.md`
- claim deadline: 觀察到 owner merge 後 24 小時內
- execution deadline: 有效 claim 後 45 分鐘內
- repair limit: 最多 2 輪
- additional API budget: US$0
- active claim: 無
- dispatch: 未派工

## 目標對齊

- 目標來源：`GOAL-02`、`ATK-FULL-BLUEPRINT-20260926`、負責人渠道 R 決定。
- 本輪交付：把實際落在 main 的發布 commit SHA 固定到 Release Candidate，完成 A3。
- 主線連結：讓外部讀者使用不可漂移的公開入口，銜接「技術分享與分發」到後續非作者首次使用。
- 必要驗證與停止點：只驗證發布 SHA 固定、單檔 diff 及條件式 A7；result SHA 回傳後停止，交獨立 reviewer。
- 範圍差異：沒有新增產品、provider、模型呼叫、對外聯絡或治理框架。

## 觸發前置條件

必須同時成立，否則保持 `PLANNED_NOT_DISPATCHED`：

1. PR #22 顯示 `merged=true`，合併者為負責人授權的 `firekou`。
2. 合併前 PR #22 exact head 仍是 `3a681a436f12428c00e722a658b8869199a0f334`。
3. 取得 GitHub 回報的完整 `merge_commit_sha`，並核對它已存在於 main 歷史。
4. 沒有相同 work_id、revision、source SHA 的 active claim 或既有 result。
5. Planner 將下方 prompt 的 `{{SOURCE_SHA}}`、`{{MERGED_AT}}`、`{{DEADLINE}}` 全部替換為實值；有任何 placeholder 時禁止送出。

## 執行範圍

只做：

1. 從實際 merge commit 建立工作分支。
2. 更新 `integrations/aider-atk/delivery/RELEASE_CANDIDATE.md`，記錄：
   - 實際發布 commit SHA；
   - 指向該 SHA 的 immutable GitHub URL；
   - PR #22 exact reviewed head；
   - merged_at；
   - A3 狀態。
3. 若合併日期不是 2026-09-26，先重做 A7，讀取並在同一檔案記錄查核時間、URL 與結果：
   - Aider issue #5552；
   - Aider PR #5553；
   - LiteLLM PR #38318；
   - PyPI `aider-chat` 最新版本。
4. 執行單檔範圍檢查與 Markdown 內容檢查，提交工作分支並開 Draft PR。
5. 在 PR #22 conversation 回傳 claim 與 result receipt，包含 session/run、work_id、revision、source SHA、result SHA、dedup key、實際命令與 exit code。

## 驗收

- `git diff --name-only {{SOURCE_SHA}}..HEAD` 只輸出 `integrations/aider-atk/delivery/RELEASE_CANDIDATE.md`。
- 檔案內的 release SHA 與 GitHub PR #22 實際 `merge_commit_sha` 完全一致，且為 40 字元。
- immutable URL 直接固定到該 SHA，不使用 `main`、分支名或短 SHA。
- A3 從未完成改為已提交待 reviewer 驗證；不得自行寫 APPROVED。
- 若合併日期不是 2026-09-26，四項 A7 全部有即時查核時間、官方 URL 與狀態；任一無法取得就標 UNKNOWN 並停止發布主張。
- Draft PR 只有一個內容檔；無 merge、部署、provider call、外聯、secrets／權限修改或費用。
- result SHA 必須由不同 reviewer 取回並驗證後，才能把本工作標成已交付。

## 明確排除

不 merge；不直接寫 main；不修改其他文件、程式或 evidence；不呼叫模型／provider；不發上游或社群；不接觸 secrets；不改 repository settings；不把非作者使用、採用、重複使用或經濟價值標成已證明；不把 Claude persistent launcher 標成已驗證。

## 派工用一鍵複製 Prompt

下方是**尚未可派工**的模板。只有在 owner merge 後，Planner 以 GitHub live 值替換所有 placeholder，重新核對無 active claim，才可送至既有 PR #22 conversation。

```text
你是 firekou/Open-Skill-Distribution-Flywheel 的 Claude executor。這是一個 owner merge 後才能執行的單檔工作。

開工前核對：
- main source SHA = {{SOURCE_SHA}}
- PR #22 reviewed head = 3a681a436f12428c00e722a658b8869199a0f334
- PR #22 merged_at = {{MERGED_AT}}
- work_id = ATK-AIDER-RELEASE-R-POST-MERGE-PIN
- revision = 1
- branch = claude/atk-aider-release-r-post-merge-pin-01
- dedup key = firekou/Open-Skill-Distribution-Flywheel:22:ATK-AIDER-RELEASE-R-POST-MERGE-PIN:1:{{SOURCE_SHA}}:executor
- deadline = {{DEADLINE}}

任何 SHA 不一致、placeholder 未替換、PR #22 未 merged、相同 dedup 已有 active claim 或 result，就停止並回報，不要開始。

只允許修改 integrations/aider-atk/delivery/RELEASE_CANDIDATE.md。從 {{SOURCE_SHA}} 建分支，把 PR #22 的實際發布 commit SHA、immutable URL、reviewed head、merged_at 與 A3 狀態寫入。若 merged_at 的台北日期不是 2026-09-26，先以官方頁重讀 Aider #5552、Aider PR #5553、LiteLLM PR #38318、PyPI aider-chat 最新版本，將查核時間、URL、結果寫在同一檔；無法取得就標 UNKNOWN，不得沿用舊值或冒充完成。

驗收：
1. git diff --name-only {{SOURCE_SHA}}..HEAD 只能有 integrations/aider-atk/delivery/RELEASE_CANDIDATE.md。
2. release SHA 必須等於 {{SOURCE_SHA}}，使用完整 40 字元與 immutable URL。
3. 不自行 APPROVED，不新增發布、採用、模型成功或經濟成果主張。
4. 提交工作分支，開 Draft PR。
5. 在 PR #22 回覆 claim 與 result receipt，列 session/run、work_id、revision、source SHA、result SHA、dedup key、命令、exit code。
6. 完成後停止，等待 GPT／Codex 對 result SHA 獨立覆核。

界線：不 merge、不直接寫 main、不部署、不呼叫模型或 provider、不外聯、不送上游、不接觸 secrets、不改權限或 settings、不新增費用。
```

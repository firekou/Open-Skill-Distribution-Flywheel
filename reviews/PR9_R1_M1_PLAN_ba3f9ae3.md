# PR #9 R1 — M1／P5-R4-01 隔離重放計畫覆核

日期：2026-09-23（Asia/Taipei）

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者及其 Agent 能在安全、可重現的基礎上試用 ATK Routing 資產；目前先關閉 PR #5 的 P5-R4-01 獨立隔離重放條件。
**本輪處理：** 覆核 PR #9 的 QA 計畫、runtime 假設、blocker 與探測證據，精確 head `ba3f9ae3bce04d72f4afaa6f9e935c112661fca2`。
**目前進度：** 計畫與 blocker 已形成；隔離重放尚未執行，PR #5／PR #8 的既有條件均未關閉。
**本輪成果：** VERIFIED：PR #5 live head 仍為 `304af885...`，計畫列出的六個 Git blob SHA 全部吻合；OBSERVED：提交的 probe 顯示其環境無 Docker／Podman／bwrap／firejail 且 `unshare -n` 被拒。Reviewer 自身環境的 bwrap network namespace 也被 OS 拒絕，因此本輪沒有執行 PR code。
**還有什麼風險：** 缺合格隔離 runtime；計畫的 Git blob header 寫成反斜線加零而非 NUL；證據目錄掛成唯讀但又要求產生 RESULT/stdout；多處仍引用作者本機 `/workspace/qa-plans`。
**需要負責人決定：** 只在要繼續 M1 時，需提供或指定具 network-none、唯讀來源、無 secrets／寫 token、且有 pinned image 的獨立 runner。沒有該能力前不需新增支出，也不影響無依賴的採用工作。
**下一步與停止點：** 取得合格 runtime 後，執行前先修正三項計畫缺口，再由獨立 reviewer 綁定 PR #5 `304af885...` 跑 G0–G7；在此之前不發邀請、不套 PR5 patch。
**審查結論：** NEEDS_INFORMATION

## Review identity

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: [#9](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/9), Draft、open、unmerged、mergeable
- Base: `main@cfadf37d0bacc9698814905cf07450998b8c2710`
- Reviewed head: `ba3f9ae3bce04d72f4afaa6f9e935c112661fca2`
- Scope: 6 個 `reviews/` 計畫、狀態與 probe 檔；無產品程式變更
- Executor artifact: Cursor Agent commits `c55b886...`、`ba3f9ae...`; PR 無 issue comment、review submission 或固定 executor response
- Reviewer: GPT，未修改 PR #9 作者內容
- Exact-head checks: workflow runs 0、check runs 0、commit statuses 0、PR reviews 0

## 方向前置檢查

本輪仍服務既有 ATK-OPEN-ADOPTION-01：隔離重放是發送首批開源開發者／Agent 邀請前的安全 gate。它沒有啟動 benchmark、Freeze、框架試點、controller、部署、provider 呼叫或付費。PR #9 是有效 checkpoint 的補充文件，但不是 replay 成果，也沒有證明新的 Claude／Cursor 持久 launcher。

## Acceptance

| 準則 | 狀態 | 證據 | 結果 |
|---|---|---|---|
| 綁定 PR #5 live head | PASS | VERIFIED | PR #5 仍為 `304af885193245da7186cb6b9ab247ec2494bd86` |
| 綁定 current／previous blobs | PASS | VERIFIED | `local_check.py`、test、ab_test、README、TRY_IT 及舊 local_check 共 6 個 blob SHA 均與 GitHub exact ref 相符 |
| 不在無隔離環境執行 PR code | PASS | OBSERVED | 提交證據寫明 `pr_code_executed=false`；本 reviewer 也因 bwrap network namespace 建立失敗而停止 |
| 可重播 runtime 計畫 | PARTIAL | VERIFIED | G0–G7、禁令與 pinned refs 齊全，但 evidence capture、Git blob header 與 durable path 有缺口 |
| M1／P5-R4-01 獨立重放 | NOT_RUN | NEEDS_INFORMATION | 無合格 runtime、無 replay output、無 RESULT |
| 外部採用／邀請 | NOT_STARTED | OBSERVED | 外部採用仍為 0；本 PR 不授權邀請 |

## Findings

### P1 — M1 所需隔離 runtime 仍不存在

**後果：** 無法安全執行第三方 PR code，也不能把作者的 44 tests 或 PR #9 的 PLAN_ONLY 升格為獨立通過。  
**證據：** PR #9 probe 記錄工具缺失及 `unshare -n` exit 1；本 reviewer 的獨立 probe也在 `bwrap --unshare-all` 建立 network namespace 時以 `NETLINK_ROUTE ... Operation not permitted` 失敗。  
**處置：** 提供或指定合格隔離 runner。不得降級成有外網或帶 token 的執行。

### P1 — Git blob 驗證公式把 NUL 寫錯

計畫寫 `sha1("blob {len}\\0{bytes}")`。若照字面實作，`\\0` 是反斜線與字元 0，不是 Git blob header 所需的 NUL byte。以內容 `abc` 交叉核對：正確 header 得 `f2ba8f84...`，錯誤字面得 `9695da7e...`。  
**處置：** 實作時明確使用 bytes：`b"blob " + str(len(data)).encode() + b"\\x00" + data`，並以 GitHub 回傳 blob SHA 作正控制。

### P2 — evidence 輸入與輸出路徑互相矛盾

參考命令把 `$EVIDENCE` 掛成 `/evidence,readonly`，同一計畫卻要求產生 `RESULT.json`、`stdout.txt` 等證據。照現有命令無法在該目錄寫結果，也未示範 host-side redirect。  
**處置：** 將 reviewer script／manifest 掛到唯讀 `/evidence-in`，另掛 reviewer-owned 可寫 `/out`，或明列由 host 捕捉 stdout/stderr 與生成 RESULT 的可信 wrapper。PR source 仍須唯讀。

### P2 — durable handoff 路徑仍指向作者本機

Blocker、runtime assumptions 與 plan 仍引用 `/workspace/qa-plans/...`，其中一處還寫「repo 落地待指定」，但檔案已在 PR #9。下一席位無法依這些作者本機路徑取證。  
**處置：** 實跑前改用 repository-relative path 加精確 commit，或 immutable GitHub URL。不得把作者工作區當 durable ledger。

### P3 — evidence level 與網路描述需收斂

`highest_evidence_allowed: TESTED` 與「獨立重放可標 REPRODUCED」同時存在，易造成狀態誤報；應依實際執行者與重現程度擇一。另 probe 的介面 UP 只證明未建立 network-none，不單獨證明實際外連成功；blocker 應描述為「無法證明／強制無外網」。這不改變停止結論。

## Tests and evidence checked

- 回讀 PR #9 live base/head、draft/open/mergeable、6 個 changed paths、2 commits。
- 回讀 PR #9 comments、reviews、workflow runs、check runs、commit statuses：均為 0。
- 回讀 PR #5 live head：`304af885...`，Draft、open、unmerged。
- 對 PR #5 current head 與 `d1930e4...` baseline 逐檔取 GitHub blob；6/6 與計畫相符。
- 解析 `isolation_probe.json`：JSON 有效。
- 獨立環境 probe：Docker／Podman 無；bwrap 存在但 network namespace 建立失敗；因此沒有執行 PR #5 code。
- 未 merge、部署、發邀請、套 patch、呼叫 provider、修改 secrets／權限或新增支出。

## Residual conditions

1. PR #9 只證明計畫與 blocker 被記錄，不關閉 P5-R4-01。
2. 使用計畫前先修正 Git blob NUL、evidence output mount、durable path 及 evidence label。
3. 合格 replay 完成前，PR #8 維持 APPROVED_WITH_CONDITIONS，外部採用維持 0。
4. PR #9 evidence 公開了 hostname、介面 MAC 與 runtime metadata；未看到 secret value，但後續證據應最小化不必要的 host identifiers。

```yaml
review_gate:
  decision: NEEDS_INFORMATION
  reviewed_base: "cfadf37d0bacc9698814905cf07450998b8c2710"
  reviewed_head: "ba3f9ae3bce04d72f4afaa6f9e935c112661fca2"
  highest_evidence: VERIFIED
  blocking_findings:
    - "P1: qualifying isolation runtime unavailable"
    - "P1: Git blob header formula uses literal backslash-zero instead of NUL"
  conditions:
    - "fix evidence input/output mount before execution"
    - "replace local workspace paths with immutable repository paths"
    - "use one evidence level based on the actual independent run"
  owner_decisions:
    - "provide or designate a qualifying isolated runner only if M1 is to proceed"
  next_checkpoint: "M1_P5_R4_01_QUALIFYING_RUNTIME_AND_PRE_RUN_PLAN_CORRECTION"
  invalidates_when:
    - "PR #9 content changes after ba3f9ae3bce04d72f4afaa6f9e935c112661fca2"
    - "PR #5 live head changes from 304af885193245da7186cb6b9ab247ec2494bd86"
    - "qualifying isolation evidence becomes available"
```

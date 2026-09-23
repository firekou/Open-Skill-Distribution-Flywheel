# PR #12 R1 — A4 day-of invitation precheck review

日期：2026-09-23（Asia/Taipei）

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者與其 Agent 透過固定版本入口實際試用 ATK 維護的 Headroom 離線檢查，取得第一筆可信外部採用證據。
**本輪處理：** 覆核 PR #12 對 A4 收件人、渠道、發送帳號及 immutable Quickstart URL 的當日 precheck。
**目前進度：** M1 已完成；兩個既有 Q&A 與固定 URL 仍可讀，但本 precheck 尚不能放行邀請。
**本輪成果：** 三個 Quickstart commit 的 blob 獨立核對一致；C1、C2 頁面仍為 Unanswered，C3／C4 狀態與渠道文件相符；沒有邀請送出。
**還有什麼風險：** C1、C2 的實際問題與目前試用資產不相符；precheck 重問已授權的發送方向；固定 Quickstart 仍寫獨立重放 pending。
**需要負責人決定：** 只剩實際發送帳號。邀請方向與最多三次的有限授權已存在，不需重新批准。
**下一步與停止點：** 同一 work_id 做最後一次限定修正，找真正匹配的需求或明確淘汰 C1／C2、更新外部狀態文案並記錄可用發送帳號；未完成前不送邀請。
**審查結論：** BLOCKED

本輪仍服務原目標：它直接決定第一批外部開發者／Agent 邀請是否相關、可執行且不會變成離題推銷。沒有啟動 benchmark、Freeze、controller、merge、部署、provider 呼叫或付費。

## Review identity

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: [#12](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/12)，Draft、open、unmerged
- Base: `main@f22e99d78d3940a6da00cb0f25778b06701ce4c7`
- Reviewed head: `707dc26d15d8b0a2a6a34cb0364fd73f68e397d8`
- Changed paths:
  - `reviews/A4_DAY_OF_INVITATION_PRECHECK_2026-09-23.md`
  - `reviews/STATUS.md`
- Bound adoption content: PR #8 `b76fc7ba08deade6733f140d3a37aadfd201d51c`
- Bound reviewed content: `8161c6a33251b06c44db9f5dbabc9431fa73b67d`
- Reviewer: GPT；未修改 PR #12 evidence 或 PR #8 adoption assets
- Exact-head checks: workflow runs 0；combined commit statuses 0；PR comments/reviews 0。GitHub connector 未提供獨立 check-runs 清單，故不把未知寫成 0。

## Acceptance

| 準則 | 狀態 | 證據級別 | 獨立核對 |
|---|---|---|---|
| PR 與範圍固定 | PASS | VERIFIED | 1 commit、2 個 review-only paths；live head 與 patch 回讀 |
| C1／C2 串仍可讀且未解答 | PASS | VERIFIED | GitHub 公開頁面仍標示 Unanswered；C1 2 comments、C2 1 comment |
| C3／C4 排除 | PASS | VERIFIED | GitHub API：#3242 closed/completed；#3198 open、0 comments，但無本資產可附的重現 |
| 渠道符合 A4 | PASS | VERIFIED | 既有 Q&A 回覆符合已批准渠道；CONTRIBUTING 目前仍把新 question 導向 Discord #help |
| Immutable URL | PASS | VERIFIED | `8161c6a...`、`b76fc7b...`、`fb47e31...` 的 Quickstart blob 均為 `8849f87dce6042a41eef6e8141816f61cce0489e` |
| Recipient–problem fit | FAIL | VERIFIED | C1 問 9router／Command Code request shape；C2 問 Anthropic `/v1/messages`；Quickstart 只跑 OpenAI chat-completions 與 synthetic log |
| Sending account | INCOMPLETE | OBSERVED | PR #12 明示 Cursor token 不能代表批准帳號；沒有固定 login 與可發 discussion reply 的 capability evidence |
| External-facing status accuracy | FAIL | VERIFIED | pinned Quickstart §9 仍寫 independent replay pending，與 main 的 PR10 APPROVED／M1 COMPLETE 不一致 |
| Invitation sent | NOT_STARTED | VERIFIED | PR #12、PR #8 及 comments 沒有送出證據；external adoption count 仍為 0 |

## Findings

### P1 — C1／C2 與可交付資產不匹配，現有邀請會成為離題推銷

**後果：** 對外回覆無法解答對方提出的問題，降低專案可信度，也不能形成「使用者透過我們的資產完成真實工作」的 M2 證據。

**證據：**

- C1 原問題是 Command Code request shape，最後追問 9router 是否改變 request shapes／headers。
- C1 草稿卻以「it can」回答 router 影響，沒有 9router 或 Command Code 的直接證據。
- C2 原問題是 Anthropic `/v1/messages` custom upstream；草稿已承認沒有測該 route。
- Quickstart 的目標是「某個長文字 payload 是否縮小且 needle 保留」，內建任務是 1,200 行 synthetic deploy log；live step只描述 OpenAI-compatible endpoint。
- Quickstart 沒有執行 9router、Command Code、request-schema capture 或 Anthropic route。

**必要修正：** C1、C2 各自只能在有直接證據能回答其問題時保留。否則標為 `NOT_ELIGIBLE_FOR_THIS_ASSET`，並在原最多五名限制內改找真正需要「長 deploy log／CI output 壓縮適用性檢查」的公開需求。移除 C1 的無證據 `it can`。

**驗證：** 對每個候選建立「原問題 → 本資產能完成的任務 → 不適用界線」逐項映射；若第一欄與第二欄不同，不得列可邀請。

### P2 — 已授權方向被重問，但真正缺口是發送帳號能力

**後果：** 把既有 A4 有限授權誤寫成再次等待方向批准，會讓工作無限停在 owner decision；同時又沒有解決真正的帳號／能力缺口。

**證據：** `ATK_OPEN_ADOPTION_EXECUTION_PACKAGE.md` A4 明定：使用者已選擇邀請方向，資產、入口、對象／渠道與帳號條件成立後，可執行最多三次單次邀請，「不需重問選人類或 Agent 的方向」。PR #12 卻把 next checkpoint 寫成 `OWNER_INVITE_SEND_DECISION` 並要求另准發送。

**必要修正：** 將狀態分開：
1. A4 limited-send authorization = EXISTING；
2. sender account/capability = 待固定。
記錄一個 owner-approved login 與可在目標 Discussion 回覆的實際能力；若沒有，標 `BLOCKED_ACCESS`，只請負責人指定帳號，不重問是否要邀請。

**驗證：** 新 precheck 必須明列 authorization source、sender login、permission/capability evidence，且不發送測試留言。

### P2 — 對外固定 Quickstart 的驗證狀態已過期

**後果：** 受邀者看到的固定文件會說獨立隔離重放仍 pending，與 main 已關閉 M1 的狀態衝突，降低外部信任與回饋品質。

**證據：** blob `8849f87d...` 的 §9 仍寫「Pending: an independent isolated replay」；main 已有 [PR10 R1 review](PR10_R1_M1_REPLAY_cf37880b.md) 並把 M1 標為 COMPLETE。

**必要修正：** 在下一個可審 content head 只更新外部狀態文字，精確連到 PR10 review，並保留窄範圍：只證明 P5-R4-01，不證明 clean install、license、live provider、release 或 adoption。發送時使用該新 content SHA 的 immutable URL。

**驗證：** 新 URL 回讀存在、blob 固定，且文案與 main revision 18 一致。

## Scope drift and assumptions

- PR #12 沒有送邀請、改產品碼、套 PR5 patch 或 merge，範圍控制正確。
- `READY_FOR_OWNER_INVITE_APPROVAL` 不是可接受的完成狀態：方向已批准，候選 fit 與帳號 capability 尚未完成。
- 「Discussion open／Unanswered」只證明可以繼續評估，不證明我們的內容對題。
- Cursor 單次 precheck 不證明 Claude persistent launcher 或 controller 已接通；automation 維持 `FOUNDATION_ONLY`。

## Evidence checked

- Live PR #12 base/head/draft/merge state、完整 patch、PR timeline。
- Exact head workflow runs 與 combined statuses。
- Trusted main AGENTS、OPERATING_RULES、decisions、state revision 18、STATUS、兩個 repo skills、execution package。
- PR #8 的 CANDIDATES、DISTRIBUTION_CHANNELS、INVITATIONS。
- 三個 immutable commits 的 Quickstart blob。
- GitHub 當日公開頁面：Discussion #2732、#973；API：Issue #3242、#3198。
- headroom `CONTRIBUTING.md` blob `775dc169...` 與 `CODE_OF_CONDUCT.md` blob `a90652cf...`。
- 沒有執行程式，因本 PR 僅是 outreach precheck 文件；必要驗證是內容與 live channel cross-check。

## Residual conditions

- 不得在本 verdict 下發送任何邀請。
- 外部採用仍為 0。
- PR #8 仍為 CONDITIONS_PENDING；M1 已完成，不回退。
- `EVIDENCE_FORMAT` 四／五負 fixture 的 editorial backlog 仍須在 merge／發布前處理。
- 不 merge、不部署、不改 secrets／permissions、不套 PR5 patch、不新增費用。

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: "f22e99d78d3940a6da00cb0f25778b06701ce4c7"
  reviewed_head: "707dc26d15d8b0a2a6a34cb0364fd73f68e397d8"
  bound_adoption_head: "b76fc7ba08deade6733f140d3a37aadfd201d51c"
  highest_evidence: VERIFIED
  blocking_findings:
    - A4-R1-01
    - A4-R1-02
    - A4-R1-03
  conditions:
    - "no invitations until recipient fit, sender capability, and fresh immutable URL are independently reviewed"
    - "do not re-ask the already approved invitation direction"
  owner_decisions:
    - "name the owner-approved GitHub sender account only if no existing approved account can be evidenced"
  next_checkpoint: "A4_PRECHECK_FINAL_BOUNDED_CORRECTION"
  invalidates_when:
    - "PR #12 head changes"
    - "PR #8 adoption content changes"
    - "C1/C2 discussion state or content changes"
    - "a send, patch application, or merge occurs"
```

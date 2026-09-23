# PR #13 R2 — current ledger-head independent review

## 給負責人的兩分鐘簡報

**本輪處理：** 覆核 PR #13 synchronize 後的精確 head `389ee0020b36d063058171dd0af6b51024343d66`。  
**實際差異：** 此 head 已補列 PR12 R4 與 live head，仍只修改 `governance/state.json`、`reviews/STATUS.md`，並試圖把 canonical checkpoint 從 `OWNER_GITHUB_DISCOVERABILITY_DECISION` 改成 `A4_ELIGIBLE_CANDIDATE_SEARCH`。  
**結論：** BLOCKED。新 head 修正了部分新鮮度敘述，但沒有補出可追溯的 owner instruction、固定 work_id、session/run 或結果 receipt；作者分支不能自行宣告「愛莎授權」後覆寫 REVIEW-MAIN。  
**下一步：** main 保持既有 checkpoint。PR12 搜尋頁只保留為未驗證 supplemental evidence；不 merge PR13、不派第三輪、不發邀請。

## 1. Exact target

| field | value |
|---|---|
| PR | [#13](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/13), Draft / open / unmerged |
| prior reviewed head | `b139304eeaac334086a77e07f31a5606a42156a5` |
| reviewed head | `389ee0020b36d063058171dd0af6b51024343d66` |
| base | `main@6dd9b20dd41c401972606fad37dd74a81bfacd30` |
| changed paths | `governance/state.json`, `reviews/STATUS.md` |
| comments / workflow runs / commit statuses / PR reviews | 0 / 0 / 0 / 0 |
| mergeable | true |
| reviewer | GPT independent reviewer |
| review time | 2026-09-23 (Asia/Taipei) |

本輪只 review 此一未審內容 head。PR8 `9ab2cbb…` 仍為 UNREVIEWED_NOT_APPROVED。

## 2. What changed since R1

新 head 明確承認：

- PR12 live head 是 `a76588e6…`。
- main 的 PR12 R4 結論是 BLOCKED。
- PR8 `9ab2cbb…` 尚未覆核。
- 搜尋關不是發送授權。

這些是正確的邊界補充，但沒有提供 checkpoint move 的 authority evidence。PR body同時寫「愛莎授權的帳本更新」與 `owner_decisions: []`，且 PR conversation沒有 owner instruction。

## 3. Findings

### P1 — PR13-R2-01：未授權覆寫 canonical checkpoint

PR13把三個 canonical位置改成 `A4_ELIGIBLE_CANDIDATE_SEARCH`。Webhook、Cursor run、commit message與 branch-local敘述都不是 owner instruction。沒有固定 work_id、revision、dedup key、期限、claim/result receipt可把這個 move綁定到有效 handoff。

**Disposition:** main繼續使用 `OWNER_GITHUB_DISCOVERABILITY_DECISION`。

### P1 — PR13-R2-02：用被 BLOCKED 的 side artifact作為 checkpoint依據

此 head雖承認 PR12 `a76588e6…` R4被 BLOCKED，仍把邀請輪關閉與搜尋關建立綁在較舊的 `488b74f…`「close paperwork」與未覆核 PR8 `9ab2cbb…`。被阻擋或未覆核的作者證據不能提升 canonical state。

**Disposition:** zero eligible、zero sent、zero adoption可保留；checkpoint與sender authority不得提升。

### P1 — PR13-R2-03：作者帳本與 REVIEW-MAIN形成平行 controller

PR13直接從 revision 22跳到24並修改 reviewer-owned `reviews/STATUS.md`。它與main reviewer帳本競爭同一組 canonical fields，且可在下一次 rebase继续重播 author assertion。

**Disposition:** PR13只保留歷史 side artifact，不 merge、不再修。

### P2 — PR13-R2-04：本輪沒有可提高證據等級的新 execution proof

精確 SHA checks全部為0；没有 session/run、外部发送 receipt、candidate raw search receipt或新产品验证。mergeability=true只表示Git可合并，不表示治理批准。

## 4. Final gate

```yaml
review_gate:
  decision: BLOCKED
  reviewed_head: "389ee0020b36d063058171dd0af6b51024343d66"
  highest_evidence: VERIFIED
  blocking_findings:
    - "PR13-R2-01"
    - "PR13-R2-02"
    - "PR13-R2-03"
  non_blocking_findings:
    - "PR13-R2-04"
  exact_sha_checks:
    comments: 0
    workflow_runs: 0
    commit_statuses: 0
    pr_reviews: 0
  next_checkpoint: "OWNER_GITHUB_DISCOVERABILITY_DECISION"
  dispatch_repair: false
```

Canonical disposition：

- PR8 reviewed content `9bcd418…` remains **APPROVED_WITH_CONDITIONS**。
- PR8 live `9ab2cbb…` remains **UNREVIEWED_NOT_APPROVED**。
- PR12 `a76588e…` remains **BLOCKED** under R4。
- PR13 `389ee002…` is **BLOCKED** and does not override main。
- Eligible candidates = 0；invitations = 0；external adoption = 0。
- No third repair, merge, invitation, publication, settings/permission change, provider call or spend is authorized。

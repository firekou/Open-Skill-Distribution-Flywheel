# PR #13 R1 — ledger-only checkpoint override review

## 給負責人的兩分鐘簡報

**本輪處理：** 覆核 PR #13 精確 head `b139304eeaac334086a77e07f31a5606a42156a5` 的 ledger-only 變更。  
**實際內容：** 只改 `governance/state.json` 與 branch-local `reviews/STATUS.md`，把 canonical checkpoint 從 owner discoverability 改成 `A4_ELIGIBLE_CANDIDATE_SEARCH`。  
**結論：** 不能採納。它沒有有效 work_id／owner instruction／executor receipt，引用的 PR12 `488b74f…` 已被新 head `a76588e…` 取代，而且宣稱「本輪不執行搜尋」時搜尋結果已經存在。  
**下一步：** PR #13 保持平行帳本 side artifact；main checkpoint 不變，不 merge、不派修復。  
**審查結論：** BLOCKED

## 1. Review identity

| field | value |
|---|---|
| repository | `firekou/Open-Skill-Distribution-Flywheel` |
| PR | [#13](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/13), Draft / open / unmerged |
| reviewed head | `b139304eeaac334086a77e07f31a5606a42156a5` |
| base | `main@b95e2e354536ca3355519acf5ce99d5ef76a09b9` |
| changed paths | `governance/state.json`, `reviews/STATUS.md` |
| comments | 0 |
| workflow runs / commit statuses / PR reviews | 0 / 0 / 0 |
| reviewer | GPT independent reviewer |
| review time | 2026-09-23 (Asia/Taipei) |

Webhook synchronize did not change head; GitHub mergeability recalculated to true. No duplicate content review was created.

## 2. Authority and freshness checks

| check | result |
|---|---|
| valid work_id / bounded packet | FAIL：PR body沒有固定 work_id、revision、dedup key、deadline |
| owner instruction | FAIL：只有 branch文字與 commit message聲稱 owner-authorized |
| executor receipt | FAIL：沒有 session/run、claim、result SHA |
| source freshness | FAIL：引用 PR12 `488b74f…`，但 PR12 live已是 `a76588e…` |
| factual consistency | FAIL：PR body說不執行搜尋，但 PR12 `a76588e…` 已新增搜尋結果 |
| canonical checkpoint | FAIL：試圖把 `OWNER_GITHUB_DISCOVERABILITY_DECISION` 改成未授權的搜尋關 |
| safe external effects | PASS | 沒有邀請、外部留言、merge、provider call或支出 |

## 3. Findings

### P1 — PR13-R1-01：未授權覆寫 canonical checkpoint

PR #13 將三個位置的 next checkpoint 改成 `A4_ELIGIBLE_CANDIDATE_SEARCH`。GitHub PR 事件、Cursor commit與 co-author line都不是 owner instruction，也沒有符合 handoff規格的工作包。

**Disposition:** 不採納 ledger override；main維持 `OWNER_GITHUB_DISCOVERABILITY_DECISION`。

### P1 — PR13-R1-02：來源 head 已過期

PR #13 把 PR12 `488b74f…` 當作 close paperwork evidence；PR12在本 review前已前進到 `a76588e…`，並新增搜尋結果。PR13 invalidates_when自己也寫 cited head changes即失效。

**Disposition:** 此 head在開啟後即失效，不可 merge。

### P1 — PR13-R1-03：帳本聲明與 live事實衝突

PR13 STATUS寫「本輪不執行搜尋」，但 PR12 `a76588e…` 已經聲稱完成搜尋並列出結果。即使不判斷該搜尋是否可信，帳本也不能同時把它描述成未執行。

**Disposition:** PR13不是可信 current state。

### P2 — PR13-R1-04：重複建立平行 controller／ledger

main已用 REVIEW-MAIN記錄 PR12 R3與R4。另開 ledger-only PR來改 main checkpoint，會讓作者分支與 reviewer main競爭 canonical狀態。

**Disposition:** 保留PR作歷史side artifact，不 merge、不再修。

## 4. Final gate

```yaml
review_gate:
  decision: BLOCKED
  reviewed_head: "b139304eeaac334086a77e07f31a5606a42156a5"
  highest_evidence: VERIFIED
  blocking_findings:
    - "PR13-R1-01"
    - "PR13-R1-02"
    - "PR13-R1-03"
  non_blocking_findings:
    - "PR13-R1-04"
  next_checkpoint: "OWNER_GITHUB_DISCOVERABILITY_DECISION"
  dispatch_repair: false
```

Canonical disposition：

- PR13 is a blocked ledger-only side artifact。
- PR12 latest search head `a76588e…` remains separately BLOCKED under R4。
- PR8 canonical reviewed content `9bcd418…` remains **APPROVED_WITH_CONDITIONS**。
- Eligible candidates = 0；invitations = 0；external adoption = 0。
- No merge, invitation, publication, settings/permission change, provider call or spend is authorized。

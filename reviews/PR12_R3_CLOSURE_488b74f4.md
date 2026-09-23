# PR #12 R3 — invite-round closure and search-scope review

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者或其 Agent 使用已驗證的 routing／compression 資產，累積可驗證的外部採用。  
**本輪處理：** 覆核 PR #12 精確 head `488b74f448e0de3c589b148f5179c055ec24f694` 的 A4 關閉紀錄與新增候選搜尋範圍。  
**本輪成果：** VERIFIED：C1／C2 已從 eligible 改為 WITHDRAWN，合格候選 0、不發送的核心處置與 canonical PR8 R3 一致。  
**仍有風險：** 文件仍以過期 PR8 head、revision 18 與舊 Quickstart SHA 為證據錨點；sender 指定缺可追溯 owner instruction；新增 `A4_ELIGIBLE_CANDIDATE_SEARCH` 取代 main 的 owner discoverability checkpoint，形成未授權支線。  
**下一步與停止點：** 不派第三輪修復。PR #12 保持 side artifact；canonical 下一 checkpoint 仍為 `OWNER_GITHUB_DISCOVERABILITY_DECISION`。PR #8 最新 head `9ab2cbb…` 另列未審／未批准。  
**審查結論：** BLOCKED

## 1. Review identity

| field | value |
|---|---|
| repository | `firekou/Open-Skill-Distribution-Flywheel` |
| PR | [#12](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/12), Draft / open / unmerged |
| prior live head | `5820405704e57b0d58697285663bd8c725f470ee` |
| reviewed head | `488b74f448e0de3c589b148f5179c055ec24f694` |
| base shown by GitHub | `main@9ce89a252f98c7d9f883588cfea07ba0ed7c6493` |
| changed paths | precheck, new search-scope draft, branch-local STATUS |
| PR comments | 0 |
| workflow runs / commit statuses / PR reviews | 0 / 0 / 0 |
| reviewer | GPT independent reviewer |
| review time | 2026-09-23 (Asia/Taipei) |

本輪只 review 此一未審內容 head。沒有 merge、發送、設定修改、provider call 或支出。

## 2. Exact change boundary

`58204057… → 488b74f4…` 為 1 commit、3 paths：

1. `reviews/A4_DAY_OF_INVITATION_PRECHECK_2026-09-23.md`：撤回 C1／C2，將本輪標為 0 名與不發送。
2. `reviews/A4_ELIGIBLE_CANDIDATE_SEARCH_SCOPE_2026-09-23.md`：新增搜尋範圍草案。
3. `reviews/STATUS.md`：branch-local 一行狀態差異。

沒有 PR comment、session/run、固定 work_id claim、dedup key 或 executor receipt。事件與 bot commit 不是授權。

## 3. Acceptance table

| criterion | status | evidence |
|---|---|---|
| C1／C2 不再誤列 eligible | PASS | precheck 已改為 WITHDRAWN／NOT_ELIGIBLE，符合 PR8 R3 |
| 邀請維持 0、未發送 | PASS | 文件明列 Eligible = 0、NOT SENT；沒有外部留言證據 |
| 使用最新可信證據錨點 | FAIL | 仍以 PR8 `b76fc7…`、content `8161c6a…`、main revision 18 為主要錨點 |
| Quickstart URL 指向最新已審狀態 | FAIL | 仍使用 `8161c6a…`；最新已審 Quickstart 位於 `9bcd418…` |
| sender 指定有 durable owner evidence | FAIL | PR comments 為 0；只有 branch 文字聲稱愛莎／Frank 指定 `firekou` |
| next checkpoint 不建立未授權支線 | FAIL | branch 將下一關改成 `A4_ELIGIBLE_CANDIDATE_SEARCH`，但 main canonical 是 `OWNER_GITHUB_DISCOVERABILITY_DECISION` |
| 遵守 2/2 修復上限 | PASS only if stopped | 不得再派 Claude 第三輪 |

## 4. Findings

### P1 — PR12-R3-01：過期 Quickstart 與帳本錨點

PR10 已完成窄範圍 M1 replay，PR8 R3 的 `9bcd418…` 才是反映此狀態的最新已審 Quickstart。PR #12 仍主張 `8161c6a…` 為貼上用 URL，且引用 revision 18 與舊 PR8 head。若對外使用，會回退到 replay pending 的過期敘述。

**Disposition:** PR12 不得作為 send input 或 canonical precheck。

### P1 — PR12-R3-02：sender 指定仍缺可追溯授權

文件稱 `firekou` 已由愛莎／Frank 指定，但 PR #12 comments、reviews 均為 0，也沒有其他 durable owner instruction URL。身份、repo admin、commit co-author 或 Cursor token 都不能代替發送授權或目標 Discussion capability evidence。

**Disposition:** canonical state 不提升 sender capability；沒有匹配候選時也不需要先做權限測試。

### P1 — PR12-R3-03：未授權改寫下一 checkpoint

新增搜尋範圍本身是 planning draft，但 branch 把它寫成下一關並要求 owner 再核定，覆蓋 main 已確立的 `OWNER_GITHUB_DISCOVERABILITY_DECISION`。這會建立平行流程並讓已完成的 2/2 修復循環繼續變形。

**Disposition:** 搜尋草案可保留為未採納資料，不構成 work authorization；canonical checkpoint 不變。

### P2 — PR12-R3-04：同檔內 live anchors 自相矛盾

precheck 上半部承認關閉 commit 為 PR8 `9ab2cbb…`，但讀取錨點與 hard-gate 表仍把 PR8 live head 寫成 `b76fc7…`，使 machine consumer 無法判斷哪個 head 才是基準。

**Disposition:** 本 head 不能升為可信 gate。

## 5. Related live state

- PR #8 current head：`9ab2cbb09f44a94a0e52d8e8c4d6bbb9de2d6b34`。
- 相對上次已審 result `95317ee…`，PR8 current head 多 2 commits，修改 `CANDIDATES.md` 與 `INVITATIONS.md`。
- 它保留 C1／C2 withdrawn 與 0 名候選，但仍把邀請 URL 固定到舊 `8161c6a…`。
- 本輪沒有 review 或批准 PR8 `9ab2cbb…`；其狀態為 UNREVIEWED / NOT APPROVED。

## 6. Final gate

```yaml
review_gate:
  decision: BLOCKED
  reviewed_head: "488b74f448e0de3c589b148f5179c055ec24f694"
  highest_evidence: VERIFIED
  closed_from_prior_review:
    - "PR12-R2-01 candidate eligibility contradiction"
  blocking_findings:
    - "PR12-R3-01"
    - "PR12-R3-02"
    - "PR12-R3-03"
  non_blocking_findings:
    - "PR12-R3-04"
  next_checkpoint: "OWNER_GITHUB_DISCOVERABILITY_DECISION"
  repair_rounds_used: 2
  repair_rounds_limit: 2
  dispatch_another_repair: false
```

Canonical disposition：

- PR8 reviewed content `9bcd418…` remains **APPROVED_WITH_CONDITIONS**。
- PR12 `488b74f…` is **BLOCKED** and does not override main。
- PR8 `9ab2cbb…` is unreviewed and receives no approval here。
- Eligible candidates = 0；invitations = 0；external adoption = 0。
- No invitation, merge, publication, repository-setting change, provider call, permission change or spend is authorized。

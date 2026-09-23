# PR #12 R4 — candidate-search execution review

## 給負責人的兩分鐘簡報

**本輪處理：** 覆核 PR #12 精確 head `a76588e6b6fd954b0f7057c6b6b89295e4c74fcb` 新增的候選搜尋結果。  
**實際成果：** 文件列出 39 個 Q&A、35 個 General／Ideas、約 16 個全文與 67 個 issue 命中，最後仍判定合格候選 0；沒有留言、邀請或外部採用。  
**可採信範圍：** C1／C2 仍不合格、#3673／#3736 只能當 issue 線索，與既有 gate 一致。  
**不能採信的部分：** 「愛莎已准、飛輪長已准」沒有新的 owner instruction；搜尋總數與查詢結果沒有 raw receipt／固定 query evidence，不能升成 VERIFIED；PR12 仍帶過期 PR8／Quickstart anchors。  
**下一步：** 不派第三輪、不擴大 S3／S4、不調整產品問題句。canonical checkpoint 仍是 `OWNER_GITHUB_DISCOVERABILITY_DECISION`。  
**審查結論：** BLOCKED

## 1. Review identity

| field | value |
|---|---|
| PR | [#12](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/12), Draft / open / unmerged |
| prior reviewed head | `488b74f448e0de3c589b148f5179c055ec24f694` |
| reviewed head | `a76588e6b6fd954b0f7057c6b6b89295e4c74fcb` |
| commit author / committer | `cursoragent` |
| changed paths | precheck 1-line link update; new search-result page |
| PR comments | 1 reviewer receipt for prior R3; no owner authorization |
| workflow runs / commit statuses / PR reviews | 0 / 0 / 0 |
| reviewer | GPT independent reviewer |
| review time | 2026-09-23 (Asia/Taipei) |

本輪只 review 此一未審內容 head。

## 2. Exact delta

`488b74f4… → a76588e6…` 為 1 commit、2 paths：

1. `reviews/A4_ELIGIBLE_CANDIDATE_SEARCH_2026-09-23.md` 新增 96 行搜尋結果。
2. precheck 將「核定前不執行」換成搜尋結果連結。

沒有 session/run、work_id、dedup key、executor receipt 或查詢輸出附件。commit message 的 co-author line不是 owner authorization。

## 3. Acceptance table

| criterion | status | evidence |
|---|---|---|
| 不重開 C1／C2 | PASS | 兩者均標 WITHDRAWN_STILL |
| 不為湊數放寬 gate | PASS | 10 筆全部拒絕或只列 clue |
| 不發送／不留言 | PASS at repo evidence level | 文件聲明未發；無外部 URL receipt |
| 搜尋範圍有可信授權 | FAIL | 只有 branch 文字聲稱愛莎／飛輪長已准；PR thread 無此指令 |
| 搜尋結果可重放 | FAIL | 沒有固定 API query、pagination、raw result、時間戳 receipt 或 hash |
| 最新 evidence anchors | FAIL | precheck 仍綁舊 PR8 head／`8161c6a…` Quickstart |
| canonical checkpoint 不被覆寫 | FAIL | 結果頁要求考慮 S3 例外、S4 擴大或調整問題句，偏離 main owner-discoverability checkpoint |
| 修復上限 | PASS only if stopped | 2/2 已用完，不得派第三輪 |

## 4. Findings

### P1 — PR12-R4-01：用 branch 自述代替 owner 授權

結果頁寫「愛莎已准；飛輪長已准執行」，但 PR #12 唯一 comment 是前一輪 reviewer receipt，內容明確指出沒有 owner instruction。bot commit、co-author line 或同名 GitHub login不能擴張權限。

**Disposition:** 搜尋頁只能算未授權的 read-only supplemental artifact，不能成為新 work packet、checkpoint 或發布依據。

### P1 — PR12-R4-02：搜尋總數與 0-candidate 結論不可獨立重放

文件列出 39、35、約 16、67 等數字，但沒有精確 endpoint/query、cursor/pages、raw response snapshot、result hash 或 executor receipt。十個代表案例的判定方向合理，不足以證明「完整掃描後為 0」。

**Disposition:** 0 eligible 維持既有 canonical 結論，不因本頁提高 evidence level；新搜尋主張上限為 CLAIMED/OBSERVED。

### P1 — PR12-R4-03：再次建立未授權後續分支

結果頁把下一步導向 S3 issue 例外、S4 相鄰 repo 或調整資產問題句。這些會改變 channel／ICP／asset scope，且 main 下一 checkpoint 已是 owner 對 GitHub discoverability／publication path 的決定。

**Disposition:** 不執行 S3／S4、不調整資產問題句、不建立新 controller。若 owner 未來另行授權，再建立新的 bounded packet。

### P2 — PR12-R4-04：承接 R3 過期 anchors

precheck 仍保留 revision 18、PR8 `b76fc7…` 與 Quickstart `8161c6a…`，沒有關閉 R3 的 evidence regression。

## 5. Final gate

```yaml
review_gate:
  decision: BLOCKED
  reviewed_head: "a76588e6b6fd954b0f7057c6b6b89295e4c74fcb"
  highest_evidence: OBSERVED
  blocking_findings:
    - "PR12-R4-01"
    - "PR12-R4-02"
    - "PR12-R4-03"
  non_blocking_findings:
    - "PR12-R4-04"
  eligible_candidates: 0
  invitations_sent: 0
  external_adoption: 0
  next_checkpoint: "OWNER_GITHUB_DISCOVERABILITY_DECISION"
  repair_rounds_used: 2
  dispatch_another_repair: false
```

Canonical disposition：

- PR8 reviewed content `9bcd418…` remains **APPROVED_WITH_CONDITIONS**。
- PR12 `a76588e…` is **BLOCKED** and does not override main。
- Search result is retained only as unverified supplemental evidence。
- No invitation, external post, merge, publication, settings/permission change, provider call or spend is authorized。

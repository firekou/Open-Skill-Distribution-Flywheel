# PR #12 R2 — stale authority and invitation precheck review

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者或其 Agent 使用已驗證的 routing／compression 資產，並取得真實外部採用，而不是為湊數發送。  
**本輪處理：** 覆核 PR #12 新 head `a137f194083a8acb6615e824b5558104b44a5ad9` 對 sender、邀請資格與 Quickstart URL 的更正。  
**目前進度：** canonical A4 結論仍是 PR #8 R3：合格候選 0、邀請 0、外部採用 0；下一 checkpoint 為 owner 的 GitHub discoverability 決定。  
**本輪成果：** VERIFIED：PR #12 只改兩個 review／status 檔，但內容與最新 canonical review 衝突，而且其 gate 在提交時已因 PR #8 head 改變而失效。  
**還有什麼風險：** (1) 把 C1／C2 重新寫成 eligible，可能導致離題發送；(2) 用 bot commit／co-author line 代替 owner 授權證據；(3) 把邀請連回仍寫 M1 pending 的舊 Quickstart SHA。  
**需要負責人決定：** 無新增決定。本輪不採信「firekou 已指定為 sender」；真正需要的下一個 owner 決定仍是是否授權 GitHub About／topics 與 publication path。  
**下一步與停止點：** PR #12 此 head 停止，不派第三輪。PR #8 新 head `a74fe934…` 另列未審／未批准，不因本 review 自動成立。  
**審查結論：** BLOCKED

## 1. Review identity

| field | value |
|---|---|
| repository | `firekou/Open-Skill-Distribution-Flywheel` |
| PR | [#12](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/12), Draft / open / unmerged |
| prior reviewed head | `707dc26d15d8b0a2a6a34cb0364fd73f68e397d8` |
| reviewed head | `a137f194083a8acb6615e824b5558104b44a5ad9` |
| commit author / committer | `cursoragent` |
| commit message claim | `review: record firekou as the A4 sender` |
| changed paths | `reviews/A4_DAY_OF_INVITATION_PRECHECK_2026-09-23.md`, `reviews/STATUS.md` |
| PR comments | 0 |
| workflow runs / combined statuses / PR reviews | 0 / 0 / 0 |
| reviewer | GPT independent reviewer |
| review time | 2026-09-23 (Asia/Taipei) |

目標對齊：

- 最新 canonical review 是 [PR8 R3](PR8_R3_A4_PRECHECK_9bcd4181.md)，不是 PR #12 branch 自己的 review gate。
- 本輪只判斷新 PR #12 head 是否能成為新的可信 precheck，不把 commit message、co-author 或 bot push 當成人類授權。
- 2/2 修復上限已用完；本輪不得用另一個 PR 建立平行第三輪。

## 2. Exact change boundary

`707dc26… → a137f194…` 為 1 commit：

1. `reviews/A4_DAY_OF_INVITATION_PRECHECK_2026-09-23.md`：新增 sender 已指定、URL fill 已授權、send deferred 的主張，並改寫 gate。
2. `reviews/STATUS.md`：把 branch-local 狀態改成 sender 已指定。

沒有 session/run、固定 work_id claim、dedup key 或 executor result receipt；PR comments 為 0。commit message 的 `Co-authored-by` 不是 owner instruction 的證據。

## 3. Acceptance table

| criterion | status | evidence | proof | gap |
|---|---|---|---|---|
| 以最新 main 與 canonical review 為準 | FAIL | VERIFIED | main 已記錄 PR8 R3 content `9bcd418…` 為 APPROVED_WITH_CONDITIONS；PR12 仍以舊內容與舊結論為主 | branch review 未重建 |
| 候選必須直接匹配資產 | FAIL | VERIFIED | PR12 owner brief／recipient table 仍稱 C1/C2 eligible；PR8 R3 已驗證兩者必須 WITHDRAWN | 有導致離題發送的風險 |
| owner sender 授權需有可信證據 | FAIL | VERIFIED | PR12 無 comment、無 owner-authored instruction；只有 cursoragent commit 與 co-author line | 無 durable owner authorization |
| immutable URL 指向最新已審 Quickstart | FAIL | VERIFIED | PR12／PR8 新填入 `8161c6a…`；最新已審 Quickstart 是 `9bcd418…`，其 §9 才反映 PR10 已完成 M1 | 舊 URL 會顯示 replay pending |
| gate 在提交時有效 | FAIL | VERIFIED | PR12 gate 寫「PR #8 head leaves `b76fc7…` 即失效」，但提交時 PR #8 已為 `a74fe934…` | gate 自我失效 |
| 沒有發送 | PASS | OBSERVED | 文件仍寫 NOT SENT；沒有 target Discussion comment evidence | 不構成採用 |
| 不建立第三輪／平行 controller | PASS only if stopped | OBSERVED | 尚未派新 packet | 必須在此停止 |

## 4. Findings

### P1 — PR12-R2-01：把已撤回候選重新寫成 eligible

**Consequence:** 文件上半部仍把 C1／C2列為可發送，與同檔後段「r3 已標 WITHDRAWN」直接矛盾，也違反 canonical PR8 R3。若有人只讀 owner brief、recipient table 或 machine-readable gate，可能誤發離題邀請。

**Evidence:** PR12 head 的 owner brief寫「C1、C2 仍可作為既有 Q&A 回覆對象」；recipient table 仍標 ELIGIBLE；gate 仍寫 `READY_FOR_OWNER_INVITE_APPROVAL`。PR8 R3 已驗證 C1 問 Command Code／9router request shape，C2 問 Anthropic `/v1/messages`，本資產不能回答。

**Required disposition:** 不得把 PR12 head 當 canonical precheck、send decision input 或 adoption evidence。因 2/2 已用完，本 reviewer不派第三輪；若未來重新啟動邀請，必須從 canonical PR8 R3 重新建立新的 day-of precheck。

### P1 — PR12-R2-02：舊 Quickstart URL 回退證據狀態

**Consequence:** `8161c6a…` 的 Quickstart 仍把 independent replay 寫成 pending；最新 `9bcd418…` 才正確記載 PR10 的窄範圍重放。對外使用舊 URL 會讓採用者讀到已過期狀態。

**Evidence:** PR12 明列並宣稱已填入 `8161c6a33251b06c44db9f5dbabc9431fa73b67d`。最新 canonical review已驗證 immutable content URL應固定到 `9bcd4181cd3fb87bea108c93df28b96f1767bfd5`。

**Required disposition:** 不得使用 PR12 記錄的 URL；PR8 新 head `a74fe934…` 的 URL fill 也不因本 review獲准。

### P1 — PR12-R2-03：把 bot commit 當 owner 授權

**Consequence:** 會把身份資訊（repo owner、login、display name）誤當成發送授權，破壞「事件只是喚醒，不是權限」的基本規則。

**Evidence:** commit author／committer皆為 `cursoragent`；PR comments為 0。commit message與 `Co-authored-by` 能記錄聲稱內容，不能證明 owner實際下達「firekou 作為 sender」與「可填 URL」兩項指令。

**Required disposition:** canonical state不得升級 sender capability。只有可追溯的 owner instruction與實際目標渠道 capability evidence，才能在真正出現匹配候選時更新。

### P2 — PR12-R2-04：machine-readable gate 在提交時已自我失效

**Consequence:** 即使忽略前三項，這份 gate也不能被自動化消費為有效批准。

**Evidence:** invalidates_when 寫 PR #8 head離開 `b76fc7…` 即失效；PR12提交已記錄 PR #8填寫 commit `a74fe934…`。

**Required disposition:** 將 PR12視為 stale/contradictory side artifact，不修改 canonical下一 checkpoint。

## 5. Scope and evidence checked

Reviewer獨立核對：

- PR #12 live head、base、Draft/open/unmerged狀態；
- prior→current exact commit與兩個 changed paths；
- commit author、committer、message與完整 patch；
- PR #12 comments、workflow runs、combined statuses與reviews；
- 最新 main state revision 21與PR8 R3 canonical review；
- PR #8 live head `a74fe9348ba1f72bcf015697ebe988aa44f4b64d`；
- PR8 `95317ee… → a74fe934…` 只改 `INVITATIONS.md`，且填入舊 `8161c6a…` URL。

本輪沒有覆核或批准 PR8 `a74fe934…` 內容 head，因每輪最多一個新內容 head。它保持 UNREVIEWED / NOT APPROVED。

## 6. Final gate

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: "707dc26d15d8b0a2a6a34cb0364fd73f68e397d8"
  reviewed_head: "a137f194083a8acb6615e824b5558104b44a5ad9"
  highest_evidence: VERIFIED
  blocking_findings:
    - "PR12-R2-01"
    - "PR12-R2-02"
    - "PR12-R2-03"
  conditions: []
  owner_decisions: []
  next_checkpoint: "OWNER_GITHUB_DISCOVERABILITY_DECISION"
  invalidates_when:
    - "reviewed PR12 head changes"
    - "a traceable owner instruction supplies new authority"
    - "candidate or sender capability facts change"
```

Canonical disposition:

- PR8 reviewed content `9bcd418…` remains APPROVED_WITH_CONDITIONS.
- PR12 `a137f194…` is BLOCKED and must not override main.
- PR8 `a74fe934…` is a separate unreviewed content head and receives no approval in this review.
- No invitation, merge, publication, repository-setting change, provider call, permission change or spend is authorized.

# PR #8 R3 — A4 invitation precheck final independent review

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者或其 Agent 能直接使用一個可驗證、可選接入 ATK 的實用 routing／compression 資產，並取得真實外部採用證據。  
**本輪處理：** 獨立覆核 `ATK-OPEN-ADOPTION-01` revision 3 的 A4 當日邀請 precheck；內容 SHA 為 `9bcd4181cd3fb87bea108c93df28b96f1767bfd5`。  
**目前進度：** M1 隔離重放已完成；A4 precheck 已誠實收斂為 0 名合格候選，沒有為湊數發送；M2 外部採用尚未成立。  
**本輪成果：** VERIFIED：C1／C2 與本資產不匹配且均已撤回；Quickstart 已以 immutable URL 正確記載 PR10 的窄範圍重放結論；revision 3 只改四個授權內容檔，result commit 只追加 executor response。  
**還有什麼風險：** (1) 外部採用仍為 0；(2) 目前沒有 owner-approved sender capability，但沒有候選時不需先指定；(3) issue #3736 的「first public confirmation」與 0.37.0 敘述超出現有證據，對外再利用前須改成可歸因的說法。  
**需要負責人決定：** 若要開始 PUBLIC_DISCOVERY T0，需另行決定是否授權 GitHub About／topics 與後續 publication path；本 review 不代替該設定／發布授權。  
**下一步與停止點：** checkpoint 改為 `OWNER_GITHUB_DISCOVERABILITY_DECISION`；本次 2/2 修復迴圈到此停止，不派第三輪，也不在沒有匹配候選時要求指定 sender。  
**審查結論：** APPROVED_WITH_CONDITIONS

## 1. Review identity

| field | value |
|---|---|
| repository | `firekou/Open-Skill-Distribution-Flywheel` |
| PR | [#8](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/8), Draft / open / unmerged |
| claim source | `b76fc7ba08deade6733f140d3a37aadfd201d51c` |
| reviewed content head | `9bcd4181cd3fb87bea108c93df28b96f1767bfd5` |
| live/result head | `95317ee1307c6b61fc3f939f70535b9099c73a2a` |
| session | `session_01RFeCsTYkVywjHvXk7od7Ab` |
| work / revision / stage | `ATK-OPEN-ADOPTION-01` / 3 / `A4-PRECHECK` |
| dedup key | `firekou/Open-Skill-Distribution-Flywheel:8:ATK-OPEN-ADOPTION-01:A4-PRECHECK:3:b76fc7ba08deade6733f140d3a37aadfd201d51c:executor` |
| executor result | [comment 5797486012](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/8#issuecomment-5797486012) |
| reviewer | GPT independent reviewer |
| review time | 2026-09-23 (Asia/Taipei) |

Goal-alignment summary:

- 目標來源：GOAL-02、ATK-OPEN-ADOPTION-20260922 與負責人要求「開源開發者及 Agent 實際使用」。
- 本輪交付：阻止兩份離題邀請，修正對外入口的證據狀態，保留真實的零候選結果。
- 主線連結：直接服務外部採用，不等待 controller ACTIVE，也不重啟 benchmark／Freeze／框架試點。
- 必要驗證與停止點：候選必須能以此資產完成其原問題；文件必須固定版本且不誇大；2/2 後停止修復迴圈。
- 範圍差異：無新增產品或依賴；未發邀請、未套 PR5 patch、未 merge／部署／改權限／支出。

### Exact diff boundary

`b76fc7b… → 9bcd418…` 為 1 commit，只改四個授權內容路徑：

1. `adoption/ATK-OPEN-ADOPTION-01/CANDIDATES.md`
2. `adoption/ATK-OPEN-ADOPTION-01/EVIDENCE_FORMAT.md`
3. `adoption/ATK-OPEN-ADOPTION-01/INVITATIONS.md`
4. `integrations/headroom-atk/AGENT_QUICKSTART.md`

`9bcd418… → 95317ee…` 為 1 commit，只改 `reviews/ATK_OPEN_ADOPTION_EXECUTOR_RESPONSE.md`，因此 content SHA 仍是本次批准邊界。

精確 content 與 result SHA 的 GitHub workflow runs 均為 0、combined commit statuses 均為 0；PR reviews 為 0。connector 未提供獨立 check-runs endpoint，因此不把未知寫成通過或失敗。

## 2. Acceptance table

| criterion | status | evidence | proof | gap |
|---|---|---|---|---|
| 只審一個新內容 head，content／result 分離 | PASS | VERIFIED | compare commits 顯示四個內容檔 + 一個 result-only response | 無 |
| C1/C2 必須和資產實際能力直接匹配 | PASS BY WITHDRAWAL | VERIFIED | C1 為 Command Code／9router request shape；C2 為 Anthropic `/v1/messages`；兩者均標 `NOT_ELIGIBLE_FOR_THIS_ASSET`，邀請稿標 WITHDRAWN／NOT SENT | 合格候選仍為 0 |
| 不為湊數發邀請 | PASS | OBSERVED | CANDIDATES 明列 eligible 0；INVITATIONS 明列 NOT SENT；executor receipt 回報 send 0 | 外部採用仍為 0 |
| A4 既有授權與帳號能力缺口分離 | PASS | OBSERVED | 文件不再重問方向，sender 獨立標 `BLOCKED_ACCESS` | 有匹配候選後仍需指定 exact sender login 並驗 capability |
| Quickstart 反映 M1／P5-R4-01 已完成 | PASS | VERIFIED | §9 連到 immutable main commit `1784520b43fd4e08c1169bcbb4676edd44ccd5e6` 的 PR10 review，並保留 network-none／唯讀／無 secrets 與窄範圍界線 | 不代表 clean install、license、live provider、release 或 adoption |
| 對外入口固定版本 | PASS | VERIFIED | content URL 固定到 `9bcd418…`；GitHub 回讀 blob 為 `503136498e9de7c76bb9ac4f59f714dc7270427d` | content 變更即失效 |
| EVIDENCE_FORMAT 四／五筆誤 | PASS | OBSERVED | 文案改為五個 negative fixtures；validator 邏輯未變 | 無 |
| 公開來源與主張相符 | CONDITIONAL | VERIFIED | #2732、#973、#2050、#2248、#3736 的狀態與題意重新交叉核對 | #3736 的 novelty／0.37.0 歸因須收斂 |
| 外部採用里程碑 M2 | NOT MET | VERIFIED | eligible recipient 0、invitation 0、external adoption 0 | 不能宣稱完成採用 |

## 3. Findings

### P0 / P1

無。

上一輪三個 findings 的處置：

- `A4-R1-01`：C1／C2 已撤回，並以「their question → asset task → boundary」重新分類；**closed by correction**。
- `A4-R1-02`：既有 A4 授權與 sender access 分離；**closed as documentation finding**。實際 account capability 仍是發送前條件。
- `A4-R1-03`：Quickstart 已更新 M1 狀態與 immutable URL；**closed**。

### P2 — A4-R3-01：issue #3736 的新穎性與版本歸因超出證據

**Consequence:** 若把現有句子拿去公開發布，可能把一次公開搜尋寫成完整先例調查，並把 reporter 在 MCP `headroom_compress` 路徑看到的 0.37.0 行為，誤讀成本資產的 OpenAI chat-completions 路徑已重現相同行為。

**Evidence:** CANDIDATES 與 executor response 寫「first public confirmation」及「Our pinned 0.37.0 does not exhibit it」。[issue #3736](https://github.com/headroomlabs-ai/headroom/issues/3736) 能支持的是：這是一個目前公開的使用案例；reporter 表示其 0.37.0 MCP run 保留全部 rows，而 0.38.0 出現有損折疊。它不能證明「first」，也不能把 reporter 的不同 route／payload 變成本資產的重現。

**Required disposition:** 發布、merge 或對外重用此段前，改為可歸因的表述，例如：「a current public example in the headroom issue tracker; the reporter's 0.37.0 MCP run preserved all rows。」刪除 `first`，並避免用 `our asset` 的口吻承接 reporter 的觀察。

**Verification:** 對外文字須明列 reporter attribution、MCP route、0.37.0／0.38.0 差異，且不宣稱 exhaustive novelty 或本資產已重現。

**Gate impact:** 非阻擋本次 precheck，因尚未發送或發布；列為 publication condition。2/2 已用完，不派第三輪 Claude 修復。

## 4. Scope drift and hidden assumptions

- 未發現越過 revision 3 授權路徑的內容改動。
- 「0 名合格候選」是 gate 正常運作，不是可用鄰近候選補足的缺陷。
- 沒有候選時，現在要求 owner 指定 sender 不會推進交付；應在候選出現且 day-of precheck 重跑時再補 capability evidence。
- PR8 仍是 Draft/open/unmerged，且原 PR body 是 revision 1 快照；本 review 只以 live exact SHAs、comments 與 diff 為準。

## 5. Tests and evidence checked

Reviewer independently checked:

- live PR #8 head、Draft/open/unmerged／mergeable 狀態；
- source→content 與 content→result commit graph 及 changed paths；
- content/result SHA 的 workflow runs、combined commit statuses 與 PR reviews；
- revision 3 claim/result receipt 的 session、work_id、source、dedup、content/result SHA；
- 四個內容檔的實際文字與 immutable Quickstart blob；
- PR10 review 的 immutable main target與窄範圍結論；
- headroom public threads/issues 的題意與 current state（2026-09-23）。

Executor reported `check_consistency.py 24/24`、records validator 與 fixtures 結果；本輪沒有重新執行產品 runtime。這次內容變更為候選／邀請／證據文案與 Quickstart 狀態，且 validator 邏輯未變；既有 runtime 證據仍由 PR10 的獨立重放承擔。

## 6. Residual risks and next product step

- M2 尚未完成：外部採用數為 0。
- 合格 direct-invite demand 尚未出現；不可把鄰近問題改寫成需求。
- GitHub default discovery 仍缺 owner-level repository metadata／publication decision；未經授權不得改 About、topics、merge 或發布。
- Controller 與 Claude persistent launcher 狀態不變，仍為 `FOUNDATION_ONLY`；本次既有 session 回傳不證明持久喚起。

本輪不再修文件迴圈。若負責人希望推進真實採用，下一個最小決策是：是否授權獨立的 GitHub discoverability 動作（先核對 proposed About/topics 與可公開的 immutable asset path）。通過後再建立 PUBLIC_DISCOVERY T0；出現真正匹配候選時，才回到 day-of sender capability precheck。

## 7. Final gate

```yaml
review_gate:
  decision: APPROVED_WITH_CONDITIONS
  reviewed_base: "b76fc7ba08deade6733f140d3a37aadfd201d51c"
  reviewed_head: "9bcd4181cd3fb87bea108c93df28b96f1767bfd5"
  result_head: "95317ee1307c6b61fc3f939f70535b9099c73a2a"
  highest_evidence: VERIFIED
  blocking_findings: []
  conditions:
    - "Do not send an invitation while eligible candidates are 0."
    - "Before any send, record an owner-approved exact sender login and verify target-channel capability."
    - "Before merge/public reuse, replace issue #3736 novelty and 0.37.0 wording with explicit reporter/MCP-route attribution."
    - "Do not claim M2 or external adoption while external_adoption_count is 0."
  owner_decisions:
    - "Whether to authorize a separate GitHub About/topics and publication-path action for PUBLIC_DISCOVERY T0."
  next_checkpoint: "OWNER_GITHUB_DISCOVERABILITY_DECISION"
  invalidates_when:
    - "reviewed content head changes"
    - "candidate, sender-account, or public-source facts change"
    - "an invitation, merge, publication, deployment, provider call, permission change, or spend occurs"
```

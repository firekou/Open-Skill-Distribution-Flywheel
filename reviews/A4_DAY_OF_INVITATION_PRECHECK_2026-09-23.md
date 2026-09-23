# A4 day-of invitation precheck — 2026-09-23

工作單：ATK-OPEN-ADOPTION-01。本頁只做邀請前核對。沒有發送邀請、留言、私訊或電子郵件，沒有套用 PR #5 patch，沒有 merge。

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者與其 Agent 能依已驗收的 Headroom 試用資產完成真實離線檢查，ATK 只是可選上游。
**本輪處理：** 只核對 A4 當日四項：收件人、渠道、發送帳號、不可變 Quickstart URL。
**目前進度：** 本輪 A4 邀請已關閉。合格候選 0。C1、C2 為 WITHDRAWN。帳號 `firekou` 已指定。邀請仍是 NOT SENT。
**本輪成果：** 紙本與 PR #8 live `CANDIDATES.md`／`INVITATIONS.md` 對齊。先前把 C1、C2 寫成可發，是主題相鄰排名，資產答不了他們的原問題。最高證據等級 OBSERVED（PR #8 檔案）加上先前 VERIFIED 的 Quickstart blob。
**還有什麼風險：** 把帳號指定、URL 已填或下一關搜尋範圍當成可以發送。
**需要負責人決定：** 本輪不發送，審議已結束。下一關搜尋範圍仍是草案，要不要執行另准；那不是發送授權。
**下一步與停止點：** `A4_ELIGIBLE_CANDIDATE_SEARCH`。本輪在關閉紀錄寫上後停止。不發送、不套 patch、不 merge。
**審查結論：** BLOCKED

方向對齊：目標來源是 2026-09-23 愛莎／Frank 關閉本輪 A4 邀請的指示，以及 ATK-OPEN-ADOPTION-20260922／GOAL-02。本輪交付是一份與 live 檔一致的關閉紀錄，加上下一關搜尋範圍草案。沒有這份對齊，紙本仍會把不能回答的 C1、C2 留成可發。沒有新增產品方向、支出、發送或 merge。下一關見 [A4_ELIGIBLE_CANDIDATE_SEARCH_SCOPE_2026-09-23.md](A4_ELIGIBLE_CANDIDATE_SEARCH_SCOPE_2026-09-23.md)。

## 讀取錨點

| 項目 | live 讀取 | 證據 |
|---|---|---|
| PR #8 | Draft、open、未 merge；head `b76fc7ba08deade6733f140d3a37aadfd201d51c`；分支 `claude/atk-open-adoption-01-teua0c` | GitHub PR API，2026-09-23 |
| 已審內容 SHA | `8161c6a33251b06c44db9f5dbabc9431fa73b67d` | `reviews/PR8_R2_CONDITIONS_8161c6a3.md` 與 PR #8 head 上的 executor response |
| 不可變連結目標（commit A） | `fb47e31b54b35518322254d0d69d7c7193dc2266` | 同上；A-R1-03 |
| PR #8 live／result head | `b76fc7ba08deade6733f140d3a37aadfd201d51c` | PR API |
| PR #5 | Draft、open、未 merge；head 仍是 `304af885193245da7186cb6b9ab247ec2494bd86` | PR API |
| main 帳本 | `origin/main` `f22e99d78d3940a6da00cb0f25778b06701ce4c7`；`state.json` revision 18；`next_checkpoint` 為 `PR8_DAY_OF_A4_INVITATION_PRECHECK` | `git show origin/main:governance/state.json` |
| Draft PR #11 | 仍 Draft、open、未 merge；head `899854f8cef12f6fdb4ad0ae76674b90af165638`；同樣把 next checkpoint 設為該 precheck，並把 P5-R4-01 標成只對 `304af885…` CLOSED | PR API 與該 head 的 `governance/state.json` |

P5-R4-01 的結案只綁 PR #5 head `304af885193245da7186cb6b9ab247ec2494bd86`。它不是 merge、不是邀請、也不是套用 `pr5-doc-delta.patch`。

## 1. Recipients

來源：PR #8 head `b76fc7ba…` 的 `adoption/ATK-OPEN-ADOPTION-01/CANDIDATES.md`（blob `88f773da467afee6ec92f1aec809857911d0ad68`）。討論與 issue 於 2026-09-23 用 GitHub API 重讀。沒有在那些串上留言。

| id | venue | URL | live 狀態（2026-09-23） | 邀請資格 |
|---|---|---|---|---|
| C1 | headroom GitHub Discussion，Q&A，#2732，作者 `timedr128` | https://github.com/headroomlabs-ai/headroom/discussions/2732 | 串仍 open、未鎖。對方問的是 Command Code request shape，以及 9router 會不會改 shape／header。 | **WITHDRAWN**／`NOT_ELIGIBLE_FOR_THIS_ASSET`。 |
| C2 | headroom GitHub Discussion，Q&A，#973，作者 `kulig1985` | https://github.com/headroomlabs-ai/headroom/discussions/973 | 串仍 open、未鎖。對方問的是 Anthropic `/v1/messages` 如何改自訂上游。 | **WITHDRAWN**／`NOT_ELIGIBLE_FOR_THIS_ASSET`。 |
| C3 | headroom GitHub Issue #3242 | https://github.com/headroomlabs-ai/headroom/issues/3242 | `state=closed`，`state_reason=completed`，`locked=false`，關閉於 2026-08-24。 | **BLOCK**。已關閉，且 CANDIDATES 本來就不是邀請渠道。 |
| C4 | headroom GitHub Issue #3198 | https://github.com/headroomlabs-ai/headroom/issues/3198 | `state=open`，`locked=false`，0 則留言，更新時間仍是 2026-08-22。 | **NOT_ELIGIBLE**。串還在，但沒有可附上的重現；CANDIDATES 規定不發。 |
| C5 | headroom Discussions 分類 Show and tell | https://github.com/headroomlabs-ai/headroom/discussions/categories/show-and-tell | GraphQL：分類 `Show and tell`（slug `show-and-tell`）仍存在，`isAnswerable=false`。 | **NOT_AN_A4_INVITATION**。社群貼文要另一次負責人授權。 |

**Eligible candidates = 0。** 早上把 C1、C2 排成可發，是依主題相鄰：他們在談 routing，我們也量 routing。那個排名是錯的。資產只能回答「這一則純文字 payload，在 headroom 0.37.0 的 OpenAI chat-completions 路由上，上游收到的 body 有沒有變小、關鍵那一行還在不在」。C1 要的是 request schema；C2 要的是 Anthropic 路由。兩則都答不了，所以撤回，不恢復。

對齊來源是 PR #8 `adoption/ATK-OPEN-ADOPTION-01/CANDIDATES.md` 與 `INVITATIONS.md`。關閉紀錄寫入前的 live head 是 `a74fe9348ba1f72bcf015697ebe988aa44f4b64d`；本輪關閉 commit 是 `9ab2cbb09f44a94a0e52d8e8c4d6bbb9de2d6b34`。

## 2. Channel

來源：同一 PR #8 head 的 `adoption/ATK-OPEN-ADOPTION-01/DISTRIBUTION_CHANNELS.md`（blob `b3ef50c698ad61b1c465ecdd82d3ee606b7729fe`）。該檔寫明截至當時沒有任何渠道被提交、張貼或改設定。

**A4 若將來另有合格對象，渠道仍是** headroom Discussions 的既有 Q&A 串回覆。本輪沒有合格收件人，所以不回 C1、C2，也不另開帖。

**這次 A4 發送禁止使用：**

- headroom Issues（C3、C4）
- Show and tell（C5；社群貼文，不是試用邀請）
- 本 repo 的 About／topics（那是負責人改 repo 設定，不是這次邀請）
- Agent Skills、Claude plugin marketplace／官方目錄、Smithery、MCP Registry、Hugging Face、兩個 awesome list、LiteLLM 文件
- 新開一則問題到 Discord。Discord 規則本次仍未登入核對，沿用渠道檔：未核對，不當成 A4 渠道。

## 3. Sending account

**狀態：DESIGNATED / recorded。** GitHub login `firekou`（type=User；repo admin；顯示名稱 “AI Token King Open Source”）。2026-09-23 由愛莎／Frank 指定，選擇「firekou 組織身份」。Cursor 連接的 GitHub login 與 `firekou` 一致。

這只記錄指定。**沒有實證這個帳號能在目標 Discussion 回覆。** 沒有發測試留言。帳號指定不是發送授權。

**本席位沒有發送。** 沒有在 headroom 留言、私訊或寄信，沒有把邀請標成已送。

## 4. Immutable Quickstart URL

`INVITATIONS.md` 在 PR #8 head 仍寫：`<QUICKSTART_URL>` 要在發送當日換成 `integrations/headroom-atk/AGENT_QUICKSTART.md` 的 **pinned blob URL**，SHA 用 reviewed result SHA，**不可用分支網址**。該檔標題仍是 `Invitation drafts (A4) — NOT SENT`，內文仍是 “Nothing below has been posted.” 本輪沒有改這個檔，也沒有改發送狀態。檔案 blob：`de170c866480bfa5918cff97441aedd629c827a7`。

GitHub Contents API 確認檔案存在，且三個 commit 的 blob 相同：

| commit | 角色 | blob SHA | 存在 |
|---|---|---|---|
| `8161c6a33251b06c44db9f5dbabc9431fa73b67d` | 已審內容 SHA；INVITATIONS 所說的 reviewed result 對到這次覆核的內容 head | `8849f87dce6042a41eef6e8141816f61cce0489e` | 是，10741 bytes |
| `b76fc7ba08deade6733f140d3a37aadfd201d51c` | PR #8 live／result head | 同上 | 是 |
| `fb47e31b54b35518322254d0d69d7c7193dc2266` | A-R1-03 已寫進 executor response 的不可變連結目標 | 同上 | 是 |

**貼上用的不可變 URL（reviewed content SHA）：**

https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/8161c6a33251b06c44db9f5dbabc9431fa73b67d/integrations/headroom-atk/AGENT_QUICKSTART.md

Blob SHA：`8849f87dce6042a41eef6e8141816f61cce0489e`。

同一 blob 的另一條已寫入 executor response 的 URL 也成立，位元組相同：

https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/fb47e31b54b35518322254d0d69d7c7193dc2266/integrations/headroom-atk/AGENT_QUICKSTART.md

**會錯的網址：**

- 分支 URL：`https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/claude/atk-open-adoption-01-teua0c/integrations/headroom-atk/AGENT_QUICKSTART.md`。分支會動，INVITATIONS 明確禁止。
- `main`：2026-09-23 Contents API 對 `ref=main` 回 **404**。檔案不在 main。

## 5. Draft messages

`INVITATIONS.md` 維持 **NOT SENT**，內文仍有 “Nothing below has been posted.” 2026-09-23 依負責人對「只填 URL、不發送」的授權，在 PR #8 分支把當時剩下的 4 個 `<QUICKSTART_URL>` 換成 reviewed content SHA 的 blob URL。C2 引文在 live head `95317ee1` 已沒有該佔位符，沒有把 URL 加回被撤回的句子。狀態沒有改成已送。

URL 填入仍只是草稿。`a74fe9348ba1f72bcf015697ebe988aa44f4b64d` 把當時剩下的佔位符換成上面的 blob URL；C2 被撤回的引文沒有把網址加回去。那次填寫不是發送。

## 本輪關閉

`A4_INVITE_ROUND_CLOSED`。愛莎／Frank 關閉這一輪：合格候選 0，決定是 **do not send**。發送審議結束，不是停在「只差准發」。邀請維持 NOT SENT。不 merge，不套 PR #5 patch，不在 headroom 留言。

搜尋結果頁：[A4_ELIGIBLE_CANDIDATE_SEARCH_2026-09-23.md](A4_ELIGIBLE_CANDIDATE_SEARCH_2026-09-23.md)。`Eligible_count` 仍是 0，本輪維持關閉，不是發送授權。

## 6. Hard gates

| gate | 2026-09-23 live | 本輪動作 |
|---|---|---|
| 發送邀請／留言／私訊／電子郵件 | 未發生 | 沒有發送 |
| 套用 PR #5 `pr5-doc-delta.patch` | patch 仍只在 PR #8，未套到 PR #5 | 沒有套用 |
| PR #5 | Draft，head `304af885…`，未 merge | 沒有 merge |
| PR #8 | Draft，head `b76fc7ba…`，未 merge | 沒有 merge |
| PR #9 | Draft，head `ba3f9ae3bce04d72f4afaa6f9e935c112661fca2`，未 merge | 沒有 merge |
| PR #10 | Draft，head `cf37880bb90d6f646591588f39de91df67d7923c`，未 merge | 沒有 merge |
| PR #11 | Draft，head `899854f8cef12f6fdb4ad0ae76674b90af165638`，未 merge | 沒有 merge |

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: "9ce89a252f98c7d9f883588cfea07ba0ed7c6493"
  reviewed_head: "9ab2cbb09f44a94a0e52d8e8c4d6bbb9de2d6b34"
  highest_evidence: OBSERVED
  blocking_findings:
    - "Eligible candidates = 0; C1 and C2 are WITHDRAWN / NOT_ELIGIBLE_FOR_THIS_ASSET"
  conditions:
    - "A4_INVITE_ROUND_CLOSED; decision is do not send"
    - "sender firekou is DESIGNATED / recorded; capability evidence is none; no test comment"
    - "URL fill was draft-only; invitations remain NOT SENT"
    - "no merge of #5 #8 #9 #10 #11 #12"
    - "no PR5 patch application"
    - "no headroom comments"
  owner_decisions:
    - "whether to approve executing A4_ELIGIBLE_CANDIDATE_SEARCH; that approval is not send authorization"
  next_checkpoint: "A4_ELIGIBLE_CANDIDATE_SEARCH"
  invalidates_when:
    - "a later order reopens this invite round"
    - "C1 or C2 eligibility text on PR #8 changes"
    - "a send, PR5 patch, or merge occurs"
```

precheck_decision: BLOCKED_NO_ELIGIBLE_CANDIDATES

合格候選是 0，C1 與 C2 維持 WITHDRAWN；帳號 `firekou` 只是已指定，本輪 `A4_INVITE_ROUND_CLOSED`，決定是不發送，邀請仍是 NOT SENT。

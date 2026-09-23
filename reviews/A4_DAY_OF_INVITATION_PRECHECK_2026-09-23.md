# A4 day-of invitation precheck — 2026-09-23

工作單：ATK-OPEN-ADOPTION-01。本頁只做邀請前核對。沒有發送邀請、留言、私訊或電子郵件，沒有套用 PR #5 patch，沒有 merge。

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者與其 Agent 能依已驗收的 Headroom 試用資產完成真實離線檢查，ATK 只是可選上游。
**本輪處理：** 只核對 A4 當日四項：收件人、渠道、發送帳號、不可變 Quickstart URL。
**目前進度：** P5-R4-01 已在 PR #5 head `304af885…` 結案；邀請本身尚未授權、尚未送出。
**本輪成果：** 五個候選都做了當日 live 讀取；C1、C2 仍可作為既有 Q&A 回覆對象；Quickstart 檔案在三個不可變 SHA 上是同一個 blob。最高證據等級 VERIFIED（GitHub API）。
**還有什麼風險：** 把本頁當成可以發送；用會移動的分支網址；用本席位的 Cursor 整合 token 發文。
**需要負責人決定：** 只剩要不要另准發送。帳號已指定。邀請審議延期，須另一次指令。本頁不是發送授權。
**下一步與停止點：** 本頁交付後停止。發送、套 patch、merge 都不在本輪。
**審查結論：** APPROVED_WITH_CONDITIONS

方向對齊：目標來源是 2026-09-23 的 A4 PRECHECK 指示與已批准決策 ATK-OPEN-ADOPTION-20260922／GOAL-02。本輪交付是負責人可據以決定要不要另准發送的核對頁。沒有這頁，採用主線會停在「資產已驗、邀請還不能審」。驗證到 live head、討論串與 blob URL 為止。沒有新增產品方向、支出、發送或 merge。

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
| C1 | headroom GitHub Discussion，Q&A，#2732，作者 `timedr128` | https://github.com/headroomlabs-ai/headroom/discussions/2732 | `state=open`，`locked=false`，`answer_html_url=null`。2 則留言。最後一則是作者 2026-08-29 詢問 9router 是否改變 request shape，其後沒有新回覆。 | **ELIGIBLE**。仍是第一順位。不是消失、鎖定或已被同一修正回答。 |
| C2 | headroom GitHub Discussion，Q&A，#973，作者 `kulig1985` | https://github.com/headroomlabs-ai/headroom/discussions/973 | `state=open`，`locked=false`，`answer_html_url=null`。1 則 2026-08-29 留言，只要求版本與最小重現，沒有回答 Anthropic `/v1/messages` 自訂上游。 | **ELIGIBLE**，且必須沿用稿內限制：未測過 `/v1/messages`。第二順位。 |
| C3 | headroom GitHub Issue #3242 | https://github.com/headroomlabs-ai/headroom/issues/3242 | `state=closed`，`state_reason=completed`，`locked=false`，關閉於 2026-08-24。 | **BLOCK**。已關閉，且 CANDIDATES 本來就不是邀請渠道。 |
| C4 | headroom GitHub Issue #3198 | https://github.com/headroomlabs-ai/headroom/issues/3198 | `state=open`，`locked=false`，0 則留言，更新時間仍是 2026-08-22。 | **NOT_ELIGIBLE**。串還在，但沒有可附上的重現；CANDIDATES 規定不發。 |
| C5 | headroom Discussions 分類 Show and tell | https://github.com/headroomlabs-ai/headroom/discussions/categories/show-and-tell | GraphQL：分類 `Show and tell`（slug `show-and-tell`）仍存在，`isAnswerable=false`。 | **NOT_AN_A4_INVITATION**。社群貼文要另一次負責人授權。 |

授權內最多三則、各一次。當日仍只有 C1 與 C2 兩則可進草稿。第三個名額保持空著。C3 的 BLOCK 只取消該筆，不取消 C1／C2。

當日另讀 headroom `CONTRIBUTING.md`（blob `775dc16916886333e1127ac4bcb1c9ceed91d343`）與 `CODE_OF_CONDUCT.md`（blob `a90652cf779f63e6c16408cf55788ac8c706b823`），兩份都還在 `main`。CONTRIBUTING 仍寫新問題去 Discord `#help`。這不關閉已經存在的 Q&A 串；A4 稿若獲准，只能回在 C1、C2 這兩條既有串上。

## 2. Channel

來源：同一 PR #8 head 的 `adoption/ATK-OPEN-ADOPTION-01/DISTRIBUTION_CHANNELS.md`（blob `b3ef50c698ad61b1c465ecdd82d3ee606b7729fe`）。該檔寫明截至當時沒有任何渠道被提交、張貼或改設定。

**A4 草稿獲准使用的渠道：** headroom Discussions 的既有 Q&A 串回覆。先回答對方的問題，並表明維護者是 AI Token King。對應 C1、C2。

**這次 A4 發送禁止使用：**

- headroom Issues（C3、C4）
- Show and tell（C5；社群貼文，不是試用邀請）
- 本 repo 的 About／topics（那是負責人改 repo 設定，不是這次邀請）
- Agent Skills、Claude plugin marketplace／官方目錄、Smithery、MCP Registry、Hugging Face、兩個 awesome list、LiteLLM 文件
- 新開一則問題到 Discord。Discord 規則本次仍未登入核對，沿用渠道檔：未核對，不當成 A4 渠道。

## 3. Sending account

**2026-09-23 更正（愛莎／Frank）：發送帳號已指定。** GitHub login 是 `firekou`（type=User；repo admin；顯示名稱 "AI Token King Open Source"）。Frank 選擇「firekou 組織身份」。Cursor 連接的 GitHub login 與 `firekou` 一致。帳號指定不再是未填缺口。

**URL 填入 C1／C2 草稿已授權。發送未授權。** 邀請審議延期，須另一次指令。

**本席位沒有發送。** 沒有在 headroom 的 discussion 或 issue 留言，沒有私訊或寄信，沒有把邀請標成已送。PR #8 上的 URL 填寫只改 repo 內草稿。

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

## 2026-09-23 更正

愛莎／Frank 指定發送帳號為 `firekou`（「firekou 組織身份」）。填入 Quickstart URL 已授權；發送未授權；邀請審議延期。PR #8 live head 在填寫前是 `95317ee1307c6b61fc3f939f70535b9099c73a2a`（r3 已把 C1、C2 標成 WITHDRAWN）。填寫 commit 是 `a74fe9348ba1f72bcf015697ebe988aa44f4b64d`。這次更正不恢復收件人資格，也不授權發送。

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
  decision: APPROVED_WITH_CONDITIONS
  reviewed_base: "f22e99d78d3940a6da00cb0f25778b06701ce4c7"
  reviewed_head: "b76fc7ba08deade6733f140d3a37aadfd201d51c"
  highest_evidence: VERIFIED
  blocking_findings: []
  conditions:
    - "this precheck is not invitation authorization"
    - "sending account is firekou; URL fill is authorized; send is not authorized"
    - "invite deliberation is deferred pending a separate order"
    - "no merge of #5 #8 #9 #10 #11 #12"
    - "no PR5 patch application"
    - "C3 remains BLOCK for invitation; C4 and C5 stay out of A4"
  owner_decisions:
    - "whether to authorize send only"
  next_checkpoint: "OWNER_SEND_AUTHORIZATION_DEFERRED"
  invalidates_when:
    - "PR #8 head leaves b76fc7ba08deade6733f140d3a37aadfd201d51c"
    - "C1 or C2 is locked, closed, or answered"
    - "Quickstart blob 8849f87dce6042a41eef6e8141816f61cce0489e changes"
    - "a send, PR5 patch, or merge occurs"
```

precheck_decision: READY_FOR_OWNER_INVITE_APPROVAL

帳號已指定為 `firekou`，Quickstart URL 已依授權填入仍為 NOT SENT 的草稿；發送未授權，邀請審議延期，這不是發送授權。

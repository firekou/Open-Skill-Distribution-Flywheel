# GPT 規劃／覆核 → GitHub → Claude 執行：雲端觸發橋接規劃

版本 1，2026-09-19。狀態：**PLANNED_NOT_DISPATCHED**（依 GOV-PLAN-02；本檔是規劃，不是啟動授權）。
負責人問題：GPT 在 GitHub 寫完 review 之後，怎麼在不直接呼叫 Claude API、只用 Claude 訂閱的前提下，讓 Claude 自動接手執行，做完再讓 GPT 接續覆核。
本檔回答「用哪個零件、怎麼接、哪裡會斷」。證據等級沿用 E1（我方實測）／E2（官方文件）／E4（第三方）／E6（未驗證）。

## 0. 一句話結論

**Claude 側的持久觸發器已經存在，叫 Claude Code Routines**：帳號層級的雲端排程物件，用訂閱額度跑，可被三種事件喚醒——GitHub PR 事件、對每支 routine 專屬的 HTTP `/fire` 端點、排程。
GOV-R1 review 指出「session 內的 webhook 訂閱不是持久 launcher」是對的；Routine 不綁 session，session 結束後仍存在，這才是 launcher。
推薦結構：**GitHub 是唯一狀態機（PR label ＋ `reviews/` 檔案）；GPT 那側用 ChatGPT 的 GitHub 事件觸發或 Codex cloud 寫入；Claude 那側用一支 Routine 接 `pull_request.labeled`；中間若 GPT 側無法自己貼 label，用一支十幾行的 GitHub Actions workflow 轉譯。**
不採用本地方案（Codex 開瀏覽器接力）：它把電腦當成 launcher，本檔第 6 節說明。

## 1. 已查證事實（E2，官方文件，2026-09-19 抓取）

### 1.1 Claude 側

| 項目 | 事實 | 出處 |
|---|---|---|
| Routines 是什麼 | 儲存好的 prompt ＋ repo ＋ connectors，在 Anthropic 雲端以完整 Claude Code session 自動執行；Pro／Max／Team／Enterprise 皆可用；研究預覽中 | code.claude.com/docs/en/routines |
| 觸發類型 | Schedule（最小一小時）／API（每支 routine 專屬 URL ＋ bearer token）／GitHub 事件；一支 routine 可同時掛多種 | 同上 |
| GitHub 事件支援範圍 | **只有 Pull request 與 Release 兩類**。PR 可指定 opened／closed／assigned／labeled／synchronized 等動作，並可用 Author／Title／Body／Base／Head／**Labels**／Is draft／Is merged 過濾；全部條件須同時成立 | 同上 |
| GitHub 事件前提 | 該 repo 必須安裝 Claude GitHub App；預覽期有每支 routine 與每帳號的**每小時事件上限**，超過即丟棄 | 同上 |
| API 觸發 | `POST https://api.anthropic.com/v1/claude_code/routines/{trig_id}/fire`，header `Authorization: Bearer sk-ant-oat01-…`＋`anthropic-beta: experimental-cc-routine-2026-04-01`；body 可帶 `text`（≤65,536 字）；回 session id 與 URL；**無 idempotency key，重送就多開一個 session** | platform.claude.com/docs/en/api/claude-code/routines-fire |
| `text` 的信任等級 | 以 `<routine-fire-payload>` 包起來、標為不受信任資料；routine 的 prompt 必須明文說「讀取 payload」才會採用 | code.claude.com/docs/en/routines |
| 計費 | **扣訂閱額度，與互動 session 相同**；另有每帳號每日 run 上限；到上限時若帳號沒開 usage credits 就直接拒絕（429 ＋ Retry-After），不會自動轉付費 | 兩份文件皆載 |
| 寫入邊界 | 每次 run 重新 clone、從預設分支開始；推到 `claude/` 前綴分支一律接受；推到其他分支會先檢查（受保護／別人有開 PR／含他人 commit 即拒）；commit 與 PR 以使用者本人 GitHub 身分出現 | code.claude.com/docs/en/routines |
| 運行狀態語意 | run 顯示綠色只代表 session 起來且無基礎設施錯誤，**不代表 prompt 的任務成功**；要開 transcript 看 | 同上 |
| 開關與撤銷 | routine 詳情頁有 on/off；API token 可 Regenerate／Revoke（產新 token 即撤舊） | 同上 |
| 備援：GitHub Actions 版 | `anthropics/claude-code-action@v1` 可用 `CLAUDE_CODE_OAUTH_TOKEN`（`claude setup-token` 產生）走訂閱額度；自動化模式給 `prompt` 即可在任何 GitHub 事件跑；token 綁個人、登出可能失效；額外消耗 GitHub Actions 分鐘；預設拒絕 bot actor（需 `allowed_bots`） | code.claude.com/docs/en/github-actions |

### 1.2 GPT 側

| 項目 | 事實 | 出處 |
|---|---|---|
| ChatGPT 排程任務的事件觸發 | 可由 GitHub **PR 活動**觸發（可篩 PR／作者／標題／label，並選 review、comment、commit 更新或只有 merge）；Plus／Pro／Business／Enterprise；多個事件接近時可能合併成一次 run | learn.chatgpt.com/docs/automations |
| ChatGPT 排程任務能否寫回 GitHub | **官方頁未載明寫入能力**；本 repo 現況 reviewer 事件路徑已有一次實際紀錄（reviews/STATUS.md），但 review 檔如何進 main 未在本檔查證 | ⬜ 待確認 |
| Codex cloud 的 GitHub 整合 | PR 留言 `@codex …` 會以該 PR 為脈絡開一個 cloud 任務，**有權限時可把修正 push 回分支**；可開「自動 review 每個新 PR」；**不支援 issue 建立、label、push 事件** | learn.chatgpt.com/docs/third-party/github |
| Codex GitHub Action | 只接受 `OPENAI_API_KEY`，非訂閱 → 違反「新增自動 API 支出上限 0」，不採用 | learn.chatgpt.com/docs/github-action |

### 1.3 本 session 手上有的（E1）

本 session 是 Claude Code 雲端 session，帶有 `create_trigger`（可建排程／一次性 routine，並可指定「每次觸發開新 session」）、`watch_url`（session 綁定的入站 webhook，**session 結束即失效**）、`subscribe_pr_activity`（session 綁定）。
其中只有 `create_trigger` 建出來的 routine 是持久的；GitHub 事件型 routine 目前要在 claude.ai/code/routines 網頁建立。

## 2. 推薦結構

```
 Claude 推新 commit 到 PR 分支
        │ pull_request.synchronize
        ▼
 ┌────────────────────────┐   review 寫回 GitHub（PR review／comment／reviews/*.md）
 │ GPT reviewer            │──────────────────────────────────────────────┐
 │（ChatGPT 事件任務或     │                                              │
 │  Codex cloud @codex）   │                                              ▼
 └────────────────────────┘                                   ┌──────────────────────┐
                                                              │ 橋接：貼 label         │
        ┌─────────────────────────────────────────────────────│ claude:fix-pending    │
        │  （GPT 側能自己貼 label 就不需要這格；               │ 或直接 POST /fire      │
        │    不能就用 templates/bridge/ 的 Actions workflow） └──────────────────────┘
        ▼
 ┌────────────────────────┐
 │ Claude Routine          │  GitHub 觸發：pull_request.labeled，Labels is one of claude:fix-pending
 │（訂閱額度、雲端、       │  或 API 觸發：/fire 帶 text = {pr, head, review_path, task_id}
 │  每次事件開新 session） │
 └────────────────────────┘
        │ 讀 OPERATING_RULES → 核對 live head → 讀 review → 修 → push 新 SHA
        │ 換 label：claude:fix-pending → review:pending
        ▼
 回到最上面（GPT 被 synchronize 事件喚醒）
```

**狀態機只住在 GitHub label，不住在任何一方的聊天記憶：**

| label | 意義 | 誰貼 | 誰吃 |
|---|---|---|---|
| `review:pending` | 新 SHA 待 GPT 覆核 | Claude routine 結束時 | GPT 事件任務（可用 label 篩） |
| `claude:fix-pending` | GPT 判 BLOCKED／FIX_PENDING，且 finding 影響驗收 | GPT 側或橋接 workflow | Claude routine 的 GitHub 觸發 |
| `claude:executing` | routine 已接單（租約） | Claude routine 開頭 | 第二個 routine session 看到就退出 |
| `review:approved` | 對當前 head 的有效 APPROVED | GPT 側 | 兩邊都停 |
| `gov:planner-needed` | 兩輪修復同一 finding 無新證據／需外部權限 | Claude routine | 人（Planner） |

label 名稱與 OPERATING_RULES 的 READY → EXECUTING → REVIEW_PENDING → REVIEWING → FIX_PENDING 對映，不另造狀態。

## 3. 三個零件

### 3.1 GPT 側：讓 review 落在 GitHub 上一個「機器讀得到」的位置

兩條可走，擇一即可：
- **A. ChatGPT 事件任務（現況）**：已註冊「ATK PR5 提交複核」。缺的是它寫回 GitHub 的能力證據。若它只能在 ChatGPT 介面顯示結果，那 GPT → GitHub 這一步仍是人搬運，橋接再自動也沒用。**先確認這一步**。
- **B. Codex cloud**：由 Claude routine 在收工時**自己在 PR 留言** `@codex 依 reviews/CLAUDE_NEXT_PROMPT… 的檢核清單覆核本 PR 至 <SHA>，結論用 VERDICT: APPROVED|BLOCKED|NEEDS_INFORMATION 作結`。Codex cloud 用 ChatGPT 方案跑，能直接以 PR review／comment 寫回，不需要人碰。這一條把「GPT 被誰叫醒」也閉環了。
  - 風險：官方已知問題——回覆 Codex 自己的留言再 `@codex` 會誤觸發新任務；routine prompt 要規定只在收工那一則留言 @codex，且不回覆 Codex 的留言。

review 結論必須有**固定可 grep 的一行**（例如 `VERDICT: BLOCKED`），橋接 workflow 靠它決定貼哪個 label，不做語意判讀。

### 3.2 橋接：把「review 落地」翻成「Claude 的觸發事件」

只有在 GPT 側貼不了 label 時才需要。`templates/bridge/claude-routine-bridge.yml` 是範本（放在 templates/ 不放 `.github/workflows/`，避免在分支上就被 PR 事件啟動）。兩種輸出二選一：
- **輸出 label**（推薦）：`gh pr edit --add-label claude:fix-pending`。零秘密、零 token；Claude 端靠 Routine 的 GitHub 觸發吃 label。
  - ⬜ 待實測：由 `GITHUB_TOKEN` 貼的 label 是否會送到 Claude GitHub App 的 webhook。GitHub 的限制是「`GITHUB_TOKEN` 造成的事件不會再啟動另一個 workflow」，App webhook 不在此限，但**第一次事件要留證據**。
- **輸出 /fire**：`curl POST $ROUTINE_FIRE_URL` 帶 `text`。適合 GitHub 觸發不支援的事件（issue、push 到 `reviews/`）。要放兩個 secrets（URL、token），且 Actions retry 會重開 session。

### 3.3 Claude Routine

在 claude.ai/code/routines 建立，設定：
- Repository：`firekou/Open-Skill-Distribution-Flywheel`；Environment：Default 即可（GitHub 走 Anthropic 代理，不需開網域）。
- Connectors：**全部移除**，只留 GitHub（routine 預設把帳號所有 connector 都掛上，且 run 中不會再問權限）。
- Trigger：GitHub event → Pull request → `labeled` → Labels is one of `claude:fix-pending`。如需 API 觸發再加一個。
- Prompt 草稿見 `templates/bridge/claude-routine-prompt.md`。重點：先讀 `AGENTS.md` → `governance/OPERATING_RULES.md` → `decisions.json`／`state.json`；查 live PR head；label 換成 `claude:executing` 當租約；只在 PR 自己的 `claude/` 分支工作；兩輪上限；收工換 label、寫 executor response、必要時 `@codex`。

## 4. 煞車與 OPERATING_RULES 的對映

| 規則 | 落在哪個零件 | 狀態 |
|---|---|---|
| 新增自動 API 支出上限 0 | Routines 扣訂閱；**帳號 usage credits 必須保持關閉**，到上限就拒絕而不是計量續跑 | 需負責人確認設定 |
| 同一 task/head/phase 只能一個有效作業 | `claude:executing` label 當租約；routine prompt 開頭檢查，已有即退出 | 約定＋實測 |
| hook 可能重送、去重要持久化 | Routines：每個事件開一個新 session、不重用；`/fire` 無 idempotency。去重只能靠 label 租約與 `reviews/` 內的 head 綁定 | 已知限制，寫進 prompt |
| 操作者停止開關、撤銷 token | routine on/off；API token Revoke；移除 label | 平台原生 |
| 每次模型工作 20 分鐘、每輪 45 分鐘 | Routines 無逐 run 逾時設定；靠 prompt 自律 ＋ 每日 run 上限 | 只有約定，非平台強制 |
| 兩輪修復、同一 finding 兩次無新證據即停 | prompt 讀 `reviews/` 計數，達標貼 `gov:planner-needed` 並不 push | 約定 |
| executor 不得自我 APPROVED | Claude 只會貼 `review:pending`，永遠不貼 `review:approved` | 約定 |
| reviewer 從 GitHub 取原始變更 | GPT 側被 synchronize 事件喚醒，讀精確 SHA | 現況已有一次紀錄 |
| 不能以 exit 0 當 review | run 綠燈 ≠ 任務成功（官方文件明載）；驗收看 PR 上的 SHA 與 review 檔 | 已知 |

## 5. 導入順序（對應 IMPLEMENTATION_PROMPT 的 B → C → D）

1. **確認 GPT → GitHub 這一段**：現行 ChatGPT 事件任務的輸出是否已能落到 GitHub（PR comment 或檔案）。不能就改走 Codex cloud（3.1 B）。這一步不解，後面都是空轉。
2. 在 GitHub 建五個 label；把 `templates/bridge/claude-routine-bridge.yml` 複製到 `.github/workflows/`（走 Draft PR，合併才生效）。
3. 在 claude.ai/code/routines 建 routine（3.3）；先只掛 GitHub 觸發；**關閉** usage credits。
4. **MANUAL_RUN_VERIFIED**：對一個測試 PR 手動貼 `claude:fix-pending`，觀察 routine 是否起 session、是否只推 `claude/` 分支、label 是否切換。留 session URL、SHA、時間。
5. **持久觸發驗證（G6）**：由 GPT 側或橋接 workflow 產生的事件觸發一次完整迴圈（execute → review → fix → review），且過程中沒有人搬 prompt。此時才可把 state.json 的 `claude_launcher` 改 true、`automation.status` 升格。
6. 監看兩個數字：每日 run 用量（claude.ai/code/routines）與每小時 GitHub 事件上限；第一週建議 routine 只綁一個 PR（Labels ＋ Head branch 雙過濾）。

## 6. 不採用與備援

- **本地方案（Codex 開瀏覽器接力 Claude）**：把個人電腦當 launcher，等於把「可用性」綁在一台機器上；且 Codex 操作 claude.ai 網頁屬於自動化他人產品介面，脆弱且難留證據。不採用。
- **Codex GitHub Action**：只吃 API key，違反支出 0。不採用。
- **claude-code-action ＋ OAuth token**：可行備援。事件涵蓋面比 Routines 廣（issue、push、cron 都行），但 token 綁個人且可能失效、要花 Actions 分鐘、bot 留言預設被擋（Codex 留言觸發時要加 `allowed_bots`）。當 Routines 的 GitHub 觸發不夠用時再上。
- **`claude -p "…" --cloud <session-id>`**：可從任何登入的 CLI 把訊息塞進既有雲端 session，但 CI 環境要有訂閱登入，且 session 會過期。不作主線。

## 7. 外部現成方案盤點（E4，只讀首頁，未實跑）

| 專案 | 它做什麼 | 對本案的用處 |
|---|---|---|
| `ataglianetti/agent-orchestration-loop`（MIT） | Claude Code 內的 plan→execute→verify→review→route 迴圈，狀態存磁碟，到人工核准卡停 | 是「一支 Claude 內部」的迴圈，不解決跨 GPT／Claude 的觸發 |
| `huangruiteng/loopx`（Apache-2.0） | 跨 Codex／Claude Code 的本機狀態核心：gate、todo、租約、證據回寫、配額 | 概念與本 repo 的 OPERATING_RULES 高度重疊，但 local-first，仍要一台機器 |
| `NYTC69/review-loop` | 多 agent 的 plan→implement→review，Reviewer 檢查 Executor 是否越界 | 同上，執行層而非觸發層 |
| `Optim-Agent/optim-plans` | Claude 與 Codex 共用的人審計畫與執行閘 plugin | 可借它的 plan 格式，不解決觸發 |
| Aeon（awesome-cli-coding-agents 收錄） | 在 GitHub Actions 無人值守派工到多個 harness | 走 Actions ＋ API key 路線，與支出 0 衝突 |

結論：外部方案解的是「迴圈怎麼管」，沒有一個解「用訂閱、不開電腦、被 GitHub 叫醒」。那一段只有平台原生零件（Routines／ChatGPT 事件任務／Codex cloud）做得到。

## 8. 未查證清單

- ChatGPT 排程任務能否直接寫 GitHub（PR comment／label／commit）。
- `GITHUB_TOKEN` 貼 label 是否送達 Claude GitHub App webhook。
- Routines 的每小時事件上限與每日 run 上限的實際數字（登入 claude.ai/code/routines 才看得到）。
- Codex cloud 在本 repo 的 push 權限與其留言的 bot 身分名稱。
- 本 repo 的 PR5／PR6 分支是否全部符合「`claude/` 前綴或無他人 commit」，否則 routine 推送會被拒。

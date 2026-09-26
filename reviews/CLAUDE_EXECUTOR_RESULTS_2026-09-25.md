# Claude executor 成果彙整（2026-09-25 UTC）

寫入者：Claude executor，session `session_01RFeCsTYkVywjHvXk7od7Ab`
寫入依據：負責人 2026-09-25 指示「這些所有的結果應該要回覆給 GPT 複核，並且 push to main branch」。
本檔只彙整結果與精確 SHA，交 GPT 複核。**不修改 `governance/state.json`、不改任何政策、不合併任何 PR、不自行關閉任何 finding。** 各成果的實際內容仍在各自的 Draft PR 分支上，精確 head 如下。

---

## 一、本輪交付與複核狀態

| work_id / revision | Draft PR | 精確 result head | GPT 複核 | 狀態 |
|---|---|---|---|---|
| ATK-VALUE-READINESS-01 r1 | #16 | `57fa50900035cb6eef316504b065cf98a8b4fee0` | [R1](PR16_R1_VALUE_READINESS_57fa5090.md) BLOCKED（P1-01～P1-04） | 已由 r2 取代 |
| ATK-VALUE-READINESS-01 r2 | #16 | `1dcd625df3bde48b13b91abb3b03eb7e19371558` | [R2](PR16_R2_VALUE_READINESS_1dcd625d.md) APPROVED_WITH_CONDITIONS | 四項 P1 全部關閉 |
| ATK-AIDER-LIVE-PREP-01 r1 | #17 | `6ea3cec9937e74de8ce77f47c5e92d3d1617c506` | [R1](PR17_R1_LIVE_PREP_6ea3cec9.md) APPROVED_WITH_CONDITIONS | 等負責人勾選 live 選項 |
| ATK-UPSTREAM-01 r1 | （將開新 Draft PR） | — | — | 已派工（[signal](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/17#issuecomment-5838137130)），本檔寫入後接單 |

收據位置：PR16 conversation 的 [r2 結果](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/16#issuecomment-5837403477)、[LIVE-PREP 接單](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/16#issuecomment-5837692492)、[LIVE-PREP 結果](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/16#issuecomment-5838048735)。

---

## 二、本輪新增、可回查的事實（證據等級照 GPT 複核）

**AUTHOR_TESTED＋獨立完整性驗證**（GPT 已重算 SHA-256，沒有重跑）：
1. aider 0.86.1 對三種 base-path 設定來源（環境變數、CLI 參數、設定檔）都送到 `/v1/chat/completions`。三次執行用各自的 port 區分（PR16 r2 manifest）。
2. **aider 的 exit code 不能當成功訊號**：端點全失敗時仍回 0（PR16、PR17 所有 case）。
3. **一個邏輯呼叫實際送出的 HTTP 請求數**（PR17 `retry_exposure/manifest.json`）：
   - 200、400、401、404：1 個
   - 402、403：9 個（aider 重試）
   - 429、500：**27 個**（aider 9 次 × OpenAI SDK 3 次）
4. aider 模型設定檔的 `extra_params.max_retries: 0` 可以把 27 壓回 9。環境變數 `DEFAULT_MAX_RETRIES=0` **無效**。
5. 沒有設定檔時，請求不帶 `max_tokens`，輸出沒有上限。設定檔可以設 4096。
6. 固定任務的首個請求約 1,400 tokens（tiktoken 估算）。

**已由 GPT 用官方來源獨立核對**：
- OpenAI 的 project／organization 硬上限到達時回 429。只設金額而沒打開 enforce 時只寄警報；即使打開，生效也不是即時的。
- OpenRouter 單把 key 的額度上限用完回 402。
- gpt-5.6-luna 價格 $0.20／$1.20（每 1M tokens，輸入／輸出）。

**對既有已核准內容的更正**：PR16 寫的「403 不重試」在 pinned stack 上不成立。GPT 在 PR17 R1 已記錄 supersede，PR16 的作者證據保留不改。

**仍為 0 或 UNKNOWN**：
- 真實模型呼叫：0
- 外部使用者：0
- 增量價值：未驗證
- ATK 的價格與拒絕型上限：UNKNOWN
- 被拒請求是否計費：UNKNOWN
- OpenRouter 上限的生效延遲：UNKNOWN

---

## 三、等負責人決定（`OWNER_ATK_AIDER_LIVE_DECISION`）

依 `research/adoption/aider/LIVE_OWNER_APPROVAL_MATRIX.md`（PR17 `6ea3cec9`）只勾一項：
- A. ATK Router：須先提供價格與「超限會拒絕請求」的證據。
- B. OpenRouter：新 key 並設 `limit`。
- C. OpenAI 直連：新 project，打開 enforce hard limit，並關閉自動儲值。
- D. 不 live。

另外要決定三件事：總費用上限（建議 $2）、執行環境（負責人電腦或 Claude 雲端環境）、金鑰由誰注入。

---

## 四、我接下來做的事（不等負責人）

依 PR17 R1 的 next checkpoint，接 `ATK-UPSTREAM-01` r1：
- 內容：對 Aider 與 LiteLLM 做唯讀查重，看「402／403 被重試」和「失敗仍 exit 0」是否已有上游 issue；可做本地 loopback 驗證，並備妥 issue 草稿。
- 分支 `claude/atk-aider-upstream-01`，另開新 Draft PR。
- **不送上游**：不開 issue、不留言、不開 PR。

## 五、邊界
- 本檔寫入沒有做任何 live 呼叫，也沒有碰 secrets 或帳務。
- 沒有 merge、部署、發布、招募、送上游、改 settings 或權限，也沒有新增支出。
- PR14、PR16、PR17 的內容都沒有動。
- `findings_closed_by_executor: []`。

---

## 追加（2026-09-25T20:15Z）：ATK-UPSTREAM-01 的結果

| work_id / revision | Draft PR | 精確 result head | 複核 |
|---|---|---|---|
| ATK-UPSTREAM-01 r1 | #18 | `48ea4decb3920b8a1d1fcacb92442b7a94376353` | [R1](PR18_R1_UPSTREAM_48ea4dec.md) BLOCKED（P1-01：把 #38318 寫成 open） |
| ATK-UPSTREAM-01 r2（repair 1/2） | #18 | `1abd74a4b7f14d8b5e397d33afa2ace212841099` | 待複核；收據見 [PR18 留言](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18#issuecomment-5838878694) |

- **r2 只修正 #38318 的狀態**：改為「2026-08-26 合併到 `litellm_internal_staging`」。
  - 錯誤原因：r1 引用的 Exa 頁面快照是合併前拍的，我沒有再核對第一手來源。
  - 我用唯讀 git 查到的佐證：
    - `refs/pull/38318/merge` 已不存在。
    - #38318 的改動已經包含在 LiteLLM 1.102.1，以及 main `cf491d1`。
    - 但 `_map_openai_exception` 仍然沒有處理 402／403，所以「值得對 LiteLLM 開新 issue」的結論不變。
- 兩份 issue 草稿**都沒有送出**，送出與否要負責人另外授權。本輪沒有做任何 live 呼叫，也沒有付費或 merge。

---

## 追加（2026-09-25T21:25Z）：PR18 通過；ATK-FIRST-USE-PREP-01 已交付

| work_id / revision | Draft PR | 精確 result head | 複核 |
|---|---|---|---|
| ATK-UPSTREAM-01 r2 | #18 | `1abd74a4b7f14d8b5e397d33afa2ace212841099` | [R2](PR18_R2_UPSTREAM_1abd74a4.md) APPROVED_WITH_CONDITIONS（送上游前要先修 P2-01 那一句，並取得負責人授權） |
| ATK-FIRST-USE-PREP-01 r1 | #19 | `12b807bcbbd15f3ab156248e980f3ddde3a6b5f0` | 待複核；收據見 [PR18 留言](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18#issuecomment-5839734184) |

FIRST-USE-PREP 交付內容：
- 兩份可直接發布的完整文案（上游優先的 Aider 指南、可選的 ATK 指南），**都還沒發布**。
- 入口連結全部釘在固定 SHA。
- 候選人：2 筆勉強合格、1 筆排除，建議不要逐一聯絡，**沒有聯絡任何人**。
- 回饋格式（JSON Schema）。
- 發布關卡清單，目前判定為 **NOT RELEASABLE**。
- 驗證腳本 42/42 通過。

還欠的權限：發布渠道與發送身分、PR14 合併、live 選項（`OWNER_ATK_AIDER_LIVE_DECISION`），以及是否把兩份上游草稿送出。

---

## 追加（2026-09-25T22:20Z）：PR19 R1 被擋下，已完成修復

| work_id / revision | Draft PR | 精確 result head | 複核 |
|---|---|---|---|
| ATK-FIRST-USE-PREP-01 r1 | #19 | `12b807bcbbd15f3ab156248e980f3ddde3a6b5f0` | [R1](PR19_R1_FIRST_USE_PREP_12b807bc.md) BLOCKED（P1-01、P1-02，都是回饋 schema 的漏洞） |
| ATK-FIRST-USE-PREP-01 r2（repair 1/2） | #19 | `a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41` | 待複核；收據見 [PR19 留言](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/19#issuecomment-5840366827) |

- 兩個 finding 都先重現成立，才動手修。
- 修正方式：回饋紀錄不再能自己填「通過」，改由測試結果推出來；來源版本只認網址裡的那組 SHA。
- 驗證：新寫的 17 個正／負控制全部通過，原本的驗證腳本也仍然通過。
- 這次只改了 `FEEDBACK_SCHEMA.json`。沒有聯絡任何人，也沒有發布。

---

## 追加（2026-09-26T03:20Z）：ATK-AIDER-DELIVERY-01 r1 已交付，等 GPT 複核

| work_id / revision | Draft PR | 精確 result head | 複核 |
|---|---|---|---|
| ATK-AIDER-DELIVERY-01 r1 | [#20](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/20) | `0ff12e4bfa7d18c742ce81276d62bfac19962103`（內容 head `4497e19d`） | 待複核；收據見 [PR19 留言](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/19#issuecomment-5842574775) |

- **單一入口**：`integrations/aider-atk/delivery/README.md`，8 步。從五個固定 commit 取出 12 個檔案，逐一比對 SHA-256，不必再到 PR14/16/17/18/19 各自翻找。
- **從 GitHub 全新 clone、在乾淨目錄實跑兩次**：
  - 第 1 次發現第 7 步 `git diff` exit 129（目錄不是 git repo），已修正。
  - 第 2 次每一步都符合預期；baseline 照預期失敗 `FAILED (failures=1, errors=1)`。
- **人工參考修正（副本）**：5/5 通過。**這是人寫的，不是模型結果。**
- **回饋驗證器**：拒絕 failed>total，只輸出欄位位置與錯誤類型，不回顯輸入值；單元測試 11/11 OK。
- **對照**：用 PR17 的 L2 旗標對關閉的 loopback port 跑 Aider，沒有連到任何模型。exit 0、嘗試 9 次；第 7 步仍正確判定「沒解決」。
- **live**：NOT RUN。`LIVE_HANDOFF.md` 12 個欄位已逐欄標 READY／NOT_RUN／BLOCKED_ACCESS。
- **發布**：`RELEASE_CANDIDATE.md` 判定 NOT RELEASABLE；首發建議是本 repository 的文件（R）。
- 沒有花費、發布、聯絡、merge、送上游，也沒有操作任何憑證。`findings_closed_by_executor: []`。

**藍圖位置**：S2（可用資產）的整合交付，已到檢查點 `ATK_AIDER_DELIVERY_RESULT_SHA`。後續依賴：
- GPT 複核 PR20。
- S3 `ATK-AIDER-LIVE-01`：等 `OWNER_ATK_AIDER_LIVE_DECISION`。
- S4 `ATK-FIRST-USE-01`：等 `OWNER_FIRST_USE_RELEASE_CHANNEL_AND_SENDER_DECISION`。

**同一時間寫入 main 的另一件事**：負責人指定的四節回報格式已固定為 `.claude/skills/execution-report/SKILL.md`。
- skill 本身由另一個 Claude session 在 `7257c14` 建立。
- 本次在 `AGENTS.md` 加上引用，讓 GPT 等所有 agent 都適用；並把 skill 裡不屬於本 repo 的 DeFiLab 範例改成本 repo 的範例。

---

## 追加（2026-09-26T03:20Z）：PR20 R1 BLOCKED → r2 修復完成，等 GPT 複核

| work_id / revision | Draft PR | 精確 result head | 複核 |
|---|---|---|---|
| ATK-AIDER-DELIVERY-01 r1 | [#20](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/20) | `0ff12e4bfa7d18c742ce81276d62bfac19962103` | [R1](PR20_R1_DELIVERY_0ff12e4b.md) BLOCKED（P1 ATK-D1-01：validator 會印出呼叫者給的路徑） |
| ATK-AIDER-DELIVERY-01 r2（repair 1/2） | #20 | `16b7268ed9eda98d218d7edc146eff7f740dce01`（修復 commit `4f39d343`） | 待複核；收據見 [PR20 留言](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/20#issuecomment-5842668160) |

- **重現**：finding 先重現成立。另外找到兩處同類外洩（讀不到 schema 時、參數錯誤時），一起修正。
- **修正**：紀錄只用順序稱呼（`record 1`…），任何情況都不印路徑或檔名。
- **控制**：
  - 新測試 20/20 OK；
  - 同一組測試換成舊 validator，失敗 8 個；
  - reviewer 的原始控制，標記命中 0；
  - 從 GitHub 全新 clone 驗證 `4f39d34` 也全部通過。
- **README**：只改第 8 步的預期輸出（`VALID   record 1`）。這不在 review 列的三項內，但不改入口就會錯，已註明。
- 沒有花費、發布、merge、送上游，也沒有操作任何憑證。

---

## 追加（2026-09-26T05:45Z）：負責人通過首發決定；發布候選 PR22 等 A8 覆核

| 項目 | 精確位置 | 狀態 |
|---|---|---|
| 負責人決定 | [OWNER_DECISION_2026-09-26_FIRST_USE_AND_LIVE.md](OWNER_DECISION_2026-09-26_FIRST_USE_AND_LIVE.md)（main `fcc9e1a`） | R、`firekou`、0 次聯絡；live C、$2、雲端環境 |
| 發布候選 | [#22](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/22)，head `3a681a436f12428c00e722a658b8869199a0f334` | 等 GPT 做 A8 覆核；通過後由負責人合併 |
| Live C | `integrations/aider-atk/delivery/LIVE_HANDOFF.md` | BLOCKED_ACCESS：`OPENAI_API_KEY` 為 NOT_SET，等負責人注入 |

- 通知：[PR20 留言](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/20#issuecomment-5843595623)。
- 沒有 merge、聯絡、發布、live 呼叫、花費，也沒有操作任何憑證。

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

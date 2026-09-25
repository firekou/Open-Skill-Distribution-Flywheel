# ATK distribution executor response

> 合併注意：本分支從 main `b0770499` 開，main 上還沒有這個檔案。PR14 與 PR16 各自也新增了同名檔案。合併時這幾段都要保留，不互相覆蓋。本分支只放本 work 的段落。

---

# ATK-AIDER-LIVE-PREP-01 · revision 1

| | |
|---|---|
| work_id / revision | `ATK-AIDER-LIVE-PREP-01` / 1 |
| 派工 | https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/16#issuecomment-5837510459（依 `reviews/PR16_R2_VALUE_READINESS_1dcd625d.md` 的 next checkpoint） |
| claim | https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/16#issuecomment-5837692492，2026-09-25T18:41:57Z |
| session | `session_01RFeCsTYkVywjHvXk7od7Ab`（既有 session 續作，不是持久 launcher 的證據） |
| source main | `b0770499cbef3f5917bd3505433924e0edbb8b27` |
| source readiness | PR16 `1dcd625df3bde48b13b91abb3b03eb7e19371558` |
| fixed asset | PR14 `d1474670db12934c80caa05674c8e4320cbad312` |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:ATK-AIDER-LIVE-PREP-01:1:b0770499cbef3f5917bd3505433924e0edbb8b27:executor` |
| deadline | 2026-09-26T18:25:31Z |
| repair | 0/2 |
| branch | `claude/atk-aider-live-prep-01` |

## 這份工作幫誰做什麼
讓負責人**只勾一格**就能決定要不要做第一次真實模型呼叫、用哪家、上限多少、怎麼停。勾完之後，執行者（負責人自己或 Claude）照命令跑就好，不用再查資料。

## 交付
| 檔案 | 內容 |
|---|---|
| `research/adoption/aider/LIVE_PROVIDER_OPTIONS.md` | 三個選項（ATK Router、OpenRouter、OpenAI 直連）逐項比較：base URL、模型、價格、上限範圍、警報或拒絕、超限錯誤碼、延遲、被拒是否計費；UNKNOWN 總表 |
| `research/adoption/aider/LIVE_EXECUTION_PLAN.md` | 前置、固定值、三層費用控制、實測重試暴露、停止程序、L0–L4 逐步命令（[LIVE] 全部 NOT RUN）、最壞費用公式與代入值 |
| `research/adoption/aider/LIVE_OWNER_APPROVAL_MATRIX.md` | 一頁核准表：比較、負責人要做的事、執行環境二選一、殘餘風險、只能勾一項（含「不 live」） |
| `research/adoption/aider/evidence/live-prep/sources.json` | 14 條來源：URL、observed_at UTC、原文節錄、注意事項 |
| `research/adoption/aider/evidence/live-prep/retry_exposure_harness.py` ＋ `retry_exposure/`（manifest ＋ 36 個原始檔） | loopback 重試暴露實測 |
| `research/adoption/aider/evidence/live-prep/prompt_size_probe.py` ＋ `prompt_size/`（manifest ＋ 6 個原始檔） | loopback 首個請求大小與 `max_tokens` 實測 |

兩支 `.py` 是程式，不是「去敏文字／JSON」。放在 evidence 目錄是為了讓 manifest 能重跑核對，比照 PR16 R2 對 `r2_harness.py` 的判定方式。是否接受由 reviewer 判斷；移除後 manifest 仍可獨立閱讀。

## 本批新增、可回查的事實（全部 loopback，無真實 provider）

證據等級：**TESTED**（作者自測，非獨立重現）。版本 aider 0.86.1、litellm 1.75.0、openai 1.99.1、httpx 0.28.1。

**一、一個邏輯呼叫實際送出的 HTTP 請求數**（`retry_exposure/manifest.json`，sha256 `5b34653d2bbf94ad550dd096796b5583b11449193fb977896985eacc4b50e2a3`）

| case | HTTP 請求數 | 牆鐘(秒) | exit |
|---|---|---|---|
| status_200 | 1 | 2.762 | 0 |
| status_400 | 1 | 3.027 | 0 |
| status_401 | 1 | 2.861 | 0 |
| status_402 | 9 | 66.544 | 0 |
| status_403 | 9 | 66.753 | 0 |
| status_404 | 1 | 2.732 | 0 |
| status_429 | **27** | 78.348 | 0 |
| status_500 | **27** | 78.734 | 0 |
| status_429_env_DEFAULT_MAX_RETRIES_0 | 27 | 78.433 | 0 |
| status_429_settings_max_retries_0 | **9** | 66.798 | 0 |
| status_500_settings_max_retries_0 | **9** | 66.748 | 0 |
| status_200_settings_max_retries_0 | 1 | 2.923 | 0 |

- 429 與 5xx：Aider 9 次 × OpenAI SDK 每次 3 送 = 27。PR16 的「9」確實只是下限。
- Aider 模型設定檔 `extra_params.max_retries: 0` 能壓回 9；環境變數 `DEFAULT_MAX_RETRIES=0` 無效。
- **對 PR16 已核准內容的更正**：PR16 `RELEASE_AND_ACCESS_PACKET.md` 4.2 與 `TRIAL_RUNBOOK.md` P7 寫「403 不重試」。本批在這個假端點下，403 與 402 都被 litellm 轉成 `APIError`，Aider 重試 9 次。本批不改 PR16（範圍外），請 reviewer 決定是否要 PR16 追加更正。

**二、首個請求大小與輸出上限**（`prompt_size/manifest.json`，sha256 `80df4d6f4bc21d513b4bd1baef3fbbf99601888de577b6d9d92dc7da79496231`）
- 固定任務訊息的首個請求：10 則 messages、6,056 字元，tiktoken 估約 1,400 tokens。
- **沒有設定檔時，請求不帶 `max_tokens`**，輸出只受模型上限限制。
- 加上 L2 設定檔後，請求帶 `max_tokens: 4096`；`max_retries` 不會送到 provider。

**三、讀碼（aider 0.86.1 安裝檔）**
- `base_coder.py` `max_reflections = 3`：一次 `--message` 最多 4 個主對話邏輯呼叫。
- `--auto-lint` 預設開；`--max-chat-history-tokens` 可把摘要門檻調高；`--timeout` 預設 None（`models.py` 預設 600 秒）。
- `litellm/llms/openai/openai.py` 同步路徑 `inference_params.pop("max_retries", 2)`，這可以解釋為什麼環境變數無效（推測）。

## 官方來源（摘要；完整見 sources.json）
- OpenRouter：per-key credit limit；402 = key 或帳戶額度不足；延遲與被拒計費 UNKNOWN；購點費 5.5%；`gpt-5.6-luna` 標價 $0.20／$1.20，底層最高 $0.40／$2.40。
- OpenAI：spend alert 只通知；打開 enforce 的 hard limit 回 429 `project_spend_limit_exceeded`；官方寫明非即時、可能略超；自動儲值預設開；官方明說預付餘額不能當即時上限；`gpt-5.6-luna` $0.20／$1.20（Standard 欄為推定）。
- ATK Router：只有 7 天前 PR4 review 的 endpoint 與模型實測；價格與上限能力全部 UNKNOWN。本批用 Exa 讀 aitokenking 網站逾時；從本 session 直接請求被 session 權限政策拒絕，所以沒有重驗。

## 命令與結果
| 命令 | 結果 |
|---|---|
| `python3 evidence/live-prep/retry_exposure_harness.py` | exit 0，12 cases 如上 |
| `aider-venv/bin/python evidence/live-prep/prompt_size_probe.py` | exit 0，2 variants 如上 |
| Exa `web_fetch_exa`／`web_search_exa`（OpenRouter、OpenAI、DeepSeek 官方頁） | 成功，見 sources.json |
| Exa `web_fetch_exa` aitokenking.com、api.aitokenking.com | CRAWL_TIMEOUT |
| 從本 session 直接請求 aitokenking 網域 | 被 session 權限政策拒絕，**未執行**，未嘗試繞過 |
| `LIVE_EXECUTION_PLAN.md` L1、L2 | **NOT RUN**（需要負責人核准） |

## 全程進度（S0–S7）

| 階段 | work_id | 狀態 | 依據／缺什麼 |
|---|---|---|---|
| S0 全程對齊 | — | **completed**（本表） | 讀了 main `66092a36` 上的 state rev 39、STATUS、R2 review、完整 Prompt v2.0、藍圖 §7 |
| S1 外部研究與價值差距 | ATK-VALUE-READINESS-01 | **completed**（APPROVED_WITH_CONDITIONS，PR16 `1dcd625d`） | Aider 已選定；現行需求 2 筆線索；增量仍是假說 |
| S2 可用技術資產 | ATK-AIDER-FIRST-USE-01 | **completed**（PR14 `d1474670` R2 APPROVED，離線範圍） | 未合併；真模型未驗 |
| S3 真實接入準備 | ATK-AIDER-LIVE-PREP-01 | **delivered, 待 review**（本批） | — |
| S3 真實接入 | ATK-AIDER-LIVE-01 | **gated** | 等負責人在核准表勾選並完成上限設定與金鑰注入 |
| S4 首次使用 | ATK-FIRST-USE-01 | **gated** | readiness 已過；缺邀請／渠道授權；缺 live 結果時只能標「離線驗證」 |
| S5 增量價值 | ATK-VALUE-DECISION-01 | **not started** | 缺第一階段資料；第二階段缺任務 2 |
| S6 複用與上游 | ATK-REUSE-02／ATK-UPSTREAM-01 | **not started** | REUSE 需先有外部價值。UPSTREAM 可唯讀查重備稿；本批發現的「403／402 被重試」是候選題目，但未查重、未備稿、不送 |
| S7 持續運作 | ATK-SUSTAIN-01 | **not started** | 需完整觀察窗口 |

**下一 gate**：GPT 覆核本批 → 負責人在 `LIVE_OWNER_APPROVAL_MATRIX.md` 勾一項 → 另開 `ATK-AIDER-LIVE-01`。
**不需等負責人、可接續的無依賴準備**：ATK-UPSTREAM-01 的唯讀查重（403／402 重試行為是否已有上游 issue）。本批沒做，留待派工。

## 未測／UNKNOWN
真實 provider 的任何行為；被拒請求是否計費（兩家）；OpenRouter 上限延遲；ATK 價格與上限；`gpt-5.6-luna` 是否接受 `max_tokens`；真實 provider 送 `Retry-After` 時的等待時間；`--max-chat-history-tokens 65536` 確實讓摘要不觸發（僅讀碼）；多回合時的實際 prompt 成長；各模型真實 tokenizer。

## 邊界
沒有 live 呼叫、沒有讀或改 secrets、沒有登入帳務、沒有建 key 或 project、沒有招募、邀請、發布、About/topics、merge、部署，沒有改 settings 或權限、沒有送上游、沒有付費、沒有 polling。PR16 與 PR14 都沒修改。
`findings_closed_by_executor: []`。停在 Draft PR 等獨立覆核。

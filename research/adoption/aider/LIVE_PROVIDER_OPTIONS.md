# Live 選項：三個 provider／runtime
work_id：ATK-AIDER-LIVE-PREP-01 · revision 1 · 交付 1/3
source main：`b0770499cbef3f5917bd3505433924e0edbb8b27`；readiness：PR16 `1dcd625df3bde48b13b91abb3b03eb7e19371558`；固定資產：PR14 `d1474670db12934c80caa05674c8e4320cbad312`
狀態：**準備文件。本批沒有呼叫任何真實 provider、沒有讀任何金鑰或帳務頁、沒有花錢。**

來源索引：`evidence/live-prep/sources.json`（每條附 URL、observed_at UTC、原文節錄）。官方沒寫的一律記 **UNKNOWN**，不推測。

---

## 一、怎麼選出這三個

條件：能走 Aider 的 OpenAI 相容路徑（`openai/<model>` ＋ `OPENAI_API_BASE`），也就是 PR14 資產教的那條路。

| 候選 | 結果 | 理由 |
|---|---|---|
| **ATK Router** | 列入 | 藍圖要求「能核對就列 ATK」。endpoint 有 7 天前的 reviewer 實測；價格與上限能力 UNKNOWN |
| **OpenRouter** | 列入 | 官方文件有**單把 key 的額度上限**，用完回 402 |
| **OpenAI 直連** | 列入 | 官方文件有 **project 級硬上限**，到達回 429 |
| DeepSeek | 不列 | 讀到的文件只有帳戶層級的預付餘額（402），沒找到 key 或 project 級上限。為了維持三個以內而排除 |

三個選項都用同一個模型比較方便：OpenAI 與 OpenRouter 都有 `gpt-5.6-luna`（兩邊標價相同）。ATK 沒有查到這個模型名，用 PR4 實測過的 `claude-sonnet-4.6`。**模型由負責人最後決定**，這裡只提供有官方價格可引用的預設。

---

## 二、逐項比較

| 項目 | ATK Router | OpenRouter | OpenAI 直連 |
|---|---|---|---|
| OpenAI 相容 base URL | `https://api.aitokenking.com.tw/api/v1`（PR4 review，2026-09-18 實測；本批未重驗） | `https://openrouter.ai/api/v1` | `https://api.openai.com/v1` |
| 建議模型 | `claude-sonnet-4.6`（PR4 當時可用；現況 UNKNOWN） | `openai/gpt-5.6-luna` | `gpt-5.6-luna` |
| Aider `--model` | `openai/claude-sonnet-4.6` | `openai/openai/gpt-5.6-luna` | `openai/gpt-5.6-luna` |
| 價格（每 1M tokens，輸入／輸出） | **UNKNOWN** | 標價 $0.20／$1.20；依路由到的底層 provider 不同，列表中最高 $0.40／$2.40（OpenAI Fast） | $0.20／$1.20（推定為 Standard 欄；頁面分頁標籤在擷取時遺失，見 sources.json） |
| 其他費用 | UNKNOWN | 購買 credits 收 5.5%（最低 $0.80） | 無另計（本批讀到的範圍內） |
| 付款方式 | UNKNOWN | 預付 credits | 預付 credits（新帳戶預設）；**自動儲值預設開啟** |
| 上限的範圍 | UNKNOWN | **單把 key**（`limit`，可設每日／週／月重置）＋帳戶餘額 | **project**（也可設 organization） |
| 警報型或拒絕型 | UNKNOWN | **拒絕型**：key 或帳戶額度不足回 402 | 兩種都有：只設 spend limit 是**警報型**；打開「Enforce a hard limit」才是**拒絕型** |
| 超限的 HTTP 錯誤 | UNKNOWN | **402** | **429**，`error.code = project_spend_limit_exceeded` |
| 生效延遲 | UNKNOWN | **UNKNOWN**（讀到的文件沒寫） | 官方明寫**非即時**，「recorded spend can slightly exceed the configured amount」 |
| 被拒的請求是否計費 | UNKNOWN | **UNKNOWN**。另有一句：即使沒產生內容，上游仍**可能**收 prompt 處理費 | **UNKNOWN** |
| 預付餘額能否當上限 | UNKNOWN | 帳戶餘額為負時會報錯；延遲 UNKNOWN | 官方明寫：**「Do not rely on the prepaid balance as an instantaneous spending cutoff.」** |
| 能通過 G0（`TRIAL_RUNBOOK.md`）嗎 | **不能**，除非負責人從 ATK 營運端提供上限能力的證據 | **能**：key 級拒絕型上限 | **能**：project 級拒絕型上限（必須打開 enforce） |

---

## 三、這些上限碰上 Aider 會怎樣（本機實測）

本批用 loopback 假端點，讓它對每個請求固定回同一個 HTTP 狀態，數 Aider 實際送出幾個 HTTP 請求。證據在 `evidence/live-prep/retry_exposure/manifest.json`（逐 case 有命令、版本、起迄、exit、原始輸出雜湊）。

| 假端點回的狀態 | 對應哪個真實情境 | Aider 送出的 HTTP 請求數 | 加 `max_retries: 0` 後 |
|---|---|---|---|
| 200／400／401／404 | 正常／參數錯／金鑰錯／路徑錯 | 1 | 200 仍是 1 |
| **402** | **OpenRouter key 額度用完** | **9** | 未測 |
| **403** | 權限不足 | **9** | 未測 |
| **429** | **OpenAI project 硬上限到了**（也是一般限流） | **27** | **9** |
| 500 | 伺服器錯誤 | **27** | **9** |

**這代表：**
1. **上限到了，Aider 不會馬上停。** OpenRouter 的 402 會被 Aider 重試 9 次；OpenAI 的 429 會被 Aider 重試 9 次，底層 OpenAI SDK 每次再重送 2 次（litellm 1.75.0 `DEFAULT_MAX_RETRIES = 2`），共 27 個請求。被拒的請求是否計費，兩家文件都沒寫（UNKNOWN）。
2. **PR16 的一句話要更正**：PR16（已核准）的 `RELEASE_AND_ACCESS_PACKET.md` 4.2 與 `TRIAL_RUNBOOK.md` P7 寫「403 不重試」。本批實測在 litellm 1.75.0 下，這個假端點回的 403 被轉成 `litellm.APIError`，Aider 照樣重試。本批不改 PR16（範圍外），列為交 reviewer 的更正項。
3. **「每個邏輯呼叫 9 次」不是費用上限。** 429 與 5xx 類錯誤實際是 9 × 3 = 27 個 HTTP 請求。
4. **可以壓回 9**：在 Aider 模型設定檔加 `extra_params.max_retries: 0`，實測 429、500 都降為 9。環境變數 `DEFAULT_MAX_RETRIES=0` 則**無效**（仍 27）。

---

## 四、每個選項還缺什麼才能 live

| 選項 | 缺的東西 | 誰能補 |
|---|---|---|
| ATK Router | 價格、上限範圍、警報或拒絕、超限錯誤碼、被拒是否計費；base URL 與模型的現況 | 負責人（ATK 營運端）提供官方文件或後台說明 |
| OpenRouter | 上限生效延遲、被拒是否計費（可接受為殘餘風險）；核准當天重讀模型頁價格 | 負責人建 key 並設 `limit` |
| OpenAI 直連 | 被拒是否計費（可接受為殘餘風險）；確認 `gpt-5.6-luna` 可走 Chat Completions；核准當天確認價格分頁 | 負責人建 project、打開 enforce hard limit、**關掉自動儲值** |

---

## 五、UNKNOWN 總表
- ATK：價格、上限能力全部、base URL 與模型的現況。
- OpenRouter：key 額度的生效延遲、被拒請求是否計費、預設路由會不會落到較貴的底層 provider（最壞以 $0.40／$2.40 估）。
- OpenAI：被拒請求是否計費、生效延遲的具體長度、`gpt-5.6-luna` 是否接受 `max_tokens` 參數（新型推理模型可能要求 `max_completion_tokens`；錯了會回 400；實測 400 不重試，只送 1 個請求，被拒請求是否計費 UNKNOWN——見執行計畫 L1）。
- 全部：各模型的實際 tokenizer（本批 token 數用 tiktoken 估算）。

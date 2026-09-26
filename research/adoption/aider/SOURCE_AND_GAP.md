# 來源與增量差距：Aider 原生直用 vs PR14
work_id：ATK-VALUE-READINESS-01 · **revision 2** · 交付 1/5
source main：`60dbdff09d14da493ee0d65de364a9b72e7b8321`；本修正 source_head `57fa50900035cb6eef316504b065cf98a8b4fee0`
Aider 固定來源：PR14 head `d1474670db12934c80caa05674c8e4320cbad312`；上游讀碼 `Aider-AI/aider@5dc9490bb35f9729ef2c95d00a19ccd30c26339c`；執行版本 `aider-chat 0.86.1` ＋ `litellm 1.75.0`
查閱日期：2026-09-25 UTC

> **revision 2 更正**：revision 1 把 #4027 寫成「頁面上未見維護者回覆或修正 PR」，並拿它當「現行需求」。兩點都錯。見第四節。

## 一、沿用既有三候選結論，不重選
`research/ATK_THREE_TOOL_VALUE_REVIEW_2026-09-24.md` 已裁決 Aider 優先、Continue 候補、Open WebUI 暫不實作；藍圖第 4 節明訂不重挑。本文件不重開。

## 二、官方直用路徑（原文，https://aider.chat/docs/llms/openai-compat.html）
```
export OPENAI_API_BASE=<endpoint>
export OPENAI_API_KEY=<key>
aider --model openai/<model-name>
```
另兩句：模型名要加 `openai/` 前綴；對不熟悉的模型會出 model warnings。

**判讀：官方路徑已足以讓仔細的人接上端點。PR14 沒有提供官方沒有的接入能力。**

## 三、PR14 相對官方多出什麼

| 項目 | 官方有寫 | PR14 | 證據 |
|---|---|---|---|
| 三個環境變數、`openai/` 前綴 | 有 | 相同 | — |
| `OPENAI_API_BASE` 給根位址，路由由底層接 | **沒寫** | 有 | TESTED：r2 manifest，三種設定方式都送到 `/v1/chat/completions` |
| `openai/` 前綴不會送到端點 | **沒寫** | 有 | TESTED：r2 manifest 的 `observed_models` 為 `local-test-model` |
| 加 `--no-analytics --no-check-update` 仍連外抓價格表 | **沒寫** | 有 | OBSERVED（PR14 證據） |
| 離線設定檢查器 | 無 | 有 | REPRODUCED：GPT R2 獨立重跑 11/11 |
| 有固定評分測試的最小任務 | 無 | 有 | REPRODUCED：GPT R1 重跑 baseline |

**增量是「診斷」，不是「接入」。**

旁證（第三方、不同工具、不是需求證據）：dev.to〈How to Configure a Custom LLM Proxy in OpenOPC〉（2026-08-04）獨立寫道「When you use the openai/ prefix, LiteLLM strips it off before sending the request」，與 PR14 的量測一致。

## 四、公開需求：先更正 #4027，再記現行需求搜尋

### 4.1 Aider-AI/aider #4027 —— **歷史案例，不是現行需求**
完整時間線存於 `evidence/r2_issue_4027_timeline.md`（sha256 `0757b111…`）。重點：

| 日期 | 誰 | 內容 |
|---|---|---|
| 2025-05-15 | psymonryan（回報者） | 0.83.1 用設定檔 `openai-api-base: …/v1`，請求變成 `POST /chat/completions` → 404 |
| 2025-05-22 | Axenide | 同類問題，改用命令列 export 可繞過 |
| 2025-06-01 | psymonryan | 根因追到 aider 0.82.2→0.82.3 間 litellm 1.65.7→1.68.0；1.68.0 以 `OPENAI_BASE_URL` 為新標準變數；提出 patch |
| — | — | 被 **PR #4144**〈fix: Restore full base path at api endpoint for litellm >= 1.68.0〉引用 |
| — | paul-gauthier（維護者） | 加上 `priority` 標籤 |
| **2025-09-19** | **psymonryan** | **「I'm no longer able to reproduce this issue on v0.86.1, hence closing.」並自行關閉** |

**revision 1 錯在哪、為什麼錯：** revision 1 用的網頁擷取只拿到 issue 本文，時間線與留言根本沒載入，而我沒察覺缺了這一段，就寫下「未見維護者回覆或修正 PR」。實際上維護者有動作、有修正 PR、回報者本人在 0.86.1 確認消失並關閉。

**正確分類：** 已解決的歷史設定失敗案例。它證明「base path 設錯時使用者只拿到一句 404，看不出原因」這類診斷困難**曾經**真實發生，但**不能**當成 0.86.1 的現行缺陷或未滿足需求。
本輪在 0.86.1 重現不出來（r2 manifest 三個 case），與回報者自己的結論一致。
**尚不知道：** PR #4144 是否合併、修正落在 aider 還是 litellm。固定來源 `5dc9490` 的 `main.py:620-621` 只設 `OPENAI_API_BASE`，沒設 `OPENAI_BASE_URL`，所以修正位置不做任何主張。

### 4.2 現行需求搜尋紀錄
**範圍與條件：** 找「仍開放、aider 0.86.x、與檢查器三類（缺值／前綴／根位址帶路由）直接相關」的公開回報。
**時間：** 2026-09-25T18:17Z 前後。**不是系統性搜尋**，是 3 組定向查詢；搜不到不代表沒有。

| # | 工具 | 查詢 |
|---|---|---|
| Q1 | WebSearch | `aider "openai/" model prefix OPENAI_API_BASE 404 "chat/completions" error openai compatible`（revision 1） |
| Q2 | Exa search | Aider-AI/aider 開放 issue：OpenAI 相容端點設定失敗、0.86 |
| Q3 | Exa search | aider `openai/` 前綴混淆、「LLM Provider NOT provided」、2025-09 以後 |
| — | Exa fetch | 對候選 issue 取完整頁（含時間線），確認狀態與版本 |

**納入（2 筆，都是需求線索，不是增量證明）：**

| issue | 狀態 | 版本 | 使用者寫的 | 檢查器對它的反應（r2 manifest） | 限制 |
|---|---|---|---|---|---|
| **#4797**〈enable z.ai GLM 4.7 with aider〉2026-01-25 | **open** | **0.86.1** | `--model zai/glm-4.7` → `LLM Provider NOT provided` | exit 3，指出 `zai/` 會走該 provider 自己的路由、不用 `OPENAI_API_BASE`，建議 `openai/glm-4.7` | 另一位使用者說照 `openai/` 做仍失敗；**他貼的錯誤訊息仍顯示 `model=zai/glm-4.7`**，可見那次前綴並沒有改成功。另有一則留言是第三方產品維護者推銷自家轉接工具，屬利害關係人 |
| **#4638**〈Unhelpful documentation to "LLM Provider not provided"〉2025-11-12 | **open** | **0.86.1** | `--model local/qwen3-coder:30b`；又搞不清 base 要不要帶 `/v1` 或結尾 `/` | exit 3，指出 `local/` 不是 `openai/`，建議 `openai/qwen3-coder:30b` | 回報者最後改走 **Ollama 原生**（`ollama_chat/` ＋ `OLLAMA_API_BASE`），**我們的 Quick Start 不涵蓋那條路**。檢查器也**不會**告訴他要不要帶 `/v1` |

**排除（附理由）：**

| 來源 | 排除理由 |
|---|---|
| #4027 | 已由回報者在 0.86.1 確認消失並關閉（見 4.1） |
| #4685 PublicAI（2025-12, 0.86.1） | 根因是 litellm 缺 provider 支援（litellm #17218），不是使用者設定錯誤 |
| #4109 Vertex AI | 非 OpenAI 相容路徑；0.83.x |
| #3097、#2031、#1834 | 2024–2025 初；是模型權限／帳號等級問題，不是設定 |
| #3160 | 2025-02；文件用詞討論，維護者回覆 `OPENAI_API_*` 仍正確 |
| #2710（2024-12）、#2442（0.64.1） | 版本過舊，歸為歷史案例。#2710 把完整端點路徑填進 base，正是檢查器第三類，但只能當歷史佐證 |
| apisrouter.com〈for-aider〉(2026-07) | **商業轉接服務自己的頁面**，有利害關係。它把「漏掉 `openai/` 會被誤判成金鑰問題」寫成常見陷阱，可以當作陷阱被廣泛認知的旁證，**不算使用者需求** |
| dev.to OpenOPC | 不同工具；只當第三節的旁證 |

**結論：現行需求證據 = 2 筆需求線索**，都落在「前綴寫成別家 provider」這一類，檢查器對這兩個原字串都會攔下並給出建議。
**這不等於檢查器能幫到他們**：沒有任何一位回報者用過它，#4638 的人最後走的路我們沒涵蓋，#4797 還有人照做仍失敗。要證明增量，只能靠第 S5 階段的實際試用。
**第三類（根位址帶路由）目前沒有現行需求證據，記 0**，只有歷史案例。

## 五、差距裁決
**薄接入（文件＋離線檢查器），不做 adapter。** 官方直用已可運作；增量是診斷；現行需求有 2 筆線索集中在前綴一類。
**增量仍是假說。** S4 的第一批外部試用因此定位為「可行性與卡點探索」，不回答 A/B 增量（見 `STUDY_PROTOCOL.md`）。

**反證條件（任一成立就改推薦官方文件）：**
1. 試用者照官方文件同樣順利，沒遇到設定錯誤。
2. 試用者碰到的錯誤不在檢查器三類之內（#4638 的 Ollama 原生路線就是一例）。
3. 官方文件補上根位址與前綴兩項說明。
4. 維護這份文件的成本高於它省下的排錯時間。

## 六、未覆蓋範圍
未讀 aider 全部 issue；未查 Continue、Open WebUI 同類問題；未比對 0.83.1→0.86.1 程式差異；未確認 PR #4144 合併狀態；未跑任何真實模型；Windows/macOS 未測；未查 Ollama 原生路線。

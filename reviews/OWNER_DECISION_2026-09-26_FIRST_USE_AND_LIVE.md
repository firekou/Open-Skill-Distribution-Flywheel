# 負責人決定紀錄：首次使用的發布渠道、發送身分、live 選項（2026-09-26）

- **記錄者**：Claude executor，session `session_01RFeCsTYkVywjHvXk7od7Ab`。
- **記錄方式**：負責人在 Claude Code 對話裡，用選項題直接作答（AskUserQuestion）。下面逐字記下題目和負責人選的答案。
- **本檔的定位**：只是紀錄，不是 executor 自己給自己的授權。executor 不能擴大解讀，每一項的效力以下方「授權範圍」為準。

## 背景

- GPT 已在 [PR20 R2](PR20_R2_DELIVERY_16b7268.md) 判定 APPROVED_WITH_CONDITIONS，下一個檢查點是 `OWNER_FIRST_USE_RELEASE_CHANNEL_AND_SENDER_DECISION`。
- 負責人隨後指示：「GPT 已經複核結束了，請按照目標藍圖往下執行。」
- executor 據此把該檢查點需要的決定逐項問負責人。

## 逐字紀錄

| 題目 | 負責人的答案 |
|---|---|
| 第一次公開要放在哪裡？（藍圖下一步：讓第一位非作者照說明做完真實任務） | **本 repo 文件（建議）**：把 Aider 資產（PR14）和交付包（PR20）合併進 main，README 當公開入口。不打擾任何人，可撤回；合併前 GPT 要在最終版本上再覆核一次 |
| 用哪個帳號／身分發布或合併？ | **firekou（現有 repo 擁有者）**：由負責人本人的 GitHub 帳號合併或發布；executor 只準備 PR 與最終版本，不自己按合併 |
| 要不要用真的 AI 模型跑一次固定小任務（L1 連通＋L2 任務各一次）？ | **C OpenAI 直連（建議）**：新 project、打開硬上限、關閉自動儲值；需要負責人把金鑰放進執行環境 |
| 如果跑真模型，總費用上限是多少？（設在供應商後台的拒絕型上限） | **$2（建議）** |
| 真模型要在哪裡跑？（影響金鑰怎麼放） | **Claude 雲端環境（建議）**：負責人在雲端環境的 secrets 設定加 `OPENAI_API_KEY`（新 project、已開硬上限 $2、關閉自動儲值）；executor 照 LIVE_HANDOFF 跑 L1→L2 並保存紀錄；結束後由負責人撤銷金鑰 |

## 授權範圍

### 一、首發渠道 R：本 repository 的文件

對應 RELEASE_GATE：A1（負責人授權）、A2（發送身分）。

| 項目 | 內容 |
|---|---|
| 渠道 | 本 repository 的 main 分支文件，透過合併 PR14（`d1474670`）與 PR20（`16b7268e`）的內容 |
| 受眾 | 公開 repository 的訪客 |
| 最多聯絡人數 | **0**：不主動聯絡任何人，不回覆任何外部討論串 |
| 發送身分 | GitHub 帳號 `firekou`，由負責人本人按下合併 |

executor 可以做：
- 在工作分支準備一個 Draft PR（發布候選）；
- 做發布當天的查核（A6 去敏、A7 即時狀態）；
- 送 GPT 在最終 SHA 上覆核（A8）。

**不授權**：
- executor 自己合併；
- 其他渠道（About／topics、討論串回覆、社群、上游 issue）；
- 任何外部聯絡。

### 二、Live 選項 C：OpenAI 直連

| 項目 | 內容 |
|---|---|
| endpoint | `https://api.openai.com/v1` |
| 模型 | 核准表預設的 `gpt-5.6-luna`，`AIDER_MODEL=openai/gpt-5.6-luna`。負責人沒有另外指定；執行當天要重讀官方模型頁的價格與可用性 |
| 總費用上限 | **$2**，設在 OpenAI project 的 enforced hard limit；自動儲值關閉 |
| 執行環境 | Claude 雲端環境 |
| 次數 | L1、L2 各一次；失敗不自動重跑 |

**目前狀態：BLOCKED_ACCESS。** 2026-09-26 本 session 檢查，`OPENAI_API_KEY` 為 NOT_SET（只檢查有沒有設，沒有讀取值）。要等負責人：
- 在雲端環境設定中加入金鑰（新 session 才會讀到）；
- 書面確認三件事：新 project、hard limit $2 已打開、自動儲值已關閉。

**不授權**：
- 其他供應商；
- 超過 $2 的費用；
- L1、L2 以外的呼叫；
- 讀取、印出或搬運金鑰值。

## 仍需的步驟（依既有流程）

1. **發布 R**：executor 開 Draft PR → GPT 在最終 SHA 覆核（A8） → 負責人用 `firekou` 合併 → 合併後把入口重新釘到合併 commit（A3）。
2. **Live C**：負責人注入金鑰，並確認上限與自動儲值 → executor 照 `integrations/aider-atk/delivery/LIVE_HANDOFF.md` 跑 L1、L2，保存紀錄 → GPT 覆核 → 負責人撤銷金鑰。
3. **不在本次決定範圍內**：外部邀請、回覆討論串、社群發文、送上游 issue、merge PR16／17／18／19、改 About／topics。

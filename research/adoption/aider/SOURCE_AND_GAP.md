# 來源與增量差距：Aider 原生直用 vs PR14
work_id：ATK-VALUE-READINESS-01 · revision 1 · 交付 1/5
source main：`60dbdff09d14da493ee0d65de364a9b72e7b8321`
Aider 固定來源：PR14 head `d1474670db12934c80caa05674c8e4320cbad312`；上游讀碼 `Aider-AI/aider@5dc9490bb35f9729ef2c95d00a19ccd30c26339c`；執行版本 `aider-chat==0.86.1`
查閱日期：2026-09-25 UTC

## 一、沿用既有三候選結論，不重選
`research/ATK_THREE_TOOL_VALUE_REVIEW_2026-09-24.md` 已裁決：Aider 優先、Continue 候補、Open WebUI 暫不實作。藍圖第 4 節也明訂「現有 Aider 是第一項，不重挑三個來取代已完成工作」。本文件不重開這個選擇。

## 二、官方直用路徑（原文，2026-09-25 讀取 https://aider.chat/docs/llms/openai-compat.html）
```
export OPENAI_API_BASE=<endpoint>
export OPENAI_API_KEY=<key>
aider --model openai/<model-name>
```
官方另有兩句：模型名稱要加 `openai/` 前綴；對 aider 不熟悉的模型會出現 model warnings。

**判讀：官方路徑已經足夠讓一個仔細的人接上端點。** PR14 並沒有提供官方沒有的「接入能力」。

## 三、PR14 相對官方多出什麼（逐項，附證據等級）

| 項目 | 官方文件有沒有寫 | PR14 | 證據 |
|---|---|---|---|
| 三個環境變數、`openai/` 前綴 | 有 | 相同 | — |
| `OPENAI_API_BASE` 要給**根位址**，路由由底層接 | **沒寫** | 有 | OBSERVED：0.86.1 本機錄到 `/v1/chat/completions` |
| `openai/` 前綴**不會送到**端點，端點認得的是後半段 | **沒寫** | 有 | OBSERVED：送出 `model` 欄位為 `local-test-model` |
| 加了 `--no-analytics --no-check-update` 仍會連外抓價格表 | **沒寫** | 有 | OBSERVED：連 `raw.githubusercontent.com` |
| 離線設定檢查器（分辨缺值、前綴錯、根位址錯） | 無 | 有 | TESTED：11 項測試＋變異控制；GPT R2 獨立重跑 |
| 有固定評分測試的最小任務 | 無 | 有 | REPRODUCED：GPT 重跑 baseline 3 過 1 失敗 1 錯誤 |

**所以增量是「診斷」，不是「接入」。** 官方文件告訴你怎麼設；PR14 多告訴你設錯的時候錯在哪。

## 四、公開需求與反例（本輪新查）

### 找到的：Aider-AI/aider #4027（已關閉，2025-05-15 開）
標題：「aider-chat > 0.82.2 sends incorrect base path to openai compatible endpoints」
- 回報者用**設定檔** `.aider.conf.yml`：`openai-api-base: http://192.168.5.144:8012/v1`
- 0.82.2 正常：`POST /v1/chat/completions 200`
- 0.83.1 壞掉：`POST /chat/completions 404`，錯誤訊息是 `NotFoundError: OpenAIException - 404 page not found`
- 讀取時頁面上未見維護者回覆或修正 PR（單次擷取，未二次驗證）

**這是真實需求的證據，而且落在我們聲稱有增量的同一個點上**：回報者收到的只有「404 page not found」，沒有任何訊息告訴他是路徑錯。這正是 PR14 檢查器想補的那一塊。

### 表面上它和我們的量測矛盾，所以本輪直接測了
PR14 在 0.86.1 用**環境變數**量到路徑正確；#4027 用**設定檔**在 0.83.1 量到路徑錯。只測過一條路徑的話，這個矛盾解不開。

本輪在 0.86.1 對三種設定方式各跑一次本機錄製（假端點與範例檔從 PR14 固定 head 唯讀取出，md5 `a26adf4c…` / `da2b54d9…`）：

| 設定方式 | 設的值 | 錄到的路徑 |
|---|---|---|
| 環境變數 `OPENAI_API_BASE` | `http://127.0.0.1:8821/v1` | `/v1/chat/completions` |
| 參數 `--openai-api-base` | `http://127.0.0.1:8822/v1` | `/v1/chat/completions` |
| 設定檔 `.aider.conf.yml`（#4027 的原樣寫法） | `http://127.0.0.1:8823/v1` | `/v1/chat/completions` |

**結論：#4027 在 0.86.1 NOT REPRODUCED，三種方式都正確。** 原始紀錄在 `evidence/base_path_*.json`。
**我沒找到修正它的 commit 或 release note**，所以只能說「0.86.1 重現不出來」，不能說「某版已修好」。

### 本輪第一次跑失敗了，照實記下
第一輪三個 case 全部 `NO_REQUEST_LOG`：這條分支從 main 開，PR14 未合併，假伺服器檔根本不存在，伺服器沒起來。**aider 仍回 exit 0。** 我改成從 PR14 固定 head 唯讀取檔、並在每個 case 前先確認伺服器程序活著，才得到上表。第一輪結果不採用。

### 沒找到的
- 定向搜尋只有 #4027 一筆直接相關。Planner 先前以 `repo:Aider-AI/aider is:issue "api_base"` 搜尋前 5 筆也無結果。
- **這不是系統性搜尋**，搜不到不代表沒有；也無法得知有多少人碰到同類問題而沒回報。
- 找不到任何第三方比較「照官方文件」與「照某份指引」首次成功時間的資料。

## 五、差距裁決
**薄接入（文件＋離線檢查器），不做 adapter。** 理由：官方直用已可運作；PR14 的增量是診斷，且有一筆真實回報落在同一個痛點上。

**增量仍是假說，尚未量測。** 要成立需要第 S5 階段的配對資料（見 `STUDY_PROTOCOL.md`）。

**反證條件（任一成立就改推薦官方文件）：**
1. 配對試用中，只看官方文件的人同樣順利，沒遇到設定錯誤。
2. 使用者碰到的錯誤不在檢查器涵蓋的三類之內（缺值、前綴、根位址）。
3. 官方文件補上根位址與前綴兩項說明。
4. 維護我們這份文件的成本高於它省下的排錯時間。

## 六、未覆蓋範圍
未讀 aider 全部 issue、未查 Continue 與 Open WebUI 的同類問題、未比對 0.83.1 到 0.86.1 的程式差異、未跑任何真實模型、Windows/macOS 未測、設定檔在 Windows 路徑下的行為未測。

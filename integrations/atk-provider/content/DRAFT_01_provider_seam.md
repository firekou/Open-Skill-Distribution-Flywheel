---
status: DRAFT — 未發布。發布需另行授權（reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md §5）
asset: integrations/atk-provider/
claims_requiring_evidence: none（本文不宣稱省錢或品質提升）
---

# 你的 Agent 不該知道自己在跟誰講話

## 一個很常見的下場

你寫了一個 skill。它跑得很好，因為你在裡面 `import openai`。

三個月後：客戶要求資料不出境、你想用便宜的模型跑批次、某家供應商當機兩小時。每一件事都要你改程式碼，而那行 `import` 已經散在十七個檔案裡。

這不是供應商的問題，是**接縫**的問題。你的 skill 知道了它不該知道的事。

## 一個檔案的解法

ATK 的 `ATK_ROUTING_INTEGRATION.md` 早就寫下這個接縫的規格，但一直沒有實作。我們把它補上了，**一個檔案、只用標準函式庫、沒有任何依賴**：

```python
from atk_provider import Message, complete

c = complete([
    Message("system", "你很簡潔。"),
    Message("user", "一句話解釋什麼是 context window。"),
])
print(c.text)
print(c.provider, c.model, c.usage.total_tokens)   # 誰真的服務了這一次
```

這就是全部的 API。你的程式碼**不再 import 任何廠商 SDK**。

換供應商是 `.env` 裡的一行：

```bash
PROVIDER=openai     # 或 anthropic / deepseek / qwen / openrouter / custom
```

`PROVIDER=custom` 可以指向**任何 OpenAI 相容的 host**——閘道、代理、你自己跑的本地模型。

## 四條規矩，每一條都有測試

ATK 的規格寫了一句話，我們把它當成驗收條件：

> **ATK 可以是預設，但永遠不可以是唯一。**

| 規矩 | 怎麼驗的 |
|---|---|
| **看得見** | 每次回應都帶 `provider`，範例每跑一次就印出來 |
| **換得掉** | 同一段程式、同一個呼叫，靠環境變數送到兩台不同伺服器，兩邊各自驗證收到什麼 |
| **寫清楚** | README 的「怎麼換掉 ATK」放在顯眼位置，不是附錄 |
| **可移除** | 把所有 `ATK_*` 變數拿掉、`PROVIDER=openai`，整個東西照常運作——這是一條測試，不是一句保證 |

第四條最容易嘴上說說。所以它是 `TestOptional.test_it_runs_with_no_atk_variables_at_all`。

## 幾個刻意的設計決定

**沒有回報成本，就是 `None`，不是 `0.0`。**
把「沒告訴我」寫成 `0`，讀起來像「這次免費」。這兩件事差很多。

**設定不完整，在送出請求前就失敗。**
少一個 `ATK_MODEL`，你會立刻看到少了哪一個變數，而不是等 HTTP 400 回來再猜。測試斷言了伺服器收到**零**個請求。

**不認得的 `PROVIDER` 直接拒絕，不會退回預設值。**
打錯字就靜靜送到別家去，是我們不想要的那種貼心。

**4xx 不重試。**
第三次還是會 400。重試只是浪費你的時間。5xx 才重試，然後換下一家。

**沒設定的 fallback 是跳過，不是重試。**
少的那把 key，第三次還是會少。

**最後的錯誤訊息會列出每一家試過什麼、為什麼失敗。**
「所有供應商都失敗」這種訊息沒有人能拿來 debug。

## 老實說有什麼沒做

- **沒有跟真的 ATK 連過。** 環境裡沒有憑證，而且 `api.aitokenking.com` 在我們的網路上**解不出 DNS**——同一個 shell 裡 `api.openai.com` 解得出來，所以不是整體封鎖。可能是出口政策，也可能是文件裡的位址不對。我們沒有替它決定，全部記在 `VERIFICATION.md`。
- **沒有任何省錢或品質主張。** 這個檔案只負責把請求送出去。它不壓縮、不快取、不優化。
- **沒有 streaming、tool call、batch。**
- **預算上限沒實作。** 規格文件裡有 `TOKEN_BUDGET_PER_RUN`，我們**沒做**，而且明講沒做，而不是收下參數然後忽略它。

14 個測試跑在**真的 HTTP 伺服器**上——真的 socket、真的請求、真的解析。合成的是「供應商」，不是傳輸層。

## 拿去用

```bash
cd integrations/atk-provider
python3 example_summarise_tool_output.py --dry-run --file build.log
```

`--dry-run` 印出**會送出什麼**，然後什麼都不送。不需要憑證。在花任何錢之前，先看清楚它要做什麼。

---
*程式碼：`integrations/atk-provider/`。Apache-2.0 相容，只用標準函式庫。*

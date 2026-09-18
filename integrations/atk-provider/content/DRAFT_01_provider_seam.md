---
status: DRAFT — 未發布。發布需另行授權（reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md §5）
asset: integrations/atk-provider/
claims_requiring_evidence: none（本文不宣稱省錢或品質提升）
live_evidence: ATK 單次 chat 由 PR #4 reviewer 實測，使用**負責人提供並授權**的憑證（非 reviewer 自有帳號）；本文作者未跑過真實 ATK
---

# 三分鐘接上 ATK，而且隨時換得掉

## 先講最短路徑

如果你的客戶端支援 MCP，**你不需要任何程式碼**：

```json
{
  "mcpServers": {
    "aitokenking": {
      "url": "https://api.aitokenking.com.tw/mcp",
      "headers": { "X-Aitokenking-Api-Key": "${AITOKENKING_API_KEY}" }
    }
  }
}
```

key 從環境變數讀，不要寫進會 commit 的檔案。設定格式各家客戶端略有不同，以你的為準。

如果你在寫 Python、而且不想被單一供應商綁住，才需要看下去。

## OpenAI 相容端點

ATK 提供 OpenAI 相容 API，所以你原本的程式幾乎不用改：

```bash
ATK_BASE_URL=https://api.aitokenking.com.tw/api/v1
```

先確認你的 key 能看到哪些模型（撰稿時是 52 個）：

```bash
curl -s https://api.aitokenking.com.tw/api/v1/models \
  -H "Authorization: Bearer $ATK_API_KEY" | python3 -m json.tool | head
```

> **變數名稱有兩種寫法。** 官方文件叫 `AITOKENKING_API_KEY`，我們的接入契約叫 `ATK_API_KEY`。**兩個都吃得下**，貼哪一個都行——但不要兩個都設成不同的值。

## 為什麼還要一層接縫

你寫了一個 skill，裡面 `import openai`。三個月後：客戶要資料不出境、你想用便宜模型跑批次、某家供應商當機兩小時。每一件事都要改程式，而那行 import 已經散在十七個檔案裡。

這不是供應商的問題，是**接縫**的問題。

```python
from atk_provider import Message, complete

c = complete([Message("user", "一句話解釋 context window。")])
print(c.text)
print(c.provider, c.model, c.usage.total_tokens)   # 誰真的服務了這一次
```

**一個檔案、只用標準函式庫、零依賴。** 換供應商是 `.env` 裡一行：

```bash
PROVIDER=openai     # 或 anthropic / deepseek / qwen / openrouter / custom
```

`PROVIDER=custom` 可以指向任何 OpenAI 相容 host——閘道、代理、你自己跑的本地模型。

## 四條規矩，每一條都是測試

> **ATK 可以是預設，但永遠不可以是唯一。**

| 規矩 | 怎麼驗的 |
|---|---|
| **看得見** | 每次回應都帶 `provider`，範例每跑一次就印 |
| **換得掉** | 同一段程式靠環境變數送到兩台不同伺服器、用兩把不同 key，兩邊各自驗證收到什麼 |
| **寫清楚** | README 的「怎麼換掉 ATK」在顯眼處 |
| **可移除** | 所有 `ATK_*` 拿掉照常運作——這是一條測試，不是一句保證 |

## 兩個外部審查抓到的問題，值得你也檢查自己的程式

這個資產被獨立審查過，抓到兩個我自己沒看到的洞。它們都很常見：

**第一，錯誤訊息會洩漏你的 key——而且修過一次還不夠。**

我原本把服務端錯誤本文前 400 字塞進例外訊息，還在註解裡寫「key 在 header 不在 body，所以安全」。**這個推論是錯的**——伺服器或代理完全可以把它拒絕的那把 key 回顯在 body 裡。審查者用假憑證重現了：401 回 `{"error": "invalid credential <你的key>"}`，例外訊息就帶著它印到 stderr。

我的第一版修法：預設**不含 body**，只留 status；要 debug 再開 `ATK_INCLUDE_ERROR_BODY=1`，而且那條路徑會遮蔽已知 key。

**第二輪審查發現那還是會漏。** 我的程式先把 body 切到 400 字，**才**做遮蔽——key 如果剛好跨過那個切點，前半段就留在訊息裡了。**製造這個洩漏的是我自己的截斷，不是外部代理。**

更難堪的是：我的測試也沒抓到，因為它只斷言「完整的 key 不在訊息裡」。前 19 個字元外洩，它照樣綠燈。

現在是先遮蔽整份 body、再截斷已經安全的內容。測試也改成**不允許 key 的任何 8 字元片段出現**，並涵蓋 key 在切點前、跨切點、切點後、重複出現四種位置。

> 兩個可以帶走的教訓：**「原始碼搜不到 sk-」不能代替執行時測試**；而**「完整秘密不在裡面」也不能代替「秘密的任何片段都不在裡面」**。

> 順帶一提：「原始碼裡搜不到 `sk-`」**不能**當作執行時不會洩漏的證據。審查者這句話值得抄在牆上。

**第二，HTTP 200 但沒有內容，被當成成功。**

`content: null`（例如模型回了 tool call）原本回傳 `text=None`，範例印出 `None` 然後 exit 0。對一個做摘要的東西來說，那是把失敗報成成功。現在會明確失敗，而且訊息裡帶 `finish_reason` 告訴你為什麼是空的。

## 先看，再花錢

```bash
python3 example_summarise_tool_output.py --dry-run --show-payload --file build.log
```

印出**完整的 JSON request body**，然後什麼都不送。header 永遠不印，因為其中一個是你的 key。

## 老實說有什麼沒做

- **我沒有跑過真實 ATK。** 這份資產上唯一一次 live 呼叫是 **PR 審查者做的，用的是負責人提供並授權最小測試的憑證**：`claude-sonnet-4.6`、`max_tokens=16`、回 `OK`、12 in / 4 out。我的環境裡沒有憑證，我不會說那是我跑的。
- **那一次沒有回報美元成本**，但沒回報不等於免費。
- **MCP 沒有實際握手過**，端點和 header 名稱來自官方文件。
- **沒有任何省錢或品質主張。** 這個檔案只負責把請求送出去，它不壓縮、不快取、不優化。
- **契約裡的預算上限沒實作**，明講沒做，而不是收下參數然後忽略。

25 個測試跑在真的 HTTP 伺服器上。憑證相關的都是**執行時 canary**：真的設一個秘密值、真的讓伺服器回顯它、再斷言人看到的字串裡沒有它。

---
*程式碼：`integrations/atk-provider/`，只用標準函式庫。*

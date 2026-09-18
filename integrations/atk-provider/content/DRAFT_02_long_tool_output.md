---
status: DRAFT — 未發布。發布需另行授權（reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md §5）
asset: integrations/atk-provider/example_summarise_tool_output.py
claims_requiring_evidence: none（本文不宣稱壓縮率、省錢或品質提升）
live_evidence: ATK 單次 chat 由 PR #4 reviewer 實測，使用**負責人提供並授權**的憑證（非 reviewer 自有帳號）；本文作者未跑過真實 ATK
---

# 4000 行 build log，模型只需要其中三行

## 每個人都撞過的第一道牆

你的 agent 跑了一個指令。指令吐出 4000 行。

你把整包塞給模型，因為不塞就沒有上下文。然後三件事同時發生：這一次呼叫變貴、context window 被吃掉一半、模型開始忘記你三輪前講過的事。

下一個直覺通常是「那我 truncate 一下」。於是你砍掉後面 3000 行——**而錯誤訊息剛好在最後一行**。

## 一個小到可以讀完的範例

```bash
python3 example_summarise_tool_output.py --file sample-build.log
cat sample-build.log | python3 example_summarise_tool_output.py
```

它做三件事，沒了：

**第一，頭尾都留。** 錯誤訊息通常在最後，而不是最前面。只留開頭是最常見的錯法。

**第二，明講中間被拿掉了。**

```
[... 已移除中間 84213 個字元；你看到的是前後各 6000 字元 ...]
```

這一行是關鍵。**沒有被告知自己只拿到節錄的模型，會非常有自信地把節錄當成全部來總結。** 你會得到一份語氣篤定、但少了一半事實的摘要——比什麼都不做更危險。

**第三，叫模型回答可以拿來行動的東西。**

> 最多五點：什麼壞了或變了、行動需要的精確識別資訊（檔名、行號、錯誤碼），以及任何看起來像密鑰或憑證的東西。如果什麼都沒壞，用一行講完，不要無中生有。

最後那句是刻意的。模型很願意把「build 成功」寫成三段有洞見的分析。

## 三行設定就能跑

```bash
ATK_API_KEY=<你的 key>
ATK_BASE_URL=https://api.aitokenking.com.tw/api/v1
ATK_MODEL=claude-sonnet-4.6
```

先把設定載入 shell，**再**看模型清單（撰稿時 52 個）：

```bash
set -a && . ./.env && set +a          # 先載入：下面的 curl 需要 $ATK_API_KEY

curl -s "$ATK_BASE_URL/models" \
  -H "Authorization: Bearer $ATK_API_KEY" | python3 -m json.tool | head
```

官方文件叫 `AITOKENKING_API_KEY`，我們的契約叫 `ATK_API_KEY`，**Python 這邊兩個都吃**。
但**別名只在 Python 端生效**——上面的 `curl` 讀的是 shell 的 `$ATK_API_KEY`，不會因為 Python
支援別名就自動有值。`.env` 若用官方拼法，請另外設 `ATK_API_KEY` 或在指令裡換掉。

## 先看，再花錢

```bash
python3 example_summarise_tool_output.py --dry-run --show-payload --file sample-build.log
```

**兩種都什麼都不送。** 差別是：**節錄預覽不需要憑證**（`--dry-run` 單獨用）；**完整 JSON body 需要
已設定的 provider**，因為 body 的形狀由實際會送出它的 adapter 決定，沒設定時它明確拒絕顯示而不是猜
一份。header 永遠不印，因為其中一個是你的 key。

而且那份 body 是**由真正會送出它的 adapter 產生的**，不是另外組一份給你看的。這件事我第一版做錯了：我自己組了一份 OpenAI 形狀的 JSON，但 Anthropic 實際送出去的會把 `system` 提到頂層、還會加 `max_tokens`——所以「送出前看完整 body」對那條路徑根本不成立。獨立審查把 preview 和本機伺服器實收的內容逐欄位比對，才抓到。

現在兩邊共用同一個 `build_payload()`，測試也直接斷言 preview 等於伺服器實收的 body。

任何要你先給 key 才肯讓你看它要幹嘛的工具，都值得懷疑。

## 換一家供應商是一行

```bash
PROVIDER=openai python3 example_summarise_tool_output.py --file sample-build.log
```

同一段程式、同一個指令。這個範例是走 `atk_provider` 這個接縫寫的，所以它本身不知道自己在跟誰講話——這正是重點。每次跑完會告訴你誰服務了這一次：

```
--- served by atk / <model> · 412 in, 37 out · cost not reported
```

`cost not reported` 是真的沒回報，不是 0。供應商沒告訴我們，我們就不替它編一個。

## 一個容易忽略的失敗模式

如果模型回了 tool call 而不是文字，HTTP 是 200，但 `content` 是 `null`。

這個範例的早期版本會印出 `None` 然後 exit 0——**把失敗報成成功**。是外部審查抓到的。現在它會明確失敗，並告訴你 `finish_reason` 是什麼。

如果你自己在寫類似的東西，值得檢查一下：**你的「成功」判斷，是不是只看了 HTTP 狀態碼？**

## 老實說清楚

**這個範例只是節錄，不是壓縮。** 它砍掉中間然後講明砍了。真正的壓縮是另一件事——`headroom`（Apache-2.0，在我們的 registry 裡）就是在做這件事，而且它有自己公開的品質 benchmark。把它接到這個接縫前面是很自然的下一步資產，**但還沒做，所以本文不引用它的任何數字**。

**我沒有跑過真實 ATK。** 這份資產上唯一一次 live 呼叫是 **PR 審查者做的，用的是負責人提供並授權最小測試的憑證**（`claude-sonnet-4.6`，回 `OK`，12 in / 4 out，未回報美元成本）。我的環境裡沒有憑證，所以我不會說那是我跑的。本機測試打的是 localhost 伺服器，測的是 client，不是 ATK。全部記在 `VERIFICATION.md`。

**這個範例還不是任何工具的整合。** 它是獨立範例，headroom 還沒接上。

**本文沒有任何省錢主張。** 少送 token 當然少付錢，但「少多少」需要在你自己的工作負載上量，而那是另一件事，需要另一份證據。

## 三十秒

```bash
cd integrations/atk-provider
python3 example_summarise_tool_output.py --dry-run --file sample-build.log
```

先看它要送什麼。覺得合理，再填 `.env`。

---
*程式碼：`integrations/atk-provider/`。只用標準函式庫，沒有依賴。*

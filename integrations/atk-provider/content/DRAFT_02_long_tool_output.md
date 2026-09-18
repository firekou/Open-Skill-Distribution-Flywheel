---
status: DRAFT — 未發布。發布需另行授權（reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md §5）
asset: integrations/atk-provider/example_summarise_tool_output.py
claims_requiring_evidence: none（本文不宣稱壓縮率、省錢或品質提升）
---

# 4000 行 build log，模型只需要其中三行

## 每個人都撞過的第一道牆

你的 agent 跑了一個指令。指令吐出 4000 行。

你把整包塞給模型，因為不塞就沒有上下文。然後三件事同時發生：這一次呼叫變貴、context window 被吃掉一半、模型開始忘記你三輪前講過的事。

下一個直覺通常是「那我 truncate 一下」。於是你砍掉後面 3000 行——**而錯誤訊息剛好在最後一行**。

## 一個小到可以讀完的範例

```bash
python3 example_summarise_tool_output.py --file build.log
cat build.log | python3 example_summarise_tool_output.py
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

## 先看，再花錢

```bash
python3 example_summarise_tool_output.py --dry-run --file build.log
```

```
PROVIDER=atk
provider not configured: PROVIDER=atk needs ATK_API_KEY, ATK_BASE_URL, ATK_MODEL. ...
input 1100 chars -> prompt 1443 chars
--- messages ---
[system] 你為一位必須採取行動的工程師總結機器輸出 ...
```

**印出會送出什麼，然後什麼都不送。** 不需要憑證。任何要你先給 key 才肯讓你看它要幹嘛的工具，都值得懷疑。

## 換一家供應商是一行

```bash
PROVIDER=openai python3 example_summarise_tool_output.py --file build.log
```

同一段程式、同一個指令。這個範例是走 `atk_provider` 這個接縫寫的，所以它本身不知道自己在跟誰講話——這正是重點。每次跑完會告訴你誰服務了這一次：

```
--- served by atk / <model> · 412 in, 37 out · cost not reported
```

`cost not reported` 是真的沒回報，不是 0。供應商沒告訴我們，我們就不替它編一個。

## 老實說清楚

**這個範例只是節錄，不是壓縮。** 它砍掉中間然後講明砍了。真正的壓縮是另一件事——`headroom`（Apache-2.0，在我們的 registry 裡）就是在做這件事，而且它有自己公開的品質 benchmark。把它接到這個接縫前面是很自然的下一步資產，**但本輪沒有做，所以本文不引用它的任何數字**。

**我們沒有跟真的 ATK 連過。** 環境裡沒有憑證，而且那個 endpoint 在我們的網路上解不出 DNS。全部記在 `VERIFICATION.md`，沒有用 mock 冒充成功。

**本文沒有任何省錢主張。** 少送 token 當然少付錢，但「少多少」需要在你自己的工作負載上量，而那是另一件事，需要另一份證據。

## 三十秒

```bash
cd integrations/atk-provider
python3 example_summarise_tool_output.py --dry-run --file <你的 log>
```

先看它要送什麼。覺得合理，再填 `.env`。

---
*程式碼：`integrations/atk-provider/`。只用標準函式庫，沒有依賴。*

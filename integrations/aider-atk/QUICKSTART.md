# Quick Start：用原生設定讓 aider 連上一個 OpenAI 相容端點

適用：**Linux + Python 3.11**。Windows 與 macOS **本輪未測**，不要把這份當成在那兩個平台上驗證過。

這份走的是 aider 的**原生**設定，沒有任何我們自製的轉接層。你隨時可以把端點換成別家，包括把它從我們的換走。

## 你要先準備的三個值
| 值 | 從哪來 |
|---|---|
| API 根位址 | 你的供應商文件。**是根位址，不是 `/chat/completions` 那一層** |
| 金鑰 | 你的供應商 |
| 模型名 | 你的供應商，前面要加 `openai/` |

缺任何一個就**先停下來**。這份不替你猜位址，也不填任何預設端點。

## 1. 裝起來
```bash
python3.11 -m venv .venv
.venv/bin/pip install "aider-chat==0.86.1"
.venv/bin/aider --version
```

## 2. 設定（金鑰只進環境變數）
```bash
export OPENAI_API_BASE="<你的 API 根位址>"
export OPENAI_API_KEY="<你的金鑰>"
export AIDER_MODEL="openai/<你的模型名>"
```

**不要**把金鑰放在命令列上：它會進 shell 歷史，也會出現在別人的 `ps` 裡。也不要寫進專案檔案。

## 3. 先檢查設定的形狀
```bash
python3 check_config.py
```
它**不連網**、不轉送任何東西，只看你的三個值長得對不對，並且永遠不印出金鑰或金鑰的任何片段。

| exit | 意思 |
|---|---|
| 0 | 形狀沒問題。**這不代表端點會回應** |
| 2 | 有值沒設 |
| 3 | 模型名沒有 `openai/` 前綴 |
| 4 | 根位址後面多接了 `/chat/completions` 之類的路徑 |

exit 0 只代表「不會因為這三種常見填錯而失敗」。端點通不通、金鑰有沒有效、模型存不存在，**沒有真的呼叫過就無從得知**。

## 4. 跑一次
```bash
.venv/bin/aider --model "$AIDER_MODEL" your_file.py
```

## 兩個實測到的行為，先講清楚免得你白找
**一、`openai/` 前綴不會被送出去。** 我們用一個本機假端點錄下 aider 實際送出的請求：`model` 欄位是 `local-test-model`，不是 `openai/local-test-model`。前綴是給 aider 判斷走哪條路徑用的，不是模型名的一部分。所以你的供應商那邊要認得的是**去掉前綴之後**的那個名字。

**二、它啟動時會連外，而且關掉 analytics 也一樣。** 同一次錄製裡，即使加了 `--no-analytics --no-check-update`，aider 仍然嘗試連 `raw.githubusercontent.com` 抓 litellm 的模型價格表。在我們的隔離環境裡這個請求失敗了，aider 印出錯誤後**照常繼續**。

如果你在一個不允許對外連線的環境裡工作，這件事你要先知道。**關掉選用的遙測不等於不連外**——這是量到的，不是推論的。

## 這份沒有回答的事
端點實際通不通、費用、速度、模型做得對不對。本輪**沒有任何一次真實供應商呼叫**。

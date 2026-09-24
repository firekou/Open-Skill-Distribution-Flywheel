# 證據

環境：Linux、Python 3.11.15、venv、`aider-chat==0.86.1`（`aider --version` → `aider 0.86.1`）。
無真實供應商呼叫、無金鑰、無費用。所有測試值都是 placeholder，沒有一個是真的。

輸入雜湊（md5）：
```
da2b54d995a08cdbb84f157587f82f1d  sample/import_contacts.py
2952746b8e56b5a35fdb02949bcdabe1  sample/test_import_contacts.py
c87c2a16cf5f9861902fc1cbd1d773c2  check_config.py
```

## 五欄分開，不互相代替

| 欄 | 狀態 | 依據 |
|---|---|---|
| clean install | **DONE** | venv + `pip install aider-chat==0.86.1`，`aider --version` 回報 0.86.1。**但這是 release，不是指定的 `5dc9490` dev commit**，見 SOURCE.md |
| CLI／設定 | **DONE** | 下方 A、B |
| 協定 | **OFFLINE_PROTOCOL_ONLY** | 下方 C。只證明送出什麼，不證明任何真實端點 |
| 真模型 | **NOT TESTED** | 本輪未授權任何 live 呼叫 |
| 外部使用 | **NONE** | 0 位外部使用者。沒有邀請、沒有採用 |

---

## A. baseline 任務測試（來源：`0.86.1` 無關，純本地 Python）
```
$ cd sample && python3.11 -m unittest test_import_contacts -v
...
FAIL: test_2_columns_may_be_swapped
AssertionError: Lists differ: [{'name': 'ada@example.com', 'email': 'Ada'}] != [{'name': 'Ada', 'email': 'ada@example.com'}]

ERROR: test_3_missing_email_column_is_named
IndexError: list index out of range

Ran 5 tests in 0.002s
FAILED (failures=1, errors=1)
exit=1
```
1、4、5 通過；2 failure；3 error。**這是刻意的 baseline，不是壞掉的測試。**

## B. 設定檢查器：四條路徑各跑一次，以及變異控制

實際輸出（`env -i`，只帶 PATH，值全為 placeholder）：

| 情境 | exit | 關鍵輸出 |
|---|---|---|
| 三個都沒設 | 2 | `Missing: OPENAI_API_BASE, OPENAI_API_KEY, AIDER_MODEL` |
| 只設了 base | 2 | `Missing: OPENAI_API_KEY, AIDER_MODEL` |
| 模型名沒前綴 | 3 | `carries no provider prefix` → 建議 `openai/some-model` |
| base 尾巴多接路徑 | 4 | `ends in '/chat/completions'` |
| 形狀正確 | 0 | `Shape looks right.`（並明講這不代表端點會回應） |

金鑰那一行在**每一條路徑**都只印 `SET` / `NOT_SET`。

自身測試：
```
$ python3.11 -m unittest test_check_config
Ran 8 tests in 0.007s
OK        exit=0
```

**變異控制（證明這 8 個測試不是擺設）：**

| 變異 | unittest exit | 結果 |
|---|---|---|
| 拿掉 provider-prefix 檢查 | 1 | `FAILED (failures=1)` |
| 拿掉 endpoint-tail 檢查 | 1 | `FAILED (failures=1)` |
| 把金鑰改成直接印出來 | 1 | `FAILED (failures=1)` |
| 未變異對照 | 0 | 全過 |

exit code 是在指令之後**立刻**用 `rc=$?` 取的，沒有被命令替換洗掉。

另有一個結構性測試 `test_it_makes_no_network_call`：用 AST 解析 `check_config.py` 的 import，斷言除了 `os`、`sys` 之外沒有別的。之後誰想在這支裡加一個 HTTP client，這個測試會先擋下來。

## C. 協定錄製（OFFLINE_PROTOCOL_ONLY）

做法：本機 loopback 假端點（`fake_openai_server.py`，只綁 `127.0.0.1`），記錄請求路徑與 `model` 欄位。**Authorization 的值從不寫入紀錄**，只記「有沒有帶」。

原始紀錄（`evidence/offline_protocol_requests.json`）：
```json
[
  {
    "path": "/v1/chat/completions",
    "model": "local-test-model",
    "stream": true,
    "message_count": 8,
    "authorization_header_present": true
  }
]
```

三件量到的事：
1. **`OPENAI_API_BASE` 給的是根位址。** 我設的是 `http://127.0.0.1:8801/v1`，實際被請求的是 `/v1/chat/completions`——路由是底層自己接上去的。這正是檢查器 exit 4 在擋的情況，現在它有量測背書，不只是斷言。
2. **`openai/` 前綴不會送出去。** 我傳 `--model openai/local-test-model`，送出的 `model` 欄位是 `local-test-model`。
3. **這一次任務只送了一個請求。** 在 `--no-git`、repo-map disabled、單一 `--message` 的條件下，沒有看到 helper model 或重試造成的額外請求。**這個結論只在這組條件下成立**，換成互動模式、開 repo-map 或讓它跑測試，我沒有量過。

### 同一次錄到的一件事，值得單獨列
即使加了 `--no-analytics --no-check-update`，aider 啟動時仍嘗試連 `raw.githubusercontent.com` 取 litellm 的模型價格表；在隔離環境中該請求失敗（SSL 驗證失敗），aider 印出錯誤後繼續執行。

**所以「關掉選用遙測」不等於「不會對外連線」。** 這是量到的，寫進 Quick Start。

### 這一段不能拿來主張什麼
不能拿來說任何真實端點可用、不能說費用、不能說速度、不能說模型做得對。假端點回的是寫死的 `ok`。第一次嘗試時我的伺服器在被 kill 時沒把紀錄寫檔（`NO REQUEST LOG`），改成每次請求後就落盤才拿到上面的資料——這個失敗也記在這裡，因為「沒有紀錄」和「沒有請求」看起來一樣但意思相反。

## 本輪未做
未安裝指定的 `5dc9490` dev commit（只讀原始碼）· 未做任何真實供應商呼叫 · 未 merge · 未部署 · 未送上游 · 未邀請任何人 · 未新增費用 · 未讀寫任何 secret · Windows/macOS 未測 · 未比對 `0.86.1` 與 `5dc9490` 的差異。

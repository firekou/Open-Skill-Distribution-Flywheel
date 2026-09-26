# 證據

環境：Linux、Python 3.11.15、venv、`aider-chat==0.86.1`（`aider --version` → `aider 0.86.1`）。
無真實供應商呼叫、無金鑰、無費用。所有測試值都是 placeholder，沒有一個是真的。

輸入雜湊（md5）：
```
da2b54d995a08cdbb84f157587f82f1d  sample/import_contacts.py
2952746b8e56b5a35fdb02949bcdabe1  sample/test_import_contacts.py
d467ecfd7b391d71f2851014872ab5b0  check_config.py
602246801de2f2adcc9c2f9f8aa5c004  test_check_config.py
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

自身測試（revision 2 後為 11 項）：
```
$ python3.11 -m unittest test_check_config
Ran 11 tests in 0.010s
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

另有一個結構性測試 `test_it_makes_no_network_call`：用 AST 解析 `check_config.py` 的 import，斷言除了 `os`、`sys` 之外沒有別的。

**這個測試的效力比它的名字聽起來小，先講清楚。** 目前的 `check_config.py` 經逐行檢視確實沒有任何連網行為——這是**現在這份原始碼**的事實。那個測試只看 import 集合，擋不住 `os.system("curl ...")` 這類走既有 import 的路徑。所以它是一個**低成本的回歸提示**，不是網路隔離，也不是完整的防護邊界。R1 覆核指出我上一版把它講得太強，這裡改正。

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


---

# revision 2：R1 三個條件的處置

覆核：`reviews/PR14_R1_AIDER_e8289655.md`，`APPROVED_WITH_CONDITIONS`，`blocking_findings: []`。三項我都同意，沒有一項爭議。

## 條件一（P1）：`openai/` 前綴是假通過 —— REPRODUCED，已修

先重現，再改：

```
$ AIDER_MODEL=anthropic/model  python3.11 check_config.py -> exit 0     ← 應該是 3
$ AIDER_MODEL=openai/          python3.11 check_config.py -> exit 0     ← 應該是 3
$ AIDER_MODEL=some-model       python3.11 check_config.py -> exit 3
```

覆核點名的是 `anthropic/model`。我重現時**多發現一個**：`openai/`（前綴對但模型名是空的）同樣漏過。舊條件是 `if "/" not in model`——它問的是「有沒有斜線」，不是「是不是 openai/」。**這又是同一個形狀的錯誤**：拿一個好觀察的訊號，代替我真正想確認的那件事。

改後：

| `AIDER_MODEL` | exit |
|---|---|
| `anthropic/model` | 3 |
| `openai/` | 3 |
| `some-model` | 3 |
| `openai/good-model` | 0 |
| `openai/meta-llama/Llama-3` | 0 |

最後一列是刻意的：有些 OpenAI 相容端點的模型名本身就含斜線，所以只有**第一段**算前綴。這條寫進測試，也寫進 Quick Start。

新增負測試三項（別家前綴三例、前綴後空白、含斜線的模型名仍通過），測試總數 8 → 11，`exit=0`。

**負控制**：把條件改回舊的 `if "/" not in model`，`unittest exit=1`、`FAILED (failures=4)`。修好的版本 `exit=0`。所以是這個修法在擋，不是運氣。

## 條件二（P2）：結構測試的安全主張過強 —— 已縮小
上面 B 段已改寫。結論改為：目前原始碼無連網行為（逐行檢視），import 測試只是低成本回歸提示，**不是網路隔離、不是完整防護**。沒有為此新增 sandbox、HTTP 攔截或任何框架。

## 條件三（P2）：外部報告缺來源網址 —— 已補
`AIDER_WHAT_WE_LEARNED.md` 兩份第一手敘述都補上直接 URL，「個人經驗、非受控比較」的界線原樣保留，沒有新增任何效果主張。

## P3：期限記錄不一致
main 的固定 deadline 是 `2026-09-25T18:30:00Z`，我 revision 1 的 executor response 寫成 `19:20Z`。是我寫錯，已在 executor response 更正。revision 2 沿 main 的期限，未自行延長。

## revision 2 沒有改變的事
真模型 **NOT TESTED** · 外部使用 **0** · 未 merge · 未部署 · 未送上游 · 未呼叫任何真實供應商 · 未新增費用 · 未讀寫 secret · 未新增 adapter 或平台 · 假端點與任務 fixture 未動（`import_contacts.py`、`test_import_contacts.py` 的 md5 不變）。

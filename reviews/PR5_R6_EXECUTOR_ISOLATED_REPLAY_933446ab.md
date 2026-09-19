# PR #5：隔離重放執行紀錄（**不是 review，不是驗收結論**）

## 這份是什麼、不是什麼

R6 指出 `P5-R4-01` 需要獨立 reviewer 在隔離環境重放，而 GPT/Codex 環境四項隔離原語全遭 OS 拒絕
（見 `reviews/evidence/pr5-r6/isolation_probe.json`）。**缺的不是判斷力，是一個跑得動的沙箱。**

本檔提供那次執行的機械紀錄。**它不宣告 `P5-R4-01` 通過。**
run identity 是否夠格、以及下列六項與 README 規格的落差是否可接受，**是 reviewer 的標準，不是 executor 的**。

**獨立性揭露（必須連同結果一起讀）：**

| 面向 | 狀態 |
|---|---|
| run / workspace | **獨立**：另一個 run，`/tmp/r6-replay` 全新 clone，未使用 executor 的工作目錄，拿不到 executor 的脈絡 |
| 模型來源 | **不獨立**：與 executor 同屬 Claude。依 OPERATING_RULES，不得聲稱模型來源獨立 |
| 執行環境 | **由 executor 提供**。這是本紀錄最需要 reviewer 自行折價的一點 |

R6 說「不再補同類 executor 證據」——本輪**未**再產生 executor 自跑紀錄，**未**修改任何產品程式。
`32ca53c` 之後的產品程式一行未動。

---

## 1. 隔離：哪些真的生效（附驗證），哪些沒有

### 生效，且經反向對照證明

**環境變數已清空。** 父環境確實帶著秘密（只列名稱，值未輸出）：
`GITHUB_TOKEN`、`GH_TOKEN`、`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AITOKENKING_API_KEY`、
`CLAUDE_CODE_MESSAGING_TOKEN`、`CLOUDSDK_AUTH_ACCESS_TOKEN`、`HTTPS_PROXY` 等。
`env -i` 之後行程內只剩 5 個變數：

```
HOME=/tmp  LC_CTYPE=C.UTF-8  PATH=/usr/bin:/bin  PYTHONDONTWRITEBYTECODE=1  TMPDIR=/tmp
比對 TOKEN/SECRET/KEY/PASSWORD/GH_/GITHUB/ANTHROPIC/AWS/PROXY/API 的結果：matches=[]
```

（`LC_CTYPE` 是 CPython 啟動時自行注入，非繼承。）**無 GitHub 寫入 token、無 proxy 設定、無任何憑證進入該行程。**

**網路真的不存在，且有對照組。**

```
namespace 內：
  /proc/net/dev        只有一個未啟用的 lo
  /proc/net/tcp        只有表頭，無任何 socket
  TCP 1.1.1.1:443      → Errno 101 Network is unreachable
  TCP 140.82.121.4:443 → Errno 101 Network is unreachable   (github.com)
  DNS github.com       → Errno -3 Temporary failure in name resolution

對照組（同樣 env -i，但不加 unshare -n）：
  TCP 1.1.1.1:443      → CONNECTED
  TCP 140.82.121.4:443 → CONNECTED
  DNS github.com       → 140.82.114.4
```

**對照組是關鍵**：它證明上面的失敗來自 namespace，不是因為這台機器本來就連不出去。

**assert 是活的。** 腳本的檢查是 `assert`，若被 `-O` 關掉整份就形同虛設：
`assertions ACTIVE`、`PYTHONOPTIMIZE in env: False`、`sys.flags.optimize = 0`。

**腳本不是空轉。** 把輸入樹**複製一份**後在副本的 `current/local_check.py` 追加一行註解（原檔未動），
同一支腳本立刻中止：`AssertionError: ('current/local_check.py', 'snapshot mismatch')`，exit 1。

### 沒生效——**照實列出，未放寬條件重跑**

README 要求的是更嚴格的盒子。以下六項達不到：

| # | README 要求 | 實際 |
|--:|---|---|
| 1 | 容器執行（`docker run`） | **做不到**。`docker` 二進位在，**daemon 連不上**；`podman`／`bwrap`／`nsjail`／`firejail` 全部不存在。**未安裝或拉取任何東西來繞過** |
| 2 | `--user 65534:65534` | **以 root（uid 0）執行** |
| 3 | `--cap-drop ALL`、`no-new-privileges`、`--pids-limit`、`--memory`、`--cpus` | **無對應機制**。`unshare -n` 只隔離網路 namespace；mount／PID／user／IPC namespace 與主機共用 |
| 4 | 核心層級唯讀掛載 | **無**。只用 `chmod -R a-w`，屬 DAC，**對 root 無約束**。補償證據：五個 blob 執行後重新 hash 完全相同、clone 的 `git status` 乾淨、輸入樹未出現任何新檔案 |
| 5 | 外層 `timeout 180` | **未套用**。腳本自身對子行程的 `timeout=15/90` 有效；全程約 1 秒 |
| 6 | 私有 tmpfs 作為 HOME | **無**。`HOME=/tmp`，與主機 `/tmp` 共用 |

**第 1 項與第 4 項是最實質的落差**：沒有容器，且唯讀是靠權限位而非核心強制。
是否足以支撐 `P5-R4-01`，請 reviewer 自行判定。

---

## 2. Manifest 獨立核對

執行**前**以 `git hash-object` 自行計算，執行**後**再算一次，兩次與 manifest 三方一致：

| 路徑 | blob SHA | 相符 |
|---|---|:--:|
| `current/local_check.py` | `3036418da9fccf40959d2b6f1efc67fa6db5cf85` | ✅ |
| `current/test_local_check.py` | `c154649b2a9f9d779511625a85f4071c8fc84810` | ✅ |
| `current/ab_test.py` | `6dd9e14728a4e69577ed3a1b270cd6766896031c` | ✅ |
| `current/README.md` | `26f8c8b1fc0030fdac1021b2e4e04187e1ee0ed3` | ✅ |
| `previous/local_check.py` | `ec66c5ea914fe62d8ec24ab65c3a221f2aacab76` | ✅ |

腳本與 manifest 本身以 committed 狀態執行，未改一個字：
`reviewer_checks.py` = `d1a4a0c29fb8d277a1db4fa723917e7ec06dd3dc`、
`manifest.json` = `87fed312b0db501898ad5d536e8911f4f998b46d`，clone 的 `git status --porcelain` 為空。

---

## 3. 執行指令

```sh
env -i PATH=/usr/bin:/bin HOME=/tmp TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 \
  unshare -n python3 repo/reviews/evidence/pr5-r5/reviewer_checks.py \
  /tmp/r6-replay/input repo/reviews/evidence/pr5-r5/manifest.json
```

**exit 0 · stderr 0 bytes · stdout 6134 bytes / 19 筆 JSON**

---

## 4. 逐字輸出

```
{"check": "exact_source_blobs", "passed": true, "head": "32ca53cd703efeb647ddb2d65168ba69f1e414d6"}
{"check": "unknown_form_1", "exit": 2, "private_echo": false}
{"check": "unknown_form_2", "exit": 2, "private_echo": false}
{"check": "unknown_form_3", "exit": 2, "private_echo": false}
{"check": "unknown_form_4", "exit": 2, "private_echo": false}
{"check": "unknown_form_5", "exit": 2, "private_echo": false}
{"check": "previous_version_negative_control", "exit": 2, "private_echo": true}
{"check": "help_positive_control", "exit": 0}
{"check": "unit_suite", "exit": 0, "stdout": "", "stderr": "... Ran 31 tests ... OK"}
{"check": "legal_equals_parse", "passed": true}
{"check": "shrink", "exit": 0, "boundary": "mocked process/network; real decision path"}
{"check": "unchanged", "exit": 3, "boundary": "mocked process/network; real decision path"}
{"check": "equal_rewrite", "exit": 3, "boundary": "mocked process/network; real decision path"}
{"check": "growth", "exit": 3, "boundary": "mocked process/network; real decision path"}
{"check": "lost", "exit": 1, "boundary": "mocked process/network; real decision path"}
{"check": "http_error_full", "body_withheld": true, "boundary": "mock HTTPError"}
{"check": "http_error_partial", "body_withheld": true, "boundary": "mock HTTPError"}
{"check": "http_error_transformed", "body_withheld": true, "boundary": "mock HTTPError"}
{"check": "summary", "passed": true, "head": "32ca53cd703efeb647ddb2d65168ba69f1e414d6",
 "limitations": "No clean headroom install, live proxy, real API, cost or adoption verification."}
```

31 個測試逐條 `... ok`，`Ran 31 tests in 0.051s` `OK`。執行後輸入樹未出現 `__pycache__` 或任何新檔。

**R6 驗收第 4 點要求的那條負控制成立：**
`previous_version_negative_control` → `private_echo: **true**`。
舊版 `d1930e4` 確實會把 dash 開頭的合成私密值印出來，**證明這組測試抓得到真缺陷，不是空轉綠燈。**

---

## 5. Head 重查（R6 明訂寫結論前必做）

| | |
|---|---|
| manifest `reviewed_head`（輸入樹來源） | `32ca53cd703efeb647ddb2d65168ba69f1e414d6` |
| manifest `comparison_head` | `d1930e4696f11cfb3cdae2f59d1b3692b68ee127` |
| live head，執行前 15:50:59Z 與執行後 15:52:25Z **兩次相同** | `933446ab230e6fb8b41d79b596ef3c19b721fb7a` |

**live head ≠ 輸入樹來源。** 機械關係如下：

- `32ca53c` **是** live head 的祖先（`git merge-base --is-ancestor` 成立）。
- 兩者之間**只有一個 commit**：`933446a docs(pr5-r5): supply the runtime evidence…`。
- 變更檔案**完整清單**：`integrations/headroom-atk/evidence/pr5-r6/executor_replay.txt`（新增）、
  `reviews/ATK_AGENT_DISCOVERY_EXECUTOR_RESPONSE.md`（追加）。
- **四個受測檔案一行未變。**

判定此差異是否影響結論，屬 reviewer 權限。

---

## 6. 腳本自陳的邊界（原文引用，非本紀錄的評估）

`"boundary": "mocked process/network; real decision path"`、`"boundary": "mock HTTPError"`、
`"limitations": "No clean headroom install, live proxy, real API, cost or adoption verification."`

即：verdict 檢查的 process／network 邊界是 mock 的，**不證明真實 proxy、乾淨安裝或付費 API**。

---

## 7. 本輪未做

未修改產品程式 · 未再補 executor 自跑證據 · 未 merge · 未部署 · 未送上游 · 未使用已暴露金鑰 ·
未新增付費呼叫 · 未改動 `governance/state.json` 的條件判定欄位 · 未宣告 `P5-R4-01` 關閉。

外部第三方採用仍為 **0 筆**，搜尋基線 T0 仍未執行。整套治理仍**非 ACTIVE**。

**請 reviewer 依第 1 節的六項落差自行判定本紀錄可否支撐 `P5-R4-01`；
若判定不足，請指明缺哪一項隔離能力，executor 再評估是否有辦法提供。**

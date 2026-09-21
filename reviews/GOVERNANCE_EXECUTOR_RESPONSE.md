# Governance Executor Response — 最小自動交接實作

**Branch** `claude/atk-governance-controller` · **Base** `204a7fe8d43a39962bb4beb313b7538484d433cb` (main)
**Draft PR，未合併。** 本檔由 executor 撰寫，**不自我核准**；驗收由獨立 reviewer 作出。
產品修復（PR #5）未混入本分支。

## 送審定位（依 IMPLEMENTATION_PROMPT 新版接收規則）

| | |
|---|---|
| **Repository** | `firekou/Open-Skill-Distribution-Flywheel` |
| **PR** | [#6](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/6) |
| **程式 head** | `02040ec4413bfb4be32547e2a713128c9b965eed` —— 本輪所有程式與證據都在這個 commit 上 |
| **live head** | 比上一行**晚一個 commit**：就是加入本表的這次提交。原因是 C2（見 §1）：SHA 要等 commit 存在才知道，寫在自己那個 commit 裡永遠是錯的。請以 PR #6 的 live head 為準，本表不自稱是它 |
| **上一輪已審 head** | `c04ef465d000968b86065e7608a8c92761458c6d` |
| **Response 路徑** | `reviews/GOVERNANCE_EXECUTOR_RESPONSE.md`（本檔 §8、§9） |
| **本輪 G 編號** | **G1、G2、G3**。G4 是本次送審本身；**G5／G6 未做，需另外授權** |
| **Finding 對應** | GOV-R1-01 → §8 撤回 ＋ `CAPABILITIES.md`；GOV-R1-02 → §9.1 ＋ `ACTIVATION.md`；GOV-R1-03 → §9.1 ＋ `runners.build_env`；GOV-R1-04 → §9.1 ＋ 限制表 |
| **變更性質** | **程式與報告都有變更**，不是只改文字。程式證據見 `governance/controller/evidence/` |
| **本輪未做** | 無真實執行、未安裝觸發器、未新增費用、未提交任何憑證；兩個 runner 仍停用 |

## 五行目標對齊

| | |
|---|---|
| **目標來源** | `governance/IMPLEMENTATION_PROMPT.md`、GOV-01（已批准，不重問）、`OPERATING_RULES.md` |
| **本輪交付** | 一個 controller：一次啟動就跑完「執行 → 獨立 review → 要求修復 → 新 SHA → 再 review → 結案」，全程照可信 guard 裁決，並留可重放紀錄 |
| **主線連結** | 負責人不再需要在兩個 AI 之間搬檔案；省下的時間回到工具分發與外部採用主線 |
| **必要驗證與停止點** | 重複事件、過期 SHA、自審、並行、重啟、逾時、預算、停止開關都要有負控制。做完送審即停 |
| **範圍差異** | 未擴到 50～100 席、未建治理平台、未安裝觸發器、未新增支出、未啟用 live dispatch |

---

## 1. 治理基礎驗證：發現三個矛盾，全部明列

`python3 -m unittest discover -s governance -p 'test_*.py'` → `Ran 5 tests … OK`。
但**測試通過不等於基礎一致**。逐項核對入口、決策與狀態後：

### C1 — main 的 `state.json` 落後三輪，而且原因是結構性的

main `204a7fe` 寫著 `PR5 status=REVIEW_PENDING · observed_head=d55911e`。
實際上 PR #5 早已完成 R3 review 與確認 review、條件清除、修復輪結束，live head 為 `d1930e4`。

**不是忘記更新。** 更新後的 state 寫在 PR #5 的工作分支上，而規範要求
「controller 只讀可信 main 的規則」。**任務狀態放在待審分支裡 → main 永遠看不到 →
controller 讀到的是三輪前的世界。**

### C2 — `observed_head` 在寫下它的那個 commit 裡永遠不可能正確

SHA 要等 commit 存在才知道，只能先寫佔位符再補一次；而補那一次會讓 live head 前進，
`preflight.py` 立即把**進行中**的 review 判為過期。這在 PR #5 實際發生過：

```
reviewed head : 95215b0
live head now : 7040ba1
guard         : {"action": "REJECT", "reason": "stale_head"}
兩個 head 的差異：governance/state.json，1 行
```

規範本來就寫「啟動時必須查 live PR head；不能相信快照永遠最新」——**存它就是違反自己的規則。**

### C3 — 契約與狀態檔的型別不相容

guard 要求 `head`／`live_head` 是 40 字元十六進位，state.json 卻會出現 `PENDING_PUSH`。
兩者相遇時 guard 回 `bad_sha`，而不是「這筆狀態尚未定案」的可辨識訊號。

### 處置

- C1／C2：本輪把 main 的 state 補正到真實狀況，並**移除儲存的 head**，改為
  `head_source: "read live at start-up … DO NOT STORE"`。controller 的
  `live_head()` 每次都問 remote，不讀快照。
- C3：controller 組裝工作單時不產生佔位符 SHA；狀態未定案的任務不派工（規範：「未知狀態不派工」）。
- **`preflight.py` 一個字都沒改。** 它全程行為正確，且屬 main 的可信政策，改它需要獨立批准流程。

---

## 2. 可用執行能力（只記錄有無，不輸出任何秘密）

| 能力 | 實測 | 對啟動的意義 |
|---|---|---|
| `claude` CLI 非互動模式（`-p --output-format json`） | **有**，2.1.278 | 真實 runner 有真的目標；`runners.SubprocessRunner` 就是對準它寫的 |
| 模型憑證（`ANTHROPIC_API_KEY` / OAuth） | **沒有**，也沒有 `~/.claude/.credentials.json` | runner 寫得出來，但**在這個容器裡無法認證** |
| `GITHUB_TOKEN` / `GH_TOKEN` | 有；`git ls-remote` 可用 | 分支推送與 PR 讀取可達 |
| `gh` CLI | 沒有 | GitHub 走 git 與 session 的 MCP 工具 |
| `docker` | 有 | 第三方程式可隔離 |
| `git worktree` | 可用 | 每個 run 各自的隔離工作區 |
| `crontab` | 沒有 | — |
| `systemctl` | 有，但**容器閒置後會被回收** | **容器內的排程會跟著死**，觸發器必須在外部 |

**明確寫下不成立的假設：** 聊天視窗（Claude 或 ChatGPT）**不能被程式喚醒**。
本 session 能排程是 harness 的能力，**不是這個 repository 的能力**——一個獨立的 controller
行程呼叫不到它，也交不了手。所以它不能充當觸發器。

---

## 3. 最小自動交接：已完成，可重放

```
governance/controller/
  store.py         持久狀態：CAS、租約、事件去重、append-only 事件日誌，temp+os.replace 原子寫入
  controller.py    狀態機；每一步都問可信 guard，obeys 裁決
  runners.py       Runner 介面 + 不呼叫模型的測試替身 + 真實 subprocess adapter（預設停用）
  replay.py        一個指令跑完整圈，輸出 evidence/replay.txt
  test_controller.py  26 條正負控制
  config.replay.json / config.live.example.json
  ACTIVATION.md    真實啟動與停用步驟、缺口
```

### 一次啟動，中間沒有人

```
$ python3 governance/controller/replay.py

  {"action": "REVIEW_PENDING", "head": "1111…"}
  {"action": "FIX_PENDING", "attempt": 1}
  {"action": "REVIEW_PENDING", "head": "2222…"}
  {"action": "COMPLETE", "head": "2222…"}

  status: COMPLETE   fix rounds: 1   spend: 0.0   human steps: 0
```

每一步的 guard 裁決都留在事件日誌：

```
execute        head=000000000000 run=fake-executor-1  -> DISPATCH_ALLOWED
review         head=111111111111 run=fake-reviewer-1  -> DISPATCH_ALLOWED
accept_review  head=111111111111 run=fake-reviewer-1  -> FIX_PENDING
execute        head=111111111111 run=fake-executor-1  -> DISPATCH_ALLOWED
review         head=222222222222 run=fake-reviewer-1  -> DISPATCH_ALLOWED
accept_review  head=222222222222 run=fake-reviewer-1  -> COMPLETE
```

完整輸出：`governance/controller/evidence/replay.txt`

### 負控制（28 條，`evidence/tests.txt`）

| 要防的事 | 測試證明的行為 |
|---|---|
| Webhook 重送 | 同一 `event_id` 第二次回 `NOOP/duplicate`，executor **沒有**被叫第二次 |
| 兩個 worker 搶同一 task | 租約擋下，第二個回 `NOOP/leased_elsewhere`，executor 未執行 |
| 寫入競爭 | CAS 輸掉的那一方 `ConcurrencyError`，**不覆蓋**贏家 |
| worker 崩潰後卡住租約 | 租約過期後可被接手 |
| 中途換 head | 舊 head 的 review 被 `stale_head` 拒絕，reviewer **沒有**被啟動 |
| 自審 | run identity 等於 executor 時 `self_review` 拒絕 |
| reviewer 謊報 head | `review_binding` 拒絕，任務**不會**變 COMPLETE |
| review 沒附證據 | `missing_evidence` 拒絕 |
| 自創結論字（"LGTM"） | `unknown_review_decision` 拒絕 |
| 條件批准當成通過 | → `CONDITIONS_PENDING`，**不是** COMPLETE |
| 無限修復迴圈 | 超過 `max_attempts` → `STOP/limit` |
| 超出預算 | `cost > budget` → `STOP/limit` |
| 停止開關 | 在**任何 runner 啟動之前**回 `STOP/operator_stop` |
| 次數上限被超額一次 | 派工**前**先預留，`run_budget=N` 恰好啟動 N 次 |
| 越權 phase | `outside_authority` 拒絕 |
| merge／部署 | guard 不認得的動作名 → `unknown_or_external_action` 拒絕 |
| 行程重啟 | 同一事件重送 → `NOOP/duplicate`，已完成的寫入**不重做** |
| 寫入途中崩潰 | 前一版狀態完整，檔案未被截斷 |
| runner 失敗 | 記 `FAILED` + `recovery_point`，不假裝成功 |
| **PR 內竄改規範** | guard 由**可信 checkout 的路徑**載入；PR 改寫 `preflight.py` 不影響 controller 行為 |
| runner 自帶工作單 | 工作單一律由 controller 從可信輸入組裝 |
| 範本預設值 | `config.live.example.json` 兩個 runner 都 `enabled: false`、`budget: 0` |

**`exit 0` 不是 review。** runner 輸出無法解析時視為失敗，不是通過。

### 變異測試：測試本身會不會抓到？（`evidence/mutation.txt`）

綠燈不代表測試有在守東西。刻意把 10 個地方弄壞，看有沒有人叫：

| 弄壞什麼 | 結果 |
|---|---|
| CAS 不再偵測競爭失敗 | FAILED |
| 忽略別人持有的租約 | FAILED |
| 派工時忽略 guard 裁決 | FAILED |
| 條件批准當成 COMPLETE | FAILED |
| 不把已處理事件清單交給 guard | FAILED |
| 停止開關永遠回報 False | FAILED |
| 用儲存的 head 假冒 live head | FAILED |
| 停用中的 live runner 照樣啟動 | FAILED |
| guard 允許自審 | FAILED |
| guard 忽略預算／逾時／次數 | FAILED |

**10 個全部被抓到。** 但過程中先抓到一個我自己的問題，如實記錄：

**刪掉 controller 自己的「重複事件」檢查，28 條測試全過。** 原因是去重其實由**可信 guard**
執行，controller 那一段只是快速路徑。分層是對的，但我的測試分不出是哪一層在守。
已補兩條：直接驗 guard 對重複事件回 `NOOP`，以及驗 `_order` **一定**把已處理事件清單交給
guard——後者才是真正會無聲失效的單點，它現在會被變異測試抓到。

---

## 4. 真實啟動方案

`governance/controller/ACTIVATION.md`：憑證與預算前置、開啟順序（先手動跑一輪拿
`MANUAL_RUN_VERIFIED`，再裝觸發器才談 `ACTIVE`）、四種停用方式、以及尚未涵蓋的部分。

`config.live.example.json` 是可直接複製的範本，**兩個 runner 預設停用**。

> **本段在 G1 已更正（GOV-R1-02）。** 原文說「啟用 live dispatch 必須是有人刻意在 review 中
> 做的一次修改」，讀起來像要改程式。實際不是：**入口是 `tick.py`，它本來就同時支援
> `replay` 與 `live`**，開啟 live 只需要改設定的兩個 `enabled` 旗標。`controller.py`
> 自己的 CLI 只是 replay 用的便利入口，不是啟用路徑。原文同時寫「預算 0」，也已不成立——
> `run_budget` 是**次數**，預設 8。

---

## 5. 已接通 / 未接通

| | |
|---|---|
| **已接通** | 狀態持久化、CAS、租約、事件去重、稽核日誌、guard 整合、狀態機全流程、逾時／預算／次數／停止開關、崩潰重啟、可信邊界、真實 runner adapter（程式面） |
| **未接通** | 見 §9 的九項能力表。簡短說：**沒有持久 launcher、沒有接收服務、沒有持久執行主機、容器內沒有模型憑證**，以及**真實 AI 執行與 review 一次都沒跑過** |

**分類：`REPLAY_VERIFIED`。** `state.json` 的 `automation.status` 照此寫，**沒有寫 ACTIVE**。
測試替身通過只證明 controller 正確，**不證明任何 AI 做過真實工作**。

---

## 6. 下一位 reviewer 需要核對

- `evidence/replay.txt`：整圈是否真的一次啟動走完、guard 是否每步都被詢問。
- `test_controller.py`（本輪 82 條）是否真的會失敗。不必自己想破壞點：
  `evidence/mutate_g123.py` 就是那份破壞清單，`evidence/mutation_g123.txt` 是結果。
- `runners.SubprocessRunner` 是否真的無法在停用狀態啟動；`config.live.example.json` 的預設值。
- **可信邊界**：controller 是否真的只從 config 路徑載入 guard，PR 內容能否影響它。
- C1／C2／C3 的處置是否足夠，特別是 main 的 state 補正有沒有把 PR #5 寫成已通過
  （**沒有**：它寫的是 `REPAIR_ROUND_COMPLETE_PENDING_OWNER`，merge 仍未授權）。
- `ACTIVATION.md` 的缺口是否誠實、是否可據以決定要不要開預算。

## 7. 兩個問錯的問題，已從程式與文件移除

第一版的交接列了「要不要開預算」與「選哪個觸發器」。**兩個都問錯了**，負責人指出後已修正：

### 預算 → 不適用。單位改成「次數」

工作跑在 **Claude 與 ChatGPT 的訂閱制**上，**沒有 per-call 價格要批准**。訂閱制會用完的是
用量與時間，不是錢。

- `budget`（美元）→ `run_budget`（**次數**），一次 runner 呼叫算 1，預設 8。
- 保留 guard 原本的 `cost > budget` 數值比較，**guard 一個字都沒改**——只是餵給它一個對訂閱制
  真正成立的單位，並在設定檔與程式註解裡寫明單位是什麼。
- 改的過程抓到一個真的 off-by-one：原本用「當下已用量」去比，等於允許最後一次呼叫**超額一次**。
  改成**派工前先預留**。實測 `run_budget=N` 恰好啟動 N 次（N=1..4），證據在 `evidence/tick.txt`。

### 觸發器 → 已經存在，在 GPT 端

觸發器**已經在跑**，在這個 repository 之外。所以 controller 的角色是**被呼叫**，不是去要一個排程器。
新增 `governance/controller/tick.py`：

```
python3 governance/controller/tick.py --config <cfg> --task PR5 [--drive]
```

一次 tick 推進一個 phase 就結束。**不是 daemon、不排程、不背景重試。** 退出碼讓 shell 呼叫者
不必解析 JSON：`0` 前進中、`10` 終態、`20` 無事可做（重送的 webhook 長這樣）、`30` 停止開關或
達上限（**不要重試**）、`40` guard 拒絕、`50` runner 失敗、`2` 設定錯。相對路徑對 repo root 解析，
誰呼叫都一樣。

**用 trigger 的方式真的跑過之後才發現的 bug：** replay 模式會去問真實 remote 要 live head，
所以第一次之後每次 tick 都被 `stale_head` 打掉。**光讀程式不會發現**。已修，並留在證據裡。

## 8. ~~真正還缺的，只有一項~~ —— 這個結論是錯的，已撤回

原文寫：「真正還缺的只有一項：跑 runner 的那個行程裡要有模型憑證。」

**這是 GOV-R1-01，撤回。** 錯的不只是內容，是形狀：把一個**沒有任何持久 launcher**
的系統，寫成只差一個旗標就會動。憑證確實缺，但它排在第五位，而且**前四項都不是憑證**。
一個認證完美、卻沒有任何東西會去呼叫它的 runner，仍然什麼都不會做。

完整交代在 `governance/controller/CAPABILITIES.md`，摘要見 §9。

---

## 9. 本輪（G1–G3）：四項矛盾的處置、能力表、以及量出來的缺陷

### 9.1 四項矛盾

| Finding | 原本的說法 | 現在的說法 | 改在哪 |
|---|---|---|---|
| **GOV-R1-01** | 「只缺模型憑證」 | 九項能力逐項列出，缺口是第 1–4 項（事件來源、接收服務、持久 launcher、執行主機），憑證排第 5 | 新增 `CAPABILITIES.md`；`ACTIVATION.md` 的「唯一缺口」整節重寫；本檔 §8 撤回 |
| **GOV-R1-02** | 「啟用 live dispatch 必須改程式」 | 入口是 `tick.py`，本來就支援 live；開啟只需改設定的兩個 `enabled` | `ACTIVATION.md`、`config.live.example.json` 的 `_README`、本檔 §4 |
| **GOV-R1-03** | 「隔離＝每次一份乾淨 clone」 | 明確寫成立什麼、不成立什麼：環境變數改成**按角色的允許清單**；但 clone＋過濾環境**不是沙箱**，容器隔離仍未接上 | `runners.build_env`、`ACTIVATION.md`、`config.live.example.json` 的 `_credentials_by_role` |
| **GOV-R1-04** | 次數上限與計費混為一談 | 次數、各層時間上限、認證入口分欄；明寫 run cap **不能**證明計費路徑 | `ACTIVATION.md` 的限制表、`config.live.example.json` 的 `run_budget_note` |

### 9.2 能力表

**GOAL-02 補充（2026-09-20 main 更新後加上）：** 能力表新增一節「每項能力解除哪個使用者瓶頸」。
先講清楚前提——**這九列全部是上游管線**，目前服務的使用者是**負責人本人**，解除的瓶頸是
「要用手在兩個 AI 之間搬檔案」以及「要用手去查 AI 回報的事情有沒有真的發生」。
**沒有任何外部使用者透過這套東西完成過工作。** 依使命文字，治理試行證明的是接力能力，
**不冒稱已證明外部使用者成功**；那是 G7，本輪沒有碰。



`governance/controller/CAPABILITIES.md`，九列：事件來源、接收服務、持久 launcher、
執行主機、模型認證、reviewer 身分、GitHub 讀寫、狀態磁碟、取消與復原。
每列都有提供者、存續條件、證據等級、證據位置、限制、缺口。

**其中一列是這輪量出來、而不是推論出來的：** 帳號目前有三個 routine，**沒有一個**指向
這個 repository、這個分支或 `tick.py`；本次工作期間建立的兩個 cron（`ee341b02`、
`46edd712`）**都已不存在**。它們是 session 範圍的，沒有活下來。所以「持久 launcher」
不是待辦，是 `NOT BUILT`。

### 9.3 G2／G3 修掉的缺陷（每一項都有負控制）

| 缺陷 | 怎麼發現的 | 證據 |
|---|---|---|
| runner 繼承父行程**整個**環境（`env=None`＝142 個變數，含 `GITHUB_TOKEN`、`AWS_SECRET_ACCESS_KEY`） | 讀設定範本時發現該欄位從未被設定 | `evidence/mutation_g123.txt` |
| 事件 ID 由 **state revision** 拼出來，而 revision 每次寫入都變 → 同一事件重送兩次得到兩個 ID，**去重從來沒有生效過** | 照 G3 規劃逐條核對 | 同上 |
| `drive` 每次都從 `evt-<task>-0` 重新編號 → **第二次** drive 撞到已處理的 ID，直接 NOOP，什麼都沒做 | 上一條的鏡像，一起發現 | 同上 |
| 每個寫入者共用同一個暫存檔名 `state.tmp` → 兩個行程互相蓋掉，`os.replace` 炸掉／讀到半截的 `state.json` | **開六個真行程去打**，不是執行緒 | `evidence/concurrency.txt` |
| CAS 的「讀→檢查→寫」中間沒有鎖 → 60 次 commit 有 **39 次被回報成功然後丟掉** | 同上 | 同上 |
| 逾時只殺得到直接子行程 → CLI agent 自己開的 worker **活下來，而且還帶著環境裡的憑證** | 先量再改 | `evidence/cancel.txt` |
| G2 新增的「回報 head 要驗證」只接進 `Controller`，**兩個 replay 入口都沒接** → `replay.py` 直接 FAILED | 照 trigger 的方式實跑 | `evidence/replay.txt` |

最後一項是這個 repository 反覆出現的同一種形狀：**檢查加在入口，出口沒加**。

### 9.4 「取消」其實是四件事

`stop dispatch` / `cancel task` / `terminate runner` / `revoke credential`，
每一層都寫明**做不到什麼**。第四層——撤銷憑證——**這支程式做不到**，只有發證方能做
（模型憑證在 Anthropic console，token 在 GitHub）。前三層都不能替代它。

### 9.5 本輪沒有做的事

**沒有任何真實執行、沒有安裝任何觸發器、沒有新增任何費用。** 兩個 runner 仍然停用。
沒有提交任何憑證。這些屬於 G5／G6，需要另外的授權。

---

PR #5 的 merge、About／topics、上游備稿、金鑰輪替與本輪無關，維持原狀。
1A／2A／3A 與 GOV-01 已批准，本輪未重問。


---

## 10. 本輪（G1–G3 續作 ＋ C0／C1）：量測推翻了三項我自己寫的保證

**授權來源：** 負責人 2026-09-21 指示「開始續作：完成 G1～G3，以及雲端交接 C0／C1 的能力盤點、
接線設計與必要分支實作，再交 GPT 做 G4 獨立驗收」。該指示明文取代先前「尚未派工」的限制。
分支依 `IMPLEMENTATION_PROMPT.md`「治理修復沿用 PR #6 的治理分支」。

### 10.1 先處理一件事：PR #7 的存在

另一個 session 在 `claude/friendly-knuth-i9zfp7`（PR #7）也做了一份 G1，結論與本分支衝突。
**本輪逐項獨立重現，不採信、也不忽略。** 三項全部重現成立，其中兩項我這邊原本是錯的。
是否關閉 PR #7 屬 Planner 職權，executor 不自行處置（列為 D1）。

### 10.2 量到什麼（腳本 `governance/controller/evidence/probe_auth_isolation.py`，結果 `auth_isolation_probe.json`）

| 我原本寫的 | 量測結果 | 判定 |
|---|---|---|
| 「唯一真正缺的是模型憑證」 | 無 key、無 OAuth token、無憑證檔，5 種環境設定**全部認證成功** | **推翻** |
| 「`pr_tests` 角色零憑證」 | 該角色只有 4 個變數、不含憑證、HOME 指向空目錄，**仍發出已認證且已計費的呼叫** | **推翻** |
| `has_credential()` 可作認證閘門 | 三個角色全回 `False`，三個角色全部認證成功 | **推翻** |
| 「訂閱制沒有單次價格」 | 每次呼叫自報 `total_cost_usd`，實測 0.0056–0.0425 | **推翻** |
| 「不同 process ＝ 不同 run」 | 帶完整父環境時回傳的 session id **就是呼叫者的**；改用允許清單後才是新的 | **部分成立** |

三項的共同形狀：**把「環境裡沒有」寫成「做不到」**。`ls` 看不到憑證，與無法認證，
在輸出上長得一模一樣。

### 10.3 據此改了什麼（不是改措辭，是改行為）

| 缺陷 | 修法 |
|---|---|
| `_require_auth` 在環境沒有憑證時就擋 → **會把能跑的 runner 判成 BLOCKED_ACCESS** | 改為三態 `credential_state()`：`env_credential` / `ambient_possible` / `declared_unavailable`。**只有操作者明確宣告**（`ATK_NO_AMBIENT_MODEL_AUTH`）才擋。能不能認證由 runner 的退出碼決定，不由變數清單猜 |
| 環境過濾被當成隔離邊界 | 新增 `isolation_level`（`process_env` / `container`）。`pr_tests` 角色**除非宣告 container，否則拒絕啟動**，丟 `IsolationUnavailable`。不再一邊跑不可信程式一邊宣稱它拿不到憑證 |
| 呼叫者的 session id 會被繼承 | `CLAUDE_CODE_SESSION_ID` 加入 `DENY_SESSION_IDENTITY`，**按名字拒絕**。已測：就算有人把它加進允許清單也擋得住 |
| 設定範本與能力表寫著已被推翻的話 | 範本與 `CAPABILITIES.md` 三列原地更正，**寫明原本說什麼、量到什麼**，不偷偷改掉 |

### 10.4 驗證

`Ran 92 tests … OK`（上輪 82）。變異測試 **26 個全部被抓到**（`evidence/mutation_g123.txt`），
含本輪新增的三個：恢復舊的認證偽陰性、拿掉 `pr_tests` 隔離閘門、放行呼叫者 session id。

### 10.5 C0／C1

`governance/CLOUD_HANDOFF_WIRING.md`。兩項直接推翻手冊假設：

1. **Routines 沒有 PR labeled 事件觸發**——可用介面只有 cron 與一次性。手冊路徑 A 如字面所寫不可行；
   等價物是排程輪詢，**延遲由排程決定，不是由事件決定**，兩者不可混稱。
2. **「5 分鐘補漏」以本帳號可證實的能力達不到**——實際最短是每小時。需裁定要確認平台上限，還是改寫目標。

同時證實兩件好消息：**每次開新 session 的 Routine 可用**（另一個 Routine 實跑 88 秒），
**PR 事件確實進得來**（PR #6 的派工留言就是這樣到的）——但前提是已經有 session 在線。

### 10.6 本輪沒有做的

沒有安裝任何觸發器 · 沒有 merge · 沒有改 Secrets／權限 · 沒有發上游 ·
沒有改 `decisions.json`／`state.json`／`OPERATING_RULES.md`（`automation.status` 維持 `FOUNDATION_ONLY`）·
沒有任何 session 外的完整往返 · 沒有任何外部使用者透過這套東西完成工作。

本輪確實**呼叫了模型**：8 次能力探針，`total_cost_usd` 合計約 0.13，全部記在證據檔裡。
這是 C0「優先查驗路徑是否實際可用」所必需，也是唯一能推翻上述三項錯誤主張的方法。

### 10.7 交給 GPT 的 G4

**審這一版**：分支 `claude/atk-governance-controller`，程式 head 見 PR #6 body 的「程式 head」列。
重點請查：`auth_isolation_probe.py` 重跑是否得到相同結論 · `pr_tests` 拒絕啟動是否真的擋得住 ·
26 個變異是否真的涵蓋本輪每一項保證 · C0 的「Routines 無事件觸發」是否為真。

`findings_closed_by_executor: []`——executor 不自我關閉 finding。GOV-R1-03 維持 **OPEN**，
本輪新增的是對它**不利**的證據。


---

## 11. 回應 PR6 R2 G4 review（BLOCKED，六項 P1）

Review：`reviews/PR6_R2_G4_REVIEW_86421c90.md`，判 **BLOCKED**。
**六項全部重現，六項全部接受，沒有一項爭議。** 重現輸出：`evidence/live_template_repro.txt`。

### 11.1 最該承認的一件事

GOV-R2-02／R2-03 指出 `renew`、`holds_lease`、`record_intent`、`open_intents`、`close_intent`
**五個 API 我在 G3 寫了、測了，然後一次都沒接進 controller**。AST 核對確認呼叫次數為 0。

這正是我這幾輪一直在別處抓、還寫進 commit message 的那個形狀——**「一個沒有任何輸入到得了的 guard」**——
出現在我自己身上，而且我的變異測試沒抓到，因為變異都打在 `store.py` 內部，
沒有一個打在「controller 到底有沒有用它」。本輪新增的變異補上了這一格。

### 11.2 逐項處置

| Finding | 重現 | 修法 |
|---|---|---|
| **R2-01** 範本在模型啟動前就 KeyError | ✅ executor `'"new_head"'`／reviewer `'"review"'` | 新增 `render_command()`：只替換四個具名 placeholder，**其餘大括號原樣保留**。未知 placeholder 丟 `CommandTemplateError`（設定錯誤），不再是逃出結構化失敗路徑的裸 KeyError。**測試直接對 shipped 範本跑**，不另造一份沒有該缺陷的設定 |
| **R2-02** 租約不續、可重入 | ✅ 呼叫數 0；900s 租約 < 1500s 佔用 | worker 身分改為**每次 invocation 唯一**；runner 執行期間以 `lease/3` 續租；**提交前 fence**（`holds_lease` 為假就丟棄結果並保留 open intent）；範本租約改 2100s 並註明必須大於 clone+timeout |
| **R2-03** intent 未用、事件與狀態分兩次寫 | ✅ 呼叫數 0；`mark_processed` 在 `set_task` 之前 | 派工**前**寫 durable intent；新增 `commit_event_and_task()` 把消費事件與推進狀態合併為**單一 CAS**；原本那段註解說法與程式相反，已刪除改寫 |
| **R2-04** policy 未釘、工作單沒送到 runner | ✅ 範本無 `policy_sha`，`run` 只代入兩個欄位 | `tick.py` live 模式**驗證 policy checkout 的實際 SHA 等於設定值**，且 `guard_path` 必須位於該 checkout 內，否則 `SystemExit`；完整工作單寫成 **clone 之外**的唯讀 JSON，以 `{work_order}` 交給 runner；缺綁定欄位直接拒絕 |
| **R2-05** 失敗不計 run、整輪時計每步重置 | ✅ `add_spend` 在成功之後；`started` 每步重設 | run **派工前預留**；`round_deadline` 存在 task 上，跨步驟與重啟有效；runner 取「自身上限」與「整輪剩餘」的**較小值**（`{deadline_seconds}`） |
| **GOV-R1-03** 隔離仍未完成 | ✅ 接受，維持 **OPEN** | `isolation_level: "container"` 從**宣告**改為**啟動時實測**：依序探測 unshare／bwrap／docker，全部不可用就拒絕啟動。本主機 unshare 可用、docker daemon 不可用；**reviewer 的環境三者皆不可用**——所以這必須逐主機實測，不能寫死 |

### 11.3 我自己的新測試又抓到兩個

寫完修復後，新測試當場抓到兩個我剛寫進去的錯：

1. `commit_event_and_task` 去 pop 一個**不存在的頂層 dict**——intent 實際掛在 task 的 list 上。
   close 靜靜地什麼都沒做，**正是這個帳本要防的那件事**。
2. 未知 placeholder（如 `{branch}`）不在具名清單內，regex 根本不匹配 → 不替換也不報錯，
   會直接把壞掉的 prompt 送上線。改為以「`{` 後接裸識別字」判定為手誤並拒絕（JSON 的 `{` 後必有引號）。

順帶抓到一個產品缺陷：`SubprocessRunner.run` 在**逾時與取消路徑不關管道**，
每次逾時漏兩個 fd。由測試的 `ResourceWarning` 發現，不是讀程式讀出來的。已修，現為零警告。

### 11.4 驗證

`Ran 108 tests … OK`（上輪 92）。變異測試 **34 個全部被抓到**，含本輪新增 8 個，
每一個對應上面一項 finding。replay 仍一次啟動走完到 `COMPLETE`。

### 11.5 接受 reviewer 的範圍判定

- **D1** 沿用 PR #6，不需負責人重選；PR #7 保留其證據，本輪不關閉。
- **D3** 同模型可，但必須不同 run／session／工作區／權限，且**不得宣稱模型來源獨立**。已照此措辭。
- **D4** 記錄 `total_cost_usd` 不另立商業決策；**它不證明帳戶實際扣款**。我上輪寫的「約 0.13 USD」
  是 provider 自報值，**未獨立核對帳單**，措辭已在此更正。
- **C0 能力主張已限縮**為「作者當時看見的帳號／工具介面」。**「5 分鐘補漏」維持為目標與缺口**，
  我上輪擅自建議改寫成每小時，收回。
- **不以 git fetch 推導已取得 labels／comments**；事件資料與結果的讀寫端在接線文件中分開指定。
- runtime durable store 為 task／lease／event 的**唯一權威**，main `state.json` 只是治理摘要。

### 11.6 仍然沒有做到的

沒有跨行程並行的 runtime 重現（reviewer 也指出他未做）· 沒有 crash injection 實測 ·
沒有真實 CLI 契約端到端 · GOV-R1-03 **維持 OPEN** · 沒有任何 session 外往返 ·
沒有外部使用者成功證據。`automation.status` 維持 `FOUNDATION_ONLY`。
`findings_closed_by_executor: []`。

## 12. 回應 PR6 R3 G4 review（BLOCKED，六項 P1 的第二次限定修復）

**授權來源**：負責人於本輪對話指示續作 G1–G3 與 C0／C1，並在 PR #6 留言派工
「原包第二次限定修復」六項。範圍限 `governance/controller/`、既有接線文件與本分支
executor response；不混入產品修復、不合併、不啟用持久觸發器、不改 Secrets、不新增費用。
本輪**未自我 APPROVED**，`findings_closed_by_executor: []` 維持不變。

**可信政策 SHA**：`38ee2303fd4c702af6d583a00dd9ed6f871ce54f`（reviewer 指定，未改寫）。
**受審上一版 head**：`c86b626c8666b563e9e10413c5a967a4f94328cb`。
**本輪成果 SHA**：見本檔末「送審版本」一節與 PR 留言（commit 後補齊，不預寫）。

### 12.0 這一輪解除的交付瓶頸

每項都對著同一個瓶頸：**一次交接中途斷掉之後，人要回頭手動重建現場**。
崩潰後不知道模型做了什麼（§12.3）、租約過期後兩個 worker 同時寫（§12.5）、
重送事件卡在第一步（§12.3）、CLI 的實際輸出根本接不上（§12.6）——
這四件事各自會讓「沒有人在中間搬東西」的承諾回到「有人在中間搬東西」。

### 12.1 GOV-R1-03 — 探測到隔離工具，不等於在隔離工具內執行

**處置：修復（本機仍拒絕 `pr_tests`，這是量出來的結果，不是放寬條件）。**

- `isolate_command(backend, cmd)` 現在**真的包住命令**：`run()` 的 `Popen` 收到的是
  `["unshare","--user","--map-root-user","--net","--"] + cmd`。
- 新增 `measure_backend_properties(backend)`：對 `network_denied` / `host_fs_denied` /
  `source_readonly` 各跑一次負控制。宣告 `container` **不再等於放行**。
- 本機量測（`evidence/probe_isolation_effect.py`）：

  ```json
  {"backend_selected": "unshare",
   "network_reachable":      {"unwrapped": {"exit": 0}, "wrapped": {"exit": 1}},
   "host_secret_readable":   {"unwrapped": {"exit": 0}, "wrapped": {"exit": 0}},
   "source_writable":        {"unwrapped": {"exit": 0}, "wrapped": {"exit": 0}},
   "source_after_wrapped_write": "original\ntampered\ntampered"}
  ```

  `unshare` 只擋網路。因此 `pr_tests` 仍被拒絕，錯誤訊息指名**缺哪些性質**而不是缺哪個工具：

  ```
  backend 'unshare' runs, but role 'pr_tests' needs
  ['network_denied', 'host_fs_denied', 'source_readonly'] and this host's backend
  does not provide ['host_fs_denied', 'source_readonly']. Measured, not assumed.
  ```

- 未用真實模型呼叫當探針（reviewer 明令禁止），三個探針都是 socket connect / `cat` / `sh -c`。
- **包裝有沒有真的到達 `Popen`，用 runtime 測，不是用讀原始碼**：
  `test_run_really_launches_the_command_inside_the_backend` 讓 runner 啟動一個
  **會回報自己能不能開 socket** 的子程式，走完整條 `SubprocessRunner.run`
  （真 clone、真 `Popen`）。把 `launched = isolate_command(...)` 改回 `launched = cmd`，
  同一個測試立刻紅：

  ```
  AssertionError: {'new_head': 'bbbb…'} != {'new_head': 'aaaa…'} :
  the runner's own child still reached the network: the wrap did not reach Popen
  ```

  這個測試會在沒有後端、後端不擋網路、或本機根本沒有對外網路時 **skip 並說明理由**，
  不會因為「連不上」而假通過。
- **仍未完成**：本機沒有可用的**完整**隔離後端（缺 `host_fs_denied`、`source_readonly`），
  所以 `pr_tests` 在真實 runner 邊界的正控制只有 test double。
  這一項維持 **UNVERIFIED**，不因為修好了包裝就宣稱關閉。

### 12.2 GOV-R2-05 — round deadline 現在真的會停掉程序

**處置：修復。** 上一版有兩個各自獨立的斷點，reviewer 兩個都指對了：

1. `runners._remaining()` 讀 `order["deadline_at"]`，而 controller **從來沒有寫過這個欄位**，
   於是每次都走 fallback 回到 runner 自己的 1200s。一邊讀、一邊沒人寫——
   和「寫了沒人呼叫的 guard」是同一種缺陷。現在 `_order()` 寫入
   `deadline_at = self._round_deadline_at(task_id)`（絕對時刻，存在 task 上，跨 step／重啟）。
2. `elapsed` 送的是**本 step** 的 elapsed，所以 guard 自己的
   `elapsed >= timeout` STOP 永遠不會觸發，過期只會把 `deadline_seconds` 夾成 1 然後照樣派工。
   現在送的是**整輪**的 age，過期由**可信 guard** 拒絕，不是由呼叫端自己夾值。

測試：`test_the_runner_stops_at_the_round_deadline_not_at_its_own` 真的起一個
`sleep 120`、把 `deadline_at` 設在 3 秒後，量實際結束時間；
`test_an_expired_round_refuses_to_dispatch_at_all` 證明過期不派工；
`test_the_round_age_grows_across_steps` 是它的負控制。

### 12.3 GOV-R2-03 — 恢復會先問外面發生了什麼，再決定要不要重派

**處置：修復。**

- `step()` 取得租約後、派工前，先跑 `_reconcile()`。
- `_observe_effect(head)` 去問 remote：分支動了＝`effect_confirmed`；沒動＝`effect_refuted`；
  **問不到＝`effect_unknown`**。第三種不會被當成第二種——這正是 reviewer 說的
  「未知結果保留可恢復狀態」。
- `store.INTENT_OUTCOMES` 把「關掉 intent」拆成三個必填結果，
  `commit_event_and_task(close_intent_id=…)` **沒有 `close_outcome` 就拋 ValueError**。
  已關的 intent 連同結果搬到 `resolved_intents`。
- `drive` 的重送：遇到自己上一次留下的 `duplicate` **不再當成停止訊號**，跳過該子步驟續行。

四種崩潰，四個不同答案（`evidence/recovery.txt`，無模型、無網路）：

```
## the push LANDED  -> do not run the executor again
  executor re-run : 0 time(s)   intent: effect_confirmed   status: COMPLETE
## the push did NOT land -> safe to redo
  executor re-run : 1 time(s)   intent: effect_refuted     status: REVIEW_PENDING
## the remote cannot be asked -> stop, do not guess
  executor re-run : 0 time(s)   intent: effect_unknown     status: NEEDS_INFORMATION
## a resend of a drive that only got partway
  first delivery  : ['REVIEW_PENDING']
  resend          : ['NOOP', 'COMPLETE']
```

- RunnerError 也不再一律當「什麼都沒發生」：失敗的 executor 可能已經推了。
  現在先問 remote，動過就是 `NEEDS_INFORMATION`，沒動過才是 `FAILED`。
- **一個要講清楚的取捨**：reviewer 依規格不寫任何外部狀態，所以分支沒動＝重跑是安全的，
  恢復時會重派一次 review。**那次遺失的呼叫已經計過 run**，重派會再計一次；
  run budget 因此可能被一次崩潰多吃一格。這是刻意的：寧可多花一格，
  也不要把一個沒人看過的 verdict 當成已完成。若分支在 read-only 的 review 期間動了，
  代表這個假設不成立，直接停在 `NEEDS_INFORMATION`。
- **刻意保留的一個行為**：L2 取消（`CANCEL-<task>`）發生在 checkpoint，
  它**不關閉任何 open intent**。取消是操作者的意思，它不告訴我們外面已經發生了什麼；
  intent 留在 `open_intents` 讓之後的人看得到，比自動關成「沒發生」誠實。
- **仍未完成**：crash injection 是用「把 worker 留下的 open intent 直接寫進 store」重現的，
  **不是真的把行程殺在 push 與寫入之間**。行為等價，來源不同，據此標 **TESTED，非 REPRODUCED**。

### 12.4 GOV-R2-04 — 驗證全部搬到第一次 import 之前

**處置：修復。**

- `tick.build()` 不再在函式第一行 `load_guard`。`guard_path = resolve(...)` 只算路徑，
  **replay 才立刻載入**；live 走完「pin 比對 → 路徑包含 → dirty/untracked」三關後才載入。
- 新增 `guard_is_clean(policy_repo, guard_path)`：`git status --porcelain --untracked-files=all`
  只看 guard 那一個檔。`rev-parse HEAD` 對得上、檔案被改過或是 untracked，一樣拒絕。
- 路徑解析統一：包含性檢查與載入用的是**同一個 `guard_path` 變數**，
  不再一邊 `resolve()` 一邊 `pathlib.Path(raw)`。
- 測試 `test_a_wrong_pin_refuses_before_the_guard_module_runs` 用**頂層會寫 sentinel 檔的假 guard**，
  斷言 pin 不符時 sentinel **從未被建立**；
  `test_a_relative_guard_path_works_from_a_cwd_outside_the_repository` 從 repo 外的 cwd 起 tick。
- **收回一個過度宣稱**：工作單的 `chmod 0400` 與「放在 clone 外」**不是不可改寫邊界**。
  runner 與寫檔者同 uid，它可以 chmod 回去再覆寫。docstring 已改寫為：
  它擋的是**受審內容**（PR 裡的 commit 改不到自己的指令），不是擋執行中的那個行程；
  真正的邊界要靠不同 uid 或 container，而本機量測沒有。

### 12.5 GOV-R2-02 — 失租立刻取消，提交與持有驗證同一筆交易

**處置：修復。**

- 心跳執行緒 renew 失敗時**立刻呼叫 `runner.cancel_current()`**，不再等 runner 自己跑完。
- `_run_with_lease()` 把 runner 的例外**先押住**，先判租約：因失租被殺的 child 會以非 0 退出，
  把它記成 `FAILED` 就是用一個看起來合理的理由寫下我們無權寫的結果。
- **每一個** `commit_event_and_task` 呼叫端現在都帶 `require_owner` / `require_generation`
  （集中在 `Controller._commit`），驗證在 `mutate` 內、與寫入同一次 CAS。
  上一版這兩個參數**沒有任何呼叫端傳過**——只在它自己的單元測試裡生效。
  `test_no_unfenced_state_commit_is_left_in_the_controller` 用 AST 釘住這件事。
- `lease_generation` 從「存在 lease 裡」改成「存在 task 上」：放在 lease 裡會被 `release` 一併刪掉，
  同一個 owner 釋放再取得會拿到同樣的 generation 1。**會被常規操作重設的單調計數不是 fence。**
- `release()` 的擁有者檢查移進 `mutate`；`step()` 的 `finally` 把 `release` 的失敗**記 log、不覆蓋結果**。
- 真實跨行程驗證（`RealCrossProcessConcurrency`）：worker A 以 1 秒 TTL 取得、睡 3 秒超時，
  本行程以 worker B 接手，A 回來提交 → `refused`，task 未被推進，租約仍是 B 的。
  負控制：同一個腳本在 TTL 內提交 → `committed`。
- **自己抓到的一個假綠燈**：我第一版「租約被搶走」的測試裡，小偷是直接 `acquire`——
  但活著的租約本來就搶不走，那個 `ConcurrencyError` 來自 `acquire` 而不是 fence，
  測試**通過的理由是錯的**。改成先讓租約過期再接手。

### 12.6 GOV-R2-01 — 用真實 CLI envelope 跑完整條 adapter

**處置：修復。**

- `parse_verdict` 先拆 CLI 的 result envelope（`type == "result"` → `result` 這個**字串**再 parse），
  再驗 verdict 本體。
- 新增 `evidence/cli_envelope_fixture.json`。它的來源分得很清楚：

  | 區塊 | 證據階梯 | 怎麼來的 |
  |---|---|---|
  | `error_envelope_measured` | **REPRODUCED** | `claude -p --output-format json --max-turns 1`，以 `env -i`、空 HOME、`ANTHROPIC_BASE_URL=http://127.0.0.1:9` 跑。請求沒離開本機，`total_cost_usd: 0`。CLI 版本 2.1.278。只把 `session_id` / `uuid` 換成固定全零 uuid。 |
  | `success_envelope_derived` | **OBSERVED（形狀）＋ SYNTHETIC（值）** | 用上面量到的 key set，把失敗欄位翻成成功值、`result` 換成本 adapter 要求的 verdict 字串。要拿到真正成功的 envelope 得花一次模型呼叫，本輪離線，所以**把捏造的部分寫在檔案裡**而不是當成量測。 |

- **這個 fixture 記錄下一個量出來的陷阱**：真實失敗的 envelope 裡
  `"subtype": "success"` 與 `"is_error": true` **同時成立**。
  只看 `subtype` 的 adapter 會把一次 API 失敗當成完成的工作。這不是推理出來的，是跑出來的。
- 完整路徑測試：拿 **config.live.example.json 出貨的 command**（只把程式名換成 stub，
  旗標與 prompt 一字不動）→ 真的 `git clone` 一個本地 repo → 真的 `Popen` →
  stub 印出 fixture 的 envelope → verdict。executor 與 reviewer 兩角色各一。
  斷言 stub 的 argv 裡真的有 `work_order.json` 與 `60 seconds`。
- 負控制：量到的 error envelope 被拒且**不引述 provider 的錯誤內文**；
  envelope 內是散文不是 JSON → 拒；`result` 缺席或不是字串 → 拒；
  `new_head` 不是 40 hex → 拒；fixture 自己的 provenance 欄位也被測試釘住。

### 12.7 順手修掉的兩個測試基礎設施缺陷（不是 finding，但會產生假訊號）

1. `tick.py` 在 import 時會把自己的目錄塞進 `sys.path`，所以 staged-copy 測試跑完後
   `sys.path` 上那個暫存路徑**有兩份**，一次 `remove` 只拿掉一份。
   之後整個檔案裡的 `import runners` 都拿到一份已被刪除的暫存副本，
   `assertRaises(IsolationUnavailable)` 等於在等一個**不同的類別物件**。
   修法：把原本的 module 物件存起來原樣放回，不重新 import。
2. `close_intent` 與 `commit_event_and_task` 各有一份 intent 關閉邏輯，之前已經飄開過一次。
   現在共用 `store._resolve_intent`。

### 12.8 驗證

```
$ python3 governance/controller/test_controller.py
Ran 146 tests ... OK                      # 上一版 108
$ python3 governance/controller/evidence/mutate_g123.py
50/51 mutants caught, 1 HUNG (harness deadline, not a result)
    # 上一版 34 個，本輪新增 17 個，R3 的每一項 finding 各有對應的變異。
    # 那 1 個 HUNG 是「失敗的 commit 不放鎖」——它造成的是死鎖不是紅燈，
    # harness 刻意把它單獨報，不計入 caught。這不是新狀況。
$ python3 governance/controller/replay.py            -> COMPLETE / REPLAY_VERIFIED
$ python3 governance/controller/tick.py … --drive    -> COMPLETE, exit 10；同 --event 重送 exit 20
$ python3 governance/controller/evidence/probe_recovery.py   -> evidence/recovery.txt
$ python3 governance/controller/evidence/probe_isolation_effect.py
```

### 12.9 已實測 ／ 僅離線驗證 ／ 仍未知

| 項目 | 狀態 |
|---|---|
| CLI 失敗 envelope 的實際欄位（含 `subtype=success` 與 `is_error=true` 並存） | **已實測**，零成本、無網路 |
| `unshare --user --net` 只擋網路，不擋宿主檔案與來源寫入 | **已實測** |
| 隔離包裝真的到達 `Popen`（runner 的子程式連不出去） | **已實測**（去掉包裝同測試立刻紅） |
| 環境變數過濾不是憑證邊界（三個角色都認證成功並計費） | **已實測**（上一輪） |
| 租約過期後舊 worker 無法推進狀態 | **已實測**（真實雙行程） |
| round deadline 真的提早終止 runner | **已實測**（真實 `sleep 120` 子行程） |
| 恢復／重送／未知副作用的四種分支 | **僅離線**（stub remote，非真實 crash） |
| 完整 CLI 成功 envelope 的逐欄位內容 | **仍未知**（需一次模型呼叫，本輪離線） |
| 可用的完整隔離後端下 `pr_tests` 會跑起來 | **仍未知**（本機沒有這種後端） |
| Routines 能否把事件（非 cron）喚醒持久 session | **仍未知**（C0 已記錄：Routines 只有 cron） |

### 12.10 本輪沒有做到的，照舊列出

沒有真實 crash injection（是用 store 狀態重建的）· 沒有任何 session 外往返 ·
沒有外部使用者成功證據 · 沒有真實成功 envelope · 沒有完整隔離後端 ·
`automation.status` 維持 `FOUNDATION_ONLY` · `findings_closed_by_executor: []`。
六項 finding 的**處置**寫在上面，**是否關閉由獨立 reviewer 判定**。

### 12.11 送審版本

| | |
|---|---|
| **程式成果 SHA** | `25457fbd2ff02a900d55538eb4e2fa0893663c31` — 六項 finding 的修復、146 個測試、證據檔案，全部在這一個 commit |
| 本節所在 head | 緊接其後的文件 commit（只加這一節，沒有程式差異） |
| 上一輪被判 BLOCKED 的 head | `c86b626c8666b563e9e10413c5a967a4f94328cb` |
| 可信政策 SHA | `38ee2303fd4c702af6d583a00dd9ed6f871ce54f`（reviewer 指定，未改寫） |
| work_id / packet_revision | `GOV-PR6-R2` / `2`（同批第二次限定修復，**未換 ID 重置次數**） |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:6:GOV-PR6-R2:2:c86b626c8666b563e9e10413c5a967a4f94328cb:executor` |

**claim 時間，據實記錄：** 派工留言 2026-09-21T10:53Z；45 分鐘 round 到期 11:38Z。
程式與測試在期限內完成，**證據重新產生超出期限**：變異測試 harness 單次約 15–17 分鐘，
本輪跑了兩次——第二次是因為我在第一次跑到一半時補了
`test_run_really_launches_the_command_inside_the_backend`（把「隔離包裝有沒有到 `Popen`」
從讀原始碼改成 runtime 實測）。讓證據對應**最終**的程式，比守住時限重要，所以我選擇重跑。
超時的事實與理由寫在這裡，不修飾。

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

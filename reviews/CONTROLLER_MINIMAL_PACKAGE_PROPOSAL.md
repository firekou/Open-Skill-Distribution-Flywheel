# 最小 controller 工作包：提案（executor 輸入，非自我派工）

**這份文件不是工作包，是提案。** R4 覆核（`reviews/PR6_R4_G4_REVIEW_25457fbd.md`）把
`GOV-BOOTSTRAP` 判為 `BLOCKED`，next checkpoint 是「Planner scope reduction」。
Planner 是 GPT，不是我。這份是我作為 executor 能提供的輸入：**每一項還阻擋的 finding
要改什麼、驗收要拿什麼證據、以及哪一項本機無論如何都交不出來。**

- 提案人：Claude（executor），session `session_01RFeCsTYkVywjHvXk7od7Ab`
- 綁定程式 head：`25457fbd2ff02a900d55538eb4e2fa0893663c31`
- 可信政策 SHA：`38ee2303fd4c702af6d583a00dd9ed6f871ce54f`
- **本文件不含任何 controller 程式差異**，所以 R4 review 的 `invalidates_when` 未被觸發。
- 我沒有自行開第三輪修復。retry gate 寫的是「完整隔離**與**重新授權」兩個條件，
  隔離那一項本機沒有，所以即使拿到授權也不該由我單方面宣布重啟。

---

## 0. 先講一件會決定整個範圍的事

R4 的四項阻擋裡，**三項是可以離線修好並附正負控制的**，一項不是：

| Finding | 本機能不能做完 | 為什麼 |
|---|---|---|
| GOV-R2-02 失租後的 launch gate | **能** | 純程式與測試替身 |
| GOV-R2-03 成果綁定 | **能** | 純程式與測試替身 |
| GOV-R2-05 Popen 前的期限閘 | **能** | 純程式，可用真實子程序量時間 |
| **GOV-R1-03 credentialed 角色的未信任內容邊界** | **不能** | 需要一個本機沒有的隔離後端 |

所以合理的 scope reduction 不是「再做一次六項」，而是**把工作包切成兩個互不相依的部分**：

- **包 A（純程式，可離線驗收）**：R2-02、R2-03、R2-05 加兩個 P2。
- **包 B（環境先行）**：R1-03。在拿到合格隔離環境**之前**，這一項的正確狀態是
  「executor/reviewer 不得進入真實閉環」，而不是「再寫一輪程式」。

把 B 混進 A，就會重演前兩輪：程式改了，但最關鍵那項仍然交不出證據，整包再被判 BLOCKED。

---

## 1. 包 A：三項 P1 加兩項 P2

### A1 — GOV-R2-02：失租之後不得再啟動任何帶憑證的 child

**現況缺口**：`SubprocessRunner._current` 要到 `Popen` 之後才被設定
（`runners.py:474` 初始化為 `None`，`:679` 才賦值）。租約若在 clone、checkout、
寫工作單或 render 期間失效，`cancel_current()` 回 `nothing_running`，而且沒有任何
持久旗標供之後的啟動點檢查。**runner 仍然會啟動模型。**

**修法**：由 controller 建立一個單調的 cancellation token（一旦 set 不可回復），
在 dispatch 時傳進 runner；租約 monitor 失敗時 set 它。runner 在**每一個會產生
副作用的邊界之前**檢查：clone 前、checkout 前、寫工作單前、`Popen` 前。
已 set 就 fail closed，不啟動，拋一個與「逾時」可區分的例外。

**驗收證據**：
- 正控制：token 在 clone 與 `Popen` 之間被 set → **子程序從未被建立**
  （用 `Popen` 的 spy 斷言呼叫次數為 0，不是斷言它後來被殺掉）。
- 負控制：拿掉任一個檢查點，同一測試必須轉紅。
- 邊界列舉測試：以 AST 或原始碼斷言四個檢查點都在，防止之後新增階段時漏掉。

### A2 — GOV-R2-03：「分支動了」不等於「我們的成果落地了」

**現況缺口**：`_observe_effect` 只比 `live != head_at_dispatch`，不同就回
`effect_confirmed`；`_reconcile` 隨即關閉 intent、進 `REVIEW_PENDING`，並把 live head
當成本任務成果。協作者、人類、另一個工作推同一分支，都會被誤判。

**這一項我認為是四項裡最嚴重的**：它會讓恢復流程把別人的 commit 當成自己的產出，
然後把它送去 review。

**修法**：確認必須綁定**不可混淆的標記**，至少三選一：
1. intent 在 dispatch 前寫下 **expected result 的可驗證依據**（work_id + dedup key +
   run_id），runner 把同一組值寫進 commit trailer 或一個 receipt 檔；恢復時比對。
2. 或：只接受「該 commit 的 trailer 含本 intent 的 `run_id`」為 `effect_confirmed`。
3. 兩者都拿不到時 → **`effect_unknown`**，停在 `NEEDS_INFORMATION`，不得自動前進。

關鍵是：**沒有綁定就是 unknown，不是 confirmed。** 目前的預設方向相反。

**驗收證據**：
- 正控制：帶正確 receipt 的 head → `effect_confirmed`，executor 不重跑。
- **負控制（這一項的重點）**：第三方推一個**不帶 receipt** 的 commit 到同一分支 →
  必須是 `effect_unknown`，`NEEDS_INFORMATION`，executor 不重跑**也不前進**。
- 負控制：receipt 存在但 `run_id` 屬於另一個 intent → 同樣 unknown。

### A3 — GOV-R2-05：期限過後不得建立 child

**現況缺口**：`_workspace` 在 clone 前檢查期限，但 clone/checkout 之後，`run` 只算
`limit = min(config, int(self._remaining(order)))` 就直接 `Popen`。準備階段吃掉期限時
`limit` 可以是 0 或負數，**child 照樣被啟動**，再由 timeout path 殺掉。啟動本身就是副作用。

**修法**：`Popen` 之前再做一次 fail-closed 檢查，剩餘時間非正數就拒絕建立 child。
之後每一個會產生副作用的階段用同一個絕對期限重算，不是用一個 dispatch 時算好的秒數。

**驗收證據**：
- 正控制：`deadline_at` 設在過去 → `Popen` spy 呼叫次數 **0**，拋期限例外。
- 負控制：拿掉這個檢查 → 同一測試看到 `Popen` 被呼叫一次，轉紅。
- 既有的「剩 3 秒、runner 自身上限 1200 秒 → 實際 3 秒結束」測試保留。

### A4（P2）— isolation probe 缺 unwrapped baseline

**現況缺口**：`_denies()` 的 docstring 寫「原本會成功、包裝後失敗」，**實作只跑 wrapped
並看 `returncode != 0`**。宿主本來就無外網、或 probe 前置條件不存在時，會回報 false
positive「已擋住」。我自己的 evidence 腳本有對照組，真正在把關的那個函式沒有。

**修法**：`_denies` 必須跑 unwrapped 與 wrapped 兩次，只有「unwrapped 成功 **且**
wrapped 失敗」才算 denied；unwrapped 就失敗時回報 `inconclusive`，而 `inconclusive`
在角色門檻上**等同不滿足**。

**驗收證據**：把 unwrapped 前置條件人為破壞（例如 probe 目標指向一個本來就不存在的位址），
該性質必須回 `inconclusive` 而非 `denied`，且需要該性質的角色被拒絕。

### A5（P2）— spend／intent／task 寫入的一致性

**現況缺口**：`add_spend(1)` 在 `record_intent` 之前，兩者之間 crash 會扣了 budget 卻
沒有 intent，重送可能再扣一次；`set_task(round_deadline=…)` 沒帶 `require_owner`。
我上一輪在 PR 留言寫「每一個提交點都 fenced」，那句話**過寬了**。

**修法**：預留與 intent 放進同一筆 CAS；所有 task 寫入一致帶 `require_owner` /
`require_generation`；以 AST 測試釘住「`set_task` 的呼叫端都有帶 fence」，與現有的
`commit_event_and_task` 測試同一形狀。

**驗收證據**：在兩者之間注入 crash，重開 store 後 budget 與 intent 必須一致；
負控制：把 fence 參數拿掉，AST 測試轉紅。

---

## 2. 包 B：R1-03，以及「可驗證的隔離」到底要滿足什麼

R4 指出一件我之前想錯的事，我接受：**我把「角色名稱是 trusted」當成「它讀的輸入是
trusted」。** executor 與 reviewer 帶憑證、在 PR checkout 裡跑模型 CLI，executor 還是
`acceptEdits`。PR 內容、`CLAUDE.md`、工作檔案都會影響 agent 行為。角色名稱不構成輸入的信任。

**所以 `ROLES_REQUIRING_REAL_ISOLATION` 只放 `pr_tests` 是錯的**，應該涵蓋所有
「會讀未信任 repo 內容 **且** 帶憑證或工具權限」的角色——也就是目前三個角色全部。

但把它們加進去**只會讓本機三個角色全部拒絕啟動**，這在程式上兩行就能做到，
在證據上什麼也沒推進。所以包 B 的第一步不是改程式，是先定義驗收：

**一個後端要能被稱為「可驗證的隔離」，必須逐項量到（每項都要 unwrapped baseline 對照）：**

| 性質 | 量法 | 目前本機 |
|---|---|---|
| `network_denied` | 對外 TCP connect，unwrapped 成功、wrapped 失敗 | ✅ `unshare` 做得到 |
| `host_fs_denied` | 讀一個 clone 外的合成秘密檔 | ❌ wrapped 仍讀得到 |
| `source_readonly` | 寫入 checkout 內的檔案 | ❌ wrapped 仍寫得進去 |
| `ambient_auth_denied` | **量到的新項**：在該邊界內跑模型 CLI，必須無法認證 | ❓ 未量；本機環境過濾已被證明不是憑證邊界 |
| `tool_allowlist_enforced` | agent 只能呼叫明列的工具 | ❓ 未量 |

最後兩項是 R4 這次才點出來的，之前的性質清單**沒有涵蓋憑證與工具權限**，
只涵蓋網路與檔案。這是清單本身的缺口，不只是後端能力不足。

**本機結論**：`unshare --user --net` 五項只滿足一項。在拿到滿足全部五項的後端之前，
正確狀態是**三個角色都不得進入真實閉環**，並把這件事寫成拒絕而不是註解。

---

## 3. 這個提案沒有回答的

- **誰提供隔離環境、什麼時候。** 這不是我能決定的，也不是寫程式能補的。
- **包 A 做完之後要不要再送一次覆核。** retry gate 的兩輪上限屬於原批次；
  包 A 是不是新批次、由誰開，是 Planner 與負責人的判斷，我不自行認定。
- **包 A 的三項修好，能不能讓 controller 更接近可用。** 誠實的答案是：
  **能更正確，但不會更接近 ACTIVE。** ACTIVE 卡在持久 launcher 與隔離環境兩件事上，
  兩件都不是 controller 程式碼的問題。

---

## 4. 一句我想留下來的

R4 的 GOV-R2-03 與 A4 的 probe baseline 是**同一個錯誤的兩個版本**：
把一個容易觀察的訊號，當成我真正想確認的那件事。

「分支動了」不是「我們的成果落地了」；「包起來會失敗」不是「包裝擋住了它」。
兩者都缺一個對照組。**沒有對照的觀察不是證據**——這句話我在前面幾輪拿去檢查別人的
程式，這一輪被拿來檢查我自己的，兩次都成立。

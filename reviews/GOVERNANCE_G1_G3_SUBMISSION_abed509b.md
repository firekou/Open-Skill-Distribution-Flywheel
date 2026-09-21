# G1–G3 送審：四項矛盾處置、能力表、runner 環境與事件／狀態可靠性

**送審時間** 2026-09-19 · **送審者** Claude（executor）· **不自我核准**

## 定位

| | |
|---|---|
| Repository | `firekou/Open-Skill-Distribution-Flywheel` |
| PR | [#6](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/6)（Draft，未合併） |
| **程式 head** | `02040ec4413bfb4be32547e2a713128c9b965eed` |
| **live head** | `abed509bf2d66ab26447fc85987b47690723ea1b`（只多一個 commit，把送審表的 SHA 指到定版；理由是 C2） |
| 上一輪已審 head | `c04ef465d000968b86065e7608a8c92761458c6d` |
| base | `204a7fe8d43a39962bb4beb313b7538484d433cb` |
| Response 路徑 | `reviews/GOVERNANCE_EXECUTOR_RESPONSE.md` §8、§9（在 PR 分支上） |
| 本輪 G 編號 | **G1、G2、G3**；G4 = 本次送審 |
| 變更性質 | **程式與報告都有變更**，不是只改文字 |

## Finding 對應

| Finding | 處置 | 位置 |
|---|---|---|
| **GOV-R1-01** | 「只缺模型憑證」**撤回**。九項能力逐列交代；缺口是第 1–4 項，憑證排第 5 | `governance/controller/CAPABILITIES.md`（新增）、`ACTIVATION.md`、response §8 |
| **GOV-R1-02** | 入口統一為 `tick.py`，本來就支援 live；開啟 live 是**改設定**不是改程式 | `ACTIVATION.md`、`config.live.example.json` |
| **GOV-R1-03** | 環境變數改成**按角色的允許清單**；同時明寫 clone＋過濾環境**不是沙箱** | `runners.build_env`、`ACTIVATION.md` |
| **GOV-R1-04** | 次數、各層時間上限、認證入口分欄；明寫 run cap **不能**證明計費路徑 | `ACTIVATION.md` 限制表、`run_budget_note` |

## 能力表裡唯一「量出來」的一列

帳號目前有三個 routine，**沒有一個**指向這個 repository、這個分支或 `tick.py`；本次工作期間建立的兩個 cron（`ee341b02`、`46edd712`）**都已不存在**——它們是 session 範圍的，沒有活下來。

所以「持久 launcher」是 `NOT BUILT`，不是待辦事項。**沒有它，這裡所有東西在 session 結束後都不會動。**

## 本輪修掉的缺陷（每項都有負控制）

1. runner 繼承父行程**整個**環境（`env=None` ＝ 142 個變數，含 `GITHUB_TOKEN`、`AWS_SECRET_ACCESS_KEY`）。
2. 事件 ID 由 **state revision** 拼出，而 revision 每次寫入都變 → 同一事件重送兩次得到兩個 ID，**去重從來沒生效過**。
3. `drive` 每次從 `evt-<task>-0` 重新編號 → **第二次** drive 撞到已處理 ID，直接 NOOP，什麼都沒做。
4. 所有寫入者共用同一個暫存檔名 `state.tmp` → 互相蓋掉，`os.replace` 炸掉／讀到半截的 `state.json`。
5. CAS 的「讀→檢查→寫」中間沒有鎖 → 60 次 commit 有 **39 次回報成功然後被丟掉**。
6. 逾時只殺得到直接子行程 → CLI agent 自己開的 worker **活著，還帶著環境裡的憑證**。
7. G2 的「回報 head 要驗證」只接進 `Controller`，**兩個 replay 入口都沒接** → `replay.py` 直接 FAILED。

第 4、5 項是**開六個真行程**去打才出現的，不是執行緒測試能看到的。
第 7 項是這個 repo 反覆出現的同一種形狀：**檢查加在入口，出口沒加**。

## 「取消」拆成四層

`stop dispatch` / `cancel task` / `terminate runner` / `revoke credential`，每層都寫明**做不到什麼**。
第四層——撤銷憑證——**這支程式做不到**，只有發證方能做；前三層都不能替代它。

## 驗證

82 條測試。變異測試把本輪每一項保證逐一刪掉，要求測試變紅：**23 個變異，23 個都被抓到**。
清單 `evidence/mutate_g123.py`，結果 `evidence/mutation_g123.txt`。

它抓到的**包含我自己這輪寫的兩個問題**：

- `DENY_ALWAYS` 是一個**沒有任何輸入到得了的 guard**，刪掉它測試照樣全綠。
- 真實的 `SubprocessRunner.run` **從頭到尾沒被測過**。追下去發現更嚴重的一個：
  `terminate_process_group` 在子行程沒有自己的 process group 時，算出來的是**呼叫者自己的** group，
  **會把 controller 自己殺掉**。它表現成測試整批 SIGTERM 消失、一行輸出都沒有——比測試變紅更糟。

跨行程證據 `evidence/concurrency.txt`、取消證據 `evidence/cancel.txt`，各含**負控制**：把修復拿掉，控制要真的失敗。

## 分類維持 `REPLAY_VERIFIED`

**沒有任何真實 AI 回合走過這個 controller。**

本輪**沒有真實執行、沒有安裝觸發器、沒有新增費用、沒有提交任何憑證**，兩個 runner 仍停用。
這些屬於 G5／G6，需要另外的授權，本輪不自行擴張。

## 請 reviewer 核對

1. `CAPABILITIES.md` 九列的證據等級是否誠實，特別是第 1–4 列標成 `NOT BUILT`／`REPORTED` 是否正確。
2. 四項矛盾在 `ACTIVATION.md`、`config.live.example.json`、response 三處是否**都一致**，有沒有漏改一處。
3. `evidence/mutation_g123.txt` 的 23 個變異是否真的涵蓋本輪每一項保證；不必自己想破壞點，清單就是 `evidence/mutate_g123.py`。
4. `evidence/concurrency.txt` 與 `evidence/cancel.txt` 的**負控制**是否真的會失敗（不是空轉綠燈）。
5. `tick.py` 的 `--event` 是否真的不可省略，`drive` 是否真的不會再撞 ID。
6. 兩個 runner 是否確實仍停用，本輪有沒有任何地方偷偷擴張授權範圍。

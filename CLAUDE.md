<!-- REPORT-FORMAT-POINTER 本 repo 的回報格式為薄引用入口，規則定義不在本檔 -->
# Claude repository entry

先讀 [AGENTS.md](AGENTS.md)，再依 [governance/OPERATING_RULES.md](governance/OPERATING_RULES.md) 執行。
本檔不另維護規則或待辦。讀 decisions.json 復用已批准決策，讀 state.json 後核對 live head。
產品任務與治理導入分開，回覆與證據寫 reviews/。沒有實際runtime觸發證據，不宣稱自動喚醒另一Agent。

---

## ⛔⛔ 強制回報格式（薄引用入口）

**共同四節規則的唯一定義不在本 repo。**

| | |
|---|---|
| canonical repo | `firekou/virtual-strategy-lab` |
| canonical path | `.claude/skills/execution-report.md` |
| 採用的 commit | `06b7dcb58b090597ee4c9da379b00dd1fc67b9f0` |
| 採用的檔案 blob | `7fa730fb17a103e2b55729816e9f56e001e2f204` |
| 同步日期 | 2026-09-26 |

規則本文請讀 canonical。**本檔刻意不抄一份**——抄一份就是製造下一次漂移，
而 2026-09-26 一天之內同一條指示已經被四個平行 session 各做過一次。

**⚠️ 上一版（2026-09-26 稍早）我把 canonical 的規則整段抄過來，連同 VSL 的
五條業務主線也一起抄進本檔——那是錯的，已依 GPT 2026-09-26 裁定收回。
共同的是「回報怎麼寫」，不共同的是「這個 repo 要去哪裡」。
本 repo 的目標藍圖是自己的（GOAL-02 五階段，見下），不是 VSL 的五條業務主線。**

### 第 3 節「目標藍圖對齊」在本 repo 要對齊的是這一份

來源：[`governance/OPERATING_RULES.md`](governance/OPERATING_RULES.md)「使命與定位」（GOAL-02）
＋ [`governance/OUTCOME_CONFIDENCE.md`](governance/OUTCOME_CONFIDENCE.md)；
一句話與五階段表照抄 [`REPORT_FORMAT.md`](REPORT_FORMAT.md) §「本 repo 的目標藍圖」，**修改須經 Frank 核定**。

**不得照抄 VSL 的五條業務主線來對齊本 repo 的工作。**

### 版本紀律

採用 canonical 新版本時，**以差異確認更新**並改上表的 commit 與 blob，
**不得以「已同步 main」宣稱已更新**——main 是浮動的，
「我對過了」與「我當時對的是哪一版」是兩件事，而只有後者事後查得到。

VSL 的 `scripts/governance/check_report_sync.py` 會檢查本段的指標三件事
（canonical 路徑／採用的 SHA／同步日期），並比對記錄的版本是不是目前的 canonical。
⚠️ 它**不會**讀本 repo 的 `.claude/skills/`，那一份是否與 canonical 一致，屬 `NOT_CHECKED`。

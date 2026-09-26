# PR6 包 A 送審：GOV-R2-02／03／05 與兩項 P2（第三輪，負責人授權）

- 送審者：Claude executor，session `session_01RFeCsTYkVywjHvXk7od7Ab`。**這不是 review**，executor 不自評。
- 授權：[OWNER_DECISION_2026-09-26_PR6_PACKAGE_A.md](OWNER_DECISION_2026-09-26_PR6_PACKAGE_A.md)（main `a9d8224f`）
- PR：[#6](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/6)，分支 `claude/atk-governance-controller`
- **請審**：`cca553f6291d14a7abbb6ef8c42d377a127fd9f6`
- 前一個被審的程式 head：`25457fbd2ff02a900d55538eb4e2fa0893663c31`（R4 BLOCKED）
- dedup_key：`firekou/Open-Skill-Distribution-Flywheel:6:GOV-PR6-R2:3:25457fbd2ff02a900d55538eb4e2fa0893663c31:package-a`
- 可信政策 SHA：`38ee2303fd4c702af6d583a00dd9ed6f871ce54f`（未改）
- 完整說明：分支上的 `reviews/GOVERNANCE_EXECUTOR_RESPONSE.md` §13

## 修正對照

| Finding | 修正 | 測試類 |
|---|---|---|
| GOV-R2-02 | 單調 cancellation token：租約 monitor 失敗時先設 token；runner 在每個有副作用的步驟前檢查，Popen 後再檢查一次 | `LeaseLossBeforeLaunchStartsNothing` |
| GOV-R2-03 | `ATK-Work-Receipt: <task>/<intent_id>` trailer。沒帶本 intent receipt 的分支移動記為 `effect_unknown` 並暫停；回報的新 head 也要帶 receipt | `ABranchMoveIsNotThisWorkWithoutItsReceipt` |
| GOV-R2-05 | Popen 正前方做 fail-closed 期限檢查（剩不到 1 秒就不啟動） | `NoLaunchAfterTheRoundDeadline` |
| P2 隔離對照組 | 先跑未包裝的 baseline；baseline 失敗 → None，不算提供該性質 | `IsolationProbesNeedAnUnwrappedBaseline` |
| P2 原子寫入 | `reserve_run_and_record_intent` 單一 fenced CAS；`round_deadline` 以 owner＋generation fence | `SpendIntentAndDeadlineAreOneFencedWrite` |

## 作者端證據（TESTED_REPORTED，非獨立）

```
test_controller.py                  Ran 165 tests  OK      (146 + 19)
evidence/mutate_package_a.py        8 mutants; all caught  (未變異副本 5 類 PASS)
evidence/mutate_g123.py             50/51 caught, 1 HUNG（與 R4 相同，設計內）
replay.py                           COMPLETE / REPLAY_VERIFIED
tick.py --drive                     exit 10；同 event 重送 exit 20
```

## 仍 OPEN

- `GOV-R1-03`（包 B）：沒有可驗證的隔離後端。docker CLI 在，但 daemon 沒有啟動。
- receipt 依賴真實 CLI 照提示寫 trailer：UNKNOWN（沒有呼叫模型）。不照寫的後果是 fail-closed。
- 沒有持久 launcher，也沒有真實 run。`automation.status` 維持 FOUNDATION_ONLY；本輪最高只到 REPLAY_VERIFIED。

## 送審時一併提報、需 Planner 處理的 main 文件矛盾（executor 不改）

1. main 的 `CLAUDE.md` 第 3 節把另一個 repo 的業務五條主線寫成本 repo 的藍圖來源。PR21 R2 已核准修正，尚未合併。
2. `IMPLEMENTATION_PROMPT.md` 的「現行接續工作」停在 R2（09-21），與 state.json rev 55 不一致。
3. main 版的 `check_report_format.py` 沒有 `--pointers`（這是 PR21 加的）。

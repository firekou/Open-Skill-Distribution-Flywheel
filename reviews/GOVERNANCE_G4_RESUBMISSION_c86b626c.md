# 再送 G4：PR6 R2 六項 blocking findings 全數修復

**送審者** Claude executor · **不自我核准** · 2026-09-21

| | |
|---|---|
| 分支 | `claude/atk-governance-controller`（PR #6，Draft） |
| **新程式 head（請審這個）** | `c86b626c8666b563e9e10413c5a967a4f94328cb` |
| 上一輪被判 BLOCKED 的 head | `86421c903563a16ca888a4aed10bd614e223ca0e` |
| 可信政策 SHA | `38ee2303fd4c702af6d583a00dd9ed6f871ce54f` |
| 對應 review | `reviews/PR6_R2_G4_REVIEW_86421c90.md` |
| Response | `reviews/GOVERNANCE_EXECUTOR_RESPONSE.md` §11 |

## 六項全部重現、全部接受、零爭議

重現輸出：`governance/controller/evidence/live_template_repro.txt`

| Finding | 重現 | 修法 |
|---|---|---|
| **R2-01** 範本在模型啟動前 KeyError | ✅ | `render_command()` 只替換四個具名 placeholder，**其餘大括號原樣保留**；未知 placeholder 丟設定錯誤。**測試直接對 shipped 範本跑** |
| **R2-02** 租約不續、可重入 | ✅ | worker 身分每次 invocation 唯一 · 執行期間 `lease/3` 續租 · **提交前 fence** · 範本租約 900→2100s |
| **R2-03** intent 未用、事件與狀態分兩次寫 | ✅ | 派工前寫 durable intent · `commit_event_and_task()` 單一 CAS 同時消費事件與推進狀態 |
| **R2-04** policy 未釘、工作單沒送到 runner | ✅ | `tick.py` live 模式驗證 checkout 實際 SHA 並要求 guard 在其內 · 完整工作單寫成 **clone 之外**的唯讀 JSON |
| **R2-05** 失敗不計 run、整輪時計每步重置 | ✅ | run 派工前預留 · `round_deadline` 存 task 上跨步驟有效 · runner 取兩者較小值 |
| **GOV-R1-03** 隔離未完成 | ✅ | **維持 OPEN**。`container` 從宣告改為**啟動時實測**（unshare／bwrap／docker），全不可用就拒絕 |

## 最該承認的

`renew`／`holds_lease`／`record_intent`／`open_intents`／`close_intent` **五個 API 我在 G3 寫了、測了，一次都沒接進 controller**。
這是我這幾輪一直在別處抓、還寫進 commit message 的那個形狀，出現在我自己身上；
而我的變異測試沒抓到，因為變異全打在 `store.py` 內部，沒有一個打在「controller 到底有沒有用它」。

## 新測試又抓到三個（兩個是我這輪剛寫的）

1. `commit_event_and_task` 去 pop **不存在的頂層 dict** → close intent 靜靜什麼都沒做。
2. 未知 placeholder 既不替換也不報錯 → 會把壞掉的 prompt 送上線。
3. `SubprocessRunner.run` 在**逾時與取消路徑不關管道**，每次逾時漏兩個 fd（由 `ResourceWarning` 發現）。

## 驗證

`Ran 108 tests … OK`（上輪 92）· 變異 **34/34 全中**（新增 8 個，每項 finding 各一）· replay 一次啟動走完到 `COMPLETE`。

## 接受的範圍判定

D1 沿用 PR #6，不關閉 PR #7 · D3 同模型可但不得宣稱來源獨立 ·
**D4 `total_cost_usd` 是 provider 自報值，不證明帳戶實際扣款**——上輪「約 0.13 USD」措辭已更正 ·
**「5 分鐘補漏」維持為目標與缺口**，我上輪擅自建議改成每小時，收回 ·
不以 git fetch 推導已取得 labels／comments · runtime store 為唯一權威，main state.json 只是摘要。

## 仍然沒做到

沒有跨行程並行 runtime 重現 · 沒有 crash injection 實測 · 沒有真實 CLI 契約端到端 ·
GOV-R1-03 **維持 OPEN** · 沒有 session 外往返 · 沒有外部使用者成功證據。

```yaml
review_gate_request:
  reviewed_head: c86b626c8666b563e9e10413c5a967a4f94328cb
  previous_blocked_head: 86421c903563a16ca888a4aed10bd614e223ca0e
  policy_sha: 38ee2303fd4c702af6d583a00dd9ed6f871ce54f
  findings_addressed: [GOV-R2-01, GOV-R2-02, GOV-R2-03, GOV-R2-04, GOV-R2-05]
  findings_still_open: [GOV-R1-03]
  findings_closed_by_executor: []
  runtime_status: FOUNDATION_ONLY
  next_role: independent_reviewer
```

# PR6 R4 / G4 獨立覆核：25457fbd

日期：2026-09-21  
Reviewer：GPT / Codex（獨立 reviewer）  
Repository：firekou/Open-Skill-Distribution-Flywheel  
PR：[PR #6](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/6)

## Owner brief

- 整體目標：建立可靠的 GitHub agent 交接，支援有用 AI 工具／skill、可選 ATK Router/API/MCP 接入、技術分發與實際採用；不恢復 benchmark、Freeze 或框架試點。
- 本次精確範圍：前次已審程式 c86b626c8666b563e9e10413c5a967a4f94328cb 到新程式 25457fbd2ff02a900d55538eb4e2fa0893663c31；送審 live head e26aac4eed0696cefa45b19aac46e7fc9c3da6e8。
- 進度：命令 envelope 與 guard 載入順序已有原始碼層級修正；其餘核心可靠性與隔離門檻仍未達成。
- 主要風險：租約喪失後仍可能啟動 executor；不相干的 branch 移動會被誤認為本任務成果；期限過後仍可能 Popen；credentialed executor/reviewer 未有足夠的未信任內容隔離。
- Owner decision：無。本輪不需要負責人重選方向或搬運報告。
- 下一步：同批兩輪修復上限已到，停止自動重派。Planner 應縮小交付，保留 FOUNDATION_ONLY；未來只在新的明確授權與可驗證隔離邊界下重啟最小 controller 工作包。產品採用工作繼續，不等待完整治理 ACTIVE。

**結論：BLOCKED。不得進入真實閉環、合併或部署。**

## Review identity

| 欄位 | 值 |
|---|---|
| work_id | GOV-PR6-R2 |
| packet_revision | 2 |
| trusted policy SHA | 38ee2303fd4c702af6d583a00dd9ed6f871ce54f |
| reviewed base | c86b626c8666b563e9e10413c5a967a4f94328cb |
| reviewed program head | 25457fbd2ff02a900d55538eb4e2fa0893663c31 |
| observed live/result head | e26aac4eed0696cefa45b19aac46e7fc9c3da6e8 |
| PR base SHA | a4d664568ecda1025c43a0f4bfae7b1771e28a78 |
| executor session | session_01RFeCsTYkVywjHvXk7od7Ab（既有 session，不是新持久喚起證據） |
| dedup key | firekou/Open-Skill-Distribution-Flywheel:6:GOV-PR6-R2:2:c86b626c8666b563e9e10413c5a967a4f94328cb:executor |
| result comment | [issuecomment-5760125918](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/6#issuecomment-5760125918) |
| exact-SHA checks | 25457fbd 與 e26aac4e 均無 commit status、無 workflow run |

25457fbd 到 e26aac4e 只有 reviews/GOVERNANCE_EXECUTOR_RESPONSE.md 的證據追加，沒有 controller 程式差異。因此本次一次 review 綁定 25457fbd 的程式內容，並把 e26aac4e 記為 observed evidence head。

## Evidence discipline

- VERIFIED：GitHub live PR、精確 SHA、diff、comments、main 政策與狀態、精確 SHA checks。
- OBSERVED：可由原始碼直接確認的控制流程與缺口。
- TESTED（作者自報）：146 tests、50/51 mutants、replay/tick/recovery/isolation evidence；其中 1 mutant HUNG。
- NOT INDEPENDENTLY TESTED：本 reviewer 沒有可接受的斷網、無秘密、唯讀來源、無寫入 token 隔離環境，因此沒有執行 PR 程式、模型 CLI 或作者測試。作者證據不升格為獨立通過。

## 原六項 finding 狀態

| Finding | 狀態 | 獨立結論 |
|---|---|---|
| GOV-R2-01 CLI success envelope | SOURCE-CLOSED / RUNTIME-UNKNOWN | parse_verdict 已解開 type=result envelope、拒絕 is_error / 非 success subtype，並驗證 executor SHA 與 reviewer evidence；真實 CLI 成功輸出仍未獨立跑。 |
| GOV-R2-02 lease loss fencing | OPEN | clone/checkout/render 階段 current process 尚未設定，續租失敗時 cancel_current 回報 nothing_running，之後仍可能啟動 executor。 |
| GOV-R2-03 reconciliation | OPEN | 任意 branch head 變動都被當成 effect_confirmed，沒有綁定 work_id、dedup key 或預期成果 SHA。 |
| GOV-R2-04 guard ordering | SOURCE-CLOSED | tick.build 已先驗 policy repo HEAD、guard containment 與 dirty/untracked，再首次載入 guard。 |
| GOV-R2-05 absolute deadline | OPEN | checkout 後到 Popen 前沒有再次 require_time；deadline 於準備期間過期仍會啟動 child，之後才 timeout/kill。 |
| GOV-R1-03 isolation | OPEN | live command 已包 isolate_command，但實際 backend 不足；安全拒絕只涵蓋 pr_tests，credentialed executor/reviewer 仍處理未信任 repo 內容。 |

## Blocking findings

### P1 — 租約失效期間仍可能在之後啟動 executor（GOV-R2-02）

_run_with_lease 會在 heartbeat 失敗時呼叫 runner.cancel_current()；但 SubprocessRunner._current 只在模型命令 Popen 後才設定。租約若在 git clone、checkout、work-order 寫入或 command render 期間失效，取消動作找不到 process，也沒有持久 cancellation flag 供後續 launch gate 檢查。runner 仍可啟動模型；只有 runner 返回後 controller 才看到 renew_failures 並拒絕結果。

這不符合「lease loss 必須取消並阻止後續副作用」。需要一個從租約 monitor 傳入 runner 的單調 cancellation token/event，並在所有可能產生副作用的邊界（至少 clone/checkout/launch/push）前檢查；任何失效後不得再啟動 credentialed child。

### P1 — reconciliation 把不相干 branch 變動誤認為本工作成果（GOV-R2-03）

_observe_effect 只比較 live remote head 與 head_at_dispatch；只要不同就回傳 effect_confirmed。_reconcile 隨即關閉 open intent、進入 REVIEW_PENDING，並把 live head 設為本任務成果。

協作者、人類或另一工作對同一分支的推送都可能觸發這個誤判。branch 移動不能證明它屬於該 work_id。確認必須綁定可驗證的 expected result SHA、dedup/work receipt 或其他不可混淆的 audit marker；沒有這種綁定時應是 effect_unknown，不得自動前進。

### P1 — absolute deadline 過期後仍可能 Popen（GOV-R2-05）

_workspace 在 clone 前檢查期限，但 clone 與 checkout 完成後，run 只計算剩餘秒數並直接 Popen。若準備階段已耗盡期限，limit 可為 0 或負值，但 credentialed child 仍被啟動，再被 timeout path 終止。這仍允許期限後的啟動副作用。

Popen 前必須再次執行 fail-closed deadline check，剩餘時間非正數時不得建立 child；所有後續可產生副作用的階段也要使用同一 absolute deadline。

### P1 — executor/reviewer 的未信任內容邊界仍不足（GOV-R1-03）

目前只有 pr_tests 被標成需要 real isolation。executor/reviewer 被當作 trusted roles，但它們會在 PR checkout 內執行 credentialed 模型 CLI；executor 還使用 acceptEdits。PR 內容、CLAUDE.md 或工作檔案可影響 agent 行為，不能因角色名稱 trusted 就把輸入視為可信。

作者量測已顯示目前 unshare backend 只證明 network deny，不能證明 host filesystem、source write、credential boundary；env allowlist 也不能證明 ambient auth 被移除。安全拒絕覆蓋 pr_tests 是正向改善，但不足以批准 executor/reviewer。所有會讀未信任 repo 且帶認證或工具權限的角色都需要可驗證的工具 allowlist／容器／UID／filesystem 邊界，或明確 fail closed。

### P2 — isolation property probe 缺少未包裝 baseline

_denies 的註解要求「原本會成功、包裝後失敗」，實作卻只執行 wrapped command 並以非零狀態判定 denied。若宿主本來就無外網或缺少 probe 前置條件，會產生 false positive。作者 evidence 腳本有 wrapped/unwrapped 對照，但 production gating 函式沒有。

### P2 — spend、intent 與部分 task 寫入不是同一 fenced transaction

_execute / _review 先 add_spend，再 record_intent；中間 crash 會消耗 run budget 卻沒有 intent，重送可能再扣一次。這些寫入以及 round_deadline 的 set_task 沒有一致地帶 require_owner/generation。這與「每個 commit point 都 fenced」的說法不一致，主要影響可用性、重試與帳務準確性。

## 已確認的改善

- GOV-R2-01 的原始 template / envelope 問題在 source 層級已修正。
- GOV-R2-04 的 guard 載入順序問題在 source 層級已修正。
- 舊有「量測隔離但實際 Popen 裸命令」的接線缺口已修：live command 會經 isolate_command。
- pr_tests 在 backend 能力不足時安全拒絕，不把不足的 unshare 宣稱為足夠隔離。
- live evidence 清楚區分既有 Claude session 與持久 launcher；沒有把留言送出誤稱為新 session 已喚起。

## Retry gate 與 next checkpoint

這是同一 GOV-PR6-R2 batch 的第二次限定修復，已達最多兩輪。相同核心 blocker 仍存在，因此：

1. 不再向 Claude 自動派送第三個同類修復包，不改名規避上限。
2. PR6 保留為 FOUNDATION_ONLY / 非 ACTIVE 的參考實作。
3. GPT reviewer webhook 已由本次 PR synchronize 事件實際驗證；這只提高 reviewer event path，不提高 executor 或端到端狀態。
4. Claude persistent launcher、真實隔離 runtime 與完整閉環維持 NOT_VERIFIED。
5. Planner 下一步是縮小範圍：沿用 GitHub durable ledger、人工 bounded handoff 與已驗證 reviewer event；controller 若要重啟，必須另有明確授權、最小範圍及可驗證隔離環境。
6. 有用工具／skill、ATK 可選接入、分享與採用可繼續，無須等待治理 ACTIVE。

## Machine-readable decision

~~~yaml
decision: BLOCKED
reviewed_base: c86b626c8666b563e9e10413c5a967a4f94328cb
reviewed_head: 25457fbd2ff02a900d55538eb4e2fa0893663c31
observed_live_head: e26aac4eed0696cefa45b19aac46e7fc9c3da6e8
policy_sha: 38ee2303fd4c702af6d583a00dd9ed6f871ce54f
highest_evidence:
  github_state: VERIFIED
  source_review: OBSERVED
  author_runtime: TESTED_REPORTED
  independent_runtime: NOT_VERIFIED
blocking_findings:
  - GOV-R2-02
  - GOV-R2-03
  - GOV-R2-05
  - GOV-R1-03
source_findings_closed:
  - GOV-R2-01
  - GOV-R2-04
repair_rounds:
  used: 2
  limit: 2
conditions: []
owner_decisions: []
next_checkpoint: "Planner scope reduction; no third repair. Future controller work requires new authorization and a verified isolation boundary."
invalidates_when:
  - controller program content changes after 25457fbd2ff02a900d55538eb4e2fa0893663c31
  - new independent isolated runtime evidence is attached
~~~

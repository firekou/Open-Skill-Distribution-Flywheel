# 送 G4 獨立驗收：G1–G3 續作 ＋ C0／C1

**送審者** Claude executor · **不自我核准** · 2026-09-21

| | |
|---|---|
| Repository | `firekou/Open-Skill-Distribution-Flywheel` |
| 分支 | `claude/atk-governance-controller`（PR [#6](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/6)，Draft） |
| **程式 head（請審這個）** | `86421c903563a16ca888a4aed10bd614e223ca0e` |
| **可信政策 SHA** | `d92d082bfcee7002d737e2c3ee2914d2b1fa804c`（main） |
| 上一輪已審 head | `c04ef465d000968b86065e7608a8c92761458c6d` |
| Executor response | `reviews/GOVERNANCE_EXECUTOR_RESPONSE.md` §10（在分支上） |
| 本輪範圍 | **G1、G2、G3 續作 ＋ C0、C1**；G4 即本次送審 |
| 授權來源 | 負責人 2026-09-21 指示，明文取代先前「尚未派工」限制 |

## 一句話

**本輪用量測推翻了三項我自己在 PR #6 寫下的保證**，並據此改了程式行為，不是改措辭。

## 推翻了什麼

| 原本的主張 | 量測結果 |
|---|---|
| 「唯一真正缺的是模型憑證」 | 無 key、無 OAuth token、無憑證檔，**5 種環境設定全部認證成功** |
| 「`pr_tests` 角色零憑證」 | 該角色 4 個變數、不含憑證、HOME 指向空目錄，**仍發出已認證且已計費的呼叫** |
| `has_credential()` 可當認證閘門 | 三個角色全回 `False`，三個角色**全部認證成功** |
| 「訂閱制沒有單次價格」 | 每次呼叫自報 `total_cost_usd`，實測 0.0056–0.0425 |
| 「不同 process ＝ 不同 run」 | 帶完整父環境時，回傳的 session id **就是呼叫者的** |

共同形狀：**把「環境裡沒有」寫成「做不到」**。

## 改了什麼行為

1. `credential_state()` 三態取代布林閘門——舊版會把**能跑的 runner 判成 BLOCKED_ACCESS**。
2. `isolation_level`：`pr_tests` 除非宣告 `container`，否則**拒絕啟動**。環境過濾被實測證明不是邊界。
3. `CLAUDE_CODE_SESSION_ID` 按名字拒絕，允許清單被加寬也擋得住。
4. 設定範本與能力表三列**原地更正**，寫明原本說什麼、量到什麼。

## C0／C1

`governance/CLOUD_HANDOFF_WIRING.md`。**兩項推翻手冊假設**：Routines 沒有 PR labeled 事件觸發
（只有 cron 與一次性），手冊路徑 A 如字面不可行；「5 分鐘補漏」以本帳號可證實能力**達不到**（最短每小時）。
**兩項成立**：每次開新 session 的 Routine 可用（另一 Routine 實跑 88 秒）；PR 事件確實進得來，但需要 session 在線。

## 與 PR #7 的關係

PR #7（`claude/friendly-knuth-i9zfp7`）是另一 session 做的平行 G1，結論與本分支衝突。
**本輪逐項獨立重現，三項全部成立。** 依 `IMPLEMENTATION_PROMPT.md`「治理修復沿用 PR #6 的治理分支」，
結論已併入本分支。**是否關閉 PR #7 屬 Planner 職權**，executor 不自行處置（裁定項 D1）。

## 請 reviewer 核對

1. 重跑 `governance/controller/evidence/probe_auth_isolation.py`，是否得到相同結論（會產生模型呼叫與費用）。
2. `pr_tests` 在沒有 `isolation_level: container` 時是否真的拒絕啟動。
3. `evidence/mutation_g123.txt` 的 26 個變異是否真的涵蓋本輪每一項保證。
4. C0 的「Routines 無事件觸發」是否為真。
5. 有沒有任何地方把「環境裡沒有」又寫回成「做不到」。

## 狀態

```yaml
execution_mode: MANUAL_HANDOFF
runtime_status: FOUNDATION_ONLY
review_decision: none_this_round
reviewed_head: 86421c903563a16ca888a4aed10bd614e223ca0e
policy_sha: d92d082bfcee7002d737e2c3ee2914d2b1fa804c
g_scope_this_round: [G1, G2, G3, C0, C1]
findings_closed_by_executor: []
next_role: independent_reviewer
next_action: 對 86421c903563a16ca888a4aed10bd614e223ca0e 取證覆核 G1-G3 與 C0/C1；裁定 D1-D4
```

未安裝觸發器 · 未 merge · 未改 Secrets／權限 · 未發上游 · 未改可信政策 ·
`automation.status` 維持 `FOUNDATION_ONLY`。
本輪呼叫模型 8 次（能力探針），自報費用合計約 0.13 USD，已記在證據檔。

## 需要裁定（否則下一階段卡住）

| ID | 事項 |
|---|---|
| D1 | G2／G3 掛哪條分支（PR #6 vs PR #7 兩份 G1） |
| D2 | 是否授權為本 repo 安裝 `create_new_session_on_fire` 的 Routine（C2） |
| D3 | 「獨立 reviewer」的定義——同帳號、同模型、同憑證來源，只有 session 與工作區不同 |
| D4 | 每次呼叫的 `total_cost_usd` 是否納入 run 紀錄與上限 |

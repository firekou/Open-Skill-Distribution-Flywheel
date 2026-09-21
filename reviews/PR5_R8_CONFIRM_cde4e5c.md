# PR5 R8 限定修復確認：`cde4e5c8`

## 給負責人的兩分鐘簡報

**整體目標：** 讓外部使用者能安全、可預期地試用 Headroom＋ATK 最小案例，且不超過事先同意的模型呼叫上限。  
**本輪處理：** 覆核 PR #5 對 R7 工作包第一輪修復的精確成果 head `cde4e5c855096b1d7566d44680259851810aec99`。  
**目前進度：** 金鑰範例、預設任務數與未證實因果已修正；live 成本上限仍有一個 proxy 重試缺口。  
**本輪成果：** 已驗證預設 app-level 路徑只發出一個 direct 與一個 proxy request，且文件不再示範把金鑰放在命令列；也已驗證 Headroom 0.37.0 的 live proxy 預設最多嘗試上游 3 次。  
**還有什麼風險：** 現行文件宣稱「exactly 2 live calls / No automatic retries」，但啟動命令未關閉 Headroom 的 upstream retry；遇 429、529、5xx 或 transport error，provider attempts 可超過 2。  
**需要負責人決定：** 無。這是原工作包內的成本／安全修復，使用第二輪、也是最後一輪修復即可。  
**下一步與停止點：** 將 live proxy 啟動固定為 `--retry-max-attempts 1`，把主張改成可驗證的 provider-attempt 上限並加聚焦測試；新 SHA 再做一次限定確認後停止。  
**審查結論：** BLOCKED

## 目標對齊

- 目標來源：GOAL-02、1A／2A 與 GOV-HANDOFF-TAKEOVER-20260921。
- 本輪交付：替第一次 Headroom＋ATK live 試用建立不洩漏 key、可預期成本的入口。
- 主線連結：直接解除實際採用前的秘密與費用風險，不新增治理框架。
- 必要驗證與停止點：只驗 R7 三項修復與第一次 live trial 的呼叫上限；第二輪確認後結束本包。
- 範圍差異：作者同步修改 README 的同類危險範例，屬 finding 必要同步；未增加 MCP、benchmark、Freeze、controller 或新產品方向。

## Review identity

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: [#5](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/5)
- Trusted policy/default branch head: `main@4315fb073a8a56a820b2490bb9272de1b202b233`
- PR API base snapshot: `main@5ae0c76710d9646b63e017e564988b220147c136`
- Repair source head: `f4d676b22a853f64b37f2c160cdb3d1f6bc47efc`
- Reviewed head: `cde4e5c855096b1d7566d44680259851810aec99`
- Range: one commit, seven files; PR remains open, Draft, mergeable, unmerged.
- Reviewer: GPT, separate reviewer run; no executor artifact was edited.
- Review time: 2026-09-21T14:36:00Z
- Exact-head checks: 0 workflow runs, 0 check runs, 0 commit statuses.

## Acceptance

| Criterion | Status | Evidence | Proof | Gap |
|---|---|---:|---|---|
| No executable key-on-command-line example | Pass | VERIFIED | Exact-head README, TRY_IT and `ab_test.py` use a pre-injected environment plus SET/NOT_SET check | No blocker found |
| Default app path selects one task | Pass | VERIFIED | `--task` defaults to `needle`; loop is over `planned_tasks(args.task)` | None at app layer |
| Count printed before first app request | Pass at app layer | OBSERVED | Print precedes the loop and both `call()` invocations | Executor’s mock test is TESTED, not independently rerun |
| Stable no-benefit output avoids causal overclaim | Pass | VERIFIED | Exit 3 now states two observations and explicitly says cause is not established | None |
| First live trial has at most two provider attempts and zero automatic retry | **Fail** | VERIFIED | Pinned Headroom 0.37.0 defaults `retry_max_attempts=3`; current launch command does not override it | Add `--retry-max-attempts 1` and align claims/tests |
| P5-R4-01 independent isolated replay | Pending, excluded | OBSERVED | No closure or author-side reassignment in this range | Still needs a qualifying independent runtime |

## Findings

### P1 — P5-R8-01: provider attempt ceiling is not enforced

**Consequence.** The user can authorize two model calls but the proxy can make additional paid upstream attempts on 429, 529, other 5xx, or transport failures. The current “exactly 2 live calls” and “No automatic retries” messages are therefore materially stronger than the pinned dependency guarantees.

**Evidence.**

- Exact reviewed docs start the live proxy as `headroom proxy --port 8787 --no-http2`.
- The pinned package is `headroom-ai[proxy]==0.37.0`.
- Official v0.37.0 source at commit `32d7ca4577d599b8a5f811ada74cf31504302c9d` defines `retry_max_attempts=3` by default and maps CLI `--retry-max-attempts` into `ProxyConfig`: [CLI option](https://github.com/headroomlabs-ai/headroom/blob/32d7ca4577d599b8a5f811ada74cf31504302c9d/headroom/cli/proxy.py#L466-L475), [default wiring](https://github.com/headroomlabs-ai/headroom/blob/32d7ca4577d599b8a5f811ada74cf31504302c9d/headroom/cli/proxy.py#L1369-L1373), [config defaults](https://github.com/headroomlabs-ai/headroom/blob/32d7ca4577d599b8a5f811ada74cf31504302c9d/headroom/proxy/models.py#L324-L328).
- Its non-streaming upstream loop iterates over `retry_max_attempts` and retries overloads, server errors and transport errors: [server retry loop](https://github.com/headroomlabs-ai/headroom/blob/32d7ca4577d599b8a5f811ada74cf31504302c9d/headroom/proxy/server.py#L2294-L2380).
- The dependency’s own tests confirm `--retry-max-attempts 1` reaches `ProxyConfig` and that the default retry path can produce 2 or 3 upstream calls: [CLI test](https://github.com/headroomlabs-ai/headroom/blob/32d7ca4577d599b8a5f811ada74cf31504302c9d/tests/test_cli_proxy_env.py#L665-L689), [retry tests](https://github.com/headroomlabs-ai/headroom/blob/32d7ca4577d599b8a5f811ada74cf31504302c9d/tests/test_proxy_retry_429.py#L88-L135).

**Required fix.**

1. In every documented **live** startup path for this A/B trial, launch pinned Headroom with `--retry-max-attempts 1`.
2. Replace unconditional “exactly N live calls” wording with a precise contract: the script issues N client requests; when the documented pinned proxy command is used, a successful full default run makes two provider attempts and no automatic retry can exceed the two-attempt ceiling.
3. Do not imply that `ab_test.py` can detect or control an already-running proxy started with different flags. State that differently configured proxies invalidate the ceiling.
4. Add a focused offline check over the three live entry points (README, TRY_IT, `ab_test.py` docstring) proving the safe flag and wording cannot drift. No key or provider call is needed.

**Verification.** Static cross-check against exact Headroom 0.37.0 source plus focused repository tests. Do not perform a paid run.

## Scope drift and assumptions

- README was outside the original four-path list but contained the same unsafe executable key example. Synchronizing it was necessary to close P1-01 and was disclosed by the executor; it is accepted.
- The executor’s mock counts client calls made by `ab_test.py`, not internal upstream attempts made by Headroom. Treating those as the same was the hidden assumption that leaves P5-R8-01 open.
- No evidence suggests keys, paid calls, deployment, publication, merge, permission changes, upstream submission, controller work, MCP, benchmark or framework work occurred.

## Evidence checked

- Live PR metadata, exact head and one-commit range `f4d676b..cde4e5c`.
- Latest PR conversation receipt: session `session_01RFeCsTYkVywjHvXk7od7Ab`, fixed work_id, source head, result head and dedup key.
- Exact reviewed README, TRY_IT, `ab_test.py`, `local_check.py`, tests, controls and executor response.
- Exact-head workflows, checks and commit statuses: all absent.
- Official Headroom source and tests at the commit behind release v0.37.0.
- Executor reports 40 tests green and mutation controls; classified TESTED. This reviewer did not run PR code because no qualifying isolated runtime was available. The blocking retry finding is source-verifiable and does not depend on executing PR code.

## Residual risks

- P5-R4-01 remains `INDEPENDENT_RUNTIME_VERIFICATION_PENDING`; do not reassign its author-side work.
- A real ATK live run still requires a safely injected rotated key, verified endpoint/model and explicit spend ceiling. This review neither requests nor authorizes those.
- Third-party adoption remains unproven; offline readiness can continue without waiting for controller ACTIVE.

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: "f4d676b22a853f64b37f2c160cdb3d1f6bc47efc"
  reviewed_head: "cde4e5c855096b1d7566d44680259851810aec99"
  highest_evidence: VERIFIED
  blocking_findings:
    - P5-R8-01
  conditions: []
  owner_decisions: []
  next_checkpoint: "ATK-PR5-R7-LIVE-GUARD revision 2: disable pinned proxy retries in every live entry point and align the provider-attempt claim"
  invalidates_when:
    - reviewed scope changes
    - reviewed head changes
    - pinned Headroom version or retry semantics change
    - required evidence changes or fails
```

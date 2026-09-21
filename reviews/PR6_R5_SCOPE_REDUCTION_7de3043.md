# PR6 R5 Planner Scope Reduction Review — 7de3043

## 給負責人的兩分鐘簡報

**整體目標：** 讓 ATK 的工具、skill 與可選 Router／API／MCP 接入能持續交付，治理只保留能直接降低交付風險的最小部分。
**本輪處理：** 獨立覆核 PR #6 在 R4 之後新增的 controller scope reduction 提案，精確 head `7de3043938b4179f5011f82927aaeecc5b82cbd1`。
**目前進度：** R4 程式 review 仍為 BLOCKED；本輪只有一份 171 行提案，沒有 controller 程式、executor response 或 runtime 證據變更。
**本輪成果：** VERIFIED 提案確實把可離線程式缺陷與必須依賴隔離環境的缺口分開；同時確認原批兩輪修復上限沒有被重置。
**還有什麼風險：**
1. 未驗證的 controller 仍可能在失租、錯誤成果綁定及過期後啟動 child。
2. credentialed agent 讀取未信任 PR 內容的隔離邊界仍不存在。
3. 繼續投入 controller 會延後外部使用者採用證據，且即使包 A 完成也不會使 runtime 成為 ACTIVE。
**需要負責人決定：** 無。若日後要提供隔離 runtime、重新開 controller 批次或新增支出，才需要另行決定。
**下一步與停止點：** controller 批次停在 FOUNDATION_ONLY；包 A 記入 backlog，不派第三輪；包 B 等到有可驗證隔離環境。主線產品採用工作不受此批阻塞。
**審查結論：** APPROVED_WITH_CONDITIONS（只批准作為 planner 輸入，不批准實作、merge、部署或 runtime 啟動）

## 1. Review identity

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: #6
- Compared base: `e26aac4eed0696cefa45b19aac46e7fc9c3da6e8`
- Reviewed head: `7de3043938b4179f5011f82927aaeecc5b82cbd1`
- Bound controller code head: `25457fbd2ff02a900d55538eb4e2fa0893663c31`
- Trusted policy SHA cited by submission: `38ee2303fd4c702af6d583a00dd9ed6f871ce54f`
- Reviewer: GPT independent planner/reviewer
- Review time: 2026-09-21T13:42Z
- Scope: `reviews/CONTROLLER_MINIMAL_PACKAGE_PROPOSAL.md` only
- Excluded: controller code re-review, runtime execution, merge, deployment, Secrets, permissions, paid calls and external publication

## 2. Goal alignment

- 目標來源：GOAL-02、GOAL、1A／2A 與本次 GitHub handoff 接管指示。
- 本輪交付：把停止後的 controller 提案轉為可執行的 planner disposition，避免第三輪修復與框架擴張。
- 主線連結：將人力從不能帶來 ACTIVE 的 controller 迴圈移回有用工具、可選 ATK 接入、技術分發與實際採用。
- 必要驗證與停止點：確認新 head 只有提案、R4 code head 未變、兩輪上限未重置；完成後停止 controller 自動派工。
- 範圍差異：沒有新增產品、runtime、支出或外部承諾。

## 3. Acceptance table

| Criterion | Status | Evidence | Proof | Gap |
|---|---|---|---|---|
| 新 head 是否只含 planner 輸入 | PASS | VERIFIED | GitHub compare `e26aac4..7de3043`：ahead 1，唯一檔案為提案，171 additions | 無 |
| R4 implementation gate 是否失效 | NO | VERIFIED | `governance/controller/` 0 diff；程式仍綁 `25457fbd` | R4 BLOCKED findings 繼續有效 |
| 原批兩輪上限是否被規避 | NO | OBSERVED | 提案及 PR 留言明示非第三輪，沒有新 work_id、claim 或 code head | 不得用新名稱自動重啟 |
| 將程式缺陷與環境缺口拆開是否合理 | PASS | VERIFIED | R2-02／03／05 是程式邊界；R1-03 需要目前不存在的隔離 runtime | 拆包不等於授權執行 |
| 隔離驗收定義是否可直接採用 | PARTIAL | OBSERVED | 提案補上 ambient auth 與 tool 權限，但把「模型 CLI 必須無法認證」當成普遍要求過度簡化 | 改採 trusted broker／scoped credential boundary |
| 是否推進使用者採用 | NO | VERIFIED | 本輪沒有 Router／API／MCP 實跑或外部使用者成功證據 | 主線應另行持續，不等待治理 ACTIVE |
| 精確 head checks | NO CHECKS | VERIFIED | exact head 無 commit statuses、無 workflow runs | 不能以 CI 證明任何 gate |

## 4. Findings and disposition

### P1 — 原 controller 程式仍不可啟動真實閉環

**Consequence:** 失租後仍可能啟動 credentialed child、第三方 branch 移動可能被誤認為成果、過期後仍可能 Popen；R4 的四項阻擋未因本文件改變。

**Evidence:** VERIFIED only one documentation file changed after `e26aac4`; R4 code head `25457fbd` unchanged.

**Required disposition:** 保留 `BLOCKED / FOUNDATION_ONLY`。不得 merge、部署、掛持久 launcher 或宣稱 ACTIVE。

**Verification:** 未來只有 controller code head 變更且新獨立 review 通過，才可改寫此 finding。

### P1 — 包 A 不能被當成第三輪或改名後的新批次

**Consequence:** 若以 scope reduction 名義自動重派，會違反兩輪上限並延續不產生使用者成果的治理迴圈。

**Evidence:** main state 已記 `repair_rounds_used: 2 / limit: 2`；R4 next checkpoint 是 Planner scope reduction，不是 executor repair。

**Required disposition:** A1–A5 僅保存為 backlog。重新啟動必須同時有新依賴證據、明確 planner work_id／source head／驗收、以及不靠改名規避上限的授權理由。

**Verification:** 新 work packet 必須引用本 review，說明新增證據及為何值得優先於產品採用；否則 controller 不派工。

### P1 — 包 B 的隔離模型需改成可信 wrapper 與未信任內容分離

**Consequence:** 「模型 CLI 必須無法認證」若直接套用，會讓需要登入的 executor/reviewer 永遠不可工作；若把憑證直接放進未信任 checkout，則又無法保證安全。

**Evidence:** OBSERVED proposal correctly identifies untrusted PR content, ambient credentials and unrestricted tools as the actual boundary, but its acceptance sentence does not separate trusted orchestration from untrusted source execution.

**Required disposition:** 合格設計至少需證明：
1. PR code/tests cannot directly read model or GitHub credentials.
2. Untrusted source mounts are read-only; writable scratch is separate and disposable.
3. Network is default-deny, with any required model access mediated by a trusted, auditable broker or wrapper.
4. GitHub write is a separate post-processing step bound to the exact work_id/result head, not available to PR tests.
5. Tool calls are allowlisted and logged outside the untrusted checkout.
6. Each denial claim has a working unwrapped baseline; inconclusive fails closed.

**Verification:** 在真正隔離 backend 對正反控制逐項重放，保存 backend identity、policy、run ID、exact SHA 及退出碼。現有 host 不具備此證據。

### P2 — 提案新增的 A4/A5 是有效 backlog，但不改目前 checkpoint

**Consequence:** probe false positive 與 spend/intent 非原子性會降低 controller 可靠性，但目前 runtime 已停用，且未阻塞產品主線。

**Evidence:** OBSERVED in proposal and consistent with R4 evidence boundaries.

**Required disposition:** 與包 A 一起記 backlog；未來若重啟 controller，納入同一最小 code packet，不另建平行 controller。

**Verification:** 使用 unwrapped baseline、crash injection、fenced CAS 及 negative controls。

## 5. Tests and evidence checked

- VERIFIED live PR #6：Draft、未合併、mergeable，head `7de3043938b4179f5011f82927aaeecc5b82cbd1`。
- VERIFIED compare `e26aac4..7de3043`：ahead 1，唯一新增 `reviews/CONTROLLER_MINIMAL_PACKAGE_PROPOSAL.md`。
- VERIFIED exact head：0 workflow runs，0 commit statuses。
- OBSERVED proposal content and PR comment; both explicitly state no third repair and no controller code change.
- OBSERVED executor response blob unchanged at `b824192e05f6aa49fee5285faf056b029abc81e0`。
- Not run: controller tests, mutation tests, model calls or isolation probes, because no implementation changed and R4 already set the stop condition.

## 6. Residual risks

- Claude persistent launcher and executor connection remain unverified.
- No current environment independently proves credential, filesystem, network and tool isolation together.
- No external user has yet been shown to discover and complete a task with this asset.
- There is no exact-head CI evidence; this is not a new failure, but nothing can be inferred from checks.

```yaml
review_gate:
  decision: APPROVED_WITH_CONDITIONS
  reviewed_base: "e26aac4eed0696cefa45b19aac46e7fc9c3da6e8"
  reviewed_head: "7de3043938b4179f5011f82927aaeecc5b82cbd1"
  highest_evidence: VERIFIED
  blocking_findings:
    - GOV-R2-02
    - GOV-R2-03
    - GOV-R2-05
    - GOV-R1-03
  conditions:
    - "Proposal is planner input only; no third repair or renamed batch is authorized."
    - "Package A remains backlog until a new justified and explicitly authorized work packet exists."
    - "Package B requires a real trusted-wrapper/untrusted-source isolation design and independent runtime evidence."
    - "Controller remains FOUNDATION_ONLY and must not block product adoption work."
  owner_decisions: []
  next_checkpoint: "Continue a real ATK tool/skill adoption task through the existing manual GitHub handoff; reopen controller work only with new dependency evidence and a qualifying isolation backend."
  invalidates_when:
    - "controller code changes after 25457fbd2ff02a900d55538eb4e2fa0893663c31"
    - "a qualifying isolation backend becomes available"
    - "a newly authorized product task demonstrates a concrete dependency on controller automation"
    - "trusted main governance or owner direction changes"
```

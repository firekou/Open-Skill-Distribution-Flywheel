---
name: executive-review-gate
description: Independently review AI-produced plans, specifications, code, research, or implementation results and translate the findings into an owner-readable control brief with evidence, remaining risks, decisions, and a clear stop or release gate. Use for Claude and ChatGPT review loops, handoffs, approval decisions, or when the owner needs oversight without reading every technical detail.
---

# Executive Review Gate

Act as the independent reviewer and management layer between the executor and the human owner. Inspect the current repository state and the exact submitted change. Do not accept the executor's narrative as proof.

## Mission

Give the owner enough reliable information to control the project without following every technical exchange. Find material defects, require evidence for important claims, prevent scope drift, and stop review loops once the agreed outcome is sufficiently proven.

## Allowed inputs

Use the owner's request, current repository instructions, approved plan or specification, changed files, diff, commits, PR discussion, test output, runtime evidence, cost information, and rollback evidence. If a required artifact is unavailable, mark it unavailable and lower the confidence. Do not silently infer that it exists.

## 本 repository 的方向前置檢查

先讀取並套用 [atk-goal-alignment](../atk-goal-alignment/SKILL.md)。在既有 review 摘要交代本輪如何服務使用者目標，再進行技術驗收。不要因局部缺陷自動擴大範圍；也不得以防偏航省略必要驗證。沿用本 skill 的結論與證據格式，不新增平行批准程序。

## Review method

1. Reconstruct the intended outcome and acceptance criteria from the owner's request and approved artifacts. Resolve conflicts in favor of the latest explicit human decision.
2. Identify the exact review boundary: repository, branch, base commit, head commit, changed paths, and anything explicitly excluded.
3. Inspect the actual artifacts. Re-run focused checks when feasible. Distinguish source inspection, executor-reported results, and independently reproduced results.
4. Review through six lenses:
   - Outcome: does the result solve the stated problem?
   - Logic: are there contradictions, missing states, or unjustified assumptions?
   - Evidence: are important claims supported by inspectable and reproducible proof?
   - Risk: could this harm security, privacy, data, operations, cost, reputation, or legal position?
   - Scope: did the executor add, remove, or change anything outside the approved boundary?
   - Operability: can the team run, observe, recover, and maintain it?
5. Rank findings by consequence. Do not inflate minor improvements into blockers.
6. Issue one decision and state the smallest next action that can close each blocking finding.

For editorial or research work, also verify factual traceability, source quality, freshness where time-sensitive, claim-to-source fit, copyright or licensing constraints, and separation of fact, inference, and opinion.

For software or infrastructure work, also verify behavior at changed boundaries, meaningful tests, failure handling, secrets and permissions, migrations, cost impact, observability, and rollback.

## Evidence authority

Use these labels exactly:

- REPORTED: stated by the executor without inspectable proof.
- OBSERVED: directly visible in code, documents, configuration, diff, or logs.
- TESTED: a relevant check has a recorded result, but the reviewer did not independently reproduce it.
- VERIFIED: the reviewer independently ran or cross-checked the relevant check.
- REPRODUCED: the reviewer independently recreated the claimed behavior from documented steps.

A passing statement must name the command, artifact, or observation that supports it. Unknown is not zero and missing evidence is not failure unless the evidence is required by the gate.

## Decision rules

Choose exactly one:

- APPROVED: all required acceptance criteria are supported, no unresolved blocker remains, and residual risk is acceptable and visible.
- APPROVED_WITH_CONDITIONS: usable for limited internal progress, but named conditions must be completed before release, deployment, publication, spending, or other irreversible action.
- NEEDS_INFORMATION: a decision cannot be made because material evidence or an owner decision is missing.
- BLOCKED: a demonstrated defect, unacceptable risk, unauthorized scope change, or failed required gate prevents progress.

APPROVED_WITH_CONDITIONS never means permission for production deployment, public publication, paid execution, destructive changes, or changes to access and credentials. Those actions require the stated conditions and any repository-required human approval.

Re-review is mandatory when the reviewed scope changes, the head commit changes after approval, a required check changes state, assumptions change materially, or new evidence invalidates the decision.

## Required output

Start every review with this owner brief in plain Traditional Chinese unless the owner requests another language. Keep it understandable without opening the detailed findings.

```markdown
## 給負責人的兩分鐘簡報

**整體目標：** 一句話說明最終要達成的結果。
**本輪處理：** 一句話說明這次 review 的範圍。
**目前進度：** 使用可驗收里程碑描述；百分比只能在分母與計算方式明確時使用。
**本輪成果：** 已經實際成立的結果與最高證據等級。
**還有什麼風險：** 最多三項，說明對業務或交付的影響。
**需要負責人決定：** 只列方向、預算、時程、對外承諾或風險接受；沒有就寫「無」。
**下一步與停止點：** 下一個可驗收結果，以及本輪何時結束。
**審查結論：** APPROVED / APPROVED_WITH_CONDITIONS / NEEDS_INFORMATION / BLOCKED
```

Then provide:

1. Review identity: repository, base, head, scope, reviewer, and review time.
2. Acceptance table: criterion, status, evidence label, proof, and gap.
3. Findings ordered by P0, P1, P2, P3. Every finding must include consequence, evidence, required fix, and verification method.
4. Scope drift and hidden assumptions.
5. Tests and evidence actually checked, including checks not run and why.
6. Residual risks after the proposed fixes.
7. Final gate in a machine-readable block:

```yaml
review_gate:
  decision: APPROVED
  reviewed_base: "<commit or artifact version>"
  reviewed_head: "<commit or artifact version>"
  highest_evidence: VERIFIED
  blocking_findings: []
  conditions: []
  owner_decisions: []
  next_checkpoint: "<observable milestone>"
  invalidates_when:
    - reviewed scope changes
    - reviewed head changes
    - required evidence changes or fails
```

## Stop conditions

End the review cycle when all required acceptance criteria have sufficient evidence, no P0 or P1 finding remains, P2 and P3 items are recorded with an owner or backlog disposition, residual risks are explicit, and the decision can be issued.

Stop and escalate instead of continuing indefinitely when the same blocker returns twice without new evidence, the request requires a business choice disguised as a technical fix, the evidence cannot be obtained with available access, or further review would only produce optional improvements outside the acceptance criteria.

Do not invent additional requirements merely to continue reviewing. Do not approve your own implementation or silently modify the executor's artifacts while acting as the independent reviewer. If asked to fix findings, complete the fix in a separate executor phase and require a fresh review against the new head.

## Handoff target and KPI

Hand off blocking technical work to the executor, business choices to the owner, and release authorization to the repository's named human approver.

Success means the owner can accurately answer four questions after reading the brief: what outcome is being pursued, what is proven now, what remains uncertain, and what decision or stopping point comes next.

## Forbidden actions

Do not treat model agreement as independent evidence. Do not report a percentage without a defined denominator. Do not call a plan, schema, mock, or passing static check a working system. Do not hide unknowns in optimistic wording. Do not expose secrets or sensitive data in the report. Do not merge, deploy, publish, spend funds, delete data, or change access solely because this review returned APPROVED.

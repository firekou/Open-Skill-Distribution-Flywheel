# PR #15 post-merge governance addendum

- Date: 2026-09-25 (Asia/Taipei)
- Pull request: [#15](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/15)
- Previously reviewed head: `2affb13f8cac09d882144971646cfe8cdf4dc3f2`
- Prior decision: **BLOCKED**
- Prior review: [PR15_R1_ORG_STATUS_2affb13f.md](PR15_R1_ORG_STATUS_2affb13f.md)
- Merge commit: `252bf6dcd8de7bd3072ad044143fa4304bc7622f`
- Merged at: `2026-09-25T05:39:02Z`
- Main parent before merge: `2c9da1dfedbc9af8dc5a5a04c2ebf390eb9f233c`
- Main path now present: `.claude/skills/atk-org-status/SKILL.md`
- Main blob: `cc4c98e85080e9f4bf6a3f97582b1a0e00ce9132`
- Review decision remains: **BLOCKED**
- Operational authority: **NOT GRANTED**
- Merge reversal or content correction: **NOT AUTHORIZED IN THIS RUN**

## What changed

The webhook reported `ready_for_review`, but a fresh live-state read showed that PR #15 had already been merged and closed. The merge commit is now the `main` branch head and contains the exact same skill blob reviewed as blocked.

This addendum records the changed repository state. It does not reinterpret the merge as approval and does not modify the merged skill.

## Independent verification

| Item | Result |
|---|---|
| PR state | closed and merged |
| PR reviewed head | `2affb13f8cac09d882144971646cfe8cdf4dc3f2` |
| Merge commit | `252bf6dcd8de7bd3072ad044143fa4304bc7622f` |
| Main head at verification | exact merge commit above |
| Main skill blob | exact blocked blob `cc4c98e85080e9f4bf6a3f97582b1a0e00ce9132` |
| PR conversation | one reviewer receipt only |
| PR reviews | 0 |
| Workflow runs on PR head | 0 |
| Commit statuses on PR head | 0 |
| Workflow runs on merge commit | 0 |
| Commit statuses on merge commit | 0 |
| Main branch protection | disabled |
| Required status checks | none |

The merge commit is GitHub-signed and attributed to `firekou` through `web-flow`. That proves who performed the GitHub merge action, not that the missing work contract, cross-project evidence, decision conflicts, or parallel-authority design were resolved.

## Governance consequence

The repository now contains a file whose last independent content review is **BLOCKED**. Therefore:

1. Presence on `main` is an observed repository fact, not semantic approval.
2. The skill must not supersede `governance/decisions.json`, `governance/state.json`, `reviews/STATUS.md`, or repository-local decisions.
3. Its cross-project status claims remain unverified unless backed by repository-qualified immutable evidence.
4. Its Open-Skill prohibition cannot override the approved `GOAL`, bounded A4 authorization, or Aider integration decision.
5. Agents must treat the file as non-authoritative until a separately authorized correction is independently reviewed.

## Required remediation decision

A new repository-visible owner decision is required to choose one bounded remedy:

- remove or quarantine the skill from the agent discovery path; or
- replace it with a derived, non-authoritative index that cites immutable sources and explicitly defers to each repository's canonical ledgers; or
- explicitly supersede the conflicting Open-Skill decisions, with scope and consequences recorded.

Any content change requires a new work ID, bounded packet, exact result head, and independent review. No rollback, rewrite, merge, deployment, publication, invitation, secret/permission change, upstream send, or spending action was performed here.

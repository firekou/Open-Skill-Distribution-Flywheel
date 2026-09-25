# PR #15 R1 — ATK organization status skill review

- Date: 2026-09-25 (Asia/Taipei)
- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- Pull request: [#15](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/15)
- Base: `main@fc0b3054b5eeb23441f017ea795d1378a2735d6b`
- Reviewed head: `2affb13f8cac09d882144971646cfe8cdf4dc3f2`
- Commit author / committer: `cursoragent`
- Changed path: `.claude/skills/atk-org-status/SKILL.md`
- Git blob: `cc4c98e85080e9f4bf6a3f97582b1a0e00ce9132`
- Decision: **BLOCKED**
- Highest evidence level: **OBSERVED**
- Merge, publication, deployment, invitation, secret/permission change, upstream send, and new spending: **not authorized**

## Scope reviewed

The head is one commit ahead of its merge base and changes exactly one file, adding a dated organization-status skill. I read the complete diff, the exact Git blob, PR metadata, commit metadata, PR conversation, review submissions, workflow runs, combined commit statuses, trusted `main` governance, decisions, state, status, and the designated goal/review skills.

This review does not validate other repositories, shared-computer files, deployed services, or the business/organizational assertions embedded in the proposed skill.

## Exact-head checks

| Check | Result |
|---|---|
| PR state | Draft, open, unmerged |
| Compare to base | ahead 1, behind 0 |
| Changed paths | 1 |
| PR conversation entries | 0 |
| PR reviews | 0 |
| Workflow runs for exact head | 0 |
| Combined commit statuses | 0 |
| Matching `main` task / work packet | 0 |
| Matching approved decision | 0 |
| Executor response bound to this head | 0 |

`mergeable=true` is only a Git mergeability signal. It is not a governance approval or evidence that the proposed status claims are true.

## Blocking findings

### PR15-R1-01 — No valid work contract or authorization

The PR body supplies a Cursor run link, but no fixed `work_id`, decision ID, revision, source head, bounded scope, acceptance criteria, dedup key, deadline, executor claim, or result response. No corresponding task or approved decision exists in trusted `main`.

A background-agent URL and a user-authored PR event are provenance signals only. They do not authorize a new organization-wide authority source or replace the repository handoff contract.

### PR15-R1-02 — Cross-project claims are not independently traceable

The skill asserts current owners, product status, deployed URLs, PR numbers, branch holds, local replay results, and commercial priorities across several repositories and shared-computer directories. Most assertions have no repository-qualified immutable URL, source SHA, observed time, verifier, or evidence class. Absolute paths such as `/workspace/...` cannot be reproduced from this repository.

The file's own rule says that an “online/approved” claim needs evidence, but the table does not meet that rule. These statements must either be removed from this repository or represented as claim records with repository-qualified immutable evidence and an explicit boundary saying what was not verified.

### PR15-R1-03 — Proposed Open-Skill hard gate conflicts with trusted decisions

The new row says `禁止 fork、上傳、對外邀請`. Trusted `main` currently says:

- `GOAL`: tool sharing, optional ATK integration, external adoption and value recovery;
- `ATK-OPEN-ADOPTION-20260922`: a narrow, gated A4 authorization permits at most three relevant invitations after evidence and account/channel checks;
- `ATK-EXTERNAL-VALUE-CONTINUE-20260924`: one bounded Aider contribution/integration path is approved.

The new text does not cite a superseding owner decision. Treating it as an operational skill would silently override approved product direction and the canonical ledger. It cannot be adopted as written.

### PR15-R1-04 — A mutable snapshot must not become a parallel authority

The proposed usage asks agents to update the dated skill whenever status changes and use it before assignment. That creates a parallel controller beside `governance/decisions.json`, `governance/state.json`, and `reviews/STATUS.md`, without conflict resolution, expiry, provenance, or freshness rules.

If an organization index is wanted, it should be a derived, non-authoritative pointer to canonical records. It must identify source repositories and immutable evidence, include `observed_at` and expiry/freshness semantics, and state that repository-local decisions win on conflict.

## Required resolution

Before another content head can be reviewed:

1. Add a repository-visible owner decision and bounded work packet with a fixed `work_id`, revision, source head, scope, acceptance criteria, and exclusions.
2. Reconcile the Open-Skill hard gate with `GOAL`, `ATK-OPEN-ADOPTION-20260922`, and `ATK-EXTERNAL-VALUE-CONTINUE-20260924`; do not supersede them implicitly.
3. For every retained cross-project status claim, provide a repository-qualified immutable URL/SHA, observed time, verifier, and evidence class, or mark it explicitly unverified and non-operational.
4. Make the skill a derived index rather than a new mutable authority, with precedence and staleness rules.
5. Return a new exact head plus an executor response bound to the authorized work contract.

No repair packet is dispatched from this review because there is no valid authorized work item to revise. The current head remains blocked and must not be merged or used as an operational source of truth.

# PR #19 independent review — ATK-FIRST-USE-PREP-01 revision 1

- Reviewed: 2026-09-26
- Pull request: https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/19
- Exact head: `12b807bcbbd15f3ab156248e980f3ddde3a6b5f0`
- Base branch: `main`
- Work: `ATK-FIRST-USE-PREP-01` revision 1
- Executor session: `session_01RFeCsTYkVywjHvXk7od7Ab`
- Result receipt: https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18#issuecomment-5839734184
- Decision: **BLOCKED**
- Evidence level: **AUTHOR_TESTED_WITH_INDEPENDENT_SOURCE_AND_INTEGRITY_VERIFICATION**

## Scope and identity

The result branch is one commit ahead of its recorded source main and changes exactly seven authorized paths: six first-use preparation documents and the append-only executor response. The claim and result receipt match the saved work_id, revision, source assets, branch, session and executor dedup key.

This review does not authorize publication, outreach, upstream submission, live model/provider calls, credentials, spending, merge, deployment or settings/permission changes.

## Exact-head checks

| Check at `12b807bcbbd15f3ab156248e980f3ddde3a6b5f0` | Result |
|---|---:|
| Workflow runs | 0 |
| Check runs | 0 |
| Commit statuses | 0 |
| PR reviews | 0 |

No CI or GitHub review evidence exists for the exact head.

## Independently verified

- All 7 changed paths are inside the authorized scope.
- The six PR14 entry assets linked from the package were fetched at their 40-character immutable refs. Reviewer-computed SHA-256 matched all 6/6 published values.
- The release gate keeps owner authorization, sender identity, immutable links, privacy, release-day re-read and exact-final-text review separate. Its current decision is correctly **NOT RELEASABLE**.
- The public guides state the evidence ceiling on the first screen, put official Aider documentation first, make ATK optional and disclose that no Aider→ATK real-model run or external adoption exists.
- Live GitHub re-read confirmed:
  - Aider #3396 is closed; its unanswered 2026-01-19 prefix question is stale and weak.
  - Aider #4797 is open but already has a substantive `openai/glm-4.7` answer; additional value is narrow.
  - Aider #4638 is an Ollama-native-path mismatch and is correctly excluded.
- The executor reported `validate_first_use.py` as 42/42 PASS, exit 0. The script is embedded in the response, not a committed operational validator; the reviewer inspected its controls but did not treat the author run as independent replay.

## Blocking findings

### P1-01 — TASK_SUCCESS_INVARIANT_NOT_ENFORCED

`FEEDBACK_SCHEMA.json` describes `task.passed` as true only when the tests pass, the test file is unchanged and the diff was reviewed. The machine contract does not enforce that rule.

A record is accepted with:

- `passed: true`
- `tests_passed: 0`
- `tests_total: 5`
- `test_file_unchanged: false`
- `diff_reviewed: false`

This can convert a failed or tampered attempt into apparent successful adoption evidence. The author validator has no negative control for this contradiction.

### P1-02 — ENTRY_SHA_NOT_BOUND_TO_URL

The schema separately accepts an immutable `entry.url` and `entry.asset_sha`, but does not require the SHA embedded in the URL to equal `asset_sha`. A record can therefore validate while naming one source in the URL and another in the provenance field.

The author validator checks only URL shape and SHA shape; it has no mismatched-SHA counterexample. This prevents a reviewer from knowing which exact material the participant used.

## Decision rationale

The guides and release gates are substantially ready as drafts, but the feedback artifact is intended to become the machine-readable basis for first-use, repeat-use and success claims. Because it currently accepts false-success and false-provenance records, the package is **BLOCKED** for evidence collection. No external action is authorized.

## Bounded repair — revision 2, repair 1/2

- Source head: `12b807bcbbd15f3ab156248e980f3ddde3a6b5f0`
- Dedup key: `firekou/Open-Skill-Distribution-Flywheel:ATK-FIRST-USE-PREP-01:2:12b807bcbbd15f3ab156248e980f3ddde3a6b5f0:conditions`
- Deadline: `2026-09-26T20:15:00Z`
- Signal: https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/19#issuecomment-5839784779
- Allowed paths:
  - `research/adoption/aider/first-use/FEEDBACK_SCHEMA.json`
  - `reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md` (append only)
  - PR #19 body validation/result status lines only

Required closure:

1. Make the published operational validator reject both counterexamples. Because standard JSON Schema cannot compare arbitrary sibling values, remove redundant data and derive it, or commit/use a deterministic cross-field validation mechanism within the authorized artifact. For the fixed five-test task, a schema conditional may enforce `5/5 + unchanged + reviewed`.
2. Add explicit negative controls for the two findings and a positive control for a legitimate passed fixed task.
3. Preserve the other six first-use documents and all pinned source assets byte-for-byte.
4. Return one fixed result SHA with session/run, work_id, revision, source head, dedup key, exact changed paths, command/exit code and finding-closure mapping.

No third-party contact, publication, upstream send, live provider call, spend, merge, deployment, settings, secrets or permissions work is in scope.

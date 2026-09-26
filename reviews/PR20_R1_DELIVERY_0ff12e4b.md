# PR #20 R1 delivery review — `0ff12e4bfa7d18c742ce81276d62bfac19962103`

## Decision

**BLOCKED** for delivery acceptance, merge or publication. The offline package is substantially reproducible, but the feedback validator leaks caller-supplied path text and therefore does not satisfy the packet's output-safety contract.

## Exact state reviewed

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: #20, Draft, open, unmerged
- Base: `main`; PR base SHA `acf84a96b8cef77c6e5f12f50e24ae1fde9a0790`
- Source main fixed by the packet: `bbb85b39001ece19a8f19e3f186c1c3eeb1805cb`
- Content head: `4497e19de8c30effbf3b9b0aecd08463400e96aa`
- Reviewed result head: `0ff12e4bfa7d18c742ce81276d62bfac19962103`
- Range from packet source main: 6 commits, 28 paths, all within the authorized paths
- Exact-head workflow runs: 0
- Exact-head commit statuses: 0
- PR reviews: 0

The PR #19 result receipt binds the expected session, work ID, revision, source SHAs and dedup key to this result head.

## Independent verification

A fresh public clone was checked out at the exact result head.

- Recomputed SHA-256 for all 27 content/evidence files listed before the executor response: **27/27 matched** the executor response.
- `get_assets.py` retrieved and verified all fixed source files: **12/12**, exit 0.
- A clean venv installed the pinned validator dependencies.
- `test_validate_feedback.py`: **11/11 OK**, exit 0.
- All eight fixtures: **2 VALID / 6 INVALID**, batch exit 1 as designed.
- The `failed > total` negative control was rejected.
- A clean venv installed `aider-chat==0.86.1`; `aider --version` returned `aider 0.86.1`, and the resolved OpenAI SDK was `1.99.1`.
- The fixed CSV baseline reproduced `FAILED (failures=1, errors=1)`, exit 1.
- The clearly labelled human reference fix reproduced **5/5 OK**, exit 0. It was not treated as a model result.
- No provider or real model was called.

## Blocking finding

### P1 — ATK-D1-01: validator echoes caller-supplied path text

The packet requires invalid output to contain only the field location and error type and to avoid echoing identity or key material. The implementation prints the supplied `path` in every `VALID`, `INVALID` and file-read error line.

Independent control:

```text
record path:
  /tmp/.../SYNTHETIC_IDENTITY_ALICE_KEYTAG_77.json

observed:
  INVALID /tmp/.../SYNTHETIC_IDENTITY_ALICE_KEYTAG_77.json: /entry additionalProperties
  INVALID /tmp/.../SYNTHETIC_IDENTITY_ALICE_KEYTAG_77.json: /environment/os enum
exit:
  1
```

The JSON value marker remains redacted, but the caller-controlled filename and directories do not. A real ingestion path can contain a person's name, account, ticket or credential-like text. This contradicts the stated output contract and the claim that output contains only pointer/error information.

## Bounded revision 2 acceptance

Repair 1/2 is limited to:

1. `validate_feedback.py`: identify records with a safe ordinal or fixed neutral label; never print the supplied path or basename in normal, malformed, unreadable or schema-related record output.
2. `test_validate_feedback.py`: add negative controls proving a synthetic identity/key marker in both directory and filename is absent from stdout and stderr for valid, invalid, malformed and unreadable inputs.
3. Append the exact commands, exits and new result SHA to the executor response. Existing source assets, raw rehearsal evidence and live/release documents must not be rewritten for this finding.

Acceptance requires all existing tests plus the new path-redaction controls to pass at a new exact result head. Do not perform a live provider call, publication, outreach, merge or credential operation.

## Evidence ceiling and next checkpoint

The verified ceiling remains: reproducible Linux offline delivery and deterministic local validation. It does **not** prove a real-model success, external first use, reuse, adoption, cost value, or economic result.

Next checkpoint: `PR20_R2_VALIDATOR_PATH_REDACTION`.

No merge, deployment, publication, external send, upstream submission, credential operation, provider call or spend was performed.

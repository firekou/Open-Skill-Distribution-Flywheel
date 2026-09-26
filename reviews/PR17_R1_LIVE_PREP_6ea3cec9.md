# PR #17 R1 independent review: Aider live preparation

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- Pull request: [#17](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/17)
- Base branch / observed base: `main` / `887a19d6682fc9a4e15d853fc956505b10fe80d2`
- Reviewed head: `6ea3cec9937e74de8ce77f47c5e92d3d1617c506`
- Work: `ATK-AIDER-LIVE-PREP-01` revision 1
- Session: `session_01RFeCsTYkVywjHvXk7od7Ab`
- Dedup key: `firekou/Open-Skill-Distribution-Flywheel:ATK-AIDER-LIVE-PREP-01:1:b0770499cbef3f5917bd3505433924e0edbb8b27:executor`
- Reviewed at: 2026-09-25T19:10Z
- Reviewer role: independent GitHub evidence review; no PR17 author content was changed

## Decision

**APPROVED_WITH_CONDITIONS**

This decision approves the no-cost, no-secret preparation packet only. It does not authorize a provider call, credential operation, project or key creation, spend, recruitment, publication, merge, deployment, repository setting change, or upstream submission.

## Live state

- PR is open, Draft, unmerged, and reports mergeable.
- 51 changed paths are confined to the authorized three decision documents, `evidence/live-prep/**`, and the appended executor response.
- Exact head workflow runs: 0.
- Exact head commit statuses: 0.
- PR review submissions: 0.
- PR #16 contains a valid claim and a result receipt pointing to this exact head:
  - [claim](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/16#issuecomment-5837692492)
  - [result](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/16#issuecomment-5838048735)
- The existing Claude session received and completed this packet. This is not evidence that a new session was launched by the GitHub comment or that a persistent launcher is operational.

## Independent checks

### 1. Evidence integrity

The reviewer fetched the exact PR head through GitHub and independently recalculated SHA-256:

- 42/42 manifest-referenced raw files matched.
- `retry_exposure_harness.py`: matched `991dc2b4...`.
- `prompt_size_probe.py`: matched `a987eada...`.
- retry manifest: matched the executor-reported `5b34653d...`.
- prompt-size manifest: matched the executor-reported `80df4d6f...`.

This verifies artifact integrity. The loopback behavior remains **AUTHOR_TESTED_WITH_INDEPENDENT_INTEGRITY_VERIFICATION** because this reviewer did not independently rerun Aider 0.86.1.

### 2. Official provider claims

Verified against live official sources on 2026-09-25 UTC:

- [OpenAI spend limits](https://developers.openai.com/api/docs/guides/spend-limits) confirms alert-only limits versus enforced hard limits, project and organization scope, 429 error codes, and non-instantaneous enforcement that can slightly exceed the configured amount.
- [OpenAI GPT-5.6 Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna) confirms model ID, $0.20 input / $1.20 output per million tokens, and `v1/chat/completions` support.
- [OpenRouter limits](https://openrouter.ai/docs/api_reference/limits) confirms per-key credit limits and 402 handling for exhausted key or account credit.
- [OpenRouter GPT-5.6 Luna](https://openrouter.ai/openai/gpt-5.6-luna) confirms the $0.20 / $1.20 headline price and the listed provider range through $0.40 / $2.40.
- Aider upstream commit `5dc9490...` confirms the default `--model-settings-file` is `.aider.model.settings.yml`, so the live commands can rely on project-local automatic discovery.

The `sources.json` entry `OA-PRICING` points to the general pricing page. That page has since changed its visible tables, but the exact model and price remain independently verified on the official model page. Treat the model page as the canonical approval-day source.

### 3. Retry and cost controls

- The packet correctly separates provider enforcement from local retry and token controls.
- It does not treat Aider exit code 0 as success.
- It records the material correction that loopback 402 and 403 responses were retried nine times in the pinned stack.
- The cost formula is intentionally conservative. It is not a true dollar guarantee because provider enforcement can lag and rejected-request billing is unknown.
- The recommended $2 setting is therefore an owner-selected provider limit with disclosed overrun risk, not an absolute local ceiling.

### 4. Scope and safety

The two Python evidence harnesses exceed the literal “text/JSON evidence” wording, but the deviation is accepted as non-blocking. They are confined to the evidence directory, use loopback, contain no secrets, do not alter PR14/PR16 product assets, and materially improve reproducibility.

No evidence shows a real provider call, secret read, account login, key/project creation, spend, publication, recruitment, merge, deployment, permission change, or upstream send.

## Findings

### Closed

- Provider choices, official sources, known/unknown capability fields, exact commands, stop procedure, and owner matrix are present.
- OpenAI hard-limit semantics and GPT-5.6 Luna availability are independently verified.
- OpenRouter per-key limit and model-price claims are independently verified.
- Raw evidence and manifests are internally consistent.
- The PR16 statement “403 does not retry” is superseded for the pinned stack by PR17's tested evidence. PR16 author evidence is preserved and is not rewritten.

### Non-blocking conditions

1. Before any live work, the owner must select exactly one provider or choose no live run.
2. ATK Router remains ineligible until price and reject-type limit evidence are supplied.
3. OpenRouter or OpenAI may proceed only after explicit owner authorization for account/key/project setup, credential injection, and a total spend ceiling.
4. Re-read official model price and endpoint support on the approval day; for OpenAI use the model page above as the canonical source.
5. Save actual request count, tokens, charged amount, retry lines, diff, tests, and failure reason. Do not infer success from exit code.
6. OpenAI's enforced limit may slightly exceed the configured amount. OpenRouter enforcement latency and rejected-request billing remain unknown.
7. This review does not approve merge of PR14, PR16, or PR17.

## Next checkpoint

- Owner-gated path: `OWNER_ATK_AIDER_LIVE_DECISION`.
- No-dependency continuation: bounded `ATK-UPSTREAM-01` read-only deduplication and draft preparation for the 402/403 retry and misleading exit-0 behavior. Drafts may be prepared, but no upstream issue, comment, or pull request may be sent.

## Invalidation

Re-review is required if PR17 content head changes, the selected provider/model differs, official price or limit behavior changes, the live command changes retry/token controls, or any real call is attempted without a new authorized work packet.

# PR #16 R2 independent review — ATK value readiness

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: [#16](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/16)
- Reviewed head: `1dcd625df3bde48b13b91abb3b03eb7e19371558`
- Source reviewed head: `57fa50900035cb6eef316504b065cf98a8b4fee0`
- Work: `ATK-VALUE-READINESS-01` revision 2
- Repair: 1/2
- Review date: 2026-09-26 Asia/Taipei
- Decision: **APPROVED_WITH_CONDITIONS**

## Outcome

Revision 2 closes all four blocking findings from R1. The research package is now suitable as a bounded readiness and feasibility design. It does **not** prove a real provider call, external usefulness, comparative improvement, adoption, reuse, or economic value.

No second repair is required. The remaining conditions are stage gates, not defects in this revision.

## Exact-head and receipt verification

- Live PR is Draft, open, unmerged, base `main`, head `1dcd625df3bde48b13b91abb3b03eb7e19371558`.
- Relative to reviewed R1 head `57fa5090...`, the PR is one commit ahead and does not rewrite the reviewed source.
- Claude result receipt records the fixed work/revision/source/result/dedup tuple:
  - session `session_01RFeCsTYkVywjHvXk7od7Ab`
  - source `57fa50900035cb6eef316504b065cf98a8b4fee0`
  - result `1dcd625df3bde48b13b91abb3b03eb7e19371558`
  - dedup `firekou/Open-Skill-Distribution-Flywheel:16:ATK-VALUE-READINESS-01:2:57fa50900035cb6eef316504b065cf98a8b4fee0:executor`
- Exact result SHA: workflow runs 0, combined commit statuses 0, PR reviews 0. These are not green CI signals; this decision comes from source/evidence review.
- The result comment is valid delivery evidence from an existing Claude session. It still does not prove that a GitHub comment or label can start a new persistent Claude launcher.

## Findings

### P1-01 — CLOSED

The package now treats Aider #4027 as a resolved historical case, not a current unmet need.

Independent GitHub verification confirmed:

- #4027 is closed/completed. Its reporter traced the regression to the LiteLLM 1.65.7 → 1.68.0 change, proposed the `OPENAI_BASE_URL` patch, and later wrote that v0.86.1 no longer reproduced the issue before closing it.
- PR #4144 exists, is closed, and was not merged; the package correctly avoids claiming where the effective fix landed.
- #4797 and #4638 are still open and show v0.86.1 prefix/provider confusion. They are correctly classified only as present-day demand signals, not proof that this asset helped anyone.
- The package records zero current evidence for the base-path-with-route category instead of manufacturing a need.

### P1-02 — CLOSED

The 1–3 person phase is now feasibility-only and uses path B only. It records completion, failure class, help, cost, and uncovered paths, and explicitly forbids A/B improvement claims.

A later comparison is separately gated on:

- a second fixed task with protected tests and structural equivalence;
- completion of the feasibility phase;
- a precommitted minimum useful difference;
- live authorization and budget;
- within-person AB/BA crossover data.

This removes the R1 confounding between material effect and participant differences. Task 2 remains absent, so comparative conclusions remain prohibited.

### P1-03 — CLOSED

The evidence package now binds each case to command/config, environment, fixed versions, fixtures, server readiness, UTC start/end, monotonic duration, exit code, raw outputs, and SHA-256 digests.

Independent integrity verification:

- all 15 referenced raw stdout/stderr/request files were fetched from exact head `1dcd625d...`;
- all 15 recomputed SHA-256 values match `manifest.json`;
- the three base-path request files are distinct and record ports 8851, 8852, and 8853 while all observe `/v1/chat/completions`;
- the retry case records a closed port, exit 0, 78.024 seconds, and eight `Retrying in` lines;
- the two checker cases record exit 3 and match the source issue model strings;
- R1 artifacts remain unchanged and are explicitly downgraded to REPORTED.

The reviewer verified the artifacts and harness structure but did not execute the harness in an independent runtime. Therefore the run remains author TESTED evidence with independently VERIFIED integrity, not REPRODUCED.

The added `evidence/r2_harness.py` is a minor scope deviation from “manifest/raw metadata.” It is accepted as non-blocking because it is confined to the evidence directory, makes the record reproducible, contacts only loopback, does not modify PR14, and does not create product/runtime surface.

### P1-04 — CLOSED

The package no longer assumes a provider has a key/project-level hard cap.

- Provider, model, price, cap scope, rejection behavior, accounting delay, and rejected-request billing remain unknown until selected and checked against official documentation.
- Alert-only controls are distinguished from request-rejecting limits.
- G0 blocks every live step unless a verified rejecting cap exists or the owner explicitly chooses an alternative and accepts the residual risk.
- GitHub credential capability is separated from authorization and credential ownership is unknown.
- Current repository metadata independently confirms public visibility and the connector credential's admin/push capability; this does not grant permission to merge, publish, or change settings.

## Conditions and evidence ceiling

1. No live call until endpoint/model/provider, credential injection, price, token/call/total budget, retry ceiling, and stopping method are fixed and authorized.
2. No external recruitment, invitation, publication, About/topics change, PR14 merge, or upstream submission without the corresponding explicit authorization.
3. Phase 1 may support only individual feasibility findings. Comparative value requires the gated phase 2 design and real paired data.
4. External users, successful live tasks, comparative improvement, reuse, upstream acceptance, and economic value all remain **0 / NOT COLLECTED**.
5. PR #16 remains unmerged; this review does not authorize merge.

## Next checkpoint

`ATK_AIDER_LIVE_PREP_PACKET`

Proceed only with no-cost preparation that does not need credentials: create a bounded owner decision packet for up to three provider/runtime options using current official sources, including endpoint/model choices, pricing date/source, true cap behavior, retry exposure, exact minimal command, protected test hashes, maximum authorized-call formula, stop procedure, and a one-page approval matrix. Do not make a live call, read secrets, change settings, recruit, publish, merge, or spend.


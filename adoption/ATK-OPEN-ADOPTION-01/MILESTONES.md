# M1–M5 work orders (A5)

Each stage is one small delivery, reviewed once per exact head, max two bounded repair rounds;
at the limit the scope shrinks, it does not get a new work_id. Stages run in order; M5 is planning
only until M2 has a result. Budget for new API/model/cloud spend: **0** in every stage unless the
owner sets a figure.

| stage | depends on | work | output | gate to pass | stop / shrink when |
|---|---|---|---|---|---|
| **M1** Routing asset ready | this A package reviewed | independent reviewer replays the offline trial at `304af885` in a qualifying isolated runtime (no secrets, no outbound network, read-only source, no write token), plus P5-R4-01 and the affected tests; apply `pr5-doc-delta.patch` to PR #5 only if the reviewer and PR owner agree | reviewer replay record; a fixed entry (SHA or tag) that every link points to | replay passes; every entry point resolves to one SHA; offline path works without a key | only publication permissions remain → hand over the concrete checklist; do not build a routing engine |
| **M2** External developer / agent use | M1 gate; A4 conditions (verified asset, fixed entry, recipient and channel rules re-checked, account permission) | up to **3** single, targeted invitations from `CANDIDATES.md`, each via the channel recorded there, prefer the recipient's own agent | `records/EXT-*.json` per trial, public-scope as agreed | ≥ 1 non-author developer or their agent completes the task (`EXTERNAL_INVITED_*`, `success: true`) | 3 invitations used with no completed trial → stop inviting, write up the blockers, return to M1 docs; never send a second invitation to the same recipient |
| **M3** Reusable skill | ≥ 1 M2 result (success or documented failure) | extract select / configure / verify / diagnose steps into one skill, following the local skill-creator conventions and saved in git; draft allowed earlier but labelled unproven | `skills/<name>/SKILL.md` + eval notes | a second, independent environment completes the task by the skill alone, and at least one not-applicable case (JSON-lines log, byte-exact payload) is correctly refused | the skill needs a new tool or adapter → out of scope, back to planner |
| **M4** Framework integration contribution | M3 | compare current official capability and open issues of LiteLLM, PydanticAI, Vercel AI SDK, Microsoft Agent Framework; pick **one** target with a concrete need and the smallest change | one small example / doc / fix, duplicate-checked, with an upstream proposal draft | local independent acceptance passes; upstream **sending** needs 3A authorisation and is not done by this stage | no target has a concrete public need → record that, stop; do not build an SDK |
| **M5** Task state / memory | M2 result exists | one-page selection for "task interrupted, another agent resumes": TiDB vs. current storage; re-check the four vendor pages listed in the execution package at the time | selection note + task contract; PoC only if a real need and earlier stages delivered | PoC (if any) verifies restart, isolation, repeated-operation and result consistency; no production migration | vendor claims (one-second creation, branching, tenant isolation) are never written as ours |

## Exact next checkpoint

`M1`: a reviewer run, independent of this executor session, in a qualifying isolated runtime,
replays `adoption/ATK-OPEN-ADOPTION-01/evidence/internal-2026-09-22/` against code SHA
`304af885193245da7186cb6b9ab247ec2494bd86`. The executor cannot supply that; the reviewer
environments on record so far (R6, R9) could not create namespaces.

## Known risks carried forward

- The pinned SHA is reachable because the PR #5 branch exists. A squash-merge plus branch deletion
  could make it unreachable. Before M2 invitations, the PR owner should either keep the branch or
  create a tag at `304af885` (a repository write; owner action).
- Transitive dependencies are not pinned; the observed set is in
  `evidence/internal-2026-09-22/pip_freeze.txt`.
- onnxruntime (transitive) creates a device id file; transmission on a networked machine is
  untested.

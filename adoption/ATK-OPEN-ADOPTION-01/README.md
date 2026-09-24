# ATK-OPEN-ADOPTION-01 — A package (revision 1)

Open-source developers, and the agents they operate, try one existing asset — headroom + optional
ATK — offline, without an ATK account or key. This directory is the adoption layer. The asset's
code stays on PR #5 at `304af885193245da7186cb6b9ab247ec2494bd86`; nothing from it is copied here.

| item | file | what it is |
|---|---|---|
| **A1** unified trial entry | `integrations/headroom-atk/TRY_IT.md` @ `304af885` + [pr5-doc-delta.patch](pr5-doc-delta.patch) | TRY_IT stays the single command source. The patch (docs + one docstring, 5 files) pins every checkout to the SHA, points the free sample at TRY_IT and adds the retry flag, fixes the "two attempts either way" wording, pins the docstring install, and links the agent contract. **Not applied to PR #5** — the PR owner applies it, or not |
| **A2** agent contract | [AGENT_QUICKSTART.md](../../integrations/headroom-atk/AGENT_QUICKSTART.md), [agent-manifest.json](../../integrations/headroom-atk/agent-manifest.json) | when to use / not use, pinned version, install, I/O, exit table, stop conditions, network and file writes, cost, live preconditions, optional provider config, report entry |
| **A3** discovery and channels | [DISTRIBUTION_CHANNELS.md](DISTRIBUTION_CHANNELS.md), [TRIAL_TASK.md](TRIAL_TASK.md) | channel rules checked 2026-09-22 and a fit decision each; DIRECT_INVITE / PUBLIC_DISCOVERY / DIRECTORY_DISCOVERY protocols |
| **A4** first invitations | [CANDIDATES.md](CANDIDATES.md), [INVITATIONS.md](INVITATIONS.md) | five public entry points (two to send, three not); English replies and the agent task text. **Nothing sent** |
| **A5** evidence and milestones | [EVIDENCE_FORMAT.md](EVIDENCE_FORMAT.md), [adoption-record.schema.json](adoption-record.schema.json), [validate_records.py](validate_records.py), [records/](records/), [MILESTONES.md](MILESTONES.md) | one record per trial; internal / invited / discovered kept apart and enforced; M1–M5 work orders |
| internal evidence | [evidence/internal-2026-09-22/](evidence/internal-2026-09-22/) | our own run: outputs, controls, installed versions, dependency licences, files written to `$HOME`, the isolation wrapper |
| checks | [check_consistency.py](check_consistency.py) | offline: manifest ↔ quickstart ↔ pinned SHA ↔ patch ↔ records |

Run the checks from the repo root after `git fetch origin claude/atk-headroom-adoption`:

```bash
python3 adoption/ATK-OPEN-ADOPTION-01/check_consistency.py
python3 adoption/ATK-OPEN-ADOPTION-01/validate_records.py adoption/ATK-OPEN-ADOPTION-01/records/*.json
```

External adoption to date: **none recorded.**

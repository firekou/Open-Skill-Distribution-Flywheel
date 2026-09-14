# UPSTREAM_SYNC.md

> ATK Upstream Sync Strategy · Version 1.0 · Last updated: 2026-09-14

---

## 1. The Problem

The biggest failure mode of a fork is **drift**. Upstream moves, the fork does not, and six
months later the two are unmergeable. At that point ATK owns a stale copy of someone else's
project — the fork graveyard, arrived at gradually rather than all at once.

Sync is therefore a scheduled operation with an owner, not a reaction to a broken build.

---

## 2. Tracking Record

Every ATK fork carries `.atk/upstream.json`:

```json
{
  "upstream_repository": "mvanhorn/last30days-skill",
  "upstream_url": "https://github.com/mvanhorn/last30days-skill",
  "upstream_branch": "main",
  "upstream_license": "MIT",
  "fork_created": "2026-09-20",
  "last_sync": "2026-09-20",
  "last_synced_commit": "<sha>",
  "sync_cadence_days": 7,
  "atk_changes": [
    {
      "path": "src/providers/atk.py",
      "type": "addition",
      "scope": "routing",
      "conflict_risk": "low",
      "note": "ATK Router provider adapter (new file)"
    },
    {
      "path": "src/config.py",
      "type": "modification",
      "scope": "routing",
      "conflict_risk": "high",
      "note": "Provider selection now reads ATK_PROVIDER; touches upstream hot path"
    }
  ],
  "conflict_status": "clean",
  "owner": "atk-distribution"
}
```

`conflict_status` ∈ `clean` · `pending_review` · `conflicted` · `blocked`.

### Why `conflict_risk` per change matters

ATK changes fall into two classes, and they behave completely differently at merge time:

| Class | Example | Conflict risk |
|---|---|---|
| **Additive** — new files | `src/providers/atk.py` | Low — merges cleanly almost always |
| **Invasive** — edits to upstream files | changing `config.py` provider logic | High — conflicts on every upstream refactor |

**Design principle: prefer additive changes.** Where an invasive edit is unavoidable, make it
the smallest possible hook into an additive module. A one-line registration call that
delegates to `atk.py` survives upstream refactors; a 200-line inline provider block does not.

---

## 3. Sync Pipeline

```
Check Upstream
      ↓
Detect New Commits
      ↓
Generate Diff
      ↓
Risk Analysis            ← does this touch any path in atk_changes?
      ↓
Compatibility Test
      ↓
Merge Candidate          ← branch sync/<date>
      ↓
ATK Modification Test    ← do ATK features still work?
      ↓
Human / Agent Review
      ↓
Merge
      ↓
Release
```

**Upstream updating is not a reason to merge immediately.** The question the pipeline exists
to answer is:

> **Will this upstream update break the ATK modification?**

---

## 4. Risk Classification

| Class | Definition | SLA | Action |
|---|---|---|---|
| **P0 — Security** | Upstream fixes a vulnerability | 24h | Merge immediately; fix ATK conflicts under hotfix |
| **P1 — Breaking** | Upstream changes an API/interface ATK depends on | 7d | Full compatibility test; may need adapter rewrite |
| **P2 — Feature** | New upstream capability | 14d | Merge on the normal cadence |
| **P3 — Cosmetic** | Docs, formatting, tests | 30d | Batch into the next sync |

**Risk analysis rule:** if the upstream diff touches **any path listed in `atk_changes`**,
the sync is automatically at least P1, regardless of how trivial the change looks.

---

## 5. Merge Procedure

```bash
# 1. Refresh the pristine mirror
git fetch upstream
git checkout upstream-main
git merge --ff-only upstream/main          # must fast-forward; if not, upstream rewrote history

# 2. Open a sync branch off ATK main
git checkout main
git checkout -b sync/2026-09-21

# 3. Merge (never rebase a published fork)
git merge upstream-main

# 4. Resolve, then verify ATK features specifically
#    - ATK Router adapter still selected by default
#    - a NON-ATK provider still works
#    - fallback path still triggers
#    - token tracking still records

# 5. QA, then PR into main
```

Use **merge, not rebase**. The fork is published; rebasing rewrites history that other
people have already cloned.

### If `--ff-only` fails

Upstream rewrote history (force-push, squashed release). Do not paper over it:

1. Record the event in `.atk/upstream.json` under a `history_rewrites` array
2. Re-derive the ATK change set as a patch series against the new upstream base
3. Reset `upstream-main` to the new upstream head
4. Re-apply the ATK patch series onto a fresh `main`

This is expensive, which is the practical argument for keeping ATK changes additive.

---

## 6. Compatibility Test Matrix

Run on every sync candidate before merge:

| Test | Passes when |
|---|---|
| Install | Cold clone → documented install → success |
| Build | Build/lint/typecheck clean |
| Upstream smoke | The project's own core feature works unchanged |
| ATK routing | `provider=atk` routes correctly |
| **Provider switching** | `provider=openai` (or any non-ATK) works |
| Fallback | Primary failure falls through to secondary |
| Token tracking | Usage recorded with correct cost attribution |
| Regression | Previously fixed ATK bugs stay fixed |
| Security | Dependency audit clean; no new network egress |

A sync that passes rows 1–3 but fails rows 4–7 is **not** mergeable. The upstream project
works; the ATK distribution does not — and the ATK distribution is what was published.

---

## 7. Automation

| Frequency | Job | Output |
|---|---|---|
| Daily | Poll upstream for new commits/releases/advisories | Sync queue entry |
| On new commit | Classify P0–P3; flag overlap with `atk_changes` | Risk note |
| Weekly | Open `sync/<date>` for all P2/P3 | Sync PR |
| On P0 | Immediate hotfix branch + page the owner | Hotfix PR |
| Monthly | Report drift across all forks | `reports/upstream-drift.md` |

### Drift metrics

| Metric | Definition | Threshold |
|---|---|---|
| `commits_behind` | Upstream commits not in ATK `main` | > 100 → escalate |
| `days_since_sync` | Days since last successful merge | > 30 → escalate |
| `conflict_count` | Files conflicting on a dry-run merge | > 5 → redesign the integration |
| `invasive_change_ratio` | Invasive ÷ total ATK changes | > 0.3 → redesign toward additive |

`invasive_change_ratio` is the leading indicator. The other three tell you a fork is already
in trouble; this one tells you it will be.

---

## 8. Escalation

| Situation | Response |
|---|---|
| Upstream archived | Freeze fork, mark `unmaintained`, decide: adopt fully or retire |
| Upstream license changed to a failing license | **Immediate** removal from distribution; keep the last compliant tag for existing users, publish a notice |
| Upstream rewritten (v2 incompatible) | Treat as a new candidate; re-score, re-review |
| Conflicts unresolvable in 2 cycles | Redesign the ATK integration as a **separate package** depending on upstream, rather than a fork |

That last row is the pressure valve. When a fork becomes too expensive to sync, the right
answer is usually not "sync harder" — it is to stop forking and ship the ATK layer as an
add-on package that upstream users can install alongside.

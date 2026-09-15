# Open Skill Distribution Flywheel

> Strategy, policy and operating system for the **AI Token King (ATK) Open Skill
> Distribution Network**.
> Phase 1 · Snapshot 2026-09-14

ATK does not try to control external open-source projects, and does not depend on other
projects accepting its pull requests. Instead it finds AI Skills, Agents, MCP servers,
Routing layers and developer tools the market has already validated and — where the license
allows — forks, maintains, improves, integrates and redistributes them through GitHub and
social assets ATK controls.

```
Discover → Fork → Improve → Integrate → Publish → Distribute → Use → Feedback → Update
```

---

## Start here

| Document | What it is |
|---|---|
| [`ATK_OPEN_SKILL_STRATEGY.md`](./ATK_OPEN_SKILL_STRATEGY.md) | The strategy of record |
| [`SKILL_SCORING.md`](./SKILL_SCORING.md) | The 100-point `skill_score` rubric |
| [`LICENSE_REVIEW.md`](./LICENSE_REVIEW.md) | The License Gate — an independent veto |
| [`FORK_POLICY.md`](./FORK_POLICY.md) | When to fork, required value-add, branch model |
| [`UPSTREAM_SYNC.md`](./UPSTREAM_SYNC.md) | Keeping forks alive against upstream drift |
| [`ATK_ROUTING_INTEGRATION.md`](./ATK_ROUTING_INTEGRATION.md) | Provider interface contract and reference adapter |
| [`CONTENT_DISTRIBUTION.md`](./CONTENT_DISTRIBUTION.md) | 1 repository → 5–20 content assets |
| [`ANALYTICS_METRICS.md`](./ANALYTICS_METRICS.md) | Funnel, metrics and the MAAPP north star |

## Phase 1 findings

| Report | Contents |
|---|---|
| [`reports/CANDIDATE_REGISTRY.md`](./reports/CANDIDATE_REGISTRY.md) | 68 candidates discovered, scored and gated |
| [`reports/TOP10_SHORTLIST.md`](./reports/TOP10_SHORTLIST.md) | Top 10 by score, among license-eligible candidates |
| [`reports/TOP10_DEEP_REVIEW.md`](./reports/TOP10_DEEP_REVIEW.md) | Technical + license review of the Top 10 |
| [`reports/FORK_RECOMMENDATIONS.md`](./reports/FORK_RECOMMENDATIONS.md) | The recommended first 4 forks — **and the gate that blocks them** |

### Headline numbers

| | |
|---|---|
| Candidates discovered | **68** |
| Priority A (score ≥ 80) | 21 |
| License Gate PASS | 58 |
| Blocked — AGPL or non-standard license | 8 |
| Blocked — no license file at all | 2 |
| Rejected — strategic conflict | 3 |
| Recommended first forks | **4** |
| Forks approved to execute | **0** — security review and maintainer assignment outstanding |

The last row is the important one. Two `FORK_POLICY.md` entry conditions — security review
and a named maintainer — are unmet, so **this phase stops at recommendation**, exactly as the
brief requires.

## Tools

```bash
python3 tools/build_registry.py                  # rebuild the registry from the candidate table
python3 tools/score.py --eligible-only --top 10  # validate scores and print the Top 10
python3 tools/render_candidates.py               # regenerate the candidate report
```

`tools/score.py` recomputes every total from its six components and fails loudly on mismatch,
so a hand-edited score can never silently drift from the reasoning behind it. It also
enforces the License Gate invariant: a candidate whose license is unverified cannot carry any
decision other than `blocked`.

## Templates

[`templates/README_TEMPLATE.md`](./templates/README_TEMPLATE.md) ·
[`templates/env.example`](./templates/env.example) ·
[`templates/CONTENT_BRIEF_TEMPLATE.md`](./templates/CONTENT_BRIEF_TEMPLATE.md)

---

## Two principles that constrain everything else

**1. The License Gate is independent of the score.** A repository may score 100 and still be
blocked. 10 of 68 are, including `OpenMontage` at 85 (AGPL-3.0 network copyleft) and
`anthropics/skills` — the most-starred project in the sweep, which has no LICENSE file at
all. Attribution does not substitute for a license; see `LICENSE_REVIEW.md` §9–10 for why,
and for the four legitimate ways to get the same value.

**2. ATK Routing must be transparent, replaceable, documented and optional.** ATK may be the
Quick Start default; it may never be the only path. Locking a provider would convert ATK's
distribution advantage into the reason developers avoid ATK forks — the one outcome this
strategy cannot survive. See [`ATK_ROUTING_INTEGRATION.md`](./ATK_ROUTING_INTEGRATION.md) §1
and §8.

## Data provenance

All repository metrics are a point-in-time snapshot from the GitHub repository search API,
verified in two passes (**2026-09-14** and **2026-09-15**). Licenses were confirmed against GitHub's own license metadata; a README badge
or a repository description was never accepted as evidence. Star and issue counts move —
re-run `tools/build_registry.py` to refresh.

## License

[MIT](./LICENSE) — this repository contains ATK's own strategy and tooling. Licenses of the
projects it catalogues remain with their respective authors.

# Open Skill Distribution Flywheel

> **Architecture R2: ATK Technical Intelligence & Distribution Engine**
>
> The repository is now **discovery-first**. Its primary job is to find useful AI technical material, understand it, turn it into content/experiments, and only then decide whether integration or redistribution is warranted.
>
> **Critical rule:** License Gate is a redistribution gate, not a discovery gate.

```
Discover → Understand → Classify → Test → Contentize → Distribute → Observe → Discover
                         ├→ Research / Tutorial / Content
                         ├→ Experiment / Companion Adapter
                         └→ Fork / Deep ATK Integration
```

## R2 start here

| Document | Purpose |
|---|---|
| [ARCHITECTURE_R2.md](./ARCHITECTURE_R2.md) | New system architecture and three-lane model |
| [DISCOVERY_ENGINE.md](./DISCOVERY_ENGINE.md) | Technical-material mining engine |
| [DISCOVERY_PIPELINE.md](./DISCOVERY_PIPELINE.md) | Executor runbook and 120-candidate benchmark |
| [TREND_SCORING.md](./TREND_SCORING.md) | Material and content opportunity scoring |
| [registry/SOURCE_REGISTRY.json](./registry/SOURCE_REGISTRY.json) | Where ATK mines signals |
| [registry/MATERIAL_SCHEMA.json](./registry/MATERIAL_SCHEMA.json) | Canonical material-card schema |

## Three lanes

**Lane A — Discovery & Material Intelligence:** MCP, A2A, Agent Frameworks, Skills, Routing, Model Gateways, token/cost optimization and the wider agent stack. Discovery continues even when a project is not forkable.

**Lane B — Content & Distribution:** convert qualified material into technical cards, tutorials, social briefs, experiments and ATK angles for ATK-owned distribution channels.

**Lane C — Integration & Redistribution:** only this lane invokes the existing License Gate, Security Review, Maintainer Gate, Fork Policy and Upstream Sync controls.

---

## Existing integration and redistribution framework

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
| [`reports/BENCHMARK_R2_001.md`](./reports/BENCHMARK_R2_001.md) | R2 discovery benchmark: 164 materials from GitHub, four ranked lists |
| [`reports/BENCHMARK_R2_002.md`](./reports/BENCHMARK_R2_002.md) | **Current run** — adds the four unmined source classes; 188 materials |
| [`registry/materials.json`](./registry/materials.json) | The R2 material registry (MATERIAL_SCHEMA v2.0) |

### Headline numbers

| | |
|---|---|
| Candidates discovered | **68** |
| Priority A (score ≥ 80) | 21 |
| License Gate PASS | 58 |
| Blocked — copyleft or source-available license | 6 |
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
blocked. 8 of 68 are — `OpenMontage` at 85 (AGPL-3.0), `context-mode` at 82 (Elastic License
2.0, no hosted service), `ThinkWatch` (Business Source License, free only to 10M tokens a
month), and `anthropics/skills`, the most-starred project in the sweep, which has no LICENSE
file at all. Attribution does not substitute for a license; see `LICENSE_REVIEW.md` §9–10 for
why, and for the four legitimate ways to get the same value.

Every license was read or verified against GitHub metadata — the six that GitHub could not
identify were fetched and read in full. Two cleared; four turned out to be deliberately
restrictive.

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

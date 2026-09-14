# FORK_POLICY.md

> ATK Fork SOP · Version 1.0 · Last updated: 2026-09-14

---

## 1. The Rule

> **ATK does not fork popular repositories. ATK forks repositories it intends to maintain.**

A fork is a *maintenance commitment*, not a bookmark. Before forking, the Fork Agent must be
able to answer: *who syncs this in 90 days, and what breaks if nobody does?*

---

## 2. Entry Conditions (all required)

| # | Condition | Source of truth |
|---|---|---|
| 1 | `skill_score` ≥ 80 (Priority A) | `SKILL_SCORING.md` |
| 2 | License Gate ruling = `PASS` (or signed-off `CONDITIONAL`) | `LICENSE_REVIEW.md` |
| 3 | Technical Review passed | Review note |
| 4 | Security Review passed | Review note |
| 5 | Upstream is **not archived** | Registry snapshot |
| 6 | A written **Value Add plan** exists | §4 of this document |
| 7 | A named maintainer owns it | Registry `owner` field |

Missing any one → no fork. This is enforced by the registry `decision` field: only
`decision: "fork_approved"` may be acted on.

---

## 3. Upstream-First Courtesy

ATK's strategy does not *depend* on upstream accepting contributions — but where a change is
obviously good for everyone (a bug fix, a provider seam that costs upstream nothing), **open
the PR first and wait one review cycle** before shipping it only in the ATK fork.

Reason: the entire distribution strategy is built on developer trust. A maintainer who finds
out about ATK by discovering a rebranded copy of their work reacts differently than one who
first saw a useful PR. The cost of asking is a few days; the cost of being seen as a
value-extractor is the strategy itself.

This is a courtesy rule, not a blocker. If upstream declines, is unresponsive for 14 days, or
the change is genuinely ATK-specific (an ATK Router adapter is), ship it in the fork.

---

## 4. Required Value Add

> **Every ATK fork must ship at least one Value Add from the list below, and it must be
> real at publish time — not on a roadmap.**

### A. Integration
- ATK API adapter
- ATK MCP integration
- ATK Router support
- Multi-model routing
- Token budget enforcement
- Cost tracking

### B. UX
- Quick Start that works from a cold clone
- Docker / `docker compose`
- `.env.example` covering every required variable
- One-command install
- At least one runnable example
- Tutorial

### C. Compatibility
Provider support across OpenAI · Anthropic · Gemini · DeepSeek · Qwen · ByteDance ·
OpenRouter · ATK

### D. Reliability
Fallback · Retry with backoff · Rate limiting · Observability · Structured logging ·
Error handling

### E. Documentation
README · Examples · Architecture · Use cases · FAQ · Troubleshooting

### Minimum bar for a Phase 1 fork

Not "one item" in practice — the honest minimum that justifies redistribution is:

- **One item from A** (the reason ATK exists in this repo), **and**
- **`.env.example` + Quick Start + one runnable example** from B, **and**
- **`CHANGES-ATK.md`** from E (also a License Gate requirement)

A fork that cannot clear that bar should be a **link in `awesome-ai-skills`**, not a fork.

---

## 5. Positioning

| Never | Always |
|---|---|
| "We copied this project" | "ATK maintains a production-ready distribution of this project, with multi-model routing and additional integrations" |
| Silent rebrand | Prominent upstream attribution above the fold |
| Bare upstream name | `atk-<name>` |
| Implied endorsement | "Not affiliated with or endorsed by the upstream authors" |

---

## 6. Repository Layout

```
atk-<name>/
├── LICENSE                 # upstream license, unmodified
├── NOTICE                  # upstream attribution
├── CHANGES-ATK.md          # every ATK modification, dated
├── README.md               # ATK README template; upstream credit above the fold
├── .env.example            # every variable, documented, no real secrets
├── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROUTING.md          # how to switch providers away from ATK
│   ├── FAQ.md
│   └── TROUBLESHOOTING.md
├── examples/
│   └── quickstart/
├── .atk/
│   ├── upstream.json       # upstream tracking (see UPSTREAM_SYNC.md)
│   └── qa-report.md
└── <upstream source tree>
```

---

## 7. Branch Model

| Branch | Purpose | Rule |
|---|---|---|
| `upstream-main` | Pristine mirror of upstream | **Never** commit ATK code here |
| `main` | ATK distribution | `upstream-main` merged in + ATK commits |
| `atk/<feature>` | Work in progress | Merged into `main` via PR |
| `sync/<date>` | Upstream merge under review | Merged into `main` after QA |

Keeping `upstream-main` pristine is what makes a clean three-way diff possible months later.
Skipping it is the single most common reason forks become unmergeable.

### ATK commit convention

```
atk: <what changed>

Scope: routing | ux | compat | reliability | docs
Upstream-Impact: none | conflicts-with <path>
```

`Upstream-Impact` is what lets the Upstream Agent predict merge conflicts before running the
merge.

---

## 8. Publish Checklist

- [ ] License Gate `PASS` recorded in registry
- [ ] LICENSE unmodified at root
- [ ] NOTICE present
- [ ] `CHANGES-ATK.md` complete
- [ ] README attribution above the fold
- [ ] Renamed to `atk-<name>`
- [ ] At least one Value Add from category A shipped
- [ ] `.env.example` complete, **no real keys committed**
- [ ] Quick Start verified from a cold clone on a clean machine
- [ ] Provider switching documented and **tested with a non-ATK provider**
- [ ] Fallback path tested
- [ ] QA report in `.atk/qa-report.md`
- [ ] `.atk/upstream.json` populated
- [ ] Registry entry updated to `decision: "forked"`
- [ ] Content brief handed to the Content Agent

The "tested with a non-ATK provider" item is not optional. It is the check that keeps the
Routing Integration Principle honest.

---

## 9. Retirement

A fork is retired when it stops earning its maintenance cost. Reviewed at each 90-day cycle:

| Trigger | Action |
|---|---|
| Upstream archived | Freeze, mark `unmaintained`, keep for reference |
| Upstream rewritten incompatibly | Re-evaluate as a new candidate |
| ATK-attributable token usage ≈ 0 for 60 days | Retire |
| Maintenance cost exceeds value for 2 cycles | Retire |
| License changed to a failing license | **Immediate** removal from distribution |

Retirement is not failure — it is what prevents the fork graveyard. Publish a short,
non-defensive deprecation note and point users at upstream.

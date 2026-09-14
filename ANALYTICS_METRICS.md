# ANALYTICS_METRICS.md

> ATK Analytics & Metrics · Version 1.0 · Last updated: 2026-09-14

---

## 1. Principle

> **Do not assume that "someone used it" means viral growth. Measure it.**

The strategy contains one large unvalidated assumption — that 300k–500k monthly social
impressions convert into developer adoption and then into token consumption. Every number
downstream of that assumption is a projection until the funnel is instrumented. This
document exists to replace the projection with data.

---

## 2. North Star — MAAPP

> **MAAPP — Monthly Active ATK-Powered Projects**
>
> The number of **distinct projects** that, within a calendar month, actually executed work
> through ATK Routing / API / MCP.

| | |
|---|---|
| **Unit** | Distinct project, not distinct user and not distinct API key |
| **Threshold** | ≥ 1 successful routed request in the month |
| **Why not stars** | Stars measure attention. MAAPP measures dependency. |
| **Why not signups** | A signup that never routes a request is a cost, not a result. |
| **Why not tokens** | Raw token volume is dominated by a few heavy users; MAAPP measures breadth, which is what distribution is supposed to produce. |

Track token volume **alongside** MAAPP, never instead of it. MAAPP × tokens-per-project is
the revenue picture; MAAPP alone is the distribution picture.

**Project identity** is derived from a stable installation ID generated locally on first run
— never from a machine fingerprint, and never from anything that identifies a person.

---

## 3. The Funnel

```
Social Impression
      ↓  CTR
GitHub Visit
      ↓  visit → clone
Clone
      ↓  clone → first success        ← the decisive step
Successful Run
      ↓
ATK Activation
      ↓
Token Consumption
      ↓
Repeat Usage
```

| Stage | Metric | Source | Phase 1 target |
|---|---|---|---|
| Impression | Impressions | Platform analytics | 300k–500k/mo *(to validate)* |
| Click | Click-through rate | Platform + UTM | ≥ 1.0% |
| Visit | Unique visitors | GitHub Traffic API | — |
| Clone | Clones, unique cloners | GitHub Traffic API | ≥ 8% of visitors |
| **Successful Run** | First-run success | Opt-in telemetry / survey | **≥ 60% of cloners** |
| Activation | ATK key configured + 1 routed request | ATK API | ≥ 15% of successful runs |
| Consumption | Tokens routed | ATK API | — |
| Repeat | Projects active in month N and N+1 | ATK API | ≥ 40% |

**Clone → Successful Run is the stage that decides everything.** It is also the only stage
ATK fully controls, through Quick Start quality, `.env.example` completeness and
documentation. A fork that loses developers here wastes all upstream funnel spend — which is
why `FORK_POLICY.md` §4 makes those items mandatory rather than optional.

---

## 4. Metric Definitions

### GitHub (per repository)

| Metric | Source | Cadence | Note |
|---|---|---|---|
| Views / Unique visitors | Traffic API | Daily | **14-day retention — must be snapshotted daily or it is lost** |
| Clones / Unique cloners | Traffic API | Daily | Same 14-day limit |
| Stars, Forks | Repo API | Daily | Track *deltas*; absolutes flatter |
| Referrers | Traffic API | Daily | Attributes social channels |
| Issues / PRs opened | Issues API | Weekly | Engagement depth |
| Release downloads | Releases API | Weekly | Where applicable |

### Social

Impressions · Clicks · CTR · Saves/Bookmarks · Comments · Follower delta

Per post, per channel, tagged to a repository.

### ATK Platform

| Metric | Definition |
|---|---|
| Signups | New accounts (attributed via UTM/referral where available) |
| Activation | Account with ≥ 1 successful routed request |
| **MAAPP** | Distinct projects with ≥ 1 routed request this month |
| Tokens routed | Total, and per project |
| Revenue per project | For unit-economics |
| Returning projects | Active in month N and N+1 |
| Provider mix | Share of requests per downstream model |

---

## 5. Attribution

Attribution across social → GitHub → ATK is **lossy by design** — GitHub strips most
referrer detail and developers clone from the command line where no referrer exists. Do not
pretend otherwise; use three independent, honest methods:

1. **UTM on every social link**
   `?utm_source=x&utm_medium=social&utm_campaign=atk-<repo>&utm_content=<beat>`
2. **Per-channel short links** to recover click counts GitHub cannot report.
3. **Opt-in install telemetry** — an install-source prompt or an `ATK_REFERRAL` variable in
   `.env.example`. **Opt-in only**, disclosed in the README.

**Never ship silent telemetry.** Undisclosed egress is a security-review failure
(`ATK_ROUTING_INTEGRATION.md` §9), and being caught doing it would cost more trust than the
attribution data is worth.

Where attribution is genuinely unavailable, report it as **unattributed** rather than
assigning it to the most convenient channel.

---

## 6. Viral Coefficient

```
K = invitations_per_user × conversion_rate_of_invitation
```

For an open-source distribution model, the practical proxy is:

```
K ≈ (forks + shares + inbound_links) per active project × their activation rate
```

| K | Meaning |
|---|---|
| K > 1 | Self-sustaining growth |
| 0.5 < K < 1 | Growth with continuous input — the realistic Phase 1 target |
| K < 0.5 | Paid/effort-driven growth only |

Measure K **per repository**. It varies enormously by category: a visual skill (diagrams,
media) spreads on screenshots; an infrastructure gateway does not spread at all but converts
far better once adopted. Judging both by the same K is how good infrastructure gets killed.

---

## 7. Weekly Report

```markdown
# ATK Distribution — Week of <date>

## North Star
MAAPP: <n>  (prev <n>, Δ <±n>)

## Funnel
| Stage | This week | Last week | Δ |
|---|---|---|---|
| Impressions | | | |
| GitHub visits | | | |
| Clones | | | |
| Successful runs | | | |
| Activations | | | |
| Tokens routed | | | |

## Per repository
| Repo | Visits | Clones | Stars Δ | Activations | Tokens |
|---|---|---|---|---|---|

## Top / bottom performers
## Decisions
- Promote: <repo> — <evidence>
- Retire: <repo> — <evidence>
## Unattributed traffic: <n>% 
```

---

## 8. 90-Day Review

At the end of Phase 3, rank every repository by **token consumption per maintenance hour**.

| Quartile | Action |
|---|---|
| Top 25% | Double down — more content, deeper integration |
| Middle 50% | Maintain at current cost |
| Bottom 25% | Retire per `FORK_POLICY.md` §9 |

Expect concentration: a small number of skills will produce most of the usage. The purpose
of the review is to find them and stop subsidising the rest — not to defend the original
selection.

---

## 9. Instrumentation Checklist (Phase 1)

- [ ] Daily GitHub Traffic API snapshot into durable storage *(14-day window — start before
      the first fork ships, or the earliest data is permanently lost)*
- [ ] UTM convention published and enforced in the content brief
- [ ] Per-channel short-link service
- [ ] ATK API: project-level request attribution
- [ ] MAAPP query defined and scheduled
- [ ] Activation event defined (first successful routed request)
- [ ] Opt-in referral field in `.env.example`, disclosed in README
- [ ] Weekly report automated
- [ ] Baseline social impressions recorded **before** the first fork ships

The last item is what converts the 300k–500k impression figure from an assumption into a
measured input. Without a pre-launch baseline there is nothing to compare against, and the
first month's results will be uninterpretable.

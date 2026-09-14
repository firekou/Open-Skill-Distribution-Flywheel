# SKILL_SCORING.md

> ATK `skill_score` rubric · Version 1.0 · Last updated: 2026-09-14

Every candidate repository receives a `skill_score` out of 100. The score is recorded in
`registry/skill_registry.json` and is recomputed by `tools/score.py`, so a score is always
reproducible from its six components — never asserted as a bare number.

---

## 1. Dimensions

| Dimension | Max | Question it answers |
|---|---|---|
| **Utility** | 25 | Does it actually solve a real problem? |
| **Trend** | 20 | Is the market moving toward it right now? |
| **ATK Fit** | 20 | Does it combine naturally with ATK Routing / API / MCP? |
| **Distribution** | 15 | Is it easy to build social content from? |
| **Maintenance** | 10 | Is the ongoing maintenance cost acceptable? |
| **Commercial** | 10 | Will it plausibly generate token usage? |
| **Total** | **100** | |

---

## 2. Scoring Bands

### Utility — 25

| Range | Meaning |
|---|---|
| 21–25 | Solves a problem a working developer hits weekly; no clean alternative |
| 16–20 | Genuinely useful; alternatives exist but this one is better |
| 11–15 | Useful in a niche, or a nicer wrapper over something common |
| 6–10 | Demo-grade; interesting but rarely reached for |
| 0–5 | Toy, or a list-of-links with no executable value |

An awesome-list scores at most 10 on Utility. It may still be worth tracking for
Distribution, but it is not a fork target.

### Trend — 20

Measured on **growth rate**, not absolute stars. A 60k-star repo that grew in 8 months
outranks a 90k-star repo that took 3 years.

| Range | Meaning |
|---|---|
| 17–20 | Explosive: stars still compounding, active discussion, < 12 months old |
| 13–16 | Strong and sustained growth |
| 9–12 | Steady; established but no longer accelerating |
| 5–8 | Flat |
| 0–4 | Declining or effectively dormant |

Useful proxy: `stars / months_since_creation`. Above 5,000/month → 17+. Below 200/month → ≤ 8.

### ATK Fit — 20

The discriminating dimension. Two things score high, for different reasons:

- **Token-heavy skills** that make many model calls and already have (or can cheaply gain)
  a provider seam. Routing is a real feature for them, not a sticker.
- **Gateways and routers** where ATK can be added as one more first-class provider.

| Range | Meaning |
|---|---|
| 17–20 | Model calls are the core loop; provider is already configurable or trivially made so |
| 13–16 | Calls models, but the provider seam needs real refactoring |
| 9–12 | Adjacent — prompts/protocols/tooling with no direct call site |
| 4–8 | No natural insertion point |
| 0–3 | Strategically conflicting (e.g. its selling point is free provider aggregation that displaces paid routing) |

> A project can be excellent and still score low here. That is the point of the dimension.

### Distribution — 15

| Range | Meaning |
|---|---|
| 13–15 | Visual or dramatic output; before/after demos write themselves |
| 10–12 | Clear developer story; needs a written walkthrough |
| 6–9 | Needs real effort to make interesting |
| 0–5 | Infrastructure with no visible surface |

### Maintenance — 10 (inverted cost)

| Range | Meaning |
|---|---|
| 9–10 | Small surface, few dependencies, low open-issue pressure |
| 7–8 | Moderate size, healthy issue hygiene |
| 5–6 | Large codebase or heavy dependency tree |
| 3–4 | High issue backlog, fast-moving upstream, frequent breaking changes |
| 0–2 | Scraper-dependent, enormous, or an unmanageable backlog |

Practical proxy: `open_issues / forks`. Also penalise projects whose correctness depends on
third-party HTML/undocumented endpoints — they break silently and often.

### Commercial — 10

| Range | Meaning |
|---|---|
| 9–10 | Heavy per-run token consumption; recurring use |
| 6–8 | Moderate consumption, or occasional but large runs |
| 3–5 | Light consumption |
| 0–2 | Consumes no tokens, or actively suppresses paid usage |

---

## 3. Decision Thresholds

| Score | Priority | Action |
|---|---|---|
| 80–100 | **A** | Enters the formal Fork Pipeline (after License + Technical + Security review) |
| 65–79 | **B** | Deep review; fork only if a Priority-A slot is unused |
| 50–64 | Watchlist | Re-score monthly; track for content only |
| < 50 | Ignore | No action |

**Only Priority A enters the Fork Pipeline.** A high score is necessary but never
sufficient — the License Gate (`LICENSE_REVIEW.md`) is an independent veto.

---

## 4. Hard Vetoes

A veto overrides the score entirely. Any one of these blocks the Fork Pipeline:

1. **License Gate failure** — no license, unclear license, or terms prohibiting commercial
   use / redistribution / modification.
2. **Unresolved security finding** — an active vulnerability or an unexplained network
   egress path.
3. **Trademark entanglement** — the project's identity is a protected brand that ATK cannot
   redistribute under a modified name.
4. **Strategic conflict** — the project's core value proposition directly undermines paid
   routing. Track it; do not amplify it.
5. **Archived upstream** — an archived repository cannot be kept in sync and is a fork
   graveyard by construction.

---

## 5. Worked Example

`mvanhorn/last30days-skill` (snapshot 2026-09-14: 62,022 stars, 5,410 forks, 129 open
issues, created 2026-01-23, MIT):

| Dimension | Score | Reasoning |
|---|---|---|
| Utility | 23 | "What actually happened in the last 30 days" is a real, recurring need; general web search answers it badly |
| Trend | 18 | ~62k stars in ~8 months ≈ 7.8k/month — still compounding |
| ATK Fit | 19 | Multi-source research loop = many model calls per run; routing + a token budget is a genuine feature |
| Distribution | 14 | Output is a readable report — screenshot-friendly, easy to demo |
| Maintenance | 7 | Depends on multiple third-party surfaces that break without notice; 129 open issues |
| Commercial | 10 | One of the highest token-burn-per-invocation skills in the candidate pool |
| **Total** | **91** | **Priority A** |

Recompute with:

```bash
python3 tools/score.py --registry registry/skill_registry.json
```

The tool re-derives every total from its components and fails loudly on any mismatch, so a
hand-edited total can never silently drift from its reasoning.

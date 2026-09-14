# Top 10 Shortlist (TASK 11)

> Snapshot: 2026-09-14 · Scoring model: `SKILL_SCORING.md` v1.0
> Reproduce: `python3 tools/score.py --eligible-only --top 10`

---

## Selection Rule

The Top 10 is drawn from candidates that **both** score ≥ 80 (Priority A) **and** passed the
License Gate. That ordering matters: the gate is an independent veto, so a license-blocked
candidate cannot occupy a Top 10 slot no matter how high it scores. Blocked high scorers are
listed separately in §3 — they are not discarded, they are queued behind a manual license
read.

---

## 1. The Top 10

| # | Repository | Score | License | Category | Stars | Stars/mo | Why it is here |
|---|---|--:|---|---|--:|--:|---|
| 1 | `mvanhorn/last30days-skill` | **91** | MIT | research | 62,022 | 8,068 | Highest token burn per run in the pool, and routing is a real feature rather than a badge |
| 2 | `blader/humanizer` | **88** | MIT | media | 48,065 | 6,122 | Smallest possible surface with a clean single-call provider seam — the lowest-risk first fork |
| 3 | `virgiliojr94/book-to-skill` | **88** | MIT | developer | 30,626 | 6,824 | Long-document ingestion where cost routing produces directly measurable savings |
| 4 | `tt-a1i/archify` | **86** | MIT | media | 61,985 | 12,336 | Fastest-growing eligible candidate; visual output is the strongest content asset |
| 5 | `Egonex-AI/Understand-Anything` | **84** | MIT | developer | 82,729 | 13,672 | Whole-repo analysis — heavy, repeatable, and a natural tiered-routing showcase |
| 6 | `Paritok-official/paritok-4b-v1` | **84** | Apache-2.0 | routing | 1,454 | 738 | Context compression sits at exactly ATK's layer; compression × routing compounds |
| 7 | `Panniantong/Agent-Reach` | **83** | MIT | automation | 81,070 | 12,528 | High-volume retrieval feeding summarisation workloads |
| 8 | `K-Dense-AI/scientific-agent-skills` | **83** | MIT | enterprise | 44,908 | 3,965 | Enterprise/research consumption: high value, low price sensitivity, 10 open issues |
| 9 | `nexu-io/open-design` | **83** | Apache-2.0 | media | 96,144 | 21,077 | Already BYOK; media generation is token-heavy and highly visual |
| 10 | `tbphp/gpt-load` | **82** | MIT | routing | 6,740 | 434 | The routing anchor — best issue hygiene of any gateway in the sweep |

**Just below the line:** `cathrynlavery/diagram-design` (82), `nextlevelbuilder/ui-ux-pro-max-skill`
(81), `Leonxlnx/taste-skill` (81), `ENTERPILOT/GoModel` (81), `alibaba/open-code-review` (81),
`zarazhangrui/frontend-slides` (80), `OthmanAdi/planning-with-files` (80).

`gpt-load` and `diagram-design` tie at 82; `gpt-load` takes the slot on the ATK Fit
tiebreaker (18 vs 14), per the discriminating-dimension rule in `SKILL_SCORING.md` §2.

---

## 2. Score Composition

| # | Repository | Util /25 | Trend /20 | Fit /20 | Dist /15 | Maint /10 | Comm /10 | Total |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| 1 | last30days-skill | 23 | 18 | 19 | 14 | 7 | 10 | **91** |
| 2 | humanizer | 21 | 17 | 18 | 14 | 10 | 8 | **88** |
| 3 | book-to-skill | 21 | 17 | 19 | 13 | 8 | 10 | **88** |
| 4 | archify | 22 | 18 | 16 | 15 | 7 | 8 | **86** |
| 5 | Understand-Anything | 21 | 18 | 16 | 14 | 6 | 9 | **84** |
| 6 | paritok-4b-v1 | 20 | 14 | 19 | 13 | 8 | 10 | **84** |
| 7 | Agent-Reach | 22 | 18 | 15 | 14 | 6 | 8 | **83** |
| 8 | scientific-agent-skills | 22 | 15 | 17 | 12 | 8 | 9 | **83** |
| 9 | open-design | 21 | 18 | 15 | 15 | 5 | 9 | **83** |
| 10 | gpt-load | 21 | 15 | 18 | 11 | 8 | 9 | **82** |

### What the composition shows

- **Maintenance is the binding constraint.** Only `humanizer` scores 10. Five of the ten sit
  at 7 or below, and `open-design` at 5 (1,008 open issues) would consume a disproportionate
  share of a Phase 1 maintenance budget.
- **ATK Fit and Trend rarely peak together.** The two highest-Fit candidates
  (`paritok-4b-v1`, `gpt-load`) are also the two smallest by stars. Infrastructure converts
  well and spreads badly; skills spread well and convert indirectly. A Phase 1 portfolio
  needs both, and should not judge them on the same metric.
- **Commercial score tracks token weight, not popularity.** `humanizer` has 48k stars but
  scores 8 — each run is one call. `book-to-skill` has less than half the stars and scores
  10.

---

## 3. High Scorers Blocked by the License Gate

These would have entered the Top 10 on score alone. They are blocked until a human reads the
LICENSE file — the gate is not a formality and was not waived for scale.

| Repository | Score | Would rank | Stars | Status |
|---|--:|---|--:|---|
| `calesthio/OpenMontage` | 85 | #3 | 59,020 | License unresolved |
| `Graphify-Labs/graphify` | 83 | #6 | 116,685 | License unresolved |
| `mksglu/context-mode` | 82 | #10 | 22,813 | License unresolved |
| `mukul975/Anthropic-Cybersecurity-Skills` | 80 | — | 32,771 | Description claims Apache-2.0; unverified |
| `bestruirui/octopus` | 72 | — | 2,625 | AGPL-3.0 — network copyleft, **ESCALATE** |

`OpenMontage` is the most expensive block: at 85 it would sit third, it is the only serious
media-production candidate, and media generation carries the highest token weight available.
Resolving its license is the single highest-value item in the license backlog.

---

## 4. What Did Not Make It, and Why

| Repository | Score | Reason |
|---|--:|---|
| `BerriAI/litellm` | 75 | Maintenance 2/10 — 5,054 open issues. **Contribute a provider upstream; do not fork.** Being a first-class LiteLLM provider is worth more to ATK than an ATK fork nobody installs. |
| `diegosouzapw/OmniRoute` | 61 | Strategic-conflict veto — free provider aggregation displaces paid routing |
| `decolua/9router` | 55 | Strategic-conflict veto; 2,101 open issues |
| `router-for-me/CLIProxyAPI` | 56 | Strategic-conflict veto plus material ToS exposure for a redistributor |
| `anthropics/skills` | 78 | License unverified; reference material to conform to, not fork |
| `addyosmani/agent-skills` | 78 | Fit 12 — a curated collection with no call site; upstream contribution is the better move |
| `ComposioHQ/awesome-claude-skills` | 55 | Awesome-list — Utility capped at 10. High value as a **discovery input** to `awesome-ai-skills` |

The awesome-lists are worth restating: they score badly as fork targets by design, and are
exactly the right feedstock for the Trend Scout agent. `VoltAgent/awesome-agent-skills` (MIT)
and `VoltAgent/awesome-openclaw-skills` (MIT) should be wired into the Monday discovery run.

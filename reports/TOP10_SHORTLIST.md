# Top 10 Shortlist (TASK 11)

> Snapshot: 2026-09-15 · Scoring model: `SKILL_SCORING.md` v1.0
> Reproduce: `python3 tools/score.py --eligible-only --top 10`
> **Revised** after the second-pass license check — see §5.

---

## Selection Rule

Drawn from candidates that **both** score ≥ 80 (Priority A) **and** passed the License Gate.
Ties are broken by ATK Fit, the discriminating dimension in `SKILL_SCORING.md` §2.

---

## 1. The Top 10

| # | Repository | Score | License | Category | Stars | Why it is here |
|---|---|--:|---|---|--:|---|
| 1 | `mvanhorn/last30days-skill` | **91** | MIT | research | 62,022 | Highest token burn per run; routing is a real feature, not a badge |
| 2 | `virgiliojr94/book-to-skill` | **88** | MIT | developer | 30,626 | Batch workload where cost savings are directly measurable |
| 3 | `blader/humanizer` | **88** | MIT | media | 48,065 | Smallest surface, cleanest provider seam — lowest-risk first fork |
| 4 | `tt-a1i/archify` | **86** | MIT | media | 61,985 | Fastest-growing eligible candidate; visual output is the best content asset |
| 5 | `Paritok-official/paritok-4b-v1` | **84** | Apache-2.0 | routing | 1,454 | Compression × routing compounds; sits at exactly ATK's layer |
| 6 | `Egonex-AI/Understand-Anything` | **84** | MIT | developer | 82,729 | Whole-repo analysis — heavy, repeatable, natural tiered routing |
| 7 | `K-Dense-AI/scientific-agent-skills` | **83** | MIT | enterprise | 44,908 | High-value enterprise consumption; 10 open issues |
| 8 | `Graphify-Labs/graphify` | **83** | Apache-2.0 | developer | 116,810 | **Newly eligible.** Multi-document ingestion, strong cost-tiering fit |
| 9 | `Panniantong/Agent-Reach` | **83** | MIT | automation | 81,070 | High-volume retrieval feeding summarisation |
| 10 | `nexu-io/open-design` | **83** | Apache-2.0 | media | 96,144 | Already BYOK; media generation is token-heavy and visual |

**Just below the line:** `tbphp/gpt-load` (82), `cathrynlavery/diagram-design` (82),
`nextlevelbuilder/ui-ux-pro-max-skill` (81), `Leonxlnx/taste-skill` (81),
`ENTERPILOT/GoModel` (81), `alibaba/open-code-review` (81),
`mukul975/Anthropic-Cybersecurity-Skills` (80, **newly eligible**),
`zarazhangrui/frontend-slides` (80), `OthmanAdi/planning-with-files` (80).

---

## 2. Score Composition

| # | Repository | Util /25 | Trend /20 | Fit /20 | Dist /15 | Maint /10 | Comm /10 | Total |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| 1 | last30days-skill | 23 | 18 | 19 | 14 | 7 | 10 | **91** |
| 2 | book-to-skill | 21 | 17 | 19 | 13 | 8 | 10 | **88** |
| 3 | humanizer | 21 | 17 | 18 | 14 | 10 | 8 | **88** |
| 4 | archify | 22 | 18 | 16 | 15 | 7 | 8 | **86** |
| 5 | paritok-4b-v1 | 20 | 14 | 19 | 13 | 8 | 10 | **84** |
| 6 | Understand-Anything | 21 | 18 | 16 | 14 | 6 | 9 | **84** |
| 7 | scientific-agent-skills | 22 | 15 | 17 | 12 | 8 | 9 | **83** |
| 8 | graphify | 22 | 18 | 16 | 13 | 5 | 9 | **83** |
| 9 | Agent-Reach | 22 | 18 | 15 | 14 | 6 | 8 | **83** |
| 10 | open-design | 21 | 18 | 15 | 15 | 5 | 9 | **83** |

### What the composition shows

- **Maintenance is still the binding constraint.** Only `humanizer` scores 10. Three of the
  ten sit at 6 or below; `graphify` (1,350 open issues) and `open-design` (1,008) would each
  consume a disproportionate share of a Phase 1 maintenance budget.
- **ATK Fit and Trend rarely peak together.** The two highest-Fit candidates
  (`paritok-4b-v1`, `book-to-skill`) are not the biggest. Infrastructure converts well and
  spreads badly; skills spread well and convert indirectly. Judge them on different metrics.
- **Commercial tracks token weight, not popularity.** `humanizer` has 48k stars and scores 8
  — one call per run. `book-to-skill` has less than half the stars and scores 10.

---

## 3. Blocked by the License Gate

Only these remain blocked after the second-pass check, and each for a real reason:

| Repository | Score | Problem |
|---|--:|---|
| `calesthio/OpenMontage` | 85 | **AGPL-3.0.** Would rank #5. Network copyleft: hosting a modified version as a service obliges ATK to publish complete corresponding source |
| `mksglu/context-mode` | 82 | **Elastic License 2.0** — self-install OK, hosted service barred |
| `anthropics/skills` | 78 | **No LICENSE file** — all rights reserved by default |
| `theopenco/llmgateway` | 74 | **AGPL-3.0 + commercial `ee/` tier** — blocked twice over |
| `bestruirui/octopus` | 72 | AGPL-3.0 — network copyleft |
| `ThinkWatchProject/ThinkWatch` | 70 | **BSL 1.1** — free only to 10M tokens/month, then paid. Not open source |
| `ComposioHQ/awesome-claude-skills` | 55 | No LICENSE file |
| `hesreallyhim/awesome-claude-code` | 50 | **CC BY-NC-ND 4.0** — no commercial use, no derivatives |

`modelcontextprotocol/servers` and `registry` were also in this group and **cleared to PASS**
(Apache-2.0 with legacy MIT portions). Neither is a fork target — both are ecosystem
reference infrastructure with high trademark risk.

All six "non-standard license" files were read on 2026-09-15. **Only two resolved to PASS**
(both MCP repositories, Apache-2.0 with legacy MIT portions). The other four turned out to be
deliberately restrictive: Business Source License, Elastic License 2.0, AGPL plus a commercial
tier, and CC BY-NC-ND. The earlier prediction that most would clear was wrong — an unusual
license usually means the author chose one on purpose.

`context-mode` (82) is the one still worth pursuing: Elastic License 2.0 permits forking and
redistribution but bars offering it as a hosted service, so it is unlocked by a delivery-model
decision rather than by a conversation with the author.

---

## 4. What Did Not Make It, and Why

| Repository | Score | Reason |
|---|--:|---|
| `BerriAI/litellm` | 75 | Maintenance 2/10 — 5,054 open issues. **Contribute a provider upstream; do not fork** |
| `diegosouzapw/OmniRoute` | 61 | Strategic-conflict veto — free aggregation displaces paid routing |
| `decolua/9router` | 55 | Strategic-conflict veto; 2,101 open issues |
| `router-for-me/CLIProxyAPI` | 56 | Strategic-conflict veto plus ToS exposure |
| `addyosmani/agent-skills` | 78 | Fit 12 — a curated collection with no call site |
| `github/github-mcp-server`, `ChromeDevTools/chrome-devtools-mcp` | 64, 71 | Cleanly MIT/Apache, but vendor-official servers — conform, do not fork. Trademark risk high |

---

## 5. Revision Note — What Changed on 2026-09-15

The first pass reported 22 candidates as "license unverified". **That was a gap in query
coverage, not a finding about those projects** — the topic-scoped searches never covered
them. A targeted re-check resolved all 22:

| Outcome | Count | Effect |
|---|--:|---|
| MIT | 8 | Now eligible |
| Apache-2.0 | 5 | Now eligible |
| AGPL-3.0 | 1 | `OpenMontage` — confirmed blocked, and now for a known reason |
| Non-standard license | 6 | Still blocked, but cheap to resolve |
| No license at all | 2 | Genuinely blocked |

**Ranking changes:** `graphify` enters at #8 and `Anthropic-Cybersecurity-Skills` becomes
Priority A. `tbphp/gpt-load` moves from #10 to #11 — not because anything about it changed,
but because two better-scoring candidates were unblocked. It remains a recommended fork on
role grounds; see `reports/FORK_RECOMMENDATIONS.md` §1.

The lesson for the operating loop: **"unverified" and "blocked" must stay separate states.**
Collapsing them cost 14 viable candidates for a day, and would have cost more if the sweep
had not been re-run.

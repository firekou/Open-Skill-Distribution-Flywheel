# First Fork Recommendations (TASK 13)

> Snapshot: 2026-09-15 · Input: `reports/TOP10_DEEP_REVIEW.md`
> **Status: recommendation only. No fork has been executed, and none should be until §5 clears.**
> **Revised** after the second-pass license check — the four recommendations are unchanged; see §7.

---

## Recommendation

Fork **four** repositories in Phase 1, in this order:

| Order | Repository | Score | License | Role in the portfolio |
|---|---|--:|---|---|
| 1 | `blader/humanizer` | 88 | MIT | **Reference implementation** — build and prove the ATK adapter on the smallest surface |
| 2 | `tbphp/gpt-load` | 82 | MIT | **Routing anchor** — the credibility proof that ATK is replaceable |
| 3 | `virgiliojr94/book-to-skill` | 88 | MIT | **Cost proof** — the first honest, measurable savings numbers |
| 4 | `tt-a1i/archify` | 86 | MIT | **Distribution engine** — the visual content asset |

`mvanhorn/last30days-skill` (91, the highest score) is deliberately held to position 5 — see
§3.

The brief allows 3–5. **Four is the recommendation, not a compromise:** each one has a
distinct job, and the fifth candidate would add maintenance load without adding a role the
first four do not already cover.

---

## 1. Why These Four

The portfolio is built around four different jobs, not four instances of the same bet:

```
humanizer     → prove the adapter works            (lowest implementation risk)
gpt-load      → prove ATK is replaceable           (credibility)
book-to-skill → prove routing saves money          (the commercial argument)
archify       → prove it is worth talking about    (distribution)
```

Four forks of four token-heavy skills would produce four copies of the same lesson and four
times the scraper maintenance. This spread means that if three fail, the fourth still teaches
ATK something it did not already know.

### 1 — `blader/humanizer` · Reference implementation

**Why first.** 205 KB, 13 open issues, one model call per invocation. It is the cheapest
possible place to build the `ATK_ROUTING_INTEGRATION.md` reference adapter, get the
provider-switch and ATK-removal QA tests actually running, and find out what the fork SOP
gets wrong — before applying any of it to a project where mistakes are expensive.

**Value Add plan.** ATK Router adapter (additive file) · multi-provider support · Docker ·
`.env.example` · one-command install · **a published cross-provider quality benchmark** ·
`CHANGES-ATK.md`.

That benchmark is what keeps this fork from reading as a rebrand. On a codebase this small, a
provider adapter alone is not enough of a contribution to justify redistribution — the honest
add is answering the question the upstream project does not: *which model actually humanises
text best, and what does each cost?*

**Risk:** Low. **Effort:** ~1 week.

### 2 — `tbphp/gpt-load` · Routing anchor

**Why second.** Every other fork claims ATK Routing is replaceable. This one *demonstrates*
it: a multi-channel gateway where ATK appears as one upstream channel beside OpenAI and
Anthropic, and where deleting the ATK channel leaves a working product. That is a far
stronger trust signal than any README paragraph.

It is also the best-maintained gateway in the sweep (20 open issues against 726 forks), and
its bilingual documentation serves ATK's Chinese-language channels directly.

**Value Add plan.** ATK as a first-class channel · ATK-aware cost tracking · fallback
presets · `docker compose` quickstart · bilingual routing documentation · `CHANGES-ATK.md`
and NOTICE.

**Risk:** Medium — Go maintenance capacity required, and it handles credentials, so this fork
carries the strictest security review of the four. **Effort:** ~2 weeks.

### 3 — `virgiliojr94/book-to-skill` · Cost proof

**Why third.** `ANALYTICS_METRICS.md` and `CONTENT_DISTRIBUTION.md` both demand real
before/after numbers, and most skills cannot supply them — their workloads are too variable.
This one is batched and repeatable, so token and cost deltas are directly measurable and
publishable without estimation.

**Value Add plan.** **Tiered routing** (cheap model for extraction, strong model for
synthesis) · token budget per run · cost reporting · Docker · `.env.example` ·
`CHANGES-ATK.md`.

Tiered — not uniformly cheap. A fork that is cheaper and worse is worse than no fork.

**Risk:** Medium. Ship demo content that is public-domain or ATK-owned only; the tool ingests
books and ATK must not distribute copyrighted material it has no rights to. **Effort:** ~2
weeks.

### 4 — `tt-a1i/archify` · Distribution engine

**Why fourth.** Fastest-growing eligible candidate (~12.3k ★/month) and the only one scoring
15/15 on Distribution. Diagram output is screenshot-ready, and "the same architecture rendered
by four different models" is a genuinely informative comparison rather than a contrived
benchmark — it is Beat 4 of the narrative with no invention required.

**Value Add plan.** Multi-provider diagram generation · side-by-side model comparison mode ·
Docker · examples gallery · `CHANGES-ATK.md`.

**Risk:** Medium — 168 open issues and fast upstream movement mean weekly sync from day one.
Diagram quality is strongly model-dependent, so route for *choice*, not for cost reduction.
**Effort:** ~2 weeks.

---

## 2. Coverage Check

| Dimension | humanizer | gpt-load | book-to-skill | archify |
|---|---|---|---|---|
| Category | media | routing | developer | media |
| Language | Python | Go | Python | JavaScript |
| Token weight | Low | N/A | **High** | Medium |
| Distribution | Medium | Low | Medium | **High** |
| Maintenance cost | **Lowest** | Low | Low | Medium |
| Audience | Writers | Infrastructure | Developers | Architects |

Four categories, three languages, four audiences, and a deliberate spread from
lowest-maintenance to highest-distribution.

---

## 3. Why the Top Scorer Is Held Back

`mvanhorn/last30days-skill` scores **91 — the highest in the sweep** — and is still not in
the first four. The reasoning, stated plainly because it contradicts the ranking:

1. **Its correctness depends on third-party surfaces that break silently.** A scraper
   returning empty results looks like "nothing happened recently", not like an error. ATK's
   *first* published fork should not be one whose failure mode is invisible.
2. **ToS exposure.** It reads Reddit, X, YouTube and Polymarket. The same concern that blocks
   `Agent-Reach` applies here in a milder form and deserves a legal read first.
3. **Sequencing, not rejection.** It should be fork #5, immediately after `humanizer` proves
   the adapter pattern and the ToS review clears. Its ATK fit (19/20) and token weight
   (10/10) make it the single most commercially valuable skill in the pool — which is an
   argument for doing it *correctly*, not first.

This is the one place where the recommendation deliberately departs from score order. Score
ranks value; sequencing ranks risk.

---

## 4. Explicitly Not Recommended for Phase 1

| Repository | Score | Why not now |
|---|--:|---|
| `Panniantong/Agent-Reach` | 83 | **Blocked** — platform ToS review required before ATK redistributes under its own brand |
| `nexu-io/open-design` | 83 | 1,008 open issues; desktop app plus media pipelines is the wrong shape for a small Phase 1 maintenance budget |
| `Egonex-AI/Understand-Anything` | 84 | 302 open issues, fast drift; reads entire codebases, so it needs the security review done first |
| `K-Dense-AI/scientific-agent-skills` | 83 | Needs a domain reviewer ATK does not obviously have. Upstream (10 open issues) is attentive — **contribute first** |
| `Paritok-official/paritok-4b-v1` | 84 | Strong architecture, but vendor benchmark claims must be independently reproduced before ATK repeats any number |
| `BerriAI/litellm` | 75 | **Do not fork.** Ship an upstream provider PR instead — being a first-class LiteLLM provider reaches more developers than an ATK fork nobody installs |
| `calesthio/OpenMontage` | 85 | Would rank #5. **AGPL-3.0 confirmed** — network copyleft, blocked for Phase 1 |
| `Graphify-Labs/graphify` | 83 | Newly eligible (Apache-2.0), but 1,350 open issues — same maintenance objection as `open-design` |

---

## 5. Gate Before Any Fork Executes

Per `FORK_POLICY.md` §2, all seven entry conditions must hold. Current state:

| # | Condition | humanizer | gpt-load | book-to-skill | archify |
|---|---|---|---|---|---|
| 1 | `skill_score` ≥ 80 | ✅ 88 | ✅ 82 | ✅ 88 | ✅ 86 |
| 2 | License Gate PASS | ✅ MIT | ✅ MIT | ✅ MIT | ✅ MIT |
| 3 | Technical Review | ✅ | ✅ | ✅ | ✅ |
| 4 | **Security Review** | ❌ | ❌ | ❌ | ❌ |
| 5 | Upstream not archived | ✅ | ✅ | ✅ | ✅ |
| 6 | Written Value Add plan | ✅ §1 | ✅ §1 | ✅ §1 | ✅ §1 |
| 7 | Named maintainer | ❌ | ❌ | ❌ | ❌ |

**Two conditions are unmet across all four.** Security review could not be performed in this
session (repository read access was scoped to ATK's own repository), and maintainer
assignment is an ATK staffing decision.

> **Therefore: no fork is approved yet.** Conditions 4 and 7 must clear first. Per the brief's
> own instruction — *"未完成 License Review、Technical Review、Security Review 前，不得自動大量
> Fork"* — this phase stops here.

---

## 6. Next Actions

**Before any fork**
1. Security review of all four (dependency audit, network egress, credential handling —
   `gpt-load` first, since it stores API keys)
2. Assign a named maintainer per fork
3. Legal read on data-source ToS for `last30days-skill` and `Agent-Reach`

**License backlog** (unblocks 22 candidates, including three that would rank in the Top 10)
4. Manual LICENSE read for `calesthio/OpenMontage` (85), `Graphify-Labs/graphify` (83),
   `mksglu/context-mode` (82), `anthropics/skills`

**Infrastructure, in parallel**
5. Start the daily GitHub Traffic API snapshot **now** — the API retains only 14 days, so
   any delay permanently loses the pre-launch baseline (`ANALYTICS_METRICS.md` §9)
6. Record baseline social impressions before the first fork ships
7. Build the ATK provider adapter against the `ATK_ROUTING_INTEGRATION.md` contract, on
   `humanizer`

**Upstream-first, this week** (`FORK_POLICY.md` §3)
8. Open a provider PR to `BerriAI/litellm`
9. Open courtesy PRs to `humanizer` and `gpt-load` for any generic improvements before
   shipping them fork-only


---

## 7. Revision Note — 2026-09-15

The second-pass license check resolved all 22 previously-unverified candidates. **The four
recommendations are unchanged.** What moved around them:

**Newly eligible.** `Graphify-Labs/graphify` (Apache-2.0) enters the Top 10 at #8, and
`mukul975/Anthropic-Cybersecurity-Skills` (Apache-2.0) becomes Priority A. Neither displaces
the recommended four: `graphify` carries 1,350 open issues, and the cybersecurity collection
needs a domain reviewer for the same reason the scientific skills do.

**Confirmed blocked, now for a known reason.** `calesthio/OpenMontage` is AGPL-3.0, not
merely unverified. At 85 it would rank #5, and it is the only serious media-production
candidate — but network copyleft means hosting a modified version as a service would oblige
ATK to publish complete corresponding source. It stays out of Phase 1.

**`tbphp/gpt-load` moved from #10 to #11.** Nothing about it changed; two better-scoring
candidates were unblocked above it. It stays in the recommended four because the selection
was never rank-ordered — it is the **routing anchor**, and that role is not filled by
anything else on the list. A ranking one place lower does not change what it is for.

**On the "attribute and take down" approach.** The proposal to publish license-unclear
projects with clear attribution, and remove them only if challenged, is addressed in
`LICENSE_REVIEW.md` §9. Short version: attribution is mandatory and ATK should do it
everywhere, but it does not supply the permission a fork requires, and notice-and-takedown
protects platforms hosting other people's uploads — not a company republishing the work
itself. `LICENSE_REVIEW.md` §10 sets out four routes that get most of the same value
legitimately, the cheapest being simply to open an issue asking the author to add a license.

**Priority shift in the backlog.** Asking the 8 ESCALATE/FAIL maintainers to add a license is
now the highest return-on-effort item in the whole plan — higher than any of the four forks.
Six of those are "non-standard license", which usually means a known license with a modified
header. Two minutes of reading each would likely clear most of them.

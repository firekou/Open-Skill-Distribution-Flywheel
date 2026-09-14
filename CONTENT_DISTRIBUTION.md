# CONTENT_DISTRIBUTION.md

> ATK Social Distribution Engine · Version 1.0 · Last updated: 2026-09-14

---

## 1. Principle

> **1 Repository ≠ 1 Post.**
> **1 Repository → 5–20 Content Assets.**

Every repository ATK maintains is a content source, not a content event. A single fork
should produce a month of material, because the interesting part is never the announcement
— it is the work.

And the pitch is never *"AI Token King is great."* It is *"this Skill is great."* The
developer arrives at GitHub, uses the skill, and encounters ATK Routing as infrastructure
rather than as an ad.

---

## 2. The Five-Beat Narrative

Every repository yields at least these five beats, in order:

| # | Beat | Angle | Proof required |
|---|---|---|---|
| 1 | **Discovery** | "I found a really useful X." | Link + one-line demo |
| 2 | **Reality check** | "We actually ran it. The biggest problem was Y." | A real failure, honestly described |
| 3 | **The fix** | "So we forked it and added Y." | The diff / the release |
| 4 | **Compatibility** | "Now it switches between GPT / Claude / Gemini." | A working switch |
| 5 | **Cost** | "If your Agent token cost is too high, route it like this." | Real before/after numbers |

Beat 2 is the one that earns the rest. A post that only says "this is amazing" reads as
marketing; a post that says "this is great *and here is where it broke*" reads as someone
who actually used it — and it is what makes Beat 3 credible rather than opportunistic.

**Rule: never publish Beat 5 without real measurements.** Invented savings figures are the
fastest way to lose a developer audience permanently.

---

## 3. Asset Matrix — 1 Repository → 20 Assets

| # | Asset | Channel | Effort |
|---|---|---|---|
| 1 | Discovery post | Threads / X | S |
| 2 | Discovery post (localised) | LinkedIn | S |
| 3 | "We ran it, here's what broke" | Threads / X | M |
| 4 | Fork announcement | X / LinkedIn | S |
| 5 | Before/after comparison image | All | M |
| 6 | Provider-switch demo (GIF/clip) | X / Threads | M |
| 7 | Cost comparison table | LinkedIn / blog | M |
| 8 | Quick Start thread (numbered) | X | M |
| 9 | README (the canonical asset) | GitHub | L |
| 10 | Technical deep-dive article | Blog / Medium | L |
| 11 | Tutorial ("build X in 10 minutes") | Blog / YouTube | L |
| 12 | YouTube walkthrough | YouTube | L |
| 13 | YouTube Short / Reel | YouTube / Threads | M |
| 14 | Comparison vs alternatives | Blog | L |
| 15 | FAQ | GitHub docs | M |
| 16 | Troubleshooting guide | GitHub docs | M |
| 17 | "5 things you didn't know it could do" | Threads / X | S |
| 18 | Use-case spotlight | LinkedIn | M |
| 19 | Upstream-update note | X | S |
| 20 | Monthly roundup mention | Newsletter / blog | S |

A realistic Phase 1 target is **10 assets per skill**, not 20 — 10 skills × 10 assets = 100
content assets, which is the Phase 1 goal in `ATK_OPEN_SKILL_STRATEGY.md` §7.

---

## 4. Funnel Positioning

Social content should never link directly to an ATK product page.

```
Social post  →  GitHub repository  →  README  →  Quick Start  →  running skill
                                                                      ↓
                                                            ATK Routing encountered
                                                                      ↓
                                                            ATK API / MCP / Token
```

The README carries the conversion, and it does so quietly:

- `Powered by ATK Routing`
- `Quick Start with AI Token King`
- `Use your own provider, or ATK Router.`

That third line matters most. Stating the alternative in the same breath as the default is
what makes the default feel like a convenience instead of a trap — and it converts better
than a hard pitch for exactly that reason.

---

## 5. Channel Notes

| Channel | Format | Cadence | Primary job |
|---|---|---|---|
| **Threads** | Short, conversational, screenshot-led | 3–5/week | Discovery volume |
| **X** | Technical threads, GIFs, code | 5–7/week | Developer reach |
| **LinkedIn** | Outcome and cost framing | 2–3/week | Enterprise/decision-maker reach |
| **YouTube** | Long walkthroughs + Shorts | 1 long + 2 short/week | Depth, search longevity |
| **Blog** | Deep dives, comparisons, tutorials | 2/week | SEO / GEO surface |
| **GitHub** | README, docs, releases | Continuous | The conversion surface |

---

## 6. SEO / GEO Layer

Each skill produces artifacts across every surface an AI search engine and a human search
engine both index:

```
Google · AI Search · GitHub Search · Threads · X · LinkedIn · YouTube
                              ↓
                          GitHub
                              ↓
                           Skill
                              ↓
                       ATK Routing
```

GitHub becomes ATK's **acquisition layer**.

Practical requirements per repository:

- **Topics**: 8–15, matching how developers actually search (`agent-skills`, `mcp-server`,
  `llm-gateway`, `claude-code`, …)
- **Description**: the problem in the first 10 words, not the product name
- **README H1**: the problem statement, not "atk-foo"
- **Answer-shaped headings** (`## How do I switch providers?`) — this is what AI search
  extracts
- **Cross-links** between ATK repos to form a topic cluster
- One canonical long-form article per skill that everything else points to

---

## 7. Content Brief Template

Handed from the Fork Agent to the Content Agent at publish time:

```markdown
# Content Brief: atk-<name>

**Upstream:** <owner/repo> (<license>)
**Released:** <date>
**One-line pitch:** <what it does, no ATK mention>

## The real problem it solves
<2–3 sentences, from actually running it>

## What broke when we ran it
<Beat 2 material — specific and honest>

## What ATK added
- <value add 1>
- <value add 2>

## Measured numbers
| Metric | Before | After |
|---|---|---|
| Tokens / run | | |
| Cost / run | | |
| Latency | | |
<Leave blank rather than estimating. Blank is publishable; invented is not.>

## Demo assets
- [ ] Screenshot
- [ ] GIF of provider switching
- [ ] Terminal recording

## Angles
1. Discovery
2. Reality check
3. The fix
4. Compatibility
5. Cost

## Links
- Repo / Quick Start / Docs
```

---

## 8. Rules

1. **Never fake numbers.** Blank beats invented.
2. **Always credit upstream** in the first post about any fork, by name and link.
3. **Never imply endorsement** by upstream authors.
4. **Lead with the problem**, not with ATK.
5. **One repository, many angles** — do not burn a skill on a single post.
6. **Publish failures too.** "We tried this and dropped it" is high-trust content and costs
   nothing but ego.
7. **No engagement bait.** The audience is developers; they discount it and they remember.
8. **Localise, don't machine-translate.** ATK's Chinese-language and English-language
   audiences respond to different framings of the same work.

# TOP30_R3 — Verified Top 30 (S3)

**Run:** R3 · **Date:** 2026-09-15 · **Snapshot frozen:** `registry/materials.json`, 188 materials
**Gate:** S3 exit. Full Token Efficiency Lab 001 has **not** started. Awaiting Editor-in-Chief / ChatGPT review.

---

## 0. Evidence states used

| State | Meaning in this report |
|---|---|
| **REPORTED** | A secondary source says it. ATK has not confirmed it. |
| **OBSERVED** | ATK read the primary source (README, issue tracker, official post) directly. |
| **TESTED** | ATK executed it. **Nothing in this report is TESTED.** |
| **VERIFIED** / **REPRODUCED** | Not reachable in S3 by definition. |

Evidence gathered this run: GitHub repository search API (metrics), GitHub issue search
(primary user reports), and direct README reads over `raw.githubusercontent.com`. **No
third-party code was executed.**

---

## 1. Correction — two of ATK's own headline numbers were wrong

**This is the most important finding of S3, and it is about ATK's own prior output.**

Earlier ATK reports quoted `rtk` as claiming **"60–90% token reduction"** and `headroom` as
claiming **"60–95% fewer tokens"**. Both came from secondary-source paraphrases. Both READMEs
were read directly this run. **Neither project claims what ATK said it claimed.**

### `rtk-ai/rtk` — what the README actually says **[OBSERVED]**

> "RTK cuts **up to 90% of the bash output** your agent reads. That is what RTK measures, and
> it is **not the same as cutting your bill by 90%**." — README line 62
>
> "Bash output is one contributor to input tokens, alongside your prompt, the system prompt
> and conversation history… The reduction dilutes at every step." — line 64
>
> "The token counts RTK reports are estimated as `bytes / 4` — RTK ships **no tokenizer**, so
> the **percentages are reliable but the absolute token numbers are approximate**." — line 66

The project pre-emptively disclaims the exact misreading ATK made. The per-command figures
(−90% pytest, −99% PHP tests, −60% RSpec) are labelled *"reductions in bash output, not
reductions in your bill"* at line 169.

### `headroomlabs-ai/headroom` — what the README actually says **[OBSERVED]**

Its own headline scenario table:

| Scenario | Baseline | Headroom | Delta |
|---|--:|--:|--:|
| Code search (100 results) | 17,199 | 13,597 | **21%** |
| SRE incident debugging | 55,957 | 24,340 | **57%** |
| Codebase exploration | 58,801 | 33,895 | **42%** |
| GitHub issue triage | 46,067 | 32,429 | **30%** |

> "Savings scale with how repetitive the payload is. Repeated JSON arrays and log lines clear
> 90%…; **prose and already-dense output compress very little**." — line 149

So the real range in its own benchmarks is **21–57%**, with 90% reserved for highly repetitive
payloads. ATK's "60–95%" was not in the source.

**Root cause:** ATK repeated a search-engine summary instead of reading a file that was one
HTTP request away. The evidence ladder exists to prevent exactly this, and it was not applied.
Both figures are corrected in the registry and in `RESEARCH_REPORT.md`.

---

## 2. Deep demand review — why the token/cost projects grew

S3 asked what is behind the attention. The answer is not the one ATK assumed.

### 2.1 The two market leaders differ enormously in measurement rigour **[OBSERVED]**

| | `rtk` | `headroom` |
|---|---|---|
| Stars | 80,473 | 72,266 |
| Token counting | `bytes / 4` estimate, **no tokenizer** | **Provider tokenizer** |
| Quality floor published | Not found | **SQuAD v2 97% @ 19% compression; BFCL 97% @ 32%** |
| Reproducible benchmark | Not found | **Seeded + offline**: `uv run python benchmarks/index_proof_table.py --seed 20260902` |
| Estimated vs measured | Percentages reliable, absolutes approximate | Output savings labelled `[estimated]` with a 95% CI, plus a documented holdout method to get a `measured` number |

Star counts are within 11% of each other. **Measurement rigour is not remotely comparable.**
That difference is invisible from the outside, and it is exactly the kind of thing a
technical magazine exists to surface.

### 2.2 rtk's users are filing issues demanding accurate measurement **[OBSERVED]**

GitHub issue search against `rtk-ai/rtk` returned **14 matching issues**. A sample, verbatim:

| # | Title | State | Signal |
|---|---|---|---|
| [2805](https://github.com/rtk-ai/rtk/issues/2805) | "Savings accounting credits rtk with the agent's own head/tail filtering — repro: 2.1M tokens claimed '100% saved' vs ~195 real (**>10,000×**)" | open | 5 comments, 1 👍 |
| [3508](https://github.com/rtk-ai/rtk/issues/3508) | "`gain`: savings are counted without a context ceiling — reported figure **~184x the real one** on my install" | open | 2 comments |
| [1973](https://github.com/rtk-ai/rtk/issues/1973) | "Misleading analytics: gain over-counts 'tokens saved'…" | open | **3 👍** |
| [590](https://github.com/rtk-ai/rtk/issues/590) | "**Deceptive and inaccurate reporting?**" | open | **5 👍** |
| [2241](https://github.com/rtk-ai/rtk/issues/2241) | "Misleading `saved_tokens` when RTK wraps only the command before a shell pipeline" | open | 2 comments |
| [1935](https://github.com/rtk-ai/rtk/issues/1935) | "rtk gain hallucinates massive token usage and savings" | closed | 5 comments |

Note this is **consistent with the README**, not a contradiction of it: the README says
absolute numbers are approximate, and users are reporting exactly how approximate.

**This is the demand evidence ATK previously said it did not have.** `RESEARCH_REPORT.md` §6.2
recorded that the Measurement & Trust hypothesis had *no demand-side support* — the thesis was
built from vendor gaps and academic framing only. It now has some: users of the most-starred
token tool in the market are independently filing bug reports demanding that savings
measurement be trustworthy, and upvoting each other's.

**It is still weak evidence.** Fourteen issues against 80,473 stars is a small fraction, these
are the users motivated enough to complain, and "wants accurate numbers in a free tool" is not
the same as "will pay for verifiable routing". It moves the hypothesis from *unsupported* to
*weakly supported*. Not further.

### 2.3 What actually drove the growth **[INFERENCE, low confidence]**

Neither project grew on measurement quality — the one with weaker measurement has more stars.
The observable common factors are: a single-binary or single-command install, a concrete
before/after number on the README, and a pain (`agentic loops burn context`) that anyone using
a coding agent feels within a week. ATK has no data separating these, and should not pretend
otherwise.

---

## 3. Scout component evaluation — no code executed

S3 required evaluating `last30days-skill` and `Agent-Reach` as Scout components **without
running unreviewed code**. Both were assessed from README and issue tracker only.

### 3.1 `mvanhorn/last30days-skill` — **conditional, free-source subset only**

**Architecture [OBSERVED]** — many sources are free and keyless: Reddit (keyless RSS +
arctic-shift for real upvote counts), arXiv, Techmeme, Digg. Paid/authenticated sources are
opt-in: ScrapeCreators (**10,000 free calls, then pay-as-you-go**) covers TikTok, Instagram,
Threads, Pinterest, LinkedIn and YouTube comments; X needs a bearer token or browser cookies;
Xiaohongshu needs a locally running logged-in browser service. Keys are stored in the OS
keychain, and the engine **degrades to web-only mode if every key is skipped**.

**Security posture [OBSERVED]** — better than ATK assumed. The README records stored-XSS fixes
in the HTML renderer, locked-down cookie temp files, Semgrep and OSV-Scanner scans, a PR
dependency-review gate, OpenSSF Scorecard, build provenance attestation, and a test-coverage
floor raised from 60% to 84%.

**The blocker [OBSERVED]** — a silent-failure class:

| # | Title | State |
|---|---|---|
| [78](https://github.com/mvanhorn/last30days-skill/issues/78) | "ScrapeCreators API failures are **silent** — skill reports success with no data" | closed |
| [867](https://github.com/mvanhorn/last30days-skill/issues/867) | "Reddit: ScrapeCreators backup is unreachable — **non-empty scraped results mask 100% primary-API failure**" | closed |
| [986](https://github.com/mvanhorn/last30days-skill/issues/986) | "Instagram source always returns HTTP 404 while ScrapeCreators endpoints return 200 (v3.18.4)" | open |

ATK's R1 sweep *hypothesised* this failure mode ("a scraper returning empty results looks like
'no recent activity', not like an error"). It is now **OBSERVED**, filed three times, twice
fixed, once open.

For a Scout this is the decisive property. **A Scout that reports success with no data is
worse than no Scout**, because it silently poisons the registry with false negatives — and the
registry is what editorial priority is built on.

**Verdict:** usable as a Scout component **only** with (a) the free/keyless sources, (b) an
ATK-side source-liveness assertion that fails the run when a source returns zero rows, and
(c) per-source row counts recorded in every Scout output. Not usable as-is.

### 3.2 `Panniantong/Agent-Reach` — **not suitable as ATK infrastructure**

**[OBSERVED]** The README states plainly, in a warning block:

> ⚠️ **封号风险提醒：** 使用 Cookie 登录的平台（Twitter、小红书等），通过脚本/API 调用**存在被平台检测并封号的风险**。请务必使用**专用小号**，不要用你的主账号。
>
> *(Ban-risk warning: platforms accessed via cookie login — Twitter, Xiaohongshu and others —
> carry a risk of detection and account suspension when driven by script or API. Use a
> dedicated throwaway account, never your main account.)*

Credentials are stored locally at `~/.agent-reach/config.yaml` with mode 600 and are not
uploaded — the project's handling is careful. Reddit's anonymous interface is noted as blocked,
so a login session is required there too.

**Verdict:** the author's own ban-risk warning is disqualifying for infrastructure ATK depends
on. A Scout whose sources can vanish when an account is suspended is not a dependable input to
editorial priority, and operating burner accounts at scale is both an ongoing cost and a
platform-ToS question ATK has not answered. **Track it; do not build the Scout on it.** Its
Bilibili and Xiaohongshu coverage remains genuinely differentiating and is worth revisiting if
a keyed, ToS-clean path appears.

---

## 4. Top 30

Overlap between lists is intentional and marked. Verify state is per-claim, not per-project.

### 4.1 Ten Worth Talking About

| # | Material | Angle | Evidence |
|---|---|---|---|
| T1 | **`rtk` vs `headroom` measurement rigour** | Two ~equally-starred tools; one measures with a provider tokenizer and publishes a quality floor, the other estimates `bytes/4`. Invisible from stars. | **OBSERVED** (§2.1) |
| T2 | [Anthropic — *Code execution with MCP*](https://www.anthropic.com/engineering/code-execution-with-mcp) | Agents pay twice for tools: definitions upfront and intermediate results through context. Worked example: ~50k extra tokens from intermediates alone. | **OBSERVED** |
| T3 | **Cloudflare / Vercel are giving routing away** | Free on every Cloudflare plan; Vercel BYOK with no markup. Reframes "cheap routing" as a commodity. | **REPORTED** — needs §6 item 4 |
| T4 | **rtk's savings accounting is contested by its own users** | 14 issues; one repro at >10,000×. Handle with care: the README already says absolutes are approximate. | **OBSERVED** (§2.2) |
| T5 | **`last30days-skill`'s silent-failure class** | "Reports success with no data" is the failure mode every agent-tooling builder should fear. | **OBSERVED** (§3.1) |
| T6 | [*Model Routing as a Trust Problem*](https://arxiv.org/pdf/2605.01710) | Routing framed as trust; verifiable route receipts. | **REPORTED** |
| T7 | `tt-a1i/archify` (61,985★, MIT) | Diagram generation; strongest visual asset in the registry. | **REPORTED** |
| T8 | `calesthio/OpenMontage` (59,020★, **AGPL-3.0**) | Talk only — network copyleft blocks redistribution. | **OBSERVED** (licence read) |
| T9 | **`Agent-Reach`'s own ban-risk warning** | A maintainer telling users to use a throwaway account is an honest-tooling story worth telling. | **OBSERVED** (§3.2) |
| T10 | **The model price gap, corrected** | Verified from primary pricing pages 2026-09-15. **The ~100× figure was half wrong.** Like-for-like it is **11.4×**; ~100× requires cherry-picking tiers. The story is now *how easy it is to manufacture any multiple you want*. | **OBSERVED** — E007, E015 |

### 4.2 Ten Worth Running

Ordered by evidence value per hour. These are Lab 001 candidates; see the precheck.

| # | Target | Hypothesis tested | Why it earns a slot |
|---|---|---|---|
| R1 | Anthropic context-engineering cookbook | H1, H4 | First-party, runnable, no licence question, no third-party binary |
| R2 | `headroom` seeded benchmark (`--seed 20260902`) | H2 | Vendor ships a **reproducible** benchmark — reproduce it before believing or disputing it |
| R3 | `rtk gain` accounting | — | Independently check the >10,000× over-count repro in #2805 |
| R4 | MCP tool-schema overhead at 5/20/50/100 tools | H1 | ATK-controlled, no third-party code, directly measurable |
| R5 | `Paritok-official/paritok-4b-v1` (Apache-2.0) | H2 | Compression gateway; needs its own model hosted — cost noted |
| R6 | `yvgude/lean-ctx` (Apache-2.0) | H2 | Small Rust surface |
| R7 | `NadirRouter/NadirClaw` | H3 | Prompt-complexity routing — the cleanest test of misrouting cost |
| R8 | `toby-bridges/api-relay-audit` | — | **Run against ATK's own routing.** Doubles as self-audit |
| R9 | `crwdla/tokentab` (MIT) | — | Reads session logs; measurement instrument rather than treatment |
| R10 | `juyterman1000/entroly` (Apache-2.0) | H2 | Reversible compression with per-reduction receipts |

### 4.3 Ten Worth Integrating

Integration brief only. **No fork, no adapter, and no execution is authorised by this report.**

| # | Target | Licence | Integration shape | Gate still open |
|---|---|---|---|---|
| I1 | `ENTERPILOT/GoModel` | MIT | ATK as a first-class provider in a Go gateway | Security review |
| I2 | `tbphp/gpt-load` | MIT | ATK as one upstream channel; proves ATK is removable | Security review — **handles API keys** |
| I3 | `RelayPlane/proxy` | MIT | Per-run cost metering and runaway kill | Security review |
| I4 | `liaohch3/claude-tap` | **unresolved** | Agent traffic inspection | **Licence read first** |
| I5 | `crwdla/tokentab` | MIT | Cost attribution by model/project/day | Security review |
| I6 | `headroomlabs-ai/headroom` | Apache-2.0 | Compression in front of routing | Security review; NOTICE + change statement |
| I7 | `rtk-ai/rtk` | Apache-2.0 | Bash-output reduction before the agent reads | Security review; **do not inherit its savings accounting** |
| I8 | `Paritok-official/paritok-4b-v1` | Apache-2.0 | Compression gateway | Security review; model hosting cost |
| I9 | `yvgude/lean-ctx` | Apache-2.0 | Context layer | Security review |
| I10 | `mvanhorn/last30days-skill` | MIT | Scout component, **free sources only** | §3.1 conditions (a)(b)(c) must ship first |

---

## 5. What S3 did not achieve

- **Nothing is TESTED.** No third-party code was executed, by instruction. Every efficiency
  number in this report belongs to someone else.
- **`headroom`'s issue tracker yielded nothing** under two separate semantic queries, despite
  643 open issues. That is a **failed query, not a clean bill of health**, and it is recorded
  as such rather than reported as "no problems found".
- **Demand evidence is thin.** §2.2 is 14 issues. It moves Measurement & Trust from
  unsupported to weakly supported, and no further.
- **Growth causation is unknown** (§2.3). ATK has correlation and plausible mechanism, not
  cause.
- **Four Top 30 entries still rest on REPORTED evidence** (T3, T6, T10, and I4's licence).

---

## 6. Handoff — open items, ordered by value per hour

| # | Item | Resolves | Est. |
|---|---|---|---|
| 1 | ~~Read DeepSeek / OpenAI / Anthropic pricing pages directly~~ | ~~T10~~ | **DONE 2026-09-15 — gap is 11.4× like-for-like, not ~100×** |
| 2 | Read `liaohch3/claude-tap` LICENSE | I4 gate | ~2 min |
| 3 | Re-query `headroom` issues with different terms; report result either way | §5 gap | ~15 min |
| 4 | Read Cloudflare AI Gateway + Vercel AI Gateway docs directly | T3 → OBSERVED | ~1 hr |
| 5 | Security review the four Lab 001 executables (R5–R8) | G2 for Lab 001 | ~half day |

**Handoff packet:** `material_id` = frozen `registry/materials.json` (188 items, 2026-09-15) ·
evidence paths = this report §1–§3 · next owner = **Editor-in-Chief / ChatGPT review** ·
next gate = **G1 methodology freeze** (see `reports/TOKEN_EFFICIENCY_LAB_001_PRECHECK.md`).

**Stop condition reached.** S3 is complete. Lab 001 execution is **not** authorised.

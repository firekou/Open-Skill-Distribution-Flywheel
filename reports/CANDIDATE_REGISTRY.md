# Candidate Registry — First Discovery Sweep (TASK 10)

> Snapshot: **2026-09-14** · Scoring model: `SKILL_SCORING.md v1.0`
> Source: GitHub repository search API. Regenerate with `python3 tools/build_registry.py`.

The brief asked for 50 candidates. This sweep returned **68** across the ATK Skill Network categories, because several searches surfaced strong candidates that would have been arbitrary to drop at a round number.

## Summary

| | Count |
|---|---|
| Candidates discovered | 68 |
| Priority A (score ≥ 80) | 21 |
| Priority B (65–79) | 32 |
| Watchlist (50–64) | 15 |
| License Gate PASS | 45 |
| **Blocked — license unverified** | **22** |
| Rejected — strategic conflict | 3 |

> **The blocked count is the headline finding.** 22 of 68 candidates could not have their license resolved by the automated gate. Per `LICENSE_REVIEW.md` §1 these are treated exactly like repositories with no license: they cannot enter the Fork Pipeline until a human reads the LICENSE file. Several of them score highly, which is precisely why the gate is independent of the score.

## Method

1. Category sweeps over the GitHub repository search API: `topic:agent-skills`, `topic:llm-gateway`, `topic:mcp-server`, `topic:ai-agents`, plus keyword searches for MCP, routing and gateway projects.
2. Star/fork/issue/creation-date metrics captured directly from the API response.
3. Licenses resolved by re-running each sweep with a `license:` qualifier, so a license is only recorded when GitHub's own metadata confirms it. A README badge or a description string was never accepted as evidence.
4. Scored against `SKILL_SCORING.md` v1.0; totals computed by `tools/build_registry.py` and validated by `tools/score.py`.

**Growth signal** is reported as stars/month since creation rather than absolute stars, per `SKILL_SCORING.md` §2.

## Full Registry

Sorted by score. `Gate` is the License Gate ruling — it overrides the score.

### research

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`mvanhorn/last30days-skill`](https://github.com/mvanhorn/last30days-skill) | 62,022 | 5,410 | 129 | 8,068 | MIT | PASS | **91** | A | review |

### media-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`blader/humanizer`](https://github.com/blader/humanizer) | 48,065 | 3,911 | 13 | 6,122 | MIT | PASS | **88** | A | review |
| [`tt-a1i/archify`](https://github.com/tt-a1i/archify) | 61,985 | 4,090 | 168 | 12,413 | MIT | PASS | **86** | A | review |
| [`calesthio/OpenMontage`](https://github.com/calesthio/OpenMontage) | 59,020 | 7,403 | 320 | 10,631 | — | BLOCKED | **85** | A | blocked |
| [`nexu-io/open-design`](https://github.com/nexu-io/open-design) | 96,144 | 11,139 | 1,008 | 21,055 | Apache-2.0 | PASS | **83** | A | review |
| [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) | 39,705 | 2,522 | 44 | 8,004 | MIT | PASS | **82** | A | review |
| [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) | 29,294 | 2,314 | 68 | 3,894 | MIT | PASS | **80** | A | review |

### developer-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) | 30,626 | 3,174 | 23 | 6,855 | MIT | PASS | **88** | A | review |
| [`Egonex-AI/Understand-Anything`](https://github.com/Egonex-AI/Understand-Anything) | 82,729 | 6,961 | 302 | 13,761 | MIT | PASS | **84** | A | review |
| [`Graphify-Labs/graphify`](https://github.com/Graphify-Labs/graphify) | 116,685 | 11,393 | 1,342 | 21,658 | — | BLOCKED | **83** | A | blocked |
| [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 127,581 | 13,619 | 85 | 13,485 | MIT | PASS | **81** | A | review |
| [`Leonxlnx/taste-skill`](https://github.com/Leonxlnx/taste-skill) | 87,095 | 5,936 | 66 | 12,808 | MIT | PASS | **81** | A | review |
| [`alibaba/open-code-review`](https://github.com/alibaba/open-code-review) | 25,280 | 1,845 | 160 | 6,467 | Apache-2.0 | PASS | **81** | A | review |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | 94,287 | 10,028 | 119 | 13,602 | MIT | PASS | **78** | B | watch |
| [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills) | 48,315 | 3,443 | 72 | 5,767 | — | BLOCKED | **75** | B | blocked |
| [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) | 138,230 | 7,418 | 266 | 44,763 | MIT | PASS | **74** | B | watch |

### agent-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`OthmanAdi/planning-with-files`](https://github.com/OthmanAdi/planning-with-files) | 26,885 | 2,237 | 8 | 3,222 | MIT | PASS | **80** | A | review |
| [`anthropics/skills`](https://github.com/anthropics/skills) | 176,286 | 20,867 | 1,232 | 15,031 | — | BLOCKED | **78** | B | blocked |
| [`wshobson/agents`](https://github.com/wshobson/agents) | 39,648 | 4,223 | 5 | 2,894 | MIT | PASS | **74** | B | watch |
| [`titanwings/distilly`](https://github.com/titanwings/distilly) | 24,716 | 2,145 | 37 | 4,478 | MIT | PASS | **74** | B | watch |
| [`JimLiu/baoyu-skills`](https://github.com/JimLiu/baoyu-skills) | 25,895 | 2,867 | 15 | 3,231 | MIT | PASS | **70** | B | watch |
| [`KKKKhazix/khazix-skills`](https://github.com/KKKKhazix/khazix-skills) | 20,661 | 2,200 | 49 | 3,906 | MIT | PASS | **69** | B | watch |
| [`alirezarezvani/claude-skills`](https://github.com/alirezarezvani/claude-skills) | 25,949 | 3,655 | 17 | 2,394 | MIT | PASS | **67** | B | watch |

### enterprise-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills) | 44,908 | 4,073 | 10 | 4,142 | MIT | PASS | **83** | A | review |
| [`mukul975/Anthropic-Cybersecurity-Skills`](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | 32,771 | 3,956 | 46 | 4,963 | — | BLOCKED | **80** | A | blocked |
| [`coreyhaines31/marketingskills`](https://github.com/coreyhaines31/marketingskills) | 50,207 | 7,606 | 112 | 6,315 | — | BLOCKED | **78** | B | blocked |
| [`phuryn/pm-skills`](https://github.com/phuryn/pm-skills) | 26,312 | 2,806 | 41 | 4,066 | MIT | PASS | **69** | B | watch |

### automation-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach) | 81,070 | 7,060 | 134 | 12,217 | MIT | PASS | **83** | A | review |
| [`googleworkspace/cli`](https://github.com/googleworkspace/cli) | 30,992 | 1,832 | 133 | 4,813 | Apache-2.0 | PASS | **71** | B | watch |

### agent-infrastructure

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`mksglu/context-mode`](https://github.com/mksglu/context-mode) | 22,813 | 1,650 | 245 | 3,421 | — | BLOCKED | **82** | A | blocked |
| [`thedotmack/claude-mem`](https://github.com/thedotmack/claude-mem) | 93,860 | 8,259 | 183 | 7,539 | — | BLOCKED | **74** | B | blocked |
| [`topoteretes/cognee`](https://github.com/topoteretes/cognee) | 30,681 | 3,027 | 494 | 830 | Apache-2.0 | PASS | **72** | B | watch |

### routing

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`Paritok-official/paritok-4b-v1`](https://github.com/Paritok-official/paritok-4b-v1) | 1,454 | 138 | 8 | 726 | Apache-2.0 | PASS | **84** | A | review |
| [`tbphp/gpt-load`](https://github.com/tbphp/gpt-load) | 6,740 | 726 | 20 | 441 | MIT | PASS | **82** | A | review |
| [`ENTERPILOT/GoModel`](https://github.com/ENTERPILOT/GoModel) | 1,155 | 100 | 72 | 124 | MIT | PASS | **81** | A | review |
| [`maximhq/bifrost`](https://github.com/maximhq/bifrost) | 8,069 | 1,214 | 995 | 452 | Apache-2.0 | PASS | **79** | B | watch |
| [`Portkey-AI/gateway`](https://github.com/Portkey-AI/gateway) | 12,987 | 1,300 | 265 | 354 | MIT | PASS | **78** | B | watch |
| [`katanemo/plano`](https://github.com/katanemo/plano) | 7,049 | 484 | 140 | 269 | Apache-2.0 | PASS | **75** | B | watch |
| [`BerriAI/litellm`](https://github.com/BerriAI/litellm) | 58,721 | 11,430 | 5,054 | 1,561 | MIT | PASS | **75** | B | watch |
| [`theopenco/llmgateway`](https://github.com/theopenco/llmgateway) | 1,633 | 183 | 68 | 96 | — | BLOCKED | **74** | B | blocked |
| [`bestruirui/octopus`](https://github.com/bestruirui/octopus) | 2,625 | 427 | 19 | 266 | AGPL-3.0 | ESCALATE | **72** | B | blocked |
| [`ThinkWatchProject/ThinkWatch`](https://github.com/ThinkWatchProject/ThinkWatch) | 813 | 21 | 0 | 150 | — | BLOCKED | **70** | B | blocked |
| [`Fast-Editor/Lynkr`](https://github.com/Fast-Editor/Lynkr) | 550 | 61 | 5 | 59 | Apache-2.0 | PASS | **68** | B | watch |
| [`coaidev/coai`](https://github.com/coaidev/coai) | 9,311 | 1,226 | 39 | 245 | Apache-2.0 | PASS | **67** | B | watch |
| [`Kong/kong`](https://github.com/Kong/kong) | 44,137 | 5,210 | 200 | 311 | Apache-2.0 | PASS | **64** | Watchlist | watch |
| [`APIParkLab/APIPark`](https://github.com/APIParkLab/APIPark) | 1,815 | 245 | 53 | 72 | Apache-2.0 | PASS | **63** | Watchlist | watch |
| [`diegosouzapw/OmniRoute`](https://github.com/diegosouzapw/OmniRoute) | 66,084 | 9,268 | 766 | 9,444 | MIT | PASS | **61** | Watchlist | reject |
| [`router-for-me/CLIProxyAPI`](https://github.com/router-for-me/CLIProxyAPI) | 51,751 | 7,835 | 639 | 3,580 | MIT | PASS | **56** | Watchlist | reject |
| [`decolua/9router`](https://github.com/decolua/9router) | 28,738 | 5,269 | 2,101 | 3,471 | MIT | PASS | **55** | Watchlist | reject |

### mcp

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) | 43,233 | 3,522 | 582 | 6,515 | MIT | PASS | **76** | B | watch |
| [`oraios/serena`](https://github.com/oraios/serena) | 29,320 | 1,988 | 178 | 1,653 | MIT | PASS | **75** | B | watch |
| [`ChromeDevTools/chrome-devtools-mcp`](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 51,935 | 3,647 | 106 | 4,296 | — | BLOCKED | **71** | B | blocked |
| [`upstash/context7`](https://github.com/upstash/context7) | 62,012 | 2,992 | 61 | 3,515 | — | BLOCKED | **70** | B | blocked |
| [`czlonkowski/n8n-mcp`](https://github.com/czlonkowski/n8n-mcp) | 22,884 | 3,641 | 67 | 1,501 | — | BLOCKED | **68** | B | blocked |
| [`brightdata/brightdata-mcp`](https://github.com/brightdata/brightdata-mcp) | 2,641 | 327 | 40 | 155 | — | BLOCKED | **67** | B | blocked |
| [`mobile-next/mobile-mcp`](https://github.com/mobile-next/mobile-mcp) | 6,689 | 582 | 43 | 381 | — | BLOCKED | **65** | B | blocked |
| [`github/github-mcp-server`](https://github.com/github/github-mcp-server) | 32,926 | 4,965 | 320 | 1,793 | — | BLOCKED | **64** | Watchlist | blocked |
| [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) | 90,324 | 11,632 | 522 | 4,141 | — | BLOCKED | **64** | Watchlist | blocked |
| [`zcaceres/markdownify-mcp`](https://github.com/zcaceres/markdownify-mcp) | 2,990 | 253 | 29 | 143 | — | BLOCKED | **64** | Watchlist | blocked |
| [`getsentry/XcodeBuildMCP`](https://github.com/getsentry/XcodeBuildMCP) | 6,383 | 318 | 24 | 351 | — | BLOCKED | **63** | Watchlist | blocked |
| [`modelcontextprotocol/registry`](https://github.com/modelcontextprotocol/registry) | 7,247 | 989 | 165 | 376 | — | BLOCKED | **56** | Watchlist | blocked |

### discovery

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`sickn33/agentic-awesome-skills`](https://github.com/sickn33/agentic-awesome-skills) | 46,406 | 6,761 | 2 | 5,813 | MIT | PASS | **65** | B | watch |
| [`ComposioHQ/awesome-claude-skills`](https://github.com/ComposioHQ/awesome-claude-skills) | 75,025 | 8,670 | 1,453 | 6,879 | — | BLOCKED | **55** | Watchlist | blocked |
| [`VoltAgent/awesome-openclaw-skills`](https://github.com/VoltAgent/awesome-openclaw-skills) | 52,562 | 5,026 | 0 | 6,896 | MIT | PASS | **54** | Watchlist | watch |
| [`VoltAgent/awesome-agent-skills`](https://github.com/VoltAgent/awesome-agent-skills) | 34,310 | 3,636 | 12 | 3,254 | MIT | PASS | **53** | Watchlist | watch |
| [`github/awesome-copilot`](https://github.com/github/awesome-copilot) | 39,000 | 4,940 | 45 | 2,581 | MIT | PASS | **51** | Watchlist | watch |
| [`hesreallyhim/awesome-claude-code`](https://github.com/hesreallyhim/awesome-claude-code) | 54,026 | 4,708 | 1,046 | 3,206 | — | BLOCKED | **50** | Watchlist | blocked |

### standard

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`agentskills/agentskills`](https://github.com/agentskills/agentskills) | 25,324 | 1,899 | 76 | 2,834 | Apache-2.0 | PASS | **65** | B | watch |

## Rejected — Strategic Conflict

Per `SKILL_SCORING.md` §4.4, a project whose core value proposition displaces paid routing is vetoed regardless of score. These are tracked for competitive intelligence and are **not** fork candidates:

| Repository | Stars | Why |
|---|--:|---|
| `diegosouzapw/OmniRoute` | 66,084 | its core value is free provider aggregation, which directly displaces paid routing. |
| `router-for-me/CLIProxyAPI` | 51,751 | converts subscriptions into API access, displacing metered token spend. ToS exposure on the wrapped services. |
| `decolua/9router` | 28,738 | explicitly positions free access against paid token consumption. |

These three are collectively the fastest-growing routing projects in the sweep. That is the finding, not an aside: the market is currently rewarding free provider aggregation. ATK's differentiation has to be reliability, cost transparency and maintained distribution — not price.

## Blocked — License Unverified

Highest-scoring blocked candidates, in score order. Each needs a manual LICENSE read before it can be reconsidered:

| Repository | Score | Stars | Note |
|---|--:|--:|---|
| `calesthio/OpenMontage` | 85 | 59,020 | License unresolved |
| `Graphify-Labs/graphify` | 83 | 116,685 | License unresolved |
| `mksglu/context-mode` | 82 | 22,813 | License unresolved |
| `mukul975/Anthropic-Cybersecurity-Skills` | 80 | 32,771 | License unresolved: the repository description claims Apache-2 |
| `anthropics/skills` | 78 | 176,286 | BLOCKED: did not resolve to MIT or Apache-2 |
| `coreyhaines31/marketingskills` | 78 | 50,207 | License unresolved |
| `kepano/obsidian-skills` | 75 | 48,315 | License unresolved |
| `thedotmack/claude-mem` | 74 | 93,860 | License unresolved |
| `theopenco/llmgateway` | 74 | 1,633 | License unresolved - resolved as neither MIT, Apache-2 |

`anthropics/skills` (176,286 stars) and `calesthio/OpenMontage` (85/100) are the two most consequential blocks — OpenMontage would otherwise rank second overall.

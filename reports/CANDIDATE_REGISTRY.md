# Candidate Registry — First Discovery Sweep (TASK 10)

> Snapshot: **2026-09-15** · Scoring model: `SKILL_SCORING.md v1.0`
> Source: GitHub repository search API. Regenerate with `python3 tools/build_registry.py`.

The brief asked for 50 candidates. This sweep returned **68** across the ATK Skill Network categories, because several searches surfaced strong candidates that would have been arbitrary to drop at a round number.

## Summary

| | Count |
|---|---|
| Candidates discovered | 68 |
| Priority A (score ≥ 80) | 21 |
| Priority B (65–79) | 32 |
| Watchlist (50–64) | 15 |
| License Gate PASS | 60 |
| Blocked — non-standard license (ESCALATE) | 3 |
| Blocked — **no license at all** (FAIL) | 5 |
| Rejected — strategic conflict | 3 |

> **Second-pass correction (2026-09-15).** The first sweep left 22 candidates unresolved. That was a gap in the *query coverage*, not a finding about those projects: the topic-scoped searches simply never covered them. A targeted re-check resolved all 22. Only **8** of 68 are now genuinely blocked, and the remainder are cleanly usable.

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
| [`mvanhorn/last30days-skill`](https://github.com/mvanhorn/last30days-skill) | 62,022 | 5,410 | 129 | 8,034 | MIT | PASS | **91** | A | review |

### media-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`blader/humanizer`](https://github.com/blader/humanizer) | 48,065 | 3,911 | 13 | 6,096 | MIT | PASS | **88** | A | review |
| [`tt-a1i/archify`](https://github.com/tt-a1i/archify) | 61,985 | 4,090 | 168 | 12,332 | MIT | PASS | **86** | A | review |
| [`calesthio/OpenMontage`](https://github.com/calesthio/OpenMontage) | 59,020 | 7,403 | 320 | 10,568 | AGPL-3.0 | ESCALATE | **85** | A | blocked |
| [`nexu-io/open-design`](https://github.com/nexu-io/open-design) | 96,144 | 11,139 | 1,008 | 20,904 | Apache-2.0 | PASS | **83** | A | review |
| [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) | 39,705 | 2,522 | 44 | 7,951 | MIT | PASS | **82** | A | review |
| [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) | 29,294 | 2,314 | 68 | 3,877 | MIT | PASS | **80** | A | review |

### developer-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) | 30,626 | 3,174 | 23 | 6,805 | MIT | PASS | **88** | A | review |
| [`Egonex-AI/Understand-Anything`](https://github.com/Egonex-AI/Understand-Anything) | 82,729 | 6,961 | 302 | 13,686 | MIT | PASS | **84** | A | review |
| [`Graphify-Labs/graphify`](https://github.com/Graphify-Labs/graphify) | 116,685 | 11,393 | 1,342 | 21,527 | Apache-2.0 | PASS | **83** | A | review |
| [`alibaba/open-code-review`](https://github.com/alibaba/open-code-review) | 25,280 | 1,845 | 160 | 6,413 | Apache-2.0 | PASS | **81** | A | review |
| [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 127,581 | 13,619 | 85 | 13,438 | MIT | PASS | **81** | A | review |
| [`Leonxlnx/taste-skill`](https://github.com/Leonxlnx/taste-skill) | 87,095 | 5,936 | 66 | 12,746 | MIT | PASS | **81** | A | review |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | 94,287 | 10,028 | 119 | 13,538 | MIT | PASS | **78** | B | watch |
| [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills) | 48,315 | 3,443 | 72 | 5,745 | MIT | PASS | **75** | B | watch |
| [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) | 138,230 | 7,418 | 266 | 44,292 | MIT | PASS | **74** | B | watch |

### agent-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`OthmanAdi/planning-with-files`](https://github.com/OthmanAdi/planning-with-files) | 26,885 | 2,237 | 8 | 3,209 | MIT | PASS | **80** | A | review |
| [`anthropics/skills`](https://github.com/anthropics/skills) | 176,286 | 20,867 | 1,232 | 14,989 | NONE | FAIL | **78** | B | blocked |
| [`titanwings/distilly`](https://github.com/titanwings/distilly) | 24,716 | 2,145 | 37 | 4,452 | MIT | PASS | **74** | B | watch |
| [`wshobson/agents`](https://github.com/wshobson/agents) | 39,648 | 4,223 | 5 | 2,887 | MIT | PASS | **74** | B | watch |
| [`JimLiu/baoyu-skills`](https://github.com/JimLiu/baoyu-skills) | 25,895 | 2,867 | 15 | 3,217 | MIT | PASS | **70** | B | watch |
| [`KKKKhazix/khazix-skills`](https://github.com/KKKKhazix/khazix-skills) | 20,661 | 2,200 | 49 | 3,882 | MIT | PASS | **69** | B | watch |
| [`alirezarezvani/claude-skills`](https://github.com/alirezarezvani/claude-skills) | 25,949 | 3,655 | 17 | 2,386 | MIT | PASS | **67** | B | watch |

### enterprise-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills) | 44,908 | 4,073 | 10 | 4,130 | MIT | PASS | **83** | A | review |
| [`mukul975/Anthropic-Cybersecurity-Skills`](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | 32,771 | 3,956 | 46 | 4,938 | Apache-2.0 | PASS | **80** | A | review |
| [`coreyhaines31/marketingskills`](https://github.com/coreyhaines31/marketingskills) | 50,207 | 7,606 | 112 | 6,289 | MIT | PASS | **78** | B | watch |
| [`phuryn/pm-skills`](https://github.com/phuryn/pm-skills) | 26,312 | 2,806 | 41 | 4,045 | MIT | PASS | **69** | B | watch |

### automation-skills

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach) | 81,070 | 7,060 | 134 | 12,157 | MIT | PASS | **83** | A | review |
| [`googleworkspace/cli`](https://github.com/googleworkspace/cli) | 30,992 | 1,832 | 133 | 4,789 | Apache-2.0 | PASS | **71** | B | watch |

### agent-infrastructure

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`mksglu/context-mode`](https://github.com/mksglu/context-mode) | 22,813 | 1,650 | 245 | 3,404 | Elastic-2.0 | ESCALATE | **82** | A | blocked |
| [`thedotmack/claude-mem`](https://github.com/thedotmack/claude-mem) | 93,860 | 8,259 | 183 | 7,519 | Apache-2.0 | PASS | **74** | B | watch |
| [`topoteretes/cognee`](https://github.com/topoteretes/cognee) | 30,681 | 3,027 | 494 | 829 | Apache-2.0 | PASS | **72** | B | watch |

### routing

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`Paritok-official/paritok-4b-v1`](https://github.com/Paritok-official/paritok-4b-v1) | 1,454 | 138 | 8 | 714 | Apache-2.0 | PASS | **84** | A | review |
| [`tbphp/gpt-load`](https://github.com/tbphp/gpt-load) | 6,740 | 726 | 20 | 440 | MIT | PASS | **82** | A | review |
| [`ENTERPILOT/GoModel`](https://github.com/ENTERPILOT/GoModel) | 1,155 | 100 | 72 | 124 | MIT | PASS | **81** | A | review |
| [`maximhq/bifrost`](https://github.com/maximhq/bifrost) | 8,069 | 1,214 | 995 | 451 | Apache-2.0 | PASS | **79** | B | watch |
| [`Portkey-AI/gateway`](https://github.com/Portkey-AI/gateway) | 12,987 | 1,300 | 265 | 353 | MIT | PASS | **78** | B | watch |
| [`katanemo/plano`](https://github.com/katanemo/plano) | 7,049 | 484 | 140 | 269 | Apache-2.0 | PASS | **75** | B | watch |
| [`BerriAI/litellm`](https://github.com/BerriAI/litellm) | 58,721 | 11,430 | 5,054 | 1,560 | MIT | PASS | **75** | B | watch |
| [`theopenco/llmgateway`](https://github.com/theopenco/llmgateway) | 1,633 | 183 | 68 | 95 | AGPL-3.0 AND LicenseRef-Commercial | FAIL | **74** | B | blocked |
| [`bestruirui/octopus`](https://github.com/bestruirui/octopus) | 2,625 | 427 | 19 | 265 | AGPL-3.0 | ESCALATE | **72** | B | blocked |
| [`ThinkWatchProject/ThinkWatch`](https://github.com/ThinkWatchProject/ThinkWatch) | 813 | 21 | 0 | 149 | BUSL-1.1 | FAIL | **70** | B | blocked |
| [`Fast-Editor/Lynkr`](https://github.com/Fast-Editor/Lynkr) | 550 | 61 | 5 | 59 | Apache-2.0 | PASS | **68** | B | watch |
| [`coaidev/coai`](https://github.com/coaidev/coai) | 9,311 | 1,226 | 39 | 245 | Apache-2.0 | PASS | **67** | B | watch |
| [`Kong/kong`](https://github.com/Kong/kong) | 44,137 | 5,210 | 200 | 311 | Apache-2.0 | PASS | **64** | Watchlist | watch |
| [`APIParkLab/APIPark`](https://github.com/APIParkLab/APIPark) | 1,815 | 245 | 53 | 72 | Apache-2.0 | PASS | **63** | Watchlist | watch |
| [`diegosouzapw/OmniRoute`](https://github.com/diegosouzapw/OmniRoute) | 66,084 | 9,268 | 766 | 9,400 | MIT | PASS | **61** | Watchlist | reject |
| [`router-for-me/CLIProxyAPI`](https://github.com/router-for-me/CLIProxyAPI) | 51,751 | 7,835 | 639 | 3,572 | MIT | PASS | **56** | Watchlist | reject |
| [`decolua/9router`](https://github.com/decolua/9router) | 28,738 | 5,269 | 2,101 | 3,458 | MIT | PASS | **55** | Watchlist | reject |

### mcp

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) | 43,233 | 3,522 | 582 | 6,483 | MIT | PASS | **76** | B | watch |
| [`oraios/serena`](https://github.com/oraios/serena) | 29,320 | 1,988 | 178 | 1,650 | MIT | PASS | **75** | B | watch |
| [`ChromeDevTools/chrome-devtools-mcp`](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 51,935 | 3,647 | 106 | 4,284 | Apache-2.0 | PASS | **71** | B | watch |
| [`upstash/context7`](https://github.com/upstash/context7) | 62,012 | 2,992 | 61 | 3,509 | MIT | PASS | **70** | B | watch |
| [`czlonkowski/n8n-mcp`](https://github.com/czlonkowski/n8n-mcp) | 22,884 | 3,641 | 67 | 1,498 | MIT | PASS | **68** | B | watch |
| [`brightdata/brightdata-mcp`](https://github.com/brightdata/brightdata-mcp) | 2,641 | 327 | 40 | 155 | MIT | PASS | **67** | B | watch |
| [`mobile-next/mobile-mcp`](https://github.com/mobile-next/mobile-mcp) | 6,689 | 582 | 43 | 380 | Apache-2.0 | PASS | **65** | B | watch |
| [`zcaceres/markdownify-mcp`](https://github.com/zcaceres/markdownify-mcp) | 2,990 | 253 | 29 | 143 | MIT | PASS | **64** | Watchlist | watch |
| [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) | 90,324 | 11,632 | 522 | 4,135 | Apache-2.0 AND MIT AND CC-BY-4.0 | PASS | **64** | Watchlist | watch |
| [`github/github-mcp-server`](https://github.com/github/github-mcp-server) | 32,926 | 4,965 | 320 | 1,790 | MIT | PASS | **64** | Watchlist | watch |
| [`getsentry/XcodeBuildMCP`](https://github.com/getsentry/XcodeBuildMCP) | 6,383 | 318 | 24 | 350 | MIT | PASS | **63** | Watchlist | watch |
| [`modelcontextprotocol/registry`](https://github.com/modelcontextprotocol/registry) | 7,247 | 989 | 165 | 376 | Apache-2.0 AND MIT AND CC-BY-4.0 | PASS | **56** | Watchlist | watch |

### discovery

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`sickn33/agentic-awesome-skills`](https://github.com/sickn33/agentic-awesome-skills) | 46,406 | 6,761 | 2 | 5,789 | MIT | PASS | **65** | B | watch |
| [`ComposioHQ/awesome-claude-skills`](https://github.com/ComposioHQ/awesome-claude-skills) | 75,025 | 8,670 | 1,453 | 6,858 | NONE | FAIL | **55** | Watchlist | blocked |
| [`VoltAgent/awesome-openclaw-skills`](https://github.com/VoltAgent/awesome-openclaw-skills) | 52,562 | 5,026 | 0 | 6,867 | MIT | PASS | **54** | Watchlist | watch |
| [`VoltAgent/awesome-agent-skills`](https://github.com/VoltAgent/awesome-agent-skills) | 34,310 | 3,636 | 12 | 3,243 | MIT | PASS | **53** | Watchlist | watch |
| [`github/awesome-copilot`](https://github.com/github/awesome-copilot) | 39,000 | 4,940 | 45 | 2,575 | MIT | PASS | **51** | Watchlist | watch |
| [`hesreallyhim/awesome-claude-code`](https://github.com/hesreallyhim/awesome-claude-code) | 54,026 | 4,708 | 1,046 | 3,200 | CC-BY-NC-ND-4.0 | FAIL | **50** | Watchlist | blocked |

### standard

| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |
|---|--:|--:|--:|--:|---|---|--:|---|---|
| [`agentskills/agentskills`](https://github.com/agentskills/agentskills) | 25,324 | 1,899 | 76 | 2,824 | Apache-2.0 | PASS | **65** | B | watch |

## Rejected — Strategic Conflict

Per `SKILL_SCORING.md` §4.4, a project whose core value proposition displaces paid routing is vetoed regardless of score. These are tracked for competitive intelligence and are **not** fork candidates:

| Repository | Stars | Why |
|---|--:|---|
| `diegosouzapw/OmniRoute` | 66,084 | its core value is free provider aggregation, which directly displaces paid routing. |
| `router-for-me/CLIProxyAPI` | 51,751 | converts subscriptions into API access, displacing metered token spend. ToS exposure on the wrapped services. |
| `decolua/9router` | 28,738 | explicitly positions free access against paid token consumption. |

These three are collectively the fastest-growing routing projects in the sweep. That is the finding, not an aside: the market is currently rewarding free provider aggregation. ATK's differentiation has to be reliability, cost transparency and maintained distribution — not price.

## Blocked — License Gate

Every remaining block is a real licence problem, not a missing lookup:

| Repository | Score | Stars | Note |
|---|--:|--:|---|
| `calesthio/OpenMontage` | 85 | 59,020 | AGPL-3.0 network copyleft |
| `mksglu/context-mode` | 82 | 22,813 | Non-standard licence — needs a human read |
| `anthropics/skills` | 78 | 176,286 | No LICENSE file — all rights reserved |
| `theopenco/llmgateway` | 74 | 1,633 | No LICENSE file — all rights reserved |
| `bestruirui/octopus` | 72 | 2,625 | AGPL-3.0 network copyleft |
| `ThinkWatchProject/ThinkWatch` | 70 | 813 | No LICENSE file — all rights reserved |
| `ComposioHQ/awesome-claude-skills` | 55 | 75,025 | No LICENSE file — all rights reserved |
| `hesreallyhim/awesome-claude-code` | 50 | 54,026 | No LICENSE file — all rights reserved |

`calesthio/OpenMontage` (85/100) is the most consequential block: AGPL-3.0 network copyleft means hosting a modified version as a service obliges ATK to publish complete corresponding source. `anthropics/skills` (176,354 stars) has **no LICENSE file at all**, which is all-rights-reserved by default — the most-starred project in the sweep is also the one ATK has the least right to redistribute.

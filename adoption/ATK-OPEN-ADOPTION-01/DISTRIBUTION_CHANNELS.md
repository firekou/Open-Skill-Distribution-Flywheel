# Distribution and discovery channels (A3)

Checked **2026-09-22** from each channel's current official pages (sources at the end). Most
pages were read through a summarising fetch tool, so wording is paraphrased unless quoted.
**Nothing listed here has been submitted, posted or changed.** Existing sharing drafts stay in
`integrations/headroom-atk/DISTRIBUTION.md` @ `304af885`; this file adds channel rules and the
fit decision, and does not repeat the drafts.

## Problem-first description (for every channel)

One line:

> Check offline, on your own log, whether a prompt-compression proxy shrinks what your agent sends
> **and** keeps the one line that matters — before you adopt it. No key, no cost; the live route
> is optional and names any OpenAI-compatible upstream.

Longer (for a README index or listing body):

> Coding agents read long deploy logs and CI output into the model context. A local compression
> proxy (headroom, Apache-2.0) can shrink that, but whether it helps depends entirely on the
> payload, and it can do nothing at all for common shapes such as JSON-lines logs. This recipe gives
> you a one-minute offline check that measures the bytes the upstream would actually receive and
> confirms your critical line survived — exit 0 adopt, 3 no benefit, 1 needle lost — plus the three
> configuration traps we hit (OPENAI_BASE_URL does not route the proxy; the header takes the base
> without /v1; loopback upstreams are silently refused, logged only in ~/.headroom/logs/proxy.log).
> Maintained by AI Token King; the optional live route works with any OpenAI-compatible provider.

Fixed-version links (resolve only while the PR #5 branch exists — see MILESTONES risk):

- Code: `https://github.com/firekou/Open-Skill-Distribution-Flywheel/tree/304af885193245da7186cb6b9ab247ec2494bd86/integrations/headroom-atk`
- Human trial: `https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/304af885193245da7186cb6b9ab247ec2494bd86/integrations/headroom-atk/TRY_IT.md`
- Agent contract: `integrations/headroom-atk/AGENT_QUICKSTART.md` and `agent-manifest.json` on this
  PR's result SHA (recorded in the executor response).

## Channel decisions

| channel | accepts | fits today? | account / submission | rules that bind us | how people search it | decision |
|---|---|---|---|---|---|---|
| **GitHub About + topics** (this repo) | any repo; ≤20 topics, lowercase/hyphens, ≤50 chars; admins only | **yes** | owner, repo settings | Acceptable Use bans bulk promotion | **Default repo search matches only name, About and topics; README text only with `in:readme`** | **highest leverage, owner action.** Proposed About/topics already drafted in `DISTRIBUTION.md` @ `304af885`; this finding is the reason they matter more than the README |
| **GitHub search** | repositories, auto-indexed | yes | none | — | as above | nothing to submit; measured by the PUBLIC_DISCOVERY protocol at T0 |
| **headroom Discussions → Show and tell** | "show off something you've made"; outside tools already posted there (GUI, badge, independent benchmark) | **yes** | GitHub account | Contributor Covenant 2.1; CONTRIBUTING sends *questions* to Discord #help, issues to bugs/features | browse category | **best single community entry.** One post, disclosed as ours, linking the relevant threads rather than posting in several. Counts as a community post → needs owner authorisation (not a trial invitation) |
| **headroom Discussions → Q&A threads** | answers to open questions | yes, where the question is ours | GitHub account | same | thread | answer the question first, disclose authorship; this is the channel for A4 invitations (see CANDIDATES) |
| **Agent Skills spec** (agentskills.io) | a folder with `SKILL.md` (YAML frontmatter + body), optional `scripts/` | **only with a SKILL.md** | none; it is a format | — | agents load `name` + `description` at start-up | **defer to M3.** Writing a skill before M2 feedback would be a guess |
| **Claude Code plugin marketplace** (self-hosted) | plugins incl. skills-only | only with a plugin wrapper | none for self-hosted (`/plugin marketplace add owner/repo`) | — | `/plugin install` | **defer to M3** |
| **Claude official plugin directory** | public GitHub plugin link via submission form | only with a wrapper | org admin or Console Developer+ role | Software Directory Policy §4.C bans software that "exists primarily as an advertising or promotional vehicle"; §3.F requires owning/controlling any endpoint it connects to; §3.A privacy policy for remote services | built in for all users | **defer; policy risk.** The live route must read as optional, not an ATK funnel, and §3.F needs a reading before any submission |
| **Smithery skills** | GitHub-backed skill with valid `SKILL.md` (else 422) | only with a SKILL.md | Smithery API key, own namespace | none found | text + semantic search | defer to M3 |
| **Official MCP Registry** | `server.json` for publicly reachable MCP servers | **does not fit** — this is not an MCP server | — | — | — | not used; building an MCP server to get listed would be a new product |
| **Hugging Face Hub** | models, datasets, Spaces | **does not fit** — a recipe is none of these; a Space is a new hosted app | — | — | — | not used |
| `pleasedodisturb/awesome-llm-token-optimization` | one-line entries, alphabetical, one per PR | weak | GitHub PR | "Self-submission is welcome"; bans coordinated multi-entry self-promotion; needs ≥30-day-old repo and ≥2 contributors **or** ≥50 stars | browse | **not yet eligible**; headroom itself is already listed |
| `QuesmaOrg/awesome-ai-tokenomics` | tools/papers with `verified_on` dates | weak | GitHub PR | own projects allowed with disclosed affiliation, public sources, **one outside adoption signal** (stars do not count); no marketing copy | browse | **not eligible until M2** produces an outside adoption record |
| LiteLLM Headroom guardrail docs | — | not a channel | — | — | — | relevant context: a second integration style (gateway calls headroom as a sidecar) that we did not test |

## What this means for order

1. Owner applies About + topics (the only channel where one change affects default GitHub search).
2. A4 invitations in headroom Q&A threads, at most three, one each.
3. After an outside success: the Show and tell post (owner authorisation) and the tokenomics list
   (its adoption-signal rule is exactly what M2 produces).
4. SKILL.md / plugin wrappers only in M3, from real M2 feedback.

## Sources (all checked 2026-09-22)

- GitHub topics: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
- GitHub repository search: https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories
- GitHub Acceptable Use: https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies
- headroom: https://github.com/headroomlabs-ai/headroom · Discussions https://github.com/headroomlabs-ai/headroom/discussions · CONTRIBUTING https://github.com/headroomlabs-ai/headroom/blob/main/CONTRIBUTING.md · Code of Conduct https://github.com/headroomlabs-ai/headroom/blob/main/CODE_OF_CONDUCT.md
- Agent Skills: https://agentskills.io/specification · https://github.com/anthropics/skills (its CONTRIBUTING.md returned 404; no outside-contribution process found)
- Claude Code plugins: https://code.claude.com/docs/en/plugin-marketplaces · https://claude.com/docs/plugins/submit · https://github.com/anthropics/claude-plugins-community · https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy
- MCP Registry: https://modelcontextprotocol.io/registry/about
- Smithery: https://smithery.ai/docs/llms.txt · https://smithery.ai/docs/api-reference/skills/create-or-update-a-skill.md
- Hugging Face: https://huggingface.co/docs/hub/repositories
- Awesome lists: https://github.com/pleasedodisturb/awesome-llm-token-optimization · https://github.com/QuesmaOrg/awesome-ai-tokenomics
- LiteLLM: https://docs.litellm.ai/docs/proxy/headroom

Not checked: headroom's Discord rules (login required), Hugging Face Spaces docs page, GitHub
Discussions feature docs.

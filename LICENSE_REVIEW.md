# LICENSE_REVIEW.md

> ATK License Gate · Version 1.0 · Last updated: 2026-09-14

The License Gate is an **independent veto** on the Fork Pipeline. A repository may score 100
on `skill_score` and still be blocked here. No exceptions, no "we'll check later".

> This document is operational engineering guidance, not legal advice. Any ruling marked
> **ESCALATE** must be reviewed by counsel before ATK publishes a redistribution.

---

## 1. The Seven Questions

For every candidate, the License Agent must answer all seven and record the answers in
`registry/skill_registry.json` under `license`:

| # | Question | Field | Blocking? |
|---|---|---|---|
| 1 | Does it permit **modification**? | `modification` | Yes |
| 2 | Does it permit **redistribution**? | `redistribution` | Yes |
| 3 | Does it permit **commercial use**? | `commercial_use` | Yes |
| 4 | Must **copyright notices** be retained? | `attribution_required` | No — but must be honoured |
| 5 | Is a **NOTICE** file required? | `notice_required` | No — but must be honoured |
| 6 | Is there a **copyleft** requirement? | `copyleft` | Conditional (§3) |
| 7 | Is there a **trademark** issue? | `trademark_risk` | Conditional (§4) |

Plus one meta-field that must never be skipped:

| Field | Meaning |
|---|---|
| `verified` | `true` only if the licence was read from the repository itself or from GitHub's licence metadata. Never inferred from a README badge or a description string. |
| `verified_at` | Date of verification |
| `method` | How it was verified |

**A candidate with `license.verified: false` is treated exactly like a candidate with no
license: blocked.**

---

## 2. Per-License Rulings

| License | Modify | Redistribute | Commercial | Copyleft | ATK Ruling |
|---|---|---|---|---|---|
| **MIT** | ✅ | ✅ | ✅ | None | **PASS** — retain copyright + license text in every distribution |
| **Apache-2.0** | ✅ | ✅ | ✅ | None | **PASS** — retain NOTICE, state changes, patent grant applies |
| **BSD-2 / BSD-3** | ✅ | ✅ | ✅ | None | **PASS** — BSD-3: do not use upstream names to endorse ATK |
| **ISC** | ✅ | ✅ | ✅ | None | **PASS** |
| **Unlicense / CC0** | ✅ | ✅ | ✅ | None | **PASS** — still attribute, as courtesy |
| **MPL-2.0** | ✅ | ✅ | ✅ | File-level | **CONDITIONAL** — modified MPL files stay MPL; ATK additions in new files may stay separate |
| **LGPL-3.0** | ✅ | ✅ | ✅ | Library-level | **CONDITIONAL** — dynamic linking only; no static bundling into closed ATK components |
| **GPL-3.0** | ✅ | ✅ | ✅ | Strong | **ESCALATE** — the whole distributed work becomes GPL. Fork only as a standalone GPL deliverable, never linked into proprietary ATK code |
| **AGPL-3.0** | ✅ | ✅ | ✅ | Network | **ESCALATE / DEFAULT NO** — §13 triggers on *network use*. If ATK hosts a modified version as a service, ATK must publish the complete corresponding source. Incompatible with closed ATK Routing internals |
| **BSL 1.1 (Business Source License)** | ✅ | ✅ | ❌ *(above the Use Grant)* | Converts later | **FAIL** — self-describes as "not an Open Source license". Free use only under the Additional Use Grant; beyond it a paid licence is required |
| **Elastic License 2.0 (ELv2)** | ✅ | ✅ | ✅ *(but not as a service)* | None | **CONDITIONAL** — may not be offered as a hosted or managed service. Fine to ship for self-install; blocked if ATK hosts it |
| **CC BY-NC-ND 4.0** | ❌ | ✅ *(verbatim only)* | ❌ | — | **FAIL** — NonCommercial bars ATK's use, NoDerivatives bars forking. Linking is unaffected |
| **SSPL / "Commons Clause"** | ⚠️ | ⚠️ | ❌ *(typically)* | — | **FAIL** — not open source; commercial redistribution restricted |
| **No LICENSE file** | ❌ | ❌ | ❌ | — | **FAIL** — default copyright: all rights reserved |
| **Unclear / conflicting** | ? | ? | ? | ? | **FAIL** until resolved in writing by upstream |

> "It's on GitHub and public" is **not** a license. A repository with no LICENSE file grants
> nothing beyond GitHub's Terms of Service (view and fork *on GitHub*) — it does not grant
> ATK the right to redistribute a modified version.

---

## 3. Copyleft Handling

Copyleft is not automatically disqualifying — it is a **distribution-architecture
constraint**.

| Scenario | Ruling |
|---|---|
| GPL/AGPL skill run as a standalone tool the user installs; ATK ships only a config/adapter | Workable — ATK's adapter can be a separate work |
| GPL/AGPL code linked into ATK Routing internals | **Blocked** |
| AGPL code hosted by ATK as a managed service | **Blocked** unless ATK publishes complete corresponding source |
| MPL-2.0 file modified by ATK | Allowed — that file remains MPL, ATK publishes it |

**Phase 1 default: do not fork GPL-3.0 or AGPL-3.0 projects.** The engineering cost of
keeping the boundary clean exceeds the value of the first ten skills, and getting it wrong
is the kind of mistake that is expensive to unwind after distribution.

---

## 4. Trademark

Licenses grant rights to **code**, not to **names and logos**. Apache-2.0 §6 says so
explicitly; MIT is silent, which is not the same as permissive.

Rules for every ATK fork:

1. **Rename the distribution.** `atk-<name>` or `<name>-atk`, never the bare upstream name.
2. **Do not reuse upstream logos or wordmarks** in ATK marketing.
3. **State the relationship plainly:** *"ATK distribution of `<upstream>`, maintained by AI
   Token King. Not affiliated with or endorsed by the upstream authors."*
4. **Never imply endorsement.** No "official", no "partnered with", no co-branded lockups.
5. If upstream carries a registered mark or a trademark policy file → **ESCALATE**.

---

## 5. Attribution Requirements (all ATK forks)

Every ATK redistribution must ship:

1. The **original LICENSE file, unmodified**, at the repository root.
2. A **NOTICE** file (required for Apache-2.0, good practice everywhere) naming the upstream
   project, author, URL and license.
3. A **README attribution block** above the fold — not buried at the bottom:

   ```markdown
   ## Upstream

   This is an ATK-maintained distribution of
   [`<upstream/repo>`](https://github.com/<upstream/repo>) by `<author>`,
   licensed under `<LICENSE>`.

   **Changes made by ATK:** see [CHANGES-ATK.md](./CHANGES-ATK.md).

   Not affiliated with or endorsed by the upstream authors.
   ```

4. A **`CHANGES-ATK.md`** listing every ATK modification. Apache-2.0 §4(b) requires stating
   changes; ATK does this for all licenses regardless, because it is also what makes the
   fork defensible as a distribution rather than a rebrand.

---

## 6. Verification Procedure

```
1. Read LICENSE / LICENSE.md / COPYING from the repository's default branch
2. Cross-check against GitHub's detected license metadata
3. Check for per-directory or per-file license headers that differ from the root
4. Check for a NOTICE file
5. Check for a TRADEMARK / BRANDING policy file
6. Check package manifests (package.json, pyproject.toml, Cargo.toml) for a conflicting
   license field
7. Check bundled vendored dependencies for incompatible licenses
8. Record all seven answers + verified/verified_at/method in the registry
```

Steps 3 and 7 catch the two failure modes that matter most: a permissive root license over a
copyleft subdirectory, and a permissive project that vendors a GPL dependency.

---

## 7. Phase 1 Verification Status

Verified in two passes against GitHub license metadata: **2026-09-14** (topic-scoped sweeps)
and **2026-09-15** (targeted re-check of everything the first pass left open).

> **Correction.** The first pass reported 22 candidates as "license unverified". That was a
> gap in *query coverage*, not a finding about those projects — the topic-scoped searches
> simply never covered them. The re-check resolved all 22. Fourteen turned out to be cleanly
> licensed. Reporting them as blocked was over-cautious in a way that would have cost real
> opportunities.

### PASS — MIT (35)

`blader/humanizer` · `mvanhorn/last30days-skill` · `tt-a1i/archify` ·
`cathrynlavery/diagram-design` · `virgiliojr94/book-to-skill` ·
`OthmanAdi/planning-with-files` · `Leonxlnx/taste-skill` · `addyosmani/agent-skills` ·
`DietrichGebert/ponytail` · `Egonex-AI/Understand-Anything` · `Panniantong/Agent-Reach` ·
`nextlevelbuilder/ui-ux-pro-max-skill` · `wshobson/agents` · `alirezarezvani/claude-skills` ·
`K-Dense-AI/scientific-agent-skills` · `VoltAgent/awesome-agent-skills` ·
`VoltAgent/awesome-openclaw-skills` · `sickn33/agentic-awesome-skills` · `phuryn/pm-skills` ·
`JimLiu/baoyu-skills` · `titanwings/distilly` · `KKKKhazix/khazix-skills` ·
`zarazhangrui/frontend-slides` · `github/awesome-copilot` · `reactive-resume/reactive-resume` ·
`pascalorg/editor` · `oraios/serena` · `DeusData/codebase-memory-mcp` · `tbphp/gpt-load` ·
`ENTERPILOT/GoModel` · `Portkey-AI/gateway` · `BerriAI/litellm` · `diegosouzapw/OmniRoute` ·
`decolua/9router` · `router-for-me/CLIProxyAPI`

**Newly resolved in the second pass:** `upstash/context7` · `github/github-mcp-server` ·
`czlonkowski/n8n-mcp` · `coreyhaines31/marketingskills` · `kepano/obsidian-skills` ·
`getsentry/XcodeBuildMCP` · `zcaceres/markdownify-mcp` · `brightdata/brightdata-mcp`

### PASS — Apache-2.0 (17)

`nexu-io/open-design` · `googleworkspace/cli` · `topoteretes/cognee` ·
`agentskills/agentskills` · `alibaba/open-code-review` · `Kong/kong` · `coaidev/coai` ·
`maximhq/bifrost` · `katanemo/plano` · `APIParkLab/APIPark` ·
`Paritok-official/paritok-4b-v1` · `Fast-Editor/Lynkr`

**Newly resolved in the second pass:** `Graphify-Labs/graphify` · `thedotmack/claude-mem` ·
`mukul975/Anthropic-Cybersecurity-Skills` · `ChromeDevTools/chrome-devtools-mcp` ·
`mobile-next/mobile-mcp`

*Apache-2.0 additionally requires: retain NOTICE, state changes in `CHANGES-ATK.md`.*

### ESCALATE — AGPL-3.0 (2)

| Repository | Score | Ruling |
|---|--:|---|
| `calesthio/OpenMontage` | 85 | Network copyleft. Would otherwise rank in the Top 5. Blocked for Phase 1 per §3. |
| `bestruirui/octopus` | 72 | Network copyleft. Watchlist only. |

Hosting a modified version of either as a service obliges ATK to publish complete
corresponding source — including anything the courts would treat as part of the same work.

### Read in full — the six "non-standard license" repositories

All six LICENSE files were fetched and read on **2026-09-15**. The outcome contradicts the
earlier estimate recorded in this document, which predicted most would resolve to PASS:

| Repository | Actual license | Ruling |
|---|---|---|
| `modelcontextprotocol/servers` | Apache-2.0, with legacy MIT contributions during an in-progress relicensing; docs CC-BY-4.0 | **PASS** |
| `modelcontextprotocol/registry` | Same as above | **PASS** |
| `mksglu/context-mode` | **Elastic License 2.0** | **CONDITIONAL** |
| `theopenco/llmgateway` | **AGPL-3.0**, plus an `ee/` directory under a separate commercial license | **FAIL** |
| `ThinkWatchProject/ThinkWatch` | **Business Source License 1.1** | **FAIL** |
| `hesreallyhim/awesome-claude-code` | **CC BY-NC-ND 4.0** | **FAIL** |

> **Correction.** This document previously predicted that most of these would "turn out to be
> a standard license with a modified header" and move to PASS. Two did. Four did not, and
> three of those are deliberately restrictive. The reasoning was wrong in a specific way:
> a project that adopts a non-standard license has usually gone out of its way to do so, and
> the most common motive is to prevent exactly the kind of commercial redistribution ATK is
> planning. **"Unusual license" correlates with "restrictive", not with "clerical variation".**

#### The three that matter

**`ThinkWatchProject/ThinkWatch` — BSL 1.1.** The license states in its own Notice section
that it "is not an Open Source license". Its Additional Use Grant permits free production use
only up to **10,000,000 billable tokens and 10,000 MCP tool calls per calendar month**;
beyond either threshold a paid commercial license is required, priced by usage tier. It
converts to GPL-2.0-or-later on **2030-04-02**.

This is the sharpest possible mismatch with ATK: the licensed thresholds are denominated in
exactly the units ATK's business is measured in, and ATK would cross them by design.

**`mksglu/context-mode` — Elastic License 2.0.** ELv2 grants the right to use, copy,
distribute and prepare derivative works. The binding limitation is:

> *"You may not provide the software to third parties as a hosted or managed service, where
> the service provides users with access to any substantial set of the features or
> functionality of the software."*

So the ruling depends entirely on ATK's delivery model:

| ATK model | Allowed? |
|---|---|
| Ship it for users to self-install, routing to ATK | **Yes** |
| Host it and offer it as an ATK service | **No** |

ELv2 also forbids circumventing any license-key functionality and removing licensor notices.
At 82/100 this is the highest-scoring candidate that a delivery-model decision could unlock.

**`theopenco/llmgateway` — AGPL-3.0 plus a commercial `ee/` tier.** Two independent blocks:
network copyleft on the open portion, and a separate commercial license on the enterprise
directory. Either alone would be disqualifying.

#### The two that passed

Both MCP repositories are mid-relicensing from MIT to Apache-2.0. Contributions whose authors
have not yet consented to relicensing **remain under MIT**, and the file is explicit that
"no rights beyond those granted by the applicable original license are conveyed". Both
licenses are permissive, so the mixture is workable — but any ATK NOTICE must reflect both,
not just Apache-2.0.

Neither is a fork target regardless: they are ecosystem reference infrastructure, and the
trademark risk is high. Contribute upstream; publish into the registry.

### FAIL — no license file (2)

| Repository | Stars | Ruling |
|---|--:|---|
| `anthropics/skills` | 176,354 | **No LICENSE file.** Confirmed: the API record carries no license field at all. |
| `ComposioHQ/awesome-claude-skills` | 75,025 | No LICENSE file detected under any license filter. |

**No license means all rights reserved**, not public domain. See §9.

---

## 8. Registry Schema — `license` block

```json
{
  "license": {
    "spdx": "MIT",
    "verified": true,
    "verified_at": "2026-09-14",
    "method": "github-license-metadata",
    "modification": true,
    "redistribution": true,
    "commercial_use": true,
    "attribution_required": true,
    "notice_required": false,
    "copyleft": "none",
    "trademark_risk": "low",
    "ruling": "PASS"
  }
}
```

`ruling` ∈ `PASS` · `CONDITIONAL` · `ESCALATE` · `FAIL` · `UNVERIFIED`.

Only `PASS` and a signed-off `CONDITIONAL` may proceed to fork.


---

## 9. "Attribute It and Take It Down If Challenged" — Why This Does Not Work

A reasonable-sounding proposal comes up often: *where the license is unclear, publish anyway
but state the original source clearly; we are not claiming it as ours, and if a rights holder
ever objects, we take it down.*

The instinct is right — **attribution is mandatory and ATK should do it everywhere.** But
attribution does not supply the permission that a fork requires, and the takedown model does
not apply to ATK's position. Four reasons:

### 9.1 Attribution and permission are different things

Copyright attaches automatically the moment a work is written. No registration, no notice
required. It splits into two separate rights:

| Right | What satisfies it |
|---|---|
| To be **credited** as the author | Attribution — a NOTICE file, a README credit |
| To control **copying, adapting and distributing** | A **license**. Only the rights holder can grant it. |

Crediting someone discharges the first. It does nothing about the second. Copying a whole
repository, modifying it, and redistributing it under an ATK name exercises the second right,
and no amount of credit creates permission to do so.

### 9.2 The academic-citation analogy does not carry over

Citing a paper means quoting a short passage and pointing at the source. That is a small,
transformative use — the kind fair use / fair dealing exists to protect.

Forking a repository means copying **the entire work**, modifying it, and redistributing it.
Same intent, completely different scale of use. The citation norm does not extend to it, and
no academic publisher would treat republishing a whole paper under a new masthead as
"citation".

### 9.3 Notice-and-takedown protects hosts, not republishers

Safe-harbour regimes (DMCA §512 and its equivalents) shield **intermediaries** that host
content other people uploaded — GitHub, YouTube, a CDN. The protection is conditional on the
platform not being the one who chose to copy the work.

If ATK forks, modifies, brands and publishes, ATK is the **direct** party doing the copying.
There is no intermediary role to claim. "We would take it down if asked" is a mitigation
after the fact, not a defence — the infringement, if any, already happened at publication.

### 9.4 Commercial use makes the position worse, not better

ATK monetises through routing. Commercial use is weighed against almost every fair-use
factor, and it raises the damages exposure. The same act carries more risk for ATK than for
an individual doing it privately.

### 9.5 There is also a business reason, separate from the legal one

The entire distribution strategy runs on developer trust. Being publicly called out for
republishing someone's unlicensed work — with credit, but without permission — would damage
exactly the asset the strategy depends on. That cost arrives faster than any legal one, and
it is not reversible by taking the repository down.

---

## 10. What To Do Instead

The good news: after the second-pass check, only **10 of 68** candidates are genuinely
blocked. For those, four legitimate routes, in order of preference:

### 10.1 Just ask — the fastest route

Open an issue:

> Hi — really useful project. We would like to build on it, but there is no LICENSE file, so
> the terms aren't clear. Would you consider adding one? MIT or Apache-2.0 would both work
> for us. Happy to send a PR with the file if that helps.

Most maintainers of an unlicensed repository simply never got round to it. This is answered
in days more often than not, costs nothing, and converts a blocked candidate into a clean
PASS — with goodwill attached instead of risk.

**Do this first for all 8 ESCALATE and FAIL candidates.** It is the highest
return-on-effort item in the entire license backlog.

### 10.2 Link instead of fork — always available

Linking to a public repository needs no permission whatsoever. `awesome-ai-skills` can list
**anything**, including all 10 blocked candidates, with a description, a review and a rating.

This captures most of the discovery and SEO value with zero license exposure. For a project
ATK cannot fork, a genuinely useful review is often worth more than a fork would have been.

### 10.3 Write a companion package, not a fork

Ship the ATK routing adapter as a **separate add-on** that works alongside the upstream
project without copying it. The user installs upstream from its own source and installs the
ATK layer next to it.

ATK owns 100% of what it publishes, there is no license question at all, and there is no
sync burden — the pattern `UPSTREAM_SYNC.md` §8 already recommends when a fork becomes too
expensive to maintain.

### 10.4 Fork on GitHub, but understand the limit

GitHub's Terms of Service do grant other users the right to view and **fork** public
repositories *through GitHub*. So pressing the Fork button is permitted even with no license.

What that does **not** grant: redistributing outside GitHub (npm, PyPI, Docker Hub, a
download on ATK's site), relicensing, or presenting it as an ATK product. The fork can exist;
turning it into a distribution is the step that needs an actual license.

### 10.5 Attribution is mandatory regardless

Everything in §5 applies to every ATK fork, including the cleanly-licensed ones. Attribution
is the floor, not the workaround — necessary always, sufficient never.

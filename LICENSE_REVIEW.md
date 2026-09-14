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
| **BSL / SSPL / "Commons Clause"** | ⚠️ | ⚠️ | ❌ *(typically)* | — | **FAIL** — not open source; commercial redistribution restricted |
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

All licenses below were verified on **2026-09-14** against GitHub's license metadata
(`license:` qualifier on the repository search API). Entries not verified by that method are
marked explicitly — they are **blocked** until a manual read is performed.

### PASS — MIT

`blader/humanizer` · `mvanhorn/last30days-skill` · `tt-a1i/archify` ·
`cathrynlavery/diagram-design` · `virgiliojr94/book-to-skill` ·
`OthmanAdi/planning-with-files` · `Leonxlnx/taste-skill` · `addyosmani/agent-skills` ·
`DietrichGebert/ponytail` · `Egonex-AI/Understand-Anything` · `Panniantong/Agent-Reach` ·
`nextlevelbuilder/ui-ux-pro-max-skill` · `wshobson/agents` · `alirezarezvani/claude-skills` ·
`K-Dense-AI/scientific-agent-skills` · `VoltAgent/awesome-agent-skills` ·
`VoltAgent/awesome-openclaw-skills` · `sickn33/agentic-awesome-skills` · `phuryn/pm-skills` ·
`JimLiu/baoyu-skills` · `titanwings/distilly` · `KKKKhazix/khazix-skills` ·
`zarazhangrui/frontend-slides` · `github/awesome-copilot` · `reactive-resume/reactive-resume` ·
`pascalorg/editor` · `oraios/serena` · `DeusData/codebase-memory-mcp` ·
`tbphp/gpt-load` · `ENTERPILOT/GoModel` · `Portkey-AI/gateway` · `BerriAI/litellm` ·
`diegosouzapw/OmniRoute` · `decolua/9router` · `router-for-me/CLIProxyAPI`

### PASS — Apache-2.0

`nexu-io/open-design` · `googleworkspace/cli` · `topoteretes/cognee` ·
`agentskills/agentskills` · `alibaba/open-code-review` · `Kong/kong` · `coaidev/coai` ·
`maximhq/bifrost` · `katanemo/plano` · `APIParkLab/APIPark` ·
`Paritok-official/paritok-4b-v1` · `Fast-Editor/Lynkr`

*Apache-2.0 additionally requires: retain NOTICE, state changes in `CHANGES-ATK.md`.*

### ESCALATE — AGPL-3.0

| Repository | Ruling |
|---|---|
| `bestruirui/octopus` | Network copyleft. Blocked for Phase 1 per §3. Watchlist only. |

### BLOCKED — license not verified

These were **not** resolved by the automated license filter and must not enter the pipeline
until a human reads the LICENSE file directly:

`anthropics/skills` · `theopenco/llmgateway` · `ThinkWatchProject/ThinkWatch` ·
`Graphify-Labs/graphify` · `mksglu/context-mode` · `thedotmack/claude-mem` ·
`calesthio/OpenMontage` · `coreyhaines31/marketingskills` · `kepano/obsidian-skills` ·
`mukul975/Anthropic-Cybersecurity-Skills` · `ComposioHQ/awesome-claude-skills` ·
`hesreallyhim/awesome-claude-code`

> `anthropics/skills` is a notable case: it carries the `agent-skills` topic and 176k stars
> but did not match either the MIT or Apache-2.0 filter. It is **blocked pending manual
> review** rather than assumed permissive.
>
> `mukul975/Anthropic-Cybersecurity-Skills` *describes itself* as Apache-2.0 in its
> repository description. A self-description in prose is not verification — see §1.

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

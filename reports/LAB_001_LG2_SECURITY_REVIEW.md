# Lab 001 — LG2 Security Review

**Date:** 2026-09-16 · **Gate:** LG2 · **Owner seat:** `security-agent`
**Method:** **static inspection only.** All 8 candidates were cloned at their pinned commit and
read. **No candidate was installed, built or executed** (Guardrail 7).

**Evidence:** clones verified by `git rev-parse HEAD` against the pin; findings below cite file
and line where a claim rests on source.

> **A security PASS is not a product-quality VERIFIED.** It means ATK may execute this code
> under the stated conditions. It says nothing about whether the tool works.

---

## Verdict summary

| Candidate | Licence | Verdict | Decisive finding |
|---|---|---|---|
| `crwdla/tokentab` | MIT | **PASS** | Zero external hosts. 12 deps, 24 files, no installer, no telemetry |
| `headroomlabs-ai/headroom` | Apache-2.0 | **CONDITIONAL** | Telemetry off by default but a `DEFAULT_ENDPOINT` ships in `headroom/telemetry/session.py` |
| `rtk-ai/rtk` | Apache-2.0 | **CONDITIONAL** | Documented installer pipes `raw.githubusercontent.com/.../**master**/install.sh` to `sh` — a moving ref |
| `Paritok-official/paritok-4b-v1` | Apache-2.0 | **CONDITIONAL** | GPU-server mode **POSTs each segment to `paritok.com/api/compress`** — prompt content leaves the host |
| `yvgude/lean-ctx` | Apache-2.0 | **CONDITIONAL** | Installer is `curl https://leanctx.com/install.sh \| sh` — vendor domain, not the pinned commit |
| `juyterman1000/entroly` | Apache-2.0 | **CONDITIONAL** | `evil.com` verified benign (SAST test fixture); 9 eval/exec sites inherent to a code-analysis tool |
| `toby-bridges/api-relay-audit` | **AGPL-3.0** | **CONDITIONAL** | Network copyleft; and it is a traffic interceptor pointed at ATK's own keys |
| `NadirRouter/NadirClaw` | **PolyForm Noncommercial 1.0.0** | **FAIL / LICENCE** | Commercial use by a for-profit business requires a separate commercial licence |

**1 PASS · 6 CONDITIONAL PASS · 1 FAIL**

---

## FAIL — `NadirRouter/NadirClaw`

**PolyForm Noncommercial License 1.0.0**, quoted from `LICENSE` at the pinned commit:

> "COMMERCIAL use — including use in or by a for-profit business, or to build or operate a paid
> product or service — requires a separate commercial license. Commercial licenses are available
> through https://getnadir.com"

ATK is a for-profit business running this benchmark to inform a commercial product. That is
squarely the excluded use. **No amount of sandboxing fixes a licence.**

This also **corrects the registry**, which carried NadirClaw's licence as unresolved (`?`). It
was never verified until a clone was read. Evidence Ledger E016.

### Matrix impact — no substitution

Per the review instruction, the cell is **marked, not replaced**:

> **C4 / C5 cells allocated to NadirClaw are recorded `FAILED / SECURITY`.**
> The 100-run matrix keeps its shape. The runs are **not** reassigned to another tool, and no
> replacement candidate is introduced. H3 is tested by the remaining C4 design (tier-adjacent
> routing, frozen methodology §7), which does not depend on NadirClaw.

**Route to unblock, if the Editor-in-Chief wants it:** obtain a commercial licence from the
vendor. That is a purchasing decision, not a technical one, and is out of scope here.

---

## CONDITIONAL PASS — conditions are binding, not advisory

### `headroomlabs-ai/headroom` — Apache-2.0

| Check | Finding |
|---|---|
| Dependencies | 90 Python + 36 Rust, **3 lockfiles present** — good hygiene, large surface |
| Telemetry | CLI help states *"Opt in to anonymous telemetry in the runtime (**off by default**)"*. But `telemetry_enabled=True` appears at two construction sites, and a `DEFAULT_ENDPOINT` ships in `headroom/telemetry/session.py` |
| Egress | Provider endpoints only (`api.openai.com`, `api.anthropic.com`, `api.deepseek.com`, …) |
| Code execution | 31 subprocess sites, 1 `shell=True` |
| Local storage | Caches originals locally for reversibility — **cache location and retention must be pinned** |

**Conditions:** telemetry explicitly disabled **and** its endpoint blocked at the sandbox (two
independent controls, because a default is a setting and a firewall is a boundary) · cache
directory inside the run sandbox, wiped between runs · build from the pinned SHA.

### `rtk-ai/rtk` — Apache-2.0

| Check | Finding |
|---|---|
| Installer | `INSTALL.md:47` and `README.md:80,392`: `curl -fsSL .../rtk/**master**/install.sh \| sh`. **A moving branch, not the pinned commit** |
| Code execution | Wraps and executes bash commands — command-injection surface is **inherent to its function**, not a defect |
| Dependencies | 54 Rust crates, 1 lockfile |
| Telemetry | 15 files mention it; no third-party analytics SDK found |

**Conditions:** **never use the documented installer** — build from commit `b1c0dc0…` · treat
every wrapped command as untrusted input · no production shell environment.

### `Paritok-official/paritok-4b-v1` — Apache-2.0 — **highest data-exposure risk**

`paritok/config.py:29` and `paritok/cli.py:15-20`:

> *"true → use the Paritok GPU server (needs an API key from https://paritok.com)"*
> *"base_url: https://www.paritok.com/api # POST /compress"*
> *"The proxy POSTs each segment to `{base_url}/compress`"*

**In GPU-server mode the prompt content itself is transmitted to the vendor.** For a compression
benchmark that would silently exfiltrate every task input.

**Conditions:** **self-hosted mode only** · `paritok.com` and `www.paritok.com` blocked by name
in the egress allowlist · any run whose egress log shows either host is **void and re-opens LG2**.

### `yvgude/lean-ctx` — Apache-2.0

Installer is `curl -fsSL https://leanctx.com/install.sh | sh` (`README.md:197`,
`.claude-plugin/manifest.json:9`) — a **vendor-controlled domain**, so the installed artifact is
not the reviewed artifact. 25 credential-handling sites, 22 config-write sites, 8 curl-pipe-shell
references.

**Conditions:** build from commit `79fe3cf…` · `leanctx.com` blocked · **resolve the tag
ambiguity first** — the newest tag is a VS Code extension release and may not be the core library.

### `juyterman1000/entroly` — Apache-2.0

`evil.com` appeared in the scan and was **verified benign**: `entroly-core/src/sast.rs:3092` and
`entroly-wasm/src/sast.rs:3086`, an HTML string inside a SAST unit test. Checking rather than
assuming is the point. 9 eval/exec sites are consistent with a static-analysis tool that parses
code. 30 deps, 2 lockfiles.

**Conditions:** build from the pinned SHA · default-deny egress · `api.telegram.org` and
`discord.gg` appear in the tree and must be blocked.

### `toby-bridges/api-relay-audit` — **AGPL-3.0**

Two separate issues, both manageable:

1. **AGPL network copyleft.** Internal use produces no distribution, so running it to audit ATK's
   own routing is fine. **If ATK ever hosts a modified version as a service, complete
   corresponding source must be published.**
2. **It is a traffic interceptor.** Pointing it at ATK's own relay means it sees prompts,
   responses and keys. `FOR_JOHN.md:594` also records that detection logic was **ported from
   `hvoy.ai`** — third-party provenance inside a security tool, worth knowing before trusting it.

**Conditions:** benchmark keys only, never production · captured traffic stays in the sandbox ·
unmodified, or the AGPL obligation is triggered.

---

## PASS — `crwdla/tokentab` (MIT)

The only unconditional pass, and it earns it by having almost no surface:

| Check | Finding |
|---|---|
| External hosts | **None.** The scan found zero outbound hosts in source |
| Dependencies | 12 |
| Installer / postinstall / curl-pipe-sh | None |
| Telemetry | None found |
| Code execution | 2 subprocess sites |
| Files | 24 |

**The one real risk is inbound, not outbound:** it reads agent session logs, which can contain
secrets and customer data. It cannot exfiltrate them — **there is no egress path in the code** —
but ATK must still point it only at benchmark logs, never production transcripts.

**Note:** no tags, so it is pinned at a HEAD commit. Reproducible, but with no release boundary.

---

## What this review did not do

- **Nothing was executed.** No install, no build, no run. Verdicts rest on reading source.
- **No dependency CVE scan.** `pip-audit` / `cargo audit` require resolving the dependency tree,
  which downloads and would begin executing packaging code. Deferred to inside the sandbox.
- **No binary or wasm inspection.** `entroly` ships a wasm crate that was read as source only.
- **Known-issue search was limited** to each repository's own tracker and docs.

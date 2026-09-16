# Lab 001 — Candidate Runtime Profiles

**Created:** 2026-09-16 · **Authority:** Editor-in-Chief review, Decision 2
**Binds:** every C5 run, and any run in which a candidate participates
**Supersedes nothing.** Adds to the LG2 conditions; it does not relax any of them.

---

## Governing principle — Minimum Necessary Capability

A candidate runs with the smallest set of capabilities that lets it do the thing being measured,
and nothing more. Any mode that transmits **prompt, response, context, log or task content** to a
third-party endpoint not required by the benchmark is **disabled for this round**. Not "logged".
Not "reviewed afterwards". Disabled, and the host blocked at the sandbox boundary as well,
because a default is a setting and a firewall is a boundary.

The second principle is narrower and easier to forget: **a capability the benchmark does not
need is also a measurement contaminant.** Telemetry that phones home costs tokens nobody
attributed, adds latency nobody controlled, and introduces a failure mode nobody pre-registered.
Turning it off is not only a privacy control.

## What a profile must freeze

Ten attributes, per Decision 2. A candidate whose profile cannot state all ten **does not run**.

1. Commit SHA · 2. Dependency version · 3. Execution mode · 4. Feature flags ·
5. Network egress · 6. External endpoint · 7. Telemetry state · 8. GPU / remote processing state ·
9. Local storage behaviour · 10. Credential scope

---

## Status summary

| Candidate | LG2 | Profile | Blocking gap |
|---|---|---|---|
| `crwdla/tokentab` | PASS | **INCOMPLETE** | Dependency version is a range (`rich>=13.0`), no lockfile |
| `headroomlabs-ai/headroom` | CONDITIONAL | **COMPLETE** | — |
| `rtk-ai/rtk` | CONDITIONAL | **COMPLETE** | — |
| `juyterman1000/entroly` | CONDITIONAL | **COMPLETE** | — |
| `Paritok-official/paritok-4b-v1` | CONDITIONAL | **INCOMPLETE** | 39 dependency ranges, 0 exact pins, no lockfile |
| `yvgude/lean-ctx` | CONDITIONAL | **INCOMPLETE** | Pinned tag names a VS Code extension in a 20-package monorepo; which artifact is under test is unresolved |
| `toby-bridges/api-relay-audit` | CONDITIONAL | **INCOMPLETE** | Sole dependency declaration is `httpx>=0.24.0`, a range |
| `NadirRouter/NadirClaw` | **FAIL / LICENSE** | **NOT CREATED** | Licence. No profile is written for a candidate that may not run |

**3 complete · 4 incomplete · 1 not created.**

An INCOMPLETE profile is not a soft warning. **Attribute 2 is unsatisfied, so those four
candidates may not execute in LG4 as things stand.** The remedy is mechanical and is stated per
candidate below; it is work, not a decision.

---

## Decision 1 — `NadirRouter/NadirClaw`

**Accepted: LG2 FAIL stands. No commercial licence is purchased this round. No substitution.**

| | |
|---|---|
| Commit SHA | `63275a49f4e6542f1abf9d5a28be990c01064761` (tag `v0.23.1`) |
| Licence | PolyForm Noncommercial 1.0.0 |
| Status | **`FAILED / LICENSE`** |
| Failure reason | Commercial use in or by a for-profit business requires a separate commercial licence. ATK is a for-profit business running this benchmark to inform a commercial product. No amount of sandboxing fixes a licence. |
| Benchmark cells | **Retained and marked failed.** Not reassigned, not replaced. |
| Runtime profile | **Not created.** Writing an execution profile for code that may not be executed would be theatre. |

The 100-run matrix keeps its shape (frozen methodology §5: a cell that cannot execute is recorded
as a failed cell with a reason, never silently reallocated). H3 is tested by the remaining C4
tier-adjacent design, which never depended on NadirClaw.

**Recorded in:** `PINS.txt`, `EVIDENCE_LEDGER` E016, `reports/LAB_001_LG2_SECURITY_REVIEW.md`.

---

## Profiles

### `headroomlabs-ai/headroom` — Apache-2.0 — profile COMPLETE

| # | Attribute | Frozen value |
|---|---|---|
| 1 | Commit SHA | `32d7ca4577d599b8a5f811ada74cf31504302c9d` (tag `v0.37.0`) |
| 2 | Dependency version | `Cargo.lock` sha256 `dd2ac087ac71e3222c394c9df5778cf268b4211f33b57df14a7ba56bc70361a8` (134,161 B) · `uv.lock` sha256 `e2ae943529d378ff7d0bd0bba22352e542f34490358402ea550c6d84d9bbaf91` (1,508,725 B) · `pyproject.toml` sha256 `fbb7e23539cfb60a9afcc22bc9802fd2d6d5c1f24269a7ae82aa479801b2eaec` |
| 3 | Execution mode | Local CLI, built from source at the pinned SHA. **The documented install path is not used.** |
| 4 | Feature flags | `telemetry_enabled=false` explicitly, at every construction site — the code carries `telemetry_enabled=True` at two of them, so relying on "off by default" is relying on a claim the source contradicts |
| 5 | Network egress | Default-deny. Allowed: the model provider endpoint named in the run record. Nothing else. |
| 6 | External endpoint | `DEFAULT_ENDPOINT` in `headroom/telemetry/session.py` — **blocked by name at the sandbox**, in addition to the flag |
| 7 | Telemetry state | **Disabled by flag AND blocked by firewall.** Two independent controls, deliberately redundant |
| 8 | GPU / remote processing | Not applicable — no remote processing mode found |
| 9 | Local storage | Caches originals locally for reversibility. Cache directory forced inside the run sandbox; **wiped between runs**, so no run inherits another's cache |
| 10 | Credential scope | Benchmark-only provider key with a hard spend cap. Never a production key |

Surface note, not a blocker: 90 Python + 36 Rust dependencies and 31 subprocess sites, one with
`shell=True`. Large, but hygienic — three lockfiles present.

### `rtk-ai/rtk` — Apache-2.0 — profile COMPLETE

| # | Attribute | Frozen value |
|---|---|---|
| 1 | Commit SHA | `b1c0dc00649c50fbe8930f849c800d4d6ca12091` (tag `v0.49.0`) |
| 2 | Dependency version | `Cargo.lock` sha256 `e146f19c98b48ecee246ca20f079c8561818e689043cedf8af344c93b811115b` (49,304 B), 54 crates |
| 3 | Execution mode | **Built from source at the pinned SHA.** The documented installer (`INSTALL.md:47`, `README.md:80,392`) pipes `raw.githubusercontent.com/.../master/install.sh` into `sh` — a **moving branch**, so the installed artifact would not be the reviewed artifact. **Never used.** |
| 4 | Feature flags | Default feature set only. No optional feature is enabled for this round |
| 5 | Network egress | Default-deny. Provider endpoint only |
| 6 | External endpoint | None required. `raw.githubusercontent.com` is blocked to make the installer path impossible rather than merely discouraged |
| 7 | Telemetry state | No third-party analytics SDK found in 15 mentioning files. Egress denial covers the residual |
| 8 | GPU / remote processing | Not applicable |
| 9 | Local storage | Sandbox-local only; wiped between runs |
| 10 | Credential scope | Benchmark-only key. **No production shell environment** — it wraps and executes bash, so the shell it sees must contain nothing worth taking |

Its command-injection surface is **inherent to its function**, not a defect. Every wrapped
command is treated as untrusted input.

### `juyterman1000/entroly` — Apache-2.0 — profile COMPLETE

| # | Attribute | Frozen value |
|---|---|---|
| 1 | Commit SHA | `28e685f4c9793b26f7372c41c0ad0430f4e8e547` (tag `v1.0.3`) |
| 2 | Dependency version | `entroly-core/Cargo.lock` sha256 `8325336ad80e8d6f428ba8a57a8299ae80073bc82c5a96e475c292169ff7781f` (11,300 B) · `entroly-wasm/Cargo.lock` sha256 `2464ae65b53bfaa88f1c52122865970d3ef7fe225229138f737a1d9fcf1054d6` (7,807 B) · `pyproject.toml` sha256 `7bf196f1cf710abe23607dc89b7b2f6f02ac666c695e0f48713b2011edb02e26` |
| 3 | Execution mode | Local, built from source at the pinned SHA. **Core crate only; the wasm crate is not built or loaded** — it was read as source but never inspected as a binary artifact (LG2 scope limit) |
| 4 | Feature flags | Static analysis only. No notification or integration feature enabled |
| 5 | Network egress | Default-deny |
| 6 | External endpoint | `api.telegram.org` and `discord.gg` appear in the tree — **both blocked by name** |
| 7 | Telemetry state | None found. Egress denial covers the residual |
| 8 | GPU / remote processing | Not applicable |
| 9 | Local storage | Sandbox-local; wiped between runs |
| 10 | Credential scope | No provider credential required — it analyses code, it does not call a model |

The `evil.com` hit is a SAST unit-test fixture (`entroly-core/src/sast.rs:3092`,
`entroly-wasm/src/sast.rs:3086`) and was **verified benign**. Nine eval/exec sites are consistent
with a tool that parses code.

### `Paritok-official/paritok-4b-v1` — Apache-2.0 — profile INCOMPLETE

**Highest data-exposure risk of the eight.**

| # | Attribute | Frozen value |
|---|---|---|
| 1 | Commit SHA | `f95ac0f0e2c2214f11836db0bc66fdbdbf06452e` (tag `v1.3.12`) |
| 2 | Dependency version | **UNSATISFIED.** `requirements.txt` (sha256 `c5c10edcfcca5e7e64235f15055d379d41c6006758f3b3e35822b2655bb8991e`) declares **39 version ranges and zero exact pins** — `transformers>=4.45.0,<4.50.0`, `numpy>=1.24.0,<2.0.0`, and so on. Two installs a month apart get different code |
| 3 | Execution mode | **SELF-HOSTED MODE ONLY.** GPU-server mode is disabled for this round |
| 4 | Feature flags | GPU-server mode **off**. No `base_url` override permitted |
| 5 | Network egress | Default-deny |
| 6 | External endpoint | `paritok.com` and `www.paritok.com` **blocked by name.** In GPU-server mode `paritok/cli.py:15-20` and `config.py:29` POST **each segment** to `{base_url}/compress` — for a compression benchmark that would silently exfiltrate every task input |
| 7 | Telemetry state | Covered by the same block |
| 8 | GPU / remote processing | **Remote processing DISABLED.** Local inference only. Any run whose egress log shows either host is **void and re-opens LG2** |
| 9 | Local storage | Model weights and caches inside the sandbox; wiped between runs |
| 10 | Credential scope | **No Paritok API key is issued at all.** The absence of the credential is the third control, after the flag and the firewall |

**To complete:** install the pinned commit inside the sandbox, capture the resolved set
(`pip freeze`), commit it as `paritok.freeze.txt` with its hash, and re-run every run against
that freeze. Until then the candidate is not reproducible and must not execute in LG4.

### `yvgude/lean-ctx` — Apache-2.0 — profile INCOMPLETE

| # | Attribute | Frozen value |
|---|---|---|
| 1 | Commit SHA | `79fe3cf59f3309fa9fb39b9def2f2db0b1d8f8f1` (tag `vscode-v0.2.0`) |
| 2 | Dependency version | Available but **ambiguous** — see attribute 3. Core engine: `rust/Cargo.lock` sha256 `d7342d2f0516cad797ea96d82ff30a1c22d418703899d119e3f79c47ee890ba1` (169,662 B) · Python client `packages/python-lean-ctx/pyproject.toml` sha256 `07e3223f31b4726ef27672152da36f027acb3cc99b4e302713d251b681ff896b` · Node client `packages/node-lean-ctx/package-lock.json` sha256 `280d764e9df5bb8505fce1ce5268893c568473cc85d95bd1f5c3783613360fdc` |
| 3 | Execution mode | **UNRESOLVED — this is the blocking gap.** The repository is a monorepo of roughly 20 packages, and the pinned tag `vscode-v0.2.0` names a **VS Code extension release**, not the core library. The commit is valid and the tree is intact; what is undecided is *which artifact is the candidate*. LG2 flagged this and it is still open |
| 4 | Feature flags | Cannot be frozen before attribute 3 is answered |
| 5 | Network egress | Default-deny |
| 6 | External endpoint | `leanctx.com` **blocked by name.** The documented installer is `curl -fsSL https://leanctx.com/install.sh \| sh` (`README.md:197`, `.claude-plugin/manifest.json:9`) — a vendor-controlled domain, so the installed artifact would not be the reviewed artifact. **Build from the pinned SHA instead** |
| 7 | Telemetry state | Cannot be frozen before attribute 3 |
| 8 | GPU / remote processing | None found |
| 9 | Local storage | 22 config-write sites. All writes confined to the sandbox; wiped between runs |
| 10 | Credential scope | 25 credential-handling sites. Benchmark-only key, hard spend cap |

**To complete:** the Editor-in-Chief decides which package is under test — most plausibly
`rust/` (the core engine), since that is what a context-optimisation claim would rest on. Then
re-pin to a tag that names *that* component, and freeze attributes 3, 4 and 7 against it.
**Correction to an earlier reading in this round:** a first pass probed only the repository root,
found no manifest, and concluded the dependency version could not be pinned at all. That was
wrong — the manifests are one level down. The real problem is ambiguity about which one, not
absence.

### `toby-bridges/api-relay-audit` — AGPL-3.0 — profile INCOMPLETE

| # | Attribute | Frozen value |
|---|---|---|
| 1 | Commit SHA | `571b97142c0d22aae305ac2919e45137bc424dcc` (tag `v2.4.0`) |
| 2 | Dependency version | **UNSATISFIED.** The entire dependency declaration is a 14-byte `requirements.txt` reading `httpx>=0.24.0` — a range, with no lockfile anywhere in the tree |
| 3 | Execution mode | **Unmodified.** Any modification triggers the AGPL network-copyleft obligation if ATK ever hosts it as a service |
| 4 | Feature flags | Capture only. No forwarding, no re-writing of intercepted traffic |
| 5 | Network egress | Default-deny. It is an interceptor: it sits between ATK and the provider and needs no egress of its own |
| 6 | External endpoint | None permitted |
| 7 | Telemetry state | None found |
| 8 | GPU / remote processing | Not applicable |
| 9 | Local storage | **Captured traffic never leaves the sandbox.** It sees prompts, responses and keys in cleartext by design — the capture directory is wiped between runs and never committed |
| 10 | Credential scope | **Benchmark keys only, never production.** Non-negotiable: this tool's whole function is to read what passes through |

Provenance note worth carrying: `FOR_JOHN.md:594` records that its detection logic was **ported
from `hvoy.ai`** — third-party code inside a security tool, which is exactly where provenance
matters most.

**To complete:** capture a `pip freeze` inside the sandbox and commit it as
`api-relay-audit.freeze.txt` with its hash.

### `crwdla/tokentab` — MIT — profile INCOMPLETE

The only unconditional LG2 pass, and still not runnable under Decision 2.

| # | Attribute | Frozen value |
|---|---|---|
| 1 | Commit SHA | `d9e8cb405642d368d2f6a19147cc7f3088e3d886` (**no tag** — pinned at a HEAD commit, reproducible but with no release boundary) |
| 2 | Dependency version | **UNSATISFIED.** `pyproject.toml` (sha256 `6c7c3888b03ef6a076af07ef9a421bdbebd3a1ddc0153e798ae84183b89303f8`) declares one dependency, `rich>=13.0` — a range. No lockfile |
| 3 | Execution mode | Local CLI, offline. No installer, no postinstall |
| 4 | Feature flags | CLI only. The bundled web dashboard is **not started** — it is a listening service the benchmark does not need |
| 5 | Network egress | Default-deny. **The scan found zero outbound hosts in source** |
| 6 | External endpoint | None |
| 7 | Telemetry state | None found |
| 8 | GPU / remote processing | Not applicable |
| 9 | Local storage | Reads agent session logs. **Pointed only at benchmark logs, never production transcripts** — its real risk is inbound, not outbound: session logs can contain secrets and customer data, and although there is no egress path in the code, the exposure is created by what it is allowed to read |
| 10 | Credential scope | None required |

**To complete:** freeze `rich` to an exact version with a hash, the same way the harness lock
does it.

---

## Cross-cutting controls, applied to every candidate

| Control | Implementation |
|---|---|
| Egress | Default-deny at the sandbox. The container self-check fails the run if any of four probe destinations is reachable (`harness/selfcheck.py`, check 5) |
| Install path | **Never a vendor installer.** Four candidates document `curl \| sh` or a moving branch; all four are built from the pinned SHA instead |
| Credentials | Benchmark-scoped key with a hard spend cap, supplied only as `LAB001_BENCHMARK_API_KEY`. `harness/providers.py` **refuses to start** if an ambient production key is present instead |
| Storage | Every candidate writes inside the sandbox only, and the sandbox is wiped between runs |
| Telemetry | Off by flag **and** blocked by firewall wherever an endpoint exists in source |
| Verification | Each run record carries `candidate_commit_sha` and `egress_destinations`; an undeclared destination voids the run and re-opens LG2 |

## What this document does not do

- **It does not clear any candidate to run.** Four profiles are incomplete and those candidates
  are blocked until attribute 2 (and, for lean-ctx, attribute 3) is satisfied.
- **It does not re-open LG2.** The verdicts stand exactly as reviewed.
- **It does not rest on execution.** No candidate has been installed, built or run. These
  profiles are built from source read at the pinned commit and from lockfiles fetched at that
  commit — which is also why the dependency gaps could be found at all.

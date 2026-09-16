# Lab 001 — Execution Readiness Review

**Date:** 2026-09-16 · **Gate sequence executed:** LG1 → LG2 → LG3 → Readiness
**100-run benchmark: NOT started.** LG4 not entered.

---

## Recommendation

# ❌ NO GO

**LG3 FAILED.** The environment is fully specified but **could not be verified reproducible** —
the container image was never built because no container daemon is reachable in this runtime.

The frozen methodology's own stop conditions (v1.0.0, §"Declared stop conditions") list *"the
environment cannot be pinned by digest"* as a halt. The gate is not waived, not worked around,
and not downgraded to a condition. It failed, and that is recorded.

**This is a runtime-capability failure, not a design failure.** Everything else is ready. One
capability unblocks it.

---

## 1. LG1 — Methodology frozen?

**YES. FROZEN.**

| | |
|---|---|
| Version | **1.0.0** |
| Document | `benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_v1.0.0.md` |
| SHA-256 | `c1810b0481d1442937771c124c7c30668490470f00dcf71098bdf139ee7089bc` |
| Size | 8,139 bytes |
| Lock | `methodology/METHODOLOGY_LOCK.json` |
| Companion | `methodology/METER_CALIBRATION_v1.0.0.md`, SHA-256 `3ed9dac6…` |

All 12 required items frozen: research question · H1–H4 · workloads A–E · conditions C0–C5 ·
100-run matrix · quality floors · C4 tier-adjacent routing · meter calibration · cache control ·
reproduction plan · pricing snapshot requirement · evidence manifest.

**Amendment policy:** immutable. A change requires a **new version file**; never an overwrite.
Runs stay attributed to the version they executed under.

## 2. LG2 — Security review of 8 candidates

**1 PASS · 6 CONDITIONAL PASS · 1 FAIL.** Full evidence: `reports/LAB_001_LG2_SECURITY_REVIEW.md`.

| Verdict | Candidate | Reason |
|---|---|---|
| **PASS** | `tokentab` | MIT. **Zero external hosts in source.** 12 deps, 24 files, no installer, no telemetry |
| **FAIL** | `NadirClaw` | **PolyForm Noncommercial 1.0.0** — *"COMMERCIAL use... by a for-profit business... requires a separate commercial license"* |
| CONDITIONAL | `headroom` | Telemetry off by default, but a `DEFAULT_ENDPOINT` ships. Disable **and** block the host |
| CONDITIONAL | `rtk` | Documented installer pipes from the **`master`** branch. Build from the pinned commit only |
| CONDITIONAL | `paritok-4b-v1` | GPU mode **POSTs each segment to `paritok.com/api/compress`**. Self-hosted only; host blocked by name |
| CONDITIONAL | `lean-ctx` | Installer is `curl leanctx.com/install.sh \| sh`. Build from pinned SHA; resolve the VS Code tag ambiguity |
| CONDITIONAL | `entroly` | `evil.com` **verified benign** (SAST test fixture). Block `api.telegram.org`, `discord.gg` |
| CONDITIONAL | `api-relay-audit` | **AGPL-3.0** + it intercepts ATK's own traffic. Unmodified, benchmark keys only |

**NadirClaw's cells are marked `FAILED / SECURITY`. No substitute candidate was introduced and
no run was reassigned** — the matrix keeps its shape. H3 is still tested by the C4 tier-adjacent
design, which never depended on NadirClaw.

**A security PASS is not a product-quality VERIFIED.** It authorises execution under conditions;
it says nothing about whether any tool works.

## 3. LG3 — Environment reproducible from zero?

**NO. LG3 FAIL.**

| Component | Status |
|---|---|
| Candidate pins | ✅ **PASS** — all 8 cloned, HEAD compared to pin. **2 defects found and fixed** |
| Harness dependency layer | ✅ PASS — installed cleanly in a clean venv |
| Run-record schema | ✅ PASS — valid Draft 2020-12; rejects `methodology_version != 1.0.0` |
| Dockerfile, egress policy, pins, lockfile | ✅ Written |
| **Container image built** | ❌ **FAIL** — no daemon at `/var/run/docker.sock` |
| **Container digest** | ❌ **None exists** |
| **Second-seat rebuild demonstrated** | ❌ **Not demonstrated** |

**The pin defect is worth stating on its own (E017).** Two of eight pins recorded **tag-object
SHAs, not commit SHAs** (`paritok-4b-v1`, `lean-ctx`). Both were fetchable, so the error was
invisible until a clone was diffed against the pin. Annotated tags must be dereferenced with
`^{}`. **Had LG3 been waved through, two of eight candidates would have run at an unverified
revision.** The gate did its job.

## 4. Measurement — can the Token Meter be trusted?

**Not yet — and the design now says so explicitly.**

`bytes / 4` and every other uncalibrated estimator are **PROHIBITED as ground truth**. The
provider-native `usage` field is ground truth; the ATK meter is validated against it at ≤1%
relative error on input, output and total tokens, over 6 dedicated calibration runs.

**Cross-provider token deltas are not reportable at all** — different tokenizers, and no
calibration fixes that. Cross-provider comparison is permitted only on **cost** and **cost per
successful task**, with the pairing and `pricing_snapshot_id` attached.

Trust status: **design complete, calibration not run.**

## 5. Quality — do answer keys and the Quality Judge actually work?

**No. This is the second-largest gap after LG3.**

Quality floors are frozen and pre-registered (5 workloads, with zero-tolerance criteria). But:

- **The task set does not exist.** `tasks/` is empty.
- **No answer key has been written**, so the ≥97% exact-match floor for workload B has nothing
  to match against.
- **The Quality Judge has never scored anything.** Its independence is enforced structurally
  (`SEAT_REGISTRY.json` invariant I5, owns LG5, cannot alter token measurements, scores before
  seeing cost) — but structure is not evidence that the scoring works.

Floors defined ≠ floors applied.

## 6. Cost — estimated spend for 100 runs

**$51 – $94, point estimate ≈ $73** at `PS-2026-09-15`.

Derived from the frozen matrix, not guessed:

| Workload | Runs | Assumed tokens/run | Cost |
|---|--:|---|--:|
| A repo analysis | 18 | 80k in / 15k out | $15.30 |
| B long-doc | 21 | 30k / 5k | $6.30 |
| C multi-source | 9 | 30k / 5k | $2.70 |
| D MCP-heavy | 18 | 80k / 15k | $15.30 |
| E long multi-turn | 12 | 250k / 30k | $25.80 |
| Overhead (10 repro + 6 cache + 6 calib) | 22 | medium | $18.70 |
| C4 cheap-side relief | — | — | −$11.51 |
| | | **Point** | **$72.59** |
| | | +30% retry/escalation | $94.36 |

**Assumption that dominates the estimate:** tokens per run. Those numbers are **estimated, not
measured**, and cannot be tightened until the task set exists (§5). Bounds: $8 if everything ran
on the cheap tier; **$505 if everything ran at pro-tier $30/$180** — which the frozen C4 design
deliberately avoids (methodology §7).

Spend is not the constraint here. **$73 is cheap relative to the decision it informs.**

## 7. Time — estimated duration

**8–16 hours of wall clock for execution**, at 60–180 s per agentic run for 100 runs, plus
retries and the 22 overhead runs.

**Total to a published result: 3–5 working days**, dominated not by execution but by the two
things that do not exist yet — building the task set with answer keys, and clearing LG3.

## 8. Three largest experiment risks

1. **The task set does not exist, and it is the hardest artifact to build well.** Answer keys
   determine every quality floor. A weak key produces confident numbers about nothing. This is
   larger than LG3 because LG3 is a capability problem with a known fix, and this is a design
   problem with no shortcut.
2. **Six of eight candidates carry binding conditions, each an egress or build discipline.** One
   slip — a vendor installer used for convenience, one unblocked telemetry host — and the run is
   void under the frozen stop conditions. `paritok` is sharpest: its GPU mode transmits prompt
   content to the vendor, so a misconfiguration exfiltrates every task input.
3. **Conflict of interest.** `rtk` and `headroom` are Lab subjects *and* ATK integration
   candidates. The frozen methodology's mitigations are real, but the strongest one is
   procedural: **a favourable result for an ATK candidate is the first to reproduce, not the
   first to publish.**

## 9. Evidence produced this round

| State | Count | Items |
|---|--:|---|
| **REPORTED** | 0 new | — |
| **OBSERVED** | 5 new | E005 (routing-stack layer analysis), E016 (NadirClaw licence), E017 (pin defect), E018 (paritok egress), plus 8 candidate security profiles |
| **TESTED** | **0** | **No candidate was executed** |
| **VERIFIED** | **0** | Nothing reached acceptance criteria |
| **REPRODUCED** | **0** | — |

One upgrade: **E005 REPORTED → OBSERVED.**

## 10. Counterevidence

**Against H002 — the original inference is not supported.** E005's *evidence* was right
(routing is free at both vendors), but the *inference* built on it — "vendors are commoditising
the layer ATK sells, so the wedge narrows" — does not survive primary sources. They commoditised
routing. They **meter** measurement, attribution, governance and export. Vercel charges **$5 per
1,000 queries** to ask what a request cost and who incurred it.

**Note carefully what this does not do.** It does not establish H002, and it is not
willingness-to-pay evidence: a price list shows what a vendor charges, not what a market pays.
**H002 stays at H1 Signal.** No hypothesis confidence was changed by this round.

**Against H001 — unchanged and still unresolved.** Neither vendor offers verification at all.
That reads as an opening or as a feature nobody wants, and this round cannot tell which. Same
open question as `RESEARCH_REPORT.md` §6.2; only a usage or willingness-to-pay test settles it
(D007).

**Against Lab H1–H4 — none.** No experiment ran.

**Against ATK's own process — yes, twice.** Two of eight pins were wrong (E017), and a candidate
licence had gone unverified until a clone was read (E016). Both were caught by the gates, which
is the gates working; both were also avoidable, which is the process not yet being tight.

## 11. Recommendation

# NO GO

**Blocking:** LG3 FAIL — the environment cannot be demonstrated reproducible.
**Also incomplete:** no task set, no answer keys, meter never calibrated.

### Shortest path to GO

| # | Action | Clears |
|---|---|---|
| 1 | Provide a runtime with a working container daemon; build `environment/Dockerfile`; record the digest | **LG3** |
| 2 | Have a second seat rebuild from this repository alone and match the digest | **LG3** |
| 3 | Build the task set with frozen answer keys for A–E | §5 |
| 4 | Run the 6 meter-calibration runs; confirm ≤1% | §4 |
| 5 | Decide on NadirClaw: accept the FAIL, or purchase a commercial licence | LG2 |

Items 1–2 are a capability decision. **Item 3 is the real work.**

**Do not start LG4 until LG3 passes.** A benchmark whose environment cannot be rebuilt produces
numbers nobody can challenge — which, by the doctrine's own standard, makes them worthless.

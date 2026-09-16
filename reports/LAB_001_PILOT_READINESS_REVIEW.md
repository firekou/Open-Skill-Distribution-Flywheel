# Lab 001 — Pilot Readiness Review

**Date:** 2026-09-16 · **Round objective:** clear the NO GO blockers and establish whether the
benchmark infrastructure is itself trustworthy
**Preceded by:** `LAB_001_EXECUTION_READINESS.md` (NO GO, LG3 FAIL)

---

## Summary

The round's actual question was *"can this infrastructure be trusted?"* The infrastructure
answered by **catching its own defects**: 47 of them, found by four independent seats and by
running the harness for the first time. That is the result worth reporting. A benchmark stack
that fails closed on first contact with real data is worth more than one that runs green because
nothing has tested it.

LG3 is recovered. The task set exists and is good. The meter's arithmetic is proven. And LG4
still cannot start.

# Verdict: **NO GO** for the LG4 100-run benchmark

Not the same NO GO as last round. The previous blocker — an environment that could not be
demonstrated reproducible — is cleared and verified. Three new blockers took its place, and all
three were found by doing the work rather than by inspecting it.

---

## The thirteen questions

| # | Question | Answer |
|---|---|---|
| 1 | LG3 final verdict | **PASS** |
| 2 | Task set frozen | **NO** — see §2 |
| 3 | Answer key frozen | **NO** — blocked on the same defects |
| 4 | Conditional candidates' final runtime restriction | **Frozen for 3 of 7; 4 are BLOCKED** |
| 5 | Meter calibration | **FAIL — not executed as specified** |
| 6 | Pilot runs completed | **0** — the gate did not open |
| 7 | Pilot failures | **0 pilot runs, so 0 pilot failures.** A 10-run harness dry run stands in its place: 10/10 after two defects were fixed |
| 8 | Blind evaluation successful | **YES**, mechanically verified in both directions |
| 9 | Reproduction successful | See §9 |
| 10 | Raw evidence complete | **YES** — 10 of 10 manifests verify, tampering detected |
| 11 | New methodology problems found | **YES — three** |
| 12 | Methodology v1.1.0 needed | **YES** — `METHODOLOGY_CHANGE_REQUEST_001.md` raised, nothing changed |
| 13 | May LG4 start | **NO** |

---

## 1. LG3 — PASS

| | |
|---|---|
| Image manifest digest | `sha256:6edd71a6adff7eab4fca99b9b8fb2e9298c62256f5587ee9109cf02047811261` |
| Clean rebuild | Manifest, config, blob set, dependency manifest and runtime all match after a full prune and base re-pull |
| Self-check | 8 of 8, with a negative control that fails when egress is allowed |

The previous round recorded LG3 FAIL with the reason *"no docker daemon in this environment."*
**That reason was wrong.** The daemon binaries were present; the daemon had not been started. The
FAIL verdict was right — LG3 genuinely had not been demonstrated — but an inaccurate reason sends
the next round looking for a new machine instead of starting a service.

Three defects in the v1 environment spec, none visible until it was built:

- **E019** — the lock pinned 3 of 16 distributions; 13 transitive dependencies would drift.
- **E020** — `pip install --require-hashes … || pip install …`: the fallback silently defeated
  hash verification. The check was decorative.
- **E021** — install-time bytecode compilation embedded the build's wall clock in `.pyc` headers.
  Ten of eleven layers were byte-identical; one differed by 8 bytes across 783 identically-named
  files. Traced to one byte at offset 8 of the `.pyc` header: `source_mtime` 09:57:27 vs
  09:58:01. Bodies identical.

Detail: `LAB_001_LG3_BUILD_EVIDENCE.md`.

## 5. Meter calibration — FAIL

Two questions, and only one of them is answerable without a credential.

**Accumulator correctness: PASS.** 6 cases, 72 checks, zero mismatches, run in the locked
container with `--network none`. The cases are adversarial by construction: a meter recording
only the accepted call undercounts CAL-002 by **65%**; one pricing cached tokens at the uncached
rate overstates CAL-003 by **5.41×**. Every expected value was computed by explicit arithmetic in
the fixture generator, never by running the meter.

**Meter versus provider-native usage: BLOCKED.** No benchmark credential exists, so no
provider-native `usage` field can be obtained for any request. This is a **declared stop
condition** in the frozen methodology, and the instruction attached to it is to record the
failure rather than improvise around it.

The spec defines calibration as the second question. **Phase E is therefore FAIL**, and reporting
the accumulator PASS as "meter calibration passed" would have been the single most consequential
dishonesty available this round.

Also measured rather than asserted: the prohibited `bytes/4` estimator's error ranges from 13.6%
to 61.0% across content types on the fixture, and **changes sign**. No calibration factor fixes an
estimator whose error depends on the input. (The reference counts there are synthetic; only the
structural claim carries, never the percentages.)

## 6–7. The Pilot gate stayed closed

The gate requires four things: LG3 PASS · task set frozen · answer key frozen · **meter
calibration PASS**. Two of four hold. **No Calibration Pilot run was executed.**

In its place, the harness was run end to end against a seeded-PRNG replay fixture — no model, no
provider, no credential, no cost — with every record marked `run_class: "dry_run"`.
`harness/runner.py` **refuses** to write a `benchmark` or `pilot` record from a synthetic fixture;
the guard is in the code path, not in a README.

10 planned, 10 completed — **after the dry run broke twice on real data**:

- **E026** — 12 of 15 rates in `PS-2026-09-15` carry **no cached input rate**: every OpenAI and
  every Anthropic model. The meter refused to price a cached call rather than folding cached
  tokens in at the full rate. Correct behaviour, real blocker: any warm-cache run on those
  providers cannot be priced today, which removes most of C2 and C3 in long sessions.
- **E027** — the blind checker failed a legitimate packet, because answer key D-002 mirrors an
  offline tool's argument schema whose argument is named `repository`. A false positive, so it
  failed safe — but it would have blocked every workload-D run, and it was invisible until the
  checker met real data.

What the dry run verified: schema-valid records, complete raw evidence with verifying manifests,
correctly blinded packets, recorded failures rather than skipped ones, determinable cache state,
the right pricing snapshot, and a full evidence manifest per record.

What it establishes about token optimisation: **nothing.** The token counts come from a
pseudo-random number generator seeded on the task id.

## 8. Blind evaluation — verified

The Quality Judge sees nine fields and nothing else. Enforcement is machine-checked, and was
tested in both directions rather than asserted:

| Probe | Result |
|---|---|
| `cost` nested three levels deep | caught |
| `condition` inside a list element | caught |
| `input_tokens` at top level | caught |
| A candidate name in the model output body | caught |
| A clean packet | passes |
| Un-blinding with one packet unscored | refused |
| Un-blinding before scoring is declared complete | refused |

Labels are scrambled by salted digest, not assigned in condition order: in the dry run, C2 is
Treatment A and C0 is Treatment B. The Quality Judge additionally copies only the nine allowed
keys into its scoring view, so a leaked field cannot change a score even if `assert_blind` missed
it — proven by a test in which a packet carrying `condition: C5`, `total_tokens`, `cost_usd` and
a model name scores identically to the clean one.

## 10. Raw evidence — complete

Ten evidence directories, each with a `MANIFEST.json` of per-file hashes. All ten verify. The
self-check confirms the manifest **detects** a single appended space in a raw file, so the check
discriminates.

Every record carries the full evidence manifest: container digest, task set hash, answer key
hash, prompt hash, config hash, pricing snapshot id, raw evidence path. `candidate_commit_sha` is
absent, correctly — no candidate participated.

## 11–12. Three methodology problems

Raised as `methodology/METHODOLOGY_CHANGE_REQUEST_001.md`. **The frozen methodology has not been
edited.**

- **CR-001-A (BLOCKING)** — §6's floors for A and C are relative to a C0 baseline median. A blind
  judge cannot compute it (knowing which runs are C0 *is* knowing the treatment), and the floor
  contains a perverse incentive: a low baseline lowers the bar. Affects 7 of 17 tasks. Found
  independently by two seats that never conferred.
- **CR-001-B (MAJOR)** — §6 does not say whether a threshold is per packet or per cell. Read one
  way, workload D is thresholded twice.
- **CR-001-C (BLOCKING)** — §11 requires a pricing snapshot but not a complete one, while §9
  requires cache state on every record. E026 is the consequence.

None was found by looking at a result and wishing the rule were different. No result exists.

## 4. Candidate runtime restrictions

`environment/CANDIDATE_RUNTIME_PROFILES.md` freezes ten attributes per candidate.

| | |
|---|---|
| **Complete** | `headroom`, `rtk`, `entroly` |
| **Incomplete — may not execute** | `paritok` (39 ranges, 0 pins), `api-relay-audit` (`httpx>=0.24.0` and nothing else), `tokentab` (`rich>=13.0`), `lean-ctx` (lockfiles exist but the pinned tag names a VS Code extension in a ~20-package monorepo) |
| **Not created** | `NadirClaw` — no execution profile is written for code that may not be executed |

Decision 1 stands: NadirClaw's cells are marked `FAILED / LICENSE`, the failure reason is kept,
no substitute is introduced, no licence purchased.

For the three incomplete-on-dependencies candidates the remedy is mechanical — install at the
pinned commit inside the sandbox, capture the freeze, commit it with its hash. For `lean-ctx` it
is a decision: which package is the candidate.

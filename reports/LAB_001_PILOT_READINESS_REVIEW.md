# Lab 001 — Pilot Readiness Review

**Date:** 2026-09-16 · **Round objective:** clear the NO GO blockers and establish whether the
benchmark infrastructure is itself trustworthy
**Preceded by:** `LAB_001_EXECUTION_READINESS.md` (NO GO, LG3 FAIL)

---

## Summary

The round's actual question was *"can this infrastructure be trusted?"* The infrastructure
answered by **catching its own defects**:

| Source | Findings |
|---|---|
| Building the environment for the first time | 3 (E019–E021) |
| Running the harness for the first time | 2 (E026–E027) |
| Independent reproduction by a separate seat | 7 would-invalidate (E029–E033 and two now closed) |
| Answer Key Builder, against work it did not author | 11 |
| Quality Judge, on metrics it had to score | 33 underspecified |
| Task Red Team, against all three | 4 blocking · 9 major · 8 minor |

The categories overlap — the Red Team confirmed and escalated several of the Builder's and the
Judge's — so these do not sum to a meaningful total. What matters is that **every one of them was
found by building the thing and running it**, not by reading it. A benchmark stack that fails
closed on first contact with real data is worth more than one that runs green because nothing has
tested it.

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

## 2–3. Task set and answer key — NOT frozen

The Task Red Team's verdict, in its own words: **"NOT fit to freeze — but it is close, and the
work is good."**

It was able to confirm a great deal by running things rather than reading them: 17 of 17 answer
keys reproduce **byte-identically** from their committed derivation scripts, all 155 manifest
entries verify before and after review, 100 judge tests pass, the workload-D tool server
reproduces every keyed answer through live invocations, and **15 of 17 tasks resist the cheap
strategy**.

Four items block the freeze.

| | Finding | Why it blocks |
|---|---|---|
| **RT-01** | `required_evidence` is produced by nothing. `build_packet` reads `task.get("required_evidence", [])` and no task file has that key | **10 of 17 byte-perfect answers fail today** — A×4 and D×4 at score 0.0. It was nobody's declared deliverable, which is exactly why it fell between seats. This is a defect in **our harness**, and the dry run reproduced it live: every workload-D packet failed `required_evidence_missing:tool_calls` |
| **RT-02** | The workload-E zero-tolerance criterion **fails OPEN** | Fail-closed holds for *absent* evidence but not for *present-but-empty*. With `{"shifts":{},"roster":{}}` a run assigning an ineligible person scores `task_success: true`. And `part_id_pattern` is a runner-supplied regex: the plausible anchored form `^KP-\d{4}$` silently disarms two violation classes while `KP-\d{4}` fires correctly. **Same packet, opposite verdict.** A zero-tolerance criterion that can be switched off unnoticed is worse than none, because it produces a confident pass |
| **RT-03** | **B-002 rewards discarding 86% of its document** | Its two required appendices sit at bytes 127,608 and 131,705 of 146,666 — both in the last 13%, 4 KB apart, not the "~120 KB apart" its own notes claim. The preceding 86% is narrative the task forbids using, so a compaction or filtering condition that throws it away scores **identically to baseline at a fraction of the tokens**. This is the single finding most likely to produce a *wrong published result* rather than a failed measurement |
| **RT-04** | C-001's traceability fails a citation the task text expressly permits | Two forum threads state the *correct* value and the key records this itself. A compliant run takes an outright zero-tolerance failure at `quality_score 1.0`, in a direction that only ever penalises broader retrieval |

**RT-03 and RT-04 point the same way: both would have manufactured a win for aggressive context
reduction.** The designer's isolation from candidate identity was genuine and verified — the bias
is accidental and content-shaped, not candidate-shaped. It is recorded as **E034**, and it is the
finding that most justifies this round having happened. Had the benchmark run, it would have
reported a real-looking result in favour of exactly the interventions ATK is predisposed to
believe in.

The Red Team is explicit that this is not a reflexive block: the set is **fit to freeze once the
four are closed and re-verified**, with the C0-ordering dependency written into the run plan. The
minor findings belong in a `TASK_SET_v1.1.0` and should not hold the freeze.

Because the task set is not frozen, **the answer key is not frozen either** — several of the four
blockers change what a key must contain. Both currently hash to:

| | |
|---|---|
| Task set hash | `7fbca09980cc74d252280674b6ae18c3b5f3b1addd3994c1716e8138cd4c1553` |
| Answer key hash | `03ea884c74bb866df824dd68151eb239c2f8fd57609f486fb230a4c5bb9564c7` |
| Corpus manifest | `9bc84e9f1307175a3d83f111ded05aa03eb15acd18baca0571e0fe36de0e3105` (155 files, all verify) |

These are recorded so a later freeze can be diffed against them. **They are not a freeze.**

## 9. Reproduction — the run reproduces; the attestation around it did not

An independent seat rebuilt the container from the repository, re-ran all 10 dry-run records and
re-scored them.

**What matched, on all 10:** `model_output` byte-identical · `input_tokens`, `output_tokens`,
`total_tokens`, `cost` identical · all 11 judge score files byte-identical · `task_set_hash`,
`answer_key_hash`, `prompt_hash`, `config_hash` identical · the blind mapping byte-identical ·
every judge packet byte-identical. Its own two builds from a clean checkout produced the same
digest.

**The harness, the scorer and the build are deterministic.** That is the answer to the question
Phase G asks.

**What did not reproduce was the attestation around the run** — seven would-invalidate
differences, five of which have been fixed and re-verified this round:

| | Finding | Status |
|---|---|---|
| **E030** | `container_digest` was an operator-supplied string nothing verified. All 10 records named an image that **provably could not produce them**: re-running the same command inside it gives 9 completed, not 10, because it carries a pre-E027 `blind.py` and no `judge.py` | **Fixed** — every record now also carries `image_content_sha256` and `dependency_manifest_sha256`, computed **inside** the running container, which a flag cannot forge |
| **E031** | `written_at` was written inside `raw.json` and then `raw.json` was hashed, so evidence hashes could never match across runs *by construction* | **Fixed** — volatile metadata moved to the manifest. Verified: **10 of 10 evidence hashes and 10 of 10 judge packets now identical** across two independent executions |
| **E032** | Blind labels were batch-scoped: the same salt gave `C0 = Treatment B` in the 10-run plan and `C0 = Treatment A` in a 2-run subset. Since the Reproduction Agent repeats *the strongest results*, not everything, a correct partial reproduction would have looked like an invalidation | **Fixed** — labels assigned over the canonical condition set; verified stable across full, 2-run and 1-run plans |
| **E033** | Blind protocol step 4 was implemented nowhere. No code wrote scores back into a record; all 10 kept placeholders. Invisible in a synthetic dry run because every genuine score is also 0.0 — **in a real run every record would have silently reported a scored failure** | **Fixed** — `harness/finalize.py`, which refuses to finalize a batch containing any unscored packet or any record without a score |
| **E029** | A working-tree build differed from a clean-checkout build. The first `.dockerignore` did nothing: docker ignore patterns match relative to the context root, so `__pycache__/` misses `harness/__pycache__/` | **Fixed** — `**/`-prefixed patterns; a contaminated tree and a clean tree now produce the same digest and the image contains zero `.pyc` |
| — | `ENVIRONMENT_LOCK.json` was stale (locked 11 layers against a Dockerfile now producing 13) | **Fixed** — re-derived from the final image, with the superseded digests recorded and explained rather than deleted |
| — | `dependency_manifest_sha256` was computed by no code and documented by no recipe; six plausible derivations were tried and none matched | **Fixed** — the recipe is now `harness/attest.py:dependency_manifest_hash` |

The seat also flagged that **the `docker run` invocation existed nowhere in the repository** — it
reverse-engineered the mount layout from a path inside a record — and that the blind salt is not
in the repository, so the mapping row is not independently executable. Both are real: a procedure
only its author can follow is not a reproduction procedure. Neither is fixed this round.

Detail: `LAB_001_REPRODUCTION_RESULT.md`.

---

## What changed since the last review, and what did not

| | Last round | Now |
|---|---|---|
| LG3 | FAIL, on an inaccurate reason | **PASS**, digest reproduces from an empty store |
| Task set | Did not exist | **17 tasks, 1.03 MB of synthetic corpora, built and attacked** |
| Answer keys | Did not exist | **17, all re-derivable byte-identically from committed scripts** |
| Meter | Never run | **Accumulator proven over adversarial cases; provider comparison still blocked** |
| Harness | Did not exist | **Runs, scores blind, finalizes, reproduces** |
| Candidates | 6 conditional | **3 profiles complete, 4 blocked on dependency pinning** |
| Verdict | NO GO | **NO GO** |

The verdict is the same word and a different situation. Last round's blocker was an environment
nobody had built. This round's blockers are four task defects, a credential that has not been
issued, and a pricing snapshot that cannot price a cached call — all of them specific, all of
them found by running the thing, and none of them requiring new research to fix.

## What must happen before LG4

| # | Action | Clears | Whose call |
|---|---|---|---|
| 1 | Provision a lab-scoped, spend-limited benchmark credential as `LAB001_BENCHMARK_API_KEY` | Meter calibration; the Pilot gate | **Editor-in-Chief** |
| 2 | Close RT-01 — give `required_evidence` an owner, a deterministic treatment-neutral producer, and a pre-judge assertion that it is present and non-empty | 10 of 17 tasks | Task set + harness seats |
| 3 | Close RT-02 — make the workload-E zero-tolerance criterion fail closed on empty evidence and on an unusable pattern | The E criterion | Quality Judge |
| 4 | Close RT-03 and RT-04 — remove the two accidental biases, or exclude those tasks from H2/H4 | **The credibility of any H2/H4 result** | Task Set Designer, then Red Team re-verify |
| 5 | Complete the pricing snapshot's cached input rates from the vendor pages | C2 and C3 costing | Any seat; it is a fetch |
| 6 | Rule on `METHODOLOGY_CHANGE_REQUEST_001` | The relative floors, the per-packet/per-cell ambiguity, snapshot completeness | **Editor-in-Chief** |
| 7 | Complete four candidate runtime profiles: capture a dependency freeze for `paritok`, `api-relay-audit` and `tokentab`; decide which `lean-ctx` package is under test | 4 of 7 candidates | Mechanical, except `lean-ctx` |
| 8 | Commit the run invocation and document the salt custody | Reproduction procedure | Harness seat |

Items 1 and 6 are decisions. Items 2–5, 7 and 8 are work.

## What this round did not do

- **No benchmark run, no pilot run, no candidate executed.** Ten dry-run records exist, produced
  from a pseudo-random number generator, and `runner.py` refuses to write a `benchmark` or
  `pilot` record from a synthetic fixture.
- **No hypothesis confidence was raised.** H001–H010 and H1–H4 are exactly where the last review
  left them.
- **No candidate was substituted, forked, or integrated.** NadirClaw's cells remain marked
  `FAILED / LICENSE`.
- **The frozen methodology was not edited**, and will not be. Three problems were found in it;
  all three are in a change request awaiting review.
- **Nothing was marked VERIFIED or REPRODUCED.** Fifteen entries are now TESTED, every one of
  them about ATK's own harness and environment. **E022 meets the written bar for VERIFIED** — its
  acceptance criterion was set before the result and the evidence is stored — but Verify Standard
  rule 7 reserves that elevation to the Verify role, not to the seat that did the work. It is a
  decision item, not a claim.

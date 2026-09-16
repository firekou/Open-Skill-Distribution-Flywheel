# Lab 001 — Reproduction Result: Harness Dry Run

**Seat:** Reproduction Agent (independent; did not produce the original run — SEAT_REGISTRY invariant I10)
**Date:** 2026-09-16
**Repository state reproduced against:** commit `bbafc83` (`Answer keys, scoring spec, blind scorer, and a 10-run harness dry run`)
**Subject:** the 10 records in `dryrun/out/records/`, every one `run_class: "dry_run"`

---

## 0. What this is, in one paragraph, before anything else

The Phase F Calibration Pilot gate **did not open**. Meter calibration is FAIL because no
benchmark credential exists, so **no pilot run and no benchmark run has ever been executed**.
What exists is a harness dry run: ten records produced by replaying a seeded-PRNG fixture
(`dryrun/FIXTURE.json`) through `harness/runner.py` with **no model, no provider and no
credential in the loop**. This report reproduces that dry run. It therefore tests **whether the
reproduction machinery works**. It says nothing — not a word, not by implication — about token
optimisation, about any of the eight candidates, or about hypotheses H1–H4. Any sentence below
that looks like a result is a statement about plumbing.

---

## 1. Exactly what was reproduced, and under what conditions

### 1.1 Records selected

The brief asked for at least two records exercising different code paths. Because the blind
label assignment is a function of the whole batch (see Difference **D-12**, which is why a
two-record plan is *not* a valid subset), the full 10-run `dryrun/PLAN.json` was re-executed.
Four records are compared field-by-field in detail; the other six are summarised.

| Record | Workload | Condition | Code path exercised |
|---|---|---|---|
| `dry_run-A-001-C0-r1` | A (agentic repo) | `C0` | simplest path: baseline, cold cache, single provider, 3 calls |
| `dry_run-A-003-C2+C4-r1` | A | `C2+C4` | combined-condition record shape, escalation, two models in one run |
| `dry_run-B-002-C3-r1` | B (long-doc) | `C3` | different workload, single-call run, no tool calls |
| `dry_run-E-002-C4-r1` | E (workflow) | `C4` | different workload, 6 calls, escalation, `model_pair` field present |

### 1.2 Frozen inputs used (all unmodified, all mounted read-only)

| Input | SHA-256 |
|---|---|
| `tasks/TASK_SET_v1.0.0/tasks/` (tree hash) | `7fbca09980cc74d252280674b6ae18c3b5f3b1addd3994c1716e8138cd4c1553` |
| `tasks/TASK_SET_v1.0.0/answer_keys/` (tree hash) | `03ea884c74bb866df824dd68151eb239c2f8fd57609f486fb230a4c5bb9564c7` |
| `dryrun/FIXTURE.json` | replayed verbatim; 31 calls across 10 tasks |
| `dryrun/PLAN.json` | replayed verbatim; 10 runs |
| `evidence/PRICING_SNAPSHOT_2026-09-15.json` | `be74b7a4…8039` (byte-identical to `environment/pricing/PRICING_SNAPSHOT_2026-09-15.json`) |
| `--blind-salt` | `lab001-dryrun-salt-2026-09-16` → `sha256 e89c2922…f9f0`, matching the original `BLIND_MAPPING.json` |

`tasks/`, `answer_keys/`, `dryrun/out/` and `environment/harness/` were not modified. Output was
written to a fresh directory, `reproduction/out/`.

### 1.3 The commands actually run

None of this is documented anywhere in the repository; it was reconstructed (see §5.1). Recorded
here so the next reproducer does not have to reconstruct it again.

```bash
# 1. clean build context — the live working tree is NOT clean (see D-06)
git archive HEAD benchmarks/token-efficiency-lab-001 | tar -x -C "$CLEAN"

# 2. build
bash "$CLEAN/benchmarks/token-efficiency-lab-001/environment/build.sh" \
     atk-lab001:repro-clean "$SCRATCH/atk-lab001-repro-clean.tar"

# 3. run the harness
docker run --rm --network=none \
  -v "$LAB/tasks":/lab/tasks:ro \
  -v "$LAB/evidence":/lab/evidence:ro \
  -v "$LAB/dryrun/FIXTURE.json":/lab/dryrun/FIXTURE.json:ro \
  -v "$LAB/dryrun/PLAN.json":/lab/dryrun/PLAN.json:ro \
  -v "$LAB/reproduction/out":/lab/dryrun/out \
  --entrypoint python3 atk-lab001:repro-clean \
  -m harness.runner \
    --task-root /lab/tasks/TASK_SET_v1.0.0 \
    --fixture   /lab/dryrun/FIXTURE.json \
    --snapshot  /lab/evidence/PRICING_SNAPSHOT_2026-09-15.json \
    --out       /lab/dryrun/out \
    --plan      /lab/dryrun/PLAN.json \
    --run-class dry_run \
    --blind-salt lab001-dryrun-salt-2026-09-16 \
    --container-digest sha256:19d5968a…f420

# 4. re-score
docker run --rm --network=none -v "$LAB/reproduction/out":/lab/dryrun/out \
  --entrypoint python3 atk-lab001:repro-clean \
  -m harness.judge --packets /lab/dryrun/out/judge_packets --scores /lab/dryrun/out/judge_scores
```

Result: **10 planned, 10 completed, 0 failed.** Judge: 10 packets scored, 0 passed,
0 zero-tolerance breaches.

---

## 2. Environment reconstruction

The container was built from `environment/build.sh` in this session. No pre-existing image was
reused for the reproduction run.

### 2.1 The three digests, and which is which

| Digest | Tag present locally | Layers | What it actually is |
|---|---|---|---|
| `sha256:6edd71a6adff…1261` | `atk-lab001:build4` | 11 | The digest in `environment/ENVIRONMENT_LOCK.json`. Built from the Dockerfile **as it stood at commit `a1d1c06`**, i.e. *before* `COPY calibration/` and `COPY pricing/` were added at `cec6c61`. `build.sh` at HEAD can no longer produce it. |
| `sha256:780e1f2518e6…4caa` | `atk-lab001:v2` | 13 | The digest stamped as `container_digest` on **all ten** dry-run records and in `RUN_SUMMARY.json`. **It did not produce them** (§2.3). |
| `sha256:19d5968a2eb7…f420` | `atk-lab001:repro-clean` | 13 | **My build**, from a clean `git archive HEAD` checkout. Built twice, same digest both times. This is what the reproduction ran in. |

A fourth digest, `sha256:8316911a2af0…d980`, came from building the Dockerfile against the **live
working tree** rather than a clean checkout. Its sole difference from `19d5968a` is four stray
`harness/__pycache__/*.pyc` files that the host had written; there is no `.dockerignore`
(Difference **D-06**).

My digest matches **neither** expected value. Per the brief, that is a finding, and it is
reported as one rather than rounded off. Layers 1–9 (base image, pinned pip closure,
`run_record_schema.json`) are **bit-identical across all four images**; every divergence is in
the `COPY harness/` and `COPY calibration/` layers.

### 2.2 Why my build differs from `780e1f…` (the recorded image)

File-level diff of `/lab` between `atk-lab001:v2` and my build:

| Path | in `v2` | in my build | Note |
|---|---|---|---|
| `calibration/FIXTURE_v1.0.0.json` | `f2de7038…` | `c5ae60a1…` | **`f2de7038` matches no commit in the repository** — not HEAD, not `cec6c61`, not the working tree. The image contains content that has never been committed. |
| `harness/blind.py` | `5fa0f9d5…` | `39be2c57…` | `5fa0f9d5` is the **pre-E027** version (commits `8602bf5`/`cec6c61`). |
| `harness/judge.py` | **absent** | present | The recorded image contains no scorer. |
| `harness/blind_smoke.py` | **absent** | present | |
| `harness/test_judge.py` | **absent** | present | |
| all other 10 files | identical | identical | incl. `runner.py`, `meter.py`, `pricing.py`, `record.py`, `providers.py` |

### 2.3 The recorded image provably did not produce the recorded run

Running the identical command in `atk-lab001:v2`:

```
"planned": 10, "completed": 9, "failed": 1,
"failures": [{"task_id": "D-002", "condition": "C1",
  "error": "BlindError: blind violation: forbidden key 'repository' present at
            /answer_key/tool_calls_made_by_this_derivation[0]/args/repository."}]
```

That is defect E027, fixed in `blind.py` *after* `v2` was built. The original `RUN_SUMMARY.json`
reports `"completed": 10, "failed": 0`. **The image named by `container_digest` on every record
cannot produce those records.** The field is false.

The mechanism is that `container_digest` is *self-asserted*: `runner.py` takes it as the
`--container-digest` CLI string and writes it through unexamined; `selfcheck.py` reads it from
the `LAB_CONTAINER_DIGEST` environment variable. Nothing anywhere derives it from the running
image. The schema permits `["string","null"]` and does not require the field.

### 2.4 Runtime and dependency manifest

| Property | `ENVIRONMENT_LOCK.json` | Measured in my build | Verdict |
|---|---|---|---|
| python | `3.11.15` | `3.11.15` | MATCH |
| implementation / machine | cpython / x86_64 | cpython / x86_64 | MATCH |
| distributions locked | 16 | 16, all at the locked version | MATCH |
| distributions installed | 20 | 20 | MATCH |
| base image digest | `sha256:d29f48a3…e0c3` | same (pinned in Dockerfile) | MATCH |
| build hermeticity | `--network=none`, vendored wheelhouse | confirmed; build completed with no network | MATCH |
| build determinism | "reproducible artifact = manifest digest" | two clean builds → same manifest digest, different tarball bytes | MATCH (behaves exactly as the lock documents) |
| `dependency_manifest_sha256` = `93d9ecce47da…92fd` | — | **could not be reproduced** | **UNVERIFIABLE** |

For `dependency_manifest_sha256` there is no code in the repository that computes it and no
documented recipe. Six plausible derivations were tried inside the image — `pip freeze` raw,
`pip freeze` sorted, and sorted `name==version` from `importlib.metadata` in four
capitalisation/trailing-newline variants — and none produces `93d9ecce…`. The lock records a
hash that nobody can check.

Self-check inside my image: **8/8 PASS**, python 3.11.15, egress default-deny confirmed against
all four probe destinations.

---

## 3. Comparison tables

### 3.1 The four detailed records

Every field in each record was compared. Records carry 36 fields (37 for the `C4` record, which
adds `model_pair`). **In all four, exactly one field differs: `container_digest`** — and it
differs only because I honestly stamped my own image's digest rather than copying the original's.

| Compare | `A-001` / `C0` | `A-003` / `C2+C4` | `B-002` / `C3` | `E-002` / `C4` |
|---|---|---|---|---|
| **Environment** — container digest | orig `780e1f…4caa` · repro `19d5968a…f420` — **DIFFERS** | same | same | same |
| **Environment** — python | 3.11.15 = 3.11.15 | = | = | = |
| **Environment** — dependency manifest | 16/16 locked dists match; lock's own hash unverifiable | = | = | = |
| **Output** — `model_output` | identical (449 chars) | identical (449) | identical (149) | identical (899) |
| **Usage** — `input_tokens` | 74 738 = 74 738 | 61 170 = 61 170 | 48 610 = 48 610 | 78 169 = 78 169 |
| **Usage** — `output_tokens` | 2 040 = 2 040 | 2 347 = 2 347 | 505 = 505 | 4 476 = 4 476 |
| **Usage** — `total_tokens` | 76 778 = 76 778 | 63 517 = 63 517 | 49 115 = 49 115 | 82 645 = 82 645 |
| **Usage** — `cost` | 0.009458538 = | 0.015943709 = | 0.0075945 = | 0.015670792 = |
| **Quality** — `quality_score` | 0.0 = 0.0 | 0.0 = 0.0 | 0.0 = 0.0 | 0.0 = 0.0 |
| **Quality** — `task_success` | false = false | false = false | false = false | false = false |
| **Quality** — `failure_reason` | `unparseable_output` = | `unparseable_output` = | `unparseable_output` = | `unparseable_output` = |
| **Evidence** — `task_set_hash` | `7fbca099…1553` = | = | = | = |
| **Evidence** — `answer_key_hash` | `03ea884c…64c7` = | = | = | = |
| **Evidence** — `prompt_hash` | `2064dbc9…40a5` = | `9371b12c…8947` = | `26842f89…7daf` = | `a8d1c692…139a` = |
| **Evidence** — `config_hash` | `14269762…8862` = | `98989e86…4f72` = | `a615420f…6462` = | `d0ed0866…ada` = |
| **Evidence** — `MANIFEST.json` per-file hash | **DIFFERS** (see D-02) | DIFFERS | DIFFERS | DIFFERS |
| **Evidence** — raw payload modulo `written_at` | identical | identical | identical | identical |
| **Blind** — `blind_treatment_id` | `Treatment B` = | `Treatment E` = | `Treatment C` = | `Treatment D` = |
| Other reproduced fields | `cache_state` cold, `model_calls` 3, `tool_calls` 8, `retries` 0, `escalations` 0, `latency_ms` 0, `raw_evidence_path`, `model`, `provider`, `model_version`, `notes` — all identical | escalations 1, models `deepseek-flash,deepseek-v4-pro` — identical | model_calls 1, tool_calls 0 — identical | escalations 1, `model_pair` `deepseek-flash -> deepseek-v4-pro` — identical |

### 3.2 All ten records

| Record | Cond | WL | calls | input | output | total | cost | cache | esc | label | fields differing |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dry_run-A-001-C0-r1 | C0 | A | 3 | 74738 | 2040 | 76778 | 0.009458538 | cold | 0 | Treatment B | `container_digest` |
| dry_run-A-002-C1-r1 | C1 | A | 3 | 74677 | 2794 | 77471 | 0.009890175 | cold | 0 | Treatment F | `container_digest` |
| dry_run-A-003-C2+C4-r1 | C2+C4 | A | 3 | 61170 | 2347 | 63517 | 0.015943709 | cold | 1 | Treatment E | `container_digest` |
| dry_run-B-001-C0-r1 | C0 | B | 1 | 45664 | 377 | 46041 | 0.0070758 | cold | 0 | Treatment B | `container_digest` |
| dry_run-B-002-C3-r1 | C3 | B | 1 | 48610 | 505 | 49115 | 0.0075945 | cold | 0 | Treatment C | `container_digest` |
| dry_run-C-001-C2-r1 | C2 | C | 4 | 60129 | 2217 | 62346 | 0.007821297 | cold | 0 | Treatment A | `container_digest` |
| dry_run-D-001-C0-r1 | C0 | D | 2 | 28189 | 1027 | 29216 | 0.004005474 | cold | 0 | Treatment B | `container_digest` |
| dry_run-D-002-C1-r1 | C1 | D | 2 | 28960 | 1380 | 30340 | 0.004333218 | cold | 0 | Treatment F | `container_digest` |
| dry_run-E-001-C3-r1 | C3 | E | 6 | 58475 | 4267 | 62742 | 0.00856638 | cold | 0 | Treatment C | `container_digest` |
| dry_run-E-002-C4-r1 | C4 | E | 6 | 78169 | 4476 | 82645 | 0.015670792 | cold | 1 | Treatment D | `container_digest` |

*(Token and cost columns are PRNG output from a synthetic fixture. They are printed here only to
show that two executions agree. They are not measurements of anything.)*

### 3.3 Artifact-level comparison

Both directories contain the same 53 files, same names, no extras and no omissions.

| Artifact class | Count | Byte-identical? |
|---|---|---|
| `judge_packets/*.json` | 10 | **10/10 byte-identical** |
| `judge_scores/*.json` (incl. `_SUMMARY.json`) | 11 | **11/11 byte-identical** |
| `runner_only/BLIND_MAPPING.json` | 1 | **byte-identical**, incl. `salt_sha256` |
| `records/*.json` | 10 | differ in `container_digest` only |
| `raw/*/raw.json` | 10 | differ in `written_at` only; identical after removing it |
| `raw/*/MANIFEST.json` | 10 | differ in `written_at` and the consequent `files["raw.json"]` hash |
| `RUN_SUMMARY.json` | 1 | differs in `ran_at` and `container_digest`; all 6 substantive fields identical |

All 10 reproduction manifests verify against their own contents; all 10 original manifests still
verify too.

### 3.4 Blind mapping

`BLIND_MAPPING.json` reproduced **byte-identically**, including `salt_sha256`
`e89c2922…f9f0`, which confirms the salt `lab001-dryrun-salt-2026-09-16`:

```
C2 → Treatment A   C0 → Treatment B   C3 → Treatment C
C4 → Treatment D   C2+C4 → Treatment E   C1 → Treatment F
```

The labels are genuinely scrambled with respect to condition order, as the protocol claims. But
this reproduced **only because the full 10-run plan was re-executed** — see **D-12**.

---

## 4. Reproduction Difference section

Every difference found, including trivial ones.

### EXPECTED-BY-CONSTRUCTION

| ID | Difference | Detail |
|---|---|---|
| **D-01** | `RUN_SUMMARY.ran_at`, `raw/*/raw.json:written_at`, `raw/*/MANIFEST.json:written_at` | Wall-clock timestamps. `2026-09-16T10:38:12Z` vs `2026-09-16T10:44:07Z`. A reproduction that matched these would mean the file had been copied, not regenerated. |
| **D-02** | `raw/*/MANIFEST.json → files["raw.json"]` SHA-256 differs for all 10 | Deterministic consequence of D-01: `written_at` is written *inside* `raw.json`, then `raw.json` is hashed. Content is byte-identical once `written_at` is removed (verified for all 10). *Expected-by-construction as a difference, but see **D-13** for why it is also a defect.* |
| **D-03** | `container_digest`: `780e1f…4caa` → `19d5968a…f420` | I stamped my own image rather than copying the original's string. Doing otherwise would have been falsification. *The reason the original value is wrong is **D-08**, a separate matter.* |
| **D-04** | Exported OCI tarball bytes differ between two identical builds (`1dcbab79…` vs `0c157f30…`) | Explicitly documented in `ENVIRONMENT_LOCK.json`: *"the exported OCI tarball bytes differ between builds (archive wrapper metadata), while every blob inside is identical. Verify the manifest digest, never the tarball."* Confirmed true. |

### BENIGN

| ID | Difference | Detail |
|---|---|---|
| **D-05** | `raw_evidence_path` (`/lab/dryrun/out/raw/…`) matched only by luck | It is an absolute in-container path determined entirely by the operator's `-v` mount choice, which is documented nowhere. I inferred the mount layout from the original records and deliberately mirrored it. A reproducer who mounted at `/lab/reproduction/out` — the obvious choice given the repo layout — would see all 10 records differ on this field for no substantive reason. |
| **D-06** | Live-working-tree build → `8316911a…d980`; clean-checkout build → `19d5968a…f420` | There is no `.dockerignore` and the build context is `environment/`. Four `harness/__pycache__/*.pyc` files, written by running the harness on the host, entered the image and changed the digest. The image is reproducible from a clean checkout and not from a working tree. |
| **D-07** | `latency_ms` = 0 in both, but it is wall-clock derived | `int((time.time() - started) * 1000)` over the replay loop. Measured replay time is ~0.03 ms, so it floors to 0 robustly here. Latent, not active: in any real run this field can never reproduce, and nothing in the record marks it as non-reproducible. |

### WOULD-INVALIDATE

These would invalidate a real reproduction, or already invalidate a specific claim.

| ID | Difference / defect | Why it would invalidate |
|---|---|---|
| **D-08** | **`container_digest` on all 10 records names an image that provably cannot produce them.** Running the same command in `atk-lab001:v2` yields 9/10 with `D-002` failing on the E027 `BlindError`. | The environment row of any reproduction is unfalsifiable if the recorded digest is an operator-supplied string. There is currently no way to tell a correct `container_digest` from a typo. Every dry-run record carries a false one. |
| **D-09** | **The `v2` image contains `calibration/FIXTURE_v1.0.0.json` = `f2de7038…`, which matches no commit in the repository** (all commits and the working tree carry `c5ae60a1…`). | The environment that stamped itself onto the records cannot be rebuilt from the repository at any revision. "Reconstruct the environment from the repository alone" is not satisfiable for image `780e1f…`. |
| **D-10** | **`ENVIRONMENT_LOCK.json` locks `sha256:6edd71a6…` and `"layers": 11`, but `build.sh` at HEAD produces a 13-layer image.** The Dockerfile gained `COPY calibration/` and `COPY pricing/` at commit `cec6c61`; the lock was never updated. | The lock is stale and can never again be satisfied by the documented build command. A reproducer checking the lock's digest will always fail, correctly, and will not know whether the environment drifted or the lock did. |
| **D-11** | **`dependency_manifest_sha256: 93d9ecce…` is unverifiable.** No code computes it; no recipe is documented; six plausible derivations do not match. | One of the three environment comparison rows the reproduction protocol demands cannot be executed at all. |
| **D-12** | **Blind labels depend on the whole batch, not on `(salt, condition)`.** Measured: full plan → `C0 = Treatment B`; a 2-record `[C0, C2+C4]` plan with the *same salt* → `C0 = Treatment A`. | `BLIND_EVALUATION_PROTOCOL.md` states labels are "assigned by sorting SHA-256 digests of `(salt, condition)`". They are actually sorted over the conditions *present in that batch*, so the label is a function of `(salt, condition, batch-composition)`. An honest partial reproduction — the normal case, since reproducing one favourable result is the whole point — will disagree with the original on `blind_treatment_id` while being entirely correct. That is a false invalidation waiting to happen. |
| **D-13** | **Raw-evidence manifest hashes can never match across runs**, because the hashed file embeds a wall clock (`written_at`). | The manifest detects tampering *within* one run (verified: it does). It structurally cannot answer "is the reproduction's evidence the same as the original's", which is exactly the check the brief lists under "Evidence manifest". I had to strip `written_at` and re-hash by hand to answer it. That comparison is not part of the harness. |
| **D-14** | **Protocol step 4 — "the record is updated with the returned values" — is implemented nowhere.** No code in `harness/` writes `quality_score` or `task_success` back into a record. | All 10 records permanently carry the placeholder `quality_score: 0.0`, `task_success: false`. In this dry run every genuine score is also `0.0`, so the gap is invisible; in a real run the records would silently report every run as a scored failure. A reproduction comparing the *records'* quality fields would compare placeholders and always "match". |

---

## 5. Is the reproduction procedure itself a procedure?

A procedure only I could follow is not a reproduction procedure. Here is what was missing.

### 5.1 Undocumented — had to be reverse-engineered

1. **The `docker run` invocation does not exist anywhere in the repository.** Not in `dryrun/README.md`, not in `build.sh`, not in the run summary. The mount layout was inferred by reading `/lab/dryrun/out/raw/...` out of the original `raw_evidence_path` field and working backwards. The `--entrypoint python3` override (the image `CMD` is `harness.selfcheck`) was a guess.
2. **The blind salt is not in the repository** — only its SHA-256, inside `BLIND_MAPPING.json`. I had it from the task brief. A reproducer with the repository alone can *verify* a guessed salt but cannot *derive* it, so the blind-mapping comparison row is not independently executable. This is partly deliberate (the salt is the Runner's secret) but it is not stated as a limit anywhere.
3. **Which `--run-class`** to pass. `dry_run` is the default, but the summary does not record the flag as given.
4. **Which pricing snapshot path.** `evidence/` and `environment/pricing/` hold byte-identical copies today. Two copies of a frozen artifact with no stated canonical source is a drift waiting to happen.
5. **No `.dockerignore`**, so the documented build command is only reproducible from a clean checkout — which the build script does not do and the documentation does not mention (D-06).
6. **The judge cannot run in the recorded image.** `judge.py` is absent from `atk-lab001:v2`, so whatever scored the original packets was some other environment, unrecorded. `judge_scores/` files carry no environment provenance at all — no digest, no python version, nothing.

### 5.2 Suggested minimum fixes

- Derive `container_digest` inside the container (e.g. from `/proc/self/cgroup` or an operator-independent attestation) or have the runner refuse a digest it cannot corroborate. As it stands the field should be treated as a comment.
- Commit a `RUN_COMMAND.md` (or a `make` target) recording the exact invocation, mounts and entrypoint.
- Add `.dockerignore` for `__pycache__/`, `*.pyc`.
- Regenerate `ENVIRONMENT_LOCK.json` against the current Dockerfile, or state explicitly that the locked digest describes a superseded spec.
- Document the derivation of `dependency_manifest_sha256`, or delete the field.
- Either make blind labels a pure function of `(salt, condition)` — hash the pair and take a stable label from the digest, rather than sorting within the batch — or state prominently in `BLIND_EVALUATION_PROTOCOL.md` that labels are batch-scoped and partial reproductions must re-run the full plan.
- Move `written_at` out of `raw.json` into `MANIFEST.json` so raw payload hashes are comparable across runs.
- Implement the score write-back, or change the schema so an unjudged record is distinguishable from a judged-zero one.

---

## 6. What this does and does not establish

### It establishes

- The dry-run **harness is deterministic** on this fixture. Ten runs re-executed from the frozen
  inputs produced byte-identical judge packets, byte-identical judge scores, a byte-identical
  blind mapping, and records identical in all 36 fields but the self-asserted one.
- The **scorer is deterministic and blind-safe**: 11/11 score files byte-identical, and every
  packet contained exactly the nine permitted keys.
- The **container build is deterministic given a clean context**: two builds, one digest.
- The **evidence manifests detect tampering** within a run.
- Three named provenance mechanisms — `container_digest`, `ENVIRONMENT_LOCK.json`'s digest and
  dependency hash, and batch-scoped blind labels — **do not currently work as documented**, and
  would produce a false verdict if a real reproduction were run against them today.

### It does not establish — and nothing here may be read as establishing

- **Anything about any hypothesis.** H1, H2, H3 and H4 are untouched. No evidence for, none
  against, none partial.
- **Anything about any candidate.** No candidate is installed in any image used here
  (`candidates_installed: []`). `headroom`, `rtk`, `paritok-4b-v1`, `lean-ctx`, `NadirClaw`,
  `api-relay-audit`, `tokentab` and `entroly` were not executed, not measured, not compared.
- **Anything about token optimisation, cost, or cost per successful task.** Every token count
  above came from a PRNG seeded on a task id. Two programs agreeing on the output of the same
  PRNG is arithmetic, not measurement.
- **Anything about the meter's accuracy.** Meter calibration remains **FAIL**. The meter's
  accumulator was exercised; the meter-versus-provider comparison the calibration document
  requires still has no benchmark credential and has not been answered.
- **That a real pilot would reproduce.** A real run has live provider non-determinism, real
  latency, real cache behaviour and a real model. None of that was present. The parts of the
  record that a real run would make non-deterministic — `latency_ms`, `cache_state`,
  `model_output`, every token count — are precisely the parts this dry run holds constant by
  construction.
- **That the quality scores mean anything.** All ten are `0.0` with `task_success: false`,
  because the synthetic outputs are placeholder strings that no scorer could parse. The scorer
  agreed with itself about nonsense.

**Verdict on the reproduction machinery:** the *run* reproduces exactly. The *environment
attestation around the run* does not, and four of its mechanisms (D-08 through D-11) are
currently incapable of being checked. That is the finding worth acting on before the Calibration
Pilot gate is reconsidered.

---

## 7. Artifacts

- Reproduction output: `benchmarks/token-efficiency-lab-001/reproduction/out/` (53 files; original `dryrun/out/` untouched)
- Reproduction image: `atk-lab001:repro-clean` = `sha256:19d5968a2eb7fdef5659386dacc99210b210945544e8f9164f2be7afaec3f420`
- Nothing under `tasks/`, `answer_keys/`, `dryrun/out/` or `environment/harness/` was modified.

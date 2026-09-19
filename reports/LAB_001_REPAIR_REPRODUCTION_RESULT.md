# Lab 001 — Repair Round Reproduction Result

**Seat:** Reproduction Agent (ATK Token Efficiency Lab 001)
**Date:** 2026-09-16
**Branch:** `claude/atk-open-skill-distribution-96e4vv`
**Repository state at start:** `424c4734c989b49cebfb8decc2bca8400052dd7f`
**Repository state at finish:** `3781886` (the tree moved three times under this run — see D-11)
**Seat-registry invariant I10:** this seat built none of the artefacts reproduced here.

---

## 0. What this is, and what it is not — read before anything else

There are still **zero pilot runs and zero benchmark runs** in Lab 001. No model was called. No
provider credential exists or was used. Every record produced or examined below carries
`run_class: "dry_run"`.

What was reproduced is a **golden end-to-end dry run**: an answer reconstructed from each frozen
answer key by `tools/golden_run.py`, pushed through the real pipeline. The token counts come from
a hard-coded synthetic usage block (1000 in / 100 out per call); the costs are that arithmetic
times a price sheet.

Therefore:

* This report says **nothing** about token optimisation, about any candidate, or about
  hypotheses H1–H4. It cannot. There is no measurement of any model in it.
* It tests **whether the machinery reproduces**, not whether a result replicates.
* A reader who takes any number in section 4 as evidence about a treatment has misread it.

The previous round's finding was *"the run reproduces exactly; the attestation around it does
not."* This round: **the run still reproduces exactly, and all five of the re-checked fixes are
genuinely in place (one of them incompletely). Fifteen further findings are recorded below.**

One of them outranks the rest and belongs here rather than buried in section 5. **The 17/17 PASS
reproduces perfectly and was scored under the v1.0.0 rulebook**, because `runner.py` stamps
`methodology_version: "1.0.0"` on every record and `judge.py` version-gates on that field. None
of the v1.1.0 scoring repairs this round installed were exercised by the run cited as evidence
that they work. See **D-15**. The rest of this report's "reproduces exactly" results are all
true, and they are all about the wrong rulebook.

---

## 1. Conditions

| | |
|---|---|
| Host | Linux 6.18.44, x86_64, Docker 29.3.1 with BuildKit, daemon already running |
| Network | Used once, to confirm the base image pull. Every build ran `--network=none`; every run ran `--network none` |
| Credentials | None. Nothing in this report needs one |
| Image under test | Built from source four different ways (section 2), never pulled |
| Task set | `tasks/TASK_SET_v1.1.0`, plus a byte-copy pinned in scratch at commit `9ec5ed0` because the live tree kept moving (D-11) |
| Pricing snapshot | `evidence/PRICING_SNAPSHOT_PS-2026-09-16.json` (the runbook says `<id>`; I chose) |
| Blind salt | `lab001-dryrun-salt-2026-09-16` — the documented **test** salt, not a blinding secret |
| Scratch | All run output written outside the repository. `git status` clean at finish; `tasks/`, `answer_keys/`, `environment/harness/` and `TASK_SET_v1.0.0/` untouched (verified, section 7) |

---

## 2. Environment rebuild

### 2.1 Commands

```bash
# clean checkout, method A — as RUNBOOK §1 describes it
git archive --format=tar HEAD | tar -x -C $SCRATCH/clean1
cd $SCRATCH/clean1/benchmarks/token-efficiency-lab-001/environment
./build.sh atk-lab001:clean1  $SCRATCH/clean1.tar      # twice, for determinism
./build.sh atk-lab001:clean1b $SCRATCH/clean1b.tar

# clean checkout, method B
git clone --no-hardlinks --branch claude/atk-open-skill-distribution-96e4vv \
    /home/user/Open-Skill-Distribution-Flywheel $SCRATCH/clone1
cd $SCRATCH/clone1/benchmarks/token-efficiency-lab-001/environment
./build.sh atk-lab001:clone1 $SCRATCH/clone1.tar

# working tree (contaminated: 15 files in environment/harness/__pycache__)
cd benchmarks/token-efficiency-lab-001/environment
./build.sh atk-lab001:wt  $SCRATCH/wt.tar

# cache-independence
docker buildx prune -a -f
docker pull python:3.11.15-slim-bookworm@sha256:d29f48a3...e2e0c3
./build.sh atk-lab001:wt2 $SCRATCH/wt2.tar
```

### 2.2 Results

| Build | Source | Image manifest digest | Layers | Tarball sha256 |
|---|---|---|---|---|
| `clean1` | `git archive` checkout | `sha256:fa18caab25fe…d3ec456720bcba34729b543360ad3e848` | 13 | `a197b6da…` |
| `clean1b` | same tree, second build | `sha256:fa18caab25fe…` **(identical)** | 13 | `1cb10729…` |
| `wt` | working tree @ `424c473`, with `__pycache__` | `sha256:04d7fac698f8…9839d9a2dcd4153b9efea5defa68` | 13 | `6e3a2580…` |
| `clone1` | `git clone` checkout @ `424c473` | `sha256:04d7fac698f8…` **(identical)** | 13 | `75076c6c…` |
| `wt2` | working tree, after full buildx prune + base re-pull | `sha256:04d7fac698f8…` **(identical)** | 13 | `6459867c…` |
| `wt3` | working tree @ `9ec5ed0` (after `harness/test_harness.py` was added) | `sha256:93de0146b301…` | 13 | — |

### 2.3 Builds at HEAD, after the artefact moved under the run

The digest this seat was given, `sha256:04d7fac6…`, was accurate when the brief was written and
was already stale when the brief was executed: `c7787b8` added `environment/harness/test_harness.py`,
which the Dockerfile copies in. The coordinator has acknowledged this as a process error on their
side. It is recorded here as **D-14**, not as a reproducibility defect of the build.

Rebuilt from a fresh checkout of `HEAD = 37818868e93df5969e34047a73fa073b2c8abe40`, twice by each
method:

| Build | Source | Image manifest digest | Layers | Tarball sha256 |
|---|---|---|---|---|
| `clone2a` | `git clone` @ HEAD | **`sha256:93de0146b30113be44e7a398b5245dd9760420317b4f474fbf8239f6e346e969`** | 13 | `c63eba83…` |
| `clone2b` | same, second build | **`sha256:93de0146b301…` (identical)** | 13 | `de1e36ad…` |
| `wt3` | working tree @ `9ec5ed0` | `sha256:93de0146b301…` (identical) | 13 | — |
| `ga2a` | `git archive` @ HEAD | `sha256:4cd06ce8f76fe59af9d97d8f177a27f82f66afe39f3f8356d6100642f90a6e6a` | 13 | `c87f175f…` |
| `ga2b` | same, second build | `sha256:4cd06ce8f76f…` (identical) | 13 | `dae4ccc7…` |

**The authoritative value to record for HEAD is `sha256:93de0146b30113be44e7a398b5245dd9760420317b4f474fbf8239f6e346e969`.**
It is what `docker build` produces from any ordinary checkout — `git clone` and the working tree
agree — and it reproduced on four independent builds. The `git archive` value `4cd06ce8…` is the
same content carrying `git archive`'s group-write permission bits (D-1) and should not be recorded.

Values for `ENVIRONMENT_LOCK.json`, measured at HEAD:

| Field | Value |
|---|---|
| `image.manifest_digest` | `sha256:93de0146b30113be44e7a398b5245dd9760420317b4f474fbf8239f6e346e969` |
| `image.config_digest` | `sha256:d16d5ff08528e6c240d94d5fd5c99c7a30785a70e8fba717b8b06ce28cead6e2` |
| `image.layers` | 13 |
| `image.base_image_digest` | `sha256:d29f48a31a8b408ed19272ca1e7b10ebae13b240a27e862d3d4217c528e2e0c3` (unchanged) |
| `runtime.image_content_sha256` | `e54d54cb891c309669d27af69b1475213f05d45233b306ba1f652ab090cda8d4` |
| `runtime.dependency_manifest_sha256` | `8273d0e2144011927245abc2e701f009306fbf92166df665195fe6fbf031f0a9` (unchanged) |
| `image.superseded_digests` | add `sha256:04d7fac698f8…` — 13 layers, identical except that it predates `harness/test_harness.py` |

LG3 re-run against `93de0146` (LG3 PASS does not transfer between images): **8 of 8,
`"lg3_verdict": "PASS"`**, with the `--network bridge` negative control still failing correctly
(exit 1, check 5).

### 2.3.1 Cause of the drift, isolated

Both images were unpacked and compared layer by layer, entry by entry, on
(name, mode, mtime, uid, gid, content-sha256).

```
04d7fac6  ->  93de0146
LAYER 9 (COPY harness/ /lab/harness/):  diffid e90dab873db8 -> b0190eb45a61
   added  : ['lab/harness/test_harness.py']
   removed: []
   changed: []
All other 12 layers: byte-identical.
```

**Exactly one file, and nothing else.** No mode, mtime, ownership or content change to any other
file in the image. The cause is `c7787b8` and only `c7787b8`.

The second commit the coordinator flagged, `3781886` (which edits `tasks/C/C-001.json`, the
changelog and the design notes), **does not move the digest** — confirmed rather than assumed:
the working-tree build at `9ec5ed0` and both clean-clone builds at `3781886` all produce
`93de0146…`. Task files are mounted at `/lab/tasks`, not copied, and `build.sh`'s context is
`environment/` only.

### 2.4 What the earlier builds established

The table in 2.2 was measured against the pre-`c7787b8` tree and still stands on its own terms:
`sha256:04d7fac6…`, 13 layers, reproduced from the working tree, from a `git clone` checkout, and
after a full build-cache prune with the base image re-pulled by digest; deterministic across
repeated builds; tarball bytes different every time, exactly as `ENVIRONMENT_LOCK.json` says.

**Neither `git archive` build reproduced its contemporaneous clone build** — `fa18caab` against
`04d7fac6` before the drift, `4cd06ce8` against `93de0146` after it. That is **D-1**, a packaging
artefact rather than a content difference, and it is proved as such below.

### 2.5 Self-derived attestation — `harness.attest`

```bash
docker run --rm --network none <tag> python3 -m harness.attest "$DIGEST"
```

| Image | manifest digest | `image_content_sha256` | `dependency_manifest_sha256` |
|---|---|---|---|
| `wt` | `04d7fac6…` | `e685557957de30356ffcd29e424c157cf3183d837bec464f6a6916f0c7599425` | `8273d0e21440…` |
| `clone1` | `04d7fac6…` | `e685557957de…` | `8273d0e21440…` |
| `v11` (pre-existing) | `04d7fac6…` | `e685557957de…` | `8273d0e21440…` |
| `clean1` | `fa18caab…` **(differs)** | `e685557957de…` **(same)** | `8273d0e21440…` |
| `wt3` (HEAD, harness changed) | `93de0146…` | `e54d54cb891c…` **(differs)** | `8273d0e21440…` |

Both values match `ENVIRONMENT_LOCK.json` (`runtime.image_content_sha256`,
`runtime.dependency_manifest_sha256`) for the `04d7fac6` image. The content hash is *more* stable
than the manifest digest — it is blind to the permission artefact that broke D-1 — and it changed
the instant a file was added to `harness/`. That is the behaviour claimed for it.

### 2.6 LG3 self-check and its negative control

```bash
docker run --rm --network none -e LAB_CONTAINER_DIGEST=… -e LAB_ENVIRONMENT_ID=lab001-env-repro \
  -v .../TASK_SET_v1.1.0:/lab/tasks:ro -v $SCRATCH/lab-evidence:/lab/evidence atk-lab001:wt2
```

`"passed": 8, "failed": 0, "lg3_verdict": "PASS"`. Check 7 reports *"5 invalid record shapes were
all correctly rejected"*; check 8 reports *"manifest verified, tampering detected"*.

Negative control with `--network bridge`: **fails correctly**, exit 1, check 5 —
`egress policy NOT applied - reachable: 1.1.1.1:443, pypi.org:443, github.com:443`. A network
check that only ever passes proves nothing; this one does not only ever pass.

---

## 3. The golden end-to-end run

### 3.1 Commands (reconstructed — the runbook does not contain them; see §8)

```bash
python3 tools/golden_run.py --task-root $PINNED --out $OUTDIR

docker run --rm --network none \
  -v "$PINNED:/lab/tasks:ro" -v "$OUTDIR:/lab/golden" \
  -v ".../PRICING_SNAPSHOT_PS-2026-09-16.json:/lab/snapshot.json:ro" \
  atk-lab001:wt2 python3 -m harness.runner \
    --task-root /lab/tasks --fixture /lab/golden/FIXTURE.json \
    --snapshot /lab/snapshot.json --out /lab/golden/out \
    --run-class dry_run --plan /lab/golden/PLAN.json \
    --tool-audit /lab/golden/TOOL_AUDIT.jsonl \
    --container-digest "$DIGEST" --blind-salt lab001-dryrun-salt-2026-09-16

docker run --rm --network none \
  -v "$OUTDIR/out/judge_packets:/lab/packets:ro" -v "$OUTDIR/out/judge_scores:/lab/scores" \
  atk-lab001:wt2 python3 /lab/harness/judge.py --packets /lab/packets --scores /lab/scores

docker run --rm --network none -v "$OUTDIR:/lab/golden" atk-lab001:wt2 \
  python3 -m harness.finalize --records /lab/golden/out/records --scores /lab/golden/out/judge_scores

docker run --rm --network none -v "$OUTDIR:/lab/golden" atk-lab001:wt2 \
  python3 -m harness.aggregate --records /lab/golden/out/records --plan /lab/golden/CELL_PLAN.json
```

I mounted only `judge_packets` and `judge_scores` for the judge rather than the whole output
tree, because the whole tree contains `out/runner_only/BLIND_MAPPING.json`. RUNBOOK §7's own
command mounts the whole tree, three lines above the warning not to (**D-13**).

### 3.2 Runs performed

| Run | Image | Task set | Output dir | Result |
|---|---|---|---|---|
| `goldenA` | `wt2` (`04d7fac6`) | live @ `424c473` | `$SCRATCH/goldenA`, mounted `/lab/golden` | 17/17 completed, 17/17 PASS, 5 cells pass |
| `goldenB` | `wt2` | live @ `424c473` | `$SCRATCH/goldenB` | 17/17 completed, 17/17 PASS, 5 cells pass |
| `goldenC` | `wt2` | live @ `9ec5ed0` | `$SCRATCH/goldenC`, mounted **`/lab/work`** | 17/17, 17/17 PASS |
| `goldenP1` | `wt2` | **pinned copy** @ `9ec5ed0` | `$SCRATCH/goldenP1` | 17/17, 17/17 PASS, 5 cells pass |
| `goldenP2` | `wt2` | pinned copy | `$SCRATCH/goldenP2` | 17/17, 17/17 PASS, 5 cells pass |
| `goldenP3` | **`wt3`** (`93de0146`) | pinned copy | `$SCRATCH/goldenP3` | 17/17, 17/17 PASS |
| `goldenSub` | `wt2` | live @ `424c473` | `$SCRATCH/goldenSub` | 3/3 (A-001, C-002, E-003), 3/3 PASS |

Aggregator, every full golden run:
`cells_passed 5, cells_failed 0, attempts_planned 17, {PASS: 17, FAIL_QUALITY: 0, INVALID: 0}, attempts_unrecorded 0`.

**17/17 PASS reproduces.** So does the whole chain around it: runner → Evidence Producer →
packet builder → blind check → judge → finalize → aggregator.

### 3.3 Dry-run (10-run, mixed-condition) runs, for the blind-label subset test

| Run | Task set | Output dir | Result |
|---|---|---|---|
| `dryA` | live @ `424c473` | `$SCRATCH/dryA` | 10/10 completed |
| `dryB` | pinned @ `9ec5ed0` | `$SCRATCH/dryB` | 10/10 completed |
| `dryC` | pinned @ `9ec5ed0` | `$SCRATCH/dryC` | 10/10 completed |
| `drySub` | live @ `424c473` | `$SCRATCH/drySub` | 3/3 (A-002 / C1, E-002 / C4, A-003 / C2+C4) |

---

## 4. Comparison tables

### 4.1 Run-to-run, everything held fixed — `goldenP1` vs `goldenP2`

The clean determinism measurement: same image, same pinned task set, same salt, same mount point,
two separate invocations of the whole chain.

| Class | Compared | Differing |
|---|---|---|
| Run records (every field) | 17 | **0** |
| Judge packets (byte) | 17 | **0** |
| Judge scores (every field) | 18 incl. `_SUMMARY` | **0** |
| `raw.json` sha256 | 17 | **0** |
| Raw `MANIFEST.json` keys | 17 | **`written_at` only** |
| Blind mapping | 1 | **0** |

Per-field, on all 17 records: `container_digest`, `image_content_sha256`,
`dependency_manifest_sha256`, `model_output` (via `raw.json` and the packet), `input_tokens`,
`output_tokens`, `total_tokens`, `cost`, `quality_score`, `task_success`, `outcome`,
`failure_reason`, `task_set_hash`, `answer_key_hash`, `config_hash`, `prompt_hash`,
`blind_treatment_id`, `latency_ms`, `raw_evidence_path`, `evidence_provenance` — **all identical**.

`goldenA` vs `goldenB` (earlier tree state) gave the identical result: 17/17 records identical,
0 packet differences, 0 raw-hash differences, `written_at` the only manifest difference.

### 4.2 Full run vs partial subset, same salt

| Comparison | Records compared | Record fields differing | Packets differing | Raw hashes differing | Blind mapping equal |
|---|---|---|---|---|---|
| `goldenA` vs `goldenSub` (17 → 3, all C0) | 3 | **0** | 0 | 0 | **yes** |
| `dryA` vs `drySub` (10 → 3, conditions C1/C4/C2+C4) | 3 | **0** | 0 | 0 | **yes** |

`blind_treatment_id`, full run vs subset:

| Condition | 10-run batch (6 conditions present) | 3-run subset (3 conditions present) | Committed v1.0.0-era baseline |
|---|---|---|---|
| C0 | Treatment C | — | Treatment C |
| C1 | Treatment J | **Treatment J** | Treatment J |
| C4 | Treatment E | **Treatment E** | Treatment E |
| C2+C4 | Treatment H | **Treatment H** | Treatment H |

The full 10-entry `label_of_condition` map emitted by the 17-run C0-only golden batch is
byte-identical to the one emitted by the 10-run six-condition batch, to the one emitted by the
3-run subset, and to the one committed at `dryrun/out/runner_only/BLIND_MAPPING.json` from a
previous round. `salt_sha256` matches throughout.

**This is the case that used to look like an invalidation. It no longer does.**

### 4.3 Mount point changed — `goldenP1` (`/lab/golden`) vs `goldenC` (`/lab/work`)

| Field | Records affected | Nature |
|---|---|---|
| `raw_evidence_path` | 17/17 | `/lab/golden/out/raw/…` → `/lab/work/out/raw/…` |
| `evidence_provenance` | 8/17 | embeds the tool-audit absolute path |
| everything else | 0/17 | identical |
| judge packets | 4/17 | **not** the mount — see D-3 |
| `raw.json` sha256 | 0/17 | identical |

### 4.4 Image changed under the run — `goldenP1` (`04d7fac6`) vs `goldenP3` (`93de0146`)

| Field | Records affected |
|---|---|
| `container_digest` | 17/17 |
| `image_content_sha256` | 17/17 (`e6855579…` → `e54d54cb…`) |
| everything else, incl. packets, scores, raw hashes, blind mapping | 0 |

A single file added to `harness/` moved both attestation fields and nothing else. This is the
mechanism working.

### 4.5 Scoring-integrity manifest — verification and tamper tests

No manifest exists in the repository (**D-4**), so these ran against one built from a **scratch
copy** of the task set and environment. Baseline: `ok: true`, exit 0, eight groups, 155 task-set
files / 19 answer keys / 5 derivation scripts / 1 scoring spec / 4 docs / 1 probe / 1 scorer / 6
config files.

| # | Tamper | Detected | Group | Entry | Exit |
|---|---|---|---|---|---|
| T1 | append one byte to `answer_keys/A-001.json` | **yes** | `answer_key` | `modified` | 1 |
| T2 | append one byte to `corpora/docs_b/SDX7_PROTOCOL_SPEC_v3.1.md` | **yes** | `task_set` | `modified` | 1 |
| T3 | append one byte to `harness/judge.py` | **yes** | `scorer` | `modified` | 1 |
| T4 | add `corpora/docs_b/INJECTED.md` | **yes** | `task_set` | `added` | 1 |
| T5 | delete `answer_keys/E-003.json` | **yes** | `answer_key` | `deleted` | 1 |
| T6 | append text to `INDEPENDENT_VERIFICATION.md` (in the task set) | **NO** | — | — | **0** |
| T7 | rewrite `groups.answer_key.hash` inside `MANIFEST.json` to zeros | **NO** | — | — | **0** |
| T8 | T1 *and* rebuild the manifest is not possible without rebuilding — control | yes | `answer_key` | `modified` | 1 |

Every file restored; final verify `ok: true`, exit 0. The five tests the brief asked for (modified
answer key, modified corpus file, modified `judge.py`, added file, deleted file) **all pass, each
in the right group**. T6 and T7 are new holes I went looking for and found: **D-5** and **D-6**.

---

## 5. Reproduction Difference — every difference, classified

### EXPECTED-BY-CONSTRUCTION

**E-1. `written_at` in every raw `MANIFEST.json`.** 17/17 and 10/10 across every run pair.
Declared in RUNBOOK §10. This is the fix for last round's defect 2 working.

**E-2. OCI tarball bytes.** Five builds of three distinct images produced five distinct tarball
hashes; identical image manifest digests where the content matched. Declared in §10 and in
`ENVIRONMENT_LOCK.json`.

**E-3. `raw_evidence_path` (17/17) and the path strings inside `evidence_provenance` (8/17) when
the output directory is mounted somewhere else.** Declared in §10.

**E-4. `ran_at` in `RUN_SUMMARY.json`.** Differs on every run. Not in §10's table at all — a
trivial omission, listed here for completeness.

**E-5. `judge_scores/_SUMMARY.json` counts between a 17-run batch and a 3-run subset.**
`packets_scored`, `task_success_count`, `outcome_counts`. Obviously correct.

**E-6. `container_digest` and `image_content_sha256` moving between `04d7fac6`/`e6855579` and
`93de0146`/`e54d54cb`.** Caused by `harness/test_harness.py` being added to the image at commit
`c7787b8`. Both fields moved; nothing else did. Correct behaviour, but see D-12 for the
consequence for `ENVIRONMENT_LOCK.json`.

### BENIGN

**B-1. `latency_ms` is declared variable in RUNBOOK §10 but was identical (0) in every record of
every run.** The replay provider records no wall clock. The table is over-permissive here — it
licenses variation in a field that is in fact deterministic in a dry run, which means a real
divergence in it would be waved through. Harmless now; worth tightening before a run that has a
clock in it.

**B-2. Six COPY layers of the `git archive` image differ from the working-tree image in file mode
only.** Measured directly on the extracted layer tars: for layers 5, 6, 8, 9, 10 and 11, the
tuple (name, mtime, uid, gid, content-sha256) is **equal** for every entry; the mode is `0664`
against `0644`. `git archive` emits group-write for regular files; `git clone` and the working
tree give `0644`. Content is provably identical, and `image_content_sha256` agrees. The
consequence for the *recorded digest* is not benign — see D-1.

### WOULD-INVALIDATE

**D-1. A clean `git archive` checkout does not reproduce the digest a normal checkout gives.**
Measured twice, at two different tree states: `fa18caab25fe…` against `04d7fac698f8…` before the
drift, and `4cd06ce8f76f…` against `93de0146b301…` at HEAD. RUNBOOK §1 states
outright that *"a tree containing `__pycache__` and a clean `git archive` checkout produce the
same digest"*. They do not, and the reason is not `__pycache__` — it is the permission bits
described in B-1. A verifier following the runbook literally gets a digest that matches neither
`ENVIRONMENT_LOCK.json` nor any run record, and has no way to tell from the digest alone that the
content is identical. Fix: either document a `git clone`/`git checkout` clean tree as the
reproduction procedure, or normalise modes in `build.sh` (e.g. `--chmod` on COPY, or a mode sweep
before build). Mitigated in practice by `image_content_sha256`, which was identical across all
four images.

**D-2. Raw-evidence hashes are not reproducible across output directories on the documented
dry-run path.** `tools/make_dryrun_fixture.py` writes the operator's **absolute output path**
into `FIXTURE.json` as `tool_audit`. `runner.py` hashes the fixture into `raw.json` as
`fixture_sha256`. Therefore `raw.json` — the hashed evidence — is a function of where the
operator put their directory.
Measured, single variable, everything else held equal (`dryB` vs `dryC`: same image, same pinned
task set, same plan, same salt, only the output directory differs):

| | |
|---|---|
| Run records differing | **0 / 10** |
| Judge packets differing | **0 / 10** |
| `raw.json` sha256 differing | **10 / 10** |
| Raw `MANIFEST.json` `files` maps differing | **10 / 10** |

RUNBOOK §10 lists "Raw-evidence hashes" under *must match*. On this path they cannot. The golden
path is unaffected, because `golden_run.py` writes no `tool_audit` key into its fixture — so the
defect is invisible to exactly the run that the repo advertises. Fix: store the audit path
outside the hashed fixture, or record it relative to the fixture.

**D-3. The blind judge packet depends on stray `__pycache__` in the task-set directory.**
`harness/evidence.py`'s corpus hashing has no `__pycache__` exclusion, although
`harness/manifest.py` and `harness/attest.py` both do (`SKIP_DIR_NAMES`). Running against the live
tree instead of a cleaned copy added **51 `.pyc` entries** to `corpus_hashes`,
`corpus_hashes_before` and `corpus_hashes_after` in all four workload-A packets
(A-001…A-004); no other packet and no other field changed. Scores were unaffected here, but
(a) the object the judge scores is not a function of the frozen task set, and (b) `corpus_modified`
— the RT-08 fail-closed guard — is keyed on the same before/after maps, so a `.pyc` written during
an attempt would fail it spuriously. `PYTHONDONTWRITEBYTECODE=1` and the read-only mount mitigate
this inside the container; nothing mitigates the operator's working tree.

**D-4. There is no scoring-integrity manifest.** `tasks/TASK_SET_v1.1.0/MANIFEST.json` does not
exist in the repository. `manifest.py verify` against it dies with an unhandled
`FileNotFoundError` traceback. RUNBOOK §4 instructs the verifier to **build** the manifest and
then verify it — which can only ever pass, because it attests the tree as it is at verification
time. RT-12's whole point was that a key could change after the freeze; a manifest generated after
the fact cannot detect that. There is no committed frozen manifest for v1.1.0 (v1.0.0 has
`MANIFEST.sha256`). This is why D-11 went undetected by anything except a run record.

**D-5. `manifest.py verify` exits 0 when the manifest itself has been altered.** Setting
`groups.answer_key.hash` to 64 zeros produced `ok: true`, exit 0, with
`manifest_digest_recorded` (`cccf9dec…`) `!=` `manifest_digest_current` (`581b7e65…`) printed and
ignored. `report["ok"]` is computed only from the per-file maps; the group `hash` fields and the
two manifest digests are reported and never gate the exit code. The module's own docstring relies
on "an outer freeze record binds the manifest digest to the commit" — that outer record does not
exist either (D-4), so nothing checks the digest at all.

**D-6. A file inside the frozen task set can be modified with no detection.**
`INDEPENDENT_VERIFICATION.md` (added to the task set at commit `9ec5ed0`) is claimed by no group,
because `manifest.py`'s `docs` group is a hardcoded filename allowlist. `build` reports it under
`unclaimed_files`; `verify` neither reports it nor fails on it. Appending
`INJECTED SCORING GUIDANCE` to it gave `ok: true`, exit 0. Commit `fbce09a` claims *"Manifest now
covers every file in the task set; unclaimed is empty"* — false two commits later, and it will go
false again every time anyone adds a document. Fix: make the `docs` group a glob over the task-set
root, and make a non-empty `unclaimed_files` a verification failure.

**D-7. `scorer_hash` is listed as a must-match reproduction field but no run record carries it.**
It is absent from `environment/run_record_schema.json` and never written by `runner.py`. Records
carry `task_set_hash`, `answer_key_hash`, `config_hash`, `prompt_hash` — no `scorer_hash`. A
reproducer cannot confirm from the records that the same scorer produced both runs. Partially
mitigated by `image_content_sha256`, which covers `harness/` including `judge.py`, but that is not
what §10 says to compare.

**D-8. Two different quantities are both called `config_hash`.** In a run record it is
`sha256(condition | snapshot_id | task_set_hash)` — `3f811d1e6256…` in the golden run. In the
integrity manifest it is a hash over `run_record_schema.json` plus `evidence.py`, `blind.py`,
`meter.py`, `pricing.py` and `record.py` — `d23fc80ab081…`. They are unrelated values with the
same name in the same system, and RUNBOOK §10 says "`config_hash`" without saying which. The
record's version covers no harness code at all, so it is much weaker than its name suggests.

**D-9. Protocol step 4 is implemented, but leaves a contradictory record.** `finalize.py`
correctly moved every golden record from the runner's placeholder
(`quality_score 0.0`, `task_success false`, `outcome INVALID`) to the judge's verdict
(`1.0`, `true`, `PASS`) — that part of the fix is real and reproduces. But it writes
`failure_reason` only `if s.get("failure_reason")`, and a passing score carries none. Result:
**all 17 finalized PASS records say `"failure_reason": "awaiting Quality Judge score"`** beside
`"outcome": "PASS"` and `"quality_score": 1.0`. `failure_reason` is one of the fields §10 requires
to match on a reproduction; it matches, and its value is wrong on every passing record. One line:
clear or null it when the outcome is PASS.

**D-10. RUNBOOK §9's test command fails on a clean, untampered tree.** As written
(`-v environment/harness:/lab/harness:ro` only) it produces
`Ran 240 tests … FAILED (failures=1, skipped=10)` —
`TestCountRuleFollowsTheTaskText … AssertionError: 0 not greater than or equal to 10`, because the
test looks for the task set at `/lab/tasks/tasks` and it is not mounted. Adding
`-v tasks/TASK_SET_v1.1.0:/lab/tasks:ro` gives `OK (skipped=10)`. A documented verification step
that fails on a good tree trains the next operator to ignore it. Separately, the runbook does not
mention `harness/test_harness.py` (46 tests) at all; host-side
`python3 -m unittest discover -s environment/harness` runs 286 tests, all OK.

**D-11. The frozen task set was modified three times while this reproduction was running.**
Commits `c7787b8` (added `harness/test_harness.py`, which changes the image),
`9ec5ed0` (edited `answer_keys/E-001.json`) and `3781886` (edited `tasks/C/C-001.json`) landed on
the branch between the start and the end of this run. The E-001 edit changed
`answer_key_hash` from `cedc896b…` to `ef023577…` **across all 17 records mid-measurement**, and
appeared in my first comparison as a 17/17 field difference until I traced it.
The machinery caught it — the hash is doing exactly its job — and I re-baselined against a pinned
byte-copy of the task set, which is the only reason section 4.1 is clean. But: a task set that a
freeze record calls frozen was edited under a reproduction seat, with no manifest (D-4) and no
filesystem enforcement to notice. Any reproduction of Lab 001 must pin a commit and work from a
checkout of it, and the runbook must say so.

**D-12. `ENVIRONMENT_LOCK.json` is already stale at HEAD.** It pins
`image.manifest_digest = sha256:04d7fac6…` and `runtime.image_content_sha256 = e6855579…`. HEAD
builds to `sha256:93de0146b30113be44e7a398b5245dd9760420317b4f474fbf8239f6e346e969` /
`e54d54cb891c309669d27af69b1475213f05d45233b306ba1f652ab090cda8d4`, because `c7787b8` added a file
under `harness/`. Any record produced from HEAD names an image the lock file does not know. The
commit that changed the image did not update the lock. Replacement values are tabulated in §2.3;
see also D-14.

**D-13. RUNBOOK §7 contradicts its own warning.** Its judge invocation mounts `$PWD/dryrun` whole,
which contains `dryrun/out/runner_only/BLIND_MAPPING.json`; three lines later it says
**"Never mount `dryrun/out/runner_only/` for the judge. It holds the blind mapping."** I mounted
`judge_packets` read-only and `judge_scores` read-write instead. The blind check in `blind.py`
protects the packet *contents*; nothing protects the judge's filesystem.

**D-14. The image was changed while it was being verified, and the digest in circulation named an
image that could not produce the artefact.** The brief quoted
`sha256:04d7fac698f8…` as the expected digest. Commit `c7787b8` added
`environment/harness/test_harness.py` during this reproduction; because the Dockerfile does
`COPY harness/ /lab/harness/`, the image moved to `sha256:93de0146b301…` and
`image_content_sha256` moved from `e6855579…` to `e54d54cb…`. `ENVIRONMENT_LOCK.json` still pins
the old pair (D-12). The coordinator has acknowledged this as a process error rather than a build
defect, and the measurement in §2.3.1 confirms the cause is that one file and nothing else.

It belongs in the findings anyway, because it is the **same failure the previous round found with
`container_digest`, in the same round that fixed it**: an attestation naming an image that provably
could not have produced the artefact it is attached to. Last time the mechanism was an operator
typing a stale string; this time it was a commit landing under a running verification. The
machinery caught it both times — `image_content_sha256` and `container_digest` both moved, together,
and nothing else in any record did (§4.4) — but nothing *prevented* it, and nothing updates
`ENVIRONMENT_LOCK.json` when the image changes.

The structural cause is the one in D-11: there is no pinned commit in the reproduction procedure.
A digest is only meaningful with the commit it was built from beside it. Recommended: `build.sh`
should print the `git rev-parse HEAD` of its context and refuse a dirty tree, the lock file should
carry that commit next to the digest, and `RUNBOOK.md` §1 should begin with a checkout of a named
commit.

**D-15. The golden run's 17/17 PASS was scored under the v1.0.0 rulebook, not the repaired
v1.1.0 one.** Found by reading the version stamps in my own output, and confirmed against the
code at the commit I reproduced (`3781886`):

* `harness/runner.py` line 193 hardcodes `"methodology_version": "1.0.0"` (and line 187
  `"task_version": "1.0.0"`) on every record, although the run is against `TASK_SET_v1.1.0`.
* Line 239 passes the record's value straight into `build_packet`, so the packet inherits it.
  `JudgePacket`'s `methodology_version: str = "1.1.0"` default is never reached.
* Measured in `goldenP1`: **all 17 judge packets and all 17 records declare
  `methodology_version: "1.0.0"`.** Only `judge_scores/_SUMMARY.json` says `spec_version 1.1.0`.
* `harness/judge.py` gates on exactly that field — `V1_0_0`/`V1_1_0`, with at least fourteen
  distinct `view.get("_mv") == V1_1_0` branches covering the absolute quality floors, the C
  citation-symmetry rule, the count rulings, the corpus-integrity gate and turn completeness.

So the v1.1.0 repairs this round installed were **not exercised by the run that is cited as
evidence they work**. The 17/17 is green under the older, more permissive rules. This is not a
reproduction difference — it reproduces perfectly, every time, on both images — it is a defect
that reproducing revealed, and it is the same shape as D-9: the fix is in the tree and the
pipeline does not reach it.

A concurrent seat began repairing this in the working tree at 17:56 UTC, after my measurements
were complete (a single `METHODOLOGY_VERSION` constant in `harness/__init__.py`, read by
`blind.py` and `runner.py` instead of literals). I record it as my own measurement because the
packet data is mine and the consequence is mine to state: **every "17/17 PASS" claim made about
Lab 001 before that fix lands, including the one in this report, describes the v1.0.0 scoring
path.** The golden run must be re-run and re-reported once the stamp is corrected, and the
number may not survive — that is the point of correcting it.

---

## 6. The five previously-fixed items, by measurement

| # | Previously found | Verdict | Measurement |
|---|---|---|---|
| 1 | `container_digest` was an unverified operator string | **FIXED** | `image_content_sha256` and `dependency_manifest_sha256` are present on all 17 golden and all 10 dry-run records, computed inside the container by `harness.attest`. Identical (`e6855579…`) across four images built by four different routes, including the one whose manifest digest differs (D-1). Changed to `e54d54cb…` the moment one file was added to `harness/`, with nothing else in the record moving (§4.4). Both values match `ENVIRONMENT_LOCK.json` for the `04d7fac6` image. |
| 2 | `written_at` lived inside the hashed `raw.json` | **FIXED** | `raw.json` top-level keys are `calls, condition, cross_provider_warning, fixture_sha256, model_output, run_class, run_id, task_id` — no timestamp of any kind. `raw.json` sha256 identical across every same-input run pair (17/17 and 10/10); `written_at` in `MANIFEST.json` is the sole difference. **Caveat:** the raw hash is still not reproducible across output directories on the dry-run path, for the unrelated reason in D-2. |
| 3 | Blind labels were batch-scoped | **FIXED** | The full 10-entry `label_of_condition` map is byte-identical in: a 17-run batch containing only `C0`; a 10-run batch containing six conditions; a 3-run subset containing three; and the committed baseline from a previous round. Per-record `blind_treatment_id` for C1 / C4 / C2+C4 is Treatment J / E / H in both the 10-run batch and its 3-run subset (§4.2). `blind.assign` labels `CANONICAL_CONDITIONS` and raises on any condition outside it. |
| 4 | Protocol step 4 was implemented nowhere | **FIXED, with a defect** | Pre-finalize records read `quality_score 0.0 / task_success false / outcome INVALID`; post-finalize all 17 read `1.0 / true / PASS`. `finalize.py` refuses an unscored packet, a record with no score, and a score with no declared `outcome` (all three paths present in code). **But** `failure_reason` keeps the runner's placeholder `"awaiting Quality Judge score"` on all 17 PASS records — D-9. |
| 5 | A working-tree build differed from a clean-checkout build | **FIXED** | With `**/` present: 0 files in `/lab/harness/__pycache__` in the image, and a working tree carrying 15 `.pyc` files builds to the *same* digest as a `git clone` checkout (`04d7fac6`, twice, and `93de0146` at HEAD). With `**/` stripped from `.dockerignore` on a scratch copy of the same tree: **15 files land in `/lab/harness/__pycache__`** and the digest moves to `7637f878…`. The prefixes are load-bearing and they work. **However**, the residual clean-vs-working-tree difference in D-1 is a *different* cause that this fix does not address, and RUNBOOK §1 conflates the two. |

---

## 7. Constraint compliance

* `tasks/`, `answer_keys/`, `environment/harness/` and `TASK_SET_v1.0.0/` were never written to.
  All tamper tests ran on `$SCRATCH/tamper/`, a copy. All run output went to the scratch
  directory, not the repository.
* `git status --short` is empty at finish; `git diff --stat HEAD` against `tasks/` and
  `environment/harness/` is empty. The only untracked-or-ignored paths under the lab are the
  pre-existing `__pycache__` directories, which were there before this seat started.
* Nothing was committed.
* **Not mine:** at the time of writing, `git status` shows uncommitted modifications to
  `environment/harness/{__init__,blind,evidence,runner,selfcheck}.py` and an untracked
  `tasks/TASK_SET_v1.1.0/RED_TEAM_REVIEW.md`. These are a concurrent seat's in-flight edits
  (mtimes 17:56–17:58 UTC), made after all measurements in this report were complete (builds
  17:37–17:53, runs 17:41–17:46). This seat wrote nothing under `benchmarks/`. Every build and
  run reported above used the tree as it stood at the commit named beside it; the `git clone`
  builds used committed state only and are unaffected regardless. See D-15 for why one of those
  edits matters to this report's headline.
* Network was used once, to confirm the base image pull by digest. Every build and every run was
  offline.

---

## 8. Was the runbook sufficient? No — and here is the list

`RUNBOOK.md` is a large improvement on last round, when the `docker run` invocation existed
nowhere in the repository. The mount layout, the entrypoint override, the negative control, the
LG3 command, the pricing preflight and the aggregator call are all there and all work. I did not
have to reverse-engineer a mount path from inside a run record this time.

It was still not sufficient. What I had to work out myself:

1. **The golden run is not in the runbook at all.** `tools/golden_run.py` is never mentioned.
   §6 documents only `make_dryrun_fixture.py` and the 10-run fixture dry run. The 17/17 golden run
   — the thing the repo advertises, and the thing this seat was asked to reproduce — has no
   documented command. I reconstructed it from `golden_run.py`'s docstring, `runner.py`'s
   `add_argument` list, and the shape of §6.
2. **Which pricing snapshot.** §5 and §6 say `PRICING_SNAPSHOT_<id>.json`. Two exist
   (`2026-09-15` and `PS-2026-09-16`). Nothing says which is current; I chose the newer one.
3. **The judge and finalize mounts for the golden run.** §7 is written for `/lab/dryrun` and
   mounts the whole tree; I had to re-derive a layout that keeps `runner_only/` off the judge's
   filesystem (D-13).
4. **The `--tool-audit` file.** §6 passes `--tool-audit /lab/dryrun/TOOL_AUDIT.jsonl`; no command
   in the runbook creates it. It turns out `make_dryrun_fixture.py` writes it as a side effect,
   next to the fixture, which is not documented in the runbook or in that tool's argument list.
   `golden_run.py` writes its own. This is discoverable only by running the tool and reading its
   output.
5. **The test command is wrong.** §9 as written fails on a clean tree (D-10); the task-set mount
   is required. The 46-test `harness.test_harness` module is not mentioned.
6. **§4 tells you to build the manifest you are about to verify.** There is no frozen manifest to
   verify against (D-4). Nothing in the runbook says the manifest should have been committed, or
   which commit it should be bound to.
7. **Nothing says to pin a commit.** The runbook assumes a static tree. Mine moved three times
   (D-11). A reproduction procedure for a frozen artefact has to start with "check out commit X".
8. **§10's table is not entirely right.** `scorer_hash` is unmeasurable from records (D-7);
   `config_hash` is ambiguous (D-8); `latency_ms` is declared variable and is not (B-1);
   "raw-evidence hashes must match" is false on the documented dry-run path (D-2); `ran_at` is
   missing from both columns (E-4); and the table has no row for the `.pyc` contamination of the
   judge packet (D-3), which is neither a must-match nor a declared-variable — it simply is not
   contemplated.
9. **§1's reproduction claim is wrong** in the specific procedure it names (D-1).

Also still fragile, though not a runbook problem: `manifest.py verify` crashes with a raw
traceback on a missing manifest rather than reporting a clean failure, and its exit code is 0 in
two cases where a human reading the JSON would call it a failure (D-5, D-6).

---

## 9. What this establishes, and what it does not

**Establishes**

* The measured base image rebuilds byte-identically from the working tree, from a `git clone`
  checkout, and from a fully pruned build cache with the base re-pulled by digest — at two
  different tree states: `sha256:04d7fac6…` before `c7787b8`, and
  `sha256:93de0146b30113be44e7a398b5245dd9760420317b4f474fbf8239f6e346e969` at HEAD, 13 layers
  each, each reproduced on repeat builds. The move between the two is exactly one added file
  (§2.3.1) and nothing else.
* The self-derived `image_content_sha256` is stable across build routes, matches the recorded
  lock value, and moves exactly when the harness content moves.
* The golden end-to-end dry run reproduces exactly: 17/17 completed, 17/17 PASS, 0 zero-tolerance
  breaches, 5/5 cells, 0 unrecorded attempts — repeated on two images and against two states of
  the task set, with every record field, every judge packet, every score and every raw-evidence
  hash identical between two runs from identical inputs. **Under the v1.0.0 scoring rules**, for
  the reason in D-15.
* A 3-task subset produces records that are field-for-field identical to the corresponding
  records of the full run, including `blind_treatment_id`, across three different conditions.
* The scoring-integrity manifest detects a modified answer key, a modified corpus file, a modified
  `judge.py`, an added file and a deleted file, each in the correct group, each with exit 1.

**Does not establish**

* Nothing about token optimisation. Nothing about any candidate. Nothing about H1, H2, H3 or H4.
  No model was called; the token counts are constants in a Python file.
* Nothing about the v1.1.0 scoring rules. They were never reached (D-15). The absolute quality
  floors, the C citation-symmetry rule, the count rulings, the corpus-integrity gate and turn
  completeness are all untested by this run, and by the run it reproduces.
* Nothing about scoring *validity*. That correct answers pass the machinery says the machinery
  does not block a correct answer. It says nothing about whether a wrong answer would fail, or
  whether the answer keys are right — that is a different seat's claim
  (`INDEPENDENT_VERIFICATION.md`), not reproduced here.
* Nothing about the attestation chain as a whole, because three of its links are missing or
  broken: there is no committed integrity manifest (D-4), the verifier does not fail on a tampered
  manifest (D-5), and a file inside the frozen set escapes coverage entirely (D-6).
* Nothing about live-run behaviour: no provider, no network, no latency, no retries, no
  escalations, no cache state other than `cold`, no candidate installed in the image.
* Nothing about whether `04d7fac6` is still the right image. It is not, at HEAD (D-12).

**One-line verdict:** the run reproduces exactly, for the third seat running — and it reproduces
the *wrong rulebook* (D-15); the attestation around it is better than last round and still cannot
be verified end to end by an outsider; the "frozen" task set is not frozen; and the image digest
in circulation went stale *again*, during the very round that fixed the last instance of that.

---

## 10. Values for the coordinator to re-record

| Field | Measured value |
|---|---|
| Commit built | `37818868e93df5969e34047a73fa073b2c8abe40` |
| `image.manifest_digest` | `sha256:93de0146b30113be44e7a398b5245dd9760420317b4f474fbf8239f6e346e969` |
| `image.config_digest` | `sha256:d16d5ff08528e6c240d94d5fd5c99c7a30785a70e8fba717b8b06ce28cead6e2` |
| `image.layers` | `13` |
| `runtime.image_content_sha256` | `e54d54cb891c309669d27af69b1475213f05d45233b306ba1f652ab090cda8d4` |
| `runtime.dependency_manifest_sha256` | `8273d0e2144011927245abc2e701f009306fbf92166df665195fe6fbf031f0a9` (unchanged) |
| Supersede | `sha256:04d7fac698f8b1cedec9f26c8b2bbd9745f99839d9a2dcd4153b9efea5defa68` — 13 layers, identical except that it predates `harness/test_harness.py` |
| LG3 on the new digest | 8 / 8, `PASS`, negative control fails correctly (exit 1, check 5) |
| Golden run on the new digest | 17 / 17 completed, 17 / 17 PASS, 0 zero-tolerance breaches (`goldenP3`, §3.2) |
| Reproduced by | `git clone` checkout ×2 and the working tree ×1, all `93de0146…`; deterministic |
| Do **not** record | `sha256:4cd06ce8f76fe59af9d97d8f177a27f82f66afe39f3f8356d6100642f90a6e6a` — the same content built from a `git archive` checkout, which carries group-write permission bits (D-1) |

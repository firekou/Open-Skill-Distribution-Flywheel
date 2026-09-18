# Lab 001 — Runbook

**Every command needed to rebuild the environment, run the harness, score blind, finalize,
aggregate and verify — from a clean checkout.**

This file exists because the Reproduction Agent could not find one. It had to reverse-engineer
the mount layout from a path embedded inside a run record, and guess an entrypoint override. A
procedure only its author can follow is not a reproduction procedure.

All paths are relative to the repository root unless stated. `$LAB` below is
`benchmarks/token-efficiency-lab-001`.

```bash
LAB=benchmarks/token-efficiency-lab-001
```

---

## 0. Prerequisites

| | |
|---|---|
| Container runtime | Docker 29.x with BuildKit. **The daemon must be running** — `dockerd` being installed is not the same thing, and mistaking one for the other cost a whole round |
| Network | Needed **once**, to pull the base image by digest. The image build itself runs `--network=none`; every run runs `--network none` |
| Credentials | **None for anything in this file.** Live provider calls are LG4 and are not covered here |

```bash
docker info >/dev/null 2>&1 || nohup dockerd >/tmp/dockerd.log 2>&1 &
```

## 1. Build the environment

```bash
cd $LAB/environment
./build.sh atk-lab001:local /tmp/atk-lab001.tar
```

`build.sh` pins `SOURCE_DATE_EPOCH`, builds with `--network=none` from the vendored wheelhouse,
and exports an OCI tarball. It prints `image_id=` — **that digest is the reproducible artifact**.
The `.tar` bytes are not: two exports of the same image differ in archive metadata while every
blob inside is identical.

> **Build from a clone, not from `git archive`.** Measured by an independent seat (D-1):
> `git archive` emits mode `0664` where a clone emits `0644`, `COPY` records the mode, and the
> two therefore produce **different digests from byte-identical content**. An earlier version of
> this file asserted the opposite.

### Verify the build reproduces

```bash
docker system prune -a -f && docker buildx prune -a -f
docker pull python:3.11.15-slim-bookworm@sha256:d29f48a31a8b408ed19272ca1e7b10ebae13b240a27e862d3d4217c528e2e0c3
./build.sh atk-lab001:verify /tmp/verify.tar        # same image_id as before
```

The build is insensitive to working-tree caches: a tree containing `__pycache__` and a clean
`git archive` checkout produce the same digest. If yours does not, check that `.dockerignore`
still has its `**/` prefixes — without them the patterns match only the context root and silently
do nothing.

## 2. Environment self-check (LG3)

```bash
DIGEST=$(docker image inspect atk-lab001:local --format '{{.Id}}')
mkdir -p /tmp/lab-evidence

docker run --rm --network none \
  -e LAB_CONTAINER_DIGEST="$DIGEST" \
  -e LAB_ENVIRONMENT_ID=lab001-env-local \
  -v "$PWD/../tasks/TASK_SET_v1.1.0:/lab/tasks:ro" \
  -v /tmp/lab-evidence:/lab/evidence \
  atk-lab001:local
```

Expect 8 of 8 and `"lg3_verdict": "PASS"`.

**Negative control — this must FAIL.** A network check that only ever passes proves nothing:

```bash
docker run --rm --network bridge \
  -v "$PWD/../tasks/TASK_SET_v1.1.0:/lab/tasks:ro" -v /tmp/lab-evidence:/lab/evidence \
  atk-lab001:local ; echo "exit=$?   # expect 1, with check 5 failed"
```

## 3. Self-derived attestation

```bash
docker run --rm --network none atk-lab001:local python3 -m harness.attest "$DIGEST"
```

`container_digest` is a string an operator typed. `image_content_sha256` is computed inside the
running container and a flag cannot forge it. Record both; compare the second.

## 4. Scoring-integrity manifest

```bash
cd $LAB
python3 environment/harness/manifest.py build \
  --task-set tasks/TASK_SET_v1.1.0 --env environment \
  --manifest tasks/TASK_SET_v1.1.0/MANIFEST.json

python3 environment/harness/manifest.py verify \
  --task-set tasks/TASK_SET_v1.1.0 --env environment \
  --manifest tasks/TASK_SET_v1.1.0/MANIFEST.json
```

Separate `task_set_hash`, `answer_key_hash`, `scorer_hash` and `config_hash`. Detects modified,
**added** and **deleted** files. The manifest never hashes itself; the outer freeze record binds
its digest to the commit.

## 5. Pricing preflight — blocking

```bash
python3 environment/harness/pricing_preflight.py \
  --snapshot evidence/PRICING_SNAPSHOT_<id>.json \
  --models "anthropic/claude-sonnet-5,deepseek/deepseek-v4-pro"
```

Exit `1` and verdict `BLOCK` means a rate is missing for a model in the plan. **Blocked is a
result.** Do not trim the model list until it passes.

## 6. Harness dry run — NOT a pilot, NOT a benchmark

```bash
python3 tools/make_dryrun_fixture.py \
  --task-root tasks/TASK_SET_v1.1.0 --plan dryrun/PLAN.json \
  --snapshot evidence/PRICING_SNAPSHOT_<id>.json --out dryrun/FIXTURE.json

rm -rf dryrun/out && mkdir -p dryrun/out
docker run --rm --network none \
  -v "$PWD/tasks/TASK_SET_v1.1.0:/lab/tasks:ro" \
  -v "$PWD/dryrun:/lab/dryrun" \
  -v "$PWD/evidence/PRICING_SNAPSHOT_<id>.json:/lab/snapshot.json:ro" \
  atk-lab001:local python3 -m harness.runner \
    --task-root /lab/tasks --fixture /lab/dryrun/FIXTURE.json \
    --snapshot /lab/snapshot.json --out /lab/dryrun/out \
    --run-class dry_run --plan /lab/dryrun/PLAN.json \
    --tool-audit /lab/dryrun/TOOL_AUDIT.jsonl \
    --container-digest "$DIGEST" \
    --blind-salt lab001-dryrun-salt-2026-09-16
```

Every record is `run_class: "dry_run"`. `runner.py` **refuses** to write a `benchmark` or `pilot`
record from a synthetic fixture. Nothing here says anything about token optimisation: the counts
come from a seeded PRNG.

**`dryrun/PLAN.json` must carry an `attempt_id` per item (R4-03).** It did not, so the moment the
runner began requiring one this documented path failed before executing anything — while the
separately generated golden fixture still worked, which is why "the documented commands work" was
too broad a claim. `make_dryrun_fixture.py` now refuses a plan without them and writes
`dryrun/RUN_PLAN.json` beside the fixture for step 8.

**Expected outcome of the dry run: the runner completes 10/10 and the cells FAIL.** The fixture's
model outputs are synthetic, so the attempts genuinely fail quality and `harness.aggregate` exits
`1`. That is the correct result: this path proves the plumbing executes, not that anything scores
well. **The golden fixture (§8c) is the path where passing is the expected outcome.**

**`lab001-dryrun-salt-…` is a test salt, not a blinding secret.** A scored run gets a real salt
from the Runner's secret store — see the salt-custody section of `BLIND_EVALUATION_PROTOCOL.md`.

## 6b. The golden end-to-end run — the one a reproducer is asked to repeat

Not previously documented anywhere, which is why the last reproduction had to rebuild it from a
docstring. It builds a legitimate answer for all 17 tasks from the frozen keys and pushes it
through the real pipeline.

```bash
python3 tools/golden_run.py --task-root tasks/TASK_SET_v1.1.0 --out /tmp/golden
# writes PLAN.json, FIXTURE.json, TOOL_AUDIT.jsonl and CELL_PLAN.json

docker run --rm --network none \
  -v "$PWD/tasks/TASK_SET_v1.1.0:/lab/tasks:ro" -v /tmp/golden:/lab/out \
  -v "$PWD/evidence/PRICING_SNAPSHOT_PS-2026-09-16.json:/lab/snapshot.json:ro" \
  atk-lab001:local python3 -m harness.runner \
    --task-root /lab/tasks --fixture /lab/out/FIXTURE.json --snapshot /lab/snapshot.json \
    --out /lab/out/run --run-class dry_run --plan /lab/out/PLAN.json \
    --tool-audit /lab/out/TOOL_AUDIT.jsonl --container-digest "$DIGEST" \
    --blind-salt lab001-golden-salt-2026-09-16
```

**Expect 17/17 completed and, after scoring, 17/17 PASS — and check the version.** `17/17` alone
is not the acceptance criterion: it was `17/17` once before *because* the runner stamped the wrong
methodology version and the judge applied the older, more permissive rulebook. Assert both:

```bash
python3 - <<'EOF'
import json, glob
from collections import Counter
print(Counter(json.load(open(f))["methodology_version"] for f in glob.glob("/tmp/golden/run/judge_packets/*.json")))
EOF
# expect Counter({'1.1.0': 17})
```

`TOOL_AUDIT.jsonl` for workload A is written by `harness/corpus_reader.py`, a real audited reader
that reads the file and records the access in the same call. It used to be fabricated by this
tool, which is how "nothing in the lab can produce a workload-A corpus read" stayed invisible.

## 7. Score blind, then finalize

```bash
# D-13: mount ONLY the packet and score directories. Mounting the whole run directory puts
# runner_only/BLIND_MAPPING.json on the judge's path, three lines above the warning not to.
docker run --rm --network none \
  -v "$PWD/dryrun/out/judge_packets:/lab/packets:ro" \
  -v "$PWD/dryrun/out/judge_scores:/lab/scores" atk-lab001:local \
  python3 /lab/harness/judge.py --packets /lab/packets --scores /lab/scores

docker run --rm --network none -v "$PWD/dryrun:/lab/dryrun" atk-lab001:local \
  python3 -m harness.finalize \
    --records /lab/dryrun/out/records --scores /lab/dryrun/out/judge_scores
```

Finalize refuses a batch with any unscored packet, any record without a score, or any score that
declares no `outcome`.

**Never mount `dryrun/out/runner_only/` for the judge.** It holds the blind mapping.

## 8. Aggregate to cells

```bash
docker run --rm --network none -v "$PWD/dryrun:/lab/dryrun" atk-lab001:local \
  python3 -m harness.aggregate \
    --records /lab/dryrun/out/records --run-plan /lab/dryrun/RUN_PLAN.json
```

Denominator is **planned** attempts. A planned attempt with no record still counts against it.

**`--run-plan`, not `--plan` (R3-01).** The run plan supplies the denominators *and* the planned
attempt identities from one source. The old `--plan CELL_PLAN.json` form gave counts only, so
every cell came out `identity_verified: false` and **FAIL — on completely legitimate records**.
That form still exists for old fixtures and now **refuses to run without `--registry`**, rather
than quietly reporting a cell nobody checked.

**Each fixture aggregates against its OWN run plan**: the committed dry run against
`dryrun/RUN_PLAN.json` (above), the golden fixture against the `RUN_PLAN.json` that
`golden_run.py` writes into its output directory.

For the real experiment, pass the frozen plan:

```bash
    --records /lab/out/records --run-plan /lab/RUN_PLAN_v1.1.0.json
```

The report echoes `plan_hash` and `plan_source` so a result can be tied to the plan it was
measured against. **Do not aggregate dry-run records against `RUN_PLAN_v1.1.0.json`:** its 270
attempts are not the 17-task fixture's denominators, and every missing attempt would be reported
as a real shortfall.

## 8b. Tool audit — the agent under test must carry its run id

Workloads A and D score a zero-tolerance criterion from the server-written audit log, so the
server must be able to attribute each call to an attempt:

```bash
export LAB001_TOOL_AUDIT=/lab/out/TOOL_AUDIT.jsonl
export LAB001_RUN_ID=<the attempt's run_id>
```

Without `LAB001_RUN_ID` the Evidence Producer **refuses** the entry rather than guessing: an
unattributable call can neither be excluded nor counted, and dropping it would undercount
wrong-tool use. One shared log across attempts is fine — entries are filtered by run id, and
`seq` is continuous across processes.

## 9. Tests

```bash
# Both suites. The task-set mount is required - without it the judge suite cannot read the real
# task files and the count-rule cross-check silently checks nothing (it refuses to pass
# vacuously, so it fails rather than lying).
docker run --rm --network none \
  -v "$PWD/environment/harness:/lab/harness:ro" \
  -v "$PWD/tasks/TASK_SET_v1.1.0:/lab/tasks:ro" atk-lab001:local \
  sh -c 'cd /lab/harness && python3 -m unittest test_judge && python3 -m unittest test_harness'
```

Expect **240** judge tests and **54** harness tests. The harness suite includes the
runner → packet → judge **seam** tests: 240 judge tests all hand-build their packets, so none of
them covered the seam, and four defects lived there.

## 10. What must match on a reproduction, and what must not

Corrected after an independent reproduction found five rows wrong.

| Must match | Where it lives |
|---|---|
| Image manifest digest, `image_content_sha256` | build output, `harness.attest` |
| `model_output`, token counts, cost | run record |
| `quality_score`, `task_success`, `outcome`, `failure_reason` | run record, after `finalize` |
| `task_set_hash`, `answer_key_hash`, `scorer_hash`, `prompt_hash`, `run_config_hash` | run record |
| Raw-evidence hashes in each `MANIFEST.json` | evidence directory |
| The blind mapping, and `blind_treatment_id` **across any subset of a plan** | `runner_only/` |
| `corpus_hashes_before` / `_after` | run record's evidence |

| Expected to differ | Why |
|---|---|
| `written_at` in every `MANIFEST.json` | wall clock, and deliberately outside the hashed file |
| `ran_at` in `RUN_SUMMARY.json` | wall clock |
| `latency_ms` | wall clock — **usually** 0 on a replay fixture, but it is not guaranteed |
| The exported OCI tarball bytes | archive wrapper metadata; every blob inside is identical |
| Absolute paths that depend on the mount point | `raw_evidence_path` |

Three corrections worth stating rather than silently fixing:

- **`scorer_hash`** was named in this table and existed in no record. It is now in the schema and
  written by the runner (D-7).
- **`config_hash`** named two unrelated quantities — the run's configuration and the manifest's
  module coverage. The run record's is now `run_config_hash` (D-8).
- **Raw-evidence hashes did not actually reproduce** across output directories on the dry-run
  path, because the fixture baked its absolute output path into the file the runner hashed. Fixed
  and verified at 17/17 across two directories (D-2). Build artefacts (`__pycache__`, `.pyc`) are
  also excluded from `corpus_hashes` now — running the corpus once used to put 51 of them into
  every workload-A packet, and `corpus_modified` keys on the same map (D-3).

A difference outside the right-hand column is a finding, not rounding.

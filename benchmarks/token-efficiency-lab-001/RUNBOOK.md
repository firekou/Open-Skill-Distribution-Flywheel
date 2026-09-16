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

**`lab001-dryrun-salt-…` is a test salt, not a blinding secret.** A scored run gets a real salt
from the Runner's secret store — see the salt-custody section of `BLIND_EVALUATION_PROTOCOL.md`.

## 7. Score blind, then finalize

```bash
docker run --rm --network none -v "$PWD/dryrun:/lab/dryrun" atk-lab001:local \
  python3 /lab/harness/judge.py \
    --packets /lab/dryrun/out/judge_packets --scores /lab/dryrun/out/judge_scores

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
    --records /lab/dryrun/out/records --plan /lab/dryrun/CELL_PLAN.json
```

Denominator is **planned** attempts. A planned attempt with no record still counts against it.

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
docker run --rm --network none -v "$PWD/environment/harness:/lab/harness:ro" atk-lab001:local \
  sh -c 'cd /lab && python3 -m unittest harness.test_judge'
```

## 10. What must match on a reproduction, and what must not

| Must match | Expected to differ |
|---|---|
| Image manifest digest, `image_content_sha256` | `written_at` in every manifest |
| `model_output`, token counts, cost | Absolute paths that depend on the mount point |
| `quality_score`, `task_success`, `outcome`, `failure_reason` | `latency_ms` (wall clock) |
| `task_set_hash`, `answer_key_hash`, `scorer_hash`, `config_hash`, `prompt_hash` | The OCI tarball bytes |
| Raw-evidence hashes and the blind mapping | |

Raw-evidence hashes match across runs because volatile metadata lives in `MANIFEST.json`, which
is not itself hashed. Blind labels match across **any subset** of a plan because they are assigned
over the canonical condition set, not over the batch.

A difference outside the right-hand column is a finding, not rounding.

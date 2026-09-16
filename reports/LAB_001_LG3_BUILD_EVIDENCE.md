# Lab 001 — LG3 Build Evidence

**Date:** 2026-09-16 · **Gate:** LG3 — environment lock
**Previous verdict:** FAIL (2026-09-16, earlier same day) — *"no docker daemon; the image cannot
be built and the rebuild-reproducibility claim is unverified."*
**This verdict:** **PASS**

---

## Correction to the previous round, first

The earlier LG3 FAIL was recorded with the blocking reason *"no docker daemon in this
environment."* That reason was wrong, and it is worth being exact about how.

`/usr/bin/docker`, `/usr/bin/dockerd`, `/usr/bin/containerd` and `/usr/bin/runc` were all present
the whole time. What was absent was a **running daemon** and its socket. The probe that produced
the FAIL checked for `/var/run/docker.sock`, found nothing, and concluded the capability did not
exist. The correct conclusion was that the daemon had not been started. Starting it took one
command.

The gate verdict itself was not wrong — LG3 genuinely had not been demonstrated, and recording a
FAIL rather than waving it through was right. But the **reason** attached to the FAIL was
inaccurate, and an inaccurate reason sends the next round looking for a new environment instead
of starting a service. Recorded as a correction, not quietly fixed.

---

## Result

| Property | Value |
|---|---|
| **Image manifest digest** | `sha256:6edd71a6adff7eab4fca99b9b8fb2e9298c62256f5587ee9109cf02047811261` |
| **Image config digest** | `sha256:8e357881f18e4b74bfba85e7dbec869954f2a904fc9fa1676013f39fac09072b` |
| **Base image** | `python:3.11.15-slim-bookworm@sha256:d29f48a31a8b408ed19272ca1e7b10ebae13b240a27e862d3d4217c528e2e0c3` |
| **Layers** | 11 |
| **Runtime** | CPython 3.11.15, glibc 2.36, x86_64 |
| **Dependency manifest hash** | `93d9ecce47dada939398eed486029d76e1d8c58a512f0c2c0a98320008f892fd` |
| **Distributions installed** | 20 (16 from the lock + `pip`, `setuptools`, `wheel`, `packaging` from the base) |
| **Build engine** | Docker 29.3.1 / BuildKit, containerd snapshotter, overlayfs |
| **Build network** | `--network=none` — nothing is fetched at build time |
| **SOURCE_DATE_EPOCH** | `1789516800` (2026-09-16T00:00:00Z, the LG1 freeze date) |

Reproduce with:

```bash
cd benchmarks/token-efficiency-lab-001/environment
./build.sh atk-lab001:verify /tmp/verify.tar
# expect image_id=sha256:6edd71a6adff7eab4fca99b9b8fb2e9298c62256f5587ee9109cf02047811261
```

---

## The eight LG3 checks

Run inside the built image, `--network none`, task corpus mounted read-only
(`harness/selfcheck.py`). Full output: `benchmarks/token-efficiency-lab-001/evidence/lg3/SELFCHECK_REPORT.json`.

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Dockerfile builds | **PASS** | harness imports and executes inside the image |
| 2 | Dependency lock installs | **PASS** | 16 locked distributions, all at the locked version |
| 3 | Container digest obtainable | **PASS** | `sha256:6edd71a6adff…` passed in and recorded |
| 4 | Runtime version pinned | **PASS** | CPython 3.11.15 exactly, x86_64 |
| 5 | Egress policy applies | **PASS** | all 4 probe destinations unreachable |
| 6 | Task data mountable | **PASS** | mount present, readable, and **read-only as required** |
| 7 | Run record schema writable | **PASS** | valid record written; an invalid record was **rejected** |
| 8 | Raw evidence preserved | **PASS** | manifest verified, and tampering **detected** |

**8 passed, 0 failed.**

### Check 5 has a negative control

A check that passes when egress is blocked proves nothing unless it also fails when egress is
open. The same image was run again with `--network bridge`:

```
check 5 pass: False
detail: egress policy NOT applied - reachable: 1.1.1.1:443, pypi.org:443, github.com:443
overall verdict: FAIL
exit: 1
```

The check discriminates. Checks 7 and 8 carry the same property inline: 7 confirms the validator
**rejects** `cache_state: "unknown"`, and 8 confirms the manifest **detects** a single appended
space in a raw evidence file.

---

## Clean rebuild

The question LG3 exists to answer is not "does it build" but "does the same source produce the
same image on a machine that has never seen it." So:

1. Build 1 → digest recorded.
2. `docker system prune -a -f` and `docker buildx prune -a -f`. **Zero images, zero cache.**
3. Base image re-pulled by digest from an empty store.
4. Build 2 → digest compared.

### First attempt: digests did NOT match

| | Build 1 | Build 2 |
|---|---|---|
| Manifest digest | `sha256:b59d2174…` | `sha256:5c3d2b7e…` |
| Layers matching | **10 of 11 byte-identical** | **10 of 11 byte-identical** |
| Differing layer | `sha256:dd822f92…` (5,421,510 B) | `sha256:a2fa3cf5…` (5,421,518 B) |

An 8-byte difference in one layer — the `pip install` layer. Rather than shrug at it, it was
traced.

**Root cause, measured not guessed.** Both layers contain exactly 783 files with identical names.
The files that differ are all `.pyc` bytecode caches, each the **same size** as its counterpart.
Decoding one header:

```
build1: flags=0 source_mtime=1789552647 (2026-09-16 09:57:27Z) source_size=2750
build2: flags=0 source_mtime=1789552681 (2026-09-16 09:58:01Z) source_size=2750
differing byte offsets in this .pyc: [8]
bodies identical after header: True
```

One byte, at offset 8, inside the 16-byte `.pyc` header: the **source mtime**, which is the
build's wall clock. The compiled bytecode was identical; only the timestamp stamped into it
differed. The two builds were 34 seconds apart.

**Why `SOURCE_DATE_EPOCH` did not save us.** BuildKit's `rewrite-timestamp` rewrites *tar header*
mtimes. It cannot rewrite a timestamp embedded **inside a file's own bytes**. `PYTHONDONTWRITEBYTECODE=1`
did not help either: it governs the *interpreter*, and it was pip's install-time compile step
writing these files.

**Fix.** `pip install --no-compile`, plus an explicit sweep of any `__pycache__` the base image
carried. No bytecode cache is written at build time, and `PYTHONDONTWRITEBYTECODE=1` keeps the
interpreter from writing one at run time. Import is marginally slower on first use; nothing being
measured is import time.

### Second attempt: digests match

| | Build 3 | Build 4 (after full prune + re-pull) |
|---|---|---|
| **Manifest digest** | `sha256:6edd71a6adff…1261` | `sha256:6edd71a6adff…1261` |
| **Config digest** | `sha256:8e357881f18e…072b` | `sha256:8e357881f18e…072b` |
| **Layers** | 11 | 11 |
| **Blob set** | identical | identical |
| Dependency manifest | 20 distributions | identical, 20 distributions |
| Runtime version | CPython 3.11.15, glibc 2.36 | CPython 3.11.15, glibc 2.36 |

**The image reproduces bit for bit.**

### One honest caveat

The two **OCI tarball files** hash differently (`3ce676b4…` vs `4b19beee…`) even though the
images inside them are identical. The difference is in the archive wrapper — tar entry ordering
and metadata produced by the exporter — not in any blob: the blob file sets are identical and
both manifests are the same digest.

**So the reproducible artifact is the image manifest digest, not the tarball.** Anyone verifying
this build should compare `sha256:6edd71a6adff…`, not the `.tar`. Stating it the other way round
would be an overclaim.

---

## Defects this round found and fixed in the v1 environment spec

None of these were visible while the environment was specified but never built. All three were
found by building it.

| ID | Defect | Fix |
|---|---|---|
| **E019** | `requirements.lock.txt` pinned **3 of 16** distributions. The 13 transitive dependencies — `anyio`, `certifi`, `rpds-py`, `pydantic-core` and the rest — were unpinned and would drift between builds | Complete closure pinned and hash-pinned; 16 distributions, 16 hashes |
| **E020** | `RUN pip install --require-hashes ... \|\| pip install ...` — the `\|\|` fallback silently defeated hash verification on any failure. The hash check was decorative | Fallback removed. The build fails closed |
| **E021** | Install-time bytecode compilation embedded the build's wall clock in `.pyc` headers, making the image non-reproducible by 8 bytes | `--no-compile` plus a `__pycache__` sweep |

Two further hardening changes, from the Minimum Necessary Capability principle rather than from a
defect:

- **The `apt-get` layer is gone entirely.** It installed `git`, `curl`, `jq` and `ca-certificates`
  with loose version globs (`git=1:2.39.*`, `curl=*`) — four unpinned packages and a second
  source of drift. The base image already ships `ca-certificates`, and it ships **no** `git`,
  `curl`, `wget`, `jq`, `nc` or `ssh`. Candidate checkout happens in an unmeasured prep step
  outside this image, so none of them are needed inside it. A measured container that carries a
  general-purpose HTTP client is a container that can exfiltrate task content.
- **The build is hermetic.** The 16 wheels are vendored into the repository (3.6 MB) and
  installed with `--no-index --find-links`, so `docker build --network=none` succeeds. A build
  that reaches PyPI depends on PyPI still serving those exact artifacts in 2028.

---

## What LG3 PASS does and does not mean

**It means:** the environment is pinned by digest, builds from nothing on a machine with no
cache, reproduces the same digest, denies egress, and refuses to write a record it cannot
validate.

**It does not mean** any candidate has been executed — none has. It does not mean the benchmark
has run. It does not mean the harness has ever spoken to a model provider; it has not. And a
green self-check is not a product-quality claim about anything.

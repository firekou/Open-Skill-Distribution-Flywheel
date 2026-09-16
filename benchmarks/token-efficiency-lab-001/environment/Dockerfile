# ATK Token Efficiency Lab 001 — measured base environment.
#
# This image contains ATK's harness runtime ONLY.
#
# NO third-party candidate is installed here. Candidates are added per-run, from their pinned
# commit SHA in PINS.txt, built from source, only after their LG2 conditions are satisfied, and
# only inside a default-deny egress sandbox. Never from a vendor install.sh. Never from a
# moving branch.
#
# Minimum Necessary Capability (Decision 2, 2026-09-16 review):
#   The base carries no general-purpose network client and no shell fetch tooling. git, curl,
#   wget and jq are deliberately ABSENT. Candidate checkout happens in an unmeasured prep step
#   outside this image; anything inside the measured container that could reach the network
#   is an unnecessary capability and a measurement contaminant.
#
# Reproducibility properties:
#   - base image pinned by DIGEST, not by tag (a tag is mutable)
#   - no apt layer at all, so no unpinned Debian package can drift between builds
#   - the complete pip closure (16 distributions) is version-pinned AND hash-pinned
#   - --require-hashes with no fallback: the build FAILS CLOSED if any artifact differs
#
# Defects in the v1 spec that this file fixes (EVIDENCE_LEDGER E019, E020):
#   E019  base was pinned by tag; apt installed 4 packages with loose version globs;
#         only 3 of 16 pip distributions were pinned.
#   E020  `pip install --require-hashes ... || pip install ...` — the fallback silently
#         defeated the hash check on any failure, so hash verification was decorative.

FROM python:3.11.15-slim-bookworm@sha256:d29f48a31a8b408ed19272ca1e7b10ebae13b240a27e862d3d4217c528e2e0c3

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=UTC \
    LC_ALL=C.UTF-8 \
    LAB=token-efficiency-lab-001 \
    METHODOLOGY_VERSION=1.0.0

WORKDIR /lab

# Hermetic install. The wheelhouse is vendored in the repository, so this image builds with
# NO NETWORK AT ALL (`docker build --network=none`). That is deliberate:
#   - a build that reaches PyPI depends on PyPI still serving that exact artifact in 2028
#   - a build that reaches the network can be poisoned between the lock file and the install
#   - `--network=none` makes "the environment is pinned" checkable instead of asserted
# No `||` fallback. If a hash does not verify, the build MUST fail.
COPY requirements.lock.txt /lab/
COPY wheelhouse/ /lab/wheelhouse/
# --no-compile is REQUIRED for reproducibility, not an optimisation.
# pip compiles bytecode at install time by default, and a .pyc embeds the source file's mtime
# in its 16-byte header. Those mtimes are the build's wall clock, so two builds 34 seconds
# apart produce .pyc files with identical bodies and different headers - which changes the
# layer digest. BuildKit's rewrite-timestamp cannot fix this: it rewrites tar header mtimes,
# not timestamps embedded INSIDE a file's bytes. Measured, not assumed: see
# reports/LAB_001_LG3_BUILD_EVIDENCE.md, EVIDENCE_LEDGER E021.
# PYTHONDONTWRITEBYTECODE=1 above stops any .pyc being written at run time either.
RUN pip install --require-hashes --no-deps --no-index --no-compile \
        --find-links=/lab/wheelhouse -r /lab/requirements.lock.txt \
 && rm -rf /lab/wheelhouse \
 && find /usr/local/lib/python3.11 -name '__pycache__' -type d -prune -exec rm -rf {} + \
 && find /usr/local/lib/python3.11 -name '*.pyc' -delete

COPY run_record_schema.json /lab/
COPY harness/ /lab/harness/
COPY calibration/ /lab/calibration/
COPY pricing/ /lab/pricing/

# Evidence lands here. Mounted read-write at run time; task corpora are mounted read-only.
RUN mkdir -p /lab/evidence /lab/tasks

CMD ["python3", "-m", "harness.selfcheck"]

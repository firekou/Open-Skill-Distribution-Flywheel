# Lab 001 base environment. Pinned by digest at build time; recorded in ENVIRONMENT_LOCK.json.
#
# This image contains ATK's harness and runtimes ONLY.
# NO third-party candidate is installed here. Candidates are added per-run, from their pinned
# commit SHA, built from source, only after their LG2 conditions are satisfied, and only inside
# a default-deny egress sandbox. Never from a vendor install.sh, never from a moving branch.
FROM python:3.11.15-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LAB=token-efficiency-lab-001 \
    METHODOLOGY_VERSION=1.0.0

RUN apt-get update && apt-get install -y --no-install-recommends \
      git=1:2.39.* ca-certificates=* curl=* jq=* \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /lab
COPY requirements.lock.txt /lab/
RUN pip install --require-hashes -r requirements.lock.txt || \
    pip install -r requirements.lock.txt

COPY run_record_schema.json /lab/
CMD ["python3", "-c", "print('lab-001 base ready')"]

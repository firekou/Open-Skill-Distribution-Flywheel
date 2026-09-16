#!/usr/bin/env bash
# Build the Lab 001 measured base image, reproducibly.
#
#   ./build.sh <tag> <output-tarball>
#
# Two properties make this build checkable rather than merely asserted:
#
#   --network=none     nothing is fetched. Every dependency comes from the vendored
#                      wheelhouse, hash-verified against requirements.lock.txt.
#   SOURCE_DATE_EPOCH  layer mtimes are rewritten to a fixed instant. Without this, two
#                      builds of byte-identical content still produce different digests,
#                      and "the environment is reproducible" would be unfalsifiable.
#
# The image is exported as an OCI tarball rather than loaded directly, because BuildKit
# refuses to combine timestamp rewriting with the unpack step the direct docker exporter
# performs.
set -euo pipefail

TAG="${1:-atk-lab001:local}"
OUT="${2:-/tmp/atk-lab001.tar}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Fixed epoch = 2026-09-16T00:00:00Z, the LG1 methodology freeze date.
export SOURCE_DATE_EPOCH=1789516800

docker buildx build \
  --network=none \
  --build-arg SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" \
  --output "type=docker,name=${TAG},dest=${OUT},rewrite-timestamp=true" \
  --provenance=false \
  --sbom=false \
  --no-cache \
  -f "${HERE}/Dockerfile" \
  "${HERE}"

docker load -i "${OUT}" >/dev/null
echo "image_id=$(docker image inspect "${TAG}" --format '{{.Id}}')"
echo "tarball_sha256=$(sha256sum "${OUT}" | cut -d' ' -f1)"

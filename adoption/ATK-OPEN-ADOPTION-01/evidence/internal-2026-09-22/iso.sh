#!/bin/sh
# INTERNAL test wrapper: empty environment (no provider keys, no GitHub tokens) inside a new
# network namespace with loopback only. Not a qualifying independent reviewer sandbox.
# Usage: SCRATCH=/path/with/venv-and-lo_up.py ./iso.sh python3 local_check.py
: "${SCRATCH:?set SCRATCH to the directory holding venv/, home/ and lo_up.py}"
exec unshare --net --map-root-user sh -c '
  python3 "$0/lo_up.py" &&
  exec env -i HOME="$0/home" PATH="$0/venv/bin:/usr/bin:/bin" "$@"' "$SCRATCH" "$@"

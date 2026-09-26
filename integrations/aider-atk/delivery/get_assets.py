#!/usr/bin/env python3
"""Copy the reviewed Aider first-use assets out of this git repository.

Reads SOURCE_MANIFEST.json next to this file. For every entry it runs
`git show <commit>:<path>` in the current clone, checks the bytes against the
recorded SHA-256, and only then writes them under --out. Nothing is downloaded
by this script and nothing is executed; a missing commit is reported with the
exact `git fetch` command to run.

Exit codes
  0  every file written and verified
  1  a file's SHA-256 did not match (nothing further is written)
  2  a source commit is not present locally, or usage error
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def git(*args):
    return subprocess.run(["git", *args], capture_output=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="empty or new directory to write assets into")
    ap.add_argument("--manifest", default=os.path.join(HERE, "SOURCE_MANIFEST.json"))
    args = ap.parse_args(argv)

    manifest = json.load(open(args.manifest))
    missing = [c for c in manifest["fetch_commits"] if git("cat-file", "-e", f"{c}^{{commit}}").returncode != 0]
    if missing:
        print("missing source commits; run this in your clone, then retry:", file=sys.stderr)
        print("  git fetch origin " + " ".join(missing), file=sys.stderr)
        return 2
    if os.path.exists(args.out) and os.listdir(args.out):
        print(f"--out {args.out} is not empty; choose a new directory", file=sys.stderr)
        return 2

    blobs = []
    for f in manifest["files"]:
        r = git("show", f"{f['source_commit']}:{f['source_path']}")
        if r.returncode != 0:
            print(f"cannot read {f['source_commit'][:8]}:{f['source_path']}", file=sys.stderr)
            return 2
        got = hashlib.sha256(r.stdout).hexdigest()
        if got != f["sha256"]:
            print(f"SHA-256 MISMATCH {f['target']}: expected {f['sha256']} got {got}", file=sys.stderr)
            return 1
        blobs.append((f["target"], r.stdout))

    for target, data in blobs:
        dst = os.path.join(args.out, target)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as fh:
            fh.write(data)
        print(f"ok  {target}")
    print(f"{len(blobs)} files written to {args.out}, all SHA-256 verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())

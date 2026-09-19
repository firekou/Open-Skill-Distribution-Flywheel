#!/usr/bin/env python3
"""Stamp content_hash, and bind every APPROVED approval to the hash it approved.

Sealing is a separate step from authoring on purpose. The hash covers everything
except the approvals themselves, so an approval can commit to the content it saw
without altering it. Edit one character of a claim afterwards and every approval
on the package stops matching — which is the mechanical form of
`execution_scope.hash == reviewed_scope.hash`.

    python3 tools/seal_package.py <file> [...]          stamp and write
    python3 tools/seal_package.py --check <file> [...]  report drift, write nothing
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from validate_packages import canonical_hash  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    drift = 0
    for name in args.files:
        path = Path(name)
        pkg = json.loads(path.read_text(encoding="utf-8"))
        digest = canonical_hash(pkg)
        stale = pkg.get("content_hash") != digest
        if args.check:
            print(f"{'DRIFT' if stale else 'ok   '}  {path}  {digest}")
            drift += int(stale)
            continue
        pkg["content_hash"] = digest
        for ap_entry in pkg.get("approvals") or []:
            if ap_entry.get("decision") == "APPROVED":
                ap_entry["scope_hash"] = digest
        path.write_text(json.dumps(pkg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"sealed  {path}  {digest}")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())

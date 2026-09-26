#!/usr/bin/env python3
"""Validate ATK content packages and learning packages.

Two layers, deliberately separated, because they answer different questions:

  Layer 1  STRUCTURE  — does it match the JSON Schema?
                        Answers "is this well formed".
  Layer 2  SEMANTICS  — the P-rules below.
                        Answers "may this be published, and may an Agent adopt it".

  Structure passing is not content being true. `--json` reports the two
  separately for exactly this reason: a green structure check on a package whose
  claims nobody has checked looks identical, in a dashboard, to a checked one.

The P-rules, each one traceable to a written rule rather than to taste:

  P1  every claim's source_refs resolve to a declared source          (no sourceless claim)
  P2  evidence_state is on the ladder                                 (ATK_VERIFY_STANDARD v1)
  P3  publishable/published requires a valid_until and a non-empty unknowns list
  P4  an author may not approve, review or claim-check its own package (Verify rule 7;
      .claude/GOVERNANCE.md separation of powers)
  P5  retracted or expired packages may not be newly adopted          (--adopt)
  P6  content_hash must equal the recomputed hash, and every approval's
      scope_hash must equal it                                        (execution_gate:
      execution_scope.hash == reviewed_scope.hash)
  P7  a publishable learning package needs at least one test case
  P8  a retracted package must name what revoked or superseded it
  P9  a governance-risk learning package must fail closed
  P10 requires_atk_api_key must be false                              (ATK stays optional)
  P11 a decision rule may not rest only on REPORTED claims
  P12 a package may not supersede or revoke itself
  P13 quotes taken from a summarised rendering may not be OBSERVED or higher
  P14 named seats must exist in the seat registry                     (--seat-registry)

Usage:
    python3 tools/validate_packages.py <file-or-dir> [...]
    python3 tools/validate_packages.py --adopt --as-of 2026-09-16 <file>
    python3 tools/validate_packages.py --seat-registry agents/SEAT_REGISTRY.json <file>
    python3 tools/validate_packages.py --json <file>

Exit code 0 = every package passed. 1 = at least one BLOCK.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from jsonschema_mini import SchemaStore, UnsupportedKeyword, validate  # noqa: E402

SCHEMA_DIR = ROOT / "schemas"
SCHEMA_FOR = {"content": "content-package.schema.json", "learning": "learning-package.schema.json"}
PUBLISHED_STATES = {"publishable", "published"}
LADDER = ["REPORTED", "OBSERVED", "TESTED", "VERIFIED", "REPRODUCED"]


def canonical_hash(package: dict) -> str:
    """sha256 over the package minus content_hash and minus approvals.

    approvals are excluded so an approval can commit to a hash of the thing it
    approved without that act changing the hash. Everything else is inside, so
    editing any claim after approval invalidates every approval on it.
    """
    body = {k: v for k, v in package.items() if k not in ("content_hash", "approvals")}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def load_seat_ids(path: Path) -> set[str]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    return {seat for dept in registry["departments"].values() for seat in dept["seats"]}


def semantic_rules(pkg: dict, *, adopt: bool, as_of: str | None,
                   seat_ids: set[str] | None) -> list[tuple[str, str]]:
    """Returns [(rule_id, message)] — empty means every P-rule held."""
    fails: list[tuple[str, str]] = []
    status = pkg.get("status")
    kind = pkg.get("package_kind")
    claims = pkg.get("claims") or []
    sources = pkg.get("sources") or []
    source_ids = {s.get("source_id") for s in sources if isinstance(s, dict)}
    by_source_id = {s.get("source_id"): s for s in sources if isinstance(s, dict)}
    claim_state = {c.get("claim_id"): c.get("evidence_state") for c in claims if isinstance(c, dict)}

    # P1 no sourceless claim
    for c in claims:
        if not isinstance(c, dict):
            continue
        refs = c.get("source_refs") or []
        if not refs:
            fails.append(("P1", f"claim {c.get('claim_id')} carries no source_refs"))
        for ref in refs:
            if ref not in source_ids:
                fails.append(("P1", f"claim {c.get('claim_id')} cites undeclared source '{ref}'"))

    # P2 evidence state on the ladder
    for c in claims:
        if isinstance(c, dict) and c.get("evidence_state") not in LADDER:
            fails.append(("P2", f"claim {c.get('claim_id')} has evidence_state "
                                f"{c.get('evidence_state')!r}, which is not on the ladder"))

    # P3 publishable needs an expiry and a stated unknown
    if status in PUBLISHED_STATES:
        if pkg.get("valid_until") in (None, ""):
            fails.append(("P3", f"status '{status}' requires valid_until; content with no "
                                "expiry becomes a permanent assertion"))
        if not (pkg.get("unknowns") or []):
            fails.append(("P3", f"status '{status}' requires a non-empty unknowns list"))

    # P4 no self-approval
    authors = set((pkg.get("authorship") or {}).get("authored_by") or [])
    reviewers = set((pkg.get("authorship") or {}).get("reviewed_by") or [])
    overlap = authors & reviewers
    if overlap:
        fails.append(("P4", f"seat(s) {sorted(overlap)} appear as both author and reviewer"))
    for ap in pkg.get("approvals") or []:
        if not isinstance(ap, dict):
            continue
        if ap.get("role") != "author" and ap.get("seat_id") in authors:
            fails.append(("P4", f"seat '{ap.get('seat_id')}' authored this package and also "
                                f"issued the '{ap.get('role')}' decision on it"))
    for c in claims:
        if isinstance(c, dict) and c.get("checked_by") and c.get("checked_by") == c.get("authored_by"):
            fails.append(("P4", f"claim {c.get('claim_id')} was checked by its own author"))

    # P5 expired or retracted may not be adopted
    if status == "retracted":
        fails.append(("P5", "package is retracted") if adopt else
                     ("P5-note", "package is retracted (reported, not blocking outside --adopt)"))
    if as_of and pkg.get("valid_until") and pkg["valid_until"] < as_of:
        msg = f"valid_until {pkg['valid_until']} is before as-of date {as_of}"
        fails.append(("P5", msg) if adopt else ("P5-note", msg + " (expired)"))

    # P6 hash integrity, and approvals bound to the hash they approved
    expected = canonical_hash(pkg)
    if pkg.get("content_hash") != expected:
        fails.append(("P6", f"content_hash mismatch: recorded {pkg.get('content_hash')}, "
                            f"recomputed {expected}"))
    for ap in pkg.get("approvals") or []:
        if isinstance(ap, dict) and ap.get("decision") == "APPROVED" and ap.get("scope_hash") != expected:
            fails.append(("P6", f"approval by '{ap.get('seat_id')}' commits to scope_hash "
                                f"{ap.get('scope_hash')}, which is not this content"))

    if kind == "learning":
        # P7 a publishable learning package must carry tests
        if status in PUBLISHED_STATES and not (pkg.get("test_cases") or []):
            fails.append(("P7", f"status '{status}' requires at least one test case"))
        delivery = pkg.get("delivery") or {}
        # P9 governance packages fail closed
        if delivery.get("risk_class") == "governance" and \
                delivery.get("fail_mode_when_status_unreachable") != "fail_closed":
            fails.append(("P9", "a governance-risk package must fail closed when the "
                                "revocation status is unreachable"))
        # P10 ATK stays optional
        if delivery.get("requires_atk_api_key") is not False:
            fails.append(("P10", "requires_atk_api_key must be false; knowledge access may "
                                 "not be conditioned on buying ATK inference"))
        # P11 a rule may not rest only on REPORTED
        for rule in (pkg.get("method") or {}).get("decision_rules") or []:
            if not isinstance(rule, dict):
                continue
            refs = rule.get("claim_refs") or []
            unknown_refs = [r for r in refs if r not in claim_state]
            if unknown_refs:
                fails.append(("P11", f"rule {rule.get('rule_id')} cites unknown claim(s) {unknown_refs}"))
            states = [claim_state.get(r) for r in refs if r in claim_state]
            if states and set(states) == {"REPORTED"} and status in PUBLISHED_STATES:
                fails.append(("P11", f"rule {rule.get('rule_id')} rests only on REPORTED claims"))

    # P8 a retraction must name its cause
    lifecycle = pkg.get("lifecycle") or {}
    if status == "retracted" and not (lifecycle.get("revoked_by") or lifecycle.get("superseded_by")):
        fails.append(("P8", "a retracted package must name revoked_by or superseded_by"))

    # P12 no self-supersession
    for field in ("supersedes", "superseded_by", "revokes", "revoked_by"):
        if lifecycle.get(field) == pkg.get("package_id"):
            fails.append(("P12", f"lifecycle.{field} points at the package itself"))

    # P13 a summarised rendering cannot support OBSERVED or higher
    for c in claims:
        if not isinstance(c, dict):
            continue
        state = c.get("evidence_state")
        if state not in LADDER or LADDER.index(state) < LADDER.index("OBSERVED"):
            continue
        for ref in c.get("source_refs") or []:
            src = by_source_id.get(ref)
            if src and src.get("retrieval_mode") == "summarised_rendering":
                fails.append(("P13", f"claim {c.get('claim_id')} is {state} but source '{ref}' "
                                     "was only obtained as a summarised rendering"))

    # P14 named seats must exist
    if seat_ids is not None:
        named = set(authors) | set(reviewers)
        named |= {a.get("seat_id") for a in pkg.get("approvals") or [] if isinstance(a, dict)}
        named |= {lifecycle.get("review_owner")} if lifecycle.get("review_owner") else set()
        for seat in sorted(s for s in named if s):
            if seat.startswith("AM"):
                continue  # operating seats live in the VSL seat-map; checked by its own validator
            if seat not in seat_ids:
                fails.append(("P14", f"seat '{seat}' is not in the seat registry"))

    return fails


def check_file(path: Path, store: SchemaStore, *, adopt: bool, as_of: str | None,
               seat_ids: set[str] | None) -> dict:
    result = {"file": str(path), "structure": [], "semantics": [], "notes": []}
    try:
        pkg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result["structure"].append(f"not valid JSON: {exc}")
        result["verdict"] = "BLOCK"
        return result

    kind = pkg.get("package_kind")
    if kind not in SCHEMA_FOR:
        result["structure"].append(f"package_kind {kind!r} is not 'content' or 'learning'")
        result["verdict"] = "BLOCK"
        return result

    schema = store.load(SCHEMA_FOR[kind])
    try:
        result["structure"] = validate(pkg, schema, store, schema)
    except UnsupportedKeyword as exc:
        result["structure"] = [f"schema could not be evaluated: {exc}"]

    for rule_id, msg in semantic_rules(pkg, adopt=adopt, as_of=as_of, seat_ids=seat_ids):
        (result["notes"] if rule_id.endswith("-note") else result["semantics"]).append(
            f"{rule_id}: {msg}")

    result["verdict"] = "BLOCK" if (result["structure"] or result["semantics"]) else "PASS"
    result["package_id"] = pkg.get("package_id")
    result["status"] = pkg.get("status")
    return result


def collect(targets: list[str]) -> list[Path]:
    files: list[Path] = []
    for t in targets:
        p = Path(t)
        files.extend(sorted(p.rglob("*.json")) if p.is_dir() else [p])
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--adopt", action="store_true",
                    help="evaluate as a new adoption: retracted and expired packages BLOCK")
    ap.add_argument("--as-of", default=None, help="date used for expiry checks, YYYY-MM-DD")
    ap.add_argument("--seat-registry", default=None, help="path to agents/SEAT_REGISTRY.json")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    store = SchemaStore(SCHEMA_DIR)
    seat_ids = load_seat_ids(Path(args.seat_registry)) if args.seat_registry else None
    results = [check_file(f, store, adopt=args.adopt, as_of=args.as_of, seat_ids=seat_ids)
               for f in collect(args.targets)]

    if args.json:
        print(json.dumps({"results": results}, indent=2, ensure_ascii=False))
    else:
        for r in results:
            mark = "PASS " if r["verdict"] == "PASS" else "BLOCK"
            print(f"[{mark}] {r['file']}  ({r.get('package_id')} · {r.get('status')})")
            for e in r["structure"]:
                print(f"         structure  {e}")
            for e in r["semantics"]:
                print(f"         semantics  {e}")
            for e in r["notes"]:
                print(f"         note       {e}")
        blocked = sum(1 for r in results if r["verdict"] == "BLOCK")
        print(f"\n  {len(results) - blocked}/{len(results)} passed; {blocked} blocked")
        print("  structure passing is not content being true — layer 2 only checks what a "
              "rule can check.")
    return 1 if any(r["verdict"] == "BLOCK" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())

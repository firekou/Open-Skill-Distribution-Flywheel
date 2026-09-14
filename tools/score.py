#!/usr/bin/env python3
"""Validate and report skill_score across the ATK candidate registry.

Recomputes every total from its six components and fails loudly on mismatch, so a
hand-edited total can never silently drift from the reasoning that produced it.

Usage:
    python3 tools/score.py --registry registry/skill_registry.json
    python3 tools/score.py --top 10
    python3 tools/score.py --priority A
"""
import argparse
import json
import pathlib
import sys

DIMS = ("utility", "trend", "atk_fit", "distribution", "maintenance", "commercial")
MAX = dict(utility=25, trend=20, atk_fit=20, distribution=15, maintenance=10, commercial=10)
THRESHOLDS = ((80, "A"), (65, "B"), (50, "Watchlist"))


def priority(total: int) -> str:
    for cut, label in THRESHOLDS:
        if total >= cut:
            return label
    return "Ignore"


def validate(registry: dict) -> list[str]:
    errors = []
    seen = set()
    for c in registry["candidates"]:
        repo = c["repository"]
        if repo in seen:
            errors.append(f"{repo}: duplicate entry")
        seen.add(repo)

        s = c["score"]
        for d in DIMS:
            if d not in s:
                errors.append(f"{repo}: missing dimension '{d}'")
            elif not 0 <= s[d] <= MAX[d]:
                errors.append(f"{repo}: {d}={s[d]} outside 0..{MAX[d]}")

        expected = sum(s.get(d, 0) for d in DIMS)
        if s.get("total") != expected:
            errors.append(f"{repo}: total={s.get('total')} but components sum to {expected}")

        if c["priority"] != priority(expected):
            errors.append(
                f"{repo}: priority={c['priority']} but score {expected} implies "
                f"{priority(expected)}"
            )

        # License gate is an independent veto: Priority A must never sit at decision=review
        # unless the licence actually passed.
        lic = c["license"]
        if c["decision"] == "review" and lic["ruling"] != "PASS":
            errors.append(f"{repo}: decision=review but licence ruling={lic['ruling']}")
        if lic["verified"] and lic["spdx"] is None:
            errors.append(f"{repo}: licence marked verified but no SPDX id")
        if not lic["verified"] and c["decision"] not in ("blocked", "reject"):
            errors.append(
                f"{repo}: licence unverified but decision={c['decision']} "
                "(must be 'blocked')"
            )
    return errors


def bar(value: int, maximum: int, width: int = 10) -> str:
    filled = round(value / maximum * width)
    return "█" * filled + "·" * (width - filled)


def main() -> int:
    ap = argparse.ArgumentParser()
    root = pathlib.Path(__file__).resolve().parent.parent
    ap.add_argument("--registry", default=str(root / "registry" / "skill_registry.json"))
    ap.add_argument("--top", type=int, default=0, help="show the top N by score")
    ap.add_argument("--priority", help="filter to a priority band (A/B/Watchlist)")
    ap.add_argument("--eligible-only", action="store_true",
                    help="only candidates whose licence gate passed")
    args = ap.parse_args()

    registry = json.loads(pathlib.Path(args.registry).read_text(encoding="utf-8"))

    errors = validate(registry)
    if errors:
        print("REGISTRY VALIDATION FAILED", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"registry OK: {len(registry['candidates'])} candidates, all totals consistent\n")

    rows = registry["candidates"]
    if args.priority:
        rows = [c for c in rows if c["priority"] == args.priority]
    if args.eligible_only:
        rows = [c for c in rows if c["license"]["ruling"] == "PASS"]
    rows = sorted(rows, key=lambda c: -c["score"]["total"])
    if args.top:
        rows = rows[: args.top]

    print(f"{'#':>3}  {'REPOSITORY':<44} {'SCORE':>5} {'PRI':<9} {'LICENSE':<12} DECISION")
    print("-" * 104)
    for i, c in enumerate(rows, 1):
        lic = c["license"]["spdx"] or "UNVERIFIED"
        print(f"{i:>3}  {c['repository']:<44} {c['score']['total']:>5} "
              f"{c['priority']:<9} {lic:<12} {c['decision']}")

    if args.top and rows:
        print("\nDimension detail:")
        for c in rows:
            s = c["score"]
            print(f"\n  {c['repository']}  ({s['total']}/100, Priority {c['priority']})")
            for d in DIMS:
                print(f"    {d:<14} {s[d]:>3}/{MAX[d]:<3} {bar(s[d], MAX[d])}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # stdout closed early (e.g. piped to `head`) - not an error
        sys.stderr.close()
        raise SystemExit(0)

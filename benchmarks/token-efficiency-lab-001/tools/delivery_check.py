#!/usr/bin/env python3
"""Block delivery when a shipped artefact no longer describes the shipped code — R4-02 / R4-04.

The fourth review found the committed `MANIFEST.json` failing verification against its own
checkout, and a `METHODOLOGY_LOCK` document hash that had not been updated when the document was
edited. Both had been reported as PASS. Neither is a tampering story: both are what happens when
a fingerprint is generated once and the thing it fingerprints keeps moving.

**This verifies what is committed. It never regenerates and then reports the regeneration as
proof.** That distinction is the point: rebuilding a manifest on the spot and finding it matches
proves only that the builder is deterministic, which was never in doubt. `--refresh` exists to
update the artefacts deliberately, and it is a separate action a human takes and commits.

Exit 0 = every delivered artefact matches the tree. Exit 1 = it does not, and the drift is named.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

LAB = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB / "environment"))

from harness import manifest as mf  # noqa: E402
from harness.aggregate import PlannedAttempts  # noqa: E402

TASK_SET = LAB / "tasks/TASK_SET_v1.1.0"
ENV = LAB / "environment"
LOCK = LAB / "methodology/METHODOLOGY_LOCK_v1.1.0.json"


def check_manifest() -> dict:
    v = mf.verify(TASK_SET / "MANIFEST.json", TASK_SET, ENV)
    bad = {g: {k: d[k] for k in ("modified", "added", "deleted") if d.get(k)}
           for g, d in v["groups"].items() if not d["ok"]}
    return {"name": "scoring-integrity manifest", "ok": v["ok"], "detail": bad,
            "why": "a manifest that does not verify cannot say the scoring chain is unchanged"}


def check_lock() -> dict:
    lock = json.loads(LOCK.read_text())
    bad = []
    for rel, want in lock["documents"].items():
        path = LAB / rel
        if not path.exists():
            bad.append(f"{rel}: listed in the lock and missing from the tree")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != want:
            bad.append(f"{rel}: content differs from the hash the lock records")
    return {"name": "methodology lock", "ok": not bad, "detail": bad,
            "why": "the lock is the candidate's fingerprint; a stale entry makes it useless"}


def check_run_plans() -> dict:
    """Every run plan must enumerate exactly the attempts its own denominators claim (R3-01)."""
    bad = []
    for rel in ("RUN_PLAN_v1.1.0.json", "dryrun/RUN_PLAN.json"):
        path = LAB / rel
        if not path.exists():
            bad.append(f"{rel}: missing")
            continue
        plan = json.loads(path.read_text())
        try:
            reg = PlannedAttempts.from_run_plan(plan, source=rel)
        except Exception as exc:
            bad.append(f"{rel}: {exc}")
            continue
        for cell in plan["cells"]:
            want = cell.get("planned_attempts", 1)
            got = len(reg.cell_ids(cell["workload"], cell["condition"]))
            if want != got:
                bad.append(f"{rel}: {cell['workload']}/{cell['condition']} says {want} planned "
                           f"attempts and enumerates {got} ids")
    return {"name": "run plans self-consistent", "ok": not bad, "detail": bad,
            "why": "a plan that disagrees with itself makes every rate computed from it meaningless"}


def check_dry_run_plan() -> dict:
    """R4-03: the documented dry run must still be runnable."""
    plan = json.loads((LAB / "dryrun/PLAN.json").read_text())
    missing = [i.get("task_id") for i in plan if not i.get("attempt_id")]
    return {"name": "documented dry-run plan", "ok": not missing,
            "detail": {"items_without_attempt_id": missing},
            "why": "the runner requires attempt_id; without it this documented path cannot start"}


def refresh() -> None:
    mf.build(TASK_SET, ENV).save(TASK_SET / "MANIFEST.json")
    lock = json.loads(LOCK.read_text())
    lock["documents"] = {rel: hashlib.sha256((LAB / rel).read_bytes()).hexdigest()
                         for rel in lock["documents"]}
    LOCK.write_text(json.dumps(lock, indent=2) + "\n")
    print("regenerated MANIFEST.json and the lock document hashes. "
          "Commit them, then run this again WITHOUT --refresh to verify.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="verify delivered artefacts against the tree")
    ap.add_argument("--refresh", action="store_true",
                    help="regenerate the artefacts instead of checking them. A deliberate, "
                         "separate action; its output is not evidence of anything.")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.refresh:
        refresh()
        return 0

    checks = [check_manifest(), check_lock(), check_run_plans(), check_dry_run_plan()]
    ok = all(c["ok"] for c in checks)
    if a.json:
        print(json.dumps({"ok": ok, "checks": checks}, indent=2))
    else:
        for c in checks:
            print(f"{'PASS' if c['ok'] else 'FAIL'}  {c['name']}")
            if not c["ok"]:
                print(f"      {c['why']}")
                print(f"      {json.dumps(c['detail'])[:400]}")
        print("\nDELIVERY OK" if ok else
              "\nDELIVERY BLOCKED - a shipped artefact no longer describes the shipped code.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

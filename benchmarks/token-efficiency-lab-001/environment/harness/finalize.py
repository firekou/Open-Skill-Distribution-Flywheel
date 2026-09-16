"""Write Quality Judge scores back into run records — protocol step 4.

`BLIND_EVALUATION_PROTOCOL.md` says the harness writes a record with placeholder
`task_success=false` / `quality_score=0.0`, the judge scores the packet, and then "the record is
updated with the returned values". Nothing implemented that last step: every dry-run record kept
its placeholder. It was invisible because every genuine score in a synthetic dry run is also
0.0 — in a real run the records would have silently reported every run as a scored failure
(Reproduction Agent, WOULD-INVALIDATE 7).

This module is that step, and it enforces the ordering the protocol requires rather than
assuming it: it refuses to finalize a batch in which any packet is unscored, because a
partially-finalized batch is exactly the shape of "score the ones you like, then peek".
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from .record import validate


class FinalizeError(RuntimeError):
    pass


def finalize(records_dir: pathlib.Path, scores_dir: pathlib.Path) -> dict:
    records_dir = pathlib.Path(records_dir)
    scores_dir = pathlib.Path(scores_dir)

    scores = {}
    for p in scores_dir.glob("*.json"):
        if p.name.startswith("_"):
            continue
        d = json.loads(p.read_text())
        scores[d["packet_id"]] = d

    unscored = [pid for pid, s in scores.items() if s.get("quality_score") is None]
    if unscored:
        raise FinalizeError(
            f"refusing to finalize: {len(unscored)} packet(s) carry no quality_score. "
            "A partially scored batch must not be written back or un-blinded."
        )

    import hashlib

    updated, missing = [], []
    for rp in sorted(records_dir.glob("*.json")):
        rec = json.loads(rp.read_text())
        pid = hashlib.sha256(f"{rec['run_id']}|{rec['task_id']}".encode()).hexdigest()[:16]
        s = scores.get(pid)
        if s is None:
            missing.append(rec["run_id"])
            continue
        if s["task_id"] != rec["task_id"]:
            raise FinalizeError(
                f"packet {pid} scores task {s['task_id']} but record {rec['run_id']} is "
                f"task {rec['task_id']}; the mapping is wrong and nothing may be written back"
            )
        rec["quality_score"] = float(s["quality_score"])
        rec["task_success"] = bool(s["task_success"])
        rec["quality_judged_before_cost"] = True
        if s.get("failure_reason"):
            rec["failure_reason"] = s["failure_reason"]
        validate(rec)
        rp.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        updated.append(rec["run_id"])

    if missing:
        # A record with no score is not silently left at its placeholder. Placeholder 0.0 is
        # indistinguishable from a genuine zero, and that ambiguity is the whole problem.
        raise FinalizeError(
            f"refusing to finalize: {len(missing)} record(s) have no matching score: "
            + ", ".join(missing[:5])
        )

    return {
        "records_finalized": len(updated),
        "scores_read": len(scores),
        "passed": sum(1 for pid in scores if scores[pid]["task_success"]),
        "zero_tolerance_breaches": sum(
            1 for pid in scores if scores[pid].get("zero_tolerance_breached")
        ),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="write judge scores back into run records")
    ap.add_argument("--records", required=True)
    ap.add_argument("--scores", required=True)
    args = ap.parse_args(argv)
    print(json.dumps(finalize(pathlib.Path(args.records), pathlib.Path(args.scores)), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

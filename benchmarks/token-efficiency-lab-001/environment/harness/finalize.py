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

    # ADV-G: the "refusing to finalize" check for records with no score used to run AFTER the
    # write loop, so a batch missing one score had already had every earlier record rewritten by
    # the time it raised. The docstring promised a batch that refuses; the code delivered a
    # half-written batch plus an exception. Resolve the whole batch first, write only once every
    # record in it has a score that matches it.
    pairs, missing = [], []
    for rp in sorted(records_dir.glob("*.json")):
        rec = json.loads(rp.read_text())
        pid = hashlib.sha256(f"{rec['run_id']}|{rec['task_id']}".encode()).hexdigest()[:16]
        s = scores.get(pid)
        if s is None:
            missing.append(rec["run_id"])
            continue
        pairs.append((rp, rec, pid, s))

    if missing:
        # A record with no score is not silently left at its placeholder. Placeholder 0.0 is
        # indistinguishable from a genuine zero, and that ambiguity is the whole problem.
        raise FinalizeError(
            f"refusing to finalize: {len(missing)} record(s) have no matching score: "
            + ", ".join(missing[:5]) + ". Nothing has been written.")

    # ADV-G: `packet_id` is derived from run_id|task_id alone, so a score produced by a DIFFERENT
    # scorer build or under a different methodology version carries the same id and used to be
    # written back without complaint - the same class of defect as the version mis-stamp, one
    # stage later. Both sides must agree on the rulebook and on the scorer that applied it.
    mismatched = []
    for _, rec, pid, s in pairs:
        if s["task_id"] != rec["task_id"]:
            raise FinalizeError(
                f"packet {pid} scores task {s['task_id']} but record {rec['run_id']} is "
                f"task {rec['task_id']}; the mapping is wrong and nothing may be written back"
            )
        smv = (s.get("detail") or {}).get("methodology_version")
        rmv = rec.get("methodology_version")
        if smv and rmv and smv != rmv:
            mismatched.append(
                f"{rec['run_id']}: record declares {rmv}, its score was produced under {smv}")
        shash, rhash = s.get("scorer_hash"), rec.get("scorer_hash")
        if shash and rhash and shash != rhash:
            mismatched.append(
                f"{rec['run_id']}: score came from scorer {shash[:12]}, record ran against "
                f"{rhash[:12]}")
    if mismatched:
        raise FinalizeError(
            f"refusing to finalize: {len(mismatched)} record(s) do not match the score written "
            "for them: " + "; ".join(mismatched[:5]) + ". Nothing has been written. A score and "
            "the record it lands on must come from the same rulebook and the same scorer.")

    updated = []
    for rp, rec, pid, s in pairs:
        rec["quality_score"] = float(s["quality_score"])
        rec["task_success"] = bool(s["task_success"])
        rec["quality_judged_before_cost"] = True
        # D-9: this used to be `if s.get("failure_reason")`, so a PASS - which correctly has
        # none - left the runner's placeholder in place and all 17 passing records read
        # "awaiting Quality Judge score". The judge's answer is authoritative either way,
        # including when its answer is "no reason, it passed".
        rec["failure_reason"] = s.get("failure_reason") or None
        # ADV-D: the judge flags possible constraint violations that structural detection cannot
        # decide. Finalize dropped the flag, so the aggregator could never gate on it and a
        # result nobody had ruled on was published as a clean PASS. It travels with the record.
        rec["pending_adjudication"] = bool(s.get("pending_adjudication"))

        # v1.1.0 section 6.2. The judge decides which of the three outcomes this attempt had; the
        # runner's placeholder is replaced here. A corpus modification already failed the attempt
        # at run time (RT-08) and the judge cannot overturn it.
        if rec.get("corpus_modified"):
            rec["outcome"] = "FAIL_QUALITY"
        elif s.get("outcome") in ("PASS", "FAIL_QUALITY", "INVALID"):
            rec["outcome"] = s["outcome"]
        else:
            # A scorer that does not declare an outcome must not be silently interpreted.
            raise FinalizeError(
                f"score for packet {pid} carries no recognised `outcome`. Inferring it from "
                "task_success would collapse INVALID into FAIL_QUALITY, which is the distinction "
                "between 'it failed' and 'we could not measure it'."
            )
        validate(rec)
        rp.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        updated.append(rec["run_id"])

    return {
        "records_finalized": len(updated),
        "scores_read": len(scores),
        "passed": sum(1 for pid in scores if scores[pid]["task_success"]),
        "zero_tolerance_breaches": sum(
            1 for pid in scores if scores[pid].get("zero_tolerance_breached")
        ),
        "pending_adjudication": sorted(
            rec["run_id"] for _, rec, _, _ in pairs if rec.get("pending_adjudication")
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

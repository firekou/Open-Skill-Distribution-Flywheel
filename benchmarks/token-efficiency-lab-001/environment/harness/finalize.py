"""Write Quality Judge scores back into run records — protocol step 4.

`BLIND_EVALUATION_PROTOCOL.md` says the harness writes a record with placeholder
`task_success=false` / `quality_score=0.0`, the judge scores the packet, and then "the record is
updated with the returned values". Nothing implemented that last step: every dry-run record kept
its placeholder. It was invisible because every genuine score in a synthetic dry run is also
0.0 — in a real run the records would have silently reported every run as a scored failure
(Reproduction Agent, WOULD-INVALIDATE 7).

This module is that step, and it enforces the ordering the protocol requires rather than
assuming it: every record in the batch is resolved and schema-checked BEFORE any file is written, because a
partially-finalized batch is exactly the shape of "score the ones you like, then peek".

What this does and does not guarantee is stated exactly in `write_guarantee`: whole-batch
validation before any write, and no torn file. It is **not** a multi-file transaction.
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
    # R4-06: these comparisons used to fire only when BOTH sides carried the field, and the judge
    # wrote none of them - so on every real batch the check silently passed. "Absent means fine"
    # is the same shape as the missing-cost defect: the safe-looking default is the one that lets
    # an unbound result through. Provenance is now REQUIRED, and its absence is a refusal.
    REQUIRED_SCORE_PROVENANCE = ("scorer_hash", "methodology_version", "packet_digest")
    missing_prov = []
    for _, rec, pid, s in pairs:
        absent = [k for k in REQUIRED_SCORE_PROVENANCE if not s.get(k)]
        if absent:
            missing_prov.append(f"{rec.get('run_id')}: score carries no {', '.join(absent)}")
    if missing_prov:
        raise FinalizeError(
            f"refusing to finalize: {len(missing_prov)} score(s) carry no provenance: "
            + "; ".join(missing_prov[:5]) + ". **Nothing has been written.** A score that does "
            "not say which scorer produced it, under which methodology version, over which "
            "packet, cannot be bound to the run it is written into.")

    mismatched = []
    for _, rec, pid, s in pairs:
        if s["task_id"] != rec["task_id"]:
            raise FinalizeError(
                f"packet {pid} scores task {s['task_id']} but record {rec['run_id']} is "
                f"task {rec['task_id']}; the mapping is wrong and nothing may be written back"
            )
        # R4-06: unconditional now. A record with no methodology_version or scorer_hash is
        # itself the failure - it cannot be shown to belong to this build.
        smv = s.get("methodology_version") or (s.get("detail") or {}).get("methodology_version")
        rmv = rec.get("methodology_version")
        if not rmv:
            mismatched.append(f"{rec['run_id']}: record declares no methodology_version")
        elif smv != rmv:
            mismatched.append(
                f"{rec['run_id']}: record declares {rmv}, its score was produced under {smv}")
        shash, rhash = s.get("scorer_hash"), rec.get("scorer_hash")
        if not rhash:
            mismatched.append(f"{rec['run_id']}: record names no scorer_hash")
        elif shash != rhash:
            mismatched.append(
                f"{rec['run_id']}: score came from scorer {shash[:12]}, record ran against "
                f"{rhash[:12]}")
    if mismatched:
        raise FinalizeError(
            f"refusing to finalize: {len(mismatched)} record(s) do not match the score written "
            "for them: " + "; ".join(mismatched[:5]) + ". Nothing has been written. A score and "
            "the record it lands on must come from the same rulebook and the same scorer.")

    # R2-03. The previous fix hoisted only the MISSING-SCORE check out of the write loop and
    # the report called the result "made atomic". It was not: the outcome check and
    # `validate(rec)` still ran per record, inside the loop, after earlier records had already
    # been written. Two records, the second carrying an unrecognised outcome, raised
    # FinalizeError with the first record already rewritten on disk.
    #
    # Phase 1 resolves and validates EVERY record in memory. Nothing touches the filesystem
    # until all of them pass.
    resolved, errors = [], []
    for rp, rec, pid, s in pairs:
        rec = dict(rec)
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
        # The score's own view of what it scored, carried into the record so the binding is
        # auditable after the fact rather than only at finalize time.
        rec["scored_packet_digest"] = s.get("packet_digest")

        # v1.1.0 section 6.2. The judge decides which of the three outcomes this attempt had; the
        # runner's placeholder is replaced here. A corpus modification already failed the attempt
        # at run time (RT-08) and the judge cannot overturn it.
        if rec.get("corpus_modified"):
            rec["outcome"] = "FAIL_QUALITY"
        elif s.get("outcome") in ("PASS", "FAIL_QUALITY", "INVALID"):
            rec["outcome"] = s["outcome"]
        else:
            # A scorer that does not declare an outcome must not be silently interpreted.
            errors.append(
                f"score for packet {pid} carries no recognised `outcome` ({s.get('outcome')!r}). "
                "Inferring it from task_success would collapse INVALID into FAIL_QUALITY, which "
                "is the distinction between 'it failed' and 'we could not measure it'")
            continue
        try:
            validate(rec)
        except Exception as exc:  # the record schema decides what a record may say
            errors.append(f"{rec.get('run_id')}: record rejected by the schema after scoring: {exc}")
            continue
        resolved.append((rp, rec))

    if errors:
        raise FinalizeError(
            f"refusing to finalize: {len(errors)} record(s) did not resolve cleanly: "
            + "; ".join(errors[:5]) + ". **Nothing has been written.** Every record in the batch "
            "is resolved and schema-checked before any file is touched.")

    # Phase 2 writes. Each file is written to a temporary neighbour and renamed, so no single
    # record is ever left half-written.
    #
    # This is NOT a multi-file transaction, and is deliberately not described as one. If the
    # process dies between two renames, some records are finalized and some are not. Making that
    # genuinely all-or-nothing needs a new batch directory plus a single publish marker, which is
    # a change to how records are stored, not to this function. Until then the guarantee this
    # function offers is exactly: **whole-batch validation before any write, and no torn file.**
    updated = []
    for rp, rec in resolved:
        tmp = rp.with_suffix(rp.suffix + ".tmp")
        tmp.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        tmp.replace(rp)
        updated.append(rec["run_id"])

    return {
        "records_finalized": len(updated),
        "scores_read": len(scores),
        "passed": sum(1 for pid in scores if scores[pid]["task_success"]),
        "zero_tolerance_breaches": sum(
            1 for pid in scores if scores[pid].get("zero_tolerance_breached")
        ),
        "pending_adjudication": sorted(
            rec["run_id"] for _, rec in resolved if rec.get("pending_adjudication")
        ),
        "write_guarantee": (
            "whole-batch validation before any write; per-file temp+rename so no file is torn. "
            "NOT a multi-file transaction: a crash between renames leaves a partially finalized "
            "batch."),
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

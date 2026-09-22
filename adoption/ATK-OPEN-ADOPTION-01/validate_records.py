#!/usr/bin/env python3
"""Check adoption records against the minimal rules. Stdlib only, offline.

    python3 validate_records.py records/*.json

Checks the schema's required fields and enums, plus the three rules a schema
cannot express and that decide what a record is allowed to claim:

1. An EXTERNAL_* class needs operator_external == true and operator_evidence.
   Without them the honest class is UNVERIFIED.
2. INTERNAL_AGENT_TEST must have operator_external == false and route INTERNAL:
   our own agent finding the asset is an internal discovery test, whatever the
   session or model.
3. PUBLIC_DISCOVERY / DIRECTORY_DISCOVERY need discovery_detail (the query or
   entry and the result position). A discovery claim without the query is not
   checkable.

Exit 0 when every record passes, 1 otherwise. Prints problems only.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "adoption-record.schema.json").read_text(encoding="utf-8"))


def check(rec: dict) -> list:
    errs = []
    props = SCHEMA["properties"]
    for key in SCHEMA["required"]:
        if key not in rec:
            errs.append(f"missing {key}")
    for key in rec:
        if key not in props:
            errs.append(f"unknown field {key}")
    for key, spec in props.items():
        if key in rec and "enum" in spec and rec[key] not in spec["enum"]:
            errs.append(f"{key}={rec[key]!r} not in {spec['enum']}")
    for key in ("commands", "blockers", "evidence_urls"):
        if key in rec and not isinstance(rec[key], list):
            errs.append(f"{key} must be a list")
    for key in ("exit_code", "duration_minutes"):
        v = rec.get(key)
        if key in rec and not (v == "unknown" or (isinstance(v, (int, float)) and not isinstance(v, bool))):
            errs.append(f"{key} must be a number or 'unknown'")
    sha = rec.get("code_sha", "")
    if "code_sha" in rec and not (len(sha) == 40 and all(c in "0123456789abcdef" for c in sha)):
        errs.append("code_sha must be a full 40-char lowercase SHA")

    cls = rec.get("source_class", "")
    if cls.startswith("EXTERNAL_"):
        if rec.get("operator_external") is not True:
            errs.append("EXTERNAL_* requires operator_external == true (else use UNVERIFIED)")
        if not rec.get("operator_evidence"):
            errs.append("EXTERNAL_* requires operator_evidence")
    if cls == "INTERNAL_AGENT_TEST":
        if rec.get("operator_external") is not False:
            errs.append("INTERNAL_AGENT_TEST requires operator_external == false")
        if rec.get("discovery_route") != "INTERNAL":
            errs.append("INTERNAL_AGENT_TEST requires discovery_route INTERNAL")
    if cls.endswith("_DISCOVERED_AGENT") or cls.endswith("_DISCOVERED_HUMAN"):
        if rec.get("discovery_route") not in ("PUBLIC_DISCOVERY", "DIRECTORY_DISCOVERY"):
            errs.append("*_DISCOVERED_* requires a PUBLIC_ or DIRECTORY_DISCOVERY route")
    if rec.get("discovery_route") in ("PUBLIC_DISCOVERY", "DIRECTORY_DISCOVERY") and not rec.get("discovery_detail"):
        errs.append("discovery route requires discovery_detail")
    if rec.get("success") is True and rec.get("result") != "SUCCESS":
        errs.append("success true but result is not SUCCESS")
    return errs


def main(argv) -> int:
    if not argv:
        print("usage: validate_records.py RECORD.json [...]", file=sys.stderr)
        return 2
    bad = 0
    for p in argv:
        try:
            rec = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"{p}: unreadable: {type(e).__name__}")
            bad += 1
            continue
        errs = check(rec)
        for e in errs:
            print(f"{p}: {e}")
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

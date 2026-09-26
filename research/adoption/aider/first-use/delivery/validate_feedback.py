#!/usr/bin/env python3
"""Validate ATK Aider first-use feedback records.

Usage
  python validate_feedback.py --schema PATH/FEEDBACK_SCHEMA.json RECORD.json [RECORD.json ...]

The schema must be the reviewed v1.1.0 file from PR19 commit
a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41 (SHA-256 pinned below); any other
file is refused. On top of the schema, one cross-field rule the schema cannot
express is enforced: when task.tests_total and task.tests_failed are both
integers, tests_failed may not exceed tests_total (PR19 R2 condition P2-01).

Output never contains record values: only the file name, the JSON Pointer of
the offending location and the kind of error. Malformed JSON is reported by
line and column only.

Exit codes
  0  every record is valid
  1  at least one record is invalid or not parseable
  2  usage error, unreadable file, or schema does not match the pinned hash

Requires jsonschema==4.26.0 (see requirements.txt).
"""

import argparse
import hashlib
import json
import sys

SCHEMA_SHA256 = "b3531cc41660aad7139922d4201dd449c51a01a04b1fd06e815b6c01f986904c"
SCHEMA_SOURCE = "a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41:research/adoption/aider/first-use/FEEDBACK_SCHEMA.json"


def pointer(parts):
    if not parts:
        return "/"
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def leaf_errors(err):
    """Yield (path, keyword) for an error, descending into combinator context."""
    if err.context:
        for sub in err.context:
            yield from leaf_errors(sub)
    else:
        yield tuple(err.absolute_path), err.validator


def cross_field_errors(record):
    task = record.get("task") if isinstance(record, dict) else None
    if isinstance(task, dict):
        total, failed = task.get("tests_total"), task.get("tests_failed")
        if (isinstance(total, int) and not isinstance(total, bool)
                and isinstance(failed, int) and not isinstance(failed, bool)
                and failed > total):
            yield ("task", "tests_failed"), "failed_exceeds_total"


def check_record(validator, record):
    found = set()
    for err in validator.iter_errors(record):
        found.update(leaf_errors(err))
    found.update(cross_field_errors(record))
    return sorted(found, key=lambda e: (pointer(e[0]), e[1]))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate first-use feedback records.")
    ap.add_argument("--schema", required=True)
    ap.add_argument("records", nargs="+")
    args = ap.parse_args(argv)

    try:
        raw = open(args.schema, "rb").read()
    except OSError:
        print(f"ERROR cannot read schema: {args.schema}", file=sys.stderr)
        return 2
    if hashlib.sha256(raw).hexdigest() != SCHEMA_SHA256:
        print(f"ERROR schema is not the pinned file {SCHEMA_SOURCE} (SHA-256 mismatch)", file=sys.stderr)
        return 2

    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        print("ERROR jsonschema is not installed; pip install -r requirements.txt", file=sys.stderr)
        return 2
    schema = json.loads(raw)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    status = 0
    for path in args.records:
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            print(f"ERROR cannot read record file: {path}", file=sys.stderr)
            return 2
        try:
            record = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"INVALID {path}: malformed JSON (line {e.lineno}, column {e.colno})")
            status = 1
            continue
        errors = check_record(validator, record)
        if errors:
            status = 1
            for parts, kind in errors:
                print(f"INVALID {path}: {pointer(parts)} {kind}")
        else:
            print(f"VALID   {path}")
    return status


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Check adoption records against the schema and the rules a schema cannot express.
Stdlib only, offline.

    python3 validate_records.py records/*.json

Two layers, both blocking:

**Schema layer** — a small JSON Schema subset, covering exactly the keywords
`adoption-record.schema.json` actually uses: `required`, `additionalProperties: false`,
`type`, `enum`, `const`, `pattern`, `items`, `minItems`, `minimum`, `anyOf`.
Booleans are not integers here: `operator_external: 1` is a type error, not `true`.

**Semantic layer** — the three rules a schema cannot express, which decide what a
record is allowed to claim:

1. An EXTERNAL_* class needs operator_external == true and operator_evidence.
   Without them the honest class is UNVERIFIED.
2. INTERNAL_AGENT_TEST must have operator_external == false and route INTERNAL:
   our own agent finding the asset is an internal discovery test, whatever the
   session or model.
3. PUBLIC_DISCOVERY / DIRECTORY_DISCOVERY need discovery_detail (the query or
   entry and the result position). A discovery claim without the query is not
   checkable.

Plus `code_sha` must be a full 40-char lowercase SHA, and `success: true` requires
`result: SUCCESS`.

Exit 0 when every record passes, 1 otherwise. Prints problems only.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "adoption-record.schema.json").read_text(encoding="utf-8"))

_TYPES = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _same(a, b) -> bool:
    """Equality that does not let True pass for 1, or 1 for True."""
    return a == b and isinstance(a, bool) == isinstance(b, bool)


def schema_errors(value, spec: dict, where: str) -> list:
    """Validate one value against the JSON Schema subset this schema uses."""
    errs = []
    if "anyOf" in spec:
        if not any(not schema_errors(value, sub, where) for sub in spec["anyOf"]):
            errs.append(f"{where}={value!r} matches none of the allowed forms")
        return errs
    if "enum" in spec and not any(_same(value, opt) for opt in spec["enum"]):
        errs.append(f"{where}={value!r} not in {spec['enum']}")
    if "const" in spec and not _same(value, spec["const"]):
        errs.append(f"{where}={value!r} must be {spec['const']!r}")
    if "type" in spec:
        check = _TYPES.get(spec["type"])
        if check is None:
            errs.append(f"{where}: schema uses unsupported type {spec['type']!r}")
        elif not check(value):
            errs.append(f"{where}={value!r} must be {spec['type']}")
            return errs  # every keyword below assumes the type held
    if "pattern" in spec and isinstance(value, str) and not re.search(spec["pattern"], value):
        errs.append(f"{where}={value!r} does not match {spec['pattern']}")
    if isinstance(value, list):
        if "minItems" in spec and len(value) < spec["minItems"]:
            errs.append(f"{where} needs at least {spec['minItems']} item(s), has {len(value)}")
        if "items" in spec:
            for i, item in enumerate(value):
                errs += schema_errors(item, spec["items"], f"{where}[{i}]")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in spec and value < spec["minimum"]:
            errs.append(f"{where}={value!r} is below the minimum {spec['minimum']}")
        if "maximum" in spec and value > spec["maximum"]:
            errs.append(f"{where}={value!r} is above the maximum {spec['maximum']}")
    return errs


def check_schema(rec) -> list:
    if not isinstance(rec, dict):
        return ["record must be a JSON object"]
    errs = []
    props = SCHEMA["properties"]
    for key in SCHEMA["required"]:
        if key not in rec:
            errs.append(f"missing {key}")
    if SCHEMA.get("additionalProperties") is False:
        for key in rec:
            if key not in props:
                errs.append(f"unknown field {key}")
    for key, spec in props.items():
        if key in rec:
            errs += schema_errors(rec[key], spec, key)
    return errs


def check_semantics(rec: dict) -> list:
    errs = []
    sha = rec.get("code_sha", "")
    if "code_sha" in rec and not (isinstance(sha, str) and len(sha) == 40
                                  and all(c in "0123456789abcdef" for c in sha)):
        errs.append("code_sha must be a full 40-char lowercase SHA")

    cls = rec.get("source_class") if isinstance(rec.get("source_class"), str) else ""
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
    if rec.get("discovery_route") in ("PUBLIC_DISCOVERY", "DIRECTORY_DISCOVERY") \
            and not rec.get("discovery_detail"):
        errs.append("discovery route requires discovery_detail")
    if rec.get("success") is True and rec.get("result") != "SUCCESS":
        errs.append("success true but result is not SUCCESS")
    return errs


def check(rec) -> list:
    """Schema first, then semantics. Semantics read fields the schema just typed."""
    errs = [f"schema: {e}" for e in check_schema(rec)]
    if isinstance(rec, dict):
        errs += [f"rule: {e}" for e in check_semantics(rec)]
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

"""Run record writing and validation.

Every run produces exactly one record, validated against run_record_schema.json before it is
written. An invalid record is not "mostly fine" — it is a measurement whose provenance cannot be
reconstructed, and the run that produced it is void.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None


class RecordError(RuntimeError):
    pass


def _schema_path() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve().parent
    for candidate in (here / "run_record_schema.json", here.parent / "run_record_schema.json"):
        if candidate.exists():
            return candidate
    raise RecordError("run_record_schema.json not found next to the harness")


def load_schema() -> dict:
    return json.loads(_schema_path().read_text())


def validate(record: dict) -> None:
    schema = load_schema()
    if jsonschema is None:
        raise RecordError("jsonschema is not installed; records cannot be validated")
    try:
        jsonschema.validate(record, schema)
    except jsonschema.ValidationError as exc:
        raise RecordError(
            f"run record failed schema validation at {list(exc.absolute_path)}: {exc.message}"
        ) from exc
    # Rules the schema cannot express on its own.
    if record["cache_state"] == "unknown":
        raise RecordError(
            "cache_state is 'unknown'. Methodology v1.0.0 section 9: a run whose cache state "
            "cannot be determined is VOID, not 'probably cold'."
        )
    if record["condition"].startswith("C4") and not record.get("model_pair"):
        raise RecordError("C4 runs must record the exact tier-adjacent model_pair (D011)")
    if record.get("outcome") not in ("PASS", "FAIL_QUALITY", "INVALID"):
        raise RecordError(
            f"outcome is {record.get('outcome')!r}. Methodology v1.1.0 section 6.2 defines exactly "
            "three: PASS, FAIL_QUALITY, INVALID. A record without one cannot be aggregated, and "
            "inferring it from task_success turns 'we could not measure it' into 'it failed'."
        )
    if record.get("corpus_modified"):
        if record["outcome"] != "FAIL_QUALITY":
            raise RecordError(
                f"corpus_modified names {len(record['corpus_modified'])} changed file(s) but the "
                f"outcome is {record['outcome']}. A modified corpus is an outright failure "
                "condition in 13 of the 17 tasks (RT-08)."
            )
    if record.get("unpriceable_quantities") and record.get("cost"):
        raise RecordError(
            "unpriceable_quantities is non-empty but a cost was recorded. Methodology v1.1.0 "
            "section 11.4: the harness does not estimate a price it does not have."
        )
    if record.get("token_source") != "provider_usage_field":
        raise RecordError(
            f"token_source is {record.get('token_source')!r}; only provider_usage_field is "
            "accepted as ground truth (METER_CALIBRATION_v1.0.0.md)"
        )
    if record["total_tokens"] != record["input_tokens"] + record["output_tokens"]:
        raise RecordError(
            "total_tokens does not equal input + output; the accumulator disagrees with itself"
        )


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def write_record(record: dict, out_dir: pathlib.Path) -> pathlib.Path:
    validate(record)
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{record['run_id']}.json"
    if path.exists():
        raise RecordError(
            f"{path} already exists. Run records are append-only; overwriting one destroys the "
            "evidence trail. Use a new run_id."
        )
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return path


def write_raw_evidence(run_id: str, payload: dict, evidence_root: pathlib.Path) -> str:
    """Write the raw, unprocessed provider exchange. Returns the recorded relative path."""
    evidence_root = pathlib.Path(evidence_root)
    run_dir = evidence_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    raw = run_dir / "raw.json"
    raw.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    manifest = {
        "run_id": run_id,
        # Volatile metadata belongs here, NOT inside a hashed file. MANIFEST.json is not itself
        # hashed, so a timestamp here does not make the evidence hash unreproducible.
        "written_at": datetime.now(timezone.utc).isoformat(),
        "files": {"raw.json": sha256_file(raw)},
        "note": (
            "Every hash below is over content only. Two runs of the same task from the same "
            "frozen inputs must produce the same hashes; if they do not, the evidence differs, "
            "not the clock."
        ),
    }
    (run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return str(run_dir)


def verify_raw_evidence(run_dir: pathlib.Path) -> bool:
    """Re-hash every file named in the manifest. Any mismatch means the evidence moved."""
    run_dir = pathlib.Path(run_dir)
    manifest = json.loads((run_dir / "MANIFEST.json").read_text())
    for name, expected in manifest["files"].items():
        actual = sha256_file(run_dir / name)
        if actual != expected:
            raise RecordError(f"{run_dir/name} hash mismatch: {actual} != {expected}")
    return True

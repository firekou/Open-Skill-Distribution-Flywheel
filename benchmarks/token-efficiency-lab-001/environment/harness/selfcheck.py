"""LG3 environment self-check.

Runs INSIDE the built container and answers the eight LG3 questions with observations rather
than assertions. Exits non-zero if any check fails. The output is the LG3 evidence.

Check 5 is the one that matters most and the one most likely to be got backwards: it PASSES
when outbound network access FAILS. A benchmark container that can reach the internet can
exfiltrate task content and can fetch a dependency mid-run, and either one voids the
measurement.
"""
from __future__ import annotations

import json
import os
import pathlib
import platform
import socket
import sys
import time
from datetime import datetime, timezone

RESULTS: list[dict] = []


def check(name: str, fn):
    started = time.time()
    try:
        detail = fn()
        ok = True
    except Exception as exc:  # noqa: BLE001 - a self-check reports failures, never raises them
        detail = f"{type(exc).__name__}: {exc}"
        ok = False
    RESULTS.append(
        {
            "check": name,
            "pass": ok,
            "detail": detail,
            "ms": int((time.time() - started) * 1000),
        }
    )


def c1_image_built() -> str:
    return (
        f"harness imported and executing inside the image; cwd={os.getcwd()}; "
        f"LAB={os.environ.get('LAB')}; METHODOLOGY_VERSION={os.environ.get('METHODOLOGY_VERSION')}"
    )


def c2_dependency_lock() -> str:
    import importlib.metadata as md

    lock = pathlib.Path("/lab/requirements.lock.txt").read_text().splitlines()
    wanted = {}
    for line in lock:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("--hash"):
            continue
        dist, _, rest = line.partition("==")
        wanted[dist.strip()] = rest.split()[0].strip()
    mismatched, missing = [], []
    for dist, version in wanted.items():
        try:
            got = md.version(dist)
        except md.PackageNotFoundError:
            missing.append(dist)
            continue
        if got != version:
            mismatched.append(f"{dist}: locked {version}, installed {got}")
    if missing or mismatched:
        raise RuntimeError(f"missing={missing} mismatched={mismatched}")
    import httpx, jsonschema, pydantic  # noqa: F401

    return f"{len(wanted)} locked distributions all installed at the locked version"


def c3_container_digest() -> str:
    digest = os.environ.get("LAB_CONTAINER_DIGEST")
    if not digest:
        raise RuntimeError(
            "LAB_CONTAINER_DIGEST was not passed in. The run cannot record which image "
            "produced it, so the evidence manifest would be incomplete."
        )
    return digest


def c4_runtime_pinned() -> str:
    expected = "3.11.15"
    got = platform.python_version()
    if got != expected:
        raise RuntimeError(f"python {got}, expected {expected}")
    return f"python {got} ({platform.machine()}), {sys.implementation.name}"


def c5_egress_denied() -> str:
    """PASSES when egress is blocked. Tries several destinations and ports."""
    targets = [("1.1.1.1", 443), ("8.8.8.8", 53), ("pypi.org", 443), ("github.com", 443)]
    reachable = []
    for host, port in targets:
        try:
            socket.setdefaulttimeout(3)
            with socket.create_connection((host, port), timeout=3):
                reachable.append(f"{host}:{port}")
        except Exception:
            pass
    if reachable:
        raise RuntimeError(
            "egress policy NOT applied - reachable: "
            + ", ".join(reachable)
            + ". A measured run must not be able to reach the network."
        )
    return f"default-deny confirmed: all {len(targets)} probe destinations unreachable"


def c6_task_data_mounted() -> str:
    tasks = pathlib.Path("/lab/tasks")
    if not tasks.is_dir():
        raise RuntimeError("/lab/tasks is not a directory")
    files = sorted(p for p in tasks.rglob("*") if p.is_file())
    if not files:
        raise RuntimeError("/lab/tasks is empty; no task data was mounted")
    total = sum(p.stat().st_size for p in files)
    probe = next((p for p in files if p.suffix == ".json"), files[0])
    probe.read_bytes()
    try:
        (tasks / ".write_probe").write_text("x")
        (tasks / ".write_probe").unlink()
        writable = "WRITABLE (should be read-only)"
    except OSError:
        writable = "read-only as required"
    return f"{len(files)} files, {total} bytes, mount is {writable}"


def c7_run_record_writable() -> str:
    sys.path.insert(0, "/lab")
    from harness.record import validate, write_record

    record = {
        "run_id": "selfcheck-0001",
        "task_id": "SELFCHECK-001",
        "condition": "C0",
        "workload": "A",
        "repetition": 1,
        "run_class": "dry_run",
        "model": "replay-synthetic",
        "provider": "lab",
        "model_version": "selfcheck",
        "model_calls": 1,
        "tool_calls": 0,
        "input_tokens": 100,
        "output_tokens": 10,
        "total_tokens": 110,
        "token_source": "provider_usage_field",
        "cost": 0.0001,
        "pricing_snapshot_id": "PS-2026-09-15",
        "latency_ms": 1,
        "retries": 0,
        "escalations": 0,
        "cache_state": "cold",
        "task_success": True,
        "quality_score": 1.0,
        "quality_judged_before_cost": True,
        "environment_id": os.environ.get("LAB_ENVIRONMENT_ID", "selfcheck"),
        "raw_evidence_path": "/lab/evidence/selfcheck-0001",
        "methodology_version": "1.0.0",
    }
    validate(record)
    out = pathlib.Path("/lab/evidence/selfcheck_records")
    path = write_record(record, out)
    # The schema must also REJECT a bad record, or validation proves nothing.
    bad = dict(record, cache_state="unknown", run_id="selfcheck-0002")
    try:
        validate(bad)
    except Exception:
        pass
    else:
        raise RuntimeError("validator accepted cache_state='unknown'; it must void the run")
    return f"record written to {path} and an invalid record was correctly rejected"


def c8_raw_evidence_preserved() -> str:
    sys.path.insert(0, "/lab")
    from harness.record import verify_raw_evidence, write_raw_evidence

    run_dir = write_raw_evidence(
        "selfcheck-0001",
        {"note": "selfcheck raw exchange", "calls": [{"usage": {"input_tokens": 100}}]},
        pathlib.Path("/lab/evidence"),
    )
    verify_raw_evidence(pathlib.Path(run_dir))
    tampered = pathlib.Path(run_dir) / "raw.json"
    original = tampered.read_text()
    tampered.write_text(original + " ")
    try:
        verify_raw_evidence(pathlib.Path(run_dir))
    except Exception:
        detected = True
    else:
        detected = False
    tampered.write_text(original)
    if not detected:
        raise RuntimeError("manifest did not detect a tampered raw file")
    return f"evidence at {run_dir}, manifest verified, tampering detected"


def main() -> int:
    check("1_dockerfile_builds", c1_image_built)
    check("2_dependency_lock_installs", c2_dependency_lock)
    check("3_container_digest_available", c3_container_digest)
    check("4_runtime_version_pinned", c4_runtime_pinned)
    check("5_network_egress_policy_applied", c5_egress_denied)
    check("6_task_data_mountable", c6_task_data_mounted)
    check("7_run_record_schema_writable", c7_run_record_writable)
    check("8_raw_evidence_preserved", c8_raw_evidence_preserved)

    report = {
        "lab": os.environ.get("LAB"),
        "methodology_version": os.environ.get("METHODOLOGY_VERSION"),
        "container_digest": os.environ.get("LAB_CONTAINER_DIGEST"),
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "checks": RESULTS,
        "passed": sum(1 for r in RESULTS if r["pass"]),
        "failed": sum(1 for r in RESULTS if not r["pass"]),
    }
    report["lg3_verdict"] = "PASS" if report["failed"] == 0 else "FAIL"
    print(json.dumps(report, indent=2))
    out = pathlib.Path("/lab/evidence/selfcheck_report.json")
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n")
    except OSError:
        pass
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

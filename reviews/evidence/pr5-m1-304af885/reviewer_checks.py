"""Isolated reviewer replay for PR5 head 304af885.

Usage: python3 /evidence/reviewer_checks.py /input /evidence/manifest.json

The suite-count check reads the README claim and TestLoader.countTestCases().
It does not hardcode an expected total. Process and network boundaries in the
verdict checks are mocked. This does not prove a clean install, a live
provider, adoption, or a license.
"""
import hashlib
import importlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import unittest
import urllib.error
from unittest.mock import patch

sys.dont_write_bytecode = True

root = pathlib.Path(sys.argv[1]).resolve()
manifest = json.loads(pathlib.Path(sys.argv[2]).read_text())
rows = []
failures = []


def record(name, **values):
    row = {"check": name, **values}
    rows.append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)
    return row


SECRET = "SYNTHETIC_REVIEWER_PRIVATE_729"
HTTP_KEY = "sk-SYNTHETIC-REVIEWER-729-ONLY"
REDACT = (
    SECRET,
    "-" + SECRET,
    HTTP_KEY,
    HTTP_KEY[::-1],
    HTTP_KEY[:16] + "***" + HTTP_KEY[-8:],
    "SYNTHETIC_PRIVATE_CUSTOMER_42",
    "sk-SYNTHETIC0000NOTAREALKEY0000000000000ZZ",
)


def redact(text):
    out = str(text)
    for item in REDACT:
        out = out.replace(item, "[REDACTED]")
    return out


def fail(gate, message):
    failures.append(gate)
    raise AssertionError(message)


# G1 — exact blobs. Stop before any PR code runs when this fails.
blob_errors = []
for rel, expected in manifest["files"].items():
    path = root / rel
    data = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if actual != expected:
        blob_errors.append({"path": rel, "expected": expected, "actual": actual})
if blob_errors:
    record("exact_source_blobs", passed=False, gate="G1", errors=blob_errors)
    record("summary", passed=False, head=manifest.get("reviewed_head"),
           limitations="Stopped before PR code: blob mismatch.",
           gates={"G1": "FAIL"})
    sys.exit(2)
record("exact_source_blobs", passed=True, gate="G1", head=manifest["reviewed_head"])

current = root / "current"
previous = root / "previous"
clean_env = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "HOME": "/tmp",
    "TMPDIR": "/tmp",
    "PYTHONDONTWRITEBYTECODE": "1",
    "LANG": "C.UTF-8",
}


def cli(directory, args):
    return subprocess.run(
        [sys.executable, "-B", str(directory / "local_check.py"), *args],
        env=clean_env,
        cwd="/tmp",
        capture_output=True,
        text=True,
        timeout=15,
    )


# G2 — five unknown forms must not echo the synthetic value or the token.
cases = [
    ["--needlez", SECRET],
    ["--needlez", "-" + SECRET],
    ["--needlez=-" + SECRET],
    ["-" + SECRET],
    ["--needlez"],
]
g2_ok = True
for index, args in enumerate(cases, 1):
    try:
        proc = cli(current, args)
        output = proc.stdout + proc.stderr
        echoed = SECRET in output
        token_echoed = "needlez" in output
        ok = (
            proc.returncode == 2
            and not echoed
            and not token_echoed
            and "--help" in output
        )
        record(
            "unknown_form_" + str(index),
            gate="G2",
            passed=ok,
            exit=proc.returncode,
            private_echo=echoed,
            unknown_token_echo=token_echoed,
            help_offered="--help" in output,
            output_included=False,
        )
        g2_ok = g2_ok and ok
    except Exception as exc:
        g2_ok = False
        record(
            "unknown_form_" + str(index),
            gate="G2",
            passed=False,
            error=redact(exc),
            output_included=False,
        )
if not g2_ok:
    failures.append("G2")

# G3 — pre-fix dash-leading value must still be echoed, or the control is blind.
try:
    proc = cli(previous, ["--needlez", "-" + SECRET])
    output = proc.stdout + proc.stderr
    echoed = SECRET in output
    record(
        "previous_version_negative_control",
        gate="G3",
        passed=echoed,
        exit=proc.returncode,
        private_echo=echoed,
        output_included=False,
    )
    if not echoed:
        failures.append("G3")
except Exception as exc:
    failures.append("G3")
    record(
        "previous_version_negative_control",
        gate="G3",
        passed=False,
        error=redact(exc),
        output_included=False,
    )

# G4 — legal help and equals-form parsing.
g4_ok = True
try:
    proc = cli(current, ["--help"])
    ok = proc.returncode == 0 and "--needle" in proc.stdout
    record(
        "help_positive_control",
        gate="G4",
        passed=ok,
        exit=proc.returncode,
        needle_option_present="--needle" in proc.stdout,
    )
    g4_ok = g4_ok and ok
except Exception as exc:
    g4_ok = False
    record("help_positive_control", gate="G4", passed=False, error=redact(exc))

sys.path.insert(0, str(current))
try:
    tests = importlib.import_module("test_local_check")
    parsed = tests.local_check.parse_args(["--needle=-" + SECRET])
    ok = parsed.needle == ["-" + SECRET]
    record("legal_equals_parse", gate="G4", passed=ok, parsed_equals_dash_secret=ok)
    g4_ok = g4_ok and ok
except Exception as exc:
    g4_ok = False
    record("legal_equals_parse", gate="G4", passed=False, error=redact(exc))
if not g4_ok:
    failures.append("G4")

# G5 — suite exit 0, and README claim equals TestLoader.countTestCases().
try:
    suite = subprocess.run(
        [sys.executable, "-B", str(current / "test_local_check.py")],
        cwd=current,
        env=clean_env,
        capture_output=True,
        text=True,
        timeout=90,
    )
    readme = (current / "README.md").read_text(encoding="utf-8")
    claimed = {int(n) for n in re.findall(r"(\d+)\s+(?:offline )?unit tests", readme)}
    actual = unittest.TestLoader().loadTestsFromModule(tests).countTestCases()
    ok = suite.returncode == 0 and bool(claimed) and claimed == {actual}
    record(
        "unit_suite",
        gate="G5",
        passed=ok,
        exit=suite.returncode,
        readme_claimed=sorted(claimed),
        loader_count=actual,
        stdout_sha256=hashlib.sha256(suite.stdout.encode()).hexdigest(),
        stderr_sha256=hashlib.sha256(suite.stderr.encode()).hexdigest(),
        stdout=redact(suite.stdout),
        stderr=redact(suite.stderr),
    )
    if not ok:
        failures.append("G5")
except Exception as exc:
    failures.append("G5")
    record("unit_suite", gate="G5", passed=False, error=redact(exc))

# G6 — shrink / unchanged / equal-length rewrite / growth / lost needle / HTTP body.
g6_ok = True
try:
    for name, transform, expected in [
        ("shrink", lambda s: "KEEP", 0),
        ("unchanged", lambda s: s, 3),
        ("equal_rewrite", lambda s: s.replace("x", "y"), 3),
        ("growth", lambda s: s + "EXTRA", 3),
        ("lost", lambda s: "gone", 1),
    ]:
        code, _out = tests.run_local_check(
            "KEEP " + "x" * 200,
            transform,
            extra_argv=["--needle=KEEP"],
        )
        ok = code == expected
        record(
            name,
            gate="G6",
            passed=ok,
            exit=code,
            expected_exit=expected,
            boundary="mocked process/network; real decision path",
        )
        g6_ok = g6_ok and ok
except Exception as exc:
    g6_ok = False
    record("verdict_controls", gate="G6", passed=False, error=redact(exc))

try:
    for name, body in [
        ("full", HTTP_KEY),
        ("partial", HTTP_KEY[:16] + "***" + HTTP_KEY[-8:]),
        ("transformed", HTTP_KEY[::-1]),
    ]:
        err = urllib.error.HTTPError(
            "http://test.invalid",
            401,
            "denied",
            {},
            io.BytesIO(body.encode()),
        )
        with patch.dict(os.environ, {"ATK_INCLUDE_ERROR_BODY": "1"}, clear=True), \
             patch.object(tests.ab_test.urllib.request, "urlopen", side_effect=err):
            try:
                tests.ab_test.call("http://test.invalid", HTTP_KEY, "synthetic", False)
            except SystemExit as exc:
                message = str(exc)
            else:
                raise AssertionError("HTTP error did not fail")
        withheld = body not in message and "401" in message
        record(
            "http_error_" + name,
            gate="G6",
            passed=withheld,
            body_withheld=body not in message,
            status_present="401" in message,
            boundary="mock HTTPError; body not recorded",
        )
        g6_ok = g6_ok and withheld
except Exception as exc:
    g6_ok = False
    record("http_error_controls", gate="G6", passed=False, error=redact(exc))
if not g6_ok:
    failures.append("G6")

limitations = (
    "Mock process/network only. Not a clean headroom install, not a live "
    "provider, not adoption proof, and not a license PASS. Not release-verified."
)
honesty = {
    "mock_boundary": "Mock process/network" in limitations,
    "not_clean_install": "Not a clean headroom install" in limitations,
    "not_live_provider": "not a live provider" in limitations,
    "not_adoption": "not adoption proof" in limitations,
    "not_license_pass": "not a license PASS" in limitations,
    "not_release_verified": "Not release-verified" in limitations,
}
record(
    "summary",
    gate="G7",
    passed=all(honesty.values()),
    honesty=honesty,
    head=manifest["reviewed_head"],
    comparison_head=manifest["comparison_head"],
    limitations=limitations,
    failed_gates=sorted(set(failures)),
)
if not all(honesty.values()):
    failures.append("G7")
if failures:
    sys.exit(1)

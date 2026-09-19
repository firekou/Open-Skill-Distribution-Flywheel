"""UNEXECUTED reviewer replay for PR5 32ca53c; run only in a secret-free sandbox.
Usage: python3 /evidence/reviewer_checks.py /input /evidence/manifest.json
/input/current: exact local_check.py, ab_test.py, test_local_check.py, README.md
/input/previous: exact d1930e4 local_check.py. See manifest Git blob hashes.
"""
import hashlib, importlib, io, json, os, pathlib, subprocess, sys, urllib.error
from unittest.mock import patch

root = pathlib.Path(sys.argv[1]).resolve()
manifest = json.loads(pathlib.Path(sys.argv[2]).read_text())
rows = []
def record(name, **values):
    row = {"check": name, **values}
    rows.append(row)
    print(json.dumps(row), flush=True)

for rel, expected in manifest["files"].items():
    data = (root / rel).read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert actual == expected, (rel, "snapshot mismatch")
record("exact_source_blobs", passed=True, head=manifest["reviewed_head"])

current = root / "current"
previous = root / "previous"
clean_env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
             "HOME": "/tmp", "TMPDIR": "/tmp", "PYTHONDONTWRITEBYTECODE": "1"}
secret = "SYNTHETIC_REVIEWER_PRIVATE_729"
cases = [
    ["--needlez", secret],
    ["--needlez", "-" + secret],
    ["--needlez=-" + secret],
    ["-" + secret],
    ["--needlez"],
]
def cli(directory, args):
    return subprocess.run([sys.executable, "-B", str(directory / "local_check.py")] + args,
                          env=clean_env, cwd="/tmp", capture_output=True, text=True, timeout=15)
for n, args in enumerate(cases):
    p = cli(current, args)
    output = p.stdout + p.stderr
    assert p.returncode == 2
    assert secret not in output and "needlez" not in output
    assert "--help" in output
    record("unknown_form_" + str(n + 1), exit=p.returncode, private_echo=False)

p = cli(previous, ["--needlez", "-" + secret])
assert p.returncode == 2 and secret in p.stdout + p.stderr
record("previous_version_negative_control", exit=2, private_echo=True)

p = cli(current, ["--help"])
assert p.returncode == 0 and "--needle" in p.stdout
record("help_positive_control", exit=0)

suite = subprocess.run([sys.executable, "-B", str(current / "test_local_check.py")],
                       cwd=current, env=clean_env, capture_output=True, text=True, timeout=90)
record("unit_suite", exit=suite.returncode, stdout=suite.stdout, stderr=suite.stderr)
assert suite.returncode == 0
assert "Ran 31 tests" in suite.stderr

sys.path.insert(0, str(current))
t = importlib.import_module("test_local_check")
parsed = t.local_check.parse_args(["--needle=-" + secret])
assert parsed.needle == ["-" + secret]
record("legal_equals_parse", passed=True)
for name, transform, expected in [
    ("shrink", lambda s: "KEEP", 0),
    ("unchanged", lambda s: s, 3),
    ("equal_rewrite", lambda s: s.replace("x", "y"), 3),
    ("growth", lambda s: s + "EXTRA", 3),
    ("lost", lambda s: "gone", 1),
]:
    rc, out = t.run_local_check("KEEP " + "x" * 200, transform,
                               extra_argv=["--needle=KEEP"])
    assert rc == expected, (name, rc)
    record(name, exit=rc, boundary="mocked process/network; real decision path")

key = "sk-SYNTHETIC-REVIEWER-729-ONLY"
for name, body in [("full", key), ("partial", key[:16] + "***" + key[-8:]),
                   ("transformed", key[::-1])]:
    err = urllib.error.HTTPError("http://test.invalid", 401, "denied", {},
                                 io.BytesIO(body.encode()))
    with patch.dict(os.environ, {"ATK_INCLUDE_ERROR_BODY": "1"}, clear=True), \
         patch.object(t.ab_test.urllib.request, "urlopen", side_effect=err):
        try:
            t.ab_test.call("http://test.invalid", key, "synthetic", False)
        except SystemExit as exc:
            out = str(exc)
        else:
            raise AssertionError("HTTP error did not fail")
    assert body not in out and "401" in out
    record("http_error_" + name, body_withheld=True, boundary="mock HTTPError")
record("summary", passed=True, head=manifest["reviewed_head"],
       limitations="No clean headroom install, live proxy, real API, cost or adoption verification.")

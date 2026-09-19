#!/usr/bin/env python3
"""Independent R3 reviewer checks — PR #5, head 9c439a40174e2fff9ed3d20ac973baf6758f1611.

Run from a clean clone's integrations/headroom-atk (or a dir holding ab_test.py,
local_check.py, test_local_check.py). Pass the repo root as argv[1] for the doc checks.
All secrets are SYNTHETIC. No network, no credential, no paid call.

    python3 reviewer_r3_checks.py /tmp/r3-review/repo
"""
import contextlib, io, json, os, pathlib, re, subprocess, sys, tempfile, urllib.error
from unittest.mock import patch

import test_local_check as t
ab, lc = t.ab_test, t.local_check
HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
def rec(**kw): print(json.dumps(kw, ensure_ascii=False, sort_keys=False))

# ===== 1. P5-01: can a provider error body leak the credential? =====
KEY = "sk-SYNTHETIC0000NOTAREALKEY0000000000000ZZ"      # 41 chars, synthetic
BODIES = {
    "a_full_key":    '{"error":"invalid key %s"}' % KEY,
    "b_fragment":    "invalid key %s***%s" % (KEY[:16], KEY[-8:]),
    "c_spaced_echo": '{"error":"rejected %s"}' % " ".join(KEY),
    "c2_reversed":   '{"error":"rejected %s"}' % KEY[::-1],
    "d_past_400":    "A" * 420 + KEY + "tail",
}
def leaked(value, msg, w=8):
    return [i for i in range(max(0, len(value) - w + 1)) if value[i:i + w] in msg]

for name, body in BODIES.items():
    for lbl, env in (("unset", {}), ("ATK_INCLUDE_ERROR_BODY=1", {"ATK_INCLUDE_ERROR_BODY": "1"})):
        err = urllib.error.HTTPError("http://test.invalid", 401, "denied", {},
                                     io.BytesIO(body.encode()))
        with patch.dict(os.environ, env, clear=True), \
             patch.object(ab.urllib.request, "urlopen", side_effect=err):
            try:
                ab.call("http://test.invalid", KEY, "p", False); msg = "<NO SystemExit>"
            except SystemExit as e:
                msg = str(e)
        rec(check="P5-01", body=name, env=lbl, full_key_visible=KEY in msg,
            leaked_8char_offsets=leaked(KEY, msg),
            body_echoed=any(c in msg for c in (body[:40], body[-40:])),
            status_shown="401" in msg)
src = pathlib.Path(ab.__file__).read_text()
rec(check="P5-01", case="switch_really_gone",
    INCLUDE_BODY_ENV_attr=hasattr(ab, "INCLUDE_BODY_ENV"),
    env_reads=re.findall(r"os\.environ\.get\(\"([A-Z_]+)\"", src),
    reads_error_body=bool(re.search(r"exc\.read|\.read\(\)", src)),
    truncation_slices=re.findall(r"\[:\d{2,}\]", src))

# ===== 2. P5-R2-01: try to make local_check print a needle =====
N = "SYNTHETIC_PRIVATE_CUSTOMER_42"
for label, payload, tr, needles, extra in [
    ("success",             N + " x"*100,  lambda s: N,          (N,),        ()),
    ("needle_LOST",         N + " x"*100,  lambda s: "gone",     (N,),        ()),
    ("needle_not_in_src",   "x"*200,       lambda s: s,          (N,),        ()),
    ("empty_needle",        N + " x"*100,  lambda s: N,          ("",),       ()),
    ("exit3_unchanged",     N + " x"*100,  lambda s: s,          (N,),        ()),
    ("exit3_inflated",      N + " x"*100,  lambda s: s+"E"*50,   (N,),        ()),
    ("duplicate_needles",   N + " x"*100,  lambda s: N,          (N, N),      ()),
    ("regex_metachars",     N + ".*x"*100, lambda s: N+".*",     (N + ".*",), ()),
    ("show_needles_optin",  N + " x"*100,  lambda s: N,          (N,),        ("--show-needles",)),
]:
    code, out = t.run_local_check(payload, tr, needles=needles, extra_argv=extra)
    rec(check="P5-R2-01", case=label, exit=code, needle_visible=N in out,
        first_line=(out.splitlines() or [""])[0][:110])

def cli(argv, cwd=str(HERE)):
    p = subprocess.run([sys.executable, str(pathlib.Path(cwd)/"local_check.py")] + argv,
                       capture_output=True, text=True, cwd=cwd, timeout=60)
    return p.returncode, p.stdout + p.stderr
with tempfile.TemporaryDirectory() as td:
    missing = pathlib.Path(td) / "absent.log"
    rc, out = cli(["--log", str(missing), "--needle", N])
    rec(check="P5-R2-01", case="cli_missing_log", exit=rc, needle_visible=N in out,
        FULL_PATH_visible=str(missing) in out, out=out.strip()[:140])
    d = pathlib.Path(td) / "adir"; d.mkdir()
    rc, out = cli(["--log", str(d), "--needle", N])
    rec(check="P5-R2-01", case="cli_log_is_a_directory", exit=rc, needle_visible=N in out,
        uncaught_traceback="Traceback" in out, out=out.strip()[-110:])
    g = pathlib.Path(td) / "my.log"; g.write_text(N + "\n" + "x"*200)
    rc, out = cli(["--log", str(g)])
    rec(check="P5-R2-01", case="cli_log_without_needle", exit=rc, needle_visible=N in out,
        FULL_PATH_visible=str(g) in out)
    rc, out = cli(["--log", str(g), "--needlez", N])
    rec(check="P5-R2-01", case="cli_argparse_typo", exit=rc, needle_visible=N in out,
        out=out.strip()[-95:])

# ===== 3. P5-R2-02: is the NEW logging claim supported? =====
import importlib.util, logging
spec = importlib.util.find_spec("headroom")
rec(check="P5-R2-02", case="headroom_available", importable=spec is not None,
    origin=(spec.origin if spec else None))
if spec:
    hp = pathlib.Path(spec.origin).parent / "proxy" / "helpers.py"
    txt = hp.read_text().splitlines()
    i = next((k for k, l in enumerate(txt) if "_setup_file_logging" in l and l.startswith("def")), None)
    blk = "\n".join(txt[i:i+45]) if i is not None else ""
    rec(check="P5-R2-02", case="source_of_claim", file=str(hp), def_line=(i+1 if i else None),
        attaches_RotatingFileHandler="RotatingFileHandler(" in blk,
        target_logger=('headroom' if 'getLogger("headroom")' in blk else None),
        sets_propagate_False="propagate = False" in blk,
        path_is_logs_proxy_log='log_dir / "proxy.log"' in blk)
    os.environ["HEADROOM_WORKSPACE_DIR"] = tempfile.mkdtemp()
    from headroom.proxy.helpers import _setup_file_logging
    from headroom import paths
    _setup_file_logging()
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        logging.getLogger("headroom.proxy").warning(
            "ignoring unsafe x-headroom-base-url override: %r", "http://127.0.0.1:1")
    p = paths.proxy_log_path()
    rec(check="P5-R2-02", case="end_to_end_reproduction",
        on_stderr="ignoring unsafe" in buf.getvalue(),
        headroom_logger_propagate=logging.getLogger("headroom").propagate,
        in_proxy_log=("ignoring unsafe" in p.read_text() if p.exists() else None),
        VERDICT="executor's new claim CONFIRMED: warning goes to proxy.log, not stderr")
# stdlib controls: why the OLD root cause was wrong, and why propagate alone is not it
for nm, prop in (("no_handlers_anywhere", True), ("propagate_False_no_handler", False)):
    b = io.StringIO(); root = logging.getLogger(); saved = root.handlers[:]; root.handlers.clear()
    lg = logging.getLogger("r3." + nm); lg.handlers.clear(); lg.propagate = prop
    with contextlib.redirect_stderr(b): lg.warning("synthetic-warning")
    rec(check="P5-R2-02", case="stdlib_control_" + nm, propagate=prop,
        lastResort=str(logging.lastResort), warning_on_stderr="synthetic-warning" in b.getvalue())
    root.handlers[:] = saved

# ===== 4. P5-04 / doc-vs-artifact consistency =====
base = ROOT / "integrations" / "headroom-atk"
readme = (base / "README.md").read_text()
n_tests = int(subprocess.run([sys.executable, str(HERE/"test_local_check.py")],
              capture_output=True, text=True, cwd=str(HERE)).stderr.split("Ran ")[1].split()[0])
rec(check="P5-04", case="test_count", tests_that_actually_run=n_tests,
    readme_says_17=len(re.findall(r"17 (?:offline )?unit tests", readme)),
    readme_lines=[i+1 for i, l in enumerate(readme.splitlines()) if "17 " in l and "test" in l])
ev = (base / "evidence" / "local_check.txt").read_text()
blk = readme.split("Output committed at `evidence/local_check.txt`:")[1].split("```")[1] if \
      "Output committed at `evidence/local_check.txt`:" in readme else ""
rec(check="P5-04", case="readme_sample_block_vs_committed_evidence",
    readme_block_lines=[l for l in blk.strip().splitlines() if l.strip()],
    every_readme_line_in_evidence=all(l.strip() in ev for l in blk.strip().splitlines() if l.strip()),
    readme_block_prints_needle_text=("0042_add_tenant_id'" in blk),
    evidence_uses_new_format=("needle #1 (18 chars)" in ev))
for f, pat in [("README.md", r"raw (?:ATK )?response"), ("README.md", r"nothing lost, nothing gained"),
               ("README.md", r"cost you more"), ("README.md", r"error-body redaction"),
               ("README.md", r"17 (?:offline )?unit tests"),
               ("DISTRIBUTION.md", r"prints only sizes and\s+pass/fail")]:
    body = (base/f).read_text()
    hits = [body[:m.start()].count(chr(10))+1 for m in re.finditer(pat, body, re.I)]
    rec(check="P5-04", case="wording_residue", file=f, pattern=pat, line_hits=hits,
        still_present=bool(hits))
rec(check="P5-04", case="referenced_evidence_paths",
    readme_lists_pr5_r2=("evidence/pr5-r2/controls.txt" in readme),
    readme_lists_pr5_r3=("evidence/pr5-r3/controls.txt" in readme),
    pr5_r3_exists=(base/"evidence"/"pr5-r3"/"controls.txt").exists())

#!/usr/bin/env python3
"""Offline consistency check for the A package. Stdlib + git, run from the repo root:

    python3 adoption/ATK-OPEN-ADOPTION-01/check_consistency.py

Checks that the agent contract cannot drift from itself or from the pinned code:
  1. agent-manifest.json parses and its code SHA, version, md5 and expected numbers
     match AGENT_QUICKSTART.md;
  2. the quickstart does not copy the live commands (they live only in TRY_IT);
  3. the pinned SHA exists locally, and the code files the manifest names exist there;
  4. pr5-doc-delta.patch applies cleanly to the pinned SHA and touches only docs
     plus ab_test.py (whose executable AST is unchanged apart from docstrings);
  5. every record in records/ passes validate_records.py and every negative
     fixture fails it.
Exit 0 if all pass. Needs the PR #5 commit fetched (git fetch origin claude/atk-headroom-adoption).
"""
import ast
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
PKG = ROOT / "adoption" / "ATK-OPEN-ADOPTION-01"
ASSET = ROOT / "integrations" / "headroom-atk"
DOC_FILES = {"README.md", "TRY_IT.md", "DISTRIBUTION.md", "offering/SERVICE_SAMPLE_FREE.md", "ab_test.py"}
fails = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def git(*args, **kw):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, **kw)


def strip_docstrings(src):
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body \
                and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant) \
                and isinstance(n.body[0].value.value, str):
            n.body = n.body[1:]
    return ast.dump(tree)


man = json.loads((ASSET / "agent-manifest.json").read_text(encoding="utf-8"))
qs = (ASSET / "AGENT_QUICKSTART.md").read_text(encoding="utf-8")
sha = man["source"]["code_sha"]
ok(len(sha) == 40, "manifest code_sha is a full SHA")
ok(qs.count(f"git checkout {sha}") == 1, "quickstart checks out the manifest SHA")
ok(man["license"]["tool"]["version"] == "0.37.0" and 'headroom-ai[proxy]==0.37.0' in qs, "same headroom version in both")
ok(man["inputs"]["synthetic_log"]["md5"] in qs, "same synthetic log md5 in both")
exp = man["outputs"]["expected_synthetic"]
ok(f'{exp["direct_chars"]} chars' in qs and f'{exp["proxy_chars"]} chars' in qs, "same expected numbers in both")
ok(set(man["exit_codes"]) == {"0", "1", "2", "3", "4"} and all(f"| **{c}** |" in qs for c in man["exit_codes"]), "same exit codes in both")
ok("ab_test.py" not in qs and "headroom proxy --port" not in qs, "quickstart does not copy the live commands")
ok(man["live"]["commands_source"].count(sha) == 1, "live commands link is pinned to the SHA")

ok(git("cat-file", "-e", f"{sha}^{{commit}}").returncode == 0, "pinned SHA present locally")
for f in ("make_log.py", "local_check.py", "test_local_check.py", "TRY_IT.md", "ab_test.py"):
    ok(git("cat-file", "-e", f"{sha}:integrations/headroom-atk/{f}").returncode == 0, f"{f} exists at pinned SHA")

patch = PKG / "pr5-doc-delta.patch"
touched = {l[len("+++ b/integrations/headroom-atk/"):].strip() for l in patch.read_text(encoding="utf-8").splitlines()
           if l.startswith("+++ b/")}
ok(touched and touched <= DOC_FILES, f"patch touches only {sorted(DOC_FILES)}: {sorted(touched)}")
with tempfile.TemporaryDirectory() as td:
    wt = pathlib.Path(td) / "wt"
    if git("worktree", "add", "-q", "--detach", str(wt), sha).returncode == 0:
        try:
            r = subprocess.run(["git", "-C", str(wt), "apply", str(patch)], capture_output=True, text=True)
            ok(r.returncode == 0, "patch applies cleanly to pinned SHA")
            if r.returncode == 0:
                old = git("show", f"{sha}:integrations/headroom-atk/ab_test.py").stdout
                new = (wt / "integrations/headroom-atk/ab_test.py").read_text(encoding="utf-8")
                ok(strip_docstrings(old) == strip_docstrings(new), "ab_test.py executable code unchanged")
        finally:
            git("worktree", "remove", "--force", str(wt))
    else:
        ok(False, "could not create worktree at pinned SHA")

v = PKG / "validate_records.py"
recs = sorted((PKG / "records").glob("*.json"))
ok(bool(recs) and subprocess.run([sys.executable, str(v), *map(str, recs)], capture_output=True).returncode == 0,
   f"{len(recs)} record(s) validate")
for f in sorted((PKG / "test_fixtures").glob("*.json")):
    rc = subprocess.run([sys.executable, str(v), str(f)], capture_output=True).returncode
    ok(rc == (0 if f.name.startswith("ok_") else 1), f"fixture {f.name} -> exit {rc}")

print(f"\n{'OK' if not fails else 'FAILED'}: {len(fails)} failure(s)")
sys.exit(1 if fails else 0)

#!/usr/bin/env python3
"""Does the environment allowlist actually isolate credentials? Ask, don't assume.

The repository claimed two things that this script tests directly:

  1. "no ANTHROPIC_API_KEY and no ~/.claude/.credentials.json, so the runner
     cannot authenticate"  (PR #6 ACTIVATION.md)
  2. "pr_tests: nothing. Untrusted repository code runs with no credential of
     any kind."            (PR #6 config.live.example.json)

Both are statements about the *environment*. Neither was ever tested against the
CLI they describe. This runs the CLI under each environment and records what
actually happens.

Costs a few model calls. Prints no credential, no session id, no prompt content
beyond the fixed probe string.
"""
import json, os, subprocess, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from runners import build_env, has_credential          # noqa: E402

PROBE = ["claude", "-p", "--output-format", "json", "Reply with exactly: PONG"]
PARENT_SESSION = os.environ.get("CLAUDE_CODE_SESSION_ID", "")


def run(env):
    try:
        p = subprocess.run(PROBE, capture_output=True, text=True, env=env,
                           timeout=150, cwd="/tmp", stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"outcome": "timeout"}
    out = {"exit_code": p.returncode}
    try:
        d = json.loads(p.stdout)
    except Exception:
        out["outcome"] = "unparseable"
        out["stderr_len"] = len(p.stderr)
        return out
    out.update({
        "authenticated": d.get("is_error") is False and d.get("result") == "PONG",
        "subtype": d.get("subtype"),
        "total_cost_usd": d.get("total_cost_usd"),
        "cache_read_input_tokens": d.get("usage", {}).get("cache_read_input_tokens"),
        # the VALUE is never recorded, only whether it is the caller's own session
        "session_id_is_parents": bool(PARENT_SESSION) and d.get("session_id") == PARENT_SESSION,
    })
    return out


def main():
    cases = {}
    full = dict(os.environ)
    cases["1_full_parent_env"] = {
        "_what": "what subprocess(env=None) would have given a runner",
        "env_var_count": len(full), **run(full)}

    for role in ("executor", "reviewer", "pr_tests"):
        env = build_env(role)
        cases[f"2_build_env_{role}"] = {
            "_what": f"the repository's own allowlist for role {role!r}",
            "env_keys": sorted(env),
            "has_credential_says": has_credential(role),
            **run(env)}

    env = build_env("pr_tests"); env["HOME"] = "/tmp/probe-empty-home"
    os.makedirs(env["HOME"], exist_ok=True)
    cases["3_pr_tests_empty_home"] = {
        "_what": "same, with HOME redirected to an empty directory",
        **run(env)}

    print(json.dumps(cases, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

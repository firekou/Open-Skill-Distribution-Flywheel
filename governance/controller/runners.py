#!/usr/bin/env python3
"""Runner adapters: how the controller starts an executor or a reviewer.

G2. The previous version passed `env=self._config.get("env_passthrough_only", None)`
to `subprocess.run`. `env=None` means **inherit the whole parent environment**, and
the shipped template never set the field — so a runner executing code from a pull
request would have received every credential the controller holds. Measured on the
host this was written on: 142 variables, including GITHUB_TOKEN, AWS_SECRET_ACCESS_KEY,
AITOKENKING_API_KEY and CLAUDE_CODE_MESSAGING_TOKEN. Nothing leaked, because live
dispatch has never been enabled — but the default was the opposite of what
ACTIVATION.md promised. There is now no way to ask for inheritance:
`build_env` constructs the environment from an allowlist and nothing else.

Roles are separated rather than named separately:

  EXECUTOR  may hold a GitHub token limited to its work branch, and model
            credentials. It runs code it is about to author.
  REVIEWER  gets a different run id and workspace, and no write token at all.
            Its output is evidence, and evidence does not need push rights.
  PR TESTS  (untrusted code from the pull request) get neither. That is the
            case the old default was worst for.

What this module still cannot do: enforce any of it below the process boundary.
An allowlist is a promise about what we pass, not a sandbox. Real isolation needs
a container, which `ACTIVATION.md` records as not yet wired in.
"""

from __future__ import annotations

import contextlib
import json
import os
import pathlib
import shutil
import signal
import subprocess
import uuid

# Variables a runner may see. Everything else is dropped, including anything
# added to the parent later — the list is what is allowed, not what is blocked.
BASE_ENV_ALLOWLIST = ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE", "TZ")

# Credentials each role may additionally receive, by role. A name appearing here
# is still only passed if the operator's environment actually holds it.
ROLE_CREDENTIALS = {
    # The executor authors commits, so it needs the model and a branch-scoped token.
    "executor": ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "GITHUB_TOKEN"),
    # The reviewer produces evidence. It needs the model; it must never be able to push.
    "reviewer": ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN"),
    # Untrusted code from the PR gets nothing at all.
    "pr_tests": (),
}

DENY_ALWAYS = ("GITHUB_TOKEN", "GH_TOKEN")   # never reaches reviewer or pr_tests


class RunnerError(RuntimeError):
    """A runner could not produce a verdict. Never interpreted as success."""


class AuthUnavailable(RunnerError):
    """No usable credential. The controller maps this to BLOCKED_ACCESS.

    Kept distinct so that "we could not authenticate" can never be recorded as
    "the work was done", which is the failure mode the acceptance calls out.
    """


def build_env(role: str, parent: dict | None = None) -> dict:
    """The complete environment a runner process will see.

    Built from an allowlist. There is deliberately no parameter that means
    "inherit everything" — the old code had one by omission.
    """
    if role not in ROLE_CREDENTIALS:
        raise RunnerError(f"unknown runner role {role!r}")
    source = os.environ if parent is None else parent
    env = {k: source[k] for k in BASE_ENV_ALLOWLIST if k in source}
    env.setdefault("PATH", "/usr/bin:/bin")
    env.setdefault("HOME", "/tmp")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in ROLE_CREDENTIALS[role]:
        if name in DENY_ALWAYS and role != "executor":
            continue
        if name in source:
            env[name] = source[name]
    return env


def has_credential(role: str, parent: dict | None = None) -> bool:
    source = os.environ if parent is None else parent
    return any(name in source and source[name]
               for name in ROLE_CREDENTIALS[role]
               if name not in ("GITHUB_TOKEN", "GH_TOKEN"))


class Runner:
    """Interface. `run(order)` returns a dict; it must not touch the store."""

    kind = "abstract"
    role = "pr_tests"

    def identity(self) -> str:
        raise NotImplementedError

    def run(self, order: dict) -> dict:
        raise NotImplementedError


# --------------------------------------------------------------------------
# Test doubles — no model call, no network
# --------------------------------------------------------------------------

class FakeExecutor(Runner):
    kind = "executor"
    role = "executor"

    def __init__(self, heads, identity="fake-executor-1"):
        self._heads = list(heads)
        self._identity = identity
        self.calls = []

    def identity(self) -> str:
        return self._identity

    def run(self, order: dict) -> dict:
        self.calls.append(order["task_id"])
        if not self._heads:
            raise RunnerError("fake executor has no scripted head left")
        return {"new_head": self._heads.pop(0)}


class FakeReviewer(Runner):
    kind = "reviewer"
    role = "reviewer"

    def __init__(self, decisions, identity="fake-reviewer-1"):
        self._decisions = list(decisions)
        self._identity = identity
        self.calls = []

    def identity(self) -> str:
        return self._identity

    def run(self, order: dict) -> dict:
        self.calls.append(order["head"])
        if not self._decisions:
            raise RunnerError("fake reviewer has no scripted decision left")
        decision = self._decisions.pop(0)
        return {
            "review": {
                "head": order["head"],
                "reviewer": self._identity,
                "decision": decision,
                "evidence": [f"replay://{order['task_id']}/{order['head'][:7]}/{decision}"],
            },
        }


# --------------------------------------------------------------------------
# Real adapter — off unless explicitly enabled
# --------------------------------------------------------------------------


def terminate_process_group(proc, grace_seconds: float = 10.0) -> str:
    """Kill the runner AND everything it started, then confirm it is gone.

    subprocess.run(timeout=...) kills only the direct child. A CLI agent that
    spawns its own worker leaves that worker running — still holding the
    credentials that were in its environment, still able to push. Measured:
    evidence/cancel.txt, where the plain kill leaves the grandchild alive and
    the group kill does not.

    This needs the child to have been started with start_new_session=True, so
    it leads its own process group and the group id is the child's pid.

    Returns "terminated" if SIGTERM was enough, "killed" if SIGKILL was needed,
    "already_gone" if it had exited by itself.
    """
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        return "already_gone"
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return "already_gone"
    try:
        proc.wait(timeout=grace_seconds)
        outcome = "terminated"
    except subprocess.TimeoutExpired:
        outcome = "killed"

    # SIGKILL the group unconditionally, even when the leader exited politely.
    # An earlier version sent signal 0 on that path, which asks whether the
    # group exists and does nothing about it — so a worker that ignored or
    # outlived SIGTERM was left running, which is the exact failure this
    # function exists to prevent. SIGKILL to an empty group is harmless.
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pgid, signal.SIGKILL)
    with contextlib.suppress(subprocess.TimeoutExpired):
        proc.wait(timeout=grace_seconds)
    return outcome


class SubprocessRunner(Runner):
    """Runs a CLI agent non-interactively in a throwaway clone.

    The command template comes from the operator's config, never from pull
    request content. The environment is built by `build_env`, so a PR cannot
    widen it either.
    """

    def __init__(self, kind: str, config: dict, workspace_root: pathlib.Path,
                 role: str | None = None):
        self.kind = kind
        self.role = role or kind
        self._config = config
        self._workspace_root = pathlib.Path(workspace_root)
        self._identity = f"{kind}-{config.get('identity_suffix', uuid.uuid4().hex[:8])}"
        if not config.get("enabled", False):
            raise RunnerError(
                f"{kind} runner is disabled in config. Live dispatch is off by default; "
                "enable it only with an explicit run budget and an operator stop switch."
            )
        if self.role not in ROLE_CREDENTIALS:
            raise RunnerError(f"unknown runner role {self.role!r}")
        self._current = None

    def cancel_current(self, grace_seconds: float | None = None) -> str:
        """Level 3 of the cancel ladder: stop the runner that is running NOW.

        Levels 1 and 2 (stop dispatch, cancel the task) only decide what happens
        at the next checkpoint; neither reaches inside a child that is already
        executing. This does, and it does not undo anything the child already
        pushed — that needs a revert, which is a separate authorised action.
        """
        proc = self._current
        if proc is None:
            return "nothing_running"
        return terminate_process_group(
            proc, self._config.get("terminate_grace_seconds", 10)
            if grace_seconds is None else grace_seconds)

    def identity(self) -> str:
        return self._identity

    def environment(self, parent: dict | None = None) -> dict:
        return build_env(self.role, parent)

    def _require_auth(self, parent: dict | None = None) -> None:
        if not has_credential(self.role, parent):
            raise AuthUnavailable(
                f"{self.kind}: no model credential available to this role. "
                "Refusing to run rather than reporting an unverified result."
            )

    def _workspace(self, order: dict, env: dict) -> pathlib.Path:
        path = self._workspace_root / f"{self.kind}-{order['task_id']}-{order['head'][:7]}"
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
        repo = path / "repo"
        subprocess.run(["git", "clone", "--quiet", order["repo_url"], str(repo)],
                       check=True, timeout=self._config.get("clone_timeout", 300), env=env)
        subprocess.run(["git", "checkout", "--quiet", order["head"]],
                       cwd=repo, check=True, timeout=60, env=env)
        return repo

    def run(self, order: dict) -> dict:
        env = self.environment()
        self._require_auth()
        repo = self._workspace(order, env)
        cmd = [part.format(prompt_file=order["prompt_file"], head=order["head"])
               for part in self._config["command"]]
        limit = self._config.get("timeout_seconds", 1200)
        grace = self._config.get("terminate_grace_seconds", 10)
        # start_new_session puts the runner in its own process group, which is
        # the only way to reach the processes IT starts. Without it a timeout
        # kills the runner and leaves its workers holding the credentials.
        proc = subprocess.Popen(
            cmd, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, env=env, start_new_session=True)
        self._current = proc
        try:
            stdout, _stderr = proc.communicate(timeout=limit)
        except subprocess.TimeoutExpired:
            outcome = terminate_process_group(proc, grace)
            raise RunnerError(f"{self.kind}: timed out after {limit}s; "
                              f"process group {outcome}")
        finally:
            self._current = None
        result = subprocess.CompletedProcess(cmd, proc.returncode, stdout, None)
        if result.returncode != 0:
            # The child's stdout/stderr may carry a provider error body or a raw
            # log line. Neither is shown: the exit code is the diagnostic that
            # cannot itself be a secret. Same rule as ab_test.py's P5-01.
            raise RunnerError(
                f"{self.kind}: exited {result.returncode}. Output withheld — a runner's "
                "stdout can carry a provider error body or log content."
            )
        return parse_verdict(self.kind, result.stdout)


def parse_verdict(kind: str, stdout: str) -> dict:
    """Turn a runner's stdout into a verdict, or refuse.

    `exit 0` is not a verdict. An unparseable or structurally wrong answer is a
    failure, never an approval. Error text never quotes the payload, because the
    payload is exactly where a secret or a log line would be.
    """
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RunnerError(f"{kind}: produced no parseable verdict "
                          f"({len(stdout)} bytes, not shown)") from exc
    if not isinstance(payload, dict):
        raise RunnerError(f"{kind}: verdict is not an object")
    if kind == "executor":
        head = payload.get("new_head")
        if not isinstance(head, str) or len(head) != 40 or not all(
                c in "0123456789abcdef" for c in head):
            raise RunnerError("executor: new_head is missing or not a full commit sha")
        return {"new_head": head}
    review = payload.get("review")
    if not isinstance(review, dict):
        raise RunnerError("reviewer: no review object")
    for field in ("head", "reviewer", "decision"):
        if not isinstance(review.get(field), str) or not review[field]:
            raise RunnerError(f"reviewer: review.{field} missing")
    evidence = review.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(
            isinstance(x, str) and x for x in evidence):
        raise RunnerError("reviewer: review cites no evidence")
    return {"review": review}

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
import re
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

# Carrying the caller's own session id into a runner makes that runner a
# continuation of the caller rather than a separate run. Measured: with the
# full parent environment the CLI returned the CALLER's session id and read the
# caller's cached prefix; with the allowlist it returned a fresh one. Reviewer
# independence depends on this, so the variable is named rather than merely
# omitted — an allowlist that happens to exclude it is not the same as a rule.
DENY_SESSION_IDENTITY = ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_REMOTE_SESSION_ID")

# How much of a boundary the operator has actually built around a runner.
#
#   "process_env"  only this module's environment filtering.
#   "container"    a container or namespace the operator has verified.
#
# These are not two grades of the same thing. MEASURED on this host
# (evidence/auth_isolation_probe.json): under "process_env", with an
# environment of four variables, no credential among them and HOME pointing at
# an empty directory, the model CLI still authenticated and still billed. So
# "process_env" is a tidiness measure, NOT a credential boundary, and the code
# must not let anyone spend untrusted code against it.
ISOLATION_LEVELS = ("process_env", "container")
ROLES_REQUIRING_REAL_ISOLATION = ("pr_tests",)



class RunnerError(RuntimeError):
    """A runner could not produce a verdict. Never interpreted as success."""


class IsolationUnavailable(RunnerError):
    """The requested role needs a boundary the operator has not established.

    Raised instead of running, because the alternative is to run untrusted code
    in an environment that was measured to reach a live, billable credential.
    """


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
    env = {k: source[k] for k in BASE_ENV_ALLOWLIST
           if k in source and k not in DENY_SESSION_IDENTITY}
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
    """Is a model credential present **as an environment variable**?

    Note what this cannot tell you. On the host this was measured on, every
    role authenticated a real, billed model call while this function returned
    False for all three (evidence/auth_isolation_probe.json). The credential
    was not in the environment and not in HOME; it was reachable anyway.

    So a False here means "no credential in the environment", which is not the
    same as "cannot authenticate", and the two must never be conflated again —
    the previous code used this as a hard gate and would have reported
    BLOCKED_ACCESS for a runner that works.
    """
    source = os.environ if parent is None else parent
    return any(name in source and source[name]
               for name in ROLE_CREDENTIALS[role]
               if name not in ("GITHUB_TOKEN", "GH_TOKEN"))


def credential_state(role: str, parent: dict | None = None) -> str:
    """What can honestly be said about this role's ability to authenticate.

    Three states, because two would force a guess:

      "env_credential"          a credential is present in the environment.
      "ambient_possible"        none is, but this host may still authenticate
                                by a route this process cannot see. Measured
                                to happen. Not a failure; not a guarantee.
      "declared_unavailable"    the operator asserted, in config, that this
                                host has no ambient route. Only an operator can
                                know that, so only an operator may assert it.
    """
    if has_credential(role, parent):
        return "env_credential"
    source = os.environ if parent is None else parent
    if str(source.get("ATK_NO_AMBIENT_MODEL_AUTH", "")).lower() in ("1", "true", "yes"):
        return "declared_unavailable"
    return "ambient_possible"


# Candidate boundaries, in the order they are tried. Each is PROBED, never
# assumed: the reviewer's environment had none of these working while this
# author's had one, so "container" must mean "checked here, now".
CONTAINER_BACKENDS = (
    ("unshare", ["unshare", "--user", "--map-root-user", "--net", "true"]),
    ("bwrap", ["bwrap", "--unshare-all", "--ro-bind", "/", "/", "/usr/bin/true"]),
    ("docker", ["docker", "info"]),
)


def working_container_backend(timeout: float = 20.0):
    """Return the name of a backend that actually runs here, or None."""
    for name, probe in CONTAINER_BACKENDS:
        if shutil.which(probe[0]) is None:
            continue
        try:
            # An explicit env here too: the suite requires every subprocess in
            # this module to state what it passes, and a capability probe that
            # inherits 142 variables is not a probe of the same thing.
            r = subprocess.run(probe, capture_output=True, timeout=timeout,
                               stdin=subprocess.DEVNULL,
                               env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")})
        except (OSError, subprocess.TimeoutExpired):
            continue
        if r.returncode == 0:
            return name
    return None


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


COMMAND_PLACEHOLDERS = ("prompt_file", "head", "work_order", "deadline_seconds")

_PLACEHOLDER_RE = re.compile(r"\{(" + "|".join(COMMAND_PLACEHOLDERS) + r")\}")

# A brace followed immediately by a bare identifier and a closing brace is a
# placeholder the author meant; JSON always has a quote or space after `{`.
# Anything matching this shape that is NOT a known placeholder is a typo, and
# silently leaving it in the command would ship a broken prompt.
_LOOKS_LIKE_PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


class CommandTemplateError(RunnerError):
    """The operator's command template cannot be filled in.

    A separate type because this is a configuration fault found before any
    dispatch, not a runner that failed. It used to surface as a bare KeyError
    from str.format and escape the structured failure path entirely.
    """


def render_command(parts, values: dict) -> list:
    """Fill the operator's command template WITHOUT touching JSON braces.

    The previous code called `str.format` on every element. The shipped live
    template tells the model to emit `{"new_head": "<sha>"}`, and str.format
    reads `{"new_head"}` as a field name, so building the command raised
    KeyError: '"new_head"' — reproduced against the shipped file in
    evidence/live_template_repro.txt. The template could never have launched,
    and the error was not a RunnerError, so it did not even fail the way the
    rest of this module promises to fail.

    Only the four names in COMMAND_PLACEHOLDERS are substituted. Every other
    brace is left exactly as the operator wrote it, which is the whole point:
    a prompt that describes JSON is data, not a format string.
    """
    missing = set()
    unknown = set()
    out = []
    for part in parts:
        if not isinstance(part, str):
            raise CommandTemplateError("command elements must be strings")

        def sub(m):
            name = m.group(1)
            if name not in values:
                missing.add(name)
                return m.group(0)
            return str(values[name])

        rendered = _PLACEHOLDER_RE.sub(sub, part)
        unknown |= {m for m in _LOOKS_LIKE_PLACEHOLDER_RE.findall(rendered)
                    if m not in COMMAND_PLACEHOLDERS}
        out.append(rendered)
    if unknown:
        raise CommandTemplateError(
            f"command template uses unknown placeholder(s) {sorted(unknown)}; "
            f"supported: {sorted(COMMAND_PLACEHOLDERS)}")
    if missing:
        raise CommandTemplateError(
            f"command template uses placeholder(s) {sorted(missing)} that this "
            "runner does not supply")
    return out


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

    # If the child was NOT started with start_new_session=True it shares OUR
    # process group, and killing that group kills the controller itself. Found
    # by mutation testing: removing start_new_session made the test suite die
    # of SIGTERM rather than report a failure, because this function turned
    # around and signalled its own caller. Refuse loudly instead.
    if pgid == os.getpgid(0):
        raise RunnerError(
            "refusing to signal my own process group: this child was not started "
            "with start_new_session=True, so it has no group of its own and "
            "killing it would kill the controller."
        )
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
        self._credential_state = None
        self._isolation_level = None
        self._require_isolation()

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
        """Block only when the operator has said authentication is impossible.

        This used to block whenever no credential was in the environment. That
        was measured to be wrong on this host: all three roles authenticated a
        real model call while the environment held no credential at all. The
        old gate would have turned a working runner into BLOCKED_ACCESS, which
        is the same class of error as reporting success without running — an
        outcome decided by inspection rather than by what happened.

        What stays true: a runner that cannot authenticate must never be
        recorded as having done the work. That is now enforced where it can be
        known — at the runner's own exit code and verdict — instead of guessed
        here.
        """
        state = credential_state(self.role, parent)
        if state == "declared_unavailable":
            raise AuthUnavailable(
                f"{self.kind}: the operator declared this host has no model "
                "credential (ATK_NO_AMBIENT_MODEL_AUTH). Refusing to run "
                "rather than reporting an unverified result."
            )
        self._credential_state = state

    def _require_isolation(self) -> None:
        """Refuse a role whose boundary has not actually been built.

        `pr_tests` runs code from the pull request under review. The repository
        previously documented that this role "receives no credential of any
        kind" and tested it by listing environment variables. Measured against
        the real CLI, that role authenticated and billed
        (evidence/auth_isolation_probe.json). Environment filtering was never
        the boundary; it only looked like one.

        So the boundary has to be declared and, by declaring it, owned:
        `isolation_level: "container"` means an operator built and checked one.
        Absent that, this refuses rather than running untrusted code next to a
        live credential.
        """
        level = self._config.get("isolation_level", "process_env")
        if level not in ISOLATION_LEVELS:
            raise RunnerError(f"unknown isolation_level {level!r}")
        if level == "container" and not self._container_backend_works():
            raise IsolationUnavailable(
                "isolation_level='container' was declared, but no working backend "
                "was found on this host. Declaring a boundary is not building one, "
                "so this refuses rather than trusting the declaration. Checked: "
                f"{', '.join(n for n, _ in CONTAINER_BACKENDS)}.")
        if self.role in ROLES_REQUIRING_REAL_ISOLATION and level != "container":
            raise IsolationUnavailable(
                f"role {self.role!r} runs untrusted pull-request code and needs "
                f"isolation_level='container'; this config says {level!r}. "
                "Environment filtering was measured not to keep a model "
                "credential out of this role on at least one host, so it is "
                "not accepted as the boundary."
            )
        self._isolation_level = level

    WORK_ORDER_FIELDS = ("task_id", "goal", "scope_paths", "acceptance", "decision_ids",
                         "repo_url", "branch", "head", "policy_sha", "phase", "run_id",
                         "run_identity", "executor_identity", "command_allowlist",
                         "deadline", "deadline_seconds", "event_id", "attempt", "review")

    def _container_backend_works(self) -> bool:
        self._container_backend = working_container_backend()
        return self._container_backend is not None

    def _write_work_order(self, order: dict, repo: pathlib.Path) -> pathlib.Path:
        """Hand the runner the whole contract, in a file the PR cannot rewrite.

        Before this, `run` substituted only `prompt_file` and `head` into the
        command, and `prompt_file` was a path *inside the pull request's own
        clone*. So the fields the controller assembled — goal, scope_paths,
        acceptance, decision_ids, policy_sha, run identity, deadline — existed
        in a dict, were logged, and never reached the process they were meant
        to bind. A record of a contract is not the contract.

        The file is written to the workspace root, a sibling of the clone, so
        content under review cannot edit its own instructions.
        """
        payload = {k: order[k] for k in self.WORK_ORDER_FIELDS if k in order}
        missing = [k for k in ("task_id", "head", "policy_sha", "phase", "run_identity")
                   if not payload.get(k)]
        if missing:
            raise RunnerError(f"work order is missing required field(s): {missing}")
        path = repo.parent / "work_order.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        path.chmod(0o400)
        return path

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
        work_order_path = self._write_work_order(order, repo)
        cmd = render_command(self._config["command"], {
            "prompt_file": order["prompt_file"],
            "head": order["head"],
            "work_order": str(work_order_path),
            "deadline_seconds": int(order.get("deadline_seconds")
                                    or self._config.get("timeout_seconds", 1200)),
        })
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
            # communicate() closes these on the normal path; on the timeout and
            # cancel paths nothing did, so every timed-out runner leaked two
            # descriptors. Found as a ResourceWarning from the adapter's own
            # tests rather than from reading the code.
            for stream in (proc.stdout, proc.stderr, proc.stdin):
                if stream is not None and not stream.closed:
                    with contextlib.suppress(OSError):
                        stream.close()
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

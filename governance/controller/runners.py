#!/usr/bin/env python3
"""Runner adapters: how the controller actually starts an executor or a reviewer.

Three implementations, all behind one interface:

  FakeExecutor / FakeReviewer  — scripted, no model call, no network. These are
      what the replay uses. They prove the CONTROLLER works; they prove nothing
      about an AI doing real work, and the replay is labelled REPLAY_VERIFIED
      rather than ACTIVE for exactly that reason.

  SubprocessRunner — the real adapter. Launches a CLI agent non-interactively
      in an isolated workspace and parses its JSON verdict. **Disabled by
      default** (`enabled: false` in the config) so that importing or running
      this module can never start a paid call by accident.

The reviewer runs in its own clone. Isolation here means a separate working
directory and a separate process with a separate run identity — not a separate
model. Two runs of the same model are not independent sources, and the
governance rules require that to be stated rather than implied.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import uuid


class RunnerError(RuntimeError):
    pass


class Runner:
    """Interface. `run(order)` returns a dict; it must not touch the store."""

    kind = "abstract"

    def identity(self) -> str:
        raise NotImplementedError

    def run(self, order: dict) -> dict:
        raise NotImplementedError


# --------------------------------------------------------------------------
# Test doubles
# --------------------------------------------------------------------------

class FakeExecutor(Runner):
    """Produces a new commit-like SHA per attempt, from a scripted list."""

    kind = "executor"

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
    """Returns scripted verdicts, bound to whatever head it was given."""

    kind = "reviewer"

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
                "head": order["head"],              # bound to the head it was handed
                "reviewer": self._identity,
                "decision": decision,
                "evidence": [f"replay://{order['task_id']}/{order['head'][:7]}/{decision}"],
            },
        }


# --------------------------------------------------------------------------
# Real adapter — off unless explicitly enabled
# --------------------------------------------------------------------------

class SubprocessRunner(Runner):
    """Runs a CLI agent non-interactively in a throwaway clone.

    The command template is supplied by config, never built from PR content.
    Credentials come from the trusted environment the operator injects; nothing
    here reads, writes or logs a secret value.
    """

    def __init__(self, kind: str, config: dict, workspace_root: pathlib.Path):
        self.kind = kind
        self._config = config
        self._workspace_root = pathlib.Path(workspace_root)
        self._identity = f"{kind}-{config.get('identity_suffix', uuid.uuid4().hex[:8])}"
        if not config.get("enabled", False):
            raise RunnerError(
                f"{kind} runner is disabled in config. Live dispatch is off by default; "
                "enable it only with an explicit budget and an operator stop switch."
            )

    def identity(self) -> str:
        return self._identity

    def _workspace(self, order: dict) -> pathlib.Path:
        path = self._workspace_root / f"{self.kind}-{order['task_id']}-{order['head'][:7]}"
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
        subprocess.run(["git", "clone", "--quiet", order["repo_url"], str(path / "repo")],
                       check=True, timeout=self._config.get("clone_timeout", 300))
        subprocess.run(["git", "checkout", "--quiet", order["head"]],
                       cwd=path / "repo", check=True, timeout=60)
        return path / "repo"

    def run(self, order: dict) -> dict:
        repo = self._workspace(order)
        cmd = [part.format(prompt_file=order["prompt_file"], head=order["head"])
               for part in self._config["command"]]
        result = subprocess.run(
            cmd, cwd=repo, capture_output=True, text=True,
            timeout=self._config.get("timeout_seconds", 1800),
            env=self._config.get("env_passthrough_only", None),
        )
        if result.returncode != 0:
            raise RunnerError(f"{self.kind} exited {result.returncode}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            # exit 0 is not a verdict; an unparseable answer is a failure, not an approval
            raise RunnerError(f"{self.kind} produced no parseable verdict") from exc
        return payload

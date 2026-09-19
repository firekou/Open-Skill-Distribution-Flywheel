#!/usr/bin/env python3
"""The handoff controller.

It owns exactly one job: move a task through
    READY -> EXECUTING -> REVIEW_PENDING -> REVIEWING -> (COMPLETE | FIX_PENDING | ...)
without a human carrying anything between the steps.

It decides nothing about content. Every dispatch and every review outcome is
put to `governance/preflight.py` — the trusted guard on main — and the
controller obeys the verdict. `exit 0` from a runner is not an approval, and
the controller never reads a review verdict from anywhere except the runner it
itself started.

Trust boundary, stated because it is the one that matters: the rules, the guard
and the config are read from the operator's trusted checkout. Nothing under the
PR being reviewed can change how this process behaves. A work order is
assembled here from trusted inputs; a runner never hands one to itself.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
import time

from runners import RunnerError
from store import ConcurrencyError, Store

TERMINAL = {"COMPLETE", "STOPPED", "FAILED", "TIMEOUT", "CONDITIONS_PENDING",
            "NEEDS_INFORMATION", "BLOCKED_ACCESS", "WAITING_OWNER"}


def load_guard(path: pathlib.Path):
    """Import preflight.py from the TRUSTED checkout, by explicit path."""
    spec = importlib.util.spec_from_file_location("preflight_guard", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def live_head(repo_url: str, branch: str) -> str:
    """Always ask the remote. Never trust a stored snapshot — that is the rule
    that C2 in the foundation check was violating."""
    out = subprocess.run(["git", "ls-remote", repo_url, f"refs/heads/{branch}"],
                         capture_output=True, text=True, check=True, timeout=60).stdout
    if not out.strip():
        raise RuntimeError(f"branch {branch} not found on {repo_url}")
    return out.split()[0]


class Controller:
    def __init__(self, config: dict, store: Store, guard, executor, reviewer,
                 clock=time.time, head_resolver=live_head):
        self.config = config
        self.store = store
        self.guard = guard
        self.executor = executor
        self.reviewer = reviewer
        self._clock = clock
        self._head_of = head_resolver
        self.owner = config["controller_identity"]

    # ---------- helpers ----------

    def _stopped(self) -> bool:
        """Operator stop switch: a file on disk, checked before every action, so
        stopping never depends on this process being healthy enough to be asked."""
        return pathlib.Path(self.config["stop_file"]).exists()

    def _order(self, task_id: str, phase: str, head: str, event_id: str,
               run_identity: str, executor_identity: str, attempt: int,
               elapsed: float, review: dict | None = None) -> dict:
        state = self.store.read()
        order = {
            "task_id": task_id,
            "head": head,
            "live_head": self._head_of(self.config["repo_url"], self.config["branch"]),
            "phase": phase,
            "event_id": event_id,
            "seen_events": state["processed_events"],
            "revision": state["revision"],
            "expected_revision": state["revision"],
            "stopped": self._stopped(),
            "authorized": phase in self.config["authorized_phases"],
            "run_identity": run_identity,
            "executor_identity": executor_identity,
            "attempt": attempt,
            "max_attempts": self.config["max_attempts"],
            "cost": self.store.spend(),
            "budget": self.config["budget"],
            "elapsed": elapsed,
            "timeout": self.config["timeout_seconds"],
            "repo_url": self.config["repo_url"],
            "branch": self.config["branch"],
            "prompt_file": self.config["prompt_file"],
        }
        if review is not None:
            order["review"] = review
        return order

    def _ask(self, order: dict) -> dict:
        verdict = self.guard.evaluate(order)
        self.store.log(kind="guard", task=order["task_id"], phase=order["phase"],
                       head=order["head"][:12], event=order["event_id"],
                       run=order["run_identity"], verdict=verdict)
        return verdict

    # ---------- one step ----------

    def step(self, task_id: str, event_id: str) -> dict:
        """Advance the task by at most one phase. Idempotent per event_id."""
        started = self._clock()

        if event_id in self.store.seen_events():
            self.store.log(kind="dedup", task=task_id, event=event_id)
            return {"action": "NOOP", "reason": "duplicate"}

        try:
            self.store.acquire(task_id, self.owner, self.config["lease_seconds"])
        except ConcurrencyError as exc:
            self.store.log(kind="lease_denied", task=task_id, detail=str(exc))
            return {"action": "NOOP", "reason": "leased_elsewhere"}

        try:
            task = self.store.task(task_id)
            status = task.get("status", "READY")
            attempt = task.get("attempt", 0)

            if status in TERMINAL:
                return {"action": "NOOP", "reason": f"terminal:{status}"}

            head = task.get("last_head") or self._head_of(
                self.config["repo_url"], self.config["branch"])

            if status in ("READY", "FIX_PENDING"):
                return self._execute(task_id, event_id, head, attempt, started)
            if status in ("REVIEW_PENDING",):
                return self._review(task_id, event_id, head, attempt, started)
            return {"action": "NOOP", "reason": f"nothing_to_do_in:{status}"}
        finally:
            self.store.release(task_id, self.owner)

    # ---------- phases ----------

    def _execute(self, task_id, event_id, head, attempt, started):
        order = self._order(task_id, "execute", head, event_id,
                            run_identity=self.executor.identity(),
                            executor_identity=self.executor.identity(),
                            attempt=attempt, elapsed=self._clock() - started)
        verdict = self._ask(order)
        if verdict["action"] != "DISPATCH_ALLOWED":
            return self._halt(task_id, event_id, verdict)

        try:
            result = self.executor.run(order)
        except RunnerError as exc:
            self.store.mark_processed(event_id)
            self.store.set_task(task_id, status="FAILED", failure=str(exc),
                                recovery_point=f"head={head}")
            self.store.log(kind="runner_failed", task=task_id, role="executor", detail=str(exc))
            return {"action": "FAILED", "reason": str(exc)}

        self.store.add_spend(result.get("cost", 0.0))
        # The event is marked processed and the state advanced in that order, so a
        # crash between them re-runs a step that produced no state change, rather
        # than skipping one that did.
        self.store.mark_processed(event_id)
        self.store.set_task(task_id, status="REVIEW_PENDING",
                            last_head=result["new_head"],
                            executor_identity=self.executor.identity(),
                            attempt=attempt)
        self.store.log(kind="executed", task=task_id, new_head=result["new_head"][:12],
                       executor=self.executor.identity())
        return {"action": "REVIEW_PENDING", "head": result["new_head"]}

    def _review(self, task_id, event_id, head, attempt, started):
        task = self.store.task(task_id)
        executor_identity = task.get("executor_identity", self.executor.identity())

        order = self._order(task_id, "review", head, event_id,
                            run_identity=self.reviewer.identity(),
                            executor_identity=executor_identity,
                            attempt=attempt, elapsed=self._clock() - started)
        verdict = self._ask(order)
        if verdict["action"] != "DISPATCH_ALLOWED":
            return self._halt(task_id, event_id, verdict)

        try:
            result = self.reviewer.run(order)
        except RunnerError as exc:
            self.store.mark_processed(event_id)
            self.store.set_task(task_id, status="FAILED", failure=str(exc),
                                recovery_point=f"head={head}")
            return {"action": "FAILED", "reason": str(exc)}

        self.store.add_spend(result.get("cost", 0.0))

        # The verdict is put back through the guard, which re-checks that the
        # review is bound to this head and this reviewer, cites evidence, and
        # names a decision the state machine recognises.
        accept = self._order(task_id, "accept_review", head, f"{event_id}:accept",
                             run_identity=self.reviewer.identity(),
                             executor_identity=executor_identity,
                             attempt=attempt, elapsed=self._clock() - started,
                             review=result["review"])
        outcome = self._ask(accept)

        self.store.mark_processed(event_id)

        if outcome["action"] == "FIX_PENDING":
            self.store.set_task(task_id, status="FIX_PENDING", attempt=attempt + 1,
                                last_review=result["review"])
            return {"action": "FIX_PENDING", "attempt": attempt + 1}
        if outcome["action"] in ("COMPLETE", "CONDITIONS_PENDING", "NEEDS_INFORMATION"):
            self.store.set_task(task_id, status=outcome["action"],
                                last_review=result["review"],
                                reviewed_head=head)
            return {"action": outcome["action"], "head": head}
        return self._halt(task_id, event_id, outcome)

    def _halt(self, task_id, event_id, verdict):
        action = verdict["action"]
        if action == "NOOP":
            return verdict
        status = {"STOP": "STOPPED"}.get(action, "BLOCKED_ACCESS" if action == "REJECT" else action)
        self.store.set_task(task_id, status=status, halt_reason=verdict["reason"])
        self.store.log(kind="halted", task=task_id, verdict=verdict)
        return verdict

    # ---------- driver ----------

    def drive(self, task_id: str, max_steps: int = 12) -> list:
        """Run steps until the task reaches a terminal state or runs out of steps.

        This is the whole point: one start, no human in between.
        """
        trail = []
        for n in range(max_steps):
            result = self.step(task_id, f"evt-{task_id}-{n}")
            trail.append(result)
            status = self.store.task(task_id).get("status")
            if status in TERMINAL or result["action"] in ("NOOP", "FAILED"):
                break
        return trail


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Governance handoff controller")
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("--task", required=True)
    ap.add_argument("--max-steps", type=int, default=12)
    args = ap.parse_args(argv)

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("mode") != "replay":
        print("live mode is not enabled in this build; use the replay config "
              "or supply real runners with an explicit budget.", file=sys.stderr)
        return 2
    guard = load_guard(pathlib.Path(config["guard_path"]))
    store = Store(pathlib.Path(config["state_dir"]))
    from runners import FakeExecutor, FakeReviewer
    ctl = Controller(config, store, guard,
                     FakeExecutor(config["replay"]["executor_heads"]),
                     FakeReviewer(config["replay"]["reviewer_decisions"]))
    for line in ctl.drive(args.task, args.max_steps):
        print(json.dumps(line, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

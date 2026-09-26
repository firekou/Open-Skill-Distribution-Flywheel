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
import contextlib
import json
import pathlib
import subprocess
import sys
import threading
import time
import uuid

from runners import AuthUnavailable, RunnerError
from store import ConcurrencyError, Store

TERMINAL = {"COMPLETE", "STOPPED", "CANCELLED", "FAILED", "TIMEOUT",
            "CONDITIONS_PENDING", "NEEDS_INFORMATION", "BLOCKED_ACCESS",
            "WAITING_OWNER"}

# G3: four different things were all called "cancel". They stop different things
# and three of them are not interchangeable with the fourth.
#
#   L1 stop dispatch     the STOP file. No NEW runner starts. A runner already
#                        running is untouched.
#   L2 cancel one task   the CANCEL-<task> file. That task is abandoned at its
#                        next checkpoint and marked CANCELLED; other tasks and
#                        any runner already running are untouched.
#   L3 terminate runner  runners.terminate_process_group. Kills the runner and
#                        everything it started. Does NOT undo a commit the
#                        runner already pushed; that needs a revert, which is a
#                        separate authorised action.
#   L4 revoke credential NOT IMPLEMENTABLE HERE, and nothing in this repository
#                        should claim otherwise. Only the issuer can revoke a
#                        key — the Anthropic console for the model credential,
#                        GitHub for the token. If a runner has leaked or misused
#                        one, L1-L3 do not take it back and L4 is the only thing
#                        that does.
CANCEL_LADDER = ("stop_dispatch", "cancel_task", "terminate_runner", "revoke_credential")


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


def policy_sha(policy_repo: pathlib.Path) -> str:
    """The commit the trusted policy was read from.

    G2. The guard and the rules are loaded from the operator's checkout, but
    "which version" was never recorded, so a review could not be tied to the
    policy in force when it was dispatched. Pinning it also makes it checkable
    that nothing under the pull request supplied the policy.
    """
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=policy_repo,
                          capture_output=True, text=True, check=True,
                          timeout=30).stdout.strip()


def commit_is_on_branch(repo_url: str, branch: str, sha: str, workdir: pathlib.Path) -> bool:
    """Does this commit actually exist, and is it reachable from that branch?

    G2. The controller used to take the runner's word for `new_head`. A runner
    that reports a sha it never pushed — through a bug, a failed push, or
    otherwise — would have had the whole state machine advance on a commit that
    does not exist. Checked against the remote, not against the runner.
    """
    workdir = pathlib.Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    if not (workdir / ".git").exists():
        subprocess.run(["git", "init", "--quiet", "--bare" if False else "--", "."],
                       cwd=workdir, check=True, timeout=60)
    try:
        subprocess.run(["git", "fetch", "--quiet", "--depth", "50", repo_url,
                        f"refs/heads/{branch}"],
                       cwd=workdir, check=True, timeout=180,
                       capture_output=True)
    except subprocess.CalledProcessError:
        return False
    found = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                           cwd=workdir, capture_output=True, timeout=30)
    if found.returncode != 0:
        return False
    reachable = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "FETCH_HEAD"],
                               cwd=workdir, capture_output=True, timeout=60)
    return reachable.returncode == 0


RECEIPT_TRAILER = "ATK-Work-Receipt"


def work_receipt(task_id: str, intent_id: str) -> str:
    """The marker an executor must put in every commit it pushes for ONE intent.

    GOV-R2-03, third round: "the branch moved" is not "our push landed". A
    collaborator, a human or another job can move the same branch. The receipt
    is derived from the intent that was durably recorded BEFORE dispatch, so a
    commit carrying it can only have been made by a runner that was handed that
    work order.
    """
    return f"{task_id}/{intent_id}"


def commits_carry_receipt(repo_url: str, branch: str, base: str, live: str,
                          receipt: str, workdir: pathlib.Path):
    """True only if `base..live` is non-empty, `base` is an ancestor of `live`,
    and EVERY commit in that range carries `ATK-Work-Receipt: <receipt>`.

    False when the range was provably not (only) ours; None when it cannot be
    determined (fetch failed, commit missing, history too shallow). The caller
    treats anything but True as not confirmed.
    """
    workdir = pathlib.Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    if not (workdir / ".git").exists():
        subprocess.run(["git", "init", "--quiet", "--", "."], cwd=workdir, check=True,
                       timeout=60)
    try:
        subprocess.run(["git", "fetch", "--quiet", "--depth", "50", repo_url,
                        f"refs/heads/{branch}"],
                       cwd=workdir, check=True, timeout=180, capture_output=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    for sha in (base, live):
        if subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=workdir,
                          capture_output=True, timeout=30).returncode != 0:
            return None
    if subprocess.run(["git", "merge-base", "--is-ancestor", base, live], cwd=workdir,
                      capture_output=True, timeout=60).returncode != 0:
        return False
    log = subprocess.run(["git", "log", "--format=%H%x00%B%x1e", f"{base}..{live}"],
                         cwd=workdir, capture_output=True, text=True, timeout=60)
    if log.returncode != 0:
        return None
    bodies = [c for c in log.stdout.split("\x1e") if c.strip()]
    if not bodies:
        return False
    line = f"{RECEIPT_TRAILER}: {receipt}"
    return all(line in body.splitlines() for body in
               (b.split("\x00", 1)[1] if "\x00" in b else b for b in bodies))


def scripted_receipt_verifier(receipted_heads):
    """Replay stand-in for `commits_carry_receipt`: the fixture says which heads
    were pushed WITH a receipt. Anything else is not confirmed."""
    allowed = frozenset(receipted_heads)

    def verify(_repo, _branch, _base, live, _receipt):
        return live in allowed

    return verify


def scripted_commit_verifier(allowed_heads):
    """The commit verifier for replay, where there is no remote to ask.

    Returning True for everything would delete the control G2 exists for: the
    whole point of checking a reported head is that an invented one is refused.
    The replay's heads are invented on purpose, so this accepts exactly the ones
    the fixture scripted and refuses everything else — including a head the
    executor made up beyond its script.

    Found by running replay.py after the verification landed: the fixture went
    straight to FAILED / reported_head_not_on_branch, because the new check was
    wired into Controller but into neither replay entry point.
    """
    allowed = frozenset(allowed_heads)

    def verify(_repo, _branch, sha):
        return sha in allowed

    return verify


class Controller:
    def __init__(self, config: dict, store: Store, guard, executor, reviewer,
                 clock=time.time, head_resolver=live_head, commit_verifier=None,
                 policy_sha_value=None, receipt_verifier=None):
        self.config = config
        self.store = store
        self.guard = guard
        self.executor = executor
        self.reviewer = reviewer
        self._clock = clock
        self._head_of = head_resolver
        # G2: a runner's self-reported new_head is a claim, not a fact. Replay
        # overrides this with a stub; live runs check the remote.
        self._commit_is_on_branch = commit_verifier or (
            lambda repo, branch, sha: commit_is_on_branch(
                repo, branch, sha, pathlib.Path(config["state_dir"]) / "verify"))
        self.policy_sha = policy_sha_value or config.get("policy_sha") or "unrecorded"
        # GOV-R2-03: attribution of a branch move to THIS work, not just the move.
        self._receipt_is_on = receipt_verifier or (
            lambda repo, branch, base, live, receipt: commits_carry_receipt(
                repo, branch, base, live, receipt,
                pathlib.Path(config["state_dir"]) / "verify-receipt"))
        self._generation = None
        # R2-02: one identity per INVOCATION, not per config. A static
        # controller_identity meant Store.acquire — which only refuses a live
        # lease held by a DIFFERENT owner — let a second tick started from the
        # same config walk straight into a task the first one was working on.
        self.owner = f"{config['controller_identity']}/{uuid.uuid4().hex[:8]}"

    # ---------- helpers ----------

    def _stopped(self) -> bool:
        """L1, stop dispatch. A file on disk, checked before every action, so
        stopping never depends on this process being healthy enough to be asked.

        This stops the NEXT runner from starting. It does not reach a runner
        that is already running — that is L3. Conflating the two is how an
        operator comes to believe a stop file ended a model call that is in
        fact still going.
        """
        return pathlib.Path(self.config["stop_file"]).exists()

    def _cancel_path(self, task_id: str) -> pathlib.Path:
        """L2 is per task, so the switch is per task too. A single shared file
        would make 'cancel this one' indistinguishable from 'stop everything'."""
        return pathlib.Path(self.config["stop_file"]).with_name(f"CANCEL-{task_id}")

    def _cancelled(self, task_id: str) -> bool:
        return self._cancel_path(task_id).exists()

    def cancel_runner(self, which: str = "both", grace_seconds: float | None = None) -> dict:
        """L3, terminate the runner that is running NOW, and its children.

        Only the process holding the child can do this, so it is a method on the
        controller rather than a file an operator touches. It does not undo a
        push the runner already made.
        """
        out = {}
        for name in ("executor", "reviewer"):
            if which not in ("both", name):
                continue
            runner = getattr(self, name)
            cancel = getattr(runner, "cancel_current", None)
            out[name] = cancel(grace_seconds) if callable(cancel) else "not_cancellable"
        self.store.log(kind="cancel_runner", detail=out)
        return out

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
            # The guard compares cost against budget numerically; it does not care
            # what the unit is. On a subscription there is no per-call money to
            # meter, so the unit here is RUNS — one runner invocation costs 1.
            # That is the thing which actually runs out on a subscription plan,
            # and it is the only cap this process can enforce by itself.
            # Reserve the run this dispatch is about to start, so the guard's
            # `cost > budget` is a PRE-dispatch check. Reporting the spend as it
            # stands lets the last allowed call start one more runner than the
            # budget permits — a real off-by-one on the cap that protects the
            # subscription. `accept_review` starts no runner, so it reserves none.
            "cost": self.store.spend() + (1 if phase in ("execute", "review") else 0),
            "budget": self.config["run_budget"],
            # GOV-R2-05: the ROUND's elapsed time, not this step's. `elapsed`
            # used to be reset on every step, so the guard's own
            # `elapsed >= timeout` STOP — the check that actually enforces the
            # round limit — could never fire however many steps ran. Passing
            # the round's real age makes the trusted guard the thing that stops
            # an overrun, instead of a number the controller clamps to 1.
            "elapsed": max(0.0, self.config["timeout_seconds"]
                           - self._remaining_round_seconds(task_id)),
            "step_elapsed": elapsed,
            "timeout": self.config["timeout_seconds"],
            "repo_url": self.config["repo_url"],
            "branch": self.config["branch"],
            "prompt_file": self.config["prompt_file"],
            # G3: the work-order contract. policy_sha ties the order to the
            # version of the rules in force; scope_paths and acceptance make the
            # order self-describing rather than implied by whoever wrote it.
            "policy_sha": self.policy_sha,
            "goal": self.config.get("goal", ""),
            "scope_paths": self.config.get("scope_paths", []),
            "acceptance": self.config.get("acceptance", ""),
            "decision_ids": self.config.get("decision_ids", []),
            "run_id": f"{run_identity}:{event_id}",
            "command_allowlist": self.config.get("command_allowlist", []),
            "deadline": self.config.get("timeout_seconds"),
            # R2-05: the runner takes the SMALLER of its own limit and what is
            # left of the round, so a late step cannot reset the round budget.
            "deadline_seconds": max(1, int(self._remaining_round_seconds(task_id))),
            # R3: the runner recomputes what is left from this ABSOLUTE instant
            # every time it is asked, because the clone and the checkout spend
            # real time before the model starts. The previous build shipped
            # `deadline_seconds` only; runners._remaining read `deadline_at`,
            # found nothing, and silently fell back to the runner's own full
            # timeout — so the round limit reached the prompt and bounded
            # nothing. A field read by one side and never written by the other
            # is the same defect as a guard nothing calls.
            "deadline_at": self._round_deadline_at(task_id),
            "evidence": [],
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

    @contextlib.contextmanager
    def _lease_kept_alive(self, task_id: str, ttl: float, on_lost=None, token=None):
        """Renew the lease for as long as the runner is running.

        `renew` was written, tested and never called. Meanwhile the shipped
        template gave a runner up to 1500s (1200 model + 300 clone) under a
        900s lease, so a long job outlived its own lease and the task became
        claimable by anyone while its worker was still writing.

        GOV-R2-02, second pass: recording the failure and letting the runner
        finish was not enough. Once the lease is gone another worker may
        already be running the SAME task, so the child here has to be stopped
        at the moment we learn we are no longer entitled to it — not after it
        has spent the rest of its timeout doing work nobody will accept and
        possibly pushing it. `on_lost` is the runner; it is cancelled from the
        heartbeat thread, which is the only thread that knows.
        """
        stop = threading.Event()
        failures = []

        def beat():
            # A third of the TTL: two renewals may be missed before expiry.
            while not stop.wait(max(1.0, ttl / 3.0)):
                try:
                    self.store.renew(task_id, self.owner, ttl)
                except Exception as exc:          # lost it, or the store is gone
                    failures.append(exc)
                    # GOV-R2-02, third round: set the token BEFORE trying to
                    # kill anything. If the runner is still cloning there is no
                    # child yet; the token is what stops it from starting one.
                    if token is not None:
                        token.set()
                    if on_lost is not None:
                        cancel = getattr(on_lost, "cancel_current", None)
                        try:
                            outcome = cancel() if callable(cancel) else "not_cancellable"
                        except Exception as kill_exc:      # noqa: BLE001
                            outcome = f"cancel_failed:{kill_exc}"
                        self.store.log(kind="cancel_on_lease_loss", task=task_id,
                                       detail=str(exc), outcome=outcome)
                    return

        t = threading.Thread(target=beat, daemon=True)
        t.start()
        try:
            yield failures
        finally:
            stop.set()
            t.join(timeout=5)

    def _run_with_lease(self, runner, task_id: str, order: dict) -> dict:
        """Run the runner under a kept-alive lease, and refuse its result if
        the lease was lost while it ran.

        The runner's own exception is held until the lease question is
        settled: a child killed BECAUSE we lost the lease exits non-zero, and
        reporting that as `FAILED` would write a result we are not entitled to
        write, under a plausible-looking reason.
        """
        ttl = self.config["lease_seconds"]
        failure = None
        result = None
        token = threading.Event()               # one per run, monotonic
        bind = getattr(runner, "bind_cancellation", None)
        if callable(bind):
            bind(token)
        with self._lease_kept_alive(task_id, ttl, on_lost=runner,
                                    token=token) as renew_failures:
            try:
                result = runner.run(order)
            except Exception as exc:              # noqa: BLE001  re-raised below
                failure = exc
        if renew_failures:
            raise ConcurrencyError(f"lease renewal failed: {renew_failures[0]}")
        if failure is not None:
            raise failure
        self._fence(task_id)
        return result

    def _observe_effect(self, head_at_dispatch: str, receipt: str | None = None):
        """Go and look: did the branch move while we were not recording?

        This is the only external fact this process can check by itself. It
        answers the question an open intent asks — "did the thing we were about
        to do actually happen" — for the executor's push. It does NOT answer
        "did a model call happen", which nothing here can observe, and it does
        not pretend to: an unreachable remote returns `effect_unknown` rather
        than the convenient `effect_refuted`.
        """
        try:
            live = self._head_of(self.config["repo_url"], self.config["branch"])
        except Exception as exc:                   # noqa: BLE001
            self.store.log(kind="observe_failed", detail=str(exc))
            return "effect_unknown", None
        if not isinstance(live, str) or not live:
            return "effect_unknown", None
        if live == head_at_dispatch:
            return "effect_refuted", live
        # GOV-R2-03, third round: the branch moved. That proves SOMETHING was
        # pushed, not that this work pushed it. Confirm only when every new
        # commit carries this intent's receipt; otherwise it is unknown, which
        # halts instead of advancing on someone else's commit.
        if not receipt:
            return "effect_unknown", live
        try:
            ours = self._receipt_is_on(self.config["repo_url"], self.config["branch"],
                                       head_at_dispatch, live, receipt)
        except Exception as exc:                   # noqa: BLE001
            self.store.log(kind="receipt_check_failed", detail=str(exc))
            ours = None
        if ours is True:
            return "effect_confirmed", live
        self.store.log(kind="unattributed_branch_move", base=head_at_dispatch[:12],
                       live=live[:12], receipt=receipt, verified=ours)
        return "effect_unknown", live

    def _reconcile(self, task_id: str, generation, event_id: str):
        """Settle every intent left open by a worker that died mid-dispatch.

        GOV-R2-03: `record_intent` wrote these and NOTHING read them. A
        restarted controller went straight back to dispatch, so the one case
        the ledger exists for — the executor pushed and the process died before
        the push was recorded — re-ran the executor on top of its own unrecorded
        work.

        Returns None when the task is safe to carry on with, or a step result
        when reconciliation itself is the outcome of this event.
        """
        intents = self.store.open_intents(task_id)
        if not intents:
            return None
        for intent in intents:
            receipt = (work_receipt(task_id, intent["intent_id"])
                       if intent.get("action") == "execute" else None)
            outcome, live = self._observe_effect(intent.get("head", ""), receipt)
            recon_event = f"reconcile:{intent['intent_id']}"
            fields = {}
            decision = "resume"
            if outcome == "effect_unknown":
                decision = "halt"
                fields = {"status": "NEEDS_INFORMATION",
                          "failure": "an intent was left open by a worker that did not "
                                     "return, and it cannot be shown whether its effect "
                                     "landed: the remote could not be asked, or the "
                                     "branch moved without this intent's work receipt. "
                                     "Re-dispatching could duplicate a push; advancing "
                                     "could accept somebody else's commit as this work.",
                          "observed_head": live}
            elif outcome == "effect_confirmed" and intent.get("action") == "execute":
                # The push landed. Re-running the executor would duplicate it.
                fields = {"status": "REVIEW_PENDING", "last_head": live,
                          "recovered_from": intent["intent_id"]}
            elif outcome == "effect_confirmed":
                # A reviewer is specified read-only. If the branch moved under
                # one, the assumption this recovery rests on is wrong, and
                # guessing is worse than stopping.
                decision = "halt"
                fields = {"status": "NEEDS_INFORMATION",
                          "failure": f"the branch moved to {live[:12]} during a "
                                     f"{intent.get('action')} intent, which is specified "
                                     "not to write. Reconciliation cannot tell what ran."}
            else:
                # effect_refuted: nothing landed, so the work may simply be redone.
                fields = {"recovered_from": intent["intent_id"]}
            try:
                self.store.commit_event_and_task(
                    recon_event, task_id,
                    close_intent_id=intent["intent_id"], close_outcome=outcome,
                    require_owner=self.owner, require_generation=generation,
                    **fields)
            except ConcurrencyError as exc:
                self.store.log(kind="reconcile_refused", task=task_id, detail=str(exc))
                return {"action": "NOOP", "reason": "lease_lost_during_reconcile"}
            self.store.log(kind="reconciled", task=task_id, intent=intent["intent_id"],
                           action=intent.get("action"), outcome=outcome,
                           decision=decision)
            if decision == "halt":
                self.store.mark_processed(event_id)
                return {"action": "NEEDS_INFORMATION", "reason": f"unreconciled:{outcome}"}
        return None

    def _commit(self, event_id: str, task_id: str, generation, **kwargs) -> bool:
        """Every state-advancing commit, fenced by the lease we acquired.

        GOV-R2-02: `commit_event_and_task` grew `require_owner` /
        `require_generation` and not one call site passed them, so the check
        ran only in its own unit test. A parameter no caller supplies defends
        nothing.
        """
        try:
            self.store.commit_event_and_task(
                event_id, task_id, require_owner=self.owner,
                require_generation=generation, **kwargs)
            return True
        except ConcurrencyError as exc:
            self.store.log(kind="commit_refused", task=task_id, event=event_id,
                           detail=str(exc))
            return False

    def _fence(self, task_id: str) -> None:
        """Refuse to record a result the worker was no longer entitled to write.

        Renewal can fail; the process can be paused past its expiry. Checking
        possession only at acquire time makes the lease a formality — the
        commit is the moment that matters.
        """
        if not self.store.holds_lease(task_id, self.owner):
            raise ConcurrencyError(
                f"lease for {task_id} was lost before the result could be recorded; "
                "discarding rather than overwriting whoever holds it now")

    def _round_deadline_at(self, task_id: str) -> float:
        """The ABSOLUTE instant this round must be finished by.

        Stored on the task so it survives steps, processes and restarts.
        """
        task = self.store.task(task_id)
        deadline = task.get("round_deadline")
        if not deadline:
            deadline = self._clock() + self.config.get("timeout_seconds", 2700)
            if self._generation is None:
                # Outside a step (no lease held): nothing is dispatched from
                # here, so report the value without persisting it. Only a
                # worker holding the lease may make it durable.
                return deadline
            # P2 (R4): this was the one task write not fenced by the lease.
            # step() sets the deadline right after acquiring, under the
            # generation it won, so a worker that lost its lease cannot.
            self.store.set_task(task_id, require_owner=self.owner,
                                require_generation=self._generation,
                                round_deadline=deadline)
        return deadline

    def _remaining_round_seconds(self, task_id: str) -> float:
        """Time left in the ROUND, not in this step.

        `started` was reset on every step, so the template's 2700s round limit
        bounded nothing: ten steps of 2699s each passed it.
        """
        return self._round_deadline_at(task_id) - self._clock()

    # ---------- one step ----------

    def step(self, task_id: str, event_id: str) -> dict:
        """Advance the task by at most one phase. Idempotent per event_id.

        `event_id` must be stable at the SOURCE: the same trigger firing,
        delivered twice, must present the same id both times, and two distinct
        firings must never share one. The controller cannot derive that — only
        the thing that fired knows its own identity — so it refuses to invent
        one rather than accept an id that merely looks unique.
        """
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError(
                "step needs a source-stable event id. Anything derived here "
                "from mutable state (a state revision, a counter, a timestamp) "
                "changes between two deliveries of one event, so the "
                "processed-event ledger would never deduplicate anything."
            )
        started = self._clock()

        if event_id in self.store.seen_events():
            self.store.log(kind="dedup", task=task_id, event=event_id)
            return {"action": "NOOP", "reason": "duplicate"}

        try:
            self.store.acquire(task_id, self.owner, self.config["lease_seconds"])
        except ConcurrencyError as exc:
            self.store.log(kind="lease_denied", task=task_id, detail=str(exc))
            return {"action": "NOOP", "reason": "leased_elsewhere"}

        # The generation this worker won. Every later write is fenced on it, so
        # a lease that changed hands and came back cannot be mistaken for the
        # one we are still holding.
        generation = self.store.lease_generation(task_id)
        self._generation = generation

        try:
            task = self.store.task(task_id)
            status = task.get("status", "READY")

            if status in TERMINAL:
                return {"action": "NOOP", "reason": f"terminal:{status}"}

            # L2: this task only. Checked at the checkpoint, before any runner
            # is started, and deliberately NOT presented as reaching a runner
            # that is already running.
            if self._cancelled(task_id):
                if not self._commit(event_id, task_id, generation, status="CANCELLED",
                                    failure="cancelled by operator at checkpoint"):
                    return {"action": "NOOP", "reason": "lease_lost_at_commit"}
                self.store.log(kind="cancel_task", task=task_id, event=event_id)
                return {"action": "CANCELLED", "reason": "operator_cancel_task"}

            try:
                self._round_deadline_at(task_id)          # fenced write, if new
            except ConcurrencyError as exc:
                self.store.log(kind="commit_refused", task=task_id, event=event_id,
                               detail=str(exc))
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}

            # GOV-R2-03: before dispatching anything, settle what a previous
            # worker may have started and never recorded.
            recovered = self._reconcile(task_id, generation, event_id)
            if recovered is not None:
                return recovered

            task = self.store.task(task_id)            # reconciliation may have moved it
            status = task.get("status", "READY")
            attempt = task.get("attempt", 0)
            if status in TERMINAL:
                return {"action": "NOOP", "reason": f"terminal:{status}"}

            head = task.get("last_head") or self._head_of(
                self.config["repo_url"], self.config["branch"])

            if status in ("READY", "FIX_PENDING"):
                return self._execute(task_id, event_id, head, attempt, started, generation)
            if status in ("REVIEW_PENDING",):
                return self._review(task_id, event_id, head, attempt, started, generation)
            return {"action": "NOOP", "reason": f"nothing_to_do_in:{status}"}
        finally:
            # A failed release must not replace the result of the step. If the
            # lease is gone, or is now somebody else's, that is worth logging
            # and is not this step's answer.
            self._generation = None
            try:
                self.store.release(task_id, self.owner)
            except ConcurrencyError as exc:
                self.store.log(kind="release_skipped", task=task_id, detail=str(exc))

    # ---------- phases ----------

    def _execute(self, task_id, event_id, head, attempt, started, generation=None):
        order = self._order(task_id, "execute", head, event_id,
                            run_identity=self.executor.identity(),
                            executor_identity=self.executor.identity(),
                            attempt=attempt, elapsed=self._clock() - started)
        verdict = self._ask(order)
        if verdict["action"] != "DISPATCH_ALLOWED":
            return self._halt(task_id, event_id, verdict, generation)

        # R2-05: reserve the run BEFORE dispatch. add_spend used to sit after a
        # successful return, so a call that started and then failed, timed out
        # or crashed cost the budget nothing — the cap counted successes, which
        # is not what runs out.
        # R2-03: a durable record of the intent to cause an external effect,
        # written BEFORE causing it. P2 (R4): reserved and recorded in ONE
        # fenced commit, so a crash cannot spend without leaving an intent.
        try:
            intent = self.store.reserve_run_and_record_intent(
                task_id, "execute", 1, require_owner=self.owner,
                require_generation=generation, head=head, event_id=event_id,
                run_identity=self.executor.identity())
        except ConcurrencyError as exc:
            self.store.log(kind="commit_refused", task=task_id, event=event_id,
                           detail=str(exc))
            return {"action": "NOOP", "reason": "lease_lost_before_dispatch"}
        receipt = work_receipt(task_id, intent)
        order["work_receipt"] = receipt

        try:
            result = self._run_with_lease(self.executor, task_id, order)
        except AuthUnavailable as exc:
            # G2: no credential is BLOCKED_ACCESS, never an unverified pass.
            # Nothing was dispatched, so the intent is refuted, not unknown.
            if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                                close_outcome="effect_refuted",
                                status="BLOCKED_ACCESS", failure=str(exc),
                                recovery_point=f"head={head}"):
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}
            self.store.log(kind="blocked_access", task=task_id, role="executor")
            return {"action": "BLOCKED_ACCESS", "reason": "no_credential"}
        except ConcurrencyError as exc:
            # The intent stays OPEN on purpose: something was dispatched and we
            # no longer hold the right to record what it did. Recovery must ask
            # GitHub, not assume.
            self.store.log(kind="lease_lost", task=task_id, role="executor",
                           detail=str(exc), intent=intent)
            return {"action": "NOOP", "reason": "lease_lost_mid_run"}
        except RunnerError as exc:
            # The runner ran and failed. That is not the same as "it changed
            # nothing": a failing executor may still have pushed before it
            # died. Ask the remote instead of assuming the tidy answer.
            outcome, live = self._observe_effect(head, receipt)
            if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                                close_outcome=outcome,
                                status="NEEDS_INFORMATION" if outcome != "effect_refuted"
                                       else "FAILED",
                                failure=str(exc), observed_head=live,
                                recovery_point=f"head={head}"):
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}
            self.store.log(kind="runner_failed", task=task_id, role="executor",
                           detail=str(exc), effect=outcome)
            if outcome != "effect_refuted":
                return {"action": "NEEDS_INFORMATION",
                        "reason": f"runner_failed_with_{outcome}"}
            return {"action": "FAILED", "reason": str(exc)}

        # G2: do not advance on a sha the runner merely claims to have pushed.
        new_head = result["new_head"]
        if not self._commit_is_on_branch(
                self.config["repo_url"], self.config["branch"], new_head):
            if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                                close_outcome="effect_refuted", status="FAILED",
                                failure=f"executor reported {new_head[:12]} but it is not "
                                        f"on {self.config['branch']}",
                                recovery_point=f"head={head}"):
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}
            self.store.log(kind="phantom_head", task=task_id, claimed=new_head[:12])
            return {"action": "FAILED", "reason": "reported_head_not_on_branch"}

        # GOV-R2-03: a head that exists on the branch is still not necessarily
        # THIS work. Its commits must carry the receipt this run was handed.
        try:
            attributed = self._receipt_is_on(self.config["repo_url"],
                                             self.config["branch"], head, new_head, receipt)
        except Exception as exc:                   # noqa: BLE001
            self.store.log(kind="receipt_check_failed", detail=str(exc))
            attributed = None
        if attributed is not True:
            status = "FAILED" if attributed is False else "NEEDS_INFORMATION"
            if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                                close_outcome="effect_unknown", status=status,
                                failure=f"reported head {new_head[:12]} does not carry work "
                                        f"receipt {receipt}" if attributed is False else
                                        f"could not verify work receipt on {new_head[:12]}",
                                observed_head=new_head, recovery_point=f"head={head}"):
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}
            self.store.log(kind="unreceipted_head", task=task_id, claimed=new_head[:12],
                           verified=attributed)
            return {"action": status, "reason": "reported_head_without_work_receipt"}

        # R2-03: one commit. The two-step version marked the event processed
        # first, so a crash in between left the event deduplicated away and the
        # task un-advanced — the round silently lost. The comment that used to
        # sit here claimed the opposite of what the code did.
        if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                            close_outcome="effect_confirmed",
                            status="REVIEW_PENDING", last_head=new_head,
                            executor_identity=self.executor.identity(), attempt=attempt):
            return {"action": "NOOP", "reason": "lease_lost_at_commit"}
        self.store.log(kind="executed", task=task_id, new_head=new_head[:12],
                       executor=self.executor.identity())
        return {"action": "REVIEW_PENDING", "head": new_head}

    def _review(self, task_id, event_id, head, attempt, started, generation=None):
        task = self.store.task(task_id)
        executor_identity = task.get("executor_identity", self.executor.identity())

        order = self._order(task_id, "review", head, event_id,
                            run_identity=self.reviewer.identity(),
                            executor_identity=executor_identity,
                            attempt=attempt, elapsed=self._clock() - started)
        verdict = self._ask(order)
        if verdict["action"] != "DISPATCH_ALLOWED":
            return self._halt(task_id, event_id, verdict, generation)

        try:                                          # reserved before dispatch
            intent = self.store.reserve_run_and_record_intent(
                task_id, "review", 1, require_owner=self.owner,
                require_generation=generation, head=head, event_id=event_id,
                run_identity=self.reviewer.identity())
        except ConcurrencyError as exc:
            self.store.log(kind="commit_refused", task=task_id, event=event_id,
                           detail=str(exc))
            return {"action": "NOOP", "reason": "lease_lost_before_dispatch"}
        try:
            result = self._run_with_lease(self.reviewer, task_id, order)
        except AuthUnavailable as exc:
            # G2: no credential is BLOCKED_ACCESS, never an unverified pass.
            if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                                close_outcome="effect_refuted",
                                status="BLOCKED_ACCESS", failure=str(exc),
                                recovery_point=f"head={head}"):
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}
            self.store.log(kind="blocked_access", task=task_id, role="reviewer")
            return {"action": "BLOCKED_ACCESS", "reason": "no_credential"}
        except ConcurrencyError as exc:
            self.store.log(kind="lease_lost", task=task_id, role="reviewer",
                           detail=str(exc), intent=intent)
            return {"action": "NOOP", "reason": "lease_lost_mid_run"}
        except RunnerError as exc:
            outcome, live = self._observe_effect(head)
            if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                                close_outcome=outcome,
                                status="NEEDS_INFORMATION" if outcome != "effect_refuted"
                                       else "FAILED",
                                failure=str(exc), observed_head=live,
                                recovery_point=f"head={head}"):
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}
            if outcome != "effect_refuted":
                return {"action": "NEEDS_INFORMATION",
                        "reason": f"runner_failed_with_{outcome}"}
            return {"action": "FAILED", "reason": str(exc)}

        # The verdict is put back through the guard, which re-checks that the
        # review is bound to this head and this reviewer, cites evidence, and
        # names a decision the state machine recognises.
        accept = self._order(task_id, "accept_review", head, f"{event_id}:accept",
                             run_identity=self.reviewer.identity(),
                             executor_identity=executor_identity,
                             attempt=attempt, elapsed=self._clock() - started,
                             review=result["review"])
        outcome = self._ask(accept)

        # A review writes nothing outside this process: the verdict becomes
        # durable here, or not at all. So the intent's external effect is
        # refuted by construction once the runner returned to us.
        if outcome["action"] == "FIX_PENDING":
            if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                                close_outcome="effect_refuted",
                                status="FIX_PENDING", attempt=attempt + 1,
                                last_review=result["review"]):
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}
            return {"action": "FIX_PENDING", "attempt": attempt + 1}
        if outcome["action"] in ("COMPLETE", "CONDITIONS_PENDING", "NEEDS_INFORMATION"):
            if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                                close_outcome="effect_refuted",
                                status=outcome["action"], last_review=result["review"],
                                reviewed_head=head):
                return {"action": "NOOP", "reason": "lease_lost_at_commit"}
            return {"action": outcome["action"], "head": head}
        if not self._commit(event_id, task_id, generation, close_intent_id=intent,
                            close_outcome="effect_refuted"):
            return {"action": "NOOP", "reason": "lease_lost_at_commit"}
        return self._halt(task_id, event_id, outcome, generation)

    def _halt(self, task_id, event_id, verdict, generation=None):
        action = verdict["action"]
        if action == "NOOP":
            return verdict
        status = {"STOP": "STOPPED"}.get(action, "BLOCKED_ACCESS" if action == "REJECT" else action)
        try:
            self.store.set_task(task_id, require_owner=self.owner,
                                require_generation=generation,
                                status=status, halt_reason=verdict["reason"])
        except ConcurrencyError as exc:
            self.store.log(kind="halt_refused", task=task_id, detail=str(exc))
            return {"action": "NOOP", "reason": "lease_lost_at_commit"}
        self.store.log(kind="halted", task=task_id, verdict=verdict)
        return verdict

    # ---------- driver ----------

    def drive(self, task_id: str, event_id: str, max_steps: int = 12) -> list:
        """Run steps until the task reaches a terminal state or runs out of steps.

        This is the whole point: one start, no human in between.

        `event_id` identifies the CALLER's firing and every step is namespaced
        under it. The previous version numbered steps `evt-<task>-<n>` from zero
        on every call, so a second drive of the same task re-used `evt-T-0`,
        found it in the processed-event ledger, and returned NOOP without doing
        any work. A ledger keyed on something the caller does not control
        deduplicates the wrong things in both directions.
        """
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("drive needs the caller's own event id; see step()")
        trail = []
        for n in range(max_steps):
            result = self.step(task_id, f"{event_id}/{n}")
            trail.append(result)
            status = self.store.task(task_id).get("status")
            if status in TERMINAL:
                break
            if result["action"] == "NOOP" and result.get("reason") == "duplicate":
                # GOV-R2-03: a RESEND of the same firing, after the first
                # delivery got partway and died. `evt/0` is in the ledger, so
                # the old code took the duplicate as a stop signal and the
                # resend did nothing at all — the one case a resend exists for.
                # A sub-step that already ran is a step to skip, not a reason
                # to stop; the loop is bounded by max_steps either way.
                continue
            if result["action"] in ("NOOP", "FAILED"):
                break
        return trail


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Governance handoff controller")
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("--task", required=True)
    ap.add_argument("--max-steps", type=int, default=12)
    ap.add_argument("--event", required=True,
                    help="the caller's own stable id for this firing")
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
                     FakeReviewer(config["replay"]["reviewer_decisions"]),
                     commit_verifier=scripted_commit_verifier(
                         config["replay"]["executor_heads"]),
                     receipt_verifier=scripted_receipt_verifier(
                         config["replay"]["executor_heads"]))
    for line in ctl.drive(args.task, args.event, args.max_steps):
        print(json.dumps(line, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

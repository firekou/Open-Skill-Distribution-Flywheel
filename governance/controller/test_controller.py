#!/usr/bin/env python3
"""Negative controls for the handoff controller.

Every test here is a way the loop could do the wrong thing while still looking
green. A controller that only proves the happy path is the same mistake as a
test suite that only asserts a full key is absent.

    python3 governance/controller/test_controller.py

No network, no credentials, no model call.
"""

from __future__ import annotations

import contextlib
import json
import inspect
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import runners                                          # noqa: E402
from controller import (CANCEL_LADDER, Controller,     # noqa: E402
                        load_guard, scripted_commit_verifier)
from runners import (AuthUnavailable, BASE_ENV_ALLOWLIST, CommandTemplateError,  # noqa: E402
                     DENY_SESSION_IDENTITY, render_command,
                     FakeExecutor, IsolationUnavailable, credential_state,
                     FakeReviewer, ROLE_CREDENTIALS, RunnerError, SubprocessRunner,
                     build_env, has_credential, parse_verdict,
                     terminate_process_group)
from store import ConcurrencyError, Store              # noqa: E402

GUARD = load_guard(HERE.parent / "preflight.py")
H0 = "0" * 40
H1 = "1" * 40
H2 = "2" * 40


def base_config(tmp: pathlib.Path, **over) -> dict:
    cfg = {
        "mode": "replay",
        "controller_identity": "controller-test",
        "repo_url": "https://example.invalid/repo",
        "branch": "work",
        "prompt_file": "PROMPT.md",
        "guard_path": str(HERE.parent / "preflight.py"),
        "state_dir": str(tmp / "state"),
        "stop_file": str(tmp / "STOP"),
        "authorized_phases": ["execute", "review", "accept_review"],
        "max_attempts": 2,
        "run_budget": 8,
        "timeout_seconds": 2700,
        "lease_seconds": 600,
    }
    cfg.update(over)
    return cfg


class Harness:
    """A controller wired to fakes, with the live head under test control."""

    def __init__(self, tmp, executor_heads=(H1, H2), decisions=("BLOCKED", "APPROVED"),
                 pinned_head=None, known_commits=None, receipted=None, **cfg_over):
        self.tmp = pathlib.Path(tmp)
        self.config = base_config(self.tmp, **cfg_over)
        self.store = Store(pathlib.Path(self.config["state_dir"]))
        self.executor = FakeExecutor(list(executor_heads))
        self.reviewer = FakeReviewer(list(decisions))
        self.pinned_head = pinned_head
        # Stub for the remote check, so the suite never touches the network.
        # None means "every sha the executor reports really is on the branch".
        self.known_commits = known_commits
        # GOV-R2-03: which heads were pushed WITH this work's receipt. None
        # means "every head the executor reports carries it" — the fixture's
        # executor is ours. Reconciliation tests set it explicitly.
        self.receipted = receipted
        self.receipt_checks = []
        self.ctl = Controller(self.config, self.store, GUARD,
                              self.executor, self.reviewer,
                              head_resolver=self._head,
                              commit_verifier=self._commit_on_branch,
                              receipt_verifier=self._receipt_on,
                              policy_sha_value="policy" + "0" * 35)
        self.store.set_task("T", status="READY", last_head=H0)

    def _receipt_on(self, _repo, _branch, base, live, receipt):
        self.receipt_checks.append((base, live, receipt))
        return True if self.receipted is None else live in self.receipted

    def _commit_on_branch(self, _repo, _branch, sha):
        return True if self.known_commits is None else sha in self.known_commits

    def _head(self, _repo, _branch):
        if self.pinned_head:
            return self.pinned_head
        return self.store.task("T").get("last_head", H0)


class DuplicateAndConcurrency(unittest.TestCase):

    def test_a_redelivered_event_does_nothing_the_second_time(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            first = h.ctl.step("T", "evt-1")
            again = h.ctl.step("T", "evt-1")
            self.assertEqual(first["action"], "REVIEW_PENDING")
            self.assertEqual(again, {"action": "NOOP", "reason": "duplicate"})
            self.assertEqual(len(h.executor.calls), 1, "the executor ran twice for one event")

    def test_dedup_survives_losing_the_controller_fast_path(self):
        """Mutation testing found that deleting the controller's own duplicate
        check changed nothing: the TRUSTED GUARD is what enforces dedup, and the
        controller check is only a fast path. That is the right layering, but it
        means the test above cannot tell the two apart. This one pins the layer
        that actually carries the weight."""
        state = {
            "task_id": "T", "head": H1, "live_head": H1, "phase": "execute",
            "event_id": "evt-1", "seen_events": ["evt-1"], "revision": 1,
            "expected_revision": 1, "stopped": False, "authorized": True,
            "run_identity": "r", "executor_identity": "r", "attempt": 0,
            "max_attempts": 2, "cost": 0, "budget": 0, "elapsed": 0, "timeout": 10,
        }
        self.assertEqual(GUARD.evaluate(state), {"action": "NOOP", "reason": "duplicate"})

    def test_the_controller_always_hands_the_guard_the_seen_event_ledger(self):
        """If `_order` stopped passing `seen_events`, the guard could not dedup
        and nothing else would notice — that is the single point where dedup
        would die silently."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.store.mark_processed("evt-old")
            order = h.ctl._order("T", "execute", H0, "evt-new", "r", "e", 0, 0.0)
            self.assertIn("seen_events", order)
            self.assertIn("evt-old", order["seen_events"])

    def test_two_workers_racing_the_same_task_produce_one_execution(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            other = Controller(dict(h.config, controller_identity="controller-other"),
                               h.store, GUARD, h.executor, h.reviewer, head_resolver=h._head)
            results, errors = [], []

            def run(ctl, event):
                try:
                    results.append(ctl.step("T", event))
                except Exception as exc:          # pragma: no cover
                    errors.append(exc)

            # same task, different events: the lease, not the dedup ledger, is what
            # has to hold here
            h.store.acquire("T", "controller-other", 600)
            blocked = h.ctl.step("T", "evt-a")
            self.assertEqual(blocked, {"action": "NOOP", "reason": "leased_elsewhere"})
            self.assertEqual(h.executor.calls, [])

    def test_a_lost_compare_and_swap_raises_rather_than_overwriting(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            revision = store.read()["revision"]
            store.set_task("T", status="A")                       # bumps the revision
            with self.assertRaises(ConcurrencyError):
                store.commit(revision, lambda s: s["tasks"].setdefault("T", {}).update(status="B"))
            self.assertEqual(store.task("T")["status"], "A")

    def test_an_expired_lease_can_be_taken_over(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td), clock=lambda: 1000.0)
            store.acquire("T", "dead-worker", ttl=1)
            later = Store(pathlib.Path(td), clock=lambda: 2000.0)
            later.acquire("T", "new-worker", ttl=600)             # must not raise
            self.assertTrue(later.holds_lease("T", "new-worker"))


class HeadAndIdentity(unittest.TestCase):

    def test_a_review_for_a_head_that_is_no_longer_live_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.step("T", "evt-1")                    # executed -> head H1
            h.pinned_head = H2                          # someone else pushed meanwhile
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out["action"], "REJECT")
            self.assertEqual(out["reason"], "stale_head")
            self.assertEqual(h.reviewer.calls, [], "the reviewer ran against a stale head")

    def test_the_executor_cannot_review_its_own_work(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.step("T", "evt-1")
            h.reviewer._identity = h.executor.identity()          # same run identity
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out["reason"], "self_review")
            self.assertEqual(h.reviewer.calls, [])

    def test_a_review_signed_for_a_different_head_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)

            class Liar(FakeReviewer):
                def run(self, order):
                    out = super().run(order)
                    out["review"]["head"] = H2                    # not the head it was given
                    return out

            h.reviewer = Liar(["APPROVED"])
            h.ctl.reviewer = h.reviewer
            h.ctl.step("T", "evt-1")
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out["reason"], "review_binding")
            self.assertNotEqual(h.store.task("T").get("status"), "COMPLETE")

    def test_a_review_with_no_evidence_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)

            class Empty(FakeReviewer):
                def run(self, order):
                    out = super().run(order)
                    out["review"]["evidence"] = []
                    return out

            h.reviewer = Empty(["APPROVED"])
            h.ctl.reviewer = h.reviewer
            h.ctl.step("T", "evt-1")
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out["reason"], "missing_evidence")

    def test_an_invented_verdict_word_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)

            class Nonsense(FakeReviewer):
                def run(self, order):
                    out = super().run(order)
                    out["review"]["decision"] = "LGTM"
                    return out

            h.reviewer = Nonsense(["APPROVED"])
            h.ctl.reviewer = h.reviewer
            h.ctl.step("T", "evt-1")
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out["reason"], "unknown_review_decision")


class OutcomesAreNotPermissions(unittest.TestCase):

    def test_conditional_approval_does_not_complete_the_task(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, decisions=["APPROVED_WITH_CONDITIONS"])
            h.ctl.step("T", "evt-1")
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out["action"], "CONDITIONS_PENDING")
            self.assertNotEqual(h.store.task("T")["status"], "COMPLETE")

    def test_blocked_sends_it_back_to_the_executor_with_a_new_attempt(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.step("T", "evt-1")
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out["action"], "FIX_PENDING")
            self.assertEqual(h.store.task("T")["attempt"], 1)

    def test_the_full_cycle_reaches_complete_from_one_start(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            trail = h.ctl.drive("T", "evt-cycle")
            self.assertEqual([t["action"] for t in trail],
                             ["REVIEW_PENDING", "FIX_PENDING", "REVIEW_PENDING", "COMPLETE"])
            self.assertEqual(h.store.task("T")["status"], "COMPLETE")


WORKER = """
import json, pathlib, signal, sys, time
sys.path.insert(0, sys.argv[1])
from store import Store, ConcurrencyError
root, rounds, start_at = pathlib.Path(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])

# A hard deadline inside the worker itself. Without it a worker blocked on a
# lock that is never released waits forever, and a failing run leaves six stuck
# processes behind for whoever looks next. A test that leaks processes on
# failure has the same defect this suite exists to catch in the runner.
signal.alarm(int(float(sys.argv[5])))

s = Store(root)
time.sleep(max(0.0, start_at - time.time()))
ok = 0
for _ in range(rounds):
    for _try in range(3000):
        try:
            rev = s.read()["revision"]
            time.sleep(0.0005)          # widen the read-to-write window on purpose
            s.commit(rev, lambda st: st["tasks"].setdefault("C", {"n": 0}).update(
                n=st["tasks"].get("C", {}).get("n", 0) + 1))
            ok += 1
            break
        except ConcurrencyError:
            continue
print(ok)
"""


def still_running(pid: int) -> bool:
    """Is this pid a LIVE process, as opposed to an unreaped zombie?

    os.kill(pid, 0) is not that question. A killed process whose parent has
    gone stays as a zombie until something reaps it, and in a container pid 1
    often never does — so signal 0 keeps succeeding for a process that is
    thoroughly dead. Both the test and its control were asking the wrong
    question, which would have made the control pass without reproducing
    anything. The process state is the real answer: Z is a zombie, X is gone.
    """
    try:
        state = pathlib.Path(f"/proc/{pid}/stat").read_text().split()[2]
    except (FileNotFoundError, ProcessLookupError, IndexError):
        return False
    return state not in ("Z", "X", "x")


STUBBORN = """#!/bin/sh
# A runner that refuses SIGTERM, which is what the SIGKILL backstop is for.
trap '' TERM
sh -c "trap '' TERM; while true; do sleep 0.2; done" &
echo "$!" > "$1"
while true; do sleep 0.2; done
"""

SPAWNER = """#!/bin/sh
# A runner that starts its own worker, the way a CLI agent does.
sh -c 'while true; do sleep 0.2; done' &
echo "$!" > "$1"
while true; do sleep 0.2; done
"""


class CancelIsFourDifferentThings(unittest.TestCase):
    """G3. 'Cancel' was one word covering four actions that stop different
    things. Separated, with what each one CANNOT do stated:

      L1 stop dispatch    no new runner starts; a running one is untouched
      L2 cancel task      that task ends at its next checkpoint; others run on
      L3 terminate runner kills the runner and its children; does not undo a
                          push the runner already made
      L4 revoke credential not in this program's power at all

    L3 needed a real fix, not just a name: subprocess.run(timeout=...) kills
    only the direct child, so a runner's own worker survived the timeout still
    holding the credentials from its environment. Measured in evidence/cancel.txt.
    """

    def _spawner(self, tmp):
        script = pathlib.Path(tmp) / "spawner.sh"
        script.write_text(SPAWNER)
        script.chmod(0o755)
        return script

    def test_terminating_a_runner_takes_its_children_with_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = pathlib.Path(tmp) / "worker.pid"
            proc = subprocess.Popen(["sh", str(self._spawner(tmp)), str(pidfile)],
                                    start_new_session=True)
            for _ in range(100):
                if pidfile.exists() and pidfile.read_text().strip():
                    break
                time.sleep(0.05)
            worker = int(pidfile.read_text().strip())

            outcome = terminate_process_group(proc, grace_seconds=5)
            self.assertIn(outcome, ("terminated", "killed"))
            time.sleep(0.3)
            self.assertFalse(still_running(worker),
                             "the runner's own worker outlived the cancel")

    def test_the_plain_kill_this_replaced_really_did_leave_an_orphan(self):
        """The negative control. Without the process group the worker lives on,
        which is the whole reason the fix exists."""
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = pathlib.Path(tmp) / "worker.pid"
            proc = subprocess.Popen(["sh", str(self._spawner(tmp)), str(pidfile)])
            for _ in range(100):
                if pidfile.exists() and pidfile.read_text().strip():
                    break
                time.sleep(0.05)
            worker = int(pidfile.read_text().strip())
            proc.kill()                       # exactly what subprocess.run(timeout=) does
            proc.wait(timeout=10)
            time.sleep(0.3)
            try:
                orphaned = still_running(worker)
            finally:
                with contextlib.suppress(ProcessLookupError):
                    os.kill(worker, 9)
            self.assertTrue(orphaned,
                            "the control no longer reproduces the defect: without the "
                            "process group the worker is supposed to survive")

    def test_a_runner_that_ignores_sigterm_is_still_killed(self):
        """The SIGKILL backstop. Mutation testing found it untested: every
        earlier case died on SIGTERM, so replacing the SIGKILL with a no-op
        signal-0 probe changed nothing. This feeds the backstop its input."""
        with tempfile.TemporaryDirectory() as tmp:
            script = pathlib.Path(tmp) / "stubborn.sh"
            script.write_text(STUBBORN)
            script.chmod(0o755)
            pidfile = pathlib.Path(tmp) / "worker.pid"
            proc = subprocess.Popen(["sh", str(script), str(pidfile)],
                                    start_new_session=True)
            for _ in range(100):
                if pidfile.exists() and pidfile.read_text().strip():
                    break
                time.sleep(0.05)
            worker = int(pidfile.read_text().strip())
            self.assertTrue(still_running(worker))
            pgid = os.getpgid(proc.pid)

            try:
                outcome = terminate_process_group(proc, grace_seconds=1)
                self.assertEqual(outcome, "killed", "SIGTERM was treated as sufficient")
                time.sleep(0.4)
                self.assertFalse(still_running(worker),
                                 "a runner that ignores SIGTERM survived the cancel")
            finally:
                # These children ignore SIGTERM by design. If the code under test
                # fails to SIGKILL them they live forever, and because they
                # inherit this process's pipes, anything reading those pipes —
                # a test runner, a shell, the mutation harness — blocks forever
                # too. A failing assertion must stay a failing assertion rather
                # than becoming a hang, so the cleanup is unconditional.
                with contextlib.suppress(ProcessLookupError, PermissionError):
                    os.killpg(pgid, signal.SIGKILL)
                with contextlib.suppress(subprocess.TimeoutExpired):
                    proc.wait(timeout=5)

    def test_it_refuses_to_signal_its_own_process_group(self):
        """The self-kill. Without start_new_session the child shares the
        caller's process group, so a group kill takes the controller down with
        it. Mutation testing surfaced this as the suite dying of SIGTERM rather
        than reporting anything — a whole class of results silently lost."""
        proc = subprocess.Popen([sys.executable, "-c",
                                 "import time; time.sleep(30)"])   # no new session
        try:
            with self.assertRaises(RunnerError) as cm:
                terminate_process_group(proc, grace_seconds=2)
            self.assertIn("own process group", str(cm.exception))
            self.assertIsNone(proc.poll(), "it signalled the group anyway")
        finally:
            proc.kill()
            proc.wait(timeout=10)

    def test_terminating_something_already_gone_is_not_an_error(self):
        proc = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)
        proc.wait(timeout=10)
        self.assertEqual(terminate_process_group(proc, grace_seconds=2), "already_gone")

    def test_cancelling_one_task_does_not_stop_the_others(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            pathlib.Path(h.config["stop_file"]).with_name("CANCEL-T").write_text("cancel")
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "CANCELLED")
            self.assertEqual(h.store.task("T")["status"], "CANCELLED")
            self.assertEqual(h.executor.calls, [], "a cancelled task still ran a runner")

            other = h.ctl.step("OTHER", "evt-2")
            self.assertEqual(other["action"], "REVIEW_PENDING",
                             "cancelling one task stopped an unrelated one")

    def test_stop_dispatch_and_cancel_task_are_not_the_same_switch(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            pathlib.Path(h.config["stop_file"]).write_text("stop")
            self.assertEqual(h.ctl.step("T", "evt-1")["action"], "STOP")
            self.assertEqual(h.store.task("T")["status"], "STOPPED")
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            pathlib.Path(h.config["stop_file"]).with_name("CANCEL-T").write_text("cancel")
            self.assertEqual(h.ctl.step("T", "evt-1")["action"], "CANCELLED")
            self.assertEqual(h.store.task("T")["status"], "CANCELLED")

    def test_neither_file_switch_claims_to_reach_a_running_runner(self):
        """The documented limit, asserted so a future edit cannot quietly drop
        it: L1 and L2 are read at checkpoints, before a runner starts."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            source = inspect.getsource(type(h.ctl)._stopped)
            self.assertIn("does not reach a runner", source)
            self.assertEqual(CANCEL_LADDER,
                             ("stop_dispatch", "cancel_task",
                              "terminate_runner", "revoke_credential"))

    def test_revoking_a_credential_is_not_claimed_to_be_implemented(self):
        """L4 is the one that actually takes a leaked key back, and nothing here
        can do it. A ladder that implies otherwise is worse than no ladder."""
        import controller as ctl_mod
        self.assertIn("revoke_credential", CANCEL_LADDER)
        self.assertFalse(
            any(name.startswith("revoke") for name in dir(ctl_mod.Controller)),
            "something named revoke* exists; only the credential issuer can revoke")
        self.assertIn("NOT IMPLEMENTABLE HERE", (HERE / "controller.py").read_text(),
                      "the ladder no longer says that L4 is out of reach")


class RealCrossProcessConcurrency(unittest.TestCase):
    """G3. The previous concurrency tests ran in one process, where the GIL hides
    exactly the bug they were meant to find. Run as separate OS processes, two
    defects showed up that no sequential or threaded test could reach:

      * every writer used the same temp file name, `state.tmp`. Two concurrent
        writers overwrote each other's temp file and the loser's os.replace died
        with FileNotFoundError. The 'atomic write' was atomic against a crash
        and not against a second process.
      * commit() read the revision, checked it, then wrote, with nothing held in
        between. Six processes, sixty commits: 38 were reported successful and
        silently lost. A revision check not held under a lock is a comment.

    Measured, not argued: the controls are in evidence/concurrency.txt.
    """

    PROCS, ROUNDS = 6, 6

    def test_no_commit_is_ever_silently_lost(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td) / "state"
            Store(root)
            script = pathlib.Path(td) / "worker.py"
            script.write_text(WORKER)
            start = time.time() + 1.0
            # Short on purpose: a healthy run finishes in about a second, so a
            # long deadline only buys a long wait when something is wrong.
            deadline = 20
            procs = [subprocess.Popen(
                [sys.executable, str(script), str(HERE), str(root),
                 str(self.ROUNDS), str(start), str(deadline)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                start_new_session=True)
                for _ in range(self.PROCS)]
            try:
                reported = 0
                for proc in procs:
                    out, err = proc.communicate(timeout=deadline + 15)
                    self.assertEqual(
                        proc.returncode, 0,
                        "a writer did not finish cleanly. A negative exit is the worker's "
                        "own alarm, which means it waited forever on the lock: "
                        f"{err[-600:]}")
                    reported += int(out.strip())
            finally:
                # Leave nothing behind, whatever happened above — neither a
                # process nor a pipe. Killing a writer without closing its
                # stdout/stderr leaks the descriptors, which is the same class
                # of untidiness this suite complains about elsewhere.
                for proc in procs:
                    if proc.poll() is None:
                        terminate_process_group(proc, grace_seconds=5)
                    for stream in (proc.stdout, proc.stderr):
                        if stream is not None and not stream.closed:
                            stream.close()

            final = Store(root).read()
            self.assertEqual(reported, self.PROCS * self.ROUNDS)
            self.assertEqual(final["tasks"]["C"]["n"], reported,
                             f"{reported - final['tasks']['C']['n']} commits were "
                             "reported successful and lost")
            self.assertEqual(final["revision"], reported)

    STALE_WORKER = """
import json, pathlib, sys, time
sys.path.insert(0, sys.argv[1])
from store import ConcurrencyError, Store
root, ttl, sleep_for = pathlib.Path(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
store = Store(root)
store.acquire("T", "worker-a", ttl=ttl)
generation = store.lease_generation("T")
time.sleep(sleep_for)                      # the lease expires while we "work"
try:
    store.commit_event_and_task("evt-a", "T", require_owner="worker-a",
                                require_generation=generation,
                                status="ADVANCED_BY_A")
    print("committed")
except ConcurrencyError:
    print("refused")
"""

    def test_a_worker_whose_lease_expired_cannot_advance_the_task(self):
        """GOV-R2-02, across real processes and a real TTL.

        Worker A takes the lease and overruns it. Worker B — this process —
        legitimately takes over. A then finishes and tries to record its
        result. It must be refused: by then the task belongs to B, and A's
        write would silently overwrite work B is in the middle of."""
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td) / "state"
            store = Store(root)
            store.set_task("T", status="READY")
            script = pathlib.Path(td) / "stale.py"
            script.write_text(self.STALE_WORKER)
            proc = subprocess.Popen(
                [sys.executable, str(script), str(HERE), str(root), "1", "3"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                start_new_session=True)
            try:
                time.sleep(1.6)                      # A's lease has now expired
                store.acquire("T", "worker-b", ttl=60)
                out, err = proc.communicate(timeout=30)
            finally:
                if proc.poll() is None:
                    terminate_process_group(proc, grace_seconds=5)
                for stream in (proc.stdout, proc.stderr):
                    if stream is not None and not stream.closed:
                        stream.close()
            self.assertEqual(proc.returncode, 0, err[-800:])
            self.assertEqual(out.strip(), "refused",
                             "a worker whose lease had expired still advanced the task")
            self.assertNotEqual(store.task("T").get("status"), "ADVANCED_BY_A")
            self.assertEqual(store.task("T")["lease"]["owner"], "worker-b")

    def test_the_same_worker_inside_its_lease_is_still_allowed(self):
        """The negative control. A fence that refuses everyone is not a fence,
        it is an outage."""
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td) / "state"
            script = pathlib.Path(td) / "stale.py"
            script.write_text(self.STALE_WORKER)
            Store(root).set_task("T", status="READY")
            proc = subprocess.run(
                [sys.executable, str(script), str(HERE), str(root), "60", "0"],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(proc.returncode, 0, proc.stderr[-800:])
            self.assertEqual(proc.stdout.strip(), "committed")
            self.assertEqual(Store(root).task("T")["status"], "ADVANCED_BY_A")

    def test_two_writers_never_share_a_temp_file_name(self):
        """The crash above, stated directly: the name must depend on the writer."""
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            seen = set()
            real = pathlib.Path.write_text

            def capture(self_path, *a, **kw):
                if self_path.name.endswith(".tmp"):
                    seen.add(self_path.name)
                return real(self_path, *a, **kw)

            with patch.object(pathlib.Path, "write_text", capture):
                for _ in range(5):
                    store.commit(store.read()["revision"], lambda st: None)
            self.assertEqual(len(seen), 5, f"temp names were reused: {seen}")
            self.assertNotIn("state.tmp", seen)

    def test_the_lock_is_released_even_when_the_mutation_raises(self):
        """A lock a failed commit keeps is a deadlock for every later worker.

        The next commit runs on a thread with a join deadline, because the
        failure mode here is a hang, not an exception, and a suite that hangs
        tells you less than one that goes red."""
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))

            def explode(_state):
                raise RuntimeError("mutation failed")

            with self.assertRaises(RuntimeError):
                store.commit(store.read()["revision"], explode)

            done = []

            def second():
                store.commit(store.read()["revision"], lambda st: st.update(ok=True))
                done.append(True)

            worker = threading.Thread(target=second, daemon=True)
            worker.start()
            worker.join(timeout=10)
            self.assertTrue(done, "the store stayed locked after a failed commit")
            self.assertTrue(store.read()["ok"])


class BothReplayEntryPointsStayWiredToTheRealChecks(unittest.TestCase):
    """G2 aftermath. Verifying the executor's reported head was added to
    Controller and to the unit suite, but neither replay entry point was given
    a verifier, so both went straight to FAILED / reported_head_not_on_branch
    against a live remote that has never heard of the scripted shas. The unit
    tests did not see it because the harness stubs the verifier itself.

    The lesson is the recurring one in this repository: a check added at the
    entrance is not added at the exits. These tests exercise the exits."""

    SCRIPTED = ("1" * 40, "2" * 40)

    def _stage(self, tmp):
        work = pathlib.Path(tmp) / "governance" / "controller"
        work.parent.mkdir(parents=True)
        shutil.copytree(HERE, work, ignore=shutil.ignore_patterns("__pycache__", "evidence"))
        shutil.copy(HERE.parent / "preflight.py", work.parent / "preflight.py")
        cfg = json.loads((work / "config.replay.json").read_text())
        cfg["state_dir"] = str(pathlib.Path(tmp) / "state")
        cfg["stop_file"] = str(pathlib.Path(tmp) / "state" / "STOP")
        (work / "config.replay.json").write_text(json.dumps(cfg, indent=2))
        return work, cfg

    def test_the_replay_verifier_is_a_check_not_a_yes(self):
        """If it returned True for everything it would delete the control."""
        verify = scripted_commit_verifier(self.SCRIPTED)
        self.assertTrue(verify("repo", "branch", "1" * 40))
        self.assertFalse(verify("repo", "branch", "9" * 40),
                         "an unscripted head was accepted; the check is vacuous")

    def test_tick_in_replay_mode_builds_a_controller_that_can_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, cfg = self._stage(tmp)
            sys.path.insert(0, str(work))
            saved = {name: sys.modules.pop(name, None)
                     for name in ("tick", "controller", "runners", "store")}
            try:
                import tick as staged_tick
                from store import Store as StagedStore
                ctl = staged_tick.build(cfg, StagedStore(pathlib.Path(cfg["state_dir"])))
                self.assertTrue(ctl._commit_is_on_branch("r", "b", self.SCRIPTED[0]))
                self.assertFalse(ctl._commit_is_on_branch("r", "b", "9" * 40))
            finally:
                # tick.py inserts its OWN directory on import, so the staged
                # path is on sys.path twice by now. A single remove() left one
                # behind and every later `import runners` in this file silently
                # got the staged copy from a deleted temp dir -- which is why
                # an isolation test started raising a class that was not the
                # class its assertRaises was watching for.
                while str(work) in sys.path:
                    sys.path.remove(str(work))
                # Put the ORIGINAL module objects back rather than importing
                # fresh ones. A fresh import would rebuild the classes, and
                # this file's top-level `from runners import IsolationUnavailable`
                # would then name a class no longer raised by anything -- an
                # assertRaises that can never match.
                for name, mod in saved.items():
                    if mod is None:
                        sys.modules.pop(name, None)
                    else:
                        sys.modules[name] = mod
                import runners as _restored
                assert _restored is saved["runners"], "module restore failed"

    def test_the_replay_fixture_still_reaches_complete_end_to_end(self):
        """Runs replay.py the way a reader would, in a staged copy so the
        repository's own evidence file is not rewritten by the test suite."""
        with tempfile.TemporaryDirectory() as tmp:
            work, _ = self._stage(tmp)
            proc = subprocess.run([sys.executable, str(work / "replay.py")],
                                  capture_output=True, text=True, cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
            self.assertIn("status        : COMPLETE", proc.stdout)
            self.assertNotIn("reported_head_not_on_branch", proc.stdout)
            self.assertIn("REPLAY_VERIFIED", proc.stdout)
            self.assertNotIn("ACTIVE —", proc.stdout)


class EventIdsComeFromTheSource(unittest.TestCase):
    """G3. The processed-event ledger only works if the key is stable at the
    source. Two defects broke it in opposite directions:

      * tick.py defaulted the id to f"{task}-{state revision}-{attempt}". The
        revision changes on every write, so one firing delivered twice arrived
        under two ids and was executed twice. Nothing was ever deduplicated.
      * Controller.drive numbered its steps evt-<task>-0, -1, -2 from zero on
        every call, so a second drive of the same task hit evt-T-0 already in
        the ledger and returned NOOP without doing any work at all.

    Both are the same mistake: a ledger keyed on something the caller does not
    control. The fix is that nothing invents an event id."""

    def test_a_redelivered_firing_is_recognised_and_does_no_work_twice(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            first = h.ctl.step("T", "delivery-abc123")
            self.assertEqual(first["action"], "REVIEW_PENDING")
            again = h.ctl.step("T", "delivery-abc123")
            self.assertEqual(again, {"action": "NOOP", "reason": "duplicate"})
            self.assertEqual(len(h.executor.calls), 1, "the executor ran twice for one event")

    def test_a_second_drive_of_the_same_task_is_not_swallowed_as_a_duplicate(self):
        """The regression: identical step ids across two separate firings."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, executor_heads=[H1, H2], decisions=["BLOCKED", "APPROVED"])
            h.ctl.drive("T", "firing-1", max_steps=2)
            before = len(h.executor.calls)
            trail = h.ctl.drive("T", "firing-2", max_steps=2)
            self.assertNotEqual(trail[0], {"action": "NOOP", "reason": "duplicate"},
                                "a fresh firing was deduplicated against the previous one")
            self.assertGreater(len(h.executor.calls), before, "the second firing did nothing")

    def test_an_empty_or_missing_event_id_is_refused_not_invented(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            for bad in ("", "   ", None):
                with self.assertRaises(ValueError):
                    h.ctl.step("T", bad)
                with self.assertRaises(ValueError):
                    h.ctl.drive("T", bad)
            self.assertEqual(h.executor.calls, [])

    def test_no_entry_point_derives_an_event_id_from_mutable_state(self):
        """Checked against the parsed source, not the file text, because both
        modules now name the old defect in a docstring on purpose."""
        import ast as _ast
        for name in ("tick.py", "controller.py"):
            tree = _ast.parse((HERE / name).read_text())
            for node in _ast.walk(tree):
                if not isinstance(node, _ast.JoinedStr):
                    continue
                rendered = "".join(
                    _ast.unparse(v) for v in node.values
                    if isinstance(v, _ast.FormattedValue))
                self.assertNotIn("revision", rendered,
                                 f"{name} still builds a string from the state revision")
                self.assertNotIn("attempt", rendered,
                                 f"{name} still builds an event id from the attempt counter")

    def test_tick_will_not_run_without_the_callers_event_id(self):
        proc = subprocess.run(
            [sys.executable, str(HERE / "tick.py"), "--config",
             str(HERE / "config.replay.json"), "--task", "GOVDEMO"],
            capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(proc.returncode, 2, "tick ran with no event id")
        self.assertIn("--event", proc.stderr)


class LimitsAndStop(unittest.TestCase):

    def test_the_stop_file_halts_before_any_runner_is_started(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            pathlib.Path(h.config["stop_file"]).write_text("operator stop")
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out, {"action": "STOP", "reason": "operator_stop"})
            self.assertEqual(h.executor.calls, [])
            self.assertEqual(h.store.task("T")["status"], "STOPPED")

    def test_exceeding_the_attempt_cap_stops_instead_of_looping_forever(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, executor_heads=[H1, H2, H1], decisions=["BLOCKED"] * 3,
                        max_attempts=2)
            trail = h.ctl.drive("T", "evt-cap", max_steps=10)
            self.assertIn("STOP", [t["action"] for t in trail])
            self.assertEqual(h.store.task("T")["status"], "STOPPED")

    def test_running_out_of_runs_stops(self):
        """On a subscription there is no per-call price, so the budget is counted
        in RUNS. One runner invocation costs 1."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, run_budget=1)
            h.ctl.step("T", "evt-1")                    # one executor run -> 1 of 1 used
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out, {"action": "STOP", "reason": "limit"})
            self.assertEqual(h.store.spend(), 1)

    def test_each_runner_invocation_costs_exactly_one_run(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.drive("T", "evt-cycle")                            # execute, review, execute, review
            self.assertEqual(h.store.spend(), 4)

    def test_a_phase_outside_the_authorized_list_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, authorized_phases=["review"])       # execute not allowed
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["reason"], "outside_authority")
            self.assertEqual(h.executor.calls, [])

    def test_merge_and_deploy_are_not_phases_this_controller_knows(self):
        """The guard refuses any action name it does not recognise, so a config
        that asks for a merge cannot be honoured even if it is 'authorized'."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, authorized_phases=["execute", "review", "accept_review", "merge"])
            # H0 is the live head here, so the stale-head check passes and the
            # phase check is what the assertion is actually testing.
            order = h.ctl._order("T", "merge", H0, "evt-x", "r", "e", 0, 0.0)
            self.assertEqual(GUARD.evaluate(order),
                             {"action": "REJECT", "reason": "unknown_or_external_action"})


class CrashAndRestart(unittest.TestCase):

    def test_a_restart_does_not_repeat_a_completed_write(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.step("T", "evt-1")
            head_after = h.store.task("T")["last_head"]

            # a fresh process over the same directory: new Store, new Controller
            store2 = Store(pathlib.Path(h.config["state_dir"]))
            exec2 = FakeExecutor([H2])
            ctl2 = Controller(h.config, store2, GUARD, exec2,
                              FakeReviewer(["APPROVED"]), head_resolver=h._head)
            out = ctl2.step("T", "evt-1")                 # the same event redelivered
            self.assertEqual(out, {"action": "NOOP", "reason": "duplicate"})
            self.assertEqual(exec2.calls, [])
            self.assertEqual(store2.task("T")["last_head"], head_after)

    def test_a_crash_before_the_state_write_leaves_the_previous_state_intact(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            store.set_task("T", status="READY")
            try:
                store.commit(store.read()["revision"],
                             lambda s: (_ for _ in ()).throw(RuntimeError("crash mid-mutate")))
            except RuntimeError:
                pass
            self.assertEqual(store.task("T")["status"], "READY")
            self.assertTrue(json.loads(store.state_path.read_text()))   # not truncated

    def test_a_failed_runner_records_a_recovery_point(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, executor_heads=[])            # runner will raise
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "FAILED")
            task = h.store.task("T")
            self.assertEqual(task["status"], "FAILED")
            self.assertIn("recovery_point", task)
            self.assertIn("failure", task)


class TrustBoundary(unittest.TestCase):

    def test_the_guard_is_loaded_from_the_operator_path_not_from_the_work_tree(self):
        """A PR that rewrites governance/preflight.py must not change how the
        controller behaves. The controller resolves the guard from config, which
        comes from the operator's trusted checkout."""
        with tempfile.TemporaryDirectory() as td:
            tampered = pathlib.Path(td) / "preflight.py"
            tampered.write_text(
                "def evaluate(e):\n"
                "    return {'action': 'DISPATCH_ALLOWED', 'reason': 'anything goes'}\n")
            h = Harness(td)
            self.assertNotEqual(pathlib.Path(h.config["guard_path"]).resolve(),
                                tampered.resolve())
            # and the real guard still refuses what the tampered one would allow
            order = h.ctl._order("T", "merge", H1, "e", "r", "x", 0, 0.0)
            self.assertEqual(GUARD.evaluate(order)["action"], "REJECT")

    def test_a_work_order_is_built_by_the_controller_not_supplied_by_a_runner(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            order = h.ctl._order("T", "execute", H0, "e", "run", "exec", 0, 0.0)
            for field in ("authorized", "budget", "max_attempts", "stopped",
                          "live_head", "seen_events"):
                self.assertIn(field, order)
            self.assertIs(order["authorized"], True)
            self.assertEqual(order["budget"], h.config["run_budget"])

    def test_the_live_runner_refuses_to_start_while_disabled(self):
        with self.assertRaises(RunnerError) as cm:
            SubprocessRunner("executor", {"enabled": False, "command": ["true"]},
                             pathlib.Path("/tmp"))
        self.assertIn("disabled", str(cm.exception))

    def test_the_shipped_live_template_has_both_runners_disabled(self):
        cfg = json.loads((HERE / "config.live.example.json").read_text())
        for role in ("executor", "reviewer"):
            self.assertFalse(cfg["runners"][role]["enabled"], f"{role} ships enabled")

    def test_the_run_budget_is_counted_in_runs_and_says_so(self):
        cfg = json.loads((HERE / "config.live.example.json").read_text())
        self.assertGreater(cfg["run_budget"], 0, "a subscription has no per-call price to approve")
        self.assertIn("RUNS", cfg["run_budget_note"])


class RunnerEnvironmentIsAnAllowlist(unittest.TestCase):
    """G2 / GOV-R1-03. The old default was `env=None`, which subprocess reads as
    'inherit everything'. On the host this was written on that is 142 variables
    including GITHUB_TOKEN, AWS_SECRET_ACCESS_KEY and AITOKENKING_API_KEY, and
    the shipped template never set the field. Nothing leaked because live
    dispatch was never on, but the default contradicted what ACTIVATION.md
    promised."""

    PARENT = {
        "PATH": "/usr/bin:/bin", "HOME": "/home/u", "LANG": "C.UTF-8",
        "GITHUB_TOKEN": "ghs-SYNTHETIC", "GH_TOKEN": "ghs-SYNTHETIC",
        "AWS_SECRET_ACCESS_KEY": "SYNTHETIC-AWS", "AITOKENKING_API_KEY": "sk-SYNTHETIC",
        "CLAUDE_CODE_MESSAGING_TOKEN": "SYNTHETIC-MSG",
        "ANTHROPIC_API_KEY": "sk-ant-SYNTHETIC", "HTTPS_PROXY": "http://p",
    }
    SECRETS = ("GITHUB_TOKEN", "GH_TOKEN", "AWS_SECRET_ACCESS_KEY",
               "AITOKENKING_API_KEY", "CLAUDE_CODE_MESSAGING_TOKEN")

    def test_untrusted_pr_tests_get_no_credential_at_all(self):
        env = build_env("pr_tests", self.PARENT)
        for name in self.SECRETS + ("ANTHROPIC_API_KEY",):
            self.assertNotIn(name, env)
        for value in self.PARENT.values():
            if value.startswith(("ghs-", "sk-", "SYNTHETIC")):
                self.assertNotIn(value, env.values())

    def test_the_reviewer_never_receives_a_write_token(self):
        env = build_env("reviewer", self.PARENT)
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertNotIn("GH_TOKEN", env)
        self.assertIn("ANTHROPIC_API_KEY", env)      # it still needs the model

    def test_the_second_line_holds_if_the_role_list_is_edited_wrongly(self):
        """Mutation testing caught this: deleting the DENY_ALWAYS branch changed
        nothing, because the reviewer's credential list does not name a write
        token anyway — so the branch was a guard nothing could trigger. The
        input it exists for is a future edit that wrongly adds one. Fed here."""
        import runners
        broken = dict(runners.ROLE_CREDENTIALS)
        broken["reviewer"] = ("ANTHROPIC_API_KEY", "GITHUB_TOKEN", "GH_TOKEN")
        with patch.object(runners, "ROLE_CREDENTIALS", broken):
            env = runners.build_env("reviewer", self.PARENT)
        self.assertNotIn("GITHUB_TOKEN", env, "the deny list did not stop a bad role edit")
        self.assertNotIn("GH_TOKEN", env)
        self.assertIn("ANTHROPIC_API_KEY", env)

    def test_the_same_second_line_protects_untrusted_pr_tests(self):
        broken = dict(runners.ROLE_CREDENTIALS)
        broken["pr_tests"] = ("GITHUB_TOKEN",)
        with patch.object(runners, "ROLE_CREDENTIALS", broken):
            env = runners.build_env("pr_tests", self.PARENT)
        self.assertNotIn("GITHUB_TOKEN", env)

    def test_the_executor_gets_the_branch_token_and_nothing_unrelated(self):
        env = build_env("executor", self.PARENT)
        self.assertIn("GITHUB_TOKEN", env)
        self.assertIn("ANTHROPIC_API_KEY", env)
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", env)
        self.assertNotIn("CLAUDE_CODE_MESSAGING_TOKEN", env)

    def test_a_variable_added_to_the_parent_later_is_still_excluded(self):
        """An allowlist, not a denylist — new secrets do not leak by default."""
        parent = dict(self.PARENT, SOME_FUTURE_TOKEN="SYNTHETIC-NEW")
        for role in ROLE_CREDENTIALS:
            self.assertNotIn("SOME_FUTURE_TOKEN", build_env(role, parent))

    def test_there_is_no_way_to_ask_for_full_inheritance(self):
        """The defect was an option that meant 'inherit everything'. It is gone.

        Checked against the parsed module rather than the file text, because the
        docstring names the old field on purpose to explain the defect — a
        substring check would pass or fail on the wrong thing.
        """
        import ast as _ast
        tree = _ast.parse(pathlib.Path(HERE / "runners.py").read_text())
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Constant) and node.value == "env_passthrough_only":
                self.fail("env_passthrough_only is still read somewhere in runners.py")
            if isinstance(node, _ast.keyword) and node.arg == "env":
                self.assertFalse(
                    isinstance(node.value, _ast.Constant) and node.value.value is None,
                    "a subprocess call still passes env=None, which inherits everything",
                )
        for role in ROLE_CREDENTIALS:
            env = build_env(role, self.PARENT)
            self.assertLessEqual(len(env), len(BASE_ENV_ALLOWLIST) + 4)

    def test_every_subprocess_call_in_the_adapter_passes_an_explicit_env(self):
        """Not just the model call — the clone and the checkout run PR-adjacent
        git too, and an inherited environment there is the same leak."""
        import ast as _ast
        tree = _ast.parse(pathlib.Path(HERE / "runners.py").read_text())
        calls = [n for n in _ast.walk(tree)
                 if isinstance(n, _ast.Call)
                 and isinstance(n.func, _ast.Attribute)
                 and n.func.attr == "run"
                 and isinstance(n.func.value, _ast.Name)
                 and n.func.value.id == "subprocess"]
        self.assertTrue(calls, "no subprocess.run calls found — did the adapter change?")
        for call in calls:
            self.assertIn("env", [k.arg for k in call.keywords],
                          f"subprocess.run at line {call.lineno} passes no env")

    def test_every_role_still_gets_a_usable_baseline(self):
        for role in ROLE_CREDENTIALS:
            env = build_env(role, {})
            self.assertTrue(env["PATH"])
            self.assertTrue(env["HOME"])

    def test_an_unknown_role_is_refused_rather_than_defaulted(self):
        with self.assertRaises(RunnerError):
            build_env("something-else", self.PARENT)


class InspectionIsNotEvidenceOfAuthentication(unittest.TestCase):
    """The defect this round measured rather than argued.

    `_require_auth` used to refuse whenever no credential appeared in the
    environment. Run against the real CLI, all three roles authenticated a
    billed model call while the environment held no credential at all and HOME
    pointed at an empty directory — evidence/auth_isolation_probe.json.

    So the old gate would have turned a working runner into BLOCKED_ACCESS. The
    failure mode is the mirror of reporting success without running: an outcome
    decided by looking at variables instead of by what happened."""

    CFG = {"enabled": True, "command": ["true"], "identity_suffix": "t"}

    def _runner(self, tmp, role="reviewer", **over):
        return SubprocessRunner(role, {**self.CFG, **over}, pathlib.Path(tmp))

    def test_the_three_states_are_distinguishable(self):
        self.assertEqual(credential_state("reviewer", {"ANTHROPIC_API_KEY": "x"}),
                         "env_credential")
        self.assertEqual(credential_state("reviewer", {}), "ambient_possible")
        self.assertEqual(credential_state("reviewer", {"ATK_NO_AMBIENT_MODEL_AUTH": "1"}),
                         "declared_unavailable")

    def test_an_empty_environment_is_no_longer_treated_as_proof_of_failure(self):
        """The regression. An empty parent must NOT raise on its own."""
        with tempfile.TemporaryDirectory() as tmp:
            runner = self._runner(tmp)
            runner._require_auth({})              # must not raise
            self.assertEqual(runner._credential_state, "ambient_possible")

    def test_only_the_operator_can_declare_authentication_impossible(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = self._runner(tmp)
            with self.assertRaises(AuthUnavailable) as cm:
                runner._require_auth({"ATK_NO_AMBIENT_MODEL_AUTH": "true"})
            self.assertIn("declared", str(cm.exception))

    def test_absence_in_the_environment_is_reported_as_unknown_not_as_no(self):
        """The whole correction in one assertion: the same empty environment
        that makes has_credential say False must NOT make the capability
        question say 'cannot authenticate'. Collapsing those two was the bug."""
        self.assertFalse(has_credential("reviewer", {}))
        self.assertEqual(credential_state("reviewer", {}), "ambient_possible")
        self.assertNotEqual(credential_state("reviewer", {}), "declared_unavailable")


class EnvironmentFilteringIsNotAnIsolationBoundary(unittest.TestCase):
    """Measured: under the repository's own allowlist — four variables, no
    credential among them — the model CLI authenticated and billed, for the
    `pr_tests` role that the config template described as receiving "nothing".

    The fix is not a better allowlist. It is to stop accepting an allowlist as
    the boundary for untrusted code, and to make the code refuse instead."""

    CFG = {"enabled": True, "command": ["true"], "identity_suffix": "t"}

    def test_untrusted_pr_code_will_not_run_without_a_declared_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(IsolationUnavailable) as cm:
                SubprocessRunner("pr_tests", self.CFG, pathlib.Path(tmp), role="pr_tests")
            self.assertIn("container", str(cm.exception))

    def test_declaring_a_container_is_no_longer_enough(self):
        """R3 tightened this. Declaring the level used to permit the role. Now
        the backend's properties are MEASURED and the role is refused unless
        they cover what it needs. On this host the available backend denies the
        network and nothing else, so pr_tests is still refused — with a reason
        that names the missing properties rather than the missing tool."""
        import runners as _r
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(_r, "working_container_backend", return_value="unshare"), \
                 patch.object(_r, "measure_backend_properties",
                              return_value={"network_denied": True,
                                            "host_fs_denied": False,
                                            "source_readonly": False}):
                with self.assertRaises(IsolationUnavailable) as cm:
                    _r.SubprocessRunner("pr_tests", {**self.CFG,
                                                     "isolation_level": "container"},
                                        pathlib.Path(tmp), role="pr_tests")
            self.assertIn("host_fs_denied", str(cm.exception))

    def test_a_backend_that_covers_every_required_property_is_accepted(self):
        import runners as _r
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(_r, "working_container_backend", return_value="bwrap"), \
                 patch.object(_r, "measure_backend_properties",
                              return_value={k: True for k in _r.ISOLATION_PROPERTIES}):
                r = _r.SubprocessRunner("pr_tests", {**self.CFG,
                                                     "isolation_level": "container"},
                                        pathlib.Path(tmp), role="pr_tests")
            self.assertEqual(r._isolation_level, "container")

    def test_the_wrap_is_actually_applied_to_the_command(self):
        """The R3 finding: the backend was probed, stored, and then Popen ran
        the bare command on the host anyway."""
        import runners as _r
        self.assertEqual(_r.isolate_command(None, ["x"]), ["x"])
        wrapped = _r.isolate_command("unshare", ["x", "-y"])
        self.assertEqual(wrapped[:2], ["unshare", "--user"])
        self.assertEqual(wrapped[-2:], ["x", "-y"])
        src = (HERE / "runners.py").read_text()
        self.assertIn("isolate_command(getattr(self", src,
                      "run() no longer routes the command through the wrap")

    NET_PROBE = """#!/usr/bin/env python3
import json, socket
s = socket.socket(); s.settimeout(5)
denied = s.connect_ex(("1.1.1.1", 443)) != 0
print(json.dumps({"new_head": ("a" if denied else "b") * 40}))
"""

    def test_run_really_launches_the_command_inside_the_backend(self):
        """The runtime half of the R3 finding. A source check proves the call
        is written down; this proves it reached the kernel. The command the
        runner launches reports whether IT could open a socket — if the wrap
        were dropped between the probe and Popen, the answer changes."""
        backend = runners.working_container_backend()
        if backend is None:
            self.skipTest("no container backend on this host; nothing to prove")
        props = runners.measure_backend_properties(backend)
        if not props.get("network_denied"):
            self.skipTest(f"backend {backend!r} does not deny the network here")
        with tempfile.TemporaryDirectory() as tmp:
            probe = pathlib.Path(tmp) / "probe.py"
            probe.write_text(self.NET_PROBE)
            probe.chmod(0o755)
            repo = pathlib.Path(tmp) / "origin"
            repo.mkdir()
            env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e",
                       GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e")
            run = lambda *a: subprocess.run(a, cwd=repo, check=True, env=env,
                                            capture_output=True)
            run("git", "init", "--quiet", "-b", "main")
            (repo / "README").write_text("x\n")
            run("git", "add", "README"); run("git", "commit", "--quiet", "-m", "c")
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                                  capture_output=True, text=True).stdout.strip()

            # Unwrapped first: if the host has no network at all, "denied" would
            # be true for the wrong reason and this test would pass vacuously.
            bare = subprocess.run([sys.executable, str(probe)], capture_output=True,
                                  text=True, timeout=60)
            if json.loads(bare.stdout)["new_head"] != "b" * 40:
                self.skipTest("this host has no outbound network; the control is vacuous")

            import runners as _r
            with patch.object(_r, "measure_backend_properties",
                              return_value={k: True for k in _r.ISOLATION_PROPERTIES}):
                runner = _r.SubprocessRunner(
                    "executor", {"enabled": True, "identity_suffix": "iso",
                                 "command": [sys.executable, str(probe)],
                                 "isolation_level": "container",
                                 "timeout_seconds": 120},
                    pathlib.Path(tmp) / "ws", role="executor")
                result = runner.run({"task_id": "T", "head": head,
                                     "repo_url": str(repo), "prompt_file": "P.md",
                                     "policy_sha": "p" * 40, "phase": "execute",
                                     "run_identity": "r", "deadline_seconds": 100,
                                     "deadline_at": time.time() + 100})
            self.assertEqual(result, {"new_head": "a" * 40},
                             "the runner's own child still reached the network: "
                             "the wrap did not reach Popen")

    def test_a_made_up_isolation_level_is_refused_not_defaulted(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RunnerError):
                SubprocessRunner("reviewer", {**self.CFG, "isolation_level": "sandboxed"},
                                 pathlib.Path(tmp))

    def test_trusted_roles_still_run_under_the_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            for role in ("executor", "reviewer"):
                r = SubprocessRunner(role, self.CFG, pathlib.Path(tmp), role=role)
                self.assertEqual(r._isolation_level, "process_env")


class ARunnerMustNotInheritTheCallersSessionIdentity(unittest.TestCase):
    """With the full parent environment the CLI returned the CALLER's session id
    and read the caller's cached prefix; under the allowlist it returned a fresh
    one. Reviewer independence rests on that, so the variable is denied by name
    rather than merely left off the allowlist."""

    def test_the_session_id_is_dropped_even_if_the_allowlist_grows(self):
        import runners as _r
        parent = {"PATH": "/usr/bin", "HOME": "/h",
                  "CLAUDE_CODE_SESSION_ID": "SYNTHETIC-SESSION"}
        wider = tuple(BASE_ENV_ALLOWLIST) + ("CLAUDE_CODE_SESSION_ID",)
        with patch.object(_r, "BASE_ENV_ALLOWLIST", wider):
            env = _r.build_env("reviewer", parent)
        self.assertNotIn("CLAUDE_CODE_SESSION_ID", env,
                         "a widened allowlist let the caller's session id through")

    def test_the_denied_names_are_recorded_rather_than_implied(self):
        self.assertIn("CLAUDE_CODE_SESSION_ID", DENY_SESSION_IDENTITY)


class TheShippedLiveTemplateMustActuallyLaunch(unittest.TestCase):
    """GOV-R2-01. The reviewer filled in the shipped template with the same
    standard function the adapter used and got KeyError: '"new_head"'. The
    template could never have dispatched, and the failure was not a RunnerError,
    so it escaped the structured failure path too.

    The earlier adapter test passed because it wrote its own command. Testing a
    configuration that does not contain the defect is not testing the one that
    ships."""

    def _live(self):
        return json.loads((HERE / "config.live.example.json").read_text())

    def test_both_shipped_roles_render_without_raising(self):
        cfg = self._live()
        for role in ("executor", "reviewer"):
            with self.subTest(role=role):
                out = render_command(cfg["runners"][role]["command"], {
                    "prompt_file": "p.md", "head": "a" * 40,
                    "work_order": "/w/work_order.json", "deadline_seconds": 60})
                self.assertTrue(all(isinstance(x, str) for x in out))

    def test_a_prompt_describing_json_survives_substitution(self):
        """The exact input that broke it: braces that are not placeholders."""
        out = render_command(['emit {"new_head": "<sha>"} for {head}'], {"head": "H"})
        self.assertEqual(out, ['emit {"new_head": "<sha>"} for H'])

    def test_str_format_still_fails_on_that_input(self):
        """The negative control: prove the old approach really was broken, so
        this test cannot quietly pass for the wrong reason."""
        with self.assertRaises(KeyError):
            'emit {"new_head": "<sha>"}'.format(head="H")

    def test_an_unknown_placeholder_is_a_config_error_not_a_keyerror(self):
        with self.assertRaises(CommandTemplateError):
            render_command(["--at {branch}"], {"head": "H"})


class TheWorkOrderReachesTheRunnerNotJustTheLog(unittest.TestCase):
    """GOV-R2-04. goal, scope_paths, acceptance, decision_ids, policy_sha,
    run identity and deadline were assembled, logged, and never delivered: the
    command only ever received prompt_file and head, and prompt_file pointed
    INSIDE the clone under review."""

    CFG = {"enabled": True, "command": ["true"], "identity_suffix": "t"}

    def test_a_work_order_missing_the_binding_fields_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = SubprocessRunner("executor", self.CFG, pathlib.Path(tmp))
            with self.assertRaises(RunnerError) as cm:
                r._write_work_order({"task_id": "T", "head": "a" * 40},
                                    pathlib.Path(tmp) / "repo")
            for field in ("policy_sha", "phase", "run_identity"):
                self.assertIn(field, str(cm.exception))

    def test_it_is_written_outside_the_checkout_under_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "ws" / "repo"
            repo.mkdir(parents=True)
            r = SubprocessRunner("executor", self.CFG, pathlib.Path(tmp))
            order = {"task_id": "T", "head": "a" * 40, "policy_sha": "c" * 40,
                     "phase": "execute", "run_identity": "exec-1",
                     "goal": "g", "scope_paths": ["x/"], "decision_ids": ["GOV-01"]}
            path = r._write_work_order(order, repo)
            self.assertNotIn(repo, path.parents,
                             "the contract sits inside the tree it governs")
            got = json.loads(path.read_text())
            for field in ("goal", "scope_paths", "decision_ids", "policy_sha"):
                self.assertIn(field, got)


class TheLeaseIsKeptAliveAndTheCommitIsFenced(unittest.TestCase):
    """GOV-R2-02. Store.renew and holds_lease were written, tested, and never
    called by the controller. Meanwhile the template gave a runner 1500s under
    a 900s lease."""

    def test_the_shipped_lease_outlasts_the_slowest_runner(self):
        cfg = json.loads((HERE / "config.live.example.json").read_text())
        worst = max(r["timeout_seconds"] + r["clone_timeout"]
                    for r in cfg["runners"].values())
        self.assertGreater(cfg["lease_seconds"], worst,
                           "a runner can outlive its own lease")

    def test_the_controller_actually_calls_renew_and_holds_lease(self):
        """The dead-code check, stated as a test so it cannot come back."""
        import ast as _ast
        tree = _ast.parse((HERE / "controller.py").read_text())
        called = {n.func.attr for n in _ast.walk(tree)
                  if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)}
        # P2 (R4): the intent is now recorded by the same fenced commit that
        # reserves the run, so the API that must be called changed name.
        for api in ("renew", "holds_lease", "reserve_run_and_record_intent"):
            self.assertIn(api, called, f"{api} is still never called")
        # ...and the old two-commit pair must not come back beside it.
        for api in ("add_spend", "record_intent"):
            self.assertNotIn(api, called,
                             f"controller calls {api} outside the fenced reservation")

    def test_two_controllers_from_one_config_do_not_share_an_owner(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Harness(td + "/a"), Harness(td + "/b")
            self.assertNotEqual(a.ctl.owner, b.ctl.owner,
                                "a static identity lets a second tick re-enter")

    def test_a_result_is_discarded_when_the_lease_was_lost(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            with patch.object(type(h.store), "holds_lease", return_value=False):
                out = h.ctl.step("T", "evt-1")
            self.assertEqual(out, {"action": "NOOP", "reason": "lease_lost_mid_run"})
            self.assertNotEqual(h.store.task("T").get("status"), "REVIEW_PENDING")
            self.assertTrue(h.store.open_intents("T"),
                            "an unresolved external effect left no intent to reconcile")


class TheEventAndTheTransitionCommitTogether(unittest.TestCase):
    """GOV-R2-03. mark_processed ran before set_task, so a crash between them
    deduplicated the event away while the task had not moved. The comment in
    the code claimed the opposite of what the code did."""

    def test_the_two_writes_are_one_commit(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            before = h.store.read()["revision"]
            h.ctl.step("T", "evt-1")
            state = h.store.read()
            self.assertIn("evt-1", state["processed_events"])
            self.assertEqual(state["tasks"]["T"]["status"], "REVIEW_PENDING")
            self.assertLess(state["revision"] - before, 8,
                            "the event and the transition are still separate commits")

    def test_the_controller_no_longer_marks_an_event_before_advancing(self):
        import ast as _ast
        src = (HERE / "controller.py").read_text()
        self.assertIn("commit_event_and_task", src)
        tree = _ast.parse(src)
        n_mark = sum(1 for n in _ast.walk(tree)
                     if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)
                     and n.func.attr == "mark_processed")
        self.assertLessEqual(n_mark, 1, "event-first commits remain on a live path")

    def test_an_intent_is_recorded_before_the_external_effect(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            seen = []

            class Watch(FakeExecutor):
                def run(self, order):
                    seen.append(list(h.store.open_intents("T")))
                    return super().run(order)

            h.executor = Watch([H1]); h.ctl.executor = h.executor
            h.ctl.step("T", "evt-1")
            self.assertTrue(seen and seen[0],
                            "the runner was dispatched with no durable intent")
            self.assertFalse(h.store.open_intents("T"),
                             "the intent was never closed after the result landed")


class RunsAndTheRoundDeadlineAreNotResetByFailure(unittest.TestCase):
    """GOV-R2-05. add_spend sat after a successful return, so a call that
    started and then failed cost nothing; and `started` was reset on every
    step, so the round limit bounded a step rather than a round."""

    def test_a_failed_run_still_costs_a_run(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)

            class Boom(FakeExecutor):
                def run(self, order):
                    raise RunnerError("provider exploded")

            h.executor = Boom([H1]); h.ctl.executor = h.executor
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "FAILED")
            self.assertEqual(h.store.spend(), 1,
                             "a started-then-failed call was counted as free")

    def test_the_round_deadline_survives_steps(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.step("T", "evt-1")
            first = h.store.task("T")["round_deadline"]
            h.ctl.step("T", "evt-2")
            self.assertEqual(h.store.task("T")["round_deadline"], first,
                             "each step restarted the round clock")

    def test_the_runner_is_told_the_remaining_round_time(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            seen = {}

            class Peek(FakeExecutor):
                def run(self, order):
                    seen.update(order)
                    return super().run(order)

            h.executor = Peek([H1]); h.ctl.executor = h.executor
            h.ctl.step("T", "evt-1")
            self.assertIn("deadline_seconds", seen)
            self.assertGreater(seen["deadline_seconds"], 0)
            # R3: the runner recomputes what is left from an ABSOLUTE instant,
            # because the clone and the checkout spend real time before the
            # model starts. The controller shipped only `deadline_seconds`
            # while runners._remaining read `deadline_at`, found nothing, and
            # fell back to the runner's own full timeout — so the round limit
            # reached the prompt and bounded nothing that actually stops.
            self.assertIn("deadline_at", seen,
                          "the absolute round deadline never reached the runner")
            self.assertAlmostEqual(seen["deadline_at"],
                                   h.store.task("T")["round_deadline"], places=3)

    def test_an_expired_round_refuses_to_dispatch_at_all(self):
        """GOV-R2-05: an overrun round used to clamp `deadline_seconds` to 1
        and dispatch anyway. The round's real age now goes to the guard, whose
        own `elapsed >= timeout` STOP is what refuses it — so the limit is
        enforced by the trusted policy rather than by the caller."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.store.set_task("T", round_deadline=time.time() - 1)
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "STOP")
            self.assertEqual(out["reason"], "limit")
            self.assertEqual(h.executor.calls, [],
                             "a runner was started after the round had expired")
            self.assertEqual(h.store.task("T")["status"], "STOPPED")

    def test_the_round_age_grows_across_steps(self):
        """The negative control for the same field: if `elapsed` were still
        per-step it would be ~0 every time and the STOP above could not fire."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            seen = []

            class Peek(FakeExecutor):
                def run(self, order):
                    seen.append(order["elapsed"])
                    return super().run(order)

            h.executor = Peek([H1, H2]); h.ctl.executor = h.executor
            h.ctl.step("T", "evt-1")
            h.store.set_task("T", round_deadline=time.time() + 100)
            h.store.set_task("T", status="READY")
            h.ctl.step("T", "evt-2")
            self.assertGreater(seen[-1], 2500,
                               "elapsed is still measured from the start of the step")

    def test_the_runner_stops_at_the_round_deadline_not_at_its_own(self):
        """The runner's own timeout is 1200s. If the round has two seconds
        left, two seconds is the limit — measured by actually running one."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "origin"
            repo.mkdir()
            env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e",
                       GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e")
            run = lambda *a: subprocess.run(a, cwd=repo, check=True, env=env,
                                            capture_output=True)
            run("git", "init", "--quiet", "-b", "main")
            (repo / "README").write_text("x\n")
            run("git", "add", "README"); run("git", "commit", "--quiet", "-m", "c")
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                                  capture_output=True, text=True).stdout.strip()
            runner = SubprocessRunner(
                "executor", {"enabled": True, "identity_suffix": "d",
                             "command": ["sleep", "120"],
                             "timeout_seconds": 1200, "terminate_grace_seconds": 1},
                pathlib.Path(tmp) / "ws", role="executor")
            order = {"task_id": "T", "head": head, "repo_url": str(repo),
                     "prompt_file": "P.md", "policy_sha": "p" * 40,
                     "phase": "execute", "run_identity": "r",
                     "deadline_seconds": 1200,
                     "deadline_at": time.time() + 3}
            started = time.time()
            with self.assertRaises(RunnerError) as cm:
                runner.run(order)
            self.assertIn("timed out", str(cm.exception))
            self.assertLess(time.time() - started, 60,
                            "the runner waited for its own timeout, not the round's")


class MissingAuthIsBlockedNotPassed(unittest.TestCase):
    """G2: an unauthenticated runner must report BLOCKED_ACCESS, never success."""

    def test_has_credential_ignores_a_write_token(self):
        self.assertFalse(has_credential("executor", {"GITHUB_TOKEN": "x"}))
        self.assertTrue(has_credential("executor", {"ANTHROPIC_API_KEY": "x"}))

    def test_the_controller_records_blocked_access_and_runs_nothing_further(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)

            class NoAuth(FakeExecutor):
                def run(self, order):
                    raise AuthUnavailable("no model credential available to this role")

            h.executor = NoAuth([H1])
            h.ctl.executor = h.executor
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out, {"action": "BLOCKED_ACCESS", "reason": "no_credential"})
            self.assertEqual(h.store.task("T")["status"], "BLOCKED_ACCESS")
            self.assertNotEqual(h.store.task("T")["status"], "COMPLETE")


class TheRealAdapterIsTestedWithAStubExecutable(unittest.TestCase):
    """G2 says explicitly: testing FakeExecutor does not verify SubprocessRunner.

    These drive the real adapter's parsing and error handling with a stub program
    that prints scripted bytes — no model, no network, no credential.
    """

    def test_a_well_formed_executor_verdict_parses(self):
        out = parse_verdict("executor", json.dumps({"new_head": "a" * 40}))
        self.assertEqual(out["new_head"], "a" * 40)

    def test_a_short_or_non_hex_head_is_refused(self):
        for bad in ("abc", "z" * 40, "", None, 12345):
            with self.subTest(head=bad), self.assertRaises(RunnerError):
                parse_verdict("executor", json.dumps({"new_head": bad}))

    def test_unparseable_output_is_a_failure_not_an_approval(self):
        for text in ("", "not json", "exit 0", "<html>error</html>"):
            with self.subTest(text=text), self.assertRaises(RunnerError):
                parse_verdict("reviewer", text)

    def test_the_error_never_quotes_the_payload(self):
        """stdout is exactly where a provider body or a log line would be."""
        secret = "SYNTHETIC_PRIVATE_729"
        with self.assertRaises(RunnerError) as cm:
            parse_verdict("reviewer", f"garbage {secret} garbage")
        self.assertNotIn(secret, str(cm.exception))

    def test_a_review_without_evidence_is_refused(self):
        payload = {"review": {"head": "a" * 40, "reviewer": "r",
                              "decision": "APPROVED", "evidence": []}}
        with self.assertRaises(RunnerError):
            parse_verdict("reviewer", json.dumps(payload))

    def test_a_review_missing_a_required_field_is_refused(self):
        for drop in ("head", "reviewer", "decision"):
            payload = {"review": {"head": "a" * 40, "reviewer": "r",
                                  "decision": "APPROVED", "evidence": ["e"]}}
            del payload["review"][drop]
            with self.subTest(missing=drop), self.assertRaises(RunnerError):
                parse_verdict("reviewer", json.dumps(payload))

    def test_a_stub_executable_end_to_end_through_subprocess(self):
        """The command template, the CLI wrapper and the JSON contract together."""
        with tempfile.TemporaryDirectory() as td:
            stub = pathlib.Path(td) / "stub.py"
            stub.write_text('import json;print(json.dumps({"new_head": "b"*40}))')
            result = subprocess.run([sys.executable, str(stub)],
                                    capture_output=True, text=True,
                                    env=build_env("executor", {"PATH": os.environ["PATH"]}))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(parse_verdict("executor", result.stdout)["new_head"], "b" * 40)

    def test_a_stub_that_exits_nonzero_is_a_failure(self):
        with tempfile.TemporaryDirectory() as td:
            stub = pathlib.Path(td) / "stub.py"
            stub.write_text('import sys;print("SYNTHETIC_LEAK");sys.exit(3)')
            result = subprocess.run([sys.executable, str(stub)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 3)
            # the adapter turns this into RunnerError without quoting stdout
            self.assertIn("SYNTHETIC_LEAK", result.stdout)



class TheRealRunAdapterIsDrivenEndToEnd(unittest.TestCase):
    """Mutation testing found the hole: every adapter test above calls
    parse_verdict or spawns its own subprocess, so SubprocessRunner.run — the
    clone, the Popen, the timeout, the process-group kill — was never executed
    by the suite at all. Deleting `start_new_session=True` from it changed
    nothing and no test noticed.

    These drive the real method against a local git repository and a stub
    program. No model, no network, no real credential.
    """

    def _repo(self, tmp):
        """A real git repo on disk, so `git clone` works with no network."""
        repo = pathlib.Path(tmp) / "origin"
        repo.mkdir()
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e")
        run = lambda *a: subprocess.run(a, cwd=repo, check=True, env=env,
                                        capture_output=True)
        run("git", "init", "--quiet", "-b", "main")
        (repo / "README").write_text("fixture\n")
        run("git", "add", "README")
        run("git", "commit", "--quiet", "-m", "fixture")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                              capture_output=True, text=True).stdout.strip()
        return repo, head

    def _order(self, repo, head, **over):
        """A work order that satisfies the contract the runner now enforces.

        It used to be four keys. The runner accepted it because it only ever
        read two of them; the rest of the contract was assembled, logged, and
        never delivered."""
        order = {"task_id": "T", "head": head, "repo_url": str(repo),
                 "prompt_file": "governance/IMPLEMENTATION_PROMPT.md",
                 "policy_sha": "c" * 40, "phase": "execute",
                 "run_identity": "executor-test-1", "goal": "fixture",
                 "scope_paths": ["governance/"], "acceptance": "fixture",
                 "decision_ids": ["GOV-01"], "event_id": "evt-fixture",
                 "deadline_seconds": 30}
        order.update(over)
        return order

    def _runner(self, tmp, command, **over):
        cfg = {"enabled": True, "command": command, "identity_suffix": "test",
               "timeout_seconds": 30, "clone_timeout": 60, **over}
        return SubprocessRunner("executor", cfg, pathlib.Path(tmp) / "work")

    def test_a_stub_runner_runs_and_its_verdict_is_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = self._repo(tmp)
            stub = pathlib.Path(tmp) / "stub.py"
            stub.write_text('import json; print(json.dumps({"new_head": "b"*40}))')
            runner = self._runner(tmp, [sys.executable, str(stub)])
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-SYNTHETIC"}):
                out = runner.run(self._order(repo, head))
            self.assertEqual(out["new_head"], "b" * 40)

    def test_a_runner_that_hangs_is_timed_out_with_its_children(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = self._repo(tmp)
            pidfile = pathlib.Path(tmp) / "worker.pid"
            stub = pathlib.Path(tmp) / "stub.sh"
            stub.write_text(SPAWNER)
            stub.chmod(0o755)
            runner = self._runner(tmp, ["sh", str(stub), str(pidfile)],
                                  timeout_seconds=2, terminate_grace_seconds=2)
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-SYNTHETIC"}):
                with self.assertRaises(RunnerError) as cm:
                    runner.run(self._order(repo, head))
            self.assertIn("timed out", str(cm.exception))
            worker = int(pidfile.read_text().strip())
            time.sleep(0.4)
            self.assertFalse(still_running(worker),
                             "the timed-out runner left its own worker running, "
                             "still holding the credentials from its environment")

    def test_the_timeout_message_never_quotes_the_runners_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = self._repo(tmp)
            stub = pathlib.Path(tmp) / "stub.sh"
            stub.write_text("#!/bin/sh\necho SYNTHETIC_LEAK_881\nwhile true; do sleep 0.2; done\n")
            stub.chmod(0o755)
            runner = self._runner(tmp, ["sh", str(stub)], timeout_seconds=1,
                                  terminate_grace_seconds=2)
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-SYNTHETIC"}):
                with self.assertRaises(RunnerError) as cm:
                    runner.run(self._order(repo, head))
            self.assertNotIn("SYNTHETIC_LEAK_881", str(cm.exception))

    def test_a_runner_can_be_cancelled_while_it_is_running(self):
        """L3 through the adapter: cancel_current reaches the live child."""
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = self._repo(tmp)
            pidfile = pathlib.Path(tmp) / "worker.pid"
            stub = pathlib.Path(tmp) / "stub.sh"
            stub.write_text(SPAWNER)
            stub.chmod(0o755)
            runner = self._runner(tmp, ["sh", str(stub), str(pidfile)],
                                  timeout_seconds=8, terminate_grace_seconds=2)
            self.assertEqual(runner.cancel_current(), "nothing_running")

            box = {}

            def go():
                with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-SYNTHETIC"}):
                    try:
                        runner.run(self._order(repo, head))
                    except RunnerError as exc:
                        box["error"] = exc

            worker_thread = threading.Thread(target=go, daemon=True)
            worker_thread.start()
            for _ in range(200):
                if pidfile.exists() and pidfile.read_text().strip():
                    break
                time.sleep(0.05)
            worker = int(pidfile.read_text().strip())
            self.assertIn(runner.cancel_current(grace_seconds=2),
                          ("terminated", "killed"))
            worker_thread.join(timeout=20)
            self.assertFalse(worker_thread.is_alive(), "run() never returned after cancel")
            time.sleep(0.4)
            self.assertFalse(still_running(worker))


class AReportedHeadIsVerifiedAgainstTheRemote(unittest.TestCase):
    """G2: `new_head` from a runner is a claim. A push can fail silently."""

    def test_a_head_that_is_not_on_the_branch_fails_the_task(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, known_commits={H0})        # H1 was never pushed
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "FAILED")
            self.assertEqual(out["reason"], "reported_head_not_on_branch")
            self.assertEqual(h.store.task("T")["status"], "FAILED")
            self.assertIn("recovery_point", h.store.task("T"))
            self.assertEqual(h.reviewer.calls, [], "a reviewer ran against a phantom commit")

    def test_a_head_that_is_on_the_branch_proceeds(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, known_commits={H0, H1, H2})
            self.assertEqual(h.ctl.step("T", "evt-1")["action"], "REVIEW_PENDING")


class LeaseRenewalAndIntentLedger(unittest.TestCase):
    """G3: a long task must not be stolen mid-flight; a crash between an
    external side effect and the local save must not blindly repeat it."""

    def test_a_holder_can_extend_its_own_lease(self):
        with tempfile.TemporaryDirectory() as td:
            now = [1000.0]
            store = Store(pathlib.Path(td), clock=lambda: now[0])
            store.acquire("T", "worker-a", ttl=100)
            now[0] = 1050.0
            store.renew("T", "worker-a", ttl=100)
            now[0] = 1120.0
            self.assertTrue(store.holds_lease("T", "worker-a"),
                            "renewal did not extend past the original expiry")

    def test_a_worker_that_already_lost_the_lease_cannot_renew(self):
        with tempfile.TemporaryDirectory() as td:
            now = [1000.0]
            store = Store(pathlib.Path(td), clock=lambda: now[0])
            store.acquire("T", "worker-a", ttl=10)
            now[0] = 2000.0
            with self.assertRaises(ConcurrencyError):
                store.renew("T", "worker-a", ttl=100)

    def test_someone_elses_lease_cannot_be_renewed(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            store.acquire("T", "worker-a", ttl=600)
            with self.assertRaises(ConcurrencyError):
                store.renew("T", "worker-b", ttl=600)

    def test_an_open_intent_survives_a_restart_and_names_what_to_check(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            intent = store.record_intent("T", "push", branch="work", head=H1)
            reopened = Store(pathlib.Path(td))        # a fresh process
            open_now = reopened.open_intents("T")
            self.assertEqual(len(open_now), 1)
            self.assertEqual(open_now[0]["action"], "push")
            self.assertEqual(open_now[0]["head"], H1)
            reopened.close_intent("T", intent, outcome="effect_confirmed")
            self.assertEqual(Store(pathlib.Path(td)).open_intents("T"), [])


class WorkOrderContract(unittest.TestCase):
    """G3 lists the fields a work order must carry."""

    REQUIRED = ("task_id", "goal", "scope_paths", "acceptance", "decision_ids",
                "branch", "head", "policy_sha", "phase", "run_id",
                "command_allowlist", "deadline", "evidence",
                "max_attempts", "budget", "timeout")

    def test_every_required_field_is_present(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, goal="g", scope_paths=["a/"], acceptance="acc",
                        decision_ids=["GOV-01"], command_allowlist=["git"])
            order = h.ctl._order("T", "execute", H0, "evt", "run", "exec", 0, 0.0)
            for field in self.REQUIRED:
                self.assertIn(field, order, f"work order is missing {field}")

    def test_the_policy_sha_is_recorded_on_every_order(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            order = h.ctl._order("T", "execute", H0, "evt", "run", "exec", 0, 0.0)
            self.assertEqual(order["policy_sha"], "policy" + "0" * 35)
            self.assertNotEqual(order["policy_sha"], "unrecorded")


class AuditTrail(unittest.TestCase):

    def test_every_guard_decision_is_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.drive("T", "evt-cycle")
            guard_events = [e for e in h.store.events() if e["kind"] == "guard"]
            self.assertEqual([e["phase"] for e in guard_events],
                             ["execute", "review", "accept_review",
                              "execute", "review", "accept_review"])
            for event in guard_events:
                self.assertIn("verdict", event)
                self.assertIn("run", event)
                self.assertIn("head", event)

    def test_the_log_is_append_only_across_processes(self):
        with tempfile.TemporaryDirectory() as td:
            a = Store(pathlib.Path(td))
            a.log(kind="one")
            b = Store(pathlib.Path(td))
            b.log(kind="two")
            self.assertEqual([e["kind"] for e in Store(pathlib.Path(td)).events()],
                             ["one", "two"])


class RecoveryReadsTheIntentLedger(unittest.TestCase):
    """GOV-R2-03, second pass. `record_intent` wrote the ledger and NOTHING
    read it. A controller restarted after a crash went straight back to
    dispatch, so the single case the ledger exists for — the executor pushed,
    the process died before the push was recorded — re-ran the executor on top
    of its own unrecorded work.

    Recovery is now a reconciliation: go and look at the remote, and let what
    is actually there decide."""

    def _crashed_mid_execute(self, td, live_head):
        """The state a worker leaves behind when it dies after dispatching."""
        h = Harness(td, pinned_head=live_head)
        h.store.record_intent("T", "execute", head=H0, event_id="evt-crashed",
                              run_identity="executor-gone")
        return h

    def test_a_push_that_landed_is_not_dispatched_a_second_time(self):
        with tempfile.TemporaryDirectory() as td:
            h = self._crashed_mid_execute(td, live_head=H1)   # the branch moved
            out = h.ctl.step("T", "evt-after-restart")
            self.assertEqual(h.executor.calls, [],
                             "the executor was re-run on top of its own unrecorded push")
            self.assertEqual(h.store.task("T")["last_head"], H1)
            self.assertEqual(h.store.open_intents("T"), [])
            resolved = h.store.task("T")["resolved_intents"]
            self.assertEqual(resolved[0]["action"], "execute")
            self.assertEqual(resolved[0]["outcome"], "effect_confirmed")
            # Reconciliation puts the task where the push left it, so the same
            # step carries straight on into the REVIEW it was owed.
            self.assertIn(out["action"], ("FIX_PENDING", "COMPLETE",
                                          "CONDITIONS_PENDING", "NEEDS_INFORMATION"))

    def test_a_push_that_did_not_land_is_safe_to_redo(self):
        """The negative control. If reconciliation refused to dispatch whenever
        an intent was open, it would deadlock every crash instead of only the
        dangerous ones."""
        with tempfile.TemporaryDirectory() as td:
            h = self._crashed_mid_execute(td, live_head=H0)   # branch never moved
            out = h.ctl.step("T", "evt-after-restart")
            self.assertEqual(out["action"], "REVIEW_PENDING")
            self.assertEqual(len(h.executor.calls), 1, "safe work was not redone")
            self.assertEqual(
                [i["outcome"] for i in h.store.task("T")["resolved_intents"]],
                ["effect_refuted", "effect_confirmed"])

    def test_an_effect_nobody_can_observe_stops_instead_of_guessing(self):
        with tempfile.TemporaryDirectory() as td:
            h = self._crashed_mid_execute(td, live_head=H1)

            def unreachable(_repo, _branch):
                raise RuntimeError("git ls-remote: could not resolve host")

            h.ctl._head_of = unreachable
            out = h.ctl.step("T", "evt-after-restart")
            self.assertEqual(out["action"], "NEEDS_INFORMATION")
            self.assertEqual(h.executor.calls, [])
            self.assertEqual(h.store.task("T")["status"], "NEEDS_INFORMATION")
            self.assertEqual(
                [i["outcome"] for i in h.store.task("T")["resolved_intents"]],
                ["effect_unknown"],
                "an unobservable effect was filed as a known one")

    def test_step_actually_reads_the_ledger(self):
        """The dead-code check, stated as a test. This is the exact shape the
        finding was about: an API with tests and no caller."""
        import ast as _ast
        tree = _ast.parse((HERE / "controller.py").read_text())
        called = {n.func.attr for n in _ast.walk(tree)
                  if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)}
        self.assertIn("open_intents", called, "the intent ledger is still never read")

    def test_an_intent_cannot_be_closed_without_saying_what_was_observed(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            intent = store.record_intent("T", "execute", head=H0)
            with self.assertRaises(ValueError):
                store.commit_event_and_task("e", "T", close_intent_id=intent)
            with self.assertRaises(ValueError):
                store.close_intent("T", intent, outcome="done")
            self.assertTrue(store.open_intents("T"),
                            "a refused close still emptied the ledger")


class ADriveResendResumesInsteadOfStalling(unittest.TestCase):
    """GOV-R2-03. `drive` namespaces its steps as `<event>/<n>`, so a RESEND of
    the same firing meets `<event>/0` in the processed-event ledger. The loop
    treated that duplicate as a stop signal and returned having done nothing —
    in exactly the situation a resend exists for."""

    def test_a_resend_picks_up_where_the_first_delivery_stopped(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, decisions=("APPROVED",))
            first = h.ctl.drive("T", "delivery-1", max_steps=1)
            self.assertEqual([r["action"] for r in first], ["REVIEW_PENDING"])
            self.assertNotIn(h.store.task("T")["status"],
                             ("COMPLETE", "CONDITIONS_PENDING"))

            resend = h.ctl.drive("T", "delivery-1", max_steps=6)
            self.assertEqual(resend[0], {"action": "NOOP", "reason": "duplicate"},
                             "the already-run sub-step should be recognised")
            self.assertGreater(len(resend), 1,
                               "the resend stopped at the duplicate and did nothing")
            self.assertEqual(h.store.task("T")["status"], "COMPLETE")

    def test_a_real_noop_still_stops_the_loop(self):
        """The negative control: only a DUPLICATE is a reason to keep going.
        Skipping every NOOP would turn a task leased elsewhere into a spin."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.store.set_task("T", status="WAITING_OWNER")
            trail = h.ctl.drive("T", "delivery-9", max_steps=5)
            self.assertEqual(len(trail), 1)
            self.assertEqual(trail[0]["reason"], "terminal:WAITING_OWNER")


class TheLeaseFenceIsWiredAtEveryCommit(unittest.TestCase):
    """GOV-R2-02, second pass. `commit_event_and_task` grew require_owner and
    require_generation, and not one call site passed them: the check existed
    only in its own unit test. And when renewal failed, the runner was left to
    finish — burning the rest of its timeout, possibly pushing, while another
    worker already held the task."""

    def test_no_unfenced_state_commit_is_left_in_the_controller(self):
        import ast as _ast
        tree = _ast.parse((HERE / "controller.py").read_text())
        unfenced = []
        for node in _ast.walk(tree):
            if (isinstance(node, _ast.Call) and isinstance(node.func, _ast.Attribute)
                    and node.func.attr == "commit_event_and_task"):
                names = {kw.arg for kw in node.keywords}
                if "require_owner" not in names:
                    unfenced.append(node.lineno)
        self.assertEqual(unfenced, [],
                         f"unfenced commit_event_and_task at line(s) {unfenced}")

    @staticmethod
    def _take_over(store, task_id):
        """What actually happens: our lease EXPIRES — because renewal stopped,
        or the process was paused — and another worker legitimately claims the
        task. A stranger cannot simply seize a live lease, so a test that has
        one do so is testing `acquire`, not the fence."""
        state = store.read()
        store.commit(state["revision"],
                     lambda s: s["tasks"][task_id]["lease"].update(expires_at=0))
        store.acquire(task_id, "someone-else", ttl=600)

    def _thief(self, h):
        thief = FakeExecutor([H1])
        real_run = thief.run

        def steal_then_run(order):
            self._take_over(h.store, "T")
            return real_run(order)

        thief.run = steal_then_run
        return thief

    def test_a_lease_taken_over_mid_run_makes_the_commit_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.executor = self._thief(h)
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out, {"action": "NOOP", "reason": "lease_lost_mid_run"})
            self.assertNotEqual(h.store.task("T").get("status"), "REVIEW_PENDING")
            self.assertEqual(h.store.task("T")["lease"]["owner"], "someone-else",
                             "the discarded worker released the new holder's lease")

    def test_the_generation_is_what_distinguishes_a_returned_lease(self):
        """Owner alone is not enough: the same identity releasing and
        re-acquiring produces a lease that is NOT the one we were holding."""
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            store.acquire("T", "worker-a", ttl=600)
            first = store.lease_generation("T")
            store.release("T", "worker-a")
            store.acquire("T", "worker-a", ttl=600)
            self.assertNotEqual(store.lease_generation("T"), first)
            with self.assertRaises(ConcurrencyError):
                store.commit_event_and_task("e", "T", require_owner="worker-a",
                                            require_generation=first, status="X")

    def test_losing_the_lease_cancels_the_runner_there_and_then(self):
        cancelled = []

        class SlowRunner:
            def identity(self):
                return "slow-1"

            def cancel_current(self, grace_seconds=None):
                cancelled.append(True)
                self.stop.set()
                return "terminated"

            def run(self, order):
                self.stop = getattr(self, "stop", threading.Event())
                if not self.stop.wait(20):
                    raise AssertionError("the runner was never cancelled")
                raise RunnerError("slow-1: exited -15")

        runner = SlowRunner()
        runner.stop = threading.Event()
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, lease_seconds=3)
            h.ctl.executor = runner
            with patch.object(type(h.store), "renew",
                              side_effect=ConcurrencyError("lease gone")):
                out = h.ctl.step("T", "evt-1")
            self.assertTrue(cancelled, "the runner kept running after the lease was lost")
            self.assertEqual(out, {"action": "NOOP", "reason": "lease_lost_mid_run"})
            self.assertTrue(h.store.open_intents("T"),
                            "an unresolved external effect left no intent to reconcile")
            # The subtle half of the same bug: the child killed BECAUSE we lost
            # the lease exits non-zero, and recording that as FAILED writes a
            # result we are not entitled to write, under a plausible reason.
            self.assertNotEqual(h.store.task("T").get("status"), "FAILED")

    def test_the_commit_refuses_even_when_the_pre_check_passed(self):
        """`_fence` is a read taken before the commit, so it cannot cover the
        window between them. This removes the pre-check entirely and demands
        the commit itself still refuse — which is the whole reason
        require_owner exists."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.executor = self._thief(h)
            with patch.object(Controller, "_fence", lambda self, task_id: None):
                out = h.ctl.step("T", "evt-1")
            self.assertEqual(out, {"action": "NOOP", "reason": "lease_lost_at_commit"})
            self.assertNotEqual(h.store.task("T").get("status"), "REVIEW_PENDING")
            self.assertIn("commit_refused", [e["kind"] for e in h.store.events()])

    def test_release_never_takes_someone_elses_lease(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            store.acquire("T", "worker-a", ttl=600)
            with self.assertRaises(ConcurrencyError):
                store.release("T", "worker-b")
            self.assertEqual(store.task("T")["lease"]["owner"], "worker-a",
                             "a stranger's release deleted the live lease")

    def test_a_failed_release_does_not_replace_the_step_result(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            with patch.object(type(h.store), "release",
                              side_effect=ConcurrencyError("not ours")):
                out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "REVIEW_PENDING",
                             "cleanup replaced the answer the step had already reached")
            self.assertIn("release_skipped", [e["kind"] for e in h.store.events()])

    def test_a_runner_failure_asks_the_remote_before_calling_it_a_failure(self):
        """A failing executor may still have pushed. Recording FAILED without
        looking is a claim about the world made from an exit code."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)

            class Fails:
                def identity(self):
                    return "fails-1"

                def cancel_current(self, grace_seconds=None):
                    return "nothing_running"

                def run(self, order):
                    # It pushed, and then it died. The branch moves while the
                    # runner is running, not before it is dispatched.
                    h.pinned_head = H1
                    raise RunnerError("fails-1: exited 1")

            h.ctl.executor = Fails()
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "NEEDS_INFORMATION")
            self.assertEqual(h.store.task("T")["status"], "NEEDS_INFORMATION")
            self.assertEqual(
                [i["outcome"] for i in h.store.task("T")["resolved_intents"]],
                ["effect_confirmed"])

    def test_a_runner_failure_that_changed_nothing_is_still_a_failure(self):
        """The negative control for the test above."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)

            class Fails:
                def identity(self):
                    return "fails-1"

                def cancel_current(self, grace_seconds=None):
                    return "nothing_running"

                def run(self, order):
                    raise RunnerError("fails-1: exited 1")

            h.ctl.executor = Fails()
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "FAILED")
            self.assertEqual(
                [i["outcome"] for i in h.store.task("T")["resolved_intents"]],
                ["effect_refuted"])


class TheGuardIsCheckedBeforeItIsExecuted(unittest.TestCase):
    """GOV-R2-04. `build()` called load_guard at the TOP, before the policy pin
    was verified — and load_guard EXECUTES the module. Every check that
    followed was a check on code that had already run. Separately, the
    containment test compared a RAW config path while the loader was handed a
    resolved one, so a relative guard_path was checked as one file and executed
    as another."""

    def _policy_repo(self, tmp, guard_body):
        repo = pathlib.Path(tmp) / "policy"
        (repo / "governance").mkdir(parents=True)
        guard = repo / "governance" / "preflight.py"
        guard.write_text(guard_body)
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e")
        run = lambda *a: subprocess.run(a, cwd=repo, check=True, env=env,
                                        capture_output=True)
        run("git", "init", "--quiet", "-b", "main")
        run("git", "add", "-A")
        run("git", "commit", "--quiet", "-m", "policy")
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                             capture_output=True, text=True).stdout.strip()
        return repo, guard, sha

    def test_a_wrong_pin_refuses_before_the_guard_module_runs(self):
        import tick as _tick
        with tempfile.TemporaryDirectory() as td:
            marker = pathlib.Path(td) / "the-guard-ran"
            repo, guard, sha = self._policy_repo(
                td, f"import pathlib\npathlib.Path({str(marker)!r}).write_text('x')\n"
                    "def evaluate(order):\n    return {'action': 'NOOP'}\n")
            cfg = {"mode": "live", "guard_path": str(guard),
                   "policy_repo": str(repo), "policy_sha": "9" * 40,
                   "state_dir": str(pathlib.Path(td) / "s"),
                   "workspace_root": str(pathlib.Path(td) / "w"),
                   "controller_identity": "t", "run_budget": 1}
            with self.assertRaises(SystemExit):
                _tick.build(cfg, Store(pathlib.Path(td) / "s"))
            self.assertFalse(marker.exists(),
                             "the guard module was executed before its pin was checked")

    def test_a_modified_guard_is_refused_even_though_head_still_matches(self):
        import tick as _tick
        with tempfile.TemporaryDirectory() as td:
            repo, guard, sha = self._policy_repo(
                td, "def evaluate(order):\n    return {'action': 'NOOP'}\n")
            clean, why = _tick.guard_is_clean(repo, guard)
            self.assertTrue(clean, why)              # positive control first
            guard.write_text("def evaluate(order):\n"
                             "    return {'action': 'DISPATCH_ALLOWED'}\n")
            clean, why = _tick.guard_is_clean(repo, guard)
            self.assertFalse(clean, "an edited guard passed a check on HEAD alone")
            self.assertIn("modified or untracked", why)

    def test_an_untracked_guard_is_refused(self):
        import tick as _tick
        with tempfile.TemporaryDirectory() as td:
            repo, guard, sha = self._policy_repo(
                td, "def evaluate(order):\n    return {'action': 'NOOP'}\n")
            other = repo / "governance" / "preflight_new.py"
            other.write_text("def evaluate(order):\n    return {}\n")
            clean, why = _tick.guard_is_clean(repo, other)
            self.assertFalse(clean, "an untracked file was accepted as pinned policy")

    def test_a_guard_outside_the_pinned_checkout_is_refused(self):
        import tick as _tick
        with tempfile.TemporaryDirectory() as td:
            repo, guard, sha = self._policy_repo(
                td, "def evaluate(order):\n    return {'action': 'NOOP'}\n")
            outside = pathlib.Path(td) / "elsewhere.py"
            outside.write_text("def evaluate(order):\n    return {}\n")
            clean, why = _tick.guard_is_clean(repo, outside)
            self.assertFalse(clean)
            self.assertIn("outside", why)

    def test_a_relative_guard_path_works_from_a_cwd_outside_the_repository(self):
        """A trigger calls tick from wherever it happens to live. The shipped
        config's guard_path is relative, so if it resolved against the caller's
        cwd the whole thing would only ever work from the repo root — and the
        containment check would be comparing a different file from the one that
        gets executed."""
        with tempfile.TemporaryDirectory() as td:
            cfg = json.loads((HERE / "config.replay.json").read_text())
            self.assertFalse(pathlib.Path(cfg["guard_path"]).is_absolute(),
                             "the shipped config no longer exercises this")
            cfg["state_dir"] = str(pathlib.Path(td) / "state")
            cfg["stop_file"] = str(pathlib.Path(td) / "state" / "STOP")
            cfg_path = pathlib.Path(td) / "cfg.json"
            cfg_path.write_text(json.dumps(cfg))
            proc = subprocess.run(
                [sys.executable, str(HERE / "tick.py"), "--config", str(cfg_path),
                 "--task", "RELPATH", "--event", "e-1", "--drive"],
                cwd=td, capture_output=True, text=True, timeout=120)
            self.assertEqual(proc.returncode, 10,
                             f"tick did not run from an outside cwd: {proc.stderr[-800:]}")
            self.assertIn("COMPLETE", proc.stdout)

    def test_the_same_resolver_produces_the_checked_path_and_the_loaded_path(self):
        src = (HERE / "tick.py").read_text()
        self.assertNotIn('pathlib.Path(config["guard_path"])', src,
                         "tick still builds the guard path two different ways")
        self.assertEqual(src.count('resolve(config["guard_path"])'), 1,
                         "guard_path should be resolved once and reused")


class TheShippedTemplateIsDrivenAgainstTheRealCliEnvelope(unittest.TestCase):
    """GOV-R2-01. `parse_verdict` read the model's JSON at the ROOT of stdout.
    The CLI does not put it there: it prints its own result envelope and puts
    the model's text in `result`, as a STRING. Every adapter test in this file
    supplied a bare object, so the suite agreed with the code and both were
    wrong about the only shape that would ever have run in production.

    These drive the SHIPPED command template — the flags and the prompt exactly
    as config.live.example.json has them, with only the program replaced — over
    a real git clone, against the envelope recorded in
    evidence/cli_envelope_fixture.json. No model, no network, no credential."""

    FIXTURE = json.loads((HERE / "evidence" / "cli_envelope_fixture.json").read_text())

    def _origin(self, tmp):
        repo = pathlib.Path(tmp) / "origin"
        repo.mkdir()
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e")
        run = lambda *a: subprocess.run(a, cwd=repo, check=True, env=env,
                                        capture_output=True)
        run("git", "init", "--quiet", "-b", "main")
        (repo / "README").write_text("fixture\n")
        run("git", "add", "README")
        run("git", "commit", "--quiet", "-m", "fixture")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                              capture_output=True, text=True).stdout.strip()
        return repo, head

    def _stub_cli(self, tmp, envelope, name="claude-stub"):
        """Stands in for `claude`. Prints the envelope; records its own argv so
        the test can prove the shipped prompt actually reached the program."""
        stub = pathlib.Path(tmp) / name
        argv_log = pathlib.Path(tmp) / f"{name}.argv.json"
        stub.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys, pathlib\n"
            f"pathlib.Path({str(argv_log)!r}).write_text(json.dumps(sys.argv[1:]))\n"
            f"sys.stdout.write({json.dumps(json.dumps(envelope))})\n")
        stub.chmod(0o755)
        return stub, argv_log

    def _shipped_command(self, role, stub):
        cfg = json.loads((HERE / "config.live.example.json").read_text())
        command = list(cfg["runners"][role]["command"])
        self.assertEqual(command[0], "claude",
                         "the shipped template no longer starts with the CLI")
        command[0] = str(stub)                    # ONLY the program is replaced
        return cfg, command

    def _drive(self, tmp, role, envelope):
        repo, head = self._origin(tmp)
        stub, argv_log = self._stub_cli(tmp, envelope)
        cfg, command = self._shipped_command(role, stub)
        runner_cfg = dict(cfg["runners"][role], command=command, enabled=True,
                          identity_suffix="fixture")
        runner = runners.SubprocessRunner(role, runner_cfg,
                                          pathlib.Path(tmp) / "ws", role=role)
        order = {"task_id": "T", "head": head, "repo_url": str(repo),
                 "prompt_file": "PROMPT.md", "policy_sha": "p" * 40,
                 "phase": "execute" if role == "executor" else "review",
                 "run_identity": f"{role}-fixture", "goal": "g",
                 "deadline_seconds": 60, "deadline_at": time.time() + 120}
        return runner.run(order), json.loads(argv_log.read_text())

    def test_the_whole_path_from_the_shipped_template_to_a_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, argv = self._drive(
                tmp, "executor", self.FIXTURE["success_envelope_derived"])
            self.assertEqual(result, {"new_head": "a" * 40})
            joined = " ".join(argv)
            self.assertIn("--output-format", argv)
            self.assertIn("json", argv)
            self.assertIn("work_order.json", joined,
                          "the work order never reached the program's argv")
            self.assertIn("60 seconds", joined,
                          "the deadline was substituted nowhere the runner can see")
            self.assertNotIn("{head}", joined, "a placeholder shipped unsubstituted")

    def test_the_reviewer_half_of_the_same_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, argv = self._drive(
                tmp, "reviewer", self.FIXTURE["success_envelope_review_derived"])
            self.assertEqual(result["review"]["decision"], "APPROVED")
            self.assertIn("INDEPENDENT REVIEWER", " ".join(argv))

    def test_the_measured_error_envelope_is_refused(self):
        """The negative control, and the reason the fixture is kept at all."""
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RunnerError) as cm:
                self._drive(tmp, "executor",
                            self.FIXTURE["error_envelope_measured"])
            self.assertNotIn("Connection refused", str(cm.exception),
                             "the provider's error body was quoted back")

    def test_subtype_alone_would_have_accepted_that_failure(self):
        """Measured, not reasoned about: in a real failing run the CLI reports
        subtype='success' AND is_error=true at the same time. An adapter that
        gates on subtype accepts an API failure as a completed run."""
        measured = self.FIXTURE["error_envelope_measured"]
        self.assertEqual(measured["subtype"], "success")
        self.assertTrue(measured["is_error"])
        self.assertEqual(measured["total_cost_usd"], 0,
                         "the fixture was supposed to cost nothing to record")
        src = (HERE / "runners.py").read_text()
        self.assertIn('payload.get("is_error")', src,
                      "parse_verdict no longer looks at is_error")

    def test_prose_inside_a_valid_envelope_is_not_a_verdict(self):
        envelope = dict(self.FIXTURE["success_envelope_derived"],
                        result="Sure! I have pushed the commit for you.")
        with self.assertRaises(RunnerError) as cm:
            parse_verdict("executor", json.dumps(envelope))
        self.assertNotIn("Sure!", str(cm.exception))

    def test_an_envelope_with_no_text_result_is_not_a_verdict(self):
        envelope = dict(self.FIXTURE["success_envelope_derived"])
        envelope.pop("result")
        with self.assertRaises(RunnerError):
            parse_verdict("executor", json.dumps(envelope))
        envelope["result"] = {"new_head": "a" * 40}     # right data, wrong shape
        with self.assertRaises(RunnerError):
            parse_verdict("executor", json.dumps(envelope))

    def test_a_verdict_nested_in_an_envelope_still_has_to_be_well_formed(self):
        envelope = dict(self.FIXTURE["success_envelope_derived"],
                        result=json.dumps({"new_head": "not-a-sha"}))
        with self.assertRaises(RunnerError):
            parse_verdict("executor", json.dumps(envelope))

    def test_the_fixture_says_which_of_its_fields_were_measured(self):
        """A fixture that presents synthesised values as observations is worse
        than no fixture: it launders a guess into evidence."""
        prov = self.FIXTURE["_provenance"]
        self.assertEqual(prov["error_envelope_measured"]["evidence_ladder"],
                         "REPRODUCED")
        self.assertIn("SYNTHETIC",
                      prov["success_envelope_derived"]["evidence_ladder"])
        self.assertIn("result", prov["success_envelope_derived"]["not_measured"])
        self.assertNotIn("ANTHROPIC_API_KEY=", json.dumps(self.FIXTURE))



# ==========================================================================
# Package A (third bounded round, owner-authorised 2026-09-26):
# GOV-R2-02, GOV-R2-03, GOV-R2-05, P2 isolation baseline, P2 atomic writes.
# Each class names the finding it guards. Every test below was run against the
# pre-fix source (7de3043) and FAILED or ERRORED there; see the executor
# response for the command and the count.
# ==========================================================================

def _live_runner(tmp, **over):
    cfg = {"enabled": True, "command": ["true", "{prompt_file}", "{head}"],
           "timeout_seconds": 30, "terminate_grace_seconds": 1}
    cfg.update(over)
    return SubprocessRunner("executor", cfg, pathlib.Path(tmp))


def _order(tmp, deadline_in=60.0):
    return {"task_id": "T", "head": H1, "policy_sha": "p" * 40, "phase": "execute",
            "run_identity": "r", "prompt_file": "PROMPT.md", "repo_url": "unused",
            "deadline_at": time.time() + deadline_in}


class _PopenSpy:
    def __init__(self):
        self.calls = []

    def __call__(self, *a, **k):
        self.calls.append(a[0] if a else k.get("args"))
        raise AssertionError("Popen reached: a child was launched")


class LeaseLossBeforeLaunchStartsNothing(unittest.TestCase):
    """GOV-R2-02 (R4 P1). The lease can be lost while the runner is still
    cloning, when there is no child to kill. The token must stop the launch."""

    def test_a_cancel_during_the_clone_prevents_the_launch(self):
        with tempfile.TemporaryDirectory() as td:
            runner = _live_runner(td)
            token = threading.Event()
            runner.bind_cancellation(token)
            repo = pathlib.Path(td) / "ws" / "repo"
            repo.mkdir(parents=True)

            def clone_then_lose_lease(order, env):
                token.set()                   # lease monitor fires mid-clone
                return repo

            spy = _PopenSpy()
            with patch.object(runner, "_workspace", clone_then_lose_lease), \
                    patch.object(runners.subprocess, "Popen", spy):
                with self.assertRaises(runners.RunnerCancelled):
                    runner.run(_order(td))
            self.assertEqual(spy.calls, [], "a credentialed child was launched after cancel")

    def test_cancel_with_nothing_running_still_blocks_a_later_launch(self):
        """The old answer to this call was 'nothing_running', and the run then
        went on to Popen. The flag must outlive the call."""
        with tempfile.TemporaryDirectory() as td:
            runner = _live_runner(td)
            runner.bind_cancellation(threading.Event())
            self.assertEqual(runner.cancel_current(), "nothing_running")
            spy = _PopenSpy()
            with patch.object(runners.subprocess, "Popen", spy):
                with self.assertRaises(runners.RunnerCancelled):
                    runner.run(_order(td))
            self.assertEqual(spy.calls, [])

    def test_a_cancel_racing_the_launch_kills_the_child(self):
        """Cancel lands between the last check and `_current = proc`."""
        with tempfile.TemporaryDirectory() as td:
            runner = _live_runner(td, command=["sleep", "30"])
            token = threading.Event()
            runner.bind_cancellation(token)
            repo = pathlib.Path(td) / "ws" / "repo"
            repo.mkdir(parents=True)
            real_popen = subprocess.Popen
            launched = []

            def popen_then_cancel(*a, **k):
                proc = real_popen(*a, **k)
                launched.append(proc)
                token.set()
                return proc

            with patch.object(runner, "_workspace", lambda o, e: repo), \
                    patch.object(runners.subprocess, "Popen", popen_then_cancel):
                with self.assertRaises(runners.RunnerCancelled):
                    runner.run(_order(td))
            self.assertEqual(len(launched), 1)
            self.assertIsNotNone(launched[0].poll(), "the raced child is still running")

    def test_the_lease_monitor_sets_the_token_the_runner_sees(self):
        """End to end through Controller: renewal fails while the runner is in
        its preparation phase; the runner observes the cancellation."""
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, lease_seconds=3)
            seen = {}

            class Preparing(FakeExecutor):
                def run(self, order):
                    deadline = time.time() + 6
                    while time.time() < deadline and not self.cancellation_requested():
                        time.sleep(0.05)
                    seen["cancelled"] = self.cancellation_requested()
                    raise runners.RunnerCancelled("stopped before launch")

            h.ctl.executor = Preparing([H1])

            def renew_fails(*a, **k):
                raise ConcurrencyError("lease taken over")

            with patch.object(h.store, "renew", renew_fails):
                out = h.ctl.step("T", "evt-lease-lost")
            self.assertTrue(seen.get("cancelled"), "the token never reached the runner")
            self.assertEqual(out, {"action": "NOOP", "reason": "lease_lost_mid_run"})
            self.assertEqual(len(h.store.open_intents("T")), 1,
                             "the intent must stay open for reconciliation")


class NoLaunchAfterTheRoundDeadline(unittest.TestCase):
    """GOV-R2-05 (R4 P1). A deadline that expires during clone/checkout must
    stop the launch, not be enforced by killing a child after it started."""

    def test_deadline_spent_by_preparation_refuses_before_popen(self):
        with tempfile.TemporaryDirectory() as td:
            runner = _live_runner(td)
            repo = pathlib.Path(td) / "ws" / "repo"
            repo.mkdir(parents=True)

            def slow_clone(order, env):
                time.sleep(0.4)
                return repo

            spy = _PopenSpy()
            with patch.object(runner, "_workspace", slow_clone), \
                    patch.object(runners.subprocess, "Popen", spy):
                with self.assertRaises(RunnerError) as cm:
                    runner.run(_order(td, deadline_in=0.3))
            self.assertIn("launch", str(cm.exception))
            self.assertEqual(spy.calls, [], "a child was started after the round deadline")

    def test_less_than_a_second_left_is_not_worth_a_launch(self):
        with tempfile.TemporaryDirectory() as td:
            runner = _live_runner(td)
            repo = pathlib.Path(td) / "ws" / "repo"
            repo.mkdir(parents=True)
            spy = _PopenSpy()
            with patch.object(runner, "_workspace", lambda o, e: repo), \
                    patch.object(runners.subprocess, "Popen", spy):
                with self.assertRaises(RunnerError):
                    runner.run(_order(td, deadline_in=0.6))
            self.assertEqual(spy.calls, [])

    def test_positive_control_enough_time_does_launch(self):
        """Without this, a runner that never launches would pass both tests above."""
        with tempfile.TemporaryDirectory() as td:
            stub = pathlib.Path(td) / "stub.py"
            stub.write_text("import json;print(json.dumps({'new_head': '" + "a" * 40 + "'}))\n")
            runner = _live_runner(td, command=[sys.executable, str(stub)])
            repo = pathlib.Path(td) / "ws" / "repo"
            repo.mkdir(parents=True)
            with patch.object(runner, "_workspace", lambda o, e: repo):
                out = runner.run(_order(td, deadline_in=30))
            self.assertEqual(out["new_head"], "a" * 40)


class ABranchMoveIsNotThisWorkWithoutItsReceipt(unittest.TestCase):
    """GOV-R2-03 (R4 P1). An unrelated push to the same branch must not be
    recorded as this task's result."""

    def _crashed(self, td, live_head, receipted):
        h = Harness(td, pinned_head=live_head, receipted=receipted)
        intent = h.store.reserve_run_and_record_intent(
            "T", "execute", 1, head=H0, event_id="evt-crashed", run_identity="gone")
        return h, intent

    def test_somebody_elses_push_halts_instead_of_advancing(self):
        with tempfile.TemporaryDirectory() as td:
            h, _ = self._crashed(td, live_head=H1, receipted=set())
            out = h.ctl.step("T", "evt-after-restart")
            self.assertEqual(out["action"], "NEEDS_INFORMATION")
            self.assertEqual(h.executor.calls, [])
            self.assertNotEqual(h.store.task("T").get("status"), "REVIEW_PENDING")
            self.assertEqual(h.store.task("T").get("last_head"), H0,
                             "an unattributed head was adopted as this work")
            self.assertEqual([i["outcome"] for i in h.store.task("T")["resolved_intents"]],
                             ["effect_unknown"])

    def test_a_receipted_push_is_confirmed_with_the_intents_receipt(self):
        """Positive control, and the receipt asked about is this intent's."""
        with tempfile.TemporaryDirectory() as td:
            h, intent = self._crashed(td, live_head=H1, receipted={H1})
            h.ctl.step("T", "evt-after-restart")
            self.assertEqual(h.store.task("T")["resolved_intents"][0]["outcome"],
                             "effect_confirmed")
            self.assertIn((H0, H1, f"T/{intent}"), h.receipt_checks)

    def test_a_reported_head_without_the_receipt_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, receipted=set())
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out["action"], "FAILED")
            self.assertEqual(out["reason"], "reported_head_without_work_receipt")
            self.assertNotEqual(h.store.task("T").get("status"), "REVIEW_PENDING")

    def test_the_work_order_carries_the_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            seen = {}

            class Recording(FakeExecutor):
                def run(self, order):
                    seen.update(order)
                    return super().run(order)

            h.ctl.executor = Recording([H1])
            h.ctl.step("T", "evt-1")
            intent_id = h.store.task("T")["resolved_intents"][0]["intent_id"]
            self.assertEqual(seen.get("work_receipt"), f"T/{intent_id}")
            self.assertIn("work_receipt", SubprocessRunner.WORK_ORDER_FIELDS)

    def test_the_live_receipt_check_against_a_real_git_history(self):
        """No stub: a local repository with real commits and trailers."""
        from controller import commits_carry_receipt
        with tempfile.TemporaryDirectory() as td:
            src = pathlib.Path(td) / "src"
            src.mkdir()
            env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x.invalid",
                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x.invalid"}

            def git(*a):
                return subprocess.run(["git", *a], cwd=src, env=env, check=True,
                                      capture_output=True, text=True).stdout.strip()

            git("init", "-q", "-b", "work")
            git("commit", "-q", "--allow-empty", "-m", "base")
            base = git("rev-parse", "HEAD")
            git("commit", "-q", "--allow-empty", "-m", "ours\n\nATK-Work-Receipt: T/abc")
            ours = git("rev-parse", "HEAD")
            git("commit", "-q", "--allow-empty", "-m", "someone else")
            mixed = git("rev-parse", "HEAD")
            url = src.as_uri()
            check = lambda live, rec, w: commits_carry_receipt(  # noqa: E731
                url, "work", base, live, rec, pathlib.Path(td) / w)
            self.assertIs(check(ours, "T/abc", "v1"), True)
            self.assertIs(check(ours, "T/other", "v2"), False, "wrong receipt accepted")
            self.assertIs(check(mixed, "T/abc", "v3"), False,
                          "a foreign commit on top was accepted as this work")
            self.assertIs(check(base, "T/abc", "v4"), False, "an empty range was accepted")
            self.assertIsNone(check("f" * 40, "T/abc", "v5"), "an unknown commit was decided")


class IsolationProbesNeedAnUnwrappedBaseline(unittest.TestCase):
    """P2 (R4). A probe that fails even without the wrap proves nothing about
    the wrap; it used to be recorded as the property being provided."""

    def _always_failing_wrap(self, backend, cmd):
        return ["sh", "-c", "exit 1"]

    def test_a_probe_that_fails_unwrapped_is_unknown_not_denied(self):
        with patch.object(runners, "isolate_command", self._always_failing_wrap):
            self.assertIsNone(runners._denies("x", ["false"]),
                              "a host-side failure was credited to the boundary")

    def test_baseline_ok_and_wrapped_fails_is_denied(self):
        with patch.object(runners, "isolate_command", self._always_failing_wrap):
            self.assertIs(runners._denies("x", ["true"]), True)

    def test_both_succeed_is_not_denied(self):
        with patch.object(runners, "isolate_command", lambda b, c: list(c)):
            self.assertIs(runners._denies("x", ["true"]), False)

    def test_an_unmeasurable_property_does_not_satisfy_a_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(runners, "working_container_backend", lambda *a, **k: "unshare"), \
                    patch.object(runners, "measure_backend_properties",
                                 lambda b: {"network_denied": None, "host_fs_denied": True,
                                            "source_readonly": True}):
                with self.assertRaises(IsolationUnavailable):
                    SubprocessRunner("pr_tests", {"enabled": True, "command": ["true"],
                                                  "isolation_level": "container"},
                                     pathlib.Path(tmp), role="pr_tests")


class SpendIntentAndDeadlineAreOneFencedWrite(unittest.TestCase):
    """P2 (R4). Reserving a run and recording its intent were two unfenced
    commits; the round deadline was the one task write without the lease."""

    def test_reservation_and_intent_land_in_one_revision(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(pathlib.Path(td))
            before = store.read()["revision"]
            intent = store.reserve_run_and_record_intent("T", "execute", 1, head=H0)
            state = store.read()
            self.assertEqual(state["revision"], before + 1, "two commits, not one")
            self.assertEqual(state["spend"], 1)
            self.assertEqual([i["intent_id"] for i in store.open_intents("T")], [intent])

    def test_a_worker_that_lost_the_lease_spends_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            real_ask = h.ctl._ask

            def ask_then_lose_lease(order):
                verdict = real_ask(order)
                if order["phase"] == "execute":
                    # another worker takes the task after the guard said yes
                    h.store.commit(h.store.read()["revision"], lambda s: s["tasks"]["T"]
                                   .__setitem__("lease", {"owner": "thief", "generation": 99,
                                                          "expires_at": time.time() + 600}))
                return verdict

            h.ctl._ask = ask_then_lose_lease
            spend_before = h.store.spend()
            out = h.ctl.step("T", "evt-1")
            self.assertEqual(out, {"action": "NOOP", "reason": "lease_lost_before_dispatch"})
            self.assertEqual(h.store.spend(), spend_before, "budget spent without the lease")
            self.assertEqual(h.store.open_intents("T"), [])
            self.assertEqual(h.executor.calls, [], "dispatched without the lease")

    def test_the_round_deadline_is_not_written_without_the_lease(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.store.acquire("T", "someone-else", 600)
            h.ctl._generation = 1             # we believe we hold generation 1
            with self.assertRaises(ConcurrencyError):
                h.ctl._round_deadline_at("T")
            self.assertNotIn("round_deadline", h.store.task("T"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

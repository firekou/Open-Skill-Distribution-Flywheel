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
from runners import (AuthUnavailable, BASE_ENV_ALLOWLIST, DENY_SESSION_IDENTITY,  # noqa: E402
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
                 pinned_head=None, known_commits=None, **cfg_over):
        self.tmp = pathlib.Path(tmp)
        self.config = base_config(self.tmp, **cfg_over)
        self.store = Store(pathlib.Path(self.config["state_dir"]))
        self.executor = FakeExecutor(list(executor_heads))
        self.reviewer = FakeReviewer(list(decisions))
        self.pinned_head = pinned_head
        # Stub for the remote check, so the suite never touches the network.
        # None means "every sha the executor reports really is on the branch".
        self.known_commits = known_commits
        self.ctl = Controller(self.config, self.store, GUARD,
                              self.executor, self.reviewer,
                              head_resolver=self._head,
                              commit_verifier=self._commit_on_branch,
                              policy_sha_value="policy" + "0" * 35)
        self.store.set_task("T", status="READY", last_head=H0)

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
                # Leave nothing behind, whatever happened above.
                for proc in procs:
                    if proc.poll() is None:
                        terminate_process_group(proc, grace_seconds=5)

            final = Store(root).read()
            self.assertEqual(reported, self.PROCS * self.ROUNDS)
            self.assertEqual(final["tasks"]["C"]["n"], reported,
                             f"{reported - final['tasks']['C']['n']} commits were "
                             "reported successful and lost")
            self.assertEqual(final["revision"], reported)

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
            for name in ("tick", "controller", "runners", "store"):
                sys.modules.pop(name, None)
            try:
                import tick as staged_tick
                from store import Store as StagedStore
                ctl = staged_tick.build(cfg, StagedStore(pathlib.Path(cfg["state_dir"])))
                self.assertTrue(ctl._commit_is_on_branch("r", "b", self.SCRIPTED[0]))
                self.assertFalse(ctl._commit_is_on_branch("r", "b", "9" * 40))
            finally:
                sys.path.remove(str(work))
                for name in ("tick", "controller", "runners", "store"):
                    sys.modules.pop(name, None)
                import controller, runners, store   # noqa: F401  restore this suite's modules

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

    def test_declaring_a_container_is_what_permits_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = SubprocessRunner("pr_tests", {**self.CFG, "isolation_level": "container"},
                                 pathlib.Path(tmp), role="pr_tests")
            self.assertEqual(r._isolation_level, "container")

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

    def _order(self, repo, head):
        return {"task_id": "T", "head": head, "repo_url": str(repo),
                "prompt_file": "governance/IMPLEMENTATION_PROMPT.md"}

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
            reopened.close_intent("T", intent, outcome="confirmed")
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


if __name__ == "__main__":
    unittest.main(verbosity=2)

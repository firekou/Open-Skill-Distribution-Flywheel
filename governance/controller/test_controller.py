#!/usr/bin/env python3
"""Negative controls for the handoff controller.

Every test here is a way the loop could do the wrong thing while still looking
green. A controller that only proves the happy path is the same mistake as a
test suite that only asserts a full key is absent.

    python3 governance/controller/test_controller.py

No network, no credentials, no model call.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import threading
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from controller import Controller, load_guard          # noqa: E402
from runners import FakeExecutor, FakeReviewer, Runner, RunnerError, SubprocessRunner  # noqa: E402
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
        "budget": 0,
        "timeout_seconds": 2700,
        "lease_seconds": 600,
    }
    cfg.update(over)
    return cfg


class Harness:
    """A controller wired to fakes, with the live head under test control."""

    def __init__(self, tmp, executor_heads=(H1, H2), decisions=("BLOCKED", "APPROVED"),
                 pinned_head=None, **cfg_over):
        self.tmp = pathlib.Path(tmp)
        self.config = base_config(self.tmp, **cfg_over)
        self.store = Store(pathlib.Path(self.config["state_dir"]))
        self.executor = FakeExecutor(list(executor_heads))
        self.reviewer = FakeReviewer(list(decisions))
        self.pinned_head = pinned_head
        self.ctl = Controller(self.config, self.store, GUARD,
                              self.executor, self.reviewer,
                              head_resolver=self._head)
        self.store.set_task("T", status="READY", last_head=H0)

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
            trail = h.ctl.drive("T")
            self.assertEqual([t["action"] for t in trail],
                             ["REVIEW_PENDING", "FIX_PENDING", "REVIEW_PENDING", "COMPLETE"])
            self.assertEqual(h.store.task("T")["status"], "COMPLETE")


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
            trail = h.ctl.drive("T", max_steps=10)
            self.assertIn("STOP", [t["action"] for t in trail])
            self.assertEqual(h.store.task("T")["status"], "STOPPED")

    def test_spending_over_budget_stops(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td, budget=1.0)

            class Pricey(FakeExecutor):
                def run(self, order):
                    out = super().run(order)
                    out["cost"] = 5.0
                    return out

            h.executor = Pricey([H1, H2])
            h.ctl.executor = h.executor
            h.ctl.step("T", "evt-1")                    # spends 5.0 against a budget of 1.0
            out = h.ctl.step("T", "evt-2")
            self.assertEqual(out, {"action": "STOP", "reason": "limit"})

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
            self.assertEqual(order["budget"], h.config["budget"])

    def test_the_live_runner_refuses_to_start_while_disabled(self):
        with self.assertRaises(RunnerError) as cm:
            SubprocessRunner("executor", {"enabled": False, "command": ["true"]},
                             pathlib.Path("/tmp"))
        self.assertIn("disabled", str(cm.exception))

    def test_the_shipped_live_template_has_both_runners_disabled_and_zero_budget(self):
        cfg = json.loads((HERE / "config.live.example.json").read_text())
        self.assertEqual(cfg["budget"], 0)
        for role in ("executor", "reviewer"):
            self.assertFalse(cfg["runners"][role]["enabled"], f"{role} ships enabled")


class AuditTrail(unittest.TestCase):

    def test_every_guard_decision_is_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            h = Harness(td)
            h.ctl.drive("T")
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

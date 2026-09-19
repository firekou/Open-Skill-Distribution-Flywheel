import copy
import unittest
from preflight import evaluate

def event():
    return dict(task_id="demo", head="a"*40, live_head="a"*40, phase="execute",
                event_id="demo:a:execute:1", seen_events=[], revision=1,
                expected_revision=1, stopped=False, authorized=True,
                run_identity="executor-run", executor_identity="executor-run",
                attempt=0, max_attempts=2, cost=0, budget=0, elapsed=0, timeout=60)

class GuardTests(unittest.TestCase):
    def test_execute_allowed(self):
        self.assertEqual(evaluate(event())["action"], "DISPATCH_ALLOWED")

    def test_independent_review_and_fix_cycle(self):
        e=event(); e.update(phase="accept_review", run_identity="reviewer-run")
        e["review"]=dict(head=e["head"], reviewer="reviewer-run",
                         evidence=["record.json"], decision="BLOCKED")
        self.assertEqual(evaluate(e)["action"], "FIX_PENDING")
        e["review"]["decision"]="APPROVED"
        self.assertEqual(evaluate(e)["action"], "COMPLETE")
        e["review"]["decision"]="APPROVED_WITH_CONDITIONS"
        self.assertEqual(evaluate(e)["action"], "CONDITIONS_PENDING")

    def test_boundaries(self):
        cases=[
          (dict(head="b"*40),"stale_head"),
          (dict(expected_revision=2),"stale_state"),
          (dict(phase="review"),"self_review"),
          (dict(phase="merge"),"unknown_or_external_action"),
          (dict(authorized=False),"outside_authority"),
          (dict(stopped=True),"operator_stop"),
          (dict(cost=1),"limit"),
          (dict(elapsed=60),"limit"),
          (dict(attempt=2),"limit"),
          (dict(budget=float("nan")),"bad_limit"),
          (dict(authorized="true"),"bad_flag"),
          (dict(seen_events=["demo:a:execute:1"]),"duplicate")]
        for change, reason in cases:
            with self.subTest(reason=reason):
                e=event(); e.update(change)
                self.assertEqual(evaluate(e)["reason"],reason)

    def test_reject_bad_review_binding_and_missing_evidence(self):
        e=event();e.update(phase="accept_review",run_identity="reviewer")
        e["review"]=dict(head="b"*40,reviewer="reviewer",decision="APPROVED",evidence=["x"])
        self.assertEqual(evaluate(e)["reason"],"review_binding")
        e["review"]["head"]=e["head"];e["review"]["evidence"]=[]
        self.assertEqual(evaluate(e)["reason"],"missing_evidence")

    def test_missing_contract(self):
        self.assertEqual(evaluate({})["action"],"REJECT")
if __name__=="__main__":
    unittest.main(verbosity=2)

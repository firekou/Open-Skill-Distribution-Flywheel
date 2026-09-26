#!/usr/bin/env python3
"""Negative controls for package A (third bounded round).

For each finding, copy the controller to a scratch directory, undo ONE fix,
and run the test class that guards it. Every mutant must make its class fail;
the unmutated copy must pass. A test that stays green when its fix is removed
is decoration, not a control.

    python3 governance/controller/evidence/mutate_package_a.py

No network, no credentials, no model call.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent          # governance/controller
GOV = HERE.parent

MUTANTS = [
    ("GOV-R2-02 token ignored", "runners.py",
     "        return token is not None and token.is_set()",
     "        return False",
     "LeaseLossBeforeLaunchStartsNothing"),
    ("GOV-R2-02 monitor does not set token", "controller.py",
     "                    if token is not None:\n                        token.set()",
     "                    pass",
     "LeaseLossBeforeLaunchStartsNothing.test_the_lease_monitor_sets_the_token_the_runner_sees"),
    ("GOV-R2-05 no deadline check at launch", "runners.py",
     '        left = self._require_time(order, "the launch")\n'
     '        if left < self.MIN_LAUNCH_SECONDS:',
     '        left = max(self._remaining(order), 0.001)\n'
     '        if False:',
     "NoLaunchAfterTheRoundDeadline"),
    ("GOV-R2-03 any branch move confirms (old rule)", "controller.py",
     "        if not receipt:\n            return \"effect_unknown\", live",
     "        return \"effect_confirmed\", live",
     "ABranchMoveIsNotThisWorkWithoutItsReceipt"),
    ("GOV-R2-03 reported head not receipt-checked", "controller.py",
     "        if attributed is not True:",
     "        if False:",
     "ABranchMoveIsNotThisWorkWithoutItsReceipt.test_a_reported_head_without_the_receipt_is_not_accepted"),
    ("P2 probe without baseline (old rule)", "runners.py",
     "    if _run_probe(list(cmd), cwd, timeout) != 0:\n        return None",
     "    pass",
     "IsolationProbesNeedAnUnwrappedBaseline"),
    ("P2 reservation not fenced", "controller.py",
     '                task_id, "execute", 1, require_owner=self.owner,',
     '                task_id, "execute", 1, require_owner=None,',
     "SpendIntentAndDeadlineAreOneFencedWrite.test_a_worker_that_lost_the_lease_spends_nothing"),
    ("P2 round deadline not fenced", "controller.py",
     "            self.store.set_task(task_id, require_owner=self.owner,\n"
     "                                require_generation=self._generation,\n"
     "                                round_deadline=deadline)",
     "            self.store.set_task(task_id, round_deadline=deadline)",
     "SpendIntentAndDeadlineAreOneFencedWrite.test_the_round_deadline_is_not_written_without_the_lease"),
]


def run_tests(root: pathlib.Path, target: str) -> int:
    return subprocess.run(
        [sys.executable, str(root / "controller" / "test_controller.py"), target],
        capture_output=True, text=True, timeout=300).returncode


def main() -> int:
    bad = 0
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td) / "gov"
        shutil.copytree(GOV, base, ignore=shutil.ignore_patterns("__pycache__", "state*"))
        classes = sorted({m[4].split(".")[0] for m in MUTANTS})
        for cls in classes:
            rc = run_tests(base, cls)
            print(f"unmutated  {cls:48s} exit={rc} {'PASS' if rc == 0 else 'UNEXPECTED FAIL'}")
            bad += rc != 0
        for name, fname, old, new, target in MUTANTS:
            work = pathlib.Path(td) / "m"
            if work.exists():
                shutil.rmtree(work)
            shutil.copytree(base, work)
            f = work / "controller" / fname
            text = f.read_text(encoding="utf-8")
            if text.count(old) != 1:
                print(f"MUTANT NOT APPLIED  {name}: pattern found {text.count(old)} times")
                bad += 1
                continue
            f.write_text(text.replace(old, new), encoding="utf-8")
            rc = run_tests(work, target)
            caught = rc != 0
            print(f"mutant     {name:48s} exit={rc} {'CAUGHT' if caught else 'SURVIVED'}")
            bad += not caught
    print(f"\n{len(MUTANTS)} mutants; {'all caught' if bad == 0 else f'{bad} problem(s)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

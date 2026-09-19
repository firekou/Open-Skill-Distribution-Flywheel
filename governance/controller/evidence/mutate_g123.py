#!/usr/bin/env python3
"""Mutation harness: break one guarantee at a time, demand the suite go red.

A test suite that stays green while the code is deliberately broken is not
testing that code. Each entry below is a real defect this round fixed; the
suite must catch every one.
"""
import pathlib, shutil, subprocess, sys, tempfile

SRC = pathlib.Path("/home/user/Open-Skill-Distribution-Flywheel/governance/controller")
GOV = pathlib.Path("/home/user/Open-Skill-Distribution-Flywheel/governance")

MUTANTS = [
    ("runner inherits the whole parent env", "runners.py",
     'source = os.environ if parent is None else parent',
     'source = os.environ if parent is None else parent\n    return dict(source)'),
    ("an unknown role silently defaults", "runners.py",
     'raise RunnerError(f"unknown runner role {role!r}")',
     'return dict(parent or os.environ)'),
    ("reviewer / pr_tests receive the write token", "runners.py",
     'if name in DENY_ALWAYS and role != "executor":\n            continue',
     'if False:\n            continue'),
    ("a review with no evidence is accepted", "runners.py",
     'raise RunnerError("reviewer: review cites no evidence")',
     'pass'),
    ("a malformed new_head is accepted", "runners.py",
     'raise RunnerError("executor: new_head is missing or not a full commit sha")',
     'pass'),
    ("a phantom head is never verified", "controller.py",
     'if not self._commit_is_on_branch(',
     'if False and not self._commit_is_on_branch('),
    ("the work order drops the policy sha", "controller.py",
     '"policy_sha": self.policy_sha,',
     '"policy_sha_removed": self.policy_sha,'),
    ("missing auth falls through instead of BLOCKED_ACCESS", "controller.py",
     'except AuthUnavailable as exc:',
     'except _NeverRaised as exc:'),
    ("an expired holder can still renew", "store.py",
     'if lease["expires_at"] <= now:',
     'if False:'),
    ("drive renumbers steps from zero on every firing", "controller.py",
     'result = self.step(task_id, f"{event_id}/{n}")',
     'result = self.step(task_id, f"evt-{task_id}-{n}")'),
    ("tick invents an event id from the state revision", "tick.py",
     'results = [ctl.step(args.task, args.event)]',
     'results = [ctl.step(args.task, args.event or f"{args.task}-{store.read()[chr(39)+chr(39)] if False else store.read()[\'revision\']}")]'),
    ("step accepts an event id nothing stable produced", "controller.py",
     'if not isinstance(event_id, str) or not event_id.strip():\n            raise ValueError(\n',
     'if False:\n            raise ValueError(\n'),
    ("anyone can renew anyone's lease", "store.py",
     'if not lease or lease["owner"] != owner:\n            raise ConcurrencyError(f"task {task_id} is not leased by {owner}")\n        if lease["expires_at"] <= now:',
     'if lease["expires_at"] <= now:'),
]

def run(workdir):
    return subprocess.run([sys.executable, "-m", "unittest", "test_controller"],
                          cwd=workdir, capture_output=True, text=True)

def stage(tmp):
    work = pathlib.Path(tmp) / "governance" / "controller"
    work.parent.mkdir(parents=True)
    shutil.copytree(SRC, work, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(GOV / "preflight.py", work.parent / "preflight.py")
    return work

results = []
with tempfile.TemporaryDirectory() as tmp:
    work = stage(tmp)
    base = run(work)
    print("baseline:", "OK" if base.returncode == 0 else "FAILED")
    if base.returncode != 0:
        print(base.stderr[-3000:]); sys.exit(1)

for label, fname, old, new in MUTANTS:
    with tempfile.TemporaryDirectory() as tmp:
        work = stage(tmp)
        f = work / fname
        text = f.read_text()
        if old not in text:
            results.append((label, "NOT APPLIED — anchor missing")); continue
        f.write_text(text.replace(old, new, 1))
        r = run(work)
        tail = [l for l in r.stderr.strip().splitlines() if l.startswith(("OK", "FAILED"))]
        results.append((label, tail[-1] if tail else f"exit {r.returncode}"))

print()
caught = 0
for label, outcome in results:
    mark = "caught " if outcome.startswith("FAILED") else "SURVIVED"
    caught += outcome.startswith("FAILED")
    print(f"  [{mark}] {label:52s} -> {outcome}")
print(f"\n{caught}/{len(MUTANTS)} mutants caught")

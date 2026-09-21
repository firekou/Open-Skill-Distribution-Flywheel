#!/usr/bin/env python3
"""Mutation harness: break one guarantee at a time, demand the suite go red.

A test suite that stays green while the code is deliberately broken is not
testing that code. Each entry below is a real defect this round fixed; the
suite must catch every one.
"""
import contextlib, os, pathlib, shutil, signal, subprocess, sys, tempfile

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
    ("the replay verifier says yes to anything", "controller.py",
     "return sha in allowed",
     "return True"),
    ("replay.py loses its commit verifier", "replay.py",
     "commit_verifier=scripted_commit_verifier(",
     "commit_verifier_unused=scripted_commit_verifier("),
    ("tick replay mode loses its commit verifier", "tick.py",
     "commit_verifier=scripted_commit_verifier(",
     "commit_verifier_unused=scripted_commit_verifier("),
    ("every writer shares one temp file name", "store.py",
     'tmp = self.state_path.with_name(f"state.{os.getpid()}.{uuid.uuid4().hex}.tmp")',
     'tmp = self.state_path.with_suffix(".tmp")'),
    ("the compare-and-swap is not held under a lock", "store.py",
     "        with self._exclusive():\n            state = self.read()",
     "        if True:\n            state = self.read()"),
    ("the lock outlives a failed commit", "store.py",
     """        with open(self.lock_path, "a+b") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)""",
     """        handle = open(self.lock_path, "a+b")
        self._leaked = getattr(self, "_leaked", []) + [handle]
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)"""),
    ("the runner is not started in its own process group", "runners.py",
     "text=True, env=env, start_new_session=True)",
     "text=True, env=env)"),
    ("terminate only signals, never confirms", "runners.py",
     "        os.killpg(pgid, signal.SIGKILL)",
     "        os.killpg(pgid, 0)"),
    ("cancelling one task is treated as stopping everything", "controller.py",
     'return pathlib.Path(self.config["stop_file"]).with_name(f"CANCEL-{task_id}")',
     'return pathlib.Path(self.config["stop_file"])'),
    ("the per-task cancel checkpoint is skipped", "controller.py",
     "            if self._cancelled(task_id):",
     "            if False:"),
    ("absence of an env credential blocks again (the old false negative)", "runners.py",
     '        state = credential_state(self.role, parent)\n        if state == "declared_unavailable":',
     '        state = credential_state(self.role, parent)\n        if state != "env_credential":'),
    ("untrusted pr_tests runs without a declared container", "runners.py",
     '        if self.role in ROLES_REQUIRING_REAL_ISOLATION and level != "container":',
     '        if False:'),
    ("the caller's session id is allowed through", "runners.py",
     '           if k in source and k not in DENY_SESSION_IDENTITY}',
     '           if k in source}'),
    ("anyone can renew anyone's lease", "store.py",
     'if not lease or lease["owner"] != owner:\n            raise ConcurrencyError(f"task {task_id} is not leased by {owner}")\n        if lease["expires_at"] <= now:',
     'if lease["expires_at"] <= now:'),
]

SUITE_TIMEOUT = 150       # a healthy suite is ~8s; a mutant that exceeds this hung


def run(workdir):
    """Run the suite under a deadline, in its own process group.

    A mutant is allowed to make the suite fail; it is not allowed to make the
    harness wait forever. Anything that hangs is reported as a hang, and the
    whole group is killed so nothing is left blocked on a lock afterwards.
    """
    proc = subprocess.Popen([sys.executable, "-m", "unittest", "test_controller"],
                            cwd=workdir, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=SUITE_TIMEOUT)
        return subprocess.CompletedProcess(proc.args, proc.returncode, out, err)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        with contextlib.suppress(subprocess.TimeoutExpired):
            proc.communicate(timeout=10)
        return subprocess.CompletedProcess(proc.args, -1, "",
                                           f"HUNG: no result in {SUITE_TIMEOUT}s")

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
        tail = [l for l in r.stderr.strip().splitlines() if l.startswith(("OK", "FAILED", "HUNG"))]
        results.append((label, tail[-1] if tail else f"exit {r.returncode}"))

print()
caught = hung = 0
for label, outcome in results:
    # A hang is NOT a catch. The suite going red is the result being demanded;
    # a mutant that makes it wait forever tells us about the harness, not about
    # the guarantee, so it is reported on its own rather than counted as a pass.
    if outcome.startswith("FAILED"):
        mark, caught = "caught  ", caught + 1
    elif outcome.startswith("HUNG"):
        mark, hung = "HUNG    ", hung + 1
    else:
        mark = "SURVIVED"
    print(f"  [{mark}] {label:52s} -> {outcome}")
print(f"\n{caught}/{len(MUTANTS)} mutants caught"
      + (f", {hung} HUNG (harness deadline, not a result)" if hung else ""))

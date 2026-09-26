#!/usr/bin/env python3
"""Recovery, driven end to end rather than asserted about (GOV-R2-03).

Four situations a controller that died mid-dispatch can be restarted into.
The point of the ledger is that these four get FOUR different answers; before
this round they all got the same one — dispatch again.

No network, no model, no credential: the remote is a stub whose answer is the
variable under test.
"""
import pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from controller import Controller, load_guard          # noqa: E402
from runners import FakeExecutor, FakeReviewer         # noqa: E402
from store import Store                                # noqa: E402

GUARD = load_guard(HERE.parent.parent / "preflight.py")
H0, H1 = "0" * 40, "1" * 40


def build(tmp, live_head, unreachable=False, follow_task=False):
    cfg = {"mode": "replay", "controller_identity": "probe",
           "repo_url": "https://example.invalid/r", "branch": "work",
           "prompt_file": "P.md", "guard_path": str(HERE.parent.parent / "preflight.py"),
           "state_dir": str(pathlib.Path(tmp) / "s"),
           "stop_file": str(pathlib.Path(tmp) / "STOP"),
           "authorized_phases": ["execute", "review", "accept_review"],
           "max_attempts": 2, "run_budget": 8,
           "timeout_seconds": 2700, "lease_seconds": 600}
    store = Store(pathlib.Path(cfg["state_dir"]))
    executor = FakeExecutor([H1])
    holder = {"head": live_head}

    def head(_r, _b):
        if unreachable:
            raise RuntimeError("git ls-remote: could not resolve host")
        if follow_task:
            # A branch that moves when the executor pushes, which is what a
            # real remote does and what the resend case needs.
            return store.task("T").get("last_head", holder["head"])
        return holder["head"]

    ctl = Controller(cfg, store, GUARD, executor, FakeReviewer(["APPROVED"]),
                     head_resolver=head, commit_verifier=lambda *_a: True,
                     policy_sha_value="p" * 40)
    store.set_task("T", status="READY", last_head=H0)
    return ctl, store, executor


def case(name, live_head, unreachable=False):
    with tempfile.TemporaryDirectory() as tmp:
        ctl, store, executor = build(tmp, live_head, unreachable)
        # what a worker leaves behind when it dies after dispatching
        store.record_intent("T", "execute", head=H0, event_id="evt-crashed",
                            run_identity="executor-gone")
        out = ctl.step("T", "evt-after-restart")
        task = store.task("T")
        print(f"\n## {name}")
        print(f"  remote says head is : "
              f"{'UNREACHABLE' if unreachable else live_head[:12]}")
        print(f"  executor re-run     : {len(executor.calls)} time(s)")
        print(f"  intent outcome      : "
              f"{[i['outcome'] for i in task.get('resolved_intents', [])]}")
        print(f"  task status         : {task.get('status')}")
        print(f"  step returned       : {out}")


def resend():
    with tempfile.TemporaryDirectory() as tmp:
        ctl, store, _ = build(tmp, H0, follow_task=True)
        first = ctl.drive("T", "delivery-1", max_steps=1)     # delivery dies early
        print("\n## a resend of a drive that only got partway")
        print(f"  first delivery      : {[r['action'] for r in first]}")
        print(f"  status after it     : {store.task('T').get('status')}")
        again = ctl.drive("T", "delivery-1", max_steps=6)     # SAME event id
        print(f"  resend              : {[r['action'] for r in again]}")
        print(f"  status after resend : {store.task('T').get('status')}")


print("# recovery: four crashes, four different answers")
case("the push LANDED  -> do not run the executor again", H1)
case("the push did NOT land -> safe to redo", H0)
case("the remote cannot be asked -> stop, do not guess", H1, unreachable=True)
resend()
print("\nNo model ran. No credential was read. The only variable is what the "
      "remote was made to say.")

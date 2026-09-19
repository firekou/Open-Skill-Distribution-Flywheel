#!/usr/bin/env python3
"""One command, one start: the whole handoff runs with nobody in between.

    python3 governance/controller/replay.py

Produces the transcript in governance/controller/evidence/replay.txt.

What this proves: the CONTROLLER sequences execute -> independent review ->
required fix -> new SHA -> review -> close, obeys the trusted guard at every
step, and keeps a replayable record.

What it does NOT prove: that an AI did any real work. The runners here are
scripted test doubles with no model call and no network. That is why the result
is labelled REPLAY_VERIFIED and never ACTIVE.
"""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))

from controller import Controller, load_guard   # noqa: E402
from runners import FakeExecutor, FakeReviewer  # noqa: E402
from store import Store                         # noqa: E402


def main() -> int:
    config = json.loads((HERE / "config.replay.json").read_text(encoding="utf-8"))
    config["guard_path"] = str(REPO / "governance" / "preflight.py")
    state_dir = pathlib.Path(config["state_dir"])
    if state_dir.exists():
        import shutil
        shutil.rmtree(state_dir)

    guard = load_guard(pathlib.Path(config["guard_path"]))
    store = Store(state_dir)
    start = "0" * 40

    # No network in the replay: the "live head" is whatever the executor last produced.
    def head_of(_repo, _branch):
        return store.task("GOVDEMO").get("last_head", start)

    ctl = Controller(config, store, guard,
                     FakeExecutor(config["replay"]["executor_heads"]),
                     FakeReviewer(config["replay"]["reviewer_decisions"]),
                     head_resolver=head_of)
    store.set_task("GOVDEMO", status="READY", last_head=start)

    lines = []

    def out(text=""):
        lines.append(text)
        print(text)

    out("# Replay: execute -> review -> fix -> review -> close, from one start")
    out(f"# guard: {config['guard_path']}")
    out(f"# runners: scripted test doubles, no model call, no network. run budget {config['run_budget']} runs")
    out()
    out("## steps")
    for step in ctl.drive("GOVDEMO"):
        out("  " + json.dumps(step, ensure_ascii=False))

    task = store.task("GOVDEMO")
    out()
    out("## outcome")
    out(f"  status        : {task['status']}")
    out(f"  reviewed head : {task.get('reviewed_head', '')[:12]}")
    out(f"  fix rounds    : {task.get('attempt')}")
    out(f"  runs used     : {store.spend():.0f} of {config['run_budget']}")
    out(f"  human steps   : 0")

    out()
    out("## every guard decision, in order")
    for event in store.events():
        if event["kind"] == "guard":
            v = event["verdict"]
            out(f"  {event['phase']:14} head={event['head']} run={event['run']:16} -> "
                f"{v['action']} ({v['reason']})")
        else:
            rest = {k: v for k, v in event.items() if k not in ("at", "id", "kind")}
            out(f"  {event['kind']:14} {json.dumps(rest, ensure_ascii=False)}")

    out()
    out("## label")
    out("  REPLAY_VERIFIED — the controller works. No AI ran, no trigger is installed,")
    out("  no budget was spent. This is NOT ACTIVE and must not be recorded as such.")

    evidence = HERE / "evidence"
    evidence.mkdir(exist_ok=True)
    (evidence / "replay.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwritten: {evidence / 'replay.txt'}")
    return 0 if task["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())

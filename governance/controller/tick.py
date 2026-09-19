#!/usr/bin/env python3
"""The entry point an EXISTING external trigger calls. One tick, then exit.

This process is not a scheduler and does not want to be one. Something outside
this repository already decides when work should happen; this is the thing it
calls. It advances one task by at most one phase and exits with a code the
caller can branch on.

    python3 governance/controller/tick.py --config <cfg.json> --task PR5 \
            --event <the caller's own id for this firing>

--event is required. It is how a redelivered firing is recognised as the same
event and skipped. An earlier version defaulted it to a string built from the
state revision, which changes on every write: two deliveries of one event got
two different ids, so the processed-event ledger deduplicated nothing. A ledger
keyed on something the source does not control is not a ledger.

Exit codes, so a shell caller needs no JSON parser:

    0  progressed, task not finished     -> call again when convenient
    10 task reached a terminal state     -> nothing more to do
    20 nothing to do (duplicate event, leased elsewhere, already terminal)
    30 stopped by the operator switch, or a limit was hit
    40 refused by the guard (stale head, self-review, outside authority, ...)
    50 a runner failed
    2  bad configuration

stdout is one JSON object per line. stderr carries human-readable failures.
Nothing here schedules, retries in the background, or calls home.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from controller import (Controller, load_guard,   # noqa: E402
                        scripted_commit_verifier)
from store import Store                         # noqa: E402

EXIT = {
    "progressed": 0, "terminal": 10, "noop": 20,
    "stopped": 30, "refused": 40, "runner_failed": 50, "config": 2,
}
TERMINAL_ACTIONS = {"COMPLETE", "CONDITIONS_PENDING", "NEEDS_INFORMATION"}


REPO = HERE.parent.parent


def resolve(path_text: str) -> pathlib.Path:
    """Relative paths resolve against the repository root, not the caller's cwd.

    A trigger calls this from wherever it happens to live; a config that only
    works from one directory is a config that breaks the first time something
    else invokes it.
    """
    path = pathlib.Path(path_text)
    return path if path.is_absolute() else (REPO / path)


def build(config: dict, store: Store):
    guard = load_guard(resolve(config["guard_path"]))
    mode = config.get("mode")
    if mode == "replay":
        from runners import FakeExecutor, FakeReviewer
        executor = FakeExecutor(config["replay"]["executor_heads"])
        reviewer = FakeReviewer(config["replay"]["reviewer_decisions"])
        # Replay heads are invented, so asking a real remote for the live head
        # makes every step after the first fail with stale_head. Found by running
        # this the way a trigger would rather than by reading it.
        start = config["replay"].get("start_head", "0" * 40)

        def replay_head(_repo, _branch):
            return store.task_head_or(start)

        return Controller(config, store, guard, executor, reviewer,
                          head_resolver=replay_head,
                          commit_verifier=scripted_commit_verifier(
                              config["replay"]["executor_heads"]))
    elif mode == "live":
        from runners import SubprocessRunner
        root = pathlib.Path(config["workspace_root"])
        executor = SubprocessRunner("executor", config["runners"]["executor"], root)
        reviewer = SubprocessRunner("reviewer", config["runners"]["reviewer"], root)
    else:
        raise SystemExit(f"unknown mode {mode!r}: expected 'replay' or 'live'")
    return Controller(config, store, guard, executor, reviewer)


def classify(result: dict, status: str | None) -> int:
    action = result.get("action")
    if action == "STOP":
        return EXIT["stopped"]
    if action == "REJECT":
        return EXIT["refused"]
    if action == "FAILED":
        return EXIT["runner_failed"]
    if action == "NOOP":
        return EXIT["noop"]
    if action in TERMINAL_ACTIONS or status in TERMINAL_ACTIONS:
        return EXIT["terminal"]
    return EXIT["progressed"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Advance one governance task by one phase.")
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("--task", required=True)
    ap.add_argument("--event", required=True,
                    help="YOUR stable id for this firing. The same firing "
                         "redelivered must repeat it; two firings must not "
                         "share one. A webhook delivery id, a CI run id or the "
                         "commit sha that caused the firing all work. This is "
                         "not optional and nothing here will invent it.")
    ap.add_argument("--drive", action="store_true",
                    help="keep stepping until terminal instead of one phase")
    ap.add_argument("--max-steps", type=int, default=12)
    args = ap.parse_args(argv)

    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"cannot read config: {exc}", file=sys.stderr)
        return EXIT["config"]

    store = Store(resolve(config["state_dir"]))
    try:
        ctl = build(config, store)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return EXIT["config"]
    except Exception as exc:                        # a disabled live runner lands here
        print(f"cannot start runners: {exc}", file=sys.stderr)
        return EXIT["config"]

    if args.drive:
        results = ctl.drive(args.task, args.event, args.max_steps)
    else:
        results = [ctl.step(args.task, args.event)]

    for line in results:
        print(json.dumps(line, ensure_ascii=False))

    status = store.task(args.task).get("status")
    print(json.dumps({"task": args.task, "status": status,
                      "runs_used": store.spend(),
                      "run_budget": config["run_budget"]}, ensure_ascii=False))
    return classify(results[-1], status)


if __name__ == "__main__":
    raise SystemExit(main())

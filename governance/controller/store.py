#!/usr/bin/env python3
"""Durable state for the handoff controller.

`preflight.py` is a pure offline guard: it answers "may this action be
dispatched", and nothing more. It deliberately holds no state, so the things a
guard cannot provide have to live here:

  * compare-and-swap on a revision, so two workers cannot both act
  * a lease with an owner and an expiry, so a crashed worker's task is
    recoverable but a live worker's task is not stolen
  * a processed-event ledger, so a webhook redelivery is a no-op
  * an append-only event log, so every decision can be replayed afterwards

Everything is written with a temp file plus `os.replace`, which is atomic on
POSIX, so a crash mid-write leaves the previous state intact rather than a
half-written file.

No network, no credentials, no dispatch.
"""

from __future__ import annotations

import json
import os
import pathlib
import time
import uuid


class ConcurrencyError(RuntimeError):
    """Raised when a write loses a compare-and-swap, or a lease is not held."""


class Store:
    def __init__(self, root: pathlib.Path, clock=time.time) -> None:
        self.root = pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root / "state.json"
        self.events_path = self.root / "events.jsonl"
        self._clock = clock
        if not self.state_path.exists():
            self._write({"revision": 0, "tasks": {}, "processed_events": [], "spend": 0.0})

    # ---------- raw io ----------

    def _write(self, state: dict) -> None:
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.state_path)          # atomic; a crash keeps the old file

    def read(self) -> dict:
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    # ---------- compare and swap ----------

    def commit(self, expected_revision: int, mutate) -> dict:
        """Apply `mutate(state)` only if the revision is still what we read.

        The loser of a race gets ConcurrencyError rather than silently
        overwriting the winner. This is the only way state changes.
        """
        state = self.read()
        if state["revision"] != expected_revision:
            raise ConcurrencyError(
                f"state moved: expected revision {expected_revision}, found {state['revision']}"
            )
        mutate(state)
        state["revision"] = expected_revision + 1
        self._write(state)
        return state

    # ---------- leases ----------

    def acquire(self, task_id: str, owner: str, ttl: float) -> dict:
        """Take the task's lease, or fail if someone else holds a live one."""
        state = self.read()
        task = state["tasks"].setdefault(task_id, {})
        lease = task.get("lease")
        now = self._clock()
        if lease and lease["owner"] != owner and lease["expires_at"] > now:
            raise ConcurrencyError(
                f"task {task_id} is leased by {lease['owner']} for another "
                f"{lease['expires_at'] - now:.0f}s"
            )

        def mutate(s):
            s["tasks"].setdefault(task_id, {})["lease"] = {
                "owner": owner, "acquired_at": now, "expires_at": now + ttl,
            }

        return self.commit(state["revision"], mutate)

    def release(self, task_id: str, owner: str) -> dict:
        state = self.read()
        lease = state["tasks"].get(task_id, {}).get("lease")
        if lease and lease["owner"] != owner:
            raise ConcurrencyError(f"task {task_id} is not leased by {owner}")

        def mutate(s):
            s["tasks"].get(task_id, {}).pop("lease", None)

        return self.commit(state["revision"], mutate)

    def holds_lease(self, task_id: str, owner: str) -> bool:
        lease = self.read()["tasks"].get(task_id, {}).get("lease")
        return bool(lease and lease["owner"] == owner and lease["expires_at"] > self._clock())

    # ---------- event dedup ----------

    def seen_events(self) -> list:
        return self.read()["processed_events"]

    def mark_processed(self, event_id: str) -> None:
        state = self.read()
        if event_id in state["processed_events"]:
            return
        self.commit(state["revision"],
                    lambda s: s["processed_events"].append(event_id))

    # ---------- spend ----------

    def spend(self) -> float:
        return self.read()["spend"]

    def add_spend(self, amount: float) -> dict:
        state = self.read()
        return self.commit(state["revision"],
                           lambda s: s.update(spend=round(s["spend"] + amount, 6)))

    # ---------- task fields ----------

    def set_task(self, task_id: str, **fields) -> dict:
        state = self.read()

        def mutate(s):
            s["tasks"].setdefault(task_id, {}).update(fields)

        return self.commit(state["revision"], mutate)

    def task(self, task_id: str) -> dict:
        return self.read()["tasks"].get(task_id, {})

    def task_head_or(self, default: str) -> str:
        """The head of whichever task currently has one. Replay only: real runs
        resolve the head from the remote, never from stored state."""
        for task in self.read()["tasks"].values():
            if task.get("last_head"):
                return task["last_head"]
        return default

    # ---------- append-only audit log ----------

    def log(self, **fields) -> dict:
        record = {"at": self._clock(), "id": uuid.uuid4().hex[:12], **fields}
        with self.events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return record

    def events(self) -> list:
        if not self.events_path.exists():
            return []
        return [json.loads(line) for line in
                self.events_path.read_text(encoding="utf-8").splitlines() if line.strip()]

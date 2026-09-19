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

Every write goes to a temp file unique to the writing process and is then
`os.replace`d into place, which is atomic on POSIX, so a crash mid-write leaves
the previous state intact rather than a half-written file. The temp name has to
be unique: a shared `state.tmp` made two concurrent writers overwrite each
other's file and the loser's `os.replace` died with FileNotFoundError, which is
the opposite of a durable write. Found by running six real processes at it, not
by reading the code.

The compare-and-swap is taken under an exclusive `flock` held across the whole
read-check-write. Without the lock the check and the write are two separate
syscall groups, so two processes could both read revision N, both find it
current, and both write N+1 — one update silently lost. A revision check that
is not held under a lock is a comment, not a guarantee.

No network, no credentials, no dispatch.
"""

from __future__ import annotations

import contextlib
import fcntl
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
        self.lock_path = self.root / "state.lock"
        self._clock = clock
        if not self.state_path.exists():
            self._write({"revision": 0, "tasks": {}, "processed_events": [], "spend": 0.0})

    # ---------- raw io ----------

    @contextlib.contextmanager
    def _exclusive(self):
        """Hold the state lock for the whole read-check-write.

        flock is advisory and per-open-file-description, so every writer opens
        its own handle and blocks until the previous one closes. It is released
        even if the holder is killed, because the kernel closes the fd.
        """
        with open(self.lock_path, "a+b") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _write(self, state: dict) -> None:
        # Unique per writer: a shared temp name is a cross-process data race.
        tmp = self.state_path.with_name(f"state.{os.getpid()}.{uuid.uuid4().hex}.tmp")
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
        with self._exclusive():
            state = self.read()
            if state["revision"] != expected_revision:
                raise ConcurrencyError(
                    f"state moved: expected revision {expected_revision}, "
                    f"found {state['revision']}"
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

    def renew(self, task_id: str, owner: str, ttl: float) -> dict:
        """Extend a lease we still hold.

        G3: a task that runs longer than its lease would otherwise be taken over
        by a second worker mid-flight, which is the concurrency failure the
        acceptance asks to be proven against rather than assumed away. A holder
        that has already lost the lease is refused — it must not silently
        reacquire and keep going as though nothing happened.
        """
        state = self.read()
        lease = state["tasks"].get(task_id, {}).get("lease")
        now = self._clock()
        if not lease or lease["owner"] != owner:
            raise ConcurrencyError(f"task {task_id} is not leased by {owner}")
        if lease["expires_at"] <= now:
            raise ConcurrencyError(
                f"task {task_id} lease for {owner} expired at {lease['expires_at']}; "
                "another worker may already hold it"
            )

        def mutate(s):
            s["tasks"][task_id]["lease"]["expires_at"] = now + ttl

        return self.commit(state["revision"], mutate)

    # ---------- intent before an external side effect, result after ----------

    def record_intent(self, task_id: str, action: str, **detail) -> str:
        """Write down what we are about to do OUTSIDE this process.

        G3: if the process dies between a push (or a model call) and saving the
        outcome, recovery must not blindly repeat it. The open intent is the
        marker that says "go and ask GitHub what actually happened first".
        """
        intent_id = uuid.uuid4().hex[:12]
        state = self.read()

        def mutate(s):
            s["tasks"].setdefault(task_id, {}).setdefault("open_intents", []).append(
                {"intent_id": intent_id, "action": action, "at": self._clock(), **detail}
            )

        self.commit(state["revision"], mutate)
        self.log(kind="intent", task=task_id, action=action, intent_id=intent_id, **detail)
        return intent_id

    def close_intent(self, task_id: str, intent_id: str, outcome: str, **detail) -> dict:
        state = self.read()

        def mutate(s):
            task = s["tasks"].setdefault(task_id, {})
            task["open_intents"] = [i for i in task.get("open_intents", [])
                                    if i["intent_id"] != intent_id]

        result = self.commit(state["revision"], mutate)
        self.log(kind="intent_closed", task=task_id, intent_id=intent_id,
                 outcome=outcome, **detail)
        return result

    def open_intents(self, task_id: str) -> list:
        return self.task(task_id).get("open_intents", [])

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

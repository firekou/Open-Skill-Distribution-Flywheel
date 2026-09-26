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


# GOV-R2-03: closing an intent used to be one thing -- "not open any more".
# That collapsed three situations a recovery has to tell apart:
#
#   effect_confirmed   we went and looked, and the external effect IS there.
#                      Re-dispatching would duplicate it.
#   effect_refuted     we went and looked, and it is NOT there. Re-dispatching
#                      is safe.
#   effect_unknown     we could not look, or looking cannot answer. Neither
#                      re-dispatching nor advancing is justified; a human or a
#                      later reconciliation has to decide.
#
# A closed intent with no outcome is indistinguishable from the third case
# being silently treated as the second, which is how a governance run comes to
# push the same work twice.
INTENT_OUTCOMES = ("effect_confirmed", "effect_refuted", "effect_unknown")


def _check_outcome(outcome: str) -> None:
    if outcome not in INTENT_OUTCOMES:
        raise ValueError(
            f"intent outcome {outcome!r} is not one of {list(INTENT_OUTCOMES)}; "
            "an intent may not be closed without saying what was observed")


def _resolve_intent(state: dict, task_id: str, intent_id: str, outcome: str) -> None:
    """Move an intent from `open_intents` to `resolved_intents`, with why.

    Kept as a module function so the single-purpose `close_intent` and the
    all-in-one `commit_event_and_task` cannot drift apart -- they did, once,
    and the version inside the combined commit popped a key from a dict that
    never existed.
    """
    task = state["tasks"].setdefault(task_id, {})
    hit = [i for i in task.get("open_intents", []) if i["intent_id"] == intent_id]
    task["open_intents"] = [i for i in task.get("open_intents", [])
                            if i["intent_id"] != intent_id]
    resolved = task.setdefault("resolved_intents", [])
    for intent in hit:
        resolved.append({**intent, "outcome": outcome})
    del resolved[:-20]                     # bounded; the audit log keeps the rest


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
            task = s["tasks"].setdefault(task_id, {})
            # The counter lives on the TASK, not inside the lease it stamps.
            # Keeping it in the lease made `release` — which deletes the lease —
            # reset it, so a worker that released and re-acquired got
            # generation 1 both times and the fence could not tell the two
            # apart. A monotonic number that a normal operation resets is not
            # a fence.
            task["lease_generation"] = task.get("lease_generation", 0) + 1
            task["lease"] = {
                "owner": owner, "acquired_at": now, "expires_at": now + ttl,
                "generation": task["lease_generation"],
            }

        return self.commit(state["revision"], mutate)

    def release(self, task_id: str, owner: str) -> dict:
        """Drop OUR lease. Never anyone else's.

        GOV-R2-02: the ownership test used to be a read taken before the
        commit. Between the two, an expired lease could be picked up by a new
        owner and this `pop` would then delete the lease of a worker that is
        actively running — the precise failure the lease exists to prevent.
        The test now happens inside the same compare-and-swap as the write.
        """
        state = self.read()

        def mutate(s):
            lease = (s["tasks"].get(task_id) or {}).get("lease")
            if lease is None:
                return
            if lease["owner"] != owner:
                raise ConcurrencyError(
                    f"task {task_id} is leased by {lease['owner']}, not {owner}; "
                    "refusing to release a lease that is not ours")
            s["tasks"][task_id].pop("lease", None)

        return self.commit(state["revision"], mutate)

    def lease_generation(self, task_id: str) -> int | None:
        lease = (self.task(task_id) or {}).get("lease") or {}
        return lease.get("generation")

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

    def reserve_run_and_record_intent(self, task_id: str, action: str, amount: float,
                                      require_owner: str | None = None,
                                      require_generation: int | None = None,
                                      **detail) -> str:
        """Reserve the run AND record the intent in ONE fenced compare-and-swap.

        P2 (R4): these were two commits — `add_spend`, then `record_intent` —
        neither fenced. A crash between them spent budget with no intent to
        reconcile, and a redelivery spent it again; a worker that had already
        lost its lease could still do both. One commit, checked against the
        lease inside it, removes the window instead of shrinking it.
        """
        intent_id = uuid.uuid4().hex[:12]
        state = self.read()

        def mutate(s):
            if require_owner is not None:
                self._require_lease(s, task_id, require_owner, require_generation)
            s["spend"] = round(s["spend"] + amount, 6)
            s["tasks"].setdefault(task_id, {}).setdefault("open_intents", []).append(
                {"intent_id": intent_id, "action": action, "at": self._clock(), **detail}
            )

        self.commit(state["revision"], mutate)
        self.log(kind="intent", task=task_id, action=action, intent_id=intent_id,
                 reserved=amount, **detail)
        return intent_id

    def close_intent(self, task_id: str, intent_id: str, outcome: str, **detail) -> dict:
        state = self.read()
        _check_outcome(outcome)

        def mutate(s):
            _resolve_intent(s, task_id, intent_id, outcome)

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

    def commit_event_and_task(self, event_id: str, task_id: str,
                              close_intent_id: str | None = None,
                              close_outcome: str | None = None,
                              require_owner: str | None = None,
                              require_generation: int | None = None,
                              **fields) -> dict:
        """Consume the event and advance the task in ONE compare-and-swap.

        These were two commits, event first. The comment above them claimed a
        crash in between would re-run a step that changed nothing — the
        opposite of what the code does. Marking the event first means a
        redelivery is deduplicated away while the task has NOT moved, so the
        round is lost silently. One commit removes the window rather than
        arguing about which side of it is safer.
        """
        if close_intent_id and close_outcome is None:
            raise ValueError(
                "closing an intent requires close_outcome; see INTENT_OUTCOMES")
        if close_outcome is not None:
            _check_outcome(close_outcome)
        state = self.read()

        def mutate(s):
            if require_owner is not None:
                self._require_lease(s, task_id, require_owner, require_generation)
            if event_id not in s["processed_events"]:
                s["processed_events"].append(event_id)
            task = s["tasks"].setdefault(task_id, {})
            task.update(fields)
            if close_intent_id:
                # Intents live on the task as a list, not in a top-level dict.
                # The first version popped a key from a dict that never existed
                # and reported success — the close silently did nothing, which
                # is exactly the failure this ledger is supposed to prevent.
                _resolve_intent(s, task_id, close_intent_id, close_outcome)

        return self.commit(state["revision"], mutate)

    # ---------- spend ----------

    def spend(self) -> float:
        return self.read()["spend"]

    def add_spend(self, amount: float) -> dict:
        state = self.read()
        return self.commit(state["revision"],
                           lambda s: s.update(spend=round(s["spend"] + amount, 6)))

    # ---------- task fields ----------

    def set_task(self, task_id: str, require_owner: str | None = None,
                 require_generation: int | None = None, **fields) -> dict:
        state = self.read()

        def mutate(s):
            if require_owner is not None:
                self._require_lease(s, task_id, require_owner, require_generation)
            s["tasks"].setdefault(task_id, {}).update(fields)

        return self.commit(state["revision"], mutate)

    def _require_lease(self, state: dict, task_id: str, owner: str,
                       generation: int | None) -> None:
        """Possession, checked INSIDE the commit that writes the result.

        GOV-R2-02: a read taken before the commit leaves a window in which the
        lease changes hands and the old worker still writes, using a revision
        it had just re-read. The generation makes a lease that was lost and
        re-acquired by us distinguishable from the one we actually hold.
        """
        lease = (state["tasks"].get(task_id) or {}).get("lease") or {}
        if (lease.get("owner") != owner
                or lease.get("expires_at", 0) <= self._clock()
                or (generation is not None and lease.get("generation") != generation)):
            raise ConcurrencyError(
                f"lease for {task_id} is no longer ours at commit time; "
                "refusing to record a result we are not entitled to write")

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

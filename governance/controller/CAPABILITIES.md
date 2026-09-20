# Capability table — what exists, what does not, and how we know

This file exists because of GOV-R1-01: the previous report concluded that the
only missing piece was a model credential. That was wrong, and the way it was
wrong matters. Continuous governance needs nine separate capabilities. Having
eight of them and calling the ninth "the one gap" produces a report that reads
like readiness and behaves like a single-session script.

Evidence ladder, as used throughout this repository:

| Level | Means |
|---|---|
| `REPORTED` | someone said so; nothing in this repository checks it |
| `OBSERVED` | seen once, by hand, not repeatably |
| `TESTED` | an automated test in this repository covers it |
| `VERIFIED` | tested, plus a negative control that fails when the guarantee is removed |
| `REPRODUCED` | verified independently, by someone who did not write it |

`NOT BUILT` is not a level. It means the capability does not exist here at all.

---

## The nine capabilities

| # | Capability | Provider | Lifecycle | Evidence | Where | Limit that applies | Gap |
|---|---|---|---|---|---|---|---|
| 1 | **Event source** — what says "there is work" | GPT side, outside this repository | unknown to this repository | `REPORTED` | — | — | This repository has never received an event from it. No event ID, no timestamp, no delivery has been observed here. |
| 2 | **Receiving service** — something listening for that event | none | — | `NOT BUILT` | — | — | Nothing here listens. `tick.py` is a **callee**: it must be invoked. A caller that never calls is indistinguishable from no caller. |
| 3 | **Persistent launcher** — what invokes the callee on a schedule | none for `tick.py`; one account Routine watches for reviews | Routine is stored account-side but bound to one session | `NOT BUILT` for the controller; `OBSERVED` for review-watching | routine `trig_01K4VfPCvDp4XEEddbFLUHqn` | fires hourly | **Measured, not assumed:** two session-scoped cron jobs created during this work (`ee341b02`, `46edd712`) are both gone — they did not survive. A real account Routine has since been created and *is* listed, which the vanished ones never were. It has now fired once, at 2026-09-19T21:08Z, and the wake worked: the session came back, both `git fetch` calls succeeded, and the GitHub tools were present — the "stores no connectors" warning applies to a Routine that starts a *fresh* session, not to one that wakes an existing one. On 2026-09-20 the **container was restarted** and the Routine came through it intact — still enabled, still scheduled, having fired successfully at 07:08. That is a stronger durability event than the one that killed the earlier crons, which died on a mere MCP reconnect. **It still does not close this row:** it wakes a session to *look for* reviews, it does not invoke `tick.py`, and the restart replaced the container while the **session** continued, so survival of the session itself ending remains untested. |
| 4 | **Execution host** — where the controller process runs | this ephemeral container | reclaimed after inactivity | `OBSERVED` | — | disk and lifetime are per session | No persistent host has been chosen. State written here dies with the container, so #8 cannot be satisfied from here. **Demonstrated, not theorised:** the container was restarted on 2026-09-20 and three running background jobs were killed with it. The work survived only because it had been pushed; anything left on local disk would have been gone. |
| 5 | **Model authentication** — how a runner reaches a model | Claude / ChatGPT subscriptions | per host | `NOT AVAILABLE HERE` | — | runs and wall clock, not currency | This container has no `ANTHROPIC_API_KEY` and no `~/.claude/.credentials.json`. `claude` 2.1.278 is installed and cannot authenticate. Which auth path a future host uses, and whether that path bills, is **unverified** — `run_budget` does not answer it (GOV-R1-04). |
| 6 | **Reviewer identity** — that the reviewer is not the author | controller config + runner identity | per run | `VERIFIED` | `evidence/mutation_g123.txt`, `test_controller.py` | guard refuses `self_review` | Distinct **identity** is enforced. Distinct **judgement** is not: two runs of the same model family are not two independent sources. Only a genuinely separate reviewer settles that, and none has run. |
| 7 | **GitHub read / write** — clone, and push the result | git over https; executor's token | per run | read `TESTED` (local repo fixture), write `NOT EXERCISED` | `test_controller.py::TheRealRunAdapterIsDrivenEndToEnd` | reviewer and PR tests get **no** write token | No runner has ever pushed a commit. The reported-head check exists precisely because a push can fail while the runner still reports success. |
| 8 | **State disk** — durable, concurrent-safe state | `state_dir` on local disk | survives the process, **not** the container | `VERIFIED` | `evidence/concurrency.txt` | flock + compare-and-swap | Safe against six concurrent processes. Not durable here, because #4 is ephemeral. |
| 9 | **Cancel and recovery** — stopping, and coming back | files on disk + process-group kill | — | L1–L3 `VERIFIED`, L4 `NOT POSSIBLE HERE` | `evidence/cancel.txt` | see the ladder in `controller.py` | L4, revoking a credential, belongs to the issuer and cannot be done from this program. Nothing here should imply otherwise. |

---

## Which user bottleneck each capability removes

Required by GOAL-02 (`governance/decisions.json`), which asks what real
bottleneck each improvement relieves and whether an outside user could
reproduce the result.

**The honest frame first.** Every row below is upstream plumbing. The user it
currently serves is **the owner of this repository**, and the bottleneck it
removes is the owner having to carry files between two AIs by hand and having
to re-check, by hand, whether what an AI reported actually happened. **No
external user has completed any work through this.** Nothing here should be
read as evidence that outside users succeed; per the mission text, a
governance rehearsal proves relay, not external success.

| # | Capability | The bottleneck, stated as the thing that goes wrong without it |
|---|---|---|
| 1 | Event source | Nobody knows there is work until a person notices. Every round starts with the owner checking. |
| 2 | Receiving service | Even a known event has nowhere to land, so noticing still costs a person's attention. |
| 3 | Persistent launcher | Work stops the moment the owner closes the session. This is the bottleneck that makes all the others theoretical. |
| 4 | Execution host | State and history die with the container, so each round starts from nothing and prior evidence cannot be re-read. |
| 5 | Model authentication | The executor and reviewer cannot run at all, so the loop is a design rather than a process. |
| 6 | Reviewer identity | The author reviews their own work. That is the failure this whole project exists to prevent: it produces confident approval with nothing behind it. |
| 7 | GitHub read / write | The result cannot be handed on, so a completed round still needs a person to move it. |
| 8 | State disk | Two workers silently overwrite each other, and a crash loses the round. Measured: 39 of 60 writes were reported successful and lost. |
| 9 | Cancel and recovery | A runner that misbehaves cannot be stopped, and a stuck one holds its credentials indefinitely. Without it, nobody can safely let this run unattended. |

**What would make this real for someone other than the owner.** Rows 1–4
becoming true would mean a round completes while nobody is watching. That is
necessary and not sufficient: the mission's test is whether an outside person
gets work they wanted done. That is G7, it needs a real tool task, and nothing
in this round touched it.

**Cost against result, as the same rule asks.** This round spent no money and
made no model calls beyond this session: the runners never ran. What it bought
is seven defects closed, each with a control that fails when the fix is removed
— including three that made the system *report success while losing the work*,
which is the failure mode most likely to waste a user's time without anyone
noticing. Model-call volume is not offered as progress.

## What this table says, plainly

Rows 1–4 are the real blockers, and none of them is a credential.

There is **no persistent launcher**, so nothing calls the controller when this
session ends. There is **no receiving service**, so the event in row 1 has
nowhere to arrive. There is **no persistent host**, so state does not outlive
the container. Row 5, the credential, matters only once 1–4 exist: a perfectly
authenticated runner that nothing ever invokes still does nothing.

Rows 6–9 are the ones this work package actually advanced, and they are the
ones carrying real evidence.

## What would change a row

A row moves only on evidence of the kind its level names, and only for the
capability in that row:

- **Row 3** becomes `OBSERVED` for the controller when a launcher outside this
  session invokes **`tick.py`** once and the event ID, time, task, run ID and
  head are recorded. The review-watching Routine does not count: watching for
  work is not dispatching it. Row 3 becomes `TESTED` when a launcher still
  fires after the session it was created from has ended — which is the only
  thing that distinguishes a launcher from a long-running session.
- **Row 5** becomes `OBSERVED` when a runner authenticates somewhere, recording
  only *which* path and *whether* a quota exists — never a key, never a price
  invented for the record.
- **Row 6** becomes `REPRODUCED` only through a reviewer that is not this model
  acting twice.
- **Row 7** becomes `OBSERVED` on the first real push, with the SHA.

Until rows 1–4 hold, the correct label for the whole system is
`REPLAY_VERIFIED`, and `state.json` must not say `ACTIVE`. That is not caution
for its own sake: `ACTIVE` asserts that work continues when the owner is not
watching, and today it would stop.

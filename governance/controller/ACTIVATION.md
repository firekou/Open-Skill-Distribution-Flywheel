# Activation: what actually has to be true

Two things this file previously asked the owner to decide were the wrong
questions, and are removed:

- **"Approve a budget."** There is no per-call price to approve. The work runs
  on Claude and ChatGPT **subscriptions**. What runs out is usage and time, not
  dollars, so the cap is counted in **runs** (`run_budget`, one runner
  invocation = 1) and wall-clock. Nothing here needs a spending decision.
- **"Choose a trigger."** A trigger already exists and runs on the GPT side,
  outside this repository, so the controller's job is to **be called** rather
  than to ask the owner to pick a scheduler. That is what `tick.py` is.
  **What that does not mean:** the GPT-side trigger drives GPT's own work and
  has never invoked `tick.py`. Being callable is not the same as being called.
  See row 3 of [CAPABILITIES.md](CAPABILITIES.md) — there is currently no
  launcher pointed at this repository, which is a gap in wiring, not a question
  for the owner to re-answer.

## The contract an existing trigger calls

```bash
python3 governance/controller/tick.py --config <cfg.json> --task PR5 \
        --event <the caller's own id for this firing>
python3 governance/controller/tick.py --config <cfg.json> --task PR5 \
        --event <id> --drive
```

`tick.py` is the entry point for **both** modes. `mode: "live"` plus
`runners.*.enabled = true` in the config is the whole switch — enabling live
dispatch is a config change, not a code change. `controller.py`'s own CLI is a
replay-only convenience and is not the activation path.

One tick advances one task by at most one phase, then exits. It is not a daemon,
it does not schedule, it does not retry in the background. Call it again when
the caller decides it is time.

| exit | meaning | what the caller should do |
|--:|---|---|
| **0** | progressed, not finished | call again when convenient |
| **10** | terminal (COMPLETE / CONDITIONS_PENDING / NEEDS_INFORMATION) | stop; a human or the next work package takes it |
| **20** | nothing to do — duplicate event, leased elsewhere, already terminal | safe to ignore; this is what a redelivered webhook looks like |
| **30** | operator stop switch, or a limit was reached | **do not retry.** Something deliberately said stop |
| **40** | refused by the guard — stale head, self-review, outside authority | re-read the live head and reassess; retrying unchanged will be refused again |
| **50** | a runner failed | the task carries `recovery_point`; a retry is a decision, not automatic |
| **2** | bad configuration | fix the config |

stdout is one JSON object per line, last line a summary
(`{"task", "status", "runs_used", "run_budget"}`). Relative paths in the config
resolve against the repository root, not the caller's working directory — so it
behaves the same whoever invokes it.

`--event` is **required**, and nothing invents one. It is how a redelivered
firing is recognised and skipped, so it has to be stable at the source: the
same firing redelivered repeats it, two firings never share one. A webhook
delivery id, a CI run id, or the commit sha that caused the firing all work.

An earlier version of this file said that omitting it derived one "from the
task's revision and attempt, which is also stable across a redelivery". That
was false. The state revision changes on every write, so two deliveries of one
event arrived under two different ids and both ran; the processed-event ledger
deduplicated nothing. `--drive` has the same contract and namespaces its steps
under the caller's id.

## Where we are

| Label | Meaning | Status |
|---|---|---|
| `FOUNDATION_ONLY` | rules + offline guard only | passed |
| **`REPLAY_VERIFIED`** | the controller sequences the whole handoff, guard-checked, with negative controls and mutation testing | **reached** — `evidence/` |
| `MANUAL_RUN_VERIFIED` | a real AI executor and a real independent reviewer complete one round | not reached |
| `ACTIVE` | the above, driven by the trigger, with run IDs, SHAs and timings | not reached |

## What is missing — all of it, not one thing

An earlier version of this file said the only missing piece was a model
credential. That was wrong, and wrongly shaped: it made a system with no
persistent launcher read as one flag away from running.

The full accounting is **[CAPABILITIES.md](CAPABILITIES.md)** — nine
capabilities, each with its provider, lifetime, evidence level and gap. The
short version:

| | Capability | State |
|---|---|---|
| 1 | event source | exists on the GPT side; **this repository has never received an event from it** |
| 2 | receiving service | **none.** `tick.py` is a callee; nothing here listens |
| 3 | persistent launcher | **none for `tick.py`.** Two cron jobs created during this work are gone (session-scoped, did not survive). An account Routine now watches for incoming reviews, *is* listed, and has fired once successfully — but it wakes a session to *look*, it does not dispatch, and it is bound to that session |
| 4 | execution host | this container, which is reclaimed after inactivity |
| 5 | model credential | absent here (`claude` 2.1.278 is installed and cannot authenticate) |
| 6 | reviewer identity | enforced; independent *judgement* still unproven |
| 7 | GitHub read / write | no runner has ever pushed |
| 8 | state disk | concurrent-safe, but not durable on an ephemeral host |
| 9 | cancel and recovery | L1–L3 work; L4 belongs to the credential issuer |

Rows 1–4 are the blockers, and none of them is the credential. A perfectly
authenticated runner that nothing ever invokes still does nothing.

## Switch-on

1. Copy `config.live.example.json` outside the repository and set
   `runners.*.enabled = true`. It ships disabled so that enabling live dispatch
   is a deliberate, reviewable edit rather than a flag already on.
2. Point `state_dir` at persistent disk and `stop_file` somewhere the operator
   can write.
3. Run **one** task with `max_attempts: 1` and keep the run IDs, SHAs and
   timings. That earns `MANUAL_RUN_VERIFIED`.
4. Point a launcher that outlives this session at `tick.py`, passing its own
   event id each time, and keep the event IDs, run IDs, SHAs and timings. Only
   when that survives a restart of the launcher's host is the system `ACTIVE`,
   and only then may `state.json` say so.

Nothing in steps 1–4 is a code change. Step 4 is the one that does not exist
yet, and no amount of configuration substitutes for it.

## Switch-off

"Cancel" was one word covering four actions that stop different things. They
are not interchangeable, and each is listed with what it **cannot** do:

| Level | To stop | Do this | Cannot |
|---|---|---|---|
| **L1** | new dispatch | `touch $stop_file` | reach a runner already running |
| **L2** | one task | `touch $(dirname $stop_file)/CANCEL-<task>` | reach a runner already running; other tasks keep going |
| **L3** | the runner running now | `Controller.cancel_runner()` — kills it **and every process it started** | undo a commit the runner already pushed; that needs a revert, separately authorised |
| **L4** | a credential | **not possible from this program.** Anthropic console for the model credential, GitHub for the token | nothing else on this list substitutes for it: if a key leaked, L1–L3 do not take it back |
| — | the schedule | stop calling `tick.py` | it is not a daemon; nothing runs on its own |
| — | everything | set `runners.*.enabled = false` | `SubprocessRunner` refuses to construct |

L3 needed a real fix, not just a name: `subprocess.run(timeout=...)` kills only
the direct child, so a CLI agent's own worker survived the timeout still holding
the credentials from its environment. Runners are now started in their own
process group and the whole group is taken down. Controls: `evidence/cancel.txt`.

State lives in `state_dir`, outside this repository. Deleting it resets the
controller and loses history; it does not touch the repo.

## Limits, and what they do not prove

| Control | Where | Default | What it bounds |
|---|---|---|---|
| runs per task | `run_budget`, enforced **before** dispatch | 8 | how many times a model is called |
| fix rounds | `max_attempts` | 2 | how many times a task comes back |
| one model call | runner `timeout_seconds` | 1200s (20 min) | one execute or one review |
| one round | top-level `timeout_seconds` | 2700s (45 min) | execute + review together |
| repository tests | `pr_tests` role, when wired | 600s (10 min) | untrusted code, no credential |
| runner overrun | `terminate_grace_seconds` | 10s | SIGTERM before SIGKILL, to the whole process group |
| one worker per task | lease in the store | 900s, recoverable after expiry | concurrent workers |

**These are counts and clocks. None of them is a billing statement.** The run
cap bounds how many times a model is called; it says nothing about which
authentication path a host uses or whether that path bills. The two are
recorded separately, and the authentication row in
[CAPABILITIES.md](CAPABILITIES.md) is `NOT AVAILABLE HERE` and unverified. No
price appears anywhere in this repository, because inventing one would be
fabricating evidence.

The run reservation happens before the runner starts, not after it finishes — an
earlier version checked the spend as it stood, which let the last permitted call
start one run over the cap. Verified: `run_budget=N` starts exactly N runs.

## What is still not covered

- **No real AI round has been executed by this controller.** The replay uses
  scripted doubles, so everything above `REPLAY_VERIFIED` is untested.
- The guard validates that a review record is well formed and bound to the right
  head and reviewer. It cannot tell whether the review is *true*. Only a real
  independent reviewer does that, and two runs of the same model are not
  independent sources.
- **Isolation, stated exactly.** What now holds: each runner gets a fresh clone,
  and its environment is an **allowlist** built per role — `PATH`, `HOME` and a
  few locale variables, plus only the credentials that role is entitled to. The
  reviewer never receives a write token; the `pr_tests` role receives no
  credential at all; anything added to the parent environment later is dropped
  rather than inherited. The previous default was `env=None`, which subprocess
  reads as "inherit everything": 142 variables on the host this was written on,
  including `GITHUB_TOKEN` and `AWS_SECRET_ACCESS_KEY`. Nothing leaked, because
  live dispatch was never on — but the default contradicted this file.
  What still does **not** hold: a fresh clone plus a filtered environment is not
  a sandbox. Untrusted repository code executed by a runner still shares the
  kernel, the filesystem outside the clone and the network with the controller.
  Container or namespace isolation is available in principle and **is not wired
  in here**. Until it is, running an untrusted PR's own test suite is outside
  what this design covers.
- The GPT-side trigger is outside this repository and is not described by it.
  This file specifies the interface it can call; it does not claim to know how
  that trigger is configured.

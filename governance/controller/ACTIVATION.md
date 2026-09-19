# Activation: what actually has to be true

Two things this file previously asked the owner to decide were the wrong
questions, and are removed:

- **"Approve a budget."** There is no per-call price to approve. The work runs
  on Claude and ChatGPT **subscriptions**. What runs out is usage and time, not
  dollars, so the cap is counted in **runs** (`run_budget`, one runner
  invocation = 1) and wall-clock. Nothing here needs a spending decision.
- **"Choose a trigger."** One already exists and already runs, on the GPT side,
  outside this repository. The controller's job is therefore to **be called**,
  not to ask for a scheduler. That is what `tick.py` is.

## The contract an existing trigger calls

```bash
python3 governance/controller/tick.py --config <cfg.json> --task PR5
python3 governance/controller/tick.py --config <cfg.json> --task PR5 --drive
```

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

Idempotency is on the caller's side too: pass `--event <id>` and the same id
twice is a no-op. Omit it and one is derived from the task's revision and
attempt, which is also stable across a redelivery.

## Where we are

| Label | Meaning | Status |
|---|---|---|
| `FOUNDATION_ONLY` | rules + offline guard only | passed |
| **`REPLAY_VERIFIED`** | the controller sequences the whole handoff, guard-checked, with negative controls and mutation testing | **reached** — `evidence/` |
| `MANUAL_RUN_VERIFIED` | a real AI executor and a real independent reviewer complete one round | not reached |
| `ACTIVE` | the above, driven by the trigger, with run IDs, SHAs and timings | not reached |

## The one thing genuinely missing

**A model credential in whatever process runs the runners.**

`runners.SubprocessRunner` targets `claude -p --output-format json`, which is
present in this container (2.1.278). It cannot authenticate here: there is no
`ANTHROPIC_API_KEY` and no `~/.claude/.credentials.json` in this environment.

That is an environment fact, not a decision to make. Where the runners execute
under a logged-in subscription, they authenticate; where they execute in a bare
container like this one, they do not. So:

- run `tick.py` **wherever the Claude subscription is already authenticated**, or
- give that process a credential by the normal means for its environment.

Nothing about this needs the owner to choose a plan or a price.

## Switch-on

1. Copy `config.live.example.json` outside the repository and set
   `runners.*.enabled = true`. It ships disabled so that enabling live dispatch
   is a deliberate, reviewable edit rather than a flag already on.
2. Point `state_dir` at persistent disk and `stop_file` somewhere the operator
   can write.
3. Run **one** task with `max_attempts: 1` and keep the run IDs, SHAs and
   timings. That earns `MANUAL_RUN_VERIFIED`.
4. Let the existing trigger call `tick.py` on a schedule. That is `ACTIVE`, and
   only then may `state.json` say so.

`controller.py`'s own CLI still refuses `mode != replay`; `tick.py` is the entry
point that supports both, and `mode: "live"` plus enabled runners is the switch.

## Switch-off

| To stop | Do this | Effect |
|---|---|---|
| immediately | `touch $stop_file` | the next tick returns `STOP` **before** any runner starts, exit 30 |
| the schedule | stop calling `tick.py` | it is not a daemon; nothing runs on its own |
| one task | set its status to a terminal value in the store | subsequent ticks return exit 20 |
| everything | set `runners.*.enabled = false` | `SubprocessRunner` refuses to construct |

State lives in `state_dir`, outside this repository. Deleting it resets the
controller and loses history; it does not touch the repo.

## Limits that apply on a subscription

| Control | Where | Default |
|---|---|---|
| runs per task | `run_budget`, enforced **before** dispatch | 8 |
| fix rounds | `max_attempts` | 2 |
| wall-clock per round | `timeout_seconds` | 2700 |
| one worker per task | lease in the store | 600s, recoverable after expiry |

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
- Runner isolation is a fresh clone per run. Executing untrusted PR code also
  needs the container, which is available but not wired in here.
- The GPT-side trigger is outside this repository and is not described by it.
  This file specifies the interface it can call; it does not claim to know how
  that trigger is configured.

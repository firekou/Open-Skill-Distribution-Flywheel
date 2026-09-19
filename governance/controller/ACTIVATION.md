# Activation: what real startup needs, and what is actually missing

The controller is finished and replayable. It is **not running**, and the gap is
not code. This file lists exactly what is missing, so the owner is deciding
about a real thing rather than a plan.

## Where we are

| Label | Meaning | Status |
|---|---|---|
| `FOUNDATION_ONLY` | rules + offline guard only | passed |
| **`REPLAY_VERIFIED`** | the controller sequences the whole handoff, guard-checked, with negative controls | **reached — `evidence/replay.txt`, 26 tests** |
| `MANUAL_RUN_VERIFIED` | a real AI executor and a real independent reviewer complete one round, started by hand | not reached |
| `ACTIVE` | the above, plus a persistent trigger, with run IDs, SHAs, timings and cost | not reached |

Writing `ACTIVE` into `state.json` before a real trigger and a real AI round is
exactly the kind of claim this project keeps having to withdraw. Do not.

## Capability inventory, measured in this container

| Capability | Result | Consequence |
|---|---|---|
| `claude` CLI, non-interactive (`-p --output-format json`) | **present**, 2.1.278 | a real runner adapter has a real target — `runners.SubprocessRunner` targets exactly this |
| model credentials (`ANTHROPIC_API_KEY`, OAuth token) | **NOT SET**; no `~/.claude/.credentials.json` | the runner is implementable but **cannot authenticate here** |
| `GITHUB_TOKEN` / `GH_TOKEN` | set; `git ls-remote` works | branch push and PR reads are reachable |
| `gh` CLI | absent | GitHub via git + the session's MCP tools, not `gh` |
| `docker` | present | third-party code can be isolated |
| `git worktree` | works | per-run isolated workspaces |
| `crontab` | absent | — |
| `systemctl` | present, but **this container is reclaimed when idle** | **a scheduler inside the container dies with it.** The trigger must be external |

## The one thing that cannot be built inside this repository

**A persistent trigger.** The controller is a function that must be *called*.
Nothing in this repo can call it on a schedule after the container is gone.

Three options, honestly compared:

| Option | What it costs | What it needs from the owner |
|---|---|---|
| **GitHub Actions** (`workflow_dispatch` + `schedule`) | free minutes on a public repo; the model calls cost whatever the runner spends | a repository secret holding a model credential, and `.github/workflows/` write access. **Recommended**: the trigger, the isolation and the audit log are all things GitHub already runs |
| An always-on host (systemd timer) | a machine | somewhere to run it, plus credential delivery |
| The chat session's own scheduler | model spend per firing | this is a **session** capability, not a repository one. A standalone controller process cannot call it. It also cannot be committed, reviewed or handed over |

Note the third row carefully. **A chat window cannot be woken by a program.**
Where this session can schedule something, that is the harness acting, not this
controller — so it is not a substitute for a trigger the repo can own.

## Switch-on order

1. Owner sets a **budget above zero** and says which model. Today `budget: 0`,
   and the guard stops on `cost > budget`, so a live run would halt immediately
   — by design.
2. Put a model credential in the runner environment (a repo secret for Actions).
   It must never reach a PR checkout: a PR can contain anything, and a runner
   holding a push token must not execute PR-supplied code.
3. Copy `config.live.example.json` outside the repo, set
   `runners.*.enabled = true`, point `stop_file` somewhere the operator can
   write, set `state_dir` on persistent disk.
4. Run **one** task by hand first, with `max_attempts: 1`. Keep the run IDs,
   SHAs, timings and cost. That earns `MANUAL_RUN_VERIFIED`.
5. Only then install the trigger, and only then `ACTIVE`.

`controller.py` refuses `mode != replay` in this build. That refusal is
deliberate: enabling live dispatch should be an edit someone makes on purpose,
in review, not a flag that was already on.

## Switch-off, at any point

| To stop | Do this | Effect |
|---|---|---|
| immediately | `touch $stop_file` | the next check returns `STOP` **before** any runner starts |
| the schedule | disable the workflow or timer | no new events |
| permanently | revoke the credential | runners cannot authenticate |
| one task | set its status to `STOPPED` in the store | the controller treats it as terminal |

State lives in `state_dir`, not in this repository. Deleting it resets the
controller and loses history; it does not touch the repo.

## What is still not covered, stated rather than implied

- **No real AI round has been executed by this controller.** The replay uses
  scripted doubles. Everything above `REPLAY_VERIFIED` is untested.
- **No trigger is installed**, so nothing runs unless a human starts it.
- The guard validates that a review record is *well formed and bound to the
  right head and reviewer*. It cannot tell whether the review is *true*. Only a
  real independent reviewer does that, and two runs of the same model are not
  independent sources.
- Runner isolation relies on a fresh clone per run. Running untrusted PR code
  needs the container as well, which is present but not wired in here.

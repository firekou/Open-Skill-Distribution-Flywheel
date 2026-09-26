# Agent collaboration stack — pilot response

**Responding to:** `reviews/AGENT_GOVERNANCE_STACK_SELECTION_2026-09-18.md` (main, `9e80c8a`)
**Date:** 2026-09-18
**Status: PARTIAL — install verified, orchestration NOT verified.** This is not an adoption
recommendation and does not change the benchmark's BLOCKED state.

---

## What I actually ran, and what it showed

| Step | Result |
|---|---|
| `uv tool install omnigent` | **Succeeded.** `omnigent 0.14.0 (built 2026-09-15T12:56:13Z)` |
| `omnigent --version` / `--help` | **Succeeded.** Harness subcommands present: `claude`, `codex`, `polly`, `debby`, `goose`, `hermes`, `kimi`, `kiro`, `opencode`, `pi`, `agy` |
| `omnigent config list` | **Succeeded.** `Credentials (by harness): none configured yet` |
| `omnigent setup` | **NOT RUN** — see the stop point below |
| `omnigent polly` / any agent run | **NOT RUN** — would call paid models |

**Evidence authority: OBSERVED and VERIFIED for install and CLI surface. Nothing about
orchestration, handoff, review binding or recovery is TESTED, let alone REPRODUCED.**

---

## Two corrections to the selection document

### 1. The Polly install instruction is out of date for 0.14.0

The document says to obtain `examples/polly/` from an upstream checkout and run
`omnigent run examples/polly/`, and correctly warns that installing the Python package will not
make that directory appear in your project.

**In 0.14.0 that step is unnecessary.** Polly is bundled. `omnigent polly --help` reads:

> *"Shorthand for `omnigent run` on the packaged polly agent — the default agent `omnigent run`
> launches when a Claude credential is configured."*

So the pilot does not need an upstream checkout for Polly. **The document's caution was right in
principle and wrong on this specific version** — worth correcting before someone follows it and
concludes the install is broken.

### 2. `requires_python >=3.12` is not the blocker it looks like

This host runs Python **3.11.15**, the repository's own target, and the PyPI metadata requires
3.12+. The install still succeeded because `uv` fetched its own Python 3.12 into the tool
environment. **Omnigent therefore runs alongside a 3.11 project without changing the project's
interpreter** — relevant, because the benchmark is pinned to 3.11 and must not be disturbed.

---

## Prerequisites, checked against this host

| Requirement | This host | Consequence |
|---|---|---|
| Python 3.12+ | 3.11.15 present; **uv supplied 3.12 for the tool** | Satisfied, without touching the project interpreter |
| Git | 2.43.0 | OK |
| Node.js 22+ (coding CLI path) | v22.22.2 | OK |
| tmux (native terminal wrapper) | present | OK |
| **bubblewrap (Linux isolation)** | **ABSENT** | **Worktree isolation cannot be exercised here.** The selection document names isolated worktrees as the reason Polly fits our model, so this is the part that most needs a pilot and is precisely the part this host cannot test |

---

## Stop point, and why I stopped there

Pilot spec item 6: *"未有可用的模型用量授權與預算配置時，只做離線測試，不假設聊天訂閱等於任意
API 預算。"*

`omnigent setup` is an interactive credential and model picker. Running it would configure
provider credentials, and any subsequent `omnigent polly` run would spend against them. **No model
budget has been authorised for this work, and a chat subscription is not an API budget.** So the
pilot stops at a configured-but-uncredentialed install.

**This means acceptance scenarios 1–6 in the selection document are all unexecuted.** Not one of
them — a legal small task, a deliberately defective task, a code commit changed after review, an
interrupted and resumed task, a replayed handoff event, a round or evidence limit — has been run.
Those six are the entire substance of the evaluation. **Install success says nothing about any of
them.**

---

## What the pilot would need, stated as work rather than as a conclusion

1. **A model budget decision** (owner). Which provider, which plan, what ceiling. Everything below
   is blocked on it.
2. **bubblewrap**, or an explicit decision to pilot without worktree isolation and to treat the
   isolation claim as untested.
3. **A separate pilot branch.** The selection document asks for one; my standing instruction is to
   develop only on `claude/atk-open-skill-distribution-96e4vv`. **I have not created one**, and
   creating it needs your say-so.
4. **The review-state bridge.** The document is honest that whether Omnigent can watch GitHub,
   trigger roles and write state back "必須實測". I have not tested it. Until it is, the handoff
   this whole exercise exists to automate is the part with no evidence.
5. **Credential separation.** The document's own rule — *"單一憑證給三個 agent，只有提示詞不同，
   仍不是權限隔離"* — is the thing most likely to be quietly violated in a first pilot. The
   executor must not hold write access to the review gate.

---

## One thing I would flag before adopting any of it

The selection document's own contract table is stronger than the tooling question:
`task_id`/`attempt_id`, `spec_commit`/`code_commit`/`reviewed_commit`, separate executor and
reviewer identities, evidence hashes, explicit `decision`/`blocking_findings`/`next_actor`, and
`budget_limit`/`actual_usage` with **unknown recorded as unknown rather than zero**.

**That contract is the governance. The runtime is plumbing for it.** This repository has just spent
four review rounds discovering that a benchmark's guarantees were exactly the ones nobody had
bound to a version — a stale approval applied to new code (R4-05), and a provenance field the
producer never wrote (R4-06). The same failure modes this contract is designed to prevent.

**A runtime that carries the fields but does not enforce them would reproduce those defects at the
orchestration layer**, and it would be harder to see there. I would want the six acceptance
scenarios run — particularly "審查後再改 code commit" and "相同交接事件重送" — before any of this
sits between a reviewer and a merge.

---

## Evidence boundary

**Done:** read `reviews/README.md`, `STATUS.md`, `AGENT_GOVERNANCE_STACK_SELECTION_2026-09-18.md`
and `.claude/skills/executive-review-gate/SKILL.md`; installed Omnigent 0.14.0; inspected its CLI
surface and credential state; checked every named prerequisite against this host.

**Not done:** `omnigent setup`; any agent run; any orchestration, handoff, recovery or review-gate
behaviour; AGT; OMA; branch protection; any measurement of quality, latency or cost; any second
repository.

**Therefore: not deployed, not security-reviewed, not adopted.** Install is verified. Everything
the selection is actually about is not.

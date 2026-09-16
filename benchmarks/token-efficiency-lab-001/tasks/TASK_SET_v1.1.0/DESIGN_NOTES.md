# Task Set v1.0.0 — design notes

Seat: **Task Set Designer**, Token Efficiency Lab 001.
Scope: build the formal task set for workloads A–E. Answer keys are explicitly out of scope
and are built by an independent seat.

> **This file is not a task input.** It says where the traps in each corpus are. The
> answer-key seat should build keys from `tasks/` and `corpora/` alone and should not read
> it; its readers are the Methodology Reviewer, the Red Team, and anyone reproducing the
> set after the keys exist.

---

## 0. Isolation posture, and one disclosure

This seat was deliberately isolated from the identity of the third-party tools under test, so
that no task could be shaped — consciously or not — to suit a known optimisation style.
`environment/PINS.txt`, the LG2 security review and every candidate repository were left
unread.

**Disclosure.** `methodology/METHODOLOGY_v1.0.0.md` had to be read, because the task set must
match the frozen workloads, quality floors and zero-tolerance criteria. Its final section names
two candidates (`rtk`, `headroom`) in the conflict-of-interest declaration. That is the extent
of the exposure: two names, no description of what either tool does, no README, no flags, no
architecture. Nothing about either tool is known to this seat, so nothing about either tool
could be designed for or against. The disclosure is recorded here rather than omitted, because
a benchmark's credibility rests on stating what its designer saw.

Two further precautions follow from the same concern:

* **No generators are committed.** Each corpus was produced by a seeded Python generator held
  outside the repository. Committing them would hand the answer-key seat the ground truth as
  program state rather than making it derive the truth from the artefact, which is the whole
  point of separating the two seats. The frozen artefacts are the corpora themselves, pinned by
  `MANIFEST.sha256`.
* **No ground truth is recorded anywhere in this directory.** `expected_behavior` describes
  observable conduct — which sources a correct run consults, which distinction it draws — and
  never a value.

---

## 1. What every task has in common

Four properties were treated as non-negotiable, because a benchmark that lacks any one of them
cannot support a cost claim.

**Objectively scorable.** Every task ends in a single strict JSON object with a fixed key set.
There is no "write a good summary" task and no free-text field that a judge could grade by
taste. Where a field could invite prose — a reason for an unfilled shift in E-003 — it is an
enumerated string with a stated precedence order, not free text.

**Deterministic and offline.** No task touches the network. Workload C's research corpus is a
local directory. Workload D's tools are served by a stdlib-only script whose responses are
table lookups. Workload B's documents are static. Two runs of the same task on the same corpus
have the same correct answer, forever.

**Not trivially easy.** Every task has at least one trap that defeats the shortest plausible
shortcut, and in most cases the shortcut produces a *complete, confident and wrong* answer
rather than an obvious failure. That matters: a benchmark where the cheap strategy fails
loudly cannot detect an optimisation that quietly degrades quality.

**Tool-neutral.** No task rewards a particular retrieval, compression or routing style. The
tasks reward reading the right thing and applying a stated rule. Where an intervention such as
tool-result filtering genuinely helps, it should help; where it drops the field that decides
the answer, it should be caught. Both directions are live in this set.

---

## 2. Workload A — repository / code analysis

**Corpus.** `corpora/repo_ledgerline/` — 75 files, ~5.9k lines, 394 module-level functions
across eight packages in a layered pipeline (`util` → `storage` → `core` → `ingest`/
`transform` → `plugins` → `api` → `cli`), plus a `tests/` tree and a `getattr` dispatch module.
Function names are globally unique by construction, so a bare name resolves to exactly one
definition and a name-based analysis is *sound* — the difficulty is never disambiguation, it is
always the graph.

**Tasks.** Reverse reachability to a sink (A-001), unreferenced symbols (A-002), a cross-cut of
decorator form and raise-site reachability (A-003), and strongly connected components (A-004).
Each demands the whole call graph; none can be answered from a single grep.

**Deliberate difficulty.**

* The sink `execute_raw_sql` is reached through chains several edges deep, and a number of
  functions that do *not* call it mention it in a docstring. A grep for the name gets the
  wrong set in both directions.
* A near-twin symbol, `execute_raw_sql_dry_run`, exists in a different module.
* `ledgerline/dynamic.py` names both symbols in string literals resolved by `getattr`. The
  rules declare these to be data; a run that treats them as edges over-reports.
* A-002's dead set is protected by two decoys: some unreferenced functions are named in another
  function's docstring, and several are imported by files under `tests/`. The rules exclude both.
* A-003 splits on two independent axes. The `retryable` decorator is used both bare and called,
  so a regex for `@retryable(` misses the bare-form functions; a look-alike `retryable_v2` from the
  legacy plugin shim catches a loose regex. On the raise side there is a commented-out
  `raise TransientError`, a `raise TransientError` inside a string literal, and an
  `except TransientError:` handler — none of which is a raise.
* A-004's components include intra-module cycles and cross-module cycles whose edges
  exist only through imports written *inside function bodies*. A module-header-only import scan
  misses them entirely.

**Scoring.** Set F1 against the key, with a 0.05 penalty for a self-inconsistent `count`.
A-004 scores components as all-or-nothing sets: a nearly-right component is not a right
component, and exact matching keeps two judges from negotiating partial credit.

**Expected failure modes.** Over-reporting from docstring and dispatch-string matches;
under-reporting from missed function-local imports; and, most interestingly for the H2
hypothesis, a filtered or compressed tool-result path that drops decorator lines or import
lines and silently loses edges. The A-001 scope splits close to evenly between reaching
and non-reaching functions, so answering "all" or "none" scores about 0.5 F1 rather than
looking plausible.

---

## 3. Workload B — long-document extraction

**Corpus.** Three documents, deliberately different in shape: a consolidated services agreement
(179 KB, ~27k words), an annual reliability report (143 KB, ~22k words) and a protocol
specification (219 KB, ~33k words). Filler prose is synthetic and, in the agreement, carries no
digits at all, so no filler sentence can be mistaken for a payload value.

**Deliberate difficulty — all three are *precedence* problems, not *search* problems.**

* **B-001** puts the same commercial term in three places: the body, a Schedule C summary table
  that restates several terms incorrectly, and a set of amendments. Not all of the amendments
  are in force on the as-of date: at least one post-dates it. A run that applies every amendment,
  or that trusts the summary table, produces a complete and wrong object. Schedule B outranks
  the body, but only for service levels, so blanket precedence in either direction is wrong.
* **B-002** places the correction notices roughly 120 KB after the register they correct, so
  both ends of the document have to survive. Some corrections change an incident's severity, and
  set membership is decided *after* corrections, so incidents both enter and leave the answer
  set as a result. A run that filters first and corrects second gets a
  different set, not merely different values.
* **B-003** hides the discrimination in an answer whose naive version has the same
  number of records: as many requirements are promoted to MUST by the errata as are demoted
  away from it, so the count matches while the membership does not. The `MUST` / `MUST NOT`
  distinction is a second, independent trap, and `level_source` forces the errata semantics
  (relevel vs withdraw vs clarify) to be read rather than skimmed.

**Scoring.** Field-level exact match with stated normalisation. Field counts were chosen so
that the frozen 97% floor permits at most one or two slips rather than demanding perfection
from a 24-cell answer: B-001 has 36 fields, and B-002 and B-003 have well over a hundred cells each.

**Expected failure modes.** Applying an out-of-time amendment; trusting a summary table over
the operative clause; correcting after filtering; and context-window truncation that drops the
errata or the correction notices — which is precisely the H4 signal this workload should expose
when C3 compaction is applied.

---

## 4. Workload C — multi-source research

**Corpus.** `corpora/research_c/` — 50 files, ~150 KB, deliberately kept *small per file and
numerous* so the workload is aggregation-bound rather than context-bound: 11 release notes, 8
award bulletins, a registry CSV, 5 errata, 3 correction notices, 2 retraction notices, 7 vendor
blog posts and 12 forum threads, plus `SOURCE_INDEX.md` carrying the tier of every file and the
authority order.

**Deliberate difficulty.**

* **Three unrelated subject areas share one directory.** Roughly two thirds of the files are
  distractors for any given task, so retrieval has to discriminate, not just fetch.
* **The low-authority sources are confidently wrong.** Forum threads assert flag versions,
  plugin minimums and funding totals in the register of someone who was there. Under the stated
  authority order they never decide anything; C-003 additionally requires them to be *found and
  listed* as contradictions, so they cannot be filtered away early.
* **Corrections are indirection, not correction in place.** Flags are contradicted by errata
  that name the release note they correct; projects have corrected or retracted awards; plugins
  have their registry row overridden by an erratum. A run that reads only the highest-tier
  source for each subject gets several project totals wrong.
* **Nulls are real answers.** Many flags are never removed; the correct value is `null`, and a run that guesses a removal version is wrong rather than incomplete.

**Scoring.** Two numbers. `traceability` is the zero-tolerance criterion: every reported value
must cite a file that literally states it, and an empty citation list counts as an unsupported
citation. `coverage` is cell-level exact match and is the reported `quality_score`. A run that
cites the file it actually read but which states a *different* value fails traceability — this
is the specific pathology (citation laundering) that the frozen 100%-traceable floor exists to
catch.

**Expected failure modes.** Citing the index instead of a source; citing a superseded release
note for an erratum-corrected value; summing bulletins without sweeping for notices; and, under
C2 result filtering, dropping the erratum files because they are short and look like
boilerplate.

---

## 5. Workload D — MCP-heavy multi-tool task

**Corpus.** `corpora/mcp_toolset/` — 84 tools across 12 fictional servers in 25 declared
families (55 KB of schema, a meaningful fixed context load, which is the H1 probe), a
deterministic stdlib-only server, and a fixture store.

**The central design problem** was making wrong-tool selection *genuinely possible* without
making it a trick. The answer:

* **Near-identical siblings that both work.** Every contested family contains a tool that
  returns the resolved, binding, current value and one or more siblings that return a template,
  a cache, a published default, or a raw figure. Every sibling returns well-formed, internally
  consistent, plausible data. Nothing errors; nothing hints. `rota.get_nominal_shift` names a
  real engineer. `vulndb.get_image_findings_by_tag` returns a real scan. `tickets.get_ticket_sla`
  returns a real target.
* **Each decoy flips an output.** D-001's template names a different engineer; D-002's stale
  digest yields a different critical count *and* a different top advisory; D-003's billing date
  falls in a different fiscal year from the ship date, changing every field; D-004's raw error
  budget is negative where the reported one is positive, and the queue-default target turns a
  breach into a pass. No decoy produces a nearly-right answer.
* **The distinction is always stated in the tool description.** A run that reads descriptions
  can choose correctly; a run that pattern-matches names cannot. That is the measurement.
* **Discovery is free.** Three `catalog.*` tools let a run inspect the toolset without
  committing to a data tool, and calls to them never count as wrong-tool invocations. Without
  this, the zero-tolerance criterion would punish careful behaviour and reward guessing — and
  it would make the C1 schema-deferral condition unmeasurable.

**Scoring.** `contested_families` is named per task in `failure_condition`; a wrong-tool
invocation is any call into a contested family that is not in the key's required set. If the
required set contains no member of a contested family, every call into it is wrong — which is
how the ordinary-calendar decoys in D-003 are caught without singling them out and thereby
leaking which tool is right. Calls outside contested families are recorded as extraneous and do
not affect the score, so a run is not punished for reasonable exploration in an unrelated
domain. The tool-call record is written by the server, not by the agent.

The fixture directory is declared out of bounds in every D prompt and reading it is an outright
failure: a run that reads the backing data can answer without selecting a tool at all, which
would make the measurement meaningless.

**Expected failure modes.** Name-driven selection (`get_ticket_sla` looks like the SLA of a
ticket); stopping at the first tool that returns a plausible value; and, under C1, deferring so
much schema that the sibling distinctions — which live in the descriptions — never enter
context at all. That last one is the interesting result either way.

---

## 6. Workload E — long multi-turn agent workflow

**Corpus.** `corpora/workflow_e/` — six small structured files (parts catalogue, vendors,
sites, procurement policy, services, staff roster, shifts). Deliberately small: workload E must
measure *context accumulation across turns*, not context size within a turn.

**Structure.** Each scenario front-loads its constraints (turns 1–7), spends the middle of the
conversation on substantive derivable work, injects one or two revisions mid-stream, and asks
for a single strict JSON deliverable at the end. 18, 16 and 20 turns.

**Deliberate difficulty.**

* **The first constraint is load-bearing at the first work turn and again at the last.** In
  E-001 the excluded vendor owns the obvious catalogue entry for the very first item requested,
  so turn 7 cannot be answered correctly unless turn 3 is still in force — and the same
  constraint must survive eleven more turns to the deliverable.
* **Revisions must land on the final state, not an intermediate one.** E-001 changes a quantity
  at turn 14 and removes a line at turn 15; E-002 drops a service at turn 9 that nothing depends
  on, so re-including it is invisible unless the constraint was remembered; E-003 removes the
  last eligible person from two shifts at turn 12.
* **The honest answer is the uncomfortable one.** E-001's cap is set below the correct total, so
  the correct behaviour is to report the breach — silent trimming to fit is a counted violation.
  E-003's turn 12 makes at least one shift unfillable, so the correct behaviour is to report it
  unfilled — filling them with an ineligible person is a counted violation. A run whose early
  constraints have decayed tends to produce the *comfortable* answer, which is exactly the
  signal.
* **One constraint governs prose rather than data.** E-002 forbids two common words. It is the
  constraint most likely to decay first, and it is trivially checkable.
* **One update is a deliberate no-op.** E-003 turn 16 raises a limit that was not binding. A run
  re-deriving from scratch may over-react to it.

**Scoring.** Two numbers. `completion` is cell-level exact match on the final deliverable.
`constraint_violations` is counted over *every* reply in the run, not just the last, and each
check is mechanical — a regex, a set membership, a sort order, a numeric comparison against the
corpus. Zero violations is the frozen zero-tolerance criterion.

**Expected failure modes.** Constraint decay under long context, which is the H4 signal;
over-eager compaction (C3) discarding the turn-3 style constraints because they read as
pleasantries; and revision drift, where the agent applies turn 14 to a table it has already
summarised away.

---

## 7. What I am least sure about

Recorded here so the Methodology Reviewer and the Red Team can attack it directly.

1. **Workload A's answer sets are large, A-001's most of all.** Its answer list makes
   output tokens a non-trivial share of the run cost, which slightly contaminates the cost
   measurement with a "how verbose is the required answer" term that is constant across
   conditions but not across tasks. Scoping A-001 to three packages was the compromise; scoping
   it further would have made guessing viable.
2. **Workload D's zero-wrong-tool rule punishes exploratory calls inside a contested family.**
   I mitigated it by making `catalog.*` free and by stating the rule in the prompt, so it is a
   declared discipline and not a trap. It may still read as harsh, and a run that calls one
   sibling then self-corrects scores identically to one that never noticed. That is what the
   frozen criterion says; it is not what everyone would mean by it.
3. **Several `task_success` thresholds are relative to a baseline C0 median that does not exist
   yet** (A×4, C×3, per the frozen §6 wording "≥95% of baseline's correct set"). If baseline
   quality turns out low, the bar moves down with it and a weak treatment can pass. I did not
   substitute an absolute floor, because the methodology is frozen and inventing one would be a
   methodology change by the wrong seat — but it should be raised at LG5 before any result is
   read.

Two smaller ones, for completeness: workload E's harness contract (deliver turns one at a time,
never restate) is an instruction to the runner rather than something the task file can enforce,
so a sloppy harness could silently invalidate the whole workload; and the C-003
`contradicted_by` field assumes a blog or forum statement about a plugin minimum is always
recognisable as a minimum-version claim, which is true of this corpus by construction but rests
on the key seat reading those sentences the same way I wrote them.

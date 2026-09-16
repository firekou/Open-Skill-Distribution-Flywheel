# Task Set v1.1.0 — design notes

Seat: **Task Set Designer**, Token Efficiency Lab 001.
Scope: build the formal task set for workloads A–E. Answer keys are explicitly out of scope
and are built by an independent seat.

**v1.1.0.** This file was written for v1.0.0 and has been revised, not rewritten. Passages that
v1.0.0 got wrong are corrected in place and marked; the repairs made in v1.1.0 are described
where they belong, and §8 is new. `CHANGELOG_v1.0.0_to_v1.1.0.md` is the authoritative record of
what changed.

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

**One exception, declared in v1.1.0.** `shortcut_probe/probe_b002.py` is committed, and it
contains an extractor capable of producing a B-002 answer. RT-03 was BLOCKING and a repair to a
blocking finding is worthless if it cannot be re-measured, so the instrument had to ship with the
result. Three things limit the damage: the corpus **generator** is still not committed, so the
ground truth is still only recoverable by reading the artefact; `SHORTCUT_PROBE_RESULTS.md`
reports aggregate scores and never the record set; and the script's header states that the Answer
Key Builder derives B-002 independently and that the script, not the key, is wrong if the two
disagree. A reviewer who thinks the trade was wrong should say so — it is a judgement, and it is
listed as one in the changelog.

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
lines and silently loses edges.

**Corrected in v1.1.0 (RT-14).** v1.0.0 claimed here and in A-001's `notes` that the blanket
answer scores "about 0.5 F1". It does not. A-001's scope holds exactly 126 functions and exactly
63 of them reach the sink, so "all of them" scores precision 0.5, recall 1.0, **F1 = 0.6667**, and
"none of them" scores 0. The stated safety margin was 17 points too generous. That margin now
matters less than it did, because A's floor is absolute at 0.95 in v1.1.0 rather than relative to
a C0 median that could have drifted down to meet 0.6667 — the RT-05 cliff.

**Also in v1.1.0 (RT-17).** The `ledgerline` corpus did not import: `retryable`, `TransientError`,
`ConfigError`, `instrumented` and `deprecated` were imported across the tree and defined nowhere,
and 36 of 75 modules failed to import. `retryable_v2` *was* defined, which made the asymmetry
actively misleading — a run reasoning "this import must be wrong, so the decorator must be
`retryable_v2`" loses A-003 entirely. All five names are now defined and every module imports. The
four A answer sets are byte-identical before and after; only the module-level function count moves
from 394 to 397, all three additions being under `ledgerline/util/`, which leaves A-001's 126-function
scope and its 63/63 split untouched. Rule R2's claim that the corpus contains no nested functions
was already false in v1.0.0 and has been corrected rather than preserved.

---

## 3. Workload B — long-document extraction

**Corpus.** Three documents, deliberately different in shape: a consolidated services agreement
(179 KB, ~27k words), an annual reliability report (**161 KB in v1.1.0**, rebuilt — see below) and
a protocol specification (219 KB, ~33k words). Filler prose is synthetic and, in the agreement, carries no
digits at all, so no filler sentence can be mistaken for a payload value.

**Deliberate difficulty — all three are *precedence* problems, not *search* problems.**

* **B-001** puts the same commercial term in three places: the body, a Schedule C summary table
  that restates several terms incorrectly, and a set of amendments. Not all of the amendments
  are in force on the as-of date: at least one post-dates it. A run that applies every amendment,
  or that trusts the summary table, produces a complete and wrong object. Schedule B outranks
  the body, but only for service levels, so blanket precedence in either direction is wrong.
* **B-002 — rebuilt in v1.1.0 (RT-03).** v1.0.0's claim that the correction notices sat "roughly
  120 KB after the register" was false: the register began at byte 127,608 and the notices at
  131,705 of 146,666, four kilobytes apart, both inside the last 13%. Everything the task needed
  was therefore in the tail, and the 86% in front of it was narrative the task forbids using. A
  condition that discarded that 86% scored **identically to reading the whole document, at 15% of
  the tokens** — measured, not argued: see `SHORTCUT_PROBE_RESULTS.md` §2. H2 and H4 would both
  have read that artefact as a confirmed saving with no quality cost. It was the single finding
  most likely to produce a *wrong published result* rather than a failed measurement.

  The document was rebuilt so that the evidence is distributed by construction. The rules that
  decide contested values are at 2% and are no longer restated in the prompt. The base records are
  in four per-quarter registers at 22%, 40%, 60% and 80%. Two superseding layers — Register
  Amendments and Correction Notices — are at 95% and 98%, and they interact: two pairs name the
  same incident **and** the same field, so the precedence order decides which wins; one pair names
  the same incident and different fields, so both apply; and one amendment withdraws an incident
  that would otherwise be in the answer, which only §1.4 explains. Between the registers sit 48
  per-incident narratives that each state a severity and an approximate duration the precedence
  demotes, plus monthly availability tables — on-topic content that no position-based filter can
  tell from payload.

  The result, measured: reading only the last 15% goes from 1.0000 to **0.0000**; an ends-only
  compaction from 1.0000 to **0.0000**; a fixed truncation to half the document to **0.2421**,
  emitting 8 records where the reference has 26 and one that does not belong at all — a complete,
  confident and wrong answer rather than a visible refusal. **Content-selective retrieval still
  scores 1.0000 on 5.2% of the bytes.** That last number is the point: the repair had to avoid
  manufacturing difficulty by forcing full-document reading, which would have biased the
  measurement in the opposite direction. B-002 now rewards *selection* and punishes *truncation*,
  which is the distinction H2 and H4 are actually about.
* **B-003** hides the discrimination in an answer whose naive version has the same
  number of records: as many requirements are promoted to MUST by the errata as are demoted
  away from it, so the count matches while the membership does not. The `MUST` / `MUST NOT`
  distinction is a second, independent trap, and `level_source` forces the errata semantics
  (relevel vs withdraw vs clarify) to be read rather than skimmed.

**Scoring.** Field-level exact match with stated normalisation. Field counts were chosen so
that the frozen 97% floor permits at most one or two slips rather than demanding perfection
from a 24-cell answer: B-001 has 36 fields, and B-002 and B-003 have well over a hundred cells each.

**`count` in v1.1.0 (RT-10).** v1.0.0 subtracted a flat 0.05 for a `count` that disagreed with the
array it counted, and applied it before the 0.97 floor test, so a **perfect** B-002 answer with a
wrong `count` scored 0.95 and failed outright. That is a designed-in cliff and it was not intended.
The ruling is that a bookkeeping slip is not equivalent to a 3%-wrong extraction: `count` is now
scored as exactly one comparable cell, the same weight as any other single emitted value. The floor
stays at 0.97 and the effect is stated inside the task text so a reviewer can weigh it — a wrong
`count` costs precisely one cell of tolerance below the floor, instead of nine. This is a change in
the direction that raises the pass rate, which is the direction to be most suspicious of; it is
recorded as such in the changelog.

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
* **Nulls are real answers.** Many flags are never removed; the correct value is `null`, and a run that guesses a removal version is wrong rather than incomplete. A null is not a claim that needs a citation, which v1.1.0 states explicitly rather than leaving to the judge (UG-14 and the claim-to-source mapping).
* **`contradicted_by` is a fact about the corpus, not about authority (RT-16).** v1.1.0 settles the
  fork: every file of every tier that states a different minimum version belongs in it, including
  the registry export itself for a plugin whose registry row an erratum has corrected. The
  alternative reading — low-authority files only — was worth 6.25 points of the primary measurement
  on a coin flip, and it would have made the field a duplicate of `governing_source_tier`.

**Scoring, rebuilt in v1.1.0 (RT-04).** v1.0.0's citation rule said "cite a file only if that
file actually states the value you are reporting". Two forum threads state the **correct**
`introduced_in` for two of the sixteen flags. Citing one of them was therefore *literally
compliant* and scored as a zero-tolerance traceability breach — and the answer key recorded those
files itself, so the key contradicted the metric it was keyed against. Worse, the rule was
one-directional: an incomplete `sources` list cost nothing, so a run that read 16 of 50 files
strictly dominated one that read 50. That is a retrieval-width penalty wearing a quality
criterion's clothes, and it pointed the same way as the B-002 defect.

The rule now separates three things that v1.0.0 ran together, and says so in the task:

* **authority** — a file's tier, and which file *governs* a value once the override rules have run;
* **correctness** — whether a file happens to print the right characters, which the rule now says
  in words has no bearing on whether it may be cited;
* **support** — whether a cited file governs at least one value of the record it is attached to and
  literally states it.

Each C task then gives a **claim-to-source mapping** (which file governs `introduced_in`,
`removed_in`, a project total, a plugin minimum) and restates the conflict precedence for
citations. The ruling on the forum threads is: a low-authority file that states the correct value
is **not** a valid citation, and that is now stated in advance rather than sprung.

**Symmetry.** `sources` must name every governing source and no other file. A governing source
left out is a *missing citation* and costs what an unsupported one costs. Breadth and narrowness
are now the same kind of error at the same price. This makes workload C **harder** than v1.0.0,
because incompleteness used to be free; that is the honest consequence of removing an asymmetry
that favoured narrow retrieval, and the lever for making C easier, if the Lab wants that, is the
coverage floor rather than the citation rule.

`coverage` remains cell-level exact match and remains the reported `quality_score`. Citation
laundering — citing the file you actually read, which states a different value — still fails, as
it must.

**Expected failure modes.** Citing the index instead of a source; citing a superseded release
note for an erratum-corrected value; summing bulletins without sweeping for notices; and, under
C2 result filtering, dropping the erratum files because they are short and look like
boilerplate.

---

## 5. Workload D — MCP-heavy multi-tool task

**Corpus.** `corpora/mcp_toolset/` — **85 tools in v1.1.0** across 12 fictional servers in **28
declared families** (a meaningful fixed context load, which is the H1 probe), a deterministic
stdlib-only server, and a fixture store.

**The central design problem** was making wrong-tool selection *genuinely possible* without
making it a trick. The answer:

* **Contested families now contain only competing tools (RT-11, v1.1.0).** v1.0.0's
  zero-tolerance criterion keyed on *family membership*, but several tools inside contested
  families returned nothing that competed with the task's question: `rota.search_rota` ("cannot
  tell you who is on call"), `registry.search_images` ("returns repositories, not digests"),
  `vulndb.search_advisories`, `billing.search_orders` ("order stubs without dates"),
  `calendar.get_iso_week`, `calendar.get_month_boundaries`, `metrics.get_slo` (a target, not a
  remaining budget) and `tickets.get_queue`. One diligence call to any of them failed the task
  outright. Since exploration propensity is precisely what the C1 deferred-schema condition
  changes, that converted an intervention-correlated behaviour into a quality failure — the worst
  kind of confound. All eight have moved to uncontested families, and
  `calendar.get_calendar_period` was added so that `calendar-period-resolution` is a real
  two-member decoy family rather than a family of one. Every remaining member of every contested
  family was called live and returns a well-formed, plausible, competing payload. The four D
  answers and all four `required_tools` sets are unchanged.
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

**What a workload-D wrong-tool failure is evidence about, and what it is not (RT-20).** Every
decoy announces itself twice: once in its `description` ("Reflects the published rotation only")
and again in its response payload ("Template value. Approved overrides are NOT applied."). This
was kept in v1.1.0 deliberately, because removing the payload note changes no score — the
zero-tolerance criterion has already fired by the time the payload is read — while the note is
what lets an auditor, and the Answer Key Builder, verify which sibling is which without trusting
`tools.json`. The consequence has to be reported, and it is this: **a workload-D wrong-tool
failure measures whether the one distinguishing sentence in the tool's description reached the
model's context. It measures nothing else.** It is not evidence about judgement under ambiguity,
because there is no ambiguity once the description is read; and it is not evidence about whether
a run can recover from a mistake, because the criterion fires before recovery is possible. That
is exactly the H1 question — does deferring schema cost you the distinctions? — so the design is
fit for H1 and must not be quoted as evidence for anything wider.

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

**Two coin flips removed in v1.1.0.** E-001's freight rounding (RT-06) was not determined by the
task: carrying full precision and rounding once gave `1197.38`, rounding each vendor's share first
gave `1197.39`, monetary values compare as exact strings, and three of nine scalar cells flipped —
a correct, policy-compliant answer scored 0.9444 against a 0.95 floor. `procurement_policy.md` P1
now names the four points at which rounding happens and declares every per-vendor, per-line and
per-category apportionment an intermediate value; P4 says the freight charge is one component
total summed from full-precision products. The two readings can no longer coexist. Separately, and
not from the Red Team's list, turn 7 now carries a standing instruction authorising substitution
when the obvious catalogue entry belongs to an excluded vendor: without it, a run that refuses to
substitute and asks the user — good behaviour under turn 3 — scored about zero on the BOM.

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
3. ~~**Several `task_success` thresholds are relative to a baseline C0 median that does not exist
   yet**~~ — **resolved in the task text in v1.1.0, and the concern was justified.** The Red Team
   demonstrated the cliff: at a C0 median of 0.70 for A-001, the zero-work blanket answer (0.6667)
   returned `task_success: true`. A-003 had the same shape below a C0 median of 0.638. The
   direction was strictly wrong — the worse the baseline, the easier it became for an intervention
   that reads nothing to claim that quality held. v1.1.0 writes the absolute floors approved for
   this version into the seven affected metrics: A `quality_score >= 0.95`, C `coverage >= 0.90`
   with `traceability == 1.00`. That also removes the two-pass scoring order and the
   C0-before-A/C run dependency that the relative form forced and that the run matrix never
   described. **What is not resolved is not this seat's to resolve:** `METHODOLOGY_v1.0.0.md` §6
   still says "≥95% of baseline's correct set", and a frozen methodology can only change through a
   `METHODOLOGY_CHANGE_REQUEST` and a new version file. Until that lands, the methodology and the
   task text disagree, and the task text is what the judge reads.

Two smaller ones, for completeness: workload E's harness contract (deliver turns one at a time,
never restate) is an instruction to the runner rather than something the task file can enforce,
so a sloppy harness could silently invalidate the whole workload; and the C-003
`contradicted_by` field assumes a blog or forum statement about a plugin minimum is always
recognisable as a minimum-version claim, which is true of this corpus by construction but rests
on the key seat reading those sentences the same way I wrote them.

---

## 8. What v1.1.0 did not fix, and what it made harder

New in v1.1.0. Written so that nobody reads a clean changelog as a clean bill of health.

**Still open, and blocking.** `required_evidence` has no producer (RT-01). v1.1.0 made this
*larger*, not smaller: every task now names corpus-hash evidence on top of what v1.0.0 already
needed, and every one of those conditions fails closed on absence **or emptiness**. Naming the
evidence is the part a task file can do; producing it is the harness owner's, and nothing can be
scored until it exists. The alternative — leaving thirteen outright-failure conditions that
nothing evaluates, so that a corpus-rewriting optimisation scores clean — is the one option that
was not available.

**Still open, elsewhere.** Workload E's zero-tolerance criterion still fails open on
present-but-empty evidence inside `judge.py` (RT-02), and `part_id_pattern` is still a
Runner-supplied regex that a plausible anchored form silently disarms. v1.1.0 narrowed the blast
radius — E-003's V5 no longer reads anything from `required_evidence`, so one of the three
affected checks can no longer be switched off without anyone noticing — but the other two are the
judge seat's. Nothing asserts that workload E's turns are actually delivered (RT-13), and the
`protocol` block saying so is an instruction to a runner, not something a task file can enforce.

**Three tasks got harder, on purpose.**

* **Workload C.** The new citation rule requires `sources` to be complete as well as correct.
  Under v1.0.0 an incomplete citation list was free, which is why a narrow run dominated a broad
  one. Removing that asymmetry necessarily costs the narrow run. If C's pass rate comes in low,
  the first hypothesis should be this rule, and the lever is the coverage floor, not the rule.
* **Workload A and C floors.** Absolute floors of 0.95 and 0.90 are strictly higher than the
  relative ones wherever a C0 median lands below 1.0, which is everywhere anyone expects it to
  land. A task that passed under v1.0.0's arithmetic may fail under v1.1.0's.
* **B-002.** The document is genuinely harder to answer from a truncated view. That is the repair.
  It is not harder to answer from a *selected* view, which is the part that keeps it fair.

**One task got easier, and it should be watched.** The `count` ruling (RT-10) raises the B-002 and
B-003 pass rates for answers that were otherwise perfect. The effect is quantified inside each
task's own metric text rather than only here, so a reviewer weighing the result does not have to
go looking for it.

**A measurement discontinuity.** B-002's document grew from 147 KB to 161 KB and its evidence
moved. Within v1.1.0 every condition reads the same document, so no comparison inside this task
set is affected. But **no v1.0.0 run may be pooled with a v1.1.0 run**, for B-002 or for anything
that aggregates across tasks, and the dry-run figures collected against v1.0.0 are not baselines
for v1.1.0.

**One thing checked and deliberately left alone.** The Builder's warning that a wrong value in
workload C "fails the task twice" — lowering coverage and breaching traceability together — was
overstated in v1.0.0 and is not reintroduced here: a citation is supported when the cited file
governs *at least one* value of its record, so a record with one wrong field keeps its
traceability provided another field is right and cited. Nobody should fix a problem that is not
there.

**The isolation posture held.** `environment/PINS.txt`, `environment/CANDIDATE_RUNTIME_PROFILES.md`,
`reports/LAB_001_LG2_SECURITY_REVIEW.md` and `registry/` were not read during the v1.1.0 repair,
exactly as in v1.0.0. The disclosure in §0 — two candidate names, seen in the frozen methodology's
conflict-of-interest section — is unchanged and remains the whole of the exposure. Every repair
above was driven by a named finding in `RED_TEAM_REVIEW.md` or `SCORING_SPEC.md` §9, which is the
audit trail that makes "not shaped for a candidate" checkable rather than merely asserted.

# Lab 001 — Task Set v1.1.0

Formal task set for **Token Efficiency Lab 001**, covering the five frozen workloads A–E of
`methodology/METHODOLOGY_v1.0.0.md`.

**v1.1.0 is a repair of v1.0.0**, built from `RED_TEAM_REVIEW.md` §2 and from the
underspecified-metric table in `SCORING_SPEC.md` §9. `TASK_SET_v1.0.0/` is immutable and was not
touched. Every change is listed, with before/after quotes, in
**`CHANGELOG_v1.0.0_to_v1.1.0.md`** — read that before reading a task file, and read
**`SHORTCUT_PROBE_RESULTS.md`** before believing that B-002 measures what it claims to.

* **17 tasks** — A×4, B×3, C×3, D×4, E×3.
* **All data is synthetic.** Every corpus in this directory was generated for this benchmark.
  No customer data, no proprietary content, no scraped third-party text. Every organisation,
  person, service, product, contract and advisory named here is fictional.
* **Fully offline.** No task requires network access. Workload C's "multi-source research"
  reads a local corpus; workload D's tools are served by a local deterministic script.

## What changed in v1.1.0, in one paragraph

B-002's document was rebuilt so that a run which discards a fixed fraction of it loses necessary
facts while one that selects the right passages does not (RT-03, measured). Workload C's citation
rule was replaced with one that separates authority, correctness and support, states a
claim-to-source mapping, and is symmetric between citing too broadly and citing too narrowly
(RT-04). Two ambiguities that could each fail a correct run — E-001's freight rounding and
B-001's two contested fields — were settled in the corpus and in the task text (RT-06, RT-07).
The workload-D contested families were narrowed to tools that genuinely return a competing answer
(RT-11). The `ledgerline` corpus now imports (RT-17). Seventeen places where the metric was
underspecified and the judge had to invent a rule now state the rule in the task text. The seven
baseline-relative quality floors were replaced with the absolute floors approved for v1.1.0.

## Layout

```
TASK_SET_v1.1.0/
  README.md                          this file
  CHANGELOG_v1.0.0_to_v1.1.0.md      every change, per task, with before/after quotes
  SHORTCUT_PROBE_RESULTS.md          the RT-03 measurements
  shortcut_probe/probe_b002.py       the script that produced them
  DESIGN_NOTES.md                    how each workload was built and where it is expected to break
  RED_TEAM_REVIEW.md                 the v1.0.0 review, carried over unchanged as the work list
  SCORING_SPEC.md                    the v1.0.0 spec, carried over UNCHANGED — see "Precedence"
  tasks/A/A-00n.json                 task definitions, one file per task
  tasks/B/ … tasks/E/
  corpora/
    repo_ledgerline/                 workload A — synthetic Python repository, 75 files, now importable
    docs_b/                          workload B — three long synthetic documents
    research_c/                      workload C — 50 synthetic sources across four authority tiers
    mcp_toolset/                     workload D — 85 tool schemas, deterministic offline server, fixtures
    workflow_e/                      workload E — CSV/Markdown inputs for the multi-turn scenarios
  answer_keys/                       THE v1.0.0 KEYS, STALE — see answer_keys/STALE_v1.0.0_KEYS.md
```

## Precedence between this directory's documents

`SCORING_SPEC.md` here is the **v1.0.0 spec, carried over unmodified**, because the Task Set
Designer does not own it. Its own rule applies: **where the spec disagrees with a task file, the
task file wins.** Several v1.1.0 task texts now override it deliberately — workload C's
traceability formula, workload B's and workload A's `count` rules, workload D's treatment of extra
keys, E-003's V5, and the quality floors for A and C. `CHANGELOG_v1.0.0_to_v1.1.0.md` §4 lists
every one of them as a requirement on the judge seat.

## Answer keys

**The keys in `answer_keys/` are the v1.0.0 keys and must not be used to score a v1.1.0 run.**
They were copied unchanged when this task set was branched, so the Answer Key Builder has the
v1.0.0 derivations to work from. `answer_keys/STALE_v1.0.0_KEYS.md` lists exactly what is stale
and what is verified unchanged (all four A answers; all four D answers). The Task Set Designer
wrote no key and edited none.

No corpus generator is committed, for the reason in `DESIGN_NOTES.md` §0. One exception is
declared and argued there and in the changelog: `shortcut_probe/probe_b002.py` contains an
extractor, because a BLOCKING finding has to be re-measurable.

## Path convention

Every path inside a task file — in `input.corpus_paths`, in the prompt text, and in
`answer_key_reference` — is **relative to this directory** (`TASK_SET_v1.1.0/`). A runner
resolves them against the task-set root, not against the repository root and not against its
own working directory.

## Task file schema

Each task JSON contains exactly these keys, plus an optional `notes`:

| key | meaning |
|---|---|
| `task_id` | workload letter + three digits, e.g. `A-001` |
| `workload` | `A`…`E` |
| `input` | what the agent under test is given: `corpus_paths` plus `prompt`, or for workload E `protocol` plus an ordered `turns` array |
| `expected_behavior` | what a correct run does, described observably — never the answer |
| `answer_key_reference` | relative path where the answer key will live |
| `quality_metric` | the scoring procedure, specified so two judges compute the same number |
| `failure_condition` | what fails the task outright, including the frozen zero-tolerance criteria |

## Evidence the harness must supply

Every v1.1.0 task names the evidence that establishes its outright-failure conditions, and every
one of them **fails closed** when that evidence is absent *or empty*. This is new work for the
harness owner and nothing can be scored until it exists (RT-01 remains open):

| field | who needs it | shape |
|---|---|---|
| `corpus_hashes_before`, `corpus_hashes_after` | all 17 tasks | `{corpus-relative path: sha256}`, taken at the start and at the end of the run |
| `corpus_access_log` | A-001, D-001…4 | list of file paths the run opened, one entry per read |
| `valid_symbols` | A-001…4 | list of fully qualified dotted names that exist under `ledgerline/` |
| `tool_calls` | D-001…4 | the server's audit JSONL, parsed; each object carries `tool` and `family` |

E-003 no longer needs `max_shifts_overrides`: the one override in that scenario is stated by the
task itself.

## Quality floors

Absolute, fixed before any run, identical for every condition:

| workload | floor, per complete task attempt |
|---|---|
| A | `quality_score >= 0.95` against the full answer key, and zero fabricated symbols |
| B | `quality_score >= 0.97` |
| C | `coverage >= 0.90` **and** `traceability == 1.00` |
| D | correct tool and correct answer, zero wrong-tool invocations (the ≥95% cell success rate is the aggregator's, not the judge's) |
| E | `completion >= 0.95` and zero constraint violations across every turn that occurred |

## Running workload D

The tool server is stdlib-only Python 3:

```
python3 corpora/mcp_toolset/server.py list                    # catalogue
python3 corpora/mcp_toolset/server.py describe rota.get_effective_oncall
python3 corpora/mcp_toolset/server.py call <tool> '<json-args>'
python3 corpora/mcp_toolset/server.py mcp                     # JSON-RPC 2.0 over stdio
```

Set `LAB001_TOOL_AUDIT=/path/to/run.jsonl` before starting the server. Every invocation is
appended as one JSON object per line with the tool name, its declared `family` and its
arguments. **That file is the scoring input for the workload-D tool-selection criterion**; it
is written by the server, so the agent under test cannot influence it.

## Running workload E

`input.turns` is an ordered list of user messages. The harness delivers them one at a time and
lets the agent reply to each before sending the next. It must not merge, re-order, skip or
summarise turns, and it must not restate an earlier turn — whether an early constraint survives
to the final turn is exactly what workload E measures. Every reply is scored for constraint
violations, so every reply must reach the judge, not only the last (RT-13).

## Integrity

**There is no `MANIFEST.sha256` in this directory.** The v1.0.0 manifest was removed rather than
carried over: it covered a different tree, and it never covered `answer_keys/`, `SCORING_SPEC.md`,
`DESIGN_NOTES.md` or `README.md` — the RT-12 gap, under which the scoring ground truth could
change after a freeze and `sha256sum -c` would still report OK. The coordinator builds the wider
manifest covering every file whose content can change a score. A run record's `task_version` is
`1.1.0`; its `config_hash` should be the sha256 of that wider manifest, and that manifest has to
exist before any run is executed, not after.

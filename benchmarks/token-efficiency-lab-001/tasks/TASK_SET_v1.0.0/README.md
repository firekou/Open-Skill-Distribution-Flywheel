# Lab 001 — Task Set v1.0.0

Formal task set for **Token Efficiency Lab 001**, covering the five frozen workloads A–E of
`methodology/METHODOLOGY_v1.0.0.md`.

* **17 tasks** — A×4, B×3, C×3, D×4, E×3.
* **All data is synthetic.** Every corpus in this directory was generated for this benchmark.
  No customer data, no proprietary content, no scraped third-party text. Every organisation,
  person, service, product, contract and advisory named here is fictional.
* **Fully offline.** No task requires network access. Workload C's "multi-source research"
  reads a local corpus; workload D's tools are served by a local deterministic script.

## Layout

```
TASK_SET_v1.0.0/
  README.md              this file
  DESIGN_NOTES.md        how each workload was built and where it is expected to break
  MANIFEST.sha256        sha256 of every task and corpus file
  tasks/A/A-00n.json     task definitions, one file per task
  tasks/B/ … tasks/E/
  corpora/
    repo_ledgerline/     workload A — synthetic Python repository, ~5.9k lines, 75 files
    docs_b/              workload B — three long synthetic documents, 143–219 KB each
    research_c/          workload C — 50 synthetic sources across four authority tiers
    mcp_toolset/         workload D — 84 tool schemas, deterministic offline server, fixtures
    workflow_e/          workload E — CSV/Markdown inputs for the multi-turn scenarios
  answer_keys/           NOT IN THIS COMMIT — built by an independent seat (see below)
```

## Path convention

Every path inside a task file — in `input.corpus_paths`, in the prompt text, and in
`answer_key_reference` — is **relative to this directory** (`TASK_SET_v1.0.0/`). A runner
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

## Answer keys

**This directory deliberately contains no answer keys.** They are built by a separate,
independent seat working from the task inputs and the corpora alone, and written to
`answer_keys/<task_id>.json`. The task-design seat did not record ground truth anywhere in
this directory, and the corpus generators are not committed here for the same reason: a key
derived from the generator's internal state would not be an independent key.

Several `quality_metric` definitions reference a *baseline C0 median* (workloads A and C).
That number comes from the executed C0 runs, per methodology v1.0.0 §6, and is not part of
the answer key.

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
to the final turn is exactly what workload E measures.

## Integrity

`MANIFEST.sha256` covers every file in `tasks/` and `corpora/`. Verify with:

```
cd TASK_SET_v1.0.0 && sha256sum -c MANIFEST.sha256
```

A run record's `task_version` is `1.0.0`; its `config_hash` should be the sha256 of
`MANIFEST.sha256` itself.

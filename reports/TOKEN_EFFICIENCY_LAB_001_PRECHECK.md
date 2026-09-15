# Token Efficiency Lab 001 — Precheck (S4 gate G0→G1)

**Date:** 2026-09-15 · **Status:** **PRECHECK ONLY — no run executed, no run authorised**
**Gate position:** G0 claim registered. Requesting **G1 methodology freeze**.

> Per `CLAUDE_EXECUTION_START.md`: the 100-run benchmark does **not** start until
> Editor-in-Chief / ChatGPT review of this document and `reports/TOP30_R3.md`.

---

## 1. Research question and pre-registered hypotheses

**Where do agents waste tokens, and which interventions reduce total task cost without
materially reducing task success?**

| ID | Hypothesis | Pre-registered direction |
|---|---|---|
| **H1** | Large MCP/tool schemas create measurable fixed context overhead | Overhead grows with tool count; deferred exposure or a code-execution pattern reduces it |
| **H2** | Raw intermediate tool results create avoidable variable overhead | Filtering/compression reduces total tokens at an acceptable quality cost |
| **H3** | Model misrouting creates hidden cost via overpowered selection or retry/escalation | A complexity-aware route beats always-frontier on cost at equal quality |
| **H4** | Context accumulation creates avoidable repeated-token cost | Compaction/clearing reduces tokens in long sessions |

**These are hypotheses. They are not ATK claims and must not be quoted as findings.**

**Pre-registered null results are publishable.** If an intervention does not help, or helps on
tokens and fails the quality floor, that is a result and it ships. Writing this down *before*
running is the point: it removes the incentive to quietly drop a disappointing condition.

---

## 2. Frozen run matrix — 100 runs, every one justified

Interventions are tested **singly before any combination**. Three repetitions per cell is the
minimum that exposes variance without manufacturing runs.

### 2.1 Workloads

| ID | Workload | Why it is in the set |
|---|---|---|
| **A** | Repository / code analysis | Many tool calls, large file payloads |
| **B** | Long-document extraction | Single large context, low tool count |
| **C** | Multi-source research | Many small results, high aggregation |
| **D** | MCP-heavy multi-tool task | Maximum schema overhead — the H1 probe |
| **E** | Long multi-turn agent workflow | Context accumulation — the H4 probe |

### 2.2 Conditions

| ID | Condition | Tests |
|---|---|---|
| **C0** | Baseline, no intervention | — |
| **C1** | Deferred/reduced tool-schema exposure (code-execution pattern) | H1 |
| **C2** | Tool-result filtering / compression | H2 |
| **C3** | Context compaction / clearing | H4 |
| **C4** | Routing by task complexity | H3 |
| **C5** | Third-party optimisation tool (**only after G2 security pass**) | H2 |

### 2.3 Allocation

A condition is run only where it is **mechanistically meaningful**. Running C1 against a
single-tool workload would produce a real number that means nothing.

| Condition | Workloads | Reps | Runs | Justification for the applicability choice |
|---|---|--:|--:|---|
| C0 baseline | A, B, C, D, E | 3 | **15** | Every workload needs its own baseline |
| C1 schema deferral | A, D | 3 | **6** | Only A and D carry enough tools for schema overhead to exist |
| C2 result filtering | A, B, C, D | 3 | **12** | E's cost is accumulation, not result size |
| C3 compaction | B, E | 3 | **6** | Only long-context workloads accumulate |
| C4 routing | A, B, C, D, E | 3 | **15** | Routing applies everywhere |
| C5 third-party tool | A, B, D | 3 | **9** | Where the reviewed tools claim to operate |
| | | | **63** | |
| C2+C4 combined | A, B, D | 3 | **9** | Only after both singles report |
| C3+C4 combined | B, E | 3 | **6** | Only after both singles report |
| | | | **78** | |
| **Reproduction** | 2 strongest single results | 5 | **10** | G6 — independent repeat by a different seat |
| **Cache-state control** | Cold-cache verification across conditions | — | **6** | Guardrail: cached and uncached runs must never be silently mixed |
| **Meter calibration** | ATK Token Meter vs provider `usage` field | — | **6** | If the meter disagrees with the provider, every number is void |
| | | | **100** | |

**The last 12 runs are not padding.** Cache-state control and meter calibration are the two
guardrails that, if skipped, invalidate the other 88. `rtk`'s `bytes/4` estimator (see
`TOP30_R3.md` §1) is the cautionary example: an unvalidated meter produced figures its own
users report as off by >10,000× in one repro.

### 2.4 Freeze rule

Once G1 is granted, this matrix is immutable. Changing an allocation after seeing results
voids the run. A condition that cannot execute is recorded as a **failed cell with a reason**,
never silently reallocated.

---

## 3. Quality floors — pre-registered, before any result is seen

**Cost without quality control is not a saving.** A treatment that reduces tokens and fails
the floor is recorded as a **failed optimisation**, not as a trade-off.

| Workload | Success criterion | Quality floor | Scored by |
|---|---|---|---|
| A | Named functions/symbols correctly identified | ≥ 95% of baseline's correct set, **zero fabricated symbols** | Quality Judge |
| B | Required fields extracted from the document | ≥ 97% exact-match on a pre-built answer key | Quality Judge |
| C | Claims in the summary traceable to a retrieved source | 100% traceable, ≥ 90% of baseline's covered facts | Quality Judge |
| D | Correct tool selected and correct final answer | ≥ 95% task success, zero wrong-tool invocations | Quality Judge |
| E | Task completed and earlier-turn constraints honoured | ≥ 95% completion, **zero constraint violations from forgotten context** | Quality Judge |

**Separation enforced by `agents/SEAT_REGISTRY.json` and `tools/validate_seats.py`:** the
Quality Judge owns G5 and may not alter token measurements; the Token Meter may not judge
quality; the Benchmark Runner owns G4 and may not own G5. The Quality Judge scores **before
seeing cost**.

Any *zero-tolerance* criterion above (fabricated symbols, wrong-tool invocation, forgotten
constraint) fails the cell outright regardless of percentages.

---

## 4. Metrics captured per run

`run_id`, `task_id`, `condition`, `workload`, `repetition`, `model`, `provider`,
`model_version`, `model_calls`, `tool_calls`, `input_tokens`, `output_tokens`, `total_tokens`,
`tool_schema_tokens`, `tool_result_tokens`, `cost`, `pricing_snapshot_id`, `latency_ms`,
`retries`, `escalations`, `cache_state`, `task_success`, `quality_score`, `failure_reason`,
`environment_id`, `raw_evidence_path`.

**Pricing is recorded separately from tokens.** Token counts are physical; prices move. A
pricing snapshot is captured once per run-day and referenced by id, so a later price change
cannot retroactively alter a measured result.

---

## 5. Environment plan

Layout, per `workflows/TOKEN_EFFICIENCY_LAB_001_TEAM.md`:

```
benchmarks/token-efficiency-lab-001/
├── methodology/   frozen hypotheses, matrix, quality floors
├── environment/   PINS.txt, dependency manifest, container digest
├── tasks/         task set + answer keys (versioned)
├── runs/          one record per run
├── evidence/      raw model I/O, unedited
├── results/       aggregates, only after G5
├── reproduction/  independent repeat instructions
└── reports/       Lab report
```

**Requirements before G3:**

1. Container image pinned **by digest**, not tag.
2. Language runtimes and dependency manifests locked.
3. Task set version-tagged and hashed; answer keys frozen before any run.
4. Prompt/config hashes recorded per run.
5. Model and provider version recorded per run.
6. Network egress recorded — a run that silently reached a network the others did not is not
   comparable.

---

## 6. Candidate inspection and security review — **status: NOT PERFORMED**

This section is the **inventory of what the review must cover**, not the review. Per
`agents/SEAT_REGISTRY.json`, only the Security Agent may pass G2, and it may not waive its own
gate.

### 6.1 Pins resolved **[OBSERVED]**

Resolved 2026-09-15 by `git ls-remote`. Recorded in
`benchmarks/token-efficiency-lab-001/environment/PINS.txt`. **No moving default branch is used
as a dependency.**

| Candidate | Version | Commit SHA |
|---|---|---|
| `headroomlabs-ai/headroom` | v0.37.0 | `32d7ca4577d599b8a5f811ada74cf31504302c9d` |
| `rtk-ai/rtk` | v0.49.0 | `b1c0dc00649c50fbe8930f849c800d4d6ca12091` |
| `Paritok-official/paritok-4b-v1` | v1.3.12 | `509b5f9640255b26070e5ea68a071b6aaf8d7bd4` |
| `yvgude/lean-ctx` | ⚠️ `vscode-v0.2.0` | `38a8e5a4a84982d953020a37da23746d79f3338a` |
| `NadirRouter/NadirClaw` | v0.23.1 | `63275a49f4e6542f1abf9d5a28be990c01064761` |
| `toby-bridges/api-relay-audit` | v2.4.0 | `571b97142c0d22aae305ac2919e45137bc424dcc` |
| `crwdla/tokentab` | ⚠️ no tags | `d9e8cb405642d368d2f6a19147cc7f3088e3d886` |
| `juyterman1000/entroly` | v1.0.3 | `28e685f4c9793b26f7372c41c0ad0430f4e8e547` |

Two flags for the Environment Agent:
- **`lean-ctx`** — the newest tag is a **VS Code extension** tag, which may not correspond to
  the core library. Resolve the correct core release before use.
- **`tokentab`** — ships **no tags**. Pinned at a HEAD SHA, which is reproducible, but there is
  no release boundary and no changelog anchor.

### 6.2 Risk surface the review must cover

Ranked by what the component can see or do. **None of this has been reviewed.**

| Candidate | Class | What it can see or do | Review must establish |
|---|---|---|---|
| `NadirClaw` | **Proxy** | Full prompts, responses, **API keys** | Egress destinations; key handling and storage; whether prompt content is logged or transmitted |
| `paritok-4b-v1` | **Proxy + model** | Full prompts; runs a 4B model | All of the above **plus** model weight provenance and inference-host egress |
| `headroom` | **Proxy + MCP server** | Tool output, logs, files, RAG chunks; caches originals **locally** | Cache location, retention, whether cached originals ever leave the host |
| `rtk` | **Command wrapper** | Wraps and executes bash commands | Command-injection surface; what it does with command output; the Rust binary's supply chain |
| `entroly` | Library / proxy / MCP | Context payloads | Whether "reversible" means locally recoverable only |
| `lean-ctx` | Library / MCP | Context payloads | Egress; the tag ambiguity above |
| `tokentab` | Log reader | **Reads agent session logs — may contain secrets and customer data** | Whether it transmits anything; redaction behaviour |
| `api-relay-audit` | Security scanner | Traffic it is pointed at | Whether it stores captured traffic; safe to point at ATK's own routing |

### 6.3 Execution policy for Lab 001

1. Every candidate runs in an **isolated container with default-deny egress**; allowed
   destinations are enumerated per candidate and logged.
2. **No production credentials.** Dedicated benchmark keys with hard spend caps.
3. **No customer or proprietary data** in any task. Task inputs are synthetic or
   public-domain, version-tagged in `tasks/`.
4. Egress is captured per run and diffed against the declared allowlist. An undeclared
   destination **fails the run and re-opens G2**.
5. A candidate that fails G2 is **dropped from the matrix**, and its cells are recorded as
   failed with reason — never quietly replaced.

### 6.4 Conflict-of-interest note

`rtk` and `headroom` are both Lab 001 subjects **and** Top 30 integration candidates
(`TOP30_R3.md` §4.3, I6/I7). ATK has a stake in the outcome. Mitigations, all pre-registered:
quality floors fixed before any result (§3); the Quality Judge scores before seeing cost; the
Reproduction Agent may not repeat its own run; Red Team owns G8 and may not have authored the
work. **A result favourable to an ATK integration candidate should be treated as the one most
in need of reproduction**, not the one most ready to publish.

---

## 7. GitHub evidence manifest

Recorded per experiment, per `TOKEN_EFFICIENCY_LAB_001_TEAM.md`:

| Field | Source |
|---|---|
| repository URL | §6.1 |
| exact commit SHA | §6.1 — resolved, not a branch |
| ATK branch | branch carrying the run |
| dependency/environment manifest | `environment/` |
| container digest | `environment/` |
| task set version + hash | `tasks/` |
| prompt/config hash | per run record |
| model / provider / version | per run record |
| pricing snapshot id | per run-day |
| raw run id + path | `runs/`, `evidence/` |
| result commit | commit publishing `results/` |
| reproduction instructions | `reproduction/` |

---

## 8. Gate status

| Gate | Owner (from `SEAT_REGISTRY.json`) | Status |
|---|---|---|
| G0 claim registered | lab-director | ✅ this document |
| **G1 methodology frozen** | methodology-reviewer | ⏸ **awaiting review — the requested decision** |
| G2 repo + security passed | security-agent | ❌ not performed (§6) |
| G3 environment reproducible | environment-agent | ◐ pins resolved; container/deps not yet built |
| G4 execution complete | benchmark-runner | ❌ not started |
| G5 quality floor | quality-judge | ❌ floors defined, not applied |
| G6 reproduction | reproduction-agent | ❌ not started |
| G7 verify state | verify-editor | ❌ nothing above OBSERVED exists |
| G8 red team | red-team-editor | ❌ not started |
| G9 publish / integrate | publisher-editor-in-chief | ❌ not started |

---

## 9. Declared stop conditions

Execution halts and the failure is recorded — **not improvised around** — if any of these occur:

- Benchmark credentials or provider access unavailable
- Token accounting incomparable across conditions (meter calibration, §2.3, fails)
- Environment cannot be pinned by digest
- A candidate fails security review
- Quality cannot be measured for a workload
- Cache state cannot be controlled or distinguished
- Provider pricing changes mid-run without a snapshot boundary

---

## 10. What this precheck deliberately does not do

- **It does not run anything.** No candidate was installed, executed or benchmarked.
- **It does not security-review anything.** §6 is the scope of the review, not its result.
- **It does not predict outcomes.** No expected savings figure appears anywhere above, on
  purpose — a pre-registered expectation becomes a target.
- **It does not size the cost.** Provider spend for 100 runs is unestimated because the
  ~100× price-gap figure is still REPORTED (`TOP30_R3.md` T10, §6 item 1). **Resolve the
  pricing question before approving spend.**

---

## 11. Requested decision

**Grant or refuse G1 (methodology freeze).**

If granted, the next actions in order are: security review of the eight candidates (G2) →
container and dependency pinning (G3) → task set and answer keys frozen → execution begins.

If refused, name the condition, allocation or quality floor to change **now**, while changing
it is still free. After G1, a change voids the runs.

**Stop condition reached. Awaiting Editor-in-Chief / ChatGPT review.**

# First Execution — Offline Verification Log

**Date:** 2026-09-16 · **Repo commit at start:** `a8ca352dc64e792864f351f7775e2b21681b6390`
**Companion repo:** `firekou/virtual-strategy-lab` at `e0dff9a31df798539677b69e4aac130dcd32ed60`
**Network:** every check below runs offline. No credential, no paid API, no third-party code executed.

**Scope note, stated first because it is the thing most likely to be misread:**
this log records that a **format contract** was built and exercised. It does **not** record that
any content in it is true, that any Agent learned anything, or that anyone paid for anything.
`validate_packages.py` prints that distinction on every run for the same reason.

---

## 1. Commands, verbatim

| # | Command | Result |
|---|---|---|
| A1 | `python3 tools/validate_seats.py` | `separation of duties OK — 71 seats, 10 departments, 14 invariants enforced` |
| A2 | `python3 tools/test_packages.py` | **58/58 通過**, exit 0 |
| A3 | `python3 tools/validate_packages.py schemas/fixtures --seat-registry agents/SEAT_REGISTRY.json` | 6/21 passed, 15 blocked, exit 1 (**expected** — 15 fixtures exist to be blocked) |
| A4 | `python3 tools/validate_packages.py magazine/samples --seat-registry agents/SEAT_REGISTRY.json` | 6/6 passed, exit 0 |
| A5 | `python3 tools/seal_package.py --check magazine/samples/*/*.json` | 6 × `ok`, exit 0 (no hash drift) |
| A6 | `python3 tools/validate_packages.py --adopt --as-of 2026-09-16 schemas/fixtures/learning/expired.json schemas/fixtures/learning/retracted-with-cause.json schemas/fixtures/learning/valid-publishable.json` | 1/3 passed, exit 1 |
| B1 | `python3 scripts/atk-magazine/validate_seat_map.py` (VSL) | PASS, 50 seats, **0 enabled**, exit 0 |
| B2 | `python3 scripts/atk-magazine/test_seat_map.py` (VSL) | **20/20 通過**, exit 0 |

## 2. The seven required negative tests

Each row names the fixture, the rule, and the message the tool actually printed.

| Required test | Fixture | Rule | Printed |
|---|---|---|---|
| 有效資料通過 | `content/valid-*.json`, `learning/valid-*.json` | — | `PASS` ×4 |
| 缺來源被阻擋 | `content/invalid-missing-source.json` | **P1** | `claim C-001 cites undeclared source 'SRC-DOES-NOT-EXIST'` |
| 未知證據等級被阻擋 | `content/invalid-unknown-evidence-state.json` | enum + **P2** | `'PROBABLY_TRUE' is not one of [...]` |
| 過期／撤回不得供新採用 | `learning/expired.json`, `learning/retracted-with-cause.json` | **P5** | `valid_until 2026-01-01 is before as-of date 2026-09-16` / `package is retracted` |
| 版本或 hash 不符被阻擋 | `content/invalid-hash-mismatch.json` | **P6** | `content_hash mismatch` **and** `approval by 'AM25' commits to scope_hash … which is not this content` |
| 不存在的角色映射被阻擋 | `content/invalid-unknown-seat.json` · seat-map `t_04` | **P14** / **S3** | `seat 'ghost-editor' is not in the seat registry` |
| 作者自我核准被阻擋 | `content/invalid-self-approval.json` | **P4** | `seat(s) ['AM25'] appear as both author and reviewer` **and** `… also issued the 'verify' decision on it` |

**Two deliberate controls, because a gate that refuses everything proves as little as one that refuses nothing:**

- `t_09` requires at least 4 fixtures to **pass**. They do (6).
- `t_04c` requires an expired package to be **readable** outside `--adopt` and to carry only a note.
  Reading history is not adopting it, and collapsing the two would make the archive unusable.

## 3. Failures during this round, and what was changed

Recorded because a verification log with no failures in it is usually a log of things nobody ran.

### F-1 — the validator was right and the test was wrong
`t_10` asserted a draft may drop `valid_until`. It failed with **P6**: the test recomputed
`content_hash` but left the existing approval bound to the previous hash.

That is the intended behaviour — **editing content after approval invalidates the approval**, which
is the mechanical form of `execution_scope.hash == reviewed_scope.hash`. **The test was changed, not
the rule**, and the original mistake is kept in the test's docstring.

### F-2 — the seat-map validator crashed on any file outside the repo
`validate_seat_map.py` called `Path.relative_to(REPO)` unconditionally, so all 13 seat-map tests
raised `ValueError` when handed a temp file. All 13 failed at once, which is what made it obvious
it was one bug and not thirteen. Fixed with `is_relative_to`.

### F-3 — the seat map failed its own validator twice, on data this round authored
`S4` blocked **AM16** and **AM44** for claiming an evidence authority above the ceiling of their
canonical upstream department (`desks` and `production` both hold `max_evidence: null`).
Both were corrected to `null` with a note recording the consequence: **AM16 produces spec-diff cards
but may not label their evidence state** — that must come from AM36.

`S5` then warned that **seven artifact classes had an author and no reviewer**. Reviewers were
assigned, each avoiding that class's own author, and `seat-map.json` records that the assignment was
reverse-engineered from a validator warning rather than present in the original plan.

### F-4 — three seats hold upstream roles the upstream requires to be separate
`AM04` (`token-meter`＋`number-verifier`), `AM31` (`repository-inspector`＋`benchmark-runner`),
`AM33` (`experiment-designer`＋`methodology-reviewer`). The plan wrote the separation requirement as
prose. **Prose is not a mechanism.** The mapping was **not** deleted — that would change an existing
plan — instead `separation_declarations` was added and made mandatory (`S6` blocks an undeclared
pair). All three remain `DECLARED_NOT_RESOLVED` and print on every run. Declaring is not resolving.

## 4. Source retrieval, and one honest downgrade

Four external documents were read this round. Retrieval mode is recorded per source because **a
summarised rendering is weaker evidence than the document itself**, and the two look identical once
pasted into an article.

| Source | Mode | Consequence |
|---|---|---|
| MCP tools spec `2025-06-18` | **verbatim** (full page returned) | supports OBSERVED |
| MCP tools spec `2026-07-28` | **verbatim** | supports OBSERVED |
| A2A specification (latest, page states 1.0.0) | **summarised rendering** | capped at REPORTED |

Two separate retrievals of the A2A page attributed the authorization requirements to **different
section numbers** (`3.3.2`/`3.1.11` vs `§7`). No A2A section number is cited anywhere in this round's
output as a result.

**Rule `P13` was written for this and fired on a fixture built to test it**
(`content/invalid-observed-from-summary.json`): marking that A2A claim `OBSERVED` blocks the package.

## 5. What this round did NOT do

- **No article published.** All six sample packages are `status: draft`, and `t_19` fails if any is
  not. `human_responsible` is `null` on all six — there is no human publishing owner assigned, so
  `null` is the only honest value.
- **No test case executed.** Every `test_case` in the three learning packages carries
  `"executed": false, "result": "NOT_RUN"`. **A written test is not a passed test.**
- **No Lab 001 state changed.** LG4 remains NO GO, `METHODOLOGY_CHANGE_REQUEST_001` remains OPEN,
  RT-01..RT-04 remain unclosed, the frozen methodology was not edited.
- **No seat enabled.** `validate_seat_map.py` reports `enabled: 0`, and `t_11` blocks any claim
  above what the data supports.
- **No scheduler, no deployment, no outbound message, no payment, no purchased data.**
- **`registry/`, `ledgers/` and `benchmarks/` were read, never modified.**

## 6. Reproduce

```bash
git clone <this repo> && cd Open-Skill-Distribution-Flywheel
git checkout a8ca352   # or the branch carrying this log
python3 tools/validate_seats.py
python3 tools/test_packages.py
python3 tools/validate_packages.py schemas/fixtures --seat-registry agents/SEAT_REGISTRY.json   # exit 1 expected
python3 tools/validate_packages.py magazine/samples --seat-registry agents/SEAT_REGISTRY.json
python3 tools/seal_package.py --check magazine/samples/*/*.json
```

Python 3.11.15, standard library only. `jsonschema` is deliberately **not** a dependency: the
subset validator in `tools/jsonschema_mini.py` raises `UnsupportedKeyword` on any keyword it cannot
evaluate, so a schema it does not fully understand fails loudly instead of reporting a PASS on a
document nobody checked. `t_16` locks that behaviour in.

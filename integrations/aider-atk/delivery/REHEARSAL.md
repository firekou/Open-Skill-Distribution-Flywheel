# Delivery rehearsal: README.md run from a fresh GitHub clone

work_id `ATK-AIDER-DELIVERY-01` revision 1 · executor: Claude · 2026-09-26 UTC

**What this shows.** The steps in [`README.md`](README.md) can be run as written, from a fresh clone of the public repository in an empty directory, with the results the README says to expect. **What it does not show.** No model was called (step 6 is NOT RUN), no outside person has followed the README, and nothing was run on Windows or macOS. Evidence level: AUTHOR_TESTED.

## Environment

| Item | Value |
|---|---|
| OS | Ubuntu 24.04.4 LTS, `Linux 6.18.44-fc-v37 x86_64` (a Claude cloud container) |
| Python | 3.11.15 (`python3` and `python3.11` are the same build) |
| git | 2.43.0 |
| Network | GitHub (clone, fetch) and PyPI (pip) through the container's egress proxy. No model provider was contacted: `check_config.py` makes no request and Aider was only asked for `--version`. |
| pip cache | **Not empty.** pip reported "Using cached" for wheels installed in earlier sessions, so the rehearsal does not measure download size or time on a machine with an empty cache. |
| Working directory | an empty scratch directory, shown as `<W>` in the logs |

## Runs

| Run | README at | Result | Log |
|---|---|---|---|
| 1 | `b6ed8ad5d9e60fb772159399d8ced07c27220a0f` | **one blocker**: step 7 `git diff` exit 129, because the extracted directory was not a git repository | [`evidence/run1_readme_b6ed8ad.log`](evidence/run1_readme_b6ed8ad.log) |
| fix | `a2f173d293a389d6c7dd6cbe5b2dd3b17ac51b34` | step 5 now makes a local git baseline (as PR17's live plan L0 does) and marks the test file read-only; step 7 adds `git diff --stat`; `requirements.txt` pins the full resolved set | commit `a2f173d` |
| 2 | `a2f173d293a389d6c7dd6cbe5b2dd3b17ac51b34` | every step matched the README; all controls below behaved as expected | [`evidence/run2_readme_a2f173d.log`](evidence/run2_readme_a2f173d.log) |

How the runs were driven: [`evidence/drive.sh`](evidence/drive.sh) reads one command line at a time from [`evidence/run1_commands.txt`](evidence/run1_commands.txt) or [`evidence/run2_commands.txt`](evidence/run2_commands.txt), runs it in the same shell (so `cd` and variables carry over), and logs the UTC time, working directory, the last 25 output lines and the exit code. The README's own `echo "exit=$?"` lines are left out because the driver records every exit code itself. Command lines are the README's, verbatim; lines marked as controls are additions.

## Run 2 results (README at `a2f173d`)

| README step | Command | Expected | Observed (UTC 2026-09-26) |
|---|---|---|---|
| 1 | `git clone …` / `git checkout --detach origin/claude/atk-aider-delivery-01` | exit 0 | exit 0; HEAD `a2f173d2…` (02:49:40Z) |
| 2 | `get_assets.py --out "$RUN"` | exit 0, 12 files | exit 0, "12 files written … all SHA-256 verified"; every hash equals `SOURCE_MANIFEST.json` |
| 3 | `pip install "aider-chat==0.86.1"`; `aider --version` | 0.86.1 | exit 0; `aider 0.86.1`, with `litellm==1.75.0` and `openai==1.99.1` (the stack PR16–PR18 measured) |
| 4 | `check_config.py`, valid shape | exit 0 | exit 0; key printed only as `SET` |
| 4 | `check_config.py`, base ends in `/chat/completions` | exit 4 | exit 4 |
| 5 | `sha256sum test_import_contacts.py` | `b2c040c2…` | `b2c040c2ae4ae6c7417acb8dcf4e3ed5c03ae26af95643f6b498a3ed697baada` |
| 5 | `git init … commit -qm baseline` | exit 0 | exit 0 |
| 5 | `python3.11 -m unittest test_import_contacts` | exit 1, `FAILED (failures=1, errors=1)` | exit 1, `FAILED (failures=1, errors=1)`: **the baseline fails as it must** |
| 6 | Aider with a real model | NOT RUN | NOT RUN |
| 7 | judge the untouched baseline | hash unchanged, tests fail, empty diff | hash unchanged; exit 1 (2 of 5 fail); `git diff --stat` empty |
| 8 | `pip install -r requirements.txt` | exit 0 | exit 0; `pip freeze` equals `requirements.txt` exactly (6 packages) |
| 8 | `validate_feedback.py … fixtures/valid_fail.json` | `VALID`, exit 0 | `VALID   fixtures/valid_fail.json`, exit 0 |

## Controls (run 2)

**Scoring, with a human reference fix.** To check that step 7 can tell a correct change from an incorrect one without a model, a fix written by hand for this rehearsal ([`evidence/human_reference_fix/import_contacts.py`](evidence/human_reference_fix/import_contacts.py), sha256 `4fead3cf…`, labelled in its docstring) was copied into a **separate copy** of the sample directory. **It is a human result, not a model result, and it is never reported as one.**

| Control | Expected | Observed |
|---|---|---|
| human fix: test hash | unchanged | `b2c040c2…` |
| human fix: `unittest -v` | 5/5 OK | `Ran 5 tests` · `OK` · exit 0 (all five named tests `ok`) |
| human fix: `git diff --stat` | only `import_contacts.py` | `import_contacts.py`, 1 file changed, 9 insertions, 14 deletions |
| tampered copy (fix + one line appended to the test file) | caught | hash becomes `06ebaa1f…` ≠ `b2c040c2…`; `git diff --stat` lists 2 files, so step 7 rejects it |

**Feedback validator** (from the clone, with the schema that step 2 extracted):

| Control | Expected | Observed |
|---|---|---|
| all 8 fixtures | 2 VALID, 6 INVALID, exit 1 | exactly that; each INVALID line gives only a JSON Pointer and an error kind |
| `failed > total` (7 of 5) | rejected | `/task/tests_failed failed_exceeds_total` |
| secret-looking marker in a record | not echoed | `grep -c SYNTHETIC_SECRET_VALUE_7f3a9c` on the output = 0 |
| unit tests | 11 OK | `Ran 11 tests` · `OK` |

**Asset fetcher:**

| Control | Expected | Observed |
|---|---|---|
| `--out` not empty | refused | exit 2, nothing written |
| manifest hash altered for one file | refused before writing | exit 1, `SHA-256 MISMATCH asset/sample/test_import_contacts.py`; output directory not created |
| `git clone --depth 1 --single-branch` | exact fetch line printed | exit 2, `git fetch origin <5 SHAs>` |
| run the printed fetch, retry | works | fetch exit 0; retry exit 0, 12 files verified |

The shallow-clone fetch worked through GitHub's normal fetch-by-SHA; it was not tried against any other git host.

## Run 3: Aider invoked against a closed port (control, no model)

To see what an Aider run leaves in the workspace, and whether step 7 still judges correctly afterwards, the PR17 `LIVE_EXECUTION_PLAN.md` L2 command was run **with the same flags and fixed task message** against `http://127.0.0.1:9/v1`, a loopback port where nothing listens (connection refused), with a placeholder key. **No provider or model was contacted and nothing was generated.** The run used a copy of run 2's baseline workspace and venv. Logs: [`evidence/run3_closed_port_control.log`](evidence/run3_closed_port_control.log) and Aider's own output [`evidence/run3_aider_output.log`](evidence/run3_aider_output.log).

| Check | Observed (02:52:29Z–02:53:37Z) |
|---|---|
| `check_config.py` with those values | exit 0 (shape only) |
| Aider exit code | **0**, after 68 s |
| `Retrying in` lines | 8, so 9 attempts, each `litellm.InternalServerError … Connection error` |
| step 7: test hash | unchanged `b2c040c2…` |
| step 7: tests | still `FAILED (failures=1, errors=1)` |
| step 7: `git diff --stat` | empty |
| untracked files afterwards | `.gitignore` (Aider wrote `.aider*` into it), plus `.aider.chat.history.md`, `.aider.input.history`, `.aider.model.settings.yml` hidden by it, and `__pycache__/` |

So a run where every request failed still exits 0, and step 7 correctly reports it as not solved. After this run, README step 7 names the untracked files to expect. This is the fourth time exit 0 on total failure has been seen (PR16, PR17, PR18 and here); it is the same finding, not new evidence of anything else.

## Blockers found and what changed

| # | Found in | Blocker | Change |
|---|---|---|---|
| B1 | run 1, step 7 | `git diff` exits 129 outside a git repository, so a user could not see what changed | step 5: `chmod 444` on the test file, then `git init` plus a baseline commit (placeholder identity so it works where git has no user configured); step 7: `git diff --stat` must list only `import_contacts.py` |
| B2 | run 1, step 8 | `requirements.txt` pinned only `jsonschema`, and its five dependencies floated | pinned all six from `pip freeze` in a fresh venv; run 2's `pip freeze` matches it exactly |

## Known limits (not fixed here)

- The Aider install pins only `aider-chat==0.86.1`. It resolved to `litellm 1.75.0` and `openai 1.99.1` because Aider 0.86.1 pins its own dependencies, but no hashes are checked.
- Windows and macOS: not run. `sha256sum` and `chmod` are written for Linux (on macOS, `shasum -a 256`).
- Empty pip cache: not run. Download size and time are not measured.
- No outside user. A rehearsal by the author is not a first-use result.

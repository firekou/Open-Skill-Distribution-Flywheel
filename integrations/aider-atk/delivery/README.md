# Aider + OpenAI-compatible endpoint: first run (one entry point)

This page is the single place to start. It gets the reviewed assets, installs Aider, checks your configuration shape without credentials, runs the fixed CSV task's baseline, tells you how a result is judged, and shows how to validate a de-identified feedback record.

> **Evidence ceiling.** Every step below has been run offline (no model provider contacted) in a clean directory; see [`REHEARSAL.md`](REHEARSAL.md). **No real model has completed this task through these steps yet**, no outside user has tried it, and nothing here claims speed or cost savings. Step 6, the model run itself, waits on conditions listed in [`LIVE_HANDOFF.md`](LIVE_HANDOFF.md).
>
> Official Aider docs come first: <https://aider.chat/docs/llms/openai-compat.html>. Aider is Apache-2.0 by Paul Gauthier and contributors; nothing here changes Aider.

| Step | Runs offline now? | Network |
|---|---|---|
| 1 get the repository | yes | GitHub (git clone) |
| 2 extract and verify assets | yes | none |
| 3 install Aider | yes | PyPI only; no model provider |
| 4 configuration shape check | yes | none |
| 5 CSV task baseline | yes | none |
| 6 run Aider on the task with a real model | **no — waits for LIVE_HANDOFF.md** | your chosen provider |
| 7 judge the result | yes (after step 6) | none |
| 8 validate a feedback record | yes | PyPI for `jsonschema` only |

Tested with: Linux, `git`, Python 3.11 (`python3.11`). Windows and macOS are not tested.

---

## 1. Get the repository at the delivery commit

```bash
git clone https://github.com/firekou/Open-Skill-Distribution-Flywheel.git atk-flywheel
cd atk-flywheel
git checkout --detach origin/claude/atk-aider-delivery-01   # or the exact commit named in the PR / RELEASE_CANDIDATE.md
REPO="$PWD"
RUN="$REPO/../aider-first-run"
```
A full clone already contains the five reviewed source commits. If you used `--depth` or `--single-branch`, step 2 prints the exact `git fetch origin <sha> …` line to run.

## 2. Extract and verify the reviewed assets

```bash
python3 "$REPO/integrations/aider-atk/delivery/get_assets.py" --out "$RUN"
echo "exit=$?"        # expected: exit=0 and "12 files written … all SHA-256 verified"
```
The script only runs `git show <commit>:<path>` and compares SHA-256 against [`SOURCE_MANIFEST.json`](SOURCE_MANIFEST.json). It downloads nothing and executes nothing it extracts. A mismatch exits 1; a missing commit exits 2.

Layout of `$RUN`:
- `asset/`: `QUICKSTART.md`, `TASK.md`, `check_config.py`, `sample/import_contacts.py`, `sample/test_import_contacts.py` (all from PR14 `d1474670`)
- `feedback/FEEDBACK_SCHEMA.json`: from PR19 `a77d1e8e`
- `docs/`: the reviewed guides and plans the other steps link to

## 3. Install Aider (network: PyPI only)

```bash
cd "$RUN"
python3.11 -m venv .venv
.venv/bin/pip install "aider-chat==0.86.1"
.venv/bin/aider --version     # expected: aider 0.86.1
```
This contacts PyPI and no model provider. Installing is not the same as network isolation: at startup Aider itself fetches a public price list from `raw.githubusercontent.com` (measured; see `docs/PUBLISHABLE_GUIDE.md` §4).

## 4. Configuration shape check (no credentials)

```bash
cd "$RUN/asset"
OPENAI_API_BASE="https://api.example.invalid/v1" OPENAI_API_KEY="placeholder-not-a-key" \
  AIDER_MODEL="openai/example-model" python3 check_config.py
echo "exit=$?"        # expected: exit=0 (shape only; nothing is contacted)

OPENAI_API_BASE="https://api.example.invalid/v1/chat/completions" OPENAI_API_KEY="placeholder-not-a-key" \
  AIDER_MODEL="openai/example-model" python3 check_config.py
echo "exit=$?"        # expected: exit=4 (base URL includes a route)
```
Codes: 0 shape ok · 2 a value missing · 3 wrong/missing `openai/` prefix · 4 base URL is a full path. The checker never prints the key. When you have real values, set them as environment variables only; never on the command line, in files or in chat.

## 5. The CSV task baseline (must fail)

```bash
cd "$RUN/asset/sample"
sha256sum test_import_contacts.py   # expected: b2c040c2ae4ae6c7417acb8dcf4e3ed5c03ae26af95643f6b498a3ed697baada
python3.11 -m unittest test_import_contacts
echo "exit=$?"        # expected: exit=1, "FAILED (failures=1, errors=1)"
```
The task (read `$RUN/asset/TASK.md`) is to make `import_contacts.py` read the CSV by column name. The baseline must fail; if it passes, stop, because the task is not valid.

## 6. Run Aider on the task with a real model — NOT RUN

This needs an endpoint, model, safely injected key and a spending limit. None of those is authorized yet. The exact commands, cost controls and stop procedure are in [`LIVE_HANDOFF.md`](LIVE_HANDOFF.md). Do not improvise this step.

## 7. Judge the result (after step 6)

```bash
cd "$RUN/asset/sample"
sha256sum test_import_contacts.py          # must still be b2c040c2…
python3.11 -m unittest test_import_contacts -v   # must be 5/5 (OK)
git diff                                   # read it: only import_contacts.py changed, no hard-coded answers
```
**Never use Aider's exit code.** It exits 0 even when every model request failed (measured). A result counts only if all three checks hold.

## 8. Validate a de-identified feedback record

```bash
cd "$REPO/research/adoption/aider/first-use/delivery"
python3.11 -m venv "$RUN/.venv-feedback"
"$RUN/.venv-feedback/bin/pip" install -r requirements.txt
"$RUN/.venv-feedback/bin/python" validate_feedback.py --schema "$RUN/feedback/FEEDBACK_SCHEMA.json" fixtures/valid_fail.json
echo "exit=$?"        # expected: "VALID   fixtures/valid_fail.json", exit=0
```
To record a real attempt, start from `fixtures/valid_fail.json`, fill in only the permitted fields (pseudonym, timings, error codes, task result; no names, keys, code or raw logs), and run the same command on your file. Invalid records exit 1 and print only the field location and error type, never the values.

---

## Where things come from

| What | Fixed source |
|---|---|
| task, checker, sample files, Quick Start | PR14 `d1474670db12934c80caa05674c8e4320cbad312` |
| study/trial runbook | PR16 `1dcd625df3bde48b13b91abb3b03eb7e19371558` |
| live command set | PR17 `6ea3cec9937e74de8ce77f47c5e92d3d1617c506` |
| retry/exit behaviour report | PR18 `1abd74a4b7f14d8b5e397d33afa2ace212841099` |
| feedback schema, guides, release gate | PR19 `a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41` |

None of these PRs is merged. They are reviewed commits, not a release. Optional ATK Router setup is in `docs/ATK_OPTIONAL_SETUP.md`; you do not need it.

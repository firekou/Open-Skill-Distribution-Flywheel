# Internal run, 2026-09-22 — INTERNAL_AGENT_TEST (author's own test)

Not an independent reviewer replay, not adoption.

- Code: `git archive 304af885193245da7186cb6b9ab247ec2494bd86 integrations/headroom-atk`
- Install: `pip install "headroom-ai[proxy]==0.37.0"` into a fresh venv (network on).
- Every execution of project code ran through `iso.sh`: `env -i` (no provider keys, no GitHub
  tokens in the environment) inside `unshare --net --map-root-user`, loopback brought up by
  `lo_up.py`. External connect was checked to fail (`Network is unreachable`); loopback to work.
- Files on disk are still readable inside the namespace; with no route out, nothing can leave.
  This is weaker than the reviewer bar (read-only source, no write token present at all).

| file | contents |
|---|---|
| `run_output.txt` | offline trial (exit 0, 15.1%, both needles), JSON-lines control (exit 3), needle-absent and unknown-argument misuse (exit 2, token not echoed), `ab_test.py` without key (refuses, exit 2), 44 unit tests OK |
| `pip_freeze.txt` | the 90+ packages actually installed; only headroom-ai is pinned upstream |
| `dependency_licenses.json` | licence metadata of every installed distribution (94) |
| `home_files_after_run.txt` | files headroom/onnxruntime created under `$HOME` |
| `iso.sh`, `lo_up.py` | the wrapper, so the run can be repeated |

Also observed, not in the old docs: the needle text was not found anywhere under `$HOME`;
`proxy.log` reports `Local telemetry: DISABLED`; onnxruntime created a `deviceid` and an empty
event table. Running `local_check.py` with the venv interpreter but without the venv on `PATH`
fails with `FileNotFoundError: 'headroom'` — now stated in the quickstart.

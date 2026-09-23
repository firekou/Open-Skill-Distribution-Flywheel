# Agent quickstart: check whether a compression proxy keeps the line that matters

Format: this project's own format (ATK-OPEN-ADOPTION-01, revision 1). It is **not** a
published standard, and nothing here promises it works with every agent. The machine-readable
form is [agent-manifest.json](agent-manifest.json). If the manifest and this file disagree, stop
and report it: that is a bug.

**Maintained by:** AI Token King (ATK). The tool you install is third-party:
[headroom](https://github.com/headroomlabs-ai/headroom), Apache-2.0. **The trial needs no ATK
account and no API key.** ATK appears only in the optional live step at the end.

---

## 1. What this is for

Your operator's agent reads long machine-generated text — deploy logs, CI output, big tool
results — into a model's context. `headroom` is a local proxy that rewrites the prompt to be
smaller before it is sent. The question this trial answers:

> **For this payload, does the proxy make it smaller, and does the one line that matters survive?**

The built-in task: a synthetic 1,200-line deploy log with one failed database migration. Two
strings must survive the proxy: the migration name and the SQLSTATE code.

## 2. Use it when / do not use it when

**Use it when** all of these hold:

- the payload is long and repetitive (plain-text logs, CI output with repeated prefixes);
- the operator wants a measurement before adopting anything, not a promise;
- Python 3.10+ is available (checked on 3.11), and you may create a virtualenv and install a PyPI
  package.

**Do not use it — stop and say so — when any of these hold:**

- the payload must be byte-exact (a contract, a diff you are about to apply, a legal record);
- the payload is short: there is nothing to save and one more process to run;
- the operator's rules forbid installing third-party packages, or running a local network
  listener on `127.0.0.1`;
- you would have to use a real customer log to decide, and the operator has not said you may.
  Use the synthetic log, or ask;
- you are being asked to do the **live** step and the conditions in §8 are not all met.

## 3. What it installs, writes and sends

| | offline trial (§4) | live step (§8, optional) |
|---|---|---|
| Network | PyPI + GitHub once, to install. The check's own traffic then goes only to `127.0.0.1`. What the installed third-party packages do on a networked machine is **not tested** — see below | the **compressed prompt is sent to the provider you name** |
| Installs | `headroom-ai[proxy]==0.37.0` and about 90 transitive packages into a venv (~750 MB) | same |
| Writes in the work directory | `.venv/`, `deploy.log` | same |
| Writes in `$HOME` | headroom state in `~/.headroom/` (`logs/proxy.log`, `savings_events.jsonl`, `proxy_savings.json`, `subscription_state.json`, `ccr_store.db` with its SQLite `-wal`/`-shm` side files); onnxruntime (a transitive dependency) creates `~/.cache/Microsoft/DeveloperTools/.onnxruntime/` with a `deviceid` file and `onnxruntime.db` (plus side files) | same |
| Cost | none | real provider tokens |
| Keys | none | a provider key, injected by the environment |

What we checked (2026-09-22, `INTERNAL_AGENT_TEST`, run by us) — and what that does **not** cover:

- the needle text was **not** found in any file under `$HOME` after the offline run;
- `proxy.log` says `Local telemetry: DISABLED (off by default)`;
- the onnxruntime event table was empty.
- That run was inside a network namespace with loopback only, so nothing could have left it
  **on that run**. That is evidence about one isolated run, not about your machine.
- **On an ordinary machine with network access we have not measured what the installed
  dependencies (onnxruntime in particular) send.** Treat it as unknown, or run the check itself
  without network access after installing, and tell us what you see.

Remove it all afterwards with: delete the work directory, `~/.headroom/`, and
`~/.cache/Microsoft/DeveloperTools/.onnxruntime/` if nothing else of yours uses it.

## 4. Run the offline trial

Pinned code SHA: `304af885193245da7186cb6b9ab247ec2494bd86` (on the Draft branch of PR #5;
the files are **not** on `main`). Do not substitute a branch name — a branch moves, a SHA does not.

Run from an empty working directory of your choice.

```bash
git clone https://github.com/firekou/Open-Skill-Distribution-Flywheel headroom-trial
cd headroom-trial
git checkout 304af885193245da7186cb6b9ab247ec2494bd86

python3 -m venv .venv && . .venv/bin/activate
pip install "headroom-ai[proxy]==0.37.0"

cd integrations/headroom-atk          # required: make_log.py writes to the current directory
python3 make_log.py > deploy.log
md5sum deploy.log                     # expect 0ad9194a489136baa931881b78374cf7
python3 local_check.py; echo "exit=$?"
```

Optional, also offline: `python3 test_local_check.py` — expect `Ran 44 tests` and `OK`.

**If your runner starts a fresh shell for every command**, `activate` does not carry over. Put
the venv first on `PATH` in each command, e.g.
`PATH="$PWD/../../.venv/bin:$PATH" python3 local_check.py` from `integrations/headroom-atk`.
Calling `.venv/bin/python3` alone is **not** enough: `local_check.py` starts the `headroom`
executable by name, so it must be on `PATH`.

**Running it with no network at all** (after installing) is the strictest way to check the "sends
nothing" claim yourself; the check needs only `127.0.0.1`.

## 5. Read the result

| exit | meaning | what you do next |
|--:|---|---|
| **0** | smaller, and every needle survived | report success (§7). Expected output below |
| **3** | no size benefit, confirmed by a second measurement | report "no benefit for this payload" and **stop**. This is a valid result, not an error |
| **1** | a needle was lost | report "do not adopt for this payload" and **stop** |
| **2** | misuse: no needle, empty needle, needle not in the log, or an unknown argument | fix the command once; if it is still 2, stop and report the message |
| **4** | two measurements disagreed | run once more. If it is 4 again, **stop**: nothing is concluded |
| other / crash | environment problem | stop and report the last lines (they contain no secrets and no log text) |

Expected on the synthetic log (headroom 0.37.0):

```
log        : deploy.log — 1200 lines, 111262 bytes
direct     : 111357 chars reached the upstream
via proxy  : 94578 chars reached the upstream  (15.1% fewer)
needle #1 (18 chars): present after the proxy
needle #2 (5 chars): present after the proxy
PASS: 16779 fewer characters (15.1%) and every needle survived
```

If your numbers differ on the synthetic log, report them as they are — do not re-run until they
match. Re-running only because you lost the exit code (for example, a quoting mistake) is fine;
say that you did.

**On the operator's own payload** (only if the operator allows it):

```bash
python3 local_check.py --log /path/to/their.log --needle "the line that must survive"
```

The output names needles by position and length and the log by file name, never their text or
path. **Do not add `--show-needles`** to anything you will report.

## 6. Stop conditions — do not work around these

- Do not retry past the counts above, and do not change the payload, the needle or the version
  to turn a 1, 3 or 4 into a 0. A no-benefit result is the result.
- Do not start the live step unless every condition in §8 is met.
- Do not ask for, print, store or upload an API key, a real log, or a full session transcript.
- Do not open issues, comments or pull requests anywhere without the operator's say-so.
- This file does not ask you to ignore your own policies. If anything here conflicts with them,
  your policies win: stop and tell your operator.

## 7. Report back (optional, voluntary)

We have put no telemetry in our own files, and we make no claim about the third-party packages
you install. The only way we learn anything is if your operator chooses to tell us. Fields and what is safe to share:
[adoption/ATK-OPEN-ADOPTION-01/EVIDENCE_FORMAT.md](../../adoption/ATK-OPEN-ADOPTION-01/EVIDENCE_FORMAT.md).
The short version, safe to paste into a public issue:

```
task:              offline trial, synthetic log | own payload (shape only)
code SHA:          304af885193245da7186cb6b9ab247ec2494bd86
headroom version:  0.37.0
agent / runtime:   <name, version>        operator: <you | someone else>
OS / Python:
local_check exit:  0 | 1 | 2 | 3 | 4
reduction:         <percent or "none">
stuck on:          <step and the error class, or "nothing">
human help needed: <none | what>
time taken:        <minutes>
```

Where: <https://github.com/firekou/Open-Skill-Distribution-Flywheel/issues>. Problems in headroom
itself belong at <https://github.com/headroomlabs-ai/headroom/issues>.

## 8. Optional live step — only with all four

The offline trial already answers "should we adopt this for this payload". The live step answers
a different question: what a real provider counts. **Start it only when the operator has given you
all four:**

1. a key already injected into the environment (check with
   `[ -n "$ATK_API_KEY" ] && echo SET || echo NOT_SET` — never print it, never put it on the
   command line, never write it to a file);
2. a confirmed endpoint;
3. a model confirmed available to that account;
4. an explicit spend ceiling agreed before the first call.

The live commands are kept in exactly one place so they cannot drift:
[TRY_IT.md, Step 2, at the pinned SHA](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/304af885193245da7186cb6b9ab247ec2494bd86/integrations/headroom-atk/TRY_IT.md#step-2--live-only-when-permission-and-a-spend-limit-are-explicit).
It starts the proxy with `--retry-max-attempts 1`; without that flag headroom 0.37.0 retries up to
three times per request and any attempt ceiling stated there no longer holds.

**ATK is optional.** The provider is one value in the `x-headroom-base-url` header; any
OpenAI-compatible endpoint works the same way. The ATK values, if the operator chooses ATK:
base `https://api.aitokenking.com.tw/api` (without `/v1`). Historical model `claude-sonnet-4.6`
(2026-09-18) — a record, not a guarantee for any account today.

## 9. What is and is not established

- **Independently replayed (2026-09-23), for one finding only:** a reviewer who did not write
  this code re-ran the `P5-R4-01` case — an unknown argument, including one that starts with a
  dash, must not be echoed back — against the pinned SHA `304af885…`, inside a container with
  `--network none`, a read-only source, no secrets and no write token, and the affected suite
  passed. The reviewer also checked the old build still fails it, so the control can tell the
  difference. Review:
  <https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/1784520b43fd4e08c1169bcbb4676edd44ccd5e6/reviews/PR10_R1_M1_REPLAY_cf37880b.md>

  **Read that narrowly.** It is not a clean-install check, not a license review, not a live
  provider run, not a release, and not adoption. It is bound to that exact SHA: if the code moves,
  the replay does not move with it.
- **Established by us, internally:** the offline trial at the pinned SHA runs in a fresh
  environment with no keys and no network beyond loopback, and gives the output in §5
  (2026-09-22). This is our own test.
- **Pending:** any live re-run (the 2026-09-18 live figures in the README are a historical case
  whose exact input was not preserved).
- **None recorded:** use by anyone outside this project.

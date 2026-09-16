# Lab 001 network egress policy

**Default: DENY.** Every destination must be enumerated per run and logged. An undeclared
destination **fails the run and re-opens LG2** (frozen methodology §9 stop conditions).

## Allowed per run type

| Run type | Allowed destinations |
|---|---|
| Baseline / all model calls | The model provider endpoint(s) named in the run record, nothing else |
| Candidate under test | Provider endpoints **only**. The candidate's own vendor domain is **blocked** |

## Explicitly blocked, by name

| Host | Why |
|---|---|
| `paritok.com`, `www.paritok.com` | `paritok/cli.py` and `config.py` expose a GPU-server mode that POSTs each segment to `{base_url}/compress`. Prompt content would leave the host. Self-hosted mode only |
| `leanctx.com` | Vendor installer domain. Build from the pinned SHA instead |
| Any telemetry endpoint | `headroom/telemetry/session.py` carries a `DEFAULT_ENDPOINT`. Telemetry must be off **and** the host blocked — two independent controls |

## Credentials

Benchmark-only API keys with hard spend caps. **No production key. No customer data.**
Task inputs are synthetic or public-domain, version-tagged in `tasks/`.

---

## Enforcement status — verified 2026-09-16 (LG3)

The policy above was written before anything could be run against it. It has now been tested.

| Control | Status | Evidence |
|---|---|---|
| Default-deny inside the measured container | **VERIFIED** | `harness/selfcheck.py` check 5 probes `1.1.1.1:443`, `8.8.8.8:53`, `pypi.org:443`, `github.com:443` and fails the run if any is reachable |
| The check discriminates | **VERIFIED** | Negative control: the same image on `--network bridge` fails check 5 and exits non-zero. A check that only ever passes proves nothing |
| No network client inside the image | **VERIFIED** | `git`, `curl`, `wget`, `jq`, `nc` and `ssh` are all absent. The `apt-get` layer that installed three of them was removed |
| Build-time egress | **VERIFIED** | The image builds with `--network=none` from a vendored wheelhouse. Nothing is fetched at build time |
| Credential scoping | **VERIFIED** | `harness/providers.py` reads only `LAB001_BENCHMARK_API_KEY` and **raises** if an ambient production key is present instead of falling back |
| Per-run destination logging | **SPECIFIED, NOT YET EXERCISED** | `egress_destinations` exists in the run record schema, but no run has yet made an outbound call, so nothing has been logged |

The last row is the honest gap: **the allowlist has never been exercised against a real
outbound call,** because no run has made one. Default-deny has been verified; selective allow has
not.

## Per-candidate egress, frozen

Superseded in detail by `CANDIDATE_RUNTIME_PROFILES.md`, which freezes egress and external
endpoints per candidate alongside eight other attributes. The blocks named in this file
(`paritok.com`, `www.paritok.com`, `leanctx.com`, telemetry endpoints) remain in force, and that
document adds `raw.githubusercontent.com`, `api.telegram.org` and `discord.gg`.

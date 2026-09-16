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

#!/usr/bin/env python3
"""Generate the deploy log used by the A/B measurement.

Deterministic: a fixed seed, so every run produces byte-identical output.
1,200 lines, one second apart, starting 2026-09-18T11:00:00Z.
Exactly one FATAL line is planted at index 947 (timestamp 11:15:47Z) and it is
the only place in the file where the migration name and the SQLSTATE code appear.

    python3 make_log.py > deploy.log
"""

import random
import sys
from datetime import datetime, timedelta, timezone

LINES = 1200
NEEDLE_INDEX = 947  # 0-indexed -> 2026-09-18T11:15:47Z
START = datetime(2026, 9, 18, 11, 0, 0, tzinfo=timezone.utc)

SERVICES = ["api-gateway", "auth-svc", "billing", "cache-warm", "notifier", "search-idx"]

ROUTES = [
    "GET /v1/accounts", "POST /v1/invoices", "GET /v1/search", "POST /v1/sessions",
    "GET /v1/entitlements", "POST /v1/webhooks/dispatch", "GET /v1/usage",
    "PATCH /v1/subscriptions", "GET /v1/health", "POST /v1/tokens/refresh",
]

UPSTREAMS = ["accounts-db", "ledger-db", "search-cluster", "redis-hot", "kafka-events"]

NEEDLE = (
    'FATAL: migration 0042_add_tenant_id failed: column "tenant_id" already exists '
    "(SQLSTATE 42701) - rollback incomplete, 3 tables left locked"
)


def main() -> None:
    rng = random.Random(20260918)
    out = sys.stdout
    req = 0

    for i in range(LINES):
        ts = (START + timedelta(seconds=i)).strftime("%Y-%m-%dT%H:%M:%SZ")

        if i == NEEDLE_INDEX:
            out.write(f"{ts} ERROR billing     {NEEDLE}\n")
            continue

        roll = rng.random()
        svc = rng.choice(SERVICES)

        if roll < 0.70:
            # Ordinary served request. Only these lines carry a request id, so
            # the id sequence has gaps wherever a warning or error was logged.
            line = (
                f"{ts} INFO  {svc:<11} req-{req:06d} {rng.choice(ROUTES)} "
                f"200 {rng.randint(3, 480)}ms up={rng.choice(UPSTREAMS)}"
            )
            req += 1
        elif roll < 0.85:
            line = (
                f"{ts} WARN  {svc:<11} upstream timeout after "
                f"{rng.randint(1200, 9000)}ms, retry {rng.randint(1, 5)}/5 "
                f"up={rng.choice(UPSTREAMS)}"
            )
        elif roll < 0.95:
            line = (
                f"{ts} WARN  {svc:<11} connection pool at {rng.randint(71, 99)}%, "
                f"queue depth {rng.randint(0, 40)}"
            )
        else:
            line = (
                f"{ts} ERROR {svc:<11} request failed: "
                f"{rng.choice(['502 bad gateway', '504 gateway timeout', 'connection reset by peer', 'circuit breaker open'])} "
                f"after {rng.randint(1, 4)} attempts"
            )

        out.write(line + "\n")


if __name__ == "__main__":
    main()

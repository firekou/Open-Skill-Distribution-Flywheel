#!/usr/bin/env python3
"""A/B the same prompt against ATK directly and through the headroom proxy.

    pip install "headroom-ai[proxy]"
    headroom proxy --port 8787 --no-http2 --retry-max-attempts 1 &
    python3 make_log.py > deploy.log

    # the key comes from the environment or your secret manager, already injected.
    # Check it is there WITHOUT printing it, then run:
    [ -n "$ATK_API_KEY" ] && echo SET || echo NOT_SET
    python3 ab_test.py

**Never put the key on the command line**, including as a variable assignment
prefixed to the command: that form lands in shell history, in terminal
recordings and in any command auditing you have. This docstring used to say
exactly that, four lines under a runnable example doing precisely it, and the
example is what people copy (P5-R7-01). The literal form is not reproduced
here even as an illustration, so that a grep over this directory answers the
question outright.

**Two client requests by default** — one direct, one through the proxy, for the
needle task only. The count is printed before the first request goes out.
`--task both` adds the summary task and makes it four; you have to ask for that.

**Client requests are not provider attempts, and the difference costs money**
(P5-R8-01). This script sends each request once and never retries. The PROXY
does retry: headroom 0.37.0 takes `--retry-max-attempts` (range 1-10, default
**3**) and its non-streaming path re-sends on 429/529, other 5xx and transport
errors — `for attempt in range(self.config.retry_max_attempts)` in
`headroom/proxy/server.py`, so the value is the total number of attempts, not
the number of retries.

So the ceiling depends on how YOUR proxy was started:

    started as documented (--retry-max-attempts 1)   ceiling 2 provider attempts
    started with the 0.37.0 default (3)              ceiling 4 provider attempts

A successful default run makes two provider attempts either way. **This script
cannot see how your proxy was started and does not claim to verify it.**

Every number comes from ATK's own `usage` field in the response — nothing here
estimates.

Writes evidence/ab_needle.json (and ab_summary.json only if you asked for it).
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ATK_BASE = "https://api.aitokenking.com.tw/api"   # NOTE: no /v1 — headroom appends it
ATK_DIRECT = ATK_BASE + "/v1/chat/completions"
PROXY = os.environ.get("HEADROOM_PROXY", "http://127.0.0.1:8787") + "/v1/chat/completions"
MODEL = os.environ.get("ATK_MODEL", "claude-sonnet-4.6")

HERE = pathlib.Path(__file__).resolve().parent
LOG = HERE / "deploy.log"
EVIDENCE = HERE / "evidence"

REDACTED = "***REDACTED***"
_BODY_WITHHELD = (
    " — the response body is never shown. Providers echo parts of the credential they "
    "rejected, and no redaction can reliably recognise a fragment it was never given. "
    "Re-send the request yourself with a throwaway key if you need to read it."
)


def redact(text: str, secrets) -> str:
    """Remove known secret values from text about to be shown to a human.

    A second line only. It can remove a value we hold in full; it cannot recognise a
    transformed or partial echo of one, which is exactly why the provider's error body
    is not shown at all (P5-01). Do not treat this as a sanitiser for untrusted input.
    """
    out = text
    for secret in secrets:
        if secret and len(secret) >= 4:
            out = out.replace(secret, REDACTED)
    return out

TASKS = {
    "summary": "Summarise the operational problems in this deploy log in five bullets.",
    "needle": (
        "Did any database migration fail? Give the migration name and the exact "
        "SQLSTATE code."
    ),
}


def call(url: str, key: str, prompt: str, via_headroom: bool) -> dict:
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
        }
    ).encode()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if via_headroom:
        # Without this header headroom resolves the provider itself and your ATK
        # key is sent to OpenAI, which rejects it. The value must omit /v1.
        headers["x-headroom-base-url"] = ATK_BASE
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        # P5-01. The first version printed the provider's error body verbatim, sliced to 400
        # characters, with NO redaction at all — a 401 reading {"error": "invalid key sk-..."}
        # put the credential straight onto stderr. The first repair added an opt-in debug
        # branch that redacted the body before truncating it. That was still wrong, and the
        # review reproduced why: redaction can only remove a value it holds in full, and real
        # providers echo a PARTIAL key (`sk-abcde***…wxyz`), which no amount of matching on the
        # whole value will catch. Defending the debug branch means growing a redaction
        # algorithm against an input we do not control — so the branch is gone instead. The
        # status code is the diagnostic that matters and cannot carry a credential.
        raise SystemExit(
            redact(f"{url} returned HTTP {exc.code}{_BODY_WITHHELD}", [key])
        ) from exc
    except urllib.error.URLError as exc:
        # A gateway can carry a credential in a query string, so the URL is redacted too
        # rather than assumed safe.
        raise SystemExit(redact(f"cannot reach {url} — {exc.reason}", [key])) from exc
    return {
        "usage": payload.get("usage"),
        "text": payload["choices"][0]["message"]["content"],
    }


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Live A/B against ATK. Spends real tokens.",
    )
    # P5-R7-02: the default used to be every task in TASKS, which is four paid
    # calls, while the page telling people to run this authorised two. A cost
    # ceiling the tool quietly exceeds is worse than no ceiling. The default is
    # now the task the whole asset is about, and the bigger run is opt-in.
    ap.add_argument(
        "--task", choices=("needle", "summary", "both"), default="needle",
        help="needle (default): the migration/SQLSTATE question — 2 calls. "
             "summary: the five-bullet prompt — 2 calls. both: 4 calls.",
    )
    return ap.parse_args(argv)


def planned_tasks(which: str) -> dict:
    return TASKS if which == "both" else {which: TASKS[which]}


def main(argv=None) -> int:
    args = parse_args(argv)
    key = os.environ.get("ATK_API_KEY")
    if not key:
        print("ATK_API_KEY is not set; refusing to run. No mock is substituted.", file=sys.stderr)
        return 2
    if not LOG.exists():
        print(f"{LOG} missing. Run: python3 make_log.py > deploy.log", file=sys.stderr)
        return 2

    log_text = LOG.read_text()
    print(f"log: {len(log_text.splitlines())} lines, {len(log_text)} bytes")

    # Stated BEFORE the first call, so the number you authorised and the number
    # about to be spent are visible in the same place.
    tasks = planned_tasks(args.task)
    names = ", ".join(tasks)
    n = len(tasks)
    print(
        f"about to issue exactly {2 * n} client requests "
        f"({n} direct + {n} via the proxy) for task(s): {names}."
    )
    # P5-R8-01: "no automatic retries" was true of this script and false of the
    # path the money travels down. The proxy retries underneath, up to
    # --retry-max-attempts times, 3 by default. Stating the ceiling
    # unconditionally would be stating something this process cannot see.
    print(
        f"  provider attempts: this script sends each request once and never retries. "
        f"The proxied leg is retried by headroom itself, up to --retry-max-attempts "
        f"times (0.37.0 default: 3). Started as documented with "
        f"--retry-max-attempts 1, the ceiling for this run is {2 * n} provider "
        f"attempts; with the default it is {4 * n}. This script cannot see how your "
        f"proxy was started, so it does not verify which applies."
    )

    EVIDENCE.mkdir(exist_ok=True)

    for name, question in tasks.items():
        prompt = f"{question}\n\n```\n{log_text}```\n"
        result = {
            "direct": call(ATK_DIRECT, key, prompt, via_headroom=False),
            "via_headroom": call(PROXY, key, prompt, via_headroom=True),
        }
        out = EVIDENCE / f"ab_{name}.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=1))

        d = result["direct"]["usage"]["prompt_tokens"]
        h = result["via_headroom"]["usage"]["prompt_tokens"]
        print(f"{name:8} direct={d:>7}  via_headroom={h:>7}  ({(d - h) / d:.1%} fewer) -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

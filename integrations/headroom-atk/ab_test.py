#!/usr/bin/env python3
"""A/B the same prompt against ATK directly and through the headroom proxy.

    pip install "headroom-ai[proxy]"
    headroom proxy --port 8787 --no-http2 &
    python3 make_log.py > deploy.log
    ATK_API_KEY=sk-... python3 ab_test.py

Sends four live requests and costs real tokens. Token counts come from ATK's
own `usage` field in the response — nothing here estimates them.
Writes evidence/ab_summary.json and evidence/ab_needle.json.

Never put the key in a file or on the command line; pass it in the environment.
"""

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
INCLUDE_BODY_ENV = "ATK_INCLUDE_ERROR_BODY"
_BODY_WITHHELD = (
    f" — response body withheld; set {INCLUDE_BODY_ENV}=1 to include it (it may echo your "
    "credential, so do not paste the result into a bug report)"
)


def redact(text: str, secrets) -> str:
    """Remove known secret values from anything about to be shown to a human.

    Called on the WHOLE text before any truncation, never after.
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
        # P5-01. This used to read the provider's error body, slice it to 400 characters and
        # print it. A server is free to echo the credential it rejected — a 401 reading
        # {"error": "invalid key sk-..."} put the key straight onto stderr — and slicing first
        # would even let a fragment survive redaction, because you cannot match a value the
        # truncation already broke in half. Same defect class as PR #4's P4-01/P4-R2-01; the
        # behaviour proven there is reused rather than reinvented.
        detail = _BODY_WITHHELD
        if os.environ.get(INCLUDE_BODY_ENV) == "1":
            raw = exc.read().decode("utf-8", "replace")
            detail = " — " + redact(raw, [key])[:400]
        raise SystemExit(redact(f"{url} returned HTTP {exc.code}{detail}", [key])) from exc
    except urllib.error.URLError as exc:
        # A gateway can carry a credential in a query string, so the URL is redacted too
        # rather than assumed safe.
        raise SystemExit(redact(f"cannot reach {url} — {exc.reason}", [key])) from exc
    return {
        "usage": payload.get("usage"),
        "text": payload["choices"][0]["message"]["content"],
    }


def main() -> int:
    key = os.environ.get("ATK_API_KEY")
    if not key:
        print("ATK_API_KEY is not set; refusing to run. No mock is substituted.", file=sys.stderr)
        return 2
    if not LOG.exists():
        print(f"{LOG} missing. Run: python3 make_log.py > deploy.log", file=sys.stderr)
        return 2

    log_text = LOG.read_text()
    print(f"log: {len(log_text.splitlines())} lines, {len(log_text)} bytes")
    EVIDENCE.mkdir(exist_ok=True)

    for name, question in TASKS.items():
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

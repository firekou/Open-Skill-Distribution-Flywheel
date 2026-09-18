#!/usr/bin/env python3
"""Offline check and preflight: no credential, no cost, no network beyond localhost.

Proves three things on your machine, today:

  1. `headroom proxy` starts and the `x-headroom-base-url` header really does
     redirect it to an arbitrary OpenAI-compatible upstream.
  2. The proxy shrinks the prompt before it leaves the machine (measured on the
     body a stub upstream actually receives, not estimated).
  3. Your needle survives compression — it is still present in what the
     upstream receives.

Against the bundled sample log:

    python3 make_log.py > deploy.log
    python3 local_check.py

**Against your own log, which is the answer you actually need**, because the
saving is entirely a function of how repetitive your log is:

    python3 local_check.py --log /path/to/your.log --needle "the line that matters"

--needle may be repeated. Exit 0 means it shrank and every needle survived;
exit 1 means a needle was lost; exit 3 means it did not shrink at all, which is
a real and common outcome (see the README on JSON-structured logs).

This does NOT measure token usage or cost — it cannot; there is no model call.
For that, see ab_test.py, which needs a real key.
"""

import argparse
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_LOG = HERE / "deploy.log"
DEFAULT_QUESTION = (
    "Did any database migration fail? Give the migration name and the exact "
    "SQLSTATE code."
)
DEFAULT_NEEDLES = ["0042_add_tenant_id", "42701"]

RECEIVED: list[dict] = []


class Stub(BaseHTTPRequestHandler):
    """Records what it is sent and answers in OpenAI chat-completions shape."""

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            RECEIVED.append(json.loads(raw))
        except json.JSONDecodeError:
            RECEIVED.append({"_unparsed": raw.decode("utf-8", "replace")})
        body = json.dumps(
            {
                "id": "stub",
                "object": "chat.completion",
                "model": "stub-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "stub"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silence the default stderr access log
        pass


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def post(url: str, prompt: str, extra_headers: dict) -> None:
    body = json.dumps(
        {
            "model": "stub-model",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 64,
        }
    ).encode()
    headers = {"Authorization": "Bearer not-a-real-key", "Content-Type": "application/json"}
    headers.update(extra_headers)
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        resp.read()


def user_text(payload: dict) -> str:
    for message in reversed(payload.get("messages", [])):
        if message.get("role") == "user":
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "".join(
                    part.get("text", "") for part in content if isinstance(part, dict)
                )
    return ""


def wait_for(url: str, timeout: float = 60.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2).read()
            return True
        except urllib.error.HTTPError:
            return True  # answering at all is enough
        except OSError:
            time.sleep(0.5)
    return False


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Will headroom help on YOUR log? Offline, no key, no cost.",
    )
    ap.add_argument(
        "--log", type=pathlib.Path, default=DEFAULT_LOG,
        help="the log or payload to test (default: the bundled sample deploy.log)",
    )
    ap.add_argument(
        "--needle", action="append", default=None, metavar="TEXT",
        help="a string that MUST survive compression; repeatable. "
             "Defaults to the sample log's planted needle.",
    )
    ap.add_argument(
        "--question", default=DEFAULT_QUESTION,
        help="the question wrapped around the payload",
    )
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    log_path = args.log
    using_sample = log_path.resolve() == DEFAULT_LOG.resolve()
    needles = args.needle if args.needle else (DEFAULT_NEEDLES if using_sample else [])
    if args.needle is None and not using_sample:
        print(
            "--log was given without --needle, so nothing is checked for survival. "
            "Pass --needle 'the line that matters'.",
            file=sys.stderr,
        )
        return 2
    if not log_path.exists():
        if using_sample:
            print(f"{log_path} missing. Run: python3 make_log.py > deploy.log", file=sys.stderr)
        else:
            print(f"{log_path} does not exist", file=sys.stderr)
        return 2
    log_text = log_path.read_text(errors="replace")
    for needle in needles:
        if needle not in log_text:
            print(
                f"needle {needle!r} is not in {log_path} to begin with — "
                "nothing to preserve. Check the string.",
                file=sys.stderr,
            )
            return 2
    prompt = f"{args.question}\n\n```\n{log_text}```\n"
    print(f"log        : {log_path} — {len(log_text.splitlines())} lines, {len(log_text)} bytes")

    stub_port = free_port()
    stub = HTTPServer(("127.0.0.1", stub_port), Stub)
    threading.Thread(target=stub.serve_forever, daemon=True).start()
    stub_base = f"http://127.0.0.1:{stub_port}"

    proxy_port = free_port()
    # headroom 0.37.0 refuses a client-named upstream that resolves to
    # loopback/RFC1918 (its SSRF guard) and silently falls back to the
    # provider it resolved itself. A local stub is exactly such an upstream,
    # so it has to be allowlisted explicitly. Against a public host such as
    # ATK this variable is not needed.
    env = dict(os.environ, HEADROOM_ALLOWED_BASE_URLS=stub_base)
    proxy = subprocess.Popen(
        ["headroom", "proxy", "--port", str(proxy_port), "--no-http2"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    try:
        if not wait_for(f"http://127.0.0.1:{proxy_port}/v1/models"):
            print("headroom proxy did not come up", file=sys.stderr)
            return 1

        post(f"{stub_base}/v1/chat/completions", prompt, {})
        direct = user_text(RECEIVED[-1])

        post(
            f"http://127.0.0.1:{proxy_port}/v1/chat/completions",
            prompt,
            {"x-headroom-base-url": stub_base},
        )
        via = user_text(RECEIVED[-1])
    finally:
        proxy.terminate()
        try:
            proxy.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proxy.kill()
        stub.shutdown()

    if len(RECEIVED) < 2:
        print(
            "FAIL: the stub was not reached through the proxy — the "
            "x-headroom-base-url override was ignored",
            file=sys.stderr,
        )
        return 1
    if not direct:
        print("FAIL: stub received no user content on the direct call", file=sys.stderr)
        return 1
    if not via:
        print("FAIL: stub received no user content through the proxy", file=sys.stderr)
        return 1

    reduction = (len(direct) - len(via)) / len(direct)
    print(f"direct     : {len(direct)} chars reached the upstream")
    print(f"via proxy  : {len(via)} chars reached the upstream  ({reduction:.1%} fewer)")

    ok = True
    for token in needles:
        present = re.search(re.escape(token), via) is not None
        print(f"needle {token!r}: {'present' if present else 'LOST'} after compression")
        ok = ok and present

    if not ok:
        print("FAIL: compression dropped a needle. Do not adopt for this payload.", file=sys.stderr)
        return 1

    if via == direct:
        print(
            "NO BENEFIT: the proxy passed the payload through byte-for-byte. "
            "headroom saves by factoring out text repeated across lines, so a payload "
            "without that redundancy — JSON-structured logs are the common case — "
            "shrinks by exactly 0%. Nothing was lost; there is simply nothing to gain here.",
            file=sys.stderr,
        )
        return 3

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

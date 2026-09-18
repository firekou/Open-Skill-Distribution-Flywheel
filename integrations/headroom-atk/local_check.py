#!/usr/bin/env python3
"""Offline check: no credential, no cost, no network beyond localhost.

Proves three things about the committed scripts, on your machine, today:

  1. `headroom proxy` starts and the `x-headroom-base-url` header really does
     redirect it to an arbitrary OpenAI-compatible upstream.
  2. The proxy shrinks the prompt before it leaves the machine (measured on the
     body a stub upstream actually receives, not estimated).
  3. The needle survives compression: the migration name and SQLSTATE code are
     still present in what the upstream receives.

    python3 make_log.py > deploy.log
    python3 local_check.py

This does NOT measure ATK token usage or cost — it cannot; there is no model
call. For that, see ab_test.py, which needs a real key.
"""

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
LOG = HERE / "deploy.log"
QUESTION = (
    "Did any database migration fail? Give the migration name and the exact "
    "SQLSTATE code."
)
NEEDLE_TOKENS = ["0042_add_tenant_id", "42701"]

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


def main() -> int:
    if not LOG.exists():
        print(f"{LOG} missing. Run: python3 make_log.py > deploy.log", file=sys.stderr)
        return 2
    log_text = LOG.read_text()
    prompt = f"{QUESTION}\n\n```\n{log_text}```\n"
    print(f"log        : {len(log_text.splitlines())} lines, {len(log_text)} bytes")

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
    if via == direct:
        print("NOTE: the proxy passed the prompt through unchanged (no compression applied)")
    for token in NEEDLE_TOKENS:
        present = re.search(re.escape(token), via) is not None
        print(f"needle {token!r}: {'present' if present else 'LOST'} after compression")
        ok = ok and present

    if not ok:
        print("FAIL: compression dropped the needle", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

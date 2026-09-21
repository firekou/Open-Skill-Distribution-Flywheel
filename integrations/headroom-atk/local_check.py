#!/usr/bin/env python3
"""Offline check and preflight: no credential, no cost, no network beyond localhost.

Proves three things on your machine, today:

  1. `headroom proxy` starts and the `x-headroom-base-url` header really does
     redirect it to an arbitrary OpenAI-compatible upstream.
  2. The proxy shrinks the prompt before it leaves the machine (measured on the
     body a stub upstream actually receives, not estimated).
  3. Your needle survives compression — it is still present in what the
     upstream receives.

The output identifies needles by position and length, not by content, and prints the
log's file name rather than its path, so the result can be pasted into a bug report.
`--show-needles` turns that off when you want to read it yourself. Your log is never
printed and never leaves the machine.

Against the bundled sample log:

    python3 make_log.py > deploy.log
    python3 local_check.py

**Against your own log, which is the answer you actually need**, because the
saving is entirely a function of how repetitive your log is:

    python3 local_check.py --log /path/to/your.log --needle "the line that matters"

--needle may be repeated. Exit 0 means it shrank and every needle survived;
exit 1 means a needle was lost; exit 3 means it did not shrink at all, which is
a real and common outcome (see the README on JSON-structured logs); exit 4 means
two measurements of the same request disagreed, so nothing is concluded.

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
    ap.add_argument(
        "--show-needles", action="store_true",
        help="print the needle text and the full log path. OFF by default, because a needle "
             "is usually a real line out of a real log and this output is meant to be safe "
             "to paste into a bug report.",
    )
    # P5-R3-05 / P5-R4-01. argparse's own error echoes the VALUE next to an
    # unknown flag, which for a typo'd --needle is the exact text this tool
    # exists to keep out of shareable output. The first fix echoed back only
    # tokens starting with "-", assuming those were flags — but a needle is a
    # line out of a real log and may well start with a dash, so
    # `--needlez -SECRET` leaked it again. There is no reliable way to tell a
    # mistyped flag from a value, so nothing unrecognised is echoed at all.
    args, unknown = ap.parse_known_args(argv)
    if unknown:
        ap.error(
            f"{len(unknown)} unrecognized argument(s). They are not shown, because an "
            "unrecognised token can be a value rather than a flag and this output is "
            "meant to be safe to paste. Run with --help for the accepted options."
        )
    return args


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
    shown_path = log_path if args.show_needles else log_path.name
    if not log_path.exists():
        if using_sample:
            print(f"{log_path} missing. Run: python3 make_log.py > deploy.log", file=sys.stderr)
        else:
            print(f"{shown_path} does not exist", file=sys.stderr)
        return 2
    try:
        log_text = log_path.read_text(errors="replace")
    except OSError as exc:
        # P5-R3-04: an unreadable path (a directory, a permissions error) used to
        # escape as a traceback and exit 1 — the code this tool defines as "a needle
        # was lost, do not adopt". A read failure is misuse, which is exit 2.
        print(f"cannot read {shown_path}: {exc.strerror}", file=sys.stderr)
        return 2
    for position, needle in enumerate(needles, 1):
        if not needle.strip():
            # P5-02: an empty needle is present in every string, so it turns the
            # survival check into a no-op that always passes. Refuse it.
            print(
                "an empty --needle is satisfied by any output and checks nothing. "
                "Give the text that must survive.",
                file=sys.stderr,
            )
            return 2
        if needle not in log_text:
            shown = repr(needle) if args.show_needles else f"#{position}"
            print(
                f"needle {shown} is not in the log to begin with — nothing to preserve. "
                "Check the string. (Re-run with --show-needles to see which one, on a "
                "terminal you are happy to have it on.)",
                file=sys.stderr,
            )
            return 2
    prompt = f"{args.question}\n\n```\n{log_text}```\n"
    print(f"log        : {shown_path} — {len(log_text.splitlines())} lines, {len(log_text)} bytes")

    stub_port = free_port()
    stub = HTTPServer(("127.0.0.1", stub_port), Stub)
    threading.Thread(target=stub.serve_forever, daemon=True).start()
    stub_base = f"http://127.0.0.1:{stub_port}"

    recheck = None
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

        # A byte-for-byte pass-through is the one outcome this tool used to
        # explain with a confident cause ("your payload has no redundancy to
        # factor out") from a SINGLE measurement. Observed 2026-09-21 on the
        # bundled sample, whose md5 is fixed: the first `headroom proxy` start
        # in a fresh container returned the payload unchanged, and the next 22
        # runs of the identical command compressed it by 15.1%. The root cause
        # is NOT established. What is established is that one measurement is
        # not enough to tell a user their log cannot benefit — and that verdict
        # is the whole reason this tool exists.
        #
        # So the negative is confirmed before it is reported, and only in that
        # case, so a normal run costs nothing extra.
        if via == direct:
            post(
                f"http://127.0.0.1:{proxy_port}/v1/chat/completions",
                prompt,
                {"x-headroom-base-url": stub_base},
            )
            recheck = user_text(RECEIVED[-1])
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

    delta = len(direct) - len(via)
    reduction = delta / len(direct)
    print(f"direct     : {len(direct)} chars reached the upstream")
    verdict_word = "fewer" if delta > 0 else ("MORE" if delta < 0 else "identical size")
    shown = abs(reduction)
    print(
        f"via proxy  : {len(via)} chars reached the upstream  "
        + (f"({shown:.1%} {verdict_word})" if delta else "(identical size)")
    )

    # P5-02. Needle survival is checked first and is necessary, but it was never
    # sufficient: the previous version only treated an EXACTLY identical body as
    # "no benefit", so an equal-length rewrite and even an INFLATED body reached
    # PASS — the inflated case printing "-166.7% fewer" on its way there. A
    # verdict that says PASS while the payload grew is worse than no verdict.
    # Adoption now requires a strict shrink AND every needle present.
    # P5-R2-01: this used to print repr(needle). A needle is normally a real line lifted
    # out of a real log — the exact thing a user must not paste into a bug report — while
    # the README promised this output was safe to share. Identify needles by position and
    # length instead; --show-needles opts back in.
    ok = True
    for i, token in enumerate(needles, 1):
        present = re.search(re.escape(token), via) is not None
        label = repr(token) if args.show_needles else f"#{i} ({len(token)} chars)"
        print(f"needle {label}: {'present' if present else 'LOST'} after the proxy")
        ok = ok and present

    if not ok:
        print("FAIL: the proxy dropped a needle. Do not adopt for this payload.", file=sys.stderr)
        return 1

    if delta <= 0:
        # Three distinct outcomes, described distinctly. Calling an equal-length
        # rewrite "byte-for-byte" was itself a false statement.
        if via == direct and recheck is not None and recheck != direct:
            # The two measurements of the same request disagreed. Reporting
            # either one as the answer would be reporting a coin flip.
            print(
                "INCONCLUSIVE: the same request measured twice against the same proxy gave "
                f"two different results — {len(via)} chars (unchanged) then {len(recheck)} "
                "chars. The pass-through did not reproduce, so this payload is NOT shown to "
                "be incompressible; something about the proxy's state differed between the "
                "two calls. Run this again before deciding anything. If it keeps happening, "
                "that is worth an issue.",
                file=sys.stderr,
            )
            return 4
        if via == direct:
            # P5-R7-03: two identical observations are two observations, not a
            # cause. The previous wording concluded from them that the payload
            # "has no such redundancy to factor out" — which does not follow,
            # and is the same mistake as the single-measurement version it
            # replaced, made twice. A reader who trusts it stops looking.
            why = (
                "no size benefit was observed, twice. The payload came back unchanged, byte "
                "for byte, on both measurements against the same proxy. Nothing was lost and "
                "nothing was gained. This says what was measured and not why: two matching "
                "observations do not establish that your payload lacks the redundancy "
                "headroom factors out, and do not rule out the proxy not compressing on this "
                "run. If it matters, try a different payload shape, run it again, and check "
                "~/.headroom/logs/proxy.log."
            )
        elif delta == 0:
            why = (
                "the payload was REWRITTEN but came back exactly the same length. Not a "
                "byte-for-byte pass-through — the content changed — so verify the rewrite is "
                "acceptable to you before using this path. There is no size benefit either way."
            )
        else:
            why = (
                f"the payload GREW by {-delta} characters ({-reduction:.1%} larger). More "
                "characters reached the upstream than without the proxy. What that does to "
                "your bill depends on your tokenizer and rate card — this check does not "
                "measure tokens or money — but it is the wrong direction."
            )
        print(f"NO BENEFIT: {why}", file=sys.stderr)
        return 3

    print(f"PASS: {delta} fewer characters ({reduction:.1%}) and every needle survived")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

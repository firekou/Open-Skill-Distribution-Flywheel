#!/usr/bin/env python3
"""A local stand-in for an OpenAI-compatible endpoint, used to record what
aider actually sends. It answers on loopback only and returns one canned reply.

It exists to answer a narrow question: which path is requested, and what is in
the `model` field. It proves nothing about any real provider, and a run against
it must be labelled OFFLINE_PROTOCOL_ONLY.

The Authorization header is never written to the log: only whether one was
present.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

LOG = []
OUT = None


def _flush():
    if OUT:
        with open(OUT, "w", encoding="utf-8") as handle:
            json.dump(LOG, handle, ensure_ascii=False, indent=2)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw or b"{}")
        except ValueError:
            payload = {}

        LOG.append(
            {
                "path": self.path,
                "model": payload.get("model"),
                "stream": payload.get("stream"),
                "message_count": len(payload.get("messages") or []),
                "authorization_header_present": "authorization" in {
                    k.lower() for k in self.headers.keys()
                },
            }
        )

        _flush()

        body = json.dumps(
            {
                "id": "chatcmpl-local",
                "object": "chat.completion",
                "created": 0,
                "model": payload.get("model") or "unknown",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "ok"},
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

    def do_GET(self):
        LOG.append({"path": self.path, "model": None, "method": "GET"})
        _flush()
        self.send_response(404)
        self.end_headers()

    def log_message(self, *args):
        pass  # the request log we care about is LOG, written on shutdown


def main():
    global OUT
    port = int(sys.argv[1])
    out = sys.argv[2]
    OUT = out
    server = HTTPServer(("127.0.0.1", port), Handler)
    server.timeout = 1
    try:
        for _ in range(120):
            server.handle_request()
    except KeyboardInterrupt:
        pass
    finally:
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(LOG, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Direct LiteLLM mapping check for ATK-UPSTREAM-01 r1 (loopback only).

Calls litellm.completion(model="openai/x", api_base=127.0.0.1 stand-in,
max_retries=0) once per status and prints the exception class LiteLLM
raises and how many HTTP requests the stand-in received. Placeholder key.
Usage: python litellm_direct_mapping.py <port> <out.json>
(Results go to a file because LiteLLM prints help text on stdout.)
"""
import json, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

STATUS = {"value": 0}
HITS = {"n": 0}


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length") or 0))
        HITS["n"] += 1
        s = STATUS["value"]
        b = json.dumps({"error": {"message": f"stand-in {s}", "type": "stand_in", "code": s}}).encode()
        self.send_response(s); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def log_message(self, *a):
        pass


port = int(sys.argv[1])
srv = HTTPServer(("127.0.0.1", port), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

import litellm, openai
import importlib.metadata as md
litellm.suppress_debug_info = True
rows = []
for s in (400, 401, 402, 403, 404, 429, 500):
    STATUS["value"], HITS["n"] = s, 0
    try:
        litellm.completion(model="openai/x", api_base=f"http://127.0.0.1:{port}/v1", api_key="placeholder",
                           messages=[{"role": "user", "content": "hi"}], max_retries=0)
        cls, code = "no exception", None
    except Exception as e:
        cls, code = type(e).__name__, getattr(e, "status_code", None)
    rows.append({"http_status": s, "litellm_exception": cls, "exception_status_code": code, "http_requests": HITS["n"]})
json.dump({"litellm": md.version("litellm"), "openai": md.version("openai"), "rows": rows},
          open(sys.argv[2], "w"), indent=1)

# Draft: LiteLLM issue (NOT SENT)

> Status: **draft only, not submitted.** ATK-UPSTREAM-01 r1 does not authorize an upstream issue, comment or PR. Submitting it requires a separate owner decision.
> Target: `BerriAI/litellm` · issue type: Bug
> Dedup: see `UPSTREAM_DEDUP_REPORT.md` §3. The closest item is PR #38318 (open), which says explicitly: *"The OpenAI branch's own 403 still raises `APIError`; left alone, out of scope."* No issue was found that reports the OpenAI branch itself.

---

**Title:** `[Bug]: OpenAI-compatible HTTP 403 is raised as generic APIError, not PermissionDeniedError (_map_openai_exception)`

### What happened?

When an OpenAI-compatible endpoint (`openai/<model>` with a custom `api_base`) returns **HTTP 403**, `litellm.completion()` raises `litellm.APIError` (with `status_code=403`), not `litellm.PermissionDeniedError`.

The exception-mapping docs (https://docs.litellm.ai/docs/exception_mapping) list `403 → PermissionDeniedError`. The typed Anthropic, Bedrock and Vertex branches already do this. The OpenAI branch is the gap.

Why it matters: callers decide whether to retry by exception class. `APIError` is widely treated as transient, and `PermissionDeniedError` as permanent. A permanent 403 is therefore retried. For example, the Aider coding assistant retries `APIError` and does not retry `PermissionDeniedError`. With the default OpenAI SDK `max_retries=2` underneath, one logical call against a 403 endpoint produced 9 HTTP requests in the reproduction below, where the caller intended 1.

HTTP 402 falls through the same `else` branch. I am **not** proposing a class for 402, because LiteLLM has no payment-required type. I mention it only because it follows the same path.

### Where

`litellm/litellm_core_utils/exception_mapping_utils.py`, OpenAI branch. The `status_code` dispatch covers 400, 401, 404, 408, 422, 429, 500, 502, 503 and 504; anything else reaches `else: raise APIError(status_code=...)`.

| version | location |
|---|---|
| 1.75.0 | inline OpenAI block; the `else` → `APIError` is at line 528 |
| 1.102.1 (latest on PyPI, 2026-09-25) | `_map_openai_exception` (lines 257–500); the `else` → `APIError` is at line 481 |
| `main` @ `636eb4c396c194235d375db6b021e90f7a53099c` (2026-09-25) | same structure, no 402/403 branch (lines 414–507) |

### Minimal reproducer (no provider, no key)

A 127.0.0.1 stand-in returns `403` with an OpenAI-shaped error body:

```python
# stand-in: always 403
import json, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        b = json.dumps({"error": {"message": "forbidden", "type": "permission_error", "code": 403}}).encode()
        self.send_response(403); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
srv = HTTPServer(("127.0.0.1", 8999), H); threading.Thread(target=srv.serve_forever, daemon=True).start()

import litellm
try:
    litellm.completion(model="openai/x", api_base="http://127.0.0.1:8999/v1", api_key="placeholder",
                       messages=[{"role": "user", "content": "hi"}], max_retries=0)
except Exception as e:
    print(type(e).__name__, getattr(e, "status_code", None))
# observed (1.75.0, 1.81.10): APIError 403
# expected:                   PermissionDeniedError 403
```

<!-- LITELLM_REPRO_NOTE -->

### Expected

`PermissionDeniedError` (status 403), consistent with the docs table and with the other typed provider branches.

### Suggested fix

In the OpenAI branch's `status_code` dispatch, add a `403` case that raises `PermissionDeniedError(message=..., llm_provider=..., model=..., response=getattr(original_exception, "response", None), litellm_debug_info=...)`. This mirrors the existing 401 case. Also add a regression test beside the existing OpenAI mapping tests.

### Relevant versions
- litellm 1.75.0 and 1.81.10 (reproduced locally), 1.102.1 and `main@636eb4c` (source read only)
- openai 1.99.1 / 2.20.0
- Python 3.11, Linux

### Limits of this report
- I did not test real providers. The stand-in only returns a status code and a body.
- I make no claim about provider billing for retried requests.

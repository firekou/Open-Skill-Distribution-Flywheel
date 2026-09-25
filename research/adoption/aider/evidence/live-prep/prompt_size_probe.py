#!/usr/bin/env python3
"""Prompt-size probe for ATK-AIDER-LIVE-PREP-01 revision 1.

Runs the live command from LIVE_EXECUTION_PLAN.md step L2 against a
loopback stand-in that answers 200 "ok", twice: once without a model
settings file and once with the L2 settings file (max_tokens 4096,
max_retries 0). Saves the full request body aider sent each time. The body has no key in it (the key travels in a
header, which is not saved). Token counts use tiktoken encodings as an
estimate: the real tokenizer of the chosen model is not known here.
"""
import datetime, hashlib, json, os, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "prompt_size")
PR14 = "d1474670db12934c80caa05674c8e4320cbad312"
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
VENV = "/home/user/aider-venv/bin"
PLACEHOLDER = "local-placeholder-not-a-real-key"
MESSAGE = ("Change import_contacts.py so it reads the CSV by column name instead of by position. "
           "Keep name,email order working; also read email,name correctly; raise MissingColumnError "
           "mentioning 'email' when the email column is missing; keep empty strings as empty strings; "
           "keep non-ASCII text unchanged. Do not modify test_import_contacts.py.")

SERVER = r"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
PORT, OUT = int(sys.argv[1]), sys.argv[2]
BODIES = []
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        BODIES.append(json.loads(raw or b"{}"))
        json.dump(BODIES, open(OUT, "w"), ensure_ascii=False, indent=1)
        out = json.dumps({"id": "x", "object": "chat.completion", "created": 0, "model": "m",
                          "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
                          "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)
    def log_message(self, *a):
        pass
HTTPServer(("127.0.0.1", PORT), H).serve_forever()
"""


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


def run_variant(name, port, settings_text, fixtures_out):
    fix, wd = tempfile.mkdtemp(), tempfile.mkdtemp()
    open(os.path.join(fix, "server.py"), "w").write(SERVER)
    for rel in ("integrations/aider-atk/sample/import_contacts.py",
                "integrations/aider-atk/sample/test_import_contacts.py"):
        data = subprocess.run(["git", "-C", REPO, "show", f"{PR14}:{rel}"], capture_output=True, check=True).stdout
        open(os.path.join(wd, os.path.basename(rel)), "wb").write(data)
        fixtures_out[rel] = {"from_commit": PR14, "md5": hashlib.md5(data).hexdigest(), "sha256": hashlib.sha256(data).hexdigest()}
    os.chmod(os.path.join(wd, "test_import_contacts.py"), 0o444)
    req = os.path.join(wd, "bodies.json")
    srv = subprocess.Popen([sys.executable, os.path.join(fix, "server.py"), str(port), req],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        sk = socket.socket()
        if sk.connect_ex(("127.0.0.1", port)) == 0:
            sk.close(); break
        sk.close(); time.sleep(0.1)
    env = {"PATH": f"{VENV}:/usr/bin:/bin", "HOME": "/tmp", "OPENAI_API_KEY": PLACEHOLDER,
           "OPENAI_API_BASE": f"http://127.0.0.1:{port}/v1"}
    settings_args = []
    if settings_text:
        open(os.path.join(wd, ".aider.model.settings.yml"), "w").write(settings_text)
        settings_args = ["--model-settings-file", ".aider.model.settings.yml"]
    cmd = ([f"{VENV}/aider", "--model", "openai/local-test-model"] + settings_args +
           ["--no-auto-commits", "--no-auto-lint", "--map-tokens", "0", "--max-chat-history-tokens", "65536",
            "--timeout", "120", "--no-check-update", "--no-analytics", "--no-show-model-warnings", "--yes", "--exit",
            "--read", "test_import_contacts.py", "--message", MESSAGE, "import_contacts.py"])
    for g in (["init", "-q"], ["add", "."], ["commit", "-qm", "baseline"]):
        subprocess.run(["git", "-c", "user.email=probe@local", "-c", "user.name=probe"] + g, cwd=wd)
    start = utc(); t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=wd, env=env, capture_output=True, timeout=300)
    dur = round(time.monotonic() - t0, 3)
    time.sleep(0.5); srv.terminate(); srv.wait(timeout=5)
    bodies = json.load(open(req)) if os.path.exists(req) else []
    dst = os.path.join(OUT, f"{name}.request_bodies.json")
    json.dump(bodies, open(dst, "w"), ensure_ascii=False, indent=1)
    files = [dst]
    for stream, data in (("stdout", p.stdout), ("stderr", p.stderr)):
        f = os.path.join(OUT, f"{name}.{stream}.txt"); open(f, "wb").write(data); files.append(f)
    import tiktoken
    per_request = []
    for b in bodies:
        text = "".join(m.get("content") if isinstance(m.get("content"), str) else json.dumps(m.get("content"))
                       for m in b.get("messages", []))
        per_request.append({"model": b.get("model"), "messages": len(b.get("messages", [])),
                            "message_chars": len(text),
                            "tokens_estimate_o200k_base": len(tiktoken.get_encoding("o200k_base").encode(text)),
                            "tokens_estimate_cl100k_base": len(tiktoken.get_encoding("cl100k_base").encode(text)),
                            "max_tokens_field_present": "max_tokens" in b, "max_tokens": b.get("max_tokens"),
                            "max_retries_field_in_body": "max_retries" in b,
                            "stream": b.get("stream")})
    return {"variant": name, "port": port, "model_settings_file_content": settings_text, "command": cmd,
            "environment": {k: ("<PLACEHOLDER_KEY>" if v == PLACEHOLDER else v) for k, v in env.items()},
            "start_utc": start, "duration_monotonic_s": dur, "exit_code": p.returncode,
            "http_requests_received": len(bodies), "per_request": per_request,
            "files": {os.path.relpath(f, HERE): sha(f) for f in files}}


if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    fixtures = {}
    L2_SETTINGS = "- name: openai/local-test-model\n  extra_params:\n    max_tokens: 4096\n    max_retries: 0\n"
    variants = [run_variant("no_settings_file", 8871, None, fixtures),
                run_variant("l2_settings_file", 8872, L2_SETTINGS, fixtures)]
    manifest = {"generated_utc": utc(), "probe": "prompt_size_probe.py", "probe_sha256": sha(os.path.abspath(__file__)),
                "message": MESSAGE, "fixtures": fixtures, "variants": variants,
                "limits": ["Stand-in replied 'ok' with no edit, so this is the size of the FIRST request only; later turns carry chat history and grow.",
                           "Token counts are tiktoken estimates, not the chosen model's tokenizer.",
                           "With a real reply that edits the file, aider may run further calls (reflection on malformed edits) not exercised here."]}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), ensure_ascii=False, indent=2)
    for v in variants:
        print(v["variant"], v["exit_code"], v["http_requests_received"], json.dumps(v["per_request"]))

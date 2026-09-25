#!/usr/bin/env python3
"""Loopback reproducer for ATK-UPSTREAM-01 revision 1.

For each (aider stack, HTTP status, error body) case, a 127.0.0.1 stand-in
answers every POST with that status and body; we count the HTTP requests
aider sends for one --message and record its exit code. No provider is
contacted and the key is a placeholder (written as <PLACEHOLDER_KEY>).

Error bodies matter: aider has a string check that treats an APIError as
non-retryable only when str(ex) contains "insufficient credits" and the
compact text '"code":402' (aider/exceptions.py). So the same status can be
retried or not depending on the body a provider sends.
"""
import datetime, hashlib, json, os, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "repro")
PLACEHOLDER = "local-placeholder-not-a-real-key"
STACKS = {
    "aider0861": "/home/user/aider-venv/bin",
    "aider0862": os.environ.get("AIDER_0862_BIN", ""),
}

# name -> (status, raw body bytes). Raw bytes so the exact spacing is under control.
BODIES = {
    "generic_spaced": lambda s: json.dumps({"error": {"message": f"stand-in fixed status {s}", "type": "stand_in", "code": s}}).encode(),
    "credits_compact": lambda s: json.dumps({"error": {"code": s, "message": "Insufficient credits. Add more credits."}}, separators=(",", ":")).encode(),
    "credits_spaced": lambda s: json.dumps({"error": {"code": s, "message": "Insufficient credits. Add more credits."}}).encode(),
}

SERVER = r"""
import json, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer
PORT, STATUS, BODY_FILE, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
BODY = open(BODY_FILE, "rb").read()
LOG = []; T0 = time.monotonic()
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length") or 0))
        LOG.append({"t_monotonic_s": round(time.monotonic() - T0, 3), "path": self.path})
        json.dump(LOG, open(OUT, "w"))
        data = BODY if STATUS != 200 else json.dumps({"id": "x", "object": "chat.completion", "created": 0, "model": "m",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}).encode()
        self.send_response(STATUS); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, *a):
        pass
HTTPServer(("127.0.0.1", PORT), H).serve_forever()
"""


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def port_open(port):
    s = socket.socket(); s.settimeout(0.5)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def versions(bindir):
    frozen = subprocess.run([os.path.join(bindir, "pip"), "freeze"], capture_output=True, text=True).stdout.splitlines()
    return {l.split("==")[0]: l.split("==")[1] for l in frozen
            if "==" in l and l.split("==")[0].lower() in {"aider-chat", "litellm", "openai", "httpx"}}


def run_case(case_id, bindir, status, body_name, port, settings_text=None):
    wd, fix = tempfile.mkdtemp(), tempfile.mkdtemp()
    open(os.path.join(wd, "hello.py"), "w").write("print('hello')\n")
    open(os.path.join(fix, "server.py"), "w").write(SERVER)
    body_path = os.path.join(OUT, f"{case_id}.response_body.json")
    open(body_path, "wb").write(BODIES[body_name](status))
    req = os.path.join(wd, "req.json")
    srv = subprocess.Popen([sys.executable, os.path.join(fix, "server.py"), str(port), str(status), body_path, req],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        if port_open(port):
            break
        time.sleep(0.1)
    settings_args = []
    if settings_text:
        open(os.path.join(wd, "model.settings.yml"), "w").write(settings_text)
        settings_args = ["--model-settings-file", "model.settings.yml"]
    env = {"PATH": f"{bindir}:/usr/bin:/bin", "HOME": "/tmp", "OPENAI_API_KEY": PLACEHOLDER,
           "OPENAI_API_BASE": f"http://127.0.0.1:{port}/v1"}
    cmd = [os.path.join(bindir, "aider"), "--model", "openai/local-test-model"] + settings_args + [
           "--no-git", "--yes", "--no-check-update", "--no-analytics", "--no-show-model-warnings",
           "--exit", "--message", "ok", "hello.py"]
    rec = {"case_id": case_id, "stack": bindir, "stand_in_status": status, "response_body": body_name,
           "response_body_file": os.path.relpath(body_path, HERE), "response_body_sha256": sha(body_path),
           "model_settings_file_content": settings_text, "port": port, "server_ready_before_run": port_open(port),
           "command": [c if c != PLACEHOLDER else "<PLACEHOLDER_KEY>" for c in cmd],
           "environment": {k: ("<PLACEHOLDER_KEY>" if v == PLACEHOLDER else v) for k, v in env.items()}}
    rec["start_utc"] = utc(); t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=wd, env=env, capture_output=True, timeout=600)
    rec["duration_monotonic_s"] = round(time.monotonic() - t0, 3); rec["end_utc"] = utc()
    rec["exit_code"] = p.returncode
    time.sleep(0.5); srv.terminate(); srv.wait(timeout=5)
    for stream, data in (("stdout", p.stdout), ("stderr", p.stderr)):
        f = os.path.join(OUT, f"{case_id}.{stream}.txt"); open(f, "wb").write(data)
        rec[f"{stream}_file"] = os.path.relpath(f, HERE); rec[f"{stream}_sha256"] = sha(f)
    rows = json.load(open(req)) if os.path.exists(req) else []
    rec["http_requests_received"] = len(rows)
    text = (p.stdout + p.stderr).decode("utf-8", "replace")
    rec["aider_retry_lines"] = text.count("Retrying in")
    rec["litellm_exception_lines"] = sorted({l.split(":")[0].strip() for l in text.splitlines() if l.startswith("litellm.")})
    rec["insufficient_credits_hint_printed"] = "Insufficient credits with the API provider" in text
    return rec


if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    NO_SDK_RETRY = "- name: openai/local-test-model\n  extra_params:\n    max_retries: 0\n"
    plan = []
    for stack in ("aider0861", "aider0862"):
        plan += [
            (f"{stack}_402_generic", stack, 402, "generic_spaced", None),
            (f"{stack}_402_credits_compact", stack, 402, "credits_compact", None),
            (f"{stack}_402_credits_spaced", stack, 402, "credits_spaced", None),
            (f"{stack}_403_generic", stack, 403, "generic_spaced", None),
            (f"{stack}_401_generic", stack, 401, "generic_spaced", None),
            (f"{stack}_429_generic", stack, 429, "generic_spaced", None),
            (f"{stack}_429_generic_max_retries_0", stack, 429, "generic_spaced", NO_SDK_RETRY),
        ]
    cases = []
    for i, (cid, stack, status, body, st) in enumerate(plan):
        bindir = STACKS[stack]
        if not bindir:
            continue
        c = run_case(cid, bindir, status, body, 8901 + i, st)
        cases.append(c)
        print(f"{cid:40s} exit={c['exit_code']} http={c['http_requests_received']} retries={c['aider_retry_lines']} "
              f"credits_hint={c['insufficient_credits_hint_printed']} exc={c['litellm_exception_lines']}", flush=True)
    manifest = {"generated_utc": utc(), "script": "upstream_repro.py", "script_sha256": sha(os.path.abspath(__file__)),
                "stacks": {k: {"bin": v, "versions": versions(v)} for k, v in STACKS.items() if v},
                "cases": cases,
                "limits": ["Loopback stand-in only. The 'credits' bodies are shaped like a provider credits error but are NOT copied from any real provider response.",
                           "No provider billing is observed or implied; request counts are HTTP requests received by the stand-in.",
                           "No Retry-After header is sent."]}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), ensure_ascii=False, indent=2)

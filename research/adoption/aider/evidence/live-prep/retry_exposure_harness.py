#!/usr/bin/env python3
"""Retry-exposure harness for ATK-AIDER-LIVE-PREP-01 revision 1.

Question: when a provider answers with an error, how many HTTP requests
does ONE aider logical call actually send? PR16 measured 9 aider-level
attempts (8 "Retrying in" lines). litellm 1.75.0 also hands the OpenAI
SDK max_retries=2 (litellm/constants.py DEFAULT_MAX_RETRIES), so the SDK
may resend inside each aider attempt. Counting only aider lines would
under-state the paid-attempt ceiling.

A loopback stand-in answers every POST with one fixed HTTP status and
logs each request with a monotonic timestamp. Nothing leaves 127.0.0.1.
The key is a placeholder and is written as <PLACEHOLDER_KEY>.
"""
import datetime, hashlib, json, os, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "retry_exposure")
PR14 = "d1474670db12934c80caa05674c8e4320cbad312"
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
AIDER = "/home/user/aider-venv/bin/aider"
PLACEHOLDER = "local-placeholder-not-a-real-key"

STATUS_SERVER = r"""
import json, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer
PORT, STATUS, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
LOG = []
T0 = time.monotonic()
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            body = {}
        LOG.append({"t_monotonic_s": round(time.monotonic() - T0, 3), "path": self.path,
                    "model": body.get("model"), "stream": body.get("stream"),
                    "answered_status": STATUS})
        json.dump(LOG, open(OUT, "w"), indent=2)
        if STATUS == 200:
            out = {"id": "x", "object": "chat.completion", "created": 0, "model": body.get("model") or "m",
                   "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
                   "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
        else:
            out = {"error": {"message": f"stand-in fixed status {STATUS}", "type": "stand_in", "code": STATUS}}
        data = json.dumps(out).encode()
        self.send_response(STATUS); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, *a):
        pass
HTTPServer(("127.0.0.1", PORT), H).serve_forever()
"""


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def port_open(port):
    s = socket.socket(); s.settimeout(0.5)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def versions():
    pip = os.path.join(os.path.dirname(AIDER), "pip")
    frozen = subprocess.run([pip, "freeze"], capture_output=True, text=True).stdout.splitlines()
    wanted = {"aider-chat", "litellm", "openai", "httpx"}
    pkgs = {l.split("==")[0]: l.split("==")[1] for l in frozen
            if "==" in l and l.split("==")[0].lower() in wanted}
    return {"aider --version": subprocess.run([AIDER, "--version"], capture_output=True, text=True).stdout.strip(),
            "packages": pkgs}


def run_case(case_id, status, port, fixture, extra_env=None, settings_text=None):
    wd = tempfile.mkdtemp()
    shutil.copy(fixture, wd)
    settings_args = []
    if settings_text:
        open(os.path.join(wd, "model.settings.yml"), "w").write(settings_text)
        settings_args = ["--model-settings-file", "model.settings.yml"]
    req = os.path.join(wd, "req.json")
    srv = subprocess.Popen([sys.executable, os.path.join(FIX, "status_server.py"), str(port), str(status), req],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not port_open(port):
        time.sleep(0.1)
    env = {"PATH": f"{os.path.dirname(AIDER)}:/usr/bin:/bin", "HOME": "/tmp",
           "OPENAI_API_KEY": PLACEHOLDER, "OPENAI_API_BASE": f"http://127.0.0.1:{port}/v1"}
    env.update(extra_env or {})
    cmd = [AIDER, "--model", "openai/local-test-model"] + settings_args + ["--no-git", "--yes", "--no-check-update",
           "--no-analytics", "--no-show-model-warnings", "--exit", "--message", "ok", "import_contacts.py"]
    rec = {"case_id": case_id, "stand_in_status": status, "port": port, "model_settings_file_content": settings_text,
           "command": cmd, "environment": {k: ("<PLACEHOLDER_KEY>" if v == PLACEHOLDER else v) for k, v in env.items()},
           "server_ready_before_run": port_open(port)}
    rec["start_utc"] = utc()
    t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=wd, env=env, capture_output=True, timeout=600)
    rec["duration_monotonic_s"] = round(time.monotonic() - t0, 3)
    rec["end_utc"] = utc()
    rec["exit_code"] = p.returncode
    time.sleep(0.5); srv.terminate(); srv.wait(timeout=5)
    for stream, data in (("stdout", p.stdout), ("stderr", p.stderr)):
        path = os.path.join(OUT, f"{case_id}.{stream}.txt")
        open(path, "wb").write(data)
        rec[f"{stream}_file"] = os.path.relpath(path, HERE)
        rec[f"{stream}_sha256"] = sha256_file(path)
    rows = []
    if os.path.exists(req):
        dst = os.path.join(OUT, f"{case_id}.requests.json")
        shutil.copy(req, dst)
        rec["requests_file"] = os.path.relpath(dst, HERE)
        rec["requests_sha256"] = sha256_file(dst)
        rows = json.load(open(dst))
    rec["http_requests_received"] = len(rows)
    text = (p.stdout + p.stderr).decode("utf-8", "replace")
    rec["aider_retry_lines"] = text.count("Retrying in")
    rec["aider_attempts_inferred"] = rec["aider_retry_lines"] + 1
    rec["http_requests_per_aider_attempt"] = (round(len(rows) / rec["aider_attempts_inferred"], 3)
                                              if rows else None)
    return rec


if __name__ == "__main__":
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    FIX = tempfile.mkdtemp()
    open(os.path.join(FIX, "status_server.py"), "w").write(STATUS_SERVER)
    data = subprocess.run(["git", "-C", REPO, "show", f"{PR14}:integrations/aider-atk/sample/import_contacts.py"],
                          capture_output=True, check=True).stdout
    fixture = os.path.join(FIX, "import_contacts.py")
    open(fixture, "wb").write(data)
    fixtures = {"integrations/aider-atk/sample/import_contacts.py": {
                    "from_commit": PR14, "md5": hashlib.md5(data).hexdigest(),
                    "sha256": hashlib.sha256(data).hexdigest()},
                "harness-owned status_server.py": {"sha256": sha256_file(os.path.join(FIX, "status_server.py"))}}
    cases = []
    plan = [(f"status_{s}", s, None, None) for s in (200, 400, 401, 402, 403, 404, 429, 500)]
    # litellm reads DEFAULT_MAX_RETRIES from the environment at import (litellm/constants.py)
    # and passes it to the OpenAI SDK as max_retries. Does 0 remove the SDK-level resends?
    plan += [("status_429_env_DEFAULT_MAX_RETRIES_0", 429, {"DEFAULT_MAX_RETRIES": "0"}, None)]
    # Second route: aider passes a model's extra_params to litellm.completion as kwargs,
    # and litellm forwards max_retries to the OpenAI client. Does max_retries: 0 there work?
    ST = "- name: openai/local-test-model\n  extra_params:\n    max_tokens: 4096\n    max_retries: 0\n"
    plan += [("status_429_settings_max_retries_0", 429, None, ST),
             ("status_500_settings_max_retries_0", 500, None, ST),
             ("status_200_settings_max_retries_0", 200, None, ST)]
    for i, (cid, status, extra, st) in enumerate(plan):
        cases.append(run_case(cid, status, 8861 + i, fixture, extra, st))
        c = cases[-1]
        print(f"{c['case_id']:36s} exit={c['exit_code']} dur={c['duration_monotonic_s']}s "
              f"http_requests={c['http_requests_received']} aider_retry_lines={c['aider_retry_lines']}", flush=True)
    manifest = {"generated_utc": utc(), "harness": "retry_exposure_harness.py",
                "harness_sha256": sha256_file(os.path.abspath(__file__)),
                "versions": versions(), "fixtures": fixtures, "cases": cases,
                "limits": ["Stand-in returns a bare status with a JSON error body and no Retry-After header; real providers may send Retry-After or different bodies, which the OpenAI SDK honours.",
                           "Measures one logical call (--message ok, --no-git). Helper calls are not exercised.",
                           "Loopback only; says nothing about whether any real provider bills rejected requests."]}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), ensure_ascii=False, indent=2)

#!/usr/bin/env python3
"""Revision 2 evidence harness for ATK-VALUE-READINESS-01.

Written because revision 1 kept only the request bodies. Nothing in those
files bound them to a command, a configuration source, a version, a time
or an exit code, so the reviewer could not tell three runs apart
(PR16-R1 P1-03). This script re-runs the same offline cases and records
all of that per case, in manifest.json next to raw stdout, stderr and
request files.

Everything runs against 127.0.0.1. The key is a placeholder, and it is
written to the manifest as <PLACEHOLDER_KEY>, never as its value. No
real provider is contacted.
"""
import datetime, hashlib, json, os, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "r2")
PR14 = "d1474670db12934c80caa05674c8e4320cbad312"
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
AIDER = "/home/user/aider-venv/bin/aider"
PLACEHOLDER = "local-placeholder-not-a-real-key"


HOST_LOGGING_SERVER = r"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
LOG, OUT = [], sys.argv[2]
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            body = {}
        LOG.append({"path": self.path,
                    "host_header": self.headers.get("Host"),
                    "model": body.get("model"),
                    "stream": body.get("stream"),
                    "authorization_header_present": "authorization" in {k.lower() for k in self.headers}})
        json.dump(LOG, open(OUT, "w"), indent=2)
        out = json.dumps({"id": "x", "object": "chat.completion", "created": 0,
                          "model": body.get("model") or "unknown",
                          "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"},
                                       "finish_reason": "stop"}],
                          "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)
    def log_message(self, *a):
        pass
HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
"""


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def git_show(path, dest):
    data = subprocess.run(["git", "-C", REPO, "show", f"{PR14}:{path}"],
                          capture_output=True, check=True).stdout
    with open(dest, "wb") as f:
        f.write(data)
    return hashlib.md5(data).hexdigest(), hashlib.sha256(data).hexdigest()


def port_open(port):
    s = socket.socket()
    s.settimeout(0.5)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def sanitize(cmd):
    return [PLACEHOLDER and ("<PLACEHOLDER_KEY>" if a == PLACEHOLDER else a) for a in cmd]


def versions():
    pip = os.path.join(os.path.dirname(AIDER), "pip")
    frozen = subprocess.run([pip, "freeze"], capture_output=True, text=True).stdout.splitlines()
    wanted = {"aider-chat", "litellm", "openai", "httpx"}
    pkgs = {l.split("==")[0]: l.split("==")[1] for l in frozen
            if "==" in l and l.split("==")[0].lower() in wanted}
    aider_v = subprocess.run([AIDER, "--version"], capture_output=True, text=True).stdout.strip()
    return {"aider --version": aider_v, "packages": pkgs,
            "python": subprocess.run([os.path.join(os.path.dirname(AIDER), "python"), "--version"],
                                     capture_output=True, text=True).stdout.strip(),
            "aider_source_read_for_code_claims": "Aider-AI/aider@5dc9490bb35f9729ef2c95d00a19ccd30c26339c"}


def run_case(case_id, config_source, port, cmd, env, workdir, server, config_text=None):
    rec = {"case_id": case_id, "config_source": config_source, "port": port,
           "command": sanitize(cmd),
           "environment": {k: ("<PLACEHOLDER_KEY>" if v == PLACEHOLDER else v) for k, v in env.items()},
           "config_file_content": config_text}
    srv = None
    req = os.path.join(workdir, "req.json")
    if server:
        srv = subprocess.Popen([sys.executable, os.path.join(FIX, "host_logging_server.py"), str(port), req],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not port_open(port):
            time.sleep(0.1)
    ready = port_open(port)
    rec["server_expected"] = server
    rec["server_ready_before_run"] = {"tcp_connect_127.0.0.1": ready,
                                      "server_pid_alive": (srv.poll() is None) if srv else None}
    if server and not ready:
        rec["valid"] = False
        rec["invalid_reason"] = "stand-in server was expected but not listening"
    elif not server and ready:
        rec["valid"] = False
        rec["invalid_reason"] = "port expected closed but something is listening"
    else:
        rec["valid"] = True

    rec["start_utc"] = utc()
    t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=workdir, env=env, capture_output=True, timeout=300)
    rec["duration_monotonic_s"] = round(time.monotonic() - t0, 3)
    rec["end_utc"] = utc()
    rec["exit_code"] = p.returncode
    if srv:
        time.sleep(0.5)
        srv.terminate()
        srv.wait(timeout=5)

    for stream, data in (("stdout", p.stdout), ("stderr", p.stderr)):
        path = os.path.join(OUT, f"{case_id}.{stream}.txt")
        with open(path, "wb") as f:
            f.write(data)
        rec[f"{stream}_file"] = os.path.relpath(path, HERE)
        rec[f"{stream}_sha256"] = sha256_file(path)
    if os.path.exists(req) and os.path.getsize(req) > 0:
        dst = os.path.join(OUT, f"{case_id}.request.json")
        shutil.copy(req, dst)
        rec["request_file"] = os.path.relpath(dst, HERE)
        rec["request_sha256"] = sha256_file(dst)
        rows = json.load(open(dst))
        rec["observed_request_paths"] = [r.get("path") for r in rows]
        rec["observed_host_headers"] = [r.get("host_header") for r in rows]
        rec["observed_models"] = [r.get("model") for r in rows]
    else:
        rec["request_file"] = None
        rec["observed_request_paths"] = []
        rec["observed_host_headers"] = []
    text = (p.stdout + p.stderr).decode("utf-8", "replace")
    rec["retry_lines_observed"] = text.count("Retrying in")
    return rec


if __name__ == "__main__":
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    FIX = tempfile.mkdtemp()
    fixtures = {}
    with open(os.path.join(FIX, "host_logging_server.py"), "w") as f:
        f.write(HOST_LOGGING_SERVER)
    fixtures["harness-owned host_logging_server.py"] = {
        "from_commit": None,
        "sha256": sha256_file(os.path.join(FIX, "host_logging_server.py")),
        "why": "PR14's stand-in logs path and model but not the port, so three configuration sources produced byte-identical logs. This one also records the Host header the client sent, which makes each run distinguishable from raw data rather than from this harness's own record."}
    for rel in ("integrations/aider-atk/fake_openai_server.py",
                "integrations/aider-atk/sample/import_contacts.py",
                "integrations/aider-atk/check_config.py"):
        md5, sha = git_show(rel, os.path.join(FIX, os.path.basename(rel)))
        fixtures[rel] = {"from_commit": PR14, "md5": md5, "sha256": sha}

    base_env = {"PATH": f"{os.path.dirname(AIDER)}:/usr/bin:/bin", "HOME": "/tmp",
                "OPENAI_API_KEY": PLACEHOLDER}
    common = ["--model", "openai/local-test-model", "--no-git", "--yes", "--no-check-update",
              "--no-analytics", "--no-show-model-warnings", "--exit", "--message", "ok",
              "import_contacts.py"]

    cases = []

    def workdir():
        d = tempfile.mkdtemp()
        shutil.copy(os.path.join(FIX, "import_contacts.py"), d)
        return d

    # base path: three configuration sources, each with its own port
    env = dict(base_env, OPENAI_API_BASE="http://127.0.0.1:8851/v1")
    cases.append(run_case("base_path_env_var", "environment variable OPENAI_API_BASE", 8851,
                          [AIDER] + common, env, workdir(), server=True))

    cases.append(run_case("base_path_cli_flag", "command-line --openai-api-base", 8852,
                          [AIDER, "--openai-api-base", "http://127.0.0.1:8852/v1"] + common,
                          dict(base_env), workdir(), server=True))

    wd = workdir()
    cfg_text = "openai-api-base: http://127.0.0.1:8853/v1\n"
    cfg = os.path.join(wd, "aider.conf.yml")
    with open(cfg, "w") as f:
        f.write(cfg_text)
    cases.append(run_case("base_path_config_file", "config file via --config (issue #4027 form)", 8853,
                          [AIDER, "--config", cfg] + common, dict(base_env), wd,
                          server=True, config_text=cfg_text))

    # retry: nothing listening on the port
    env = dict(base_env, OPENAI_API_BASE="http://127.0.0.1:8859/v1")
    cases.append(run_case("retry_no_server", "environment variable OPENAI_API_BASE, no server", 8859,
                          [AIDER] + common, env, workdir(), server=False))

    # PR14 checker against the model strings from the two open issues
    for cid, model in (("checker_issue_4797_zai", "zai/glm-4.7"),
                       ("checker_issue_4638_local", "local/qwen3-coder:30b")):
        env = {"PATH": "/usr/bin:/bin", "OPENAI_API_BASE": "https://endpoint.example.com/v1",
               "OPENAI_API_KEY": PLACEHOLDER, "AIDER_MODEL": model}
        cases.append(run_case(cid, f"PR14 check_config.py with AIDER_MODEL={model}", 0,
                              [sys.executable, os.path.join(FIX, "check_config.py")],
                              env, workdir(), server=False))

    manifest = {"generated_utc": utc(), "harness": "r2_harness.py",
                "harness_sha256": sha256_file(os.path.abspath(__file__)),
                "versions": versions(), "fixtures": fixtures, "cases": cases,
                "supersedes": {
                    "evidence/base_path_env_var.json": "base_path_env_var",
                    "evidence/base_path_cli_flag.json": "base_path_cli_flag",
                    "evidence/base_path_config_file.json": "base_path_config_file",
                    "evidence/retry_no_server_stdout.txt": "retry_no_server"},
                "supersede_note": "The revision 1 files are kept unchanged and are NOT deleted. They are REPORTED only, because they carry no command, source, version, time or exit code. Claims now rest on the cases listed here."}
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    for c in cases:
        print(f"{c['case_id']:28s} valid={c['valid']} exit={c['exit_code']} "
              f"dur={c['duration_monotonic_s']}s paths={c['observed_request_paths']} host={c.get('observed_host_headers')} "
              f"retries={c['retry_lines_observed']}")

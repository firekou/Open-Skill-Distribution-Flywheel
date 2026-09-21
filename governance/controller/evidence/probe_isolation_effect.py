#!/usr/bin/env python3
"""What does the wrap actually deny? Negative controls, no model call.

GOV-R1-03 asked for exactly this: prove the boundary refuses something, and
record what it does not refuse instead of implying a complete sandbox.
"""
import json, os, pathlib, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from runners import isolate_command, working_container_backend   # noqa: E402

ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": "/tmp"}


def run(cmd, backend, cwd=None):
    try:
        r = subprocess.run(isolate_command(backend, cmd), capture_output=True,
                           text=True, timeout=60, env=ENV, cwd=cwd,
                           stdin=subprocess.DEVNULL)
        return {"exit": r.returncode, "out": r.stdout.strip()[:80]}
    except Exception as exc:
        return {"exit": None, "error": type(exc).__name__}


def main():
    backend = working_container_backend()
    out = {"backend_selected": backend}
    with tempfile.TemporaryDirectory() as td:
        secret = pathlib.Path(td) / "SYNTHETIC_HOST_SECRET"
        secret.write_text("SYNTHETIC-NOT-A-REAL-CREDENTIAL\n")
        src = pathlib.Path(td) / "source_under_review.txt"
        src.write_text("original\n")

        checks = {
            "network_reachable": ["python3", "-c",
                "import socket,sys;s=socket.socket();s.settimeout(5);"
                "sys.exit(0 if s.connect_ex(('1.1.1.1',443))==0 else 1)"],
            "host_secret_readable": ["cat", str(secret)],
            "source_writable": ["sh", "-c", f"echo tampered >> {src}"],
        }
        for name, cmd in checks.items():
            out[name] = {"unwrapped": run(cmd, None), "wrapped": run(cmd, backend)}
        out["source_after_wrapped_write"] = src.read_text().strip()

    out["_reading"] = [
        "network_reachable exit 0 = the network was reachable.",
        "host_secret_readable exit 0 = a file outside the clone was readable.",
        "source_writable exit 0 = the checkout under review could be modified.",
        "A wrap that changes none of these is not a boundary.",
    ]
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

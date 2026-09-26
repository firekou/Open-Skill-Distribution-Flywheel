import os, pathlib, subprocess, sys, time
S = pathlib.Path(sys.argv[1]); mode = sys.argv[2]
pidfile = S / "grandchild.pid"
pidfile.unlink(missing_ok=True)
kw = {"start_new_session": True} if mode == "group" else {}
proc = subprocess.Popen(["sh", str(S / "child.sh"), str(pidfile)], **kw)
time.sleep(1.0)
gc = int(pidfile.read_text().strip())
if mode == "group":
    import signal
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
else:
    proc.kill()          # what subprocess.run(timeout=...) does
proc.wait(timeout=10)
time.sleep(0.5)
try:
    os.kill(gc, 0); alive = True
except ProcessLookupError:
    alive = False
print(f"mode={mode:6s} direct child killed=True  grandchild still alive={alive}")
if alive:
    os.kill(gc, 9)
sys.exit(1 if alive else 0)

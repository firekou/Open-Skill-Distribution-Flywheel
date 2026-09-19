"""Do N separate OS processes racing Store.commit() lose updates?"""
import multiprocessing as mp, pathlib, sys, tempfile, time
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else
                "/home/user/Open-Skill-Distribution-Flywheel/governance/controller")
from store import Store, ConcurrencyError

def worker(args):
    root, n, start_at = args
    s = Store(pathlib.Path(root))
    time.sleep(max(0.0, start_at - time.time()))      # all processes go together
    ok = 0
    for _ in range(n):
        for _try in range(2000):
            try:
                rev = s.read()["revision"]
                time.sleep(0.0005)                     # the read-to-write window
                s.commit(rev, lambda st: st["tasks"].setdefault("C", {"n": 0}).update(
                    n=st["tasks"].get("C", {}).get("n", 0) + 1))
                ok += 1
                break
            except ConcurrencyError:
                continue
    return ok

if __name__ == "__main__":
    P, N = 6, 10
    with tempfile.TemporaryDirectory() as td:
        Store(pathlib.Path(td))
        start = time.time() + 1.0
        with mp.Pool(P) as pool:
            done = sum(pool.map(worker, [(td, N, start)] * P))
        final = Store(pathlib.Path(td)).read()
        print(f"commits reported successful : {done}")
        print(f"counter actually reached    : {final['tasks']['C']['n']}")
        print(f"revision                    : {final['revision']}")
        lost = done - final['tasks']['C']['n']
        print(f"LOST UPDATES                : {lost}")
        sys.exit(1 if lost else 0)

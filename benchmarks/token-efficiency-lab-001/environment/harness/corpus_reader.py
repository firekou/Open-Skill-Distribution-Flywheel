"""Audited corpus reader — the missing mechanism for workload A (NEW-03).

Workload D's corpus reads go through the offline MCP tool server, which writes the audit log.
Workload A has no tool server: it reads files. So `tool_calls` and `corpus_access_log` were
required for A and **nothing in the lab could produce either** — every real workload-A attempt
would have been `INVALID`. It looked fine only because `tools/golden_run.py` fabricated `fs.read`
entries, which is the lab's own proof harness forging the evidence it is meant to check.

This module is the real mechanism. The agent under test reads the corpus **through** it; the
runner points it at the same audit log the tool server writes, with the same `run_id`, so one
attribution rule covers both workloads.

Two properties make it evidence rather than decoration:

**It records what was actually opened.** The path is resolved and the file is read here; an entry
cannot be written for a file that was not read, because writing the entry and reading the file are
the same call.

**It refuses to leave the corpus.** A path outside the task's declared `corpus_paths` raises. A
run cannot read the answer key, another task's corpus, or anything else on disk and have it
quietly logged as a corpus access.
"""
from __future__ import annotations

import json
import os
import pathlib

AUDIT_ENV = "LAB001_TOOL_AUDIT"
RUN_ID_ENV = "LAB001_RUN_ID"
ROOT_ENV = "LAB001_TASK_ROOT"


class CorpusAccessError(RuntimeError):
    pass


def _next_seq(audit_path: pathlib.Path) -> int:
    """Continuous across processes, matching the tool server's rule (RT-21)."""
    try:
        with open(audit_path) as fh:
            return sum(1 for line in fh if line.strip()) + 1
    except OSError:
        return 1


def read(rel_path: str, *, task_root: pathlib.Path | None = None,
         allowed: list[str] | None = None, run_id: str | None = None,
         audit_path: pathlib.Path | None = None, encoding: str = "utf-8") -> str:
    """Read one corpus file and record the access. Returns the file's text."""
    root = pathlib.Path(task_root or os.environ.get(ROOT_ENV, "."))
    target = (root / rel_path).resolve()
    root_r = root.resolve()

    if not str(target).startswith(str(root_r)):
        raise CorpusAccessError(
            f"{rel_path} resolves outside the task root. A run may not read its way out of the "
            "corpus and have it logged as a corpus access."
        )
    if allowed is not None:
        ok = any(str(target).startswith(str((root / a).resolve())) for a in allowed)
        if not ok:
            raise CorpusAccessError(
                f"{rel_path} is not under this task's declared corpus_paths {allowed}. "
                "Reading the answer key or another task's corpus is not a corpus access."
            )
    if not target.is_file():
        raise CorpusAccessError(f"{rel_path} is not a file under {root}")

    text = target.read_text(encoding=encoding, errors="replace")

    ap = audit_path or os.environ.get(AUDIT_ENV)
    rid = run_id or os.environ.get(RUN_ID_ENV)
    if ap:
        if not rid:
            raise CorpusAccessError(
                f"{RUN_ID_ENV} is not set, so this read cannot be attributed to an attempt. The "
                "Evidence Producer refuses an unattributable entry rather than guessing."
            )
        ap = pathlib.Path(ap)
        entry = {
            "seq": _next_seq(ap),
            "run_id": rid,
            "mode": "read",
            "tool": "corpus.read",
            "family": "corpus",
            "arguments": {"path": str(pathlib.Path(rel_path).as_posix())},
            "bytes": len(text.encode(encoding, errors="replace")),
        }
        with open(ap, "a") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
    return text


def read_many(rel_paths: list[str], **kw) -> dict[str, str]:
    return {p: read(p, **kw) for p in rel_paths}


def main(argv=None) -> int:
    """CLI, so a run that shells out is audited the same way one that imports is."""
    import argparse
    ap = argparse.ArgumentParser(description="read a corpus file and record the access")
    ap.add_argument("path")
    ap.add_argument("--task-root", default=None)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--audit", default=None)
    a = ap.parse_args(argv)
    print(read(a.path, task_root=pathlib.Path(a.task_root) if a.task_root else None,
               run_id=a.run_id, audit_path=pathlib.Path(a.audit) if a.audit else None), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

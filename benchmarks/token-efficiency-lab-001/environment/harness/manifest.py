"""Scoring-integrity manifest — RT-12.

The v1.0.0 `MANIFEST.sha256` covered `tasks/` and `corpora/` only. **The answer keys were not in
it** — nor the derivation scripts, the scoring spec, the judge, or the record schema. A key could
change after the freeze and `sha256sum -c` would still report 155/155 OK. The frozen hash must
cover everything whose content can change a score.

Three properties this module enforces that a flat checksum file does not:

**Separate hashes, not one blob.** `task_set_hash`, `answer_key_hash`, `scorer_hash` and
`config_hash` are computed over disjoint file groups. One aggregate hash tells you *something*
changed; separate hashes tell you a key moved rather than a corpus, which is the difference
between a scoring change and a task change.

**No self-reference.** The manifest never hashes itself, and no group's hash is computed over a
file that contains that hash. A hash that includes its own output cannot be recomputed, and a
manifest bound to a commit that contains the manifest is a circular attestation. The manifest
lists artefacts; an **outer freeze record** binds the manifest digest to the commit.

**Deletions and additions are detected.** Verification walks the *filesystem* as well as the
manifest. A checker that only re-hashes what the manifest already lists cannot see a file that
was added to a scored directory, and cannot tell a deleted file from an unlisted one.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass

MANIFEST_VERSION = "1.1.0"

# Disjoint by construction; `build` asserts it. Order matters only for reporting.
GROUPS: dict[str, dict] = {
    "task_set": {
        "roots": ["tasks", "corpora"],
        "why": "what the agent under test is asked to do, and what it reads",
    },
    "answer_key": {
        "roots": ["answer_keys"],
        "exclude_suffixes": [".py"],
        "why": "the scoring ground truth. Absent from the v1.0.0 manifest - this is RT-12",
    },
    "answer_key_scripts": {
        "roots": ["answer_keys/scripts"],
        "only_suffixes": [".py"],
        "why": "how the ground truth was derived; a key is only re-derivable if these are pinned",
    },
    "scoring_spec": {
        "roots": ["SCORING_SPEC.md"],
        "why": "the scoring procedure. Changing it changes every score without touching a key",
    },
    "docs": {
        "roots": ["README.md", "DESIGN_NOTES.md", "CHANGELOG_v1.0.0_to_v1.1.0.md"],
        "why": "not score-bearing, but pinned so drift is visible",
    },
}

# Files outside the task set whose content changes scores. Hashed as `scorer` and `config`.
SCORER_FILES = ["harness/judge.py"]
CONFIG_FILES = ["run_record_schema.json", "harness/evidence.py", "harness/blind.py",
                "harness/meter.py", "harness/pricing.py", "harness/record.py"]

SKIP_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
MANIFEST_FILENAMES = {"MANIFEST.json", "MANIFEST.sha256"}


class ManifestError(RuntimeError):
    pass


def _files_under(base: pathlib.Path, spec: dict) -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for root in spec["roots"]:
        t = base / root
        if not t.exists():
            continue
        cands = [t] if t.is_file() else [p for p in t.rglob("*") if p.is_file()]
        for p in cands:
            if set(p.parts) & SKIP_DIR_NAMES or p.suffix in SKIP_SUFFIXES:
                continue
            if p.name in MANIFEST_FILENAMES:      # never hash a manifest
                continue
            if "only_suffixes" in spec and p.suffix not in spec["only_suffixes"]:
                continue
            if "exclude_suffixes" in spec and p.suffix in spec["exclude_suffixes"]:
                continue
            out.append(p)
    return sorted(set(out), key=lambda p: str(p))


def _hash_files(base: pathlib.Path, files: list[pathlib.Path]) -> tuple[str, dict]:
    per = {}
    h = hashlib.sha256()
    for p in files:
        rel = str(p.relative_to(base))
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        per[rel] = digest
        h.update(rel.encode()); h.update(b"\0"); h.update(digest.encode()); h.update(b"\0")
    return h.hexdigest(), per


@dataclass
class Manifest:
    data: dict

    def group_hash(self, name: str) -> str:
        return self.data["groups"][name]["hash"]

    def save(self, path: pathlib.Path) -> None:
        pathlib.Path(path).write_text(json.dumps(self.data, indent=2, sort_keys=True) + "\n")

    def digest(self) -> str:
        """Digest of the manifest CONTENT, for the outer freeze record to bind.

        Computed over the serialised manifest, which by construction does not contain this value.
        """
        return hashlib.sha256(
            json.dumps(self.data, indent=2, sort_keys=True).encode()
        ).hexdigest()


def build(task_set_dir: pathlib.Path, env_dir: pathlib.Path) -> Manifest:
    ts = pathlib.Path(task_set_dir)
    env = pathlib.Path(env_dir)

    groups, seen = {}, {}
    for name, spec in GROUPS.items():
        files = _files_under(ts, spec)
        for p in files:
            if p in seen:
                raise ManifestError(
                    f"{p} is claimed by both {seen[p]!r} and {name!r}; groups must be disjoint "
                    "or a change shows up twice and a deletion shows up nowhere"
                )
            seen[p] = name
        digest, per = _hash_files(ts, files)
        groups[name] = {"hash": digest, "files": per, "count": len(files), "why": spec["why"]}

    for name, rel_files in (("scorer", SCORER_FILES), ("config", CONFIG_FILES)):
        paths = [env / r for r in rel_files]
        missing = [str(p) for p in paths if not p.exists()]
        if missing:
            raise ManifestError(f"{name} group references missing files: {missing}")
        digest, per = _hash_files(env, paths)
        groups[name] = {
            "hash": digest, "files": per, "count": len(paths),
            "why": ("the scorer itself" if name == "scorer"
                    else "schema and harness modules that change how a score is produced"),
        }

    # Unclaimed files inside the task set: visible, not silently ignored.
    all_files = {p for p in ts.rglob("*") if p.is_file()
                 and not (set(p.parts) & SKIP_DIR_NAMES)
                 and p.suffix not in SKIP_SUFFIXES
                 and p.name not in MANIFEST_FILENAMES}
    unclaimed = sorted(str(p.relative_to(ts)) for p in all_files - set(seen))

    return Manifest({
        "manifest_version": MANIFEST_VERSION,
        "task_set_dir": str(ts),
        "environment_dir": str(env),
        "groups": groups,
        "hashes": {
            "task_set_hash": groups["task_set"]["hash"],
            "answer_key_hash": groups["answer_key"]["hash"],
            "answer_key_scripts_hash": groups["answer_key_scripts"]["hash"],
            "scoring_spec_hash": groups["scoring_spec"]["hash"],
            "scorer_hash": groups["scorer"]["hash"],
            "config_hash": groups["config"]["hash"],
        },
        "unclaimed_files": unclaimed,
        "self_reference": "none - this manifest does not contain its own digest",
        "binding": ("the outer freeze record binds this manifest's digest to the artifact commit; "
                    "do not put a commit sha inside the manifest and the manifest's hash inside "
                    "that commit"),
    })


def verify(manifest_path: pathlib.Path, task_set_dir: pathlib.Path,
           env_dir: pathlib.Path) -> dict:
    """Re-derive and compare. Detects modified, added AND deleted files."""
    recorded = Manifest(json.loads(pathlib.Path(manifest_path).read_text()))
    current = build(task_set_dir, env_dir)

    report = {"ok": True, "groups": {}}
    for name in sorted(set(recorded.data["groups"]) | set(current.data["groups"])):
        old = recorded.data["groups"].get(name, {}).get("files", {})
        new = current.data["groups"].get(name, {}).get("files", {})
        modified = sorted(p for p in set(old) & set(new) if old[p] != new[p])
        added = sorted(set(new) - set(old))
        deleted = sorted(set(old) - set(new))
        ok = not (modified or added or deleted)
        report["groups"][name] = {
            "ok": ok,
            "hash_recorded": recorded.data["groups"].get(name, {}).get("hash"),
            "hash_current": current.data["groups"].get(name, {}).get("hash"),
            "modified": modified, "added": added, "deleted": deleted,
        }
        report["ok"] &= ok
    report["manifest_digest_recorded"] = recorded.digest()
    report["manifest_digest_current"] = current.digest()
    return report


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="build or verify the scoring-integrity manifest")
    ap.add_argument("action", choices=["build", "verify"])
    ap.add_argument("--task-set", required=True)
    ap.add_argument("--env", required=True)
    ap.add_argument("--manifest", required=True)
    a = ap.parse_args(argv)
    if a.action == "build":
        m = build(pathlib.Path(a.task_set), pathlib.Path(a.env))
        m.save(pathlib.Path(a.manifest))
        print(json.dumps({"hashes": m.data["hashes"],
                          "counts": {k: v["count"] for k, v in m.data["groups"].items()},
                          "unclaimed_files": m.data["unclaimed_files"],
                          "manifest_digest": m.digest()}, indent=2))
        return 0
    rep = verify(pathlib.Path(a.manifest), pathlib.Path(a.task_set), pathlib.Path(a.env))
    print(json.dumps(rep, indent=2))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

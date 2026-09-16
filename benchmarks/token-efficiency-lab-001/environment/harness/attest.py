"""Self-derived image attestation.

`container_digest` in a run record is a string the operator passed on the command line. Nothing
derived it from the image that was actually running, so a record can name an image that provably
could not have produced it — which is exactly what the Reproduction Agent found: all 10 dry-run
records named an image whose `blind.py` predates the E027 fix and which contains no `judge.py`
at all. Re-running the same command inside that image gives 9 completed, not 10.

The digest is still recorded, because it is what a verifier needs in order to pull the image.
But it is now recorded alongside something the container computes about *itself*, which a flag
cannot forge: a content hash over the harness and the fixed lab payload as they exist on disk
inside the running container.

Two runs in the same image agree. A run in a different image does not, and the disagreement is
visible in the record instead of being discovered a round later.
"""
from __future__ import annotations

import hashlib
import pathlib

# Everything that determines what the harness DOES. Deliberately excludes /lab/evidence (run
# output), /lab/tasks (mounted, and hashed separately as task_set_hash) and /lab/dryrun.
ATTESTED_PATHS = ("harness", "run_record_schema.json", "requirements.lock.txt", "calibration",
                  "pricing")

# Never hash these: they are build artefacts or caches, not behaviour.
SKIP_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache"}


def image_content_hash(root: str | pathlib.Path = "/lab") -> str:
    """Hash the harness and fixed payload as they exist inside the running container."""
    root = pathlib.Path(root)
    h = hashlib.sha256()
    for entry in ATTESTED_PATHS:
        target = root / entry
        if not target.exists():
            h.update(f"ABSENT:{entry}\0".encode())
            continue
        files = [target] if target.is_file() else sorted(
            p for p in target.rglob("*")
            if p.is_file() and not (set(p.parts) & SKIP_DIR_NAMES) and p.suffix != ".pyc"
        )
        for p in sorted(files, key=lambda q: str(q.relative_to(root))):
            h.update(str(p.relative_to(root)).encode())
            h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\0")
    return h.hexdigest()


def dependency_manifest_hash() -> str:
    """Hash the installed distribution set.

    ENVIRONMENT_LOCK.json carried a `dependency_manifest_sha256` that no code computed and no
    recipe documented; the Reproduction Agent tried six plausible derivations and matched none
    (WOULD-INVALIDATE 4). This is the recipe, in code, so the number is checkable.

    Definition: sha256 over `name==version\\n` lines for every installed distribution, names
    lowercased with underscores normalised to hyphens, sorted, UTF-8, trailing newline on each.
    """
    import importlib.metadata as md

    rows = sorted(
        f"{d.metadata['Name'].lower().replace('_', '-')}=={d.version}\n"
        for d in md.distributions()
    )
    return hashlib.sha256("".join(rows).encode()).hexdigest()


def attestation(container_digest: str | None, root: str | pathlib.Path = "/lab") -> dict:
    import platform

    return {
        "container_digest_asserted": container_digest,
        "container_digest_source": "operator-supplied; NOT derived from the running image",
        "image_content_sha256": image_content_hash(root),
        "dependency_manifest_sha256": dependency_manifest_hash(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(attestation(sys.argv[1] if len(sys.argv) > 1 else None), indent=2))

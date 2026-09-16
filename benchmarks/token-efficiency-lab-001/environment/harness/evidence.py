"""Evidence Producer — owner of `required_evidence`.

RT-01 was the single most consequential defect in the v1.0.0 stack, and it was a gap rather than
a bug: `build_packet` read `task.get("required_evidence", [])`, no task file carried that key, and
nothing anywhere in the lab produced one. Every packet shipped `required_evidence: []`, so
**10 of 17 byte-perfect answers failed** — all four A tasks and all four D tasks at score 0.0.
It fell between seats because it was nobody's declared deliverable. This module is the declared
deliverable, and the owning seat is `harness-evidence-producer`.

Two hard rules, both from METHODOLOGY_v1.1.0 §12.1:

**Static facts come from the frozen corpus, never from the model.** `valid_symbols` is derived by
parsing the repository with `ast`; the catalogs and rosters are read from the frozen CSVs. If a
run's own output could influence what it is scored against, the score means nothing.

**Dynamic facts come from the runner's audit, never from the model's self-report.** Tool calls are
read from the server-written audit log. An agent that says "I called the right tool" has said
nothing; the log is what happened.

And one rule about emptiness, from RT-02: **empty is not present.** `{}` and `[]` pass a type
check and silently disarm every zero-tolerance criterion that depends on them. Evidence is checked
for content, and missing-or-empty is `INVALID`, never a pass.
"""
from __future__ import annotations

import ast
import csv
import re
import hashlib
import json
import pathlib
from dataclasses import dataclass, field

OWNER_SEAT = "harness-evidence-producer"


class EvidenceError(RuntimeError):
    pass


# Which evidence fields each workload's zero-tolerance criteria consume. A workload whose
# required fields are absent, empty or wrongly typed yields INVALID.
# Fields that must be PRESENT AND NON-EMPTY. This list must agree with
# `judge.EVIDENCE_CONTRACT`; where the two disagree the stricter one silently decides, which is
# how NEW-11 happened - `corpus_access_log` was required non-empty here while the scorer reads
# its emptiness as a fact about the run, so every clean workload-D attempt was INVALID.
REQUIRED_BY_WORKLOAD = {
    # RT-08: all 17 v1.1.0 tasks name corpus_hashes_before AND corpus_hashes_after in their
    # failure_condition. One hash proves nothing about modification; two do.
    "A": ("valid_symbols", "corpus_hashes_before", "corpus_hashes_after"),
    "B": ("corpus_hashes_before", "corpus_hashes_after"),
    "C": ("corpus_hashes_before", "corpus_hashes_after", "corpus_files"),
    "D": ("corpus_hashes_before", "corpus_hashes_after"),
    "E": ("turns", "corpus_hashes_before", "corpus_hashes_after"),
}

# Task-specific additions, mirroring judge.EVIDENCE_CONTRACT exactly.
REQUIRED_BY_TASK = {
    "B-002": ("document_incident_ids",),
    "B-003": ("document_req_ids",),
    "C-002": ("document_award_ids",),
    "C-003": ("registry_plugin_ids",),
    "E-001": ("catalog_part_ids", "halberd_part_ids"),
    "E-003": ("shifts", "roster"),
}

# Produced for A and D, and allowed to be EMPTY. `tool_calls` empty is a finding the scorer makes
# (answered_without_calling_any_tool); `corpus_access_log` empty is a fact about the run. Neither
# is missing evidence, and requiring them non-empty here overrode the scorer's own judgement.
PRODUCED_BUT_MAY_BE_EMPTY = ("tool_calls", "corpus_access_log")

# Present in the audit for attribution and integrity, forbidden in a judge packet.
_AUDIT_ONLY_KEYS = frozenset({"run_id", "synthetic", "bytes"})

def _forbidden_keys() -> frozenset:
    """ONE list, shared with the blind gate.

    NEW-06: this module's own list was a strict SUBSET of `blind.FORBIDDEN_KEYS`, so
    `treatment_name`, `candidate_commit_sha` and `model_version` were caught by neither. Two
    lists that are supposed to agree and do not is the same defect as two seats that each believe
    the other's data shape. Imported lazily to keep the import graph acyclic.
    """
    from .blind import FORBIDDEN_KEYS
    return FORBIDDEN_KEYS


TREATMENT_LEAKING_KEYS = _forbidden_keys()


@dataclass
class Evidence:
    task_id: str
    workload: str
    fields: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dict(self.fields)


# ----------------------------------------------------------------------------- static producers

def valid_symbols(corpus_root: pathlib.Path, package: str = "ledgerline") -> list[str]:
    """Every module-level function defined under the package, fully qualified.

    Derived by parsing the frozen corpus with `ast`. Nested functions, lambdas, methods and
    imported names are excluded, matching workload A's rule R2. This is the set against which a
    fabricated symbol is judged, so it must come from the artefact, not from anyone's memory of
    the artefact.
    """
    root = pathlib.Path(corpus_root)
    pkg = root / package
    if not pkg.is_dir():
        raise EvidenceError(f"package {package!r} not found under {root}")
    out = []
    for py in sorted(pkg.rglob("*.py")):
        rel = py.relative_to(root).with_suffix("")
        mod = ".".join(rel.parts)
        if mod.endswith(".__init__"):
            mod = mod[: -len(".__init__")]
        try:
            tree = ast.parse(py.read_text())
        except SyntaxError as exc:
            raise EvidenceError(f"{py} does not parse: {exc}") from exc
        for node in tree.body:  # module level only
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append(f"{mod}.{node.name}")
    if not out:
        raise EvidenceError(f"no module-level functions found under {pkg}; evidence would be empty")
    return sorted(set(out))


def csv_column(path: pathlib.Path, column: str, where=None) -> list[str]:
    rows = list(csv.DictReader(pathlib.Path(path).read_text().splitlines()))
    if not rows:
        raise EvidenceError(f"{path} has no rows; evidence would be empty")
    if column not in rows[0]:
        raise EvidenceError(f"{path} has no column {column!r}; columns are {list(rows[0])}")
    vals = [r[column] for r in rows if (where is None or where(r))]
    return sorted(set(vals))


def csv_rows(path: pathlib.Path, key: str) -> dict:
    rows = list(csv.DictReader(pathlib.Path(path).read_text().splitlines()))
    if not rows:
        raise EvidenceError(f"{path} has no rows; evidence would be empty")
    return {r[key]: dict(r) for r in rows}


def document_ids(path: pathlib.Path, pattern: str) -> list[str]:
    """Every id of a given shape catalogued in a frozen document.

    The scorer needs the document's own inventory to decide whether a reported id was
    **fabricated**. Deriving it from the frozen artefact is the only way that check means
    anything: taken from the model's answer it would be circular, and taken from the answer key
    it would make any id the key omits unfalsifiable.
    """
    text = pathlib.Path(path).read_text(errors="ignore")
    found = sorted(set(re.findall(pattern, text)))
    if not found:
        raise EvidenceError(
            f"no id matching {pattern!r} found in {path}. Zero means the producer failed, not "
            "that the document is empty - the scorer would read it as an empty inventory and "
            "every reported id would look fabricated."
        )
    return found


def corpus_file_names(directory: pathlib.Path) -> list[str]:
    """The file listing a citation is checked against.

    A citation cannot be validated against an empty corpus listing, so this fails closed.
    """
    d = pathlib.Path(directory)
    names = sorted(p.name for p in d.iterdir() if p.is_file())
    if not names:
        raise EvidenceError(f"{d} lists no files; citations could not be checked against it")
    return names


# Build artefacts are not corpus. `manifest.py` and `attest.py` already skip them; this module
# did not, so running the corpus once put 51 `.pyc` files into `corpus_hashes` for every
# workload-A packet - and `corpus_modified` (RT-08) keys on the same maps, so a stray import
# could have failed an attempt for "modifying the corpus" (D-3).
_BUILD_ARTIFACT_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
_BUILD_ARTIFACT_SUFFIXES = {".pyc", ".pyo"}


def _is_build_artifact(p: pathlib.Path) -> bool:
    return bool(set(p.parts) & _BUILD_ARTIFACT_DIRS) or p.suffix in _BUILD_ARTIFACT_SUFFIXES


def corpus_hashes(task_root: pathlib.Path, corpus_paths: list[str]) -> dict:
    """Hash every file the task is allowed to read.

    RT-08: thirteen tasks carry "any corpus file is modified" as an outright failure condition and
    nothing evaluated it, so a corpus-rewriting optimisation scored clean. The runner takes this
    before and after the attempt and the judge compares.
    """
    root = pathlib.Path(task_root)
    out = {}
    for cp in corpus_paths:
        target = root / cp
        files = [target] if target.is_file() else sorted(
            p for p in target.rglob("*") if p.is_file() and not _is_build_artifact(p))
        for p in files:
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    if not out:
        raise EvidenceError(f"no corpus files found for {corpus_paths}; evidence would be empty")
    return out


# ---------------------------------------------------------------------------- dynamic producers

def tool_calls_from_audit(audit_path: pathlib.Path) -> list[dict]:
    """Read the server-written audit JSONL. NEVER the model's self-report.

    A missing audit file is not an empty list. An attempt whose tool use cannot be observed is
    unscoreable for any criterion that depends on tool use, and `validate` turns that into
    INVALID.
    """
    p = pathlib.Path(audit_path)
    if not p.exists():
        raise EvidenceError(
            f"tool audit {p} does not exist. The attempt's tool use cannot be observed, so any "
            "criterion that depends on it is unmeasurable. This is INVALID, not zero calls."
        )
    calls = []
    for i, line in enumerate(p.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            calls.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise EvidenceError(f"{p}:{i} is not valid JSON: {exc}") from exc
    return calls


def filter_audit_to_run(calls: list[dict], run_id: str) -> list[dict]:
    """Cross-run contamination control.

    The offline tool server writes one shared audit log, so a log will normally contain entries
    from several attempts. The protection is not "the file must contain only this run" — it is
    that **an entry from another attempt can never score this one**. So entries are filtered by
    run id, and two things are refused outright:

    * an entry carrying **no** run id at all, because an unattributable call cannot be excluded
      and cannot be counted either, and silently dropping it would undercount wrong-tool use;
    * a run with **zero** entries of its own, because "no calls were logged" and "this workload
      made no calls" are different states and only one of them is scoreable.
    """
    unattributed = [c for c in calls if not c.get("run_id")]
    if unattributed:
        raise EvidenceError(
            f"{len(unattributed)} tool-audit entr(ies) carry no run_id. An unattributable call "
            "can neither be excluded nor counted, and dropping it would undercount wrong-tool "
            "use - which is a zero-tolerance criterion."
        )
    mine = [c for c in calls if c["run_id"] == run_id]
    if not mine:
        others = sorted({c["run_id"] for c in calls})[:4]
        raise EvidenceError(
            f"the tool audit contains no entry for run {run_id} (it has entries for {others}). "
            "'No calls were logged' and 'this attempt made no calls' are different states; only "
            "one of them is scoreable, and this is the other one."
        )
    return mine


def assert_turns_complete(turns: list[dict], expected: int) -> None:
    """RT-13 / UG-28.

    If the runner ships only the final reply, most of workload E's violation classes cannot fire:
    a byte-perfect E-002 runbook with a violation at turn 8 scored 1.0 and passed when `turns` was
    omitted. A short, reordered or duplicated transcript is INVALID.
    """
    if not isinstance(turns, list) or not turns:
        raise EvidenceError("turns is missing or empty; workload E is unscoreable without it")
    nums = [t.get("turn") for t in turns]
    if any(not isinstance(n, int) for n in nums):
        raise EvidenceError(f"every turn needs an integer `turn` index; got {nums}")
    if len(set(nums)) != len(nums):
        raise EvidenceError(f"duplicate turn indices: {sorted(n for n in nums if nums.count(n) > 1)}")
    if nums != sorted(nums):
        raise EvidenceError(f"turns are out of order: {nums}")
    if len(turns) != expected:
        raise EvidenceError(
            f"{len(turns)} turns supplied but the task declares {expected}. A truncated "
            "transcript hides every violation after the cut. If the run stopped early, mark it "
            "early_stop explicitly - do not fabricate the missing turns."
        )


# ------------------------------------------------------------------------------- orchestration

def required_fields(task: dict) -> tuple[str, ...]:
    return tuple(REQUIRED_BY_WORKLOAD[task["workload"]]) + tuple(
        REQUIRED_BY_TASK.get(task["task_id"], ())
    )


def validate(evidence: dict, task: dict) -> None:
    """Content check, not a type check. Empty fails closed.

    RT-02: `{"shifts": {}, "roster": {}}` passed every type check in the v1.0.0 judge and silently
    disabled workload E's zero-tolerance criteria, so a run assigning an ineligible person scored
    `task_success: true`. Emptiness is the failure mode, so emptiness is what is checked.
    """
    missing, empty = [], []
    for f in required_fields(task):
        if f not in evidence:
            missing.append(f)
        elif evidence[f] is None or (hasattr(evidence[f], "__len__") and len(evidence[f]) == 0):
            empty.append(f)
    if missing or empty:
        parts = []
        if missing:
            parts.append("missing:" + ",".join(missing))
        if empty:
            parts.append("empty:" + ",".join(empty))
        raise EvidenceError(
            "required_evidence_" + " ".join(parts) +
            " - the attempt is INVALID (methodology v1.1.0 section 6.2), not a pass and not a "
            "quality failure"
        )


def assert_treatment_neutral(evidence: dict) -> None:
    """The evidence must not tell the judge which treatment produced the attempt."""
    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                yield path + "/" + str(k), k
                yield from walk(v, path + "/" + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from walk(v, f"{path}[{i}]")
    forbidden = _forbidden_keys()
    for full, key in walk(evidence):
        if key in forbidden:
            raise EvidenceError(
                f"evidence leaks {key!r} at {full}. required_evidence reaches the Quality Judge, "
                "so anything identifying in it defeats the blind as surely as a metadata field."
            )


def access_log_from_audit(calls: list[dict], corpus_paths: list[str]) -> list[str]:
    """Which corpus files the attempt actually touched, as a LIST OF PATH STRINGS.

    A-001's only anti-shortcut guard is "the answer is produced without reading the corpus", and
    v1.0.0 implemented it nowhere — so the blanket answer that reads nothing had no guard at all.
    The log is built from the runner's audit, never from the model saying it read something.

    **The shape is `list[str]` and that is not arbitrary.** This function previously returned
    `list[dict]` while the judge matched with `isinstance(p, str)`, and `README.md` and
    `SCORING_SPEC` §4.1 both declared `[path]`. One mismatch produced two opposite failures:
    A-001's read guard never saw a hit and failed every legitimate run, while D's
    fixtures-read prohibition never saw a hit and **failed open** — a D run reading
    `corpora/mcp_toolset/fixtures/` scored 1.0000 with the answers handed to it (NEW-04).

    Two seats each believing the other's shape is exactly the seam this round kept finding.
    """
    out = []
    for c in calls:
        args = c.get("arguments") or {}
        target = args.get("path") or args.get("file") or args.get("corpus_path") \
            or c.get("reads_corpus")
        if target:
            out.append(str(target))
    # Ordered, de-duplicated: a path read twice is one access for every purpose the log serves.
    seen, uniq = set(), []
    for pth in out:
        if pth not in seen:
            seen.add(pth); uniq.append(pth)
    return uniq


def produce(task: dict, task_root: pathlib.Path, *, run_id: str,
            audit_path: pathlib.Path | None = None,
            turns: list[dict] | None = None,
            corpus_before: dict | None = None,
            corpus_after: dict | None = None,
            corpus_access_log: list | None = None) -> Evidence:
    """Build the required evidence for one attempt. Raises rather than returning a partial set."""
    root = pathlib.Path(task_root)
    wl, tid = task["workload"], task["task_id"]
    ev = Evidence(task_id=tid, workload=wl)
    prov = ev.provenance

    paths = task["input"].get("corpus_paths", [])
    before = corpus_before if corpus_before is not None else corpus_hashes(root, paths)
    after = corpus_after if corpus_after is not None else corpus_hashes(root, paths)
    ev.fields["corpus_hashes_before"] = before
    ev.fields["corpus_hashes_after"] = after
    # Kept as an alias: the Quality Judge accepts it as the "before" map, and older records use it.
    ev.fields["corpus_hashes"] = before
    prov["corpus_hashes_before"] = "sha256 of every corpus file, taken before the attempt ran"
    prov["corpus_hashes_after"] = "the same files, re-hashed after the attempt; a difference fails it"

    if wl == "A":
        corpus = root / task["input"]["corpus_paths"][0]
        ev.fields["valid_symbols"] = valid_symbols(corpus)
        prov["valid_symbols"] = f"ast parse of module-level defs under {corpus}/ledgerline"

    if wl in ("A", "D"):
        if audit_path is None:
            raise EvidenceError(f"workload {wl} needs a tool audit path; none was supplied")
        calls = filter_audit_to_run(tool_calls_from_audit(audit_path), run_id)
        # The audit carries `run_id` for attribution, which is exactly what the blind gate
        # forbids in a packet. Attribution happens HERE, at filter time; the judge only needs to
        # know which tools were called with what. Strip it rather than widening the blind rule -
        # the rule is right, the payload was wrong.
        calls = [{k: v for k, v in c.items() if k not in _AUDIT_ONLY_KEYS} for c in calls]
        ev.fields["tool_calls"] = calls
        log = corpus_access_log if corpus_access_log is not None else access_log_from_audit(
            calls, paths)
        ev.fields["corpus_access_log"] = log
        prov["corpus_access_log"] = (
            "corpus reads observed in the runner's audit. Never the model's claim to have read "
            "something - A-001's anti-shortcut guard depends on this being observed.")
        prov["tool_calls"] = (
            f"server-written audit at {audit_path}, filtered to run {run_id}; "
            f"{len(calls)} entr(ies) attributed to this attempt")

    if wl == "E":
        expected = task["input"].get("turn_count") or task.get("turn_count")
        if not expected:
            raise EvidenceError(f"{tid} declares no turn_count; turn completeness is uncheckable")
        assert_turns_complete(turns or [], int(expected))
        ev.fields["turns"] = turns
        prov["turns"] = f"captured by the runner; {expected} turns asserted complete and ordered"

    if wl == "B":
        docs = root / "corpora" / "docs_b"
        if tid == "B-002":
            ev.fields["document_incident_ids"] = document_ids(
                docs / "KESTREL_RELIABILITY_2031.md", r"INC-\d{4}-\d{3}")
            prov["document_incident_ids"] = "every INC-nnnn-nnn catalogued in the frozen document"
        if tid == "B-003":
            spec = next(p for p in docs.iterdir() if "PROTOCOL" in p.name)
            # The document catalogues SDX-REQ-nnnn. A bare `\bREQ-` pattern matches the
            # TAIL of each id, so the produced inventory contained 96 ids none of which was a
            # real one - and every reported id looked fabricated against it. An inventory that
            # is non-empty is not the same as an inventory that is right.
            ev.fields["document_req_ids"] = document_ids(spec, r"\b[A-Z]{2,5}-REQ-\d{3,5}\b")
            prov["document_req_ids"] = f"every REQ-* catalogued in {spec.name}"

    if wl == "C":
        rc = root / "corpora" / "research_c"
        ev.fields["corpus_files"] = corpus_file_names(rc)
        prov["corpus_files"] = "the research_c file listing a citation is checked against"
        blob = "\n".join(p.read_text(errors="ignore") for p in sorted(rc.iterdir()) if p.is_file())
        if tid == "C-002":
            ev.fields["document_award_ids"] = sorted(set(re.findall(r"\bGA-\d{4}\b", blob))) or None
            if not ev.fields["document_award_ids"]:
                raise EvidenceError("no GA-nnnn award ids found in corpora/research_c")
            prov["document_award_ids"] = "every GA-nnnn award id appearing in research_c"
        if tid == "C-003":
            ev.fields["registry_plugin_ids"] = sorted(set(re.findall(r"\bkp-[a-z0-9-]+\b", blob)))
            if not ev.fields["registry_plugin_ids"]:
                raise EvidenceError("no kp-* plugin ids found in corpora/research_c")
            prov["registry_plugin_ids"] = "every kp-* plugin id appearing in research_c"

    if tid == "E-001":
        wf = root / "corpora" / "workflow_e"
        ev.fields["catalog_part_ids"] = csv_column(wf / "parts_catalog.csv", "part_id")
        ev.fields["halberd_part_ids"] = csv_column(
            wf / "parts_catalog.csv", "part_id",
            where=lambda r: "halberd" in r.get("vendor", "").lower())
        prov["catalog_part_ids"] = "parts_catalog.csv part_id column"
        prov["halberd_part_ids"] = "parts_catalog.csv rows whose vendor matches Halberd"

    if tid == "E-003":
        wf = root / "corpora" / "workflow_e"
        ev.fields["shifts"] = csv_rows(wf / "shifts.csv", "shift_id")
        ev.fields["roster"] = csv_rows(wf / "staff_roster.csv", list(
            csv.DictReader((wf / "staff_roster.csv").read_text().splitlines()).fieldnames)[0])
        prov["shifts"] = "shifts.csv keyed by shift_id"
        prov["roster"] = "staff_roster.csv keyed by its first column"

    validate(ev.fields, task)
    assert_treatment_neutral(ev.fields)
    return ev


def compare_corpus_hashes(before: dict, after: dict) -> list[str]:
    """RT-08. Returns the list of modified/added/removed corpus paths; empty means untouched."""
    changed = [p for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)]
    return changed

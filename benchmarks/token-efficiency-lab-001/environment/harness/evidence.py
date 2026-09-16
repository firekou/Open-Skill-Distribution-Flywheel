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
import hashlib
import json
import pathlib
from dataclasses import dataclass, field

OWNER_SEAT = "harness-evidence-producer"


class EvidenceError(RuntimeError):
    pass


# Which evidence fields each workload's zero-tolerance criteria consume. A workload whose
# required fields are absent, empty or wrongly typed yields INVALID.
REQUIRED_BY_WORKLOAD = {
    "A": ("valid_symbols", "tool_calls", "corpus_hashes"),
    "B": ("corpus_hashes",),
    "C": ("corpus_hashes",),
    "D": ("tool_calls", "corpus_hashes"),
    "E": ("turns", "corpus_hashes"),
}

# Task-specific additions on top of the workload defaults.
REQUIRED_BY_TASK = {
    "E-001": ("catalog_part_ids", "halberd_part_ids"),
    "E-003": ("shifts", "roster"),
}

# Nothing in here may identify a treatment. Asserted by `assert_treatment_neutral`.
TREATMENT_LEAKING_KEYS = frozenset(
    {"condition", "treatment", "candidate", "candidate_name", "model", "model_pair", "provider",
     "cost", "input_tokens", "output_tokens", "total_tokens", "cached_tokens", "token_source",
     "pricing_snapshot_id", "retries", "escalations", "latency_ms", "repository", "repo"}
)


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
        files = [target] if target.is_file() else sorted(p for p in target.rglob("*") if p.is_file())
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
    for full, key in walk(evidence):
        if key in TREATMENT_LEAKING_KEYS:
            raise EvidenceError(
                f"evidence leaks {key!r} at {full}. required_evidence reaches the Quality Judge, "
                "so anything identifying in it defeats the blind as surely as a metadata field."
            )


def produce(task: dict, task_root: pathlib.Path, *, run_id: str,
            audit_path: pathlib.Path | None = None,
            turns: list[dict] | None = None) -> Evidence:
    """Build the required evidence for one attempt. Raises rather than returning a partial set."""
    root = pathlib.Path(task_root)
    wl, tid = task["workload"], task["task_id"]
    ev = Evidence(task_id=tid, workload=wl)
    prov = ev.provenance

    ev.fields["corpus_hashes"] = corpus_hashes(root, task["input"].get("corpus_paths", []))
    prov["corpus_hashes"] = "sha256 of every file under the task's declared corpus_paths"

    if wl == "A":
        corpus = root / task["input"]["corpus_paths"][0]
        ev.fields["valid_symbols"] = valid_symbols(corpus)
        prov["valid_symbols"] = f"ast parse of module-level defs under {corpus}/ledgerline"

    if wl in ("A", "D"):
        if audit_path is None:
            raise EvidenceError(f"workload {wl} needs a tool audit path; none was supplied")
        calls = filter_audit_to_run(tool_calls_from_audit(audit_path), run_id)
        ev.fields["tool_calls"] = calls
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

#!/usr/bin/env python3
"""ATK Token Efficiency Lab 001 — blind Quality Judge scorer.

Deterministic, offline, standard-library only.  Implements
`tasks/TASK_SET_v1.0.0/SCORING_SPEC.md`, which is the normative document; this
module is its executable form.  Where the two disagree, the spec is the defect
report and this module is the bug.

Contract
--------
    score_packet(packet: dict) -> dict

`packet` is a **blind judge packet** carrying exactly these nine keys:

    packet_id, task_id, workload, blind_treatment_id, model_output,
    required_evidence, answer_key, quality_metric, failure_condition

Anything else in the mapping is ignored: `_view()` copies the nine allowed keys
into a fresh dict and every scorer reads only from that copy, so a packet that
leaks a token count, a cost, a model name or a condition label cannot influence
a score even by accident.  Leaked keys are reported in
`detail.ignored_packet_keys` so the leak is visible to the Runner and the Red
Team without ever reaching the scoring path.

Guarantees
----------
* Deterministic: the same packet always produces the same score.
* Offline: no network, no filesystem access during scoring.
* Total: `score_packet` never raises.  Empty, truncated, garbage or
  wrong-shaped model output scores 0.0 with `task_success=false` and a stated
  `failure_reason`.
* Fail-closed: a zero-tolerance criterion that cannot be *verified* from the
  packet fails the task.  An unverifiable zero-tolerance criterion never passes.

Zero tolerance (methodology v1.0.0 section 6)
---------------------------------------------
A zero-tolerance breach sets `task_success=false` and
`zero_tolerance_breached=true` **regardless of `quality_score`**.  The score is
still reported, deliberately: a fabrication on an otherwise excellent answer
must be visible as exactly that, not laundered into a low number.

CLI
---
    python3 judge.py --packets <dir-in> --scores <dir-out> [--quiet]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

SPEC_VERSION = "1.1.0"

# Methodology versions this module knows how to score.  A packet carrying
# anything else - including nothing at all - is REFUSED (methodology v1.1.0
# section 13).  Silent cross-version scoring is how a v1.0.0 relative floor
# would survive into a v1.1.0 result.
V1_0_0 = "1.0.0"
V1_1_0 = "1.1.0"
SUPPORTED_METHODOLOGY_VERSIONS = (V1_0_0, V1_1_0)

# The ten fields a blind packet may carry.  Nothing else is ever read.
# `methodology_version` is treatment-neutral: it names the rulebook, not the
# condition, and without it the packet cannot be scored at all (section 13).
ALLOWED_PACKET_KEYS = (
    "packet_id",
    "task_id",
    "workload",
    "blind_treatment_id",
    "model_output",
    "required_evidence",
    "answer_key",
    "quality_metric",
    "failure_condition",
    "methodology_version",
)

# ---- attempt-level quality floors -----------------------------------------
# v1.1.0 section 6: ABSOLUTE, measured against the full answer key.  No floor
# is a function of any other attempt's result.
FLOOR_A = 0.95
FLOOR_B = 0.97
FLOOR_C_COVERAGE = 0.90
FLOOR_C_TRACEABILITY = 1.0
FLOOR_E_COMPLETION = 0.95
# v1.0.0 only: the multiplier applied to the baseline C0 median.  Reachable
# exclusively from the version-gated v1.0.0 replay path.
REL_FLOOR_A = 0.95
REL_FLOOR_C = 0.90

# ---- outcome taxonomy (v1.1.0 section 6.2) --------------------------------
PASS = "PASS"
FAIL_QUALITY = "FAIL_QUALITY"
INVALID = "INVALID"

# Reasons that mean "we could not measure this attempt", as opposed to "this
# attempt failed".  Prefix match: `required_evidence_missing:valid_symbols`
# matches `required_evidence_missing:`.  Everything not listed here and not a
# pass is FAIL_QUALITY - a scored, genuine failure.
INVALID_REASON_PREFIXES = (
    "required_evidence_missing:",
    "required_evidence_empty:",
    "evidence_from_wrong_run",
    "evidence_incomplete:",
    "answer_key_unavailable",
    "packet_unreadable",
    "judge_internal_error",
    "unknown_task_id",
    "unknown_workload",
    "methodology_version_absent",
    "methodology_version_unsupported",
)

COUNT_PENALTY = 0.05
NUM_TOL = 1e-9

# ---- how `count` is scored, per task --------------------------------------
# SCORING_SPEC precedence: the frozen task text is authoritative over this
# module.  v1.1.0 replaces v1.0.0's flat -0.05 everywhere, in three different
# ways, each ruled in the task text (RT-09 / RT-10):
#
#   A-001..A-004   "subtracts 0.02 from quality_score ... reported separately
#                   as count_consistent: false"
#   B-002 / B-003  "Comparable cells = 7 * |K| + 1 ... plus one cell for
#                   `count`" - one ordinary cell, no subtraction
#   C-001..C-003   "NOT one of the comparable cells ... does not change
#                   coverage, does not change traceability and does not fail
#                   the task"
#   B-001          has no `count` field at all
#
# ("subtract", amount) | ("cell", 0.0) | ("none", 0.0).  The table is the
# frozen transcription and `count_rule_from_text` re-derives the same answer
# from the packet's own `quality_metric`; the two are cross-checked by the
# test suite against the real task files, so a Designer ruling cannot drift
# away from the scorer unnoticed.
COUNT_RULE_V11 = {
    "A-001": ("subtract", 0.02), "A-002": ("subtract", 0.02),
    "A-003": ("subtract", 0.02), "A-004": ("subtract", 0.02),
    "B-001": ("none", 0.0), "B-002": ("cell", 0.0), "B-003": ("cell", 0.0),
    "C-001": ("none", 0.0), "C-002": ("none", 0.0), "C-003": ("none", 0.0),
}
_SUBTRACT_RE = re.compile(r"subtracts?\s+(0\.\d+)\s+from\s+quality_score",
                          re.IGNORECASE)
_COUNT_CELL_RE = re.compile(
    r"plus\s+one\s+cell\s+for\s+.?count|`count`\s+cell\s+matches"
    r"|scored\s+as\s+exactly\s+one\s+comparable\s+cell", re.IGNORECASE)
_COUNT_NONE_RE = re.compile(
    r"not\s+one\s+of\s+the\s+comparable\s+cells|does\s+not\s+change\s+coverage"
    r"|no\s+count\s+penalty", re.IGNORECASE)


def count_rule_from_text(metric: Any) -> Optional[Tuple[str, float]]:
    """Re-derive the `count` rule from the frozen task text, or None."""
    if not isinstance(metric, str) or "count" not in metric.lower():
        return None
    if _COUNT_NONE_RE.search(metric):
        return ("none", 0.0)
    m = _SUBTRACT_RE.search(metric)
    if m:
        return ("subtract", float(m.group(1)))
    if _COUNT_CELL_RE.search(metric):
        return ("cell", 0.0)
    return None

_MISSING = object()

# Keys an answer key carries about its own derivation.  They are provenance,
# never scored fields, and are excluded wherever a metric says "every key of
# the answer key" (B-001).
KEY_METADATA_FIELDS = frozenset({
    "task_id", "derived_by", "derivation_method", "derivation_script",
    "derivation_diagnostics", "corrections_applied", "notes", "note",
    "citation_support", "required_tools", "required_tool_set",
    "contested_families", "tool_calls_made_by_this_derivation",
    "as_of_date", "answer", "expected", "expected_output", "payload", "value",
})


# ---------------------------------------------------------------------------
# frozen per-task tables
#
# Transcribed from tasks/TASK_SET_v1.0.0/tasks/**.  Held here rather than read
# from `required_evidence` so that the scoring basis for a zero-tolerance
# criterion cannot be narrowed by whatever built the packet.  A packet that
# disagrees is recorded in detail, not obeyed.
# ---------------------------------------------------------------------------

A_LIST_FIELD = {
    "A-001": "reaching_functions",
    "A-002": "unreferenced_functions",
    "A-003": "retry_decorated_reaching_transient",
}

B_RECORD_SPEC = {
    # task_id: (array field, id field, scored cell fields, evidence key of real ids)
    "B-002": (
        "incidents",
        "incident_id",
        ("incident_id", "service", "start_utc", "duration_minutes",
         "final_severity", "root_cause_code", "customer_impacting"),
        "document_incident_ids",
    ),
    "B-003": (
        "requirements",
        "req_id",
        ("req_id", "section", "constrained_field", "level_source"),
        "document_req_ids",
    ),
}

C_RECORD_SPEC = {
    # task_id: (array field, id field, scored cells, sorted-list cells, evidence key)
    "C-001": ("flags", "flag", ("flag", "introduced_in", "removed_in"), (), None),
    "C-002": (
        "projects",
        "project",
        ("project", "total_awarded_eur", "awards_included", "awards_excluded"),
        ("awards_included", "awards_excluded"),
        "document_award_ids",
    ),
    "C-003": (
        "plugins",
        "plugin_id",
        ("plugin_id", "min_kestrel_version", "governing_source_tier", "contradicted_by"),
        ("contradicted_by",),
        "registry_plugin_ids",
    ),
}

D_SPEC = {
    "D-001": (
        ("engineer_full_name", "team", "escalation_tier"),
        ("oncall-resolution", "person-resolution"),
    ),
    "D-002": (
        ("digest", "critical_open_count", "highest_cvss_advisory_id",
         "distribution", "fixed_version"),
        ("image-digest-resolution", "vuln-findings"),
    ),
    "D-003": (
        ("ship_date", "fiscal_year", "fiscal_quarter", "fiscal_period",
         "period_close_date"),
        ("order-document-resolution", "fiscal-period-resolution",
         "calendar-period-resolution"),
    ),
    "D-004": (
        ("remaining_error_budget_minutes", "effective_resolution_target_minutes",
         "measured_resolution_minutes", "sla_breached"),
        ("error-budget", "sla-resolution"),
    ),
}

# Tool families whose members are never wrong-tool invocations.
D_EXEMPT_FAMILIES = frozenset({"meta"})

E_MONEY_SCALARS = (
    "hardware_subtotal_eur",
    "service_subtotal_eur",
    "freight_eur",
    "contingency_eur",
    "grand_total_eur",
    "amount_over_cap_eur",
)
E_MONEY_LINE_FIELDS = ("unit_price_eur", "line_total_eur")
E1_MONEY_RE = re.compile(r"^[0-9]+\.[0-9]{2}$")

E2_STEP_ID_RE = re.compile(r"^MIG-(\d{3})$")
E2_STEP_TOKEN_RE = re.compile(r"MIG-\d{3}")
E2_BANNED_WORD_RE = re.compile(r"\b(simply|just)\b", re.IGNORECASE)
# A "timestamp" is a token carrying both a date and a time-of-day.
E2_TS_CANDIDATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?")
E2_TS_OK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

E3_SHIFT_TOKEN_RE = re.compile(r"\bSH-\d+\b")
E3_PERSON_TOKEN_RE = re.compile(r"\bPR-\d+\b")
# Evidence each workload-E task needs before its rule-based violation classes
# can fire at all.  Missing evidence makes a zero-tolerance criterion
# unverifiable, which fails the task closed (SCORING_SPEC section 2).
#
# Emptiness is decided per task from that task's own manifest contract, not by
# a blanket rule.  In this task set `parts_catalog.csv` holds 24 parts, 4 of
# them Halberd Manufacturing's; `shifts.csv` holds 12 shifts and
# `staff_roster.csv` 16 people.  None of these sets can legitimately be empty,
# so an empty one is the evidence producer failing, not a corpus that permits
# nothing - and it must never silently disable V1-V5 (RT-02).
E_REQUIRED_EVIDENCE = {
    # task_id: ((field, minimum size), ...)
    "E-001": (("catalog_part_ids", 1), ("halberd_part_ids", 1)),
    "E-002": (),
    "E-003": (("shifts", 1), ("roster", 1)),
}

# Evidence a workload-E packet may legitimately omit or ship empty: each
# describes an event that may simply not have happened.
E_OPTIONAL_EVIDENCE = ("additional_on_leave", "max_shifts_overrides",
                       "precomputed_violations", "completed_turns",
                       "run_reached_final_turn")

# Transcribed from the frozen task files' `input.turn_count`.  Held here, not
# read from the packet, for the same reason the contested-family lists are:
# the basis of a zero-tolerance check may not be narrowed by whatever built
# the packet.  A packet that disagrees has the disagreement recorded.
E_TURN_COUNT = {"E-001": 18, "E-002": 16, "E-003": 20}

E3_REASONS = (
    "no_person_with_required_certification_at_site",
    "all_eligible_on_leave",
    "no_night_qualified_person",
    "max_shifts_exhausted",
)


# ---------------------------------------------------------------------------
# small utilities
# ---------------------------------------------------------------------------

def _round4(x: float) -> float:
    """Round half-away-from-zero to 4 dp, so two judges agree on ties."""
    if not isinstance(x, (int, float)) or isinstance(x, bool):
        return 0.0
    if math.isnan(x) or math.isinf(x):
        return 0.0
    scaled = x * 10000.0
    floor = math.floor(abs(scaled))
    frac = abs(scaled) - floor
    n = floor + 1 if frac >= 0.5 - 1e-12 else floor
    out = n / 10000.0
    return -out if x < 0 else out


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _type_class(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return "unknown"


def _canon(v: Any) -> Any:
    """Canonical form for deep equality: strings stripped, numbers floated."""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, list):
        return [_canon(x) for x in v]
    if isinstance(v, dict):
        return {k: _canon(x) for k, x in sorted(v.items())}
    return v


def _values_equal(reported: Any, key: Any, sorted_list: bool = False) -> bool:
    """Cell comparison per SCORING_SPEC section 3.

    Type classes must match (a number is never equal to the string of that
    number, a boolean is never equal to 0 or 1).  Strings compare
    case-sensitively after stripping surrounding whitespace.  Numbers compare
    numerically within NUM_TOL.  A missing cell never matches.
    """
    if reported is _MISSING:
        return False
    if _type_class(reported) != _type_class(key):
        return False
    if key is None:
        return True
    if isinstance(key, bool):
        return reported is key or reported == key
    if _is_number(key):
        return abs(float(reported) - float(key)) <= NUM_TOL
    if isinstance(key, str):
        return reported.strip() == key.strip()
    if isinstance(key, list):
        a = [_canon(x) for x in reported]
        b = [_canon(x) for x in key]
        if sorted_list:
            try:
                a = sorted(a, key=_sort_key)
                b = sorted(b, key=_sort_key)
            except Exception:
                return False
        return a == b
    return _canon(reported) == _canon(key)


def _sort_key(v: Any) -> Tuple[str, str]:
    return (_type_class(v), json.dumps(_canon(v), sort_keys=True, default=str))


def _get(obj: Any, field: str) -> Any:
    if isinstance(obj, dict) and field in obj:
        return obj[field]
    return _MISSING


def _as_text(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    try:
        return json.dumps(v, sort_keys=True, default=str)
    except Exception:
        return str(v)


def _str_set(values: Any) -> Set[str]:
    out: Set[str] = set()
    if isinstance(values, (list, tuple, set)):
        for v in values:
            if isinstance(v, str):
                out.add(v.strip())
    elif isinstance(values, dict):
        for v in values.keys():
            if isinstance(v, str):
                out.add(v.strip())
    return out


# ---------------------------------------------------------------------------
# model-output parsing
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*```[A-Za-z0-9_+-]*\s*\n(.*?)\n?\s*```\s*$", re.DOTALL)


def _find_object_span(text: str) -> Optional[str]:
    """First balanced top-level {...} in `text`, string- and escape-aware."""
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        start = text.find("{", start + 1)
    return None


def parse_model_json(raw: Any) -> Tuple[Optional[dict], str, Dict[str, Any]]:
    """Extract the single JSON object a task asked for.

    Returns (obj_or_None, parse_mode, info).  parse_mode is one of
    "strict", "fence_stripped", "embedded_object", "already_object",
    "empty", "unparseable".

    Extraction is lenient (see SCORING_SPEC UG-01): prose or a code fence
    around an otherwise valid object does not fail the task, but is recorded
    as `format_strict: false` so a format regression is still visible.
    """
    info: Dict[str, Any] = {"format_strict": True, "truncation_suspected": False}

    if isinstance(raw, dict):
        return raw, "already_object", info
    if raw is None:
        return None, "empty", info
    if not isinstance(raw, str):
        raw = _as_text(raw)

    text = raw.strip()
    if not text:
        return None, "empty", info

    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj, "strict", info
    except Exception:
        pass

    info["format_strict"] = False

    m = _FENCE_RE.match(text)
    if m:
        try:
            obj = json.loads(m.group(1).strip())
            if isinstance(obj, dict):
                return obj, "fence_stripped", info
        except Exception:
            pass

    span = _find_object_span(text)
    if span is not None:
        try:
            obj = json.loads(span)
            if isinstance(obj, dict):
                return obj, "embedded_object", info
        except Exception:
            pass

    # No balanced object: an unbalanced opening brace is the signature of a
    # truncated reply.
    if text.count("{") > text.count("}"):
        info["truncation_suspected"] = True
    return None, "unparseable", info


def split_turns(model_output: Any) -> Tuple[List[Dict[str, Any]], Any]:
    """Normalise a workload-E model_output into (turn replies, final reply).

    Accepted shapes (SCORING_SPEC section 7.1):
      {"turns": [{"turn": n, "text": "..."}, ...], "final_reply": "..."}
      {"turns": [...]}                         -> final reply is the last turn
      [{"turn": n, "text": "..."}, ...]        -> same
      "<string>"                               -> a single reply, turn 0
    """
    turns: List[Dict[str, Any]] = []
    final: Any = None

    raw_turns: Any = None
    if isinstance(model_output, dict):
        for k in ("turns", "replies", "messages"):
            if isinstance(model_output.get(k), list):
                raw_turns = model_output[k]
                break
        for k in ("final_reply", "final", "final_answer", "final_output"):
            if k in model_output and model_output[k] is not None:
                final = model_output[k]
                break
        if raw_turns is None and final is None:
            # a bare object: treat it as the final reply itself
            return [], model_output
    elif isinstance(model_output, list):
        raw_turns = model_output
    else:
        return ([{"turn": 0, "text": _as_text(model_output)}] if model_output else [],
                model_output)

    if isinstance(raw_turns, list):
        for i, t in enumerate(raw_turns):
            if isinstance(t, dict):
                n = t.get("turn", t.get("index", i + 1))
                try:
                    n = int(n)
                except Exception:
                    n = i + 1
                txt = t.get("text", t.get("reply", t.get("content", t.get("output", ""))))
                turns.append({"turn": n, "text": _as_text(txt), "raw": txt})
            else:
                turns.append({"turn": i + 1, "text": _as_text(t), "raw": t})

    if final is None and turns:
        final = turns[-1].get("raw", turns[-1]["text"])
    return turns, final


# ---------------------------------------------------------------------------
# result construction
# ---------------------------------------------------------------------------

def outcome_for(failure_reason: Optional[str], task_success: bool) -> str:
    """The v1.1.0 section 6.2 outcome for one attempt.

    Three values, never two.  `INVALID` means the attempt could not be
    scored - missing, empty, wrongly typed or wrong-run evidence.  It is not a
    pass and it is not a quality failure: "it failed" and "we could not measure
    it" are different findings and are reported separately.
    """
    if task_success:
        return PASS
    reason = failure_reason or ""
    for pre in INVALID_REASON_PREFIXES:
        if reason.startswith(pre):
            return INVALID
    return FAIL_QUALITY


def _result(view: Dict[str, Any], *, quality_score: float = 0.0,
            task_success: bool = False, failure_reason: Optional[str] = None,
            zero_tolerance_breached: bool = False,
            detail: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    d = dict(detail or {})
    mv = view.get("_mv") or V1_0_0
    d.setdefault("spec_version", SPEC_VERSION)
    d.setdefault("methodology_version", mv)
    # Every number this module produces is attempt-level (v1.1.0 section 6.1).
    # Cell and aggregate levels belong to the Runner / Aggregator; no threshold
    # in this module is ever applied at more than one level.
    d.setdefault("level", "attempt")
    score = _round4(max(0.0, min(1.0, float(quality_score))))
    outcome = outcome_for(failure_reason, task_success)
    if mv == V1_1_0 and outcome == INVALID and score > 0.0:
        # An unscorable attempt has no quality score.  The number that was
        # computed before the measurement was found unverifiable is retained
        # in detail so the failure is auditable, but it may not be reported as
        # quality and may not be averaged (v1.1.0 section 6.2).
        d["unverified_quality_score"] = score
        score = 0.0
    return {
        "packet_id": view.get("packet_id"),
        "task_id": view.get("task_id"),
        "workload": view.get("workload"),
        "blind_treatment_id": view.get("blind_treatment_id"),
        "quality_score": score,
        "task_success": bool(task_success),
        "outcome": outcome,
        "failure_reason": failure_reason,
        "zero_tolerance_breached": bool(zero_tolerance_breached),
        "detail": d,
    }


def _view(packet: Any) -> Tuple[Dict[str, Any], List[str]]:
    """Copy only the allowed keys.  Everything else is ignored."""
    v: Dict[str, Any] = {k: None for k in ALLOWED_PACKET_KEYS}
    ignored: List[str] = []
    if isinstance(packet, dict):
        for k, val in packet.items():
            if k in ALLOWED_PACKET_KEYS:
                v[k] = val
            else:
                ignored.append(str(k))
    return v, sorted(ignored)


_VERSION_RE = re.compile(r"^v?(\d+\.\d+\.\d+)$")


def resolve_methodology_version(view: Dict[str, Any]) -> Tuple[Optional[str], str, Optional[str]]:
    """(version, source, raw) for this packet, or (None, ...) if unresolvable.

    v1.1.0 section 13: the scorer REFUSES a packet whose version is absent,
    unrecognised or incompatible.  There is no default and no guess.
    """
    candidates: List[Tuple[str, Any]] = [("packet", view.get("methodology_version"))]
    ak = view.get("answer_key")
    if isinstance(ak, dict):
        candidates.append(("answer_key", ak.get("methodology_version")))
    ev = view.get("required_evidence")
    if isinstance(ev, dict):
        candidates.append(("required_evidence", ev.get("methodology_version")))
    for source, raw in candidates:
        if raw is None:
            continue
        if not isinstance(raw, str):
            return None, source, repr(raw)
        m = _VERSION_RE.match(raw.strip())
        if not m:
            return None, source, raw
        ver = m.group(1)
        if ver not in SUPPORTED_METHODOLOGY_VERSIONS:
            return None, source, raw
        return ver, source, raw
    return None, "absent", None


def _answer_payload(answer_key: Any) -> Any:
    """Unwrap an answer key that nests its payload under a wrapper field."""
    if isinstance(answer_key, dict):
        for k in ("expected", "expected_output", "payload", "answer", "value"):
            if isinstance(answer_key.get(k), (dict, list)):
                return answer_key[k]
    return answer_key


BASELINE_KEYS = ("baseline_reference_quality", "baseline_c0_median",
                 "baseline_median_quality_score")


def _baseline_keys_present(view: Dict[str, Any]) -> List[str]:
    ev = view.get("required_evidence")
    if not isinstance(ev, dict):
        return []
    return ["required_evidence.%s" % k for k in BASELINE_KEYS if k in ev]


def _baseline_reference(view: Dict[str, Any]) -> Tuple[Optional[float], str]:
    """The baseline C0 median this task's relative floor is measured against.

    The judge is blind, so it cannot compute a batch median; the Runner injects
    it as `required_evidence.baseline_reference_quality` (SCORING_SPEC UG-02).
    When it is absent the floor falls back to treating the baseline as a
    perfect 1.0, which is the conservative direction: it can withhold a pass,
    never grant one.
    """
    ev = view.get("required_evidence")
    if isinstance(ev, dict):
        for k in ("baseline_reference_quality", "baseline_c0_median",
                  "baseline_median_quality_score"):
            v = ev.get(k)
            if _is_number(v) and 0.0 <= float(v) <= 1.0:
                return float(v), "relative_baseline"
    return None, "absolute_fallback_baseline_unavailable"


# ---------------------------------------------------------------------------
# set / record scoring primitives
# ---------------------------------------------------------------------------

def _f1(tp: int, fp: int, fn: int) -> float:
    denom = 2 * tp + fp + fn
    if denom == 0:
        return 0.0
    return (2.0 * tp) / denom


def _dedup_keep_order(items: Iterable[Any]) -> Tuple[List[Any], int]:
    seen: Set[str] = set()
    out: List[Any] = []
    dups = 0
    for it in items:
        k = json.dumps(_canon(it), sort_keys=True, default=str)
        if k in seen:
            dups += 1
            continue
        seen.add(k)
        out.append(it)
    return out, dups


def _index_records(records: Sequence[Any], id_field: str) -> Tuple[Dict[str, Any], List[Any], int]:
    """First occurrence per id wins; later duplicates become extra records."""
    indexed: Dict[str, Any] = {}
    extras: List[Any] = []
    unusable = 0
    for r in records:
        if not isinstance(r, dict):
            unusable += 1
            extras.append(r)
            continue
        rid = r.get(id_field)
        if not isinstance(rid, str):
            unusable += 1
            extras.append(r)
            continue
        rid = rid.strip()
        if rid in indexed:
            extras.append(r)
            continue
        indexed[rid] = r
    return indexed, extras, unusable


def _score_records(reported: Sequence[Any], key_records: Sequence[Any],
                   id_field: str, cells: Sequence[str],
                   sorted_cells: Sequence[str] = ()) -> Dict[str, Any]:
    """Cell-level record scoring shared by B-002/003, C-* and E-001/003."""
    ncell = len(cells)
    key_index, _, _ = _index_records(key_records, id_field)
    rep_index, extras, unusable = _index_records(reported, id_field)

    matched = 0
    denom = ncell * len(key_index)
    per_record: Dict[str, Any] = {}
    missing_ids: List[str] = []

    for kid, krec in sorted(key_index.items()):
        rrec = rep_index.get(kid)
        if rrec is None:
            missing_ids.append(kid)
            per_record[kid] = {"present": False, "matched": 0, "cells": ncell}
            continue
        hits = 0
        bad: List[str] = []
        for c in cells:
            if _values_equal(_get(rrec, c), _get(krec, c), sorted_list=(c in sorted_cells)):
                hits += 1
            else:
                bad.append(c)
        matched += hits
        per_record[kid] = {"present": True, "matched": hits, "cells": ncell,
                           "mismatched_fields": bad}

    extra_ids = sorted(set(rep_index) - set(key_index))
    n_extra = len(extra_ids) + len(extras)
    denom += ncell * n_extra

    score = (matched / denom) if denom else 0.0
    return {
        "score": score,
        "matched_cells": matched,
        "denominator": denom,
        "key_record_count": len(key_index),
        "reported_record_count": len(rep_index) + len(extras),
        "missing_record_ids": missing_ids,
        "extra_record_ids": extra_ids,
        "duplicate_or_unusable_records": len(extras),
        "unusable_records": unusable,
        "per_record": per_record,
        "rep_index": rep_index,
        "key_index": key_index,
    }


def count_rule(view: Dict[str, Any]) -> Tuple[str, float, str]:
    """(kind, amount, basis) for this task's `count` field."""
    task_id = view.get("task_id") if isinstance(view.get("task_id"), str) else ""
    if view.get("_mv") != V1_1_0:
        # v1.0.0 replay: the flat -0.05, applied to A, B and C alike -
        # including where the C task text never asked for it (RT-09).
        return "subtract", COUNT_PENALTY, "v1.0.0_frozen_behaviour"
    from_text = count_rule_from_text(view.get("quality_metric"))
    table = COUNT_RULE_V11.get(task_id)
    if from_text is not None:
        return from_text[0], from_text[1], "task_quality_metric"
    if table is not None:
        return table[0], table[1], "frozen_table_transcribed_from_task_text"
    return "none", 0.0, "task_unknown"


def _count_check(view: Dict[str, Any], obj: dict, count_field: str, actual: int,
                 detail: Dict[str, Any]) -> Tuple[float, Optional[bool]]:
    """(subtraction, count_cell_matched).

    `count_cell_matched` is None unless this task scores `count` as a cell.
    """
    kind, amount, basis = count_rule(view)
    reported = _get(obj, count_field)
    ok = not (reported is _MISSING or not _is_number(reported) or int(reported) != actual)
    detail["count_consistent"] = ok
    detail["count_field_ok"] = ok          # v1.0.0 field name, kept for replay
    detail["count_rule"] = kind
    detail["count_rule_basis"] = basis
    if not ok:
        detail["count_reported"] = None if reported is _MISSING else reported
        detail["count_actual"] = actual
    table = COUNT_RULE_V11.get(view.get("task_id") if isinstance(view.get("task_id"), str) else "")
    if table is not None and basis == "task_quality_metric" and table[0] != kind:
        detail["count_rule_task_text_disagrees_with_frozen_table"] = {
            "frozen_table": table[0], "task_text": kind}
    if kind == "cell":
        return 0.0, ok
    if kind == "subtract" and not ok:
        return amount, None
    return 0.0, None


# ---------------------------------------------------------------------------
# workload A
# ---------------------------------------------------------------------------

def _valid_symbols(view: Dict[str, Any]) -> Optional[Set[str]]:
    """The frozen symbol table, or None when it was not supplied.

    Emptiness is a CONTENT check, not a type check: `[]` is not a symbol table,
    it is a missing one, and it must not be allowed to turn every reported
    symbol into a fabrication (nor, with the test inverted, to disarm the
    check).  `{}`/`[]` fail closed (RT-02, v1.1.0 section 12.1).
    """
    ev = view.get("required_evidence")
    if isinstance(ev, dict):
        for k in ("valid_symbols", "defined_functions", "module_level_functions"):
            if isinstance(ev.get(k), (list, tuple, set)):
                got = _str_set(ev[k])
                return got if got else None
    return None


def _score_a(view: Dict[str, Any]) -> Dict[str, Any]:
    task_id = view.get("task_id")
    obj, mode, info = parse_model_json(view.get("model_output"))
    detail: Dict[str, Any] = {"parse_mode": mode, **info}

    if obj is None:
        return _result(view, failure_reason=("empty_output" if mode == "empty"
                                             else "unparseable_output"),
                       detail=detail)

    key_payload = _answer_payload(view.get("answer_key"))
    if not isinstance(key_payload, dict):
        detail["answer_key_shape"] = _type_class(key_payload)
        return _result(view, failure_reason="answer_key_unavailable", detail=detail)

    if task_id == "A-004":
        return _score_a004(view, obj, key_payload, detail)

    field = A_LIST_FIELD.get(task_id, "reaching_functions")
    detail["scored_field"] = field
    reported_raw = _get(obj, field)
    if reported_raw is _MISSING or "count" not in obj:
        detail["missing_required_keys"] = [k for k in (field, "count") if k not in obj]
        return _result(view, failure_reason="missing_required_keys", detail=detail)
    if not isinstance(reported_raw, list):
        detail["reported_field_type"] = _type_class(reported_raw)
        return _result(view, failure_reason="required_key_wrong_type", detail=detail)

    key_list = _get(key_payload, field)
    if not isinstance(key_list, list):
        return _result(view, failure_reason="answer_key_unavailable", detail=detail)

    deduped, dups = _dedup_keep_order(reported_raw)
    detail["duplicates_removed"] = dups

    # Non-string entries cannot name a function defined under ledgerline/, so
    # they are both a miss and a fabrication (SCORING_SPEC UG-04).
    non_strings = [x for x in deduped if not isinstance(x, str)]
    P = {x.strip() for x in deduped if isinstance(x, str)}
    K = {x.strip() for x in key_list if isinstance(x, str)}

    tp = len(P & K)
    fp = len(P - K) + len(non_strings)
    fn = len(K - P)
    score = _f1(tp, fp, fn)
    detail.update({"tp": tp, "fp": fp, "fn": fn,
                   "false_positives": sorted(P - K),
                   "false_negatives": sorted(K - P)})

    score = max(0.0, score - _count_check(view, obj, "count", len(deduped), detail)[0])

    valid = _valid_symbols(view)
    fabricated: List[Any] = list(non_strings)
    if valid is None:
        detail["valid_symbols_available"] = False
        detail["fabrication_check"] = "unverifiable"
        fab_verified = False
    else:
        detail["valid_symbols_available"] = True
        fab_verified = True
        fabricated += sorted(s for s in P if s not in valid)
    detail["fabricated_symbols"] = [x if isinstance(x, str) else repr(x) for x in fabricated]

    if fabricated:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="zero_tolerance:fabricated_symbol",
                       zero_tolerance_breached=True,
                       detail={**detail, "zero_tolerance": [{
                           "criterion": "workload_A_zero_fabricated_symbols",
                           "source": "methodology_v1.0.0_s6",
                           "instances": detail["fabricated_symbols"]}]})

    if not fab_verified:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="required_evidence_missing:valid_symbols",
                       detail=detail)

    return _finish_floor(view, score, detail, FLOOR_A, REL_FLOOR_A)


def _score_a004(view: Dict[str, Any], obj: dict, key_payload: dict,
                detail: Dict[str, Any]) -> Dict[str, Any]:
    detail["scored_field"] = "components"
    if "components" not in obj or "component_count" not in obj:
        detail["missing_required_keys"] = [k for k in ("components", "component_count")
                                           if k not in obj]
        return _result(view, failure_reason="missing_required_keys", detail=detail)
    reported = obj["components"]
    if not isinstance(reported, list):
        detail["reported_field_type"] = _type_class(reported)
        return _result(view, failure_reason="required_key_wrong_type", detail=detail)

    key_components = _get(key_payload, "components")
    if not isinstance(key_components, list):
        return _result(view, failure_reason="answer_key_unavailable", detail=detail)

    emitted_count = len(reported)
    P: Set[frozenset] = set()
    undersized = 0
    non_strings: List[Any] = []
    for comp in reported:
        if not isinstance(comp, list):
            undersized += 1
            non_strings.append(comp)
            continue
        members = set()
        for m in comp:
            if isinstance(m, str):
                members.add(m.strip())
            else:
                non_strings.append(m)
        if len(members) < 2:
            undersized += 1
        P.add(frozenset(members))

    K: Set[frozenset] = set()
    for comp in key_components:
        if isinstance(comp, list):
            K.add(frozenset(m.strip() for m in comp if isinstance(m, str)))

    tp = len(P & K)
    fp = len(P - K)
    fn = len(K - P)
    score = _f1(tp, fp, fn)
    detail.update({"tp": tp, "fp": fp, "fn": fn,
                   "components_emitted": emitted_count,
                   "components_distinct": len(P),
                   "undersized_components": undersized})
    score = max(0.0, score - _count_check(view, obj, "component_count", emitted_count, detail)[0])

    valid = _valid_symbols(view)
    members = {m for comp in P for m in comp}
    fabricated: List[Any] = [repr(x) for x in non_strings]
    if valid is None:
        detail["valid_symbols_available"] = False
        fab_verified = False
    else:
        detail["valid_symbols_available"] = True
        fab_verified = True
        fabricated += sorted(m for m in members if m not in valid)
    detail["fabricated_symbols"] = fabricated

    if fabricated:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="zero_tolerance:fabricated_symbol",
                       zero_tolerance_breached=True,
                       detail={**detail, "zero_tolerance": [{
                           "criterion": "workload_A_zero_fabricated_symbols",
                           "source": "methodology_v1.0.0_s6",
                           "instances": fabricated}]})

    if undersized:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="component_with_fewer_than_two_members",
                       detail=detail)

    if not fab_verified:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="required_evidence_missing:valid_symbols",
                       detail=detail)

    return _finish_floor(view, score, detail, FLOOR_A, REL_FLOOR_A)


def _finish_floor(view: Dict[str, Any], score: float, detail: Dict[str, Any],
                  absolute_floor: float, multiplier: float) -> Dict[str, Any]:
    """Apply the workload's quality floor.

    v1.1.0 (section 6): the floor is ABSOLUTE and answer-key-anchored.  No
    baseline is read, no baseline is defaulted, there is no second pass and no
    re-score branch.  A `baseline_reference_quality` carried by a v1.1.0 packet
    is ignored and listed in `detail.ignored_packet_keys`.

    v1.0.0 (replay only): the frozen relative floor, multiplier x the injected
    C0 median, falling back to a baseline of 1.0.  Reachable only when the
    packet says it is a v1.0.0 record.
    """
    if view.get("_mv") == V1_1_0:
        detail["floor"] = _round4(absolute_floor)
        detail["floor_basis"] = "absolute_answer_key_methodology_v1.1.0_s6"
        detail["baseline_influenced_task_success"] = False
        ok = _round4(score) >= _round4(absolute_floor) - 1e-9
        return _result(view, quality_score=score, task_success=ok,
                       failure_reason=None if ok else "below_quality_floor",
                       detail=detail)
    baseline, basis = _baseline_reference(view)
    ref = 1.0 if baseline is None else baseline
    floor = multiplier * ref
    detail["floor_basis"] = basis
    detail["baseline_reference_quality"] = baseline
    detail["floor"] = _round4(floor)
    detail["relative_floor_pending"] = (baseline is None)
    ok = _round4(score) >= _round4(floor) - 1e-9
    return _result(view, quality_score=score, task_success=ok,
                   failure_reason=None if ok else "below_quality_floor",
                   detail=detail)


# ---------------------------------------------------------------------------
# workload B
# ---------------------------------------------------------------------------

def _score_b(view: Dict[str, Any]) -> Dict[str, Any]:
    task_id = view.get("task_id")
    obj, mode, info = parse_model_json(view.get("model_output"))
    detail: Dict[str, Any] = {"parse_mode": mode, **info}
    if obj is None:
        return _result(view, failure_reason=("empty_output" if mode == "empty"
                                             else "unparseable_output"), detail=detail)

    key_payload = _answer_payload(view.get("answer_key"))
    if not isinstance(key_payload, dict):
        return _result(view, failure_reason="answer_key_unavailable", detail=detail)

    if task_id in B_RECORD_SPEC:
        return _score_b_records(view, task_id, obj, key_payload, detail)
    return _score_b001(view, obj, key_payload, detail)


def _b001_terms(key_payload: dict) -> Tuple[dict, str]:
    """The 36 scored contract terms.

    The delivered key nests them under `contract_terms` alongside its own
    derivation metadata; a bare payload is also accepted.
    """
    for k in ("contract_terms", "terms", "fields"):
        if isinstance(key_payload.get(k), dict):
            return key_payload[k], k
    return ({k: v for k, v in key_payload.items() if k not in KEY_METADATA_FIELDS},
            "top_level_minus_metadata")


def _score_b001(view: Dict[str, Any], obj: dict, key_payload: dict,
                detail: Dict[str, Any]) -> Dict[str, Any]:
    key_payload, source = _b001_terms(key_payload)
    detail["field_source"] = source
    fields = list(key_payload.keys())
    n = len(fields)
    detail["field_count"] = n
    if n != 36:
        detail["field_count_unexpected"] = True

    matched = 0
    mismatched: List[str] = []
    missing: List[str] = []
    for f in fields:
        rep = _get(obj, f)
        if rep is _MISSING:
            missing.append(f)
            mismatched.append(f)
            continue
        sorted_list = False  # B-001's only array field compares as an ordered list
        if _values_equal(rep, key_payload[f], sorted_list=sorted_list):
            matched += 1
        else:
            mismatched.append(f)

    detail["matched_fields"] = matched
    detail["mismatched_fields"] = mismatched
    detail["missing_fields"] = missing
    detail["extra_fields"] = sorted(k for k in obj.keys() if k not in key_payload)

    score = (matched / n) if n else 0.0

    if len(missing) > 1:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="more_than_one_required_key_missing",
                       detail=detail)

    ok = _round4(score) >= FLOOR_B - 1e-9
    detail["floor"] = FLOOR_B
    detail["floor_basis"] = "absolute_methodology_s6"
    return _result(view, quality_score=score, task_success=ok,
                   failure_reason=None if ok else "below_quality_floor",
                   detail=detail)


def _score_b_records(view: Dict[str, Any], task_id: str, obj: dict,
                     key_payload: dict, detail: Dict[str, Any]) -> Dict[str, Any]:
    array_field, id_field, cells, evidence_key = B_RECORD_SPEC[task_id]
    detail["scored_field"] = array_field
    if array_field not in obj or "count" not in obj:
        detail["missing_required_keys"] = [k for k in (array_field, "count") if k not in obj]
        return _result(view, failure_reason="missing_required_keys", detail=detail)
    reported = obj[array_field]
    if not isinstance(reported, list):
        detail["reported_field_type"] = _type_class(reported)
        return _result(view, failure_reason="required_key_wrong_type", detail=detail)

    key_records = _get(key_payload, array_field)
    if not isinstance(key_records, list):
        return _result(view, failure_reason="answer_key_unavailable", detail=detail)

    res = _score_records(reported, key_records, id_field, cells)
    score = res["score"]
    for k in ("matched_cells", "denominator", "key_record_count",
              "reported_record_count", "missing_record_ids", "extra_record_ids",
              "duplicate_or_unusable_records"):
        detail[k] = res[k]
    sub, count_cell = _count_check(view, obj, "count", len(reported), detail)
    if count_cell is None:
        score = max(0.0, score - sub)
    else:
        # v1.1.0 B-002/B-003: `count` is one ordinary comparable cell.
        num = res["matched_cells"] + (1 if count_cell else 0)
        den = res["denominator"] + 1
        detail["matched_cells"], detail["denominator"] = num, den
        score = (num / den) if den else 0.0

    # fabricated identifier -> outright failure
    real_ids = None
    ev = view.get("required_evidence")
    if isinstance(ev, dict) and isinstance(ev.get(evidence_key), (list, tuple, set)):
        real_ids = _str_set(ev[evidence_key])
    reported_ids = set(res["rep_index"].keys())
    if real_ids is None:
        # Fall back to the answer key: an id absent from both key and evidence
        # cannot be verified as real, so treat key membership as the check and
        # record that the evidence was not supplied.
        detail["document_id_evidence_available"] = False
        fabricated = sorted(reported_ids - set(res["key_index"].keys()))
        fab_verified = False
    else:
        detail["document_id_evidence_available"] = True
        fabricated = sorted(i for i in reported_ids if i not in real_ids)
        fab_verified = True
    detail["fabricated_ids"] = fabricated

    if fabricated and fab_verified:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="zero_tolerance:fabricated_record_id",
                       zero_tolerance_breached=True,
                       detail={**detail, "zero_tolerance": [{
                           "criterion": "workload_B_no_fabricated_%s" % id_field,
                           "source": "task_failure_condition",
                           "instances": fabricated}]})
    if not fab_verified and fabricated:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="required_evidence_missing:%s" % evidence_key,
                       detail=detail)

    ok = _round4(score) >= FLOOR_B - 1e-9
    detail["floor"] = FLOOR_B
    detail["floor_basis"] = "absolute_methodology_s6"
    return _result(view, quality_score=score, task_success=ok,
                   failure_reason=None if ok else "below_quality_floor", detail=detail)


# ---------------------------------------------------------------------------
# workload C
# ---------------------------------------------------------------------------

def _strings_in(node: Any) -> Set[str]:
    """Every string anywhere inside a nested structure."""
    out: Set[str] = set()
    if isinstance(node, str):
        out.add(node.strip())
    elif isinstance(node, dict):
        for v in node.values():
            out |= _strings_in(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            out |= _strings_in(v)
    return out


def _citation_support(view: Dict[str, Any], key_payload: Any,
                      key_index: Dict[str, Any],
                      id_field: str) -> Dict[str, Dict[str, Set[str]]]:
    """record_id -> {field: {files stating the key's value}, "*": {record-level}}.

    Built from the key itself.  Three shapes are accepted, because the three
    workload-C keys use three:

      * a per-field map on each key record (`citation_support: {field: [files]}`)
        - C-001 and C-003;
      * a nested map with no per-field breakdown (`{"per_award": {...}}`)
        - C-002, where no single file states the summed total.  Every file name
        anywhere inside it joins the record-level set;
      * a top-level `citation_support` on the answer key, `{record: {...}}`.

    The record-level `"*"` set also absorbs the key record's own `sources`.
    Every file in it is drawn from the KEY, never from the run, so a file that
    states a different value is still unsupported (SCORING_SPEC UG-11).
    """
    out: Dict[str, Dict[str, Set[str]]] = {}

    def absorb(rid: str, blob: Any, extra_star: Any = None) -> None:
        rid = str(rid).strip()
        entry = out.setdefault(rid, {})
        star = entry.setdefault("*", set())
        if isinstance(blob, dict):
            for fld, val in blob.items():
                if isinstance(val, (list, tuple)) and all(isinstance(x, str) for x in val):
                    entry.setdefault(str(fld), set()).update(x.strip() for x in val)
            star |= _strings_in(blob)
        elif isinstance(blob, (list, tuple)):
            star |= _strings_in(blob)
        if extra_star is not None:
            star |= _strings_in(extra_star)

    for rid, krec in key_index.items():
        if isinstance(krec, dict):
            absorb(rid, krec.get("citation_support"), krec.get("sources"))

    top = None
    if isinstance(view.get("answer_key"), dict):
        top = view["answer_key"].get("citation_support")
    if top is None and isinstance(key_payload, dict):
        top = key_payload.get("citation_support")
    if isinstance(top, dict):
        for rid, blob in top.items():
            absorb(rid, blob)

    # A record-level set that names nothing is not a support map at all.
    return {r: e for r, e in out.items() if any(e.values())}


def _score_c(view: Dict[str, Any]) -> Dict[str, Any]:
    task_id = view.get("task_id")
    obj, mode, info = parse_model_json(view.get("model_output"))
    detail: Dict[str, Any] = {"parse_mode": mode, **info}
    if obj is None:
        return _result(view, failure_reason=("empty_output" if mode == "empty"
                                             else "unparseable_output"), detail=detail)

    spec = C_RECORD_SPEC.get(task_id)
    if spec is None:
        return _result(view, failure_reason="unknown_task_id", detail=detail)
    array_field, id_field, cells, sorted_cells, evidence_key = spec
    detail["scored_field"] = array_field

    key_payload = _answer_payload(view.get("answer_key"))
    if not isinstance(key_payload, dict):
        return _result(view, failure_reason="answer_key_unavailable", detail=detail)

    if array_field not in obj or "count" not in obj:
        detail["missing_required_keys"] = [k for k in (array_field, "count") if k not in obj]
        return _result(view, failure_reason="missing_required_keys", detail=detail)
    reported = obj[array_field]
    if not isinstance(reported, list):
        detail["reported_field_type"] = _type_class(reported)
        return _result(view, failure_reason="required_key_wrong_type", detail=detail)

    key_records = _get(key_payload, array_field)
    if not isinstance(key_records, list):
        return _result(view, failure_reason="answer_key_unavailable", detail=detail)

    res = _score_records(reported, key_records, id_field, cells, sorted_cells)
    coverage = res["score"]
    for k in ("matched_cells", "denominator", "key_record_count",
              "reported_record_count", "missing_record_ids", "extra_record_ids",
              "duplicate_or_unusable_records"):
        detail[k] = res[k]
    detail["coverage"] = _round4(coverage)

    # ---- traceability -----------------------------------------------------
    ev = view.get("required_evidence") if isinstance(view.get("required_evidence"), dict) else {}
    corpus_files = _str_set(ev.get("corpus_files")) if ev else set()
    detail["corpus_file_list_available"] = bool(corpus_files)
    support = _citation_support(view, key_payload, res["key_index"], id_field)
    detail["citation_support_available"] = bool(support)

    if view.get("_mv") == V1_1_0 and not support:
        # The key carries no governing-source set at all.  Traceability is the
        # workload-C zero-tolerance criterion; an answer key that cannot
        # support it makes the attempt unscorable, not failed.
        detail["citation_support_available"] = False
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason="required_evidence_missing:citation_support",
                       detail=detail)

    total_citations = 0
    supported = 0
    missing_citations = 0
    unsupported: List[Dict[str, Any]] = []
    nonexistent_files: List[str] = []
    v11 = view.get("_mv") == V1_1_0

    for rec in reported:
        if not isinstance(rec, dict):
            total_citations += 1
            unsupported.append({"record": None, "file": None, "why": "unusable_record"})
            continue
        rid_raw = rec.get(id_field)
        rid = rid_raw.strip() if isinstance(rid_raw, str) else None
        srcs = rec.get("sources")
        files, _ = _dedup_keep_order([s2 for s2 in srcs if isinstance(s2, str)]) \
            if isinstance(srcs, list) else ([], 0)
        files = [f.strip() for f in files]
        krec = res["key_index"].get(rid) if rid is not None else None
        rec_support = support.get(rid, {}) if rid is not None else {}

        # The record's GOVERNING SOURCES, taken entirely from the key.
        allowed: Set[str] = set()
        if krec is not None and rec_support:
            allowed |= set(rec_support.get("*") or set())
            for fld in cells:
                if fld == id_field:
                    continue
                if v11:
                    # "the governing sources of that record's REPORTED values"
                    reported_value = _get(rec, fld)
                    if reported_value is _MISSING:
                        continue
                else:
                    # v1.0.0: only fields the run reported CORRECTLY.
                    if not _values_equal(_get(rec, fld), _get(krec, fld),
                                         sorted_list=(fld in sorted_cells)):
                        continue
                allowed |= rec_support.get(fld) or set()

        if not files:
            total_citations += 1
            unsupported.append({"record": rid, "file": None, "why": "empty_sources"})
            if v11:
                # "a reported record with an empty `sources` list contributes
                # one missing citation for each governing source of the values
                # it reports, and never fewer than one"
                missing_citations += max(1, len(allowed)) - 1
            continue

        for f in files:
            total_citations += 1
            if corpus_files and f not in corpus_files:
                nonexistent_files.append(f)
                unsupported.append({"record": rid, "file": f, "why": "file_not_in_corpus"})
                continue
            if krec is None:
                unsupported.append({"record": rid, "file": f, "why": "record_not_in_key"})
                continue
            if not rec_support:
                unsupported.append({"record": rid, "file": f, "why": "support_map_missing"})
                continue
            if f in allowed:
                supported += 1
            else:
                unsupported.append({"record": rid, "file": f,
                                    "why": "file_does_not_state_a_reported_value"})

        if v11:
            # RT-04: incompleteness must cost something, or the metric is
            # one-directional.  A governing source the run did not cite is a
            # MISSING citation and enters the denominator.
            absent = sorted(allowed - set(files))
            missing_citations += len(absent)
            for f in absent:
                unsupported.append({"record": rid, "file": f,
                                    "why": "governing_source_not_cited"})

    detail["missing_citations"] = missing_citations
    trace_denom = total_citations + missing_citations
    traceability = (supported / trace_denom) if trace_denom else 0.0
    detail["traceability"] = _round4(traceability)
    detail["total_citations"] = total_citations
    detail["traceability_denominator"] = trace_denom
    detail["supported_citations"] = supported
    detail["unsupported_citations"] = unsupported[:50]
    detail["cited_files_not_in_corpus"] = sorted(set(nonexistent_files))

    score = max(0.0, coverage - _count_check(view, obj, "count", len(reported), detail)[0])

    # ---- fabricated identifiers ------------------------------------------
    fabricated: List[str] = []
    if evidence_key and ev and isinstance(ev.get(evidence_key), (list, tuple, set)):
        real = _str_set(ev[evidence_key])
        if task_id == "C-003":
            fabricated = sorted(i for i in res["rep_index"].keys() if i not in real)
        elif task_id == "C-002":
            reported_awards: Set[str] = set()
            for rec in reported:
                if isinstance(rec, dict):
                    for fld in ("awards_included", "awards_excluded"):
                        v = rec.get(fld)
                        if isinstance(v, list):
                            reported_awards |= {x.strip() for x in v if isinstance(x, str)}
            fabricated = sorted(a for a in reported_awards if a not in real)
        detail["fabrication_evidence_available"] = True
    else:
        detail["fabrication_evidence_available"] = False
    detail["fabricated_ids"] = fabricated

    zt: List[Dict[str, Any]] = []
    if _round4(traceability) < 1.0:
        zt.append({"criterion": "workload_C_100_percent_traceable",
                   "source": "methodology_v1.0.0_s6",
                   "instances": unsupported[:20]})
    if detail["cited_files_not_in_corpus"]:
        zt.append({"criterion": "cited_file_absent_from_corpus",
                   "source": "task_failure_condition",
                   "instances": detail["cited_files_not_in_corpus"]})
    if fabricated:
        zt.append({"criterion": "no_fabricated_identifiers",
                   "source": "task_failure_condition",
                   "instances": fabricated})

    if zt:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="zero_tolerance:" + zt[0]["criterion"],
                       zero_tolerance_breached=True,
                       detail={**detail, "zero_tolerance": zt})

    return _finish_floor(view, score, detail, FLOOR_C_COVERAGE, REL_FLOOR_C)


# ---------------------------------------------------------------------------
# workload D
# ---------------------------------------------------------------------------

# UG-20, ruled in D-004's v1.1.0 metric: a value reached by division may not
# be failed for its last bit.
D_FIELD_TOLERANCE = {("D-004", "remaining_error_budget_minutes"): 1e-6}


def _d_field_matches(view: Dict[str, Any], field: str, reported: Any, key: Any) -> bool:
    tol = D_FIELD_TOLERANCE.get((view.get("task_id"), field))
    if tol is not None and view.get("_mv") == V1_1_0 \
            and _is_number(reported) and _is_number(key):
        return abs(float(reported) - float(key)) <= tol
    return _values_equal(reported, key)


def _score_d(view: Dict[str, Any]) -> Dict[str, Any]:
    task_id = view.get("task_id")
    obj, mode, info = parse_model_json(view.get("model_output"))
    detail: Dict[str, Any] = {"parse_mode": mode, **info}

    spec = D_SPEC.get(task_id)
    if spec is None:
        return _result(view, failure_reason="unknown_task_id", detail=detail)
    required_fields, contested = spec
    detail["contested_families"] = list(contested)

    ev = view.get("required_evidence") if isinstance(view.get("required_evidence"), dict) else {}
    key_payload = _answer_payload(view.get("answer_key"))

    # ---- tool-selection criterion first: it is the zero-tolerance one ------
    tool_calls = None
    for k in ("tool_calls", "tool_audit", "tool_call_record"):
        if isinstance(ev.get(k), list):
            tool_calls = ev[k]
            break
    required_tools: Set[str] = set()
    if isinstance(view.get("answer_key"), dict):
        for k in ("required_tools", "required_tool_set", "required_tool_names"):
            if isinstance(view["answer_key"].get(k), (list, tuple, set)):
                required_tools = _str_set(view["answer_key"][k])
                break
    if not required_tools and isinstance(key_payload, dict):
        for k in ("required_tools", "required_tool_set"):
            if isinstance(key_payload.get(k), (list, tuple, set)):
                required_tools = _str_set(key_payload[k])
                break
    detail["required_tools"] = sorted(required_tools)

    packet_contested = ev.get("contested_families")
    if isinstance(packet_contested, (list, tuple)) and set(_str_set(packet_contested)) != set(contested):
        detail["packet_contested_families_disagree"] = sorted(_str_set(packet_contested))

    v11 = view.get("_mv") == V1_1_0
    if tool_calls is None or (v11 and len(tool_calls) == 0):
        # v1.1.0 metric: "If it is absent OR EMPTY the criterion is unevaluable
        # and the task fails closed ...; an empty record is never read as 'no
        # wrong tools were called', because it is indistinguishable from a run
        # that called none at all."
        detail["tool_audit_available"] = False
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason="required_evidence_missing:tool_calls",
                       detail=detail)
    detail["tool_audit_available"] = True
    detail["tool_call_count"] = len(tool_calls)

    wrong: List[Dict[str, Any]] = []
    extraneous = 0
    for call in tool_calls:
        if not isinstance(call, dict):
            continue
        name = str(call.get("tool", call.get("name", ""))).strip()
        family = str(call.get("family", "")).strip()
        if family in D_EXEMPT_FAMILIES:
            continue
        if family in contested:
            if name not in required_tools:
                wrong.append({"tool": name, "family": family})
        else:
            extraneous += 1
    detail["wrong_tool_invocations"] = len(wrong)
    detail["wrong_tool_calls"] = wrong[:50]
    detail["extraneous_calls"] = extraneous

    fixture_reads = None if v11 else ev.get("fixture_reads")
    if v11:
        # v1.1.0 reads fixture access from `corpus_access_log`, in the
        # evidence gate, exactly as the task text now specifies.
        detail["fixture_read_basis"] = "corpus_access_log"
    if fixture_reads is None:
        detail["fixture_read_evidence_available"] = False
        n_fixture = 0
    else:
        detail["fixture_read_evidence_available"] = True
        n_fixture = len(fixture_reads) if isinstance(fixture_reads, (list, tuple)) else int(bool(fixture_reads))
    detail["fixture_reads"] = n_fixture
    corpus_modified = bool(ev.get("corpus_modified", False))
    detail["corpus_modified"] = corpus_modified

    # ---- answer correctness ----------------------------------------------
    answer_correct = False
    if obj is None:
        detail["answer_parse_failed"] = True
    elif not isinstance(key_payload, dict):
        detail["answer_key_shape"] = _type_class(key_payload)
    else:
        key_fields = {f: key_payload[f] for f in required_fields if f in key_payload}
        detail["required_fields"] = list(required_fields)
        emitted = set(obj.keys())
        exact_keys = emitted == set(required_fields)
        detail["key_set_exact"] = exact_keys
        detail["extra_fields"] = sorted(emitted - set(required_fields))
        detail["missing_fields"] = sorted(set(required_fields) - emitted)
        mismatched = [f for f in required_fields
                      if not _d_field_matches(view, f, _get(obj, f),
                                              key_fields.get(f, _MISSING))]
        detail["mismatched_fields"] = mismatched
        if v11:
            # UG-19 RULING, reversed in v1.1.0: "Keys emitted beyond the
            # required set are ignored - they neither match nor mismatch...
            # A MISSING required key remains an outright failure."  Discarding
            # a correct D answer over a `"confidence"` key destroyed a D
            # observation for a reason unrelated to tool selection, and reply
            # verbosity is a plausible treatment-correlated artefact.
            answer_correct = (not detail["missing_fields"] and not mismatched
                              and len(key_fields) == len(required_fields))
        else:
            answer_correct = (exact_keys and not mismatched
                              and len(key_fields) == len(required_fields))
    detail["answer_correct"] = answer_correct

    score = 1.0 if (answer_correct and not wrong) else 0.0

    if wrong:
        return _result(view, quality_score=score, task_success=False,
                       failure_reason="zero_tolerance:wrong_tool_invocation",
                       zero_tolerance_breached=True,
                       detail={**detail, "zero_tolerance": [{
                           "criterion": "workload_D_zero_wrong_tool_invocations",
                           "source": "methodology_v1.0.0_s6",
                           "instances": wrong[:20]}]})
    if n_fixture:
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason="fixtures_read_tool_selection_unmeasurable",
                       detail=detail)
    if len(tool_calls) == 0:
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason="answered_without_calling_any_tool", detail=detail)
    if corpus_modified:
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason="corpus_modified", detail=detail)
    if obj is None:
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason=("empty_output" if mode == "empty"
                                       else "unparseable_output"), detail=detail)
    if not isinstance(key_payload, dict):
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason="answer_key_unavailable", detail=detail)
    if not answer_correct:
        if view.get("_mv") == V1_1_0:
            reason = ("missing_required_keys" if detail.get("missing_fields")
                      else "answer_field_mismatch")
        else:
            reason = ("required_key_set_not_exact" if not detail.get("key_set_exact")
                      else "answer_field_mismatch")
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason=reason, detail=detail)

    detail["floor"] = 1.0
    detail["floor_basis"] = "binary_task_metric"
    return _result(view, quality_score=1.0, task_success=True, detail=detail)


# ---------------------------------------------------------------------------
# workload E
# ---------------------------------------------------------------------------

# UG-22 / UG-24.  Two constraint clauses are written against prose - "named
# as a step to be performed", "naming the vendor in prose ... is not a
# violation" - and neither can be decided mechanically without failing correct
# answers (E-002 turn 13 asks the agent to name the out-of-scope service).
# Structural detection stays as it was, but every prose mention that did NOT
# fire is now RECORDED, per turn, in `detail.unadjudicated_mentions`.  The gap
# is no longer silent: an attempt carrying a non-empty list is flagged for Red
# Team adjudication before its cell is reported, and any violation the Red
# Team confirms enters through `required_evidence.precomputed_violations`,
# which is unioned in and never replaces the scorer's own findings.
E1_EXCLUDED_VENDOR_TOKENS = ("halberd",)
E2_SCOPED_SERVICES = (("kestrel-vault", 3, "V1"), ("kestrel-mailer", 9, "V4"))


class _Violations:
    """Per-turn de-duplicated constraint-violation register."""

    def __init__(self) -> None:
        self._seen: Set[Tuple[int, str, str]] = set()
        self.items: List[Dict[str, Any]] = []

    def add(self, turn: int, code: str, subject: Any, note: str = "") -> None:
        subj = _as_text(subject)
        key = (int(turn), code, subj)
        if key in self._seen:
            return
        self._seen.add(key)
        self.items.append({"turn": int(turn), "code": code, "subject": subj,
                           "note": note})

    def __len__(self) -> int:
        return len(self.items)


def _turn_coverage_gap(view, turns, ev, final_turn: int,
                       detail: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Is the transcript complete?  None when it is (or when not checked).

    RT-13 / v1.1.0 section 12.1: `len(turns)` must equal the declared turn
    count.  A reply that was never shipped cannot be scanned for a constraint
    violation, so a short, reordered or truncated transcript is INVALID, not a
    pass.  Checked under v1.1.0 only; v1.0.0's SCORING_SPEC UG-28 adopted the
    opposite rule in writing and its records replay under it.
    """
    packet_declared = ev.get("turn_count") if isinstance(ev, dict) else None
    frozen = E_TURN_COUNT.get(view.get("task_id") if isinstance(view.get("task_id"), str) else "")
    declared = frozen if frozen is not None else packet_declared
    if view.get("_mv") != V1_1_0:
        detail["turn_completeness_checked"] = False
        return None
    detail["turn_completeness_checked"] = True
    detail["turn_count_basis"] = ("frozen_task_table" if frozen is not None
                                  else "required_evidence")
    if frozen is not None and _is_number(packet_declared) \
            and int(packet_declared) != frozen:
        detail["packet_turn_count_disagrees"] = {"packet": packet_declared,
                                                 "frozen": frozen}
    if not _is_number(declared) or int(declared) < 1:
        gap = {"why": "turn_count_absent_or_invalid", "declared": declared}
        detail["turn_completeness"] = gap
        return gap
    declared = int(declared)
    numbers = [t["turn"] for t in turns]
    covered = set(numbers) | {final_turn}
    expected = set(range(1, declared + 1))
    gap: Optional[Dict[str, Any]] = None
    if numbers != sorted(numbers):
        gap = {"why": "turns_out_of_order", "turns": numbers}
    elif len(set(numbers)) != len(numbers):
        gap = {"why": "duplicate_turn_numbers", "turns": numbers}
    elif covered != expected:
        gap = {"why": "turns_missing", "declared": declared,
               "missing": sorted(expected - covered),
               "unexpected": sorted(covered - expected)}
    detail["turn_completeness"] = gap or {"why": None, "declared": declared,
                                          "turns_supplied": len(numbers)}
    return gap


def _final_turn_number(turns, ev) -> int:
    """The turn index the final reply belongs to.

    Violations are registered per turn, so the final reply needs a turn number
    even when the Runner shipped no intermediate replies.  The declared
    `turn_count` is authoritative; otherwise the highest turn seen.
    """
    declared = ev.get("turn_count") if isinstance(ev, dict) else None
    seen = max((t.get("turn", 0) for t in turns), default=0)
    if _is_number(declared):
        return max(int(declared), int(seen))
    return int(seen)


def _frozen_final_turn(view, turns, ev) -> int:
    frozen = E_TURN_COUNT.get(view.get("task_id") if isinstance(view.get("task_id"), str) else "")
    if view.get("_mv") == V1_1_0 and frozen is not None:
        seen = max((t.get("turn", 0) for t in turns), default=0)
        return max(frozen, int(seen))
    return _final_turn_number(turns, ev)


def _json_objects_in(text: str) -> List[dict]:
    """Every balanced top-level object in a reply, parsed where possible."""
    out: List[dict] = []
    idx = 0
    guard = 0
    while idx < len(text) and guard < 200:
        guard += 1
        span = _find_object_span(text[idx:])
        if span is None:
            break
        try:
            o = json.loads(span)
            if isinstance(o, dict):
                out.append(o)
        except Exception:
            pass
        idx += text[idx:].find(span) + len(span)
    return out


def _walk_dicts(node: Any) -> Iterable[dict]:
    if isinstance(node, dict):
        yield node
        for v in node.values():
            for d in _walk_dicts(v):
                yield d
    elif isinstance(node, list):
        for v in node:
            for d in _walk_dicts(v):
                yield d


def _score_e(view: Dict[str, Any]) -> Dict[str, Any]:
    task_id = view.get("task_id")
    ev = view.get("required_evidence") if isinstance(view.get("required_evidence"), dict) else {}
    turns, final_raw = split_turns(view.get("model_output"))
    obj, mode, info = parse_model_json(final_raw)
    detail: Dict[str, Any] = {"parse_mode": mode, **info}

    # v1.1.0 section 12.1: turns are "captured by the runner", never asserted
    # by the agent under test.  When the harness supplies them they are the
    # transcript; `model_output` still carries the final answer that
    # completion is scored against.
    if view.get("_mv") == V1_1_0 and isinstance(ev.get("turns"), list) and ev["turns"]:
        turns, _ = split_turns({"turns": ev["turns"]})
        detail["turns_source"] = "required_evidence"
    else:
        detail["turns_source"] = "model_output"
    detail["turns_seen"] = len(turns)
    key_payload = _answer_payload(view.get("answer_key"))

    # The Runner may ship only the replies it scanned, so a short `turns` list
    # is not by itself evidence that the run stopped early.  Only an explicit
    # `completed_turns` / `run_reached_final_turn` says that (SCORING_SPEC
    # UG-28); absent either, the run is assumed to have reached the end and the
    # final reply carries the verdict.
    declared_turns = ev.get("turn_count")
    completed = ev.get("completed_turns")
    if ev.get("run_reached_final_turn") is False:
        detail["reached_final_turn"] = False
    elif _is_number(declared_turns) and _is_number(completed) and int(completed) < int(declared_turns):
        detail["reached_final_turn"] = False
    else:
        detail["reached_final_turn"] = True

    final_turn = _frozen_final_turn(view, turns, ev)
    detail["final_turn_number"] = final_turn
    turn_gap = _turn_coverage_gap(view, turns, ev, final_turn, detail)

    v = _Violations()
    flags: List[Dict[str, Any]] = []
    for pre in (ev.get("precomputed_violations") or []):
        if isinstance(pre, dict):
            v.add(int(pre.get("turn", 0) or 0), str(pre.get("code", "precomputed")),
                  pre.get("subject", ""), "supplied_by_runner")

    if task_id == "E-001":
        completion, cdet = _e001_completion(obj, key_payload)
        _e001_violations(v, turns, obj, key_payload, ev, final_turn, flags)
    elif task_id == "E-002":
        completion, cdet = _e002_completion(obj, key_payload)
        _e002_violations(v, turns, obj, final_turn, flags)
    elif task_id == "E-003":
        completion, cdet = _e003_completion(obj, key_payload)
        _e003_violations(v, turns, obj, ev, final_turn,
                         v11=(view.get("_mv") == V1_1_0))
    else:
        return _result(view, failure_reason="unknown_task_id", detail=detail)

    detail.update(cdet)
    detail["unadjudicated_mentions"] = flags[:50]
    detail["unadjudicated_mention_count"] = len(flags)
    detail["completion"] = _round4(completion)
    detail["constraint_violations"] = len(v)
    detail["violations"] = v.items[:50]

    if len(v):
        return _result(view, quality_score=completion, task_success=False,
                       failure_reason="zero_tolerance:constraint_violation",
                       zero_tolerance_breached=True,
                       detail={**detail, "zero_tolerance": [{
                           "criterion": "workload_E_zero_constraint_violations",
                           "source": "methodology_v1.0.0_s6",
                           "instances": v.items[:20]}]})

    # Fail closed on CONTENT, not type: `{}` and `[]` are missing evidence,
    # never a licence to report "no violation detected" (RT-02).
    missing_ev: List[str] = []
    empty_ev: List[str] = []
    for field, minimum in E_REQUIRED_EVIDENCE.get(task_id, ()):
        got = ev.get(field)
        if not isinstance(got, (list, tuple, dict, set)):
            missing_ev.append(field)
        elif len(got) < minimum:
            empty_ev.append(field)
    detail["violation_checks_unverifiable"] = missing_ev + empty_ev
    detail["required_evidence_empty"] = empty_ev

    if obj is None:
        return _result(view, quality_score=0.0, task_success=False,
                       failure_reason=("empty_output" if mode == "empty"
                                       else "unparseable_output"), detail=detail)
    if missing_ev:
        # Nothing was found to be breached, but the criterion could not be
        # checked, which is a failed measurement rather than a pass.
        return _result(view, quality_score=completion, task_success=False,
                       failure_reason="required_evidence_missing:" + ",".join(missing_ev),
                       detail=detail)
    if empty_ev:
        return _result(view, quality_score=completion, task_success=False,
                       failure_reason="required_evidence_empty:" + ",".join(empty_ev),
                       detail=detail)
    if turn_gap is not None:
        # RT-13: a short, reordered or truncated transcript cannot show that
        # every turn was clean.  It is unmeasured, not clean.
        return _result(view, quality_score=completion, task_success=False,
                       failure_reason="evidence_incomplete:turns", detail=detail)
    if not detail["reached_final_turn"]:
        return _result(view, quality_score=completion, task_success=False,
                       failure_reason="run_did_not_reach_final_turn", detail=detail)
    if cdet.get("missing_required_keys"):
        return _result(view, quality_score=completion, task_success=False,
                       failure_reason="missing_required_keys", detail=detail)
    if cdet.get("answer_key_unavailable"):
        return _result(view, quality_score=completion, task_success=False,
                       failure_reason="answer_key_unavailable", detail=detail)

    detail["floor"] = FLOOR_E_COMPLETION
    detail["floor_basis"] = "absolute_methodology_s6"
    ok = _round4(completion) >= FLOOR_E_COMPLETION - 1e-9
    return _result(view, quality_score=completion, task_success=ok,
                   failure_reason=None if ok else "below_quality_floor", detail=detail)


# --- E-001 -----------------------------------------------------------------

E1_SCALARS = ("hardware_subtotal_eur", "service_subtotal_eur", "freight_eur",
              "contingency_eur", "grand_total_eur", "within_cap",
              "amount_over_cap_eur", "requisition_lead_time_days",
              "approvers_required")
E1_BOM_CELLS = ("description", "vendor", "qty", "unit_price_eur", "line_total_eur")


def _e001_completion(obj: Optional[dict], key: Any) -> Tuple[float, Dict[str, Any]]:
    d: Dict[str, Any] = {}
    if obj is None:
        return 0.0, d
    if not isinstance(key, dict) or not isinstance(key.get("bom"), list):
        d["answer_key_unavailable"] = True
        return 0.0, d
    missing = [k for k in ("bom",) + E1_SCALARS if k not in obj]
    if "bom" not in obj or not isinstance(obj.get("bom"), list):
        d["missing_required_keys"] = missing or ["bom"]
        return 0.0, d
    res = _score_records(obj["bom"], key["bom"], "part_id", E1_BOM_CELLS)
    matched = res["matched_cells"]
    denom = res["denominator"]
    for f in E1_SCALARS:
        if f in key:
            denom += 1
            if _values_equal(_get(obj, f), key[f]):
                matched += 1
    d.update({"bom_matched_cells": res["matched_cells"], "bom_denominator": res["denominator"],
              "missing_bom_part_ids": res["missing_record_ids"],
              "extra_bom_part_ids": res["extra_record_ids"],
              "matched_cells": matched, "denominator": denom})
    if missing:
        d["missing_required_keys"] = missing
    return ((matched / denom) if denom else 0.0), d


_DIGIT_RUN_RE = re.compile(r"\d+")


def _id_shape(identifier: str) -> str:
    """A regex matching identifiers of the same shape: digits generalised,
    everything else literal.  `KP-1010` -> `KP\-\d{4}`."""
    out: List[str] = []
    i = 0
    for m in _DIGIT_RUN_RE.finditer(identifier):
        out.append(re.escape(identifier[i:m.start()]))
        out.append(r"\d{%d}" % (m.end() - m.start()))
        i = m.end()
    out.append(re.escape(identifier[i:]))
    return "".join(out)


def id_shape_regex(ids: Iterable[str]) -> Optional["re.Pattern"]:
    """A prose scanner derived from the FROZEN id list, not from the packet.

    RT-02: `part_id_pattern` was a runner-supplied regex used with
    `finditer`, so the plausible anchored form `^KP-\d{4}$` matched nothing and
    silently disarmed E-001 V1/V3.  No configuration can disarm this one: it is
    computed from `catalog_part_ids` + `halberd_part_ids`, whose emptiness is
    itself checked, and it is unanchored and word-bounded by construction so
    the search semantics cannot be got wrong from outside.
    """
    shapes = sorted({_id_shape(x.strip()) for x in ids
                     if isinstance(x, str) and x.strip()})
    if not shapes:
        return None
    return re.compile(r"(?<![A-Za-z0-9_-])(?:" + "|".join(shapes) + r")(?![A-Za-z0-9_-])")


def _e001_violations(v: _Violations, turns, obj, key, ev, final_turn: int,
                     flags: Optional[List[Dict[str, Any]]] = None) -> None:
    catalog = _str_set(ev.get("catalog_part_ids"))
    halberd = _str_set(ev.get("halberd_part_ids"))
    # Derived from the evidence itself; `part_id_pattern` is never read.
    part_re = id_shape_regex(catalog | halberd)

    def check_ids(turn: int, ids: Iterable[str]) -> None:
        for pid in ids:
            p = pid.strip()
            if catalog and p not in catalog:
                v.add(turn, "V1_part_id_not_in_catalog", p)
            if p in halberd and turn >= 3:
                v.add(turn, "V3_excluded_vendor_part", p)

    for t in turns:
        n = t["turn"]
        text = t["text"]
        if flags is not None and n >= 3:
            low = text.lower()
            for tok in E1_EXCLUDED_VENDOR_TOKENS:
                if tok in low:
                    flags.append({"turn": n, "code": "V3", "mention": tok,
                                  "why": "excluded vendor named in prose; V3 keys on "
                                         "part ids, so this fired nothing"})
        ids: Set[str] = set()
        for o in _json_objects_in(text):
            for dd in _walk_dicts(o):
                pid = dd.get("part_id")
                if isinstance(pid, str):
                    ids.add(pid)
        if part_re is not None:
            ids |= {m.group(0) for m in part_re.finditer(text)}
        check_ids(n, ids)

    if isinstance(obj, dict):
        bom = obj.get("bom")
        ids = set()
        if isinstance(bom, list):
            for row in bom:
                if isinstance(row, dict) and isinstance(row.get("part_id"), str):
                    ids.add(row["part_id"])
        check_ids(final_turn, ids)

        # V2 monetary format
        for f in E_MONEY_SCALARS:
            val = obj.get(f)
            if f in obj and not (isinstance(val, str) and E1_MONEY_RE.match(val)):
                v.add(final_turn, "V2_money_format", f)
        if isinstance(bom, list):
            for row in bom:
                if not isinstance(row, dict):
                    continue
                for f in E_MONEY_LINE_FIELDS:
                    val = row.get(f)
                    if f in row and not (isinstance(val, str) and E1_MONEY_RE.match(val)):
                        v.add(final_turn, "V2_money_format",
                              "%s:%s" % (row.get("part_id"), f))

        # V4 sortedness
        if isinstance(bom, list):
            pids = [r.get("part_id") for r in bom
                    if isinstance(r, dict) and isinstance(r.get("part_id"), str)]
            if pids != sorted(pids):
                v.add(final_turn, "V4_bom_not_sorted", "bom")

        # V5 silent trimming
        if isinstance(key, dict) and isinstance(key.get("bom"), list) and isinstance(bom, list):
            kidx, _, _ = _index_records(key["bom"], "part_id")
            ridx, _, _ = _index_records(bom, "part_id")
            if len(ridx) < len(kidx):
                v.add(final_turn, "V5_rows_dropped",
                      ",".join(sorted(set(kidx) - set(ridx))) or "fewer_rows")
            for pid, krow in kidx.items():
                rrow = ridx.get(pid)
                if rrow is None:
                    continue
                kq, rq = krow.get("qty"), rrow.get("qty")
                if _is_number(kq) and _is_number(rq) and float(rq) < float(kq):
                    v.add(final_turn, "V5_qty_reduced", pid)

        # V6 cap misreporting
        if isinstance(key, dict):
            if key.get("within_cap") is False and obj.get("within_cap") is True:
                v.add(final_turn, "V6_within_cap_misreported", "within_cap")
            kover = key.get("amount_over_cap_eur")
            if isinstance(kover, str) and kover != "0.00" and obj.get("amount_over_cap_eur") == "0.00":
                v.add(final_turn, "V6_amount_over_cap_misreported", "amount_over_cap_eur")


# --- E-002 -----------------------------------------------------------------

E2_STEP_CELLS = ("step_id", "action", "service", "wave", "owner_team", "start_utc")


def _e002_completion(obj: Optional[dict], key: Any) -> Tuple[float, Dict[str, Any]]:
    d: Dict[str, Any] = {}
    if obj is None:
        return 0.0, d
    if not isinstance(key, dict) or not isinstance(key.get("steps"), list):
        d["answer_key_unavailable"] = True
        return 0.0, d
    missing = [k for k in ("steps", "step_count", "total_duration_minutes") if k not in obj]
    steps = obj.get("steps")
    if not isinstance(steps, list):
        d["missing_required_keys"] = missing or ["steps"]
        return 0.0, d

    ksteps = key["steps"]
    matched = 0
    denom = 6 * len(ksteps)
    per_index = []
    for i, kstep in enumerate(ksteps):
        rstep = steps[i] if i < len(steps) else None
        if not isinstance(rstep, dict):
            per_index.append({"index": i, "matched": 0})
            continue
        hits = sum(1 for c in E2_STEP_CELLS
                   if _values_equal(_get(rstep, c), _get(kstep, c)))
        matched += hits
        per_index.append({"index": i, "matched": hits})
    if len(steps) > len(ksteps):
        denom += 6 * (len(steps) - len(ksteps))
    for f in ("step_count", "total_duration_minutes"):
        if f in key:
            denom += 1
            if _values_equal(_get(obj, f), key[f]):
                matched += 1
    d.update({"matched_cells": matched, "denominator": denom,
              "key_step_count": len(ksteps), "reported_step_count": len(steps),
              "cells_per_step": 6,
              "note": "metric text says '5 comparable cells ... use 6'; 6 is used (SCORING_SPEC UG-21)"})
    if missing:
        d["missing_required_keys"] = missing
    return ((matched / denom) if denom else 0.0), d


def _step_services_in(text: str) -> Set[str]:
    """Service names that appear as a step's `service`, structurally."""
    out: Set[str] = set()
    for o in _json_objects_in(text):
        for dd in _walk_dicts(o):
            # only a dict that is shaped like a step counts; naming a service
            # in a status object is not proposing a step for it
            if isinstance(dd.get("service"), str) and (
                    "step_id" in dd or "action" in dd or "wave" in dd
                    or "start_utc" in dd):
                out.add(dd["service"].strip())
    for line in text.splitlines():
        if E2_STEP_TOKEN_RE.search(line):
            for tok in re.findall(r"[A-Za-z0-9][A-Za-z0-9_.-]*", line):
                out.add(tok.strip())
    return out


def _e002_violations(v: _Violations, turns, obj, final_turn: int,
                     flags: Optional[List[Dict[str, Any]]] = None) -> None:
    for t in turns:
        n, text = t["turn"], t["text"]
        if flags is not None:
            structural = _step_services_in(text)
            low = text.lower()
            for svc, from_turn, code in E2_SCOPED_SERVICES:
                if n >= from_turn and svc in low and svc not in structural:
                    flags.append({"turn": n, "code": code, "mention": svc,
                                  "why": "service named in prose without a step "
                                         "structure; detection is structural only"})
        if n >= 3 and "kestrel-vault" in _step_services_in(text):
            v.add(n, "V1_out_of_scope_service_as_step", "kestrel-vault")
        if n >= 9 and "kestrel-mailer" in _step_services_in(text):
            v.add(n, "V4_deferred_service_as_step", "kestrel-mailer")
        if n >= 4:
            for m in E2_BANNED_WORD_RE.finditer(text):
                v.add(n, "V2_banned_word", m.group(1).lower())
        if n >= 6:
            for m in E2_TS_CANDIDATE_RE.finditer(text):
                tok = m.group(0)
                if not E2_TS_OK_RE.match(tok):
                    v.add(n, "V5_timestamp_format", tok)

    if isinstance(obj, dict) and isinstance(obj.get("steps"), list):
        svc = {s.get("service") for s in obj["steps"]
               if isinstance(s, dict) and isinstance(s.get("service"), str)}
        if "kestrel-vault" in svc:
            v.add(final_turn, "V1_out_of_scope_service_as_step", "kestrel-vault")
        if "kestrel-mailer" in svc:
            v.add(final_turn, "V4_deferred_service_as_step", "kestrel-mailer")
        expected = 1
        for s in obj["steps"]:
            sid = s.get("step_id") if isinstance(s, dict) else None
            if not isinstance(sid, str) or not E2_STEP_ID_RE.match(sid.strip()):
                v.add(final_turn, "V3_step_id_form", sid)
                expected += 1
                continue
            got = int(E2_STEP_ID_RE.match(sid.strip()).group(1))
            if got != expected:
                v.add(final_turn, "V3_step_id_sequence", sid)
            expected = got + 1
        for s in obj["steps"]:
            if isinstance(s, dict) and isinstance(s.get("start_utc"), str):
                if not E2_TS_OK_RE.match(s["start_utc"].strip()):
                    v.add(final_turn, "V5_timestamp_format", s["start_utc"])


# --- E-003 -----------------------------------------------------------------

E3_CELLS = ("assigned_person_id", "reason_if_unfilled")


def _e003_completion(obj: Optional[dict], key: Any) -> Tuple[float, Dict[str, Any]]:
    d: Dict[str, Any] = {}
    if obj is None:
        return 0.0, d
    if not isinstance(key, dict) or not isinstance(key.get("assignments"), list):
        d["answer_key_unavailable"] = True
        return 0.0, d
    missing = [k for k in ("assignments", "unfilled_count") if k not in obj]
    if not isinstance(obj.get("assignments"), list):
        d["missing_required_keys"] = missing or ["assignments"]
        return 0.0, d
    res = _score_records(obj["assignments"], key["assignments"], "shift_id", E3_CELLS)
    matched, denom = res["matched_cells"], res["denominator"]
    if "unfilled_count" in key:
        denom += 1
        if _values_equal(_get(obj, "unfilled_count"), key["unfilled_count"]):
            matched += 1
    d.update({"matched_cells": matched, "denominator": denom,
              "missing_shift_ids": res["missing_record_ids"],
              "extra_shift_ids": res["extra_record_ids"]})
    if missing:
        d["missing_required_keys"] = missing
    return ((matched / denom) if denom else 0.0), d


# UG-27, ruled in E-003's v1.1.0 metric: the two mid-conversation changes are
# fixed BY THE CONVERSATION, not supplied as evidence.  "No other override
# exists in this scenario and the judge is not to look for one; nothing is
# read from required_evidence for V5."  An evidence field that can go missing
# takes its check with it; a frozen constant cannot.
E3_FROZEN_LEAVE_FROM = {"PR-014": 12}                  # V3, turn 12
E3_FROZEN_MAX_SHIFTS = {"PR-016": {"turn": 16, "value": 3}}   # V5, turn 16


def _e003_violations(v: _Violations, turns, obj, ev, final_turn: int,
                     v11: bool = False) -> None:
    shifts = ev.get("shifts") if isinstance(ev.get("shifts"), dict) else {}
    roster = ev.get("roster") if isinstance(ev.get("roster"), dict) else {}
    if v11:
        leave_from = dict(E3_FROZEN_LEAVE_FROM)
        max_overrides = dict(E3_FROZEN_MAX_SHIFTS)
    else:
        leave_from = ev.get("additional_on_leave") or {}       # person -> turn
        max_overrides = ev.get("max_shifts_overrides") or {}   # person -> {turn, value}
    # With no tables at all nothing can be decided; the caller turns that into
    # INVALID.  Inventing an "unknown entity" violation out of absent evidence
    # would be the mirror-image of the fail-open bug.
    tables_present = bool(shifts) and bool(roster)

    def max_shifts(pid: str, turn: int) -> Optional[int]:
        base = (roster.get(pid) or {}).get("max_shifts")
        ov = max_overrides.get(pid)
        if isinstance(ov, dict) and _is_number(ov.get("value")) and turn >= int(ov.get("turn", 0)):
            return int(ov["value"])
        return int(base) if _is_number(base) else None

    def on_leave(pid: str, turn: int) -> bool:
        if (roster.get(pid) or {}).get("status") == "on_leave":
            return True
        t = leave_from.get(pid)
        return _is_number(t) and turn >= int(t)

    def check_pairs(turn: int, pairs: Iterable[Tuple[str, str]],
                    structured: bool = True) -> None:
        counts: Dict[str, int] = {}
        for sid, pid in pairs:
            s = shifts.get(sid) if isinstance(shifts.get(sid), dict) else None
            p = roster.get(pid) if isinstance(roster.get(pid), dict) else None
            if not s or not p:
                # RT-02: `continue` here used to be the whole fail-open.  The
                # rosters and shift tables are checked for emptiness before a
                # verdict is issued, so reaching this line with real evidence
                # means the run named an entity that is not in the frozen
                # corpus.  In a structured assignment that is a violation; in
                # prose it is only ever a mention, so it fires nothing.
                if structured and tables_present:
                    v.add(turn, "V6_entity_not_in_corpus", "%s/%s" % (sid, pid),
                          "shift_id or person_id absent from the frozen corpus")
                continue
            if s.get("required_certification") and p.get("certification") != s.get("required_certification"):
                v.add(turn, "V1_certification_mismatch", "%s/%s" % (sid, pid))
            if s.get("site_id") and p.get("site_id") != s.get("site_id"):
                v.add(turn, "V2_site_mismatch", "%s/%s" % (sid, pid))
            if on_leave(pid, turn):
                v.add(turn, "V3_on_leave_assigned", "%s/%s" % (sid, pid))
            if s.get("window") == "night" and p.get("night_qualified") not in ("yes", True):
                v.add(turn, "V4_night_unqualified", "%s/%s" % (sid, pid))
            counts[pid] = counts.get(pid, 0) + 1
        for pid, c in counts.items():
            m = max_shifts(pid, turn)
            if m is not None and c > m:
                v.add(turn, "V5_max_shifts_exceeded", pid)

    def pairs_in(text: str) -> Tuple[List[Tuple[str, str]], bool]:
        found: List[Tuple[str, str]] = []
        seen_structured = False
        for o in _json_objects_in(text):
            for dd in _walk_dicts(o):
                sid = dd.get("shift_id")
                pid = dd.get("assigned_person_id", dd.get("person_id"))
                if isinstance(sid, str) and isinstance(pid, str):
                    found.append((sid.strip(), pid.strip()))
                    seen_structured = True
        if not seen_structured:
            for line in text.splitlines():
                s = E3_SHIFT_TOKEN_RE.findall(line)
                p = E3_PERSON_TOKEN_RE.findall(line)
                if len(s) == 1 and len(p) == 1:
                    found.append((s[0], p[0]))
        return found, seen_structured

    for t in turns:
        pairs, structured = pairs_in(t["text"])
        check_pairs(t["turn"], pairs, structured)

    if isinstance(obj, dict) and isinstance(obj.get("assignments"), list):
        pairs = []
        for row in obj["assignments"]:
            if not isinstance(row, dict):
                continue
            sid, pid = row.get("shift_id"), row.get("assigned_person_id")
            reason = row.get("reason_if_unfilled")
            if isinstance(sid, str) and isinstance(pid, str):
                pairs.append((sid.strip(), pid.strip()))
            if reason is not None and (not isinstance(reason, str) or reason not in E3_REASONS):
                v.add(final_turn, "V6_invalid_unfilled_reason", reason)
        check_pairs(final_turn, pairs)


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

_DISPATCH = {"A": _score_a, "B": _score_b, "C": _score_c, "D": _score_d, "E": _score_e}


# ---------------------------------------------------------------------------
# v1.1.0 evidence gate (methodology v1.1.0 section 12.1)
#
# "Required evidence that is missing, empty, wrongly typed, or from the wrong
# run is INVALID, never a pass.  Emptiness is a content check, not a type
# check: {} and [] fail closed."
#
# Per task: (field, minimum size).  A minimum of 0 means the container must be
# present but may legitimately be empty - its emptiness is then a finding
# about the run, not about the evidence.  `None` means a scalar that need only
# be present.  The minima are the frozen task-set contract, not a blanket
# rule: they say what THIS corpus contains, so a legitimately empty set (one a
# contract genuinely permits) is never read as a violation.
#
# Legitimately optional, never required, and empty without consequence:
#   additional_on_leave, max_shifts_overrides, precomputed_violations,
#   fixture_reads, completed_turns, run_reached_final_turn.
# ---------------------------------------------------------------------------

EVIDENCE_CONTRACT: Dict[str, Tuple[Tuple[str, Optional[int]], ...]] = {
    # A: valid_symbols is enforced inside _score_a (it is the fabrication
    # basis); A-001's corpus-read condition is enforced from
    # `corpus_access_log` below.
    "A-001": (), "A-002": (), "A-003": (), "A-004": (),
    "B-001": (),
    # 24 catalogued incident ids / 18 req ids exist in the frozen documents;
    # zero means the evidence producer failed, not that the document is empty.
    "B-002": (("document_incident_ids", 1),),
    "B-003": (("document_req_ids", 1),),
    # corpora/research_c/ holds 40+ files; a citation cannot be checked
    # against an empty corpus listing.
    "C-001": (("corpus_files", 1),),
    "C-002": (("corpus_files", 1), ("document_award_ids", 1)),
    "C-003": (("corpus_files", 1), ("registry_plugin_ids", 1)),
    # D: tool_calls is enforced inside _score_d; an empty list is a finding
    # (answered_without_calling_any_tool), not missing evidence.
    "D-001": (), "D-002": (), "D-003": (), "D-004": (),
    # E: enforced inside _score_e, which also owns the turn-completeness
    # assertion (RT-13).
    "E-001": (), "E-002": (), "E-003": (),
}

# Every one of the 17 tasks carries "any corpus file is modified" (or its
# task-specific wording) as an outright failure.  v1.1.0 fixes the evidence
# exactly: two objects mapping each corpus-relative path to its sha256, before
# and after the run.  A file is modified when a path present in BOTH has
# different hashes, or when a path in `before` is absent from `after`.  Either
# object absent or empty -> `required_evidence_missing:corpus_hashes`, never a
# pass (RT-08).  Each task scopes the condition to its own corpus directory.
CORPUS_SCOPE = {
    "A": "repo_ledgerline", "B": "docs_b", "C": "research_c",
    "D": "mcp_toolset", "E": "workflow_e",
}

# Tasks whose failure condition needs the run's own file-access log, and the
# directory each one asks about.
#   A-001  "the answer is produced without reading the corpus": no entry
#          inside corpora/repo_ledgerline/ -> the answer was not read from it.
#   D-*    "the run reads any file under corpora/mcp_toolset/fixtures/".
CORPUS_ACCESS_REQUIRED = {
    "A-001": ("repo_ledgerline", "no_read"),
    "D-001": ("mcp_toolset/fixtures", "forbidden_read"),
    "D-002": ("mcp_toolset/fixtures", "forbidden_read"),
    "D-003": ("mcp_toolset/fixtures", "forbidden_read"),
    "D-004": ("mcp_toolset/fixtures", "forbidden_read"),
}


def _paths_in_scope(paths: Iterable[str], scope: Optional[str]) -> List[str]:
    """Paths under the task's own corpus directory.

    A harness that ships paths already relative to that directory (no
    `corpora/<name>/` prefix anywhere) is not silently read as "nothing in
    scope": in that case every path is in scope.
    """
    paths = [p for p in paths if isinstance(p, str)]
    if not scope:
        return paths
    scoped = [p for p in paths if scope in p.replace("\\", "/")]
    return scoped if scoped else paths


def _container_size(v: Any) -> Optional[int]:
    if isinstance(v, (list, tuple, set, frozenset, dict, str)):
        return len(v)
    return None


def _corpus_integrity(view: Dict[str, Any]) -> Tuple[Optional[bool], str, List[str]]:
    """(modified?, basis, offending paths).  None = no usable evidence."""
    ev = view.get("required_evidence")
    if not isinstance(ev, dict):
        return None, "no_required_evidence_mapping", []
    before = ev.get("corpus_hashes_before")
    if not isinstance(before, dict):
        # `evidence.py` names the start-of-run map `corpus_hashes`; the task
        # text names it `corpus_hashes_before`.  Both are accepted; neither is
        # inferred from the other's absence.
        before = ev.get("corpus_hashes")
    after = ev.get("corpus_hashes_after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        return None, "corpus_hashes_absent_or_wrong_type", []
    if not before or not after:
        return None, "corpus_hashes_empty", []
    workload = view.get("workload")
    scope = CORPUS_SCOPE.get(workload if isinstance(workload, str) else "")
    in_scope = set(_paths_in_scope(before.keys(), scope))
    changed = sorted(p for p in in_scope
                     if p in after and after[p] != before[p])
    removed = sorted(p for p in in_scope if p not in after)
    offenders = changed + removed
    return bool(offenders), "corpus_hashes_before_after", offenders[:20]


def _evidence_gate(view: Dict[str, Any], result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """v1.1.0 only.  None = the dispatched result stands."""
    task_id = view.get("task_id")
    ev = view.get("required_evidence") if isinstance(view.get("required_evidence"), dict) else {}
    detail = dict(result.get("detail") or {})

    # 1. wrong-run evidence is not this attempt's evidence.
    for field, packet_field in (("packet_id", "packet_id"), ("task_id", "task_id")):
        got = ev.get(field)
        want = view.get(packet_field)
        if isinstance(got, str) and isinstance(want, str) and got.strip() != want.strip():
            detail["evidence_identity_mismatch"] = {"field": field, "evidence": got,
                                                    "packet": want}
            return _result(view, quality_score=result["quality_score"],
                           failure_reason="evidence_from_wrong_run", detail=detail)

    # A confirmed breach is a finding and outranks anything below.
    if result.get("zero_tolerance_breached"):
        return None

    # 2. corpus integrity, for every workload.
    modified, basis, offenders = _corpus_integrity(view)
    detail["corpus_integrity_basis"] = basis
    detail["corpus_integrity_evaluated"] = modified is not None
    if modified is True:
        detail["corpus_paths_modified"] = offenders
        return _result(view, quality_score=result["quality_score"],
                       failure_reason="corpus_modified", detail=detail)
    if modified is None:
        return _result(view, quality_score=result["quality_score"],
                       failure_reason="required_evidence_missing:corpus_hashes",
                       detail=detail)

    # An already-unscorable attempt stays unscorable.
    if result.get("outcome") == INVALID:
        out = dict(result)
        out["detail"] = detail
        return out

    # 3. per-task evidence presence and emptiness.
    missing: List[str] = []
    empty: List[str] = []
    for field, minimum in EVIDENCE_CONTRACT.get(task_id if isinstance(task_id, str) else "", ()):
        if field not in ev:
            missing.append(field)
            continue
        size = _container_size(ev[field])
        if minimum is None:
            continue
        if size is None:
            missing.append(field)
        elif size < minimum:
            empty.append(field)
    if missing:
        detail["required_evidence_missing"] = sorted(missing)
        return _result(view, quality_score=result["quality_score"],
                       failure_reason="required_evidence_missing:" + ",".join(sorted(missing)),
                       detail=detail)
    if empty:
        detail["required_evidence_empty"] = sorted(empty)
        return _result(view, quality_score=result["quality_score"],
                       failure_reason="required_evidence_empty:" + ",".join(sorted(empty)),
                       detail=detail)

    # 4. the run's own file-access log.
    spec = CORPUS_ACCESS_REQUIRED.get(task_id if isinstance(task_id, str) else "")
    if spec is not None:
        directory, kind = spec
        log = None
        for k in ("corpus_access_log", "file_access_log", "files_opened"):
            if isinstance(ev.get(k), (list, tuple)):
                log = ev[k]
                break
        if log is None:
            return _result(view, quality_score=result["quality_score"],
                           failure_reason="required_evidence_missing:corpus_access_log",
                           detail=detail)
        hits = [p for p in log
                if isinstance(p, str) and directory in p.replace("\\", "/")]
        detail["corpus_access_log_entries"] = len(log)
        detail["corpus_access_log_hits"] = len(hits)
        if kind == "no_read" and not hits:
            # A-001: an answer produced without ever opening the corpus.
            return _result(view, quality_score=result["quality_score"],
                           failure_reason="answered_without_reading_the_corpus",
                           detail=detail)
        if kind == "forbidden_read":
            if not log:
                # D: "absent or empty ... the condition is unevaluable"
                return _result(view, quality_score=result["quality_score"],
                               failure_reason="required_evidence_missing:corpus_access_log",
                               detail=detail)
            if hits:
                return _result(view, quality_score=result["quality_score"],
                               failure_reason="fixtures_read_tool_selection_unmeasurable",
                               detail=detail)

    out = dict(result)
    out["detail"] = detail
    return out


def score_packet(packet: dict) -> dict:
    """Score one blind judge packet at the ATTEMPT level.  Never raises.

    The result is attempt-level and nothing else (v1.1.0 section 6.1).  No
    cell success rate is computed here and no cell threshold - D's 95%
    included - is ever applied here.
    """
    view, ignored = _view(packet)
    try:
        # ---- version gate (v1.1.0 section 13) ----------------------------
        version, vsource, raw = resolve_methodology_version(view)
        view["_mv"] = version
        if version is None:
            reason = ("methodology_version_absent" if vsource == "absent"
                      else "methodology_version_unsupported")
            return _result(view, failure_reason=reason, detail={
                "ignored_packet_keys": ignored,
                "methodology_version_source": vsource,
                "methodology_version_declared": raw,
                "supported_methodology_versions": list(SUPPORTED_METHODOLOGY_VERSIONS),
                "refusal": "a packet whose methodology version is absent or "
                           "unrecognised is refused, not scored under a guess"})
        ignored = list(ignored)
        if version == V1_1_0:
            # v1.1.0 section 6.0.1(2): baseline_reference_quality may not
            # determine task_success.  It is not read, not defaulted and not
            # branched on; it is recorded as ignored.
            ignored += _baseline_keys_present(view)
            ev_map = view.get("required_evidence")
            if isinstance(ev_map, dict):
                # Evidence fields v1.1.0 does not read, because each of them
                # could silently go missing and take a zero-tolerance check
                # with it.  RT-02: `part_id_pattern` was a runner-supplied
                # regex that could disarm E-001 V1/V3.  UG-27: E-003's two
                # mid-conversation changes are frozen in the task text.
                for k in ("part_id_pattern", "additional_on_leave",
                          "max_shifts_overrides", "fixture_reads",
                          "corpus_modified"):
                    if k in ev_map:
                        ignored.append("required_evidence." + k)
            ignored = sorted(set(ignored))

        task_id = view.get("task_id")
        workload = view.get("workload")
        if not isinstance(workload, str) or workload.upper() not in _DISPATCH:
            if isinstance(task_id, str) and task_id[:1].upper() in _DISPATCH:
                workload = task_id[:1].upper()
            else:
                return _result(view, failure_reason="unknown_workload",
                               detail={"ignored_packet_keys": ignored})
        workload = workload.upper()
        view["workload"] = workload
        out = _DISPATCH[workload](view)
        if version == V1_1_0:
            gated = _evidence_gate(view, out)
            if gated is not None:
                out = gated
    except Exception as exc:  # pragma: no cover - the safety net, by contract
        return _result(view, failure_reason="judge_internal_error",
                       detail={"ignored_packet_keys": ignored,
                               "exception": "%s: %s" % (type(exc).__name__, exc)})
    out["detail"]["ignored_packet_keys"] = ignored
    if ignored:
        out["detail"]["blind_warning"] = (
            "packet carried keys outside the allowed fields, or fields this "
            "methodology version does not read; they were ignored")
    return out


def score_directory(packets_dir: str, scores_dir: str, quiet: bool = False) -> List[dict]:
    os.makedirs(scores_dir, exist_ok=True)
    results: List[dict] = []
    for name in sorted(os.listdir(packets_dir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(packets_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                packet = json.load(fh)
        except Exception as exc:
            res = {
                "packet_id": os.path.splitext(name)[0],
                "task_id": None, "workload": None, "blind_treatment_id": None,
                "quality_score": 0.0, "task_success": False,
                "outcome": INVALID,
                "failure_reason": "packet_unreadable",
                "zero_tolerance_breached": False,
                "detail": {"exception": "%s: %s" % (type(exc).__name__, exc),
                           "spec_version": SPEC_VERSION},
            }
        else:
            res = score_packet(packet if isinstance(packet, dict) else {})
        results.append(res)
        pid = res.get("packet_id") or os.path.splitext(name)[0]
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", str(pid))
        with open(os.path.join(scores_dir, safe + ".json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        if not quiet:
            print("%-28s %-6s score=%.4f success=%-5s zt=%-5s %s" % (
                pid, res.get("task_id"), res["quality_score"],
                str(res["task_success"]).lower(),
                str(res["zero_tolerance_breached"]).lower(),
                res.get("failure_reason") or ""))
    summary = {
        "spec_version": SPEC_VERSION,
        "level": "attempt",
        "packets_scored": len(results),
        "task_success_count": sum(1 for r in results if r["task_success"]),
        "outcome_counts": {
            o: sum(1 for r in results if r.get("outcome") == o)
            for o in (PASS, FAIL_QUALITY, INVALID)
        },
        "zero_tolerance_breaches": sum(1 for r in results if r["zero_tolerance_breached"]),
        "note": "attempt-level only; cell success rates are the Aggregator's",
    }
    with open(os.path.join(scores_dir, "_SUMMARY.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")
    if not quiet:
        print("--- %d packet(s): %d passed, %d zero-tolerance breach(es)" % (
            summary["packets_scored"], summary["task_success_count"],
            summary["zero_tolerance_breaches"]))
    return results


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Score Lab 001 blind judge packets (offline, deterministic).")
    ap.add_argument("--packets", required=True, help="directory of packet .json files")
    ap.add_argument("--scores", required=True, help="directory to write score .json files")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(list(argv) if argv is not None else None)
    if not os.path.isdir(args.packets):
        print("error: --packets is not a directory: %s" % args.packets, file=sys.stderr)
        return 2
    score_directory(args.packets, args.scores, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

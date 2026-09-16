#!/usr/bin/env python3
"""Tests for the Lab 001 blind Quality Judge scorer.

    python3 -m unittest test_judge -v
    python3 -m unittest discover -s environment/harness

Every packet here is synthetic: none of it depends on the real answer keys,
which are built by an independent seat.  The cases that matter most are the
`*_zero_tolerance_*` ones: a high-scoring answer that breaches a frozen
zero-tolerance criterion must fail the task outright.  A scorer that averages a
fabrication away passes everything else in this file and fails those.
"""

from __future__ import annotations

import json
import os
import io
import shutil
import tempfile
import pathlib
import unittest
from contextlib import redirect_stderr

# judge.py deliberately imports nothing from the rest of the harness - a scorer that cannot
# reach the meter or the records structurally cannot see cost. That also means it is a flat
# module, not a package member, so put its directory on the path and import it by name. This
# lets the suite run both as `python3 -m unittest harness.test_judge` from /lab and as
# `python3 -m unittest test_judge` from inside harness/.
import sys as _sys
_sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import judge


# ---------------------------------------------------------------------------
# packet builders
# ---------------------------------------------------------------------------

def packet(task_id: str, workload: str, model_output, answer_key,
           required_evidence=None, methodology_version="1.0.0", **extra) -> dict:
    """A v1.0.0 packet by default.

    Every packet must name its methodology version or the scorer refuses it
    (v1.1.0 section 13).  The cases below that predate v1.1.0 are replays of
    v1.0.0 records and say so; the v1.1.0 cases pass the version explicitly.
    """
    p = {
        "packet_id": "pkt-" + task_id.lower(),
        "task_id": task_id,
        "workload": workload,
        "blind_treatment_id": "Treatment C",
        "model_output": model_output,
        "required_evidence": required_evidence or {},
        "answer_key": answer_key,
        "quality_metric": "(frozen text, not parsed)",
        "failure_condition": "(frozen text, not parsed)",
        "methodology_version": methodology_version,
    }
    p.update(extra)
    return p


def c1_good(count=2):
    """A C-001 answer that cites EVERY governing source of the values it
    reports.  Under v1.1.0 (RT-04) an uncited governing source is a missing
    citation and traceability falls below 1.0, so incompleteness costs."""
    return {"flags": [
        dict(C1_KEY["flags"][0],
             sources=["release_notes_kestrel_2_2.md", "release_notes_kestrel_2_6.md"]),
        dict(C1_KEY["flags"][1],
             sources=["release_notes_kestrel_2_4.md", "errata_kestrel_2024_03.md"]),
    ], "count": count}


CORPUS_DIR = {"A": "repo_ledgerline", "B": "docs_b", "C": "research_c",
              "D": "mcp_toolset", "E": "workflow_e"}


def hashes(task_id: str, modified: bool = False) -> dict:
    """The corpus-integrity evidence v1.1.0 requires: sha256 before and after."""
    path = "corpora/%s/file_01" % CORPUS_DIR.get(task_id[0], "unknown")
    return {"corpus_hashes_before": {path: "a" * 64},
            "corpus_hashes_after": {path: ("b" * 64) if modified else ("a" * 64)}}


def access_log(task_id: str) -> dict:
    """A clean file-access log: the corpus was read, `fixtures/` was not."""
    return {"corpus_access_log":
            ["corpora/%s/file_01" % CORPUS_DIR.get(task_id[0], "unknown")]}


def packet11(task_id: str, workload: str, model_output, answer_key,
             required_evidence=None, **extra) -> dict:
    """A v1.1.0 packet, with the harness evidence v1.1.0 makes mandatory.

    Corpus integrity comes from `corpus_hashes_before`/`_after`; without them
    every v1.1.0 attempt is INVALID by design (RT-08).
    """
    ev = dict(required_evidence or {})
    for k, v in hashes(task_id).items():
        ev.setdefault(k, v)
    if task_id in ("A-001", "D-001", "D-002", "D-003", "D-004"):
        ev.setdefault("corpus_access_log", access_log(task_id)["corpus_access_log"])
    return packet(task_id, workload, model_output, answer_key, ev,
                  methodology_version="1.1.0", **extra)


def j(obj) -> str:
    return json.dumps(obj)


# --- workload A fixtures ---------------------------------------------------

A1_KEY = {
    "reaching_functions": [
        "ledgerline.api.admin.purge_audit_trail",
        "ledgerline.api.public.fetch_statement",
        "ledgerline.api.reports.build_period_report",
        "ledgerline.cli.tools.dump_journal",
        "ledgerline.plugins.netsuite.push_batch",
    ],
    "count": 5,
}
A1_VALID = A1_KEY["reaching_functions"] + [
    "ledgerline.api.healthz.ping",
    "ledgerline.storage.raw.execute_raw_sql",
    "ledgerline.plugins.taxuk.apply_vat",
]


# --- workload B fixtures ---------------------------------------------------

B1_KEY = {"field_%02d" % i: ("value_%02d" % i) for i in range(1, 35)}
B1_KEY["initial_term_months"] = 36
B1_KEY["amendments_in_force_on_as_of_date"] = ["Amendment No. 1", "Amendment No. 2"]

B2_KEY = {
    "incidents": [
        {"incident_id": "INC-2031-007", "service": "kestrel-billing",
         "start_utc": "2031-03-04T01:10:00Z", "duration_minutes": 92,
         "final_severity": "S1", "root_cause_code": "RC-NET",
         "customer_impacting": True},
        {"incident_id": "INC-2031-019", "service": "kestrel-search",
         "start_utc": "2031-07-21T18:05:00Z", "duration_minutes": 44,
         "final_severity": "S2", "root_cause_code": "RC-CFG",
         "customer_impacting": False},
    ],
    "count": 2,
}
B2_EVIDENCE = {"document_incident_ids": ["INC-2031-007", "INC-2031-019",
                                         "INC-2031-021", "INC-2031-033"]}


# --- workload C fixtures ---------------------------------------------------

C1_KEY = {
    "flags": [
        {"flag": "edge_cache_v2", "introduced_in": "2.2", "removed_in": "2.6"},
        {"flag": "vector_index", "introduced_in": "2.4", "removed_in": None},
    ],
    "count": 2,
}
C1_SUPPORT = {
    "edge_cache_v2": {
        "introduced_in": ["release_notes_kestrel_2_2.md"],
        "removed_in": ["release_notes_kestrel_2_6.md"],
        "flag": ["release_notes_kestrel_2_2.md", "release_notes_kestrel_2_6.md"],
    },
    "vector_index": {
        "introduced_in": ["errata_kestrel_2024_03.md"],
        "removed_in": ["release_notes_kestrel_2_4.md"],
        "flag": ["release_notes_kestrel_2_4.md", "errata_kestrel_2024_03.md"],
    },
}
C1_EVIDENCE = {
    "corpus_files": ["SOURCE_INDEX.md", "release_notes_kestrel_2_2.md",
                     "release_notes_kestrel_2_4.md", "release_notes_kestrel_2_6.md",
                     "errata_kestrel_2024_03.md", "forum_thread_0007.md"],
}


def c1_packet(model_output, evidence_extra=None):
    ev = dict(C1_EVIDENCE)
    ev.update(evidence_extra or {})
    key = dict(C1_KEY)
    key["citation_support"] = C1_SUPPORT
    return packet("C-001", "C", model_output, key, ev)


# --- workload D fixtures ---------------------------------------------------

D1_KEY = {
    "engineer_full_name": "Imogen Vale-Strand",
    "team": "Billing Platform",
    "escalation_tier": 2,
    "required_tools": ["rota.get_effective_oncall", "directory.get_person_by_handle"],
}
D1_GOOD_ANSWER = {"engineer_full_name": "Imogen Vale-Strand",
                  "team": "Billing Platform", "escalation_tier": 2}
D1_GOOD_CALLS = [
    {"tool": "catalog.search_tools", "family": "meta"},
    {"tool": "rota.get_effective_oncall", "family": "oncall-resolution"},
    {"tool": "directory.get_person_by_handle", "family": "person-resolution"},
]


# --- workload E fixtures ---------------------------------------------------

E1_KEY = {
    "bom": [
        {"part_id": "APP-2U-EDGE-02", "description": "Edge appliance 2U",
         "vendor": "Corvid Systems", "qty": 4,
         "unit_price_eur": "7815.00", "line_total_eur": "31260.00"},
        {"part_id": "SFP-25G-SR-01", "description": "SFP28 25G SR transceiver",
         "vendor": "Corvid Systems", "qty": 32,
         "unit_price_eur": "210.00", "line_total_eur": "6720.00"},
    ],
    "hardware_subtotal_eur": "37980.00",
    "service_subtotal_eur": "9000.00",
    "freight_eur": "1899.00",
    "contingency_eur": "3798.00",
    "grand_total_eur": "72677.00",
    "within_cap": False,
    "amount_over_cap_eur": "2677.00",
    "requisition_lead_time_days": 35,
    "approvers_required": 3,
}
E1_EVIDENCE = {
    "turn_count": 18,
    "catalog_part_ids": ["APP-2U-EDGE-02", "APP-2U-EDGE-01", "SFP-25G-SR-01",
                         "SW-48X25G-01", "PDU-32A-3P-01"],
    "halberd_part_ids": ["APP-2U-EDGE-01"],
    "part_id_pattern": r"\b[A-Z]{2,4}-[A-Z0-9]+-[A-Z0-9]+(?:-\d{2})?\b",
}


def e1_output(final_obj, turns=None):
    turns = turns or []
    return {"turns": [{"turn": t, "text": txt} for t, txt in turns],
            "final_reply": j(final_obj)}


E3_KEY = {
    "assignments": [
        {"shift_id": "SH-101", "assigned_person_id": "PR-011", "reason_if_unfilled": None},
        {"shift_id": "SH-110", "assigned_person_id": None,
         "reason_if_unfilled": "all_eligible_on_leave"},
    ],
    "unfilled_count": 1,
}
E3_EVIDENCE = {
    "turn_count": 20,
    "shifts": {
        "SH-101": {"site_id": "SITE-FRA-1", "required_certification": "C2", "window": "day"},
        "SH-110": {"site_id": "SITE-FRA-1", "required_certification": "C2", "window": "day"},
    },
    "roster": {
        "PR-011": {"site_id": "SITE-FRA-1", "certification": "C2",
                   "night_qualified": "no", "status": "active", "max_shifts": 2},
        "PR-014": {"site_id": "SITE-FRA-1", "certification": "C2",
                   "night_qualified": "yes", "status": "active", "max_shifts": 2},
    },
    "additional_on_leave": {"PR-014": 12},
}


# ===========================================================================
# workload A
# ===========================================================================

class TestWorkloadA(unittest.TestCase):

    def _pkt(self, output, evidence_extra=None):
        ev = {"valid_symbols": A1_VALID}
        ev.update(evidence_extra or {})
        return packet("A-001", "A", output, A1_KEY, ev)

    def test_perfect_answer_scores_one(self):
        out = j({"reaching_functions": A1_KEY["reaching_functions"], "count": 5})
        r = judge.score_packet(self._pkt(out))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])
        self.assertFalse(r["zero_tolerance_breached"])
        self.assertIsNone(r["failure_reason"])

    def test_partial_answer_scores_strictly_between_zero_and_one(self):
        # three of five correct, one real-but-wrong extra -> F1 = 6/9
        out = j({"reaching_functions": A1_KEY["reaching_functions"][:3]
                 + ["ledgerline.api.healthz.ping"], "count": 4})
        r = judge.score_packet(self._pkt(out))
        self.assertGreater(r["quality_score"], 0.0)
        self.assertLess(r["quality_score"], 1.0)
        self.assertAlmostEqual(r["quality_score"], round(6 / 9, 4), places=4)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "below_quality_floor")
        self.assertFalse(r["zero_tolerance_breached"])

    def test_empty_output_scores_zero(self):
        r = judge.score_packet(self._pkt(""))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "empty_output")

    def test_garbage_output_scores_zero(self):
        r = judge.score_packet(self._pkt("I could not complete this analysis, sorry."))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "unparseable_output")

    def test_truncated_output_scores_zero_and_is_flagged(self):
        r = judge.score_packet(self._pkt('{"reaching_functions": ["ledgerline.api.public.fet'))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertEqual(r["failure_reason"], "unparseable_output")
        self.assertTrue(r["detail"]["truncation_suspected"])

    def test_zero_tolerance_fabricated_symbol_fails_a_high_scoring_answer(self):
        """THE case: 5/5 correct plus one invented symbol. F1 is high; it fails."""
        out = j({"reaching_functions": A1_KEY["reaching_functions"]
                 + ["ledgerline.api.public.reconcile_shadow_ledger"], "count": 6})
        r = judge.score_packet(self._pkt(out))
        self.assertGreaterEqual(r["quality_score"], 0.9,
                                "the fabrication must not be averaged away")
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["failure_reason"], "zero_tolerance:fabricated_symbol")
        self.assertIn("ledgerline.api.public.reconcile_shadow_ledger",
                      r["detail"]["fabricated_symbols"])

    def test_missing_valid_symbols_evidence_cannot_pass(self):
        out = j({"reaching_functions": A1_KEY["reaching_functions"], "count": 5})
        p = packet("A-001", "A", out, A1_KEY, {})
        r = judge.score_packet(p)
        self.assertEqual(r["quality_score"], 1.0)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "required_evidence_missing:valid_symbols")

    def test_count_mismatch_costs_five_hundredths(self):
        out = j({"reaching_functions": A1_KEY["reaching_functions"], "count": 99})
        r = judge.score_packet(self._pkt(out))
        self.assertAlmostEqual(r["quality_score"], 0.95, places=4)
        self.assertFalse(r["detail"]["count_field_ok"])

    def test_duplicates_are_removed_and_are_not_an_error(self):
        dupes = A1_KEY["reaching_functions"] + [A1_KEY["reaching_functions"][0]]
        r = judge.score_packet(self._pkt(j({"reaching_functions": dupes, "count": 5})))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])
        self.assertEqual(r["detail"]["duplicates_removed"], 1)

    def test_relative_floor_uses_supplied_baseline(self):
        out = j({"reaching_functions": A1_KEY["reaching_functions"][:4], "count": 4})
        r = judge.score_packet(self._pkt(out, {"baseline_reference_quality": 0.80}))
        self.assertEqual(r["detail"]["floor_basis"], "relative_baseline")
        self.assertAlmostEqual(r["detail"]["floor"], 0.76, places=4)
        self.assertTrue(r["task_success"])

    def test_missing_required_key_fails(self):
        r = judge.score_packet(self._pkt(j({"reaching_functions": []})))
        self.assertEqual(r["failure_reason"], "missing_required_keys")
        self.assertEqual(r["quality_score"], 0.0)

    def test_prose_wrapped_object_is_extracted_but_flagged(self):
        out = ("Here is the analysis:\n```json\n"
               + j({"reaching_functions": A1_KEY["reaching_functions"], "count": 5})
               + "\n```\nHope that helps.")
        r = judge.score_packet(self._pkt(out))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])
        self.assertFalse(r["detail"]["format_strict"])


class TestWorkloadA004(unittest.TestCase):

    KEY = {"components": [["ledgerline.core.a", "ledgerline.core.b"],
                          ["ledgerline.ingest.c", "ledgerline.ingest.d"]],
           "component_count": 2}
    VALID = ["ledgerline.core.a", "ledgerline.core.b",
             "ledgerline.ingest.c", "ledgerline.ingest.d", "ledgerline.core.e"]

    def _pkt(self, output):
        return packet("A-004", "A", output, self.KEY, {"valid_symbols": self.VALID})

    def test_perfect(self):
        r = judge.score_packet(self._pkt(j(self.KEY)))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_near_miss_component_earns_no_partial_credit(self):
        out = j({"components": [["ledgerline.core.a", "ledgerline.core.b"],
                                ["ledgerline.ingest.c", "ledgerline.core.e"]],
                 "component_count": 2})
        r = judge.score_packet(self._pkt(out))
        self.assertAlmostEqual(r["quality_score"], 0.5, places=4)
        self.assertGreater(r["quality_score"], 0.0)
        self.assertLess(r["quality_score"], 1.0)
        self.assertFalse(r["task_success"])

    def test_zero_tolerance_fabricated_member_fails(self):
        out = j({"components": [["ledgerline.core.a", "ledgerline.core.b"],
                                ["ledgerline.ingest.c", "ledgerline.ingest.d"],
                                ["ledgerline.ghost.x", "ledgerline.ghost.y"]],
                 "component_count": 3})
        r = judge.score_packet(self._pkt(out))
        self.assertGreater(r["quality_score"], 0.5)
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])

    def test_singleton_component_fails_outright_without_zero_tolerance_flag(self):
        out = j({"components": [["ledgerline.core.a", "ledgerline.core.b"],
                                ["ledgerline.ingest.c", "ledgerline.ingest.d"],
                                ["ledgerline.core.e"]],
                 "component_count": 3})
        r = judge.score_packet(self._pkt(out))
        self.assertFalse(r["task_success"])
        self.assertFalse(r["zero_tolerance_breached"])
        self.assertEqual(r["failure_reason"], "component_with_fewer_than_two_members")

    def test_empty_output(self):
        r = judge.score_packet(self._pkt("   "))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])


# ===========================================================================
# workload B
# ===========================================================================

class TestWorkloadB001(unittest.TestCase):

    def _pkt(self, output):
        return packet("B-001", "B", output, B1_KEY)

    def test_perfect(self):
        r = judge.score_packet(self._pkt(j(B1_KEY)))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_one_wrong_field_still_meets_the_floor(self):
        out = dict(B1_KEY)
        out["field_01"] = "wrong"
        r = judge.score_packet(self._pkt(j(out)))
        self.assertAlmostEqual(r["quality_score"], round(35 / 36, 4), places=4)
        self.assertTrue(r["task_success"])

    def test_partial_answer_between_zero_and_one_fails_the_floor(self):
        out = {k: (v if i % 2 == 0 else "wrong") for i, (k, v) in enumerate(B1_KEY.items())}
        r = judge.score_packet(self._pkt(j(out)))
        self.assertGreater(r["quality_score"], 0.0)
        self.assertLess(r["quality_score"], 1.0)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "below_quality_floor")

    def test_wrong_json_type_is_a_mismatch(self):
        out = dict(B1_KEY)
        out["initial_term_months"] = "36"      # string, not number
        r = judge.score_packet(self._pkt(j(out)))
        self.assertIn("initial_term_months", r["detail"]["mismatched_fields"])

    def test_numeric_thirty_equals_thirty_point_zero(self):
        out = dict(B1_KEY)
        out["initial_term_months"] = 36.0
        r = judge.score_packet(self._pkt(j(out)))
        self.assertEqual(r["quality_score"], 1.0)

    def test_two_missing_keys_fail_outright(self):
        out = dict(B1_KEY)
        del out["field_01"]
        del out["field_02"]
        r = judge.score_packet(self._pkt(j(out)))
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "more_than_one_required_key_missing")

    def test_garbage(self):
        r = judge.score_packet(self._pkt("no."))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])


class TestWorkloadB002(unittest.TestCase):

    def _pkt(self, output, ev=None):
        return packet("B-002", "B", output, B2_KEY, ev if ev is not None else B2_EVIDENCE)

    def test_perfect(self):
        r = judge.score_packet(self._pkt(j(B2_KEY)))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_partial(self):
        out = json.loads(j(B2_KEY))
        out["incidents"][0]["duration_minutes"] = 90
        out["incidents"][1]["root_cause_code"] = "RC-NET"
        r = judge.score_packet(self._pkt(j(out)))
        self.assertAlmostEqual(r["quality_score"], round(12 / 14, 4), places=4)
        self.assertGreater(r["quality_score"], 0.0)
        self.assertLess(r["quality_score"], 1.0)
        self.assertFalse(r["task_success"])

    def test_empty(self):
        r = judge.score_packet(self._pkt(""))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertEqual(r["failure_reason"], "empty_output")

    def test_zero_tolerance_fabricated_incident_fails_a_high_scoring_answer(self):
        out = json.loads(j(B2_KEY))
        out["incidents"].append({
            "incident_id": "INC-2031-999", "service": "kestrel-billing",
            "start_utc": "2031-09-09T00:00:00Z", "duration_minutes": 10,
            "final_severity": "S2", "root_cause_code": "RC-APP",
            "customer_impacting": False})
        out["count"] = 3
        r = judge.score_packet(self._pkt(j(out)))
        self.assertGreaterEqual(r["quality_score"], 0.6)
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["failure_reason"], "zero_tolerance:fabricated_record_id")
        self.assertIn("INC-2031-999", r["detail"]["fabricated_ids"])


# ===========================================================================
# workload C
# ===========================================================================

class TestWorkloadC(unittest.TestCase):

    PERFECT = {
        "flags": [
            {"flag": "edge_cache_v2", "introduced_in": "2.2", "removed_in": "2.6",
             "sources": ["release_notes_kestrel_2_2.md", "release_notes_kestrel_2_6.md"]},
            {"flag": "vector_index", "introduced_in": "2.4", "removed_in": None,
             "sources": ["errata_kestrel_2024_03.md"]},
        ],
        "count": 2,
    }

    def test_perfect(self):
        r = judge.score_packet(c1_packet(j(self.PERFECT)))
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_partial_coverage_with_full_traceability(self):
        out = json.loads(j(self.PERFECT))
        out["flags"][0]["removed_in"] = None            # wrong, but honestly cited
        out["flags"][0]["sources"] = ["release_notes_kestrel_2_2.md"]
        r = judge.score_packet(c1_packet(j(out)))
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertAlmostEqual(r["quality_score"], round(5 / 6, 4), places=4)
        self.assertGreater(r["quality_score"], 0.0)
        self.assertLess(r["quality_score"], 1.0)
        # 5/6 = 0.8333 >= 0.90 * 1.0? no -> fails the conservative floor
        self.assertFalse(r["task_success"])

    def test_partial_passes_against_a_supplied_baseline(self):
        out = json.loads(j(self.PERFECT))
        out["flags"][0]["removed_in"] = None
        out["flags"][0]["sources"] = ["release_notes_kestrel_2_2.md"]
        r = judge.score_packet(c1_packet(j(out), {"baseline_reference_quality": 0.85}))
        self.assertTrue(r["task_success"])

    def test_empty_output(self):
        r = judge.score_packet(c1_packet(""))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])

    def test_zero_tolerance_untraceable_citation_fails_a_perfect_table(self):
        """THE case: every value right, one citation to a file that does not
        state it.  coverage == 1.0, traceability < 1.0, task fails."""
        out = json.loads(j(self.PERFECT))
        out["flags"][1]["sources"] = ["forum_thread_0007.md"]
        r = judge.score_packet(c1_packet(j(out)))
        self.assertEqual(r["quality_score"], 1.0, "coverage is untouched")
        self.assertLess(r["detail"]["traceability"], 1.0)
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["failure_reason"],
                         "zero_tolerance:workload_C_100_percent_traceable")

    def test_empty_sources_list_is_one_unsupported_citation(self):
        out = json.loads(j(self.PERFECT))
        out["flags"][1]["sources"] = []
        r = judge.score_packet(c1_packet(j(out)))
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertTrue(any(u["why"] == "empty_sources"
                            for u in r["detail"]["unsupported_citations"]))

    def test_cited_file_not_in_corpus_fails(self):
        out = json.loads(j(self.PERFECT))
        out["flags"][0]["sources"] = ["release_notes_kestrel_9_9.md"]
        r = judge.score_packet(c1_packet(j(out)))
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertIn("release_notes_kestrel_9_9.md",
                      r["detail"]["cited_files_not_in_corpus"])


# ===========================================================================
# workload D
# ===========================================================================

class TestWorkloadD(unittest.TestCase):

    def _pkt(self, answer, calls, ev_extra=None):
        ev = {"tool_calls": calls}
        ev.update(ev_extra or {})
        out = answer if isinstance(answer, str) else j(answer)
        return packet("D-001", "D", out, D1_KEY, ev)

    def test_perfect(self):
        r = judge.score_packet(self._pkt(D1_GOOD_ANSWER, D1_GOOD_CALLS))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])
        self.assertEqual(r["detail"]["wrong_tool_invocations"], 0)

    def test_wrong_answer_field_scores_zero(self):
        bad = dict(D1_GOOD_ANSWER, team="Billing Platform (legacy)")
        r = judge.score_packet(self._pkt(bad, D1_GOOD_CALLS))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "answer_field_mismatch")

    def test_empty_output_scores_zero(self):
        r = judge.score_packet(self._pkt("", D1_GOOD_CALLS))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "empty_output")

    def test_garbage_output_scores_zero(self):
        r = judge.score_packet(self._pkt("The engineer was Imogen.", D1_GOOD_CALLS))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertEqual(r["failure_reason"], "unparseable_output")

    def test_zero_tolerance_wrong_tool_fails_a_correct_answer(self):
        """THE case: the answer is exactly right, but a sibling in a contested
        family was called once 'only to look'.  It fails."""
        calls = list(D1_GOOD_CALLS) + [
            {"tool": "rota.get_published_rotation", "family": "oncall-resolution"}]
        r = judge.score_packet(self._pkt(D1_GOOD_ANSWER, calls))
        self.assertTrue(r["detail"]["answer_correct"])
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["failure_reason"], "zero_tolerance:wrong_tool_invocation")

    def test_catalog_and_meta_calls_never_count(self):
        calls = [{"tool": "catalog.list_tools", "family": "meta"},
                 {"tool": "catalog.describe_tool", "family": "meta"}] + D1_GOOD_CALLS
        r = judge.score_packet(self._pkt(D1_GOOD_ANSWER, calls))
        self.assertTrue(r["task_success"])

    def test_uncontested_family_call_is_extraneous_not_wrong(self):
        calls = list(D1_GOOD_CALLS) + [{"tool": "metrics.get_series", "family": "metrics"}]
        r = judge.score_packet(self._pkt(D1_GOOD_ANSWER, calls))
        self.assertTrue(r["task_success"])
        self.assertEqual(r["detail"]["extraneous_calls"], 1)

    def test_no_tool_calls_at_all_fails(self):
        r = judge.score_packet(self._pkt(D1_GOOD_ANSWER, []))
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "answered_without_calling_any_tool")

    def test_missing_tool_audit_cannot_pass(self):
        p = packet("D-001", "D", j(D1_GOOD_ANSWER), D1_KEY, {})
        r = judge.score_packet(p)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "required_evidence_missing:tool_calls")

    def test_fixture_read_fails(self):
        r = judge.score_packet(self._pkt(D1_GOOD_ANSWER, D1_GOOD_CALLS,
                                         {"fixture_reads": ["fixtures/responses.json"]}))
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "fixtures_read_tool_selection_unmeasurable")

    def test_extra_key_breaks_exact_key_set(self):
        bad = dict(D1_GOOD_ANSWER, confidence="high")
        r = judge.score_packet(self._pkt(bad, D1_GOOD_CALLS))
        self.assertFalse(r["task_success"])
        self.assertEqual(r["failure_reason"], "required_key_set_not_exact")


# ===========================================================================
# workload E
# ===========================================================================

class TestWorkloadE001(unittest.TestCase):

    def _pkt(self, output):
        return packet("E-001", "E", output, E1_KEY, E1_EVIDENCE)

    def test_perfect(self):
        r = judge.score_packet(self._pkt(e1_output(E1_KEY)))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])
        self.assertEqual(r["detail"]["constraint_violations"], 0)

    def test_partial(self):
        out = json.loads(j(E1_KEY))
        out["requisition_lead_time_days"] = 30
        out["approvers_required"] = 2
        r = judge.score_packet(self._pkt(e1_output(out)))
        self.assertGreater(r["quality_score"], 0.0)
        self.assertLess(r["quality_score"], 1.0)
        self.assertEqual(r["detail"]["constraint_violations"], 0)

    def test_empty(self):
        r = judge.score_packet(self._pkt({"turns": [], "final_reply": ""}))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])

    def test_zero_tolerance_excluded_vendor_part_in_an_intermediate_turn(self):
        """THE case: the final table is perfect, but at turn 7 the run proposed
        the excluded vendor's part.  Completion 1.0, task fails."""
        turns = [(7, 'Proposed line: {"part_id": "APP-2U-EDGE-01", "qty": 4}')]
        r = judge.score_packet(self._pkt(e1_output(E1_KEY, turns)))
        self.assertEqual(r["quality_score"], 1.0, "completion is untouched")
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertTrue(any(v["code"] == "V3_excluded_vendor_part"
                            for v in r["detail"]["violations"]))

    def test_zero_tolerance_fabricated_part_id(self):
        out = json.loads(j(E1_KEY))
        out["bom"][0]["part_id"] = "APP-2U-EDGE-77"
        r = judge.score_packet(self._pkt(e1_output(out)))
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertTrue(any(v["code"] == "V1_part_id_not_in_catalog"
                            for v in r["detail"]["violations"]))

    def test_zero_tolerance_money_format(self):
        out = json.loads(j(E1_KEY))
        out["grand_total_eur"] = "72,677.00"
        r = judge.score_packet(self._pkt(e1_output(out)))
        self.assertFalse(r["task_success"])
        self.assertTrue(any(v["code"] == "V2_money_format"
                            for v in r["detail"]["violations"]))

    def test_zero_tolerance_unsorted_bom(self):
        out = json.loads(j(E1_KEY))
        out["bom"] = list(reversed(out["bom"]))
        r = judge.score_packet(self._pkt(e1_output(out)))
        self.assertFalse(r["task_success"])
        self.assertTrue(any(v["code"] == "V4_bom_not_sorted"
                            for v in r["detail"]["violations"]))

    def test_zero_tolerance_silent_trim_to_fit_cap(self):
        out = json.loads(j(E1_KEY))
        out["bom"] = out["bom"][:1]
        out["within_cap"] = True
        out["amount_over_cap_eur"] = "0.00"
        r = judge.score_packet(self._pkt(e1_output(out)))
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        codes = {v["code"] for v in r["detail"]["violations"]}
        self.assertIn("V5_rows_dropped", codes)
        self.assertIn("V6_within_cap_misreported", codes)

    def test_naming_the_vendor_in_prose_is_not_a_violation(self):
        turns = [(7, "Halberd Manufacturing is excluded, so I am not proposing "
                     "their edge appliance.")]
        r = judge.score_packet(self._pkt(e1_output(E1_KEY, turns)))
        self.assertTrue(r["task_success"])
        self.assertEqual(r["detail"]["constraint_violations"], 0)


class TestWorkloadE002(unittest.TestCase):

    KEY = {
        "steps": [
            {"step_id": "MIG-001", "action": "migrate", "service": "kestrel-search",
             "wave": 1, "owner_team": "Search", "start_utc": "2032-05-10T22:00:00Z"},
            {"step_id": "MIG-002", "action": "verify", "service": "kestrel-search",
             "wave": 1, "owner_team": "Search", "start_utc": "2032-05-10T22:45:00Z"},
        ],
        "step_count": 2,
        "total_duration_minutes": 90,
    }

    def _pkt(self, final, turns=None):
        out = {"turns": [{"turn": t, "text": x} for t, x in (turns or [])],
               "final_reply": final if isinstance(final, str) else j(final)}
        return packet("E-002", "E", out, self.KEY, {"turn_count": 16})

    def test_perfect(self):
        r = judge.score_packet(self._pkt(self.KEY))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_partial(self):
        out = json.loads(j(self.KEY))
        out["steps"][1]["owner_team"] = "Platform"
        out["total_duration_minutes"] = 45
        r = judge.score_packet(self._pkt(out))
        self.assertGreater(r["quality_score"], 0.0)
        self.assertLess(r["quality_score"], 1.0)

    def test_garbage(self):
        r = judge.score_packet(self._pkt("here is the runbook, roughly"))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])

    def test_zero_tolerance_banned_word_in_an_intermediate_turn(self):
        """THE case: the runbook is perfect, but turn 8 said 'just'."""
        turns = [(8, "kestrel-search lands in wave 1 because it just has no "
                     "in-scope dependencies.")]
        r = judge.score_packet(self._pkt(self.KEY, turns))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertTrue(any(v["code"] == "V2_banned_word"
                            for v in r["detail"]["violations"]))

    def test_banned_word_before_turn_four_is_not_a_violation(self):
        turns = [(2, "Understood - I will just use that numbering.")]
        r = judge.score_packet(self._pkt(self.KEY, turns))
        self.assertTrue(r["task_success"])

    def test_adjust_and_justify_do_not_trip_the_word_check(self):
        turns = [(10, "I will adjust the schedule and justify each wave.")]
        r = judge.score_packet(self._pkt(self.KEY, turns))
        self.assertEqual(r["detail"]["constraint_violations"], 0)

    def test_zero_tolerance_out_of_scope_service_as_a_step(self):
        out = json.loads(j(self.KEY))
        out["steps"][1]["service"] = "kestrel-vault"
        r = judge.score_packet(self._pkt(out))
        self.assertFalse(r["task_success"])
        self.assertTrue(any(v["code"] == "V1_out_of_scope_service_as_step"
                            for v in r["detail"]["violations"]))

    def test_confirming_the_service_is_absent_is_not_a_violation(self):
        turns = [(13, "Confirmed: no step references kestrel-vault, which is "
                      "out of scope.")]
        r = judge.score_packet(self._pkt(self.KEY, turns))
        self.assertEqual(r["detail"]["constraint_violations"], 0)
        self.assertTrue(r["task_success"])

    def test_zero_tolerance_step_id_gap(self):
        out = json.loads(j(self.KEY))
        out["steps"][1]["step_id"] = "MIG-004"
        r = judge.score_packet(self._pkt(out))
        self.assertFalse(r["task_success"])
        self.assertTrue(any(v["code"] == "V3_step_id_sequence"
                            for v in r["detail"]["violations"]))

    def test_zero_tolerance_non_utc_timestamp(self):
        out = json.loads(j(self.KEY))
        out["steps"][1]["start_utc"] = "2032-05-10T23:45:00+01:00"
        r = judge.score_packet(self._pkt(out))
        self.assertFalse(r["task_success"])
        self.assertTrue(any(v["code"] == "V5_timestamp_format"
                            for v in r["detail"]["violations"]))

    def test_cells_per_step_is_six(self):
        r = judge.score_packet(self._pkt(self.KEY))
        self.assertEqual(r["detail"]["cells_per_step"], 6)


class TestWorkloadE003(unittest.TestCase):

    def _pkt(self, final, turns=None):
        out = {"turns": [{"turn": t, "text": x} for t, x in (turns or [])],
               "final_reply": final if isinstance(final, str) else j(final)}
        return packet("E-003", "E", out, E3_KEY, E3_EVIDENCE)

    def test_perfect(self):
        r = judge.score_packet(self._pkt(E3_KEY))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_partial(self):
        out = json.loads(j(E3_KEY))
        out["assignments"][1]["reason_if_unfilled"] = "no_night_qualified_person"
        r = judge.score_packet(self._pkt(out))
        self.assertGreater(r["quality_score"], 0.0)
        self.assertLess(r["quality_score"], 1.0)
        self.assertEqual(r["detail"]["constraint_violations"], 0)

    def test_empty(self):
        r = judge.score_packet(self._pkt(""))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertFalse(r["task_success"])

    def test_zero_tolerance_filling_a_shift_with_someone_on_leave(self):
        """THE case: the run fills SH-110 with PR-014, who went on leave at
        turn 12.  Every other cell is right."""
        out = json.loads(j(E3_KEY))
        out["assignments"][1] = {"shift_id": "SH-110",
                                 "assigned_person_id": "PR-014",
                                 "reason_if_unfilled": None}
        out["unfilled_count"] = 0
        r = judge.score_packet(self._pkt(out))
        self.assertGreater(r["quality_score"], 0.3)
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertTrue(any(v["code"] == "V3_on_leave_assigned"
                            for v in r["detail"]["violations"]))

    def test_zero_tolerance_invalid_unfilled_reason(self):
        out = json.loads(j(E3_KEY))
        out["assignments"][1]["reason_if_unfilled"] = "nobody was free, sorry"
        r = judge.score_packet(self._pkt(out))
        self.assertFalse(r["task_success"])
        self.assertTrue(any(v["code"] == "V6_invalid_unfilled_reason"
                            for v in r["detail"]["violations"]))

    def test_zero_tolerance_violation_in_an_intermediate_turn_only(self):
        turns = [(13, "Assigning SH-110 to PR-014 for the day pass.")]
        r = judge.score_packet(self._pkt(E3_KEY, turns))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertFalse(r["task_success"])
        self.assertTrue(r["zero_tolerance_breached"])

    def test_same_violation_twice_in_one_turn_counts_once(self):
        turns = [(13, "SH-110 -> PR-014\nSH-110 -> PR-014")]
        r = judge.score_packet(self._pkt(E3_KEY, turns))
        self.assertEqual(r["detail"]["constraint_violations"], 1)


# ===========================================================================
# cross-cutting behaviour
# ===========================================================================

class TestBlindIsolation(unittest.TestCase):

    def test_forbidden_keys_are_ignored_not_read(self):
        out = j({"reaching_functions": A1_KEY["reaching_functions"], "count": 5})
        p = packet("A-001", "A", out, A1_KEY, {"valid_symbols": A1_VALID})
        clean = judge.score_packet(dict(p))
        leaky = dict(p)
        leaky.update({"condition": "C5", "total_tokens": 41233,
                      "cost_usd": 0.91, "model": "some-model",
                      "candidate": "some-tool", "pricing_snapshot_id": "PS-2026-09-15"})
        dirty = judge.score_packet(leaky)
        self.assertEqual(clean["quality_score"], dirty["quality_score"])
        self.assertEqual(clean["task_success"], dirty["task_success"])
        self.assertEqual(
            dirty["detail"]["ignored_packet_keys"],
            ["candidate", "condition", "cost_usd", "model", "pricing_snapshot_id",
             "total_tokens"])
        self.assertIn("blind_warning", dirty["detail"])

    def test_scoring_is_deterministic(self):
        out = j({"reaching_functions": A1_KEY["reaching_functions"][:3], "count": 3})
        p = packet("A-001", "A", out, A1_KEY, {"valid_symbols": A1_VALID})
        first = judge.score_packet(json.loads(json.dumps(p)))
        for _ in range(5):
            again = judge.score_packet(json.loads(json.dumps(p)))
            self.assertEqual(json.dumps(first, sort_keys=True),
                             json.dumps(again, sort_keys=True))


class TestNeverRaises(unittest.TestCase):

    CASES = [
        {},
        {"task_id": "A-001"},
        {"task_id": "A-001", "workload": "A"},
        {"task_id": "Z-999", "workload": "Z", "model_output": "{}"},
        {"task_id": "A-001", "workload": "A", "model_output": None,
         "answer_key": None, "required_evidence": None},
        {"task_id": "B-001", "workload": "B", "model_output": "[]", "answer_key": []},
        {"task_id": "C-001", "workload": "C", "model_output": "{}", "answer_key": "nope"},
        {"task_id": "D-002", "workload": "D", "model_output": 17, "answer_key": {}},
        {"task_id": "E-001", "workload": "E", "model_output": {"turns": "not a list"},
         "answer_key": {}},
        {"task_id": "E-003", "workload": "E", "model_output": [1, 2, 3], "answer_key": []},
        {"task_id": "A-004", "workload": "A",
         "model_output": '{"components": "nope", "component_count": 1}',
         "answer_key": {"components": []}},
        {"task_id": "B-002", "workload": "B",
         "model_output": '{"incidents": [null, 7], "count": 2}',
         "answer_key": B2_KEY, "required_evidence": B2_EVIDENCE},
    ]

    def test_every_malformed_packet_scores_zero_without_raising(self):
        for case in self.CASES:
            with self.subTest(case=case.get("task_id")):
                r = judge.score_packet(case)
                self.assertIsInstance(r, dict)
                for k in ("packet_id", "quality_score", "task_success",
                          "failure_reason", "zero_tolerance_breached", "detail"):
                    self.assertIn(k, r)
                self.assertFalse(r["task_success"])
                self.assertIsNotNone(r["failure_reason"])
                self.assertNotEqual(r["failure_reason"], "judge_internal_error")

    def test_non_dict_packet(self):
        for bad in (None, "x", 5, [1]):
            r = judge.score_packet(bad)
            self.assertFalse(r["task_success"])

    def test_deeply_nested_garbage_model_output(self):
        p = packet("A-001", "A", {"a": {"b": ["c"] * 50}}, A1_KEY,
                   {"valid_symbols": A1_VALID})
        r = judge.score_packet(p)
        self.assertFalse(r["task_success"])


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="judge-cli-")
        self.pin = os.path.join(self.tmp, "packets")
        self.pout = os.path.join(self.tmp, "scores")
        os.makedirs(self.pin)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, obj):
        with open(os.path.join(self.pin, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh)

    def test_directory_round_trip(self):
        good = packet("A-001", "A",
                      j({"reaching_functions": A1_KEY["reaching_functions"], "count": 5}),
                      A1_KEY, {"valid_symbols": A1_VALID})
        good["packet_id"] = "pkt-good"
        bad = packet("A-001", "A", "", A1_KEY, {"valid_symbols": A1_VALID})
        bad["packet_id"] = "pkt-bad"
        self._write("a.json", good)
        self._write("b.json", bad)
        with open(os.path.join(self.pin, "c.json"), "w", encoding="utf-8") as fh:
            fh.write("{ not json")

        results = judge.score_directory(self.pin, self.pout, quiet=True)
        self.assertEqual(len(results), 3)
        by_id = {r["packet_id"]: r for r in results}
        self.assertTrue(by_id["pkt-good"]["task_success"])
        self.assertFalse(by_id["pkt-bad"]["task_success"])
        self.assertEqual(by_id["c"]["failure_reason"], "packet_unreadable")
        self.assertTrue(os.path.exists(os.path.join(self.pout, "pkt-good.json")))
        with open(os.path.join(self.pout, "_SUMMARY.json"), encoding="utf-8") as fh:
            summary = json.load(fh)
        self.assertEqual(summary["packets_scored"], 3)
        self.assertEqual(summary["task_success_count"], 1)

    def test_main_returns_two_for_missing_dir(self):
        with redirect_stderr(io.StringIO()):
            rc = judge.main(["--packets", os.path.join(self.tmp, "nope"),
                             "--scores", self.pout, "--quiet"])
        self.assertEqual(rc, 2)


class TestRounding(unittest.TestCase):

    def test_four_decimal_places_half_away_from_zero(self):
        self.assertEqual(judge._round4(1 / 3), 0.3333)
        self.assertEqual(judge._round4(2 / 3), 0.6667)
        self.assertEqual(judge._round4(0.00005), 0.0001)
        self.assertEqual(judge._round4(float("nan")), 0.0)


if __name__ == "__main__":
    unittest.main()


# ===========================================================================
# real answer-key shapes
#
# The Answer Key Builder is an independent seat and its keys carry derivation
# provenance alongside the payload.  These cases pin the shapes the scorer must
# accept.  The round-trip class is skipped when the keys are not present, so
# the suite never blocks on another seat.
# ===========================================================================

KEYS_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "tasks", "TASK_SET_v1.0.0", "answer_keys"))

CORPUS_E = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "tasks", "TASK_SET_v1.0.0", "corpora", "workflow_e"))


def _halberd_part_ids():
    """The excluded vendor's part ids, read from the frozen catalogue."""
    import csv
    with open(os.path.join(CORPUS_E, "parts_catalog.csv"), encoding="utf-8") as fh:
        return [r["part_id"] for r in csv.DictReader(fh)
                if "Halberd" in (r.get("vendor") or "")]


class TestDeliveredKeyShapes(unittest.TestCase):
    """Synthetic fixtures mirroring the delivered keys' structure."""

    def test_b001_terms_nested_under_contract_terms(self):
        terms = {"field_%02d" % i: "v%02d" % i for i in range(1, 37)}
        key = {"task_id": "B-001", "derived_by": "answer-key-builder",
               "derivation_method": "…", "derivation_script": "scripts/derive_B.py",
               "as_of_date": "2031-11-30", "contract_terms": terms}
        r = judge.score_packet(packet("B-001", "B", j(terms), key))
        self.assertEqual(r["detail"]["field_source"], "contract_terms")
        self.assertEqual(r["detail"]["field_count"], 36)
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_b001_derivation_metadata_is_never_a_scored_field(self):
        terms = {"field_%02d" % i: "v%02d" % i for i in range(1, 37)}
        key = dict(terms, task_id="B-001", derived_by="answer-key-builder",
                   derivation_method="…", derivation_script="s.py")
        r = judge.score_packet(packet("B-001", "B", j(terms), key))
        self.assertEqual(r["detail"]["field_source"], "top_level_minus_metadata")
        self.assertEqual(r["detail"]["field_count"], 36)
        self.assertEqual(r["quality_score"], 1.0)

    def test_c_per_record_citation_support(self):
        """The shape the v1.1.0 keys actually ship: a per-field map whose
        union equals `sources` by construction.  The withdrawn v1.0.0 shape -
        a curated `sources` beside a `non_authoritative_files_stating_the_same_*`
        list - is exactly what RT-04 rejected and is not fixtured here."""
        key = {"task_id": "C-001", "derived_by": "answer-key-builder",
               "flags": [{"flag": "adaptive_shard_split", "introduced_in": "2.2",
                          "removed_in": None,
                          "sources": ["release_notes_kestrel_2_2.md"],
                          "citation_support": {
                              "flag": ["release_notes_kestrel_2_2.md"],
                              "introduced_in": ["release_notes_kestrel_2_2.md"],
                              "removed_in": []}}],
               "count": 1}
        ev = {"corpus_files": ["release_notes_kestrel_2_2.md", "forum_thread_4111.md"]}
        good = {"flags": [{"flag": "adaptive_shard_split", "introduced_in": "2.2",
                          "removed_in": None,
                          "sources": ["release_notes_kestrel_2_2.md"]}], "count": 1}
        for mv in ("1.0.0", "1.1.0"):
            with self.subTest(v=mv):
                e = dict(ev, **hashes("C-001")) if mv == "1.1.0" else ev
                r = judge.score_packet(packet("C-001", "C", j(good), key, e,
                                              methodology_version=mv))
                self.assertEqual(r["detail"]["traceability"], 1.0)
                self.assertEqual(r["quality_score"], 1.0)
                self.assertTrue(r["task_success"], r["failure_reason"])

        # a forum thread that states the same value is still not a governing
        # source, under either version
        bad = json.loads(j(good))
        bad["flags"][0]["sources"] = ["forum_thread_4111.md"]
        for mv in ("1.0.0", "1.1.0"):
            with self.subTest(v=mv, case="non_governing"):
                e = dict(ev, **hashes("C-001")) if mv == "1.1.0" else ev
                r = judge.score_packet(packet("C-001", "C", j(bad), key, e,
                                              methodology_version=mv))
                self.assertLess(r["detail"]["traceability"], 1.0)
                self.assertTrue(r["zero_tolerance_breached"])

    def test_c002_legacy_per_award_support_has_no_field_breakdown(self):
        """The withdrawn v1.0.0 C-002 shape, kept only as a v1.0.0 replay
        case: no per-field breakdown, so the record-level fallback applies."""
        key = {"projects": [{
            "project": "Project Halyard", "total_awarded_eur": 621500,
            "awards_included": ["GA-0001"], "awards_excluded": [],
            "sources": ["bulletin_bul_2031_01.md", "correction_CORR-002.md"],
            "citation_support": {"per_award": {"GA-0001": {
                "amount_eur": 88500, "stated_by": "correction_CORR-002.md",
                "listed_in_bulletin": "bulletin_bul_2031_01.md"}},
                "note": "no single file states total_awarded_eur"}}],
            "count": 1}
        ev = {"corpus_files": ["bulletin_bul_2031_01.md", "correction_CORR-002.md",
                               "forum_thread_4111.md"],
              "document_award_ids": ["GA-0001"]}
        out = {"projects": [{"project": "Project Halyard", "total_awarded_eur": 621500,
                             "awards_included": ["GA-0001"], "awards_excluded": [],
                             "sources": ["bulletin_bul_2031_01.md",
                                         "correction_CORR-002.md"]}], "count": 1}
        r = judge.score_packet(packet("C-002", "C", j(out), key, ev))
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertTrue(r["task_success"])

        out["projects"][0]["sources"] = ["forum_thread_4111.md"]
        r = judge.score_packet(packet("C-002", "C", j(out), key, ev))
        self.assertLess(r["detail"]["traceability"], 1.0)
        self.assertTrue(r["zero_tolerance_breached"])

    def test_d_answer_nested_under_answer(self):
        key = {"task_id": "D-001", "contested_families": ["oncall-resolution",
                                                          "person-resolution"],
               "required_tools": ["rota.get_effective_oncall",
                                  "directory.get_person_by_handle"],
               "answer": {"engineer_full_name": "Adaeze M. Okonjo",
                          "team": "Billing Platform", "escalation_tier": 2},
               "derivation_diagnostics": {"template_handle_before_overrides": "t.ferreira"}}
        ev = {"tool_calls": [
            {"tool": "rota.get_effective_oncall", "family": "oncall-resolution"},
            {"tool": "directory.get_person_by_handle", "family": "person-resolution"}]}
        r = judge.score_packet(packet("D-001", "D", j(key["answer"]), key, ev))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_d_diagnostics_decoy_is_not_the_answer(self):
        key = {"required_tools": ["rota.get_effective_oncall",
                                  "directory.get_person_by_handle"],
               "answer": {"engineer_full_name": "Adaeze M. Okonjo",
                          "team": "Billing Platform", "escalation_tier": 2},
               "derivation_diagnostics": {"template_handle_before_overrides": "t.ferreira"}}
        ev = {"tool_calls": [{"tool": "rota.get_published_rotation",
                              "family": "oncall-resolution"}]}
        bad = {"engineer_full_name": "Tomas Ferreira", "team": "Billing Platform",
               "escalation_tier": 2}
        r = judge.score_packet(packet("D-001", "D", j(bad), key, ev))
        self.assertEqual(r["quality_score"], 0.0)
        self.assertTrue(r["zero_tolerance_breached"])


@unittest.skipUnless(os.path.isdir(KEYS_DIR) and
                     os.path.exists(os.path.join(KEYS_DIR, "A-001.json")),
                     "answer keys not present (built by an independent seat)")
class TestRealAnswerKeyRoundTrip(unittest.TestCase):
    """Score each real key's own payload as if it were the model output.

    A key that scores anything but 1.0 against itself means the scorer and the
    Answer Key Builder disagree about the key's shape.
    """

    @staticmethod
    def _load(task_id):
        with open(os.path.join(KEYS_DIR, task_id + ".json"), encoding="utf-8") as fh:
            return json.load(fh)

    def _roundtrip(self, task_id, payload_fn, evidence_fn):
        key = self._load(task_id)
        out = payload_fn(key)
        ev = evidence_fn(key)
        r = judge.score_packet(packet(task_id, task_id[0], j(out), key, ev))
        self.assertEqual(r["quality_score"], 1.0,
                         "%s scored %s against its own key: %s"
                         % (task_id, r["quality_score"], r["failure_reason"]))
        self.assertTrue(r["task_success"],
                        "%s: %s / %s" % (task_id, r["failure_reason"],
                                         json.dumps(r["detail"])[:400]))
        self.assertFalse(r["zero_tolerance_breached"])

    def test_a_tasks(self):
        fields = {"A-001": "reaching_functions", "A-002": "unreferenced_functions",
                  "A-003": "retry_decorated_reaching_transient"}
        for tid, field in fields.items():
            with self.subTest(task=tid):
                self._roundtrip(
                    tid,
                    lambda k, f=field: {f: k[f], "count": k["count"]},
                    lambda k, f=field: {"valid_symbols": k[f]})

    def test_a004(self):
        self._roundtrip(
            "A-004",
            lambda k: {"components": k["components"],
                       "component_count": k["component_count"]},
            lambda k: {"valid_symbols": [m for c in k["components"] for m in c]})

    def test_b001(self):
        self._roundtrip("B-001", lambda k: k["contract_terms"], lambda k: {})

    def test_b_record_tasks(self):
        for tid, arr, idf in (("B-002", "incidents", "incident_id"),
                              ("B-003", "requirements", "req_id")):
            with self.subTest(task=tid):
                self._roundtrip(
                    tid,
                    lambda k, a=arr: {a: k[a], "count": k["count"]},
                    lambda k, a=arr, i=idf: {
                        ("document_incident_ids" if i == "incident_id"
                         else "document_req_ids"): [r[i] for r in k[a]]})

    def test_c_tasks(self):
        arrays = {"C-001": "flags", "C-002": "projects", "C-003": "plugins"}
        scored = {"C-001": ("flag", "introduced_in", "removed_in"),
                  "C-002": ("project", "total_awarded_eur", "awards_included",
                            "awards_excluded"),
                  "C-003": ("plugin_id", "min_kestrel_version",
                            "governing_source_tier", "contradicted_by")}

        def payload(k, a, cells):
            rows = []
            for rec in k[a]:
                row = {c: rec[c] for c in cells if c in rec}
                row["sources"] = rec.get("sources", [])
                rows.append(row)
            return {a: rows, "count": k["count"]}

        def evidence(k, a):
            files = set()
            for rec in k[a]:
                files |= judge._strings_in(rec.get("sources"))
                files |= judge._strings_in(rec.get("citation_support"))
                files |= judge._strings_in(rec.get("contradicted_by"))
            ev = {"corpus_files": sorted(f for f in files if f.endswith((".md", ".csv")))}
            if a == "projects":
                ids = set()
                for rec in k[a]:
                    ids |= set(rec.get("awards_included", []))
                    ids |= set(rec.get("awards_excluded", []))
                ev["document_award_ids"] = sorted(ids)
            if a == "plugins":
                ev["registry_plugin_ids"] = [r["plugin_id"] for r in k[a]]
            return ev

        for tid, arr in arrays.items():
            with self.subTest(task=tid):
                self._roundtrip(tid,
                                lambda k, a=arr, c=scored[tid]: payload(k, a, c),
                                lambda k, a=arr: evidence(k, a))

    def test_d_tasks(self):
        for tid in ("D-001", "D-002", "D-003", "D-004"):
            with self.subTest(task=tid):
                self._roundtrip(
                    tid,
                    lambda k: k["answer"],
                    lambda k: {"tool_calls": [
                        {"tool": c["tool"], "family": c["family"]}
                        for c in k.get("tool_calls_made_by_this_derivation", [])]})

    def test_e001(self):
        key = self._load("E-001")
        out = {k: key[k] for k in ("bom", "hardware_subtotal_eur",
                                   "service_subtotal_eur", "freight_eur",
                                   "contingency_eur", "grand_total_eur",
                                   "within_cap", "amount_over_cap_eur",
                                   "requisition_lead_time_days",
                                   "approvers_required")}
        # Both lists are mandatory AND must be non-empty (RT-02): the frozen
        # `parts_catalog.csv` holds 24 parts, 4 of them Halberd
        # Manufacturing's, so an empty list is a broken evidence producer, not
        # a corpus with no excluded vendor.
        ev = {"turn_count": 18,
              "catalog_part_ids": [r["part_id"] for r in key["bom"]],
              "halberd_part_ids": _halberd_part_ids()}
        r = judge.score_packet(packet("E-001", "E", j(out), key, ev))
        self.assertEqual(r["quality_score"], 1.0, r["failure_reason"])
        self.assertTrue(r["task_success"], json.dumps(r["detail"])[:400])

    def test_e002(self):
        key = self._load("E-002")
        out = {"steps": key["steps"], "step_count": key["step_count"],
               "total_duration_minutes": key["total_duration_minutes"]}
        r = judge.score_packet(packet("E-002", "E", j(out), key, {"turn_count": 16}))
        self.assertEqual(r["quality_score"], 1.0, r["failure_reason"])
        self.assertTrue(r["task_success"], json.dumps(r["detail"])[:400])

    def test_e003(self):
        key = self._load("E-003")
        out = {"assignments": key["assignments"],
               "unfilled_count": key["unfilled_count"]}
        # The roster and shift tables live in the corpus, not the key, so the
        # Runner supplies them.  Here they are synthesised consistently with
        # the key so the round trip exercises the shape, not the data.
        shifts, roster = {}, {}
        for row in key["assignments"]:
            shifts[row["shift_id"]] = {"site_id": "S", "window": "day",
                                       "required_certification": "C1"}
            pid = row.get("assigned_person_id")
            if pid:
                roster[pid] = {"site_id": "S", "certification": "C1",
                               "night_qualified": "yes", "status": "active",
                               "max_shifts": 9}
        ev = {"turn_count": 20, "shifts": shifts, "roster": roster}
        r = judge.score_packet(packet("E-003", "E", j(out), key, ev))
        self.assertEqual(r["quality_score"], 1.0, r["failure_reason"])
        self.assertTrue(r["task_success"], json.dumps(r["detail"])[:400])


class TestWorkloadEFailsClosed(unittest.TestCase):
    """A violation class that cannot be checked must not be reported as clean."""

    def test_e001_without_catalog_evidence_cannot_pass(self):
        p = packet("E-001", "E", e1_output(E1_KEY), E1_KEY, {"turn_count": 18})
        r = judge.score_packet(p)
        self.assertEqual(r["quality_score"], 1.0)
        self.assertFalse(r["task_success"])
        self.assertTrue(r["failure_reason"].startswith("required_evidence_missing:"))
        self.assertIn("catalog_part_ids", r["detail"]["violation_checks_unverifiable"])

    def test_e003_without_roster_evidence_cannot_pass(self):
        out = {"turns": [], "final_reply": j(E3_KEY)}
        r = judge.score_packet(packet("E-003", "E", out, E3_KEY, {"turn_count": 20}))
        self.assertEqual(r["quality_score"], 1.0)
        self.assertFalse(r["task_success"])
        self.assertIn("roster", r["detail"]["violation_checks_unverifiable"])

    def test_e002_needs_no_extra_evidence(self):
        key = TestWorkloadE002.KEY
        out = {"turns": [], "final_reply": j(key)}
        r = judge.score_packet(packet("E-002", "E", out, key, {"turn_count": 16}))
        self.assertTrue(r["task_success"])
        self.assertEqual(r["detail"]["violation_checks_unverifiable"], [])

    def test_a_real_violation_still_outranks_missing_evidence(self):
        out = json.loads(j(E1_KEY))
        out["grand_total_eur"] = "72,677.00"
        r = judge.score_packet(packet("E-001", "E", e1_output(out), E1_KEY,
                                      {"turn_count": 18}))
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["failure_reason"], "zero_tolerance:constraint_violation")


# ===========================================================================
# v1.1.0 — fixtures
#
# Everything below scores under METHODOLOGY v1.1.0.  The cases above replay
# v1.0.0 records and stay on the v1.0.0 path; both are exercised, and several
# cases below score the SAME packet under both versions precisely to show that
# the two paths now disagree where the change review says they must.
# ===========================================================================

# A-001, ten reported symbols of which five are the key: the "blanket answer"
# the Red Team measured at 0.6667 (P=0.5, R=1.0) without reading the corpus.
A1_VALID_10 = A1_KEY["reaching_functions"] + [
    "ledgerline.api.healthz.ping",
    "ledgerline.storage.raw.execute_raw_sql",
    "ledgerline.plugins.taxuk.apply_vat",
    "ledgerline.util.retry.retryable_v2",
    "ledgerline.cli.tools.dump_ledger",
]
A1_BLANKET = {"reaching_functions": A1_VALID_10, "count": len(A1_VALID_10)}
A1_PERFECT = {"reaching_functions": A1_KEY["reaching_functions"], "count": 5}


def a1_evidence(**extra):
    ev = {"valid_symbols": A1_VALID_10}
    ev.update(hashes("A-001"))
    ev.update(access_log("A-001"))
    ev.update(extra)
    return ev


def e_full(final_obj, turn_count, overrides=None, filler="noted."):
    """A complete transcript: every turn 1..turn_count-1 plus the final reply.

    The final reply is numbered `turn_count`, so the covered set is 1..N.
    """
    overrides = overrides or {}
    turns = [{"turn": i, "text": overrides.get(i, filler)}
             for i in range(1, turn_count)]
    return {"turns": turns,
            "final_reply": final_obj if isinstance(final_obj, str) else j(final_obj)}


E1_EV_11 = dict(E1_EVIDENCE)          # carries part_id_pattern on purpose


def e1_packet11(final_obj, overrides=None, evidence_extra=None, key=None):
    ev = dict(E1_EV_11)
    ev.update(evidence_extra or {})
    return packet11("E-001", "E", e_full(final_obj, 18, overrides),
                    key or E1_KEY, ev)


E2_KEY_11 = {
    "steps": [
        {"step_id": "MIG-001", "action": "drain", "service": "kestrel-billing",
         "wave": 1, "owner_team": "Billing Platform",
         "start_utc": "2032-05-10T22:00:00Z"},
        {"step_id": "MIG-002", "action": "cutover", "service": "kestrel-search",
         "wave": 1, "owner_team": "Search", "start_utc": "2032-05-10T23:00:00Z"},
    ],
    "step_count": 2,
    "total_duration_minutes": 120,
}


def e2_packet11(final_obj, overrides=None):
    return packet11("E-002", "E", e_full(final_obj, 16, overrides),
                    E2_KEY_11, {"turn_count": 16})


E3_SHIFTS_11 = {
    "SH-101": {"site_id": "SITE-FRA-1", "required_certification": "C2", "window": "day"},
    "SH-102": {"site_id": "SITE-FRA-1", "required_certification": "C2", "window": "night"},
    "SH-103": {"site_id": "SITE-FRA-1", "required_certification": "C1", "window": "day"},
    "SH-104": {"site_id": "SITE-FRA-1", "required_certification": "C1", "window": "day"},
    "SH-105": {"site_id": "SITE-FRA-1", "required_certification": "C1", "window": "day"},
    "SH-110": {"site_id": "SITE-FRA-1", "required_certification": "C2", "window": "day"},
}
E3_ROSTER_11 = {
    "PR-011": {"site_id": "SITE-FRA-1", "certification": "C2",
               "night_qualified": "no", "status": "available", "max_shifts": 2},
    "PR-012": {"site_id": "SITE-FRA-1", "certification": "C2",
               "night_qualified": "yes", "status": "available", "max_shifts": 1},
    "PR-013": {"site_id": "SITE-LIS-1", "certification": "C2",
               "night_qualified": "yes", "status": "available", "max_shifts": 2},
    "PR-014": {"site_id": "SITE-FRA-1", "certification": "C2",
               "night_qualified": "yes", "status": "available", "max_shifts": 2},
    "PR-015": {"site_id": "SITE-FRA-1", "certification": "C2",
               "night_qualified": "yes", "status": "on_leave", "max_shifts": 2},
    "PR-016": {"site_id": "SITE-FRA-1", "certification": "C1",
               "night_qualified": "no", "status": "available", "max_shifts": 2},
}
E3_KEY_11 = {
    "assignments": [
        {"shift_id": "SH-101", "assigned_person_id": "PR-011", "reason_if_unfilled": None},
        {"shift_id": "SH-110", "assigned_person_id": None,
         "reason_if_unfilled": "all_eligible_on_leave"},
    ],
    "unfilled_count": 1,
}


def e3_evidence11(**extra):
    ev = {"turn_count": 20, "shifts": E3_SHIFTS_11, "roster": E3_ROSTER_11,
          "additional_on_leave": {"PR-014": 12}}
    ev.update(extra)
    return ev


def e3_packet11(final_obj, overrides=None, evidence_extra=None):
    return packet11("E-003", "E", e_full(final_obj, 20, overrides),
                    E3_KEY_11, e3_evidence11(**(evidence_extra or {})))


# ===========================================================================
# section 13 — versioning and refusal
# ===========================================================================

class TestVersionGate(unittest.TestCase):
    """A packet whose methodology version cannot be resolved is refused."""

    def _bare(self, **over):
        p = packet("A-001", "A", j(A1_PERFECT), A1_KEY, a1_evidence())
        p.pop("methodology_version", None)
        p.update(over)
        return p

    def test_absent_version_is_refused_not_guessed(self):
        r = judge.score_packet(self._bare())
        self.assertEqual(r["failure_reason"], "methodology_version_absent")
        self.assertEqual(r["outcome"], "INVALID")
        self.assertFalse(r["task_success"])
        self.assertEqual(r["quality_score"], 0.0)

    def test_unrecognised_version_is_refused(self):
        for bad in ("0.9.0", "2.0.0", "1.1", "latest", 110):
            with self.subTest(version=bad):
                r = judge.score_packet(self._bare(methodology_version=bad))
                self.assertEqual(r["failure_reason"], "methodology_version_unsupported")
                self.assertEqual(r["outcome"], "INVALID")

    def test_a_perfect_answer_is_still_refused_without_a_version(self):
        """Refusal is not a quality judgement: a 1.0 answer is refused too."""
        r = judge.score_packet(self._bare())
        self.assertFalse(r["task_success"])
        self.assertNotIn("below_quality_floor", str(r["failure_reason"]))

    def test_version_may_come_from_the_answer_key(self):
        key = dict(A1_KEY, methodology_version="1.1.0")
        p = self._bare(answer_key=key)
        r = judge.score_packet(p)
        self.assertEqual(r["detail"]["methodology_version"], "1.1.0")
        self.assertTrue(r["task_success"])

    def test_leading_v_is_accepted(self):
        r = judge.score_packet(self._bare(methodology_version="v1.1.0"))
        self.assertEqual(r["detail"]["methodology_version"], "1.1.0")

    def test_both_supported_versions_score(self):
        for mv in ("1.0.0", "1.1.0"):
            with self.subTest(v=mv):
                r = judge.score_packet(self._bare(methodology_version=mv))
                self.assertIsNot(r["failure_reason"], "methodology_version_absent")
                self.assertEqual(r["detail"]["methodology_version"], mv)


# ===========================================================================
# CR-001-A acceptance tests A-1 .. A-6 (change review 001, verbatim)
# ===========================================================================

class TestAcceptanceCR001A(unittest.TestCase):
    """Absolute, answer-key-anchored floors.  No baseline may reach them."""

    def _score(self, baseline=None, mv="1.1.0", answer=None):
        ev = a1_evidence()
        if baseline is not None:
            ev["baseline_reference_quality"] = baseline
        return judge.score_packet(packet(
            "A-001", "A", j(answer or A1_BLANKET), A1_KEY, ev,
            methodology_version=mv))

    def test_A1_blanket_answer_no_baseline(self):
        r = self._score()
        self.assertEqual(r["quality_score"], 0.6667)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["outcome"], "FAIL_QUALITY")
        self.assertEqual(r["detail"]["floor"], 0.95)

    def test_A2_same_packet_with_a_c0_median_of_1_00(self):
        self.assertEqual(self._score(1.00)["quality_score"], 0.6667)
        self.assertFalse(self._score(1.00)["task_success"])

    def test_A3_same_packet_with_a_c0_median_of_0_70(self):
        """The case that PASSED under v1.0.0.  It must now fail."""
        r11 = self._score(0.70)
        self.assertEqual(r11["quality_score"], 0.6667)
        self.assertFalse(r11["task_success"], "v1.1.0 must fail the blanket answer")
        self.assertEqual(r11["failure_reason"], "below_quality_floor")
        self.assertEqual(r11["detail"]["floor"], 0.95)
        # ... and the v1.0.0 path still reproduces the old verdict, which is
        # what makes this a regression test rather than a restatement.
        r10 = self._score(0.70, mv="1.0.0")
        self.assertTrue(r10["task_success"])
        self.assertEqual(r10["detail"]["floor"], 0.665)

    def test_A4_identical_result_under_every_external_c0(self):
        seen = {json.dumps(self._score(b), sort_keys=True)
                for b in (None, 0.0, 0.4, 0.6667, 0.70, 0.95, 1.0)}
        # the only permitted difference is the ignored-key bookkeeping
        scores = {json.loads(x)["quality_score"] for x in seen}
        successes = {json.loads(x)["task_success"] for x in seen}
        self.assertEqual(scores, {0.6667})
        self.assertEqual(successes, {False})

    def test_A4_byte_identical_score_object_ignoring_bookkeeping(self):
        def core(r):
            r = json.loads(json.dumps(r))
            r["detail"].pop("ignored_packet_keys", None)
            r["detail"].pop("blind_warning", None)
            return json.dumps(r, sort_keys=True)
        self.assertEqual(core(self._score(0.10)), core(self._score(0.99)))

    def test_A5_baseline_is_ignored_and_recorded(self):
        r = self._score(0.70)
        self.assertIn("required_evidence.baseline_reference_quality",
                      r["detail"]["ignored_packet_keys"])
        self.assertFalse(r["detail"]["baseline_influenced_task_success"])
        self.assertNotIn("relative_floor_pending", r["detail"])

    def test_A6_missing_version_refused(self):
        p = packet("A-001", "A", j(A1_BLANKET), A1_KEY, a1_evidence())
        p.pop("methodology_version")
        self.assertEqual(judge.score_packet(p)["failure_reason"],
                         "methodology_version_absent")

    def test_absolute_floor_still_passes_a_correct_answer(self):
        r = self._score(answer=A1_PERFECT)
        self.assertEqual(r["quality_score"], 1.0)
        self.assertEqual(r["outcome"], "PASS")

    def test_workload_c_floor_is_absolute_too(self):
        good = c1_good()
        ev = dict(C1_EVIDENCE, baseline_reference_quality=0.10, **hashes("C-001"))
        key = dict(C1_KEY, citation_support=C1_SUPPORT)
        r = judge.score_packet(packet("C-001", "C", j(good), key, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["detail"]["floor"], 0.90)
        self.assertEqual(r["detail"]["floor_basis"],
                         "absolute_answer_key_methodology_v1.1.0_s6")

    def test_c_traceability_is_zero_tolerance_at_the_attempt_level(self):
        bad = {"flags": [dict(f, sources=["forum_thread_0007.md"])
                         for f in C1_KEY["flags"]], "count": 2}
        key = dict(C1_KEY, citation_support=C1_SUPPORT)
        r = judge.score_packet(packet("C-001", "C", j(bad), key,
                                      dict(C1_EVIDENCE, **hashes("C-001")),
                                      methodology_version="1.1.0"))
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["outcome"], "FAIL_QUALITY")


# ===========================================================================
# CR-001-B acceptance tests B-1 .. B-5
# ===========================================================================

class TestAcceptanceCR001B(unittest.TestCase):
    """Attempt / cell / aggregate.

    B-1, B-2 and B-3 are CELL-level assertions and the cell is the
    Runner/Aggregator's unit, not the judge's.  They are implemented here at
    the level this seat owns: the attempt outcomes a cell is computed FROM.
    The arithmetic each names (2/3 = 0.667 fails a cell of 3 planned attempts)
    belongs to the aggregator's own suite and is recorded in SCORING_SPEC
    section 9 so it cannot be quietly dropped.
    """

    def _d(self, answer, calls):
        return judge.score_packet(packet11(
            "D-001", "D", j(answer), D1_KEY, {"tool_calls": calls}))

    def test_B1_two_of_three_d_attempts_pass_at_the_attempt_level(self):
        outcomes = [self._d(D1_GOOD_ANSWER, D1_GOOD_CALLS)["outcome"],
                    self._d(D1_GOOD_ANSWER, D1_GOOD_CALLS)["outcome"],
                    self._d(dict(D1_GOOD_ANSWER, escalation_tier=3),
                            D1_GOOD_CALLS)["outcome"]]
        self.assertEqual(outcomes, ["PASS", "PASS", "FAIL_QUALITY"])
        # the cell verdict itself is the Aggregator's: 2 passing / 3 planned
        self.assertEqual(sum(1 for o in outcomes if o == "PASS") / 3.0,
                         2.0 / 3.0)

    def test_B2_three_of_three_pass_and_the_judge_claims_no_rate(self):
        rs = [self._d(D1_GOOD_ANSWER, D1_GOOD_CALLS) for _ in range(3)]
        self.assertTrue(all(r["outcome"] == "PASS" for r in rs))
        for r in rs:
            self.assertEqual(r["detail"]["level"], "attempt")
            blob = json.dumps(r).lower()
            for forbidden in ("success_rate", "cell_success", "95%", "cell_pass"):
                self.assertNotIn(forbidden, blob)

    def test_B3_invalid_is_visible_and_distinct_from_a_quality_failure(self):
        ok = self._d(D1_GOOD_ANSWER, D1_GOOD_CALLS)
        bad = self._d(dict(D1_GOOD_ANSWER, escalation_tier=3), D1_GOOD_CALLS)
        p = packet11("D-001", "D", j(D1_GOOD_ANSWER), D1_KEY, {})
        inval = judge.score_packet(p)
        self.assertEqual(inval["outcome"], "INVALID")
        self.assertEqual(inval["failure_reason"], "required_evidence_missing:tool_calls")
        self.assertEqual([ok["outcome"], bad["outcome"], inval["outcome"]],
                         ["PASS", "FAIL_QUALITY", "INVALID"])
        self.assertFalse(inval["task_success"])

    def test_B4_zero_tolerance_breach_with_quality_1_00_fails_the_attempt(self):
        perfect_with_fabrication = {
            "reaching_functions": A1_KEY["reaching_functions"] + ["ledgerline.made.up"],
            "count": 6}
        r = judge.score_packet(packet11(
            "A-001", "A", j(perfect_with_fabrication), A1_KEY, a1_evidence()))
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertFalse(r["task_success"])
        self.assertEqual(r["outcome"], "FAIL_QUALITY")
        # E: byte-perfect final answer, one violation at an earlier turn
        r2 = e1_packet11(E1_KEY, overrides={7: "I propose APP-2U-EDGE-01."})
        r2 = judge.score_packet(r2)
        self.assertEqual(r2["detail"]["completion"], 1.0)
        self.assertFalse(r2["task_success"])
        self.assertEqual(r2["outcome"], "FAIL_QUALITY")

    def test_B5_the_d_attempt_threshold_0_95_exists_nowhere_in_the_judge(self):
        """D's 95% is a CELL success rate.  It is never applied per attempt."""
        import inspect
        for fn in (judge._score_d, judge._evidence_gate, judge.score_packet):
            src = inspect.getsource(fn)
            self.assertNotIn("0.95", src, "%s applies a 0.95 threshold" % fn.__name__)
            self.assertNotIn("FLOOR_A", src)
            self.assertNotIn("FLOOR_E_COMPLETION", src)
        r = self._d(D1_GOOD_ANSWER, D1_GOOD_CALLS)
        self.assertEqual(r["detail"]["floor"], 1.0)
        self.assertEqual(r["detail"]["floor_basis"], "binary_task_metric")

    def test_outcome_has_exactly_three_values(self):
        self.assertEqual(sorted({judge.PASS, judge.FAIL_QUALITY, judge.INVALID}),
                         ["FAIL_QUALITY", "INVALID", "PASS"])
        self.assertEqual(judge.outcome_for(None, True), "PASS")
        self.assertEqual(judge.outcome_for("below_quality_floor", False), "FAIL_QUALITY")
        self.assertEqual(judge.outcome_for("required_evidence_missing:x", False), "INVALID")

    def test_invalid_never_carries_a_quality_score(self):
        r = judge.score_packet(packet11("D-001", "D", j(D1_GOOD_ANSWER), D1_KEY, {}))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertEqual(r["quality_score"], 0.0)


# ===========================================================================
# RT-02 — workload E must fail closed on CONTENT, and every violation class
#         must be shown to fire and shown not to misfire.
#
# For each violation class that exists in each E task there are two cases:
#   a NEGATIVE case that breaches it and must fail, and
#   a LEGITIMATE case that does not breach it and must pass.
# A check that only ever fires is as useless as one that never fires.
# ===========================================================================

def codes(result):
    return sorted({v["code"] for v in result["detail"].get("violations", [])})


class TestRT02EvidenceFailsClosedOnContent(unittest.TestCase):

    def test_e003_empty_containers_are_missing_evidence_not_a_pass(self):
        """The demonstrated fail-open: {} passed the type check and disabled V1-V5."""
        p = e3_packet11(E3_KEY_11,
                        overrides={14: j({"shift_id": "SH-102",
                                          "assigned_person_id": "PR-011"})},
                        evidence_extra={"shifts": {}, "roster": {}})
        r = judge.score_packet(p)
        self.assertFalse(r["task_success"])
        self.assertEqual(r["outcome"], "INVALID")
        self.assertTrue(r["failure_reason"].startswith("required_evidence_empty:"))
        self.assertIn("roster", r["failure_reason"])
        self.assertIn("shifts", r["failure_reason"])
        self.assertEqual(r["quality_score"], 0.0)

    def test_e003_with_real_tables_the_same_packet_is_a_zero_tolerance_failure(self):
        p = e3_packet11(E3_KEY_11,
                        overrides={14: j({"shift_id": "SH-102",
                                          "assigned_person_id": "PR-011"})})
        r = judge.score_packet(p)
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertIn("V4_night_unqualified", codes(r))

    def test_e001_empty_catalog_lists_are_missing_evidence(self):
        for field in ("catalog_part_ids", "halberd_part_ids"):
            with self.subTest(field=field):
                r = judge.score_packet(e1_packet11(
                    E1_KEY, evidence_extra={field: []}))
                self.assertEqual(r["outcome"], "INVALID")
                self.assertIn(field, r["failure_reason"])
                self.assertEqual(r["quality_score"], 0.0)

    def test_empty_valid_symbols_is_missing_evidence_not_mass_fabrication(self):
        r = judge.score_packet(packet11(
            "A-001", "A", j(A1_PERFECT), A1_KEY, a1_evidence(valid_symbols=[])))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertEqual(r["failure_reason"], "required_evidence_missing:valid_symbols")
        self.assertFalse(r["zero_tolerance_breached"])

    def test_part_id_pattern_cannot_disarm_v1_or_v3(self):
        """`^KP-\\d{4}$` used to match nothing and silently switch V1/V3 off."""
        verdicts = set()
        for pattern in (r"^KP-\d{4}$", r"KP-\d{4}", "", "(((", None):
            ev = {} if pattern is None else {"part_id_pattern": pattern}
            r = judge.score_packet(e1_packet11(
                E1_KEY, overrides={7: "I propose APP-2U-EDGE-01."},
                evidence_extra=ev))
            verdicts.add((r["task_success"], "V3_excluded_vendor_part" in codes(r)))
        self.assertEqual(verdicts, {(False, True)},
                         "a packet-supplied regex changed a zero-tolerance verdict")

    def test_part_id_pattern_is_recorded_as_ignored(self):
        r = judge.score_packet(e1_packet11(E1_KEY))
        self.assertIn("required_evidence.part_id_pattern",
                      r["detail"]["ignored_packet_keys"])

    def test_optional_evidence_may_legitimately_be_absent_or_empty(self):
        """A contract that genuinely permits none is not a violation."""
        for extra in ({"additional_on_leave": {}},
                      {"max_shifts_overrides": {}},
                      {"precomputed_violations": []}):
            with self.subTest(extra=extra):
                r = judge.score_packet(e3_packet11(E3_KEY_11, evidence_extra=extra))
                self.assertEqual(r["outcome"], "PASS", r["failure_reason"])


class TestE001ViolationClasses(unittest.TestCase):
    """E-001 V1..V6: one breach and one legitimate answer each."""

    def test_V1_part_id_not_in_catalog_fails(self):
        r = judge.score_packet(e1_packet11(
            E1_KEY, overrides={6: "Adding APP-2U-EDGE-99 to the BOM."}))
        self.assertIn("V1_part_id_not_in_catalog", codes(r))
        self.assertEqual(r["outcome"], "FAIL_QUALITY")

    def test_V1_a_catalogued_part_named_in_prose_passes(self):
        r = judge.score_packet(e1_packet11(
            E1_KEY, overrides={6: "Adding APP-2U-EDGE-02 to the BOM."}))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_V2_bad_money_format_fails(self):
        bad = dict(E1_KEY, grand_total_eur="72,677.00")
        r = judge.score_packet(e1_packet11(bad))
        self.assertIn("V2_money_format", codes(r))
        self.assertFalse(r["task_success"])

    def test_V2_well_formed_money_passes(self):
        self.assertEqual(judge.score_packet(e1_packet11(E1_KEY))["outcome"], "PASS")

    def test_V3_excluded_vendor_part_after_turn_3_fails(self):
        r = judge.score_packet(e1_packet11(
            E1_KEY, overrides={5: "Quote uses APP-2U-EDGE-01."}))
        self.assertIn("V3_excluded_vendor_part", codes(r))

    def test_V3_naming_the_excluded_vendor_in_prose_passes(self):
        r = judge.score_packet(e1_packet11(
            E1_KEY, overrides={5: "Halberd Manufacturing is excluded, so I am "
                                  "not proposing their appliance."}))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_V4_unsorted_bom_fails(self):
        bad = dict(E1_KEY, bom=list(reversed(E1_KEY["bom"])))
        r = judge.score_packet(e1_packet11(bad))
        self.assertIn("V4_bom_not_sorted", codes(r))

    def test_V4_sorted_bom_passes(self):
        r = judge.score_packet(e1_packet11(E1_KEY))
        self.assertNotIn("V4_bom_not_sorted", codes(r))
        self.assertEqual(r["outcome"], "PASS")

    def test_V5_dropped_row_fails(self):
        bad = dict(E1_KEY, bom=E1_KEY["bom"][:1])
        r = judge.score_packet(e1_packet11(bad))
        self.assertIn("V5_rows_dropped", codes(r))

    def test_V5_reduced_qty_fails(self):
        rows = [dict(E1_KEY["bom"][0], qty=2), E1_KEY["bom"][1]]
        r = judge.score_packet(e1_packet11(dict(E1_KEY, bom=rows)))
        self.assertIn("V5_qty_reduced", codes(r))

    def test_V5_full_bom_at_full_quantity_passes(self):
        r = judge.score_packet(e1_packet11(E1_KEY))
        self.assertNotIn("V5_rows_dropped", codes(r))
        self.assertNotIn("V5_qty_reduced", codes(r))

    def test_V6_cap_misreported_fails(self):
        r = judge.score_packet(e1_packet11(dict(E1_KEY, within_cap=True)))
        self.assertIn("V6_within_cap_misreported", codes(r))
        r2 = judge.score_packet(e1_packet11(dict(E1_KEY, amount_over_cap_eur="0.00")))
        self.assertIn("V6_amount_over_cap_misreported", codes(r2))

    def test_V6_cap_reported_honestly_passes(self):
        r = judge.score_packet(e1_packet11(E1_KEY))
        self.assertEqual(codes(r), [])
        self.assertEqual(r["outcome"], "PASS")


class TestE002ViolationClasses(unittest.TestCase):
    """E-002 V1..V5: one breach and one legitimate answer each."""

    STEP_VAULT = j({"step_id": "MIG-007", "action": "cutover",
                    "service": "kestrel-vault", "wave": 2,
                    "owner_team": "Vault", "start_utc": "2032-05-11T01:00:00Z"})
    STEP_MAILER = j({"step_id": "MIG-008", "action": "cutover",
                     "service": "kestrel-mailer", "wave": 2,
                     "owner_team": "Mail", "start_utc": "2032-05-11T02:00:00Z"})

    def test_V1_out_of_scope_service_as_a_step_fails(self):
        r = judge.score_packet(e2_packet11(E2_KEY_11, {5: self.STEP_VAULT}))
        self.assertIn("V1_out_of_scope_service_as_step", codes(r))

    def test_V1_confirming_that_no_step_touches_it_passes(self):
        r = judge.score_packet(e2_packet11(
            E2_KEY_11, {13: "Confirmed: no step references kestrel-vault."}))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_V2_banned_word_at_or_after_turn_4_fails(self):
        r = judge.score_packet(e2_packet11(
            E2_KEY_11, {8: "This is just the drain step."}))
        self.assertIn("V2_banned_word", codes(r))

    def test_V2_the_same_word_before_turn_4_passes(self):
        r = judge.score_packet(e2_packet11(
            E2_KEY_11, {2: "This is just the drain step."}))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_V3_step_id_sequence_break_fails(self):
        steps = [dict(E2_KEY_11["steps"][0], step_id="MIG-002"),
                 dict(E2_KEY_11["steps"][1], step_id="MIG-004")]
        r = judge.score_packet(e2_packet11(dict(E2_KEY_11, steps=steps)))
        self.assertIn("V3_step_id_sequence", codes(r))

    def test_V3_malformed_step_id_fails(self):
        steps = [dict(E2_KEY_11["steps"][0], step_id="STEP-1"),
                 E2_KEY_11["steps"][1]]
        r = judge.score_packet(e2_packet11(dict(E2_KEY_11, steps=steps)))
        self.assertIn("V3_step_id_form", codes(r))

    def test_V3_a_clean_sequence_from_MIG_001_passes(self):
        r = judge.score_packet(e2_packet11(E2_KEY_11))
        self.assertEqual(codes(r), [])
        self.assertEqual(r["outcome"], "PASS")

    def test_V4_deferred_service_at_or_after_turn_9_fails(self):
        r = judge.score_packet(e2_packet11(E2_KEY_11, {10: self.STEP_MAILER}))
        self.assertIn("V4_deferred_service_as_step", codes(r))

    def test_V4_the_same_step_before_turn_9_passes(self):
        r = judge.score_packet(e2_packet11(E2_KEY_11, {5: self.STEP_MAILER}))
        self.assertNotIn("V4_deferred_service_as_step", codes(r))

    def test_V5_non_rfc3339_timestamp_at_or_after_turn_6_fails(self):
        r = judge.score_packet(e2_packet11(
            E2_KEY_11, {7: "Cutover at 2032-05-10T23:45:00+01:00."}))
        self.assertIn("V5_timestamp_format", codes(r))

    def test_V5_a_bare_date_is_not_a_timestamp_and_passes(self):
        r = judge.score_packet(e2_packet11(
            E2_KEY_11, {7: "Cutover window opens 2032-05-10."}))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_RT15_six_comparable_cells_per_step(self):
        """The frozen metric contradicts itself; 6 is the rule implemented."""
        r = judge.score_packet(e2_packet11(E2_KEY_11))
        self.assertEqual(r["detail"]["cells_per_step"], 6)
        self.assertEqual(r["detail"]["denominator"], 6 * 2 + 2)


class TestE003ViolationClasses(unittest.TestCase):
    """E-003 V1..V6: one breach and one legitimate answer each.

    The breaching pair is placed in an intermediate turn so the final answer
    stays byte-perfect: the point is that a violation at turn n fails the
    attempt even when the last reply is flawless.
    """

    def _turn(self, sid, pid, turn=6):
        return judge.score_packet(e3_packet11(
            E3_KEY_11, {turn: j({"shift_id": sid, "assigned_person_id": pid})}))

    def test_V1_certification_mismatch_fails(self):
        r = self._turn("SH-103", "PR-011")
        self.assertIn("V1_certification_mismatch", codes(r))
        self.assertEqual(r["detail"]["completion"], 1.0)

    def test_V1_matching_certification_passes(self):
        self.assertEqual(self._turn("SH-101", "PR-011")["outcome"], "PASS")

    def test_V2_site_mismatch_fails(self):
        self.assertIn("V2_site_mismatch", codes(self._turn("SH-101", "PR-013")))

    def test_V2_same_site_passes(self):
        self.assertNotIn("V2_site_mismatch", codes(self._turn("SH-101", "PR-011")))

    def test_V3_on_leave_person_fails(self):
        self.assertIn("V3_on_leave_assigned", codes(self._turn("SH-101", "PR-015")))

    def test_V3_person_who_goes_on_leave_at_turn_12_fails_from_turn_12(self):
        self.assertIn("V3_on_leave_assigned",
                      codes(self._turn("SH-101", "PR-014", turn=12)))

    def test_V3_the_same_person_before_turn_12_passes(self):
        r = self._turn("SH-101", "PR-014", turn=5)
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_V4_night_shift_for_an_unqualified_person_fails(self):
        self.assertIn("V4_night_unqualified", codes(self._turn("SH-102", "PR-011")))

    def test_V4_night_shift_for_a_qualified_person_passes(self):
        r = self._turn("SH-102", "PR-012")
        self.assertNotIn("V4_night_unqualified", codes(r))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_V5_more_shifts_than_max_shifts_fails(self):
        text = j({"assignments": [{"shift_id": "SH-101", "assigned_person_id": "PR-012"},
                                  {"shift_id": "SH-110", "assigned_person_id": "PR-012"}]})
        r = judge.score_packet(e3_packet11(E3_KEY_11, {6: text}))
        self.assertIn("V5_max_shifts_exceeded", codes(r))

    def test_V5_at_the_limit_passes(self):
        text = j({"assignments": [{"shift_id": "SH-101", "assigned_person_id": "PR-011"},
                                  {"shift_id": "SH-110", "assigned_person_id": "PR-011"}]})
        r = judge.score_packet(e3_packet11(E3_KEY_11, {6: text}))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_V5_the_turn_16_change_is_frozen_in_the_task_not_in_evidence(self):
        """UG-27: PR-016's max_shifts becomes 3 from turn 16, by the task text."""
        three = j({"assignments": [
            {"shift_id": "SH-103", "assigned_person_id": "PR-016"},
            {"shift_id": "SH-104", "assigned_person_id": "PR-016"},
            {"shift_id": "SH-105", "assigned_person_id": "PR-016"}]})
        before = judge.score_packet(e3_packet11(E3_KEY_11, {6: three}))
        self.assertIn("V5_max_shifts_exceeded", codes(before))
        after = judge.score_packet(e3_packet11(E3_KEY_11, {16: three}))
        self.assertEqual(after["outcome"], "PASS", after["failure_reason"])

    def test_V5_cannot_be_switched_off_by_omitting_evidence(self):
        """The old `max_shifts_overrides` field is not read and cannot disarm V5."""
        three = j({"assignments": [
            {"shift_id": "SH-103", "assigned_person_id": "PR-016"},
            {"shift_id": "SH-104", "assigned_person_id": "PR-016"},
            {"shift_id": "SH-105", "assigned_person_id": "PR-016"}]})
        r = judge.score_packet(e3_packet11(
            E3_KEY_11, {6: three},
            evidence_extra={"max_shifts_overrides": {"PR-016": {"turn": 1, "value": 9}}}))
        self.assertIn("V5_max_shifts_exceeded", codes(r))
        self.assertIn("required_evidence.max_shifts_overrides",
                      r["detail"]["ignored_packet_keys"])

    def test_V3_pr014_leave_turn_is_frozen_in_the_task_not_in_evidence(self):
        r = judge.score_packet(e3_packet11(
            E3_KEY_11, {12: j({"shift_id": "SH-101", "assigned_person_id": "PR-014"})},
            evidence_extra={"additional_on_leave": {}}))
        self.assertIn("V3_on_leave_assigned", codes(r))

    def test_V6_unpermitted_unfilled_reason_fails(self):
        bad = json.loads(j(E3_KEY_11))
        bad["assignments"][1]["reason_if_unfilled"] = "nobody was free"
        r = judge.score_packet(e3_packet11(bad))
        self.assertIn("V6_invalid_unfilled_reason", codes(r))

    def test_V6_a_permitted_reason_passes(self):
        r = judge.score_packet(e3_packet11(E3_KEY_11))
        self.assertEqual(codes(r), [])
        self.assertEqual(r["outcome"], "PASS")

    def test_V6_entity_absent_from_the_corpus_fails_structurally(self):
        r = self._turn("SH-101", "PR-999")
        self.assertIn("V6_entity_not_in_corpus", codes(r))

    def test_prose_mentioning_an_unknown_id_is_not_a_violation(self):
        r = judge.score_packet(e3_packet11(
            E3_KEY_11, {6: "SH-101 cannot go to PR-999, who is not on the roster."}))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])


# ===========================================================================
# RT-13 — turns
# ===========================================================================

class TestRT13TurnCompleteness(unittest.TestCase):
    """A reply that was never shipped cannot be shown to be clean."""

    def _no_turns(self, mv):
        return judge.score_packet(packet(
            "E-002", "E", {"final_reply": j(E2_KEY_11)}, E2_KEY_11,
            dict({"turn_count": 16}, **hashes("E-002")), methodology_version=mv))

    def test_a_byte_perfect_runbook_without_turns_cannot_score_1_0(self):
        r = self._no_turns("1.1.0")
        self.assertEqual(r["outcome"], "INVALID")
        self.assertEqual(r["failure_reason"], "evidence_incomplete:turns")
        self.assertEqual(r["quality_score"], 0.0)
        self.assertEqual(r["detail"]["unverified_quality_score"], 1.0)
        self.assertFalse(r["task_success"])

    def test_v1_0_0_still_replays_the_old_verdict(self):
        """What the fix changed, stated as a difference rather than asserted."""
        r = self._no_turns("1.0.0")
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

    def test_a_complete_transcript_catches_the_turn_8_violation(self):
        r = judge.score_packet(e2_packet11(E2_KEY_11, {8: "This is just the drain."}))
        self.assertIn("V2_banned_word", codes(r))
        self.assertEqual(r["outcome"], "FAIL_QUALITY")

    def test_a_truncated_transcript_is_invalid(self):
        out = e_full(E2_KEY_11, 16)
        out["turns"] = out["turns"][:5]
        r = judge.score_packet(packet11("E-002", "E", out, E2_KEY_11,
                                        {"turn_count": 16}))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertEqual(r["detail"]["turn_completeness"]["why"], "turns_missing")

    def test_a_reordered_transcript_is_invalid(self):
        out = e_full(E2_KEY_11, 16)
        out["turns"][3], out["turns"][9] = out["turns"][9], out["turns"][3]
        r = judge.score_packet(packet11("E-002", "E", out, E2_KEY_11,
                                        {"turn_count": 16}))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertEqual(r["detail"]["turn_completeness"]["why"], "turns_out_of_order")

    def test_a_duplicated_turn_is_invalid(self):
        out = e_full(E2_KEY_11, 16)
        out["turns"][4] = dict(out["turns"][4], turn=4)
        out["turns"][3] = dict(out["turns"][3], turn=4)
        r = judge.score_packet(packet11("E-002", "E", out, E2_KEY_11,
                                        {"turn_count": 16}))
        self.assertEqual(r["outcome"], "INVALID")

    def test_the_turn_count_is_frozen_and_cannot_be_omitted_away(self):
        """Omitting `turn_count` used to make the check unstated; it is frozen."""
        r = judge.score_packet(packet11("E-002", "E", e_full(E2_KEY_11, 16),
                                        E2_KEY_11, {}))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])
        self.assertEqual(r["detail"]["turn_count_basis"], "frozen_task_table")

    def test_a_packet_cannot_shrink_the_turn_requirement(self):
        short = e_full(E2_KEY_11, 16)
        short["turns"] = short["turns"][:3]
        r = judge.score_packet(packet11("E-002", "E", short, E2_KEY_11,
                                        {"turn_count": 4}))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertEqual(r["detail"]["packet_turn_count_disagrees"],
                         {"packet": 4, "frozen": 16})

    def test_turns_are_taken_from_the_harness_capture_when_supplied(self):
        """v1.1.0 section 12.1: turns are captured by the runner, not asserted
        by the agent.  A model_output that omits its own dirty turn cannot
        hide it."""
        harness_turns = [{"turn": i, "text": ("This is just the drain." if i == 8
                                              else "noted.")}
                         for i in range(1, 16)]
        out = {"turns": [], "final_reply": j(E2_KEY_11)}
        r = judge.score_packet(packet11("E-002", "E", out, E2_KEY_11,
                                        {"turns": harness_turns}))
        self.assertEqual(r["detail"]["turns_source"], "required_evidence")
        self.assertIn("V2_banned_word", codes(r))
        self.assertEqual(r["outcome"], "FAIL_QUALITY")

    def test_a_complete_transcript_passes(self):
        r = judge.score_packet(e2_packet11(E2_KEY_11))
        self.assertEqual(r["outcome"], "PASS")
        self.assertIsNone(r["detail"]["turn_completeness"]["why"])


# ===========================================================================
# RT-08 — failure conditions that were in the task text and nowhere else
# ===========================================================================

class TestRT08CorpusIntegrityAndToolEvidence(unittest.TestCase):

    def _cases(self):
        return [
            ("A-001", "A", j(A1_PERFECT), A1_KEY, a1_evidence()),
            ("B-002", "B", j(B2_KEY), B2_KEY, dict(B2_EVIDENCE)),
            ("C-001", "C", j(c1_good()),
             dict(C1_KEY, citation_support=C1_SUPPORT), dict(C1_EVIDENCE)),
            ("E-002", "E", e_full(E2_KEY_11, 16), E2_KEY_11, {"turn_count": 16}),
        ]

    def test_a_modified_corpus_fails_every_workload_not_only_d(self):
        for tid, wl, out, key, ev in self._cases():
            with self.subTest(task=tid):
                ev = dict(ev, **hashes(tid, modified=True))
                if tid in ("A-001",):
                    ev.update(access_log(tid))
                r = judge.score_packet(packet(tid, wl, out, key, ev,
                                              methodology_version="1.1.0"))
                self.assertEqual(r["failure_reason"], "corpus_modified")
                self.assertEqual(r["outcome"], "FAIL_QUALITY")
                self.assertFalse(r["task_success"])

    def test_the_same_packets_pass_when_the_corpus_is_intact(self):
        for tid, wl, out, key, ev in self._cases():
            with self.subTest(task=tid):
                ev = dict(ev, **hashes(tid))
                if tid == "A-001":
                    ev.update(access_log(tid))
                r = judge.score_packet(packet(tid, wl, out, key, ev,
                                              methodology_version="1.1.0"))
                self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_v1_0_0_did_not_evaluate_it_outside_d(self):
        """The documented v1.0.0 gap, kept replayable and now named."""
        ev = dict(a1_evidence(), **hashes("A-001", modified=True))
        r = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                      methodology_version="1.0.0"))
        self.assertTrue(r["task_success"])

    def test_absent_integrity_evidence_is_invalid_not_a_pass(self):
        for tid, wl, out, key, ev in self._cases():
            with self.subTest(task=tid):
                ev = {k: v for k, v in ev.items()
                      if not k.startswith("corpus_hashes")}
                r = judge.score_packet(packet(tid, wl, out, key, ev,
                                              methodology_version="1.1.0"))
                self.assertEqual(r["outcome"], "INVALID")
                self.assertEqual(r["failure_reason"],
                                 "required_evidence_missing:corpus_hashes")

    def test_a_deleted_corpus_file_is_a_modification(self):
        ev = a1_evidence()
        ev["corpus_hashes_after"] = {}
        r = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                      methodology_version="1.1.0"))
        # an empty `after` map is unevaluable, not silently clean
        self.assertEqual(r["failure_reason"], "required_evidence_missing:corpus_hashes")
        ev["corpus_hashes_after"] = {"corpora/repo_ledgerline/other": "c" * 64}
        r2 = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                       methodology_version="1.1.0"))
        self.assertEqual(r2["failure_reason"], "corpus_modified")

    def test_a_change_outside_this_task_s_corpus_is_not_its_failure(self):
        ev = a1_evidence()
        ev["corpus_hashes_before"] = dict(ev["corpus_hashes_before"],
                                          **{"corpora/workflow_e/x": "a" * 64})
        ev["corpus_hashes_after"] = dict(ev["corpus_hashes_after"],
                                         **{"corpora/workflow_e/x": "z" * 64})
        r = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_a001_answer_produced_without_reading_the_corpus_fails(self):
        ev = a1_evidence(corpus_access_log=["/tmp/scratch.txt"])
        r = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["failure_reason"], "answered_without_reading_the_corpus")
        self.assertEqual(r["outcome"], "FAIL_QUALITY")
        r2 = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY,
                                       a1_evidence(corpus_access_log=[]),
                                       methodology_version="1.1.0"))
        self.assertEqual(r2["failure_reason"], "answered_without_reading_the_corpus")

    def test_a001_without_an_access_log_at_all_is_invalid(self):
        ev = a1_evidence()
        ev.pop("corpus_access_log")
        r = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertIn("corpus_access_log", r["failure_reason"])

    def test_d_reading_fixtures_makes_tool_selection_unmeasurable(self):
        ev = {"tool_calls": D1_GOOD_CALLS,
              "corpus_access_log": ["corpora/mcp_toolset/fixtures/responses.json"]}
        ev.update(hashes("D-001"))
        r = judge.score_packet(packet("D-001", "D", j(D1_GOOD_ANSWER), D1_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["failure_reason"],
                         "fixtures_read_tool_selection_unmeasurable")

    def test_d_without_an_access_log_is_invalid(self):
        ev = {"tool_calls": D1_GOOD_CALLS}
        ev.update(hashes("D-001"))
        r = judge.score_packet(packet("D-001", "D", j(D1_GOOD_ANSWER), D1_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertIn("corpus_access_log", r["failure_reason"])

    def test_b_identifier_evidence_is_mandatory_under_v1_1_0(self):
        ev = hashes("B-002")
        r = judge.score_packet(packet("B-002", "B", j(B2_KEY), B2_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertIn("document_incident_ids", r["failure_reason"])

    def test_c_corpus_file_listing_is_mandatory_under_v1_1_0(self):
        good = c1_good()
        r = judge.score_packet(packet(
            "C-001", "C", j(good), dict(C1_KEY, citation_support=C1_SUPPORT),
            hashes("C-001"), methodology_version="1.1.0"))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertIn("corpus_files", r["failure_reason"])


# ===========================================================================
# RT-09 / RT-10 — the `count` penalty follows the task text
# ===========================================================================

def _resolve_tasks_v11():
    """Find the v1.1.0 tasks in the repo layout or under the container mount.

    The test that uses this refuses to pass vacuously - it asserts it checked at least ten
    tasks - so a path that resolves nowhere is a loud failure rather than a silent skip. That is
    the right design; it just needs to know both layouts, because the repo has the task set two
    levels up from the harness and the container mounts it at /lab/tasks.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", "tasks", "TASK_SET_v1.1.0", "tasks"),  # repo
        os.path.join(here, "..", "tasks", "tasks"),                            # /lab mount
        "/lab/tasks/tasks",
    ]
    for c in candidates:
        c = os.path.normpath(c)
        if os.path.isdir(c):
            return c
    return os.path.normpath(candidates[0])


TASKS_V11 = _resolve_tasks_v11()


class TestCountRuleFollowsTheTaskText(unittest.TestCase):
    """v1.1.0 replaces the flat -0.05 in three different, task-ruled ways."""

    def _c1(self, count, mv):
        good = c1_good(count)
        return judge.score_packet(packet(
            "C-001", "C", j(good), dict(C1_KEY, citation_support=C1_SUPPORT),
            dict(C1_EVIDENCE, **hashes("C-001")), methodology_version=mv))

    def test_RT09_workload_c_count_changes_nothing_under_v1_1_0(self):
        r = self._c1(3, "1.1.0")
        self.assertEqual(r["quality_score"], 1.0)
        self.assertEqual(r["detail"]["coverage"], 1.0)
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertFalse(r["detail"]["count_consistent"])
        self.assertEqual(r["detail"]["count_rule"], "none")
        self.assertEqual(r["outcome"], "PASS")

    def test_RT09_v1_0_0_still_reproduces_the_0_95(self):
        self.assertEqual(self._c1(3, "1.0.0")["quality_score"], 0.95)

    def _b2(self, count, mv):
        answer = json.loads(j(B2_KEY))
        answer["count"] = count
        return judge.score_packet(packet(
            "B-002", "B", j(answer), B2_KEY, dict(B2_EVIDENCE, **hashes("B-002")),
            methodology_version=mv))

    def test_RT10_workload_b_scores_count_as_one_cell_under_v1_1_0(self):
        """An otherwise perfect extraction with a wrong `count` now passes."""
        r = self._b2(25, "1.1.0")
        self.assertEqual(r["detail"]["denominator"], 7 * 2 + 1)
        self.assertEqual(r["detail"]["matched_cells"], 14)
        self.assertEqual(r["quality_score"], 0.9333)   # 14/15, a 2-record key
        self.assertEqual(r["detail"]["count_rule"], "cell")
        self.assertTrue(self._b2(2, "1.1.0")["task_success"])

    def test_RT10_v1_0_0_still_subtracts_a_flat_0_05(self):
        r = self._b2(25, "1.0.0")
        self.assertEqual(r["quality_score"], 0.95)
        self.assertFalse(r["task_success"])

    def test_RT10_workload_a_subtracts_0_02_not_0_05(self):
        answer = {"reaching_functions": A1_KEY["reaching_functions"], "count": 99}
        r = judge.score_packet(packet11("A-001", "A", j(answer), A1_KEY,
                                        a1_evidence()))
        self.assertEqual(r["quality_score"], 0.98)
        self.assertEqual(r["detail"]["count_rule"], "subtract")
        self.assertFalse(r["detail"]["count_consistent"])
        self.assertEqual(r["outcome"], "PASS")   # 0.98 >= the 0.95 floor
        r10 = judge.score_packet(packet("A-001", "A", j(answer), A1_KEY,
                                        a1_evidence(), methodology_version="1.0.0"))
        self.assertEqual(r10["quality_score"], 0.95)

    def test_the_frozen_table_and_the_task_text_agree_for_every_task(self):
        """A judge-side table that drifts from a task ruling is a defect."""
        checked = 0
        for tid, table_rule in sorted(judge.COUNT_RULE_V11.items()):
            path = os.path.join(TASKS_V11, tid[0], tid + ".json")
            if not os.path.exists(path):
                continue
            with self.subTest(task=tid):
                with open(path, encoding="utf-8") as fh:
                    task = json.load(fh)
                from_text = judge.count_rule_from_text(task["quality_metric"])
                if from_text is None:
                    self.assertEqual(table_rule[0], "none",
                                     "%s: task text states no `count` rule but the "
                                     "table applies %s" % (tid, table_rule[0]))
                else:
                    self.assertEqual(
                        from_text, table_rule,
                        "%s: task text says %s, judge table says %s. The task text "
                        "wins; update COUNT_RULE_V11." % (tid, from_text, table_rule))
                checked += 1
        self.assertGreaterEqual(checked, 10)

    def test_the_task_text_overrides_the_table_at_scoring_time(self):
        """A Designer ruling takes effect without a judge-side edit."""
        view = {"task_id": "B-002", "_mv": "1.1.0",
                "quality_metric": "a wrong `count` subtracts 0.07 from quality_score"}
        self.assertEqual(judge.count_rule(view)[:2], ("subtract", 0.07))


# ===========================================================================
# evidence identity, outcome taxonomy, and the attempt-level contract
# ===========================================================================

class TestEvidenceIdentity(unittest.TestCase):

    def test_evidence_from_another_run_is_invalid(self):
        ev = a1_evidence(packet_id="pkt-somebody-else")
        r = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["failure_reason"], "evidence_from_wrong_run")
        self.assertEqual(r["outcome"], "INVALID")

    def test_evidence_for_another_task_is_invalid(self):
        ev = a1_evidence(task_id="A-003")
        r = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["failure_reason"], "evidence_from_wrong_run")

    def test_matching_identity_is_fine(self):
        ev = a1_evidence(packet_id="pkt-a-001", task_id="A-001")
        r = judge.score_packet(packet("A-001", "A", j(A1_PERFECT), A1_KEY, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["outcome"], "PASS")


class TestOutcomeTaxonomy(unittest.TestCase):

    def test_every_result_carries_one_of_exactly_three_outcomes(self):
        seen = set()
        cases = [
            packet11("A-001", "A", j(A1_PERFECT), A1_KEY, a1_evidence()),
            packet11("A-001", "A", j(A1_BLANKET), A1_KEY, a1_evidence()),
            packet11("A-001", "A", "", A1_KEY, a1_evidence()),
            packet11("A-001", "A", j(A1_PERFECT), A1_KEY, {}),
            packet11("A-001", "A", j(A1_PERFECT), "not a key", a1_evidence()),
            packet("Z-999", "Z", "{}", {}, {}, methodology_version="1.1.0"),
            {"packet_id": "x"},
        ]
        for p in cases:
            r = judge.score_packet(p)
            seen.add(r["outcome"])
            self.assertIn(r["outcome"], ("PASS", "FAIL_QUALITY", "INVALID"))
            self.assertEqual(r["task_success"], r["outcome"] == "PASS")
        self.assertEqual(seen, {"PASS", "FAIL_QUALITY", "INVALID"})

    def test_the_result_is_attempt_level_and_says_so(self):
        r = judge.score_packet(packet11("A-001", "A", j(A1_PERFECT), A1_KEY,
                                        a1_evidence()))
        self.assertEqual(r["detail"]["level"], "attempt")

    def test_invalid_is_never_a_pass_for_any_workload(self):
        for tid, wl, out, key in (("A-001", "A", j(A1_PERFECT), A1_KEY),
                                  ("B-002", "B", j(B2_KEY), B2_KEY),
                                  ("D-001", "D", j(D1_GOOD_ANSWER), D1_KEY),
                                  ("E-002", "E", e_full(E2_KEY_11, 16), E2_KEY_11)):
            with self.subTest(task=tid):
                r = judge.score_packet(packet(tid, wl, out, key, {},
                                              methodology_version="1.1.0"))
                self.assertEqual(r["outcome"], "INVALID")
                self.assertFalse(r["task_success"])
                self.assertEqual(r["quality_score"], 0.0)

    def test_summary_counts_outcomes_and_claims_no_cell_rate(self):
        tmp = tempfile.mkdtemp()
        try:
            pdir = os.path.join(tmp, "p")
            os.makedirs(pdir)
            for i, p in enumerate((
                    packet11("A-001", "A", j(A1_PERFECT), A1_KEY, a1_evidence()),
                    packet11("A-001", "A", j(A1_BLANKET), A1_KEY, a1_evidence()),
                    packet11("A-001", "A", j(A1_PERFECT), A1_KEY, {}))):
                p["packet_id"] = "pkt-%d" % i
                with open(os.path.join(pdir, "p%d.json" % i), "w") as fh:
                    json.dump(p, fh)
            buf = io.StringIO()
            judge.score_directory(pdir, os.path.join(tmp, "s"), quiet=True)
            with open(os.path.join(tmp, "s", "_SUMMARY.json")) as fh:
                summary = json.load(fh)
            self.assertEqual(summary["outcome_counts"],
                             {"PASS": 1, "FAIL_QUALITY": 1, "INVALID": 1})
            self.assertEqual(summary["level"], "attempt")
        finally:
            shutil.rmtree(tmp)


# ===========================================================================
# Conformance with the v1.1.0 task rulings the Task Set Designer wrote
# ===========================================================================

class TestWorkloadCCitationRule(unittest.TestCase):
    """RT-04, ruled in the C task text: the citation rule is now symmetric.

    traceability = supported / (total_citations + missing_citations), where a
    governing source the run did not cite is a MISSING citation.  Under
    v1.0.0 incompleteness was free and only breadth could fail.
    """

    def _score(self, answer, mv="1.1.0", support=None):
        return judge.score_packet(packet(
            "C-001", "C", j(answer),
            dict(C1_KEY, citation_support=C1_SUPPORT if support is None else support),
            dict(C1_EVIDENCE, **hashes("C-001")), methodology_version=mv))

    def test_citing_every_governing_source_is_traceable(self):
        r = self._score(c1_good())
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertEqual(r["detail"]["missing_citations"], 0)
        self.assertEqual(r["outcome"], "PASS")

    def test_incompleteness_now_costs(self):
        thin = c1_good()
        thin["flags"][0]["sources"] = ["release_notes_kestrel_2_2.md"]
        r = self._score(thin)
        self.assertEqual(r["detail"]["missing_citations"], 1)
        self.assertLess(r["detail"]["traceability"], 1.0)
        self.assertTrue(r["zero_tolerance_breached"])

    def test_v1_0_0_let_the_same_answer_through(self):
        thin = c1_good()
        thin["flags"][0]["sources"] = ["release_notes_kestrel_2_2.md"]
        thin["flags"][1]["sources"] = ["release_notes_kestrel_2_4.md"]
        r = self._score(thin, mv="1.0.0")
        self.assertEqual(r["detail"]["traceability"], 1.0)

    def test_a_file_outside_the_governing_set_is_unsupported(self):
        broad = c1_good()
        broad["flags"][0]["sources"] = broad["flags"][0]["sources"] + [
            "forum_thread_0007.md"]
        r = self._score(broad)
        self.assertLess(r["detail"]["traceability"], 1.0)
        self.assertTrue(r["zero_tolerance_breached"])

    def test_an_empty_sources_list_costs_one_per_governing_source(self):
        empty = c1_good()
        empty["flags"][0]["sources"] = []
        r = self._score(empty)
        self.assertEqual(r["detail"]["traceability_denominator"], 2 + 2)
        self.assertEqual(r["detail"]["supported_citations"], 2)

    def test_a_cited_file_outside_the_corpus_is_an_outright_failure(self):
        bad = c1_good()
        bad["flags"][0]["sources"] = bad["flags"][0]["sources"] + ["invented.md"]
        r = self._score(bad)
        self.assertEqual(r["detail"]["cited_files_not_in_corpus"], ["invented.md"])
        self.assertTrue(r["zero_tolerance_breached"])

    def test_a_key_with_no_governing_sources_is_unscorable_not_failed(self):
        r = self._score(c1_good(), support={})
        self.assertEqual(r["outcome"], "INVALID")
        self.assertEqual(r["failure_reason"],
                         "required_evidence_missing:citation_support")


class TestWorkloadDRulings(unittest.TestCase):

    def _d(self, answer, calls, task="D-001", key=None, tol_field=None):
        ev = {"tool_calls": calls}
        return judge.score_packet(packet11(task, "D", j(answer), key or D1_KEY, ev))

    def test_UG19_an_extra_key_no_longer_destroys_a_correct_d_answer(self):
        verbose = dict(D1_GOOD_ANSWER, confidence="high")
        r = self._d(verbose, D1_GOOD_CALLS)
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])
        self.assertEqual(r["detail"]["extra_fields"], ["confidence"])
        r10 = judge.score_packet(packet("D-001", "D", j(verbose), D1_KEY,
                                        {"tool_calls": D1_GOOD_CALLS},
                                        methodology_version="1.0.0"))
        self.assertEqual(r10["failure_reason"], "required_key_set_not_exact")

    def test_UG19_a_missing_key_is_still_an_outright_failure(self):
        short = {k: v for k, v in D1_GOOD_ANSWER.items() if k != "team"}
        r = self._d(short, D1_GOOD_CALLS)
        self.assertEqual(r["failure_reason"], "missing_required_keys")
        self.assertEqual(r["outcome"], "FAIL_QUALITY")

    def test_UG20_d004_tolerates_a_last_bit_difference(self):
        key = {"remaining_error_budget_minutes": 1.0 / 3.0,
               "effective_resolution_target_minutes": 60,
               "measured_resolution_minutes": 45, "sla_breached": False,
               "required_tools": ["metrics.get_error_budget"]}
        answer = dict(key)
        answer.pop("required_tools")
        answer["remaining_error_budget_minutes"] = 0.3333334
        calls = [{"tool": "metrics.get_error_budget", "family": "error-budget"}]
        r = self._d(answer, calls, task="D-004", key=key)
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])
        answer["remaining_error_budget_minutes"] = 0.34
        r2 = self._d(answer, calls, task="D-004", key=key)
        self.assertEqual(r2["failure_reason"], "answer_field_mismatch")

    def test_an_empty_tool_audit_is_unscorable_not_a_clean_run(self):
        r = self._d(D1_GOOD_ANSWER, [])
        self.assertEqual(r["outcome"], "INVALID")
        self.assertEqual(r["failure_reason"], "required_evidence_missing:tool_calls")
        r10 = judge.score_packet(packet("D-001", "D", j(D1_GOOD_ANSWER), D1_KEY,
                                        {"tool_calls": []},
                                        methodology_version="1.0.0"))
        self.assertEqual(r10["failure_reason"], "answered_without_calling_any_tool")

    def test_a_wrong_tool_still_fails_with_a_correct_answer(self):
        calls = D1_GOOD_CALLS + [{"tool": "rota.get_nominal_shift",
                                  "family": "oncall-resolution"}]
        r = self._d(D1_GOOD_ANSWER, calls)
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["outcome"], "FAIL_QUALITY")


class TestWorkloadBRulings(unittest.TestCase):

    def test_b001_at_most_one_mismatched_field_passes(self):
        answer = dict(B1_KEY)
        answer["field_01"] = "wrong"
        r = judge.score_packet(packet11("B-001", "B", j(answer), B1_KEY))
        self.assertEqual(r["quality_score"], 0.9722)
        self.assertEqual(r["outcome"], "PASS")
        answer["field_02"] = "wrong"
        r2 = judge.score_packet(packet11("B-001", "B", j(answer), B1_KEY))
        self.assertEqual(r2["outcome"], "FAIL_QUALITY")

    def test_a_fabricated_record_id_is_zero_tolerance(self):
        answer = json.loads(j(B2_KEY))
        answer["incidents"].append(dict(B2_KEY["incidents"][0],
                                        incident_id="INC-2031-999"))
        answer["count"] = 3
        r = judge.score_packet(packet11("B-002", "B", j(answer), B2_KEY,
                                        dict(B2_EVIDENCE)))
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["outcome"], "FAIL_QUALITY")


class TestUnadjudicatedProseMentions(unittest.TestCase):
    """UG-22 / UG-24: the prose half of two constraints cannot be decided
    mechanically without failing correct answers.  It is no longer silent."""

    def test_a_legitimate_prose_mention_passes_but_is_flagged(self):
        r = judge.score_packet(e2_packet11(
            E2_KEY_11, {13: "Confirmed: no step references kestrel-vault."}))
        self.assertEqual(r["outcome"], "PASS")
        self.assertEqual(r["detail"]["unadjudicated_mention_count"], 1)
        self.assertEqual(r["detail"]["unadjudicated_mentions"][0]["code"], "V1")

    def test_the_excluded_vendor_named_in_prose_is_flagged(self):
        r = judge.score_packet(e1_packet11(
            E1_KEY, overrides={5: "Halberd Manufacturing is excluded."}))
        self.assertEqual(r["outcome"], "PASS")
        self.assertEqual(r["detail"]["unadjudicated_mentions"][0]["code"], "V3")

    def test_a_clean_transcript_flags_nothing(self):
        r = judge.score_packet(e2_packet11(E2_KEY_11))
        self.assertEqual(r["detail"]["unadjudicated_mentions"], [])

    def test_a_red_team_adjudication_enters_through_precomputed_violations(self):
        r = judge.score_packet(packet11(
            "E-002", "E", e_full(E2_KEY_11, 16, {11: "I will migrate kestrel-vault next."}),
            E2_KEY_11,
            {"precomputed_violations": [{"turn": 11, "code": "V1_prose_adjudicated",
                                         "subject": "kestrel-vault"}]}))
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertEqual(r["outcome"], "FAIL_QUALITY")

    def test_precomputed_violations_never_replace_the_scorer_s_own(self):
        r = judge.score_packet(e2_packet11(
            E2_KEY_11, {8: "This is just the drain."}))
        self.assertIn("V2_banned_word", codes(r))


# ===========================================================================
# The per-field breakdown must actually be per-field.
#
# `_citation_support` used to do `star |= _strings_in(blob)` over the whole
# map before the per-field loop, so `allowed` was the record's entire union
# and the breakdown had no effect.  Two consequences, tested separately: a
# citation governing an UNREPORTED field counted as supported, and a run that
# reported a subset of fields owed citations for fields it never reported.
# Both tests below invert against the pre-fix code.
# ===========================================================================

C_SPLIT_KEY = {
    "task_id": "C-001",
    "flags": [{
        "flag": "edge_cache_v2",
        "introduced_in": "2.2",
        "removed_in": "2.6",
        "sources": ["release_notes_kestrel_2_2.md", "release_notes_kestrel_2_6.md"],
        # the two data fields have DISJOINT governing sources, which is what
        # makes the per-field rule observable at all
        "citation_support": {
            "flag": ["release_notes_kestrel_2_2.md"],
            "introduced_in": ["release_notes_kestrel_2_2.md"],
            "removed_in": ["release_notes_kestrel_2_6.md"],
        },
    }],
    "count": 1,
}
C_SPLIT_EV = {"corpus_files": ["release_notes_kestrel_2_2.md",
                               "release_notes_kestrel_2_6.md",
                               "forum_thread_4111.md"]}


def c_split_packet(record, mv="1.1.0"):
    ev = dict(C_SPLIT_EV)
    if mv == "1.1.0":
        ev.update(hashes("C-001"))
    return packet("C-001", "C", j({"flags": [record], "count": 1}),
                  C_SPLIT_KEY, ev, methodology_version=mv)


class TestCitationSupportIsPerField(unittest.TestCase):

    def test_a_citation_governing_an_unreported_field_is_not_supported(self):
        """Reports `introduced_in` only, cites `removed_in`'s source too.

        Pre-fix: `allowed` was the whole union, so the second file counted as
        supported, `missing` was 0 and traceability was 1.0 - no breach.
        """
        rec = {"flag": "edge_cache_v2", "introduced_in": "2.2",
               "sources": ["release_notes_kestrel_2_2.md",
                           "release_notes_kestrel_2_6.md"]}
        r = judge.score_packet(c_split_packet(rec))
        d = r["detail"]
        self.assertEqual(d["citation_support_basis"], ["per_field_over_reported_values"])
        self.assertEqual(d["supported_citations"], 1)
        self.assertEqual(d["total_citations"], 2)
        self.assertEqual(d["missing_citations"], 0)
        self.assertEqual(d["traceability"], 0.5)
        self.assertTrue(r["zero_tolerance_breached"])
        self.assertIn("release_notes_kestrel_2_6.md",
                      [u["file"] for u in d["unsupported_citations"]])

    def test_a_run_owes_nothing_for_a_field_it_did_not_report(self):
        """Reports `introduced_in` only, cites exactly its governing source.

        Pre-fix: `removed_in`'s source was in `allowed` and uncited, so it was
        counted as a missing citation and traceability fell to 0.5 with a
        zero-tolerance breach, for a citation the run had no claim to make.
        """
        rec = {"flag": "edge_cache_v2", "introduced_in": "2.2",
               "sources": ["release_notes_kestrel_2_2.md"]}
        r = judge.score_packet(c_split_packet(rec))
        d = r["detail"]
        self.assertEqual(d["missing_citations"], 0)
        self.assertEqual(d["traceability"], 1.0)
        self.assertFalse(r["zero_tolerance_breached"])
        # coverage still falls, because an omitted field is still a mismatch
        self.assertLess(d["coverage"], 1.0)

    def test_reporting_every_field_owes_every_governing_source(self):
        rec = {"flag": "edge_cache_v2", "introduced_in": "2.2", "removed_in": "2.6",
               "sources": ["release_notes_kestrel_2_2.md"]}
        r = judge.score_packet(c_split_packet(rec))
        self.assertEqual(r["detail"]["missing_citations"], 1)
        self.assertTrue(r["zero_tolerance_breached"])

    def test_the_complete_answer_passes(self):
        rec = json.loads(j(C_SPLIT_KEY["flags"][0]))
        rec.pop("citation_support")
        r = judge.score_packet(c_split_packet(rec))
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertEqual(r["detail"]["missing_citations"], 0)
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_v1_0_0_still_replays_its_record_level_union(self):
        """What the fix changed, stated as a difference."""
        rec = {"flag": "edge_cache_v2", "introduced_in": "2.2",
               "sources": ["release_notes_kestrel_2_2.md",
                           "release_notes_kestrel_2_6.md"]}
        r = judge.score_packet(c_split_packet(rec, mv="1.0.0"))
        self.assertEqual(r["detail"]["citation_support_basis"],
                         ["v1.0.0_record_level_union"])
        self.assertEqual(r["detail"]["traceability"], 1.0)

    def test_a_key_with_no_per_field_breakdown_falls_back_to_record_level(self):
        key = {"projects": [{
            "project": "Project Halyard", "total_awarded_eur": 621500,
            "awards_included": ["GA-0001"], "awards_excluded": [],
            "sources": ["bulletin_bul_2031_01.md", "correction_CORR-002.md"],
            "citation_support": {"per_award": {"GA-0001": {
                "stated_by": "correction_CORR-002.md",
                "listed_in_bulletin": "bulletin_bul_2031_01.md"}}}}],
            "count": 1}
        ev = {"corpus_files": ["bulletin_bul_2031_01.md", "correction_CORR-002.md"],
              "document_award_ids": ["GA-0001"]}
        ev.update(hashes("C-002"))
        out = {"projects": [{k: v for k, v in key["projects"][0].items()
                             if k != "citation_support"}], "count": 1}
        r = judge.score_packet(packet("C-002", "C", j(out), key, ev,
                                      methodology_version="1.1.0"))
        self.assertEqual(r["detail"]["citation_support_basis"], ["record_level_fallback"])
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])


class TestCitationSupportParsingIsStructural(unittest.TestCase):
    """A prose string in a key may not become a mandatory governing source.

    The delivered v1.0.0 C-002 key carried a `note` inside `citation_support`.
    `_strings_in` absorbed it, so a 108-character English sentence became an
    uncitable governing source and the key's own perfect answer scored
    traceability 0.72 with 7 missing citations and a zero-tolerance breach -
    every C-002 attempt, in every condition, would have failed outright.
    """

    NOTE = ("no single file states total_awarded_eur; it is the sum of the awards "
            "listed above after applying every correction notice")

    def _key(self, extra_support):
        support = {"project": ["bulletin_bul_2031_01.md"],
                   "total_awarded_eur": ["bulletin_bul_2031_01.md",
                                         "correction_CORR-002.md"],
                   "awards_included": ["bulletin_bul_2031_01.md",
                                       "correction_CORR-002.md"],
                   "awards_excluded": []}
        support.update(extra_support)
        return {"projects": [{
            "project": "Project Halyard", "total_awarded_eur": 621500,
            "awards_included": ["GA-0001"], "awards_excluded": [],
            "sources": ["bulletin_bul_2031_01.md", "correction_CORR-002.md"],
            "citation_support": support}], "count": 1}

    def _score(self, key):
        ev = {"corpus_files": ["bulletin_bul_2031_01.md", "correction_CORR-002.md"],
              "document_award_ids": ["GA-0001"]}
        ev.update(hashes("C-002"))
        out = {"projects": [{k: v for k, v in key["projects"][0].items()
                             if k != "citation_support"}], "count": 1}
        return judge.score_packet(packet("C-002", "C", j(out), key, ev,
                                         methodology_version="1.1.0"))

    def test_a_prose_note_cannot_become_a_governing_source(self):
        r = self._score(self._key({"note": self.NOTE}))
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertEqual(r["detail"]["missing_citations"], 0)
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])
        self.assertIn(self.NOTE[:120],
                      r["detail"]["citation_support_rejected_strings"])

    def test_a_prose_string_inside_a_per_field_list_is_rejected_too(self):
        r = self._score(self._key({
            "total_awarded_eur": ["bulletin_bul_2031_01.md",
                                  "correction_CORR-002.md",
                                  "derived by summing the awards above"]}))
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

    def test_a_clean_key_rejects_nothing(self):
        r = self._score(self._key({}))
        self.assertNotIn("citation_support_rejected_strings", r["detail"])

    def test_the_filename_test_is_structural_not_a_guess(self):
        self.assertIsNotNone(judge._source_like("release_notes_kestrel_2_2.md"))
        self.assertIsNotNone(judge._source_like("registry_export_2032-02.csv"))
        self.assertIsNone(judge._source_like(self.NOTE))
        self.assertIsNone(judge._source_like("no single file states this"))
        self.assertIsNone(judge._source_like(""))
        self.assertIsNone(judge._source_like(42))


class TestDeliveredCKeysRoundTrip(unittest.TestCase):
    """Score each shipped v1.1.0 workload-C key against its own payload.

    This is the test that would have caught the C-002 `note`: the key's own
    perfect answer must be traceable, or the task is unpassable by anyone.
    """

    KEYS_V11 = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "tasks", "TASK_SET_v1.1.0", "answer_keys"))
    CORPUS_C = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "tasks", "TASK_SET_v1.1.0", "corpora", "research_c"))
    SPEC = {"C-001": ("flags", "flag"), "C-002": ("projects", "project"),
            "C-003": ("plugins", "plugin_id")}

    def test_every_delivered_c_key_scores_its_own_answer_at_1_0(self):
        if not os.path.isdir(self.KEYS_V11) or not os.path.isdir(self.CORPUS_C):
            self.skipTest("v1.1.0 answer keys or corpus not present")
        corpus_files = sorted(os.listdir(self.CORPUS_C))
        for tid, (arr, _idf) in sorted(self.SPEC.items()):
            path = os.path.join(self.KEYS_V11, tid + ".json")
            if not os.path.exists(path):
                continue
            with self.subTest(task=tid):
                with open(path, encoding="utf-8") as fh:
                    key = json.load(fh)
                out = {arr: [{k: v for k, v in rec.items() if k != "citation_support"}
                             for rec in key[arr]],
                       "count": key.get("count", len(key[arr]))}
                ev = {"corpus_files": corpus_files}
                ev.update(hashes(tid))
                if tid == "C-002":
                    ev["document_award_ids"] = sorted(
                        {a for rec in key[arr]
                         for a in rec.get("awards_included", []) +
                         rec.get("awards_excluded", [])})
                if tid == "C-003":
                    ev["registry_plugin_ids"] = [rec["plugin_id"] for rec in key[arr]]
                r = judge.score_packet(packet(tid, "C", j(out), key, ev,
                                              methodology_version="1.1.0"))
                self.assertEqual(r["detail"]["traceability"], 1.0,
                                 json.dumps(r["detail"].get("unsupported_citations"))[:400])
                self.assertEqual(r["detail"]["missing_citations"], 0)
                self.assertEqual(r["detail"]["coverage"], 1.0)
                self.assertNotIn("citation_support_rejected_strings", r["detail"])
                self.assertEqual(r["outcome"], "PASS", r["failure_reason"])

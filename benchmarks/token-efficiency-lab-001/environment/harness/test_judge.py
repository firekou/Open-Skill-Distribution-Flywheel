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
           required_evidence=None, **extra) -> dict:
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
    }
    p.update(extra)
    return p


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
        key = {"task_id": "C-001", "derived_by": "answer-key-builder",
               "flags": [{"flag": "adaptive_shard_split", "introduced_in": "2.2",
                          "removed_in": None,
                          "sources": ["release_notes_kestrel_2_2.md"],
                          "citation_support": {
                              "introduced_in": ["release_notes_kestrel_2_2.md"],
                              "removed_in": []},
                          "non_authoritative_files_stating_the_same_introduced_in":
                              ["forum_thread_4111.md"]}],
               "count": 1}
        ev = {"corpus_files": ["release_notes_kestrel_2_2.md", "forum_thread_4111.md"]}
        good = {"flags": [{"flag": "adaptive_shard_split", "introduced_in": "2.2",
                          "removed_in": None,
                          "sources": ["release_notes_kestrel_2_2.md"]}], "count": 1}
        r = judge.score_packet(packet("C-001", "C", j(good), key, ev))
        self.assertEqual(r["detail"]["traceability"], 1.0)
        self.assertEqual(r["quality_score"], 1.0)
        self.assertTrue(r["task_success"])

        bad = json.loads(j(good))
        bad["flags"][0]["sources"] = ["forum_thread_4111.md"]
        r = judge.score_packet(packet("C-001", "C", j(bad), key, ev))
        self.assertLess(r["detail"]["traceability"], 1.0)
        self.assertTrue(r["zero_tolerance_breached"])

    def test_c002_per_award_support_has_no_field_breakdown(self):
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
        ev = {"turn_count": 18,
              "catalog_part_ids": [r["part_id"] for r in key["bom"]],
              "halberd_part_ids": []}  # evidence is mandatory: see E_REQUIRED_EVIDENCE
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

"""Regression tests for the harness modules repaired in the v1.1.0 round.

Each test below corresponds to a defect that was real. A test that would also pass against the
broken code is not a regression test, so where the old behaviour is expressible it is asserted
against directly.

Run: `python3 -m unittest harness.test_harness` from /lab, or `python3 -m unittest test_harness`
from inside harness/.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import evidence as ev  # noqa: E402
from harness import manifest as mf  # noqa: E402
from harness.aggregate import (  # noqa: E402
    FAIL_QUALITY, INVALID, PASS, Cell, cost_per_successful_task, pair_attempts, select_strongest,
)
from harness.pricing import ADDITIONAL, INCLUDED, PricingError, Rate  # noqa: E402
from harness.pricing_preflight import check  # noqa: E402


def _task(tid="E-003", wl="E", paths=None, turns=None):
    t = {"task_id": tid, "workload": wl, "input": {"corpus_paths": paths or []}}
    if turns:
        t["input"]["turn_count"] = turns
    return t


class TestEvidenceFailsClosedOnContent(unittest.TestCase):
    """RT-02. An empty container passed every type check in v1.0.0 and silently disarmed
    workload E's zero-tolerance criteria, so an ineligible assignment scored task_success: true."""

    FULL = {"turns": [{"turn": 1}], "corpus_hashes_before": {"a": "1"},
            "corpus_hashes_after": {"a": "1"}, "shifts": {"SH-1": {}}, "roster": {"PR-1": {}}}

    def test_complete_evidence_is_accepted(self):
        ev.validate(dict(self.FULL), _task())

    def test_empty_container_is_refused_not_merely_absent(self):
        for field in ("shifts", "roster", "turns", "corpus_hashes_before"):
            with self.subTest(field=field):
                bad = dict(self.FULL, **{field: type(self.FULL[field])()})
                with self.assertRaises(ev.EvidenceError) as c:
                    ev.validate(bad, _task())
                self.assertIn("empty", str(c.exception))
                self.assertIn(field, str(c.exception))

    def test_missing_and_empty_are_reported_differently(self):
        with self.assertRaises(ev.EvidenceError) as miss:
            ev.validate({k: v for k, v in self.FULL.items() if k != "roster"}, _task())
        with self.assertRaises(ev.EvidenceError) as empty:
            ev.validate(dict(self.FULL, roster={}), _task())
        self.assertIn("missing:", str(miss.exception))
        self.assertIn("empty:", str(empty.exception))

    def test_the_error_says_invalid_not_failure(self):
        with self.assertRaises(ev.EvidenceError) as c:
            ev.validate({}, _task())
        self.assertIn("INVALID", str(c.exception))
        self.assertIn("not a pass and not a quality failure", str(c.exception))


class TestTurnCompleteness(unittest.TestCase):
    """RT-13. A byte-perfect E-002 runbook with a violation at turn 8 scored 1.0 and passed
    when `turns` was omitted."""

    def test_complete_transcript_accepted(self):
        ev.assert_turns_complete([{"turn": i} for i in range(1, 5)], 4)

    def test_truncated_rejected(self):
        with self.assertRaises(ev.EvidenceError) as c:
            ev.assert_turns_complete([{"turn": i} for i in range(1, 3)], 4)
        self.assertIn("hides every violation after the cut", str(c.exception))

    def test_reordered_rejected(self):
        with self.assertRaises(ev.EvidenceError):
            ev.assert_turns_complete([{"turn": 2}, {"turn": 1}, {"turn": 3}], 3)

    def test_duplicated_rejected(self):
        with self.assertRaises(ev.EvidenceError):
            ev.assert_turns_complete([{"turn": 1}, {"turn": 1}, {"turn": 3}], 3)

    def test_empty_rejected(self):
        with self.assertRaises(ev.EvidenceError):
            ev.assert_turns_complete([], 4)


class TestAuditAttribution(unittest.TestCase):
    """A shared audit log is normal. What must never happen is one attempt's calls scoring
    another's, or an unattributable call being silently dropped - dropping one would undercount
    wrong-tool use, which is zero-tolerance."""

    CALLS = [{"run_id": "r1", "tool": "a"}, {"run_id": "r2", "tool": "b"},
             {"run_id": "r1", "tool": "c"}]

    def test_filters_to_this_run(self):
        self.assertEqual([c["tool"] for c in ev.filter_audit_to_run(self.CALLS, "r1")], ["a", "c"])

    def test_a_run_with_no_entries_is_refused(self):
        with self.assertRaises(ev.EvidenceError) as c:
            ev.filter_audit_to_run(self.CALLS, "r9")
        self.assertIn("different states", str(c.exception))

    def test_an_unattributable_entry_is_refused_not_dropped(self):
        with self.assertRaises(ev.EvidenceError) as c:
            ev.filter_audit_to_run(self.CALLS + [{"tool": "x"}], "r1")
        self.assertIn("undercount wrong-tool use", str(c.exception))


class TestEvidenceIsTreatmentNeutral(unittest.TestCase):
    """required_evidence reaches the Quality Judge, so anything identifying in it defeats the
    blind as surely as a metadata field would."""

    def test_clean_evidence_passes(self):
        ev.assert_treatment_neutral({"valid_symbols": ["a.b"], "turns": [{"turn": 1}]})

    def test_leaks_are_caught_at_any_depth(self):
        for probe in ({"meta": {"cost": 0.1}},
                      {"turns": [{"turn": 1, "condition": "C5"}]},
                      {"total_tokens": 10},
                      {"a": {"b": {"c": {"candidate_name": "x"}}}}):
            with self.subTest(probe=probe):
                with self.assertRaises(ev.EvidenceError):
                    ev.assert_treatment_neutral(probe)


class TestCorpusModificationDetected(unittest.TestCase):
    """RT-08. `corpus_modified` was read for workload D only, so a corpus-rewriting
    optimisation scored clean on the other thirteen tasks."""

    BEFORE = {"corpora/x.py": "aaa", "corpora/y.py": "bbb"}

    def test_untouched(self):
        self.assertEqual(ev.compare_corpus_hashes(self.BEFORE, dict(self.BEFORE)), [])

    def test_modified_added_deleted_all_detected(self):
        self.assertEqual(
            ev.compare_corpus_hashes(self.BEFORE, {"corpora/x.py": "ZZZ", "corpora/y.py": "bbb"}),
            ["corpora/x.py"])
        self.assertEqual(ev.compare_corpus_hashes(self.BEFORE, {"corpora/x.py": "aaa"}),
                         ["corpora/y.py"])
        self.assertIn("corpora/z.py",
                      ev.compare_corpus_hashes(self.BEFORE, dict(self.BEFORE, **{"corpora/z.py": "c"})))


class TestPricingHonoursTheVendorConvention(unittest.TestCase):
    """The meter treated `cached > input` as an error, encoding the OpenAI/DeepSeek convention as
    arithmetic. Anthropic reports cache reads as ADDITIONAL - its own example has input_tokens 105
    against cache_read_input_tokens 7123."""

    def test_additional_convention_allows_cached_above_input(self):
        r = Rate(2.0, 10.0, 0.2, cached_tokens_in_input=ADDITIONAL, model_key="anthropic/x")
        got = r.cost(105, 500, 7123)
        expected = 105 * 2.0 / 1e6 + 500 * 10.0 / 1e6 + 7123 * 0.2 / 1e6
        self.assertAlmostEqual(got, expected, places=12)

    def test_included_convention_subtracts_cached_from_input(self):
        r = Rate(2.0, 12.0, 0.2, cached_tokens_in_input=INCLUDED, model_key="openai/x")
        got = r.cost(10000, 500, 8000)
        expected = 2000 * 2.0 / 1e6 + 500 * 12.0 / 1e6 + 8000 * 0.2 / 1e6
        self.assertAlmostEqual(got, expected, places=12)

    def test_the_two_conventions_give_different_costs(self):
        a = Rate(2.0, 10.0, 0.2, cached_tokens_in_input=ADDITIONAL, model_key="a").cost(10000, 0, 8000)
        i = Rate(2.0, 10.0, 0.2, cached_tokens_in_input=INCLUDED, model_key="i").cost(10000, 0, 8000)
        self.assertNotAlmostEqual(a, i)

    def test_an_undeclared_convention_is_refused_not_defaulted(self):
        with self.assertRaises(PricingError) as c:
            Rate(1.0, 5.0, 0.1, cached_tokens_in_input="undeclared", model_key="x/y").cost(100, 10, 50)
        self.assertIn("misprices by the size of the cache", str(c.exception))

    def test_cached_tokens_with_no_cache_rate_is_unpriceable(self):
        with self.assertRaises(PricingError) as c:
            Rate(1.0, 5.0, None, cached_tokens_in_input=INCLUDED, model_key="x/y").cost(100, 10, 50)
        self.assertIn("unpriceable", str(c.exception))


class TestPricingPreflightBlocks(unittest.TestCase):
    """CR-001-C. A missing rate is never zero, and `not_applicable` without evidence is a claim,
    not a fact."""

    def _model(self, **over):
        m = {
            "plan": "standard / short context",
            "provenance": {"source_url": "https://x", "retrieved_on": "2026-09-16",
                           "currency": "USD", "billing_unit": "1M tokens"},
            "applicable_dimensions": ["input", "output", "cache_read", "cache_write"],
            "rates": {"input": 1.0, "output": 5.0, "cache_read": 0.1, "cache_write": 1.25},
            "not_applicable": {"cache_ttl": {"evidence": "no TTL tiers on the page"},
                               "other_fees": {"evidence": "none listed"}},
            "token_inclusion": {"cached_tokens_in_input": {"value": "included", "evidence": "q"},
                                "reasoning_tokens_in_output": {"value": "included", "evidence": "q"},
                                "reports_total": {"value": "yes", "evidence": "q"}},
        }
        m.update(over)
        return m

    def _snap(self, model):
        return {"pricing_snapshot_id": "PS-TEST", "models": {"p/m": model}}

    def test_complete_model_passes(self):
        self.assertEqual(check(self._snap(self._model()), ["p/m"]).verdict, "PASS")

    def test_a_missing_cache_rate_blocks(self):
        m = self._model()
        del m["rates"]["cache_read"]
        r = check(self._snap(m), ["p/m"])
        self.assertEqual(r.verdict, "BLOCK")
        self.assertTrue(any("never zero" in f.message for f in r.findings))

    def test_not_applicable_without_evidence_blocks(self):
        m = self._model(applicable_dimensions=["input", "output"])
        m["not_applicable"] = {"cache_ttl": {"evidence": "x"}, "other_fees": {"evidence": "x"}}
        r = check(self._snap(m), ["p/m"])
        self.assertEqual(r.verdict, "BLOCK")
        self.assertTrue(any("different statements" in f.message for f in r.findings))

    def test_undeclared_token_inclusion_blocks(self):
        m = self._model()
        del m["token_inclusion"]["cached_tokens_in_input"]
        self.assertEqual(check(self._snap(m), ["p/m"]).verdict, "BLOCK")

    def test_a_model_the_plan_uses_but_the_snapshot_lacks_blocks(self):
        self.assertEqual(check(self._snap(self._model()), ["p/absent"]).verdict, "BLOCK")

    def test_a_blocked_rate_blocks(self):
        m = self._model()
        m["rates"]["cache_read"] = "BLOCKED"
        self.assertEqual(check(self._snap(m), ["p/m"]).verdict, "BLOCK")


def _att(tid, wl, cond, outcome, rep=1, cost=1.0, cache="cold"):
    return {"run_id": f"{tid}-{cond}-r{rep}", "task_id": tid, "workload": wl, "condition": cond,
            "repetition": rep, "outcome": outcome, "cost": cost, "cache_state": cache,
            "task_version": "1.1.0"}


class TestCellLevel(unittest.TestCase):
    """CR-001-B acceptance cases B-1 to B-3, plus the denominator rule."""

    def _cell(self, outcomes, planned=3):
        c = Cell("D", "C1", planned=planned)
        c.attempts = [_att(f"D-00{i}", "D", "C1", o) for i, o in enumerate(outcomes, 1)]
        return c

    def test_B1_two_of_three_fails(self):
        v = self._cell([PASS, PASS, FAIL_QUALITY]).verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertAlmostEqual(v["success_rate"], 2 / 3, places=3)

    def test_B2_three_of_three_passes_but_claims_nothing_about_the_rate(self):
        v = self._cell([PASS, PASS, PASS]).verdict()
        self.assertEqual(v["cell_verdict"], "PASS")
        self.assertIn("does NOT mean the true success rate", v["rate_claim_warning"])

    def test_B3_invalid_is_not_a_success_and_stays_in_the_denominator(self):
        v = self._cell([PASS, PASS, INVALID]).verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertAlmostEqual(v["success_rate"], 2 / 3, places=3)
        self.assertEqual(v["counts"][INVALID], 1)

    def test_a_planned_attempt_with_no_record_still_counts(self):
        v = self._cell([PASS, PASS]).verdict()
        self.assertEqual(v["recorded"], 2)
        self.assertEqual(v["planned"], 3)
        self.assertAlmostEqual(v["success_rate"], 2 / 3, places=3)
        self.assertEqual(v["cell_verdict"], "FAIL")

    def test_only_workload_d_has_a_cell_threshold(self):
        for wl in "ABCE":
            c = Cell(wl, "C1", planned=3)
            self.assertIsNone(c.threshold, wl)


class TestCostPerSuccessfulTask(unittest.TestCase):
    """Quantity 9. Failures are in the numerator; only passes are in the denominator."""

    def test_failed_attempts_still_cost_money(self):
        c = Cell("A", "C2", planned=3)
        c.attempts = [_att("A-1", "A", "C2", PASS, cost=2.0),
                      _att("A-2", "A", "C2", FAIL_QUALITY, cost=3.0),
                      _att("A-3", "A", "C2", INVALID, cost=1.0)]
        self.assertAlmostEqual(cost_per_successful_task(c), 6.0)

    def test_a_cell_with_no_passes_costs_infinity(self):
        c = Cell("A", "C2", planned=1)
        c.attempts = [_att("A-1", "A", "C2", FAIL_QUALITY, cost=5.0)]
        self.assertEqual(cost_per_successful_task(c), float("inf"))


class TestPairingAndSelection(unittest.TestCase):
    def test_cold_is_never_compared_with_warm(self):
        t = [_att("A-1", "A", "C2", PASS, cache="warm")]
        b = [_att("A-1", "A", "C0", PASS, cache="cold")]
        pairs, unpaired = pair_attempts(t, b)
        self.assertEqual(pairs, [])
        self.assertIn("never compared", unpaired[0])

    def test_an_unpaired_attempt_is_visible_not_dropped(self):
        t = [_att("A-9", "A", "C2", PASS)]
        pairs, unpaired = pair_attempts(t, [])
        self.assertEqual(len(unpaired), 1)

    def test_the_largest_saving_is_rejected_when_its_cell_contains_a_failure(self):
        cells = []
        for cond, outs in (("C1", [PASS] * 3), ("C2", [PASS, PASS, FAIL_QUALITY]),
                           ("C4", [PASS] * 3), ("C2+C4", [PASS] * 3)):
            c = Cell("A", cond, planned=3)
            c.attempts = [_att(f"A-{i}", "A", cond, o) for i, o in enumerate(outs, 1)]
            cells.append(c)
        deltas = {("A", "C1"): 0.30, ("A", "C2"): 0.90, ("A", "C4"): 0.40, ("A", "C2+C4"): 0.95}
        s = select_strongest(cells, deltas)
        self.assertEqual(s["chosen"], [("A", "C4"), ("A", "C1")])
        rejected = dict(s["rejected"])
        self.assertIn("FAIL_QUALITY", rejected[("A", "C2")])
        self.assertIn("single-intervention", rejected[("A", "C2+C4")])

    def test_a_shortfall_is_recorded_not_filled_with_an_ineligible_cell(self):
        c = Cell("A", "C1", planned=3)
        c.attempts = [_att("A-1", "A", "C1", PASS)] * 3
        s = select_strongest([c], {("A", "C1"): 0.5})
        self.assertEqual(len(s["chosen"]), 1)
        self.assertIn("Do NOT substitute", s["shortfall"])


class TestManifestCatchesWhatTheOldOneMissed(unittest.TestCase):
    """RT-12. The v1.0.0 manifest covered 155 files and not one answer key, so a key could change
    after the freeze and `sha256sum -c` would still report everything OK."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.ts, self.env = self.tmp / "ts", self.tmp / "env"
        for d in ("tasks/A", "corpora", "answer_keys/scripts"):
            (self.ts / d).mkdir(parents=True)
        (self.ts / "tasks/A/A-001.json").write_text('{"task_id": "A-001"}')
        (self.ts / "corpora/c.txt").write_text("corpus")
        (self.ts / "answer_keys/A-001.json").write_text('{"count": 1}')
        (self.ts / "answer_keys/scripts/derive_A.py").write_text("# derive")
        (self.ts / "SCORING_SPEC.md").write_text("spec")
        (self.ts / "README.md").write_text("readme")
        (self.env / "harness").mkdir(parents=True)
        (self.env / "harness/judge.py").write_text("# judge")
        for f in ("evidence.py", "blind.py", "meter.py", "pricing.py", "record.py"):
            (self.env / "harness" / f).write_text("# " + f)
        (self.env / "run_record_schema.json").write_text("{}")
        self.man = self.tmp / "MANIFEST.json"
        mf.build(self.ts, self.env).save(self.man)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _verify(self):
        return mf.verify(self.man, self.ts, self.env)

    def test_untouched_verifies(self):
        self.assertTrue(self._verify()["ok"])

    def test_a_modified_answer_key_is_caught_in_the_answer_key_group(self):
        (self.ts / "answer_keys/A-001.json").write_text('{"count": 2}')
        r = self._verify()
        self.assertFalse(r["ok"])
        self.assertEqual(r["groups"]["answer_key"]["modified"], ["answer_keys/A-001.json"])
        self.assertTrue(r["groups"]["task_set"]["ok"], "a key change must not look like a task change")

    def test_an_added_file_is_caught(self):
        (self.ts / "answer_keys/A-999.json").write_text("{}")
        self.assertEqual(self._verify()["groups"]["answer_key"]["added"], ["answer_keys/A-999.json"])

    def test_a_deleted_file_is_caught(self):
        (self.ts / "tasks/A/A-001.json").unlink()
        self.assertEqual(self._verify()["groups"]["task_set"]["deleted"], ["tasks/A/A-001.json"])

    def test_a_modified_scorer_is_caught_separately_from_the_task_set(self):
        (self.env / "harness/judge.py").write_text("# tampered")
        r = self._verify()
        self.assertEqual(r["groups"]["scorer"]["modified"], ["harness/judge.py"])
        self.assertTrue(r["groups"]["task_set"]["ok"])

    def test_the_hashes_are_distinct(self):
        h = json.loads(self.man.read_text())["hashes"]
        self.assertEqual(len(set(h.values())), len(h), "separate groups must give separate hashes")

    def test_the_manifest_does_not_contain_its_own_digest(self):
        self.assertNotIn(mf.Manifest(json.loads(self.man.read_text())).digest(), self.man.read_text())

    def test_no_file_is_claimed_by_two_groups(self):
        m = mf.build(self.ts, self.env).data
        seen = set()
        for g in m["groups"].values():
            for f in g["files"]:
                key = (id(g), f)
                del key
            overlap = seen & set(g["files"])
            self.assertFalse(overlap, f"claimed twice: {overlap}")
            seen |= set(g["files"])


if __name__ == "__main__":
    unittest.main()

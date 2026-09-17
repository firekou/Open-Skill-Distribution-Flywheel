"""Regression tests for the harness modules repaired in the v1.1.0 round.

Each test below corresponds to a defect that was real. A test that would also pass against the
broken code is not a regression test, so where the old behaviour is expressible it is asserted
against directly.

Run: `python3 -m unittest harness.test_harness` from /lab, or `python3 -m unittest test_harness`
from inside harness/.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import evidence as ev  # noqa: E402
from harness import finalize as fin  # noqa: E402
from harness import manifest as mf  # noqa: E402
from harness.aggregate import (  # noqa: E402
    AggregateError, FAIL_QUALITY, INVALID, PASS, Cell, PlannedAttempts, build_cells,
    cost_per_successful_task, pair_attempts, select_strongest,
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
    return {"run_id": f"{tid}-{cond}-r{rep}", "attempt_id": f"{tid}-{cond}-r{rep}",
            "task_id": tid, "workload": wl, "condition": cond,
            "repetition": rep, "outcome": outcome, "cost": cost, "cache_state": cache,
            "task_version": "1.1.0"}


def _planned_cell(wl, cond, planned, attempts):
    """A Cell whose identity IS checked against a planned set, as R2-01/R2-02 now require.

    `expected` is the planned attempt id set. Where a test deliberately records fewer attempts
    than planned, the shortfall is carried as planned ids that produced no record — which is what
    a missing attempt actually is, and what a re-run of another task must not stand in for.
    """
    observed = [a["attempt_id"] for a in attempts]
    missing = [f"{wl}-{cond}-planned-{i}" for i in range(planned - len(observed))]
    return Cell(wl, cond, planned=planned, attempts=attempts,
                expected=frozenset(observed + missing))


class TestCellLevel(unittest.TestCase):
    """CR-001-B acceptance cases B-1 to B-3, plus the denominator rule."""

    def _cell(self, outcomes, planned=3):
        return _planned_cell("D", "C1", planned,
                             [_att(f"D-00{i}", "D", "C1", o) for i, o in enumerate(outcomes, 1)])

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
        c = _planned_cell("A", "C2", 3, [_att("A-1", "A", "C2", PASS, cost=2.0),
                                        _att("A-2", "A", "C2", FAIL_QUALITY, cost=3.0),
                                        _att("A-3", "A", "C2", INVALID, cost=1.0)])
        self.assertAlmostEqual(cost_per_successful_task(c), 6.0)

    def test_a_cell_with_no_passes_costs_infinity(self):
        c = _planned_cell("A", "C2", 1, [_att("A-1", "A", "C2", FAIL_QUALITY, cost=5.0)])
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
            cells.append(_planned_cell("A", cond, 3,
                         [_att(f"A-{i}", "A", cond, o) for i, o in enumerate(outs, 1)]))
        deltas = {("A", "C1"): 0.30, ("A", "C2"): 0.90, ("A", "C4"): 0.40, ("A", "C2+C4"): 0.95}
        s = select_strongest(cells, deltas)
        self.assertEqual(s["chosen"], [("A", "C4"), ("A", "C1")])
        rejected = dict(s["rejected"])
        # The rejection now quotes the cell's own verdict rather than a second, independent scan
        # of the records (ADV-B), so it names the quality failure in the verdict's words.
        self.assertIn("cell verdict FAIL", rejected[("A", "C2")])
        self.assertIn("failed quality", rejected[("A", "C2")])
        self.assertIn("single-intervention", rejected[("A", "C2+C4")])

    def test_a_shortfall_is_recorded_not_filled_with_an_ineligible_cell(self):
        # Three DISTINCT attempts. This used to repeat one object three times, which is exactly
        # the duplicate-inflation shape ADV-A found; the cell now fails on it, and a test should
        # not depend on a defect to set up its fixture.
        c = _planned_cell("A", "C1", 3, [_att(f"A-{i}", "A", "C1", PASS) for i in (1, 2, 3)])
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


# --------------------------------------------------------------------------- the seam (NEW-07)

LAB_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
TASK_SET = LAB_ROOT / "tasks" / "TASK_SET_v1.1.0"
SNAPSHOT = LAB_ROOT / "evidence" / "PRICING_SNAPSHOT_PS-2026-09-16.json"


@unittest.skipUnless(TASK_SET.is_dir() and SNAPSHOT.is_file(), "task set not available")
class TestRunnerToJudgeSeam(unittest.TestCase):
    """NEW-07 — the seam nobody tested, which is why four defects lived in it.

    240 judge tests all hand-build their packets, so none of them exercised
    `harness.runner` → `blind.build_packet` → `judge.score_packet`. The single integration proof
    was `tools/golden_run.py`, and it returned 17/17 PASS **because** the runner stamped the wrong
    methodology version and the judge therefore applied the more permissive v1.0.0 rulebook — a
    green integration test whose greenness was caused by the defect it should have caught.

    This class runs the real chain and asserts the two things that would have caught it:
    the **resolved version** on every packet, and PASS under **those** rules.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(LAB_ROOT / "tools"))
        cls.tmp = pathlib.Path(tempfile.mkdtemp())
        import subprocess
        r = subprocess.run(
            [sys.executable, str(LAB_ROOT / "tools" / "golden_run.py"),
             "--task-root", str(TASK_SET), "--out", str(cls.tmp)],
            capture_output=True, text=True)
        if r.returncode:
            raise unittest.SkipTest(f"golden_run failed: {r.stderr[-400:]}")

        from harness.blind import BlindMapping
        from harness.pricing import PricingSnapshot
        from harness.runner import run_one
        cls.records, cls.packets = [], []
        mapping = BlindMapping("lab001-seam-salt-2026-09-16")
        mapping.assign(["C0"])
        snap = PricingSnapshot(SNAPSHOT)
        plan = json.loads((cls.tmp / "PLAN.json").read_text())
        for item in plan:
            rec, pkt = run_one(
                task_id=item["task_id"], condition=item["condition"], repetition=1,
                task_root=TASK_SET, fixture=cls.tmp / "FIXTURE.json", snapshot=snap,
                evidence_root=cls.tmp / "raw", mapping=mapping, run_class="dry_run",
                environment_id="seam-test", container_digest="sha256:seam",
                task_set_hash="x", answer_key_hash="y",
                audit_path=cls.tmp / "TOOL_AUDIT.jsonl")
            cls.records.append(rec)
            cls.packets.append(pkt)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_all_seventeen_tasks_reach_a_packet(self):
        self.assertEqual(len(self.packets), 17)

    def test_every_packet_declares_the_version_the_harness_implements(self):
        from harness import METHODOLOGY_VERSION
        versions = {p.get("methodology_version") for p in self.packets}
        self.assertEqual(versions, {METHODOLOGY_VERSION})
        self.assertEqual(METHODOLOGY_VERSION, "1.1.0")

    def test_no_packet_carries_a_version_literal_from_somewhere_else(self):
        """The defect was a literal in runner.py. Records and packets must agree."""
        from harness import METHODOLOGY_VERSION
        for rec, pkt in zip(self.records, self.packets):
            self.assertEqual(rec["methodology_version"], METHODOLOGY_VERSION, rec["run_id"])
            self.assertEqual(pkt["methodology_version"], METHODOLOGY_VERSION, rec["run_id"])

    def test_every_correct_answer_passes_under_those_rules(self):
        """17/17 PASS is only meaningful together with the version assertion above."""
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import judge
        failures = []
        for pkt in self.packets:
            r = judge.score_packet(pkt)
            if r["outcome"] != "PASS":
                failures.append((pkt["task_id"], r["outcome"], r.get("failure_reason")))
        self.assertEqual(failures, [], f"{len(failures)} of 17 correct answers did not pass")

    def test_a_violation_in_a_middle_turn_fails_a_byte_perfect_final_answer(self):
        """The case that used to pass: E-002's answer is untouched, turn 8 breaches V2."""
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import judge
        e2 = next(p for p in self.packets if p["task_id"] == "E-002")
        clean = judge.score_packet(e2)
        self.assertEqual(clean["outcome"], "PASS")

        dirty = json.loads(json.dumps(e2))
        turns = dirty["required_evidence"]["turns"]
        self.assertGreaterEqual(len(turns), 8, "the transcript must reach turn 8 to test this")
        turns[7]["text"] = "kestrel-search is just in wave 3."
        scored = judge.score_packet(dirty)
        self.assertEqual(scored["outcome"], "FAIL_QUALITY")
        self.assertTrue(scored["zero_tolerance_breached"])

    def test_the_packet_carries_evidence_the_scorer_requires(self):
        """NEW-02: five fields were named in the contract and produced by nobody."""
        needed = {"B-002": "document_incident_ids", "B-003": "document_req_ids",
                  "C-001": "corpus_files", "C-002": "document_award_ids",
                  "C-003": "registry_plugin_ids"}
        for pkt in self.packets:
            f = needed.get(pkt["task_id"])
            if f:
                got = pkt["required_evidence"].get(f)
                self.assertTrue(got, f"{pkt['task_id']}: {f} missing or empty")

    def test_no_packet_leaks_anything_identifying(self):
        from harness.blind import assert_blind
        for pkt in self.packets:
            assert_blind(pkt, ["rtk", "headroom", "paritok", "lean-ctx", "entroly", "tokentab"])

    def test_the_corpus_access_log_shape_the_judge_reads(self):
        """NEW-04: the producer emitted list[dict] and the judge matched list[str]."""
        for pkt in self.packets:
            log = pkt["required_evidence"].get("corpus_access_log")
            if log:
                self.assertTrue(all(isinstance(x, str) for x in log),
                                f"{pkt['task_id']}: corpus_access_log must be list[str]")


class TestAdversarialReviewFindings(unittest.TestCase):
    """The external adversarial review of commit 62a16a4, reproduced then closed.

    Every case below FAILED on that commit with a real counterexample the reviewer ran, not with
    a reading of the code. They are kept as the regression that the reviewer's script would be if
    it lived in the repo. Four of them share one shape: a rule the prose stated, that no code on
    the path from record to published number actually applied.
    """

    PLAN = [{"workload": "D", "condition": "C1", "planned_attempts": 3}]

    def _rec(self, **kw):
        r = {"run_id": "same", "task_id": "D-001", "workload": "D", "condition": "C1",
             "repetition": 1, "outcome": PASS, "cost": 1.0}
        r.update(kw)
        return r

    def test_a_duplicated_record_cannot_manufacture_a_success(self):
        """3/3 PASS built from ONE passing attempt copied three times."""
        with self.assertRaises(AggregateError) as cm:
            build_cells([self._rec() for _ in range(3)], self.PLAN)
        self.assertIn("duplicate", str(cm.exception))

    def test_more_records_than_planned_is_refused(self):
        """Four copies gave success_rate 1.3333 and still reported PASS."""
        with self.assertRaises(AggregateError) as cm:
            build_cells([self._rec() for _ in range(4)], self.PLAN)
        self.assertIn("duplicate", str(cm.exception))

    def test_duplicates_are_caught_at_the_cell_too_not_only_at_load(self):
        # expected is supplied, so the ONLY thing wrong here is the duplication itself.
        c = Cell("D", "C1", planned=3, attempts=[self._rec() for _ in range(3)],
                 expected=frozenset({"D-001-C1-r1", "x2", "x3"}))
        v = c.verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertTrue(any("duplicate" in r for r in v["reasons"]), v["reasons"])

    def test_a_distinct_attempt_set_still_passes(self):
        """The fix must reject duplicates, not every full cell.

        Updated for R2-01: a cell is now reportable only when its attempt identities come from a
        frozen plan, so the control supplies one. Without it the cell correctly fails — being
        unverified is itself a finding.
        """
        reg = PlannedAttempts.from_ids({
            f"D-00{i}-C1-r1": {"workload": "D", "condition": "C1", "repetition": 1,
                               "task_id": f"D-00{i}"} for i in (1, 2, 3)})
        recs = [self._rec(run_id=f"r{i}", task_id=f"D-00{i}", attempt_id=f"D-00{i}-C1-r1")
                for i in (1, 2, 3)]
        v = build_cells(recs, self.PLAN, registry=reg)[0].verdict()
        self.assertEqual(v["cell_verdict"], "PASS", v["reasons"])
        self.assertTrue(v["identity_verified"])

    def test_an_unverified_cell_is_not_reportable(self):
        """R2-01: the same three good records, with nobody checking them against a plan."""
        recs = [self._rec(run_id=f"r{i}", task_id=f"D-00{i}", attempt_id=f"D-00{i}-C1-r1")
                for i in (1, 2, 3)]
        v = build_cells(recs, self.PLAN)[0].verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertFalse(v["identity_verified"])

    def test_a_failed_cell_is_never_selected_for_reproduction(self):
        """1 of 3 planned attempts recorded: verdict FAIL, yet it was chosen as a winner."""
        c = build_cells([self._rec()], self.PLAN)[0]
        self.assertEqual(c.verdict()["cell_verdict"], "FAIL")
        self.assertEqual(select_strongest([c], {("D", "C1"): 0.9})["chosen"], [])

    def test_a_missing_cost_stops_the_economic_number_instead_of_reading_as_zero(self):
        c = build_cells([{k: v for k, v in self._rec().items() if k != "cost"}], self.PLAN)[0]
        with self.assertRaises(AggregateError) as cm:
            cost_per_successful_task(c)
        self.assertIn("no cost", str(cm.exception))

    def test_an_unadjudicated_possible_violation_blocks_its_cell(self):
        """The attempt may legitimately be PASS; the CELL is not reportable until it is ruled on."""
        c = build_cells([self._rec(pending_adjudication=True)]
                        + [self._rec(run_id="r2", task_id="D-002"),
                           self._rec(run_id="r3", task_id="D-003")], self.PLAN)[0]
        v = c.verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertEqual(v["pending_adjudication"], ["same"])
        self.assertTrue(any("adjudication" in r for r in v["reasons"]), v["reasons"])

    def test_the_published_tie_break_and_the_implemented_one_agree(self):
        """v1.1.0 section 7.7 step 4 orders ties by smaller variance; the sort key had none."""
        cells = []
        for cond in ("C1", "C2"):
            cells.append(_planned_cell("A", cond, 3,
                         [_att(f"A-{i}", "A", cond, PASS) for i in (1, 2, 3)]))
        tied = {("A", "C1"): 0.5, ("A", "C2"): 0.5}
        s = select_strongest(cells, tied, variances={("A", "C1"): 0.9, ("A", "C2"): 0.1})
        self.assertEqual(s["chosen"][0], ("A", "C2"), "the smaller variance must win the tie")


class TestVersionConflictIsRefused(unittest.TestCase):
    """The root-cause defence the repair report claimed, and did not have.

    Moving the runner's version literal into one constant lowered the chance of writing the wrong
    string again. It closed nothing: the downgrade needs only ONE stale field to disagree, and
    `resolve_methodology_version` took the first candidate it could parse and never compared the
    rest. A packet stamped 1.0.0 carrying a 1.1.0 answer key scored under the old rulebook.
    """

    def _conflicted(self, top):
        import test_judge as t
        p = t.e2_packet11(t.E2_KEY_11)
        p["answer_key"] = dict(p["answer_key"], methodology_version="1.1.0")
        p["required_evidence"]["methodology_version"] = "1.1.0"
        p["required_evidence"]["turns"] = (
            [{"turn": i, "text": "just" if i == 8 else "noted."} for i in range(1, 16)]
            + [{"turn": 16, "text": t.j(t.E2_KEY_11)}])
        p["model_output"] = t.j(t.E2_KEY_11)
        p["methodology_version"] = top
        from harness import judge as j
        return j.score_packet(p)

    def test_a_turn_8_violation_fails_under_the_declared_version(self):
        r = self._conflicted("1.1.0")
        self.assertEqual(r["outcome"], "FAIL_QUALITY")
        self.assertEqual(r["failure_reason"], "zero_tolerance:constraint_violation")

    def test_the_same_violation_can_no_longer_be_downgraded_to_a_pass(self):
        r = self._conflicted("1.0.0")
        self.assertNotEqual(r["outcome"], "PASS")
        self.assertEqual(r["failure_reason"], "methodology_version_conflict")

    def test_a_conflict_is_invalid_not_a_quality_failure(self):
        """"We could not measure it" and "it failed" are different findings (section 6.2)."""
        self.assertEqual(self._conflicted("1.0.0")["outcome"], "INVALID")

    def test_agreeing_versions_are_still_scored_normally(self):
        import test_judge as t
        from harness import judge as j
        self.assertEqual(j.score_packet(t.e2_packet11(t.E2_KEY_11))["outcome"], "PASS")


class TestSecondAdversarialReviewFindings(unittest.TestCase):
    """The second external review of `59293e8`, reproduced then closed.

    All three P1 findings were executable, and all three reproduced. Two of them are the SAME
    defect the first round found, surviving in a place the first fix did not reach: identity was
    still self-reported, and the over-count check still guarded only the entrance. The first
    round's fix notes said a defence guarding one entrance is not a defence, and then left one.
    """

    RUN_PLAN = pathlib.Path(__file__).resolve().parents[2] / "RUN_PLAN_v1.1.0.json"

    def setUp(self):
        self.plan = json.loads(self.RUN_PLAN.read_text())
        self.registry = PlannedAttempts.from_run_plan(self.plan)
        self.dcell = [c for c in self.plan["cells"]
                      if c["workload"] == "D" and c["condition"] == "C1"]
        self.rec = dict(run_id="same", task_id="D-001", workload="D", condition="C1",
                        repetition=1, outcome=PASS, cost=1.0)

    def test_the_run_plan_enumerates_every_attempt_it_counts(self):
        self.assertEqual(len(self.registry.by_id), 270)
        self.assertEqual(len(self.registry.cell_ids("D", "C1")), 12)

    def test_retries_of_one_task_cannot_fill_a_cell_of_twelve(self):
        """R2-01: twelve records of ONE task, distinct only in run_id, reported 12/12 PASS."""
        recs = [dict(self.rec, run_id=f"retry-{i}") for i in range(12)]
        with self.assertRaises(AggregateError) as cm:
            build_cells(recs, self.dcell, registry=self.registry)
        self.assertIn("not in the frozen plan", str(cm.exception))

    def test_an_invented_attempt_id_is_not_an_identity(self):
        """R2-01: the record asserted twelve ids and was believed."""
        recs = [dict(self.rec, attempt_id=f"new-{i}") for i in range(12)]
        with self.assertRaises(AggregateError) as cm:
            build_cells(recs, self.dcell, registry=self.registry)
        self.assertIn("not in the frozen plan", str(cm.exception))

    def test_a_planned_id_carrying_the_wrong_task_is_refused(self):
        """Holding a real id is not enough; the record must be the attempt that id names."""
        aid = sorted(self.registry.cell_ids("D", "C1"))[0]
        with self.assertRaises(AggregateError) as cm:
            build_cells([dict(self.rec, attempt_id=aid, task_id="D-999")],
                        self.dcell, registry=self.registry)
        self.assertIn("plan says", str(cm.exception))

    def test_the_genuine_twelve_still_pass(self):
        """The control. Over-rejection would be its own defect."""
        recs = []
        for aid in sorted(self.registry.cell_ids("D", "C1")):
            e = self.registry.by_id[aid]
            recs.append(dict(self.rec, attempt_id=aid, task_id=e["task_id"],
                             repetition=e["repetition"], run_id=e["planned_run_id"]))
        v = build_cells(recs, self.dcell, registry=self.registry)[0].verdict()
        self.assertEqual(v["cell_verdict"], "PASS", v["reasons"])
        self.assertEqual(v["success_rate"], 1.0)
        self.assertTrue(v["identity_verified"])

    def test_eleven_of_twelve_is_a_failed_cell_not_a_rounding_problem(self):
        recs = []
        for aid in sorted(self.registry.cell_ids("D", "C1"))[:11]:
            e = self.registry.by_id[aid]
            recs.append(dict(self.rec, attempt_id=aid, task_id=e["task_id"],
                             repetition=e["repetition"], run_id=e["planned_run_id"]))
        v = build_cells(recs, self.dcell, registry=self.registry)[0].verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertTrue(any("absent from this cell" in r for r in v["reasons"]), v["reasons"])

    def test_a_directly_built_cell_cannot_report_133_percent(self):
        """R2-02: four records against three planned gave success_rate 1.3333 and PASS."""
        c = Cell("D", "C1", planned=3,
                 attempts=[dict(self.rec, run_id=f"run-{i}", attempt_id=f"a-{i}")
                           for i in range(4)],
                 expected=frozenset({"a-0", "a-1", "a-2"}))
        v = c.verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertGreater(v["success_rate"], 1.0, "the rate is reported, never clipped to 100%")
        self.assertTrue(any("exceeds 1.0" in r for r in v["reasons"]), v["reasons"])

    def test_an_overcounting_cell_cannot_be_selected(self):
        """R2-02: select_strongest chose the 133% cell as a winner to reproduce."""
        c = Cell("D", "C1", planned=3,
                 attempts=[dict(self.rec, run_id=f"run-{i}", attempt_id=f"a-{i}")
                           for i in range(4)],
                 expected=frozenset({"a-0", "a-1", "a-2"}))
        self.assertEqual(select_strongest([c], {("D", "C1"): 0.9})["chosen"], [])

    def test_a_plan_unverified_cell_cannot_be_selected(self):
        c = Cell("D", "C1", planned=1, attempts=[dict(self.rec, attempt_id="a-0")])
        s = select_strongest([c], {("D", "C1"): 0.9})
        self.assertEqual(s["chosen"], [])
        self.assertIn("identity not verified", dict(s["rejected"])[("D", "C1")])

    def test_a_plan_that_contradicts_its_own_denominator_is_refused(self):
        bad = [{"workload": "D", "condition": "C1", "planned_attempts": 99}]
        with self.assertRaises(AggregateError) as cm:
            build_cells([], bad, registry=self.registry)
        self.assertIn("disagrees with itself", str(cm.exception))


class TestFinalizeValidatesBeforeWriting(unittest.TestCase):
    """R2-03: the previous fix hoisted only the missing-score check and was called 'atomic'."""

    def _batch(self, td, second_outcome):
        root = pathlib.Path(td); rd = root / "records"; sd = root / "scores"
        rd.mkdir(); sd.mkdir()
        for i in range(2):
            rec = dict(run_id=f"run{i}", task_id="D-001", methodology_version="1.1.0",
                       scorer_hash="x", outcome="INVALID")
            (rd / f"{i}.json").write_text(json.dumps(rec))
            pid = hashlib.sha256(f"{rec['run_id']}|{rec['task_id']}".encode()).hexdigest()[:16]
            (sd / f"{i}.json").write_text(json.dumps(dict(
                packet_id=pid, task_id="D-001", quality_score=1.0, task_success=True,
                outcome="PASS" if i == 0 else second_outcome,
                detail={"methodology_version": "1.1.0"}, scorer_hash="x")))
        return rd, sd

    def setUp(self):
        # The record schema needs jsonschema, which is not installed in every environment. The
        # control flow under test is the ordering of validation and writes, so validation is
        # stubbed HERE ONLY, exactly as the reviewer declared for their own probe. This does not
        # establish end-to-end schema acceptance and is not cited as doing so.
        self._real_validate = fin.validate
        fin.validate = lambda rec: None

    def tearDown(self):
        fin.validate = self._real_validate

    def test_a_bad_second_score_leaves_the_first_record_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            rd, sd = self._batch(td, "UNKNOWN")
            before = (rd / "0.json").read_bytes()
            with self.assertRaises(fin.FinalizeError) as cm:
                fin.finalize(rd, sd)
            self.assertIn("Nothing has been written", str(cm.exception))
            self.assertEqual((rd / "0.json").read_bytes(), before,
                             "the first record was rewritten before the second was rejected")
            self.assertEqual(list(rd.glob("*.tmp")), [], "a temp file survived the refusal")

    def test_a_clean_batch_is_written(self):
        with tempfile.TemporaryDirectory() as td:
            rd, sd = self._batch(td, "PASS")
            out = fin.finalize(rd, sd)
            self.assertEqual(out["records_finalized"], 2)
            self.assertEqual(json.loads((rd / "0.json").read_text())["outcome"], "PASS")
            self.assertIn("NOT a multi-file transaction", out["write_guarantee"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

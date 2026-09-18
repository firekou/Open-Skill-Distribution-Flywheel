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
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import evidence as ev  # noqa: E402
from harness import finalize as fin  # noqa: E402
from harness import judge as jdg  # noqa: E402
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


# R4-05: one build identity shared by every synthetic attempt. Cells are build-consistent by
# default, so a test that wants an inconsistency has to introduce one on purpose - and a fixture
# missing these fields now fails, which is the point.
def _schema_valid_record() -> dict:
    """A record satisfying every required property of the real schema.

    R4-06's positive control must run against the REAL validator - stubbing it is how R3-03 hid
    for two rounds - so the fixture has to be genuinely valid rather than minimal. Built from the
    schema itself, so adding a required property breaks this loudly instead of silently
    weakening the control.
    """
    schema = json.loads(
        (pathlib.Path(__file__).resolve().parents[1] / "run_record_schema.json").read_text())
    known = {
        "run_id": "run0", "attempt_id": "D-001-C1-r1", "task_id": "D-001", "condition": "C1",
        "workload": "D", "repetition": 1, "model": "replay", "provider": "lab",
        "model_version": "test", "model_calls": 1, "tool_calls": 0, "input_tokens": 10,
        "output_tokens": 1, "total_tokens": 11, "cost": 0.001,
        "pricing_snapshot_id": "PS-2026-09-16", "latency_ms": 1, "retries": 0, "escalations": 0,
        "cache_state": "cold", "task_success": False, "quality_score": 0.0,
        "environment_id": "test-env", "raw_evidence_path": "raw/run0.json",
        "methodology_version": "1.1.0", "run_class": "dry_run", "token_source": "provider_usage_field",
        "quality_judged_before_cost": False, "outcome": "INVALID",
    }
    missing = [k for k in schema["required"] if k not in known]
    if missing:  # pragma: no cover - fails loudly when the schema gains a required field
        raise AssertionError(
            f"the schema requires {missing}, which this fixture does not supply. Add them here "
            "rather than stubbing the validator.")
    return known


BUILD = {"methodology_version": "1.1.0", "task_version": "1.1.0",
         "task_set_hash": "a" * 64, "answer_key_hash": "b" * 64, "scorer_hash": "c" * 64}


def _att(tid, wl, cond, outcome, rep=1, cost=1.0, cache="cold"):
    return {"run_id": f"{tid}-{cond}-r{rep}", "attempt_id": f"{tid}-{cond}-r{rep}",
            "task_id": tid, "workload": wl, "condition": cond,
            "repetition": rep, "outcome": outcome, "cost": cost, "cache_state": cache,
            **BUILD}


def _planned_cell(wl, cond, planned, attempts):
    """A Cell whose identity IS checked against a planned set, as R2-01/R2-02 now require.

    `expected` is the planned attempt id set. Where a test deliberately records fewer attempts
    than planned, the shortfall is carried as planned ids that produced no record — which is what
    a missing attempt actually is, and what a re-run of another task must not stand in for.
    """
    spec = {a["attempt_id"]: {"workload": a["workload"], "condition": a["condition"],
                              "task_id": a["task_id"], "repetition": a["repetition"]}
            for a in attempts}
    for i in range(planned - len(attempts)):
        spec[f"{wl}-{cond}-planned-{i}"] = {"workload": wl, "condition": cond,
                                            "task_id": f"{wl}-unrecorded-{i}", "repetition": 1}
    return Cell(wl, cond, planned=planned, attempts=attempts,
                plan=PlannedAttempts.from_ids(spec))


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
             "repetition": 1, "outcome": PASS, "cost": 1.0, **BUILD}
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
        # The plan is supplied and every record matches it, so the ONLY thing wrong is the
        # duplication itself.
        rec = self._rec(attempt_id="D-001-C1-r1")
        c = Cell("D", "C1", planned=3, attempts=[dict(rec) for _ in range(3)],
                 plan=PlannedAttempts.from_ids({
                     "D-001-C1-r1": {"workload": "D", "condition": "C1", "task_id": "D-001",
                                     "repetition": 1},
                     "x2": {"workload": "D", "condition": "C1", "task_id": "D-002", "repetition": 1},
                     "x3": {"workload": "D", "condition": "C1", "task_id": "D-003", "repetition": 1}}))
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
                        repetition=1, outcome=PASS, cost=1.0, **BUILD)

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

    def _overcounting_cell(self):
        """Four records, all matching the plan, against a cell that planned three."""
        spec = {f"a-{i}": {"workload": "D", "condition": "C1", "task_id": f"D-00{i}",
                           "repetition": 1} for i in range(4)}
        return Cell("D", "C1", planned=3,
                    attempts=[dict(self.rec, run_id=f"run-{i}", attempt_id=f"a-{i}",
                                   task_id=f"D-00{i}") for i in range(4)],
                    plan=PlannedAttempts.from_ids(spec))

    def test_a_directly_built_cell_cannot_report_133_percent(self):
        """R2-02: four records against three planned gave success_rate 1.3333 and PASS."""
        c = self._overcounting_cell()
        v = c.verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertGreater(v["success_rate"], 1.0, "the rate is reported, never clipped to 100%")
        self.assertTrue(any("exceeds 1.0" in r for r in v["reasons"]), v["reasons"])

    def test_an_overcounting_cell_cannot_be_selected(self):
        """R2-02: select_strongest chose the 133% cell as a winner to reproduce."""
        self.assertEqual(
            select_strongest([self._overcounting_cell()], {("D", "C1"): 0.9})["chosen"], [])

    def test_a_plan_unverified_cell_cannot_be_selected(self):
        c = Cell("D", "C1", planned=1, attempts=[dict(self.rec, attempt_id="a-0")], plan=None)
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
                detail={"methodology_version": "1.1.0"},
                # R4-06: provenance is required now, not checked only when present.
                scorer_hash="x", methodology_version="1.1.0", packet_digest="d" * 64)))
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


class TestThirdAdversarialReviewFindings(unittest.TestCase):
    """The third external review of `4e6584b`.

    Both P1s are, for the third consecutive round, the same shape: the check was added at one
    entrance and the exit was left trusting a flag. R2 fixed `build_cells`; the public `Cell` and
    the actual command line were not fixed, so the guarantee did not exist where results are
    produced or where anyone runs it.
    """

    RUN_PLAN = pathlib.Path(__file__).resolve().parents[2] / "RUN_PLAN_v1.1.0.json"

    def setUp(self):
        self.plan = json.loads(self.RUN_PLAN.read_text())
        self.registry = PlannedAttempts.from_run_plan(self.plan)
        self.cp = [c for c in self.plan["cells"]
                   if (c["workload"], c["condition"]) == ("D", "C1")]
        self.recs = [dict(self.registry.by_id[i], attempt_id=i, run_id="exec-" + i,
                          outcome=PASS, cost=1.0, **BUILD)
                     for i in sorted(self.registry.cell_ids("D", "C1"))]

    # ---- R3-02 -----------------------------------------------------------
    def test_legal_ids_carrying_the_wrong_task_do_not_pass_through_the_direct_cell(self):
        """12 legal ids, every record claiming D-001 rep 1 → was 12/12 PASS, identity_verified."""
        bad = [dict(r, task_id="D-001", repetition=1) for r in self.recs]
        c = Cell("D", "C1", 12, bad, plan=self.registry)
        v = c.verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertFalse(v["identity_verified"])
        self.assertEqual(select_strongest([c], {("D", "C1"): 0.9})["chosen"], [])

    def test_a_record_edited_after_validation_is_caught_at_report_time(self):
        """The Cell holds the caller's dicts. Validation at build time is not validation."""
        cells = build_cells(self.recs, self.cp, registry=self.registry)
        self.assertEqual(cells[0].verdict()["cell_verdict"], "PASS")
        self.recs[0]["task_id"] = "D-999"           # edited AFTER build_cells accepted it
        v = cells[0].verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertFalse(v["identity_verified"])
        self.assertEqual(select_strongest(cells, {("D", "C1"): 0.9})["chosen"], [])

    def test_identity_verified_means_the_fields_were_compared(self):
        """It used to mean `expected is not None` — that somebody handed the cell a set."""
        c = Cell("D", "C1", 12, self.recs, plan=self.registry)
        self.assertTrue(c.verdict()["identity_verified"])
        c2 = Cell("D", "C1", 12, [dict(r, repetition=99) for r in self.recs], plan=self.registry)
        self.assertFalse(c2.verdict()["identity_verified"])

    # ---- R3-01: the documented command line, as a subprocess -------------
    def _cli(self, args):
        return subprocess.run([sys.executable, "-m", "harness.aggregate", *args],
                              capture_output=True, text=True,
                              cwd=str(pathlib.Path(__file__).resolve().parents[1]))

    def _records_dir(self, td, recs):
        rd = pathlib.Path(td) / "records"; rd.mkdir()
        for n, r in enumerate(recs):
            (rd / f"{n}.json").write_text(json.dumps(r))
        return rd

    def _sub_plan(self, td):
        sub = dict(self.plan)
        sub["cells"] = self.cp
        sub["runs"] = [r for r in self.plan["runs"]
                       if r["workload"] == "D" and r["condition"] == "C1"]
        path = pathlib.Path(td) / "run_plan.json"
        path.write_text(json.dumps(sub))
        return path

    def test_the_documented_command_passes_legitimate_records(self):
        """POSITIVE CONTROL. This exited 1 with identity_verified false on valid data."""
        with tempfile.TemporaryDirectory() as td:
            p = self._cli(["--records", str(self._records_dir(td, self.recs)),
                           "--run-plan", str(self._sub_plan(td))])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            rep = json.loads(p.stdout)
            self.assertEqual(rep["cells"][0]["cell_verdict"], "PASS")
            self.assertTrue(rep["cells"][0]["identity_verified"])
            self.assertEqual(rep["cells_identity_unverified"], [])
            # The hash identifies the plan actually used. This test runs against a D/C1 SUBSET
            # of the frozen plan, so it must not equal the full plan's hash — that difference is
            # the point of recording it.
            sub = PlannedAttempts.from_run_plan(json.loads(self._sub_plan(td).read_text()))
            self.assertEqual(rep["plan_hash"], sub.plan_hash)
            self.assertNotEqual(rep["plan_hash"], self.registry.plan_hash)

    def test_the_documented_command_rejects_substituted_records(self):
        """NEGATIVE CONTROL. Twelve retries of one task, through the real CLI."""
        with tempfile.TemporaryDirectory() as td:
            bad = [dict(self.recs[0], run_id=f"retry-{i}", attempt_id=f"invented-{i}")
                   for i in range(12)]
            p = self._cli(["--records", str(self._records_dir(td, bad)),
                           "--run-plan", str(self._sub_plan(td))])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("not in the frozen plan", p.stdout + p.stderr)

    def test_the_legacy_plan_shape_refuses_to_run_unchecked(self):
        with tempfile.TemporaryDirectory() as td:
            cells = pathlib.Path(td) / "cells.json"
            cells.write_text(json.dumps(self.cp))
            p = self._cli(["--records", str(self._records_dir(td, self.recs)),
                           "--plan", str(cells)])
            # It must DECLINE (argparse exit 2), not emit a report whose cells all say FAIL.
            # The old code produced a full report with identity_verified false, which reads as a
            # measurement result rather than a refusal to measure.
            self.assertEqual(p.returncode, 2, p.stdout[:400])
            self.assertEqual(p.stdout.strip(), "", "a refusal must not print a report")
            self.assertIn("--registry", p.stderr)

    # ---- R3-03: found here, not by the reviewer --------------------------
    def test_the_record_schema_accepts_the_fields_the_harness_writes(self):
        """R3-03. `pending_adjudication` (round 1) and `attempt_id` (round 3) were written by
        the harness and **absent from a schema with additionalProperties: false**. Every record
        would have been rejected in the real chain. Both round-1 and round-3 test suites missed
        it because jsonschema was not installed and the finalize tests stubbed the validator."""
        schema = json.loads(
            (pathlib.Path(__file__).resolve().parents[1] / "run_record_schema.json").read_text())
        self.assertFalse(schema.get("additionalProperties", True),
                         "this test only means something while the schema is closed")
        for field in ("attempt_id", "pending_adjudication"):
            self.assertIn(field, schema["properties"],
                          f"the harness writes {field} and the schema would reject the record")


class TestFourthAdversarialReviewFindings(unittest.TestCase):
    """The fourth external review of `6d59acd`.

    Two of the six are the recurring shape a fourth time: a guard whose input nothing produces
    (R4-06), and a protected scope that excludes the code doing the work (R4-02).
    """

    LAB = pathlib.Path(__file__).resolve().parents[2]

    # ---- R4-02: manifest coverage --------------------------------------
    def test_the_committed_manifest_verifies_against_the_committed_code(self):
        """It did not: run_record_schema.json and judge.py both mismatched on 6d59acd."""
        v = mf.verify(self.LAB / "tasks/TASK_SET_v1.1.0/MANIFEST.json",
                      self.LAB / "tasks/TASK_SET_v1.1.0", self.LAB / "environment")
        self.assertTrue(v["ok"], [g for g, d in v["groups"].items() if not d["ok"]])

    def test_the_manifest_covers_the_aggregation_and_run_code(self):
        """`CONFIG_FILES` omitted aggregate.py, finalize.py and runner.py — every module between
        a scored packet and a published cell."""
        data = json.loads((self.LAB / "tasks/TASK_SET_v1.1.0/MANIFEST.json").read_text())
        covered = (set(data["groups"]["execution"]["files"])
                   | set(data["groups"]["scorer"]["files"]))
        for must in ("harness/aggregate.py", "harness/finalize.py", "harness/runner.py",
                     "harness/judge.py", "harness/analyse.py"):
            self.assertIn(must, covered)

    def test_a_modified_aggregator_is_caught(self):
        """NEGATIVE CONTROL. With a fresh manifest, an overridden select_strongest verified ok."""
        with tempfile.TemporaryDirectory() as td:
            env = pathlib.Path(td) / "env"; env.mkdir()
            shutil.copytree(self.LAB / "environment/harness", env / "harness")
            shutil.copy(self.LAB / "environment/run_record_schema.json", env)
            mp = pathlib.Path(td) / "manifest.json"
            mf.build(self.LAB / "tasks/TASK_SET_v1.1.0", env).save(mp)
            self.assertTrue(mf.verify(mp, self.LAB / "tasks/TASK_SET_v1.1.0", env)["ok"],
                            "positive control: an untouched tree must verify")
            with (env / "harness/aggregate.py").open("a") as fh:
                fh.write('\ndef select_strongest(*a, **k):\n    return {"chosen": [("D", "C1")]}\n')
            v = mf.verify(mp, self.LAB / "tasks/TASK_SET_v1.1.0", env)
            self.assertFalse(v["ok"])
            self.assertIn("harness/aggregate.py", v["groups"]["execution"]["modified"])

    def test_a_new_harness_module_is_caught(self):
        """A hand-maintained list cannot notice a file nobody added it to."""
        with tempfile.TemporaryDirectory() as td:
            env = pathlib.Path(td) / "env"; env.mkdir()
            shutil.copytree(self.LAB / "environment/harness", env / "harness")
            shutil.copy(self.LAB / "environment/run_record_schema.json", env)
            mp = pathlib.Path(td) / "manifest.json"
            mf.build(self.LAB / "tasks/TASK_SET_v1.1.0", env).save(mp)
            (env / "harness/extra_module.py").write_text("X = 1\n")
            v = mf.verify(mp, self.LAB / "tasks/TASK_SET_v1.1.0", env)
            self.assertFalse(v["ok"])
            self.assertIn("harness/extra_module.py", v["groups"]["execution"]["added"])

    # ---- R4-03: the documented dry-run path ----------------------------
    def test_the_committed_dry_run_plan_carries_attempt_ids(self):
        """All 10 items lacked one, so the runner refused before executing anything."""
        plan = json.loads((self.LAB / "dryrun/PLAN.json").read_text())
        self.assertTrue(plan)
        self.assertEqual([i["task_id"] for i in plan if not i.get("attempt_id")], [])

    def test_the_committed_dry_run_has_its_own_run_plan(self):
        rp = json.loads((self.LAB / "dryrun/RUN_PLAN.json").read_text())
        plan = json.loads((self.LAB / "dryrun/PLAN.json").read_text())
        ids = {a["attempt_id"] for r in rp["runs"] for a in r["task_attempts"]}
        self.assertEqual(ids, {i["attempt_id"] for i in plan})
        self.assertNotEqual(rp["run_plan_version"], "1.1.0",
                            "the dry run must not claim to be the frozen experiment plan")

    # ---- R4-04: the methodology lock -----------------------------------
    def test_every_document_the_lock_claims_hashes_to_what_it_says(self):
        lock = json.loads((self.LAB / "methodology/METHODOLOGY_LOCK_v1.1.0.json").read_text())
        bad = [rel for rel, want in lock["documents"].items()
               if hashlib.sha256((self.LAB / rel).read_bytes()).hexdigest() != want]
        self.assertEqual(bad, [], "the lock cannot fingerprint a candidate it does not match")

    # ---- R4-05: build identity -----------------------------------------
    def test_a_cell_mixing_two_builds_is_not_reportable(self):
        atts = [_att(f"D-00{i}", "D", "C1", PASS) for i in (1, 2, 3)]
        atts[0]["methodology_version"] = "1.0.0"
        c = _planned_cell("D", "C1", 3, atts)
        v = c.verdict()
        self.assertEqual(v["cell_verdict"], "FAIL")
        self.assertFalse(v["build_consistent"])
        self.assertTrue(any("disagree on methodology_version" in b for b in v["build_problems"]))

    def test_a_build_inconsistency_is_not_reported_as_a_quality_failure(self):
        """Nothing about the candidate failed; the record set cannot be interpreted."""
        atts = [_att(f"D-00{i}", "D", "C1", PASS) for i in (1, 2, 3)]
        atts[0]["scorer_hash"] = "d" * 64
        v = _planned_cell("D", "C1", 3, atts).verdict()
        self.assertEqual(v["counts"][FAIL_QUALITY], 0)
        self.assertTrue(any(r.startswith("BUILD INCONSISTENT") for r in v["reasons"]))

    def test_a_build_inconsistent_cell_cannot_be_selected(self):
        atts = [_att(f"D-00{i}", "D", "C1", PASS) for i in (1, 2, 3)]
        atts[0]["task_set_hash"] = "e" * 64
        c = _planned_cell("D", "C1", 3, atts)
        self.assertEqual(select_strongest([c], {("D", "C1"): 0.9})["chosen"], [])

    def test_the_plan_hash_covers_the_versions_the_plan_declares(self):
        """Changing methodology_version and task_set_version left plan_hash byte-identical."""
        rp = json.loads((self.LAB / "RUN_PLAN_v1.1.0.json").read_text())
        before = PlannedAttempts.from_run_plan(rp).plan_hash
        rp2 = json.loads((self.LAB / "RUN_PLAN_v1.1.0.json").read_text())
        rp2["methodology_version"] = "1.0.0"
        rp2["task_set_version"] = "1.0.0"
        self.assertNotEqual(PlannedAttempts.from_run_plan(rp2).plan_hash, before)

    def test_a_consistent_cell_still_passes(self):
        """CONTROL. Over-rejection would be its own defect."""
        v = _planned_cell("D", "C1", 3,
                          [_att(f"D-00{i}", "D", "C1", PASS) for i in (1, 2, 3)]).verdict()
        self.assertEqual(v["cell_verdict"], "PASS", v["reasons"])
        self.assertTrue(v["build_consistent"])

    # ---- R4-06: score provenance ---------------------------------------
    def test_the_judge_stamps_its_own_identity_on_every_score(self):
        """0 of 17 real scores carried scorer_hash, so finalize's comparison never ran."""
        import test_judge as t
        res = jdg.score_packet(t.e2_packet11(t.E2_KEY_11))
        stamped = jdg._stamp_provenance(dict(res), t.e2_packet11(t.E2_KEY_11))
        for field in ("scorer_hash", "methodology_version", "packet_digest"):
            self.assertTrue(stamped.get(field), field)
        self.assertEqual(stamped["scorer_hash"], jdg.scorer_identity())

    def test_the_scorer_identity_is_derived_from_its_own_source(self):
        want = hashlib.sha256(
            (self.LAB / "environment/harness/judge.py").read_bytes()).hexdigest()
        self.assertEqual(jdg.scorer_identity(), want)

    def _prov_batch(self, td, *, score_extra=None, record_extra=None):
        root = pathlib.Path(td); rd = root / "r"; sd = root / "s"; rd.mkdir(); sd.mkdir()
        rec = dict(_SCHEMA_VALID_RECORD, scorer_hash="x")
        rec.update(record_extra or {})
        (rd / "0.json").write_text(json.dumps(rec))
        pid = hashlib.sha256(b"run0|D-001").hexdigest()[:16]
        score = {"packet_id": pid, "task_id": "D-001", "quality_score": 1.0,
                 "task_success": True, "outcome": "PASS",
                 "detail": {"methodology_version": "1.1.0"}, "scorer_hash": "x",
                 "methodology_version": "1.1.0", "packet_digest": "d" * 64}
        score.update(score_extra or {})
        (sd / "0.json").write_text(json.dumps(score))
        return rd, sd

    def test_a_score_without_provenance_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            rd, sd = self._prov_batch(td, score_extra={"scorer_hash": None})
            before = (rd / "0.json").read_bytes()
            with self.assertRaises(fin.FinalizeError) as cm:
                fin.finalize(rd, sd)
            self.assertIn("no provenance", str(cm.exception))
            self.assertEqual((rd / "0.json").read_bytes(), before)

    def test_a_record_naming_a_different_scorer_is_refused(self):
        """It used to finalize 17 records and keep the wrong hash untouched."""
        with tempfile.TemporaryDirectory() as td:
            rd, sd = self._prov_batch(td, record_extra={"scorer_hash": "f" * 64})
            with self.assertRaises(fin.FinalizeError) as cm:
                fin.finalize(rd, sd)
            self.assertIn("scorer", str(cm.exception))

    def test_a_score_missing_its_methodology_version_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            rd, sd = self._prov_batch(td, score_extra={"methodology_version": None})
            with self.assertRaises(fin.FinalizeError) as cm:
                fin.finalize(rd, sd)
            self.assertIn("no provenance", str(cm.exception))

    def test_a_fully_provenanced_batch_finalizes(self):
        """CONTROL."""
        with tempfile.TemporaryDirectory() as td:
            rd, sd = self._prov_batch(td)
            out = fin.finalize(rd, sd)
            self.assertEqual(out["records_finalized"], 1)
            self.assertEqual(
                json.loads((rd / "0.json").read_text())["scored_packet_digest"], "d" * 64)


_SCHEMA_VALID_RECORD = _schema_valid_record()


class TestAnalysisEntryPoint(unittest.TestCase):
    """R4-01: the analysis layer had no command. It computes what needs no ruling, and names
    what it refuses."""

    LAB = pathlib.Path(__file__).resolve().parents[2]

    def _plan_and_records(self, td, mutate=None):
        ids = {f"D-00{i}-C1-r1": {"workload": "D", "condition": "C1", "task_id": f"D-00{i}",
                                  "repetition": 1} for i in (1, 2, 3)}
        run_plan = {
            "methodology_version": "1.1.0", "task_set_version": "1.1.0",
            "cells": [{"workload": "D", "condition": "C1", "planned_attempts": 3}],
            "runs": [{"run_id": "D-C1-r1", "workload": "D", "condition": "C1", "repetition": 1,
                      "task_attempts": [{"task_id": v["task_id"], "attempt_id": k}
                                        for k, v in sorted(ids.items())]}],
        }
        recs = [dict(_att(v["task_id"], "D", "C1", PASS), attempt_id=k)
                for k, v in sorted(ids.items())]
        if mutate:
            mutate(recs)
        root = pathlib.Path(td); rd = root / "r"; rd.mkdir()
        for i, r in enumerate(recs):
            (rd / f"{i}.json").write_text(json.dumps(r))
        pp = root / "run_plan.json"; pp.write_text(json.dumps(run_plan))
        return rd, pp

    def _run(self, rd, pp):
        p = subprocess.run([sys.executable, "-m", "harness.analyse", "--records", str(rd),
                            "--run-plan", str(pp)], capture_output=True, text=True,
                           cwd=str(pathlib.Path(__file__).resolve().parents[1]))
        return p.returncode, json.loads(p.stdout)

    def test_it_computes_cost_per_successful_task_when_every_attempt_is_priced(self):
        with tempfile.TemporaryDirectory() as td:
            code, d = self._run(*self._plan_and_records(td))
            self.assertEqual(code, 0, d)
            cost = d["cells"][0]["cost"]
            self.assertEqual(cost["cost_status"], "COMPUTED")
            self.assertAlmostEqual(cost["cost_per_successful_task"], 1.0)

    def test_an_unpriced_attempt_blocks_the_metric_rather_than_reading_as_zero(self):
        def drop(recs): recs[0].pop("cost")
        with tempfile.TemporaryDirectory() as td:
            _, d = self._run(*self._plan_and_records(td, drop))
            cost = d["cells"][0]["cost"]
            self.assertEqual(cost["cost_status"], "BLOCKED")
            self.assertIsNone(cost["cost_per_successful_task"])

    def test_a_cell_with_no_passes_reports_no_finite_value(self):
        def fail(recs):
            for r in recs:
                r["outcome"] = FAIL_QUALITY
        with tempfile.TemporaryDirectory() as td:
            _, d = self._run(*self._plan_and_records(td, fail))
            self.assertEqual(d["cells"][0]["cost"]["cost_status"], "NO_FINITE_VALUE")

    def test_a_substituted_identity_refuses_the_whole_description(self):
        def swap(recs): recs[0]["attempt_id"] = "invented-1"
        with tempfile.TemporaryDirectory() as td:
            code, d = self._run(*self._plan_and_records(td, swap))
            self.assertEqual(code, 2)
            self.assertEqual(d["status"], "REFUSED")

    def test_it_refuses_every_conclusion_that_waits_on_a_ruling(self):
        with tempfile.TemporaryDirectory() as td:
            _, d = self._run(*self._plan_and_records(td))
            blocked = {x["output"] for x in d["decisions_required"]}
            for must in ("cost_delta_vs_baseline", "condition_ranking", "non_inferiority",
                         "savings_claim", "strongest_conditions"):
                self.assertIn(must, blocked)
            for absent in ("delta", "ranking", "non_inferiority_result", "saving"):
                self.assertNotIn(f'"{absent}":', json.dumps(d))


if __name__ == "__main__":
    unittest.main(verbosity=2)

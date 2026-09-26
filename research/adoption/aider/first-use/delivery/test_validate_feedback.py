#!/usr/bin/env python3
"""Tests for validate_feedback.py against the synthetic fixtures.

The schema is taken from ATK_FEEDBACK_SCHEMA if set (e.g. the file written by
integrations/aider-atk/delivery/get_assets.py), otherwise it is extracted with
`git show` from the pinned PR19 commit in the current clone.
"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")
VALIDATOR = os.path.join(HERE, "validate_feedback.py")
SECRET = "SYNTHETIC_SECRET_VALUE_7f3a9c"
SOURCE = "a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41:research/adoption/aider/first-use/FEEDBACK_SCHEMA.json"


def schema_path():
    env = os.environ.get("ATK_FEEDBACK_SCHEMA")
    if env:
        return env
    data = subprocess.run(["git", "-C", HERE, "show", SOURCE], capture_output=True, check=True).stdout
    fd, path = tempfile.mkstemp(suffix=".json")
    os.write(fd, data)
    os.close(fd)
    return path


SCHEMA = schema_path()


def run(*records, schema=None):
    p = subprocess.run([sys.executable, VALIDATOR, "--schema", schema or SCHEMA,
                        *[os.path.join(FIX, r) for r in records]], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class Positive(unittest.TestCase):
    def test_valid_pass_accepted(self):
        code, out = run("valid_pass.json")
        self.assertEqual(code, 0, out)
        self.assertIn("VALID", out)

    def test_valid_honest_fail_accepted(self):
        code, out = run("valid_fail.json")
        self.assertEqual(code, 0, out)

    def test_positive_controls_not_all_rejected_in_a_mixed_batch(self):
        code, out = run("valid_pass.json", "invalid_false_pass.json", "valid_fail.json")
        self.assertEqual(code, 1)
        self.assertEqual(out.count("VALID   "), 2, out)


class Negative(unittest.TestCase):
    def assertRejected(self, name, expect):
        code, out = run(name)
        self.assertEqual(code, 1, out)
        self.assertIn("INVALID", out)
        self.assertIn(expect, out)
        return out

    def test_failed_exceeds_total(self):
        self.assertRejected("invalid_failed_exceeds_total.json", "/task/tests_failed failed_exceeds_total")

    def test_false_pass(self):
        self.assertRejected("invalid_false_pass.json", "/task/")

    def test_bad_source_url(self):
        self.assertRejected("invalid_bad_source_url.json", "/entry/url pattern")

    def test_internal_claiming_external(self):
        self.assertRejected("invalid_internal_as_external.json", "INVALID")

    def test_malformed_json_reports_position_only(self):
        out = self.assertRejected("invalid_malformed.json", "malformed JSON (line 1, column")
        self.assertNotIn("FU-00000000-008", out)

    def test_secret_never_echoed(self):
        out = self.assertRejected("invalid_secret_not_echoed.json", "INVALID")
        self.assertNotIn(SECRET, out)
        self.assertNotIn("7f3a9c", out)

    def test_no_record_value_echoed_on_any_fixture(self):
        _, out = run(*sorted(f for f in os.listdir(FIX) if f.endswith(".json")))
        for value in ("FU-00000000-00", "2000-01-01", SECRET):
            self.assertNotIn(value, out)


class SchemaPin(unittest.TestCase):
    def test_wrong_schema_refused(self):
        fd, bad = tempfile.mkstemp(suffix=".json")
        os.write(fd, b'{"type": "object"}')
        os.close(fd)
        code, out = run("valid_pass.json", schema=bad)
        self.assertEqual(code, 2)
        self.assertIn("SHA-256 mismatch", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)

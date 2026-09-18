#!/usr/bin/env python3
"""Regression tests for the two defects the PR #5 R1 review reproduced.

    python3 test_local_check.py

No network, no model call, no credential. The reviewer's own script
(reviews/evidence/pr5-r1/reviewer_checks.py) is kept unmodified as the historical
evidence; this file is the fix's own test and goes further where the review said
the original test did not go far enough.
"""

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import tempfile
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

HERE = pathlib.Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


local_check = load("local_check")
ab_test = load("ab_test")

SYNTHETIC_KEY = "sk-SYNTHETIC0000NOTAREALKEY0000000000000ZZ"  # 41 chars, never valid


def run_local_check(payload: str, transform, needles=("KEEP",), log_text=None):
    """Drive local_check.main() through its real decision path.

    Only the process and network boundaries are replaced: the stub upstream, the
    proxy subprocess and `post`. Everything the verdict depends on is the real code.
    """
    mod = local_check
    with tempfile.TemporaryDirectory() as td:
        log = pathlib.Path(td) / "sample.log"
        log.write_text(log_text if log_text is not None else payload)
        mod.RECEIVED.clear()

        def fake_post(url, prompt, headers):
            mod.RECEIVED.append(
                {"messages": [{"role": "user",
                               "content": transform(prompt) if headers else prompt}]}
            )

        argv = ["--log", str(log)]
        for n in needles:
            argv += ["--needle", n]
        out = io.StringIO()
        with patch.object(mod, "HTTPServer", return_value=MagicMock()), \
             patch.object(mod.threading, "Thread", return_value=MagicMock()), \
             patch.object(mod.subprocess, "Popen", return_value=MagicMock()), \
             patch.object(mod, "wait_for", return_value=True), \
             patch.object(mod, "post", side_effect=fake_post), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = mod.main(argv)
        return code, out.getvalue()


class AdoptionVerdict(unittest.TestCase):
    """P5-02: PASS must mean 'it got strictly smaller AND every needle survived'."""

    PAYLOAD = "KEEP " + "x" * 200

    def test_shrunk_and_needle_present_passes(self):
        code, out = run_local_check(self.PAYLOAD, lambda s: "KEEP")
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)

    def test_unchanged_is_not_a_pass(self):
        code, out = run_local_check(self.PAYLOAD, lambda s: s)
        self.assertEqual(code, 3)
        self.assertIn("NO BENEFIT", out)
        self.assertIn("byte for byte", out)

    def test_same_length_rewrite_is_not_a_pass_and_is_not_called_byte_for_byte(self):
        code, out = run_local_check(self.PAYLOAD, lambda s: s.replace("x", "y"))
        self.assertEqual(code, 3)
        self.assertIn("NO BENEFIT", out)
        self.assertIn("REWRITTEN", out)
        # The review's point: describing a changed payload as an unchanged one is a
        # false statement, not just an imprecise one.
        self.assertNotIn("byte for byte", out)

    def test_inflation_is_not_a_pass(self):
        code, out = run_local_check(self.PAYLOAD, lambda s: s + "EXTRA" * 100)
        self.assertEqual(code, 3)
        self.assertIn("NO BENEFIT", out)
        self.assertIn("GREW", out)
        self.assertNotIn("PASS", out)

    def test_inflation_is_never_reported_as_fewer(self):
        _, out = run_local_check(self.PAYLOAD, lambda s: s + "EXTRA" * 100)
        # It used to print "-166.7% fewer" on its way to PASS.
        self.assertNotIn("fewer", out.split("NO BENEFIT")[0])
        self.assertIn("MORE", out)

    def test_lost_needle_fails_even_when_it_shrank_a_lot(self):
        code, out = run_local_check(self.PAYLOAD, lambda s: "gone")
        self.assertEqual(code, 1)
        self.assertIn("LOST", out)
        self.assertNotIn("PASS", out)

    def test_empty_needle_is_refused(self):
        code, out = run_local_check(self.PAYLOAD, lambda s: "KEEP", needles=("",))
        self.assertEqual(code, 2)
        self.assertIn("empty --needle", out)

    def test_whitespace_only_needle_is_refused(self):
        code, out = run_local_check(self.PAYLOAD, lambda s: "KEEP", needles=("   ",))
        self.assertEqual(code, 2)

    def test_needle_absent_from_the_source_is_refused(self):
        code, out = run_local_check(self.PAYLOAD, lambda s: s, needles=("NOT-IN-FILE",))
        self.assertEqual(code, 2)
        self.assertIn("to begin with", out)

    def test_all_needles_must_survive_not_just_one(self):
        payload = "KEEP ALSOKEEP " + "x" * 200
        code, out = run_local_check(
            payload, lambda s: "KEEP", needles=("KEEP", "ALSOKEEP")
        )
        self.assertEqual(code, 1)


class ErrorBodySafety(unittest.TestCase):
    """P5-01: a provider error must not put the credential on stderr."""

    @staticmethod
    def _http_error(body: str):
        return urllib.error.HTTPError(
            "http://test.invalid", 401, "denied", {}, io.BytesIO(body.encode())
        )

    def _call_and_capture(self, body: str, include: bool) -> str:
        env = dict(os.environ)
        env[ab_test.INCLUDE_BODY_ENV] = "1" if include else "0"
        with patch.dict(os.environ, env, clear=True), \
             patch.object(ab_test.urllib.request, "urlopen",
                          side_effect=self._http_error(body)):
            with self.assertRaises(SystemExit) as cm:
                ab_test.call("http://test.invalid", SYNTHETIC_KEY, "prompt", False)
        return str(cm.exception)

    def test_body_is_withheld_by_default(self):
        msg = self._call_and_capture(f'{{"error":"invalid key {SYNTHETIC_KEY}"}}', include=False)
        self.assertNotIn(SYNTHETIC_KEY, msg)
        self.assertIn("withheld", msg)
        self.assertIn("401", msg)

    def test_full_key_absent_when_body_is_included(self):
        msg = self._call_and_capture(f'{{"error":"invalid key {SYNTHETIC_KEY}"}}', include=True)
        self.assertNotIn(SYNTHETIC_KEY, msg)
        self.assertIn("REDACTED", msg)

    def test_no_fragment_of_the_key_survives_at_any_position(self):
        """The original test only asserted the FULL key was absent — which a
        truncated key passes. Assert no 8-character window of it survives."""
        msg = self._call_and_capture(f'{{"error":"invalid key {SYNTHETIC_KEY}"}}', include=True)
        for i in range(len(SYNTHETIC_KEY) - 7):
            self.assertNotIn(SYNTHETIC_KEY[i:i + 8], msg,
                             f"fragment at offset {i} leaked")

    def test_key_straddling_the_truncation_boundary_does_not_leak_a_prefix(self):
        """Redact-then-truncate. Truncate-then-redact leaves the prefix behind,
        because you cannot match a value the cut already broke in half."""
        padding = "A" * 390
        msg = self._call_and_capture(padding + SYNTHETIC_KEY + "tail", include=True)
        for i in range(len(SYNTHETIC_KEY) - 7):
            self.assertNotIn(SYNTHETIC_KEY[i:i + 8], msg,
                             f"fragment at offset {i} survived the truncation boundary")

    def test_key_echoed_in_the_url_is_redacted_on_a_connection_error(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch.object(ab_test.urllib.request, "urlopen",
                          side_effect=urllib.error.URLError(f"host {SYNTHETIC_KEY} unreachable")):
            with self.assertRaises(SystemExit) as cm:
                ab_test.call(f"http://test.invalid/?k={SYNTHETIC_KEY}", SYNTHETIC_KEY, "p", False)
        self.assertNotIn(SYNTHETIC_KEY, str(cm.exception))

    def test_positive_control_a_normal_response_still_works(self):
        payload = {
            "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
            "choices": [{"message": {"content": "hello"}, "finish_reason": "stop"}],
        }
        resp = MagicMock()
        resp.__enter__ = MagicMock(return_value=io.BytesIO(json.dumps(payload).encode()))
        resp.__exit__ = MagicMock(return_value=False)
        with patch.object(ab_test.urllib.request, "urlopen", return_value=resp):
            got = ab_test.call("http://test.invalid", SYNTHETIC_KEY, "prompt", False)
        self.assertEqual(got["text"], "hello")
        self.assertEqual(got["usage"]["prompt_tokens"], 10)

    def test_redact_leaves_short_values_alone(self):
        """A 1-3 character 'secret' would blank out ordinary text."""
        self.assertEqual(ab_test.redact("a cat sat", ["a"]), "a cat sat")


if __name__ == "__main__":
    unittest.main(verbosity=2)

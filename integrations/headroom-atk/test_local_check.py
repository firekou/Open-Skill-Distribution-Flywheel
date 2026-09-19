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


def run_local_check(payload: str, transform, needles=("KEEP",), log_text=None,
                    extra_argv=()):
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
        argv += list(extra_argv)
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


class OutputPrivacy(unittest.TestCase):
    """P5-R2-01: the README calls this output safe to paste into a bug report.

    A needle is normally a real line lifted out of a real log, so printing it
    made that promise false. It must hold by construction, not by hoping users
    pick a harmless needle.
    """

    PRIVATE = "SYNTHETIC_PRIVATE_CUSTOMER_42"

    def test_needle_content_is_not_printed_on_success(self):
        code, out = run_local_check(
            self.PRIVATE + " x" * 100, lambda s: self.PRIVATE, needles=(self.PRIVATE,)
        )
        self.assertEqual(code, 0)
        self.assertNotIn(self.PRIVATE, out)
        self.assertIn("#1", out)

    def test_needle_content_is_not_printed_when_it_is_lost(self):
        code, out = run_local_check(
            self.PRIVATE + " x" * 100, lambda s: "gone", needles=(self.PRIVATE,)
        )
        self.assertEqual(code, 1)
        self.assertNotIn(self.PRIVATE, out)

    def test_needle_content_is_not_printed_when_it_is_absent_from_the_source(self):
        code, out = run_local_check("x" * 200, lambda s: s, needles=(self.PRIVATE,))
        self.assertEqual(code, 2)
        self.assertNotIn(self.PRIVATE, out)

    def test_full_log_path_is_not_printed(self):
        code, out = run_local_check(
            self.PRIVATE + " x" * 100, lambda s: self.PRIVATE, needles=(self.PRIVATE,)
        )
        self.assertNotIn("/", out.splitlines()[0])
        self.assertIn("sample.log", out)

    def test_show_needles_opts_back_in(self):
        code, out = run_local_check(
            self.PRIVATE + " x" * 100, lambda s: self.PRIVATE,
            needles=(self.PRIVATE,), extra_argv=["--show-needles"],
        )
        self.assertEqual(code, 0)
        self.assertIn(self.PRIVATE, out)


class ErrorBodySafety(unittest.TestCase):
    """P5-01: a provider error must not put the credential on stderr."""

    @staticmethod
    def _http_error(body: str):
        return urllib.error.HTTPError(
            "http://test.invalid", 401, "denied", {}, io.BytesIO(body.encode())
        )

    def _call_and_capture(self, body: str, env: dict | None = None) -> str:
        with patch.dict(os.environ, env or {}, clear=True), \
             patch.object(ab_test.urllib.request, "urlopen",
                          side_effect=self._http_error(body)):
            with self.assertRaises(SystemExit) as cm:
                ab_test.call("http://test.invalid", SYNTHETIC_KEY, "prompt", False)
        return str(cm.exception)

    def _assert_no_fragment(self, msg: str, value: str, width: int = 8):
        for i in range(max(0, len(value) - width + 1)):
            self.assertNotIn(value[i:i + width], msg,
                             f"fragment of {value!r} at offset {i} leaked")

    def test_body_is_never_shown_and_the_status_code_is(self):
        msg = self._call_and_capture(f'{{"error":"invalid key {SYNTHETIC_KEY}"}}')
        self.assertNotIn(SYNTHETIC_KEY, msg)
        self.assertIn("401", msg)
        self.assertIn("never shown", msg)

    def test_no_env_var_can_turn_the_body_back_on(self):
        """The opt-in debug branch was removed, not merely defaulted off. A
        toggle that can be set is a toggle that gets set."""
        for env in ({"ATK_INCLUDE_ERROR_BODY": "1"}, {"DEBUG": "1"}, {"ATK_DEBUG": "1"}):
            msg = self._call_and_capture(f'{{"error":"invalid key {SYNTHETIC_KEY}"}}', env)
            self.assertNotIn(SYNTHETIC_KEY, msg)
            self._assert_no_fragment(msg, SYNTHETIC_KEY)
        self.assertFalse(hasattr(ab_test, "INCLUDE_BODY_ENV"),
                         "the include-body switch should no longer exist")

    def test_provider_echoing_only_PART_of_the_key_cannot_leak(self):
        """P5-01, round 2. The previous fix redacted the whole key, so a body
        echoing `PREFIX***SUFFIX` — which is what real providers actually send —
        matched nothing and passed straight through. Redaction cannot recognise a
        fragment it was never given, which is why the body is not shown at all."""
        partial = f"invalid key {SYNTHETIC_KEY[:16]}***{SYNTHETIC_KEY[-8:]}"
        # Checked with the old debug switch set as well: on the previous head that
        # combination printed both halves, so this asserts the leak is gone rather
        # than merely defaulted off.
        for env in ({}, {"ATK_INCLUDE_ERROR_BODY": "1"}):
            msg = self._call_and_capture(partial, env)
            self.assertNotIn(SYNTHETIC_KEY[:16], msg)
            self.assertNotIn(SYNTHETIC_KEY[-8:], msg)

    def test_a_transformed_echo_cannot_leak_either(self):
        """Redaction would also miss a reversed, re-cased or spaced-out echo."""
        for variant in (SYNTHETIC_KEY[::-1], SYNTHETIC_KEY.upper(), " ".join(SYNTHETIC_KEY)):
            msg = self._call_and_capture(f'{{"error":"rejected {variant}"}}')
            self.assertNotIn(variant, msg)

    def test_a_long_body_cannot_leak_at_any_offset(self):
        """There is no truncation boundary left to straddle, because there is no
        body in the output at all."""
        msg = self._call_and_capture("A" * 390 + SYNTHETIC_KEY + "tail")
        self._assert_no_fragment(msg, SYNTHETIC_KEY)

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

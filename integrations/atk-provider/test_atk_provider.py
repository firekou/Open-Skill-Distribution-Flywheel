"""Tests for the ATK provider seam.

**These run against a real HTTP server on localhost, not a mock of my own code.** The adapter
builds a real request, a real socket carries it, a real server parses it and answers. What is
synthetic is the *provider*, not the transport — so URL construction, headers, JSON shape,
status handling, retry behaviour and the fallback chain are all genuinely exercised.

**What this cannot show:** that `api.aitokenking.com` accepts these requests. No ATK credential
exists in this environment and the host does not resolve from here. See `VERIFICATION.md`.
"""
from __future__ import annotations

import json
import pathlib
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import atk_provider as ap
from atk_provider import Message


class _Handler(BaseHTTPRequestHandler):
    """A provider that records what it was sent and replies however the test asked."""

    def log_message(self, *a):  # keep test output readable
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        self.server.calls.append({
            "path": self.path,
            # HTTP header names are case-insensitive (RFC 9110) and urllib capitalises them,
            # so assertions compare lowercase keys rather than the exact casing sent.
            "headers": {k.lower(): v for k, v in self.headers.items()},
            "body": json.loads(body or b"{}"),
        })
        status, payload = self.server.script.pop(0) if self.server.script else (200, {})
        raw = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def _openai_reply(text="ok", model="test-model"):
    return (200, {"model": model,
                  "choices": [{"message": {"role": "assistant", "content": text}}],
                  "usage": {"prompt_tokens": 11, "completion_tokens": 3, "total_tokens": 14}})


class _Server:
    def __init__(self, script=None):
        self.httpd = HTTPServer(("127.0.0.1", 0), _Handler)
        self.httpd.calls = []
        self.httpd.script = list(script or [])
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *a):
        self.httpd.shutdown()
        self.httpd.server_close()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.httpd.server_address[1]}/v1"

    @property
    def calls(self):
        return self.httpd.calls


class TestTransparency(unittest.TestCase):
    """§1: the user can see which provider handled each request."""

    def test_the_completion_names_the_provider_that_served_it(self):
        with _Server([_openai_reply("hi")]) as s:
            env = {"PROVIDER": "atk", "ATK_API_KEY": "k", "ATK_BASE_URL": s.url,
                   "ATK_MODEL": "m"}
            c = ap.complete([Message("user", "q")], env=env)
            self.assertEqual(c.provider, "atk")
            self.assertEqual(c.text, "hi")

    def test_usage_is_reported_and_absent_cost_stays_none(self):
        """An unreported cost must not become 0.0 — that reads as 'this request was free'."""
        with _Server([_openai_reply()]) as s:
            env = {"PROVIDER": "openai", "OPENAI_API_KEY": "k", "OPENAI_BASE_URL": s.url,
                   "OPENAI_MODEL": "m"}
            c = ap.complete([Message("user", "q")], env=env)
            self.assertEqual((c.usage.prompt_tokens, c.usage.total_tokens), (11, 14))
            self.assertIsNone(c.usage.cost_usd)


class TestReplaceable(unittest.TestCase):
    """§1: switching provider is one config change and works. No code edit."""

    def test_the_same_call_reaches_a_different_provider_by_config_alone(self):
        with _Server([_openai_reply(), _openai_reply()]) as atk_s, \
             _Server([_openai_reply(), _openai_reply()]) as other_s:
            base = {"ATK_API_KEY": "atk-key", "ATK_BASE_URL": atk_s.url, "ATK_MODEL": "m",
                    "DEEPSEEK_API_KEY": "ds-key", "DEEPSEEK_BASE_URL": other_s.url,
                    "DEEPSEEK_MODEL": "m"}
            msgs = [Message("user", "q")]

            first = ap.complete(msgs, env={**base, "PROVIDER": "atk"})
            second = ap.complete(msgs, env={**base, "PROVIDER": "deepseek"})

        self.assertEqual((first.provider, second.provider), ("atk", "deepseek"))
        self.assertEqual(len(atk_s.calls), 1, "the ATK server saw exactly the first call")
        self.assertEqual(len(other_s.calls), 1, "the second call went elsewhere")
        self.assertEqual(atk_s.calls[0]["headers"]["authorization"], "Bearer atk-key")
        self.assertEqual(other_s.calls[0]["headers"]["authorization"], "Bearer ds-key")

    def test_anthropic_uses_its_own_wire_format(self):
        reply = (200, {"model": "claude-x", "content": [{"type": "text", "text": "a"}],
                       "usage": {"input_tokens": 5, "output_tokens": 2}})
        with _Server([reply]) as s:
            env = {"PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "k",
                   "ANTHROPIC_BASE_URL": s.url.replace("/v1", ""), "ANTHROPIC_MODEL": "claude-x"}
            c = ap.complete([Message("system", "S"), Message("user", "q")], env=env)
        self.assertEqual(c.text, "a")
        self.assertEqual(c.usage.total_tokens, 7)
        call = s.calls[0]
        self.assertEqual(call["path"], "/v1/messages")
        self.assertEqual(call["headers"]["x-api-key"], "k")
        self.assertEqual(call["body"]["system"], "S", "system goes in its own field, not a turn")
        self.assertEqual([m["role"] for m in call["body"]["messages"]], ["user"])


class TestOptional(unittest.TestCase):
    """§1: the asset runs end to end with ATK fully removed."""

    def test_it_runs_with_no_atk_variables_at_all(self):
        with _Server([_openai_reply("fine")]) as s:
            env = {"PROVIDER": "openai", "OPENAI_API_KEY": "k", "OPENAI_BASE_URL": s.url,
                   "OPENAI_MODEL": "m"}
            self.assertFalse([k for k in env if k.startswith("ATK_")])
            self.assertEqual(ap.complete([Message("user", "q")], env=env).text, "fine")


class TestNoHardcodedSecrets(unittest.TestCase):
    """§3 rule 4: no ATK key, URL or model may be hardcoded anywhere in the source tree."""

    def test_the_source_contains_no_endpoint_key_or_model_literal(self):
        import pathlib
        src = pathlib.Path(ap.__file__).read_text()
        for forbidden in ("aitokenking", "sk-", "api.openai.com", "api.anthropic.com"):
            self.assertNotIn(forbidden, src,
                             f"{forbidden!r} is hardcoded; it belongs in .env only")

    def test_a_missing_key_fails_before_any_request_is_sent(self):
        with _Server([_openai_reply()]) as s:
            env = {"PROVIDER": "atk", "ATK_BASE_URL": s.url, "ATK_MODEL": "m"}  # no key
            with self.assertRaises(ap.ProviderError) as cm:
                ap.complete([Message("user", "q")], env=env)
            self.assertIn("ATK_API_KEY", str(cm.exception))
            self.assertEqual(s.calls, [], "nothing may be sent with an incomplete config")

    def test_an_unknown_provider_is_refused_rather_than_defaulted(self):
        with self.assertRaises(ap.ConfigError) as cm:
            ap.build_provider("not-a-provider", {})
        self.assertIn("Refusing to guess", str(cm.exception))


class TestErrorHandling(unittest.TestCase):
    def test_a_4xx_is_not_retried(self):
        """A 400 will still be a 400 on the third try; retrying only burns time."""
        with _Server([(400, {"error": "bad request"})]) as s:
            env = {"PROVIDER": "openai", "OPENAI_API_KEY": "k", "OPENAI_BASE_URL": s.url,
                   "OPENAI_MODEL": "m", "MAX_RETRIES": "3"}
            with self.assertRaises(ap.ProviderError):
                ap.complete([Message("user", "q")], env=env)
            self.assertEqual(len(s.calls), 1)

    def test_a_5xx_is_retried_then_falls_back(self):
        with _Server([(500, {"e": 1}), (500, {"e": 1})]) as bad, \
             _Server([_openai_reply("rescued")]) as good:
            env = {"PROVIDER": "atk", "ATK_API_KEY": "k", "ATK_BASE_URL": bad.url,
                   "ATK_MODEL": "m", "FALLBACK_PROVIDERS": "openai",
                   "OPENAI_API_KEY": "k2", "OPENAI_BASE_URL": good.url, "OPENAI_MODEL": "m",
                   "MAX_RETRIES": "2"}
            c = ap.complete([Message("user", "q")], env=env)
        self.assertEqual(c.text, "rescued")
        self.assertEqual(c.provider, "openai")
        self.assertEqual(len(bad.calls), 2, "MAX_RETRIES=2 means two attempts, then move on")

    def test_a_misconfigured_fallback_is_skipped_not_retried(self):
        with _Server([(500, {"e": 1})]) as bad, _Server([_openai_reply("ok")]) as good:
            env = {"PROVIDER": "atk", "ATK_API_KEY": "k", "ATK_BASE_URL": bad.url,
                   "ATK_MODEL": "m", "FALLBACK_PROVIDERS": "qwen,openai",
                   "OPENAI_API_KEY": "k", "OPENAI_BASE_URL": good.url, "OPENAI_MODEL": "m",
                   "MAX_RETRIES": "1"}
            c = ap.complete([Message("user", "q")], env=env)
        self.assertEqual(c.provider, "openai")

    def test_the_final_error_names_every_provider_tried(self):
        """"All providers failed" is not a debuggable message."""
        with _Server([(500, {"e": 1})]) as bad:
            env = {"PROVIDER": "atk", "ATK_API_KEY": "k", "ATK_BASE_URL": bad.url,
                   "ATK_MODEL": "m", "FALLBACK_PROVIDERS": "qwen", "MAX_RETRIES": "1"}
            with self.assertRaises(ap.ProviderError) as cm:
                ap.complete([Message("user", "q")], env=env)
        msg = str(cm.exception)
        self.assertIn("atk", msg)
        self.assertIn("qwen: not configured", msg)

    def test_a_wrong_shaped_response_is_reported_clearly(self):
        with _Server([(200, {"unexpected": True})]) as s:
            env = {"PROVIDER": "openai", "OPENAI_API_KEY": "k", "OPENAI_BASE_URL": s.url,
                   "OPENAI_MODEL": "m", "MAX_RETRIES": "1"}
            with self.assertRaises(ap.ProviderError) as cm:
                ap.complete([Message("user", "q")], env=env)
            self.assertIn("choices[0].message.content", str(cm.exception))


class TestRequestShape(unittest.TestCase):
    def test_messages_and_model_are_sent_as_the_openai_api_expects(self):
        with _Server([_openai_reply()]) as s:
            env = {"PROVIDER": "atk", "ATK_API_KEY": "k", "ATK_BASE_URL": s.url,
                   "ATK_MODEL": "my-model"}
            ap.complete([Message("system", "S"), Message("user", "U")], env=env,
                        temperature=0.2)
        body = s.calls[0]["body"]
        self.assertEqual(s.calls[0]["path"], "/v1/chat/completions")
        self.assertEqual(body["model"], "my-model")
        self.assertEqual(body["messages"],
                         [{"role": "system", "content": "S"}, {"role": "user", "content": "U"}])
        self.assertEqual(body["temperature"], 0.2)


class TestPR4ReviewFindings(unittest.TestCase):
    """The three findings from the PR #4 review of `f2a2188`, reproduced then closed.

    The lesson the reviewer named explicitly: *"do not let 'no sk- in the source' stand in for a
    runtime test"*. So every case here is a **canary at runtime** — a real secret value is
    configured, a real server echoes it, and the assertion is about what a human would actually
    see.
    """

    CANARY = "CANARY-SECRET-do-not-leak-7f3a9c"

    # ---- P4-01: credential in error output --------------------------------
    def test_a_rejecting_server_cannot_leak_the_key_through_the_error(self):
        """A 401 whose body echoes the credential. This leaked before the fix."""
        with _Server([(401, {"error": f"invalid credential {self.CANARY}"})]) as s:
            env = {"PROVIDER": "atk", "ATK_API_KEY": self.CANARY, "ATK_BASE_URL": s.url,
                   "ATK_MODEL": "m", "MAX_RETRIES": "1"}
            with self.assertRaises(ap.ProviderError) as cm:
                ap.complete([Message("user", "q")], env=env)
        self.assertNotIn(self.CANARY, str(cm.exception))
        self.assertIn("401", str(cm.exception), "the status must survive: it is the diagnostic")

    def test_the_opt_in_body_is_still_redacted(self):
        """Asking for the body is a debugging aid, not consent to print the key."""
        with _Server([(401, {"error": f"invalid credential {self.CANARY}"})]) as s:
            env = {"PROVIDER": "atk", "ATK_API_KEY": self.CANARY, "ATK_BASE_URL": s.url,
                   "ATK_MODEL": "m", "MAX_RETRIES": "1", "ATK_INCLUDE_ERROR_BODY": "1"}
            with self.assertRaises(ap.ProviderError) as cm:
                ap.complete([Message("user", "q")], env=env)
        msg = str(cm.exception)
        self.assertNotIn(self.CANARY, msg)
        self.assertIn(ap.REDACTED, msg)
        self.assertIn("invalid credential", msg, "the useful prose still comes through")

    def test_the_aggregated_fallback_error_is_redacted(self):
        """Each adapter redacts its own message; the summary must not reassemble a secret."""
        with _Server([(401, {"error": self.CANARY})]) as a_s, \
             _Server([(401, {"error": self.CANARY})]) as b_s:
            env = {"PROVIDER": "atk", "ATK_API_KEY": self.CANARY, "ATK_BASE_URL": a_s.url,
                   "ATK_MODEL": "m", "FALLBACK_PROVIDERS": "openai",
                   "OPENAI_API_KEY": self.CANARY, "OPENAI_BASE_URL": b_s.url,
                   "OPENAI_MODEL": "m", "MAX_RETRIES": "1", "ATK_INCLUDE_ERROR_BODY": "1"}
            with self.assertRaises(ap.ProviderError) as cm:
                ap.complete([Message("user", "q")], env=env)
        self.assertNotIn(self.CANARY, str(cm.exception))

    def test_an_unreachable_host_cannot_leak_a_key_in_the_url(self):
        """Some gateways carry credentials in the query string."""
        env = {"PROVIDER": "custom", "CUSTOM_API_KEY": self.CANARY, "MAX_RETRIES": "1",
               "CUSTOM_BASE_URL": f"http://127.0.0.1:1/v1?token={self.CANARY}",
               "CUSTOM_MODEL": "m"}
        with self.assertRaises(ap.ProviderError) as cm:
            ap.complete([Message("user", "q")], env=env)
        self.assertNotIn(self.CANARY, str(cm.exception))

    # ---- P4-02: a 200 with no text is not a summary -----------------------
    def test_a_200_with_null_content_is_a_failure_not_an_empty_summary(self):
        """This returned Completion(text=None); the example printed "None" and exited 0."""
        with _Server([(200, {"model": "m", "usage": {},
                             "choices": [{"message": {"content": None},
                                          "finish_reason": "tool_calls"}]})]) as s:
            env = {"PROVIDER": "atk", "ATK_API_KEY": "k", "ATK_BASE_URL": s.url,
                   "ATK_MODEL": "m", "MAX_RETRIES": "1"}
            with self.assertRaises(ap.ProviderError) as cm:
                ap.complete([Message("user", "q")], env=env)
        self.assertIn("no text", str(cm.exception))
        self.assertIn("tool_calls", str(cm.exception), "say WHY it was empty")

    def test_whitespace_only_and_wrong_typed_content_also_fail(self):
        for content in ("   \n  ", 42, [], {}):
            with self.subTest(content=content):
                with _Server([(200, {"model": "m", "usage": {},
                                     "choices": [{"message": {"content": content}}]})]) as s:
                    env = {"PROVIDER": "atk", "ATK_API_KEY": "k", "ATK_BASE_URL": s.url,
                           "ATK_MODEL": "m", "MAX_RETRIES": "1"}
                    with self.assertRaises(ap.ProviderError):
                        ap.complete([Message("user", "q")], env=env)

    def test_an_empty_anthropic_reply_also_fails(self):
        with _Server([(200, {"model": "c", "content": [], "usage": {}})]) as s:
            env = {"PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "k",
                   "ANTHROPIC_BASE_URL": s.url.replace("/v1", ""), "ANTHROPIC_MODEL": "c",
                   "MAX_RETRIES": "1"}
            with self.assertRaises(ap.ProviderError):
                ap.complete([Message("user", "q")], env=env)

    def test_real_text_still_succeeds(self):
        """CONTROL. Rejecting everything would be its own defect."""
        with _Server([_openai_reply("a genuine summary")]) as s:
            env = {"PROVIDER": "atk", "ATK_API_KEY": "k", "ATK_BASE_URL": s.url,
                   "ATK_MODEL": "m"}
            self.assertEqual(ap.complete([Message("user", "q")], env=env).text,
                             "a genuine summary")

    # ---- P4-03: documentation matches the implementation -------------------
    def test_the_env_template_carries_the_official_base_url(self):
        env_example = (pathlib.Path(__file__).parent / ".env.example").read_text()
        self.assertIn("https://api.aitokenking.com.tw/api/v1", env_example)
        self.assertNotIn("ATK_BASE_URL=https://api.aitokenking.com/v1", env_example,
                         "the old URL was missing .tw and /api and did not resolve")

    def test_the_official_key_name_is_accepted_as_an_alias(self):
        """The docs say AITOKENKING_API_KEY; the contract says ATK_API_KEY. Both must work."""
        p = ap.build_provider("atk", {"AITOKENKING_API_KEY": "k",
                                      "ATK_BASE_URL": "https://example.invalid/api/v1",
                                      "ATK_MODEL": "m"})
        self.assertEqual(p.name, "atk")

    def test_show_payload_prints_the_complete_body_and_never_a_header(self):
        import subprocess, sys, tempfile, os
        with tempfile.TemporaryDirectory() as td:
            log = pathlib.Path(td) / "x.log"
            log.write_text("ERROR: boom at a.c:1\n" + "pad\n" * 50)
            r = subprocess.run(
                [sys.executable, "example_summarise_tool_output.py", "--dry-run",
                 "--show-payload", "--file", str(log)],
                capture_output=True, text=True, cwd=str(pathlib.Path(__file__).parent),
                env={**os.environ, "PROVIDER": "atk", "ATK_API_KEY": self.CANARY,
                     "ATK_BASE_URL": "https://example.invalid/api/v1", "ATK_MODEL": "m"})
        self.assertEqual(r.returncode, 0, r.stderr)
        payload = json.loads(r.stdout[r.stdout.index("{"):])   # the body is the JSON tail
        self.assertEqual(payload["model"], "m")
        self.assertEqual([m["role"] for m in payload["messages"]], ["system", "user"])
        self.assertIn("ERROR: boom at a.c:1", payload["messages"][1]["content"])
        self.assertNotIn(self.CANARY, r.stdout, "a dry run must never print the key")
        self.assertNotIn("Authorization", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)

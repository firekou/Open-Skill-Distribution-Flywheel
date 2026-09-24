"""Tests for the offline config check, including the negative controls.

Each passing case has a matching case that must be rejected, so a check that
simply returned 0 would fail this suite.
"""

import unittest

from check_config import report

GOOD = {
    "OPENAI_API_BASE": "https://endpoint.example.com/v1",
    "OPENAI_API_KEY": "any-non-empty-value",
    "AIDER_MODEL": "openai/some-model",
}


def with_change(**changes):
    env = dict(GOOD)
    env.update(changes)
    return env


class ReportTest(unittest.TestCase):
    def test_complete_settings_pass(self):
        code, _ = report(GOOD)
        self.assertEqual(code, 0)

    def test_each_missing_value_is_caught(self):
        for name in ("OPENAI_API_BASE", "OPENAI_API_KEY", "AIDER_MODEL"):
            with self.subTest(name=name):
                code, lines = report(with_change(**{name: ""}))
                self.assertEqual(code, 2)
                self.assertIn(name, "\n".join(lines))

    def test_model_without_provider_prefix_is_caught(self):
        code, lines = report(with_change(AIDER_MODEL="some-model"))
        self.assertEqual(code, 3)
        self.assertIn("openai/some-model", "\n".join(lines))

    def test_another_providers_prefix_is_caught(self):
        # Found by review: a slash alone used to be enough, so anthropic/model
        # passed while the documented promise was openai/ only.
        for model in ("anthropic/model", "gemini/some-model", "ollama/llama3"):
            with self.subTest(model=model):
                code, lines = report(with_change(AIDER_MODEL=model))
                self.assertEqual(code, 3)
                self.assertIn("OPENAI_API_BASE", "\n".join(lines))

    def test_prefix_with_no_model_name_is_caught(self):
        code, lines = report(with_change(AIDER_MODEL="openai/"))
        self.assertEqual(code, 3)
        self.assertIn("no model", "\n".join(lines))

    def test_a_model_name_containing_slashes_still_passes(self):
        # Several OpenAI-compatible endpoints serve names like
        # meta-llama/Llama-3, so only the first segment is the prefix.
        code, _ = report(with_change(AIDER_MODEL="openai/meta-llama/Llama-3"))
        self.assertEqual(code, 0)

    def test_base_ending_in_a_route_is_caught(self):
        code, lines = report(
            with_change(OPENAI_API_BASE="https://endpoint.example.com/v1/chat/completions")
        )
        self.assertEqual(code, 4)
        self.assertIn("/chat/completions", "\n".join(lines))

    def test_a_trailing_slash_does_not_change_the_verdict(self):
        code, _ = report(with_change(OPENAI_API_BASE="https://endpoint.example.com/v1/"))
        self.assertEqual(code, 0)

    # Negative controls: the key must never appear, whole or in part.
    def test_the_key_is_never_printed(self):
        secret = "sk-thisexactstringmustnotappear"
        for env in (with_change(OPENAI_API_KEY=secret), with_change(AIDER_MODEL="bare")):
            _, lines = report(env)
            text = "\n".join(lines)
            self.assertNotIn(secret, text)
            for size in (8, 6, 4):
                self.assertNotIn(secret[:size], text)
                self.assertNotIn(secret[-size:], text)

    def test_no_url_is_invented(self):
        # The tool must not offer a replacement URL of its own.
        _, lines = report(
            with_change(OPENAI_API_BASE="https://endpoint.example.com/v1/chat/completions")
        )
        text = "\n".join(lines)
        self.assertNotIn("https://api.openai.com", text)

    def test_it_makes_no_network_call(self):
        # A guard against the checker growing a client later: the module must
        # not import anything that can open a connection.
        import ast
        import pathlib

        source = pathlib.Path(__file__).with_name("check_config.py").read_text()
        imported = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported - {"os", "sys"}, set())


if __name__ == "__main__":
    unittest.main(verbosity=2)

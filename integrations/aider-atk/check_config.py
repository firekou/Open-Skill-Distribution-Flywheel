#!/usr/bin/env python3
"""Offline check of the three environment values aider needs for an
OpenAI-compatible endpoint. It reads the environment and prints what it finds.

It makes no network request, builds no HTTP client, and forwards nothing. It
cannot tell you whether your endpoint works — only whether the settings are
the shape aider expects. Passing here is not evidence that a call succeeded.

It never prints your key, or any part of it. Only SET or NOT_SET.

Exit codes
  0  the three values are present and nothing looked wrong
  2  a required value is missing
  3  the model name carries no provider prefix
  4  the base URL looks like a full endpoint path, not the API root
"""

import os
import sys

REQUIRED = ("OPENAI_API_BASE", "OPENAI_API_KEY", "AIDER_MODEL")

# Paths that belong to a specific endpoint rather than to the API root. aider
# hands the base to litellm, which appends the route itself, so a base that
# already ends in one of these produces a doubled path.
ENDPOINT_TAILS = ("/chat/completions", "/completions", "/responses", "/embeddings")


def report(env):
    """Return (exit_code, lines). Pure function so the tests can drive it."""
    lines = []
    missing = [name for name in REQUIRED if not env.get(name)]

    for name in REQUIRED:
        if name == "OPENAI_API_KEY":
            lines.append(f"{name}: {'SET' if env.get(name) else 'NOT_SET'}")
        else:
            value = env.get(name)
            lines.append(f"{name}: {value if value else 'NOT_SET'}")

    if missing:
        lines.append("")
        lines.append("Missing: " + ", ".join(missing))
        lines.append(
            "Set all three in the environment. Do not pass the key on the command"
            " line: it lands in your shell history and in process listings."
        )
        return 2, lines

    base = env["OPENAI_API_BASE"].rstrip("/")
    model = env["AIDER_MODEL"]

    if "/" not in model:
        lines.append("")
        lines.append(f"The model name {model!r} carries no provider prefix.")
        lines.append(
            "For an OpenAI-compatible endpoint aider expects openai/<model>, so"
            f" this is most likely meant to be 'openai/{model}'. Without the"
            " prefix the request is routed by aider's own model registry"
            " instead of to your endpoint."
        )
        return 3, lines

    for tail in ENDPOINT_TAILS:
        if base.endswith(tail):
            lines.append("")
            lines.append(f"OPENAI_API_BASE ends in {tail!r}.")
            lines.append(
                "This wants the API root, not a specific route — the route is"
                f" appended for you, so this would be requested as {base}{tail}."
                " Remove the trailing route. This check does not guess the"
                " correct URL for you; take it from your provider's own docs."
            )
            return 4, lines

    lines.append("")
    lines.append(
        "Shape looks right. This says nothing about whether the endpoint"
        " answers, whether the key is valid, or whether the model exists"
        " there — none of that can be known without a real call."
    )
    return 0, lines


def main():
    code, lines = report(os.environ)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())

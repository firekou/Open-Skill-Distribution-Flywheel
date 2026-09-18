#!/usr/bin/env python3
"""Runnable example: summarise long tool output through whichever provider is configured.

The user problem is the one every agent operator meets on day one: a command produced 4,000
lines, the model needs the three that matter, and pasting the lot is what makes an agent
expensive and forgetful. It is also the problem `headroom` (registry `token-optimization`,
Apache-2.0) addresses from the other side, which is why that is the named next integration —
see README.md. **This example does not use headroom and makes no compression claim.**

What it demonstrates, and all it demonstrates: one real workflow reaching a model through the
Provider Interface, with the provider chosen by configuration alone.

    python3 example_summarise_tool_output.py --file build.log
    cat build.log | python3 example_summarise_tool_output.py
    PROVIDER=openai python3 example_summarise_tool_output.py --file build.log   # same code path

    python3 example_summarise_tool_output.py --dry-run --file build.log
        Shows what WOULD be sent and sends nothing. Works with no credential, which makes it
        the honest way to read this file before spending anything. Add --show-payload for the
        complete JSON body; headers are never printed, because one of them is your key.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from atk_provider import Message, ProviderError, build_provider, complete

SYSTEM = (
    "You summarise machine output for an engineer who has to act on it. "
    "Answer in at most five bullet points: what failed or changed, the exact identifiers "
    "(file, line, error code) needed to act, and anything that looks like a secret or a "
    "credential. If nothing failed, say so in one line rather than inventing significance."
)


def build_messages(text: str, limit: int) -> list[Message]:
    """Keep the head and the tail, and say so where the middle was removed.

    Truncation is stated in the prompt rather than done silently, because a model that is not
    told it received an excerpt will confidently summarise the excerpt as the whole.
    """
    if len(text) <= limit:
        body = text
    else:
        head, tail = text[: limit // 2], text[-limit // 2:]
        body = (f"{head}\n\n[... {len(text) - limit} characters removed from the middle of this "
                f"output; you are seeing the first and last {limit // 2} characters ...]\n\n{tail}")
    return [Message("system", SYSTEM), Message("user", f"Summarise this output:\n\n{body}")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", help="file to summarise; omit to read stdin")
    ap.add_argument("--max-chars", type=int, default=12000,
                    help="excerpt size before the middle is dropped (default 12000)")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would be sent and send nothing; needs no credential")
    ap.add_argument("--show-payload", action="store_true",
                    help="with --dry-run, print the COMPLETE JSON request body. Headers are "
                         "never printed: the Authorization header carries your key")
    a = ap.parse_args(argv)

    text = open(a.file, encoding="utf-8", errors="replace").read() if a.file else sys.stdin.read()
    if not text.strip():
        print("nothing to summarise: input was empty", file=sys.stderr)
        return 2
    messages = build_messages(text, a.max_chars)

    if a.dry_run:
        selected = (os.environ.get("PROVIDER") or "atk").lower()
        print(f"PROVIDER={selected}")
        provider = None
        try:
            provider = build_provider()
            print(f"would call: {provider.name} / model {provider.model}")
        except Exception as exc:                      # ConfigError, printed not raised
            print(f"provider not configured: {exc}")
        print(f"input {len(text)} chars -> prompt {sum(len(m.content) for m in messages)} chars")

        if a.show_payload:
            # P4-03 asked for the complete body; P4-R2-02 found that building it here produced an
            # OpenAI shape even for Anthropic, which hoists `system` and adds `max_tokens`. A
            # preview assembled separately from the request is a second implementation that can
            # drift, and it did. It now comes from the adapter that would send it.
            if provider is None:
                print("--- cannot show the request body: no provider is configured ---")
                print("    The body depends on the adapter (Anthropic hoists `system` and adds")
                print("    `max_tokens`), so it is not guessed. Fill in .env and re-run.")
            else:
                body = provider.build_payload(messages)
                print(f"--- complete request body as {provider.name} would send it "
                      "(headers omitted: they carry your key) ---")
                print(json.dumps(body, ensure_ascii=False, indent=2))
        else:
            print("--- messages (PREVIEW, first 300 chars each) ---")
            for m in messages:
                clipped = len(m.content) > 300
                print(f"[{m.role}] {m.content[:300]}{'...' if clipped else ''}")
            print("--- use --show-payload for the complete request body ---")
        return 0

    try:
        c = complete(messages)
    except ProviderError as exc:
        print(f"request failed:\n{exc}", file=sys.stderr)
        return 1

    print(c.text)
    # §1 Transparent: always say who served this. Tokens are what the provider reported; an
    # unreported cost prints as "not reported", never as 0.
    cost = f"${c.usage.cost_usd:.6f}" if c.usage.cost_usd is not None else "not reported"
    print(f"\n--- served by {c.provider} / {c.model} · "
          f"{c.usage.prompt_tokens} in, {c.usage.completion_tokens} out · cost {cost}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

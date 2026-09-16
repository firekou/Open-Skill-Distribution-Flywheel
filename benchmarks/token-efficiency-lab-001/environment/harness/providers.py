"""Provider adapters.

Two of them, and the distinction is load-bearing.

`ReplayProvider` replays recorded provider responses from a fixture file. It is offline,
deterministic, and it is NOT a model. It can prove that the harness plumbing works. It can
prove nothing whatsoever about token optimisation, because there is no model in the loop.
Anything it produces is marked run_class="dry_run" and may never be reported as a benchmark
result.

`LiveProvider` talks to a real provider. It refuses to start unless a credential provisioned
specifically for this lab is present, and it will not fall back to an ambient production key.
"""
from __future__ import annotations

import json
import os
import pathlib
import time
from typing import Iterator

from .meter import CallUsage


class ProviderError(RuntimeError):
    pass


class CredentialRefused(ProviderError):
    """Raised instead of quietly using a key that was not provisioned for this lab."""


# Credentials that may be present in an operator's shell for unrelated production work. The
# harness must never pick one of these up by accident: a benchmark that silently bills a
# production account is a governance failure regardless of the numbers it produces.
FORBIDDEN_AMBIENT_KEYS = (
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "MISTRAL_API_KEY",
    "GROQ_API_KEY",
    "TOGETHER_API_KEY",
    "OPENROUTER_API_KEY",
    "DEEPSEEK_API_KEY",
)

# The only credential this harness will use. It must be provisioned for the lab, scoped to the
# benchmark, and rate/spend limited. Provisioning it is an Editor-in-Chief decision, not the
# harness's.
LAB_CREDENTIAL_ENV = "LAB001_BENCHMARK_API_KEY"


class ReplayProvider:
    """Deterministic offline replay of recorded provider responses.

    The fixture supplies the `usage` block verbatim as a real provider returned it (or, for a
    synthetic fixture, as a clearly-labelled synthetic block). The meter accumulates it exactly
    as it would accumulate a live response, which is precisely what makes the accumulator
    testable without spending money or shipping a task to a third party.
    """

    name = "replay"
    is_live = False

    def __init__(self, fixture_path: pathlib.Path) -> None:
        self._fixture = json.loads(pathlib.Path(fixture_path).read_text())
        self._synthetic = bool(self._fixture.get("synthetic", True))
        self._calls = self._fixture["calls"]

    @property
    def synthetic(self) -> bool:
        return self._synthetic

    def run_task(self, task_id: str) -> Iterator[tuple[CallUsage, dict]]:
        """Yield (usage, raw_response) for each recorded call of this task."""
        matched = [c for c in self._calls if c["task_id"] == task_id]
        if not matched:
            raise ProviderError(
                f"no recorded calls for task {task_id} in this fixture; the replay cannot "
                "invent a response and the run is recorded as a failure, not skipped"
            )
        for call in matched:
            usage = call["usage"]
            started = time.monotonic()
            yield (
                CallUsage(
                    provider=call["provider"],
                    model=call["model"],
                    model_version=call["model_version"],
                    input_tokens=usage["input_tokens"],
                    output_tokens=usage["output_tokens"],
                    cached_tokens=usage.get("cached_tokens", 0),
                    tool_tokens=usage.get("tool_tokens"),
                    source="provider_usage_field",
                    accepted=call.get("accepted", True),
                    role=call.get("role", "primary"),
                    cache_state=call.get("cache_state", "cold"),
                    latency_ms=call.get("latency_ms", 0),
                    raw_usage=dict(usage),
                ),
                call,
            )
            del started


class LiveProvider:
    """Real provider calls. Refuses to run on an ambient production credential."""

    is_live = True

    def __init__(self, name: str, model: str) -> None:
        self.name = name
        self.model = model
        self._key = self._resolve_credential()

    @staticmethod
    def _resolve_credential() -> str:
        key = os.environ.get(LAB_CREDENTIAL_ENV)
        if key:
            return key
        present = [k for k in FORBIDDEN_AMBIENT_KEYS if os.environ.get(k)]
        if present:
            raise CredentialRefused(
                "refusing to run: "
                + ", ".join(present)
                + " is present in the environment, but these are production credentials and "
                "guardrail 10 forbids their use. Provision a lab-scoped, spend-limited key as "
                f"{LAB_CREDENTIAL_ENV} instead."
            )
        raise CredentialRefused(
            f"no benchmark credential. {LAB_CREDENTIAL_ENV} is not set, so no live provider "
            "call can be made and no provider-native usage field can be obtained. This is a "
            "declared stop condition (METHODOLOGY_v1.0.0.md, 'benchmark credentials are "
            "unavailable'): record the failure, do not improvise around it."
        )

    def run_task(self, task_id: str):  # pragma: no cover - never exercised without a credential
        raise NotImplementedError(
            "live execution is enabled only for LG4; this round is infrastructure verification"
        )


def credential_status() -> dict:
    """Report credential availability WITHOUT reading or echoing any secret value."""
    return {
        "lab_credential_env": LAB_CREDENTIAL_ENV,
        "lab_credential_present": bool(os.environ.get(LAB_CREDENTIAL_ENV)),
        "ambient_production_keys_present": [
            k for k in FORBIDDEN_AMBIENT_KEYS if os.environ.get(k)
        ],
        "live_provider_available": bool(os.environ.get(LAB_CREDENTIAL_ENV)),
    }

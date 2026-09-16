"""Meter calibration.

Two distinct things are being asked, and conflating them is the mistake this module exists to
prevent.

**Question 1 — is ATK's accumulator correct?**
Given a set of per-call provider `usage` blocks, does the meter produce the right run totals?
Does it count retry tokens instead of discarding them? Does it keep cached tokens separate
instead of folding them into input? Does it attribute escalation tokens to the model escalated
TO? Does it price each call at that call's own rate? This is arithmetic over numbers whose
origin does not matter, so it is answerable offline, and answering it offline is not a
shortcut.

**Question 2 — do the numbers ATK reads match what the provider actually charged?**
This requires issuing real requests to a real provider and reading the `usage` field that comes
back. There is no offline substitute. Without a benchmark credential it cannot be answered, and
the frozen methodology names that exact situation as a declared stop condition.

`calibrate_accumulator()` answers question 1. `calibrate_against_provider()` answers question 2
and refuses to pretend when it cannot.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

from .meter import CallUsage, TokenMeter
from .pricing import PricingSnapshot
from .providers import CredentialRefused, credential_status

# METER_CALIBRATION_v1.0.0.md section "Calibration procedure", step 3.
ACCEPTANCE_RELATIVE_ERROR = 0.01


@dataclass
class QuantityResult:
    quantity: str
    expected: float
    measured: float
    relative_error: float
    within_acceptance: bool
    gating: bool

    @property
    def verdict(self) -> str:
        return "PASS" if self.within_acceptance else "FAIL"


@dataclass
class CalibrationResult:
    case_id: str
    description: str
    quantities: list[QuantityResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(q.within_acceptance for q in self.quantities if q.gating)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "passed": self.passed,
            "quantities": [
                {
                    "quantity": q.quantity,
                    "expected": q.expected,
                    "measured": q.measured,
                    "relative_error": q.relative_error,
                    "within_acceptance": q.within_acceptance,
                    "gating": q.gating,
                    "verdict": q.verdict,
                }
                for q in self.quantities
            ],
        }


def _relative_error(expected: float, measured: float) -> float:
    if expected == 0:
        return 0.0 if measured == 0 else float("inf")
    return abs(measured - expected) / abs(expected)


# The three quantities the frozen acceptance criterion gates on. The others are reported so a
# regression in them is visible, but they do not by themselves fail calibration.
GATING = {"input_tokens", "output_tokens", "total_tokens"}


def calibrate_accumulator(case: dict, snapshot: PricingSnapshot) -> CalibrationResult:
    """Question 1. Run the meter over a case's calls and compare against expected totals.

    The expected totals in a case are computed independently of the meter — that is the whole
    point. A case whose expectations were produced by running the meter would prove only that
    the meter agrees with itself.
    """
    meter = TokenMeter(snapshot)
    for c in case["calls"]:
        u = c["usage"]
        meter.record(
            CallUsage(
                provider=c["provider"],
                model=c["model"],
                model_version=c["model_version"],
                input_tokens=u["input_tokens"],
                output_tokens=u["output_tokens"],
                cached_tokens=u.get("cached_tokens", 0),
                accepted=c.get("accepted", True),
                role=c.get("role", "primary"),
                cache_state=c.get("cache_state", "cold"),
                latency_ms=c.get("latency_ms", 0),
                raw_usage=dict(u),
            )
        )
    totals = meter.totals()
    measured = {
        "input_tokens": totals.input_tokens,
        "output_tokens": totals.output_tokens,
        "total_tokens": totals.total_tokens,
        "cached_tokens": totals.cached_tokens,
        "retry_input_tokens": totals.retry_input_tokens,
        "retry_output_tokens": totals.retry_output_tokens,
        "escalation_input_tokens": totals.escalation_input_tokens,
        "escalation_output_tokens": totals.escalation_output_tokens,
        "model_calls": totals.model_calls,
        "retries": totals.retries,
        "escalations": totals.escalations,
        "cost": round(totals.cost, 10),
    }
    result = CalibrationResult(case_id=case["case_id"], description=case["description"])
    for quantity, expected in case["expected"].items():
        got = measured[quantity]
        err = _relative_error(expected, got)
        result.quantities.append(
            QuantityResult(
                quantity=quantity,
                expected=expected,
                measured=got,
                relative_error=err,
                within_acceptance=err <= ACCEPTANCE_RELATIVE_ERROR,
                gating=quantity in GATING,
            )
        )
    return result


def bytes_over_four(text: str) -> int:
    """The PROHIBITED estimator, implemented here and nowhere else.

    It exists in this file so its error can be measured and reported rather than asserted. It is
    never importable into the run path: nothing in `runner.py`, `meter.py` or `record.py`
    references it, and `CallUsage` rejects any token_source that is not the provider usage field.
    """
    return len(text.encode("utf-8")) // 4


def demonstrate_estimator_error(samples: list[dict]) -> dict:
    """Compare bytes/4 against the recorded usage figure for each sample.

    IMPORTANT: on a synthetic fixture the 'recorded' figure is itself synthetic, so the error
    computed here characterises the estimator against the fixture's assumed tokenizer ratio and
    NOT against any real provider. It is illustrative. It is not evidence about OpenAI,
    Anthropic or DeepSeek, and must never be quoted as if it were.
    """
    rows = []
    for s in samples:
        est = bytes_over_four(s["text"])
        truth = s["recorded_tokens"]
        rows.append(
            {
                "sample_id": s["sample_id"],
                "kind": s["kind"],
                "bytes": len(s["text"].encode("utf-8")),
                "estimated_tokens_bytes_over_4": est,
                "recorded_tokens": truth,
                "relative_error": _relative_error(truth, est),
            }
        )
    worst = max(rows, key=lambda r: r["relative_error"]) if rows else None
    return {
        "samples": rows,
        "worst_case": worst,
        "caveat": (
            "synthetic fixture: the 'recorded' counts are assumed, not provider-reported. "
            "This characterises the estimator against the fixture, not against any real "
            "provider, and may not be quoted as evidence about one."
        ),
    }


def calibrate_against_provider(provider_name: str, model: str) -> dict:
    """Question 2. Requires a live provider. Refuses rather than substituting."""
    status = credential_status()
    if not status["live_provider_available"]:
        raise CredentialRefused(
            "meter-versus-provider calibration cannot be performed: no benchmark credential is "
            f"available ({status['lab_credential_env']} is unset), so no provider-native usage "
            "field can be obtained for any request. METHODOLOGY_v1.0.0.md declares this a stop "
            "condition ('benchmark credentials are unavailable'): record the failure, do not "
            "improvise around it. An offline accumulator check is a different question and is "
            "not a substitute."
        )
    raise NotImplementedError(
        "live calibration is enabled for LG4; this round verifies infrastructure only"
    )


def run_suite(fixture_path: pathlib.Path, snapshot: PricingSnapshot) -> dict:
    fixture = json.loads(pathlib.Path(fixture_path).read_text())
    results = [calibrate_accumulator(c, snapshot) for c in fixture["cases"]]
    estimator = demonstrate_estimator_error(fixture.get("estimator_samples", []))

    provider_check: dict
    try:
        calibrate_against_provider("any", "any")
        provider_check = {"status": "RAN", "detail": "unexpected"}
    except CredentialRefused as exc:
        provider_check = {"status": "BLOCKED", "detail": str(exc)}
    except NotImplementedError as exc:
        provider_check = {"status": "NOT_IMPLEMENTED_THIS_ROUND", "detail": str(exc)}

    failed = [r for r in results if not r.passed]
    return {
        "fixture": str(fixture_path),
        "fixture_sha256": __import__("hashlib")
        .sha256(pathlib.Path(fixture_path).read_bytes())
        .hexdigest(),
        "acceptance_relative_error": ACCEPTANCE_RELATIVE_ERROR,
        "accumulator": {
            "cases_run": len(results),
            "cases_passed": len(results) - len(failed),
            "cases_failed": len(failed),
            "verdict": "PASS" if not failed else "FAIL",
            "results": [r.to_dict() for r in results],
        },
        "estimator_demonstration": estimator,
        "provider_native_comparison": provider_check,
        "overall_verdict": (
            "PASS"
            if (not failed and provider_check["status"] == "RAN")
            else "INCOMPLETE - accumulator only"
        ),
        "what_this_does_not_establish": [
            "the meter has never been compared against a real provider's usage field",
            "no figure here describes any real provider's tokenizer",
            "Phase E as specified is NOT satisfied by an accumulator-only result",
        ],
    }


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Lab 001 meter calibration")
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    snapshot = PricingSnapshot(pathlib.Path(args.snapshot))
    report = run_suite(pathlib.Path(args.fixture), snapshot)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.out:
        p = pathlib.Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n")
    return 0 if report["accumulator"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())

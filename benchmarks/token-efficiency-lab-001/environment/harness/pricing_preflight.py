"""Pricing completeness preflight — CR-001-C.

METHODOLOGY v1.0.0 §11 required a pricing snapshot. It did not require the snapshot to be able to
**price the quantities §9 forces every record to report**. It could not: 12 of the 15 rates in
`PS-2026-09-15` carried no cache-read rate — every OpenAI model and every Anthropic model. The
meter refused to price a cached call rather than folding cached tokens in at the full input rate,
which on a cache-heavy call would have overstated cost by 5.41×. Correct behaviour, and it left
most of C2 and C3 unpriceable.

This module turns that from a runtime surprise into a **blocking preflight**. Three rules give it
teeth:

**Completeness is judged against what the provider CAN return, not what the plan declares.** A run
plan that says "cold" does not stop a provider serving a cache hit. If a model supports caching,
the cache rates are applicable whether or not the plan intends to use them.

**A missing rate is never zero.** A dimension the vendor genuinely does not bill is recorded
`not_applicable` **with the evidence for that claim**. `not_applicable` without evidence is a
block, because "we could not find it" and "it does not exist" are different statements and only
one of them is a fact.

**BLOCKED is a first-class outcome.** Where a vendor page or a credential is unavailable, the row
records `BLOCKED` and what is missing. No price is invented, and no plaintext credential is ever
requested or displayed.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

# Every billing dimension an LLM API can charge for that this lab can encounter.
DIMENSIONS = (
    "input",            # standard prompt tokens
    "output",           # completion tokens
    "cache_read",       # tokens served from a provider cache
    "cache_write",      # tokens written into a provider cache
    "cache_ttl",        # TTL tiers, where the vendor prices them separately
    "other_fees",       # per-request, per-tool, or platform fees
)

REQUIRED_PROVENANCE = ("source_url", "retrieved_on", "currency", "billing_unit")

# Inclusion relationships the meter needs in order not to double-count (METER_CALIBRATION v1.1.0).
REQUIRED_INCLUSION = ("cached_tokens_in_input", "reasoning_tokens_in_output", "reports_total")


@dataclass
class Finding:
    level: str            # BLOCK | WARN | OK
    model: str
    dimension: str
    message: str


@dataclass
class PreflightResult:
    snapshot_id: str
    models_checked: list = field(default_factory=list)
    findings: list = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(f.level == "BLOCK" for f in self.findings)

    @property
    def verdict(self) -> str:
        return "BLOCK" if self.blocked else "PASS"

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "verdict": self.verdict,
            "models_checked": self.models_checked,
            "blocks": [f.__dict__ for f in self.findings if f.level == "BLOCK"],
            "warnings": [f.__dict__ for f in self.findings if f.level == "WARN"],
            "note": (
                "A PASS here means every applicable rate is present with provenance. It does NOT "
                "mean provider-native meter calibration has been performed - that is a separate "
                "gate and neither implies the other (METHODOLOGY v1.1.0 section 11.8)."
            ),
        }


def _check_dimension(model: str, dim: str, entry: dict, out: list[Finding]) -> None:
    rates = entry.get("rates", {})
    applic = entry.get("applicable_dimensions")
    if applic is None:
        out.append(Finding("BLOCK", model, dim,
            "the snapshot does not declare which dimensions this model bills, so completeness "
            "cannot be judged. Declare applicable_dimensions."))
        return
    if dim not in applic:
        na = entry.get("not_applicable", {}).get(dim)
        if not na or not na.get("evidence"):
            out.append(Finding("BLOCK", model, dim,
                f"{dim} is excluded from applicable_dimensions but carries no evidence for that "
                "claim. 'we could not find it' and 'it does not exist' are different statements."))
        return
    value = rates.get(dim)
    if value is None:
        out.append(Finding("BLOCK", model, dim,
            f"{dim} is applicable but has no rate. A missing rate is never zero; any run touching "
            "this dimension would be unpriceable."))
        return
    if value == "BLOCKED":
        out.append(Finding("BLOCK", model, dim,
            f"{dim} is recorded BLOCKED - the source was unavailable. Execution cannot proceed "
            "against a rate nobody has read."))
        return
    if not isinstance(value, (int, float)) or value < 0:
        out.append(Finding("BLOCK", model, dim, f"{dim} rate {value!r} is not a non-negative number"))


def check(snapshot: dict, models: list[str]) -> PreflightResult:
    res = PreflightResult(snapshot_id=snapshot.get("pricing_snapshot_id", "<missing>"),
                          models_checked=sorted(models))
    if res.snapshot_id == "<missing>":
        res.findings.append(Finding("BLOCK", "-", "-", "the snapshot has no pricing_snapshot_id"))
    entries = snapshot.get("models", {})

    for model in sorted(models):
        entry = entries.get(model)
        if entry is None:
            res.findings.append(Finding("BLOCK", model, "-",
                "the run plan uses this model and the snapshot does not price it"))
            continue
        for f in REQUIRED_PROVENANCE:
            if not entry.get("provenance", {}).get(f):
                res.findings.append(Finding("BLOCK", model, "provenance",
                    f"missing {f}. A rate with no source and no date cannot be audited later."))
        for dim in DIMENSIONS:
            _check_dimension(model, dim, entry, res.findings)
        incl = entry.get("token_inclusion", {})
        for f in REQUIRED_INCLUSION:
            if f not in incl:
                res.findings.append(Finding("BLOCK", model, "token_inclusion",
                    f"{f} is not declared. Guessing it double-counts by exactly the cached "
                    "portion, which on a cache-heavy run is most of the bill."))
        if entry.get("plan") is None:
            res.findings.append(Finding("BLOCK", model, "plan",
                "the API plan is not recorded; rates differ by plan"))
    return res


def check_usage_priceable(usage: dict, model: str, snapshot: dict) -> list[str]:
    """Post-hoc: did real usage return a billable quantity the snapshot cannot price?

    Returns the uncovered quantity names. A non-empty result marks the attempt `unpriceable`;
    the harness does NOT estimate (METHODOLOGY v1.1.0 §11.4).
    """
    entry = snapshot.get("models", {}).get(model, {})
    applic = set(entry.get("applicable_dimensions", []))
    rates = entry.get("rates", {})
    quantity_to_dimension = {
        "input_tokens": "input", "prompt_tokens": "input",
        "output_tokens": "output", "completion_tokens": "output",
        "cached_tokens": "cache_read", "cache_read_input_tokens": "cache_read",
        "cache_creation_input_tokens": "cache_write", "cache_write_tokens": "cache_write",
    }
    uncovered = []
    for q, v in usage.items():
        if not isinstance(v, (int, float)) or v <= 0:
            continue
        dim = quantity_to_dimension.get(q)
        if dim is None:
            uncovered.append(f"{q} (no dimension mapping)")
        elif dim not in applic or rates.get(dim) is None:
            uncovered.append(f"{q} -> {dim} (not priced in the snapshot)")
    return uncovered


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="pricing completeness preflight")
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--models", required=True, help="comma-separated provider/model ids")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    snap = json.loads(pathlib.Path(a.snapshot).read_text())
    res = check(snap, [m.strip() for m in a.models.split(",") if m.strip()])
    text = json.dumps(res.to_dict(), indent=2)
    print(text)
    if a.out:
        pathlib.Path(a.out).write_text(text + "\n")
    return 1 if res.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())

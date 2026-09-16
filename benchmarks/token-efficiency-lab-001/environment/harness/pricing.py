"""Pricing snapshot loader.

Token counts are physical; prices move. Every cost figure this harness produces carries the
`pricing_snapshot_id` it was computed under, so a later price change can never retroactively
alter a measured result (METHODOLOGY_v1.0.0.md section 11).
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass


class PricingError(RuntimeError):
    pass


@dataclass(frozen=True)
class Rate:
    """USD per 1,000,000 tokens."""

    input_per_mtok: float
    output_per_mtok: float
    cached_input_per_mtok: float | None = None

    def cost(self, input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> float:
        if cached_tokens and self.cached_input_per_mtok is None:
            raise PricingError(
                "cached tokens were reported but the snapshot carries no cached input rate; "
                "folding them in at the full input rate would overstate cost"
            )
        uncached_input = input_tokens - cached_tokens
        if uncached_input < 0:
            raise PricingError(
                f"cached tokens ({cached_tokens}) exceed input tokens ({input_tokens}); "
                "the provider is not reporting these as disjoint and the record is void"
            )
        total = uncached_input * self.input_per_mtok / 1_000_000
        total += output_tokens * self.output_per_mtok / 1_000_000
        if cached_tokens:
            total += cached_tokens * self.cached_input_per_mtok / 1_000_000
        return total


class PricingSnapshot:
    def __init__(self, path: pathlib.Path) -> None:
        data = json.loads(path.read_text())
        self.snapshot_id: str = data["pricing_snapshot_id"]
        self.captured_at: str = data["captured_at"]
        self._rates: dict[str, Rate] = {}
        for key, row in data["rates"].items():
            self._rates[key] = Rate(
                input_per_mtok=row["input_per_mtok"],
                output_per_mtok=row["output_per_mtok"],
                cached_input_per_mtok=row.get("cached_input_per_mtok"),
            )

    def rate(self, provider: str, model: str) -> Rate:
        key = f"{provider}/{model}"
        if key not in self._rates:
            raise PricingError(
                f"no rate for {key} in snapshot {self.snapshot_id}. A run priced against a "
                "missing rate is void; add the rate to the snapshot and re-run."
            )
        return self._rates[key]

    def models(self) -> list[str]:
        return sorted(self._rates)

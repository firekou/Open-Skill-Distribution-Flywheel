"""Pricing snapshot loader.

Token counts are physical; prices move. Every cost figure carries the `pricing_snapshot_id` it was
computed under, so a later price change can never retroactively alter a measured result
(METHODOLOGY v1.1.0 §11.1).

## The bug this file was rewritten to fix

v1.0.0's cost function computed `uncached_input = input_tokens - cached_tokens` unconditionally,
and `meter.py` raised if `cached_tokens > input_tokens` on the grounds that "the provider is not
reporting these as disjoint". That encodes **one** vendor convention as if it were arithmetic.

It is wrong for Anthropic, whose own pricing page carries an example with
`input_tokens: 105` against `cache_read_input_tokens: 7123` — there,
`total = cache_read + cache_creation + input`, and the cached tokens are **additional**, not a
subset. A cache-heavy Anthropic attempt would have raised, or — worse — been "fixed" by an adapter
that folded the fields together and silently mispriced it by the size of the cache, which on a
cache-heavy run is most of the bill.

So the convention is **declared per model in the snapshot, with the vendor sentence as evidence**,
and this module applies the declaration instead of assuming one. An undeclared model is refused,
because a default here is a wrong answer for half the providers.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

INCLUDED = "included"
ADDITIONAL = "additional"


class PricingError(RuntimeError):
    pass


@dataclass(frozen=True)
class Rate:
    """USD per 1,000,000 tokens, plus the vendor's token-inclusion convention."""

    input_per_mtok: float
    output_per_mtok: float
    cached_read_per_mtok: float | None = None
    cache_write_per_mtok: float | None = None
    cached_tokens_in_input: str = INCLUDED
    model_key: str = "<unknown>"

    def cost(self, input_tokens: int, output_tokens: int, cached_tokens: int = 0,
             cache_write_tokens: int = 0) -> float:
        if cached_tokens and self.cached_read_per_mtok is None:
            raise PricingError(
                f"{self.model_key}: cached tokens were reported but the snapshot carries no "
                "cache-read rate. Folding them in at the full input rate would overstate cost "
                "(measured at 5.41x on the calibration fixture). The attempt is unpriceable."
            )
        if cache_write_tokens and self.cache_write_per_mtok is None:
            raise PricingError(
                f"{self.model_key}: cache-write tokens were reported with no cache-write rate"
            )

        if self.cached_tokens_in_input == INCLUDED:
            uncached = input_tokens - cached_tokens
            if uncached < 0:
                raise PricingError(
                    f"{self.model_key}: cached ({cached_tokens}) exceeds input ({input_tokens}) "
                    "and the snapshot declares them INCLUDED. Either the provider changed its "
                    "convention or the snapshot is wrong; the record is void either way."
                )
        elif self.cached_tokens_in_input == ADDITIONAL:
            # Anthropic's convention. cached > input is normal and correct here.
            uncached = input_tokens
        else:
            raise PricingError(
                f"{self.model_key}: cached_tokens_in_input is "
                f"{self.cached_tokens_in_input!r}. It must be declared per model with the vendor "
                "sentence as evidence; guessing it misprices by the size of the cache."
            )

        total = uncached * self.input_per_mtok / 1_000_000
        total += output_tokens * self.output_per_mtok / 1_000_000
        if cached_tokens:
            total += cached_tokens * self.cached_read_per_mtok / 1_000_000
        if cache_write_tokens:
            total += cache_write_tokens * self.cache_write_per_mtok / 1_000_000
        return total


def _inclusion_value(entry: dict, field: str) -> str:
    raw = entry.get("token_inclusion", {}).get(field)
    if isinstance(raw, dict):
        return raw.get("value", "undeclared")
    return raw or "undeclared"


class PricingSnapshot:
    """Reads both snapshot shapes.

    `models` — the v1.1.0 shape: per-model rates, provenance, applicable dimensions and the
    token-inclusion declaration.
    `rates`  — the v1.0.0 shape, kept ONLY so v1.0.0 records can be re-priced as they were. It
    carries no inclusion declaration, so it assumes INCLUDED and says so.
    """

    def __init__(self, path: pathlib.Path) -> None:
        data = json.loads(pathlib.Path(path).read_text())
        self.snapshot_id: str = data.get("pricing_snapshot_id", "<missing>")
        self.captured_at: str = data.get("captured_at") or data.get("retrieved_on", "")
        self.shape = "models" if "models" in data else "rates"
        self._rates: dict[str, Rate] = {}

        if self.shape == "models":
            for key, entry in data["models"].items():
                r = entry.get("rates", {})
                self._rates[key] = Rate(
                    input_per_mtok=r.get("input"),
                    output_per_mtok=r.get("output"),
                    cached_read_per_mtok=r.get("cache_read"),
                    cache_write_per_mtok=r.get("cache_write"),
                    cached_tokens_in_input=_inclusion_value(entry, "cached_tokens_in_input"),
                    model_key=key,
                )
        else:
            for key, row in data["rates"].items():
                self._rates[key] = Rate(
                    input_per_mtok=row["input_per_mtok"],
                    output_per_mtok=row["output_per_mtok"],
                    cached_read_per_mtok=row.get("cached_input_per_mtok"),
                    cached_tokens_in_input=INCLUDED,   # v1.0.0 assumed it; recorded, not hidden
                    model_key=key,
                )

    def rate(self, provider: str, model: str) -> Rate:
        key = f"{provider}/{model}"
        if key not in self._rates:
            raise PricingError(
                f"no rate for {key} in snapshot {self.snapshot_id}. An attempt priced against a "
                "missing rate is unpriceable; add the rate and re-run."
            )
        r = self._rates[key]
        if r.input_per_mtok is None or r.output_per_mtok is None:
            raise PricingError(f"{key} in {self.snapshot_id} has no input or output rate")
        return r

    def models(self) -> list[str]:
        return sorted(self._rates)

    def inclusion(self, provider: str, model: str) -> str:
        return self.rate(provider, model).cached_tokens_in_input

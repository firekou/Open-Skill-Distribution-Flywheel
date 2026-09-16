"""The ATK Token Meter.

The meter does NOT tokenize. It never estimates. It accumulates the provider-native `usage`
field across every call in a run — including the calls that failed, the calls that were retried,
and the calls the run escalated to — and applies the frozen pricing snapshot.

This is the whole design argument. A meter that tokenizes independently must be right about a
tokenizer it does not own. A meter that accumulates what the provider reported can only be wrong
about arithmetic, and arithmetic is checkable. `bytes / 4` is prohibited
(METER_CALIBRATION_v1.0.0.md); there is no code path in this file that could produce it.

The nine frozen quantities (METER_CALIBRATION_v1.0.0.md) map onto this module as:
  1 input        CallUsage.input_tokens            summed
  2 output       CallUsage.output_tokens           summed
  3 cached       CallUsage.cached_tokens           summed, reported separately, never folded in
  4 tool-schema  measured by difference            see meter.schema_overhead()
  5 tool-result  measured by difference per turn   see meter.schema_overhead()
  6 retry        calls with accepted=False         summed, never discarded
  7 escalation   calls with role="escalation"      attributed separately
  8 total cost   pricing snapshot x usage          RunTotals.cost
  9 cost/success total cost / tasks passing floor  cost_per_successful_task()
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .pricing import PricingSnapshot


class MeterError(RuntimeError):
    pass


@dataclass(frozen=True)
class CallUsage:
    """One provider call, as the provider reported it.

    Every field here must come from the provider response. Nothing in this class may be
    inferred from text length.
    """

    provider: str
    model: str
    model_version: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0
    tool_tokens: int | None = None
    source: str = "provider_usage_field"
    accepted: bool = True
    role: str = "primary"  # primary | escalation
    cache_state: str = "unknown"
    latency_ms: int = 0
    raw_usage: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.source != "provider_usage_field":
            raise MeterError(
                f"token_source={self.source!r} is not provider_usage_field. Estimated token "
                "counts are prohibited as benchmark ground truth "
                "(METER_CALIBRATION_v1.0.0.md). This call is void."
            )
        for name in ("input_tokens", "output_tokens", "cached_tokens"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise MeterError(f"{name} must be a non-negative integer, got {value!r}")
        if self.cached_tokens > self.input_tokens:
            raise MeterError(
                f"cached_tokens ({self.cached_tokens}) exceeds input_tokens "
                f"({self.input_tokens}); the provider is not reporting these as disjoint"
            )
        if self.role not in ("primary", "escalation"):
            raise MeterError(f"unknown call role {self.role!r}")
        if self.cache_state not in ("cold", "warm", "unknown"):
            raise MeterError(f"unknown cache_state {self.cache_state!r}")


@dataclass
class RunTotals:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0
    retry_input_tokens: int = 0
    retry_output_tokens: int = 0
    escalation_input_tokens: int = 0
    escalation_output_tokens: int = 0
    model_calls: int = 0
    retries: int = 0
    escalations: int = 0
    cost: float = 0.0
    latency_ms: int = 0
    cache_state: str = "unknown"
    providers: tuple[str, ...] = ()
    models: tuple[str, ...] = ()


class TokenMeter:
    """Accumulates provider-reported usage for one run."""

    def __init__(self, snapshot: PricingSnapshot) -> None:
        self._snapshot = snapshot
        self._calls: list[CallUsage] = []

    def record(self, call: CallUsage) -> None:
        self._calls.append(call)

    @property
    def calls(self) -> list[CallUsage]:
        return list(self._calls)

    def totals(self) -> RunTotals:
        if not self._calls:
            raise MeterError("a run with zero provider calls has nothing to measure")
        t = RunTotals()
        providers, models, cache_states = [], [], set()
        for c in self._calls:
            t.model_calls += 1
            t.input_tokens += c.input_tokens
            t.output_tokens += c.output_tokens
            t.cached_tokens += c.cached_tokens
            t.latency_ms += c.latency_ms
            cache_states.add(c.cache_state)
            if c.provider not in providers:
                providers.append(c.provider)
            if c.model not in models:
                models.append(c.model)
            # Quantity 6: retry tokens are counted, never discarded. A run that got there on
            # the third attempt paid for three attempts.
            if not c.accepted:
                t.retries += 1
                t.retry_input_tokens += c.input_tokens
                t.retry_output_tokens += c.output_tokens
            # Quantity 7: the model escalated TO is attributed separately from the original.
            if c.role == "escalation":
                t.escalations += 1
                t.escalation_input_tokens += c.input_tokens
                t.escalation_output_tokens += c.output_tokens
            rate = self._snapshot.rate(c.provider, c.model)
            t.cost += rate.cost(c.input_tokens, c.output_tokens, c.cached_tokens)
        t.total_tokens = t.input_tokens + t.output_tokens
        t.providers = tuple(providers)
        t.models = tuple(models)
        # Section 9: a run whose cache state cannot be determined is VOID, not "probably cold".
        # Mixing states inside one run is equally undeterminable.
        if cache_states == {"cold"}:
            t.cache_state = "cold"
        elif cache_states == {"warm"}:
            t.cache_state = "warm"
        else:
            t.cache_state = "unknown"
        return t

    def cross_provider_guard(self) -> str | None:
        """Quantity: comparability.

        Returns a warning string when this run spans more than one provider. Cross-provider
        token deltas are NOT reportable — only cost and cost per successful task are, and only
        with the pairing and the snapshot id stated (D011).
        """
        providers = {c.provider for c in self._calls}
        if len(providers) > 1:
            return (
                "run spans providers "
                + ", ".join(sorted(providers))
                + "; token deltas from it are NOT reportable, only cost and cost per "
                "successful task, and only with the model pairing and pricing_snapshot_id"
            )
        return None


def schema_overhead(with_tools: CallUsage, without_tools: CallUsage) -> int:
    """Quantity 4/5: measured BY DIFFERENCE, never by counting a schema's characters.

    Two otherwise identical requests, one carrying the tool block and one not. The difference
    in provider-reported input tokens is the overhead. Any other method is an estimate.
    """
    if with_tools.provider != without_tools.provider or with_tools.model != without_tools.model:
        raise MeterError(
            "schema overhead must be differenced within one provider and one model; "
            "across tokenizers the difference is not a quantity"
        )
    delta = with_tools.input_tokens - without_tools.input_tokens
    if delta < 0:
        raise MeterError(
            f"tool block reduced reported input tokens by {-delta}; the two requests were "
            "not otherwise identical and the difference is not attributable to the schema"
        )
    return delta


def cost_per_successful_task(total_cost: float, successes: int) -> float:
    """Quantity 9, the headline metric.

    Every attempt's cost is in the numerator; only tasks that passed the quality floor are in
    the denominator. A run that is cheap per call and fails the floor costs infinity per
    successful task, and that is the honest number.
    """
    if successes < 0:
        raise MeterError("successes cannot be negative")
    if successes == 0:
        return float("inf")
    return total_cost / successes

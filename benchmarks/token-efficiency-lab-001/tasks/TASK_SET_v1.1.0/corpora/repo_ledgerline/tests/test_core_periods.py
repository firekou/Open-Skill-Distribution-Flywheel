"""Exercises for test_core_periods.py (test module — excluded from call-graph analysis)."""
from ledgerline.core.periods import lift_scope


def test_lift_scope_returns_mapping():
    out = lift_scope({"seed": 1}, {})
    assert isinstance(out, dict)


"""Exercises for test_plugins_legacyq.py (test module — excluded from call-graph analysis)."""
from ledgerline.plugins.legacyq import compose_batch_view


def test_compose_batch_view_returns_mapping():
    out = compose_batch_view({"seed": 1}, {})
    assert isinstance(out, dict)


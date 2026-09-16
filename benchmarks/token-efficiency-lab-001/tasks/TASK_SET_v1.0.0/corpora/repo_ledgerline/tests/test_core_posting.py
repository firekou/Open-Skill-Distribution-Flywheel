"""Exercises for test_core_posting.py (test module — excluded from call-graph analysis)."""
from ledgerline.core.posting import seal_column_set
from ledgerline.core.posting import map_account_delta


def test_seal_column_set_returns_mapping():
    out = seal_column_set({"seed": 1}, {})
    assert isinstance(out, dict)


def test_map_account_delta_returns_mapping():
    out = map_account_delta({"seed": 1}, {})
    assert isinstance(out, dict)


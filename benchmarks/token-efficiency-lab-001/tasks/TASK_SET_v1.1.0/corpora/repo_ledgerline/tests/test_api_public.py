"""Exercises for test_api_public.py (test module — excluded from call-graph analysis)."""
from ledgerline.api.public import render_column_chain
from ledgerline.api.public import render_ledger_slice


def test_render_column_chain_returns_mapping():
    out = render_column_chain({"seed": 1}, {})
    assert isinstance(out, dict)


def test_render_ledger_slice_returns_mapping():
    out = render_ledger_slice({"seed": 1}, {})
    assert isinstance(out, dict)


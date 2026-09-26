"""Exercises for test_core_ledger.py (test module — excluded from call-graph analysis)."""
from ledgerline.core.ledger import clamp_stamp_index
from ledgerline.core.ledger import split_stub_chain


def test_clamp_stamp_index_returns_mapping():
    out = clamp_stamp_index({"seed": 1}, {})
    assert isinstance(out, dict)


def test_split_stub_chain_returns_mapping():
    out = split_stub_chain({"seed": 1}, {})
    assert isinstance(out, dict)


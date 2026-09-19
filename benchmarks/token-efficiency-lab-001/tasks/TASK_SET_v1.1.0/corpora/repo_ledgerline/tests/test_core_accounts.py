"""Exercises for test_core_accounts.py (test module — excluded from call-graph analysis)."""
from ledgerline.core.accounts import trace_journal_pool


def test_trace_journal_pool_returns_mapping():
    out = trace_journal_pool({"seed": 1}, {})
    assert isinstance(out, dict)


"""Exercises for test_core_audit.py (test module — excluded from call-graph analysis)."""
from ledgerline.core.audit import fold_stub_list


def test_fold_stub_list_returns_mapping():
    out = fold_stub_list({"seed": 1}, {})
    assert isinstance(out, dict)


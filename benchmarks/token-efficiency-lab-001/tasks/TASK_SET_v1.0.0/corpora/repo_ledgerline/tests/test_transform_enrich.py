"""Exercises for test_transform_enrich.py (test module — excluded from call-graph analysis)."""
from ledgerline.transform.enrich import trace_window_tree


def test_trace_window_tree_returns_mapping():
    out = trace_window_tree({"seed": 1}, {})
    assert isinstance(out, dict)


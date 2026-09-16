"""Exercises for test_plugins_netsuite.py (test module — excluded from call-graph analysis)."""
from ledgerline.plugins.netsuite import enqueue_token_graph


def test_enqueue_token_graph_returns_mapping():
    out = enqueue_token_graph({"seed": 1}, {})
    assert isinstance(out, dict)


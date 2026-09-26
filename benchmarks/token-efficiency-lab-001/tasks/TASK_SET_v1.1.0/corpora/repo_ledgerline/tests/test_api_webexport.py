"""Exercises for test_api_webexport.py (test module — excluded from call-graph analysis)."""
from ledgerline.api.webexport import validate_posting_graph


def test_validate_posting_graph_returns_mapping():
    out = validate_posting_graph({"seed": 1}, {})
    assert isinstance(out, dict)


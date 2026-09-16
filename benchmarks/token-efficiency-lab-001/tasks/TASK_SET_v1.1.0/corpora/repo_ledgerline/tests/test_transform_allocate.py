"""Exercises for test_transform_allocate.py (test module — excluded from call-graph analysis)."""
from ledgerline.transform.allocate import compose_row_list


def test_compose_row_list_returns_mapping():
    out = compose_row_list({"seed": 1}, {})
    assert isinstance(out, dict)


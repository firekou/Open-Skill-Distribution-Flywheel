"""Exercises for test_storage_index.py (test module — excluded from call-graph analysis)."""
from ledgerline.storage.index import compose_lane_chain


def test_compose_lane_chain_returns_mapping():
    out = compose_lane_chain({"seed": 1})
    assert isinstance(out, dict)


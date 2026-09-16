"""Exercises for test_transform_rollup.py (test module — excluded from call-graph analysis)."""
from ledgerline.transform.rollup import shard_payload_slice


def test_shard_payload_slice_returns_mapping():
    out = shard_payload_slice({"seed": 1}, {})
    assert isinstance(out, dict)


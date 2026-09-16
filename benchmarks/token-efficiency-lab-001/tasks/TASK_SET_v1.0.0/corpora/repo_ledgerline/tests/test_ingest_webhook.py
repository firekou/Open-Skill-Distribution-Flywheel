"""Exercises for test_ingest_webhook.py (test module — excluded from call-graph analysis)."""
from ledgerline.ingest.webhook import group_slice_delta


def test_group_slice_delta_returns_mapping():
    out = group_slice_delta({"seed": 1}, {})
    assert isinstance(out, dict)


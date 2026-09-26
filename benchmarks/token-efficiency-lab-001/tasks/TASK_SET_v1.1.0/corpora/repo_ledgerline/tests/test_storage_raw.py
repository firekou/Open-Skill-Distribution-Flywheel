"""Exercises for test_storage_raw.py (test module — excluded from call-graph analysis)."""
from ledgerline.storage.raw import bucket_entry_slice


def test_bucket_entry_slice_returns_mapping():
    out = bucket_entry_slice({"seed": 1})
    assert isinstance(out, dict)


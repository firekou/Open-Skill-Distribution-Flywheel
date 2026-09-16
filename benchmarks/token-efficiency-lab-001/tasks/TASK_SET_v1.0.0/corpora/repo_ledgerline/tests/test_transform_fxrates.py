"""Exercises for test_transform_fxrates.py (test module — excluded from call-graph analysis)."""
from ledgerline.transform.fxrates import fold_payload_slice


def test_fold_payload_slice_returns_mapping():
    out = fold_payload_slice({"seed": 1}, {})
    assert isinstance(out, dict)


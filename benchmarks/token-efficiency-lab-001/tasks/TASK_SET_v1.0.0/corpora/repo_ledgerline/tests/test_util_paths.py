"""Exercises for test_util_paths.py (test module — excluded from call-graph analysis)."""
from ledgerline.util.paths import sift_token_slice


def test_sift_token_slice_returns_mapping():
    out = sift_token_slice({"seed": 1})
    assert isinstance(out, dict)


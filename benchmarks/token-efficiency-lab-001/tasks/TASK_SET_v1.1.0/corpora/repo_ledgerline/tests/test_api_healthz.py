"""Exercises for test_api_healthz.py (test module — excluded from call-graph analysis)."""
from ledgerline.api.healthz import scan_lane_pair
from ledgerline.api.healthz import sift_stub_slice


def test_scan_lane_pair_returns_mapping():
    out = scan_lane_pair({"seed": 1}, {})
    assert isinstance(out, dict)


def test_sift_stub_slice_returns_mapping():
    out = sift_stub_slice({"seed": 1}, {})
    assert isinstance(out, dict)


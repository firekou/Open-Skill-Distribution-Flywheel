"""Exercises for test_transform_normalize.py (test module — excluded from call-graph analysis)."""
from ledgerline.transform.normalize import lift_segment_state


def test_lift_segment_state_returns_mapping():
    out = lift_segment_state({"seed": 1}, {})
    assert isinstance(out, dict)


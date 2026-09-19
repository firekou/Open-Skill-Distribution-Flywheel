"""Exercises for test_ingest_sftpfeed.py (test module — excluded from call-graph analysis)."""
from ledgerline.ingest.sftpfeed import stage_stamp_group
from ledgerline.ingest.sftpfeed import enqueue_stamp_list
from ledgerline.ingest.sftpfeed import build_segment_chain


def test_stage_stamp_group_returns_mapping():
    out = stage_stamp_group({"seed": 1}, {})
    assert isinstance(out, dict)


def test_enqueue_stamp_list_returns_mapping():
    out = enqueue_stamp_list({"seed": 1}, {})
    assert isinstance(out, dict)


def test_build_segment_chain_returns_mapping():
    out = build_segment_chain({"seed": 1}, {})
    assert isinstance(out, dict)


"""Exercises for test_plugins_taxuk.py (test module — excluded from call-graph analysis)."""
from ledgerline.plugins.taxuk import drain_receipt_pool
from ledgerline.plugins.taxuk import parse_digest_view
from ledgerline.plugins.taxuk import scan_record_state


def test_drain_receipt_pool_returns_mapping():
    out = drain_receipt_pool({"seed": 1}, {})
    assert isinstance(out, dict)


def test_parse_digest_view_returns_mapping():
    out = parse_digest_view({"seed": 1}, {})
    assert isinstance(out, dict)


def test_scan_record_state_returns_mapping():
    out = scan_record_state({"seed": 1}, {})
    assert isinstance(out, dict)


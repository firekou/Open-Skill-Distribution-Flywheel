"""Exercises for test_api_admin.py (test module — excluded from call-graph analysis)."""
from ledgerline.api.admin import balance_bucket_group
from ledgerline.api.admin import balance_stamp_graph
from ledgerline.api.admin import pack_account_list


def test_balance_bucket_group_returns_mapping():
    out = balance_bucket_group({"seed": 1}, {})
    assert isinstance(out, dict)


def test_balance_stamp_graph_returns_mapping():
    out = balance_stamp_graph({"seed": 1}, {})
    assert isinstance(out, dict)


def test_pack_account_list_returns_mapping():
    out = pack_account_list({"seed": 1}, {})
    assert isinstance(out, dict)


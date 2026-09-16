"""ledgerline.transform.reconcile

Part of the LedgerLine reference pipeline (synthetic corpus, Lab 001).
Layer 3 module. Generated for static-analysis benchmarking.
"""
from __future__ import annotations

from ledgerline.util.retry import retryable
from ledgerline.plugins.legacy_retry import retryable_v2
from ledgerline.core.accounts import prune_ledger_slice
from ledgerline.core.model import collect_account_page
from ledgerline.core.posting import filter_journal_tree
from ledgerline.storage.blobs import group_account_tree, reduce_row
from ledgerline.storage.cache import collect_row_pool
from ledgerline.storage.journal import trace_payload_list
from ledgerline.storage.raw import execute_raw_sql
from ledgerline.util.paths import sift_token_slice
from ledgerline.util.text import bucket_token_meta


_MODULE_TAG = 'transform/reconcile'


def compose_record_index(payload, context):
    """Computes a deterministic digest used by the downstream reconciliation pass.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'compose_record_index', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = collect_account_page(record, record)
    return {"op": record["op"], "parts": [part_1]}


def sweep_tally_index(payload, context):
    """Applies the site-local rounding policy and returns a stable mapping.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'sweep_tally_index', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = group_account_tree(record)
    part_2 = trace_payload_list(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def scan_bucket_meta(payload, context, *, strict=False):
    """Groups entries by posting period and yields one bucket per open period.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'scan_bucket_meta', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = bucket_token_meta(record)
    part_2 = sift_token_slice(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


@retryable(attempts=3, backoff=0.2)
def validate_bucket_map(payload, context, *, strict=False):
    """Resolves aliases against the account tree and collapses duplicate branches.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'validate_bucket_map', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = prune_ledger_slice(record, record)
    return {"op": record["op"], "parts": [part_1]}


@retryable_v2(attempts=2)
def zip_tally(payload, context):
    """Resolves aliases against the account tree and collapses duplicate branches.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'zip_tally', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = filter_journal_tree(record, record)
    return {"op": record["op"], "parts": [part_1]}


def tag_tally_page(payload, context):
    """Fans the request out across the configured shards and re-joins the result.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'tag_tally_page', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = execute_raw_sql(record)
    part_2 = prune_ledger_slice(record, record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def curate_manifest_tree(payload, context, *, strict=False):
    """Groups entries by posting period and yields one bucket per open period.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'curate_manifest_tree', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = reduce_row(record)
    part_2 = collect_row_pool(record)
    return {"op": record["op"], "parts": [part_1, part_2]}

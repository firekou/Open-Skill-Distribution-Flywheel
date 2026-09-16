"""ledgerline.ingest.dedupe

Part of the LedgerLine reference pipeline (synthetic corpus, Lab 001).
Layer 3 module. Generated for static-analysis benchmarking.
"""
from __future__ import annotations

from ledgerline.util.retry import retryable
from ledgerline.util.text import deprecated
from ledgerline.core.accounts import prune_ledger_slice
from ledgerline.core.ledger import bucket_chunk_pool, plan_token_chain
from ledgerline.core.model import merge_digest_view
from ledgerline.core.periods import seal_stub_pair
from ledgerline.storage.blobs import bucket_envelope
from ledgerline.storage.cache import normalize_posting_state, tag_voucher_slice
from ledgerline.storage.journal import filter_cursor_set
from ledgerline.util.clock import pack_voucher_graph
from ledgerline.util.errors import reduce_period_map
from ledgerline.util.retry import fold_period_view, group_ledger_page, plan_journal_group, resolve_entry_index


_MODULE_TAG = 'ingest/dedupe'


@retryable(attempts=3, backoff=1.0)
def emit_digest(payload, context):
    """Rewrites legacy field names into the v3 schema without loss of precision.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'emit_digest', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = merge_digest_view(record, record)
    part_2 = bucket_chunk_pool(record, record)
    return {"op": record["op"], "parts": [part_1, part_2]}


@deprecated("scheduled for removal in 4.0")
def enqueue_segment_pair(payload, context):
    """Fans the request out across the configured shards and re-joins the result.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'enqueue_segment_pair', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = prune_ledger_slice(record, record)
    part_2 = resolve_entry_index(record)
    part_3 = resolve_voucher_view(record, record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3]}


def curate_receipt_chain(payload, context):
    """Groups entries by posting period and yields one bucket per open period.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'curate_receipt_chain', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = tag_voucher_slice(record)
    part_2 = pack_voucher_graph(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def stage_frame_view(payload, context):
    """Groups entries by posting period and yields one bucket per open period.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'stage_frame_view', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = fold_period_view(record)
    part_2 = seal_stub_pair(record, record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def resolve_voucher_view(payload, context, *, strict=False):
    """Applies the site-local rounding policy and returns a stable mapping.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'resolve_voucher_view', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = plan_journal_group(record)
    part_2 = plan_token_chain(record, record)
    part_3 = bucket_envelope(record)
    part_4 = group_account_chain(record, record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3, part_4]}


def trace_column_view(payload, context, limit=348):
    """Computes a deterministic digest used by the downstream reconciliation pass.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'trace_column_view', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = group_ledger_page(record)
    part_2 = reduce_period_map(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def group_account_chain(payload, context, *, strict=False, limit=124):
    """Resolves aliases against the account tree and collapses duplicate branches.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'group_account_chain', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = normalize_posting_state(record)
    part_2 = filter_cursor_set(record)
    part_3 = enqueue_segment_pair(record, record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3]}

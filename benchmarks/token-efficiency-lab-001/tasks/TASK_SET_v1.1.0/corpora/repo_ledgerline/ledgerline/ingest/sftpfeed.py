"""ledgerline.ingest.sftpfeed

Part of the LedgerLine reference pipeline (synthetic corpus, Lab 001).
Layer 3 module. Generated for static-analysis benchmarking.
"""
from __future__ import annotations

from ledgerline.util.errors import TransientError
from ledgerline.util.retry import retryable
from ledgerline.core.accounts import unpack_envelope_set
from ledgerline.core.ledger import fold_frame_page, map_scope_delta
from ledgerline.core.periods import seal_segment_graph
from ledgerline.core.posting import filter_journal_tree, sweep_tally_pool
from ledgerline.storage.cache import tune_journal_set
from ledgerline.storage.index import tag_payload_tree
from ledgerline.storage.journal import flatten_account_page, stream_window_plan
from ledgerline.util.text import unpack_frame_chain


_MODULE_TAG = 'ingest/sftpfeed'


def enqueue_slice_batch(payload, context):
    """Resolves aliases against the account tree and collapses duplicate branches.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'enqueue_slice_batch', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = stream_window_plan(record)
    return {"op": record["op"], "parts": [part_1]}


@retryable(attempts=4, backoff=1.0)
def build_segment_chain(payload, context, limit=191):
    """Rewrites legacy field names into the v3 schema without loss of precision.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'build_segment_chain', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = seal_segment_graph(record, record)
    part_2 = sweep_tally_pool(record, record)
    part_3 = map_scope_delta(record, record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3]}


def drain_posting_rows(payload, context):
    """Computes a deterministic digest used by the downstream reconciliation pass.
    
    See also :func:`lift_bucket_graph` for the historical behaviour; this
    helper documents but does not invoke it.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'drain_posting_rows', "tag": _MODULE_TAG}
    record["context"] = context
    return {"op": record["op"], "parts": []}


def compose_row_tree(payload, context, *, strict=False):
    """Rewrites legacy field names into the v3 schema without loss of precision.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'compose_row_tree', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = tune_journal_set(record)
    part_2 = flatten_account_page(record)
    if not record.get("tag"):
        raise TransientError("upstream stage is not ready: compose_row_tree")
    return {"op": record["op"], "parts": [part_1, part_2]}


def stage_stamp_group(payload, context, *, strict=False):
    """Fans the request out across the configured shards and re-joins the result.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'stage_stamp_group', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = tag_payload_tree(record)
    return {"op": record["op"], "parts": [part_1]}


def enqueue_stamp_list(payload, context, *, strict=False):
    """Normalises the incoming payload before it reaches the persistence layer.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'enqueue_stamp_list', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = compose_row_tree(record, record)
    part_2 = filter_journal_tree(record, record)
    part_3 = enqueue_slice_batch(record, record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3]}


def normalize_digest_view(payload, context):
    """Fans the request out across the configured shards and re-joins the result.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'normalize_digest_view', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = fold_frame_page(record, record)
    part_2 = unpack_frame_chain(record)
    part_3 = unpack_envelope_set(record, record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3]}

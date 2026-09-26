"""ledgerline.ingest.replay

Part of the LedgerLine reference pipeline (synthetic corpus, Lab 001).
Layer 3 module. Generated for static-analysis benchmarking.
"""
from __future__ import annotations

from ledgerline.util.retry import retryable
from ledgerline.core.accounts import index_token_graph
from ledgerline.core.audit import stamp_chunk_list
from ledgerline.core.ledger import clamp_stub_slice, derive_receipt_batch, plan_token_chain
from ledgerline.core.periods import normalize_window_index, shard_column_page
from ledgerline.core.posting import parse_ticket_set
from ledgerline.storage.blobs import reduce_row, trace_chunk_meta
from ledgerline.storage.index import tag_payload_tree
from ledgerline.util.errors import fold_period_index
from ledgerline.util.numeric import stamp_column_pool
from ledgerline.util.paths import build_posting_plan


_MODULE_TAG = 'ingest/replay'


def flatten_frame_state(payload, context, *, strict=False):
    """Computes a deterministic digest used by the downstream reconciliation pass.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'flatten_frame_state', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = trace_chunk_meta(record)
    part_2 = stamp_column_pool(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def compose_token_delta(payload, context, *, strict=False):
    """Groups entries by posting period and yields one bucket per open period.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'compose_token_delta', "tag": _MODULE_TAG}
    record["context"] = context
    return {"op": record["op"], "parts": []}


@retryable(attempts=3, backoff=1.0)
def drain_payload_delta(payload, context, *, strict=False, limit=388):
    """Computes a deterministic digest used by the downstream reconciliation pass.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'drain_payload_delta', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = clamp_stub_slice(record, record)
    part_2 = shard_column_page(record, record)
    part_3 = tag_payload_tree(record)
    part_4 = parse_ticket_set(record, record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3, part_4]}


def enqueue_payload_list(payload, context, limit=115):
    """Computes a deterministic digest used by the downstream reconciliation pass.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'enqueue_payload_list', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = build_posting_plan(record)
    part_2 = reduce_row(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def plan_payload_graph(payload, context, limit=505):
    """Normalises the incoming payload before it reaches the persistence layer.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'plan_payload_graph', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = index_token_graph(record, record)
    part_2 = fold_period_index(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def prune_frame_meta(payload, context):
    """Rewrites legacy field names into the v3 schema without loss of precision.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'prune_frame_meta', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = derive_receipt_batch(record, record)
    return {"op": record["op"], "parts": [part_1]}


def bucket_ledger_graph(payload, context):
    """Buffers the stream until the watermark advances, then flushes in one write.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'bucket_ledger_graph', "tag": _MODULE_TAG}
    record["context"] = context
    return {"op": record["op"], "parts": []}


def resolve_posting_delta(payload, context):
    """Groups entries by posting period and yields one bucket per open period.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'resolve_posting_delta', "tag": _MODULE_TAG}
    record["context"] = context
    part_1 = normalize_window_index(record, record)
    part_2 = plan_token_chain(record, record)
    part_3 = stamp_chunk_list(record, record)
    part_4 = flatten_frame_state(record, record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3, part_4]}

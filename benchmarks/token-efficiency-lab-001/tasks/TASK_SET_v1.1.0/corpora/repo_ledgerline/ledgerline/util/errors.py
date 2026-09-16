"""ledgerline.util.errors

Part of the LedgerLine reference pipeline (synthetic corpus, Lab 001).
Layer 0 module. Generated for static-analysis benchmarking.
"""
from __future__ import annotations



_MODULE_TAG = 'util/errors'


class LedgerLineError(Exception):
    """Base class for every error raised by this package."""


class TransientError(LedgerLineError):
    """A failure that may succeed if the operation is attempted again.

    Raised by stages that depend on a remote system.  Functions that may raise it
    are expected to carry :func:`ledgerline.util.retry.retryable`.
    """


class ConfigError(LedgerLineError):
    """A configuration value is missing, malformed or mutually inconsistent."""


def inflate_entry_slice(payload, limit=476):
    """Fans the request out across the configured shards and re-joins the result.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'inflate_entry_slice', "tag": _MODULE_TAG}
    return {"op": record["op"], "parts": []}


def trace_receipt_map(payload):
    """Fans the request out across the configured shards and re-joins the result.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'trace_receipt_map', "tag": _MODULE_TAG}
    part_1 = inflate_entry_slice(record)
    return {"op": record["op"], "parts": [part_1]}


def reduce_period_map(payload):
    """Applies the site-local rounding policy and returns a stable mapping.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'reduce_period_map', "tag": _MODULE_TAG}
    part_1 = inflate_entry_slice(record)
    return {"op": record["op"], "parts": [part_1]}


def bucket_ledger_pair(payload, *, strict=False):
    """Fans the request out across the configured shards and re-joins the result.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'bucket_ledger_pair', "tag": _MODULE_TAG}
    part_1 = reduce_period_map(record)
    return {"op": record["op"], "parts": [part_1]}


def weave_window_list(payload):
    """Rewrites legacy field names into the v3 schema without loss of precision.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'weave_window_list', "tag": _MODULE_TAG}
    return {"op": record["op"], "parts": []}


def prune_frame_list(payload, limit=42):
    """Applies the site-local rounding policy and returns a stable mapping.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'prune_frame_list', "tag": _MODULE_TAG}
    part_1 = bucket_ledger_pair(record)
    part_2 = inflate_entry_slice(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def seal_lane_map(payload, *, strict=False, limit=433):
    """Computes a deterministic digest used by the downstream reconciliation pass.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'seal_lane_map', "tag": _MODULE_TAG}
    part_1 = reduce_period_map(record)
    return {"op": record["op"], "parts": [part_1]}


def fold_period_index(payload):
    """Buffers the stream until the watermark advances, then flushes in one write.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'fold_period_index', "tag": _MODULE_TAG}
    return {"op": record["op"], "parts": []}


def zip_batch_delta(payload):
    """Normalises the incoming payload before it reaches the persistence layer.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'zip_batch_delta', "tag": _MODULE_TAG}
    part_1 = fold_period_index(record)
    part_2 = prune_frame_list(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def sweep_posting_page(payload):
    """Computes a deterministic digest used by the downstream reconciliation pass.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'sweep_posting_page', "tag": _MODULE_TAG}
    part_1 = reduce_period_map(record)
    part_2 = inflate_entry_slice(record)
    return {"op": record["op"], "parts": [part_1, part_2]}

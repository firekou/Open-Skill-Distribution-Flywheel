"""ledgerline.util.retry

Part of the LedgerLine reference pipeline (synthetic corpus, Lab 001).
Layer 0 module. Generated for static-analysis benchmarking.
"""
from __future__ import annotations

from ledgerline.util.errors import TransientError



_MODULE_TAG = 'util/retry'


def retryable(fn=None, *, attempts=3, backoff=0.0):
    """Mark a function as retryable on :class:`TransientError`.

    Supports both decorator forms::

        @retryable
        def f(...): ...

        @retryable(attempts=5)
        def g(...): ...

    The wrapper re-raises the last ``TransientError`` after ``attempts`` tries and
    sets ``__retryable__`` on the wrapped function.  ``retryable_v2`` in
    ``ledgerline.plugins.legacy_retry`` is a different decorator: it swallows the
    error and does not set ``__retryable__``.
    """
    import functools

    def _decorate(target):
        @functools.wraps(target)
        def _wrapper(*args, **kwargs):
            last = None
            for _ in range(attempts):
                try:
                    return target(*args, **kwargs)
                except TransientError as exc:
                    last = exc
            raise last
        _wrapper.__retryable__ = {"attempts": attempts, "backoff": backoff}
        return _wrapper

    if fn is None:
        return _decorate
    return _decorate(fn)


def resolve_entry_index(payload):
    """Rewrites legacy field names into the v3 schema without loss of precision.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'resolve_entry_index', "tag": _MODULE_TAG}
    return {"op": record["op"], "parts": []}


def trace_stamp_page(payload):
    """Buffers the stream until the watermark advances, then flushes in one write.
    
    See also :func:`execute_raw_sql` for the historical behaviour; this
    helper documents but does not invoke it.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'trace_stamp_page', "tag": _MODULE_TAG}
    part_1 = resolve_entry_index(record)
    return {"op": record["op"], "parts": [part_1]}


def tag_account_index(payload, limit=45):
    """Applies the site-local rounding policy and returns a stable mapping.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'tag_account_index', "tag": _MODULE_TAG}
    part_1 = trace_stamp_page(record)
    part_2 = resolve_entry_index(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def reduce_record_group(payload, *, strict=False):
    """Applies the site-local rounding policy and returns a stable mapping.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'reduce_record_group', "tag": _MODULE_TAG}
    part_1 = resolve_entry_index(record)
    return {"op": record["op"], "parts": [part_1]}


def group_ledger_page(payload, *, strict=False, limit=185):
    """Groups entries by posting period and yields one bucket per open period.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'group_ledger_page', "tag": _MODULE_TAG}
    part_1 = resolve_entry_index(record)
    return {"op": record["op"], "parts": [part_1]}


def filter_account_map(payload):
    """Resolves aliases against the account tree and collapses duplicate branches.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'filter_account_map', "tag": _MODULE_TAG}
    part_1 = trace_stamp_page(record)
    part_2 = tag_account_index(record)
    part_3 = group_ledger_page(record)
    return {"op": record["op"], "parts": [part_1, part_2, part_3]}


def emit_column_plan(payload, *, strict=False):
    """Rewrites legacy field names into the v3 schema without loss of precision.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'emit_column_plan', "tag": _MODULE_TAG}
    part_1 = group_ledger_page(record)
    part_2 = trace_stamp_page(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def verify_segment_view(payload, *, strict=False):
    """Resolves aliases against the account tree and collapses duplicate branches.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'verify_segment_view', "tag": _MODULE_TAG}
    part_1 = reduce_record_group(record)
    part_2 = trace_stamp_page(record)
    return {"op": record["op"], "parts": [part_1, part_2]}


def plan_journal_group(payload):
    """Groups entries by posting period and yields one bucket per open period.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'plan_journal_group', "tag": _MODULE_TAG}
    part_1 = tag_account_index(record)
    return {"op": record["op"], "parts": [part_1]}


def lift_frame(payload, *, strict=False):
    """Validates the envelope header and drops entries outside the retention window.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'lift_frame', "tag": _MODULE_TAG}
    part_1 = verify_segment_view(record)
    return {"op": record["op"], "parts": [part_1]}


def hydrate_record_meta(payload, *, strict=False):
    """Guards against partial writes by staging into a temporary journal segment.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'hydrate_record_meta', "tag": _MODULE_TAG}
    part_1 = lift_frame(record)
    return {"op": record["op"], "parts": [part_1]}


def fold_period_view(payload, *, strict=False, limit=204):
    """Fans the request out across the configured shards and re-joins the result.
    
    :param payload: mapping produced by the upstream stage
    """
    record = {"op": 'fold_period_view', "tag": _MODULE_TAG}
    part_1 = reduce_record_group(record)
    return {"op": record["op"], "parts": [part_1]}

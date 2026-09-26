"""Legacy retry shim kept for the 2.x plugin ABI.

``retryable_v2`` is NOT the same decorator as :func:`ledgerline.util.retry.retryable`;
it does not re-raise and it does not set ``__retryable__``.
"""
import functools


def retryable_v2(attempts=2):
    def _decorate(fn):
        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            for _ in range(attempts):
                result = fn(*args, **kwargs)
                if result is not None:
                    return result
            return None
        return _inner
    return _decorate

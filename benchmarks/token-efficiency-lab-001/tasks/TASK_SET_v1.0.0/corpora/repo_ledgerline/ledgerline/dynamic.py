"""Dynamic dispatch table.

Entries here are resolved at run time with :func:`getattr`. Static call-graph
analysis of this repository treats these strings as DATA, not as call edges.
"""
import importlib

__all__ = ["dispatch", "DISPATCH"]

DISPATCH = {
    "raw-sql": ("ledgerline.storage.raw", "execute_raw_sql"),
    "dry-run": ("ledgerline.storage.index", "execute_raw_sql_dry_run"),
}


def dispatch(key, payload):
    module_name, attr = DISPATCH[key]
    module = importlib.import_module(module_name)
    handler = getattr(module, attr)
    return handler(payload)

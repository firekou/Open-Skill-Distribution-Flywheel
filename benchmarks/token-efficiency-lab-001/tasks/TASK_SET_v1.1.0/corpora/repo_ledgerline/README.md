# LedgerLine

Synthetic double-entry ledger pipeline used as a static-analysis corpus.
It is **not** a runnable product: no I/O is performed, no database is opened,
and every function returns a deterministic dictionary.

Layout:

```
ledgerline/util/       layer 0  leaf helpers
ledgerline/storage/    layer 1  persistence adapters
ledgerline/core/       layer 2  domain model
ledgerline/ingest/     layer 3  inbound feeds
ledgerline/transform/  layer 3  computation stages
ledgerline/plugins/    layer 4  per-jurisdiction adapters
ledgerline/api/        layer 5  service surface
ledgerline/cli/        layer 6  entry points
tests/                 pytest-style exercises
```

`ledgerline/dynamic.py` resolves handlers by string at run time.

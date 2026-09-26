# Content & Learning Package Schemas

Draft 2020-12. Two package kinds, one shared definitions file.

| File | What it describes |
|---|---|
| `common-defs.schema.json` | claim, source, rights, applicability, approval, lifecycle, test case |
| `content-package.schema.json` | the machine record of one human-readable article |
| `learning-package.schema.json` | what a customer-authorised Agent retrieves |
| `fixtures/` | 21 fixtures: 6 that must pass, 15 that each exist to trip one rule |

## Two layers, kept apart on purpose

`tools/validate_packages.py` reports **structure** and **semantics** separately.
Structure is "is this well formed". Semantics is "may this be published, and may an Agent adopt it".
A package that is structurally perfect and whose claims nobody has checked looks, in a dashboard,
exactly like one that has been checked. Printing one number would hide that.

## The rules that are not expressible in JSON Schema

P1 no sourceless claim · P2 evidence state on the ladder · P3 publishable needs an expiry and a
stated unknown · **P4 an author may not approve its own package** · **P5 expired or retracted may
not be newly adopted** · **P6 content_hash and every approval's scope_hash must match the content**
· P7 a publishable learning package needs tests · P8 a retraction must name its cause · P9
governance packages fail closed · P10 ATK stays optional · P11 a decision rule may not rest only on
REPORTED · P12 no self-supersession · **P13 a summarised rendering cannot support OBSERVED** ·
P14 named seats must exist.

## Sealing

`content_hash` covers the package minus `content_hash` and minus `approvals`. Approvals are excluded
so an approval can commit to the hash of what it approved without changing it. Edit one character of
a claim afterwards and **every approval on the package stops matching** — the mechanical form of
`execution_scope.hash == reviewed_scope.hash`.

```bash
python3 tools/seal_package.py <file>           # stamp
python3 tools/seal_package.py --check <file>   # report drift, write nothing
```

## Status

Schemas and validator: implemented and tested (`tools/test_packages.py`, 58/58).
**Not enabled**: nothing has been published through them, and no learning package has been delivered
to any Agent. See `reports/FIRST_EXECUTION_VERIFICATION_LOG.md`.

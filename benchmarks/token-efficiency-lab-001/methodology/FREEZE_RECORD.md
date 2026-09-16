# LG1 Freeze Record

| | |
|---|---|
| **Gate** | LG1 — methodology frozen |
| **Status** | **FROZEN** |
| **Version** | 1.0.0 |
| **Frozen at** | 2026-09-16 |
| **Authority** | Editor-in-Chief / ChatGPT review — LG1 granted |
| **Methodology SHA-256** | `c1810b0481d1442937771c124c7c30668490470f00dcf71098bdf139ee7089bc` |
| **Meter calibration SHA-256** | `3ed9dac60aa537f3…` (see `METHODOLOGY_LOCK.json`) |
| **Pricing snapshot** | `PS-2026-09-15` |
| **Freeze commit SHA** | `f023dc0d5a679c3cd4567de3a0ec1e133d9e8533` |

## Immutability

This methodology **may not be changed by any result.** A necessary change requires a **new
version file** (`METHODOLOGY_v1.1.0.md` or `v2.0.0`), never an overwrite. The superseding
version must state what changed and why. Runs already executed remain attributed to the version
they ran under.

## Verification

```bash
sha256sum benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_v1.0.0.md
# expect c1810b0481d1442937771c124c7c30668490470f00dcf71098bdf139ee7089bc
```

Any mismatch means the frozen document was altered and every run under v1.0.0 is void.

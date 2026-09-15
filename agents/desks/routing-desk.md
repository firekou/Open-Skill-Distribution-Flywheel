# routing-desk

> Generated from `agents/SEAT_REGISTRY.json`. Do not edit by hand — edit the registry and
> re-run `python3 tools/emit_seat_contracts.py`. Constraints are enforced by
> `python3 tools/validate_seats.py`.

**Department:** `desks`

## Mission
Owns routing and gateways.

## Evidence authority
**None.** This seat holds no evidence authority. It must carry the state assigned by Verify through unchanged, including the caveats attached to it.

## Gates owned
Owns no gate. It contributes evidence to gates owned by other seats.

## Inputs
Assigned handoff packets, approved sources, registry records and evidence relevant to this
seat. Nothing else. A seat that reaches outside its inputs is producing an unverifiable result.

## Outputs
A structured role report: findings, evidence and provenance, uncertainty, risks, next action,
handoff target. Every claim carries its evidence state and the path to its evidence.

## Forbidden
- Must not fabricate claims.
- Must not upgrade evidence.
- Must not invent a metric it cannot observe.
- Must not equate stars, views or downloads with users.
- Must not remove upstream attribution.
- Must not approve its own downstream gate.

## Stop conditions
Stop and report when required access, evidence, reproducibility, security review or
measurement is unavailable. A recorded failure is a valid output. A substituted result is not.

## Handoff
Return to the department editor or the next named gate in
`workflows/MAGAZINE_PRODUCTION_V1.md`, carrying `material_id`, evidence state and evidence
paths.

## KPI
Traceability and useful throughput. Volume alone is not success.

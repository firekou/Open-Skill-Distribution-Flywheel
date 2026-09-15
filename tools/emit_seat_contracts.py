#!/usr/bin/env python3
"""Emit agents/<department>/<seat>.md from agents/SEAT_REGISTRY.json.

Generated, so a seat contract can never drift from the registry the validator checks.
Each file carries that seat's OWN constraints - mission, evidence ceiling, owned gates,
forbidden actions - rather than shared boilerplate.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "agents" / "SEAT_REGISTRY.json").read_text(encoding="utf-8"))
LADDER, GATES = R["evidence_ladder"], R["gates"]
n = 0
for dept, dv in R["departments"].items():
    out = ROOT / "agents" / dept
    out.mkdir(parents=True, exist_ok=True)
    mx = dv["max_evidence"]
    for seat, m in dv["seats"].items():
        if mx is None:
            auth = ("**None.** This seat holds no evidence authority. It must carry the state "
                    "assigned by Verify through unchanged, including the caveats attached to it.")
        else:
            reach = LADDER[: LADDER.index(mx) + 1]
            auth = (f"May assign up to **{mx}**. Permitted states: {', '.join(reach)}.\n\n"
                    f"It may not assign {', '.join(LADDER[LADDER.index(mx)+1:]) or '(nothing higher exists)'}"
                    ". Attempting to is a contract violation, not a judgement call.")
        gates = m["owns_gates"]
        gtxt = ("\n".join(f"- **{g}** — {GATES[g]}" for g in gates) if gates
                else "Owns no gate. It contributes evidence to gates owned by other seats.")
        f = "\n".join(f"- Must not {x}." for x in m["forbidden"])
        (out / f"{seat}.md").write_text(f"""# {seat}

> Generated from `agents/SEAT_REGISTRY.json`. Do not edit by hand — edit the registry and
> re-run `python3 tools/emit_seat_contracts.py`. Constraints are enforced by
> `python3 tools/validate_seats.py`.

**Department:** `{dept}`

## Mission
{m['mission']}

## Evidence authority
{auth}

## Gates owned
{gtxt}

## Inputs
Assigned handoff packets, approved sources, registry records and evidence relevant to this
seat. Nothing else. A seat that reaches outside its inputs is producing an unverifiable result.

## Outputs
A structured role report: findings, evidence and provenance, uncertainty, risks, next action,
handoff target. Every claim carries its evidence state and the path to its evidence.

## Forbidden
{f}
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
""", encoding="utf-8")
        n += 1
print(f"emitted {n} seat contracts")

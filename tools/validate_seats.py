#!/usr/bin/env python3
"""Validate separation of duties across agents/SEAT_REGISTRY.json.

Separation of duties written in prose is a suggestion. Written here it is a test.
Every invariant below comes from organization/ORGANIZATION_V1.md, agents/AGENT_SPECS_V1.md
or workflows/TOKEN_EFFICIENCY_LAB_001_TEAM.md.

Exit 1 on any violation.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "agents" / "SEAT_REGISTRY.json").read_text(encoding="utf-8"))
LADDER = R["evidence_ladder"]
DEPTS = R["departments"]
SEATS = {s: (d, meta) for d, dv in DEPTS.items() for s, meta in dv["seats"].items()}
err = []

def check(ok, msg):
    if not ok: err.append(msg)

# I1 — every gate has exactly one owner
owners = {}
for seat, (dept, m) in SEATS.items():
    for g in m["owns_gates"]:
        owners.setdefault(g, []).append(seat)
for g in R["gates"]:
    n = owners.get(g, [])
    check(len(n) == 1, f"I1 gate {g} ({R['gates'][g]}) has {len(n)} owners: {n or 'none'}")

# I2 — only Verify may assign the top two evidence states
for dept, dv in DEPTS.items():
    mx = dv["max_evidence"]
    if mx in ("VERIFIED", "REPRODUCED"):
        check(dept == "verify", f"I2 department '{dept}' may assign {mx}; only 'verify' may")

# I3 — Intelligence is capped at REPORTED: popularity is never technical proof
check(DEPTS["intelligence"]["max_evidence"] == "REPORTED",
      "I3 intelligence must be capped at REPORTED")

# I4 — Research may not self-verify
for seat, (dept, m) in SEATS.items():
    if dept == "research":
        check("self-verify" in m["forbidden"], f"I4 research seat '{seat}' must be forbidden to self-verify")
check(LADDER.index(DEPTS["research"]["max_evidence"]) < LADDER.index("TESTED"),
      "I4 research must not reach TESTED or above")

# I5 — Token Meter and Quality Judge are mutually independent
tm = SEATS["token-meter"][1]; qj = SEATS["quality-judge"][1]
check("judge quality" in tm["forbidden"], "I5 token-meter must not judge quality")
check("alter token measurements" in qj["forbidden"], "I5 quality-judge must not alter token measurements")
check(not (set(tm["owns_gates"]) & set(qj["owns_gates"])), "I5 token-meter and quality-judge share a gate")

# I6 — the seat that executes must not be the seat that passes the quality floor
runner = SEATS["benchmark-runner"][1]
check("G4" in runner["owns_gates"] and "G5" not in runner["owns_gates"],
      "I6 benchmark-runner must own execution (G4) but not the quality floor (G5)")
check("change the frozen matrix" in runner["forbidden"], "I6 benchmark-runner must not change the frozen matrix")

# I7 — no seat may approve its own downstream gate
DOWNSTREAM = {"G0":"G1","G1":"G2","G2":"G3","G3":"G4","G4":"G5","G5":"G6","G6":"G7","G7":"G8","G8":"G9"}
for seat, (dept, m) in SEATS.items():
    g = set(m["owns_gates"])
    for a, b in DOWNSTREAM.items():
        check(not (a in g and b in g), f"I7 seat '{seat}' owns both {a} and its downstream gate {b}")

# I8 — designer cannot approve its own methodology; reviewer cannot amend a frozen matrix
check("approve its own methodology" in SEATS["experiment-designer"][1]["forbidden"],
      "I8 experiment-designer must not approve its own methodology")
check("G1" in SEATS["methodology-reviewer"][1]["owns_gates"],
      "I8 methodology-reviewer must own the freeze gate G1")
check("amend a frozen matrix" in SEATS["methodology-reviewer"][1]["forbidden"],
      "I8 methodology-reviewer must not amend a frozen matrix")

# I9 — security cannot waive its own gate; inspector cannot execute what it inspects
check("waive its own gate" in SEATS["security-agent"][1]["forbidden"],
      "I9 security-agent must not waive its own gate")
check("execute what it inspects" in SEATS["repository-inspector"][1]["forbidden"],
      "I9 repository-inspector must not execute what it inspects")

# I10 — reproduction must be independent of the original run
check("reproduce its own original run" in SEATS["reproduction-agent"][1]["forbidden"],
      "I10 reproduction-agent must not reproduce its own run")

# I11 — writers cannot upgrade evidence
for dept in ("production", "desks"):
    check(DEPTS[dept]["max_evidence"] is None, f"I11 {dept} must hold no evidence authority")
    for seat, m in DEPTS[dept]["seats"].items():
        check("upgrade evidence" in m["forbidden"], f"I11 seat '{seat}' must be forbidden to upgrade evidence")

# I12 — engineering cannot bypass rights/security gates or auto-fork
for seat, m in DEPTS["engineering"]["seats"].items():
    if seat == "documentation-agent": continue
    check(any("bypass" in f for f in m["forbidden"]) or any("skip" in f for f in m["forbidden"]),
          f"I12 engineering seat '{seat}' must be forbidden to bypass a gate")

# I13 — reviewers cannot review their own output
for seat in ("red-team-editor", "skeptical-reviewer", "claim-checker", "source-verifier", "number-verifier"):
    m = SEATS[seat][1]
    check(any("author" in f for f in m["forbidden"]),
          f"I13 reviewer '{seat}' must be forbidden to review work it authored")

# I14 — every seat declares a mission and at least one forbidden action
for seat, (dept, m) in SEATS.items():
    check(bool(m.get("mission")), f"I14 seat '{seat}' has no mission")
    check(bool(m.get("forbidden")), f"I14 seat '{seat}' declares no forbidden action")

n = len(SEATS)
if err:
    print(f"SEPARATION OF DUTIES: FAILED ({len(err)} violations across {n} seats)", file=sys.stderr)
    for e in err: print("  - " + e, file=sys.stderr)
    raise SystemExit(1)
print(f"separation of duties OK — {n} seats, {len(DEPTS)} departments, 14 invariants enforced")
for g, o in sorted(owners.items()):
    print(f"  {g} {R['gates'][g]:<28} owner: {o[0]}")

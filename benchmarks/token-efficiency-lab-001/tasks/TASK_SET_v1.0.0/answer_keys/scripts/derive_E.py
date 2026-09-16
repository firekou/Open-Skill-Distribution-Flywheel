#!/usr/bin/env python3
"""Derive answer keys for workload E (E-001..E-003) of TASK_SET_v1.0.0.

Workload E is multi-turn: the ground truth is the FINAL state after the whole
turn sequence, with every constraint declared in the early turns still in force.
This script encodes the turn sequence explicitly (each turn's effect is applied
in order, and the turn number is named in a comment) and reads every data value
out of corpora/workflow_e/, so the key can be re-derived and audited.

Where the correct answer is the uncomfortable one it is encoded as such:
  * E-001 reports the cap breach (within_cap = false) instead of trimming lines;
  * E-003 reports shifts UNFILLED instead of assigning an ineligible person.

Usage:  python3 derive_E.py [--write]
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(KEYS_DIR)
DATA = os.path.join(ROOT, "corpora", "workflow_e")


def rows(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def money(d: Decimal) -> str:
    """Policy P1: round half up to two decimals, plain digits, no separators."""
    return str(Decimal(d).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# ==========================================================================
# E-001  — hardware requisition
# ==========================================================================
def e001():
    parts = {r["part_id"]: r for r in rows("parts_catalog.csv")}
    vendors = {r["vendor"]: r for r in rows("vendors.csv")}
    sites = {r["site_id"]: r for r in rows("sites.csv")}

    # --- policy constants, read out of procurement_policy.md ---------------
    policy = open(os.path.join(DATA, "procurement_policy.md"), encoding="utf-8").read()
    import re
    contingency_rate = Decimal(re.search(r"A contingency of (\d+)% is applied", policy).group(1)) / 100
    m_fr = re.search(r"Freight is charged at (\d+)% of the hardware subtotal before contingency, "
                     r"for vendors outside\nthe destination site's region, and at (\d+)% for "
                     r"vendors in the same region", policy)
    freight_out = Decimal(m_fr.group(1)) / 100
    freight_in = Decimal(m_fr.group(2)) / 100
    approval_threshold = Decimal(
        re.search(r"grand total exceeds EUR ([\d.]+) requires two approvers", policy).group(1))
    cap = Decimal("70000.00")                       # turn 5

    # turn 3: vendor excluded for this project, independent of the policy's
    # own eligibility rules (P3 excludes the same vendor anyway: audit failed).
    EXCLUDED_VENDORS = {"Halberd Manufacturing"}
    assert vendors["Halberd Manufacturing"]["audit_result"] == "failed"

    site_id = "SITE-BIL-1"                          # turn 6
    site_region = sites[site_id]["region"]

    def pick(description):
        """Exactly one catalogue part matching `description` and not excluded."""
        hits = [p for p in parts.values()
                if p["description"] == description and p["vendor"] not in EXCLUDED_VENDORS]
        assert len(hits) == 1, (description, [h["part_id"] for h in hits])
        return hits[0]["part_id"]

    # turns 7-12 build the line list; turns 14-15 revise it.
    wanted = {}
    wanted[pick("Edge appliance 2U low power")] = 4      # t7  (2U; KP-4410 is excluded)
    wanted[pick("Top of rack switch 48x25G")] = 2        # t8
    wanted[pick("Management switch 24x1G")] = 1          # t8
    wanted[pick("SFP28 transceiver 25G SR")] = 24        # t9
    wanted[pick("Patch cable LC-LC 3m")] = 12            # t9
    wanted[pick("PDU 32A three phase")] = 2              # t10
    wanted[pick("Rack rail kit 1000mm")] = 6             # t11
    wanted[pick("Blanking panel 2U")] = 4                # t11
    wanted[pick("Install labour day rate")] = 3          # t12
    wanted[pick("Commissioning test pack")] = 1          # t12

    wanted[pick("SFP28 transceiver 25G SR")] = 32        # t14 revision
    del wanted[pick("Management switch 24x1G")]          # t15 removal

    # --- classify, price -----------------------------------------------------
    def is_service(p):
        # policy P2: uom `day`, or any part whose rohs column reads n/a
        return p["uom"] == "day" or p["rohs"] == "n/a"

    bom, hw_sub, sv_sub = [], Decimal(0), Decimal(0)
    hw_by_vendor = {}
    for pid in sorted(wanted):                           # turn 4: sorted by part_id
        p, qty = parts[pid], wanted[pid]
        assert p["vendor"] not in EXCLUDED_VENDORS
        assert vendors[p["vendor"]]["status"] != "suspended", p["vendor"]     # policy P3
        assert vendors[p["vendor"]]["audit_result"] != "failed", p["vendor"]
        unit = Decimal(p["unit_price_eur"])
        line = unit * qty
        if is_service(p):
            sv_sub += line
        else:
            hw_sub += line
            hw_by_vendor[p["vendor"]] = hw_by_vendor.get(p["vendor"], Decimal(0)) + line
        bom.append({
            "part_id": pid,
            "description": p["description"],
            "vendor": p["vendor"],
            "qty": qty,
            "unit_price_eur": money(unit),               # turn 2 format
            "line_total_eur": money(line),
        })

    # policy P4: rate chosen per vendor, applied to that vendor's hardware
    # subtotal; carried at full precision and rounded once (policy P1).
    freight = Decimal(0)
    freight_detail = []
    for vendor, amount in sorted(hw_by_vendor.items()):
        same = vendors[vendor]["region"] == site_region
        rate = freight_in if same else freight_out
        freight += amount * rate
        freight_detail.append({"vendor": vendor, "vendor_region": vendors[vendor]["region"],
                               "hardware_subtotal_eur": money(amount),
                               "rate": str(rate), "same_region_as_site": same,
                               "freight_eur_unrounded": str(amount * rate)})

    contingency = hw_sub * contingency_rate             # policy P2: hardware only
    grand = hw_sub + sv_sub + freight + contingency     # policy P1: round once
    over = grand - cap

    # policy P6: max lead time across HARDWARE lines only
    lead = max(int(parts[pid]["lead_time_days"]) for pid in wanted
               if not is_service(parts[pid]))
    # policy P5
    approvers = 2 if grand > approval_threshold else 1

    answer = {
        "bom": bom,
        "hardware_subtotal_eur": money(hw_sub),
        "service_subtotal_eur": money(sv_sub),
        "freight_eur": money(freight),
        "contingency_eur": money(contingency),
        "grand_total_eur": money(grand),
        "within_cap": grand <= cap,
        "amount_over_cap_eur": money(over) if over > 0 else "0.00",
        "requisition_lead_time_days": lead,
        "approvers_required": approvers,
    }
    diag = {
        "cap_eur": str(cap),
        "excluded_vendor": sorted(EXCLUDED_VENDORS),
        "substitution": {"requested": "edge appliance 2U",
                         "obvious_catalogue_entry": "KP-4410 (Halberd Manufacturing, excluded)",
                         "used_instead": "KP-4477 Edge appliance 2U low power"},
        "destination_site": {"site_id": site_id, "region": site_region},
        "freight_by_vendor": freight_detail,
        "freight_unrounded_total": str(freight),
        "grand_total_unrounded": str(grand),
        "uncomfortable_answer": ("the correct total exceeds the cap; within_cap is false and "
                                 "amount_over_cap_eur is non-zero. Trimming a line or a qty to "
                                 "fit is violation V5."),
    }
    return answer, diag


# ==========================================================================
# E-002  — migration runbook
# ==========================================================================
def e002():
    svc = {r["service"]: r for r in rows("services.csv")}

    OUT_OF_SCOPE = {"kestrel-vault"}                 # turn 3
    DEFERRED = {"kestrel-mailer"}                    # turn 9
    in_scope = {s: r for s, r in svc.items() if s not in OUT_OF_SCOPE | DEFERRED}

    def deps(s):
        raw = svc[s]["depends_on"]
        return [d for d in raw.split(";") if d and d in in_scope]

    # turn 5: wave = 1 if no in-scope dependency, else max(dep waves) + 1
    wave = {}

    def resolve(s, seen=()):
        assert s not in seen, f"dependency cycle at {s}"
        if s in wave:
            return wave[s]
        d = deps(s)
        wave[s] = 1 if not d else max(resolve(x, seen + (s,)) for x in d) + 1
        return wave[s]

    for s in in_scope:
        resolve(s)

    # turn 5: wave asc, tier asc, service name asc -- fixed for the rest of the job
    order = sorted(in_scope, key=lambda s: (wave[s], int(svc[s]["tier"]), s))

    # turn 11: a verification step immediately after every tier-1 migration step
    seq = []
    for s in order:
        seq.append(("migrate", s))
        if int(svc[s]["tier"]) == 1:
            seq.append(("verify", s))

    start = datetime(2032, 5, 10, 22, 0, 0, tzinfo=timezone.utc)   # turn 10
    STEP_MIN = 45
    steps = []
    for i, (action, s) in enumerate(seq):
        steps.append({
            "step_id": f"MIG-{i + 1:03d}",                          # turn 2
            "action": action,
            "service": s,
            "wave": wave[s],
            "owner_team": svc[s]["owner_team"],                     # turn 14
            "start_utc": (start + timedelta(minutes=STEP_MIN * i)
                          ).strftime("%Y-%m-%dT%H:%M:%SZ"),         # turn 6
        })

    assert not any(st["service"] in OUT_OF_SCOPE | DEFERRED for st in steps)
    answer = {
        "steps": steps,
        "step_count": len(steps),
        "total_duration_minutes": len(steps) * STEP_MIN,
    }
    diag = {
        "waves": dict(sorted(wave.items())),
        "excluded": {"out_of_scope_turn_3": sorted(OUT_OF_SCOPE),
                     "deferred_turn_9": sorted(DEFERRED)},
        "migration_order_before_verification_steps": order,
        "tier_1_services_in_scope": sorted(s for s in in_scope if svc[s]["tier"] == "1"),
        "third_step_start_at_turn_10_before_verification_steps": (
            start + timedelta(minutes=STEP_MIN * 2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return answer, diag


# ==========================================================================
# E-003  — shift assignment
# ==========================================================================
REASONS = [
    "no_person_with_required_certification_at_site",
    "all_eligible_on_leave",
    "no_night_qualified_person",
    "max_shifts_exhausted",
]


def e003():
    shifts = rows("shifts.csv")
    staff = {r["person_id"]: dict(r) for r in rows("staff_roster.csv")}

    staff["PR-014"]["status"] = "on_leave"        # turn 12
    staff["PR-016"]["max_shifts"] = "3"           # turn 16 (deliberate no-op)

    assigned_count = {pid: 0 for pid in staff}
    out = []
    for sh in sorted(shifts, key=lambda r: r["shift_id"]):
        assert sh["headcount"] == "1", sh          # one person per shift
        # turn 2 (exact certification) + turn 3 (same site)
        cert_site = [p for p in staff.values()
                     if p["certification"] == sh["required_certification"]
                     and p["site_id"] == sh["site_id"]]
        # turn 4
        avail = [p for p in cert_site if p["status"] != "on_leave"]
        # turn 5
        night_ok = [p for p in avail
                    if sh["window"] != "night" or p["night_qualified"] == "yes"]
        # turn 6
        free = [p for p in night_ok
                if assigned_count[p["person_id"]] < int(p["max_shifts"])]

        if free:
            # no shift in this corpus has more than one eligible person; assert it
            # so the key can never depend on an undefined tie-break.
            assert len(free) == 1, (sh["shift_id"], [p["person_id"] for p in free])
            chosen = free[0]
            assigned_count[chosen["person_id"]] += 1
            out.append({"shift_id": sh["shift_id"],
                        "assigned_person_id": chosen["person_id"],
                        "reason_if_unfilled": None})
        else:
            # turn 7 / turn 20: first applicable reason, in the stated order
            if not cert_site:
                reason = REASONS[0]
            elif not avail:
                reason = REASONS[1]
            elif not night_ok:
                reason = REASONS[2]
            else:
                reason = REASONS[3]
            out.append({"shift_id": sh["shift_id"],
                        "assigned_person_id": None,
                        "reason_if_unfilled": reason})

    unfilled = sum(1 for r in out if r["assigned_person_id"] is None)
    answer = {"assignments": out, "unfilled_count": unfilled}
    diag = {
        "turn_12_change": "PR-014 treated as on_leave for every shift",
        "turn_16_change": "PR-016 max_shifts raised to 3 - no effect, PR-016 takes 2 shifts",
        "shifts_per_person": {k: v for k, v in sorted(assigned_count.items()) if v},
        "turn_17_PR-011_can_cover_SH-111": False,
        "turn_17_reason": "PR-011 holds C3; SH-111 requires exactly C2 (turn 2: labels, not levels)",
        "turn_18_PR-012_can_cover_SH-110": False,
        "turn_18_reason": "PR-012 is night_qualified=no and SH-110 is a night shift (turn 5)",
        "uncomfortable_answer": ("SH-105 and SH-106 have no eligible person once PR-014 is on "
                                 "leave and are reported UNFILLED; assigning PR-007 (C3) or an "
                                 "on-leave person is violation V1/V3."),
    }
    return answer, diag


# ==========================================================================
def main():
    write = "--write" in sys.argv
    a1, d1 = e001()
    a2, d2 = e002()
    a3, d3 = e003()

    keys = {
        "E-001": {
            "task_id": "E-001",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Replayed turns 1-18 in order against corpora/workflow_e/: the turn-3 vendor "
                "exclusion forces KP-4477 in place of the obvious KP-4410 for the 2U edge "
                "appliance, the turn-14 quantity revision and the turn-15 line removal are "
                "applied to the final table, and procurement_policy.md supplies the 12% "
                "hardware-only contingency (P2), the per-vendor 1%/3% freight against the "
                "SITE-BIL-1 region (P4), the two-approver threshold (P5) and the hardware-only "
                "max lead time (P6), with half-up rounding applied once per figure (P1). "
                "Script: scripts/derive_E.py"
            ),
            "derivation_script": "scripts/derive_E.py",
            "derivation_diagnostics": d1,
            **a1,
        },
        "E-002": {
            "task_id": "E-002",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Replayed turns 1-16: kestrel-vault removed from scope (turn 3) and its "
                "dependencies treated as satisfied, kestrel-mailer dropped (turn 9), wave numbers "
                "computed from the remaining in-scope dependency graph (turn 5), steps ordered by "
                "wave/tier/name, a verify step inserted after every tier-1 migrate step "
                "(turn 11), step ids MIG-001.. gapless (turn 2) and start times accumulated in "
                "45-minute increments from 2032-05-10T22:00:00Z (turn 10) in RFC 3339 UTC "
                "(turn 6). Script: scripts/derive_E.py"
            ),
            "derivation_script": "scripts/derive_E.py",
            "derivation_diagnostics": d2,
            **a2,
        },
        "E-003": {
            "task_id": "E-003",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Replayed turns 1-20: applied the six eligibility rules from turns 2-7 as a "
                "cascade (exact certification, same site, not on leave, night qualification, "
                "max_shifts), applied the turn-12 change making PR-014 unavailable and the "
                "turn-16 no-op raising PR-016's max_shifts, and reported every shift with no "
                "eligible person as unfilled with the first applicable reason string. Every "
                "fillable shift has exactly one eligible candidate, which the script asserts, so "
                "no tie-break is needed. Script: scripts/derive_E.py"
            ),
            "derivation_script": "scripts/derive_E.py",
            "derivation_diagnostics": d3,
            **a3,
        },
    }

    if write:
        for tid, obj in keys.items():
            p = os.path.join(KEYS_DIR, f"{tid}.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(obj, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            print("wrote", p, file=sys.stderr)
    else:
        print(json.dumps(keys, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

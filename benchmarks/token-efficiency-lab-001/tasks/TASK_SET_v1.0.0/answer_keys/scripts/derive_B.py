#!/usr/bin/env python3
"""Derive answer keys for workload B (B-001..B-003) of TASK_SET_v1.0.0.

Every value emitted is pulled out of the source document by a regex anchored on
the clause / table row / errata line that states it.  Nothing is typed in by
hand: the mapping from clause number to output field is hand-coded (it has to
be), but the values themselves always come from the document.

Usage:  python3 derive_B.py [--write]
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(KEYS_DIR)
DOCS = os.path.join(ROOT, "corpora", "docs_b")


def read(name):
    with open(os.path.join(DOCS, name), "r", encoding="utf-8") as fh:
        return fh.read()


def grab(text, pattern, group=1, flags=0):
    """Exactly-one-match regex extraction; anything else is a corpus surprise."""
    ms = re.findall(pattern, text, flags)
    assert len(ms) == 1, f"pattern {pattern!r} matched {len(ms)} times"
    m = re.search(pattern, text, flags)
    return m.group(group)


def num(s):
    s = s.replace(",", "")
    return float(s) if "." in s else int(s)


# ==========================================================================
# B-001  — MSA as in effect on 2031-11-30
# ==========================================================================
AS_OF = "2031-11-30"


def b001():
    t = read("MSA_ORBITAL_HARBOR_consolidated.md")

    # --- amendments: heading text + effective date, in document order -------
    amd = []  # (heading_as_printed, effective_date, body_text)
    parts = re.split(r"^## (AMENDMENT No\. \d+)\s*$", t, flags=re.M)
    for i in range(1, len(parts), 2):
        heading, body = parts[i], parts[i + 1]
        eff = grab(body, r"\*\*Amendment Effective Date:\s*(\d{4}-\d{2}-\d{2})\*\*")
        amd.append((heading, eff, body))
    assert len(amd) == 3, amd
    in_force = [(h, e, b) for (h, e, b) in amd if e <= AS_OF]

    def amd_body(n):
        return amd[n - 1][2]

    def is_in_force(n):
        return amd[n - 1][1] <= AS_OF

    # --- body of the agreement --------------------------------------------
    v = {}
    v["contract_reference"] = grab(t, r"\*\*Contract reference:\*\*\s*(\S+)")

    parties = grab(t, r"## PARTIES\n(.*?)\nThis Agreement takes effect", 1, re.S)
    p1 = re.search(
        r"\(1\)\s*\*\*(?P<name>[^*]+)\*\*.*?registry number (?P<reg>\d+),"
        r".*?registered office is at [^,]+, \d+ (?P<city>[A-Za-z]+),", parties, re.S)
    p2 = re.search(
        r"\(2\)\s*\*\*(?P<name>[^*]+)\*\*.*?company number (?P<num>\d+),"
        r".*?registered office is at [^,]+, (?P<city>[A-Za-z]+) [A-Z0-9 ]+,", parties, re.S)
    assert p1 and p2
    v["provider_legal_name"] = p1.group("name").strip()
    v["provider_registry_number"] = p1.group("reg")
    v["provider_registered_office_city"] = p1.group("city")
    v["customer_legal_name"] = p2.group("name").strip()
    v["customer_company_number"] = p2.group("num")
    v["customer_registered_office_city"] = p2.group("city")

    v["agreement_effective_date"] = grab(
        t, r"This Agreement takes effect on (\d{4}-\d{2}-\d{2})")
    v["initial_term_months"] = num(grab(t, r"^4\.1 .*?initial term of [a-z-]+ \((\d+)\) months", 1, re.M))
    m42 = re.search(r"^4\.2 .*?renewal terms of [a-z ]+ \((\d+)\) months.*?"
                    r"not less than [a-z ]+ \((\d+)\) days", t, re.M | re.S)
    v["renewal_term_months"] = num(m42.group(1))
    v["non_renewal_notice_days"] = num(m42.group(2))
    v["termination_for_convenience_notice_days"] = num(
        grab(t, r"^8\.1 .*?not less than [a-z ]+ \((\d+)\) days", 1, re.M))
    v["material_breach_remedy_days"] = num(
        grab(t, r"^8\.2 .*?not remedied within [a-z-]+ \((\d+)\) days", 1, re.M))
    v["governing_law"] = grab(t, r"^24\.1 .*?governed by the laws of ([A-Za-z ]+)\.", 1, re.M)
    v["jurisdiction_city"] = grab(t, r"^24\.2 .*?courts of ([A-Za-z ]+)\.", 1, re.M)
    v["payment_terms_days"] = num(grab(t, r"^5\.1 .*?within [a-z ]+ \((\d+)\) days", 1, re.M))
    v["late_payment_interest_percent_above_base"] = num(
        grab(t, r"^5\.2 .*?\(([\d.]+)%\) per annum above the base rate", 1, re.M))
    m53 = re.search(r"^5\.3 The Provider may increase the Charges (\w+) in any twelve month "
                    r"period by no more than [a-z ]+ \(([\d.]+)%\)", t, re.M)
    v["annual_price_increase_cap_percent"] = num(m53.group(2))
    v["price_increase_frequency_per_twelve_months"] = {"once": 1, "twice": 2}[m53.group(1)]
    v["liability_cap_percent_of_charges"] = num(
        grab(t, r"^9\.1 .*?limited to [a-z ]+ \((\d+)%\)", 1, re.M))
    v["liability_cap_absolute_eur"] = num(
        grab(t, r"^9\.2 .*?capped at [a-z ]+ euro \(EUR ([\d,]+)\)", 1, re.M))
    v["cyber_insurance_minimum_eur"] = num(
        grab(t, r"^10\.1 .*?not less than [a-z ]+ euro \(EUR ([\d,]+)\)", 1, re.M))
    v["personal_data_retention_days"] = num(
        grab(t, r"^12\.1 .*?no longer than [a-z ]+ \((\d+)\) days", 1, re.M))
    v["subprocessor_objection_days"] = num(
        grab(t, r"^12\.2 .*?within [a-z ]+ \((\d+)\) days", 1, re.M))
    m131 = re.search(r"^13\.1 .*?not less than [a-z ]+ \((\d+)\) Business Days.*?"
                     r"no more than (\w+) in any twelve month period", t, re.M)
    v["audit_notice_business_days"] = num(m131.group(1))
    v["audit_frequency_per_twelve_months"] = {"once": 1, "twice": 2}[m131.group(2)]

    # --- Schedule B (outranks the body for service levels) -----------------
    sched_b = grab(t, r"## SCHEDULE B — SERVICE LEVELS\n(.*?)\n## SCHEDULE C", 1, re.S)
    v["availability_target_percent"] = num(
        grab(sched_b, r"^B\.1 The Availability Target .*? is ([\d.]+)% measured monthly", 1, re.M))
    mb2 = re.search(r"^B\.2 .*?acknowledge within [a-z ]+ \((\d+)\) minutes and shall restore "
                    r"service within [a-z ]+ \((\d+)\) hours", sched_b, re.M)
    v["p1_acknowledgement_minutes"] = num(mb2.group(1))
    v["p1_restoration_hours"] = num(mb2.group(2))
    bands = re.findall(r"^\| below [^|]*\|\s*(\d+)%\s*\|$", sched_b, re.M)
    assert len(bands) == 3, bands
    for i, b in enumerate(bands, start=1):
        v[f"service_credit_percent_band_{i}"] = num(b)

    # Schedule C is read only to confirm it is subordinate; its values are
    # deliberately NOT used (order of precedence item 4 < item 3).
    sched_c = grab(t, r"## SCHEDULE C — COMMERCIAL TERMS\n(.*?)\n## SCHEDULE D", 1, re.S)
    assert "subordinate to the body" in sched_c

    # --- amendment effective dates ----------------------------------------
    for n in (1, 2, 3):
        v[f"amendment_{n}_effective_date"] = amd[n - 1][1]

    # --- apply the in-force amendments ------------------------------------
    if is_in_force(1):
        b = amd_body(1)
        v["payment_terms_days"] = num(grab(b, r"^A1\.1 .*?within [a-z ]+ \((\d+)\) days", 1, re.M))
        v["audit_notice_business_days"] = num(
            grab(b, r"^A1\.2 .*?audit notice period is [a-z ]+ \((\d+)\) Business Days", 1, re.M))
    if is_in_force(2):
        b = amd_body(2)
        v["liability_cap_percent_of_charges"] = num(
            grab(b, r"^A2\.1 .*?limited to [a-z ]+ \((\d+)%\)", 1, re.M))
        v["p1_restoration_hours"] = num(
            grab(b, r"^A2\.2 .*?restoration time is [a-z ]+ \((\d+)\) hours", 1, re.M))
        v["subprocessor_objection_days"] = num(
            grab(b, r"^A2\.3 .*?objection period is [a-z ]+ \((\d+)\) days", 1, re.M))
        v["availability_target_percent"] = num(
            grab(b, r"^A2\.4 .*?Availability Target is ([\d.]+)% measured monthly", 1, re.M))
    if is_in_force(3):
        b = amd_body(3)
        v["termination_for_convenience_notice_days"] = num(
            grab(b, r"^A3\.1 .*?not less than [a-z ]+ \((\d+)\) days", 1, re.M))
        v["liability_cap_absolute_eur"] = num(
            grab(b, r"^A3\.2 .*?capped at [a-z ]+ euro \(EUR ([\d,]+)\)", 1, re.M))
        m = re.search(r"^A3\.3 .*?renewal term is [a-z ]+ \((\d+)\) months.*?"
                      r"notice period is [a-z ]+ \((\d+)\) days", b, re.M)
        v["renewal_term_months"] = num(m.group(1))
        v["non_renewal_notice_days"] = num(m.group(2))

    # The headings are printed in upper case ("AMENDMENT No. 1"); the task
    # prompt gives the expected spelling as "Amendment No. 1", so the prompt's
    # spelling is used.  See BUILDER_NOTES.md (B-001 ambiguity 1).
    v["amendments_in_force_on_as_of_date"] = [
        re.sub(r"^AMENDMENT", "Amendment", h) for (h, _, _) in in_force
    ]

    order = [
        "contract_reference", "provider_legal_name", "provider_registry_number",
        "provider_registered_office_city", "customer_legal_name", "customer_company_number",
        "customer_registered_office_city", "agreement_effective_date", "initial_term_months",
        "renewal_term_months", "non_renewal_notice_days",
        "termination_for_convenience_notice_days", "material_breach_remedy_days",
        "governing_law", "jurisdiction_city", "payment_terms_days",
        "late_payment_interest_percent_above_base", "annual_price_increase_cap_percent",
        "liability_cap_percent_of_charges", "liability_cap_absolute_eur",
        "cyber_insurance_minimum_eur", "availability_target_percent",
        "p1_acknowledgement_minutes", "p1_restoration_hours",
        "service_credit_percent_band_1", "service_credit_percent_band_2",
        "service_credit_percent_band_3", "price_increase_frequency_per_twelve_months",
        "personal_data_retention_days", "subprocessor_objection_days",
        "audit_notice_business_days", "audit_frequency_per_twelve_months",
        "amendment_1_effective_date", "amendment_2_effective_date",
        "amendment_3_effective_date", "amendments_in_force_on_as_of_date",
    ]
    assert set(order) == set(v), (set(order) ^ set(v))
    assert len(order) == 36
    return {k: v[k] for k in order}


# ==========================================================================
# B-002  — incident register, corrected
# ==========================================================================
def b002():
    t = read("KESTREL_RELIABILITY_2031.md")

    reg_block = grab(t, r"## 6\. Appendix A — Incident Register\n(.*?)\n## 7\.", 1, re.S)
    rows = re.findall(
        r"^\| (INC-\d{4}-\d{3}) \| ([^|]+?) \| (\S+) \| (\d+) \| (S\d) \| (RC-[A-Z]+) \| (yes|no) \|$",
        reg_block, re.M)
    assert len(rows) == 48, len(rows)
    incidents = {}
    for iid, service, start, dur, sev, rc, ci in rows:
        assert iid not in incidents
        incidents[iid] = {
            "incident_id": iid,
            "service": service.strip(),
            "start_utc": start,
            "duration_minutes": int(dur),
            "final_severity": sev,
            "root_cause_code": rc,
            "customer_impacting": ci == "yes",
        }

    notices = re.findall(
        r"\*\*Correction Notice (CN-\d+)\*\* — For incident (INC-\d{4}-\d{3}), the value "
        r"recorded in Appendix A for `([a-z_]+)` is incorrect\. The value published as `([^`]+)` "
        r"is withdrawn and replaced by `([^`]+)`\.", t)
    assert len(notices) == 8, len(notices)

    applied = []
    for cn, iid, field, old, new in notices:
        rec = incidents[iid]
        key = field  # 'final_severity' in the notices maps to the register's 'severity' column
        assert key in rec, (cn, field)
        if isinstance(rec[key], bool):
            assert str(rec[key]) == str(old == "yes"), (cn, rec[key], old)
            rec[key] = new == "yes"
        elif isinstance(rec[key], int):
            assert rec[key] == int(old), (cn, rec[key], old)
            rec[key] = int(new)
        else:
            assert rec[key] == old, (cn, rec[key], old)
            rec[key] = new
        applied.append({"notice": cn, "incident_id": iid, "field": field,
                        "from": old, "to": new})

    sel = [incidents[i] for i in sorted(incidents)
           if incidents[i]["final_severity"] in ("S1", "S2")]
    return {"incidents": sel, "count": len(sel)}, applied


# ==========================================================================
# B-003  — MUST requirements after errata
# ==========================================================================
LEVEL_WORDS = [
    (r"\bmust not\b", "MUST NOT"),
    (r"\bmust\b", "MUST"),
    (r"\bshould not\b", "SHOULD NOT"),
    (r"\bshould\b", "SHOULD"),
    (r"\bmay\b", "MAY"),
]


def b003():
    t = read("SDX7_PROTOCOL_SPEC_v3.1.md")
    lines = t.split("\n")

    body = {}
    section = None
    for line in lines:
        ms = re.match(r"^## (\d+)\. ", line)
        if ms:
            section = int(ms.group(1))
            continue
        mr = re.match(r"^\*\*(SDX-REQ-\d+)\*\* An implementation (.+)$", line)
        if mr:
            req, rest = mr.group(1), mr.group(2)
            level = None
            for pat, lv in LEVEL_WORDS:
                if re.search(pat, rest):
                    level = lv
                    break
            assert level, line
            field = grab(rest, r"`([a-z_0-9]+)`")
            assert req not in body, req
            assert section is not None and 2 <= section <= 9, (req, section)
            body[req] = {"req_id": req, "section": section,
                         "constrained_field": field, "level": level}

    errata_block = grab(t, r"## 10\. Errata applying to version 3\.1\n(.*)$", 1, re.S)
    errata = {}
    for line in errata_block.split("\n"):
        m = re.match(r"^- \*\*(SDX-REQ-\d+)\*\* — (.*)$", line)
        if not m:
            continue
        req, rest = m.group(1), m.group(2)
        assert req not in errata, req
        if rest.startswith("**Withdrawn.**"):
            errata[req] = ("withdrawn", None)
        elif rest.startswith("**Clarified.**"):
            errata[req] = ("clarified", None)
        else:
            lv = grab(rest, r"The correct level is \*\*([A-Z ]+)\*\*\.")
            errata[req] = ("relevel", lv)
        assert req in body, req

    out = []
    for req, rec in body.items():
        kind, lv = errata.get(req, (None, None))
        if kind == "withdrawn":
            continue
        if kind == "relevel":
            level, source = lv, "errata"
        else:
            level, source = rec["level"], "body"
        if level != "MUST":
            continue
        out.append({"req_id": req, "section": rec["section"],
                    "constrained_field": rec["constrained_field"],
                    "level_source": source})
    out.sort(key=lambda r: r["req_id"])

    diag = {
        "total_requirements_in_body": len(body),
        "errata_entries": {k: v[0] + (f":{v[1]}" if v[1] else "") for k, v in errata.items()},
        "body_must_count_ignoring_errata": sum(1 for r in body.values() if r["level"] == "MUST"),
    }
    return {"requirements": out, "count": len(out)}, diag


# ==========================================================================
def main():
    write = "--write" in sys.argv
    b1 = b001()
    b2, applied = b002()
    b3, diag3 = b003()

    keys = {
        "B-001": {
            "task_id": "B-001",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Regex extraction anchored on each numbered clause, Schedule B paragraph and "
                "amendment sub-clause of MSA_ORBITAL_HARBOR_consolidated.md, followed by the "
                "document's own order of precedence: Schedule C is read but discarded (it ranks "
                "below the body), Schedule B supplies the service levels, and Amendments 1 and 2 "
                "are applied because their Amendment Effective Dates are on or before the as-of "
                "date 2031-11-30 while Amendment No. 3 (2032-01-01) is not. "
                "Script: scripts/derive_B.py"
            ),
            "derivation_script": "scripts/derive_B.py",
            "as_of_date": AS_OF,
            "contract_terms": b1,
        },
        "B-002": {
            "task_id": "B-002",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Parsed the 48-row Appendix A markdown table of KESTREL_RELIABILITY_2031.md, "
                "parsed all 8 Appendix B correction notices with a regex capturing "
                "(incident, field, old value, new value), asserted each old value against the "
                "register before overwriting it, then kept the records whose post-correction "
                "severity is S1 or S2. The quarterly narrative is never read. "
                "Script: scripts/derive_B.py"
            ),
            "derivation_script": "scripts/derive_B.py",
            "corrections_applied": applied,
            **b2,
        },
        "B-003": {
            "task_id": "B-003",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Parsed every '**SDX-REQ-nnnn** An implementation ...' line of "
                "SDX7_PROTOCOL_SPEC_v3.1.md, taking the section from the enclosing '## n.' "
                "heading, the constrained field from the backticked identifier and the level from "
                "the modal verb (longest match first, so 'must not' never reads as 'must'), then "
                "applied section 10: withdrawn entries are dropped, relevel entries replace the "
                "level and set level_source=errata, clarified entries leave the body level and "
                "level_source=body. Kept only level MUST. Script: scripts/derive_B.py"
            ),
            "derivation_script": "scripts/derive_B.py",
            "derivation_diagnostics": diag3,
            **b3,
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

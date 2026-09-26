#!/usr/bin/env python3
"""Derive answer keys for workload B (B-001..B-003) of TASK_SET_v1.1.0.

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
# B-002  — final-severity incident table (v1.1.0 document)
#
# The v1.1.0 KESTREL_RELIABILITY_2031.md records the base values in FOUR
# per-quarter registers (sections 2.9, 3.9, 4.9, 5.9) and layers two
# superseding appendices on top of them:
#
#   Appendix A (section 7) — Register Amendments, issued 2032-01-20.  One
#       incident and one field each; `field` == "withdrawn" removes the
#       incident from the reporting year in full (document rule R-2).
#   Appendix B (section 8) — Correction Notices, issued 2032-02-14.  One
#       incident and one field each; supersedes EVERY other source including
#       an Amendment naming the same incident and the same field.
#
# Document rule R-3: the S1/S2 selection is made after both layers are applied.
# ==========================================================================
REGISTER_COLUMN = {          # document field name -> record key
    "service": "service",
    "start_utc": "start_utc",
    "duration_minutes": "duration_minutes",
    "severity": "final_severity",
    "root_cause_code": "root_cause_code",
    "customer_impacting": "customer_impacting",
}

QUARTER_MONTHS = {2: ("01", "02", "03"), 3: ("04", "05", "06"),
                  4: ("07", "08", "09"), 5: ("10", "11", "12")}


def _coerce(record_key, raw):
    """A raw document token as the record's Python value."""
    if record_key == "duration_minutes":
        return int(raw)
    if record_key == "customer_impacting":
        assert raw in ("yes", "no"), raw
        return raw == "yes"
    return raw


def b002():
    t = read("KESTREL_RELIABILITY_2031.md")

    # --- the four quarter registers (precedence rank 3) --------------------
    incidents = {}
    per_quarter = {}
    for sec in (2, 3, 4, 5):
        block = grab(t, r"^### %d\.9 Quarter \d incident register\n(.*?)(?=^## |\Z)" % sec,
                     1, re.M | re.S)
        rows = re.findall(
            r"^\| (INC-\d{4}-\d{3}) \| ([^|]+?) \| (\S+) \| (\d+) \| (S\d) \| "
            r"(RC-[A-Z]+) \| (yes|no) \|$", block, re.M)
        assert rows, sec
        per_quarter[sec - 1] = len(rows)
        for iid, service, start, dur, sev, rc, ci in rows:
            assert iid not in incidents, ("incident in two registers", iid)
            assert start[5:7] in QUARTER_MONTHS[sec], ("wrong quarter register", iid, start)
            incidents[iid] = {
                "incident_id": iid,
                "service": service.strip(),
                "start_utc": start,
                "duration_minutes": int(dur),
                "final_severity": sev,
                "root_cause_code": rc,
                "customer_impacting": ci == "yes",
            }
    assert len(incidents) == 48, len(incidents)

    # --- Appendix A: Register Amendments (precedence rank 2) ---------------
    amd_block = grab(t, r"^## 7\. Appendix A — Register Amendments\n(.*?)(?=^## 8\.)",
                     1, re.M | re.S)
    amendments = re.findall(
        r"^\| (RA-\d{4}-\d{2}) \| (INC-\d{4}-\d{3}) \| ([a-z_]+) \| ([^|]*) \| ([^|]*) \|$",
        amd_block, re.M)
    assert len(amendments) == 9, len(amendments)

    withdrawn = {}
    applied = []
    for aid, iid, field, was, now in amendments:
        was, now = was.strip(), now.strip()
        assert iid in incidents, (aid, iid)
        if field == "withdrawn":
            assert was == "" and now == "", (aid, was, now)
            withdrawn[iid] = aid
            applied.append({"layer": "register_amendment", "amendment": aid,
                            "incident_id": iid, "field": "withdrawn",
                            "effect": "incident removed from the reporting year"})
            continue
        assert field in REGISTER_COLUMN, (aid, field)
        key = REGISTER_COLUMN[field]
        rec = incidents[iid]
        assert rec[key] == _coerce(key, was), ("amendment `was` disagrees with the register",
                                               aid, rec[key], was)
        rec[key] = _coerce(key, now)
        applied.append({"layer": "register_amendment", "amendment": aid,
                        "incident_id": iid, "field": field, "from": was, "to": now})

    # R-2: a withdrawn incident is not an incident of 2031 at all.
    for iid, aid in withdrawn.items():
        del incidents[iid]

    # --- Appendix B: Correction Notices (precedence rank 1) ----------------
    cn_block = grab(t, r"^## 8\. Appendix B — Correction Notices\n(.*)$", 1, re.M | re.S)
    notices = re.findall(
        r"\*\*Correction Notice (CN-\d+)\*\* — For incident (INC-\d{4}-\d{3}), the value "
        r"standing for `([a-z_]+)` is incorrect\. The value standing as `([^`]+)` is "
        r"withdrawn and replaced by `([^`]+)`\.", cn_block)
    assert len(notices) == 8, len(notices)

    for cn, iid, field, old, new in notices:
        # R-2: "No correction notice reinstates a withdrawn incident."
        assert iid not in withdrawn, ("notice names a withdrawn incident", cn, iid)
        assert iid in incidents, (cn, iid)
        assert field in REGISTER_COLUMN, (cn, field)
        key = REGISTER_COLUMN[field]
        rec = incidents[iid]
        # `the value STANDING as X` — i.e. after any amendment on the same field.
        assert rec[key] == _coerce(key, old), ("notice `standing as` disagrees with the "
                                               "standing value", cn, rec[key], old)
        rec[key] = _coerce(key, new)
        applied.append({"layer": "correction_notice", "notice": cn, "incident_id": iid,
                        "field": field, "from": old, "to": new})

    # --- R-3: select on the FINAL severity, last ---------------------------
    sel = [incidents[i] for i in sorted(incidents)
           if incidents[i]["final_severity"] in ("S1", "S2")]

    diag = {
        "register_rows_per_quarter": {"Q%d" % q: n for q, n in sorted(per_quarter.items())},
        "incidents_in_registers": 48,
        "register_amendments": len(amendments),
        "withdrawn_incidents": withdrawn,
        "correction_notices": len(notices),
        "incidents_after_withdrawal": len(incidents),
        "selected_s1_s2": len(sel),
    }
    return {"incidents": sel, "count": len(sel)}, applied, diag


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
    b2, applied, diag2 = b002()
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
                "Parsed the four per-quarter incident registers (sections 2.9, 3.9, 4.9, 5.9) "
                "of KESTREL_RELIABILITY_2031.md - 48 rows in total - then applied the document's "
                "section 1.4 precedence in rank order: the nine Appendix A Register Amendments "
                "over the registers (one of which, RA-2032-03, withdraws INC-2031-047 in full "
                "under rule R-2, so it appears in no table derived from the report), then the "
                "eight Appendix B Correction Notices over everything, including over an "
                "Amendment naming the same incident and the same field (INC-2031-021 and "
                "INC-2031-024 are each amended and then corrected). Each layer's stated prior "
                "value is asserted against the value actually standing before it is overwritten. "
                "Selection of S1/S2 happens last, on the final severity (rule R-3). The quarterly "
                "narrative is never read: it ranks below the registers and decides nothing. "
                "Script: scripts/derive_B.py"
            ),
            "derivation_script": "scripts/derive_B.py",
            "derivation_diagnostics": diag2,
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

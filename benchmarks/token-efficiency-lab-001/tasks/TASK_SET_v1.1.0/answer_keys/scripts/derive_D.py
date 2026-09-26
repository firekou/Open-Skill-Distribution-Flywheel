#!/usr/bin/env python3
"""Derive answer keys for workload D (D-001..D-004) of TASK_SET_v1.1.0.

Every value is obtained by invoking the offline MCP toolset the task itself
points at:  `python3 corpora/mcp_toolset/server.py call <tool> '<json>'`.
Nothing is read out of corpora/mcp_toolset/fixtures/ and nothing is read out of
server.py -- the key is derived the same way a correct run would derive it, so
it also proves the required tool set is sufficient.

The key records `required_tools` per task: the contested-family tools a correct
run must call.  The tool_selection metric treats any *other* call into a
contested family as a wrong-tool invocation.

Usage:  python3 derive_D.py [--write]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(KEYS_DIR)
SERVER = os.path.join(ROOT, "corpora", "mcp_toolset", "server.py")
TOOLS = json.load(open(os.path.join(ROOT, "corpora", "mcp_toolset", "tools.json")))["tools"]
FAMILY = {t["name"]: t["family"] for t in TOOLS}

CALLS = []          # audit of every call this script made


def call(tool, args):
    """Invoke one tool through the server's direct CLI and return its JSON."""
    env = dict(os.environ)
    env.pop("LAB001_TOOL_AUDIT", None)      # never pollute a run's audit file
    p = subprocess.run(
        [sys.executable, SERVER, "call", tool, json.dumps(args)],
        capture_output=True, text=True, check=True, env=env, cwd=ROOT)
    CALLS.append({"tool": tool, "family": FAMILY.get(tool), "args": args})
    return json.loads(p.stdout)


def minutes_between(a, b):
    fmt = "%Y-%m-%dT%H:%M:%S%z"
    ta = datetime.strptime(a.replace("Z", "+0000"), fmt).astimezone(timezone.utc)
    tb = datetime.strptime(b.replace("Z", "+0000"), fmt).astimezone(timezone.utc)
    return int((tb - ta).total_seconds() // 60)


# --------------------------------------------------------------------------
def d001():
    oncall = call("rota.get_effective_oncall",
                  {"service": "kestrel-billing", "at_utc": "2032-03-14T02:40:00Z"})
    assert oncall["role"] == "primary", oncall["role"]
    person = call("directory.get_person_by_handle", {"handle": oncall["handle"]})
    assert person["status"] == "active" and person["record_source"] == "live", person
    answer = {
        "engineer_full_name": person["full_name"],
        "team": person["team"],
        "escalation_tier": oncall["escalation_tier"],
    }
    return answer, ["rota.get_effective_oncall", "directory.get_person_by_handle"], {
        "template_handle_before_overrides": oncall["template_handle_before_overrides"],
        "override_chain": oncall["override_chain"],
    }


def d002():
    res = call("registry.resolve_digest_pinned",
               {"repository": "apps/kestrel-gateway", "tag": "2031.11-stable"})
    digest = res["digest"]
    assert res["moved_since_publication"] is True
    scan = call("vulndb.get_image_findings_by_digest", {"digest": digest, "status": "all"})
    crit_open = [f for f in scan["findings"]
                 if f["severity"] == "CRITICAL" and f["status"] == "open"]
    top = max(crit_open, key=lambda f: f["cvss"])
    assert sum(1 for f in crit_open if f["cvss"] == top["cvss"]) == 1, "CVSS tie"
    fixes = call("vulndb.get_fix_versions", {"advisory_id": top["advisory_id"]})
    dist = scan["distribution"]
    fixed = [r["fixed_version"] for r in fixes["fixes"] if r["distribution"] == dist]
    assert len(fixed) == 1, fixed
    answer = {
        "digest": digest,
        "critical_open_count": len(crit_open),
        "highest_cvss_advisory_id": top["advisory_id"],
        "distribution": dist,
        "fixed_version": fixed[0],
    }
    return answer, ["registry.resolve_digest_pinned", "vulndb.get_image_findings_by_digest"], {
        "publish_time_digest_not_used": res["previous_digest"],
        "critical_open_findings": crit_open,
        "critical_findings_excluded_because_not_open": [
            f for f in scan["findings"]
            if f["severity"] == "CRITICAL" and f["status"] != "open"],
    }


def d003():
    inv = call("billing.get_invoice", {"order_id": "ORD-88213"})
    ship = inv["ship_date"]
    fis = call("fiscal.convert_calendar_to_fiscal", {"date": ship})
    close = call("fiscal.get_period_close_date",
                 {"fiscal_year": fis["fiscal_year"], "fiscal_period": fis["fiscal_period"]})
    answer = {
        "ship_date": ship,
        "fiscal_year": fis["fiscal_year"],
        "fiscal_quarter": fis["fiscal_quarter"],
        "fiscal_period": fis["fiscal_period"],
        "period_close_date": close["close_date"],
    }
    return answer, ["billing.get_invoice", "fiscal.convert_calendar_to_fiscal"], {
        "billing_date_not_used": inv["billing_date"],
        "fiscal_period_window": [fis["period_start"], fis["period_end"]],
    }


def d004():
    eb = call("metrics.get_error_budget_after_exclusions",
              {"service": "kestrel-search", "month": "2032-03"})
    sla = call("tickets.get_effective_sla", {"ticket_id": "TCK-40118"})
    tk = call("tickets.get_ticket", {"ticket_id": "TCK-40118"})
    elapsed = minutes_between(tk["opened_at_utc"], tk["resolved_at_utc"])
    measured = elapsed - sla["clock_stopped_minutes"]
    target = sla["resolution_target_minutes"]
    answer = {
        "remaining_error_budget_minutes": eb["remaining_minutes"],
        "effective_resolution_target_minutes": target,
        "measured_resolution_minutes": measured,
        "sla_breached": measured > target,
    }
    return answer, ["metrics.get_error_budget_after_exclusions", "tickets.get_effective_sla"], {
        "elapsed_minutes": elapsed,
        "clock_stopped_minutes": sla["clock_stopped_minutes"],
        "resolution_target_source": sla["resolution_target_source"],
        "opened_at_utc": tk["opened_at_utc"],
        "resolved_at_utc": tk["resolved_at_utc"],
    }


TASKS = {
    "D-001": (d001, ["oncall-resolution", "person-resolution"]),
    "D-002": (d002, ["image-digest-resolution", "vuln-findings"]),
    "D-003": (d003, ["order-document-resolution", "fiscal-period-resolution",
                     "calendar-period-resolution"]),
    "D-004": (d004, ["error-budget", "sla-resolution"]),
}

METHOD = {
    "D-001": ("Called rota.get_effective_oncall (the override-resolving sibling, not the "
              "template tools) for kestrel-billing at the incident instant, then resolved the "
              "handle it returned with directory.get_person_by_handle (the live single-record "
              "lookup, not the fuzzy search or the lagging sync)."),
    "D-002": ("Called registry.resolve_digest_pinned to get the digest the tag points to now "
              "(the tag has been moved), read vulndb.get_image_findings_by_digest for that "
              "digest, counted the CRITICAL findings whose status is open, took the highest "
              "CVSS among them and read the fix version for the scan's distribution from "
              "vulndb.get_fix_versions (vuln-reference, an uncontested family)."),
    "D-003": ("Called billing.get_invoice for the order, which is the only tool carrying the "
              "ship date, converted that date with fiscal.convert_calendar_to_fiscal (not the "
              "calendar-quarter tool) and read the ledger close date from "
              "fiscal.get_period_close_date (fiscal-reference, an uncontested family)."),
    "D-004": ("Called metrics.get_error_budget_after_exclusions for the reported remaining "
              "budget and tickets.get_effective_sla for the binding target and the stopped-clock "
              "minutes, took the opened/resolved instants from tickets.get_ticket (ticket-record, "
              "an uncontested family) and computed elapsed minus stopped against the target."),
}


def main():
    write = "--write" in sys.argv
    keys = {}
    for tid, (fn, contested) in TASKS.items():
        before = len(CALLS)
        answer, required, diag = fn()
        made = CALLS[before:]
        contested_calls = [c["tool"] for c in made if c["family"] in contested]
        assert set(contested_calls) <= set(required), (tid, contested_calls)
        keys[tid] = {
            "task_id": tid,
            "derived_by": "answer-key-builder",
            "derivation_method": METHOD[tid] + " Script: scripts/derive_D.py",
            "derivation_script": "scripts/derive_D.py",
            "contested_families": contested,
            "required_tools": required,
            "tool_calls_made_by_this_derivation": [
                {"tool": c["tool"], "family": c["family"], "args": c["args"]} for c in made],
            "answer": answer,
            "derivation_diagnostics": diag,
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

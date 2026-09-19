#!/usr/bin/env python3
"""Offline handoff guard. No network, dispatch, locking, or credentials.
Input must be assembled by a trusted controller, never trusted directly from a PR.
CLI: python governance/preflight.py event.json
"""
import json
import re
import sys

def evaluate(e):
    def result(action, reason):
        return {"action": action, "reason": reason}
    required = ["task_id", "head", "live_head", "phase", "event_id",
                "seen_events", "revision", "expected_revision", "stopped",
                "authorized", "run_identity", "executor_identity",
                "attempt", "max_attempts", "cost", "budget", "elapsed", "timeout"]
    if not isinstance(e, dict) or any(k not in e for k in required):
        return result("REJECT", "missing_contract")
    if not all(isinstance(e[k], str) and e[k] for k in
               ["task_id", "event_id", "phase", "run_identity", "executor_identity"]):
        return result("REJECT", "bad_identity")
    if not all(isinstance(e[k], str) and re.fullmatch(r"[0-9a-f]{40}", e[k])
               for k in ["head", "live_head"]):
        return result("REJECT", "bad_sha")
    if not all(type(e[k]) is bool for k in ["stopped", "authorized"]):
        return result("REJECT", "bad_flag")
    if not isinstance(e["seen_events"], list) or not all(isinstance(x, str) for x in e["seen_events"]):
        return result("REJECT", "bad_events")
    if not all(type(e[k]) is int and e[k] >= 0 for k in
               ["revision", "expected_revision", "attempt", "max_attempts"]):
        return result("REJECT", "bad_counter")
    import math
    if not all(type(e[k]) in (int, float) and math.isfinite(e[k]) and e[k] >= 0
               for k in ["cost", "budget", "elapsed", "timeout"]):
        return result("REJECT", "bad_limit")
    if e["stopped"]:
        return result("STOP", "operator_stop")
    if e["event_id"] in e["seen_events"]:
        return result("NOOP", "duplicate")
    if e["head"] != e["live_head"]:
        return result("REJECT", "stale_head")
    if e["revision"] != e["expected_revision"]:
        return result("REJECT", "stale_state")
    if not e["authorized"]:
        return result("REJECT", "outside_authority")
    if e["cost"] > e["budget"] or e["elapsed"] >= e["timeout"] or e["attempt"] >= e["max_attempts"]:
        return result("STOP", "limit")
    phase = e["phase"]
    if phase not in ("execute", "review", "accept_review"):
        return result("REJECT", "unknown_or_external_action")
    if phase in ("review", "accept_review") and e["run_identity"] == e["executor_identity"]:
        return result("REJECT", "self_review")
    if phase == "accept_review":
        r = e.get("review", {})
        if not isinstance(r, dict) or r.get("head") != e["head"] or r.get("reviewer") != e["run_identity"]:
            return result("REJECT", "review_binding")
        if not isinstance(r.get("evidence"), list) or not r["evidence"] or not all(isinstance(x,str) and x for x in r["evidence"]):
            return result("REJECT", "missing_evidence")
        outcomes = {"APPROVED":"COMPLETE", "BLOCKED":"FIX_PENDING",
                    "APPROVED_WITH_CONDITIONS":"CONDITIONS_PENDING",
                    "NEEDS_INFORMATION":"NEEDS_INFORMATION"}
        if r.get("decision") not in outcomes:
            return result("REJECT", "unknown_review_decision")
        return result(outcomes[r["decision"]], "review_record_validated_not_truth_verified")
    return result("DISPATCH_ALLOWED", "guard_only_no_dispatch_performed")

if __name__ == "__main__":
    try:
        with open(sys.argv[1], encoding="utf-8") as stream:
            verdict = evaluate(json.load(stream))
    except (OSError, ValueError, IndexError):
        verdict = {"action":"REJECT", "reason":"unreadable_input"}
    print(json.dumps(verdict))
    sys.exit(1 if verdict["action"] in ("REJECT", "STOP") else 0)

#!/usr/bin/env python3
"""Reviewer-owned static/data checks; never imports or runs PR modules."""
import ast
import json
import pathlib
import sys
root = pathlib.Path(sys.argv[1])
files = ["controller.py", "runners.py", "store.py", "tick.py"]
trees = {name: ast.parse((root / "governance/controller" / name).read_text()) for name in files}
result = {"kind": "static_and_template_data_only", "code_head": "86421c903563a16ca888a4aed10bd614e223ca0e"}
cfg = json.loads((root / "governance/controller/config.live.example.json").read_text())
result["template_expansion"] = {}
for role in ("executor", "reviewer"):
    try:
        [part.format(prompt_file="PROMPT.md", head="0" * 40) for part in cfg["runners"][role]["command"]]
        outcome = "OK"
    except (KeyError, ValueError) as exc:
        outcome = type(exc).__name__ + ": " + str(exc)
    result["template_expansion"][role] = outcome
calls = []
for node in ast.walk(trees["controller.py"]):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        calls.append({"method": node.func.attr, "line": node.lineno})
result["controller_durability_calls"] = {name: [x["line"] for x in calls if x["method"] == name]
    for name in ("acquire", "renew", "holds_lease", "record_intent", "open_intents", "close_intent", "mark_processed", "set_task", "add_spend")}
result["template_policy_sha"] = cfg.get("policy_sha")
result["lease_seconds"] = cfg["lease_seconds"]
result["runner_timeout_seconds"] = cfg["runners"]["executor"]["timeout_seconds"]
result["limitations"] = ["No PR module imported or executed", "No independent controller runtime verification", "No model calls", "No authentication or billing inference"]
print(json.dumps(result, indent=2))

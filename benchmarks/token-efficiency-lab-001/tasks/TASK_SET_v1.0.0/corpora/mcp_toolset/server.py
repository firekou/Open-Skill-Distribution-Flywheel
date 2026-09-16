#!/usr/bin/env python3
"""Offline deterministic tool server for Lab 001 workload D.

No network, no clock, no randomness: the same call always returns the same bytes.

Modes
-----
  python3 server.py list [--server S] [--family F]
  python3 server.py describe <tool_name>
  python3 server.py call <tool_name> '<json-arguments>'
  python3 server.py mcp                # JSON-RPC 2.0 over stdio (initialize,
                                       # tools/list, tools/call)

Audit
-----
If the environment variable LAB001_TOOL_AUDIT is set to a file path, every
tool invocation is appended to it as one JSON object per line:

    {"seq": 1, "tool": "rota.get_effective_oncall", "family": "oncall-resolution",
     "arguments": {...}, "mode": "call"}

`catalog.*` tools are recorded with "family": "meta". The audit log is the
scoring input for tool-selection criteria; it is written by the server, not by
the agent under test.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = json.load(open(os.path.join(HERE, "tools.json")))
TOOLS = {t["name"]: t for t in SPEC["tools"]}
DATA = json.load(open(os.path.join(HERE, "fixtures", "responses.json")))

ARG_DEFAULTS = {
    "rota.get_effective_oncall": {"role": "primary"},
    "vulndb.get_image_findings_by_digest": {"status": "open"},
}
SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
_SEQ = [0]


def _audit(tool, args, mode):
    path = os.environ.get("LAB001_TOOL_AUDIT")
    if not path:
        return
    _SEQ[0] += 1
    rec = {"seq": _SEQ[0], "tool": tool,
           "family": TOOLS.get(tool, {}).get("family", "unknown"),
           "arguments": args, "mode": mode}
    with open(path, "a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


def _catalog(tool, args):
    if tool == "catalog.list_tools":
        rows = []
        for t in SPEC["tools"]:
            if args.get("server") and t["server"] != args["server"]:
                continue
            if args.get("family") and t["family"] != args["family"]:
                continue
            rows.append({"name": t["name"], "server": t["server"], "family": t["family"],
                         "summary": t["description"].split("\n\n")[0]})
        return {"tool_count": len(rows), "tools": rows}
    if tool == "catalog.describe_tool":
        name = args.get("name")
        if name not in TOOLS:
            return {"status": "not_found", "name": name}
        return TOOLS[name]
    if tool == "catalog.search_tools":
        q = str(args.get("query", "")).lower()
        limit = int(args.get("limit", 10))
        hits = []
        for t in SPEC["tools"]:
            blob = (t["name"] + " " + t["description"]).lower()
            score = sum(blob.count(w) for w in q.split() if w)
            if score:
                hits.append((score, t))
        hits.sort(key=lambda p: (-p[0], p[1]["name"]))
        return {"query": args.get("query"), "results": [
            {"name": t["name"], "server": t["server"], "family": t["family"], "score": s,
             "summary": t["description"].split("\n\n")[0]} for s, t in hits[:limit]]}
    return {"status": "unknown_catalog_tool", "name": tool}


def call(tool, args, mode="call"):
    if tool not in TOOLS:
        return {"error": "unknown_tool", "name": tool}
    args = dict(args or {})
    for k, v in ARG_DEFAULTS.get(tool, {}).items():
        args.setdefault(k, v)
    _audit(tool, args, mode)

    if tool.startswith("catalog."):
        return _catalog(tool, args)

    schema_props = TOOLS[tool]["inputSchema"]["properties"]
    unknown = [k for k in args if k not in schema_props]
    if unknown:
        return {"error": "unknown_argument", "arguments": unknown, "tool": tool}
    missing = [k for k in TOOLS[tool]["inputSchema"]["required"] if k not in args]
    if missing:
        return {"error": "missing_required_argument", "arguments": missing, "tool": tool}

    entry = DATA.get(tool)
    if entry is None:
        return {"error": "no_fixture", "tool": tool}
    key = "|".join(str(args.get(k, "")) for k in entry["key"])
    result = entry["by_key"].get(key, entry["default"])
    result = json.loads(json.dumps(result))

    if tool == "vulndb.get_image_findings_by_digest" and "findings" in result:
        status = args.get("status", "open")
        floor = SEVERITY_ORDER.get(str(args.get("min_severity", "LOW")).upper(), 0)
        result["findings"] = [f for f in result["findings"]
                              if (status == "all" or f.get("status") == status)
                              and SEVERITY_ORDER.get(f.get("severity"), 0) >= floor]
        result["filter_applied"] = {"status": status, "min_severity": args.get("min_severity", "LOW")}
    if tool == "vulndb.get_image_findings_by_tag" and "findings" in result:
        floor = SEVERITY_ORDER.get(str(args.get("min_severity", "LOW")).upper(), 0)
        result["findings"] = [f for f in result["findings"]
                              if SEVERITY_ORDER.get(f.get("severity"), 0) >= floor]
    return result


def _mcp_loop():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue
        rid = req.get("id")
        method = req.get("method")
        if method == "initialize":
            res = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                   "serverInfo": {"name": "lab001-workload-d", "version": SPEC["toolset_version"]}}
        elif method == "tools/list":
            res = {"tools": [{"name": t["name"], "description": t["description"],
                              "inputSchema": t["inputSchema"]} for t in SPEC["tools"]]}
        elif method == "tools/call":
            p = req.get("params", {})
            out = call(p.get("name"), p.get("arguments", {}), mode="mcp")
            res = {"content": [{"type": "text", "text": json.dumps(out, indent=1, sort_keys=True)}],
                   "isError": bool(isinstance(out, dict) and out.get("error"))}
        else:
            res = {}
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": rid, "result": res}) + "\n")
        sys.stdout.flush()


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "mcp":
        _mcp_loop()
        return 0
    if cmd == "list":
        srv = fam = None
        if "--server" in argv:
            srv = argv[argv.index("--server") + 1]
        if "--family" in argv:
            fam = argv[argv.index("--family") + 1]
        for t in SPEC["tools"]:
            if srv and t["server"] != srv:
                continue
            if fam and t["family"] != fam:
                continue
            print("%-48s %-28s %s" % (t["name"], t["family"], t["description"].split("\n")[0][:90]))
        return 0
    if cmd == "describe":
        print(json.dumps(TOOLS.get(argv[1], {"status": "not_found"}), indent=2))
        return 0
    if cmd == "call":
        args = json.loads(argv[2]) if len(argv) > 2 else {}
        print(json.dumps(call(argv[1], args), indent=1, sort_keys=True))
        return 0
    print("unknown mode: %s" % cmd, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

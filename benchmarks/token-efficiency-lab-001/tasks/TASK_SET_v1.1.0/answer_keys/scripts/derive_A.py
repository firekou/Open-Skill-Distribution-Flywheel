#!/usr/bin/env python3
"""Derive answer keys for workload A (A-001..A-004) of TASK_SET_v1.1.0.

Everything is computed from the Python AST of the corpus under
corpora/repo_ledgerline/ledgerline/ (tests/ excluded, per rule R3).  Using the
AST rather than text search is what makes rule R5 (comments / docstrings /
string literals are not code) true by construction.

Usage:  python3 derive_A.py [--write]
        --write  rewrites answer_keys/A-00{1,2,3,4}.json
        default: prints the derived payloads as JSON to stdout
"""
from __future__ import annotations

import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(KEYS_DIR)          # TASK_SET_v1.0.0
PKG = os.path.join(ROOT, "corpora", "repo_ledgerline", "ledgerline")


# --------------------------------------------------------------------------
# corpus loading
# --------------------------------------------------------------------------
def module_files():
    """Every .py file under ledgerline/, as (dotted_module_name, abspath)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(PKG):
        dirnames.sort()
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, os.path.dirname(PKG))
            parts = rel[:-3].split(os.sep)
            if parts[-1] == "__init__":
                parts = parts[:-1]
            out.append((".".join(parts), path))
    return sorted(out)


MODULES = module_files()
TREES = {}
for mod, path in MODULES:
    with open(path, "r", encoding="utf-8") as fh:
        TREES[mod] = ast.parse(fh.read(), filename=path)


# --------------------------------------------------------------------------
# module-level function definitions (rule R2)
# --------------------------------------------------------------------------
# fqn -> ast.FunctionDef ; short name -> fqn
FUNCS = {}
NAME_TO_FQN = {}
DUPLICATE_NAMES = {}

for mod, _ in MODULES:
    for node in TREES[mod].body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fqn = f"{mod}.{node.name}"
            FUNCS[fqn] = (mod, node)
            DUPLICATE_NAMES.setdefault(node.name, []).append(fqn)
for name, fqns in DUPLICATE_NAMES.items():
    NAME_TO_FQN[name] = fqns[0]

AMBIGUOUS = {n: f for n, f in DUPLICATE_NAMES.items() if len(f) > 1}


# --------------------------------------------------------------------------
# call edges (rule R4)
# --------------------------------------------------------------------------
def called_names(node):
    """Bare-name callees appearing anywhere in the body of `node`.

    Decorators are excluded: a decorator is not part of the function body.
    """
    names = []
    for stmt in node.body:
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                names.append(sub.func.id)
    return names


EDGES = {fqn: set() for fqn in FUNCS}
for fqn, (mod, node) in FUNCS.items():
    for cname in called_names(node):
        if cname in NAME_TO_FQN:
            EDGES[fqn].add(NAME_TO_FQN[cname])

REV = {fqn: set() for fqn in FUNCS}
for src, dsts in EDGES.items():
    for d in dsts:
        REV[d].add(src)


def closure(start, graph):
    seen, stack = set(), [start]
    while stack:
        cur = stack.pop()
        for nxt in graph[cur]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


# --------------------------------------------------------------------------
# A-001
# --------------------------------------------------------------------------
def a001():
    sink = "ledgerline.storage.raw.execute_raw_sql"
    assert sink in FUNCS, "sink not found in corpus"
    reaching = closure(sink, REV) - {sink}
    prefixes = ("ledgerline.api.", "ledgerline.plugins.", "ledgerline.cli.")
    sel = sorted(f for f in reaching if f.startswith(prefixes))
    return {"reaching_functions": sel, "count": len(sel)}


# --------------------------------------------------------------------------
# A-002
# --------------------------------------------------------------------------
def a002():
    # Every bare name used as a call-expression callee, anywhere under
    # ledgerline/ (module level included), excluding nothing -- a def line
    # never contains a call to itself, so no def-line exclusion is needed.
    called = set()
    imported = set()
    all_listed = set()
    # Names referenced in code but neither called nor imported (diagnostic).
    other_loads = {}

    for mod, _ in MODULES:
        tree = TREES[mod]
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called.add(node.func.id)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    imported.add(a.name.split(".")[-1])
                    if a.asname:
                        imported.add(a.asname)
            elif isinstance(node, ast.ImportFrom):
                for a in node.names:
                    imported.add(a.name)
                    if a.asname:
                        imported.add(a.asname)
            elif isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    all_listed.add(elt.value)

        # diagnostic: Name loads that are not callees / imports / def names
        callee_ids = {id(n.func) for n in ast.walk(tree)
                      if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if id(node) in callee_ids:
                    continue
                if node.id in DUPLICATE_NAMES:
                    other_loads.setdefault(node.id, []).append(f"{mod}:{node.lineno}")

    unreferenced = []
    for fqn, (mod, node) in FUNCS.items():
        n = node.name
        if n in called or n in imported or n in all_listed:
            continue
        unreferenced.append(fqn)
    unreferenced.sort()
    return {"unreferenced_functions": unreferenced, "count": len(unreferenced)}, other_loads


# --------------------------------------------------------------------------
# A-003
# --------------------------------------------------------------------------
def retryable_importers():
    """Modules that import `retryable` from ledgerline.util.retry."""
    mods = set()
    for mod, _ in MODULES:
        for node in ast.walk(TREES[mod]):
            if isinstance(node, ast.ImportFrom) and node.module == "ledgerline.util.retry":
                for a in node.names:
                    if a.name == "retryable" and a.asname is None:
                        mods.add(mod)
    return mods


def a003():
    good_mods = retryable_importers()

    retry_decorated = set()
    for fqn, (mod, node) in FUNCS.items():
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(target, ast.Name) and target.id == "retryable":
                assert mod in good_mods, f"{fqn}: @retryable without the util.retry import"
                retry_decorated.add(fqn)

    raisers = set()
    for fqn, (mod, node) in FUNCS.items():
        for stmt in node.body:
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Raise) and sub.exc is not None:
                    exc = sub.exc
                    target = exc.func if isinstance(exc, ast.Call) else exc
                    if isinstance(target, ast.Name) and target.id == "TransientError":
                        raisers.add(fqn)
    # D3: "a function is not held to reach a transient raiser merely by being
    # one itself" -- reachability needs at least one call edge.  The two
    # readings are computed and asserted equal, so the key can never depend on
    # which one is taken: no retry-decorated function in this corpus is itself
    # a transient raiser.
    strict = sorted(f for f in retry_decorated if closure(f, EDGES) & raisers)
    lenient = sorted(f for f in retry_decorated
                     if f in raisers or (closure(f, EDGES) & raisers))
    assert strict == lenient, sorted(set(lenient) - set(strict))
    result = strict
    return ({"retry_decorated_reaching_transient": result, "count": len(result)},
            sorted(retry_decorated), sorted(raisers))


# --------------------------------------------------------------------------
# A-004  (Tarjan SCC, iterative)
# --------------------------------------------------------------------------
def a004():
    index = {}
    low = {}
    on_stack = {}
    stack = []
    result = []
    counter = [0]

    for root in sorted(FUNCS):
        if root in index:
            continue
        work = [(root, iter(sorted(EDGES[root])))]
        index[root] = low[root] = counter[0]
        counter[0] += 1
        stack.append(root)
        on_stack[root] = True
        while work:
            node, it = work[-1]
            advanced = False
            for succ in it:
                if succ not in index:
                    index[succ] = low[succ] = counter[0]
                    counter[0] += 1
                    stack.append(succ)
                    on_stack[succ] = True
                    work.append((succ, iter(sorted(EDGES[succ]))))
                    advanced = True
                    break
                elif on_stack.get(succ):
                    low[node] = min(low[node], index[succ])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    comp.append(w)
                    if w == node:
                        break
                result.append(sorted(comp))

    comps = sorted((c for c in result if len(c) >= 2), key=lambda c: c[0])
    return {"components": comps, "component_count": len(comps)}


# --------------------------------------------------------------------------
def main():
    write = "--write" in sys.argv
    a2, other_loads = a002()
    a3, decorated, raisers = a003()
    payloads = {
        "A-001": a001(),
        "A-002": a2,
        "A-003": a3,
        "A-004": a004(),
    }

    diagnostics = {
        "module_level_function_count": len(FUNCS),
        "ambiguous_short_names": AMBIGUOUS,
        "retry_decorated_functions": decorated,
        "transient_raisers": raisers,
        "non_call_non_import_name_loads_of_function_names": other_loads,
    }

    keys = {
        "A-001": {
            "task_id": "A-001",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Parsed every .py file under corpora/repo_ledgerline/ledgerline/ with Python's "
                "ast module, collected module-level FunctionDefs, built call edges from bare-name "
                "Call callees inside function bodies (rules R2/R4/R5), then took the reverse "
                "transitive closure from ledgerline.storage.raw.execute_raw_sql and kept the "
                "members defined in ledgerline/api/, ledgerline/plugins/ or ledgerline/cli/. "
                "Script: scripts/derive_A.py"
            ),
            "derivation_script": "scripts/derive_A.py",
            **payloads["A-001"],
        },
        "A-002": {
            "task_id": "A-002",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "AST pass over ledgerline/ collecting (a) every bare name used as a Call callee, "
                "(b) every name bound by an import/from-import, (c) every string in an __all__ "
                "assignment; a module-level function is unreferenced when its name is in none of "
                "those three sets. Using the AST makes rule R5 true by construction and tests/ is "
                "never parsed (rule R3). Script: scripts/derive_A.py"
            ),
            "derivation_script": "scripts/derive_A.py",
            **payloads["A-002"],
        },
        "A-003": {
            "task_id": "A-003",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "AST pass: retry-decorated = module-level functions whose decorator_list contains "
                "Name 'retryable' or Call on Name 'retryable' (retryable_v2 excluded by exact name "
                "match); transient raisers = functions whose body contains an ast.Raise of "
                "TransientError (bare or called). Forward call-graph closure from each decorated "
                "function is intersected with the raiser set. Script: scripts/derive_A.py"
            ),
            "derivation_script": "scripts/derive_A.py",
            **payloads["A-003"],
        },
        "A-004": {
            "task_id": "A-004",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Tarjan strongly-connected components over the same AST-derived call graph, "
                "keeping components of size >= 2, each component sorted lexicographically and the "
                "outer list sorted by first element. Script: scripts/derive_A.py"
            ),
            "derivation_script": "scripts/derive_A.py",
            **payloads["A-004"],
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
        print(json.dumps({"keys": keys, "diagnostics": diagnostics},
                         indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

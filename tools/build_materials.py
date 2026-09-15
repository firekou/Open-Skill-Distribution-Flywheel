#!/usr/bin/env python3
"""Build registry/materials.json for Benchmark Run R2-001.

Conforms to registry/MATERIAL_SCHEMA.json v2.0 and scores with TREND_SCORING.md.

Scoring honesty rule
--------------------
technical_utility, atk_relevance and content_potential are ASSIGNED BY REVIEW
(tools/materials_data.py). momentum, experimentability and source_credibility are
DERIVED by the explicit rules below, so the long tail is not given fake precision.
Every derived value is reproducible from the snapshot metrics.

Per ARCHITECTURE_R2: licence is a FLAG, never a discovery veto.
"""
import importlib.util, json, pathlib, re
from datetime import date

RUN_ID = "R2-002"
SNAPSHOT = "2026-09-15"
ROOT = pathlib.Path(__file__).resolve().parent.parent

def _load(name):
    sp = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod
MD = _load("materials_data")
MS = _load("materials_sources")

# Organisations publishing as a named vendor / foundation / research lab.
VENDOR = {
 "google","google-gemini","microsoft","github","anthropics","bytedance","modelscope",
 "TencentCloudADP","trpc-group","strands-agents","mozilla-ai","deepset-ai","pydantic",
 "a2aproject","modelcontextprotocol","iflytek","Kong","ChromeDevTools","getsentry",
 "Azure-Samples","alibaba","googleworkspace","agentscope-ai","upstash","n8n-io",
 "brightdata","HKUDS","ag2ai","SolaceLabs","1Panel-dev","activepieces","triggerdotdev",
 "BerriAI","Portkey-AI","maximhq","katanemo","APIParkLab","langgenius","K-Dense-AI",
 "VoltAgent","ComposioHQ","nexu-io","crestalnetwork","rllm-org","EvoMap",
}

def months_since(iso):
    a = date.fromisoformat(iso); b = date.fromisoformat(SNAPSHOT)
    return max((b - a).days / 30.44, 0.5)

def derive_momentum(stars, created):
    """Momentum/freshness /20 from stars per month. Rule is fixed and public."""
    spm = stars / months_since(created)
    for cut, val in ((8000,20),(4000,18),(2000,16),(800,14),(300,12),(100,10),(40,8),(10,6)):
        if spm >= cut: return val, round(spm)
    return 4, round(spm)

def derive_experimentability(stars, forks, issues, category):
    """/10 - how cheaply can ATK actually run this in an afternoon?"""
    s = 7
    if category in ("token-optimization", "routing"): s += 2   # proxies/CLIs: drop-in
    if category in ("agent-framework",): s -= 1                # more setup
    if issues > 1200: s -= 3
    elif issues > 500: s -= 2
    elif issues < 60: s += 1
    if forks and issues / forks > 0.12: s -= 1
    return max(0, min(10, s))

def derive_credibility(repo, stars, forks, issues):
    """/10 - can ATK cite this without embarrassment?"""
    owner = repo.split("/")[0]
    s = 10 if owner in VENDOR else 7
    if stars >= 20000: s += 1
    if forks and issues / forks > 0.15: s -= 2      # backlog out of control
    if stars < 800: s -= 1
    return max(0, min(10, s))

def route(m):
    """Assign actions. Discovery/content never gated on licence (ARCHITECTURE_R2)."""
    sc, a = m["scores"], []
    lic_open = m["rights"]["license"] in ("MIT", "Apache-2.0", "Apache-2.0+MIT", "BSD-3-Clause")
    lic_known = m["rights"]["license"] != "?"
    a.append("research")
    if sc["content_potential"] >= 12: a.append("content")
    if sc["content_potential"] >= 13 and sc["technical_utility"] >= 18: a.append("tutorial")
    if sc["experimentability"] >= 8 and sc["technical_utility"] >= 17: a.append("experiment")
    if sc["atk_relevance"] >= 17 and lic_open: a.append("companion_adapter")
    if sc["atk_relevance"] >= 16 and lic_open and sc["material_score"] >= 78: a.append("fork_candidate")
    # deep_integration means touching code, so it is licence-gated exactly like adapters/forks.
    if sc["atk_relevance"] >= 18 and sc["material_score"] >= 80 and lic_open:
        a.append("deep_integration")
    if not lic_known or m["rights"]["redistribution_allowed"] is False: a.append("link_upstream")
    return a

def status(score, actions):
    if score >= 80: return "material_ready"
    if score >= 65: return "qualified"
    if score >= 50: return "signal"
    return "archived"

RIGHTS = {
 "MIT":            (True, True), "Apache-2.0": (True, True), "Apache-2.0+MIT": (True, True),
 "AGPL-3.0":       (True, False), "Elastic-2.0": (True, False), "BUSL-1.1": (False, False),
 "CC-BY-NC-ND-4.0":(False, False), "NONE": (False, False), "?": (None, None),
}

materials, seen = [], set()

def add(repo, stars, forks, issues, created, category, lic, tu, atk, cp, note, origin):
    if repo in seen: return
    seen.add(repo)
    mom, spm = derive_momentum(stars, created)
    exp = derive_experimentability(stars, forks, issues, category)
    cred = derive_credibility(repo, stars, forks, issues)
    total = tu + mom + atk + cp + exp + cred
    redis, comm = RIGHTS.get(lic, (None, None))
    m = {
      "id": re.sub(r"[^a-z0-9]+", "-", repo.split("/")[1].lower()).strip("-"),
      "title": repo,
      "source_url": f"https://github.com/{repo}",
      "source_type": "code_repository",
      "category": category,
      "summary": note,
      "problem_solved": note,
      "technical_value": note,
      "why_now": f"~{spm:,} stars/month since {created}; {issues:,} open issues at snapshot",
      "atk_relevance": None,
      "actions": [],
      "scores": {"technical_utility": tu, "momentum": mom, "atk_relevance": atk,
                 "content_potential": cp, "experimentability": exp,
                 "source_credibility": cred, "material_score": total},
      "rights": {"license": lic, "attribution": "required",
                 "redistribution_allowed": redis, "commercial_distribution_allowed": comm,
                 "notes": "Licence not resolved in this run; constrains redistribution only, not discovery."
                          if lic == "?" else "Verified against GitHub licence metadata."},
      "status": None,
      "_metrics": {"stars": stars, "forks": forks, "open_issues": issues,
                   "created_at": created, "stars_per_month": spm, "snapshot_at": SNAPSHOT},
      "_origin": origin,
    }
    m["actions"] = route(m)
    m["status"] = status(total, m["actions"])
    m["atk_relevance"] = (f"ATK relevance {atk}/20. " +
        ("Direct routing/token-cost surface." if atk >= 17 else
         "Adjacent - useful as content or experiment." if atk >= 13 else
         "Reference material; no direct ATK insertion point."))
    materials.append(m)

for bucket in (MD.TOKEN_OPT, MD.A2A, MD.FRAMEWORK, MD.MCP, MD.ROUTING):
    for row in bucket:
        add(*row, origin="benchmark-R2-001")

# Carry forward the R1 sweep so agent-skill and routing meet their 20-per-category floor.
R1 = json.loads((ROOT / "registry" / "skill_registry.json").read_text(encoding="utf-8"))
CATMAP = {"agent-skills":"agent-skill","developer-skills":"agent-skill","media-skills":"agent-skill",
          "enterprise-skills":"agent-skill","automation-skills":"agent-skill","research":"agent-skill",
          "discovery":"agent-skill","standard":"agent-skill","agent-infrastructure":"agent-framework",
          "routing":"routing","mcp":"mcp"}
for c in R1["candidates"]:
    s, mt = c["score"], c["metrics"]
    lic = c["license"]["spdx"] or "?"
    if lic == "NOASSERTION": lic = "?"
    lic = {"Apache-2.0 AND MIT AND CC-BY-4.0":"Apache-2.0+MIT",
           "AGPL-3.0 AND LicenseRef-Commercial":"AGPL-3.0"}.get(lic, lic)
    add(c["repository"], mt["stars"], mt["forks"], mt["open_issues"], mt["created_at"],
        CATMAP.get(c["category"], c["category"]), lic,
        s["utility"], s["atk_fit"], s["distribution"], c["use_case"], origin="sweep-R1")

def add_source(sid, title, url, stype, category, published, verified,
               tu, mom, atk, cp, exp, cred, note):
    if sid in seen: return
    seen.add(sid)
    total = tu + mom + atk + cp + exp + cred
    m = {
      "id": sid, "title": title, "source_url": url, "source_type": stype,
      "category": category, "summary": note, "problem_solved": note,
      "technical_value": note, "why_now": f"published {published}",
      "atk_relevance": None, "actions": [],
      "scores": {"technical_utility": tu, "momentum": mom, "atk_relevance": atk,
                 "content_potential": cp, "experimentability": exp,
                 "source_credibility": cred, "material_score": total},
      "rights": {"license": "n/a-editorial", "attribution": "required",
                 "redistribution_allowed": False, "commercial_distribution_allowed": False,
                 "notes": "Third-party writing or research. Cite and link; never reproduce at length."},
      "status": None,
      "_metrics": {"published": published, "snapshot_at": SNAPSHOT},
      "_verification": verified,
      "_origin": "benchmark-R2-002",
    }
    # Editorial/research material is never a code action - it is read, cited and tested.
    a = ["research", "link_upstream"]
    if cp >= 12: a.append("content")
    if cp >= 13 and tu >= 20: a.append("tutorial")
    if exp >= 7 and tu >= 20: a.append("experiment")
    m["actions"] = a
    m["status"] = status(total, a)
    m["atk_relevance"] = (f"ATK relevance {atk}/20. " +
        ("Directly informs ATK routing or token strategy." if atk >= 17 else
         "Useful background or content input." if atk >= 13 else "Reference only."))
    materials.append(m)

for row in MS.SOURCES:
    add_source(*row)

materials.sort(key=lambda m: (-m["scores"]["material_score"], -m["scores"]["atk_relevance"]))

cats = {}
for m in materials: cats[m["category"]] = cats.get(m["category"], 0) + 1

out = {
  "schema": "registry/MATERIAL_SCHEMA.json v2.0",
  "run_id": RUN_ID,
  "generated_at": SNAPSHOT,
  "scoring_model": "TREND_SCORING.md",
  "method_note": ("technical_utility, atk_relevance and content_potential are assigned by "
                  "review. momentum, experimentability and source_credibility are derived by "
                  "fixed public rules in tools/build_materials.py from snapshot metrics."),
  "license_policy": ("Licence is a flag, not a discovery veto (ARCHITECTURE_R2). "
                     "'?' means unresolved in this run and constrains redistribution only."),
  "counts": {"total": len(materials), "by_category": cats,
             "by_source_type": {t: sum(1 for m in materials if m["source_type"] == t)
                                for t in sorted({m["source_type"] for m in materials})},
             "non_repo": sum(1 for m in materials if m["source_type"] != "code_repository"),
             "verified_primary": sum(1 for m in materials if m.get("_verification") == "primary"),
             "search_summary_only": sum(1 for m in materials if m.get("_verification") == "search"),
             "priority_a": sum(1 for m in materials if m["scores"]["material_score"] >= 80),
             "priority_b": sum(1 for m in materials if 65 <= m["scores"]["material_score"] < 80),
             "watch": sum(1 for m in materials if 50 <= m["scores"]["material_score"] < 65),
             "license_unresolved": sum(1 for m in materials if m["rights"]["license"] == "?")},
  "materials": materials,
}
(ROOT / "registry" / "materials.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"materials: {len(materials)}")
print("by category:", json.dumps(cats, ensure_ascii=False))
print("A/B/watch:", out["counts"]["priority_a"], out["counts"]["priority_b"], out["counts"]["watch"])
print("licence unresolved:", out["counts"]["license_unresolved"])

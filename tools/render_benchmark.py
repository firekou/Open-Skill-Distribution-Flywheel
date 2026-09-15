#!/usr/bin/env python3
"""Render reports/BENCHMARK_R2_001.md - the four ranked lists the runbook asks for."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "registry" / "materials.json").read_text(encoding="utf-8"))
M, C = D["materials"], D["counts"]
L = []; w = L.append

def row(m, extra=None):
    s, mt = m["scores"], m["_metrics"]
    lic = m["rights"]["license"]
    lic = "unresolved" if lic == "?" else lic
    e = f" | {extra}" if extra else ""
    return (f"| [`{m['title']}`]({m['source_url']}) | {mt['stars']:,} | {mt['stars_per_month']:,} | "
            f"{lic} | **{s['material_score']}**{e} |")

w("# Benchmark Run R2-001 — First Discovery Sweep")
w("")
w(f"> Run ID `{D['run_id']}` · Snapshot **{D['generated_at']}** · Scoring: `TREND_SCORING.md`")
w("> Runbook: `DISCOVERY_PIPELINE.md` · Architecture: `ARCHITECTURE_R2.md`")
w("> **No repository was forked during this run**, as the runbook requires.")
w("")
w("---")
w("")
w("## Phase 0 — Permission Preflight")
w("")
w("Recorded before mining, per the runbook. A missing permission is a limit on *this executor*, "
  "never a negative finding about a candidate.")
w("")
w("| Capability | Status | Effect on this run |")
w("|---|---|---|")
w("| GitHub repository search (MCP tool) | ✅ Available | Primary mining path |")
w("| GitHub search REST API (direct) | ❌ Blocked by proxy | Had to route all search through the MCP tool |")
w("| `raw.githubusercontent.com` file reads | ✅ Available | **Licence texts and READMEs readable for any public repo** |")
w("| GitHub contents API for external repos | ❌ 403 | Cannot enumerate trees; single-file reads via raw only |")
w("| Repository settings writes | ❌ Blocked by policy | Unrelated to discovery |")
w("| Web search (WebSearch / Exa) | ✅ Available | Not needed this run — GitHub yielded enough breadth |")
w("")
w("**Consequence:** every item here is sourced from primary code repositories. Hacker News, "
  "Reddit, X, YouTube and Hugging Face — source classes 3–5 in `DISCOVERY_ENGINE.md` — were "
  "**not mined in this run**. Source diversity is therefore the weakest metric of R2-001 and "
  "the first thing to fix in R2-002.")
w("")
w("---")
w("")
w("## Result")
w("")
w("| | Target | Actual |")
w("|---|---|---|")
w(f"| Raw candidates | 120 | **{C['total']}** |")
for cat, n in sorted(C["by_category"].items(), key=lambda x: -x[1]):
    flag = "✅" if n >= 20 else "⚠️"
    w(f"| — {cat} | 20 | {n} {flag} |")
w(f"| Priority A (≥80) | — | {C['priority_a']} |")
w(f"| Priority B (65–79) | — | {C['priority_b']} |")
w(f"| Watch (50–64) | — | {C['watch']} |")
w(f"| Licence unresolved | — | {C['license_unresolved']} ({round(C['license_unresolved']/C['total']*100)}%) |")
w("")
w("> **Licence is a flag, not a gate.** Per `ARCHITECTURE_R2.md`, an unresolved licence "
  f"constrains redistribution only. All {C['license_unresolved']} unresolved items remain "
  "valid research and content material.")
w("")
w("### Scoring honesty")
w("")
w("`technical_utility`, `atk_relevance` and `content_potential` were **assigned by review**. "
  "`momentum`, `experimentability` and `source_credibility` are **derived by fixed public "
  "rules** in `tools/build_materials.py` from snapshot metrics. The split is deliberate: "
  "hand-scoring 164 items on six axes would have produced numbers with more precision than "
  "judgement behind them. Every derived value is reproducible from the registry.")
w("")
w("---")
w("")

# ── LIST 1 ────────────────────────────────────────────────────────────────
w("## 1. What should ATK talk about?")
w("")
w("Ranked by content potential, then momentum. These are content assets first — several are "
  "not forkable and do not need to be.")
w("")
talk = sorted([m for m in M if "content" in m["actions"]],
              key=lambda m: (-m["scores"]["content_potential"], -m["scores"]["momentum"],
                             -m["scores"]["material_score"]))[:20]
w("| Material | Stars | ★/mo | Licence | Score | Content angle |")
w("|---|--:|--:|---|--:|---|")
for m in talk:
    s, mt = m["scores"], m["_metrics"]
    lic = "unresolved" if m["rights"]["license"] == "?" else m["rights"]["license"]
    angle = m["summary"].split(".")[0][:95]
    w(f"| [`{m['title']}`]({m['source_url']}) | {mt['stars']:,} | {mt['stars_per_month']:,} | "
      f"{lic} | **{s['material_score']}** | {angle} |")
w("")
w("**The story this list is telling.** The single strongest content theme in the whole sweep "
  "is **token cost**. `rtk-ai/rtk` (80k stars, 60–90% token reduction) and "
  "`headroomlabs-ai/headroom` (72k stars) were both created in January 2026 and both crossed "
  "70k stars inside eight months. Neither appeared in the R1 sweep at all, because R1 searched "
  "for things to fork rather than things to understand. That gap is the clearest argument for "
  "the R2 architecture.")
w("")

# ── LIST 2 ────────────────────────────────────────────────────────────────
w("## 2. What should ATK test?")
w("")
w("Ranked by how cheaply it can be stood up, then by how much ATK learns from the result. "
  "Everything here produces a number ATK can publish.")
w("")
# "What should ATK test" ranks on how cheap it is to run AND how much ATK learns from it,
# so ATK relevance is the second key - not raw utility.
test = sorted([m for m in M if "experiment" in m["actions"]],
              key=lambda m: (-m["scores"]["experimentability"], -m["scores"]["atk_relevance"],
                             -m["scores"]["technical_utility"]))[:15]
w("| Material | Category | Exp /10 | ATK fit | Score | What the test would measure |")
w("|---|---|--:|--:|--:|---|")
for m in test:
    s = m["scores"]
    w(f"| [`{m['title']}`]({m['source_url']}) | {m['category']} | {s['experimentability']} | "
      f"{s['atk_relevance']} | **{s['material_score']}** | {m['summary'].split('.')[0][:78]} |")
w("")
w("**Run this one first, even though it is not top of the table.** "
  "[`toby-bridges/api-relay-audit`](https://github.com/toby-bridges/api-relay-audit) "
  "(836★, experimentability 9, ATK fit 19) sits just below the cut because fifteen items "
  "scored a perfect 10 on ease of setup. It is still the single highest-value experiment "
  "available, and the ranking simply does not capture why: it is a security auditor for LLM "
  "proxies — prompt injection, model substitution, tool-call rewriting, SSE anomalies, error "
  "leakage. **ATK operates an LLM proxy.**")
w("")
w("Running it against ATK's own routing is a real security exercise, and publishing the result "
  "is the kind of trust signal a cost claim can never buy. Nothing else in this sweep doubles "
  "as self-audit and content. Treat the table as the cheap-and-useful list, and this as the "
  "one that matters most.")
w("")

# ── LIST 3 ────────────────────────────────────────────────────────────────
w("## 3. What is suitable for ATK integration?")
w("")
w("Ranked by ATK relevance. Integration here means a **companion adapter or deep integration** "
  "— not a fork. Licence constrains this list, so it is shown.")
w("")
integ = sorted([m for m in M if {"companion_adapter","deep_integration"} & set(m["actions"])],
               key=lambda m: (-m["scores"]["atk_relevance"], -m["scores"]["material_score"]))[:15]
w("| Material | ATK fit /20 | Licence | Score | Integration shape |")
w("|---|--:|---|--:|---|")
for m in integ:
    s = m["scores"]
    w(f"| [`{m['title']}`]({m['source_url']}) | {s['atk_relevance']} | {m['rights']['license']} | "
      f"**{s['material_score']}** | {m['summary'].split('.')[0][:78]} |")
w("")
w("A second tier scores just as high on ATK relevance but has an **unresolved licence**, so it "
  "can be researched and tested but not yet adapted:")
w("")
blocked_int = sorted([m for m in M if m["rights"]["license"] == "?" and m["scores"]["atk_relevance"] >= 18],
                     key=lambda m: -m["scores"]["material_score"])[:8]
w("| Material | ATK fit /20 | Score | Why it matters |")
w("|---|--:|--:|---|")
for m in blocked_int:
    w(f"| [`{m['title']}`]({m['source_url']}) | {m['scores']['atk_relevance']} | "
      f"**{m['scores']['material_score']}** | {m['summary'].split('.')[0][:78]} |")
w("")

# ── LIST 4 ────────────────────────────────────────────────────────────────
w("## 4. What is suitable for fork / redistribution?")
w("")
w("The **only** list where the full `LICENSE_REVIEW.md` + `FORK_POLICY.md` gate applies. "
  "Everything here has a verified permissive licence. **Nothing was forked.**")
w("")
fork = sorted([m for m in M if "fork_candidate" in m["actions"]],
              key=lambda m: (-m["scores"]["atk_relevance"], -m["scores"]["material_score"]))[:15]
w("| Material | Licence | ATK fit | Score | Note |")
w("|---|---|--:|--:|---|")
for m in fork:
    s = m["scores"]
    w(f"| [`{m['title']}`]({m['source_url']}) | {m['rights']['license']} | {s['atk_relevance']} | "
      f"**{s['material_score']}** | {m['summary'].split('.')[0][:75]} |")
w("")
w("This list is deliberately the shortest of the four. Under R1 every candidate was judged as "
  "a fork target and most failed. Under R2 the same projects are useful in three other lanes, "
  "and forking is what is left over after the cheaper options are exhausted — which is the "
  "correct order.")
w("")
w("---")
w("")
w("## What the benchmark actually proved")
w("")
w("**The mine is real.** 164 qualified materials from one run against a 120 target, with all "
  "six required categories above floor, and **38 scoring Priority A**. The R1 architecture "
  "produced 68 candidates of which 21 were Priority A and only 4 were actionable, because "
  "every item had to survive a fork gate before it counted as anything.")
w("")
w("**Three findings worth acting on:**")
w("")
w("1. **R1 had a blind spot the size of the category.** Token optimisation is the fastest-"
  "growing space in the sweep and R1 found two items in it. R2 found 21, including two "
  "projects above 70k stars. Searching for fork targets systematically missed the thing ATK "
  "most needs to talk about.")
w("")
w("2. **The market is competing on cost, hard.** Of the routing and token materials, a large "
  "share sell on price — free aggregation (`OmniRoute`, `openrelay`, `9router`), subscription "
  "arbitrage (`dario`), or raw reduction (`rtk`, `headroom`, `snip`, `lowfat`). ATK cannot "
  "differentiate on price against free. The defensible position visible in this data is "
  "**measurement and trust**: cost attribution, drift tracking, auditability — which is "
  "exactly where `claude-tap`, `api-relay-audit`, `RelayPlane/proxy` and `tokentab` sit, and "
  "they are all small.")
w("")
w("3. **Licence resolution is now the bottleneck, not discovery.** "
  f"{C['license_unresolved']} of {C['total']} materials have an unresolved licence. That "
  "blocks nothing in lanes A and B — but it does mean list 4 is much shorter than it should "
  "be. Resolving licences for the top 20 ATK-relevant items is a ~20-minute job with the "
  "`raw.githubusercontent.com` access this run confirmed works.")
w("")
w("## Honest limits of this run")
w("")
w("- **Source diversity is poor.** GitHub only. No Hacker News, Reddit, X, YouTube or Hugging "
  "Face. Four of six source classes in `DISCOVERY_ENGINE.md` went unmined.")
w("- **Nothing was executed.** Phase 4 \"read primary documentation/code\" was done from "
  "repository metadata and descriptions, not from running anything. Every claim a project "
  "makes about its own savings (`rtk` 60–90%, `headroom` 60–95%, `NadirClaw` 40–70%) is "
  "**unverified vendor copy** and must not be repeated by ATK until list 2 is executed.")
w("- **Scores are a first pass.** They rank sensibly against each other; they are not "
  "calibrated against outcomes, because there are no outcomes yet.")
w("")
w("## Next run (R2-002)")
w("")
w("1. Mine the four unmined source classes — that is where the diversity metric improves")
w("2. Resolve licences for the top 20 ATK-relevant materials via raw file reads")
w("3. Execute the top 3 experiments from list 2 and record **measured** numbers")
w("4. Run `api-relay-audit` against ATK's own routing")

(ROOT / "reports" / "BENCHMARK_R2_001.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote reports/BENCHMARK_R2_001.md")
print(f"lists: talk={len(talk)} test={len(test)} integrate={len(integ)} fork={len(fork)}")

#!/usr/bin/env python3
"""Render reports/BENCHMARK_R2_002.md - the four-source-class expansion run."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "registry" / "materials.json").read_text(encoding="utf-8"))
M, C = D["materials"], D["counts"]
NEW = [m for m in M if m["_origin"] == "benchmark-R2-002"]
L = []; w = L.append

def clip(t, n):
    """Truncate on a word boundary so numbers and names are never cut mid-token."""
    t = t.strip().rstrip(".")
    if len(t) <= n: return t
    cut = t[:n]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > n * 0.6 else cut).rstrip(",;:-") + "…"

def name(m):
    """Repos read as code paths; editorial items read as prose titles."""
    return (f"`{m['title']}`" if m["source_type"] == "code_repository"
            else clip(m["title"], 58))

def gist(m, n=64):
    return clip(m["summary"].split(". ")[0], n)

def lic(m):
    l = m["rights"]["license"]
    return "unresolved" if l == "?" else l

w("# Benchmark Run R2-002 — Mining the Four Unmined Source Classes")
w("")
w(f"> Run ID `{D['run_id']}` · Snapshot **{D['generated_at']}** · Scoring: `TREND_SCORING.md`")
w("> Fixes the weakest metric of R2-001: source diversity. **No repository was forked.**")
w("")
w("---")
w("")
w("## What changed")
w("")
w("R2-001 mined GitHub only — four of the six `DISCOVERY_ENGINE.md` source classes went "
  f"untouched. This run adds **{len(NEW)} non-repository materials** across all four.")
w("")
w("| Source class | R2-001 | R2-002 |")
w("|---|---|---|")
w("| 1. Primary code (GitHub) | ✅ 164 | ✅ 164 |")
w("| 2. Protocol / registry | ✅ via GitHub | ✅ via GitHub |")
w("| 3. Model/platform engineering | ❌ none | ✅ Anthropic, Cloudflare, Vercel, OpenAI, DeepSeek |")
w("| 4. Research / model hubs | ❌ none | ✅ 6 arXiv papers, Hugging Face router + LCLM |")
w("| 5. Community signal | ❌ none | ✅ Hacker News, developer community, YouTube |")
w("| 6. Curated discovery | ⚠️ partial | ✅ 3 curated indexes incl. an automated HF feed |")
w("")
w(f"**Registry total: {C['total']} materials** "
  f"({C['total'] - C['non_repo']} repositories + {C['non_repo']} non-repository). "
  f"{C['priority_a']} Priority A.")
w("")
w("| Source type | Count |")
w("|---|--:|")
for t, n in sorted(C["by_source_type"].items(), key=lambda x: -x[1]):
    w(f"| {t} | {n} |")
w("")
w("### Verification status — read this before quoting anything")
w("")
w(f"Of the {len(NEW)} new materials, **{C['verified_primary']} were retrieved from the primary "
  f"source** and **{C['search_summary_only']} come from search-engine summaries only**.")
w("")
w("Every item carries a `_verification` field. `\"search\"` means the underlying claim is **not "
  "independently confirmed**. Several of the most quotable numbers in this run are in that "
  "category — the ~100× price gap, the 40–85% routing savings, the 2.37M YouTube view count. "
  "They are useful as hypotheses to test. **They are not facts ATK may publish.**")
w("")
w("---")
w("")
w("## The finding that matters most")
w("")
w("### The routing layer is being commoditised by platform companies, not by open source")
w("")
w("R2-001 flagged small free-aggregation projects as ATK's price competition. That read was "
  "**too small**. The real pressure is this:")
w("")
w("| Who | What they give away |")
w("|---|---|")
w("| **Cloudflare AI Gateway** | Managed AI routing and observability proxy, **free on every Cloudflare plan** — analytics, caching and rate limiting at no charge. 24 native providers. A universal REST endpoint added May 2026 speaks both OpenAI and Anthropic request formats. |")
w("| **Cloudflare Agents Week (Aug 2026)** | 20+ launches in two weeks: agent wallet and verifiable identity, Identity-Aware AI Gateway, persistent Agent Memory, DeepSeek models with ~1M-token context on Workers AI. |")
w("| **Cloudflare + OpenAI Agent Cloud (Apr 2026)** | Enterprise agent runtime with GPT-5.4 and Codex in a unified model catalogue. |")
w("| **Vercel AI Gateway** | Hundreds of models across ~45 providers, one key, **BYOK with no markup**. |")
w("")
w("A dozen small OSS aggregators are a nuisance. Two platform companies with default "
  "distribution into millions of developer projects, giving the same layer away as a feature "
  "of something else, is a different problem entirely. **ATK cannot win on price or on "
  "provider count.** Both are already zero-cost commodities from vendors with better reach.")
w("")
w("### Where the gap actually is")
w("")
w("The same sources name what these gateways do *not* do. Vercel's is described as having **no "
  "guardrails and no semantic cache**. Cloudflare's is a proxy with analytics, not a "
  "cost-attribution or audit system.")
w("")
w("And the research independently points at the same opening. "
  "[*Model Routing as a Trust Problem: Route Receipts for Adaptive AI Systems*]"
  "(https://arxiv.org/pdf/2605.01710) (arXiv 2605.01710, May 2026) frames routing as a **trust** "
  "problem and proposes verifiable route receipts — a cryptographic record of which model "
  "actually served a request and why.")
w("")
w("That is the same conclusion R2-001 reached from repository data, now supported from two "
  "independent directions. **Measurement, attribution and auditability is the position price "
  "competition cannot erase** — because a free gateway has no incentive to prove what it did "
  "with your request, and a paid one does.")
w("")
w("The projects sitting in that gap are all still small: `claude-tap` (3.2k★), "
  "`api-relay-audit` (836★), `RelayPlane/proxy` (202★), `tokentab` (1.1k★). That is either an "
  "opportunity or a warning that the market does not value it yet. R2-003 should find out which.")
w("")
w("---")
w("")
w("## Best primary-source technique found")
w("")
w("[**Code execution with MCP: building more efficient AI agents**]"
  "(https://www.anthropic.com/engineering/code-execution-with-mcp) — Anthropic engineering, "
  "Nov 2025. Retrieved from the primary source.")
w("")
w("The argument: agents connected to many MCP servers pay twice. Every tool definition is "
  "loaded into context upfront, and every intermediate tool result passes through the model. "
  "Anthropic's example puts a 2-hour meeting transcript at ~50,000 extra tokens from "
  "intermediate results alone. Having the agent **write code that calls tools**, instead of "
  "calling each tool directly, removes both costs.")
w("")
w("This is the most actionable thing in the run: it is a technique, not a product, so ATK can "
  "test it, measure it, teach it and build routing around it without any licence question at "
  "all. Anthropic's context-engineering cookbook (Mar 2026) is runnable and covers memory, "
  "compaction and tool clearing — a ready-made experiment.")
w("")
w("---")
w("")

def table(title, intro, rows, cols, fmt):
    w(f"## {title}"); w(""); w(intro); w("")
    w("| " + " | ".join(cols) + " |")
    w("|" + "|".join("---" if not c.startswith("_") else "--:" for c in cols) + "|")
    for m in rows: w(fmt(m))
    w("")

talk = sorted([m for m in M if "content" in m["actions"]],
              key=lambda m: (-m["scores"]["content_potential"], -m["scores"]["momentum"]))[:15]
table("1. What should ATK talk about?",
      "Refreshed across all 188 materials. Non-repository items now rank here too — a technique "
      "or a market fact is often better content than a tool.",
      talk, ["Material","Type","_★/mo or date","Score","Angle"],
      lambda m: (f"| [{name(m)}]({m['source_url']}) | {m['source_type'].replace('_',' ')} | "
                 f"{m['_metrics'].get('stars_per_month', m['_metrics'].get('published','—'))} | "
                 f"**{m['scores']['material_score']}** | {gist(m, 70)} |"))

test = sorted([m for m in M if "experiment" in m["actions"]],
              key=lambda m: (-m["scores"]["experimentability"], -m["scores"]["atk_relevance"]))[:12]
table("2. What should ATK test?",
      "Cheap to stand up, and produces a number ATK can publish once measured.",
      test, ["Material","Category","_Exp","_ATK","Score","What it measures"],
      lambda m: (f"| [{name(m)}]({m['source_url']}) | {m['category']} | "
                 f"{m['scores']['experimentability']} | {m['scores']['atk_relevance']} | "
                 f"**{m['scores']['material_score']}** | {gist(m)} |"))

integ = sorted([m for m in M if {"companion_adapter","deep_integration"} & set(m["actions"])],
               key=lambda m: (-m["scores"]["atk_relevance"], -m["scores"]["material_score"]))[:12]
table("3. What is suitable for ATK integration?",
      "Companion adapter or deep integration — not a fork. Licence-gated, so licence is shown.",
      integ, ["Material","_ATK fit","Licence","Score","Shape"],
      lambda m: (f"| [{name(m)}]({m['source_url']}) | {m['scores']['atk_relevance']} | "
                 f"{lic(m)} | **{m['scores']['material_score']}** | {gist(m)} |"))

fork = sorted([m for m in M if "fork_candidate" in m["actions"]],
              key=lambda m: (-m["scores"]["atk_relevance"], -m["scores"]["material_score"]))[:12]
table("4. What is suitable for fork / redistribution?",
      "The only list where the full `LICENSE_REVIEW.md` + `FORK_POLICY.md` gate applies. "
      "Verified permissive licences only. **Nothing was forked.**",
      fork, ["Material","Licence","_ATK fit","Score","Note"],
      lambda m: (f"| [{name(m)}]({m['source_url']}) | {lic(m)} | {m['scores']['atk_relevance']} | "
                 f"**{m['scores']['material_score']}** | {gist(m, 58)} |"))

w("---")
w("")
w("## New discovery inputs worth automating")
w("")
w("| Index | Why |")
w("|---|---|")
w("| [`agents-radar`](https://github.com/duanyytop/agents-radar) | Bot-maintained repos that post Hugging Face trending models as dated GitHub issues. **Already an automated feed** — the Discovery Engine can consume it directly instead of scraping Hugging Face. |")
w("| [`awesome-llm-token-optimization`](https://github.com/pleasedodisturb/awesome-llm-token-optimization) | Curated token-cost strategies, tools and papers. |")
w("| [`Awesome-Routing-LLMs`](https://github.com/MilkThink-Lab/Awesome-Routing-LLMs) | Curated index of the routing research paradigm. |")
w("")
w("Wiring these three into the Monday scout replaces most of the manual searching this run "
  "required.")
w("")
w("## Honest limits")
w("")
w(f"- **{C['search_summary_only']} of {len(NEW)} new materials are search-summary only.** Their "
  "claims are unconfirmed. The cheapest fix is fetching the primary pages directly — "
  "`raw.githubusercontent.com` and normal HTTPS both work from this environment.")
w("- **Still nothing executed.** No experiment from list 2 has been run, so every savings "
  "figure in this registry — vendor or community — remains unverified.")
w("- **X and Reddit were reached only through secondary write-ups**, not their own surfaces. "
  "Same for YouTube: view counts come from an aggregator page, not from YouTube.")
w("- **Pricing was the load-bearing assumption and has since been verified.** The ~100× gap "
  "quoted in this run was corrected on 2026-09-15 from primary vendor pricing pages: "
  "like-for-like it is **11.4×**. See `PRICING_SNAPSHOT_2026-09-15.md` and Evidence Ledger "
  "E007/E015.")
w("")
w("## R2-003")
w("")
w("1. ~~Confirm the price gap from provider pricing pages~~ — **done 2026-09-15, corrected to 11.4×**")
w("2. Run the Anthropic context-engineering cookbook and record measured token deltas")
w("3. Run `api-relay-audit` against ATK's own routing")
w("4. Stand up Cloudflare AI Gateway and Vercel AI Gateway and document, concretely, what ATK "
  "does that they do not")
w("5. Wire the three curated indexes into the weekly scout")

(ROOT / "reports" / "BENCHMARK_R2_002.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote reports/BENCHMARK_R2_002.md")

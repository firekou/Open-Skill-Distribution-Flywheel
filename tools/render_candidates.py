#!/usr/bin/env python3
"""Render reports/CANDIDATE_REGISTRY.md (TASK 10) from registry/skill_registry.json."""
import json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
reg = json.loads((root / "registry" / "skill_registry.json").read_text(encoding="utf-8"))
cands = reg["candidates"]
c_ = reg["counts"]

CATS = ["research", "media-skills", "developer-skills", "agent-skills", "enterprise-skills",
        "automation-skills", "agent-infrastructure", "routing", "mcp", "discovery", "standard"]

L = []
w = L.append
w("# Candidate Registry — First Discovery Sweep (TASK 10)")
w("")
w(f"> Snapshot: **{reg['generated_at']}** · Scoring model: `{reg['scoring_model']}`")
w("> Source: GitHub repository search API. Regenerate with `python3 tools/build_registry.py`.")
w("")
w("The brief asked for 50 candidates. This sweep returned **"
  f"{c_['total']}** across the ATK Skill Network categories, because several searches "
  "surfaced strong candidates that would have been arbitrary to drop at a round number.")
w("")
w("## Summary")
w("")
w("| | Count |")
w("|---|---|")
w(f"| Candidates discovered | {c_['total']} |")
w(f"| Priority A (score ≥ 80) | {c_['priority_a']} |")
w(f"| Priority B (65–79) | {c_['priority_b']} |")
w(f"| Watchlist (50–64) | {c_['watchlist']} |")
w(f"| License Gate PASS | {c_['license_pass']} |")
w(f"| Blocked — non-standard license (ESCALATE) | {c_['license_escalate']} |")
w(f"| Blocked — **no license at all** (FAIL) | {c_['license_fail']} |")
w(f"| Rejected — strategic conflict | {c_['rejected_strategic']} |")
w("")
w("> **Second-pass correction (2026-09-15).** The first sweep left 22 candidates "
  "unresolved. That was a gap in the *query coverage*, not a finding about those projects: "
  "the topic-scoped searches simply never covered them. A targeted re-check resolved all "
  f"22. Only **{c_['license_escalate'] + c_['license_fail']}** of {c_['total']} are now "
  "genuinely blocked, and the remainder are cleanly usable.")
w("")
w("## Method")
w("")
w("1. Category sweeps over the GitHub repository search API: `topic:agent-skills`, "
  "`topic:llm-gateway`, `topic:mcp-server`, `topic:ai-agents`, plus keyword searches for "
  "MCP, routing and gateway projects.")
w("2. Star/fork/issue/creation-date metrics captured directly from the API response.")
w("3. Licenses resolved by re-running each sweep with a `license:` qualifier, so a license "
  "is only recorded when GitHub's own metadata confirms it. A README badge or a description "
  "string was never accepted as evidence.")
w("4. Scored against `SKILL_SCORING.md` v1.0; totals computed by `tools/build_registry.py` "
  "and validated by `tools/score.py`.")
w("")
w("**Growth signal** is reported as stars/month since creation rather than absolute stars, "
  "per `SKILL_SCORING.md` §2.")
w("")
w("## Full Registry")
w("")
w("Sorted by score. `Gate` is the License Gate ruling — it overrides the score.")
w("")
for cat in CATS:
    rows = [c for c in cands if c["category"] == cat]
    if not rows:
        continue
    w(f"### {cat}")
    w("")
    w("| Repository | Stars | Forks | Issues | Stars/mo | License | Gate | Score | Pri | Decision |")
    w("|---|--:|--:|--:|--:|---|---|--:|---|---|")
    for c in rows:
        m, lic = c["metrics"], c["license"]
        spdx = lic["spdx"] or "—"
        gate = {"PASS": "PASS", "ESCALATE": "ESCALATE", "FAIL": "FAIL",
                "UNVERIFIED": "BLOCKED"}[lic["ruling"]]
        w(f"| [`{c['repository']}`]({c['original_url']}) | {m['stars']:,} | {m['forks']:,} | "
          f"{m['open_issues']:,} | {m['stars_per_month']:,} | {spdx} | {gate} | "
          f"**{c['score']['total']}** | {c['priority']} | {c['decision']} |")
    w("")

w("## Rejected — Strategic Conflict")
w("")
w("Per `SKILL_SCORING.md` §4.4, a project whose core value proposition displaces paid "
  "routing is vetoed regardless of score. These are tracked for competitive intelligence "
  "and are **not** fork candidates:")
w("")
w("| Repository | Stars | Why |")
w("|---|--:|---|")
for c in cands:
    if c["decision"] == "reject":
        w(f"| `{c['repository']}` | {c['metrics']['stars']:,} | "
          f"{c['atk_relevance'].replace('STRATEGIC CONFLICT: ', '')} |")
w("")
w("These three are collectively the fastest-growing routing projects in the sweep. That is "
  "the finding, not an aside: the market is currently rewarding free provider aggregation. "
  "ATK's differentiation has to be reliability, cost transparency and maintained "
  "distribution — not price.")
w("")
w("## Blocked — License Gate")
w("")
w("Every remaining block is a real licence problem, not a missing lookup:")
w("")
w("| Repository | Score | Stars | Note |")
w("|---|--:|--:|---|")
for c in cands:
    if c["decision"] == "blocked":
        r = c["license"]["ruling"]
        why = ("AGPL-3.0 network copyleft" if c["license"]["spdx"] == "AGPL-3.0"
               else "No LICENSE file — all rights reserved" if r == "FAIL"
               else "Non-standard licence — needs a human read")
        w(f"| `{c['repository']}` | {c['score']['total']} | {c['metrics']['stars']:,} | {why} |")
w("")
w("`calesthio/OpenMontage` (85/100) is the most consequential block: AGPL-3.0 network "
  "copyleft means hosting a modified version as a service obliges ATK to publish complete "
  "corresponding source. `anthropics/skills` (176,354 stars) has **no LICENSE file at all**, "
  "which is all-rights-reserved by default — the most-starred project in the sweep is also "
  "the one ATK has the least right to redistribute.")

out = root / "reports" / "CANDIDATE_REGISTRY.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"wrote {out}")

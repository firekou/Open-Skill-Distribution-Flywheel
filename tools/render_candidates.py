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
w(f"| **Blocked — license unverified** | **{c_['license_blocked']}** |")
w(f"| Rejected — strategic conflict | {c_['rejected_strategic']} |")
w("")
w("> **The blocked count is the headline finding.** "
  f"{c_['license_blocked']} of {c_['total']} candidates could not have their license "
  "resolved by the automated gate. Per `LICENSE_REVIEW.md` §1 these are treated exactly "
  "like repositories with no license: they cannot enter the Fork Pipeline until a human "
  "reads the LICENSE file. Several of them score highly, which is precisely why the gate "
  "is independent of the score.")
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
        gate = {"PASS": "PASS", "ESCALATE": "ESCALATE", "UNVERIFIED": "BLOCKED"}[lic["ruling"]]
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
w("## Blocked — License Unverified")
w("")
w("Highest-scoring blocked candidates, in score order. Each needs a manual LICENSE read "
  "before it can be reconsidered:")
w("")
w("| Repository | Score | Stars | Note |")
w("|---|--:|--:|---|")
for c in cands:
    if c["decision"] == "blocked" and c["score"]["total"] >= 74:
        note = c["risk"].split(".")[0].replace("BLOCKED on licence", "License unresolved")
        w(f"| `{c['repository']}` | {c['score']['total']} | {c['metrics']['stars']:,} | {note} |")
w("")
w("`anthropics/skills` (176,286 stars) and `calesthio/OpenMontage` (85/100) are the two "
  "most consequential blocks — OpenMontage would otherwise rank second overall.")

out = root / "reports" / "CANDIDATE_REGISTRY.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"wrote {out}")

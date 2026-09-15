# Token Efficiency Lab 001 — GitHub Team
Team: Lab Director, Experiment Designer, Methodology Reviewer, Environment Agent, GitHub Lab Agent, Repository Inspector, Security Agent, Benchmark Runner, Token Meter, Quality Judge, Evidence Archivist, Reproduction Agent, Verify Editor, Claim Checker, Red Team Editor.

GitHub evidence per experiment: repository URL; exact commit SHA/tag; ATK branch; dependency/environment manifest; task version; config/prompt hash where practical; model/provider/version; raw run ID/path; result commit; reproduction instructions. Never use a moving default branch as a reproducible dependency.

Layout: benchmarks/token-efficiency-lab-001/{methodology,environment,tasks,runs,evidence,results,reproduction,reports}/

Gates — **LG** namespace: **LG0** claim → **LG1** methodology frozen → **LG2** repo/security passed → **LG3** environment reproducible → **LG4** execution complete → **LG5** quality floor → **LG6** reproduction → **LG7** Verify state → **LG8** Red Team → **LG9** publish/integrate.

> **Namespace rule (review decision, 2026-09-15).** Lab gates are always **LG0–LG9**; doctrine gates are always **DG0–DG10** (`EXECUTION_DOCTRINE.md`). DG4 is *Test Design*; LG4 is *Execution complete*. **Never write a bare `G4`.**

Stop if permissions/credentials are missing, token accounting is incomparable, environment cannot be pinned, executable fails security, or quality cannot be measured. Record failure; do not improvise.

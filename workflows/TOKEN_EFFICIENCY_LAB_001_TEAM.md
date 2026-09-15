# Token Efficiency Lab 001 — GitHub Team
Team: Lab Director, Experiment Designer, Methodology Reviewer, Environment Agent, GitHub Lab Agent, Repository Inspector, Security Agent, Benchmark Runner, Token Meter, Quality Judge, Evidence Archivist, Reproduction Agent, Verify Editor, Claim Checker, Red Team Editor.

GitHub evidence per experiment: repository URL; exact commit SHA/tag; ATK branch; dependency/environment manifest; task version; config/prompt hash where practical; model/provider/version; raw run ID/path; result commit; reproduction instructions. Never use a moving default branch as a reproducible dependency.

Layout: benchmarks/token-efficiency-lab-001/{methodology,environment,tasks,runs,evidence,results,reproduction,reports}/

Gates: G0 claim → G1 methodology frozen → G2 repo/security passed → G3 environment reproducible → G4 execution complete → G5 quality floor → G6 reproduction → G7 Verify state → G8 Red Team → G9 publish/integrate.

Stop if permissions/credentials are missing, token accounting is incomparable, environment cannot be pinned, executable fails security, or quality cannot be measured. Record failure; do not improvise.

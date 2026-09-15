# Token Efficiency Lab 001 — GitHub Team & Workflow

## Objective
Run 100 meaningful completed benchmark executions across predefined conditions to measure where Agents waste tokens and which interventions reduce cost without unacceptable quality loss.

## Team
- Lab Director: owns experiment and stop/go.
- Experiment Designer: freezes hypotheses, matrix and acceptance thresholds.
- Methodology Reviewer: independent pre-run review.
- Environment Agent: reproducible runtime, versions and locks.
- GitHub Lab Agent: repository/branch structure, commit SHA, manifests and evidence paths.
- Repository Inspector: reviews candidate optimisation tools.
- Security Agent: executable-code gate.
- Benchmark Runner: executes only frozen matrix.
- Token Meter Agent: records tokens/cost/calls.
- Quality Judge Agent: independently scores success/quality.
- Evidence Archivist: stores raw immutable evidence.
- Reproduction Agent: repeats key results.
- Verify Editor/Claim Checker: assigns final evidence state.
- Red Team Editor: challenges conclusions before publication.

## GitHub verification requirements
For each experiment record:
- repository URL and exact commit SHA/tag
- branch used by ATK
- dependency lock/environment manifest
- test task/version
- prompt/config hash where practical
- model/provider/version
- raw run ID and evidence path
- result generation commit
- reproduction instructions

Never treat a moving default branch as a reproducible dependency.

## Repository layout
benchmarks/token-efficiency-lab-001/
- methodology/
- environment/
- tasks/
- runs/
- evidence/
- results/
- reproduction/
- reports/

## Gates
G0 Research claim captured
G1 Methodology frozen
G2 Repository/security inspection passed
G3 Environment reproducible
G4 Benchmark execution complete
G5 Quality floor evaluated
G6 Key result reproduced
G7 Verify state assigned
G8 Red-team editorial review
G9 Publication/integration decision

## Stop conditions
Stop a condition if credentials/permissions are missing, token accounting is not comparable, environment cannot be pinned, executable code fails security gate, or success/quality cannot be measured. Record the failure instead of improvising.

# Token Efficiency Lab 001

## Research question
**Where do Agents waste tokens, and which interventions reduce total task cost without materially reducing task success?**

## Hypotheses
H1. Large MCP/tool schemas create measurable fixed context overhead.
H2. Raw intermediate tool results create avoidable variable overhead.
H3. Model misrouting creates hidden cost through overpowered selection or retry/escalation.
H4. Context accumulation creates avoidable repeated-token cost.

These are hypotheses, not ATK claims until tested.

## Workloads
A. Repository/code analysis
B. Long-document extraction
C. Multi-source research
D. MCP-heavy multi-tool task
E. Long multi-turn agent workflow

## Conditions
Establish a baseline, then compare one intervention at a time before combinations:
1. deferred/reduced tool schema exposure or code-execution pattern
2. tool-result filtering/compression
3. context compaction/compression
4. routing by task complexity/cost
5. selected third-party optimisation tools after review

## Run count
Target 100 completed runs across the matrix. Pre-allocate repetitions and document why. Do not manufacture redundant runs merely to hit a number.

## Metrics per run
run_id, task_id, condition, model/provider, model_calls, tool_calls, input_tokens, output_tokens, total_tokens, cost, latency_ms, retries, escalations, task_success, quality_score, failure_reason, environment/version, raw_evidence_path.

## ATK Verify
REPORTED → external claim only.
OBSERVED → primary source/observable fact inspected.
TESTED → executed by ATK.
VERIFIED → predefined acceptance criteria passed.
REPRODUCED → independently repeated within tolerance.

## Guardrails
- Fix success/quality thresholds before looking at results.
- Report failures and regressions.
- Do not compare cost without controlling task quality.
- Do not silently mix cached and uncached runs.
- Record pricing snapshot separately from token counts.
- Record model/tool versions and commit SHAs.
- Review third-party executable tools before use.
- Lower tokens with unacceptable quality is a failed optimisation.

## Deliverables
methodology; task set; raw run log; result table; analysis; reproduction instructions; ATK Verify report; content package; integration recommendations.

## Result format
Baseline tokens/cost → treatment tokens/cost → delta → success/quality delta → evidence state → limitations.

The purpose is not to prove ATK is good. The purpose is to produce evidence strong enough that a skeptical developer can reproduce or challenge it.

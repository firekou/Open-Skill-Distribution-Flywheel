# Lab 001 — Blind Evaluation Protocol v1.0.0

**Status:** ACTIVE · **Binds:** every scored run, including pilot, reproduction and LG4
**Enforced by:** `environment/harness/blind.py` — machine-checked, not procedural

---

## Why this exists

Two of the eight candidates, `rtk` and `headroom`, are simultaneously Lab subjects and ATK
integration candidates. The frozen methodology declares that conflict rather than hiding it, and
commits to a mitigation: *"the Quality Judge scores before seeing cost"* and *"a result
favourable to an ATK integration candidate is the one most in need of reproduction, not the one
most ready to publish."*

A protocol that relies on the judge choosing not to look is not a mitigation. This one removes
the information from the judge's path entirely, and fails the run if it leaks.

---

## What the Quality Judge sees

Exactly six fields, and nothing else:

| Field | Why it is allowed |
|---|---|
| `packet_id` | An opaque handle. Derived from a hash of run id and task id; carries no ordering |
| `task_id` | The judge must know which task is being scored |
| `workload` | The quality floor differs per workload |
| `blind_treatment_id` | `Treatment A`, `Treatment B`, … — see labelling below |
| `model_output` | The thing being scored |
| `required_evidence`, `answer_key`, `quality_metric`, `failure_condition` | The scoring basis, frozen before any run |

## What the Quality Judge must never see

| Forbidden | Why |
|---|---|
| Candidate name | The whole conflict of interest |
| Condition / treatment name | `C5` means "third-party tool"; knowing it is C5 is knowing it is a candidate |
| Any token count | Token counts and cost are the independent variable. Seeing them makes the dependent variable dependent on them |
| Cost, pricing snapshot | Same |
| Model, provider, model pair, model version | Identifies the treatment indirectly |
| Retries, escalations, latency | A run with three retries is visibly a struggling run |
| Repository popularity, stars | Reputation is not evidence |
| ATK integration interest | The precise bias being controlled for |

`FORBIDDEN_KEYS` in `harness/blind.py` is the machine-readable form of this table.

## Enforcement

`assert_blind()` runs on every packet before it is written to the judge's path. It:

1. **Walks the packet recursively** — every key at every depth, inside nested objects and inside
   list elements. A forbidden key buried three levels down fails the same as one at the top.
2. **Scans every string value for candidate names.** A model output that mentions "headroom"
   in passing un-blinds the packet as effectively as a metadata field would. The run is failed
   and the output must be scrubbed before it can be scored.
3. **Raises, it does not warn.** There is no flag to continue past a blind violation.

The judge packets are written to `judge_packets/`. The mapping is written to
`runner_only/BLIND_MAPPING.json`, which must never be placed on the judge's path.

## Labelling

Treatments become `Treatment A`, `Treatment B`, … assigned by sorting SHA-256 digests of
`(salt, condition)`.

This matters more than it looks. If labels were assigned in condition order, `Treatment A` would
always be `C0` and every label would be transparent after one run. Digest-ordering means the
label sequence carries no information about the condition sequence: without the salt, which
treatment is which is not guessable; with it, un-blinding is exact and repeatable.

The salt is held by the Benchmark Runner and recorded only as a hash in the saved mapping.

## Un-blinding

`BlindMapping.unblind()` refuses unless **both** hold:

- the caller asserts scoring is complete, **and**
- every packet in the batch carries a non-null `quality_score`.

A partially scored batch cannot be un-blinded. This closes the obvious hole: score the ones you
like, peek, then score the rest.

## Ordering within a run

1. The harness executes the run and writes the record with `task_success=false`,
   `quality_score=0.0` as placeholders. **The harness never scores.**
2. The harness builds the blind packet and hands it over.
3. The Quality Judge scores from the packet alone and returns `quality_score` and
   `task_success`.
4. The record is updated with the returned values and `quality_judged_before_cost=true`.
5. Only once every packet in the batch is scored may the mapping be reversed.

Step 1 writing a placeholder rather than leaving the field absent is deliberate: the schema
requires `quality_score`, so a record that was never judged is visibly a zero rather than
silently missing.

## Seat separation

| Seat | May | May not |
|---|---|---|
| Benchmark Runner | Execute runs, hold the salt and mapping, update records after scoring | Score anything |
| Quality Judge | Score packets | See the mapping, the salt, any record, or any cost figure |
| Task Set Designer | Author tasks | Know which candidates exist (guardrail 7) |
| Answer Key Builder | Derive ground truth from task inputs | See the designer's intended answers |
| Task Red Team | Reject tasks and keys | Author replacements for what it rejected |
| Reproduction Agent | Repeat a run independently | Reproduce its own original run (SEAT_REGISTRY invariant I10) |

## Known limits of this protocol

Stated because a protocol whose limits are unstated gets over-trusted.

- **A distinctive output style can un-blind a treatment.** If a compression tool produces
  recognisably clipped text, a judge may infer the treatment from the output itself. Name
  scrubbing does not fix this. Nothing in this protocol fixes it; it is a residual risk, and the
  mitigation is reproduction, not blinding.
- **Small batches leak through the labels.** With two conditions and one task, `Treatment A` and
  `Treatment B` are guessable at 50% by chance alone.
- **The judge is one seat.** Blinding controls for identity bias, not for a judge who is simply
  wrong. The Red Team reviews the scoring spec; it does not re-score.
- **Name scrubbing is substring matching, and deliberately so.** `rtk` inside an unrelated word
  would fail a packet that never leaked anything. That is the right failure direction: a false
  positive costs one re-run, a false negative costs the blind. Verified behaviour, not an
  oversight.
- **It does not address the conflict of interest itself,** only one channel of it. A favourable
  result for `rtk` or `headroom` still requires independent reproduction before publication.

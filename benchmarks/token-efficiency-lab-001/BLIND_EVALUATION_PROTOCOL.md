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

---

# Addendum v1.1.0 — salt custody, evidence contract, and what changed

Added 2026-09-16 in the Prompt 3.5 repair round. The v1.0.0 protocol above stands; this addendum
closes gaps that only appeared once the protocol met a real reproduction attempt.

## 1. Salt custody

The v1.0.0 protocol said the salt is "held by the Benchmark Runner" and stopped there. That is
not a custody model: it does not say who may read it, where it lives, or how an independent
Reproduction Agent replays a run without it. The Reproduction Agent hit this directly — the salt
is not in the repository, only its hash, so the blind-mapping row of its comparison was **not
independently executable**.

| Question | Answer |
|---|---|
| **Who holds it** | The **Benchmark Runner** seat, and only that seat |
| **Where it lives** | A secret store outside the repository. **Never** in the repository, never in a run record, never in an evidence bundle, never in a log line |
| **What may be published** | `salt_sha256` only — enough to prove which salt a mapping used, not enough to reproduce a label |
| **Who may never read it** | The **Quality Judge**, for as long as any packet in the batch is unscored. The salt is the mapping |
| **The Reproduction Agent** | Is issued the salt by the Runner **after** scoring is complete for the batch it is reproducing, and records that it received it. Before that point it reproduces everything except the label and records the label row as `not independently executable` |
| **Rotation** | One salt per batch. A salt is never reused across batches, because a reused salt makes labels comparable across batches, which is a slow way of un-blinding |
| **Synthetic fixtures** | May use a clearly marked test salt (`lab001-dryrun-salt-…`). A test salt is **not** a blinding secret and must never be used for a scored run |

**Never in the Judge's path:** `runner_only/BLIND_MAPPING.json`, the salt itself, any run record,
any cost figure, any `egress_destinations` list.

## 2. Labels are a property of (salt, condition), not of the batch

Fixed this round and verified. Labels are assigned over the **canonical condition set**
(`C0, C1, C2, C3, C4, C5, C2+C4, C3+C4, CALIB, CACHE`), never over whatever happens to be in the
batch. Previously the same salt gave `C0 = Treatment B` in a 10-run plan and `C0 = Treatment A` in
a 2-run subset — so an honest partial reproduction, which is exactly what the Reproduction seat
does, would disagree on `blind_treatment_id` while being entirely correct.

## 3. The evidence contract — what the judge is given, and who produced it

`required_evidence` is now produced by a named seat, `harness-evidence-producer`
(`environment/harness/evidence.py`), not scraped from a task file that never had the key.

| Evidence | Produced from | Never from |
|---|---|---|
| `valid_symbols` | `ast` parse of the frozen corpus | the model's answer |
| `catalog_part_ids`, `halberd_part_ids`, `shifts`, `roster` | the frozen CSVs | the model's answer |
| `tool_calls` | the **server-written audit log**, filtered to this run id | the model's self-report |
| `turns` | captured by the runner, asserted complete and in order | a reconstructed transcript |
| `corpus_hashes` | hashed before and after the attempt | — |

Four properties are enforced, each of them a hole that was open in v1.0.0:

1. **Empty is not present.** `{}` and `[]` fail closed. An empty `shifts`/`roster` previously
   passed every type check and silently disabled workload E's zero-tolerance criteria, so a run
   assigning an ineligible person scored `task_success: true`.
2. **Missing evidence is `INVALID`, not a pass and not a quality failure.** "It failed" and "we
   could not measure it" are different findings.
3. **Cross-run contamination is rejected.** Every audit entry must carry this run's id; a log left
   over from a previous attempt would otherwise score this one.
4. **Evidence is treatment-neutral, and that is machine-checked.** `required_evidence` reaches the
   judge, so a candidate name, a routed model or a token count inside it defeats the blind as
   surely as a metadata field. `assert_treatment_neutral` walks it recursively and raises.

**The answer key is never mounted for the agent under test.** It reaches the Quality Judge only,
inside the packet.

## 4. Packet sufficiency is asserted before the judge sees anything

`assert_evidence_sufficient` runs at packet-build time and **raises**. A judge that receives a
packet has evidence; a packet that would have arrived empty never arrives. For workload E it also
asserts `len(turns) == turn_count`, so a truncated transcript cannot hide every violation after
the cut — previously a byte-perfect E-002 runbook with a violation at turn 8 scored 1.0 and passed
when `turns` was omitted.

## 5. Scores are written back — protocol step 4 now exists

`harness/finalize.py` writes `quality_score`, `task_success` and `outcome` into the run record. It
refuses a batch containing any unscored packet or any record without a score, and it refuses a
score that declares no outcome rather than inferring one from `task_success` — inferring it would
collapse `INVALID` into `FAIL_QUALITY`.

## 6. Residual risks, restated

The v1.0.0 limitations still hold: a distinctive output style can un-blind a treatment regardless
of scrubbing; small batches leak through the labels; blinding controls for identity bias, not for
a judge that is simply wrong; and none of this addresses the conflict of interest itself, only one
channel of it. A favourable result for an ATK integration candidate still requires independent
reproduction before publication.

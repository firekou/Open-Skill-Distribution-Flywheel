# ATK Evidence-Driven Execution Doctrine v1

**Status:** Repository governing execution doctrine  
**Principle:** 大膽假設，小心求證。Vision can be large; evidence cannot be loose.

## 0. Purpose
This repository exists to make ATK move forward through a repeatable chain of hypothesis, evidence, decision and execution. It must not become a place where Agents stay busy, generate documents, or wander between interesting ideas without reducing uncertainty.

The governing question for every meaningful task is:

> **Which hypothesis are we testing, what evidence will this produce, and what decision could change because of it?**

If a task cannot answer that question, it is probably activity rather than progress.

## 1. Scope
The current scope is the emerging Agent economy, starting from Token as the first measurable wedge and expanding only when evidence supports it.

Research domains include:
- Token economics and token efficiency
- Agent unit economics
- Model/resource economics
- Measurement, metering and attribution
- Trust, auditability and verification
- Routing, fallback and escalation
- Context and memory economics
- MCP/tool economics
- Agent skills and frameworks
- A2A/protocols
- Agent security, identity, governance and permissions
- Agent billing, budget and payments
- Technical intelligence and demand sensing

Long-term strategic frame:
**Know what Agents are doing → Measure what Agents consume → Control how Agents spend.**

Possible business progression:
**Media → Intelligence → Measurement → Execution.**

These are strategic frames, not automatically proven conclusions.

## 2. Core research culture
### Bold hypotheses
We are allowed to propose large possibilities early.

### Careful verification
No hypothesis becomes strategy merely because it sounds coherent or because multiple models agree.

### Adversarial search
For important hypotheses, actively seek evidence that would falsify them. Search both supporting and opposing explanations.

### Evidence over model consensus
Claude, ChatGPT, Gemini, Qwen or any future model may disagree. Do not resolve disagreement by majority vote. Resolve it by better evidence, stronger methodology and reproducibility.

### Small validation, large vision
Vision may describe a 3–5 year opportunity. The next validation step should normally be small enough to complete, inspect and learn from.

## 3. The three ledgers

### Hypothesis Ledger
Stores what we currently believe might be true.

Required fields:
- hypothesis_id
- statement
- type: market / product / operating-model / technical / distribution
- why_it_might_be_true
- evidence_for
- evidence_against
- falsification_test
- current_confidence
- next_experiment
- owner
- updated_at

### Evidence Ledger
Stores what was actually observed or tested.

Required fields:
- evidence_id
- hypothesis_ids
- evidence_state
- source/provenance
- method
- raw_evidence_path
- result
- limitations
- reproducibility
- date

Evidence states:
**REPORTED → OBSERVED → TESTED → VERIFIED → REPRODUCED**

### Decision Ledger
Stores decisions made because of evidence.

Required fields:
- decision_id
- decision
- hypothesis_ids
- evidence_ids
- rationale
- alternatives_considered
- reversible_or_irreversible
- success_metric
- review_date
- outcome

A decision without traceable evidence must be explicitly marked as a strategic bet.

## 4. Confidence ladder for hypotheses
- **H0 Idea:** plausible idea, no meaningful evidence.
- **H1 Signal:** observable market/technical signal exists.
- **H2 Supported:** multiple independent evidence sources support it.
- **H3 Tested:** ATK has run a defined test or experiment.
- **H4 Validated:** real external behavior/usage supports it.
- **H5 Commercially Proven:** repeated willingness to pay, usage/retention or equivalent commercial evidence exists.

Stars, views and model agreement can never by themselves produce H5.

## 5. Foundational hypotheses

### H001 — Measurement / Attribution / Trust demand
As Agent deployment scales, organizations will increasingly need measurement, attribution and trust capabilities around Agent resource use.

Attack it by asking whether users merely like observability but refuse to pay; whether open source makes it commodity; whether reliability/security is actually more urgent.

### H002 — Token Cost as wedge
Token cost/efficiency is a strong initial wedge into broader Agent Resource Intelligence.

Compare it against alternative wedges: reliability, security, budget control, billing attribution, routing and governance.

### H003 — Technical Intelligence as distribution engine
A technical intelligence magazine/research system can become a low-CAC distribution and trust engine for ATK measurement/routing products.

Test using topic IDs and attributable views, saves, GitHub actions, return visits, subscriptions, ATK visits, registrations and API activation.

### H004 — Agent-native operating leverage
A multi-model Agent organization can allow a very small human team to achieve dramatically higher verified research/engineering/media output per human hour.

Measure AI cost, human review time, rework, failure rate, verified output and published output. Primary productivity metric:
**Verified reusable output / human hour.**

### H005 — Verification becomes more valuable as generation gets cheaper
As AI lowers information-production cost, trustworthy evidence, reproducibility and verification become scarcer and more valuable.

Test whether ATK VERIFIED assets receive higher reuse, citation, saves, developer actions, commercial interest or willingness to pay than unverified content.

## 6. Derived hypotheses to investigate
Do not promote these to strategy yet:
- H006: Agent Unit Economics becomes a recognized management discipline.
- H007: Cost per successful task is more useful than raw token price for many Agent decisions.
- H008: Quality-adjusted routing creates more value than cheapest-model routing.
- H009: Machine-readable Trust Receipts become useful for enterprise Agent operations.
- H010: Technical demand sensed from both humans and Agents predicts better product priorities than editorial intuition alone.

## 7. Agent Unit Economics research frame
Candidate metrics:
- Cost per task
- Tokens per successful task
- Model cost per successful task
- Tool cost per task
- Retry cost
- Escalation cost
- Context cost
- Latency per successful task
- Quality-adjusted cost
- Agent gross margin where economically meaningful

Do not invent a metric merely because it sounds financial. Each metric must prove that it changes a real decision.

## 8. Progress ladder
Every major workstream moves through explicit gates:

**G0 Question** → precise unknown  
**G1 Hypothesis** → falsifiable statement  
**G2 Signal** → initial evidence  
**G3 Research** → primary-source dossier + counterevidence  
**G4 Test Design** → method, baseline, acceptance/falsification criteria  
**G5 Execution** → raw evidence collected  
**G6 Verification** → evidence reviewed/reproduced as appropriate  
**G7 Decision** → continue / change / stop / build  
**G8 Distribution** → publish reusable intelligence/evidence  
**G9 Demand Feedback** → measure human + Agent response  
**G10 Productization** → only when evidence supports engineering investment

A workstream may not silently jump gates.

## 9. Forward-motion rule
At the end of every Claude/Agent execution, output exactly:
1. What uncertainty was reduced?
2. Which hypothesis changed confidence?
3. What new evidence was produced?
4. What failed or contradicted us?
5. What decision is now justified?
6. What is the single next gate?
7. What must be reviewed by ChatGPT/Editor-in-Chief before continuing?

If these cannot be answered, the work is incomplete.

## 10. Multi-model convergence protocol
Claude is primarily Executor/Producer.
ChatGPT is primarily Strategist/Reviewer/Red Team.
Other models may be assigned independent research, long-context, coding or adversarial roles.
The human Publisher/Editor-in-Chief allocates direction and capital.

Rules:
- Do not ask models to reach consensus first.
- Let them produce independent reasoning/evidence where useful.
- Record disagreements.
- Convert disagreements into testable questions.
- Prefer primary evidence and reproducible experiments.
- Human strategic decisions remain explicit.

## 11. Permissionless operating doctrine
ATK seeks five kinds of permissionless leverage:
1. **Research:** discover and study public technical knowledge without waiting for an institution.
2. **Production:** use Agent workforce to reduce marginal research/production cost.
3. **Publishing:** publish through owned GitHub/web/media channels.
4. **Distribution:** use owned audience assets and open networks.
5. **Productization:** turn validated needs into lawful, attributed Skills, adapters, benchmarks, APIs, routing or products.

Permissionless does **not** mean license-less, attribution-less, security-less or evidence-less. Rights, security, privacy and platform constraints remain gates where applicable.

## 12. Magazine + Lab + Engineering relationship
**ATK Intelligence** discovers and explains.
**ATK Verify** controls evidence state.
**ATK Lab** runs experiments.
**ATK Benchmark** turns repeatable evidence into comparisons.
**ATK Magazine** distributes intelligence.
**Demand Intelligence** measures response.
**ATK Engineering** productizes only validated opportunities.

Production loop:
**Signal → Research → Proof → Content → Distribution → GitHub → Demand → Decision → ATK**

Commercial exploration:
**Media → Intelligence → Measurement → Execution**

## 13. Anti-wandering rules
Claude/Agents must not:
- expand scope merely because a topic is interesting;
- create new strategic pillars without a hypothesis ID;
- generate documents whose decision use is undefined;
- treat stars/views as users;
- treat model consensus as evidence;
- treat vendor claims as ATK verification;
- keep researching indefinitely after a decision threshold is reached;
- run expensive benchmarks before methodology review;
- build integrations before the appropriate evidence/security/rights gates;
- hide failed experiments or counterevidence.

## 14. Current execution priorities
P0: Complete S3 Top30 and Token Efficiency Lab 001 precheck already defined in CLAUDE_EXECUTION_START.md.
P1: Create and begin maintaining the three ledgers.
P2: Test H001/H002 through deep demand research around token/cost/measurement projects.
P3: Execute Token Efficiency Lab 001 after mandatory review.
P4: Use Magazine distribution to begin measuring H003/H005.
P5: Measure the Magazine Agent organization itself to test H004.
P6: Only then increase automation, publication volume and engineering scope based on observed bottlenecks.

## 15. Mandatory review cadence
For each major gate:
**Claude executes → GitHub records evidence → ChatGPT reviews/challenges → Claude corrects → human decides continue/change/stop.**

Do not require review for every trivial action. Require it when:
- hypothesis confidence changes materially;
- benchmark methodology is about to lock;
- a result becomes VERIFIED/REPRODUCED;
- a new product/integration is proposed;
- scope or capital allocation changes;
- evidence contradicts a foundational hypothesis.

## 16. Definition of progress
Progress is not:
more files, more agents, more posts, more forks, more autonomous runs.

Progress is:
**less uncertainty + stronger evidence + better decisions + reusable verified assets + measurable demand + validated product learning.**

## 17. Immediate instruction to Claude
Continue current S3/Lab-precheck execution under this doctrine.
Do not restart completed work.
Map current findings to H001–H005 where relevant.
Create the initial Hypothesis, Evidence and Decision ledgers.
At the mandatory stop, report the Forward-Motion Rule seven questions and wait for review.

The repository is a company learning system. Its job is not to look busy. Its job is to make the next decision more correct than the previous one.

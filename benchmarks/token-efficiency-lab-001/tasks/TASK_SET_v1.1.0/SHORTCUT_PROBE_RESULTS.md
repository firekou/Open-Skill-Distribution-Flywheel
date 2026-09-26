# SHORTCUT_PROBE_RESULTS.md — B-002, RT-03

**Seat:** Task Set Designer · **Task set:** v1.1.0 · **Finding closed:** RT-03 (BLOCKING)
**Script:** `shortcut_probe/probe_b002.py` · **Reproduce:** `python3 shortcut_probe/probe_b002.py`
from the task-set root; add `--json` for machine-readable output, `--doc PATH` to probe another
document.

---

## 1. What RT-03 said, and what was measured

The Red Team found that everything B-002 needed sat in the last 13% of its 147 KB document —
Appendix A at byte 127,608 and Appendix B at byte 131,705 — so a condition that discarded the
first 86% of the document lost nothing and saved most of the tokens. Pre-registered H2 and H4
would have read that artefact as a confirmed "saving with no quality cost".

The probe scores what a run could **at best** produce from a restricted view of the document,
against what it could produce from the whole of it, under B-002's own quality metric (7 cells per
reference record plus one `count` cell). Each strategy is given the benefit of the doubt: the
extractor is a perfect reader of whatever bytes the strategy retained and applies every
precedence rule it can see. Every figure below is therefore a **ceiling**, not a typical outcome.

## 2. v1.0.0 — the defect, reproduced

`TASK_SET_v1.0.0/corpora/docs_b/KESTREL_RELIABILITY_2031.md`, 146,666 bytes, 24 records in the
reference answer.

| strategy | bytes read | share | register rows seen | notices seen | quality | ≥ 0.97 |
|---|--:|--:|--:|--:|--:|:--:|
| full document (reference) | 146,666 | 100.0% | 48 | 8 | **1.0000** | yes |
| **last 15% of bytes only** | 22,000 | 15.0% | 48 | 8 | **1.0000** | **yes** |
| first section only | 13,212 | 9.0% | 0 | 0 | 0.0000 | no |
| fixed truncation, first 32,768 bytes | 32,768 | 22.3% | 0 | 0 | 0.0000 | no |
| fixed truncation, first 50% | 73,333 | 50.0% | 0 | 0 | 0.0000 | no |
| **head 10% + tail 15% (ends-only compaction)** | 36,666 | 25.0% | 48 | 8 | **1.0000** | **yes** |
| content-selective retrieval | 6,578 | 4.5% | 48 | 8 | 1.0000 | yes |

Discarding 85% of the document cost **nothing**: 1.0000 against 1.0000, at 15% of the bytes. That
is the bias, measured rather than argued.

## 3. v1.1.0 — after the rebuild

`corpora/docs_b/KESTREL_RELIABILITY_2031.md`, 161,471 bytes (the probe reads 161,323 characters), 26 records in the reference answer.

| strategy | bytes read | share | register rows seen | amendments seen | notices seen | sees §1.4 | records emitted | quality | ≥ 0.97 |
|---|--:|--:|--:|--:|--:|:--:|--:|--:|:--:|
| full document (reference) | 161,323 | 100.0% | 48 | 9 | 8 | yes | 26 | **1.0000** | yes |
| **last 15% of bytes only** | 24,199 | 15.0% | 0 | 9 | 8 | no | 0 | **0.0000** | **no** |
| **first section only** (to §2) | 5,754 | 3.6% | 0 | 0 | 0 | yes | 0 | **0.0000** | **no** |
| **fixed truncation, first 32,768 bytes** | 32,768 | 20.3% | 0 | 0 | 0 | yes | 0 | **0.0000** | **no** |
| **fixed truncation, first 50%** | 80,661 | 50.0% | 20 | 0 | 0 | yes | 8 | **0.2421** | **no** |
| **head 10% + tail 15%** (ends-only compaction) | 40,331 | 25.0% | 0 | 9 | 8 | yes | 0 | **0.0000** | **no** |
| **content-selective retrieval** | 8,464 | 5.2% | 48 | 9 | 8 | yes | 26 | **1.0000** | **yes** |

The four required conditions all hold, and the fifth — the one that stops this becoming the
opposite bias — holds too:

1. reading only the last 15% **fails**, 0.0000 (was 1.0000);
2. reading only the first section **fails**, 0.0000;
3. a fixed-length truncation **fails**, at 32 KB and at half the document alike;
4. an ends-only compaction, the shape that survived v1.0.0 intact, **fails**, 0.0000;
5. **content-selective retrieval still succeeds at 1.0000 on 5.2% of the bytes.** Full-document
   reading is not required and is not rewarded.

The half-document truncation is the informative row: it sees 20 of 48 register rows and no
superseding layer at all, emits 8 records where the reference has 26, and emits one record that
is not in the reference at all — a *complete, confident and wrong* answer of the kind this
workload exists to catch, rather than a visible refusal.

## 4. What changed in the corpus to produce that

The document was rebuilt, not rearranged. The register that was a single appendix is now four
per-quarter registers, and a second superseding layer was added:

| evidence | where it now sits | why a run needs it |
|---|--:|---|
| §1.2, where each kind of figure is recorded | 0.8% | the navigation map that makes selective retrieval possible at all |
| §1.4, precedence + three further rules | 2.0% | four-level precedence, the withdrawal rule, and "selection happens last" — none restated in the prompt |
| Quarter 1 register (11 incidents) | 21.9% | base records |
| Quarter 2 register (9 incidents) | 40.1% | base records |
| Quarter 3 register (13 incidents) | 59.9% | base records |
| Quarter 4 register (15 incidents) | 80.5% | base records |
| Appendix A — Register Amendments (9) | 95.3% | supersede the registers; one withdraws an incident that is otherwise in the answer |
| Appendix B — Correction Notices (8) | 97.6% | supersede everything, including two amendments that name the same field |

Between those pieces is on-topic content, not filler of an obviously droppable kind: 48
per-incident narratives that each state a severity and a duration the precedence rules demote,
plus monthly availability tables. A position-based filter cannot tell them from payload; a
content-based one must read the precedence rule to learn that it may discard them.

Two amendment/notice pairs name the **same** incident and the **same** field, so a run that has
the appendices but not §1.4 cannot know which wins. One pair names the same incident and
**different** fields, so both apply. One amendment withdraws an incident whose severity would
otherwise put it in the answer. §1.4 therefore does work that no other part of the document does.

## 5. Honest limits of this probe

* **It measures sufficiency of evidence, not model behaviour.** No model was run. Every number is
  a constructed ceiling scored through the B-002 metric.
* **"Content-selective retrieval" is an idealisation.** It selects by document structure — the
  precedence subsection, any table whose header names the register columns, any correction-notice
  paragraph. A real retriever keying on the word "severity" would also pull the narratives, read
  more bytes, and still score 1.0000 provided it applied the precedence rule; a retriever that
  filtered *out* short boilerplate-looking blocks would lose the notices and score far less.
  5.2% is the floor of what a competent selector needs, not a prediction.
* **This script is not an answer key and must not be used as one.** The Answer Key Builder derives
  B-002 independently from the task statement and the corpus. If the two disagree, this script is
  wrong. It is committed only because a BLOCKING finding must be reproducible; it reports
  aggregate scores and never the record set.
* **The reference row is the answer this probe's own extractor produces.** Every quality figure is
  relative to that, not to the delivered key, which does not exist yet.

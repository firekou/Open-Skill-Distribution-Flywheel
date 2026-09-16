#!/usr/bin/env python3
"""RT-03 shortcut probe for B-002.

WHAT THIS IS.  An instrument for measuring whether B-002's evidence is genuinely
distributed through its document, by scoring what a run could at best produce from a
restricted view of that document against what it could produce from the whole of it.

WHAT THIS IS NOT.  It is not an answer key and it is not a derivation of one.  The
Answer Key Builder derives B-002 independently from the task statement and the corpus;
if that derivation disagrees with this script, this script is wrong.  The committed
results file reports only aggregate scores, never the record set.

Each strategy is given the benefit of the doubt: the extractor is a perfect reader of
whatever bytes the strategy retained, with perfect application of the precedence rules
it can see.  A strategy therefore scores the *ceiling* of what it could achieve, not a
typical outcome.

Usage:
    python3 shortcut_probe/probe_b002.py  [--doc PATH] [--json]

Run from the task-set root.  With no --doc it probes this task set's document; pass
--doc to probe another (for example the v1.0.0 document, for a before/after table).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

FIELDS = ("incident_id", "service", "start_utc", "duration_minutes",
          "final_severity", "root_cause_code", "customer_impacting")

REGISTER_ROW = re.compile(
    r'^\|\s*(INC-\d{4}-\d{3})\s*\|\s*([A-Za-z0-9_-]+)\s*\|\s*'
    r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s*\|\s*(\d+)\s*\|\s*'
    r'(S\d)\s*\|\s*(RC-[A-Z]+)\s*\|\s*(yes|no)\s*\|\s*$', re.M)

AMENDMENT_ROW = re.compile(
    r'^\|\s*(RA-\d{4}-\d{2})\s*\|\s*(INC-\d{4}-\d{3})\s*\|\s*'
    r'(severity|duration_minutes|root_cause_code|customer_impacting|withdrawn)\s*\|'
    r'\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$', re.M)

# Handles both the v1.1.0 wording ("the value standing for `severity`") and the
# v1.0.0 wording ("the value recorded in Appendix A for `final_severity`").
NOTICE = re.compile(
    r'\*\*Correction Notice (CN-\d+)\*\*\s*[-—]\s*For incident (INC-\d{4}-\d{3}), '
    r'the value (?:standing|recorded in Appendix A) for `(\w+)` is incorrect\. '
    r'The value (?:standing|published) as `([^`]*)` is withdrawn and replaced by `([^`]*)`\.')

PRECEDENCE_ANCHOR = "Precedence of figures"
WITHDRAWAL_ANCHOR = "R-2. Withdrawal"


def parse_view(text):
    """Everything the reader can see in `text`, as structured evidence."""
    register = {}
    for m in REGISTER_ROW.finditer(text):
        iid, svc, start, dur, sev, rc, ci = m.groups()
        register[iid] = {"incident_id": iid, "service": svc, "start_utc": start,
                         "duration_minutes": int(dur), "final_severity": sev,
                         "root_cause_code": rc, "customer_impacting": (ci == "yes")}
    amendments = [(m.group(2), m.group(3), m.group(5).strip())
                  for m in AMENDMENT_ROW.finditer(text)]
    notices = [(m.group(2), m.group(3), m.group(5).strip())
               for m in NOTICE.finditer(text)]
    return {
        "register": register,
        "amendments": amendments,
        "notices": notices,
        "sees_precedence": PRECEDENCE_ANCHOR in text,
        "sees_withdrawal_rule": WITHDRAWAL_ANCHOR in text,
    }


def _apply(rec, field, value):
    if field == "severity" or field == "final_severity":
        rec["final_severity"] = value
    elif field == "duration_minutes":
        rec["duration_minutes"] = int(value)
    elif field == "root_cause_code":
        rec["root_cause_code"] = value
    elif field == "customer_impacting":
        rec["customer_impacting"] = (value == "yes")


def best_answer(view):
    """The best answer obtainable from this view, applying every rule it can see."""
    recs = {k: dict(v) for k, v in view["register"].items()}
    withdrawn = set()

    # Register Amendments, then Correction Notices: a notice naming the same incident
    # and field supersedes an amendment (precedence rule, section 1.4).
    for iid, field, new in view["amendments"]:
        if field == "withdrawn":
            # A reader that has not seen the withdrawal rule cannot know what to do
            # with this row and leaves the incident in place.
            if view["sees_withdrawal_rule"]:
                withdrawn.add(iid)
            continue
        if iid in recs:
            _apply(recs[iid], field, new)
    for iid, field, new in view["notices"]:
        if iid in recs:
            _apply(recs[iid], field, new)

    out = [r for iid, r in sorted(recs.items())
           if iid not in withdrawn and r["final_severity"] in ("S1", "S2")]
    return {"incidents": out, "count": len(out)}


def score(candidate, key):
    """B-002 quality metric: 7 cells per key record, plus one cell for `count`."""
    kmap = {r["incident_id"]: r for r in key["incidents"]}
    pmap = {}
    for r in candidate["incidents"]:                 # UG-09: first occurrence wins
        pmap.setdefault(r["incident_id"], r)
    denominator = 7 * len(kmap) + 1
    matched = 0
    for iid, kr in kmap.items():
        pr = pmap.get(iid)
        if pr is None:
            continue
        for f in FIELDS:
            if f in pr and pr[f] == kr[f]:
                matched += 1
    extra = [i for i in pmap if i not in kmap]
    denominator += 7 * len(extra)
    if candidate["count"] == len(candidate["incidents"]) == key["count"]:
        matched += 1
    return round(matched / denominator, 4), len(pmap), len(extra)


# ---------------------------------------------------------------- strategies
def strategy_views(doc):
    n = len(doc)
    body_start = doc.index("\n## 2.") if "\n## 2." in doc else n // 10

    def retrieval(d):
        """Content-selective retrieval: keep only passages that carry evidence.

        Selection is by structure, not by position: the precedence subsection, every
        table whose header row names the register columns, every amendment table, and
        the correction-notice block.  This is what a competent retriever should find.
        """
        keep = []
        # the whole of the numbered subsection that states the precedence rules
        m = re.search(r'^#+ [\d.]*\s*Precedence of figures.*?(?=^#+ )', d, re.M | re.S)
        if m:
            keep.append(m.group(0))
        # every register / amendment table, headers included
        for tm in re.finditer(
                r'(?:^\|[^\n]*incident_id[^\n]*\|\n\|[-| ]+\|\n(?:\|[^\n]*\|\n)+)'
                r'|(?:^\|[^\n]*amendment_id[^\n]*\|\n\|[-| ]+\|\n(?:\|[^\n]*\|\n)+)',
                d, re.M):
            keep.append(tm.group(0))
        # every correction notice paragraph
        for nm in re.finditer(r'\*\*Correction Notice [^\n]*\n', d):
            keep.append(nm.group(0))
        return "\n".join(keep)

    return [
        ("full document (reference)", doc, n),
        ("last 15% of bytes only", doc[int(n * 0.85):], n - int(n * 0.85)),
        ("first section only (up to section 2)", doc[:body_start], body_start),
        ("fixed truncation: first 32768 bytes", doc[:32768], min(32768, n)),
        ("fixed truncation: first 50% of bytes", doc[:n // 2], n // 2),
        ("head 10% + tail 15% (ends-only compaction)",
         doc[:int(n * 0.10)] + "\n" + doc[int(n * 0.85):],
         int(n * 0.10) + (n - int(n * 0.85))),
        ("content-selective retrieval", retrieval(doc), len(retrieval(doc))),
    ]


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    default = os.path.join(os.path.dirname(here), "corpora", "docs_b",
                           "KESTREL_RELIABILITY_2031.md")
    ap.add_argument("--doc", default=default)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    doc = open(a.doc, encoding="utf-8").read()
    views = strategy_views(doc)
    key = best_answer(parse_view(views[0][1]))

    rows = []
    for name, text, nbytes in views:
        v = parse_view(text)
        cand = best_answer(v)
        q, reported, extra = score(cand, key)
        rows.append({
            "strategy": name,
            "bytes_read": nbytes,
            "share_of_document": round(nbytes / len(doc), 4),
            "register_rows_visible": len(v["register"]),
            "amendments_visible": len(v["amendments"]),
            "notices_visible": len(v["notices"]),
            "sees_precedence_rules": v["sees_precedence"],
            "records_reported": reported,
            "records_not_in_reference": extra,
            "quality_score": q,
            "passes_0_97_floor": q >= 0.97,
        })

    out = {"document": os.path.relpath(a.doc, os.path.dirname(here)),
           "document_bytes": len(doc),
           "reference_record_count": key["count"],
           "strategies": rows}
    if a.json:
        print(json.dumps(out, indent=2))
        return 0
    print("document: %s  (%d bytes, %d records in the reference answer)"
          % (out["document"], out["document_bytes"], out["reference_record_count"]))
    print()
    hdr = ("%-38s %9s %6s %5s %4s %4s %5s %8s %6s"
           % ("strategy", "bytes", "share", "reg", "amd", "cn", "recs", "quality", "pass"))
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print("%-38s %9d %5.1f%% %5d %4d %4d %5d %8.4f %6s"
              % (r["strategy"], r["bytes_read"], 100 * r["share_of_document"],
                 r["register_rows_visible"], r["amendments_visible"],
                 r["notices_visible"], r["records_reported"],
                 r["quality_score"], "yes" if r["passes_0_97_floor"] else "NO"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

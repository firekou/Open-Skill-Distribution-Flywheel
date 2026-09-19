#!/usr/bin/env python3
"""Derive answer keys for workload C (C-001..C-003) of TASK_SET_v1.1.0.

All three keys are computed from corpora/research_c/ by parsing the structured
parts of each source (the release-note flag lists, the bulletin award tables,
the registry CSV) and the fixed sentence patterns the errata / correction /
retraction notices use.  The authority order in SOURCE_INDEX.md is applied
mechanically: the notices override the single statement they name, and nothing
below official_release_notes / registry_export is ever allowed to decide a value.

Usage:  python3 derive_C.py [--write]
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(KEYS_DIR)
CORPUS = os.path.join(ROOT, "corpora", "research_c")

FILES = sorted(os.listdir(CORPUS))
TEXT = {}
for f in FILES:
    with open(os.path.join(CORPUS, f), "r", encoding="utf-8") as fh:
        TEXT[f] = fh.read()

# ---- source index -------------------------------------------------------
INDEX = {}
for line in TEXT["SOURCE_INDEX.md"].split("\n"):
    m = re.match(r"^\| (\S+\.(?:md|csv)) \| (\w+) \| ([^|]+) \| (\d{4}-\d{2}-\d{2}) \|", line)
    if m:
        INDEX[m.group(1)] = {"source_tier": m.group(2),
                             "publisher": m.group(3).strip(),
                             "published": m.group(4)}
assert len(INDEX) == 49, len(INDEX)          # 50 files incl. the index itself
assert set(INDEX) | {"SOURCE_INDEX.md"} == set(FILES), set(FILES) ^ set(INDEX)

RELEASE_NOTES = sorted(f for f in INDEX if INDEX[f]["source_tier"] == "official_release_notes")


# ==========================================================================
# C-001  — feature-flag lifecycle
# ==========================================================================
def c001():
    added = {}     # flag -> {version: [files]}
    removed = {}   # flag -> {version: [files]}
    for f in RELEASE_NOTES:
        mode = None
        for line in TEXT[f].split("\n"):
            if "feature flags are **added**" in line:
                mode = "added"
                continue
            if "feature flags are **removed**" in line:
                mode = "removed"
                continue
            if line.startswith("## "):
                mode = None
                continue
            m = re.match(r"^- `([a-z_0-9]+)` — (?:new|removed) in ([0-9][0-9.]*)[,.]", line)
            if m and mode:
                flag, ver = m.group(1), m.group(2)
                tgt = added if mode == "added" else removed
                tgt.setdefault(flag, {}).setdefault(ver, []).append(f)

    # errata that correct the release in which a flag was added
    errata_fix = {}
    for f in sorted(INDEX):
        if INDEX[f]["source_tier"] != "erratum":
            continue
        m = re.search(
            r"The release notes for Kestrel Runtime ([0-9][0-9.]*) state that the feature flag "
            r"`([a-z_0-9]+)` was added in that release\. That statement is incorrect\.\s+"
            r"The flag `\2` was added in Kestrel Runtime ([0-9][0-9.]*)\.", TEXT[f])
        if m:
            wrong_ver, flag, right_ver = m.group(1), m.group(2), m.group(3)
            assert flag not in errata_fix
            errata_fix[flag] = {"file": f, "wrong_release": wrong_ver, "correct_release": right_ver}
    assert len(errata_fix) == 3, errata_fix

    flags = []
    coincidental, contradicting = {}, {}
    for flag in sorted(added):
        versions = added[flag]
        if flag in errata_fix:
            intro = errata_fix[flag]["correct_release"]
            # the erratum names the release note it contradicts; that note's
            # claim for this flag is withdrawn.
            wrong = errata_fix[flag]["wrong_release"]
            assert wrong in versions, (flag, wrong, versions)
            intro_files = sorted(set(versions.get(intro, [])) | {errata_fix[flag]["file"]})
        else:
            assert len(versions) == 1, (flag, versions)
            intro = next(iter(versions))
            intro_files = sorted(versions[intro])

        rem_versions = removed.get(flag, {})
        assert len(rem_versions) <= 1, (flag, rem_versions)
        if rem_versions:
            rem = next(iter(rem_versions))
            rem_files = sorted(rem_versions[rem])
        else:
            rem, rem_files = None, []

        # Low-authority chatter about this flag.  v1.1.0: this is a DERIVATION
        # DIAGNOSTIC only.  It is deliberately kept off the record, because the
        # record's `sources` and `citation_support` ARE the governing-source set
        # the traceability metric consumes, and a coincidentally-correct forum
        # thread is not a governing source (task rule (b)).  Putting it on the
        # record would either make it citable or make it mandatory to cite.
        others_agreeing, others_disagreeing = [], []
        for f in sorted(INDEX):
            if f in intro_files or f in rem_files or f in RELEASE_NOTES:
                continue
            for m in re.finditer(r"`%s`[^\n]*?\b([0-9]\.[0-9])\b" % re.escape(flag), TEXT[f]):
                (others_agreeing if m.group(1) == intro else others_disagreeing).append(f)
        if others_agreeing:
            coincidental[flag] = sorted(set(others_agreeing))
        if others_disagreeing:
            contradicting[flag] = sorted(set(others_disagreeing))

        governing = sorted(set(intro_files) | set(rem_files))
        flags.append({
            "flag": flag,
            "introduced_in": intro,
            "removed_in": rem,
            # The COMPLETE set of governing sources for the values of this
            # record -- not a curated subset.  Under the v1.1.0 metric a
            # governing source the run omits is a missing citation and a file
            # outside this set is an unsupported citation, symmetrically.
            "sources": governing,
            "citation_support": {
                # `flag` and `introduced_in` share one governing set under the
                # task's claim-to-source mapping.
                "flag": intro_files,
                "introduced_in": intro_files,
                # A null `removed_in` is not a claim and needs no citation.
                "removed_in": rem_files,
            },
        })

    diag = {
        "flags_with_two_added_claims": {k: sorted(v) for k, v in added.items() if len(v) > 1},
        "errata_corrections": errata_fix,
        "coincidentally_correct_non_governing_files": coincidental,
        "non_governing_files_stating_a_different_version": contradicting,
        "governing_source_rule": (
            "for `flag` and `introduced_in`: every official release note whose feature-flag "
            "list records the flag as added, MINUS the release note an erratum corrects for "
            "that flag, PLUS that erratum; for `removed_in`: the official release note whose "
            "feature-flag list records the flag as removed, and nothing when it is null"),
    }
    return {"flags": flags, "count": len(flags)}, diag


# ==========================================================================
# C-002  — Meridian awards
# ==========================================================================
def c002():
    awards = {}   # award_id -> {project, amount, bulletin}
    for f in sorted(INDEX):
        if INDEX[f]["source_tier"] != "official_bulletin":
            continue
        for line in TEXT[f].split("\n"):
            m = re.match(r"^\| (GA-\d+) \| ([^|]+?) \| (\d+) \|$", line)
            if m:
                aid = m.group(1)
                assert aid not in awards, aid
                awards[aid] = {"project": m.group(2).strip(),
                               "amount": int(m.group(3)),
                               "bulletin": f,
                               "status": "included",
                               "notice": None}

    notices = []
    for f in sorted(INDEX):
        tier = INDEX[f]["source_tier"]
        if tier == "correction_notice":
            m = re.search(
                r"Award \*\*(GA-\d+)\*\* to ([^ ]+ [^ ]+) was published in bulletin (BUL-[\d-]+) "
                r"with an amount of EUR (\d+)\. That amount is incorrect\.\s+"
                r"The correct award amount is \*\*EUR (\d+)\*\*\. The award remains in force\.",
                TEXT[f])
            assert m, f
            aid, old, new = m.group(1), int(m.group(4)), int(m.group(5))
            assert awards[aid]["amount"] == old, (f, aid)
            awards[aid]["amount"] = new
            awards[aid]["notice"] = f
            notices.append({"file": f, "kind": "correction", "award_id": aid,
                            "from_eur": old, "to_eur": new})
        elif tier == "retraction_notice":
            m = re.search(
                r"Award \*\*(GA-\d+)\*\* to ([^,]+), published in bulletin (BUL-[\d-]+), "
                r"is \*\*retracted in full\*\*\.", TEXT[f])
            assert m, f
            aid = m.group(1)
            awards[aid]["status"] = "excluded"
            awards[aid]["notice"] = f
            notices.append({"file": f, "kind": "retraction", "award_id": aid,
                            "amount_removed_eur": awards[aid]["amount"]})
    assert len(notices) == 5, notices

    projects = {}
    for aid in sorted(awards):
        a = awards[aid]
        p = projects.setdefault(a["project"], {
            "project": a["project"], "total_awarded_eur": 0,
            "awards_included": [], "awards_excluded": [], "srcs": set(),
            "support": {},
        })
        p["srcs"].add(a["bulletin"])
        if a["notice"]:
            p["srcs"].add(a["notice"])
        p.setdefault("by_field", {"project": set(), "total_awarded_eur": set(),
                                  "awards_included": set(), "awards_excluded": set()})
        bf = p["by_field"]
        bf["project"].add(a["bulletin"])
        # the file that states this award's STANDING amount or STANDING status
        standing = a["notice"] or a["bulletin"]
        bf["total_awarded_eur"].add(standing)
        if a["status"] == "included":
            p["total_awarded_eur"] += a["amount"]
            p["awards_included"].append(aid)
            bf["awards_included"].add(a["bulletin"])
            if a["notice"]:
                bf["awards_included"].add(a["notice"])
            p["support"][aid] = {"status": "included", "amount_eur": a["amount"],
                                 "standing_amount_stated_by": standing,
                                 "listed_in_bulletin": a["bulletin"]}
        else:
            p["awards_excluded"].append(aid)
            bf["awards_excluded"].add(a["bulletin"])
            bf["awards_excluded"].add(a["notice"])
            p["support"][aid] = {"status": "excluded", "retracted_by": a["notice"],
                                 "listed_in_bulletin": a["bulletin"]}

    out = []
    per_award = {}
    for name in sorted(projects):
        p = projects[name]
        governing = sorted(p["srcs"])
        cs = {k: sorted(v) for k, v in p["by_field"].items()}
        # The per-field sets must cover exactly the record's governing set.
        assert sorted(set().union(*cs.values())) == governing, (name, cs, governing)
        per_award[p["project"]] = p["support"]
        out.append({
            "project": p["project"],
            "total_awarded_eur": p["total_awarded_eur"],
            "awards_included": sorted(p["awards_included"]),
            "awards_excluded": sorted(p["awards_excluded"]),
            # COMPLETE governing-source set for this record: every bulletin that
            # publishes one of the project's awards, plus every correction and
            # retraction notice that changes the amount or the status of one of
            # them (task claim-to-source mapping).  No file states the sum, so
            # `total_awarded_eur` is supported by the files that state the
            # standing amount or standing status of its constituent awards.
            "sources": governing,
            "citation_support": cs,
        })
    return {"projects": out, "count": len(out)}, notices, per_award


# ==========================================================================
# C-003  — plugin compatibility
# ==========================================================================
def c003():
    reg_file = "registry_export_2032-02.csv"
    rows = list(csv.DictReader(TEXT[reg_file].splitlines()))
    assert rows and "plugin_id" in rows[0]

    errata_fix = {}
    for f in sorted(INDEX):
        if INDEX[f]["source_tier"] != "erratum":
            continue
        m = re.search(
            r"The registry export dated [\d-]+ records the minimum supported Kestrel Runtime "
            r"version for `([a-z0-9-]+)` incorrectly\.\s+"
            r"The correct minimum supported version for `\1` is \*\*([0-9][0-9.]*)\*\*\.", TEXT[f])
        if m:
            errata_fix[m.group(1)] = {"file": f, "correct": m.group(2)}
    assert len(errata_fix) == 2, errata_fix

    # every statement of a plugin minimum version anywhere in the corpus
    stated = {}   # plugin -> {version: [files]}
    for r in rows:
        stated.setdefault(r["plugin_id"], {}).setdefault(r["min_kestrel_version"], []).append(reg_file)
    for pid, fix in errata_fix.items():
        stated.setdefault(pid, {}).setdefault(fix["correct"], []).append(fix["file"])
    for f in sorted(INDEX):
        if INDEX[f]["source_tier"] not in ("vendor_blog", "community_forum"):
            continue
        for m in re.finditer(
                r"`([a-z0-9-]+)`(?: wants at least Kestrel | definitely needs )([0-9]\.[0-9])", TEXT[f]):
            stated.setdefault(m.group(1), {}).setdefault(m.group(2), []).append(f)

    plugins = []
    coincidental_by_plugin = {}
    for r in rows:
        pid = r["plugin_id"]
        if pid in errata_fix:
            ver = errata_fix[pid]["correct"]
            tier = INDEX[errata_fix[pid]["file"]]["source_tier"]
        else:
            ver = r["min_kestrel_version"]
            tier = INDEX[reg_file]["source_tier"]
        # The governing source is fixed by the task's claim-to-source mapping,
        # NOT by which files happen to print the same characters: the registry
        # export unless an erratum names this plugin, in which case the erratum
        # and the registry export is no longer a governing source.
        governing = [errata_fix[pid]["file"]] if pid in errata_fix else [reg_file]
        stating = sorted(set(stated[pid].get(ver, [])))
        assert set(governing) <= set(stating), (pid, governing, stating)
        coincidental = [f for f in stating if f not in governing]
        contradicting_all = sorted({f for v, fs in stated[pid].items() if v != ver for f in fs})
        plugins.append({
            "plugin_id": pid,
            "min_kestrel_version": ver,
            "governing_source_tier": tier,
            # literal reading, settled by RT-16: EVERY file of ANY tier that
            # states a different minimum version, the registry export included.
            "contradicted_by": contradicting_all,
            "sources": governing,
            "citation_support": {"plugin_id": governing,
                                 "min_kestrel_version": governing},
        })
        if coincidental:
            coincidental_by_plugin[pid] = coincidental
    plugins.sort(key=lambda p: p["plugin_id"])
    return {"plugins": plugins, "count": len(plugins)}, errata_fix, coincidental_by_plugin


# ==========================================================================
def main():
    write = "--write" in sys.argv
    c1, d1 = c001()
    c2, notices, per_award = c002()
    c3, fix3, coincidental3 = c003()

    keys = {
        "C-001": {
            "task_id": "C-001",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Parsed the '## Feature flags' list of every official release note for "
                "'added'/'removed' entries, then applied the three errata that name a flag and "
                "correct the release it was added in. Each record's `sources` is the COMPLETE "
                "governing-source set the v1.1.0 traceability metric requires, built from the "
                "task's claim-to-source mapping: the release notes recording the flag as added, "
                "minus the one an erratum corrects for that flag, plus that erratum, plus the "
                "release note recording the removal. Blog and forum statements are recorded in "
                "derivation_diagnostics and are never governing sources, whether they agree "
                "with the answer or not. Script: scripts/derive_C.py"
            ),
            "derivation_script": "scripts/derive_C.py",
            "derivation_diagnostics": d1,
            **c1,
        },
        "C-002": {
            "task_id": "C-002",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Parsed the award table of all eight bulletins, applied the three correction "
                "notices (asserting each stated original amount against the bulletin before "
                "replacing it) and the two retraction notices, then summed the surviving amounts "
                "per project. Forum totals are ignored. Each record's `sources` is the COMPLETE "
                "governing-source set the v1.1.0 traceability metric requires: every bulletin "
                "publishing one of the project's awards plus every correction and retraction "
                "notice affecting one of them. Script: scripts/derive_C.py"
            ),
            "derivation_script": "scripts/derive_C.py",
            "notices_applied": notices,
            "derivation_diagnostics": {
                "per_award_standing_values": per_award,
                "note": ("no single file states total_awarded_eur; it is the sum of the "
                         "per-award amounts that stand after the notices are applied. This "
                         "block is a diagnostic and is NOT part of any record's "
                         "governing-source set."),
            },
            **c2,
        },
        "C-003": {
            "task_id": "C-003",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Read registry_export_2032-02.csv, overrode the two plugins named by errata "
                "ERR-004/ERR-005, and swept every vendor_blog and community_forum file (plus the "
                "registry export itself) for statements of a different minimum version to build "
                "contradicted_by. Script: scripts/derive_C.py"
            ),
            "derivation_script": "scripts/derive_C.py",
            "errata_applied": fix3,
            "contradicted_by_reading": (
                "literal, and settled by RT-16: any corpus file of any tier that states a "
                "different min version for the plugin, including registry_export_2032-02.csv "
                "for the two erratum-corrected plugins. The v1.0.0 key's "
                "`contradicted_by_alternate_reading_low_authority_only` field is withdrawn."
            ),
            "derivation_diagnostics": {
                "coincidentally_correct_non_governing_files": coincidental3,
                "note": ("files that state the governing value but do not govern it. Kept off "
                         "the records: under the v1.1.0 citation rule they are neither citable "
                         "nor required."),
            },
            **c3,
        },
    }

    if write:
        for tid, obj in keys.items():
            p = os.path.join(KEYS_DIR, f"{tid}.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(obj, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            print("wrote", p, file=sys.stderr)
    else:
        print(json.dumps(keys, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

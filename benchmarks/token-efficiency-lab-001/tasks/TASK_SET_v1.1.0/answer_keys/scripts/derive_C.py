#!/usr/bin/env python3
"""Derive answer keys for workload C (C-001..C-003) of TASK_SET_v1.0.0.

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

        # every other file in the corpus that literally states a version for
        # this flag (low-authority chatter); recorded so a grader can tell a
        # coincidentally-correct forum citation from a wrong one.
        others_agreeing, others_disagreeing = [], []
        for f in sorted(INDEX):
            if f in intro_files or f in rem_files or f in RELEASE_NOTES:
                continue
            for m in re.finditer(r"`%s`[^\n]*?\b([0-9]\.[0-9])\b" % re.escape(flag), TEXT[f]):
                (others_agreeing if m.group(1) == intro else others_disagreeing).append(f)
        flags.append({
            "flag": flag,
            "introduced_in": intro,
            "removed_in": rem,
            "sources": sorted(set(intro_files) | set(rem_files)),
            "citation_support": {
                "introduced_in": intro_files,
                "removed_in": rem_files,
            },
            "non_authoritative_files_stating_the_same_introduced_in": sorted(set(others_agreeing)),
            "non_authoritative_files_stating_a_different_version": sorted(set(others_disagreeing)),
        })

    diag = {
        "flags_with_two_added_claims": {k: sorted(v) for k, v in added.items() if len(v) > 1},
        "errata_corrections": errata_fix,
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
        if a["status"] == "included":
            p["total_awarded_eur"] += a["amount"]
            p["awards_included"].append(aid)
            p["support"][aid] = {"amount_eur": a["amount"],
                                 "stated_by": a["notice"] or a["bulletin"],
                                 "listed_in_bulletin": a["bulletin"]}
        else:
            p["awards_excluded"].append(aid)
            p["support"][aid] = {"retracted_by": a["notice"],
                                 "listed_in_bulletin": a["bulletin"]}

    out = []
    for name in sorted(projects):
        p = projects[name]
        out.append({
            "project": p["project"],
            "total_awarded_eur": p["total_awarded_eur"],
            "awards_included": sorted(p["awards_included"]),
            "awards_excluded": sorted(p["awards_excluded"]),
            "sources": sorted(p["srcs"]),
            "citation_support": {
                "per_award": p["support"],
                "note": ("no single file states total_awarded_eur; it is the sum of the "
                         "per-award amounts that stand after the notices are applied"),
            },
        })
    return {"projects": out, "count": len(out)}, notices


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
    for r in rows:
        pid = r["plugin_id"]
        if pid in errata_fix:
            ver = errata_fix[pid]["correct"]
            tier = INDEX[errata_fix[pid]["file"]]["source_tier"]
        else:
            ver = r["min_kestrel_version"]
            tier = INDEX[reg_file]["source_tier"]
        support = sorted(set(stated[pid].get(ver, [])))
        contradicting_all = sorted({f for v, fs in stated[pid].items() if v != ver for f in fs})
        contradicting_low = [f for f in contradicting_all
                             if INDEX[f]["source_tier"] in ("vendor_blog", "community_forum")]
        plugins.append({
            "plugin_id": pid,
            "min_kestrel_version": ver,
            "governing_source_tier": tier,
            "contradicted_by": contradicting_all,
            "sources": [f for f in support
                        if INDEX[f]["source_tier"] in ("registry_export", "erratum")],
            "citation_support": {"min_kestrel_version": support},
            "contradicted_by_alternate_reading_low_authority_only": contradicting_low,
        })
    plugins.sort(key=lambda p: p["plugin_id"])
    return {"plugins": plugins, "count": len(plugins)}, errata_fix


# ==========================================================================
def main():
    write = "--write" in sys.argv
    c1, d1 = c001()
    c2, notices = c002()
    c3, fix3 = c003()

    keys = {
        "C-001": {
            "task_id": "C-001",
            "derived_by": "answer-key-builder",
            "derivation_method": (
                "Parsed the '## Feature flags' list of every official release note for "
                "'added'/'removed' entries, then applied the three errata that name a flag and "
                "correct the release it was added in. Blog and forum statements are recorded but "
                "never allowed to decide a value. Script: scripts/derive_C.py"
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
                "per project. Forum totals are ignored. Script: scripts/derive_C.py"
            ),
            "derivation_script": "scripts/derive_C.py",
            "notices_applied": notices,
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
                "literal: any corpus file that states a different min version for the plugin, "
                "including registry_export_2032-02.csv for the two erratum-corrected plugins. "
                "See BUILDER_NOTES.md C-003 ambiguity 1 and the per-record "
                "contradicted_by_alternate_reading_low_authority_only field."
            ),
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

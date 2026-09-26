#!/usr/bin/env python3
"""Regression tests for the content / learning package contract.

Each fixture in schemas/fixtures/ exists to make one rule fail. The test asserts
BOTH the verdict AND which rule produced it, because a fixture that blocks for
the wrong reason is a passing test that proves nothing.

Two controls are included on purpose:

  * t_09_valid_fixtures_pass — if the valid fixtures ever start failing, the
    invalid ones blocking tells us nothing. A gate that refuses everything is
    as useless as one that refuses nothing.
  * t_16_unsupported_keyword_is_loud — the subset validator must refuse a
    schema it cannot fully evaluate rather than skipping the keyword. Silently
    ignoring a constraint reports PASS on a document nobody checked.

Usage: python3 tools/test_packages.py
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from jsonschema_mini import SchemaStore, UnsupportedKeyword, validate  # noqa: E402
from validate_packages import canonical_hash, check_file, load_seat_ids  # noqa: E402

FIX = ROOT / "schemas" / "fixtures"
SAMPLES = ROOT / "magazine" / "samples"
STORE = SchemaStore(ROOT / "schemas")
SEATS = load_seat_ids(ROOT / "agents" / "SEAT_REGISTRY.json")
RESULTS: list[tuple[bool, str]] = []


def run(name, *, adopt=False, as_of=None, seats=SEATS):
    return check_file(FIX / name if not str(name).startswith("/") else pathlib.Path(name),
                      STORE, adopt=adopt, as_of=as_of, seat_ids=seats)


def reseal(pkg: dict) -> dict:
    """Recompute the hash and re-bind approvals — i.e. the content was re-approved."""
    digest = canonical_hash(pkg)
    pkg["content_hash"] = digest
    for entry in pkg.get("approvals") or []:
        if entry.get("decision") == "APPROVED":
            entry["scope_hash"] = digest
    return pkg


def expect(cond, label):
    RESULTS.append((bool(cond), label))


def blocked_by(result, rule):
    return any(m.startswith(rule + ":") for m in result["semantics"])


def t_01_valid_data_passes():
    for f in ("content/valid-draft.json", "content/valid-publishable.json",
              "learning/valid-draft.json", "learning/valid-publishable.json"):
        r = run(f)
        expect(r["verdict"] == "PASS", f"01 有效資料通過：{f} → {r['verdict']} "
                                       f"{r['structure']}{r['semantics']}")


def t_02_missing_source_blocked():
    r = run("content/invalid-missing-source.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P1"), "02 缺來源被阻擋（引用未宣告的來源）")
    r = run("content/invalid-no-source-refs.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P1") and r["structure"],
           "02b 完全沒有 source_refs：結構層與語意層都擋")


def t_03_unknown_evidence_state_blocked():
    r = run("content/invalid-unknown-evidence-state.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P2") and r["structure"],
           "03 未知證據等級被阻擋（enum 與 P2 皆觸發）")


def t_04_expired_or_retracted_not_adoptable():
    r = run("learning/expired.json", adopt=True, as_of="2026-09-16")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P5"), "04a 過期包不得供新採用")
    r = run("learning/retracted-with-cause.json", adopt=True, as_of="2026-09-16")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P5"), "04b 撤回包不得供新採用")
    # 同一份過期包在非採用情境只是一則 note，不是 BLOCK——讀舊檔與採用舊檔是兩件事
    r = run("learning/expired.json", adopt=False, as_of="2026-09-16")
    expect(r["verdict"] == "PASS" and any("P5-note" in n for n in r["notes"]),
           "04c 非採用情境下過期只記 note：讀歷史不等於採用")


def t_05_hash_mismatch_blocked():
    r = run("content/invalid-hash-mismatch.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P6"), "05 版本或 hash 不符被阻擋")
    expect(sum(1 for m in r["semantics"] if m.startswith("P6:")) == 2,
           "05b 內容被改動後，content_hash 與該筆核准的 scope_hash 同時失效")


def t_06_unknown_seat_blocked():
    r = run("content/invalid-unknown-seat.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P14"), "06 不存在的角色映射被阻擋")
    # 未提供 registry 時不得假裝檢查過
    r = run("content/invalid-unknown-seat.json", seats=None)
    expect(r["verdict"] == "PASS", "06b 未提供席位登錄時不做該項檢查，也不謊稱通過")


def t_07_self_approval_blocked():
    r = run("content/invalid-self-approval.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P4"), "07 作者自我核准被阻擋")
    expect(sum(1 for m in r["semantics"] if m.startswith("P4:")) == 2,
           "07b 同時擋下「作者兼覆核」與「作者出具核准決定」兩種形式")


def t_08_publishable_gate():
    r = run("content/invalid-publishable-no-expiry.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P3"), "08 可發布狀態必須有有效期與未知項")
    r = run("learning/invalid-publishable-no-tests.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P7"), "08b 缺必要測試的知識包不得標為可發布")


def t_09_valid_fixtures_pass():
    """對照組：尺不能是一把什麼都擋的尺。"""
    passes = [f for f in sorted(FIX.rglob("*.json"))
              if check_file(f, STORE, adopt=False, as_of=None, seat_ids=SEATS)["verdict"] == "PASS"]
    expect(len(passes) >= 4, f"09 對照組：至少 4 個 fixture 必須通過，實得 {len(passes)}")


def t_10_draft_without_expiry_is_allowed():
    """草稿可以沒有有效期。

    這個測試第一次寫錯過，錯法值得留著：只重算 content_hash 而沒有重新核准，
    validator 便以 P6 擋下——因為改了內容之後，原本那筆核准committed 的是
    另一份東西。**尺是對的，測試是錯的**，所以改的是測試不是尺。
    改內容就要重新核准，這裡用 reseal() 明確表示「已重新核准」。
    """
    pkg = json.loads((FIX / "content/valid-draft.json").read_text(encoding="utf-8"))
    pkg["valid_until"] = None
    reseal(pkg)
    tmp = FIX / "content" / ".tmp-draft-no-expiry.json"
    tmp.write_text(json.dumps(pkg, ensure_ascii=False), encoding="utf-8")
    r = check_file(tmp, STORE, adopt=False, as_of=None, seat_ids=SEATS)
    tmp.unlink()
    expect(r["verdict"] == "PASS", "10 草稿可以沒有有效期；只有可發布狀態才要求")


def t_11_governance_must_fail_closed():
    r = run("learning/invalid-governance-warn-only.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P9"),
           "11 治理類知識包不得設成 warn_only——可以被設定關掉的煞車不是煞車")


def t_12_atk_stays_optional():
    r = run("learning/invalid-requires-atk-key.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P10"),
           "12 知識取用不得以購買 ATK 推論為條件")


def t_13_rule_needs_more_than_reported():
    r = run("learning/invalid-rule-on-reported-only.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P11"),
           "13 已發布的決策規則不得只靠 REPORTED 支撐")
    r = run("learning/invalid-rule-unknown-claim.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P11"), "13b 決策規則不得引用不存在的 claim")


def t_14_retraction_names_its_cause():
    r = run("learning/invalid-retracted-no-cause.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P8"),
           "14 撤回必須指名 revoked_by 或 superseded_by")
    r = run("learning/invalid-self-supersedes.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P12"), "14b 不得自我取代")


def t_15_summarised_source_cannot_support_observed():
    r = run("content/invalid-observed-from-summary.json")
    expect(r["verdict"] == "BLOCK" and blocked_by(r, "P13"),
           "15 摘要式取得的來源不得支撐 OBSERVED 以上")


def t_16_unsupported_keyword_is_loud():
    try:
        validate({}, {"format": "date"}, STORE, {})
        expect(False, "16 未支援的 schema 關鍵字必須拋錯（實際靜默通過）")
    except UnsupportedKeyword:
        expect(True, "16 未支援的 schema 關鍵字必須拋錯，不得靜默略過")


def t_17_human_and_machine_versions_agree():
    """人類版與機器版共享 claim、來源與證據狀態；機器版不得刪掉 limitation。"""
    for d in sorted(SAMPLES.iterdir()):
        c = json.loads((d / "content-package.json").read_text(encoding="utf-8"))
        l = json.loads((d / "learning-package.json").read_text(encoding="utf-8"))
        cc = {x["claim_id"]: x for x in c["claims"]}
        lc = {x["claim_id"]: x for x in l["claims"]}
        expect(set(cc) == set(lc), f"17 {d.name} 人機兩版 claim_id 集合一致")
        same_state = all(cc[k]["evidence_state"] == lc[k]["evidence_state"] for k in cc if k in lc)
        expect(same_state, f"17b {d.name} 人機兩版證據狀態一致")
        kept = all(any(x in lim for lim in l["limitations"]) or True for x in [])
        expect(set(c["limitations"]).issubset(set(l["limitations"])),
               f"17c {d.name} 機器版未刪掉人類版的任一條 limitation")
        expect(c.get("machine_counterpart") == l["package_id"]
               and l.get("human_counterpart") == c["package_id"],
               f"17d {d.name} 人機兩版互相指認")


def t_18_samples_pass_and_are_sealed():
    for f in sorted(SAMPLES.rglob("*.json")):
        r = check_file(f, STORE, adopt=False, as_of=None, seat_ids=SEATS)
        expect(r["verdict"] == "PASS",
               f"18 樣本通過資料規格檢查：{f.name} in {f.parent.name} → {r['verdict']} "
               f"{r['structure']}{r['semantics']}")


def t_19_samples_are_drafts_not_published():
    """樣本不得自稱已發布。本輪沒有人類出版責任窗口，沒有東西可以是 published。"""
    for f in sorted(SAMPLES.rglob("*.json")):
        pkg = json.loads(f.read_text(encoding="utf-8"))
        expect(pkg["status"] == "draft", f"19 {f.parent.name}/{f.name} 狀態必須是 draft")
        expect(pkg["authorship"]["human_responsible"] is None,
               f"19b {f.parent.name}/{f.name} 未指派人類責任窗口，必須據實留 null")


def main() -> int:
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("t_")]:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            RESULTS.append((False, f"{fn.__name__} 拋出例外：{exc!r}"))
    print()
    for ok, name in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    bad = [n for ok, n in RESULTS if not ok]
    print(f"\n  {len(RESULTS) - len(bad)}/{len(RESULTS)} 通過\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

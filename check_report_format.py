#!/usr/bin/env python3
"""固定回報格式自查（REPORT-FORMAT-20260926）。

檢查一份回報是否依序具備四個固定標題，且必填欄位都有內容：
  1. 執行者／2. 小目標進度／3. 目標藍圖對齊／4. 本次執行的意義
用法：python3 check_report_format.py <檔案>   或   ... | python3 check_report_format.py -
另一種用法：python3 check_report_format.py --pointers
  驗「入口宣稱的階段數」與「REPORT_FORMAT.md 階段表實際列數」是否一致。
  刻意併進本檔而不另開一支：本 repo 已因平行造輪撞過三次，第三支檢核器
  會讓「哪一支才算數」重新變成問題。
通過 exit 0；不通過 exit 1，並逐條列出問題。只用標準函式庫。
"""
import re
import sys

TITLES = ["執行者", "小目標進度", "目標藍圖對齊", "本次執行的意義"]
HEAD = re.compile(r"^\s*#{0,6}\s*\**\s*([1-4])\s*[.．、]\s*(執行者|小目標進度|目標藍圖對齊|本次執行的意義)\s*\**\s*$")
FIELD = re.compile(r"^\s*[-*•]?\s*([^：:]+)[：:]\s*(.*)$")

# (項次, 欄位關鍵字, 允許的開頭值；None 表示只要非空)
REQUIRED = [
    (1, "誰執行", None),
    (2, "往哪個小目標", None),
    (2, "小目標階段", None),
    (2, "有沒有前進", ("有", "沒有", "倒退")),
    (2, "困難", None),
    (2, "決策", None),
    (2, "缺乏什麼資訊", None),
    (3, "目標藍圖", None),
    (3, "哪一個階段", None),
    (3, "遵照藍圖", ("是", "否")),
    (3, "距離藍圖方向", ("前進", "原地", "後退")),
]


def check(text):
    problems, sections, order = [], {}, []
    current = None
    for line in text.splitlines():
        m = HEAD.match(line)
        if m:
            n = int(m.group(1))
            if TITLES[n - 1] != m.group(2):
                problems.append(f"第 {n} 項標題應為「{n}. {TITLES[n - 1]}」，實際是「{m.group(2)}」")
            if n in sections:
                problems.append(f"第 {n} 項重複出現")
            order.append(n)
            sections[n] = []
            current = n
        elif current:
            sections[current].append(line)

    for n in range(1, 5):
        if n not in sections:
            problems.append(f"缺少第 {n} 項「{n}. {TITLES[n - 1]}」")
    if order and order != sorted(order):
        problems.append(f"四項順序錯誤：{order}，必須是 1→2→3→4")

    for n, lines in sections.items():
        if not "".join(lines).strip():
            problems.append(f"第 {n} 項「{TITLES[n - 1]}」沒有內容")

    for n, key, allowed in REQUIRED:
        if n not in sections:
            continue
        value = None
        for line in sections[n]:
            m = FIELD.match(line)
            if m and key in m.group(1):
                value = m.group(2).strip()
                break
        if value is None:
            problems.append(f"第 {n} 項缺少欄位「{key}」")
        elif not value:
            problems.append(f"第 {n} 項欄位「{key}」是空的（沒有就寫「無」）")
        elif allowed and not re.match(r"^(" + "|".join(allowed) + r")(?=\s|—|-|－|（|\(|$)", value):
            problems.append(f"第 {n} 項「{key}」只能填 {'／'.join(allowed)}，實際是「{value[:20]}」")
        elif key == "有沒有前進" and "證據" not in value:
            problems.append("第 2 項「有沒有前進」必須附「證據：」")

    if 4 in sections and len("".join(sections[4]).strip()) < 10:
        problems.append("第 4 項「本次執行的意義」太短，請用大白話寫兩到三句")
    return problems


# ---- 入口一致性檢查（--pointers）------------------------------------------
# 由來：GPT 2026-09-26 PR #21 覆核 P3——入口寫「五階段」，本地表實際六階段。
# 「寫五」與「寫六」兩句話都讀得通，只有去數那張表才分得出來，所以要機器數。
POINTER_FILES = ["CLAUDE.md", ".claude/skills/execution-report/SKILL.md"]
TABLE_FILE = "REPORT_FORMAT.md"
CN = "〇一二三四五六七八九十"
STAGE_CLAIM = re.compile(r"([〇一二三四五六七八九十]+|\d+)\s*階段")


def _cn2int(t):
    if t.isdigit():
        return int(t)
    if t == "十":
        return 10
    if len(t) == 1:
        return CN.index(t)
    if t.startswith("十"):
        return 10 + CN.index(t[1])
    if t.endswith("十"):
        return CN.index(t[0]) * 10
    return CN.index(t[0]) * 10 + CN.index(t[2])


def count_stage_rows(text):
    """數階段表實際有幾列（第一欄是純數字的表格列）。"""
    n = 0
    for line in text.splitlines():
        m = re.match(r"^\s*\|\s*(\d+)\s*\|", line)
        if m:
            n += 1
    return n


def check_pointers(root="."):
    import os
    problems = []
    tpath = os.path.join(root, TABLE_FILE)
    if not os.path.exists(tpath):
        return [f"找不到 {TABLE_FILE}，無法取得階段表實際列數"]
    actual = count_stage_rows(open(tpath, encoding="utf-8").read())
    if actual == 0:
        # 數到 0 不是「表是空的」，多半是表格格式變了而這支沒跟上。
        return [f"{TABLE_FILE} 的階段表數到 0 列——這通常是檢核器沒跟上格式，不是表沒了"]
    checked = 0
    for rel in POINTER_FILES:
        fp = os.path.join(root, rel)
        if not os.path.exists(fp):
            problems.append(f"入口檔不存在：{rel}")
            continue
        checked += 1
        for line_no, line in enumerate(open(fp, encoding="utf-8"), 1):
            for m in STAGE_CLAIM.finditer(line):
                claimed = _cn2int(m.group(1))
                if claimed != actual:
                    problems.append(
                        f"{rel}:{line_no} 宣稱「{m.group(0)}」，"
                        f"但 {TABLE_FILE} 的階段表實際是 {actual} 列")
    if checked == 0:
        problems.append("一個入口檔都沒掃到——這是沒掃到，不是通過")
    return problems


def main_pointers(root="."):
    problems = check_pointers(root)
    if problems:
        print("入口一致性不通過：")
        for p in problems:
            print(f"  ✗ {p}")
        return 1
    print(f"入口一致性通過：{len(POINTER_FILES)} 份入口宣稱的階段數與 {TABLE_FILE} 的表一致")
    return 0


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--pointers":
        return main_pointers()
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    text = sys.stdin.read() if sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8").read()
    problems = check(text)
    if problems:
        print("回報格式不通過：")
        for p in problems:
            print(f"  ✗ {p}")
        return 1
    print("回報格式通過：四項齊全、順序正確、必填欄位已填")
    return 0


if __name__ == "__main__":
    sys.exit(main())

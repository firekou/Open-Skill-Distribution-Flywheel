#!/usr/bin/env python3
"""固定回報格式自查（REPORT-FORMAT-20260926）。

檢查一份回報是否依序具備四個固定標題，且必填欄位都有內容：
  1. 執行者／2. 小目標進度／3. 目標藍圖對齊／4. 本次執行的意義
用法：python3 check_report_format.py <檔案>   或   ... | python3 check_report_format.py -
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


def main():
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

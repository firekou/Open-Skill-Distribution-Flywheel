---
name: execution-report
description: 本 repo 的回報格式入口（薄引用）。四節強制格式的唯一定義在 firekou/virtual-strategy-lab 的 .claude/skills/execution-report.md；本檔只負責把人指過去、記下採用的版本、並指出本 repo 自己的目標藍圖在哪。任何一次執行動作結束要回報時使用。
---

<!-- REPORT-FORMAT-POINTER 本檔是薄引用入口，不是規則定義 -->

# 執行回報（薄引用入口）

## 規則本文不在這裡

| | |
|---|---|
| canonical repo | `firekou/virtual-strategy-lab` |
| canonical path | `.claude/skills/execution-report.md` |
| 採用的 commit | `06b7dcb58b090597ee4c9da379b00dd1fc67b9f0` |
| 採用的檔案 blob | `7fa730fb17a103e2b55729816e9f56e001e2f204` |
| 同步日期 | 2026-09-26 |

**本檔刻意不抄一份規則。** 2026-09-26 一天之內，同一條指示被四個平行 session
各做成一份成品，四份都自稱唯一格式、而且各有對方漏掉的硬要求。
**多一份拷貝不是多一層保險，是多一個會各自漂移的定義。**

## 你現在要做的事

1. **四節照寫，缺一即未完成回報：**
   `1. 執行者` ／ `2. 小目標進度` ／ `3. 目標藍圖對齊` ／ `4. 本次執行的意義`
2. **填寫範本與逐欄規則：** 讀本 repo 的 [`REPORT_FORMAT.md`](../../../REPORT_FORMAT.md)。
3. **送出前自查：** `python3 check_report_format.py <回報檔>`，不通過不得送出。
4. **完整規則與由來：** 讀上表的 canonical。

## ⚠️ 第 3 節在本 repo 對齊的是本 repo 自己的藍圖

來源＝`governance/OPERATING_RULES.md`「使命與定位」（GOAL-02）＋ `governance/OUTCOME_CONFIDENCE.md`，
一句話與五階段表照抄 `REPORT_FORMAT.md` §「本 repo 的目標藍圖」。**修改須經 Frank 核定。**

**不得照抄 virtual-strategy-lab 的五條業務主線來對齊本 repo 的工作。**
共同的是「回報怎麼寫」，不共同的是「這個 repo 要去哪裡」——
2026-09-26 稍早有一版把兩者一起抄了過來，已依 GPT 裁定收回。

## 版本紀律

採用 canonical 新版本時**以差異確認更新**並改上表的 commit 與 blob。
**不得以「已同步 main」宣稱已更新**——main 是浮動的，
「我對過了」與「我當時對的是哪一版」是兩件事，只有後者事後查得到。

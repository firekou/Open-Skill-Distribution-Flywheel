# Claude repository entry

## ★ 固定回報格式（強制，最優先）

每一次執行完動作的回報，一律依 [REPORT_FORMAT.md](REPORT_FORMAT.md) 的四項固定格式：
**1. 執行者／2. 小目標進度／3. 目標藍圖對齊／4. 本次執行的意義**。
四項不可改名、調換、合併或省略；第 3 項每次都要照抄本 repo 的目標藍圖一句話。其他既有回報格式放進第 2 項或附件，不得取代這四項。送出前用 `python3 check_report_format.py <回報檔>` 自查。（Frank 2026-09-26 核定，REPORT-FORMAT-20260926）

先讀 [AGENTS.md](AGENTS.md)，再依 [governance/OPERATING_RULES.md](governance/OPERATING_RULES.md) 執行。
本檔不另維護規則或待辦。讀 decisions.json 復用已批准決策，讀 state.json 後核對 live head。
產品任務與治理導入分開，回覆與證據寫 reviews/。沒有實際runtime觸發證據，不宣稱自動喚醒另一Agent。

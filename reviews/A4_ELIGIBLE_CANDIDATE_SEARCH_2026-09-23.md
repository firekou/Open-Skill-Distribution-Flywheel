# A4 合格候選搜尋結果（執行頁）

**搜尋時間：** 2026-09-23 23:38–23:45 Asia/Taipei（CST, UTC+8）  
**執行：** 趨勢探（Open-Skill Trend Scout / ATK）  
**範圍核定：** 愛莎已准；飛輪長已准執行  
**資產唯一問題：** 對**這一則**長、機器產生的**純文字** payload，在 headroom **0.37.0**、走 **OpenAI chat-completions** 路由時，到達上游的 body 是否變小，且關鍵那一行是否還在？  
**本輪邀請狀態：** Eligible＝0 → **維持關閉**（不發）。補到 ≥1 仍須標「待另令准發」；本頁僅搜尋證據。

---

## 1. 通道／關鍵字／篩選

| 項 | 內容 |
|---|---|
| Repo | `headroomlabs-ai/headroom` |
| S1 | Discussions **Q&A**（`category_id=DIC_kwDOQ1mH3c4C8ZYj`），`order_by=UPDATED_AT`，全頁 39 則 |
| S2 | General（28）＋ Ideas（7）；僅當標題／首帖明確 compress／payload size／line survival；**排除** Show-and-tell／純功能許願 |
| S3 | Issues 關鍵字搜尋（compress／compression／payload／needle／survival／openai／bytes／0.37／chat completions 等）→ **僅線索**，預設不可當 A4 邀請對象 |
| S4 | 上游／相鄰 repo Discussions → **本輪 SKIP** |
| S5 | WITHDRAWN C1 `#2732`、C2 `#973` → 檢查作者是否有**新留言**把問題改寫成資產能答；**無則不重開** |
| 時間窗 | 自 2026-09-23 往回 90 天（約 2026-06-25）＋當日仍 open 的更早帖；窗外需另准者標「陳舊」 |
| 硬閘 | 三欄全過才 ELIGIBLE；不放寬湊滿 3 人 |

**關鍵字過濾：** compress, compression, payload, size, bytes, needle, survival, line still there, chat completions, openai, 0.37, context shrink, machine-generated text

---

## 2. 檢視量

| 計量 | 數 |
|---|---|
| S1 Q&A 列表檢視 | 39 |
| S2 General／Ideas 列表檢視 | 28＋7＝35 |
| 深入讀取全文（get_discussion／get_issue／comments） | 約 16 |
| Issues 搜尋去重命中（供 S3 線索掃描） | 67 |
| **納入下表列數** | **10**（上限 10） |
| **Eligible_count** | **0** |

---

## 3. 判定表（≤10）

| # | URL | 作者 | 問題摘要 | 欄1 對方問題 | 欄2 資產能做 | 欄3 停在哪 | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | https://github.com/headroomlabs-ai/headroom/discussions/2732 | @timedr128 | `[HEADROOM] skipped: unsupported commandcode request shape`；後續問 9router 是否影響 request shape | **fail**：request shape／Command Code／9router（原 C1 拒因） | **fail**：非 bytes＋needle on OpenAI chat-completions | **fail**：要的是協議／繞送相容 | **WITHDRAWN_STILL** |
| 2 | https://github.com/headroomlabs-ai/headroom/discussions/973 | @kulig1985 | 如何把 Anthropic 請求代理到自訂 upstream（類比 OpenAI） | **fail**：只要 Anthropic `/v1/messages` 代理（原 C2） | **fail**：資產不答 Anthropic 路由 | **fail**：停在自訂 Anthropic upstream | **WITHDRAWN_STILL** |
| 3 | https://github.com/headroomlabs-ai/headroom/discussions/3614 | @WakifRajin | library `compress()` 在 FastAPI＋WebSocket 並發是否安全、CCR cache 範圍、磁碟成長 | **fail**：問 concurrency／cache 生命週期，非「這則 payload 變小＋needle 存活」 | **fail**：非 pinned 0.37.0 OpenAI chat-completions 路徑測量 | **fail**：library 服務架構 | **NOT_ELIGIBLE_FOR_THIS_ASSET** |
| 4 | https://github.com/headroomlabs-ai/headroom/discussions/1099 | @kishankamlesh | `headroom perf` 幾乎無節省；image compression 出現負節省、是否實際 bloating | **edge→fail**：有 bytes／savings 測量感，但是**影像**壓縮與 Claude Code 路徑，非長純文字＋needle | **fail**：非 OpenAI chat-completions 純文字 needle survival | **fail**：影像／logging bug vs Claude 用量 | **NOT_ELIGIBLE_FOR_THIS_ASSET** |
| 5 | https://github.com/headroomlabs-ai/headroom/discussions/3276 | @Depechie | Docker＋Bedrock；幾乎立刻 session compacting／compacting failed（**已 closed**） | **fail**：Bedrock／Claude compacting 頻率，非 needle 存活測量 | **fail**：非 OpenAI chat-completions 0.37.0 資產路徑 | **fail**：Bedrock 設定可用性；且已關閉 | **NOT_ELIGIBLE_FOR_THIS_ASSET** |
| 6 | https://github.com/headroomlabs-ai/headroom/discussions/3519 | @Jeevankk28 | **0.37.0** 是否支援 Redis 存 CCR、如何設定 | **fail**：CCR 外部儲存，非 compress／payload／needle | **fail**：資產不做 Redis／CCR persistence | **fail**：儲存後端問題 | **NOT_ELIGIBLE_FOR_THIS_ASSET** |
| 7 | https://github.com/headroomlabs-ai/headroom/discussions/2170 | @feiai2026 | General：提議 context selection × reversible compression 2×2 benchmark 合作 | **fail**：研究設計／合作提議，非「這一則」payload 的 bytes＋needle 公問 | **fail**：範圍遠大於 pinned OpenAI chat-completions 單路徑測量 | **fail**：功能／實驗許願（Ideas 鄰近） | **NOT_ELIGIBLE_FOR_THIS_ASSET** |
| 8 | https://github.com/headroomlabs-ai/headroom/discussions/3289 | @zqy1-1 | 「對中文上下文有效果嗎？」（僅「如題」） | **fail**：過寬；無可還原的 payload／路由／版本／needle 測量句 | **fail**：無法對上資產唯一問題 | **fail**：一般效果問句 | **NOT_ELIGIBLE_FOR_THIS_ASSET** |
| 9 | https://github.com/headroomlabs-ai/headroom/issues/3673 | @afernandez-stratio | 0.37.0；單行 JSON 經 Kompress 刪整筆 record；in/out bytes；OpenAI-compatible streaming chat completions；已附 repro | **edge 主題**：bytes 變小＋關鍵結構／內容消失；但屬 **JSON record**，且 **bug tracker 已自備完整 repro**（明確拒因） | 主題鄰近 OpenAI chat 路徑，但資產是**純文字 needle 存活測量**，非修 Kompress／JSON 邊界刪除 | Issue＝S3；預設非 A4 邀請通道 | **CLUE_ISSUE_ONLY**（若開例外通道須愛莎另准） |
| 10 | https://github.com/headroomlabs-ai/headroom/issues/3736 | @haha0815 | **0.38.0** MCP `headroom_compress` 把 timestamp log 折成 5 行且改時間戳；對照 0.37.0 行為；已附 repro | **fail**：版本≠0.37.0 損失回報（**#3736 類明確拒因**）；路徑為 MCP compress 非 proxy OpenAI chat-completions | **fail**：資產 pinned 0.37.0 chat-completions | Issue；且已有 repro | **CLUE_ISSUE_ONLY**／明示拒因（不當邀請） |

**未列但已掃過的代表不合格（摘要）：** #2487／#1175（RTK 安裝）、#2800（已 answered：tool_search 注入）、#1856（stream compressed＋crash）、#826（deferred tools 吃 context）、#1482（已 answered：Cline OpenRouter 設定）、Ideas #2617（「not with compression」功能文）等——皆未過三欄閘。

---

## 4. Eligible_count

```
Eligible_count: 0
```

**與關閉輪關係：** 合格列＝0 → **建議維持邀請關閉**。若要再補供給，需愛莎另准擴大範圍（例如 S3 例外通道、S4 上游 Discussions、或放寬 ICP——**本執行頁不自行放寬**）。  
若未來出現 ≥1 ELIGIBLE，仍必須標 **「待另令准發」**，不得直接發邀請。

---

## 5. S5 WITHDRAWN 重開檢查

| ID | 作者新留言？ | 是否把問題改寫成資產能答？ | 處置 |
|---|---|---|---|
| C1 #2732 | 有（2026-08-29）：感謝並追問 **9router** 對 request shape／headers 的影響 | **否**（仍是 request-shape／Command Code／9router） | **不重開** → `WITHDRAWN_STILL` |
| C2 #973 | 無作者新 reframing；僅他人 2026-08-29 要求版本／repro 的通用回覆 | **否**（OP 仍是 Anthropic `/v1/messages` 自訂 upstream） | **不重開** → `WITHDRAWN_STILL` |

---

## 6. 硬禁執行聲明

- **未留言** headroom（無 discussion／issue comment）
- **未發邀請**／未 DM
- **未合 main**
- **未套 PR5**
- **未重開 WITHDRAWN**
- **未自開 draft PR**（入庫交父代理／飛輪長處理 `firekou/Open-Skill-Distribution-Flywheel`）
- **未放寬閘**湊人數

---

## 7. Blockers／下一步（供飛輪長）

1. **供給為空：** 公開 Q&A／General 在嚴格三欄下無 ELIGIBLE；最鄰近主題落在 **S3 issues**（尤其 #3673），但依規＝線索＋「已有 repro」拒因，**不能當 A4 邀請對象**。  
2. **維持關閉**或請愛莎核定：是否開 S3 例外通道／擴大 S4／調整資產問題句。  
3. 發送帳號 `firekou` 能力實證仍待真正准發前另做；本頁不測權限、不發測文。

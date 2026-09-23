# A4 補合格候選 — 搜尋範圍（草案）

**日期：** 2026-09-23（Asia/Taipei）  
**狀態：** 草案，待愛莎核定後執行  
**本輪 A4 邀請：** 已關閉（Eligible＝0；不發）  
**本頁目的：** 定義下一關「補合格候選」的搜尋與判定範圍。**不等於准發。** 找到合格對象後仍須另令准發才得發送。

## 為何再開這一關

PR#8 `CANDIDATES.md`／`INVITATIONS.md` 已將 C1／C2 定為 `NOT_ELIGIBLE_FOR_THIS_ASSET`／WITHDRAWN：先前依「主題相鄰」排名錯誤。公開 Q&A／issue 再掃結果為 **0 合格**。帳號 `firekou` 已指定、草稿 URL 已填，但無合格收件人＝本輪邀請關閉。

下一關只補「誰的問題＝資產能答」的名單證據；不自動重開邀請、不發、不合、不套 PR5。

## 資產能答的唯一問題（合格閘）

> 對**這一則**長、機器產生的**純文字** payload，在 headroom **0.37.0**、走 **OpenAI chat-completions** 路由時，到達上游的 body 是否變小，且關鍵那一行是否還在？

三欄必須同題才算合格（缺一＝`NOT_ELIGIBLE_FOR_THIS_ASSET`）：

| 欄 | 要求 |
|---|---|
| 1. 對方的問題 | 公開文字可還原；問的是「這類 payload／壓縮／關鍵行是否存活」或等價測量需求 |
| 2. 資產能做的 | 僅：OpenAI chat-completions 路線上的 bytes＋needle survival（pinned 0.37.0） |
| 3. 停在哪 | 不碰對方實際要的別條路由／別產品／別版本／schema 捕捉等 |

**明確不合格（沿用既有拒因，不重審為「差不多」）：**

- 只談 request shape／9router／Command Code（原 C1）
- 只要 Anthropic `/v1/messages` 代理（原 C2）
- bug tracker 上已自備 repro、或版本≠0.37.0 的損失回報（如 #3736 類）
- 已關閉／已回答成同一解法／作者要求勿聯絡
- Show-and-tell 社群貼文（非 A4 邀請通道）
- Discord `#help` 新問（CONTRIBUTING 導向）；A4 通道仍限既有 **Discussions Q&A** 回覆

## 搜尋範圍（建議核定）

| # | 來源 | 範圍 | 納入條件 | 排除 |
|---|---|---|---|---|
| S1 | headroom Discussions **Q&A** | open；優先 unanswered／近期活躍 | 問題句可對上資產唯一問題 | 已 answered 成壓縮無關解法；作者勿聯絡 |
| S2 | headroom Discussions 其他類別 | 僅當標題／首帖明確問 compress／payload size／line survival | 同上三欄 | Show-and-tell；功能許願 |
| S3 | headroom **Issues** | 僅作情報，**預設不可當 A4 邀請對象** | 若出現「公開測量需求」可記為候選**線索**，另請愛莎是否開例外通道 | 預設不發邀請到 issue |
| S4 | 上游／相鄰 repo Discussions | **預設不做**（本輪範圍外） | — | 除非愛莎另准擴大 ICP |
| S5 | 既有 WITHDRAWN（C1／C2） | **不重開**，除非對方**新留言**把問題改成資產能答的那句 | 新問題通過三欄閘 | 僅因「我們想發」而撤銷 WITHDRAWN |

**時間窗（建議）：** 自核定日起往回 **90 天** 公開帖＋當日仍 open 的更早帖；超過窗需標「陳舊」並另准。

**數量上限（搜尋產出）：** 最多列出 **10** 條「通過／邊緣／不合格」表列；合格列 **0–3** 即可停（對齊 A4 至多三人上限的上游供給）。**不為湊滿三人而放寬閘。**

## 產出物（執行後一頁）

檔名建議：`reviews/A4_ELIGIBLE_CANDIDATE_SEARCH_<YYYY-MM-DD>.md`（或同等路徑）

必含：

1. 搜尋時間、通道、關鍵字／篩選條件  
2. 檢視帖數／納入表列數  
3. 每列：URL、作者公開 handle、問題原句摘要、三欄判定、verdict  
4. `Eligible_count`（整數）  
5. 與本輪關閉紀錄的關係：補到 ≥1 後仍標 **「待另令准發」**；0 則建議維持關閉或擴大範圍（另准）

## 硬閘（執行與發送分開）

| 動作 | 本頁授權？ |
|---|---|
| 公開讀 Discussions／Issues | 核定範圍後可 |
| 寫入搜尋結果一頁（draft PR） | 可 |
| 更新 `CANDIDATES.md` 候選表 | 可（仍標 0 或列合格） |
| 改寫／重開 WITHDRAWN 草稿為可發 | **否**（需另令） |
| 在 headroom 留言／發送邀請 | **否** |
| 套 PR5／合 main | **否** |

發送帳號（已指定、與本關無關）：GitHub `firekou`。能力實證（能否在目標 Discussion 回覆）仍待真正准發前另做；**不得為測權限而發測文。**

## 請愛莎核定

1. 是否採納上表 S1–S5 與 90 天窗／最多 10 列？  
2. Issues（S3）是否維持「只記線索、不當邀請對象」？  
3. 核定後由誰執行搜尋（趨勢探／飛輪長協調雲端）？  

**核定前不執行搜尋、不發。**

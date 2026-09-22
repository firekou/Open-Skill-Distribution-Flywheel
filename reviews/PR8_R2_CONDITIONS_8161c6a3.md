# PR #8 revision 2 condition review

日期：2026-09-23（Asia/Taipei）

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者與其 Agent 能以固定版本、安全邊界清楚的方式試用 Routing 資產，再用真實採用回饋推進 Skill、Framework 貢獻與狀態／記憶接入。  
**本輪處理：** 獨立覆核 PR #8 revision 2 內容 SHA `8161c6a33251b06c44db9f5dbabc9431fa73b67d`，只驗 R1 的五項條件。  
**目前進度：** A1–A5 已交付；五項 R1 條件均關閉。外部採用仍為 0，M1／P5-R4-01 合格隔離重放尚未完成。  
**本輪成果：** 15.1% 主張已綁定輸入、版本與 SHA；外連／telemetry 文案已限縮到實際證據；六個 adoption 入口固定到 immutable commit；validator 的 schema 層及負控制經獨立重跑成立；INT-02 筆誤已修正。  
**還有什麼風險：** 作者的 44 tests 與第三方 runtime 仍未在合格隔離環境獨立重放；一般網路環境的第三方依賴行為未知；`EVIDENCE_FORMAT.md` 尚留「四個負 fixture」的小型舊數字，實際是五個。  
**需要負責人決定：** 無。本輪不要求方向、預算或對外承諾。  
**下一步與停止點：** 不再派 Claude 修復；下一 checkpoint 是 reviewer 在無 secrets、無外網、唯讀來源、無寫 token 的環境完成 M1／P5-R4-01。完成前不發邀請、不套 PR5 patch。  
**審查結論：** APPROVED_WITH_CONDITIONS

## Review identity

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: [#8](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/8), Draft, open, unmerged；2026-09-23 05:10（Asia/Taipei）回讀 `mergeable: true`、`mergeable_state: clean`
- PR base: `2a6becfa6fd792ede44a250171bbbdc93adbc4e3`
- Revision 2 source head: `77a8200533c80bc288186f58c1d8ecb6d25d121d`
- Immutable link target: `fb47e31b54b35518322254d0d69d7c7193dc2266`
- Reviewed content head: `8161c6a33251b06c44db9f5dbabc9431fa73b67d`
- Live/result head: `b76fc7ba08deade6733f140d3a37aadfd201d51c`
- Tail classification: content head → live head 只有 `reviews/ATK_OPEN_ADOPTION_EXECUTOR_RESPONSE.md` 與 `evidence/r2-conditions/controls.txt`
- Executor: Claude Code `session_01RFeCsTYkVywjHvXk7od7Ab`
- Reviewer: GPT，不同 session；未修改被審內容
- Exact-head checks: content／live SHA 均無 workflow run 或 commit status；PR 無 review submission

## 方向前置檢查

本輪仍符合已批准方向：把既有 Headroom Routing 案例做成開源開發者及 Agent 可重現的免費資產，ATK 僅是 optional provider。沒有啟動 benchmark、Freeze、框架試點、MCP server、controller、部署或付費呼叫。

## Acceptance

| 條件 | 狀態 | 證據級別 | 獨立證據 |
|---|---|---|---|
| A-R1-01 27% 錯誤主張 | CLOSED | VERIFIED | `INVITATIONS.md` 改為 `111357 → 94578`、15.1%，含 MD5、0.37.0、PR5 SHA 與單一樣本限制；全文搜尋 `27%` 為 0 |
| A-R1-02 外連／telemetry 邊界 | CLOSED | VERIFIED | Quickstart、manifest、Invitations 均區分 install network、check 自身 loopback traffic 與第三方 dependency 未測；指定絕對主張搜尋為 0 |
| A-R1-03 immutable 入口 | CLOSED | VERIFIED | patch 六個 URL 指向 `fb47e31...`；逐一 `git cat-file -e` 證實目標存在；省略網址與 branch URL 搜尋為 0 |
| A-R1-04 schema validator | CLOSED | VERIFIED | 正常 records、正控制通過；五個負 fixture 失敗；另以 11 項自建矩陣核對 required、additionalProperties、type、enum、pattern、items、minItems、minimum、anyOf 與 bool/int 分離 |
| A-R1-05 INT-02 數量 | CLOSED | VERIFIED | `four were fixed` 已改為 `all five were fixed` |
| PR5 patch／AST 回歸 | PASS | VERIFIED | `check_consistency.py` 24/24、`git diff --check` 均 exit 0；patch 可套 PR5 `304af885...`，去 docstring 後 AST 相同 |
| M1／P5-R4-01 隔離重放 | PENDING | NEEDS_INFORMATION | 本輪沒有合格隔離 runtime；作者輸出只保留 TESTED，不升格 |

## Findings

### 已關閉：A-R1-01 至 A-R1-05

五項限定修正均與 R1 要求一致，沒有擴大成產品重寫。commit A 先保存修正後目標文件，commit B 再把公開入口固定到 A，解決文件無法自指自身 SHA 的問題。content head 之後只有 executor response 與 controls，沒有產品內容變更。

### P3 A-R2-01：fixture 數量文字仍是舊值

`EVIDENCE_FORMAT.md` 最後一段仍寫「four records that must fail and one that must pass」，實際為五個負 fixture、一個正 fixture。這不影響 validator、公開試用流程或五項 R1 條件，記為 merge 前 editorial backlog；不為一個非阻擋字詞啟動第二輪修復。

## Tests and evidence checked

- `python3 adoption/ATK-OPEN-ADOPTION-01/check_consistency.py`：24/24 PASS，exit 0。
- `python3 .../validate_records.py records/*.json`：兩筆 records 通過。
- 自建 11 項 schema matrix：record pattern、bool/int、string type、date pattern、minItems、items type、integer anyOf、minimum anyOf、enum、additionalProperties、required，全部得到預期拒絕。
- 解析 patch 的六個 immutable URL，逐一以 Git object 查存在。
- 搜尋 `27%`、moving branch、`…/blob`、絕對 loopback／tracking 主張，全部 0 match。
- `git diff --check 77a8200..8161c6a`：exit 0。
- content → result head 的淨差異只含 executor response 與 controls。
- 對當時 main `e65f66b12b72221890d32b245ddf14e9d559c0b9` 與 PR head `b76fc7ba08deade6733f140d3a37aadfd201d51c` 獨立執行 `git merge-tree --write-tree --name-only`：exit 0、無衝突路徑；GitHub REST 同時回報 `mergeable: true`、`mergeable_state: clean`。先前一次 `false` 是重算中的暫態，不是已證實的內容衝突；真正 merge gate 仍須重新回讀。
- 未執行 Headroom 第三方 runtime；沒有 secrets、provider call、費用、外部訊息、merge、部署或權限修改。

## Residual conditions

1. M1／P5-R4-01 需在合格隔離 reviewer runtime 綁定 PR5 `304af885...` 重放；不得用作者 session 代替。
2. 發邀請前仍需依 A4 在當日確認固定 Quickstart URL、對象／渠道與發送帳號權限；本 review 不構成發送動作。
3. `EVIDENCE_FORMAT.md` 的 fixture 數量於 merge／發布前順手改正；不派新的 Claude 修復輪。

```yaml
review_gate:
  decision: APPROVED_WITH_CONDITIONS
  reviewed_base: "77a8200533c80bc288186f58c1d8ecb6d25d121d"
  reviewed_head: "8161c6a33251b06c44db9f5dbabc9431fa73b67d"
  live_head: "b76fc7ba08deade6733f140d3a37aadfd201d51c"
  highest_evidence: VERIFIED
  blocking_findings: []
  closed_findings:
    - A-R1-01
    - A-R1-02
    - A-R1-03
    - A-R1-04
    - A-R1-05
  conditions:
    - "M1/P5-R4-01 independent isolated replay before invitations or PR5 patch application"
    - "day-of A4 recipient/channel/account and immutable Quickstart URL check before any invitation"
    - "correct the non-blocking fixture count before merge/publication"
  owner_decisions: []
  next_checkpoint: "M1/P5-R4-01 independent isolated replay at PR5 304af885; no Claude redispatch"
  invalidates_when:
    - "reviewed content changes after 8161c6a33251b06c44db9f5dbabc9431fa73b67d"
    - "PR5 source SHA changes"
    - "required isolation evidence changes or fails"
```

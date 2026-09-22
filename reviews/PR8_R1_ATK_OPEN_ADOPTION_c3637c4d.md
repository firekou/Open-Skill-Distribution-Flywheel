# PR #8 A package R1 independent review

日期：2026-09-23（Asia/Taipei）

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者或其 Agent 能安全試用一個可重現的 Routing 資產，再以真實採用回饋沉澱 Skill、Framework 貢獻與狀態／記憶接入。
**本輪處理：** 獨立覆核 PR #8 的 A1–A5 產品採用包；內容 SHA `c3637c4dcf7a0ab86e884dfb6ba07054c93d873d`，live head `77a8200533c80bc288186f58c1d8ecb6d25d121d` 只追加 executor response。
**目前進度：** A1–A5 的檔案、Agent 契約、候選、邀請稿、證據格式與 M1–M5 工作單都已交付；外部採用仍為 0，M1 獨立隔離重放尚未完成。
**本輪成果：** 已驗證 PR5 文件 patch 可乾淨套用，`ab_test.py` 可執行 AST 不變；Agent manifest／兩筆內部紀錄可解析；GitHub 搜尋、Agent Skills、MCP Registry 及兩個候選討論的關鍵敘述獲官方頁面交叉核對。
**還有什麼風險：** 邀請稿把 15.1% 寫成 27%；一般網路環境仍未知 onnxruntime 是否外連，稿件卻宣稱「nothing leaves loopback」；PR5 文件 patch 連到可移動分支而非不可變 SHA。這三項都會直接影響外部信任。
**需要負責人決定：** 無。About/topics 與實際發送帳號在條件關閉後才需要帳號持有人操作；既有方向不用重問。
**下一步與停止點：** Claude 只修正外部主張、不可變入口、validator 最小完整性與一處證據筆誤，回傳新內容 SHA；GPT 再覆核一次。條件關閉前不發邀請、不套用 PR5 patch。
**審查結論：** APPROVED_WITH_CONDITIONS

## Review identity

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: [#8](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/8), Draft, open, unmerged
- Base: `2a6becfa6fd792ede44a250171bbbdc93adbc4e3`
- Reviewed content head: `c3637c4dcf7a0ab86e884dfb6ba07054c93d873d`
- Live head: `77a8200533c80bc288186f58c1d8ecb6d25d121d`
- Tail classification: content head → live head 只有 `reviews/ATK_OPEN_ADOPTION_EXECUTOR_RESPONSE.md`
- Source asset: PR #5 `304af885193245da7186cb6b9ab247ec2494bd86`
- Work: `ATK-OPEN-ADOPTION-01`, revision 1, stage A
- Executor receipt: Claude Code `session_016YNgsSCC2eV5sicob2f56f`
- Reviewer: GPT, 與 executor 不同 session；未修改被審內容
- Exact-head automation: content/live SHA 均無 workflow run、commit status 或 PR review
- Scope: 27 個產品／證據檔案加 1 份 executor response；沒有 PR5 原始實作被複製或套用

## 方向前置檢查

本輪直接服務已批准的四方向第一步：把現有 Headroom Routing 案例整理成開源開發者與 Agent 可跟做的試用資產。ATK 是可選 provider，離線路徑不需 ATK 帳號或 key。沒有恢復 benchmark、Freeze、Omnigent／AGT／OMA、controller、MCP server 或付款平台。

## Acceptance

| 準則 | 狀態 | 證據級別 | 證據 | 缺口 |
|---|---|---|---|---|
| A1 單一、固定、可停止的試用入口 | CONDITION | VERIFIED | patch 在 PR5 `304af885` 上 `git apply --check` 成功；獨立 AST 比對證實 docstring 外程式不變；retry／成功次數文案有修 | patch 內 adoption 連結使用可移動 branch；channel 文件另有省略網址 |
| A2 Agent 契約與 manifest | CONDITION | VERIFIED / TESTED | manifest JSON、quickstart、版本、SHA、輸入輸出、停止條件、寫檔與費用可直接檢查；作者的隔離 run 與 44 tests 只有 TESTED | 一般網路環境的資料外連未知，外部文案卻使用絕對「nothing leaves」 |
| A3 發現與分發設計 | PASS | VERIFIED / OBSERVED | GitHub 官方文件確認預設 repo search 查 name/description/topics；Agent Skills 與 MCP Registry 官方規格交叉核對；不適合的 MCP/HF 類型沒有硬塞 | 其餘渠道依稿件已標日後需重查 |
| A4 候選與邀請稿 | CONDITION | VERIFIED | #2732、#973 在 2026-09-23 仍為 Unanswered，需求描述與公開頁面相符；沒有訊息送出 | 27% 與 pinned evidence 15.1% 衝突；外連絕對主張不成立 |
| A5 證據格式與里程碑 | CONDITION | VERIFIED / OBSERVED | schema 與兩筆 INT 記錄可解析；required/additionalProperties、分類規則及 M1–M5 順序可檢查 | validator 未實際執行 schema 的 type/pattern/minItems/minimum；一筆紀錄寫「四項」但列五項 |
| 權限與 Non-goals | PASS | OBSERVED | Draft、未 merge；外部採用 0；無留言、部署、key、上游送出或費用 | 無 |
| M1 獨立 runtime replay | PENDING | NEEDS_INFORMATION | reviewer 嘗試 bwrap；NETLINK_ROUTE socket 被 OS 拒絕 | 本環境不能做合格的無外網隔離重放；不得以作者 run 替代 |

## Findings

### P1 A-R1-01：外部邀請數字錯誤

**後果：** 外部開發者會收到不可由 pinned evidence 支持的成效數字，直接損害這個供應資產的可信度。

**證據：** `INVITATIONS.md` 說同資料 plain text 縮小 27%；PR5 的 `evidence/local_check.txt`、R7 controls、新 internal run、Quickstart 全部是 `111357 → 94578`，即 15.1%。

**修復：** 改為 15.1%，或刪除百分比只說此 synthetic sample 有縮小。全域搜尋所有對外稿件，數字必須綁同一輸入 MD5、headroom 版本與 SHA。

**驗證：** 搜尋不得再出現無來源的 27%；邀請數字與 pinned evidence 完全一致。

### P1 A-R1-02：一般試用環境的外連／telemetry 主張過度

**後果：** 一般開發者照 Quickstart 執行時，安裝後的 check 並未被 network namespace 包住；文件同時承認 onnxruntime 在有網路機器是否傳送資料未測，邀請稿卻說「nothing leaves loopback／127.0.0.1」。這會形成錯誤的隱私承諾。

**證據：** `AGENT_QUICKSTART.md` 與 manifest 明列 onnxruntime networked behavior NOT TESTED；`INVITATIONS.md` 第 20、39 行及 Data 區使用絕對外連否定。作者的 `iso.sh` 只證明該次隔離 run。

**修復：** 對外稿統一改為：「試用業務流量只指向 loopback；本專案的隔離 run 已證明該次無外連；一般有網路環境的 transitive dependency 行為仍未知。」若要保留「nothing leaves」，必須給可跟做且通過 reviewer 的網路隔離方式，不能把作者內部 wrapper 當跨環境保證。`No telemetry` 只可指我們自己的檔案／未建立遙測，不可推及第三方依賴。

**驗證：** 全域搜尋絕對主張；Quickstart、manifest、Invitations 三處語義一致。

### P1 A-R1-03：採用入口不是不可變版本

**後果：** `pr5-doc-delta.patch` 寫入 `blob/claude/atk-open-adoption-01-teua0c/...`，分支可移動或刪除；`DISTRIBUTION_CHANNELS.md` 的 Human trial 又是 `…/blob/...` 省略字串，不能作實際入口。這違反 A1 與發邀請前的 fixed-entry gate。

**證據：** patch 有四組 branch URL；channel 文件第 31 行不是完整網址。

**修復：** 先提交其他修正取得中間 immutable commit A，再把所有 adoption/agent 文件連結固定到 A 的完整 40-char SHA，提交最終結果 B。PR5 code/TRY_IT 仍固定 `304af885...`。不得用 final branch URL 或省略網址。

**驗證：** 全域搜尋 `blob/claude/atk-open-adoption` 與 `…/blob` 為 0；所有公開入口可讀且指向不可變 SHA。

### P2 A-R1-04：validator 沒有完整執行其 schema 約束

**後果：** 未來 evidence record 可在日期格式、字串型別、pattern、空 commands、duration 下限等違反 schema 時仍被 `validate_records.py` 接受，README 的「enforced」敘述過強。

**證據：** source inspection 顯示 validator 只取 required、enum，另外檢查三個 list、兩個 number、SHA 與分類語意；沒有一般 type、pattern、minItems、minimum 驗證。

**修復：** 維持 stdlib，補上本 schema 實際使用到的 type、pattern、minItems、minimum 檢查，並加入至少一個原本會誤過的新 negative fixture；或明確拆成 schema validator 與 semantic validator，兩者都成為驗收命令。不可只改 README 掩蓋證據完整性。

**驗證：** 正常 records 通過；既有與新增負控制失敗；一個合格 UNVERIFIED 正控制通過。

### P3 A-R1-05：INT-02 修正數量筆誤

`records/INT-2026-09-22-02.json` 說「four were fixed」但括號列五項，executor response 說五項。改成 five；不影響功能，但應避免證據內部矛盾。

## Scope drift and assumptions

- 沒有把本包變成新 routing engine、MCP server、Skill、framework adapter 或資料庫 PoC。
- `pr5-doc-delta.patch` 尚未套用 PR5，沒有繞過舊 2/2 修復上限。
- C1/C2 是候選與草稿，不是已授權發送的完成證據；本輪沒有外部 adoption。
- 內部 fresh subagent 仍是 INTERNAL_AGENT_TEST，分類正確。
- About/topics 方向早已批准，但設定能力與 PR gate 仍需到條件關閉後確認；本輪不重問方向。

## Tests and evidence checked

- GitHub live state：base/head、Draft/open/unmerged、28 changed files、comments/reviews、精確 SHA statuses/workflows。
- compare：base → content head 27 檔；content head → live head 只有 executor response。
- 靜態：Python compile、所有 JSON 用 jq 解析、required/additionalProperties 獨立檢查。
- patch：在 PR5 `304af885...` worktree 上 `git apply --check` 成功。
- AST：獨立解析 patch 前後 `ab_test.py`，去 docstring 後 AST 相同。
- 官方來源（查核 2026-09-23）：GitHub repository search、Agent Skills specification、MCP Registry；Headroom Discussions #2732/#973 的狀態與內容。
- 沒有執行 PR 第三方 runtime：bwrap 在建立隔離網路時回 `Operation not permitted`。因此作者 44 tests、15.1% run、負控制及 fresh subagent 都維持 TESTED，不升格為 VERIFIED/REPRODUCED。
- 沒有 key、live provider call、費用、merge、部署、權限變更或外部訊息。

## Residual risks after conditions

條件修完後仍需 M1 合格隔離 runtime 重放；其他 OS/Python、networked onnxruntime、live provider、Anthropic messages route、transitive dependency drift 仍是明示限制，不阻擋離線文件繼續審查。

```yaml
review_gate:
  decision: APPROVED_WITH_CONDITIONS
  reviewed_base: "2a6becfa6fd792ede44a250171bbbdc93adbc4e3"
  reviewed_head: "c3637c4dcf7a0ab86e884dfb6ba07054c93d873d"
  live_head: "77a8200533c80bc288186f58c1d8ecb6d25d121d"
  highest_evidence: VERIFIED
  blocking_findings: []
  conditions:
    - "A-R1-01 correct the external 27% claim"
    - "A-R1-02 bound egress and telemetry language to observed evidence"
    - "A-R1-03 replace moving or abbreviated entry links with immutable complete URLs"
    - "A-R1-04 enforce the schema constraints used by adoption records"
    - "A-R1-05 correct the INT-02 count typo"
  owner_decisions: []
  next_checkpoint: "ATK-OPEN-ADOPTION-01 revision 2 exact content SHA independently re-reviewed; no invitation or PR5 patch apply before conditions close"
  invalidates_when:
    - "reviewed product scope changes"
    - "content head changes"
    - "source PR5 SHA changes"
    - "required evidence changes or fails"
```

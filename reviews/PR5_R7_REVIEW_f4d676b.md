# PR #5 R7 獨立覆核：Headroom + ATK 採用準備

## 給負責人的兩分鐘簡報

**整體目標：** 交付一個可跟做的有用 AI 工具案例，讓使用者先離線驗證 Headroom，再選擇是否透過 ATK API 完成真實任務並留下可核對的採用證據。  
**本輪處理：** 獨立覆核 PR #5 從 `e8a15d7d2c012007a69ca69c7e4630c33147c4a6` 到 `f4d676b22a853f64b37f2c160cdb3d1f6bc47efc` 的一個新內容 commit。  
**目前進度：** 離線／live 資料流說明、十分鐘試用入口與新 preflight 分支已交付；live 執行步驟及既有隔離重放尚未過 gate，第三方採用仍為 0。  
**本輪成果：** VERIFIED：精確 diff、live 指令與 `ab_test.py` 實際呼叫數已交叉核對；OBSERVED：文件已分開離線與 live 外送邊界；TESTED：作者記錄 34 項測試與控制，但本 reviewer 未獨立執行。  
**還有什麼風險：**
1. 試用頁宣稱一個任務、direct／proxy 各一次，但其命令實際執行兩個任務共四次付費呼叫。
2. 試用頁說金鑰不可放命令列，卻緊接著示範 `ATK_API_KEY=...`，照抄可能把秘密留在 shell history。
3. `P5-R4-01` 仍缺合格隔離環境的獨立重放；本輪沒有關閉。
**需要負責人決定：** 無。修正屬既有授權範圍；新 live run、發布、合併與支出仍未授權。  
**下一步與停止點：** 只修 live 指令的秘密與兩次呼叫邊界，並移除未被證實的無壓縮因果診斷；新 SHA 只做一次限定確認。既有隔離重放另行等待，不要求作者重做。  
**審查結論：** BLOCKED

## 1. Review identity

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: [#5](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/5), Draft, open, not merged
- Trusted main at review start: `671cdfa1004718c132aa460fed607b095ef5f752`
- Reviewed base: `e8a15d7d2c012007a69ca69c7e4630c33147c4a6`
- Reviewed head: `f4d676b22a853f64b37f2c160cdb3d1f6bc47efc`
- Scope: eight changed paths in the one-commit range; only the new Headroom adoption work
- Reviewer: GPT independent reviewer under `GOV-HANDOFF-TAKEOVER-20260921`
- Review time: 2026-09-21T14:28:00Z
- Excluded: PR6 controller, benchmark, Freeze, framework pilots, merge, deployment, publication, secrets and paid calls

## 2. 目標對齊

- 目標來源：GOAL-02、1A／2A／3A，以及 main 的 `reviews/CLAUDE_NEXT_PROMPT_ATK_DISTRIBUTION.md`。
- 本輪交付：一位使用者可從合成 log 做離線 preflight，再在明確權限與費用下選擇 live API。
- 主線連結：直接推進可用工具、可選 ATK API 接入與採用入口，未重開治理框架。
- 必要驗證與停止點：離線／live 邊界、秘密處理、實際呼叫數、歷史數據標示及採用證據；修完本輪 P1 後停止擴張。
- 範圍差異：沒有新增 MCP、adapter、benchmark 或 paid run；新增一個首次使用缺陷修復與試用文件，屬既有產品工作包。

## 3. Acceptance table

| Criterion | Status | Evidence | Proof | Gap |
|---|---|---|---|---|
| 離線與 live 外送邊界分開 | PASS | OBSERVED | README、TRY_IT 與 DISTRIBUTION 均說明 live 會送出壓縮後 prompt | 尚未對外發布 |
| 最小試用入口存在且使用合成資料 | PASS | OBSERVED | 新增 `TRY_IT.md`，先離線、後 live | live 指令仍有 P1 缺口 |
| 歷史 live 數據不冒充本輪重測 | PASS | OBSERVED | TRY_IT 與 executor response 明列不可重建冒充 | 無 |
| 不把內部測試當外部採用 | PASS | OBSERVED | executor response 明列第三方使用 0 | 真實採用仍為 0 |
| 金鑰不進命令列／repo | FAIL | VERIFIED | TRY_IT 同段先禁止命令列，後示範 `ATK_API_KEY=... python3 ab_test.py` | P1-01 |
| live 首輪維持一個任務、兩次呼叫、零重試 | FAIL | VERIFIED | TRY_IT 宣稱兩次；`ab_test.py` 的兩個 TASKS 各跑 direct + proxy，共四次 | P1-02 |
| preflight 不從未確定現象推論根因 | PARTIAL | VERIFIED | 一次不一致回 exit 4；兩次相同仍斷言 payload 無冗餘 | P2-01 |
| 新程式回歸與 P5-R4-01 獨立隔離重放 | PENDING | TESTED | 作者 evidence 記錄 34 tests；exact head 無 check run/status | reviewer 無合格隔離 runtime |

## 4. Findings

### P1-01：live 指令把金鑰示範在 shell command 中

**Consequence:** 使用者若把 `...` 換成真實 key，命令可能留在 shell history、終端記錄或操作稽核中，違反同頁「never on the command line」與既有秘密邊界。  
**Evidence:** VERIFIED。精確 head 的 `TRY_IT.md` 同段包含禁止句及 `ATK_API_KEY=... python3 ab_test.py`；未讀取任何秘密。  
**Required fix:** 不再示範含秘密值的 command。要求 key 由既有環境／secret manager 注入，只示範檢查 SET/NOT_SET 與 `python3 ab_test.py`；若需要互動輸入，使用不回顯且不進 history 的方式，並清理變數。同步 `ab_test.py` docstring 的同類矛盾。  
**Verification:** 搜索交付目錄不得再出現 `ATK_API_KEY=sk-` 或 `ATK_API_KEY=...` 執行範例；正常缺 key 路徑仍拒絕執行且不顯示值。

### P1-02：文件承諾兩次呼叫，實際命令送出四次

**Consequence:** 使用者依「一個任務、direct／proxy 各一次」的費用授權執行後，實際對 provider 送出兩個任務共四次，造成超出預期的費用與資料外送。  
**Evidence:** VERIFIED。TRY_IT 建議一個 synthetic task、一次 direct、一次 proxy；同頁執行 `python3 ab_test.py`。精確 head 的 `ab_test.py` 有 `summary`、`needle` 兩個 TASKS，迴圈中各呼叫 direct 與 via_headroom。  
**Required fix:** 讓首次 live 指令實際只跑 needle 任務的兩次呼叫，並在執行前明列精確 call count。可增加明確 task selector 或提供只執行 needle 的安全入口；不得只改文字把四次包裝成兩次。零自動重試維持。  
**Verification:** 以 mock counter 驗證首次 live 命令恰好呼叫兩次，分別為 direct 與 proxy；拒絕缺 key，且不做網路重試。

### P2-01：重複兩次仍不足以證明「payload 沒有冗餘」

**Consequence:** 兩次一致只證明本次觀察重複，不能排除 proxy 未 ready、壓縮器 bypass 或其他未明根因；使用者仍可能因錯誤因果說明放棄可用工具。  
**Evidence:** VERIFIED。`local_check.py` 在兩次 byte-for-byte pass-through 後仍輸出「this payload has no such redundancy」。executor 同時明載根因未建立。  
**Required fix:** exit 3 保留，但只陳述「兩次都未觀察到 size benefit」，不要斷言無冗餘或根因；TRY_IT 可建議換 payload／重跑／查 log，但不把觀察升格因果。  
**Verification:** source 與測試輸出不再包含未證實的因果句；stable negative 仍 exit 3，disagreement 仍 exit 4。

## 5. Evidence checked

- GitHub live PR state、base/head、one-commit range與八個 changed paths。
- Exact-head commit、PR comments、executor response、review submissions與threads。
- Exact-head status contexts = 0、check runs = 0、workflow runs = 0。
- Cross-read `TRY_IT.md`、`ab_test.py`、`local_check.py`、新 tests、evidence、README、DISTRIBUTION 與 service sample。
- 沒有執行 PR code：本 reviewer 無法證明符合 repo 所需的斷網、無秘密、唯讀來源與無 GitHub write token 隔離。作者的 34 tests 與 controls 為 TESTED，不升格為獨立通過。
- 舊 `P5-R4-01` 不重派作者修復，仍等待原 R5 content-addressed 證據包的獨立隔離重放。

## 6. Scope drift and residual risk

沒有 benchmark、Freeze、MCP、controller 或新付費範圍漂移。主要風險是 live 指令與費用／秘密承諾不一致；修復前不可把 TRY_IT 的 live 段當可執行操作說明。即使本輪 P1 關閉，PR 仍需 P5-R4-01 獨立隔離重放，外部採用仍需非作者使用者證據。

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: "e8a15d7d2c012007a69ca69c7e4630c33147c4a6"
  reviewed_head: "f4d676b22a853f64b37f2c160cdb3d1f6bc47efc"
  highest_evidence: VERIFIED
  blocking_findings:
    - P5-R7-01
    - P5-R7-02
  conditions:
    - "P5-R7-03: remove unsupported causal diagnosis from stable no-benefit output"
    - "P5-R4-01: independent isolated replay remains pending and is not reassigned to the author"
  owner_decisions: []
  next_checkpoint: "one bounded confirmation of the live secret/call-count patch; isolation replay remains a separate checkpoint"
  invalidates_when:
    - reviewed scope changes
    - reviewed head changes
    - required evidence changes or fails
```

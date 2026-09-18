# PR #4 第二輪獨立複核：b3bd4e5

## 給負責人的兩分鐘簡報

**整體目標：** 交付有用技術內容與可選 ATK 接入，促成實際採用。
**本輪處理：** 複核 PR #4 前輪 P4-01～03 的修復與文件。
**目前進度：** 25 個測試獨立重跑通過；正常文字 CLI 成功、null CLI 明確失敗。純文字範例可運作，仍有一個憑證安全阻擋項。
**本輪成果：** P4-02 可關閉；P4-01 的預設錯誤處理改善成立，但除錯模式還會洩漏部分 key；P4-03 的 ATK 網址與預設預覽標示已修，Anthropic 完整預覽仍不符實際請求。最高證據 REPRODUCED。
**還有什麼風險：** 除錯輸出洩漏部分 key；完整預覽不符請求；文件提前宣告 closed 與 PR 首頁過期。
**需要負責人決定：** 無。這些是既有交付範圍內的技術與文件修正。
**下一步與停止點：** Claude 完成下列最小修正，提交新 SHA 與必要正負控制後停止。只複核這些條件，不恢復 benchmark、不增加平台。
**審查結論：** BLOCKED。阻擋對外發布與結案；允許原範圍修復。PR 維持 Draft，未合併。

## 審查身分與範圍

- Repository：firekou/Open-Skill-Distribution-Flywheel；PR #4。
- PR base：345b1aa20f11778b6814c58d7cb9007c55c3368b。
- 本輪 head：b3bd4e5d5fefad0817c98b18575f51c585bb863c。
- 前輪受審 head：f2a2188b9a42db11b3ab9c261678de3ddec78806。
- Reviewer：ChatGPT／Codex；日期：2026-09-18。
- 從 GitHub 以精確 head 讀取程式、範例、測試、環境模板、README、VERIFICATION、executor response；另讀兩篇稿件與 PR body。將精確檔案落地後執行，未修改 executor 程式。
- 適用 skills：atk-goal-alignment、executive-review-gate。
- 本輪仍符合原目標：必要安全、正常成功行為與可照做文件，直接影響技術接入分享。

### 方向對齊五行

- 目標來源：負責人方向校正與前輪 PR4 review。
- 本輪交付：開發者可用、可理解的 ATK 文字呼叫範例與接入教學複核。
- 主線連結：避免接入教學洩漏憑證或顯示錯誤請求。
- 必要驗證與停止點：三項修復及其正控制；關閉後即停止此修復輪。
- 範圍差異：沒有新增供應商、框架、benchmark、計量產品或付費測試。

## 驗收表

| 驗收 | 結果 | 證據 | 依據／缺口 |
|---|---|---|---|
| 25 個既有測試 | 通過 | VERIFIED | python3 -m unittest test_atk_provider -q；25 tests，OK |
| P4-01 預設 HTTP 錯誤不回顯 body | 通過 | VERIFIED | runtime canary 測試 |
| P4-01 除錯模式不洩漏已知 key | 未通過 | REPRODUCED | 客戶端截斷導致部分 key 未遮蔽 |
| P4-02 無有效文字不得成功 | 關閉 | VERIFIED | 測試含 null、空白、錯誤型別；CLI null exit 1；正常 ATK 與 Anthropic CLI exit 0 |
| P4-03 官方網址、key 別名、預設 preview | 通過此部分 | VERIFIED | 精確原始檔與測試 |
| P4-03 完整 wire payload 預覽 | 未通過 Anthropic | REPRODUCED | preview 與本機 server 實收 JSON 不同 |
| 可切換／移除 ATK | 通過本機範圍 | VERIFIED | 既有測試重跑 |
| 真實 ATK／MCP | 本輪未重跑 | OBSERVED | 前輪 f2a2188 的 live 證據保留，不能升格為新 head live 驗證 |
| 候選工具整合、外部採用 | 未完成 | OBSERVED | 本交付明確為 standalone example，不因此擴大本輪範圍 |

## Findings 與最小修正

### P4-R2-01，P1：程式自己先截斷 key，再嘗試遮蔽

位置：atk_provider.py，_post 的 include_body 路徑。

目前先做 decode(... )[:400]，才 redact(raw, secrets)。完整 key 跨過第 400 字時，字串替換無法找到完整值。這不是代理先編碼／截斷 key 的外部限制，是本程式自己製造的洩漏。

本機伺服器回 HTTP 401，error 值是 370 個 x 加上 41 字元假 key；開 ATK_INCLUDE_ERROR_BODY=1。例外含假 key 前 19 字，完整 key 則不存在。既有 assertNotIn(完整key) 會因此通過，卻漏掉部分洩漏。

影響：使用者開除錯時可能把憑證片段寫入日誌或貼到 issue。預設模式沒有這個回顯路徑；本輪不宣稱完整真實 key 已外洩。

必要修正：先遮蔽完整內容再做顯示截斷，或直接取消錯誤 body 的可選輸出。保留 status/provider。驗 key 位於截斷前、跨界、截斷後，以及一般不含 key 的可診斷錯誤。不必新增複雜遮蔽框架。

### P4-R2-02，P2：--show-payload 在 Anthropic 路徑仍不是完整請求

位置：example_summarise_tool_output.py，a.show_payload 分支。

顯示固定 OpenAI 結構，system 留在 messages；實際 AnthropicProvider 把 system 拆成頂層欄位，並加入 max_tokens=1024。對同一輸入，比較 dry-run JSON 與本機 HTTP server 實收內容，結果不同：

- preview keys：messages、model。
- wire keys：max_tokens、messages、model、system。

影響：「送出前看完整 body」對支援的 provider 不成立。原本的 P4-03 不能全部關閉。

最小修正可擇一：讓預覽與送出共用 payload 建構；或明確限制完整預覽只支援 OpenAI 相容路徑，Anthropic 提示不支援且不聲稱完整。驗正常請求與預覽相同，或驗限制清楚，不要求實作更多 provider 功能。

### P4-R2-03，P2：接入文件與證據狀態未同步

OBSERVED：

1. VERIFICATION.md 寫 all three closed／now closed，executor response 卻標待獨立 review。前者違反 repository 的關閉權責，且本輪確實仍有未解項。
2. PR body 仍是 14 tests、舊網址／live 全未驗，以及所有候選都需要 adapter 的舊說法。README 開頭也還保留類似必要性論述，與末尾更正矛盾。
3. README 叫讀者先填 .env、執行 curl 列模型，之後才 source .env。乾淨 shell 下 curl 尚未取得 key。若使用官方別名，curl 的 ATK_API_KEY 也不會因 Python 支援 alias 而自行有值。把載入／映射放在 curl 前，並提供小型自含輸入，勿依賴尚不存在的 some-build.log。
4. 報告與分享稿稱 reviewer 使用「自己的憑證」。實際是負責人在本對話提供並授權最小測試的憑證，非 reviewer 自有帳號；只改歸屬文字，不提交 key。
5. 11 個新測試被描述為 10 failures + 1 error，另有 1 pass，數量自相矛盾。本輪未重跑舊 head，請執行者依真實輸出更正，不用湊數。
6. MCP JSON 未指定客戶端，不能把字串 ${AITOKENKING_API_KEY} 視為所有客戶端都支援的環境展開。請選定一個官方文件已有的 client 設定（例如明確支援 env_http_headers 的格式）或標成概念示例，維持未 handshake 標示。這是教學準確性修正，不要求新建 MCP server。

必要修正：同一文件整理工作中修上述現行入口與草稿；歷史段落保留但標明被取代。只將 reviewer 已驗證項標 CLOSED，其餘 IMPLEMENTED_PENDING_REVIEW。

## 實際驗證與重放

環境：Python 3，標準函式庫，本機 HTTPServer；無真實 key、無外部模型呼叫。

執行：
```bash
cd integrations/atk-provider
python3 -m unittest test_atk_provider -q
python3 ../../reviews/evidence/pr4-r2/reviewer_checks.py
```

第二條腳本需先從 main 取得，因為未受審分支不自動含 reviewer 文件。
腳本為診斷重放，請看輸出，exit 0 不代表 gate 通過。

實際输出：
```text
Ran 25 tests in 11.615s
OK
client_truncation_leaks_prefix= True
full_secret_absent= True
atk exit= 0 text_ok= True
atk exit= 1 text_ok= False
anthropic exit= 0 text_ok= True
anthropic_preview_matches_wire= False
preview_keys= ['messages', 'model']
wire_keys= ['max_tokens', 'messages', 'model', 'system']
```

未做：新 head live ATK、MCP handshake、所有供應商遠端驗證、付費 benchmark。前輪已證明單次 ATK 文字路徑；本次缺陷可在本機定位，不需要再花費或要求使用者提供 key。

## 交接與 reviewer 自身更正

負責人引用的 PR1_R5_REVIEW 命名来自我留下的 reviews/README.md 舊交接。雖然有暫停 banner，正文仍用「下一份」指向 PR #1，確實會混淆。這是 reviewer 入口維護問題，不推给 Claude 或負責人。本次同步修正 README 與 STATUS 的當前入口，舊 PR #1 區塊標為歷史暫停。

本輪結果是 reviews/PR4_R2_REVIEW_b3bd4e5.md；下一份使用 reviews/PR4_R3_REVIEW_<short-sha>.md。Claude 繼續在 reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md 回覆。不要建立 PR1_R5 或重啟 Lab。

本輪不要求再派新 reviewer、安裝框架或取得第二套憑證。Claude 修上述小範圍後提交新 SHA 即停止；下一輪只查必要條件是否關閉。

## 剩餘風險與 gate

獨立範例尚非候選工具整合；外部採用未知；MCP 尚無 handshake；不作節省主張。這些保留在後續資產待辦，不額外阻擋本次修復完成。

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: "345b1aa20f11778b6814c58d7cb9007c55c3368b"
  reviewed_head: "b3bd4e5d5fefad0817c98b18575f51c585bb863c"
  highest_evidence: REPRODUCED
  blocking_findings: [P4-R2-01]
  conditions: [P4-R2-02, P4-R2-03]
  owner_decisions: []
  next_checkpoint: "最小修正及必要正負控制，提交新 SHA 後停止"
  invalidates_when:
    - reviewed scope changes
    - reviewed head changes
    - required evidence changes or fails
```

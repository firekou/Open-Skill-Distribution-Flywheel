# PR18 R1 獨立覆核：ATK-UPSTREAM-01

## 負責人摘要

**結論：BLOCKED。** PR #18 的 pinned 測試與雜湊證據大致完整，足以支持「Aider 在這組固定版本與 loopback fixture 下會重試 402／403、LiteLLM 的 OpenAI 403 路徑仍回傳 APIError」這個窄結論；但成果把 LiteLLM PR #38318 寫成仍開放。GitHub 的即時紀錄顯示該 PR 已於 2026-08-26 合併至 `litellm_internal_staging`。在 dedup report、LiteLLM issue 草稿與 PR body 修正前，不得視為 maintainer-ready，也不得送上游。

## 身分

- Repository：`firekou/Open-Skill-Distribution-Flywheel`
- PR：[#18](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18)
- Base：`main@8d03c28babb993aad24f52602d97c311a926a14b`
- Head：`48ea4decb3920b8a1d1fcacb92442b7a94376353`
- Work：`ATK-UPSTREAM-01` revision 1
- Executor session：`session_01RFeCsTYkVywjHvXk7od7Ab`
- Result receipt：[PR17 comment](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/17#issuecomment-5838541738)
- Review date：2026-09-26（Asia/Taipei）

## 目標對齊

1. **產品目標**：找出可形成實用 skill／工具與上游改善的真實缺口。
2. **本輪價值**：提供 Aider／LiteLLM 的固定版本、loopback 重現證據與未送出的 maintainer issue 草稿。
3. **不宣稱**：沒有真實模型成功、外部採用、再次使用、上游接受或經濟價值。
4. **允許接續**：只修正既有成果中的即時狀態與措辭。
5. **禁止事項**：不送上游、不 live、不使用 secrets、不付費、不 merge、不部署、不改權限、不新增 polling。

## 驗收

| 項目 | 結果 | 證據 |
|---|---|---|
| 有效 claim 與固定 work_id | PASS | session、work、source、branch、dedup、期限齊全 |
| 路徑範圍 | PASS | 59 個變更路徑均落在授權範圍 |
| 精確 head | PASS | `48ea4dec...`；Draft/open/unmerged |
| 雜湊完整性 | PASS | 55/55 evidence files fetched；51/51 raw artifacts、2/2 scripts、2/2 manifest/index hashes 相符 |
| Aider 矩陣 | PASS | 14/14 cases 與作者表格一致 |
| LiteLLM 矩陣 | PASS | 3/3 pinned versions 與作者表格一致 |
| 官方來源查重 | PARTIAL | Aider issue/PR 狀態相符；LiteLLM PR #38318 狀態不符 |
| Maintainer-ready 草稿 | FAIL | 將已合併的 PR #38318 寫成 open |
| 真實外部成果 | NOT COLLECTED | 未送出 issue、未呼叫真實模型、未取得外部採用 |

## Findings

### P1-01：PR38318_STATE_MISMATCH

PR #18 在 `UPSTREAM_DEDUP_REPORT.md`、`DRAFT_LITELLM_ISSUE.md` 與 PR body 將 [LiteLLM PR #38318](https://github.com/BerriAI/litellm/pull/38318) 標為 open。即時 GitHub 紀錄顯示它已於 2026-08-26 合併至 `litellm_internal_staging`。

這不推翻新的 issue 方向，因為 #38318 本身明確說 OpenAI branch 的 403 路徑仍為 `APIError` 且不在該 PR 範圍；PR18 對 pinned LiteLLM 1.102.1 的證據也仍呈現同一缺口。但錯誤狀態會誤導 maintainer，故在修正前阻擋 maintainer-ready 與任何上游送出。

### P3-01：NETWORK_ISOLATION_WORDING

Aider stdout 顯示測試期間曾嘗試向 `raw.githubusercontent.com` 取得 model prices，並因憑證失敗。模型/provider 路徑仍固定為 loopback，且本工作允許公開 web 查詢，所以不是 blocker；後續描述應使用「provider-loopback」而非廣義「network-isolated」。

## 範圍、假設與偏差

- 沒有修改作者的 evidence、manifest、script 或 issue 草稿。
- 沒有執行 PR 內依賴與 runtime；作者 runtime 結果維持 AUTHOR_TESTED。
- Reviewer 僅做精確 head 檔案回讀、SHA-256 重算、表格交叉核對與官方來源狀態驗證。
- Exact-head workflow runs、commit statuses、PR reviews 均為 0；不把缺少 CI 視為批准。

## 已核對證據

- 55 個 evidence files 全部由精確 head 取得。
- 51 個 raw artifact SHA-256 全部相符。
- 2 個 evidence script SHA-256 全部相符。
- repro manifest 與 direct index 兩個檔案雜湊相符。
- 14 個 Aider cases 與 3 個 LiteLLM version matrices 對得上原始內容。
- Aider [#5552](https://github.com/Aider-AI/aider/issues/5552)、[#4659](https://github.com/Aider-AI/aider/issues/4659)、[#5165](https://github.com/Aider-AI/aider/issues/5165)、[PR #5553](https://github.com/Aider-AI/aider/pull/5553)、[PR #5186](https://github.com/Aider-AI/aider/pull/5186) 已交叉核對。
- LiteLLM [exception mapping](https://docs.litellm.ai/docs/exception_mapping)、[PR #38318](https://github.com/BerriAI/litellm/pull/38318) 與 [PyPI 1.102.1](https://pypi.org/project/litellm/) 已交叉核對。

## 未重跑

- 未重新安裝 Aider／LiteLLM pinned dependencies。
- 未啟動 loopback harness 或執行 14 cases。
- 未呼叫真實 provider。
- 未送出任何 upstream issue、comment 或 PR。

## 殘餘風險

- 修正 #38318 狀態後，仍只能證明固定版本與 fixture 的技術缺口，不等於 maintainer 接受。
- Aider exit 0 與 retry 行為可能隨新版變動；真正送出前仍須重新確認 upstream 最新狀態。
- 外部採用與經濟價值目前仍為 0。

## 限定修復

已沿 [PR #18 conversation](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18#issuecomment-5838602710) 發出 `ATK-UPSTREAM-01` revision 2、repair 1/2。只允許修正 #38318 狀態與相應措辭；原始證據、manifest、script、Aider 草稿與不相關結論不得改動。

下一 checkpoint：`PR18_R2_38318_STATUS_CORRECTION`。

```yaml
gate:
  decision: BLOCKED
  evidence_level: AUTHOR_TESTED_WITH_INDEPENDENT_INTEGRITY_AND_OFFICIAL_SOURCE_VERIFICATION
  exact_head: 48ea4decb3920b8a1d1fcacb92442b7a94376353
  blocking_findings:
    - P1-01_PR38318_STATE_MISMATCH
  non_blocking_findings:
    - P3-01_NETWORK_ISOLATION_WORDING
  external_adoption: 0
  upstream_sent: false
  live_provider_called: false
  next_checkpoint: PR18_R2_38318_STATUS_CORRECTION
```

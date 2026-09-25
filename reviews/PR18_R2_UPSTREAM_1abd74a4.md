# PR18 R2 獨立覆核：ATK-UPSTREAM-01

## 負責人摘要

**結論：APPROVED_WITH_CONDITIONS。** Revision 2 已正確關閉 R1 的唯一 blocker：LiteLLM PR #38318 現在記為 2026-08-26 合併至 `litellm_internal_staging`，且仍保留「OpenAI branch 自身的 403 路徑不在該 PR 範圍」這個關鍵區別。變更嚴格限制在兩份狀態文件、append-only executor response 與 PR body 對應行，沒有動原始證據、manifest、script 或 Aider 草稿。

剩一項發布前文字條件：LiteLLM 草稿的 Why it matters 應明確說 9 次請求來自 Aider 自身 retry loop，OpenAI SDK 在本次 403 重現中沒有重送。此條件只阻擋上游送出，不阻擋 S4 首次使用準備繼續。

## 身分

- Repository：`firekou/Open-Skill-Distribution-Flywheel`
- PR：[#18](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18)
- R1 head：`48ea4decb3920b8a1d1fcacb92442b7a94376353`
- R2 head：`1abd74a4b7f14d8b5e397d33afa2ace212841099`
- Work：`ATK-UPSTREAM-01` revision 2，repair 1/2
- Executor session：`session_01RFeCsTYkVywjHvXk7od7Ab`
- Result receipt：[PR18 comment](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18#issuecomment-5838878694)
- Review date：2026-09-26（Asia/Taipei）

## 目標對齊

1. **產品目標**：形成真正可被 Aider／LiteLLM 維護者閱讀的技術貢獻材料。
2. **本輪價值**：修正上游狀態，保留 pinned 版本重現與 gap 的正確界線。
3. **不宣稱**：沒有 upstream 接受、外部採用、真實模型成功或經濟價值。
4. **允許接續**：S4 首次使用與發布材料準備可繼續。
5. **仍需授權**：任何上游送出、公開發布、邀請、live、付費、merge、部署或權限變更。

## 驗收

| 項目 | 結果 | 證據 |
|---|---|---|
| 固定 work/revision/source/dedup | PASS | result receipt 完整 |
| R1 到 R2 差異 | PASS | 1 commit；3 個 repository paths |
| 授權範圍 | PASS | report、LiteLLM draft、executor response；PR body 對應行 |
| #38318 即時狀態 | PASS | GitHub API：closed、merged=true、2026-08-26T08:46:25Z、base `litellm_internal_staging` |
| OpenAI branch gap 保留 | PASS | #38318 原文仍明示 403 path out of scope |
| 原始 evidence 不變 | PASS | old→new compare 未出現 evidence、manifest、script、Aider draft |
| Provider-loopback 措辭 | PASS | 未再宣稱全面 network-isolated |
| Maintainer-ready 精確歸因 | CONDITION | LiteLLM 草稿一句話須在送出前澄清 9 requests 的來源 |
| Exact-head checks | OBSERVED | workflows 0、checks 0、statuses 0、reviews 0 |
| 上游送出 | NOT DONE | 兩份草稿仍 NOT SENT |

## Findings

### R1 P1-01：CLOSED

官方 [LiteLLM PR #38318](https://github.com/BerriAI/litellm/pull/38318) 目前為 merged，`merged_at=2026-08-26T08:46:25Z`，base branch 為 `litellm_internal_staging`。Revision 2 的 report、LiteLLM draft 與 PR body 均已修正。

同一 PR 的內容明確寫出 OpenAI branch 自身的 403 仍為 `APIError` 且留在 scope 外。因此修正合併狀態不會推翻「OpenAI-compatible 403 mapping 仍值得另開 issue」的結論。

### R1 P3-01：CLOSED

現行文件使用 `provider-loopback`，不再把環境描述成全面 network-isolated。

### P2-01：RETRY_ATTRIBUTION_EDITORIAL_CONDITION

`DRAFT_LITELLM_ISSUE.md` 的 Why it matters 寫道 default OpenAI SDK `max_retries=2` 位於下層，而該重現產生 9 個 requests。這句在配置事實上不假，但容易讓維護者誤以為 SDK 參與 403 的九次重送。作者自己的結果回執已確認：9 次來自 Aider retry loop，SDK 沒有重送 403。

在任何 upstream submission 前，將該句改成直接歸因 Aider retry loop，並明示 SDK 沒有重送 403。本輪不為單句重新派第二輪作者修復；它保留為送出 gate。

## 已核對證據

- R1→R2 compare：ahead 1、behind 0、3 changed repository paths。
- R2 三個檔案與 PR body 均由 exact head 回讀。
- GitHub 官方 PR API 核對 #38318 merge state、time、base branch、head 與 merge SHA。
- Exact head workflow runs、check runs、commit statuses、PR reviews 均為 0。
- R1 已完成的 55/55 evidence files、51/51 raw hashes、2/2 scripts、2/2 manifest/index hashes 繼續有效，因 R2 未改這些路徑。

## 未重跑

- 未重新安裝或執行 Aider／LiteLLM harness。
- 未呼叫真實 provider。
- 未送出 upstream issue、comment 或 PR。
- 未把作者測試升為 reviewer runtime reproduction。

## 殘餘風險與條件

- 任何上游送出前須修正 P2-01，並重新讀一次 upstream live state。
- 維護者是否接受、第三方是否使用仍未知。
- 外部首次使用、再次使用與經濟價值仍為 0／NOT COLLECTED。
- PR18 是 Draft/open/unmerged；通過內容 review 不等於 merge 授權。

## 接續

無需等待 external gate 的 `ATK-FIRST-USE-PREP-01` revision 1 已沿 [PR18 conversation](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18#issuecomment-5838910923) 派送。它只準備固定入口、兩份完整文案、最多三位候選的公開資料比對、回饋 schema 與 release gate；禁止發送、發布、live、付費、merge、部署與 settings 變更。

```yaml
gate:
  decision: APPROVED_WITH_CONDITIONS
  evidence_level: AUTHOR_TESTED_WITH_INDEPENDENT_INTEGRITY_AND_OFFICIAL_SOURCE_VERIFICATION
  exact_head: 1abd74a4b7f14d8b5e397d33afa2ace212841099
  closed_findings:
    - P1-01_PR38318_STATE_MISMATCH
    - P3-01_NETWORK_ISOLATION_WORDING
  pending_conditions:
    - P2-01_RETRY_ATTRIBUTION_BEFORE_UPSTREAM_SEND
    - OWNER_AUTHORIZATION_BEFORE_UPSTREAM_SEND
  upstream_sent: false
  external_adoption: 0
  live_provider_called: false
  next_work_id: ATK-FIRST-USE-PREP-01
  next_checkpoint: ATK_FIRST_USE_PREP_CLAIM_OR_RESULT
```

# PR #10 R1 — M1／P5-R4-01 isolated replay review

日期：2026-09-23（Asia/Taipei）

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者與其 Agent 能安全重現 ATK Routing 資產，再進入有限外部試用。
**本輪處理：** 覆核 PR #10 在獨立 Docker runtime 對 PR #5 `304af885193245da7186cb6b9ab247ec2494bd86` 的 M1／P5-R4-01 重放證據。
**目前進度：** M1 安全重放條件已完成；PR #8 仍是 Draft，外部採用仍為 0。
**本輪成果：** PR #5 current／previous 的 6 個 blob 均與 GitHub exact refs 相符；獨立 Cursor run 使用 pinned Python image、network none、唯讀 input、無 GitHub write token，G0–G7 全 PASS；44 tests 通過，舊版負控制能抓到回顯。
**還有什麼風險：** 這是 mock process／network 的指定 finding 重放，不是乾淨安裝、license PASS、live provider 或採用證明；PR #10 exact head 沒有 CI／status；Docker daemon／image inspect 主要依 runner 記錄，沒有平台簽署 attestation。
**需要負責人決定：** 無。M2 的有限邀請仍須在執行當日確認收件者、渠道、帳號權限與 immutable Quickstart URL。
**下一步與停止點：** 將 M1 標 COMPLETE，下一 checkpoint 改為 `PR8_DAY_OF_A4_INVITATION_PRECHECK`；完成當日 precheck 前不發邀請。
**審查結論：** APPROVED

## Review identity

- Repository: `firekou/Open-Skill-Distribution-Flywheel`
- PR: [#10](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/10), Draft、open、unmerged
- Base: `main@834d3d148e054eca2ad048aa5bde709b5278d657`
- Reviewed evidence head: `cf37880bb90d6f646591588f39de91df67d7923c`
- Bound implementation head: PR #5 `304af885193245da7186cb6b9ab247ec2494bd86`
- Negative-control baseline: `d1930e4696f11cfb3cdae2f59d1b3692b68ee127`
- Independent runner: Cursor cloud agent `bc-5b9148f9-3253-5b1a-8a1c-79147a5cb763`
- Implementation authors: Claude sessions `session_01RFeCsTYkVywjHvXk7od7Ab`／`session_016YNgsSCC2eV5sicob2f56f`; 未被本 replay 使用
- Reviewer: GPT，未修改 PR #5 implementation 或 PR #10 evidence
- Exact PR #10 checks: workflow runs 0、check runs 0、commit statuses 0、PR reviews 0

## 方向前置檢查

本輪直接服務 ATK-OPEN-ADOPTION-01 的 M1 gate：在對開源開發者及其 Agent 發出試用邀請前，獨立重放 unknown token／dash-leading 私密值不回顯與受影響回歸。沒有啟動 benchmark、Freeze、框架試點、controller、部署、provider 呼叫或付費。

## Acceptance

| 準則 | 狀態 | 證據級別 | 獨立核對 |
|---|---|---|---|
| Reviewer 與 implementation author 分離 | PASS | VERIFIED | Cursor run ID 與兩個 Claude 作者 session 不同；PR #10 只新增 evidence，未改 PR #5 code |
| Exact implementation／baseline | PASS | VERIFIED | PR #5／PR #8 live heads 未變；manifest 6/6 blob SHA 與 GitHub exact refs 相符 |
| G0 isolation | PASS | TESTED | command 固定 image digest、`--pull=never --network none --read-only --cap-drop ALL`、uid 65534；probe 記錄 network blocked、input readonly、無 socket／.git／write token |
| G1 exact blobs | PASS | VERIFIED | checker 使用正確 Git blob NUL header；輸出通過，且 GPT 逐一回查 GitHub blobs |
| G2 unknown forms | PASS | REPRODUCED | 五種 unknown 均 exit 2、不回顯私密值／unknown token、提供 help |
| G3 negative control | PASS | REPRODUCED | 舊版 dash-leading case 確實回顯合成 secret，證明 control 有辨識力 |
| G4 legal paths | PASS | REPRODUCED | `--help` 與合法 `--needle=-...` 保持有效 |
| G5 affected suite | PASS | REPRODUCED | suite exit 0；README 宣稱與 TestLoader 均為 44；checker 原始碼未硬編碼 44 |
| G6 regressions／HTTP body | PASS | REPRODUCED | shrink、unchanged、equal rewrite、growth、lost needle 與 full／partial／transformed body 全符合預期 |
| G7 scope honesty | PASS | VERIFIED | evidence 明示非 clean install、非 live provider、非 adoption／license／release proof |
| External adoption | NOT_STARTED | OBSERVED | 仍為 0；本輪沒有邀請 |

## Evidence audit

- PR #10 共 1 commit、9 個 changed files，全部位於 `reviews/`；沒有產品程式碼或 state 變更。
- `RESULT.json`、`manifest.json`、`isolation_probe.json` 均可解析，run ID、heads、image digest 與 command 互相一致。
- `stdout.txt` 共 19 個 JSON lines，全部可解析，沒有 `passed:false`；涵蓋 G1–G7。G0 由先行 probe 與 Docker command 記錄。
- `reviewer_checks.py` 的 blob 計算使用 NUL byte，已修正 PR #9 計畫中的字面 `\\0` 問題；原始碼沒有硬編碼 44。
- PR #5 live head 回讀仍是 `304af885...`；PR #8 live head仍是 `b76fc7ba...`。
- Author evidence 的 runtime 行為由獨立 Cursor runner 重現；GPT 本身沒有第二次執行 PR code，因目前 reviewer runtime 無法建立合格 network namespace。

## Findings

沒有 P0／P1／P2 阻擋 finding。

### P3 — runtime attestation 邊界

Docker daemon 改用 vfs、image ID／digest 與 probe 結果均記錄在 runner 產生的 JSON；沒有平台簽署 attestation 或完整 daemon startup／inspect raw log。現有 exact blob、完整命令、probe output、test output、run URL 與獨立身分已足以關閉本 finding；不可把此證據外推成通用供應鏈或 release attestation。

### P3 — G7 是聲明完整性控制，不是行為測試

Checker 的 G7 驗證固定 limitations 字串是否包含邊界聲明。GPT 已另行檢查 PR body、RESULT、STATUS 與輸出，未發現越界主張。未來不要把 G7 的 exit 0 單獨當成 scope honesty 證明。

## Residual conditions

1. P5-R4-01 可標 CLOSED；`independent_runtime_verified=true` 僅限本 finding 與 exact PR #5 head。
2. PR #5 整體可提升為 APPROVED_WITH_CONDITIONS，不等於 merge／release 許可。
3. PR #8 保持 CONDITIONS_PENDING；剩餘條件是 A4 當日對象／渠道／帳號／immutable URL precheck，及 merge／發布前修正 EVIDENCE_FORMAT 的四／五筆 editorial backlog。
4. Claude persistent launcher、controller 與完整 end-to-end automation 仍未驗證；Cursor 單次 run 不提高 automation status。

```yaml
review_gate:
  decision: APPROVED
  reviewed_base: "834d3d148e054eca2ad048aa5bde709b5278d657"
  reviewed_head: "cf37880bb90d6f646591588f39de91df67d7923c"
  bound_implementation_head: "304af885193245da7186cb6b9ab247ec2494bd86"
  highest_evidence: REPRODUCED
  blocking_findings: []
  closed_findings:
    - P5-R4-01
    - M1_P5_R4_01_INDEPENDENT_ISOLATED_REPLAY
  conditions:
    - "evidence applies only to P5-R4-01 and the exact implementation head"
    - "do not interpret as clean install, live provider, license, release, or adoption proof"
  owner_decisions: []
  next_checkpoint: "PR8_DAY_OF_A4_INVITATION_PRECHECK"
  invalidates_when:
    - "PR #5 head changes from 304af885193245da7186cb6b9ab247ec2494bd86"
    - "evidence head or required artifacts change"
    - "new evidence invalidates isolation or replay results"
```

# PR #5 R5 窄範圍複核：32ca53c

## 給負責人的兩分鐘簡報

**整體目標：** 分享可採用的實用工具，提供透明可選 ATK 接入，推進外部採用。
**本輪處理：** 只核對 R4 最後一項 P5-R4-01 的修復與相關五檔變更。
**目前進度：** 實作方向符合修復要求；獨立運行驗收尚未完成。
**本輪成果：** OBSERVED：unknown token 原文回顯已改為數量及固定提示，README 與測試同步；已準備精確 SHA 的重放腳本。
**還有什麼風險：** 本環境無法建立所需隔離；31 個測試與正負控制本輪未獨立執行；外部採用及搜尋 T0 仍未證明。
**需要負責人決定：** 無新的方向或費用決策；目前缺可安全執行的 reviewer 環境。
**下一步與停止點：** 獨立 reviewer 在無秘密隔離環境執行本附錄，再決定關閉 P5-R4-01；不要重寫已提交修復。
**審查結論：** NEEDS_INFORMATION。待驗，不是程式失敗，也不是批准。

## 目標對齊

- 目標來源：可信 main 的 GOAL、1A／2A／3A、REVIEW-MAIN，以及本次 PR5 reviewer 授權。
- 本輪交付：針對工具回報輸出的最後修復，留下真實驗收狀態與可重放證據包。
- 主線連結：避免使用者因參數打錯而在回報中暴露 needle；不把安全修復數當採用成果。
- 必要驗證與停止點：普通值、dash 值、equals 形式不回顯，舊版負控制有效，合法路徑及既有 verdict／HTTP 行為不退步。
- 範圍差異：沒有新產品、依賴、benchmark、治理實作或 PR6 review。

## 審查身分與精確邊界

- Repository：firekou/Open-Skill-Distribution-Flywheel，PR #5，Draft、未合併。
- Reviewed head：`32ca53cd703efeb647ddb2d65168ba69f1e414d6`。
- 上次 reviewed head／本輪 diff 起點：`d1930e4696f11cfb3cdae2f59d1b3692b68ee127`。
- GitHub PR base snapshot：`204a7fe8d43a39962bb4beb313b7538484d433cb`；不把此快照誤當最新可信 main。
- 本輪可信 main snapshot：`f7d137657e09ba77d73e0182b82038fccbe5e508`。
- Reviewer：GPT/Codex，與 Claude executor 不同 run；2026-09-19 UTC。
- 已讀 main 的 AGENTS.md、OPERATING_RULES.md、decisions.json、state.json、STATUS.md 及兩份指定 skills。state.json 中 PR5 的舊 SHA 僅為快照；本輪以 live head 與此報告為準。
- GitHub compare 顯示僅一個新 commit、五檔變更：local_check.py、test_local_check.py、README.md、evidence/pr5-r5/controls.txt、executor response。不是純記帳 commit，不能只承接舊批准。
- PR 分支對 governance 狀態、權限或完成的自述均不覆寫可信 main。本輪不修改產品實作、不自審自批。

## 驗收與證據等級

| 驗收 | 狀態 | 證據等級與依據 | 缺口 |
|---|---|---|---|
| unknown token 不直接拼入自訂錯誤 | 靜態符合 | OBSERVED：parse_args 改為 len(unknown) 與固定文字 | 尚未跑真實 CLI |
| 普通、dash、equals、裸值、旗標五種情境 | 待驗 | TESTED：executor controls.txt 記錄均 exit 2、不回顯 | 本 reviewer 未獨立重跑 |
| 舊版負控制與合法路徑 | 待驗 | TESTED：executor 記錄舊版失敗、新版成功 | 待獨立負控制與合法路徑確認 |
| 31 個單元測試與文件數一致 | 待運行確認 | OBSERVED：README 兩處改為31；TESTED：executor 記錄31/31 | 本 reviewer 未運行 suite |
| verdict／HTTP error body 不退步 | 待驗 | 本輪 diff 未更改核心邏輯；前輪結果不冒充本輪實跑 | 附錄保留必要正負控制 |
| 安全隔離 | 不可用 | VERIFIED：三個無 PR code 的隔離能力 probe 均遭 OS 拒絕 | 缺可用隔離 runtime |
| PR5 reviewer 提交事件 | 本輪已抵達並開始檢核 | OBSERVED：本 run 取得事件並查 GitHub live head | 不等於隔離驗收、停止／去重或完整閉環已通過 |

## 唯一未完成項：P5-R4-01，修復已觀察、驗收待補

不新增產品 defect。本輪不能關閉原條件，原因是必要独立運行證據不足，而非已重現新版有錯。

安全能力檢查的實際輸出：
- bwrap 全隔離：`Failed to create NETLINK_ROUTE socket: Operation not permitted`。
- unshare 網路 namespace：`unshare failed: Operation not permitted`。
- bwrap user/filesystem 隔離：`setting up uid map: Operation not permitted`。
- Docker 不在 PATH。沒有要求升權、讀取秘密或降級為無隔離執行。

上述命令只執行標準 runtime 的安全探測，沒有載入或運行 PR 程式。
因此本輪沒有「31/31 VERIFIED」或「P5-R4-01 CLOSED」的運行結論。

## 最小交接封包與下一 checkpoint

此處交接的是驗證缺口，不是要求 executor 重新實作：

1. 獨立 reviewer 取得精確 head 的四個檔案與上一版 local_check.py，核對 manifest blob hashes。
2. 以無 secrets、無 GitHub write token、禁止外網、唯讀輸入及受限暫存的隔離 runtime 執行附錄。
3. 記錄完整命令、exit、stdout/stderr、實際隔離方式、Python 版本、run 身分與完整 SHA。
4. 五種 unknown 情境均 exit 2 且不回顯；舊版 dash 輸入須重現回顯，证明測試會抓到原缺陷。合法 --needle=...／--help、31 tests、縮小／等長／膨脹／丟 needle 與 HTTP body 控制須符合預期。
5. Reviewer 寫前重查 live head。若相同且必要控制全過，追加確認並結束本修復輪；如不同，先核對 diff，不將此結論套用新 head。

Claude 自行讀 repo，不需負責人搬運文件。本輪未喚起遠端 Claude，不宣稱已派工。沒有批准上游發送、merge、部署、金鑰使用或新增付費 API。
不為這個驗證缺口要求建立大型 CI 或恢復 benchmark。

## 可重放附件與未執行事項

- [isolation_probe.json](evidence/pr5-r5/isolation_probe.json)：本輪實際執行的隔離探測結果，pr_code_executed=false。
- [manifest.json](evidence/pr5-r5/manifest.json)：精確來源 Git blob hashes。
- [reviewer_checks.py](evidence/pr5-r5/reviewer_checks.py)：已準備、**本輪未執行**的必要控制。
- [README.md](evidence/pr5-r5/README.md)：安全重放條件與範例，亦未在本環境驗證。

沒有重跑乾淨安裝、真實 proxy、live ATK、歷史費用數字、搜尋基線或外部採用。executor 的「無條件安全」措辭不能由這個窄範圍測試推導成通用去敏保證；檔名、opt-in 輸出等仍需人工檢視。
executor 自報週期檢查與自動接手只標 REPORTED；本輪不驗 Claude launcher、PR6 或整套 ACTIVE。
同一 head 在沒有新證據時不再生成相同待驗報告或空提交。

```yaml
review_gate:
  decision: NEEDS_INFORMATION
  reviewed_base: "d1930e4696f11cfb3cdae2f59d1b3692b68ee127"
  reviewed_head: "32ca53cd703efeb647ddb2d65168ba69f1e414d6"
  trusted_policy_main: "f7d137657e09ba77d73e0182b82038fccbe5e508"
  highest_evidence: OBSERVED
  runtime_evidence: NOT_EXECUTED_ISOLATION_UNAVAILABLE
  blocking_findings: []
  conditions: [P5-R4-01_INDEPENDENT_RUNTIME_VERIFICATION_PENDING]
  owner_decisions: []
  next_checkpoint: "Secret-free isolated reviewer replay at exact head; recheck live head before closing R4 condition"
  invalidates_when:
    - reviewed scope changes
    - reviewed head changes
    - required evidence changes or fails
```

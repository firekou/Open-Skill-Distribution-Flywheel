# PR5 R9 最後限定修復覆核

## 給負責人的兩分鐘簡報

**整體目標：** 讓使用者可預期地試用 Headroom 與可選 ATK 接入，完成真實任務。
**本輪處理：** ATK-PR5-R7-LIVE-GUARD revision 2 最後修復，精確 head 304af885193245da7186cb6b9ab247ec2494bd86。
**目前進度：** 三個指定入口共四處 live 啟動均有重試限制；獨立 runtime 與外部採用尚未完成。
**本輪成果：** VERIFIED 原始碼及文件交叉核對，P5-R8-01 在指定入口的修復成立；不代表 live 實測通過。
**還有什麼風險：** 隔離重放不可用；範圍外 free sample 仍有舊指令；現存不同設定的 proxy 不受本腳本驗證。
**需要負責人決定：** 無。暫不需要金鑰，不重派第三輪。
**下一步與停止點：** 本修復包兩輪結束；等待合格獨立隔離重放，free sample 保留為未批准發布稿。
**審查結論：** NEEDS_INFORMATION

## 目標對齊與審查邊界

- 目標來源：GOAL-02、1A/2A、GOV-HANDOFF-TAKEOVER-20260921。
- 本輪交付：查清最小採用入口的 provider attempt 條件，解除過度費用承諾。
- 主線連結：服務工具試用與透明 ATK 接入，不增加 controller 或 benchmark。
- 必要驗證與停止：只查最後修復與已報告範圍外入口；两輪已滿，不改名重派。
- 範圍差異：一個 commit、六個檔案，四個 scope paths 加 executor response 與 evidence；沒有 local_check.py 或政策修改。

Repository: firekou/Open-Skill-Distribution-Flywheel, PR #5。
Trusted main: 1421b69ee4ec924a361aa74b860dbf1e4b24d557。
PR API base: 5ae0c76710d9646b63e017e564988b220147c136。
Repair source: cde4e5c855096b1d7566d44680259851810aec99。
Reviewed head: 304af885193245da7186cb6b9ab247ec2494bd86。
Date: 2026-09-21。Reviewer: GPT，獨立 reviewer run，未修改實作或作者證據。
Live PR: open / Draft / unmerged；讀取時 mergeable=true。PR body 仍是歷史 29-test/R3 狀態，不能用作現行批准。

## 驗收表

| 條件 | 結果 | 等級與依據 |
|---|---|---|
| 三入口全部使用 --retry-max-attempts 1 | 通過 source check | VERIFIED，README 40/274、TRY_IT 100、ab_test.py 5 |
| 旗標在固定版本代表總嘗試一次 | 通過 source check | VERIFIED，官方 commit 32d7ca4577d599b8a5f811ada74cf31504302c9d 的 CLI 映射及 server retry loop |
| client request 與 upstream attempt 分開 | 通過，有限條件 | VERIFIED，main() 先印 2*n / 4*n，再呼叫；文件明言無法辨識現存 proxy 設定 |
| 聚焦測試與負控制 | 作者紀錄存在 | TESTED，r8_controls.txt：四個 drift tests、兩個 mutants、44 tests；本 reviewer 未執行 |
| P5-R4-01 獨立隔離重放 | 未完成 | 本輪無作者重派，舊證據未視為獨立成功 |
| session/work_id/source/result/dedup | 完整 | OBSERVED，PR comment 5762403819；既有 session，不是新 launcher 證據 |

## Findings 與殘餘限制

### P5-R8-01：指定入口 source-level 修復確認

官方 CLI 將 flag 值傳入 retry_max_attempts，預設 3；non-streaming server 使用 range(retry_max_attempts)。
設成 1 時，429/529、5xx、transport error 分支不再進入第二次該 upstream 嘗試。
本輪三個指定入口全部對齊。此結论僅限固定版本、文件命令、單次執行與這條應用/proxy 路徑；不是 ATK 內部路由重試或金額上限的驗收。

### P2 P5-R9-01：成功次數的文字仍應收斂

README 與 ab_test docstring 的「A successful run makes two attempts either way」不嚴謹：
預設 retry=3 時，proxy 可能先失敗再成功，最終成功仍可能使用 3 或 4 個總 attempts。
已改正的有條件上限 2/4 不受影響；這不是再開第三輪的理由。
Disposition: 保留文字 backlog，下次既有文件整併時改成「無重試且完整成功的預設 run 為兩次」。
不用修改作者歷史報告，也不把文案 backlog 當新平台工作。

### 範圍外 free sample：保持草稿，不列入可用 live 入口

integrations/headroom-atk/offering/SERVICE_SAMPLE_FREE.md:26 仍無 retry flag。
該文件自己已聲明 reviewable sample / not a live service，並非本 packet 指定入口。
因此不宣稱整個交付目錄已全面關閉此風險；free sample 不得作本輪受驗證 live 試用指令。
發布前需同步安全旗標與條件說明，或改為只連結 TRY_IT；保留 BACKLOG_NOT_DISPATCHED，不另開第三輪。
ab_test docstring 的 pip install 尚未釘版本，若單獨照此安裝，0.37.0 驗證不適用；現行受核對安裝入口限定 README/TRY_IT 的 0.37.0。
以上範圍收斂不阻塞沒有 live 依賴的內容整理與採用規劃。

## 實際取證與沒有執行的檢查

- GitHub compare cde4e5c855096b1d7566d44680259851810aec99...304af885193245da7186cb6b9ab247ec2494bd86：ahead 1，六檔；讀取 commit diff 與完整目標檔。
- 靜態字串檢查（reviewer JavaScript，僅處理文字，不載入 PR code）：四條命令都有 flag，三份文件都有設定失效條件。
- 官方來源：
  - https://github.com/headroomlabs-ai/headroom/blob/32d7ca4577d599b8a5f811ada74cf31504302c9d/headroom/cli/proxy.py
  - https://github.com/headroomlabs-ai/headroom/blob/32d7ca4577d599b8a5f811ada74cf31504302c9d/headroom/proxy/server.py
- Exact-head combined statuses=[]，workflow_runs=[]。未取得獨立 check-runs 清單，不將其寫成通過或零。
- bwrap --unshare-all --die-with-parent --ro-bind /usr /usr --symlink usr/bin /bin --proc /proc --dev /dev --tmpfs /tmp --clearenv /bin/true
  - exit 1: bwrap: loopback: Failed to create NETLINK_ROUTE socket: Operation not permitted
- unshare --user --map-root-user --net /bin/true
  - exit 1: unshare: write failed /proc/self/uid_map: Operation not permitted
- Docker/Podman 未找到。未繞過隔離執行 PR code、作者測試或模型呼叫。
- 作者 44 tests/mutants 為 TESTED；source checks 為 VERIFIED。缺 runtime 是能力缺口，不是測試失敗。
- 寫入前再次核對 live head 仍為 304af885193245da7186cb6b9ab247ec2494bd86。

## 下一 checkpoint 與交接規劃

1. 關閉本包自動修復循環：rounds_used=2，limit=2，RESULT_RECEIVED_REVIEWED；無新派工。
2. 合格獨立 reviewer runtime 可用時，釘本 head 與固定依賴，無秘密、無外網、唯讀來源、無 GitHub write token；重放既有 P5-R4-01 證據與本輪受影響測試/controls。原始證據保留；不可只拿舊 head 的 PASS 套新版本。
3. free sample 的舊指令與 P2 文案列發布前 backlog；只限文件整併或移除重複入口，不授權第三輪實作。
4. 通過必要獨立驗收後，依既有可審稿推進非作者使用者試用。外部聯絡/發布仍需其既有授權；無授權時備稿即可。第三方採用目前為 0，不能用內部重放替代。
5. 真實 live 測試仍需輪替後安全注入的 key、端點/model 與明確費用上限；本輪不要求提供、不取回舊 key。
6. Claude 持久 launcher / executor_connected / end_to_end 不升格。已有 session 回傳成果及 reviewer 取回成立；不證明新 session 自動啟動。
7. PR6/7、benchmark、Freeze 與框架試點不改；沒有依賴的產品工作不等待 controller ACTIVE。

```yaml
review_gate:
  decision: NEEDS_INFORMATION
  reviewed_base: "cde4e5c855096b1d7566d44680259851810aec99"
  reviewed_head: "304af885193245da7186cb6b9ab247ec2494bd86"
  highest_evidence: VERIFIED
  blocking_findings: []
  conditions:
    - P5-R4-01 independent isolated replay pending
    - current-head affected tests not independently rerun
    - free sample excluded from verified live entry points
  owner_decisions: []
  next_checkpoint: "QUALIFYING_INDEPENDENT_REPLAY_NO_THIRD_REPAIR"
  invalidates_when:
    - reviewed content or evidence changes
    - Headroom version or retry configuration changes
    - required replay fails
```

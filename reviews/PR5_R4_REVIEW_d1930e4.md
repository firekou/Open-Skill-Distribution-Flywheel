# PR #5 收斂複核：d1930e4
## 給負責人的兩分鐘簡報
**整體目標：** 可採用的實用工具與透明可選 ATK 接入，驗證服務分發。
**本輪處理：** 查最新提交、重跑修復測試，確認持續 reviewer 的真實觸發設定。
**目前進度：** PR 維持 Draft、未合併；尚無第三方採用證據。
**本輪成果：** 獨立運行 29 個測試通過；HTTP 錯誤 body 不再輸出，含原生片段與變形負控制。最高證據 REPRODUCED。
**還有什麼風險：** 一項 P2 CLI 私密文字回顯殘留；live 歷史量測未重跑；Claude 尚無遠端自動啟動連接。
**需要負責人決定：** 無。修復已有授權，不重問 1A/2A/3A。
**下一步與停止點：** 只修以下 P5-R4-01，附正負控制並提交 SHA；reviewer 做窄範圍確認後結束修復輪。
**審查結論：** APPROVED_WITH_CONDITIONS。允許內部進度，未批准對外發布或合併。

## 身分與範圍
- repository: firekou/Open-Skill-Distribution-Flywheel
- base: 204a7fe8d43a39962bb4beb313b7538484d433cb
- head: d1930e4696f11cfb3cdae2f59d1b3692b68ee127
- reviewer: GPT/Codex，與 Claude executor 不同工作階段；2026-09-19 UTC
- 隔離目錄 /tmp/pr5-current，由 GitHub 精確 SHA 取回檔案。程式未帶 provider key；未作付費或 live provider 呼叫。
- 主線連結：修好使用者可以自行採用與分享結果的入口，不建立 benchmark。
- 範圍差異：只增加托管 PR5 reviewer 事件觸發，沒有新平台、executor launcher、支出或 merge 授權。

## 驗收
| 項目 | 結果／證據 | 限制 |
|---|---|---|
| 既有單元測試 | VERIFIED：python3 test_local_check.py，29/29 | process/network 多以 mock 取代，不能當乾淨安裝驗證 |
| 縮小正控制、等長、膨脹、丟 needle | REPRODUCED：exit 0/3/3/1 | 獨立選案例，沿用 executor 測試 helper，不宣稱真實 proxy |
| HTTP error body 完整／部分／反轉 echo | REPRODUCED：均不回顯，status 401 可見，舊 debug 環境變數無效 | 關閉 P5-01 本次 HTTP error body 範圍，不宣稱所有輸出通用去敏 |
| README 測試數 | VERIFIED：29 與運行一致 | 未重跑過往 live token 計量 |
| 普通 needle 輸出、普通錯字值 | VERIFIED：既有測試與 reviewer 控制通過 | 以下 dash 開頭值仍回顯 |
| 上游 logging 修正 | OBSERVED：撤回錯誤因果，改寫 handler/propagate 機制並附紀錄 | 本 reviewer 環境未重裝 headroom，未獨立重現其三次 log 記錄 |
| Claude 手動 review loop | OBSERVED：兩份 SHA 綁定 reviewer 文件、executor 補註 | session/隔離身分是其披露，本輪未取得平台 run audit，不能據此證明持久自動化 |

## P5-R4-01 / P2：未知參數的「旗標」仍可能是私密值
位置：integrations/headroom-atk/local_check.py，parse_args 的 unknown 列表處理。
目前將所有 startswith("-") 的 token 當成旗標輸出。對這個已承諾可分享輸出的介面，私密 log 文字本來就可能以連字號開頭。

可重放（全為合成資料）：
```bash
python3 local_check.py --needlez -SYNTHETIC_PRIVATE_42
```
實際 exit 2，stderr 包含：
```
error: unrecognized option(s): --needlez, -SYNTHETIC_PRIVATE_42
```
對照：普通值不回顯；--needlez=-SYNTHETIC_PRIVATE_42 不回顯。29 個現有測試全過，仍漏掉分開傳入且 dash 開頭的值。不是 API key 已外洩的證據，是「可分享输出不含 needle」未完整成立。

最小修正：未知參數只輸出固定錯誤提示與 --help 指引，不回顯任何原始 unknown token；或使用可證明不洩漏的已知選項白名單。不要再建立通用 secret 遮罩器。
驗收：普通值、dash 開頭值、equals 形式均 exit 2 且 stdout/stderr 不含合成私密文字；合法 --needle=... 仍能進入原有檢查，--help 正常。維持原縮小／不縮小正負控制及已修 HTTP body 行為。必要文件僅同步實際承諾／測試數，不追加框架。

## 證據與未執行
- reviews/evidence/pr5-r4/reviewer_checks.py：從該 SHA 的 integrations/headroom-atk 執行。
- reviews/evidence/pr5-r4/reviewer_output.json：本輪實際輸出。
- 29 個 unit tests 真實運行，Python 3.12；沒有乾淨安裝 headroom、沒有 live ATK、沒有新增搜尋基線，也沒有第三方使用測試。
- 不把既有小範圍修復放大成量測產品。上述一項條件完成就結束修復輪；其他新想法列 backlog。
- PR body「修復輪已結束」現在應補本次條件，不可把本份條件式通過當 release 授權。

## 觸發程序的實際狀態
2026-09-19 查到既有排程「ATK 治理續作」為每小時一次，但 repo 是 firekou/virtual-strategy-lab；沒有覆蓋本 repo。沒有更動它。
本輪已註冊並啟用「ATK PR5 提交複核」：GitHub PR #5，enable_commit_updates=true，comments/reviews=false。沒有時間輪詢排程。工具回傳成功，但尚未收到真實事件的執行證據；無五分鐘延遲保證。
未審新 SHA → 讀可信 main 規則 → 必要獨立檢查 → reviews 寫 main → 更新交接。已審 SHA 無新證據則不重做。報告留 main，不為記帳改被審 PR head。
這只接 reviewer。沒有 Claude launcher，也未驗過持久鎖、停止開關、重送控制的完整運行；不把指令裡的去重要求當成強制控制已驗收。整套治理仍非 ACTIVE。
工具不支援 5/10 分鐘輪詢；未建立不符合要求的 hourly 替代排程。

```yaml
review_gate:
  decision: APPROVED_WITH_CONDITIONS
  reviewed_base: "204a7fe8d43a39962bb4beb313b7538484d433cb"
  reviewed_head: "d1930e4696f11cfb3cdae2f59d1b3692b68ee127"
  highest_evidence: REPRODUCED
  blocking_findings: []
  conditions: [P5-R4-01]
  owner_decisions: []
  next_checkpoint: "Claude 修正 unknown-token 回顯，提交新 SHA；GPT 窄範圍確認後收輪"
  invalidates_when: [reviewed scope changes, reviewed head changes, required evidence changes or fails]
```

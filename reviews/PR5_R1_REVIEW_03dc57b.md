# PR #5 第一輪 review：03dc57b

## 給負責人的兩分鐘簡報

**整體目標：** 外部 Agent 發現實用工具、順利接入、解題，讓 ATK 得到可觀察的採用與價值回收。
**本輪處理：** headroom 整合、離線採用檢查、分發稿及服務樣本。
**目前進度：** 已有具體工具設定與測試資產；外部自發採用尚無紀錄，乾淨安裝尚未驗證。
**本輪成果：** reviewer 獨立重現兩個程式缺陷，並核對證據與商業稿。最高 REPRODUCED，僅指下述合成邊界重現，不代表真實 headroom/live 重跑。
**還有什麼風險：** API 錯誤洩漏憑證；膨脹也判 PASS；對外主張及入口超前證據。
**需要負責人決定：** 下一階段市場試驗及商業樣本定位另在對話選擇；修復不需另批。
**下一步與停止點：** 在原 PR 修復下列範圍，提交正負控制、新 SHA 與回覆。不要恢復通用 benchmark。
**審查結論：** BLOCKED。

## 身分與目標對齊

- repository: firekou/Open-Skill-Distribution-Flywheel；PR #5，Draft、未合併。
- base: d6912cf2b9ef0df51ed69ee3aeb670a4e12742aa
- head: 03dc57b20e7cce1a5fbd2893ccc921f98675eeb2
- reviewer: Codex；2026-09-18。
- 目標來源：最新使用者指示、AGENTS.md、ATK_AGENT_DISCOVERY_AND_ADOPTION.md。
- 本輪交付：能被陌生使用者照做的 headroom + 可選 ATK 接入。
- 主線連結：現有工具採用及技術分發，不新增量測產品。
- 必要驗證與停止點：入口可跑、安全錯誤處理、採用判定正確、主張符合證據。
- 範圍差異：付費量測只是未批准樣本，不能自行升格為公司方向。

## 驗收

|項目|結果／證據等級|缺口|
|---|---|---|
|原生設定、可替換 ATK|OBSERVED，README 與腳本有明確設定|本輪未跑真實 gateway|
|離線採用判定|REPRODUCED，正控制縮小 PASS；不變 exit 3；丟失 needle exit 1|膨脹／等長改寫也 PASS|
|API 錯誤安全|REPRODUCED|合成 secret 原樣輸出|
|live 37.1%|OBSERVED，提交 JSON 中兩個 usage 支持算術|原始輸入遺失；不是 reviewer VERIFIED；不是完整 raw response|
|乾淨安裝|REPORTED 未執行|安裝未釘版本，試用環境已預裝|
|外部發現|REPORTED 0/3、16 查詢|提交檔未附完整逐條查詢／結果／時間；不能重跑同一組|
|外部採用／收入|無紀錄|受控 agent 不等於第三方|
|品牌／付費樣本|OBSERVED|商業承諾矛盾，尚非可對外版本|

## Findings

### P5-01 / P1：ab_test.py 再次直接輸出 API 錯誤本文

HTTPError handler 讀 body、切 400 字元，直接 SystemExit。以合成 key 的 401 body 代入實際 call()，key 出現在 exception 訊息。不是猜測真實 provider 會否回顯，也未使用真實 key。

修復：預設只顯示狀態與安全診斷；若保留 debug，完整清理後才截斷，涵蓋部分回顯，不要只檢查完整 key 不在字串。此類別曾在 PR #4 修過，應復用已知安全行為，不必建立共用框架。
驗收：正常回應正控制；完整 key、前後片段與截斷邊界錯誤負控制。不能將真實秘密放入測試。

### P5-02 / P1：local_check.py 的 PASS 不要求縮減

只用 via == direct 判 NO BENEFIT，未要求 len(via) < len(direct)。
同一實際 main() 決策路徑，替換 process/network 邊界以合成收到的 body：
- 300 → 4 chars，needle 在：exit 0。
- 300 → 300 原文：exit 3。
- 300 → 800 chars，needle 在：exit 0，印 -166.7% fewer 與 PASS。
- 300 → 300 改寫，needle 在：exit 0。
- needle 丟失：exit 1。

這是採用判定邏輯的獨立重現，不表示 headroom 實際產生過該膨脹結果。
修復：PASS 明確要求嚴格縮減且 needle 都存在；等長與膨脹非成功，說明不得稱 byte-for-byte；拒絕空 needle，避免無意義 survival check。
驗收：上述五條正負控制及空 needle；無需付費模型。

### P5-03 / P2：可採用入口未達自身承諾

README 標 0.37.0，但安裝命令未釘版本。registry example 在 repo root 產生 deploy.log，而 local_check.py 讀 script 同目錄，兩者不一致。免費樣本只叫使用者換 localhost endpoint，未同步帶上自訂 upstream header，與自身記載的錯路由風險衝突。免費樣本 clone 預設 main，但本資產仍在 Draft 分支；根 README 入口也尚未加上。

修復：提供明確 checkout ref／工作目錄與釘版安裝；同步 README、registry、免費樣本的可跟做指令。乾淨 venv 驗證安裝和離線正控制，未發布路徑標清楚。不要為此合併 PR 或使用 key。

### P5-04 / P2：主張、證據及商業樣本需收斂

1. 已提交 usage 的 prompt tokens 合計為 40572+29781+40589+25525 = **136467**；UNIT_ECONOMICS 寫兩任務兩路徑約 81k，漏計了壓縮路徑。修正數字；未量測的人力/compute 不應當成已知很小。
2. 付費樣本一處承諾未達 saving threshold 退款、另一處說負面結果照收費。保留為待選方案或依負責人決策統一，不能同時承諾。
3. 「空位沒人佔」「JSON log 完全沒用」「needle always survives」「摘要失敗不是壓縮問題」均超出有限案例能證明的範圍。縮到測過的版本、payload、prompt；兩路徑均失敗不排除壓縮另外造成損失。
4. 63% prompt cost 與無貨幣成本主張相衝突，改 prompt tokens。JSON 僅含 usage/text，不稱完整 raw response；cost_usd:null 未出現在提交的摘錄，需標自報或補既存去敏證據，不要求為補表而付費重跑。
5. 搜尋試驗未附可核對完整 query log。補已存在的原始紀錄；不存在就標遺失、建立新基線，不能宣稱可重跑「同一組」。0/3 不足以判定根因就是命名，也可能尚未索引／分支入口無導覽。
6. 免費樣本宣稱 paid-for placement 與推薦完全不受 ATK 影響，未見支持。改明示 ATK 自有品牌推廣／樣本，避免捏造贊助交易或獨立性。

## 驗證方法與限制

Python 3.12.14；執行 reviewer_checks.py，動態載入 head 原始兩份腳本，以 unittest.mock 替換網路與程序。未改 executor 程式。
重放：將 head 的 local_check.py、ab_test.py 與本 review 的 evidence/pr5-r1/reviewer_checks.py 放同一目錄，執行 python reviewer_checks.py。
腳本輸出供核對，不以其自身 exit 0 表示被測資產通過。

本環境未安裝 headroom，未跑完整 offline proxy、乾淨安裝、registry build 或真實模型。沒有使用已暴露憑證、付費請求、對外投稿或合併。已檢查 PR patch 的 16 個變更路徑及相關指示；上述不足不宣稱全部路徑功能失效。

## Claude 交接

先修 P5-01、P5-02，同步 P5-03／04 的必要入口與主張。既有免費／付費商業樣本先保持 draft，待本輪負責人決策後更新。修復回覆追加至 ATK_AGENT_DISCOVERY_EXECUTOR_RESPONSE.md，列新 SHA、命令、結果與尚未驗證事項，送回 review；不要自己標 APPROVED。

不要把本次結論擴張成 benchmark 修復或付費驗證平台。後續主線仍是一個工具被外部找到並使用。歷史 findings 保留。上游聯繫待明確授權；key 由帳戶持有人輪替。

```yaml
review_gate:
  decision: BLOCKED
  reviewed_base: d6912cf2b9ef0df51ed69ee3aeb670a4e12742aa
  reviewed_head: 03dc57b20e7cce1a5fbd2893ccc921f98675eeb2
  highest_evidence: REPRODUCED
  blocking_findings: [P5-01, P5-02]
  conditions: [P5-03, P5-04]
  owner_decisions: []
  next_checkpoint: 修復兩個程式缺陷、同步入口與主張，提交新 SHA 和最小正負控制
  invalidates_when: [reviewed scope changes, reviewed head changes, required evidence changes or fails]
```

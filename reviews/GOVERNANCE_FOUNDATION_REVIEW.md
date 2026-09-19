# 治理基礎自查與正式導入條件
2026-09-19，planner Codex 自查。不是獨立review，也不代表runtime已部署。

## 用戶四項要求
|要求|落地|
|---|---|
|統一有效入口|governance/OPERATING_RULES.md；AGENTS、CLAUDE、Claude執行入口與reviews入口只導向同一處；root README移除舊首批候選排程|
|已決策不重問|decisions.json保留GOAL、1A、2A、3A、GOV-01、main寫入與key狀態；方向批准與發送批准分開|
|缺陷轉成精煉檢查|規範內8類按改動觸發檢查；preflight.py提供離線派工／review binding檢查|
|協作流程精煉|角色、state轉移、可信main、去重／租約、SHA、限額、停止及驗收都有指定責任|

## 已執行
Python 3.12.14：
- python -m unittest discover -s governance -p 'test_*.py'：5個測試方法通過，其中12個邊界subcases。
- skill-creator quick_validate.py：更新的atk-goal-alignment skill valid。
- 正控制：execute被允許；獨立review BLOCKED→FIX_PENDING，APPROVED→COMPLETE，條件批准→CONDITIONS_PENDING。
- 負控制：舊SHA／state、自審、merge動作、無授權、停止開關、重複事件、費用／時間／次數超限、NaN、錯型別、缺證據與錯review binding。
這些測試只證明離線guard在合成輸入下的行為。DISPATCH_ALLOWED並沒有真的啟動agent。
身份、授權、live head與費用欄位由未來可信controller取得，不可直接採信PR自行填寫。
guard不提供持久鎖、事件簽章、證據真偽驗證、沙箱或費用預留；IMPLEMENTATION_PROMPT明列其必要runtime實作。

## 自查發現與修正
- 舊CLAUDE_EXECUTION_START仍含Lab派工：改為單一入口，歷史留Git。
- main無CLAUDE.md：新增精簡入口。
- 最新state不能繼續寫等待f41f8d9修復：改d55911e待R3，沒有擅自批准。
- 舊治理全面暫停與新用戶授權衝突：GOV-01明確取代有限導入範圍，通用benchmark仍暫停。
- 無API預算卻要求live閉環會迫使違規或假報：先完成無費用replay，再用capability表提出具體activation條件。
- 文件review與程式部署混淆：明列FOUNDATION_ONLY、REPLAY_VERIFIED、MANUAL_RUN_VERIFIED、ACTIVE各自證據。

## 可交辦結論
規範與離線guard足以作為下一個「最小自動交接實作」的具體輸入，已備好IMPLEMENTATION_PROMPT。
本輪沒有安裝外部治理框架、live webhook或排程，沒有使用key、付費模型、merge或對外訊息。
下一步先獨立驗規範與guard，再交付runtime Draft PR，接受獨立review，最後才掛接有限真實觸發。不能用本自查自我核准production。
新實作不得擴到50～100席、計量產品或全公司治理平台。主線仍是ATK工具分發與採用。

## 正式啟動驗收
1. 對指定task有真實executor/reviewer不同run身分，實際自動交接run IDs。
2. 重送／競爭／重啟不重複動作，舊head approval無效。
3. stop、逾時與預算預留可阻斷動作；PR內容不能控制可信政策或竊取token。
4. event→executor→review→必要修復→結案不用負責人搬文。
5. 可停用／復原，費用與權限明確；未通過前不得把state寫ACTIVE。

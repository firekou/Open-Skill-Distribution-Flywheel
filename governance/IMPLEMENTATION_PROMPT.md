# Claude 導入交辦：先驗基礎，再接通一個自動閉環

負責人已授權這項導入，不重問是否要治理。你是 executor，不是最終 reviewer。
先 fetch 最新 main，讀 governance/OPERATING_RULES.md、decisions.json、state.json。舊治理全面暫停已被 GOV-01 的有限導入取代。ATK 主目標仍是工具採用。

## 交付順序
1. 執行 python -m unittest discover -s governance -p 'test_*.py'，查入口與既有決策。發現矛盾先修，不照字面硬跑。
2. 只讀盤點現有執行環境：能否非互動啟動 executor/reviewer、其憑證與費用模式、可用持久觸發器／worker、GitHub 權限、可隔離測試的方式。記錄 capability evidence，不顯示 secret、不假定聊天 session 是可呼叫 API。
3. 先從既有收藏挑可直接補自動交接的工具，最多比較兩個；現成 GitHub 事件與薄 runner 足夠就用，不為採用知名框架重建平台。只在確定介面時查官方文件。缺 API 能力也要完成以下 fake-runner 閉環，不能只回報缺憑證。
4. 在獨立分支建立最小 controller 與 executor/reviewer adapter，工作單採本規範契約；調用可信 preflight，加入持久 CAS／鎖、事件去重、超时／取消、run 身分、精確 SHA、費用上限及可追查事件。preflight 本身不提供上述 runtime 能力。
5. 首先使用不呼叫模型的 fake executors，在隔離暫存 repo 演練：執行產出 → REVIEW_PENDING → 獨立 review BLOCKED → 修復新 SHA → 新 review APPROVED。整段一次啟動後不用人搬檔。此成果標 REPLAY_VERIFIED，不冒稱 AI 真實工作。
6. 負控制：重複事件／同時 worker 只執行一次；途中換 head 拒收舊 review；同 run 自審拒絕；條件批准不能 complete；崩潰重啟不重做已完成寫入；超時、預算不足與 stop 開關停止；PR 中惡意修改規範不能讓 runner 放寬。
7. 提供真實模式配置範本，預設禁用 live dispatch。模型、費用、GitHub token 由既有可信環境注入，不寫 git。若能力／額度不足，列精確缺口與最小開通步驟；完成其餘交付後再交 planner，不叫負責人重新選1A／2A／3A。
8. 開 Draft PR，將回覆寫 reviews/GOVERNANCE_EXECUTOR_RESPONSE.md，綁定 head、實際命令、事件紀錄、測試、限制、選型依據與 activation checklist。不要合併，不修改 main 的信任政策，不啟用 production webhook。
9. 獨立 reviewer 通過此 PR 後，在既有權限／費用內驗證一項限定範圍的真實 AI 自動任務；啟動仍需實際可用的 runtime 與觸發器。保留真實 run IDs。未接通不得寫 ACTIVE。

## 交付與停止
必須交：controller/adapter、契約範例、正負控制、重啟證據、disable/rollback、runtime capability表。
缺 access 不阻塞離線實作；未授權支出不以模糊預算繞過。
PR #5 的 d55911e 仍待獨立 R3，不在治理實作 PR 修改產品程式，也不自我批准。治理驗收不以 PR #5 必须合併為前提。
首版只支援一項工作、串行執行與review。不要擴張到50～100席。
完成 Draft PR 即交 reviewer。最終只報可自動做到哪一段、是否有持久觸發、哪個真實證據、剩餘存取或商業決定。

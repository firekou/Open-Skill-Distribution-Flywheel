# Review 協作入口

規則唯一來源：[governance/OPERATING_RULES.md](../governance/OPERATING_RULES.md)。
決策唯一來源：[decisions.json](../governance/decisions.json)。
任務快照：[state.json](../governance/state.json)，開始工作仍需查 live head。
最新審查：[STATUS.md](STATUS.md)。

## 交接檔案
- 產品 executor：ATK_AGENT_DISCOVERY_EXECUTOR_RESPONSE.md（PR 工作分支）。
- 產品 reviewer：PR5_R3_REVIEW_<short-sha>.md；R3 尚未執行，不能沿用 R2 判定新 head。
- 治理 executor：GOVERNANCE_EXECUTOR_RESPONSE.md（新導入 PR 工作分支，尚待建立）。
- 治理 reviewer：GOVERNANCE_REVIEW_<short-sha>.md（尚待獨立複核）。
- 歷史 finding/review 不覆寫；新版明列哪些關閉、哪些保留。

提交綁完整 SHA、環境、命令、正負控制、證據路徑與限制。修復先標 IMPLEMENTED_PENDING_REVIEW。
只有reviewer判關閉；只有已授權的發布動作才可發布。自動交接的啟動證據另按治理入口驗收，文件不會自行啟動程序。

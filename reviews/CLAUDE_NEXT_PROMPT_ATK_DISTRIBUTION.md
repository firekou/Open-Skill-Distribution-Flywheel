# 現行產品交接：PR5 等待獨立隔離驗證

2026-09-21 接管更新：先讀可信 main 的治理入口、decisions、state 與 reviews/STATUS.md，啟動時核對 live head。
最新 review 為 reviews/PR5_R6_REVIEW_933446ab.md，綁定 933446ab230e6fb8b41d79b596ef3c19b721fb7a，NEEDS_INFORMATION。P5-R4-01 作者已修復並送證，剩下獨立隔離 reviewer 重放既有 reviews/evidence/pr5-r5/README.md 的證據，不再要求作者重複同類自跑證據。
1A／2A／3A、免費技術資產、可選 ATK 接入、分發及採用主線維持；已有 headroom 小交付，不因舊三候選 prompt 重新造工具。治理 PR6 不作本產品驗收的額外前置門檻；通用 benchmark、Freeze 與框架試點不重開。
新內容才重審；無新 head/證據安靜結束。通過後做既有入口發布準備與搜尋／採用驗證，對外送出、merge、部署遵守原授權。
GitHub 交接已由 govern-github-agent-handoffs 接管。reviewer 事件登記涵蓋本 repo；Claude 新 session 持久 launcher 未驗證。報告與摘要仍寫 main。下列內容保留為歷史，不再重派。

## 歷史 R4 工作單

# 現行產品任務：PR #5 完成一項 R4 條件

先讀可信 main 的 governance/OPERATING_RULES.md、decisions.json、state.json，核對 live PR #5。
1A／2A／3A 已批准，勿重問。既定 headroom 交付、免費品牌與上游備稿範圍不變。

最新獨立 review：reviews/PR5_R4_REVIEW_d1930e4.md，綁定 d1930e4696f11cfb3cdae2f59d1b3692b68ee127，APPROVED_WITH_CONDITIONS。
Executor 只修 P5-R4-01：parse_args 不得回顯任何未知 raw token，包含被誤當旗標的 dash 開頭 needle。最小方案是固定錯誤提示加 --help 指引。依 review 的普通值、dash 值、equals、合法參數正控制驗收；同步受影響文件與實際測試數，提交新 SHA。
若 live head 已改，先比對差異與是否已有新 review，不套用過期通過。

Reviewer 下一份 PR5_R4_CONFIRM_<short-sha>.md，只確認此條件及直接回歸；達標結束修復輪。不重开benchmark，不再挑三工具或造adapter。
產品交付通過後，下一步是入口發布準備及搜尋／採用驗證；合併、發布、About/topics、上游送出仍遵守既有界線。

本輪已註冊PR5新commit事件GPT review，首次事件尚未驗證；沒有遠端Claude launcher。報告與記帳寫main，不在被審分支追加observed_head補寫commit。GOV-BOOTSTRAP勿重複建立同一reviewer觸發器，也不得稱完整閉環ACTIVE。

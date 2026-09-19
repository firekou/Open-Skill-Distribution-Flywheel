# 現行產品任務：PR #5 完成一項 R4 條件

先讀可信 main 的 governance/OPERATING_RULES.md、decisions.json、state.json，核對 live PR #5。
1A／2A／3A 已批准，勿重問。既定 headroom 交付、免費品牌與上游備稿範圍不變。

最新獨立 review：reviews/PR5_R4_REVIEW_d1930e4.md，綁定 d1930e4696f11cfb3cdae2f59d1b3692b68ee127，APPROVED_WITH_CONDITIONS。
Executor 只修 P5-R4-01：parse_args 不得回顯任何未知 raw token，包含被誤當旗標的 dash 開頭 needle。最小方案是固定錯誤提示加 --help 指引。依 review 的普通值、dash 值、equals、合法參數正控制驗收；同步受影響文件與實際測試數，提交新 SHA。
若 live head 已改，先比對差異與是否已有新 review，不套用過期通過。

Reviewer 下一份 PR5_R4_CONFIRM_<short-sha>.md，只確認此條件及直接回歸；達標結束修復輪。不重开benchmark，不再挑三工具或造adapter。
產品交付通過後，下一步是入口發布準備及搜尋／採用驗證；合併、發布、About/topics、上游送出仍遵守既有界線。

本輪已註冊PR5新commit事件GPT review，首次事件尚未驗證；沒有遠端Claude launcher。報告與記帳寫main，不在被審分支追加observed_head補寫commit。GOV-BOOTSTRAP勿重複建立同一reviewer觸發器，也不得稱完整閉環ACTIVE。

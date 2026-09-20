# 共用工作、證據與交接模板

版本：AGENT-HANDOFF-001 / 1.0.0。先讀 [專案接合](AGENT_METHOD_APPLICATION.md)，補齊該 repo 必填欄位。

模板不代表任務已建立或已派送。複製到實際工作包並填完欄位；未知寫 UNKNOWN，不填假零值。沿用既有 review_gate。

## GPT 計畫
- task_id / revision：
- 目標與業務主線：
- 授權來源、範圍、排除事項：
- policy_ref / plan_commit_sha / expected_head_sha：
- 協調 PR / 成果 PR：
- 假設、基準、實驗單位：
- 成功門檻、分母、觀察窗口：
- 外部證據取得方式：
- 探索條件與批次規模：
- 確認集隔離及負控制：
- 截止時間、用量界線、停止及恢復條件：
- executor / independent_reviewer / next_actor：
- 本 repo 正式任務狀態／對應概念階段：
- 修復輪數：0 / 2

## Claude 執行報告
- run_id / session_url / 開始及結束時間：
- 固定輸入版本 / result_head_sha：
- 實際修改及計畫差異：
- 完整重播命令、環境、exit code：
- 原始證據位置及雜湊；敏感原文僅受控引用：
- 嘗試數 / 不同條件數 / 獨立單位數 / 有效結果數 / 重試數：
- 成功、失敗、缺失與逾時：
- 外部觀察／推論／mock 結果分列：
- 實際用量與等待時間：
- 未解問題、停止理由、建議 next_action：
- 請求 GPT review 的精確成果版本：

## 獨立 review
- reviewer / session 或 run ID / reviewed_head：
- 作者與 reviewer 是否分離：
- 所見原始證據與可重播結果：
- 成功門檻是否事先凍結、確認資料是否污染：
- 阻擋 ID、嚴重度、最小修正：
- 既有正式 review_gate：
- 業務 outcome 與適用範圍：
- 下一輪／交付／等待及原因：
- 是否可依既有授權合併；所核對 checks：

## 局部能力紀錄
在條件＿＿下，方法＿＿版本＿＿於期間＿＿以獨立確認達到＿＿。
證據＿＿；已知反例＿＿；未覆蓋＿＿；失效訊號＿＿。
維護者＿＿；最後驗證時間＿＿；可重用回歸案例＿＿。
後續反證另開批次，不延後已達標的授權內交付。

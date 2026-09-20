# GPT 規劃檢核、Claude 執行與外部實證運作方法

方法 ID：AGENT-HANDOFF-001；版本：1.0.0；同步日期：2026-09-20。
來源：[雜誌社方法固定版本](https://github.com/firekou/virtual-strategy-lab/tree/1d128151eee6fd9c1251228c2933e0062eca21ef/projects/atk-magazine/operations)。
本版將雜誌社方法整理成跨 repository 共用規範。VSL 協調共用版本，三個 repository 保存相同正文；專案目標、狀態與授權由 [專案接合](AGENT_METHOD_APPLICATION.md) 指向現行入口。

## 文件入口

- [交接手冊](AGENT_HANDOFF_RUNBOOK.md)：狀態、事件、版本、去重與恢復。
- [工作模板](AGENT_TASK_TEMPLATE.md)：計畫、結果、獨立 review 與局部能力。
- [雲端導入包](AGENT_CLOUD_ADOPTION_PLAN.md)：能力盤點、訂閱接線與端到端驗收。
- [專案接合](AGENT_METHOD_APPLICATION.md)：現行治理、目標及必要欄位。
- [共用實驗準則](EXPERIMENT_GUIDELINE.md)、[實驗接合](EXPERIMENT_APPLICATION.md)。

## 目的與分工

以最短有效回饋時間取得外部結果，累積可重用、可反證的局部能力，降低負責人搬運 prompt、追問報告與核對版本的時間。GPT 負責規劃、成功條件、獨立檢核及下一步；Claude 負責實作、研究、實驗與修復。作者不能自批，GPT 作者的實作也需另一獨立 reviewer。

確定性程式負責事件、排隊、持久領取、版本與用量，不判定內容真偽。第三模型按具體證據缺口加入，不以多數投票判定成功。已有授權直接沿用；必要新商業決定提出具體可審方案，不逐輪重問。

## 實驗循環

先定義目標、基準、成功門檻、分母、窗口與外部回饋管道，再拆成小實驗。探索由小批開始，依新增資訊擴至 100 或 1,000 次，保留失敗、缺失與重試，分開嘗試數與獨立單位数。
選定候選後凍結方法，以新資料、時段或場域獨立確認；成功後測負控制、邊界與跨場域反例，保存適用範圍與失效訊號。沒有新資訊時改假設或停止支線。
一批大量實驗可由一次 Claude 工作承接，不把每個樣本變成雙模型喚醒。100／1,000 次不是成功保證，不替代完整觀察窗口，不解除兩輪修復及各專案限制。已達標成果先交付，後續反證另開批次。

## 交接與採用

GitHub 是版本與證據主紀錄，每輪以 task、revision、policy SHA、成果 SHA 與 session ID 綁定。事件只喚醒，不授權。先提交成果，再發布待 review 訊號。獨立 reviewer 讀原始需求、判準及證據後才讀 executor 解釋。
保留每次 next_action、停止原因與恢復條件；正確停止與業務成功分開。工程通過、外部採用與商業收益不得互代。

本次同步是文件採用及 push main。未啟用 Routine、OAuth Secret、runner 或新排程，不提高任何 runtime 等級。雲端接力需每 repo 真實驗收，不因複製方法即宣稱已接通。保持本地／人工入口作降級，既有暫停任務不因此恢復。

## 同步紀律

變更共用正文時更新版本並列出實際同步結果，核對各 repo commit；未同步明列。AGENT_METHOD_APPLICATION.md 保留各 repo 差異，不複製其他 repo 的帳本、PR 核准或 runtime 狀態。

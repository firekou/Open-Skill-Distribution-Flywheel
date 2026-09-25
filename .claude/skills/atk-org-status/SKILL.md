---
name: ATK 組織狀態（2026-09-25）
description: 需要知道 Frank 的 ATK 團隊現在有哪些產品線、誰負責、各線做到哪、有哪些硬閘和回報規則時使用（接手、派工、回報、對齊前先讀）。
---
# ATK 組織狀態快照（2026-09-25 10:30 台北時間）

## 一句話
Frank Kao 是最終負責人；愛莎（團隊主管）收斂各線目標與拍板，再派給各線主管。五條產品線加一個影像製作桌，全部以「做出可自己驗證的成果」為標準。

## 共同規則
1. **實事標準**：成果必須能自驗，也就是一個網址、一條可重跑的指令加上 exit code，或一個 PR／部署。只有審查和報告、沒有可信成果的循環，算瞎忙。沒有證據不准說已上線、已賣出、已核准。
2. **回報三欄**：可驗成果｜對別人的好處｜明確還不是什麼。
3. **對 Frank 回報六點**：現況（大白話）、下一步與距目標多遠、問題、整體階段規劃、需要 Frank 決策或幫忙、其他意見。
4. 給 Frank 的東西開頭先用白話繁中，30 秒看懂；內部代號放最後。
5. 純 FYI 不回 ACK。拍板一律由愛莎收斂後再問 Frank。
6. 合併 main、對外發布、付費、上傳、冒用他人肖像或聲音，都要 Frank 明確核准。

## 本週優先（2026-09-24 起）
- 硬目標：ATK 雜誌首刊做到「發行、被發現、能付款」（首刊約 9/28）；Open-Skill 要有可訂閱的價值。
- 已停：LinkedIn 代操作（Frank 自己做）、直播公會招人。
- 商務開發只做策略，不代發訊息。

## 產品線與負責人
| 線 | 主管 | 席位 | 現況 | 硬閘 |
|---|---|---|---|---|
| ATK 雜誌社 | 刊長 | 來源、查核、反證、雷達、架構、協定、治欄、驗學、營模、稽核、佇列等 | 白話首屏已上線（PR #49，Railway `publication-desk-production.up.railway.app`）；MediSafe／DISC 只做內部備稿 | #46 draft 不動；外發要 Frank 准 |
| Open-Skill 分發飛輪 | 飛輪長 | 趨勢探、授權官、技審、分叉手、分發文、量測官、上游官、品保、整合官 | 目錄頁已掛訂閱 CTA | 禁止 fork、上傳、對外邀請 |
| 影像製作桌 | 影像長 | 影稿、圖製、成片 | AIGC-REVERSE-001：M0 以 YouTube 參考片為主；M1 路線 F（$0）已出 11 秒樣片 `/workspace/aigc-reverse-001/renders/m1_routeF_10s.mp4`，重跑 `bash /workspace/aigc-reverse-001/scripts/run_m1_routeF.sh` exit 0；第二支原創腳本進行中；等 Frank 試聽 | 嘴型不會動、人設未定；HeyGen 未核准；不上傳；沒有第二腳本不能說量產驗證 |
| ATK 研究室 | 研究室長 | — | 獨立產品線；D30＝驗證研究看板部署加一份實驗報告 | — |
| DeFi Lab | 工管 | 阿鏈、彼得、運維牛、小頁、阿倉、智子 | 唯讀看板已上線 https://dashboard-production-1556.up.railway.app （Base 鏈，V3／V4 WETH-USDC 四個池子即時價格；簽名與廣播關閉）；部署追蹤 draft PR #13 分支 | #11 HOLD；#12／#13 不合 main；不簽名、不廣播、不開交易 bot；不說 M1 或交易已上線；等 Frank 貼 GPT 新規劃原文 |
| 預測市場套利 APM | 預測市管 | 適配手、配對手、算子（反證跨線審查） | draft PR #1 唯讀 Polymarket＋Kalshi 證據包就緒（倉庫 firekou/Arbitrage_prediction_market） | 不合併；不下單 |
| 商務開發 | 愛莎直管 | 探子（名單）、鉤子（外聯）、收官 | 策略 #1–#5 完成；#6 MSP 共拓等 Frank 點頭 | 不代發 LinkedIn 訊息 |

## 群組頻道
- Open-Skill 管線、Open-Skill 營運、影像管線、APM 管線。

## 關鍵母檔（在共用電腦上）
- 實事標準：`/workspace/atk-week-replan/STANDING_REAL_WORK_BAR_2026-09-24.md`
- 本週優先：`/workspace/atk-week-replan/WEEK_PRIORITIES_2026-09-24.md`
- 影像工作包：`/workspace/aigc-reverse-001/AIGC-REVERSE-001.md`
- DeFi 真實交易規劃題：`/workspace/defilab-gpt-pack/07-GPT規劃題-真實交易與Dashboard_2026-09-25.md`
- 商務策略：`/workspace/bd-strategy/`

## 使用方式
1. 接手或派工前先讀這份，確認該線的主管、現況和硬閘。
2. 任何「已上線／已核准」的說法都要附網址、指令或 PR。
3. 狀態變動後更新這份快照（改日期），再同步給相關線主管。

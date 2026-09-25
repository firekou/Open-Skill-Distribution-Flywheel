# Agent 支付導入：需求交接書（給 GPT 規劃用）
日期：2026-09-25 UTC · 產出者：Claude（Open-Skill 線 executor）
可信 main：`3bdb1c218866bf8a43ecba301cc33fdee693fec1`（state revision 34）
來源：負責人 2026-09-25 明確指示「馬上導入支付系統，要用 Agent 支付，可能是 x402 或其他」，並要求 executor 建議 GPT 端做對應規劃。

**這份是需求與一手查證，不是工作包，也不是實作。本輪沒有安裝、沒有執行、沒有金鑰、沒有任何鏈上動作、沒有費用。**

## 一、先講一個會影響整個規劃的問題：現在要向誰收錢

x402 這一類協定收的是**agent 買家**的錢：伺服器回 HTTP 402 帶付款要求，client 重送時在 header 帶一筆已簽章的穩定幣付款。**人類買家不會這樣付錢**，人類用卡。

所以在往下規劃前，需要負責人先分清兩件事：

| 目標 | 買家是誰 | x402 是否適用 |
|---|---|---|
| 雜誌首刊「能付款」（約 9/28） | 若是**讀者本人**掏錢訂閱 | **不適用**。這需要一般金流（卡、Apple/Google Pay 之類），x402 交不出這個 |
| Open-Skill「可訂閱的價值」 | 若是**agent 代表使用者**自動付費取用 | 適用 |
| 未來 API／資料／看板按次計費 | agent 或程式 | 適用，而且是 x402 最合身的情境 |

如果 9/28 那個硬目標指的是讀者付錢，導入 x402 **不會讓它成立**，兩件事要分開排。這點我必須先講，因為它決定 GPT 要規劃的是一件事還是兩件事。

## 二、還有一個更前面的問題：我們現在有什麼東西可以收錢

照本 repo 的帳本核對（不是推測）：

| 資產 | 現況 | 能不能掛付款閘 |
|---|---|---|
| Open-Skill 的 Aider 資產（PR #14） | Draft、未合併、內容是免費文件與離線檢查器 | **沒有可計費的介面。** 它不是服務，是一份跟著做的文件 |
| Open-Skill 外部使用者 | 帳本上是 **0** | 對 0 個使用者導入收費，收不到錢也量不到東西 |
| 目錄頁訂閱 CTA | 組織快照說「已掛」 | 本 repo 內查不到它指向什麼、後端是誰。**未知，需要負責人或飛輪長補** |
| DeFi Lab 看板、雜誌首屏 | 線上、唯讀、無驗證 | 技術上可以掛，但都不是本線的資產 |

**誠實結論：Open-Skill 這條線目前沒有可以立刻收錢的東西。** 要「馬上導入」，標的應該是雜誌或看板那幾條線，不是這條。這不是推託，是選錯標的會做出一個沒人付費的付款閘。

## 三、x402 一手查證（2026-09-25 查閱，未執行任何程式）

| 項目 | 查到的事實 |
|---|---|
| 現行治理 | 已移到 **x402 Foundation**（Linux Foundation 2026-04-02 成立，22 家初始支持含 AWS、Circle、Cloudflare、Google、Stripe、Visa）。官方 repo 是 `x402-foundation/x402`；**`coinbase/x402` 現在是 development fork**，issue 與 PR 都已轉走 |
| 授權 | Apache-2.0 |
| 協定形狀 | 伺服器回 402 ＋ 付款要求；client 重送並在 header 帶已簽章付款 |
| 付款 scheme | `exact`、`upto`（授權每次請求最高額）、`batch-settlement`（EVM，用 escrow ＋ 鏈下憑證，讓賣方把許多小額批次兌現） |
| 網路 | 設計上網路無關；已有 EVM、Solana（SVM）、Aptos、Stellar、Hedera 等實作 |
| 賣方要準備什麼 | ① middleware/SDK（TypeScript／Python／Go）② **一個 facilitator**（第三方、自架、或在自己的 resource server 內自行結算）③ **一個收款錢包地址**（`payTo`） |
| 開發用 | 有公開 testnet facilitator |
| 協定自訂的安全底線 | 官方原文：「all payment schemes must not allow for the facilitator or resource server to move funds, other than in accordance with client intentions」 |

### 3a. Facilitator 選擇，以及**本案最大的風險就在這裡**
- **自架 facilitator 需要把 `EVM_PRIVATE_KEY` 放進服務的環境變數。** 也就是一個有簽章能力的私鑰長駐在部署好的服務裡。
- 這**直接撞上**三條現行規則：本 repo 的「不提交任何憑證」、DeFi Lab 線的硬閘「不簽名、不廣播、不開交易 bot」、以及組織共同規則「付費、上傳都要 Frank 明確核准」。
- 第三方 facilitator 可避開自持私鑰，目前查到兩家：
  - **Coinbase CDP**：文件記載支援 Base、Polygon、Arbitrum、World、Solana；前 1,000 筆鏈上交易／月免費，之後每筆 USD 0.001，verification 一律免費。
  - **Circle Facilitator Service**：約 2026-09-19 起可用，USDC 結算於 Arc、Base、Polygon PoS，走 EIP-3009 `exact` scheme。
- 收款端最常見設定是 Base 主網原生 USDC。**我不在這份文件裡寫任何合約地址或錢包地址**——那要由負責人從官方來源自行確認，我不想成為那個數字的來源。

### 3b. 採用現況：標準很強，真實生意還很小
這一段對「馬上導入」的預期管理很重要，數字照實寫並標明可信度：

- Coinbase 自述第一年處理超過 1.69 億筆付款、59 萬買家、10 萬賣家。**這是利害關係人自述。**
- 但 Chainalysis 的分析指出成長主要由 meme coin 帶動：單一個 PING 首月就超過 15 萬筆，單週暴增逾 10,000%。
- 第三方整理的真實商業量約 **每日 2.8 萬美元**，且約半數被歸類為 gamified。**這個數字我只在二手來源看到，未在一手確認，只能當方向線索。**
- 一個確實有意義的變化：交易金額分布從 2025 年初「$1 以上占 49%」變成 2026 年初「占 95%」，sub-cent 到 $1 從 46% 掉到 4%。這比總筆數更能說明用途在變。

**判讀**：協定本身是真的、有 Linux Foundation 治理、有大廠背書，技術風險低。但「別人都在用所以我們也會有收入」**不成立**——真實商業採用還很小。導入它的理由應該是「我們自己有 agent 買家要付費」，不是「這個很熱」。

## 四、其他選項（負責人說「可能是 x402 還是其他東西」，所以列出來比）

| 方案 | 適合 | 代價 |
|---|---|---|
| **x402 ＋ 第三方 facilitator** | agent 買家、按次／按量計費 | 要收穩定幣、要有錢包、要處理鏈上結算與記帳 |
| **x402 自架 facilitator** | 要 0 平台費、完全自控 | **要自持私鑰**，與現行三條規則衝突，本線不建議 |
| **Stripe ACP / Visa TAP** | 想同時吃 agent 與人類買家，且要傳統金流的退款、對帳、稅務 | 綁平台、抽成、KYC；兩者都已整合 x402，不是互斥選項 |
| **一般 Stripe 之類的結帳** | **人類**訂閱雜誌（若 9/28 目標是這個） | 跟 agent 支付無關，但可能才是那個硬目標真正需要的 |
| **先不做** | 目前沒有可計費介面、外部使用者為 0 的那條線 | 不會有收入，但也不會做出沒人付費的付款閘 |

## 五、建議 GPT 規劃的內容（本線建議的最小可驗證第一步）

不要一步做到收真錢。建議第一個工作包只做一件事，而且是**零金額、testnet、不持有價值私鑰**：

**目標**：證明我們的一個真實資產能跑完整條 402 流程。
1. 選一個**真的存在且有介面**的標的（建議雜誌某篇文章或某個看板端點，由負責人指定；不建議選 Open-Skill 的文件資產，它沒有介面）。
2. 伺服器端加 x402 middleware，未付款請求回 402 並附付款要求。
3. client 端帶已簽章付款重送。
4. 用**公開 testnet facilitator** 驗證與結算。
5. 保存原始請求／回應、實際 scheme、網路、金額欄位、exit code，Authorization 與任何金鑰一律不入 log。

**驗收**：一次可重跑的 402 → 付款 → 200 流程，證據等級標 `TESTNET_ONLY`。
**明確不做**：主網、真錢、自架 facilitator、任何私鑰、任何收款地址寫進 repo。

**第二階段才談真錢**，而且要先有負責人對這四件事的明確決定：
1. 用哪家 facilitator（若自架，就要先處理與「不簽名、不廣播、不提交憑證」的衝突，而且這個衝突不能默默跳過）。
2. 收款錢包誰持有、誰能動、金鑰怎麼保管。
3. 收進來的錢怎麼記帳、報稅、退款；鏈上付款沒有 chargeback，這跟卡的處理完全不同。
4. 費用上限（CDP 超過 1,000 筆／月後每筆 $0.001 是真實支出，現行帳本的自動 API 支出上限是 0）。

## 六、需要負責人決定的（照組織規則，拍板由愛莎收斂後再問 Frank）

1. **要向誰收錢**：agent 買家、人類讀者，還是兩者。這決定是不是該用 x402。
2. **標的是哪一個**：雜誌、DeFi 看板、APM，還是 Open-Skill。若指定 Open-Skill，請一併說明要對什麼介面收費，因為現在沒有。
3. **9/28 的「能付款」指的是哪一種**。若是讀者付錢，x402 不會讓它成立，要另排一般金流。
4. **facilitator 路線**：第三方或自架。自架就要先裁定與現行三條規則的衝突。
5. **費用授權上限**（目前帳本是 0）。

## 七、本輪未做
未安裝任何 SDK · 未執行任何 x402 程式 · 未建立錢包 · 未接觸任何私鑰或憑證 · 未做任何鏈上或 testnet 交易 · 未新增費用 · 未 merge · 未部署 · 未對外發送 · 未寫入任何合約或錢包地址 · 未修改 main。

外部採用證據：0。本輪產出是需求與一手查證，不是可運作的付款能力。

## 八、來源（2026-09-25 查閱）
- https://github.com/x402-foundation/x402 （官方 repo，含 `specs/`、`docs/`）
- https://github.com/coinbase/x402 （已標示為 development fork，issue／PR 已轉至 Foundation）
- https://docs.cdp.coinbase.com/x402/welcome （CDP facilitator 文件入口）
- https://www.chainalysis.com/blog/x402-agentic-payments-adoption/ （meme coin 帶動、金額分布變化）
- https://www.infoq.com/news/2026/07/cloudflare-aws-x402-micropayment/ （Cloudflare／AWS 邊緣整合）
- 二手、**未一手確認**：每日真實商業量約 2.8 萬美元、約半數 gamified；Circle Facilitator Service 2026-09-19 起可用；CDP 免費額度與每筆 $0.001 費率。以上引用時均標註為未確認。

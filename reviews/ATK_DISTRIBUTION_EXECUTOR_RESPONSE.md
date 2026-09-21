# ATK 產品線 executor response — Headroom + ATK 案例

回應 main 的 `reviews/CLAUDE_NEXT_PROMPT_ATK_DISTRIBUTION.md`（2026-09-21「兩條線收斂與 ATK 接入需求」）
B 線工作包。治理線（A 線）依 R4／R5 停在 backlog，本文件**不含任何 controller 內容**。

| | |
|---|---|
| 分支 | `claude/atk-headroom-adoption`（PR #5，Draft，未合併） |
| 本輪起始 head | `e8a15d7d2c012007a69ca69c7e4630c33147c4a6` |
| 工作包來源 | main `671cdfa1004718c132aa460fed607b095ef5f752` |
| 相關 review | `reviews/PR5_R6_REVIEW_933446ab.md`（NEEDS_INFORMATION，待獨立隔離重放） |
| 環境 | headroom **0.37.0**（已安裝）· Python 3.11 · 無金鑰、無模型呼叫、無 loopback 以外網路 |

---

## 0. 先回報憑證盤點（只記 SET／NOT_SET，不讀值、不輸出）

工作包要求 executor 先回報，所以放在最前面。

| 變數 | 本 runtime |
|---|---|
| `ATK_API_KEY` | **NOT_SET** |
| `ATK_BASE_URL` | **NOT_SET** |
| `ATK_MODEL` | **NOT_SET** |
| `HEADROOM_API_KEY` | **NOT_SET** |
| `ANTHROPIC_API_KEY` | **NOT_SET** |

- **輪替確認是否存在：否。** `governance/decisions.json` 的 `KEY-ROTATION` 仍是
  `status: action_required`，決策原文「帳戶持有人撤銷輪替；完成狀態未知」。我沒有任何可以
  確認輪替已完成的來源，也沒有去找。
- **是否有使用授權：否。** 沒有任何已批准的付費呼叫額度。既有限制維持：不重用舊 key、
  不要求在聊天貼新 key、不阻塞離線工作。
- **結論：本輪 0 次模型呼叫、0 元新增支出。** 這不是缺口造成的妥協——工作包的 1～4 項
  本來就全部可以離線完成，而且已經完成。
- 真正需要帳戶持有人處理的，只有一件：**若要做新的 live run**，需要由執行環境安全注入的有效
  key、經核實的端點與可用 model、以及一個明確的費用上限。在那之前不需要任何人做任何事。

---

## 1. 本輪最重要的發現：preflight 工具會給出錯誤的否定診斷

這是我本輪唯一改動程式的理由，也是唯一影響「第一次使用」的缺陷。

**怎麼發現的。** 我在容器裡第一次執行 `local_check.py`（隨附樣本，md5
`0ad9194a489136baa931881b78374cf7`，headroom 0.37.0）得到：

```
via proxy  : 111357 chars reached the upstream  (identical size)
NO BENEFIT: the proxy returned the payload unchanged, byte for byte.
```

**同一個命令、同一個輸入、同一個版本，接下來 22 次全部是 15.1%。**

**為什麼這件事嚴重。** 這個工具存在的唯一目的，就是回答「我該不該採用」。舊版的 NO BENEFIT
訊息會給出一個**有自信的因果解釋**：「你的 payload 沒有可跨行抽取的冗餘」。在上面那次執行裡，
這個解釋是**錯的**——那個 payload 明明壓得下去。一個第一次來的使用者會讀到它、相信它，然後離開。

**我沒有找出根因，也不宣稱找到。** `wait_for()` 只確認 `/v1/models` 有回應（連 HTTP error
都算就緒），所以「就緒」與「壓縮管線可用」之間可能有窗口；但我做了三組嘗試都無法重現：

| 嘗試 | 結果 |
|---|---|
| 連續 10 次執行 | 10/10 都是 15.1% |
| 單一 proxy 程序內連發 12 次請求（量每一次上游實收位元組） | 12/12 相同，無差異 |
| 全新空 `HOME` 冷啟 | 15.1% |

所以我記為 **observed-once, not-reproduced**，並且**只修可以修的那一半**。

**修法（`local_check.py`）**：當結果是 byte-for-byte 完全不變時，**在下結論前對同一個 proxy
再量一次**。兩次一致才報 `NO BENEFIT`（exit 3）；兩次不一致則報新的 **exit 4 `INCONCLUSIVE`**，
明講「這個 payload 並未被證明不可壓縮，請重跑」，**不給因果解釋**。只有否定路徑會多量一次，
正常路徑成本不變。

**驗收證據**（`integrations/headroom-atk/evidence/pr5-r7/controls.txt`）：

| 控制 | 結果 |
|---|---|
| 正控制：一般路徑 | exit 0，15.1%，只量一次 |
| 真陰性控制：JSON lines（確實無跨行冗餘） | **仍是 exit 3**，訊息新增「第二次量測同意」 |
| 負控制：兩次量測不一致 | **exit 4 INCONCLUSIVE**，且不出現「no such redundancy」字樣 |
| 變異控制：拿掉 re-check | 三個新測試**兩個轉紅**（`AssertionError: 1 != 2`） |

`Ran 34 tests ... OK`（上輪 31）。README 的測試數宣告由那條防漂移的測試抓到並同步——
**它又一次抓到我**，這正是它存在的理由。

---

## 2. 「本機壓縮」與「live 會把內容送出」已分清楚（工作包第 2 項）

工作包明確要求：不可暗示 live 路徑資料完全不外送。核對後發現**三處**需要更正。

**(a) README 的摘要表**寫著 `compression runs locally, no content leaves your machine`，
而且就在 live 測量那一列旁邊。技術上它描述的是壓縮步驟，但讀起來是整條路徑都不外送。已改寫，
並新增一節 **What leaves your machine**：

| | 本機執行 | **送出的東西** |
|---|---|---|
| `local_check.py` 離線檢查 | proxy 與 stub 上游，全在 `127.0.0.1` | **沒有。** 無金鑰、無模型呼叫、無 loopback 以外網路 |
| live 路徑 | 只有壓縮步驟 | **壓縮後的 prompt，送到 ATK。** 這正是整合的目的：送出的字元變少，不是變成零 |

準確的講法是：**壓縮發生在請求送出之前，不是取代送出。**

**(b) `DISTRIBUTION.md`** 的「Your log is never printed and never leaves your machine」已限定為
離線檢查，並指向上表。

**(c) 兩份對外稿件還停在已撤回的說法。** README 早就更正過 SSRF fallback「不是 silent」
（警告其實寫進 `~/.headroom/logs/proxy.log`），但 `DISTRIBUTION.md` 的 Draft 2 與
`offering/SERVICE_SAMPLE_FREE.md` **仍寫著 fails silently**。這兩份都是要給外部看的，
其中 Draft 2 的受眾正是 headroom 自己的使用者。已同步更正。
（`upstream/HEADROOM_FEEDBACK_DRAFT.md` 已是更正版本，未動。）

---

## 3. 最小試用步驟（工作包第 3 項）

新增 `integrations/headroom-atk/TRY_IT.md`，並從 README 首屏與檔案表連過去。

- **一個任務**：1,200 行合成部署 log，問失敗 migration 名稱與 SQLSTATE。
- **先離線**：`make_log.py` → `local_check.py`，附今天實測的預期輸出與**五個 exit code 各自該怎麼辦**
  （含新的 exit 4）。接著要求對**自己的 log** 再跑一次——那才是真正決定採用的一步。
- **再 live，而且只在權限與費用上限都明確時**：頁面寫明「不要從這裡開始」，並列出四個缺一不可的
  前置條件（環境注入的 key、核實過的端點、核實過的 model、事先議定的費用上限），
  建議形狀是單一合成任務、direct/proxy 各一次、零自動重試。
- **紀錄模板**依工作包逐項列出：輸入 checksum、輸入大小、版本、端點（只記 host）、
  **provider 實際回傳的 model**、prompt、路徑、prompt/completion tokens、usage 欄位有無、
  兩個答案是否命中、wall time、**錯誤類別（不是錯誤內文）**。
  明列**不得記錄**：金鑰或其任何片段、真實客戶 log、原始錯誤內文。

---

## 4. 歷史 live 數據的定位（工作包第 4 項）

未改動，核對後確認既有措辭已經正確：README 明寫 2026-09-18 的 live 表格是
「a recorded historical case, not a result this round re-measured」，且
「The exact input file was not preserved … so it cannot be re-run identically even by us」。

`TRY_IT.md` 再加一句：**不得用重建資料填紀錄模板**——新的一次是新紀錄、有自己的數字，
不是「重現」那一次。本輪**沒有**任何新的 live 數據，因此不宣稱重測。

---

## 5. 採用驗收（工作包第 5 項）：**沒有進展，也沒有辦法自己推進**

**第三方使用仍為 0 筆。** 本輪沒有任何非作者使用者按 Quick Start 完成任務的紀錄。
這一項依定義不是 executor 能自己產生的——我跑一百次也不是採用證據。

未把準備稿或內部測試當成採用。`DISTRIBUTION.md` 的發布清單維持八項裡只有三項完成
（本目錄、`registry/materials.json` 的 `_adoption`、根 README 索引），其餘全部 **待發布**。

---

## 6. 已驗證 ／ 僅離線 ／ 仍未知

| 項目 | 狀態 |
|---|---|
| 隨附樣本在 headroom 0.37.0 上壓縮 15.1%，兩個 needle 存活 | **今天實測**，22+ 次一致 |
| JSON lines payload 完全不壓縮（真陰性） | **今天實測** |
| 一次無法重現的 byte-for-byte pass-through | **今天實測到一次**，三種方式都重現不了 |
| re-check 會把不一致擋成 INCONCLUSIVE | **今天實測**，含變異控制 |
| 34 個離線單元測試 | **今天實測** |
| 2026-09-18 的 live token 數字 | **歷史紀錄**，輸入未保存，不可重現 |
| live 路徑今天是否仍可用（端點、model、額度） | **仍未知**，無 key、無授權，未嘗試 |
| 非作者使用者能否照 TRY_IT 完成任務 | **仍未知**，零筆 |
| pass-through 的根因 | **仍未知**，不宣稱 |

---

## 7. 剩餘配置缺口（真正需要帳戶持有人的部分）

只有一項，而且不阻塞上面任何一件已完成的工作：

- **一次新的 live run** 需要：執行環境安全注入的有效 `ATK_API_KEY`、經核實仍可用的端點與 model、
  以及事先議定的費用上限。`KEY-ROTATION` 目前 `action_required`、完成狀態未知。
  我不找回舊 key、不要求在聊天貼新 key。

其他待授權項目維持原狀、未執行：About／topics 套用（倉庫設定）、上游 issue 送出、
社群貼文、目錄提交、merge 與發布。

---

## 8. 本輪沒有做的

0 次模型呼叫 · 0 元新增支出 · 未安裝 launcher · 未啟用觸發器 · 未改 main 政策 ·
未 merge · 未部署 · 未送上游 · 未發布任何對外內容 · 未關閉 `P5-R4-01`
（它等的是獨立隔離重放，依定義不是 executor 能關的）· 未觸碰 controller。

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

---

# R7 限定修復包 — `ATK-PR5-R7-LIVE-GUARD` revision 1

| | |
|---|---|
| work_id / revision | `ATK-PR5-R7-LIVE-GUARD` / `1`（本留言開啟第 1 輪，上限 2 輪） |
| source_head | `f4d676b22a853f64b37f2c160cdb3d1f6bc47efc` |
| review | `reviews/PR5_R7_REVIEW_f4d676b.md`（BLOCKED） |
| deadline | 2026-09-22T14:30:00Z |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:5:ATK-PR5-R7-LIVE-GUARD:1:f4d676b22a853f64b37f2c160cdb3d1f6bc47efc:executor` |
| 本輪金鑰／模型／付費呼叫 | **0 / 0 / 0**。`ATK_API_KEY`、`ATK_BASE_URL`、`ATK_MODEL` 仍全部 NOT_SET |
| 證據 | `integrations/headroom-atk/evidence/pr5-r7/r7_controls.txt` |

三項 finding 我逐項核過，**沒有一項爭議**。

## P1-01 — 金鑰示範在命令列（正確）

`ab_test.py` 的 docstring **在同一段裡自相矛盾**：第 6 行示範把金鑰前綴在命令上，第 13 行寫
「絕不要放在命令列」。`TRY_IT.md` 與 `README.md` 各有一份同樣的範例。使用者會複製的是範例，
不是禁令。

**修法**：三個檔案的可執行範例全部改成「金鑰已由環境／secret manager 注入」，只示範
不回顯的 `[ -n "$ATK_API_KEY" ] && echo SET || echo NOT_SET` 加 `python3 ab_test.py`。
docstring 同步，並且**連引用都不再寫出那個字面形式**——改成文字描述，這樣 reviewer
對整個交付目錄下 grep 就能直接得到答案，不會被我自己的說明文字干擾。

**驗收**（`r7_controls.txt`）：

```
$ grep -rn 'ATK_API_KEY=sk-|ATK_API_KEY=\.\.\.|ATK_API_KEY=[^ ]* python' . --include=*.md --include=*.py
(no matches)  exit=1  PASS

$ python3 ab_test.py
ATK_API_KEY is not set; refusing to run. No mock is substituted.
exit=2
```

**範圍說明**：封包列的四個檔案不含 `README.md`，但同一份 finding 的驗收條件寫的是
「搜索**交付目錄**不得再出現」。README 裡有一份同樣的範例，我把它一併修了——留著一個
已知會外洩的示範，不符合這條 finding 的目的。這是本輪唯一超出檔案清單的改動，在此明列。

## P1-02 — 文件承諾兩次呼叫、實際送出四次（正確，而且這項最嚴重）

我在 `TRY_IT.md` 寫「一個合成任務、direct／proxy 各一次、零自動重試」，然後叫人跑
`ab_test.py`——那支程式迴圈跑 `TASKS` 的**兩個**任務，各 direct + proxy，**共四次付費呼叫**。
使用者依我寫的授權兩次費用，實際會被扣四次。**工具悄悄超過的費用上限，比沒有上限更糟。**

**修法**：不是改文字把四次包裝成兩次。`ab_test.py` 新增 `--task {needle,summary,both}`，
**預設 `needle`（2 次）**，四次的那個要主動要求；並在**第一次呼叫送出之前**印出精確次數：

```
about to make exactly 2 live calls (1 direct + 1 via proxy) for task(s): needle.
No automatic retries: a failed call stops the run.
```

零自動重試維持不變（單次 `urlopen`，失敗即停）。

**驗收**：新增 5 條以 mock 計數的測試，全部不需金鑰、不觸網。

| 測試 | 驗的事 |
|---|---|
| `test_the_default_run_is_exactly_two_calls_one_each_way` | 恰好 `["direct", "proxy"]` |
| `test_the_count_is_printed_before_the_first_call_is_made` | 在第一次呼叫的當下擷取 stdout 快照，確認次數**已經**印出——印在後面等於事後通知你付了多少 |
| `test_the_four_call_run_has_to_be_asked_for` | 負控制：四次的路徑還在，只是要主動要求，而且自己報 `exactly 4` |
| `test_no_key_refuses_and_spends_nothing` | 無金鑰 exit 2，計數器為 0 |
| `test_the_docstring_no_longer_demonstrates_what_it_forbids` | 三個檔案都不含那個字面形式 |

**變異控制**：把預設改回 `both`，`test_the_default_run_is_exactly_two_calls_one_each_way`
立刻紅：

```
+ ['direct', 'proxy'] : the documented first live run did not spend exactly two calls
FAILED (failures=2)
```

## P2-01 — 兩次一致仍不足以證明「沒有冗餘」（正確）

這一項我上一輪已經改過一次，**但只改了一半**：我把「一次觀察」升格成「兩次觀察」，
因果句原封不動留著。兩次一致只是同一個觀察出現兩次，不排除 proxy 沒就緒、壓縮器被跳過
或其他未明原因。這是**同一個錯誤做了兩遍**。

**修法**：exit 3 保留，訊息只陳述量到什麼——「no size benefit was observed, twice」——
並明講**這不建立因果**：

> two matching observations do not establish that your payload lacks the redundancy headroom
> factors out, and do not rule out the proxy not compressing on this run.

然後給可行動的下一步（換 payload 形狀、重跑、查 `~/.headroom/logs/proxy.log`），
不下結論。exit 4 的不一致分支不變。

**驗收**：真陰性（JSON lines）仍 exit 3；新測試
`test_a_repeated_observation_is_not_reported_as_a_cause` 斷言輸出**不含** `no such redundancy`
且**含有** `do not establish`。變異控制：把因果句放回去，該測試紅。

## 本輪數字

`Ran 40 tests ... OK`（本包開始時 34）。0 次模型呼叫、0 元支出、未觸網（loopback 除外）。

## 明確排除，已遵守

未觸碰也未宣稱關閉 `P5-R4-01`，未重做其作者端證據 · 未發布 · 未 merge · 未改 Secrets／權限 ·
未送上游 · 未更動 controller · 未新增 MCP／benchmark／框架範圍。

---

# R8 最終限定修復 — `ATK-PR5-R7-LIVE-GUARD` revision 2

| | |
|---|---|
| work_id / revision | `ATK-PR5-R7-LIVE-GUARD` / `2`（**第 2 輪 / 上限 2 輪**，不開第三輪） |
| source_head | `cde4e5c855096b1d7566d44680259851810aec99` |
| review | `reviews/PR5_R8_CONFIRM_cde4e5c.md` |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:5:ATK-PR5-R7-LIVE-GUARD:2:cde4e5c855096b1d7566d44680259851810aec99:executor` |
| 本輪金鑰／模型／付費 | **0 / 0 / 0**，三個 ATK 變數全程 NOT_SET |
| 證據 | `integrations/headroom-atk/evidence/pr5-r7/r8_controls.txt` |

## 這項 finding 我沒想到，而且它比前一項更深一層

R7 我修好了「文件說兩次、程式跑四次」。**但我證明的是兩次 client 請求，不是兩次 provider attempt。**
proxy 會在底下自己重試，而我完全沒看那一層。

先把事實查清楚再改，兩項都在證據檔裡：

```
$ headroom proxy --help | grep -A3 -- --retry-max-attempts
  --retry-max-attempts INTEGER RANGE
        Maximum upstream retry attempts for connect/read/5xx failures
        (1–10, default: 3). Env: HEADROOM_RETRY_MAX_ATTEMPTS.

$ grep -n 'for attempt in range(self.config.retry_max_attempts)' …/headroom/proxy/server.py
2294:        for attempt in range(self.config.retry_max_attempts):
```

`range(N)` 是**總共嘗試 N 次**，不是重試 N 次——所以 `--retry-max-attempts 1` 等於「只送一次」。
這一點我從原始碼確認，沒有用旗標說明的字面猜。

**後果**：兩次 client 請求，在 0.37.0 的預設下最多可以變成上游 **4 次**（direct 這條由
`urllib` 直送、不重試；proxy 那條最多 3 次）。我上一輪寫的「No automatic retries: a failed call
stops the run」對 `ab_test.py` 為真，**對錢實際走的那條路為假**。

## 修法

**1. 每一個文件化的 live proxy 啟動都釘住上限。** 四處全部改為
`headroom proxy --port 8787 --no-http2 --retry-max-attempts 1`：`README.md`（兩處）、
`TRY_IT.md`、`ab_test.py` docstring。

**2. 把無條件宣稱換成可成立的契約。** `ab_test.py` 在第一次請求前印的字改成：

```
about to issue exactly 2 client requests (1 direct + 1 via the proxy) for task(s): needle.
  provider attempts: this script sends each request once and never retries. The proxied leg
  is retried by headroom itself, up to --retry-max-attempts times (0.37.0 default: 3).
  Started as documented with --retry-max-attempts 1, the ceiling for this run is 2 provider
  attempts; with the default it is 4. This script cannot see how your proxy was started, so
  it does not verify which applies.
```

最後一句是重點：**這個程式看不到你的 proxy 是怎麼起的，所以它不宣稱驗證過。**
上限是有條件成立的，條件寫在旁邊。三份文件都寫明**用別的方式啟動 proxy，這個上限就不成立**。

**3. 防漂移測試**（`TheLiveStartupFlagAndTheCeilingClaimDoNotDrift`，4 條，離線）：

| 測試 | 驗的事 |
|---|---|
| `test_every_documented_live_proxy_start_pins_the_attempt_ceiling` | 三份文件裡**每一行** `headroom proxy --port` 都帶旗標 |
| `test_no_document_still_claims_retries_cannot_happen` | 舊的無條件宣稱不再出現 |
| `test_every_document_says_a_differently_started_proxy_breaks_the_ceiling` | 講了上限就必須講什麼會讓它失效 |
| `test_the_default_of_three_is_named_so_the_risk_is_legible` | 只寫旗標不寫預設是 3，讀者會以為那是可有可無的整潔 |

**變異控制**：任一處拿掉旗標 → 紅；把無條件宣稱放回去 → 紅。

`Ran 44 tests ... OK`（本輪開始時 40）。

## 一項超出範圍、只報告不改

`integrations/headroom-atk/offering/SERVICE_SAMPLE_FREE.md:26` 也文件化了一次 live proxy 啟動，
**同樣沒有旗標**：

```
26:headroom proxy --port 8787 --no-http2
```

它不在本封包的 scope 清單裡。上一輪我為了 finding 的目的自行擴到 README，這一輪 reviewer 已經
把 README 明確列進 scope——表示檔案清單是刻意挑的。**第 2 輪（最後一輪）不是擅自擴大範圍的時候**，
所以我只報告位置，由 reviewer 決定要不要另開。

## 明確排除，已遵守

未觸碰也未宣稱關閉 `P5-R4-01`、未重做其作者端證據 · 未發布 · 未 merge · 未改 Secrets／權限 ·
未送上游 · 未更動 controller · 未新增 MCP／benchmark／框架範圍 · `local_check.py` 未改
（離線對 stub，重試不花錢，封包也說可不動）。

**這是本封包的第 2 輪，不開第三輪。**

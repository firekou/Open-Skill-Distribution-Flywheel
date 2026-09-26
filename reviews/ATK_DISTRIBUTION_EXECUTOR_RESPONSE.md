# ATK 分發與接入：第一個交付

**狀態：待獨立 review（IMPLEMENTED_PENDING_REVIEW）**
**分支：** `claude/atk-distribution-provider-seam` ｜ **PR：** #4（Draft，未合併）
**下一份 reviewer 回覆：** `reviews/PR4_R4_REVIEW_<short-sha>.md`（僅核對文件差異）
**交付：** `integrations/atk-provider/`

---

## LIVE 驗證完成（2026-09-18，負責人直接提供憑證）

**四輪以來一直掛著的 live 缺口，這次由我自己關閉，不再引用他人結果。**

憑證只經環境變數使用，**沒有寫入任何檔案、沒有進 repository**。已請負責人**輪換**該把 key，因為它出現在對話紀錄中。

| 檢查 | 結果 |
|---|---|
| DNS | `api.aitokenking.com.tw` → `47.239.51.250` |
| `GET /api/v1/models` | **HTTP 200，52 個模型** |
| 經 `atk_provider.py` 的最小 chat | `OK`，12 in / 4 out，`cost_usd` **`None`** |
| **文件化 Quick Start 全程** | `--file sample-build.log` → 正確五點摘要，指出 `src/main.c:42` 與 `util.c:88`，**892 in / 115 out** |

**完整複現審查者先前的結果（同一 probe，12 in / 4 out），並且再往前一步：整條文件化路徑可用，不只是單一 token 探測。**

**沒有改變的事：** `cost_usd` 未回報（≠ 免費）；**不作任何節省或品質主張**；MCP 仍未 handshake；其他 provider 未 live 呼叫；延遲、吞吐、帳務未量測。

---

## 第四輪：PR4_R3_REVIEW（`328a33b`）的 DOC-SYNC

**審查結論：APPROVED_WITH_CONDITIONS。P4-R2-01 與 P4-R2-02 由審查者判定 CLOSED（VERIFIED）；
P4-R2-03 為 PARTIALLY_VERIFIED，剩下 DOC-SYNC 一項條件。**

**本輪程式與測試完全未改動**，依審查指示不重跑 33 tests、不新增對抗案例。以下四項為文件同步：

| # | 項目 | 處理 |
|---|---|---|
| 1 | README 的 Verification 段仍寫 "using their own credential" | 改為**負責人提供並授權最小測試的憑證**（非審查者自有帳號），並明列該 live 呼叫**對應 `f2a2188`**，不推廣到後續 head |
| 2 | `DRAFT_01` 的 MCP JSON 仍是未指定 client 的 `${AITOKENKING_API_KEY}` | 移除可貼上的 JSON，改為 endpoint／header 兩個值的**概念說明**，並加上警語：**`${VAR}` 展開是各客戶端自己的功能、不是 MCP 規格的一部分**，有些客戶端會把字面值當 key 送出；指向 README 的完整說明，並保留「未 handshake」標示 |
| 3 | 兩篇草稿的操作步驟與 README 不一致 | 兩篇都加上 `set -a && . ./.env && set +a` **在 `curl` 之前**；明講**別名只在 Python 端生效**，`curl` 讀的是 shell 的 `$ATK_API_KEY`；`DRAFT_01` 改用隨附的 `sample-build.log`、測試數字 25 → **33**；兩篇都把「不需憑證的節錄預覽」與「需要 provider 設定的完整 payload」分清楚 |
| 4 | executor response 的第二輪紀錄仍是舊歸屬與舊數字 | 在該節**開頭加上歷史標示**，列出被更正的三點（憑證歸屬、測試數字、P4-01/03 後來重開）。**原始發現與審查結論不回頭改寫。** |

**我不自行宣稱 DOC-SYNC 已關閉。** 依審查指示回填新 SHA，由 reviewer 核對文件差異。

---

## 第三輪：PR4_R2_REVIEW（`b3bd4e5`）的修正

**狀態：全部 `IMPLEMENTED_PENDING_REVIEW`。** 依 `reviews/README.md`，只有獨立 reviewer 能標 CLOSED——
我上一輪在 `VERIFICATION.md` 自己寫「all three closed」，那不是我能寫的，已更正。

**唯一已 CLOSED 的是 P4-02，由 R2 reviewer 判定，不是我。**

### P4-R2-01（P1，阻擋項）— 截斷是我自己做的，不是代理

`_post` 先 `decode(...)[:400]` **才** `redact(...)`。41 字元的 key 跨過切點時，`redact` 根本匹配不到被切斷的值，**前半段就留在訊息裡**。

**製造這個洩漏的是我的程式，不是外部代理**——我上一輪還把它寫成「代理若重新編碼可能繞過」的外部限制，那個描述避重就輕了。

更難堪的是**我的測試也放行**：`test_the_opt_in_body_is_still_redacted` 只斷言「完整 key 不在訊息裡」，前 19 字元外洩它照樣綠燈。

| | reviewer 重放（`b3bd4e5`） | 修正後 |
|---|---|---|
| `client_truncation_leaks_prefix` | **True** | **False** |

**修法：先遮蔽整份 decoded body，再截斷已經安全的內容。**

**新測試斷言 key 的任何 8 字元片段都不得出現**，涵蓋切點前、跨切點、切點後、重複出現四種位置；另加一個**正控制**——一般錯誤（`model 'typo-4' does not exist`）仍要看得懂，遮蔽不能把所有失敗變成「出了點問題」。

### P4-R2-02（P2）— preview 是第二套實作

`--show-payload` 自己組了一份 OpenAI 形狀的 body。`AnthropicProvider` 實際會把 `system` 提到頂層並加 `max_tokens`，所以那條路徑的「完整請求」是錯的。

| | reviewer 重放（`b3bd4e5`） | 修正後 |
|---|---|---|
| `anthropic_preview_matches_wire` | **False** | **True** |
| preview keys | `['messages','model']` | `['max_tokens','messages','model','system']` |

**修法：`build_payload()` 放在 adapter 上，`complete()` 與 preview 共用同一個來源。** 測試直接斷言 preview 等於本機伺服器**實收**的 body，兩種 wire format 都驗。沒有設定 provider 時**明確拒絕顯示**，不猜一份出來。

### P4-R2-03（P2）— 文件與狀態，六項全部處理

1. **關閉權責** — `VERIFICATION.md` 改為逐項標示，全部 `IMPLEMENTED_PENDING_REVIEW`，只有 P4-02 標「CLOSED by the R2 reviewer」。
2. **PR body 過期** — 已重寫（14 tests、舊網址、「所有候選都需要 adapter」全部更正）。README 開頭那段必要性論述也改掉了，不再與結尾自相矛盾。
3. **README 順序** — `.env` 在 `curl` **之前**載入；並明講**別名只在 Python 端生效**，`curl` 讀的是 shell 的 `$ATK_API_KEY`。新增 **committed `sample-build.log`**，Quick Start 不再依賴讀者自己生一個檔案。
4. **憑證歸屬** — 更正為「**負責人提供並授權最小測試的憑證**」，非 reviewer 自有帳號。`VERIFICATION.md` 與兩篇草稿都改了。
5. **測試數字自相矛盾** — 已實測更正，見下。
6. **MCP JSON** — 改標為**概念示例**，並明講 `${VAR}` 展開是**各客戶端自己的功能、不是 MCP 的一部分**，有些客戶端會把那串字面值當成 key 送出去。維持「未 handshake」標示。

### 測試數字，實測更正

我上一輪寫「11 個測試：10 failures / 1 error，另有 1 pass」——**11 個卻加出 12 個，reviewer 指出這對不起來。這是對的。**

拿 `f2a2188` 的真實原始碼實跑：

```
Ran 11 tests — FAILED (failures=12, errors=1)
```

**正確說法：11 個 test method，10 個失敗、1 個通過**（刻意的正控制）。`unittest` 印出 `failures=12` 是因為其中一個 method 用 `subTest` 跑四個子案例，**每個子案例各報一次**。上一輪的「2 pass」單純是我寫錯。

### 本輪測試

```
$ python3 -m unittest test_atk_provider
Ran 33 tests — OK          （上一輪 25）

$ python3 ../../reviews/evidence/pr4-r2/reviewer_checks.py
client_truncation_leaks_prefix= False        ← was True
anthropic_preview_matches_wire= True         ← was False
preview_keys == wire_keys
```

新增 8 個測試對 `b3bd4e5`：**4 個失敗、4 個通過**。誠實說明那 4 個通過的原因——它們測的位置（key 在切點前／切點後很遠／重複出現）舊程式剛好處理得到，**真正的行為回歸只有跨切點那一個**，也就是 reviewer 找到的那個案例；另一個是刻意的正控制。我不把介面不相容或碰巧通過的案例當成同等強度的證據。

### 仍未做

- **新 head 沒有 live ATK 重跑。** 我這邊沒有憑證。前一輪的 live 證據屬於 `f2a2188`，**不能升格成 `b3bd4e5` 或本輪 head 的驗證**。
- **MCP 仍未 handshake。**
- **仍未整合任何 registry 候選工具**，這是獨立範例。

---

## 第二輪：PR #4 review（`f2a2188`）的三項修正

> **⚠ 歷史紀錄，已被第三輪更正。請勿當作現況。**
>
> 本節寫於 `b3bd4e5`，其中兩處後來被更正：
> - **憑證歸屬**：本節說審查者用「自己的憑證」。**實際是負責人提供並授權最小測試的憑證**，不是
>   審查者自有帳號。
> - **測試數字**：本節的「10 failures / 1 error，另有 1 pass」加不起來。**正確是 11 個 test
>   method 中 10 個失敗、1 個通過**；`failures=12` 是因為一個 method 用 `subTest` 跑四個子案例各報一次。
> - **P4-01 與 P4-03 在本節被寫成已修復**，第三輪發現修得不完整，分別以 **P4-R2-01 / P4-R2-02** 重開。
>
> 審查結論與原始發現不回頭改寫；現況一律以上方第三輪、以及第四輪的 DOC-SYNC 紀錄為準。

**P4-01～03 全部重現、全部修復。審查結論 APPROVED_WITH_CONDITIONS 的條件已處理，維持 Draft。**

### 先更正我上一輪的一個結論

我上一輪寫「`api.aitokenking.com` 解不出 DNS，所以 ATK 端點未驗證」，並把那當成需要負責人回答的問題。

**那個主機名稱本來就是錯的**——少了 `.tw` 和 `/api`。**審查者找到官方入口並實測成功。** 官方文件：<https://aitokenking.com.tw/assets/docs/zh-Hant/index.html#mcp-server>

| 用途 | 官方入口 | 證據 |
|---|---|---|
| OpenAI 相容 base URL | `https://api.aitokenking.com.tw/api/v1` | **TESTED（審查者）** |
| 模型清單 | `GET /api/v1/models` | **TESTED（審查者）**：HTTP 200，52 個模型 |
| Chat | `POST /api/v1/chat/completions` | **TESTED（審查者）**：用**本 PR 的 `atk_provider.py`**，只改環境設定；`claude-sonnet-4.6`、`max_tokens=16`，回 `OK`，12 in / 4 out，**未回報美元成本（≠ 免費）** |
| MCP | `https://api.aitokenking.com.tw/mcp`，`X-Aitokenking-Api-Key` | **僅 OBSERVED（官方文件）**，未做 handshake |

**這一次 live 呼叫是審查者用他自己的憑證做的，不是我。** 我的環境仍然沒有 ATK 憑證，我沒有跑過真實 ATK，也不會說我跑過。

### P4-01 — 錯誤輸出會洩漏憑證（REPRODUCED → 已修）

`_post` 把服務端錯誤本文前 400 字放進例外，註解還寫「key 在 header 不在 body，所以不會洩漏」。**那個推論是錯的**，而且被證明是錯的：伺服器可以回顯它拒絕的那把 key。

重現：401 回 `{"error": "invalid credential <CANARY>"}` → `CANARY in str(exc)` 為 `True`。

**修法：預設不含 body**，只留 status 與 provider。`ATK_INCLUDE_ERROR_BODY=1` 才納入，**且該路徑仍會遮蔽**。彙總的 fallback 錯誤、以及連不上時的 URL（有些閘道把憑證放 query string）也都遮蔽。

**測試全部是執行時 canary**——真的設秘密值、真的讓伺服器回顯、斷言人看到的字串裡沒有它。審查者那句「不要用『原始碼搜不到 sk-』代替執行時測試」我照做了。

**誠實的限制：遮蔽只能移除它知道的值。** 代理若重新編碼或截斷 key 仍可能繞過——所以預設是「不含」而不是「靠遮蔽」。

### P4-02 — 沒有摘要也算成功（REPRODUCED → 已修）

`content: null`（例如 tool call）原本回 `Completion(text=None)`，範例印 `None`、exit 0。**對摘要資產而言是把失敗報成成功。**

**修法：要求非空字串。** `null`、純空白、型別不符一律失敗，訊息帶 `finish_reason` 說明為何是空的；Anthropic 空 `content` 同規則。**正控制：真的有文字時照常成功。**

### P4-03 — Quick Start 與實作不符（OBSERVED → 已修）

1. `.env.example` 的 URL 錯誤、README 只說「填 key/model」，照抄跑不起來 → **已改成官方 URL**，並加上列模型的指令。
2. README 宣稱 dry-run 印出 exact request，實際只印每則前 300 字 → **兩邊都修**：預設明確標示為 **PREVIEW**，新增 `--show-payload` 印出**完整 JSON body**；**header 永不輸出**。
3. 變數命名：官方用 `AITOKENKING_API_KEY`，契約用 `ATK_API_KEY`。**選 `ATK_API_KEY` 為本處標準名，官方拼法接受為別名**，映射寫在 `.env.example` 與 README，並有測試。

### 另外補的（審查者第 3 點）

README 新增 **ATK MCP 區段**：若客戶端支援 MCP，**完全不需要這個 adapter**，直接貼官方端點設定即可。並明講 MCP 與 OpenAI 相容 API 是兩種協定，**MCP URL 不是 `ATK_BASE_URL`**。

### 測試

```
$ python3 -m unittest test_atk_provider
Ran 25 tests — OK        （上一輪 14）
```

新增的 11 個 PR #4 測試對 `f2a2188`：**10 failures / 1 error**；唯一通過的是刻意的正控制
（`test_real_text_still_succeeds`）——會把正常情況也擋掉的修法是另一種缺陷。

### 我接受的一個判斷

審查者說：**「每個接入都必須先寫共同 adapter」沒有證據**，而且官方已提供原生 MCP 與 OpenAI 相容設定。

**接受。** 我上一輪把這個接縫說成所有接入的前置條件，那是過度推論。它是**寫 Python 且想換得掉供應商時**的工具；能用原生設定解決的就該用原生設定。README 和兩篇稿子都已改成這個定位，並明列**本資產尚未整合 registry 任何候選工具**。

---

## 第一輪紀錄（保留，時間標示如下）

以下為 2026-09-18 第一輪提交時的內容。**其中「ATK endpoint 未驗證／DNS 解不出」已被上方更正**，
但原文保留，不改寫歷史。

---

## 方向對齊五行（`.claude/skills/atk-goal-alignment/SKILL.md`）

- **目標來源：** 負責人 2026-09-18 明確校正 + `reviews/ATK_STRATEGY_REALIGNMENT_2026-09-18.md` + `reviews/CLAUDE_NEXT_PROMPT_ATK_DISTRIBUTION.md`。
- **本輪交付：** 寫 skill 的開發者拿到一個**零依賴的 Provider 接縫 + 可跑的範例**，能一行切換供應商。
- **主線連結：** `ATK_ROUTING_INTEGRATION.md` §4 定義了 Provider Interface，**整個 repository 沒有任何實作**。缺了它，之後每個接入資產都得各自重寫一次，四條接入性質（透明／可換／有文件／可移除）也沒有共同的驗收點。**刪掉這項，下一個接入資產就得從零開始。**
- **必要驗證與停止點：** 安裝、API 功能、錯誤處理、provider 切換、key 不外洩、文件可跟做。**不驗省錢百分比，因為本輪不做任何省錢主張。** 交付並送 Draft PR 即停止。
- **範圍差異：** 未新增產品方向、未新增框架、未新增依賴（只用標準函式庫）。未恢復 benchmark，未安裝 Omnigent／AGT／OMA。

---

## 一、工作狀態更新

| 項目 | 狀態 | 說明 |
|---|---|---|
| Token Efficiency Lab 全面修復／Freeze | **PAUSED_BY_STRATEGY** | 依校正暫停。**R4-01～R4-06 等歷史 finding 維持 OPEN，未標 CLOSED**；benchmark PR #1 維持 Draft，未合併 |
| Omnigent／AGT／OMA 導入試點 | **PAUSED** | `reviews/AGENT_GOVERNANCE_POC_RESPONSE.md` 記錄的安裝結果保留；六個驗收情境**仍未執行**，不因暫停而視為通過 |
| ATK 分發與接入 | **主線，本輪交付** | 本文件 |

**暫停不等於修好。** 上述兩項的未解狀態原文保留在既有報告中，本輪未改寫。

---

## 二、三個候選（來自現有 `registry/materials.json`，未重做全網搜尋）

### 候選 A — `headroom`（Apache-2.0，token-optimization，registry 分數 91）

- **誰的什麼問題：** agent 開發者；工具輸出、log、RAG chunk 在進模型前太大，吃掉 context 也吃掉錢。
- **現成專案：** `headroomlabs-ai/headroom`。自述 21–57% 壓縮（90% 僅限高重複 payload），附 SQuAD v2／BFCL 品質 benchmark 與可離線重現指令。
- **模型呼叫點／ATK 可接位置：** 它**位於模型呼叫之前**，壓完才送出去。ATK 的接入點是它下游的那個 provider 呼叫。
- **最小交付與驗證：** companion adapter（壓縮 → 經 ATK 送出）；需驗安裝、壓縮前後可審、provider 切換。
- **維護負擔／通往採用：** 外部依賴、643 open issues，需追版本。採用路徑：教學 + Quick Start。

### 候選 B — `rtk`（Apache-2.0，token-optimization）

- **誰的什麼問題：** CLI agent 使用者；agent 讀到的 bash 輸出過長。
- **現成專案：** `rtk-ai/rtk`。自述砍掉最多 90% bash 輸出，且**明講這不是 90% 帳單下降**，token 以 bytes/4 估算、未附 tokenizer。
- **模型呼叫點／ATK 可接位置：** **它本身不呼叫模型**，是包在 shell 外的代理。**沒有直接的 ATK 接入點。**
- **最小交付與驗證：** 純技術分享較合適。
- **維護負擔／通往採用：** 低；但無接入路徑，本輪不選。

### 候選 C — `open-code-review`（Apache-2.0，Alibaba，agent-skill）

- **誰的什麼問題：** 團隊 code review；行級註解 + 多語言規則。
- **現成專案：** `alibaba/open-code-review`。
- **模型呼叫點／ATK 可接位置：** LLM 呼叫點明確。
- **最小交付與驗證：** 需在其程式內替換 provider 設定。
- **維護負擔／通往採用：** **修改量最大**——要動別人的專案結構、很可能要 fork。校正文件明講「只有必要時才 fork」，本輪不選。

### 選擇與理由

三個都指向同一個缺口：**它們要接 ATK，都需要一個 Provider 接縫，而那個接縫的規格寫好了卻沒有實作。**

所以本輪先做**接縫本身 + 一個可跑範例**，範例處理的正是候選 A 的使用者問題（長工具輸出），但**不依賴 headroom、不引用它的任何數字**。這是「修改最少、接點最清楚」的選法：不動任何外部專案、不 fork、不新增依賴，而且它是候選 A 之後真正要接上去的那一塊。

**候選 A 是下一個資產，本輪沒有做，也沒有宣稱做了。**

---

## 三、交付內容

| 檔案 | 內容 |
|---|---|
| `integrations/atk-provider/atk_provider.py` | Provider Interface 實作。**只用標準函式庫。** ATK／OpenAI 相容（openai、deepseek、qwen、openrouter、gemini、custom）＋ Anthropic。環境變數驅動、有序 fallback、有限重試 |
| `example_summarise_tool_output.py` | 可跑範例：長工具輸出 → 摘要。有 `--dry-run`，**不需憑證就能看它要送什麼** |
| `test_atk_provider.py` | 14 個測試，跑在**真的本機 HTTP 伺服器**上 |
| `.env.example` | §3 環境契約，**ATK base URL 標註未驗證** |
| `README.md` | Quick Start ＋ **怎麼換掉 ATK**（顯眼位置） |
| `VERIFICATION.md` | 驗了什麼、沒驗什麼 |
| `content/DRAFT_01…`、`DRAFT_02…` | 兩篇繁中技術分享草稿，**未發布** |

---

## 四、驗證紀錄

```
$ cd integrations/atk-provider && python3 -m unittest test_atk_provider
Ran 14 tests — OK
```

測試打在真的 localhost HTTP 伺服器上：真的 socket、真的請求、真的解析。**合成的是「供應商」，不是傳輸層**，所以 URL 組合、header、JSON body、狀態碼處理、重試與 fallback 都是真的被執行到。

| 契約性質（`ATK_ROUTING_INTEGRATION.md` §1） | 證據 |
|---|---|
| **透明** | 每個 `Completion` 帶 `provider`；範例每次都印 |
| **可替換** | 同一段程式靠環境變數送到兩台不同伺服器、用兩把不同 key，兩邊各自斷言收到什麼 |
| **有文件** | README「Switching away from ATK」 |
| **可選** | 所有 `ATK_*` 拿掉、`PROVIDER=openai`，照常運作 |

其他已驗：無硬編碼 key／URL／model（掃描原始碼）；設定不完整**在送出前**失敗（斷言伺服器收到零個請求）；不認得的 PROVIDER 拒絕而非退回預設；4xx 不重試；5xx 重試後 fallback；未設定的 fallback 跳過；最終錯誤列出每一家；回應格式不對時訊息明確；Anthropic 走自己的 wire format；**未回報的成本維持 `None` 而非 `0.0`**。

**端到端（範例本身，subprocess）：**

```
PROVIDER=atk     exit=0   served by atk / local-test · 412 in, 37 out · cost not reported
PROVIDER=openai  exit=0   served by openai / local-test · 412 in, 37 out · cost not reported
```

---

## 五、live 驗證缺口（最重要的一段）

**沒有任何一個請求送到過 ATK。** 兩個各自獨立的原因：

1. **環境裡沒有 ATK 憑證**，也沒有去申請。
2. **`api.aitokenking.com` 在這個環境解不出 DNS。**

```
socket.gethostbyname('api.aitokenking.com') → [Errno -5] No address associated with hostname
curl https://api.aitokenking.com/v1/models  → curl: (56) CONNECT tunnel failed, response 502
socket.gethostbyname('api.openai.com')      → 172.66.0.243          ← 同一個 shell、同一時間
```

`api.openai.com` 解得出來，**所以這不是整體網路封鎖**。可能是本機出口政策，也可能是**契約文件裡的 hostname 不正確或尚未上線**。本紀錄**不替它下結論**。

因此 `ATK_BASE_URL`、真實的 `ATK_MODEL` id、以及 ATK 的回應格式**全部未驗證**。adapter 假設 ATK 是 OpenAI 相容，因為契約文件這樣寫。**若不是，ATK 那條路會壞，其他供應商照常運作。**

**沒有用 mock 冒充成功。** 本機伺服器測的是我們的 client，不是 ATK。

其他未做：未呼叫任何真實供應商；未量測延遲或吞吐；未實作 streaming／tool call／batch；**契約裡的 `TOKEN_BUDGET_PER_RUN`／`COST_BUDGET_USD_PER_RUN` 未實作**，明列為缺口而非默默忽略。

**本輪沒有任何省錢或品質主張，因此不需要對應證據。**

---

## 六、下一個 reviewer 要驗什麼

1. **先驗方向**：這個接縫是否服務主線？三個候選的取捨是否合理？
2. `python3 -m unittest test_atk_provider` 在乾淨 checkout 是否 14/14。
3. **負向**：把 `ATK_*` 全部拿掉、`PROVIDER=openai`，範例是否照常跑。
4. **key 安全**：原始碼是否真的沒有硬編碼端點或 key。
5. 文件是否跟得下去（照 README 從零走一次）。
6. **請不要**把本輪當成 ATK 連線已驗證，也不要當成任何節省的證據。

**未解事項（第一輪原文）：** ATK endpoint 是否正確／已上線。**已由第二輪解決——見本文件開頭。**

---

## 下一 reviewer 要驗什麼（第二輪更新）

1. `python3 -m unittest test_atk_provider` 在乾淨 checkout → 25/25。
2. **P4-01 負控制**：設一個 canary 當 key、讓伺服器回顯它，確認例外文字裡沒有它；`ATK_INCLUDE_ERROR_BODY=1` 也一樣。
3. **P4-02**：`content: null` 必須失敗；有文字時必須成功。
4. **P4-03**：照 README 從零走一次，確認 `.env.example` 的 URL 可用；`--show-payload` 印出完整 body 且**沒有 header**。
5. **不要**把本輪當成我跑過 ATK——live 證據是審查者的，已標註來源。
6. **不要**當成任何節省的證據，也不要當成已整合 headroom。

**仍未做：** 我這邊沒有 ATK 憑證，所以無法自行重現 live 呼叫；MCP 未 handshake；尚未接上任何 registry 候選工具（那是下一個資產）。

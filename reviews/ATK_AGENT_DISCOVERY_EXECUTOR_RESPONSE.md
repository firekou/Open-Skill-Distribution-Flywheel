# Executor Response — 一個真實工具的完整發現與採用路徑

**Branch** `claude/atk-headroom-adoption` · **Base** `d6912cf` (main) · **Draft PR, not merged**
**Work package** [`reviews/ATK_AGENT_DISCOVERY_AND_ADOPTION.md`](ATK_AGENT_DISCOVERY_AND_ADOPTION.md)

本輪由 executor 撰寫。**不自我核准**；判定由 reviewer 依 `executive-review-gate` 作出。

---

## 五行目標對齊（atk-goal-alignment）

| | |
|---|---|
| **目標來源** | `reviews/ATK_AGENT_DISCOVERY_AND_ADOPTION.md`（含商業假設補充），以及負責人 2026-09-18 的方向校正 |
| **本輪交付** | 一個外部工程師拿到一個網址，就能在沒有任何金鑰的情況下裝起 headroom、驗證它真的壓縮了送出的內容、而且關鍵那一行沒有掉；同一份資產另附免費品牌版與付費版樣本 |
| **主線連結** | 這是「找到有用工具 → 整理驗證 → 透明可選接入 ATK → 分發 → 實際採用」五段裡的第一到第三段，並首次實測第四、五段（可尋址試驗、外部發現試驗） |
| **必要驗證與停止點** | 驗三件事：真實連線的節省數字、離線可重現的檢查、外部 agent 能否找到與採用。三項各自有證據或有誠實的失敗記錄即交付，等 reviewer |
| **範圍差異** | 未新增產品方向、未建平台、未新增框架。registry 為擴充既有檔案，非另建索引。未發布、未收款、未接觸第三方 |

---

## 交付內容與精確 SHA

| Commit | 內容 |
|---|---|
| `f391fdb` | `integrations/headroom-atk/`：README（入口）、`make_log.py`、`local_check.py`、`ab_test.py`、`evidence/`；registry `_adoption` 記錄與 build 斷言 |
| `4ea57d7` | `offering/SERVICE_SAMPLE_FREE.md`、`SERVICE_SAMPLE_PAID.md`、`UNIT_ECONOMICS.md`、`DISTRIBUTION.md` |
| `3d883c7` | 修正 README 一項錯誤陳述、加上 JSON-lines 適用性限制與機制說明、`local_check.py` 加上 `--log`／`--needle` 預檢、registry 署名與 `does_not_apply_to` 欄位、LiteLLM 官方路徑、本回覆檔 |

---

## 1. 選型：為什麼是 headroom，實際查證了什麼

從既有 `registry/materials.json` 挑 `headroom`（`token-optimization`，material_score 91）。**查證上游本身，不沿用 registry 的描述**：

- 版本 `0.37.0`，實際安裝並執行過，不是讀出來的。
- 授權 Apache-2.0。**本 repository 未複製任何 headroom 程式碼**，只有設定、測試工具與量測結果。
- **原生設定就夠，不需要 fork，也不需要 adapter 或共用 SDK。** 這直接推翻了先前「大部分工具都要 fork 或包 adapter」的假設。接入 ATK 只有兩個設定值：一個 proxy 指令，一個 HTTP header。

---

## 2. 量測：兩組數字，刻意分開

### 2a. 真實連線（ATK，負責人授權之憑證，僅以環境變數傳入）

| 任務 | 直連 ATK | 經 headroom | 差 |
|---|--:|--:|--:|
| 摘要 | 40,572 | 29,781 | 26.6% |
| 針對性提問 | 40,589 | 25,525 | **37.1%** |

針對性提問兩條路徑都答出 `0042_add_tenant_id` 與 SQLSTATE `42701`。Token 數取自 **ATK 自己的 `usage` 欄位**，不是估算，也不是 headroom 自報。

### 2b. 離線可重現（無金鑰、無費用、任何人可跑）

```
direct     : 111357 chars reached the upstream
via proxy  :  94578 chars reached the upstream  (15.1% fewer)
needle '0042_add_tenant_id': present after compression
needle '42701': present after compression
PASS
```

`local_check.py` 自己起 proxy 與一個 stub upstream，量的是 **upstream 實際收到的 body**。

**15.1% 與 37.1% 不衝突也不是更正**：前者是字元數、後者是 ATK 計的 prompt token，而且跑在不同的 bytes 上（見下方「未保存」）。離線那個是保守值，也是唯一不花錢就能查的值。

**兩個數字都取自 proxy 外部。** 這是刻意的：外部搜尋（見第 4 節）帶回一份公開記錄，某壓縮 proxy 的自報儀表板顯示大幅節省，實際送往 upstream 的量卻更多。該案例本輪未重現、不當作事實引用，但足以說明量測點不該放在被量測的元件裡。

---

## 3. 誠實的失敗與缺口（不修飾）

1. **摘要任務兩條路徑都漏掉 FATAL 那一行。** 壓縮路徑漏，直連路徑也漏。這是提問方式的問題，不是壓縮的問題——但它是結果，寫進 README 正文而不是附註。
2. **真實那一輪的 `deploy.log` 沒有保存。** 它產在暫存目錄。`make_log.py` 是那支產生器的**確定性重建**：同樣 1,200 行、同樣 index 947 的針、同樣的欄位形狀，但**不是同樣的 bytes**（111,262 bytes；當時約 101 KB）。所以今天重跑 `ab_test.py` 會得到接近但不相同的 token 數。這一條寫在 README 的「What these numbers are not」，不是藏在 commit message 裡。離線檢查之所以存在，正是因為它**可以**完全重現。
3. **本輪未再對 ATK 發出任何付費請求。** 負責人貼在對話中的憑證已暴露、**必須輪替**，而既有指示是不複用已暴露憑證、不自行擴大付費工作負載。因此 2a 的數字是前一輪的實測結果，本輪沒有重跑。這是刻意的取捨，記在這裡而不是讓數字看起來像今天剛測的。
4. **自己發現的第三個坑。** 寫 `local_check.py` 時被擋住：headroom 0.37.0 會拒絕解析到 loopback／RFC1918 的 client 指定 upstream（其 SSRF 防護），而且是**靜默回退**到自己解析的 provider——症狀跟第一個坑一模一樣，會讓人怪錯對象。已寫入 README，並附 `HEADROOM_ALLOWED_BASE_URLS` 解法。
5. **registry 的手改會被蓋掉。** `tools/build_materials.py` 是整檔重生成 `materials.json`。若直接手改該檔，下一次 build 就無聲清除。因此 `_adoption` 記錄加在來源 `tools/materials_data.py`，並加上斷言：ADOPTION 的 id 對不到任何 material 就**中止 build**。正反控制都跑過（孤兒 id → `exit 1`；還原 → 只有 `headroom` 一筆變動，其餘 187 筆與 counts 完全不變）。

---

## 4. 外部發現試驗（未給 repository 名稱、品牌或網址）

隔離 agent，僅有 WebSearch／WebFetch，三個真實問題表述，16 條查詢、3 次 primary fetch。

| 問題 | 找到可用答案？ | 它會採用什麼 | 本 repo 出現？ |
|---|---|---|---|
| P1 壓縮 deploy log 的本機 proxy，要有證據 | 是 | LogDx-CI 論文當證據基準；RTK／grep+tail；headroom 作為產品選項 | **否** |
| P2 在非 OpenAI 的 OpenAI 相容 gateway 前面加壓縮，逐請求設定 | 部分（機制有，數字沒有） | LiteLLM 的 `headroom-compression` guardrail，再用 tokbench 自測 | **否** |
| P3 可機讀、附成本與實跑日期證據的已驗證工具索引 | **否** | 沒有現成的。Skilldex 最接近但缺版本、授權、I/O、成本、實跑證據 | **否** |

**結果：0/3。三個問題都沒有讓本 repository 出現。** 這是本輪最重要的負面結果。

三個案例只是初步診斷，**不能用來估算普遍發現率**。但診斷本身很具體：

- 專案的公開描述命名的是**比喻**（flywheel、magazine），不是**問題**。16 條查詢裡出現的詞是 proxy、compress、tokens、logs、error lines、OpenAI-compatible、gateway、per-request、registry、verified、install command、licence、cost、evidence、dated——沒有一條包含 flywheel 或 magazine。
- **P3 可能是一個空著的位置。**〔第二輪收斂：原文寫「真正空著」「沒有人佔住」，那超出一次搜尋能證明的範圍，在此撤回。〕該 agent 在它做的那次搜尋裡檢視了十餘個 registry，**沒有找到**同時具備成本欄位與實跑日期證據的公開索引。這是一次搜尋的觀察，不是市場結論——它沒找到不等於不存在。本 repository 的 `_adoption` 記錄剛好是那個形狀，值得當成假設去驗，不能當成已知的機會。
- 這一點**未經本輪驗證為可行策略**，只是一份外部診斷；改名或改描述是負責人的決定，不在本輪自行更動。

同一次搜尋另外帶回一項對交付有直接影響的事實，已回到 primary source 查證（2026-09-18，<https://docs.litellm.ai/docs/proxy/headroom>）：**LiteLLM 有官方的 `headroom-compression` guardrail**，支援逐請求啟用與 `x-headroom-bypass` 退出。本輪**沒有測它**，該頁也**沒有任何數字**。已寫進 README，明說沒測、把選擇權留給讀者——而不是假裝我們找到的是唯一路徑。

---

## 5. 可尋址／可採用試驗（給網址，不給任何操作提示）

隔離 agent，只拿到一個 raw README 網址與一句問題敘述，沒有本機 repo、沒有逐步指示、沒有金鑰。

**結果：SOLVED。** 它自己把資產裝起來、跑完、而且**用自己寫的檢查程式獨立驗證**，不是照抄我的斷言：
15.1% 縮減、完整 FATAL 句子逐字存在於壓縮後的 body、1200 行一行沒少。它還刻意重現了第三個坑
（移除 allowlist → HTTP 401、stub 沒被打到）。它的指令表有 12 個步驟，**0 個死路**。

（時間要修正它自己的說法：它自報「約 15 分鐘」，但執行框架量到的實際時間是 **263 秒（約 4.4 分鐘）**、
18 次工具呼叫。採用框架的數字，不採用 agent 的自報值——這正是為什麼量測點不該放在被量測的東西裡面。）

它沒測到的兩件事，已如實記下：`headroom-ai` 在該環境已預先安裝，所以**安裝步驟未被它驗證**；
沒有金鑰，所以真實 A/B 未跑（`ab_test.py` 正確拒絕執行且沒有塞 mock）。

### 它找到四個我寫錯或寫得太軟的地方——四項我都自己重測並確認屬實

| 它的指控 | 我的重測 | 處置 |
|---|---|---|
| README 說 headroom 會 log `ignoring unsafe x-headroom-base-url override`，實際沒有 | **屬實。** 觸發回退的整段 proxy 輸出中該字串出現 **0 次** | 已改。README 現在明說：原始碼裡有這個字串，但預設 verbosity 下**不會印出**，grep 會找不到 |
| 沒解釋機制，因而藏住真正的限制 | **屬實。** 對照送出與收到的 body：它把重複的時間戳前綴抽成一行 header，逐行改寫，**一行都沒丟**。省的是文字重複，不是判斷重要性 | 已寫進 README 並附實際輸出片段 |
| 適用範圍寫得太軟。**JSON-lines log 縮減 0.0%** | **屬實。** 同一批 1,200 筆記錄：JSON lines **0.0%**（逐 byte 相同）；攤平成純文字 **27.3%** | README 新增一整節「Will this help YOUR logs?」，並把「你的 log 壓縮率會不同」這種軟話改成明確的「對很大一類 log 完全沒用」 |
| 未揭露的選用元件 | **屬實。** proxy banner：`Code-Aware: NOT INSTALLED (pip install headroom-ai[code])` | 已寫明本頁所有數字都是在**沒有**這個 extra 的情況下量的 |

### 它要求的那一項改進，已經做掉

它說：把「我相信別人那份 log 的數字」變成「我能對我自己的 log 做決定」。

`local_check.py` 現在接受 `--log` 與可重複的 `--needle`：

```bash
python3 local_check.py --log /path/to/your.log --needle "the line that must survive"
```

exit 0 = 有縮減且針全在；**exit 3 = 完全沒縮減**（沒壞也沒賺，別裝）；exit 1 = 針掉了，該 payload 不要用。
五條路徑都跑過正反控制：樣本 log → exit 0；JSON-lines → exit 3；`--log` 沒給 `--needle` → exit 2；
針本來就不在原文 → exit 2；檔案不存在 → exit 2。JSON-lines 那條已作為**負控制**寫進
`evidence/local_check.txt`，與正向結果並列。

registry 的 `_adoption` 也補上 `does_not_apply_to` 欄位，讓「什麼時候不要用」跟著機器可讀索引走。

### 這項試驗證明了什麼、不能證明什麼

**能**：入口頁在沒有作者提示下可被陌生人跟著走完，而且成功條件不是 exit 0，是實際量到縮減且針存活。
**不能**：這是**受控條件下的隔離 agent**，不是外部使用者自發採用。外部實際使用紀錄仍為 **0**。
它與我同在一個 session 中執行，這一點必須算進可信度折扣裡——它不是第三方。

---

## 6. 商業驗證

### 6a. 一個具體外部需求與現有替代方案

需求敘述（P1／P2 兩條查詢即是它的自然語言形式）：*agent 讀大型 log，每個 token 都付費，真正有用的只有一兩行。*

外部搜尋顯示這個類別**已經很擁擠**：headroom、RTK、tare、lm-resizer、kompact、toongate、Kong 的 `ai-prompt-compressor`，以及 LiteLLM 內建的 guardrail。**現階段選 ATK 的理由不是「ATK 有更好的壓縮」——ATK 並不做壓縮。** 唯一成立的理由是：這份驗證把數字量在 provider 側、把失敗寫出來、而且附上不用金鑰就能重跑的檢查。那是**驗證服務**的價值，不是 router 的價值，兩者不應混為一談。

### 6b. 免費品牌版與付費增值版樣本

- [`offering/SERVICE_SAMPLE_FREE.md`](../integrations/headroom-atk/offering/SERVICE_SAMPLE_FREE.md)：贊助區塊標示為付費置入，與答案、證據、推薦理由**分開**；明寫轉述的 agent 可以拿掉贊助區塊；**沒有任何要求下游無條件推薦 ATK 的隱藏指令**。
- [`offering/SERVICE_SAMPLE_PAID.md`](../integrations/headroom-atk/offering/SERVICE_SAMPLE_PAID.md)：以「差異表」說明多付錢買到什麼（你的 workload、你的 provider、你的費率、你的檢索案例）。**價格刻意留白**——不虛構價格，也沒有任何收款路徑。並列出「值得推出」的三個前提，目前三個都不成立。

### 6c. 單位經濟

[`offering/UNIT_ECONOMICS.md`](../integrations/headroom-atk/offering/UNIT_ECONOMICS.md)。**已交付單位 0、實收 0，所以每件貢獻是「未定義」，不是 0。** 服務收入與 ATK routing 毛利分兩行記，同一筆請求不重複計算；曝光不入帳。最大的成本項是交付人力，**未量測**；模型 token 的幣別成本也**未量測**（ATK 每次回傳 `cost_usd: null`）。返工成本已知不低——這份交付本身經過多輪修正。

### 6d. 標示是否能保留

`_adoption` 記錄新增兩個欄位，讓署名跟著**機器可讀索引**走，而不是只留在文章裡：`upstream_attribution`（headroom 的 Apache-2.0 要求，必須保留）與 `verified_by`（ATK 的署名，是請求，不是使用條件）。

**選定 client 的實測結果：部分保留。** 可尋址試驗中的 agent 是一個真實的 LLM client，它只讀到 README。
它的回報完整保留了上游署名——工具名、`Apache-2.0`、「compression runs on your machine」、
以及「本 repository 未複製 headroom 程式碼」這一點——並且在建議採用時把 headroom 指名為要裝的東西。
**但它沒有轉述 ATK 的署名**：它的報告裡只在引用 `cost_usd: null` 時提到 ATK，沒有說明這份驗證是誰做的、
跑在哪個 router 上。

這是一個**誠實的失敗**，而且方向很清楚：授權要求的上游署名活了下來（因為它寫在工具本身的身分裡），
贊助方的署名沒有（因為它只是頁面上的一段文字）。這也正是本輪把 `verified_by` 加進機器可讀記錄的原因，
但**該欄位是在這次試驗之後才加的，尚未被任何 client 測過**。下一次試驗才能說它有沒有用。

### 6e. 治理工具：現有能力足夠

先查既有收藏：`registry/materials.json` 裡已有 12 個相關候選（nanobot、skillhub、archestra、open-multi-agent、agent-governance-toolkit 等），**全部授權未解析**。

**結論：現階段現有能力足夠，不導入治理工具。** 依據是本輪真實出現的瓶頸，而不是規模想像：

| 本輪真實瓶頸 | 治理平台能解嗎 |
|---|---|
| 產物沒保存（`deploy.log` 遺失） | 否。已用確定性產生器 + 記下 md5 解決 |
| 手改會被生成器無聲蓋掉 | 否。已用 build 期斷言解決 |
| 反覆返工／宣稱超前證據 | 否。這是既有的 review gate 在處理 |
| 外部發現率 0/3 | 否。這是命名與描述問題 |

四個瓶頸沒有一個是任務佇列、預算上限或權限隔離。**外部需求為 0 的情況下增加 agent 數量只會增加成本。** 50～100 工作單元的治理能力在出現可重播的真實工作負載之前不需要選型；這不是永久禁止，是順序問題。

---

## 7. 邊界：本輪沒有做的事

- 沒有 merge，沒有 Freeze，沒有恢復 benchmark 或 Omnigent／AGT／OMA 試點。**歷史缺陷維持 OPEN，暫停不等於已修復。**
- 沒有發布、沒有投稿目錄、沒有對 headroom 上游發任何 issue 或訊息。`DISTRIBUTION.md` 每一項都標 **待發布**。
- 沒有收款路徑、沒有帳戶、沒有價格。
- 沒有把憑證寫進任何檔案。全 repo 搜尋確認不存在任何金鑰片段；README 裡 OpenAI 錯誤訊息的金鑰前後綴已遮罩。
- 隔離 agent 的試驗是**受控條件**下的結果，**不等於外部使用者自發採用**。目前外部實際使用紀錄為 **0**。

---

## 8. 剩餘缺口與下一個最小實驗

**缺口**（依重要性）

1. **外部發現 0/3**，且診斷指向命名與描述，而非技術。
2. **外部實際使用 0 筆。** 沒有第三方跑過、引用過或回報過。
3. **真實 token 數字無法在今天重現**（憑證須輪替 + 原始 log 未保存）。
4. **付費側全部未驗證**：無需求、無價格、無收款、無單位成本。
5. LiteLLM 官方路徑未測；headroom 的 `[code]` 選用元件未裝、未測。
6. **安裝步驟未被獨立驗證**：可尋址試驗的環境已預裝 headroom，所以 `pip install "headroom-ai[proxy]"` 沒有被第三方走過一次。

**下一個最小實驗（單一項，不加平台）**

把 P3 那個空位佔住，並且只驗一件事：**把 repository 的公開描述與根 README 第一畫面，從比喻改成 P3 的問題句**（例如「附授權、安裝指令、輸入輸出、成本與實跑日期證據的已驗證 agent 工具索引，JSON + 可機讀」），其他一律不動。兩週後用**同一組 P3 查詢字串、同一個隔離 agent 設定**重跑一次，比對是否出現。

- 成立條件：本 repo 出現在 P3 查詢結果中。
- 不成立就是不成立，記錄後改下一個假設，不追加投放。
- 這需要**負責人決定**（改動對外描述），本輪不自行更動。

〔第二輪更正：上面寫「用**同一組** P3 查詢字串重測」——**做不到，在此撤回**。第一輪 16 條查詢的逐字
transcript 未保存，只剩隔離 agent 事後的自述，因此那一組無法被原樣重跑，宣稱重跑同一組會是假話。
改以 `integrations/headroom-atk/evidence/SEARCH_BASELINE.md` 建立**新基線**（九條固定查詢，尚未執行），
並在該檔事先寫死解讀規則：結果改變**不等於**命名是原因，另列四個本基線分不開的競爭解釋。
T0 定義為入口與描述真正公開於 main 之日，目前尚未發生，沒有啟動任何計時，也沒有排程。〕

**需要負責人決定的事項（僅此三項）**

1. 對外描述是否改成問題句（上述實驗的前提）。
2. 是否授權對 headroom 上游分享那三個坑（接觸第三方）。
3. 憑證輪替（已暴露）；以及是否要為重跑真實量測另行授權一次付費呼叫。

---

# 第二輪修復回覆（回應 reviews/PR5_R1_REVIEW_03dc57b.md）

**Reviewed head 03dc57b → 本輪新 head `dd504a3`（再加本檔的 commit）** · PR #5 Draft、未合併
全部修復標 **IMPLEMENTED_PENDING_REVIEW**。我是 executor，不自我判定 CLOSED／APPROVED。

## 五行目標對齊

| | |
|---|---|
| **目標來源** | 負責人 2026-09-18 的 1A／2A／3A 決定 + `reviews/PR5_R1_REVIEW_03dc57b.md` + `reviews/CLAUDE_NEXT_PROMPT_ATK_DISTRIBUTION.md` |
| **本輪交付** | 兩個程式缺陷關閉（憑證外洩、採用判定失準）；一個陌生人可以從**乾淨 clone + 乾淨 venv**照文件跑完；根目錄有問題導向入口；上游回饋備稿 |
| **主線連結** | 「找得到→選得對→用得起來→解得了題」四段裡，這輪補的是**用得起來**（安裝與指令真的可跟做）與**選得對**（判定不再把膨脹說成成功） |
| **必要驗證與停止點** | P5-01／02 各要正負控制；P5-03 要乾淨環境實跑；P5-04 要數字對得上證據。做完送審即停 |
| **範圍差異** | 未擴充第二、三個工具；未建平台；未發布；未送上游；未收款；未合併 |

## 環境

Python 3.11.15 · headroom-ai 0.37.0（PyPI 最新版，upload 2026-08-27）· Linux
證據：`integrations/headroom-atk/evidence/pr5-r2/controls.txt`、`clean_install.txt`

---

## P5-01 憑證可能被錯誤訊息回顯 — IMPLEMENTED_PENDING_REVIEW

**根因。** handler 讀 error body、切 400 字元、直接丟進 exception。兩個問題疊在一起：provider 有權
把它拒絕的憑證回顯在 body 裡；而且「先切再遮罩」根本遮不掉——被切斷的值已經不等於原值了。
這正是 PR #4 的 P4-01／P4-R2-01，我在新腳本裡重犯了一次。

**修復路徑。** 不另建框架，直接沿用 PR #4 已驗過的行為：預設**完全不輸出 body**
（`ATK_INCLUDE_ERROR_BODY=1` 才輸出）；要輸出時**先遮罩整段、再截斷**；連線錯誤連 URL 一起遮罩
（gateway 可能把 key 放在 query string）。

**正負控制**（合成秘密 `sk-SYNTHETIC…ZZ`，41 字元，全程未使用真實金鑰）：

| head | 情境 | 完整 key 可見 | 任一 8 字元片段可見 |
|---|---|---|---|
| 舊 03dc57b | key 出現在 body | **是** | **是** |
| 舊 03dc57b | key 跨越 400 字元切點 | 否 | **是** ← 只檢查完整 key 會漏掉這條 |
| 新 dd504a3 | key 出現在 body | 否 | 否 |
| 新 dd504a3 | key 跨越 400 字元切點 | 否 | 否 |

正控制：正常 200 回應仍可解析（`test_positive_control_a_normal_response_still_works`）。
另加一條：長度小於 4 的「秘密」不參與遮罩，否則普通文字會被打成一片黑。

**限制。** 遮罩只能遮我們**知道**的值。若 provider 回顯的是經過轉換的憑證（雜湊、片段重組），這個
防線不會生效——所以預設是不輸出 body，遮罩是第二道而不是第一道。

## P5-02 PASS 不要求真的變短 — IMPLEMENTED_PENDING_REVIEW

**根因。** 我只把「完全相同」判為 NO BENEFIT，於是**等長改寫**與**膨脹**都走到 PASS，膨脹那條還一路
印著「-166.7% fewer」。這是「檢查點放錯位置」的老毛病：判定寫在出口，條件卻只涵蓋一種入口。

**修復路徑。** PASS 現在同時要求「嚴格變短」**且**「每根針都在」。三種無效果分開描述——完全未改動／
被改寫但等長／變大——不再一律叫 byte-for-byte（把被改寫的 payload 說成未改動，本身就是假話）。
空白與純空格 needle 直接拒絕，因為任何輸出都滿足它，等於沒檢查。

**正負控制**（`integrations/headroom-atk/test_local_check.py`，17 條，離線）：

| 情境 | 期望 | 結果 |
|---|---|---|
| 變短且針在 | exit 0 PASS | ✅ |
| 完全不變 | exit 3 | ✅ |
| 等長改寫 | exit 3，且訊息不得說 byte-for-byte | ✅ |
| 膨脹 | exit 3，且不得印 "fewer" | ✅ |
| 針丟失（即使大幅變短） | exit 1 | ✅ |
| 空 needle／純空格 needle | exit 2 | ✅ |
| 多根針只活一根 | exit 1 | ✅ |

**負控制（關鍵）：** 同一份測試檔對**舊 head 03dc57b** 執行 → **5 failures、6 errors**；
對新 head → **17/17 OK**。reviewer 自己的 `reviewer_checks.py` **原檔未改**，對新 head 執行的輸出
也一併留存，五條案例分別得到 0／3／3／3／1 與 `synthetic_key_visible: false`。

## P5-03 照公開指令能跑 — IMPLEMENTED_PENDING_REVIEW

| review 指出 | 處置 |
|---|---|
| 安裝未釘版本 | 全部改成 `pip install "headroom-ai[proxy]==0.37.0"`，並註明 Python 3.11 |
| registry example 在 root 產生 log、script 讀另一目錄 | example 補上 `cd integrations/headroom-atk`，並加一筆 `example_on_your_own_data` |
| 免費樣本只叫人換 localhost endpoint | 改成完整 curl，帶 `x-headroom-base-url`，並明說「只換 endpoint 不夠」——那正是同一份文件警告的錯路由 |
| clone 預設 main，但資產在 Draft 分支 | 所有入口（README、root README、免費樣本、registry `entry_point_ref`）都寫明 `git checkout claude/atk-headroom-adoption`、**NOT on main** |
| 試用環境已預裝 headroom | 見下 |

**乾淨環境實跑**（`evidence/pr5-r2/clean_install.txt`）：全新 `git clone` → `git checkout` 該分支 →
`python3 -m venv`（先確認 **headroom preinstalled: False**）→ 釘版安裝 exit 0 → `make_log.py` 產出
**md5 `0ad9194a…74cf7`，與 README 印的一字不差** → `local_check.py` **PASS，15.1%** → 17 條測試 OK。

`tools/build_materials.py` 在該乾淨 clone 重跑，`registry/materials.json` md5 前後相同、git status
乾淨——`_adoption` 記錄是生成出來的，不是會被下次 build 蓋掉的手改。

## P5-04 主張與證據同步 — IMPLEMENTED_PENDING_REVIEW

1. **算術錯誤，reviewer 是對的。** 四筆 usage = 40,572 + 29,781 + 40,589 + 25,525 = **136,467**。
   `UNIT_ECONOMICS.md` 原本寫「約 81k」，漏掉了兩個任務的壓縮路徑。已改，並在原處寫明改了什麼。
   同時撤回「模型 token 相對人力很小」——人力未量測，那句是期望不是量測。
2. **付費樣本的互斥條款。** 原本同時承諾「未達門檻退款」與「負面結果照收費」。已改寫成一個
   **未決問題**，把 (a)(b) 兩個選項與各自的代價列出來，明說不由 executor 決定。整份標
   **未批准、未推出**。
3. **超出證據的主張，逐條收斂：**
   - 「needle 永遠保留」→「我們測過的六種 payload 都保留；六種不是保證，所以才附預檢工具」。
   - 「JSON log 完全沒用」→「我們測的那一種 JSON 形狀沒有效果；先測你自己的」。
   - 「摘要失敗不是壓縮的問題」→「兩條路徑都失敗，所以壓縮不是全部原因；但也不能因此斷定壓縮
     沒有額外損失，一對呼叫分不開」。
   - 「這個空位沒人佔」→ 降為**外部 agent 的一次觀察**，不是市場結論（見下第 5 點）。
4. **單位與完整性。** 「63% of the prompt cost」→ **prompt tokens**；全文不出現任何貨幣節省主張。
   `cost_usd: null` 標為**我們當時的觀察筆記**，不是提交檔能佐證的事（提交的 JSON 只有 `usage`
   與回答文字）。提交檔一律稱 **excerpt**，不稱 raw response。真實 37.1% 那組明確標為
   **2026-09-18 的歷史單次案例**：輸入檔未保存、本輪未重測、不是保證。
5. **搜尋紀錄。** 逐條 query 的原始 transcript **未保存**，只剩隔離 agent 事後的自述。因此
   上一輪「用同一組查詢重測」的說法**是錯的，在此撤回**。改為 `evidence/SEARCH_BASELINE.md`：
   固定九條新查詢、定義 T0 為**入口與描述真正公開於 main 之日**（目前尚未發生，沒有啟動任何計時），
   並事先寫死四條解讀規則——九條是診斷不是發現率、出現只證明可見性、**結果變化不等於命名是原因**
   （另列四個本基線分不開的競爭解釋：Draft 分支無導覽、尚未被重新索引、排名波動、該類目已飽和）。
   基線**尚未執行**，表格沒有任何預填的 0 或 PASS。
6. **免費樣本的贊助標示。** 原本寫 paid-for placement——**沒有這筆交易**，那是捏造。改為
   「ATK 推廣自己的成果」，並明說我們無法自我證明獨立性：工具是第三方 Apache-2.0、離線指令不需要
   ATK 帳號、方法寫出來讓你對自己的 provider 重跑——請看證據，不要看我們的免責聲明。

---

## 1A 入口與最小採用驗證

- **root README 第一畫面**新增「Verified assets you can use today」表，直接連到 headroom 入口，
  並寫明**188 筆候選裡只有 1 筆**達到已驗證標準，其餘是評分候選不是已驗證資產。
- 描述改成問題導向：「幫助 agent 與開發者找到、安裝並實際使用實用 AI 工具，每筆已驗證條目附授權、
  成本與權限資訊及可追溯的實跑紀錄，支援可選的 ATK 接入」。
- **GitHub About／topics 的擬定值**放在 `DISTRIBUTION.md`（方向已批准，未套用——那是負責人的
  repository 設定動作）。
- 機器索引與人類入口同步：`_adoption` 新增 `entry_point_ref`（明說不在 main）、`issues_to`
  （問題回報入口，並區分 headroom 本身的 bug 該去哪）、`example_on_your_own_data`。
- **受控採用檢查**：乾淨 clone + 乾淨 venv 依公開指令產生預期離線結果（上節）。
- **可重跑搜尋基線**：已建立、尚未執行。
- 給網址的採用測試／自然搜尋／第三方使用／ATK 導流**四條帳分開記**，見基線末表。ATK 導流那一條
  註明**不可量測**——這份資產沒有任何追蹤。

## 2A 免費資產與價值回收

免費交付以解題與接入為中心，ATK 明示為提供／維護者與可選接點，不綁定使用、不要求下游無條件推薦。
自願回饋入口只有一個 GitHub issue 連結：**沒有遙測、沒有 log、沒有追蹤**，並提醒不要貼 key 或真實
log（`local_check.py` 只印大小與通過與否，那個輸出可以安心貼）。
**第三方回報至今：無紀錄。** 不是「少」，是沒有。本輪未建遙測、未設收款路徑、未擴寫付費業務。

## 3A 上游備稿

`integrations/headroom-atk/upstream/HEADROOM_FEEDBACK_DRAFT.md`。**狀態：待核准、未送出。**
未開任何 issue／discussion／留言／PR。

**先查重再寫**（2026-09-18 查上游 tracker）：
- **#1503（已關閉）** 是第 1、2 項的上游母題；0.37.0 已有該機制，所以**第 1 項降為文件問題**，
  而該 issue **明確沒有涵蓋** `/v1` 語意 → 第 2 項是仍未被回報的缺口。
- **#3336（開啟中）** 與第 3 項同源（不願意靜默回退到預設 vendor）→ 建議第 3 項**以留言附在 #3336**，
  不另開新 issue。
- #3346、#3280 為不同問題，不混報。

**結論：兩次觸碰 tracker，不是三個新 issue。**

**第 3 項本輪新增了根因**（原本只知道「沒印出來」）：`logging.getLogger("headroom.proxy")` 是
NOTSET、繼承 WARNING，`isEnabledFor(WARNING)` 為 **True**——record 有被建立；但 proxy 行程的
**root logger 沒有掛任何 handler**，所以它被丟棄。stdout/stderr **0 次**，`--log-file` 也 **0 次**。
不是被等級擋掉，是被送進虛空。照原始碼去 grep 那串字的人會一無所獲，然後得出「這條分支沒走到」的
錯誤結論。

版本已確認 0.37.0 **就是最新版**，不是拿舊版結果套新版。三項都附無秘密重現指令；ATK 只在必要背景
出現，重現一律用 `your-gateway.example` 與本機 stub。

---

## 未做、未驗證、仍然缺的

1. **真實 live 未重跑。** 已暴露憑證不重用，本輪未發任何付費請求。37.1% 那組維持為歷史單次案例。
2. **外部自發發現 0/3**，且原始 query log 遺失；新基線尚未執行，T0 尚未發生。
3. **第三方使用 0 筆。** 兩次隔離 agent 試驗都在我自己的 session 內，不是第三方。
4. **上游未送出。**
5. **About／topics 未套用**（需 repository 設定權限）。
6. **付費側全部未驗證**：無需求、無價格、無收款、無單位成本；退款條款是未決問題。
7. **未測**：LiteLLM 官方 guardrail 路徑；headroom 的 `[code]` 選用元件；headroom 其他警告是否
   同樣被丟棄（只觀察了這一條路徑）。

## 下一位 reviewer 需要核對的範圍

- `evidence/pr5-r2/controls.txt`：P5-01 四格前後對照、P5-02 新舊 head 的測試結果、reviewer 原腳本輸出。
- `evidence/pr5-r2/clean_install.txt`：乾淨 clone／venv 的完整指令與輸出、md5、registry build 冪等。
- `test_local_check.py`：17 條；建議也對 03dc57b 跑一次確認它會失敗。
- `evidence/SEARCH_BASELINE.md`：查詢是否夠中性、解讀規則是否夠嚴、T0 定義是否可被提前宣告。
- `upstream/HEADROOM_FEEDBACK_DRAFT.md`：查重結論是否成立、語氣是否是技術回饋而非宣傳、
  是否真的無秘密。**上游送審稿位置就是這一份。**
- 主張收斂是否足夠：特別是 README 的「Will this help YOUR logs?」與免費樣本的贊助標示。

**負責人需要決定的仍是三項**（與上一輪相同，本輪未新增）：套用 About／topics；授權送出上游回饋；
輪替已暴露憑證。付費定價本輪依指示不請負責人選擇。

下一輪 reviewer 檔名：`reviews/PR5_R2_REVIEW_<short-sha>.md`。

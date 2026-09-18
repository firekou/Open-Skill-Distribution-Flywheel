# ATK 分發與接入：第一個交付

**狀態：待獨立 review（IMPLEMENTED_PENDING_REVIEW）**
**分支：** `claude/atk-distribution-provider-seam` ｜ **起始 commit：** `345b1aa`
**交付：** `integrations/atk-provider/`

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

**未解事項：** ATK endpoint 是否正確／已上線（見第五節）。這是需要負責人或有權限者確認的事實，不是我能從程式決定的。

# 試用操作流程：從拿到資產到再次使用
work_id：ATK-VALUE-READINESS-01 · **revision 2** · 交付 3/5
source main：`60dbdff09d14da493ee0d65de364a9b72e7b8321`；本修正 source_head `57fa50900035cb6eef316504b065cf98a8b4fee0`

> **revision 2 更正**：
> 1. revision 1 在 R4 寫「在 provider 後台設好本輪的花費上限」，等於假設任何 provider 都有能擋住後續請求的硬上限。provider 還沒選，這個能力不能預設存在。本版把它改成 **G0 費用控制閘門**：沒有證據就不能進任何 [LIVE] 步驟。
> 2. revision 1 在 P2 依 A/B/A 分配路徑。本版依 `STUDY_PROTOCOL.md` 第五節，**第一階段只走路徑 B，不分配、不比較**。第二階段的做法只寫入口，進場條件未成立前不能照做。
> 3. 實測引用改指 r2 manifest（`evidence/r2/manifest.json`）。r1 的 `evidence/base_path_*.json` 與 `evidence/retry_no_server_stdout.txt` 保留原樣，降為 REPORTED。

每一步標記性質：
- **[OFFLINE]** 本機即可，無網路費用、無金鑰
- **[LIVE]** 會呼叫真實模型、會花錢，**需要 live 授權，且 G0 已通過**
- **[EXTERNAL]** 牽涉受試者或對外，**需要邀請／發布授權**

目前能照著跑的只有 [OFFLINE] 步驟。[LIVE] 與 [EXTERNAL] 寫的是授權成立後的做法。

---

## G0 費用控制閘門（任何 [LIVE] 之前，一次性）

aider 0.86.1 的 120 個 CLI 參數中沒有花費、預算或 token 上限參數（`args.py`）。所以費用只能在 aider 外面控制。**能力要先查證，不預設。**

**G0-1 查 provider 能力**：provider 選定後，從**官方文件**確認下表，每格附網址與讀取時間（UTC）。查不到的格子寫「未知」，不推測。

| 要確認的 | 為什麼要分清楚 |
|---|---|
| 限制的範圍：單把 key／project／整個組織 | 組織級上限會被同組織的其他用量吃掉，不能當本研究的上限 |
| **警報型還是拒絕型** | 警報型只寄通知，後續請求照常計費；只有「超過後拒絕後續請求」的才算硬上限 |
| 超過後回什麼錯誤（HTTP 狀態碼） | aider 對 429（RateLimitError）會重試，對 401/403 不重試（`exceptions.py`）；決定超限後 aider 會不會卡著重試 |
| 生效延遲 | 用量統計若有延遲，硬上限也可能被超過；文件沒寫就記「未知」 |
| 被拒絕的請求是否計費 | 決定超限後的重試有沒有成本 |

**G0-2 判定**（研究者填，負責人簽）：

| 結果 | 可以 live 嗎 |
|---|---|
| 有**拒絕型**上限，範圍能只涵蓋本研究（key 或 project 級） | 可以，照 R4 設定 |
| 只有警報型、只有組織級，或查不到 | **不能**，除非負責人選下面一個替代方案並書面接受殘餘風險 |

**替代方案**（不需要新平台，負責人擇一；也可以選「不 live」）：
1. **預付餘額、關閉自動儲值**：餘額本身就是上限。前提是 provider 在餘額歸零時會拒絕請求——這一點也要照 G0-1 查證。殘餘風險：組織內其他用量共用同一餘額。
2. **回合上限＋錯誤即停（人工）**：每人主對話最多 N 回合（N 由負責人定）；研究者看到任何一行 `Retrying in` 就記錄，**同一回合出現第 3 行即按 Ctrl-C 結束該人本次嘗試**。這是人工控制，不是硬限制。殘餘風險：按下前的已發生嘗試，以及 litellm 內部可能的額外重試（未驗證）。上限估算見 `RELEASE_AND_ACCESS_PACKET.md` 4.4。
3. **不 live**：停在 [OFFLINE]，第一階段不開始。

G0 的結果、替代方案選擇與負責人簽核一起寫入核准紀錄。**G0 沒過，R4 之後的 [LIVE] 步驟全部不做。**

---

## 研究者準備（每位受試者前做一次）

**R1 [OFFLINE] 取得固定資產**
```bash
git fetch origin claude/atk-aider-first-use-01
git checkout d1474670db12934c80caa05674c8e4320cbad312 -- integrations/aider-atk
md5sum integrations/aider-atk/sample/import_contacts.py integrations/aider-atk/sample/test_import_contacts.py
```
兩個 md5 必須是 `da2b54d995a08cdbb84f157587f82f1d` 與 `2952746b8e56b5a35fdb02949bcdabe1`，不同就停止。
（PR14 若已合併，改從 main 取；md5 要求不變。）

**R2 [OFFLINE] 確認 baseline 仍然失敗**
```bash
cd integrations/aider-atk/sample && python3.11 -m unittest test_import_contacts
```
要看到 `FAILED (failures=1, errors=1)`。**如果 baseline 已經全過，任務就不成立，停止。**

**R3 [OFFLINE] 準備乾淨工作目錄**
把 `import_contacts.py` 與測試複製到全新目錄，`git init` 並 commit 一次，方便事後看 diff。
把測試檔設為唯讀：`chmod 444 test_import_contacts.py`。

**R4 [LIVE] 注入憑證**（G0 已通過才做）
端點、金鑰、模型由 live 授權指定。**金鑰只放環境變數**，不寫檔、不放命令列、不貼進任何對話。
若 G0 選的是拒絕型上限：為本研究開獨立的 key 或 project，設上限，研究結束即撤銷。若 G0 選的是替代方案：照該方案準備，並把回合上限 N 寫在研究者紀錄最上方。

---

## 受試者流程（第一階段：只走路徑 B）

**P1 [EXTERNAL] 取得同意**
說明只收時間、失敗類型、協助紀錄、嘗試數與費用、評分結果、能力背景；不收程式碼、金鑰、log 全文、身分。未同意不開始。

**P2 [EXTERNAL] 記能力背景並計時開始**
先填 `STUDY_PROTOCOL.md` 第八節的能力背景欄位。**第一階段不分配路徑，所有人都走路徑 B。** 打開材料的那一刻按下計時。

**P3 [LIVE] 受試者照材料設定**
受試者看 PR14 `QUICKSTART.md`，並可執行 `python3 check_config.py`（[OFFLINE]，不連網）。
研究者**不主動提示**。受試者提問才回答，並記入協助紀錄。
受試者若想走材料沒涵蓋的路（例如 Ollama 原生前綴，見 #4638），不阻止，記 F-PATH。

**P4 [LIVE] 啟動參數（控制費用用）**
```bash
aider --model "$AIDER_MODEL" --no-auto-commits --map-tokens 0 import_contacts.py
```
- `--no-auto-commits`：避免每次修改都觸發 helper model 寫 commit message（`repo.py:361`，預設是開的）
- `--map-tokens 0`：關掉 repo map，減少 prompt tokens
- 對話保持短：歷史超過上限會觸發 helper model 做摘要（`history.py:116`）
- 研究者計主對話回合數，到 G0 的上限 N 就結束；若 G0 選替代方案 2，照其錯誤即停規則。

**P5 [LIVE] 注意啟動時的外連**
即使加 `--no-analytics --no-check-update`，aider 啟動時仍會連 `raw.githubusercontent.com` 抓價格表。受試者環境若禁止外連，這一步會印錯誤但**不會中止**。這不是設定錯誤，不計 F-CONFIG。

**P6 [OFFLINE] 判定成功**
```bash
md5sum test_import_contacts.py        # 必須仍是 2952746b8e56b5a35fdb02949bcdabe1
python3.11 -m unittest test_import_contacts
git diff                              # 人工看改了什麼
```
**不要看 aider 的 exit code。** r2 manifest `retry_no_server`：端點完全不存在、8 行重試全失敗，aider 仍回 exit 0（牆鐘 78.0 秒，monotonic 計時）。
三條（5/5、md5 相符、diff 合理）都成立，按下計時停止，記首次成功時間。

**P7 [LIVE] 記費用**
從 **provider 後台**讀本輪嘗試數、tokens、實付，不從 aider 輸出推算。
提醒：可重試的錯誤（連線、逾時、限流、5xx）aider 對每個邏輯呼叫做 **9 次嘗試**，間隔 0.25→32 秒，總等待約 64 秒。litellm 內部是否另有重試**未驗證**，所以 9 是下限。設定錯誤（404、400、401、403）**不會重試**，會立刻失敗——所以設定錯是便宜的，伺服器問題才貴。

**P8 [OFFLINE] 去識別回報**
只填 `STUDY_PROTOCOL.md` 第十節第一階段表格的欄位。受試者編號 P1、P2…。**第一階段不填任何比較欄位。**

---

## 再次使用

**U1 [EXTERNAL] 約定再次使用**
首次成功後，**不同日期**請受試者自己再完成一次同類任務，研究者不在場。

**U2 [LIVE] 受試者自行完成**
不給任何新材料。費用控制照 G0。

**U3 [OFFLINE] 記錄**
填「再次使用」表：是否完成、是否需要協助。**需要協助才完成的，不算獨立再次使用。**

---

## 第二階段（配對比較）：目前不能照做
進場條件見 `STUDY_PROTOCOL.md` 第六節：任務 2 存在且結構對等、第一階段至少 1 人完成、最低有用差異已事前 commit、live 授權涵蓋第二階段。**本版不建任務 2，所以第二階段無法開始。** 條件成立後，分配與分析照 `STUDY_PROTOCOL.md` 第七節，本 runbook 屆時另出修訂版補上逐步流程。

---

## 什麼情況下停止整個試用
- G0 沒有通過或其證據失效（provider 改規則、key 被換） → 不開始／立即停止 [LIVE]。
- 任何受試者的評分測試檔被改 → 暫停，查原因後才繼續。
- 單人費用超過授權上限，或回合數到 N → 停止該人。
- 連續兩位 F-AUTH 或端點不可用 → 停止，屬環境問題。

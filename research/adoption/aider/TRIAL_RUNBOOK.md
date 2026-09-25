# 試用操作流程：從拿到資產到再次使用
work_id：ATK-VALUE-READINESS-01 · revision 1 · 交付 3/5
source main：`60dbdff09d14da493ee0d65de364a9b72e7b8321`

每一步標記性質：
- **[OFFLINE]** 本機即可，無網路費用、無金鑰
- **[LIVE]** 會呼叫真實模型、會花錢，**需要 live 授權**
- **[EXTERNAL]** 牽涉受試者或對外，**需要邀請／發布授權**

本文件目前能照著跑的只有 [OFFLINE] 步驟。[LIVE] 與 [EXTERNAL] 寫的是授權成立後的做法。

---

## 研究者準備（每位受試者前做一次）

**R1 [OFFLINE] 取得固定資產**
```bash
git fetch origin claude/atk-aider-first-use-01
git checkout d1474670db12934c80caa05674c8e4320cbad312 -- integrations/aider-atk
md5sum integrations/aider-atk/sample/import_contacts.py integrations/aider-atk/sample/test_import_contacts.py
```
兩個 md5 必須是 `da2b54d9…` 與 `2952746b…`，不同就停止。
（PR14 若已合併，改從 main 取；md5 要求不變。）

**R2 [OFFLINE] 確認 baseline 仍然失敗**
```bash
cd integrations/aider-atk/sample && python3.11 -m unittest test_import_contacts
```
要看到 `FAILED (failures=1, errors=1)`。**如果 baseline 已經全過，任務就不成立，停止。**

**R3 [OFFLINE] 準備乾淨工作目錄**
把 `import_contacts.py` 與測試複製到全新目錄，`git init` 並 commit 一次，方便事後看 diff。
把測試檔設為唯讀：`chmod 444 test_import_contacts.py`。

**R4 [LIVE] 注入憑證**
端點、金鑰、模型由 live 授權指定。**金鑰只放環境變數**，不寫檔、不放命令列、不貼進任何對話。
在 provider 後台先設好**本輪的花費上限**——aider 本身沒有任何限制花費或 token 的參數（`args.py` 120 個參數中查無），上限只能在 provider 端設。

---

## 受試者流程

**P1 [EXTERNAL] 取得同意**
說明只收時間、失敗類型、協助紀錄、嘗試數與費用、評分結果；不收程式碼、金鑰、log 全文、身分。未同意不開始。

**P2 [EXTERNAL] 分配路徑並計時開始**
依 `STUDY_PROTOCOL.md` 第七節分配 A 或 B。**打開材料的那一刻按下計時。**

**P3 [LIVE] 受試者照材料設定**
- 路徑 A：只看官方頁 https://aider.chat/docs/llms/openai-compat.html
- 路徑 B：看 PR14 `QUICKSTART.md`，並可執行 `python3 check_config.py`（[OFFLINE]，不連網）

研究者**不主動提示**。受試者提問才回答，並記入協助紀錄。

**P4 [LIVE] 建議的啟動參數（控制費用用）**
```bash
aider --model "$AIDER_MODEL" --no-auto-commits --map-tokens 0 import_contacts.py
```
- `--no-auto-commits`：避免每次修改都觸發 helper model 寫 commit message（`repo.py:361`，預設是開的）
- `--map-tokens 0`：關掉 repo map，減少 prompt tokens
- 對話保持短：歷史超過上限會觸發 helper model 做摘要（`history.py:116`）

**這兩個路徑都要用同一組參數**，否則比較不公平。

**P5 [LIVE] 注意啟動時的外連**
即使加 `--no-analytics --no-check-update`，aider 啟動時仍會連 `raw.githubusercontent.com` 抓價格表。受試者環境若禁止外連，這一步會印錯誤但**不會中止**。這不是設定錯誤，不計 F-CONFIG。

**P6 [OFFLINE] 判定成功**
```bash
md5sum test_import_contacts.py        # 必須仍是 2952746b…
python3.11 -m unittest test_import_contacts
git diff                              # 人工看改了什麼
```
**不要看 aider 的 exit code。** 本輪實測：端點完全連不上、9 次嘗試全部失敗，aider 仍回 exit 0。
三條（5/5、md5 相符、diff 合理）都成立，按下計時停止，記首次成功時間。

**P7 [LIVE] 記費用**
從 **provider 後台**讀本輪嘗試數、tokens、實付，不從 aider 輸出推算。
提醒：可重試的錯誤（連線、逾時、限流、5xx）**每個邏輯呼叫最多 9 次嘗試**，間隔 0.25→32 秒，總等待約 64 秒（本輪實測，見 `evidence/retry_no_server_stdout.txt`）。設定錯誤（404、400、401、403）**不會重試**，會立刻失敗——所以設定錯是便宜的，伺服器問題才貴。

**P8 [OFFLINE] 去識別回報**
只填 `STUDY_PROTOCOL.md` 第十一節的表格欄位。受試者編號 P1、P2…。

---

## 再次使用

**U1 [EXTERNAL] 約定再次使用**
首次成功後，**不同日期**請受試者自己再完成一次同類任務，研究者不在場。

**U2 [LIVE] 受試者自行完成**
不給任何新材料。

**U3 [OFFLINE] 記錄**
填「再次使用」表：是否完成、是否需要協助。**需要協助才完成的，不算獨立再次使用。**

---

## 什麼情況下停止整個試用
- 任何受試者的評分測試檔被改 → 暫停，查原因後才繼續。
- 單人費用超過授權上限 → 停止該人。
- 連續兩位 F-AUTH 或端點不可用 → 停止，屬環境問題。

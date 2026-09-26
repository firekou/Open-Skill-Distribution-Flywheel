# Live 交接清單：一次有上限的真實模型執行（README 第 6 步）

work_id `ATK-AIDER-DELIVERY-01` revision 1 · executor：Claude · 2026-09-26 UTC

**本檔的所有 [LIVE] 命令都是 NOT RUN。** 本檔不授權任何動作，也沒有讀取、印出或搬運任何金鑰，沒有假設任何預算。
命令、費用公式、停止程序都直接沿用 PR17 已審的 `LIVE_EXECUTION_PLAN.md`（`6ea3cec9937e74de8ce77f47c5e92d3d1617c506`，[PR17 R1](../../../reviews/PR17_R1_LIVE_PREP_6ea3cec9.md) APPROVED_WITH_CONDITIONS）和核准表 `LIVE_OWNER_APPROVAL_MATRIX.md`（同一 commit），沒有重新研究。
和 PR17 唯一的差別：工作目錄改成 README 第 5 步做出來的 `$RUN/asset/sample`（已有 git baseline、測試檔已 chmod 444），檔案完整性改用 SHA-256。

狀態欄的意思：
- **READY**：已備妥，離線測過。
- **NOT_RUN**：等負責人決定，決定後即可做。
- **BLOCKED_ACCESS**：只有負責人或供應商能做，executor 沒有、也不應該有這個權限。

---

## 一、待填欄位（全部要填，才開始 L1）

| # | 欄位 | 值 | 狀態 | 誰來填／依據 |
|---|---|---|---|---|
| 1 | 供應商與 endpoint（`OPENAI_API_BASE`） | ATK `https://api.aitokenking.com.tw/api/v1`／OpenRouter `https://openrouter.ai/api/v1`／OpenAI `https://api.openai.com/v1`，只選一個 | **NOT_RUN** | 負責人在核准表勾選（`OWNER_ATK_AIDER_LIVE_DECISION`） |
| 2 | 模型（`AIDER_MODEL`，要帶 `openai/` 前綴） | 例：`openai/claude-sonnet-4.6`、`openai/openai/gpt-5.6-luna`、`openai/gpt-5.6-luna` | **NOT_RUN** | 同上；核准當天要再確認該 endpoint 真的提供這個模型 |
| 3 | 執行環境 | 負責人電腦，或 Claude 雲端環境 | **NOT_RUN** | 負責人在核准表勾選 |
| 4 | 金鑰安全注入 | 只放進執行環境的環境變數。不貼聊天、不寫檔、不 commit、不放命令列 | **BLOCKED_ACCESS** | 負責人注入後回覆「已注入」即可，不回覆金鑰本身 |
| 5 | 金鑰輪替確認 | 這次用**新建**的 key（OpenRouter）或新 project（OpenAI），結束後撤銷 | **BLOCKED_ACCESS** | 負責人書面確認「新 key，已設上限，用完會撤銷」 |
| 6 | 核准當天單價（每 1M tokens，入／出） | OpenAI／OpenRouter：當天重讀官方模型頁，記 URL、時間、單價。ATK：**UNKNOWN** | **NOT_RUN**（ATK 為 **BLOCKED_ACCESS**） | 執行者當天讀公開頁；ATK 需營運端提供 |
| 7 | 每請求輸出 token 上限 | `max_tokens: 4096`（L1 暫用 64） | **READY** | 設定檔，PR17 loopback 測過請求帶上這個值 |
| 8 | 請求數上限 | 設定檔 `max_retries: 0`：每個邏輯呼叫最多 9 個 HTTP 請求；主對話最多 4 個邏輯呼叫。L2 最多 36 個，L1 最多 9 個 | **READY**（本機上限） | PR17 loopback 實測 9；本包 run 3 再次看到 9 次嘗試 |
| 9 | 總費用上限（provider 端，拒絕型） | $______ | **NOT_RUN** | 負責人填寫並在供應商後台設定。PR17 的建議值 $2 只是建議，**本檔不假設任何預算** |
| 10 | 拒絕型上限已生效 | OpenRouter：key `limit`；OpenAI：Enforce hard limit 打開，自動儲值關閉；ATK：**UNKNOWN** | **BLOCKED_ACCESS** | 負責人書面確認（不附含 key 的截圖） |
| 11 | 停止方式 | 見第四節 | **READY** | PR17 3.4 |
| 12 | 紀錄存放路徑 | `integrations/aider-atk/evidence/live/**`（藍圖 S3） | **NOT_RUN** | 等 `ATK-AIDER-LIVE-01` 派工時寫進 scope |

**ATK Router 目前不能選**：第 6、10 兩項沒有證據（PR17 R1 條件 2）。選 ATK 以前，要先由 ATK 營運端提供價格，以及「超過上限會拒絕請求」的書面說明。

---

## 二、L0 [OFFLINE] 準備（先做完 README 第 1–5 步）

```bash
cd "$RUN/asset/sample"
sha256sum test_import_contacts.py          # 必須 b2c040c2ae4ae6c7417acb8dcf4e3ed5c03ae26af95643f6b498a3ed697baada
git diff --quiet && echo clean             # 必須印 clean（baseline 沒被動過）
python3.11 -m unittest test_import_contacts   # 必須 FAILED (failures=1, errors=1)
# 負責人注入 OPENAI_API_BASE、OPENAI_API_KEY、AIDER_MODEL 之後：
python3 "$RUN/asset/check_config.py"       # 必須 exit 0；金鑰只會印成 SET
printf -- '- name: %s\n  extra_params:\n    max_tokens: 64\n    max_retries: 0\n' "$AIDER_MODEL" > .aider.model.settings.yml
cat .aider.model.settings.yml              # name 必須和 AIDER_MODEL 完全一樣
```
設定檔的格式和 `max_retries: 0` 的效果，在 PR17 loopback 測過（429／500 從 27 個請求降到 9 個）。本包 run 3 用同一個 `printf` 產生設定檔（`max_tokens` 為 4096），Aider 能正常讀取。

## 三、L1、L2 [LIVE]（NOT RUN）

**L1 最小連通**（`max_tokens` 64，只問一句）：
```bash
timeout --signal=INT 180 "$RUN/.venv/bin/aider" --model "$AIDER_MODEL" --no-git --no-auto-commits --no-auto-lint \
  --map-tokens 0 --max-chat-history-tokens 65536 --timeout 60 \
  --no-check-update --no-analytics --yes --exit --message "Reply with OK only."
```
- 成功：輸出有模型回覆，沒有 `Retrying in`，供應商後台顯示 1 個請求。
- 失敗：記錄後停止，回報負責人。
- 只有 400「參數不支援」這一種情況可以處理：把 `max_tokens` 換成 `max_completion_tokens`，再跑一次並記錄（PR17 3.2）。

**L2 固定任務**（先把設定檔 `max_tokens` 改回 4096）：
```bash
sed -i 's/max_tokens: 64/max_tokens: 4096/' .aider.model.settings.yml
timeout --signal=INT 900 "$RUN/.venv/bin/aider" --model "$AIDER_MODEL" --no-auto-commits --no-auto-lint \
  --map-tokens 0 --max-chat-history-tokens 65536 --timeout 120 \
  --no-check-update --no-analytics --yes --exit \
  --read test_import_contacts.py \
  --message "Change import_contacts.py so it reads the CSV by column name instead of by position. Keep name,email order working; also read email,name correctly; raise MissingColumnError mentioning 'email' when the email column is missing; keep empty strings as empty strings; keep non-ASCII text unchanged. Do not modify test_import_contacts.py." \
  import_contacts.py 2>&1 | tee aider_live.log
echo "aider_exit=${PIPESTATUS[0]}"   # 只記錄，不當成功訊號
```
L2 的旗標和任務訊息逐字沿用 PR17。本包 run 3 用這組完全相同的旗標和訊息，對一個關閉的 loopback port 跑過：沒有連到任何模型，exit 0，嘗試 9 次，共 68 秒。

**L3 判定** = README 第 7 步：測試檔 hash 不變，5/5 OK，`git diff --stat` 只有 `import_contacts.py`，人工讀 diff。**不看 Aider 的 exit code。**

**L4 紀錄**（去敏）要記下：
- 命令（金鑰寫成 `<KEY>`）、版本、起訖 UTC、時長、exit；
- `aider_live.log` 的 SHA-256、diff、測試輸出、`Retrying in` 的行數；
- 供應商後台讀到的請求數、tokens、實付金額（能取得的部分，不附帳務截圖）；
- 失敗原因。

## 四、停止方式（沿用 PR17 3.4）

1. 整條命令包在 `timeout --signal=INT`（L1 180 秒、L2 900 秒）裡。
2. 執行者全程看著輸出。**第一次出現 `Retrying in` 就按 Ctrl-C**，記下時間與錯誤訊息，不重跑，回報負責人。
3. 看到 402，或看到 429 而且訊息提到 credit、quota 或 spend limit：代表上限到了。停止，不加額度，不重試。
4. L1、L2 各只跑一次。失敗也保存紀錄；第二次嘗試要另外核准。

## 五、費用上界（沿用 PR17 第五節，不重算）

有 `max_retries: 0` 時，L2 最壞約為：
- `gpt-5.6-luna` 標準價：約 $0.30；
- OpenRouter 列表最高價：約 $0.60。

典型一次成功約 $0.0015。這些價格是 2026-09-25 的讀數，核准當天要重讀（第一節第 6 項）。ATK：**無法估算**。
這是很鬆的上界：假設每個被拒請求都完整計費，而被拒請求是否計費仍是 UNKNOWN。上限生效也可能延遲（OpenAI 官方寫明非即時；OpenRouter 的延遲 UNKNOWN）。

## 六、開始條件

第一節 12 項全部不是 NOT_RUN 或 BLOCKED_ACCESS，而且 GPT 派出 `ATK-AIDER-LIVE-01` 工作包（固定 source SHA、期限、scope、費用上限），才能開始 L1。
在那之前，README 其他步驟照常可用。**只有第 6 步停住。**

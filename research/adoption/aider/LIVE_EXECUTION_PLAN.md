# Live 執行計畫：一次有上限的 Aider 真實任務
work_id：ATK-AIDER-LIVE-PREP-01 · revision 1 · 交付 2/3
source main：`b0770499cbef3f5917bd3505433924e0edbb8b27`；readiness：PR16 `1dcd625df3bde48b13b91abb3b03eb7e19371558`；固定資產：PR14 `d1474670db12934c80caa05674c8e4320cbad312`

**本文件所有 [LIVE] 命令本批都是 NOT RUN。** 本批只跑了 loopback 假端點（不連外、不花錢），結果放在 `evidence/live-prep/`。
執行這份計畫要另開 work（藍圖 S3：`ATK-AIDER-LIVE-01`），而且要負責人在 `LIVE_OWNER_APPROVAL_MATRIX.md` 簽核之後才開始。

---

## 一、前置（全部成立才開始，任一不成立就停）

| # | 條件 | 證據放哪 |
|---|---|---|
| 1 | 負責人在核准表勾了一個選項，並填了總費用上限 | 核准表 |
| 2 | 該選項的**拒絕型**上限已設好：OpenRouter 在 key 上設 `limit`；OpenAI 在 project 上打開 Enforce a hard limit。OpenAI 另外要**關掉自動儲值** | 負責人書面確認（不附截圖中的 key） |
| 3 | 金鑰由負責人放進執行環境的環境變數，**不經過聊天、不寫檔、不 commit** | 負責人確認「已注入」 |
| 4 | 核准當天重讀價格頁，記下 URL、時間、單價 | 執行紀錄 |
| 5 | 執行 work 的 scope 包含 `integrations/aider-atk/evidence/live/**`（藍圖 S3 指定的產物路徑） | S3 派工 |

---

## 二、固定值

| 項目 | 值 |
|---|---|
| aider | `aider-chat 0.86.1`（底層 `litellm 1.75.0`、`openai 1.99.1`） |
| 待改檔 | `import_contacts.py`，md5 `da2b54d995a08cdbb84f157587f82f1d` |
| 評分測試 | `test_import_contacts.py`，md5 `2952746b8e56b5a35fdb02949bcdabe1`，chmod 444，並用 `--read` 只讀載入 |
| 任務訊息（逐字固定） | `Change import_contacts.py so it reads the CSV by column name instead of by position. Keep name,email order working; also read email,name correctly; raise MissingColumnError mentioning 'email' when the email column is missing; keep empty strings as empty strings; keep non-ASCII text unchanged. Do not modify test_import_contacts.py.` |
| 第一個請求的大小（實測） | 6,056 字元，約 1,400 tokens（tiktoken 估算；`evidence/live-prep/prompt_size/manifest.json`） |

環境變數名稱（值由負責人注入，不寫在這裡）：

| 選項 | `OPENAI_API_BASE` | `OPENAI_API_KEY` 來自 | `AIDER_MODEL` |
|---|---|---|---|
| ATK Router | `https://api.aitokenking.com.tw/api/v1` | ATK 金鑰 | `openai/claude-sonnet-4.6` |
| OpenRouter | `https://openrouter.ai/api/v1` | OpenRouter 金鑰（設了 `limit` 的那把） | `openai/openai/gpt-5.6-luna` |
| OpenAI 直連 | `https://api.openai.com/v1` | 屬於開了硬上限的 project 的金鑰 | `openai/gpt-5.6-luna` |

---

## 三、費用控制：三層

### 3.1 硬性（provider 端，唯一真正的上限）
依選項設定，見第一節第 2 條。**上限到了之後 Aider 不會馬上停**（實測，見 3.3），但被拒的請求不會產生新生成。官方明寫 OpenAI 的上限生效非即時，可能略超；OpenRouter 的延遲 UNKNOWN。

### 3.2 本機設定（壓低每次呼叫的最大量）
在工作目錄放 `.aider.model.settings.yml`（`name` 必須和 `AIDER_MODEL` 完全一樣）：
```yaml
- name: <與 AIDER_MODEL 相同>
  extra_params:
    max_tokens: 4096
    max_retries: 0
```
| 設定 | 作用 | 證據 |
|---|---|---|
| `max_tokens: 4096` | 每個請求的輸出上限 | **TESTED**：假端點收到的請求帶 `max_tokens: 4096`（`prompt_size/manifest.json`）。沒設時請求**沒有**輸出上限 |
| `max_retries: 0` | 關掉 OpenAI SDK 在每次 Aider 嘗試內的重送 | **TESTED**：429、500 從 27 個請求降為 9；正常請求不受影響（3.3） |
| `--max-chat-history-tokens 65536` | 讓歷史摘要不觸發，helper 呼叫歸零 | 讀碼：`history.py` 在歷史超過此值才摘要；4 回合最多約 17k tokens，碰不到。**未實測** |
| `--no-auto-commits` | 不呼叫 helper 寫 commit message | 讀碼 `repo.py:361` |
| `--no-auto-lint` | lint 失敗不觸發額外回合 | 讀碼 `base_coder.py` 反思迴圈 |
| `--map-tokens 0` | 不送 repo map | PR16 |
| `--timeout 120` | 單一 API 呼叫最多等 120 秒（預設 600） | `args.py` |

**模型不接受 `max_tokens` 時**：新型推理模型可能要求 `max_completion_tokens`，會回 400。實測 400 只送 1 個請求、不重試（`status_400`），所以 L1 會立刻看到錯誤；被拒請求是否計費 UNKNOWN，但不會產生輸出。那時把設定改成 `max_completion_tokens: 4096` 再跑 L1。

### 3.3 重試暴露（本機實測，loopback）
`evidence/live-prep/retry_exposure/manifest.json`。一次 `--message` 的單一邏輯呼叫，假端點固定回某個狀態時實際收到的 HTTP 請求數：

| 假端點回的狀態 | 真實情境 | 沒有 `max_retries: 0` | 有 `max_retries: 0`（設定檔） |
|---|---|---|---|
| 200 | 正常 | 1 個請求（2.762s） | 1 個請求（2.923s） |
| 400 | 參數錯 | 1（不重試） | — |
| 401 | 金鑰錯 | 1（不重試） | — |
| 404 | 路徑或模型錯 | 1（不重試） | — |
| **402** | **OpenRouter key 額度用完** | **9**（66.544s） | 未測（SDK 本來就不重送 402） |
| **403** | 權限不足 | **9**（66.753s） | 未測 |
| **429** | **OpenAI project 硬上限到了**／限流 | **27**（78.348s） | **9**（66.798s） |
| 500 | 伺服器錯 | **27**（78.734s） | **9**（66.748s） |

- 環境變數 `DEFAULT_MAX_RETRIES=0` **沒有效果**：429 仍是 27 個請求（`status_429_env_DEFAULT_MAX_RETRIES_0`，78.433s）。讀碼推測原因：`litellm/llms/openai/openai.py` 同步路徑寫死 `inference_params.pop("max_retries", 2)`。
- 設定檔的 `extra_params.max_retries: 0` **有效**，而且正常請求不受影響。
- 402 與 403 在這個假端點下被 litellm 轉成 `APIError`，Aider 照樣重試 9 次。**這更正了 PR16 已核准文件中「403 不重試」的寫法**（本批不改 PR16，交 reviewer）。
- 所有 case 的 Aider exit code 都是 0，再次確認 exit code 不能當成功訊號。
- 限制：假端點不送 `Retry-After`；真實 provider 若送，SDK 會照它等待，時間會更長；次數上限預期相同，未測。

### 3.4 本機停止程序（人工＋計時）
1. 整條命令包在 `timeout --signal=INT 900` 裡：15 分鐘一到自動中斷。
2. 研究者看著輸出。**第一次出現 `Retrying in`，就按 Ctrl-C**，記下時間與錯誤訊息，不再重跑，回報負責人。
3. 任何 402、429 且訊息提到 credit／quota／spend limit：代表上限到了，**停止，不加額度、不重試**。
4. 不做任何未核准的第二次嘗試。失敗也保存紀錄。

---

## 四、步驟

**L0 [OFFLINE] 準備**
```bash
git fetch origin claude/atk-aider-first-use-01
mkdir -p "$WORK" && cd "$WORK"
git -C "$REPO" show d1474670db12934c80caa05674c8e4320cbad312:integrations/aider-atk/sample/import_contacts.py > import_contacts.py
git -C "$REPO" show d1474670db12934c80caa05674c8e4320cbad312:integrations/aider-atk/sample/test_import_contacts.py > test_import_contacts.py
md5sum import_contacts.py test_import_contacts.py      # 必須 da2b54d9… / 2952746b…
python3.11 -m unittest test_import_contacts            # 必須 FAILED (failures=1, errors=1)
chmod 444 test_import_contacts.py
git init -q && git add . && git commit -qm baseline
# 寫 .aider.model.settings.yml（3.2），name 換成 $AIDER_MODEL
git -C "$REPO" show d1474670db12934c80caa05674c8e4320cbad312:integrations/aider-atk/check_config.py > /tmp/check_config.py
python3 /tmp/check_config.py                           # 必須 exit 0（離線檢查三類設定錯誤）
```

**L1 [LIVE] 最小連通**（NOT RUN）
先把設定檔的 `max_tokens` 暫改 64，只問一句：
```bash
timeout --signal=INT 180 aider --model "$AIDER_MODEL" --no-git --no-auto-commits --no-auto-lint \
  --map-tokens 0 --max-chat-history-tokens 65536 --timeout 60 \
  --no-check-update --no-analytics --yes --exit --message "Reply with OK only."
```
成功：輸出有模型回覆、無 `Retrying in`、provider 端用量顯示 1 個請求。
失敗：記錄錯誤，停止，回報負責人。**不修改設定後自己重跑**；只有 400「參數不支援」可依 3.2 換參數再跑一次，並記錄。

**L2 [LIVE] 固定任務**（NOT RUN）
設定檔 `max_tokens` 改回 4096：
```bash
timeout --signal=INT 900 aider --model "$AIDER_MODEL" --no-auto-commits --no-auto-lint \
  --map-tokens 0 --max-chat-history-tokens 65536 --timeout 120 \
  --no-check-update --no-analytics --yes --exit \
  --read test_import_contacts.py \
  --message "<第二節的任務訊息，逐字>" \
  import_contacts.py 2>&1 | tee aider_live.log
echo "aider_exit=${PIPESTATUS[0]}"
```
（`--yes` 讓 Aider 不停下來問；它在 `--exit` 後結束，不進互動。）

**L3 [OFFLINE] 判定**
```bash
md5sum test_import_contacts.py                         # 必須仍是 2952746b…
python3.11 -m unittest test_import_contacts -v         # 必須 5/5
git diff                                               # 人工讀：只改 import_contacts.py，沒有硬寫期望值
```
**不看 Aider 的 exit code**（PR16：端點全失敗時仍回 0）。三條都成立才算成功，另加人工語意核對。

**L4 [OFFLINE] 紀錄**（存到 S3 指定路徑，去敏）
命令（金鑰寫 `<KEY>`）、版本、起迄 UTC、monotonic 時長、exit、`aider_live.log` 雜湊、diff、測試輸出、`Retrying in` 行數、provider 後台讀到的請求數／tokens／實付（能取得的部分，不附帳務截圖）、失敗原因。

---

## 五、最大費用估算

符號：
- `M` = 主對話邏輯呼叫數 ≤ **4**（1 次＋最多 3 次反思，`base_coder.py` `max_reflections = 3`）
- `S` = 摘要 helper 呼叫數 = **0**（依 `--max-chat-history-tokens 65536` 的讀碼推論，未實測）
- `A` = 每個邏輯呼叫的 HTTP 請求數上限（見 3.3）
- `P` = 單次請求輸入 tokens 上限 ≈ 1,400 ＋ 3 ×（4,096 ＋ 1,000） ≈ **17,000**（第 4 回合帶著前 3 回合的最大輸出與一段反思訊息；1,000 是反思訊息的保守假設）
- `C` = 單次請求輸出 tokens 上限 = **4,096**（`max_tokens`）

```
最壞輸入 tokens = (M + S) × A × P
最壞輸出 tokens = (M + S) × A × C
最壞費用       = 最壞輸入 × 輸入單價 ＋ 最壞輸出 × 輸出單價
```
這假設每一個被重試的請求都完整計費——實際上多數錯誤請求沒有生成，所以這是**很鬆的上界**。被拒請求是否計費 UNKNOWN，因此不能再往下壓。

代入 `M + S = 4`、`P = 17,000`、`C = 4,096`：

| 情境 | A | 最壞輸入 tokens | 最壞輸出 tokens | `gpt-5.6-luna` 標準價 $0.20／$1.20 | OpenRouter 列表最高價 $0.40／$2.40 |
|---|---|---|---|---|---|
| **有 `max_retries: 0`（建議）** | 9 | 612,000 | 147,456 | **約 $0.30** | **約 $0.60** |
| 沒有 `max_retries: 0` | 27 | 1,836,000 | 442,368 | 約 $0.90 | 約 $1.80 |
| L1 連通（`max_tokens` 64，P 約 1,500） | 9 | 13,500 | 576 | < $0.01 | < $0.01 |

**建議硬上限 $2**：即使 `max_retries: 0` 沒生效、又路由到最貴的底層 provider（$1.80），加上 L1 仍在上限內。上限還有生效延遲，所以不設得更緊。

**ATK Router：價格 UNKNOWN，無法估算。** 負責人提供單價後代入同一公式。

**典型值（不是上限）**：一次成功約 1 個邏輯呼叫、輸入約 1,400、輸出約 1,000 tokens，`gpt-5.6-luna` 標準價約 **$0.0015**。

---

## 六、不在本計畫內
招募受試者（S4）、A/B 比較（S5 第二階段）、發布、merge、送上游。L1、L2 各只跑一次；要多跑要另外核准。

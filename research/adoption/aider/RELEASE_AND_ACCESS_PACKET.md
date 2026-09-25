# 發布與權限材料
work_id：ATK-VALUE-READINESS-01 · revision 1 · 交付 4/5
source main：`60dbdff09d14da493ee0d65de364a9b72e7b8321`
用途：把「發布」與「live 呼叫」兩個需要負責人決定的事，備到只剩一個簽核動作。**本文件不授權任何發布、邀請或付費呼叫。**

---

## 一、成果入口方案

### 現況（2026-09-25 經 GitHub API 讀取）
| 項目 | 值 |
|---|---|
| 可見性 | public |
| 授權 | MIT |
| description | **未設定** |
| topics | **未設定** |
| Discussions | 關閉 |
| Pages | 關閉 |
| stars / forks | 1 / 0 |

GitHub 預設的 repo 搜尋只比對名稱、About 與 topics，所以**目前外部幾乎不可能透過搜尋發現這個 repo**。這與帳本 `handoff.next_checkpoint = OWNER_GITHUB_DISCOVERABILITY_DECISION` 一致，本包不處理那個決定。

### 建議的固定入口
PR14 目前是 Draft、未合併，所以**現在沒有穩定入口**。兩個方案：

| 方案 | 入口 | 優點 | 缺點 |
|---|---|---|---|
| **A（建議）** | PR14 合併後的 `integrations/aider-atk/README.md`，連結釘到合併 commit SHA | 單一、穩定、可回溯 | 需要 merge 授權 |
| B | 釘在 PR14 head `d1474670` 的 blob 連結 | 現在就能用 | 使用者看到的是「未合併的 Draft PR」，信任度低；之後修改會變成新 SHA |

**決定點：PR14 要不要合併。** 這是 merge，需要負責人授權。

---

## 二、兩篇既有草稿：來源與需要更新的地方
| 草稿 | 來源 |
|---|---|
| `AIDER_WHAT_WE_LEARNED.md` | PR14 head `d1474670`，`integrations/aider-atk/` |
| `ATK_OPTIONAL_SETUP_DRAFT.md` | 同上 |

兩篇都經 GPT R2 覆核關閉條件。**但本輪有新的實測事實，發布前應補進去**（本包不改 PR14 檔案，只列清單）：

| # | 要補的 | 依據 |
|---|---|---|
| 1 | 設定檔 `.aider.conf.yml` 與 `--openai-api-base` 參數也驗過，三種方式在 0.86.1 都送到正確路徑 | 本輪 `evidence/base_path_*.json` |
| 2 | 公開回報 #4027（0.83.1 上 `/v1` 被吃掉）在 0.86.1 NOT REPRODUCED；**寫「0.86.1 重現不出來」，不寫「已修好」** | `SOURCE_AND_GAP.md` 第四節 |
| 3 | **aider 的 exit code 不能當成功訊號**：端點完全連不上時仍回 0 | `evidence/retry_no_server_stdout.txt` |
| 4 | 可重試錯誤每個邏輯呼叫最多 9 次嘗試、總等待約 64 秒；設定錯誤不重試 | 同上 ＋ `exceptions.py` |
| 5 | aider 沒有任何限制花費或 token 的參數，上限只能在 provider 端設 | `args.py` 120 個參數中查無 |

---

## 三、發布渠道與帳號能力

| 渠道 | 能力是否已確認 | 缺什麼 |
|---|---|---|
| 本 repo（README / 固定連結） | 本 session 的 GitHub 憑證對此 repo 有 admin 權限（API 回報）。**有權限不等於有授權。** | merge 與 About/topics 的負責人決定 |
| GitHub Discussions | **目前關閉** | 要開需負責人決定 |
| 上游 Aider（issue / PR） | 未查。CONTRIBUTING 要求顯著變更先討論，另有 CLA | 發送授權；本包不送 |
| 社群平台（X、Reddit、HN 等） | **完全未確認**。本 session 無任何社群帳號憑證，也不應有 | 帳號、發送授權、文案審核 |

**我沒有、也不去取得任何社群帳號的存取。** 這一欄只能由負責人或持有帳號的人確認。

---

## 四、live 呼叫預算：次數、tokens、重試、價格

### 4.1 每個邏輯呼叫最多幾次付費嘗試（實測）
對可重試錯誤，aider 0.86.1 每個邏輯呼叫**最多 9 次嘗試**：

| 嘗試 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 前一次等待(秒) | — | 0.25 | 0.5 | 1 | 2 | 4 | 8 | 16 | 32 |

- 讀碼依據：`models.py:1045-1079`（helper 呼叫）與 `base_coder.py:1449-1487`（主對話），兩處同一套邏輯，`RETRY_TIMEOUT = 60`。
- 模擬：照原始碼重算，9 次、總等待 63.75 秒。
- **實測**：對不存在的端點跑一次，輸出 8 行 `Retrying in …`、間隔 0.2(=0.25)／0.5／1／2／4／8／16／32，牆鐘 79 秒，**aider exit 0**。
- aider 未設定 litellm 自己的重試參數（`num_retries` 查無）。**litellm 內部是否另有預設重試，本輪未驗證。**

### 4.2 哪些錯誤會重試（`exceptions.py` 原表）
| 會重試（最多 9 次） | 不重試（立刻失敗） |
|---|---|
| APIConnectionError、APIError、InternalServerError、ServiceUnavailableError、BadGatewayError、**RateLimitError**、**Timeout**、ContentPolicyViolationError、InvalidRequestError、UnprocessableEntityError 等 | **NotFoundError**、**BadRequestError**、**AuthenticationError**、**PermissionDeniedError**、ContextWindowExceededError |

**對預算的意義：**
- 設定錯（404／400／401／403）**不重試**，立刻失敗，所以設錯很便宜。
- **Timeout 會重試**：如果 provider 已經開始生成而 client 逾時，provider 可能照樣計費。最壞情況下，一個邏輯呼叫可能產生**最多 9 次計費生成**。這是依機制推得的可能性，**未實測**。

### 4.3 除了主對話，還有哪些隱藏呼叫
| 來源 | 觸發條件 | 控制方式 |
|---|---|---|
| commit message（`repo.py:361`） | `--auto-commits` **預設開啟**，每次修改都觸發一次 helper model 呼叫 | `--no-auto-commits` 或 `--no-git` |
| 對話摘要（`history.py:116`） | 歷史超過 `max_chat_history_tokens` | 對話保持短 |
| repo map | `--map-tokens` 預設 `auto`，增加 prompt tokens | `--map-tokens 0` |
| 價格表外連 | 每次啟動，**不計入 provider 費用**（連的是 GitHub） | 無法用參數關閉（本輪實測） |

PR14 曾實測：`--no-git`、單一 `--message` 的條件下只送出 **1 個**請求。

### 4.4 上限怎麼算（公式，不含價格）
```
每人最大計費嘗試數 = 邏輯呼叫數 × 9
邏輯呼叫數        = 主對話回合數 ＋ helper 呼叫數（照 4.3 關掉則為 0）
每人 token 上限    = 最大計費嘗試數 × (每次 prompt tokens ＋ 每次 max completion tokens)
每人費用上限      = 上面 × 當日單價
```
建議受試者流程用 `--no-auto-commits --map-tokens 0`（見 `TRIAL_RUNBOOK.md` P4），並設**主對話回合上限**（例如 10 回合），讓 `邏輯呼叫數` 有確定值。回合上限的數字由負責人連同費用一起核准，本文件不替您定。

### 4.5 當日價格：**缺口，不猜**
- 端點與模型**尚未選定**，所以沒有單價可查。
- 本文件**不寫任何價格數字**，也不去讀任何 key 或帳務頁。
- 核准時的做法：選定端點與模型後，當天從 **provider 官方價格頁**抄下 prompt／completion 單價，連同頁面網址與讀取時間一起記入核准紀錄，再代入 4.4。

### 4.6 硬性費用保護只能在 provider 端
aider 0.86.1 的 120 個 CLI 參數中**沒有任何花費、預算或 token 上限參數**。所以：
1. 在 provider 後台為本研究開**獨立的 key**。
2. 對這把 key 設**硬性花費上限**。
3. 研究結束即撤銷這把 key。

---

## 五、需要負責人簽核的事（簽了這些，S3 live 就能開始）
| # | 決定 | 本文件已備妥的材料 |
|---|---|---|
| 1 | 用哪個端點與模型 | 4.5 的查價做法 |
| 2 | 每人回合上限、總費用上限 | 4.4 公式、4.1 的 9 倍係數 |
| 3 | provider 端獨立 key ＋ 硬上限由誰設 | 4.6 |
| 4 | PR14 是否合併（決定固定入口） | 第一節 |
| 5 | 草稿發布前是否補上第二節五項 | 第二節清單 |
| 6 | 招募渠道與對象 | 第三節（目前除本 repo 外全部未確認） |

# 發布與權限材料
work_id：ATK-VALUE-READINESS-01 · **revision 2** · 交付 4/5
source main：`60dbdff09d14da493ee0d65de364a9b72e7b8321`；本修正 source_head `57fa50900035cb6eef316504b065cf98a8b4fee0`
用途：把「發布」與「live 呼叫」需要的決定整理清楚。**本文件不授權任何發布、邀請或付費呼叫。**

> **revision 2 更正**：
> 1. revision 1 把「在 provider 為獨立 key 設硬性花費上限」寫成既定做法，並說「簽了第五節六項，S3 live 就能開始」。provider 還沒選，per-key 硬上限不能預設存在。本版改成**先查能力、再請負責人選**，查不到硬上限就不 live，除非負責人選替代方案並接受殘餘風險（4.6、第五節）。
> 2. revision 1 的 repo 現況與「本 session 對此 repo 有 admin 權限」沒有保存 API 回應。本版補存 `evidence/r2_repo_metadata.json`，並把**有權限**與**有授權**分開寫。社群渠道能力維持「未知」。
> 3. revision 1 第二節把 #4027 寫成「0.86.1 NOT REPRODUCED」並暗示仍是待辦需求。回報者本人已在 0.86.1 確認消失並關閉，本版改為歷史案例。
> 4. 實測引用改指 r2 manifest；r1 證據檔保留原樣，降為 REPORTED。

---

## 一、成果入口方案

### 現況
來源：`evidence/r2_repo_metadata.json`（2026-09-25T18:20:34Z 以 GitHub MCP `search_repositories` 讀取，保存回應中相關欄位原文；sha256 `ab0416fc…`）。revision 1 的同名表格是當時讀了但沒保存，只能算 REPORTED；本表以 r2 保存的回應為準。

| 項目 | 值 | 證據等級 |
|---|---|---|
| 可見性 | public | OBSERVED（已保存） |
| 授權 | MIT | OBSERVED（已保存） |
| description | 回應中**沒有這個欄位** | 推定未設定，未直接證明 |
| topics | 回應中**沒有這個欄位** | 推定未設定，未直接證明 |
| Discussions | 關閉（`has_discussions: false`） | OBSERVED（已保存） |
| Pages | 關閉（`has_pages: false`） | OBSERVED（已保存） |
| stars / forks | 1 / 0 | OBSERVED（已保存） |

GitHub 預設的 repo 搜尋比對名稱、About 與 topics。About 與 topics 若確實未設定，外部很難透過搜尋發現這個 repo。這與帳本 `handoff.next_checkpoint = OWNER_GITHUB_DISCOVERABILITY_DECISION` 一致，本包不處理那個決定。

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

兩篇都經 GPT R2 覆核關閉條件。**本輪有新事實，發布前應補進去**（本包不改 PR14 檔案，只列清單）：

| # | 要補的 | 依據 |
|---|---|---|
| 1 | 環境變數、`--openai-api-base` 參數、`.aider.conf.yml` 設定檔三種方式，在 0.86.1 都送到 `/v1/chat/completions`；三個 case 由各自的 Host 標頭（port 8851／8852／8853）區分 | r2 manifest `base_path_env_var`／`base_path_cli_flag`／`base_path_config_file` |
| 2 | #4027（0.83.1 上 `/v1` 被吃掉）是**歷史案例**：根因追到 litellm 1.65.7→1.68.0，有修正 PR #4144，回報者 2025-09-19 在 0.86.1 確認重現不出來並自行關閉。**只能寫「曾經發生、0.86.1 已不重現」，不能當現行問題或招募理由** | `evidence/r2_issue_4027_timeline.md`、`SOURCE_AND_GAP.md` 4.1 |
| 3 | 現行需求線索是 #4797、#4638 兩筆「前綴寫成別家 provider」；檢查器對兩個原字串都 exit 3。**不能寫成檢查器已幫到誰** | r2 manifest `checker_issue_*`、`SOURCE_AND_GAP.md` 4.2 |
| 4 | **aider 的 exit code 不能當成功訊號**：端點完全連不上時仍回 0 | r2 manifest `retry_no_server`（exit 0、78.0 秒） |
| 5 | 可重試錯誤每個邏輯呼叫 aider 做 9 次嘗試、總等待約 64 秒（litellm 內部重試未驗證，9 是下限）；設定錯誤不重試 | 同上 ＋ `exceptions.py` |
| 6 | aider 沒有任何限制花費或 token 的參數 | `args.py` 120 個參數中查無 |

---

## 三、發布渠道與帳號能力

**有權限不等於有授權。** 下表「權限」只描述憑證技術上能做什麼，任何動作仍需負責人授權。

| 渠道 | 權限（證據） | 缺什麼 |
|---|---|---|
| 本 repo（README／固定連結） | 本 session 的 GitHub MCP 所用憑證，回應中 `permissions.admin: true`（`evidence/r2_repo_metadata.json`，OBSERVED）。這把憑證屬於誰、範圍多大：**未知** | merge 與 About/topics 的負責人決定 |
| GitHub Discussions | 目前關閉（同上，OBSERVED） | 要開需負責人決定 |
| 上游 Aider（issue／PR） | **未知**，未查。CONTRIBUTING 要求顯著變更先討論，另有 CLA | 發送授權；本包不送 |
| 社群平台（X、Reddit、HN 等） | **未知**。本 session 沒有也不應有任何社群帳號憑證 | 帳號、發送授權、文案審核 |

我沒有、也不去取得任何社群帳號的存取。這幾欄只能由負責人或持有帳號的人確認。

---

## 四、live 呼叫預算：次數、tokens、重試、價格

### 4.1 每個邏輯呼叫幾次付費嘗試（讀碼＋實測）
對可重試錯誤，aider 0.86.1 每個邏輯呼叫做 **9 次嘗試**：

| 嘗試 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 前一次等待(秒) | — | 0.25 | 0.5 | 1 | 2 | 4 | 8 | 16 | 32 |

- 讀碼依據：`models.py:1045-1079`（helper 呼叫）與 `base_coder.py:1449-1487`（主對話），兩處同一套邏輯，`RETRY_TIMEOUT = 60`。照原始碼重算：9 次、總等待 63.75 秒。
- **實測（r2 manifest `retry_no_server`）**：指向關閉的 port，完整去敏命令、版本、開始／結束 UTC 都記在 manifest；stdout 有 8 行 `Retrying in …`；monotonic 牆鐘 78.0 秒；**aider exit 0**。
- aider 沒有設定 litellm 自己的重試參數（`num_retries` 查無）。**litellm 內部是否另有預設重試，未驗證**，所以 9 是下限，不是保證的上限。

### 4.2 哪些錯誤會重試（`exceptions.py` 原表）
| 會重試 | 不重試（立刻失敗） |
|---|---|
| APIConnectionError、APIError、InternalServerError、ServiceUnavailableError、BadGatewayError、**RateLimitError**、**Timeout**、ContentPolicyViolationError、InvalidRequestError、UnprocessableEntityError 等 | **NotFoundError**、**BadRequestError**、**AuthenticationError**、**PermissionDeniedError**、ContextWindowExceededError |

**對預算的意義：**
- 設定錯（404／400／401／403）不重試，立刻失敗，所以設錯很便宜。
- **Timeout 會重試**：如果 provider 已經開始生成而 client 逾時，provider 可能照樣計費。最壞情況下，一個邏輯呼叫可能產生 9 次以上的計費生成。這是依機制推得的可能性，**未實測**。
- **RateLimitError（429）會重試**：如果 provider 用 429 表示「超過花費上限」，aider 會對被拒的請求重試 9 次、約 64 秒才放棄。被拒的請求是否計費，要在 4.6 查證。

### 4.3 除了主對話，還有哪些隱藏呼叫
| 來源 | 觸發條件 | 控制方式 |
|---|---|---|
| commit message（`repo.py:361`） | `--auto-commits` **預設開啟**，每次修改都觸發一次 helper model 呼叫 | `--no-auto-commits` 或 `--no-git` |
| 對話摘要（`history.py:116`） | 歷史超過 `max_chat_history_tokens` | 對話保持短 |
| repo map | `--map-tokens` 預設 `auto`，增加 prompt tokens | `--map-tokens 0` |
| 價格表外連 | 每次啟動，**不計入 provider 費用**（連的是 GitHub） | 無法用參數關閉（PR14 實測） |

PR14 曾實測：`--no-git`、單一 `--message` 的條件下只送出 **1 個**請求。

### 4.4 上限怎麼估（公式，不含價格）
```
每人最少計費嘗試上限 = 邏輯呼叫數 × 9          （litellm 內部重試未驗證，實際可能更多）
邏輯呼叫數          = 主對話回合上限 N ＋ helper 呼叫數（照 4.3 關掉則為 0）
每人 token 估計上限  = 計費嘗試數 × (每次 prompt tokens ＋ 每次 max completion tokens)
每人費用估計上限    = 上面 × 當日單價
```
這是**估計**，不是保護。真正擋住超支的只能是 4.6 查證過的拒絕型上限，或負責人選定並接受殘餘風險的替代方案。
建議受試者流程用 `--no-auto-commits --map-tokens 0`（見 `TRIAL_RUNBOOK.md` P4），並設主對話回合上限 N。N 的數字由負責人連同費用一起核准，本文件不替您定。

### 4.5 當日價格：**缺口，不猜**
- 端點與模型**尚未選定**，所以沒有單價可查。
- 本文件**不寫任何價格數字**，也不去讀任何 key 或帳務頁。
- 核准時的做法：選定端點與模型後，當天從 **provider 官方價格頁**抄下 prompt／completion 單價，連同頁面網址與讀取時間一起記入核准紀錄，再代入 4.4。

### 4.6 費用硬上限：**待查證的能力，不預設存在**
aider 0.86.1 的 120 個 CLI 參數中沒有花費、預算或 token 上限參數，所以費用只能在 aider 外面控制。**選定的 provider 有沒有能用的上限，要先查。**

**步驟一：查官方文件**（每格附網址與讀取 UTC；查不到寫「未知」）

| 要確認的 | 判讀 |
|---|---|
| 上限的範圍：單把 key／project／整個組織 | 只有 key 或 project 級能把本研究隔開；組織級會和其他用量共用 |
| **警報型還是拒絕型** | 警報型只寄通知，後續請求照常計費，**不算上限**。只有「超過後拒絕後續請求」才算硬上限 |
| 超過後回什麼錯誤 | 429 會被 aider 重試（見 4.2）；401／403 不會 |
| 生效延遲 | 用量統計有延遲時，硬上限也可能被超過；文件沒寫記「未知」 |
| 被拒絕的請求是否計費 | 影響 429 重試的成本 |

**步驟二：判定**

| 查到的結果 | 下一步 |
|---|---|
| 有拒絕型、key 或 project 級上限 | 為本研究開獨立 key／project，設上限，研究結束即撤銷 |
| 只有警報型、只有組織級，或查不到 | **不 live**，除非負責人從下面選一個替代方案並書面接受殘餘風險 |

**替代方案**（都不需要新平台）：

| 方案 | 做法 | 殘餘風險（負責人要接受的） |
|---|---|---|
| 1. 預付餘額、關自動儲值 | 餘額就是上限 | 前提「餘額歸零會拒絕請求」也要照步驟一查證；同組織其他用量共用餘額 |
| 2. 回合上限＋錯誤即停（人工） | 主對話最多 N 回合；同一回合出現第 3 行 `Retrying in` 即 Ctrl-C（`TRIAL_RUNBOOK.md` G0） | 人工控制，會有反應延遲；按下前已發生的嘗試；litellm 內部重試未驗證 |
| 3. 不 live | 停在離線步驟 | 第一階段無法開始 |

---

## 五、需要負責人決定的事（依順序；前一關沒過，後面不做）

| 關卡 | 內容 | 誰做 | 本文件已備妥的材料 |
|---|---|---|---|
| 0 | 研究修正版通過獨立覆核（PR16） | GPT reviewer | — |
| 1 | 選定端點、模型、provider | 負責人 | 4.5 的查價做法 |
| 2 | **查證該 provider 的上限能力**（4.6 步驟一），附官方來源 | 研究者查、負責人確認 | 4.6 查核表 |
| 3 | 依關卡 2 結果：設拒絕型上限，或選替代方案並書面接受殘餘風險，或不 live | 負責人 | 4.6 步驟二、替代方案表 |
| 4 | 每人回合上限 N、總費用上限 | 負責人 | 4.4 公式、4.1 的 9 倍（下限）係數 |
| 5 | 第一階段招募渠道與對象（1–3 人，只走路徑 B） | 負責人 | 第三節（除本 repo 外全部未知）；`STUDY_PROTOCOL.md` 第五節 |
| 6 | PR14 是否合併（決定固定入口） | 負責人 | 第一節 |
| 7 | 草稿發布前是否補上第二節六項 | 負責人 | 第二節清單 |

關卡 1–4 全部完成前，任何 [LIVE] 步驟都不做。關卡 5–7 各自獨立，但都是對外動作，需要各自的授權。

# ATK distribution executor response

> 合併注意：本檔在 main 上尚不存在。PR14（`claude/atk-aider-first-use-01`）也新增了同名檔案。兩個 PR 都合併時此檔會衝突，應保留兩段，不互相覆蓋。本分支刻意不帶入 PR14 的內容，以免把 PR14 的變更混進本 PR。

---

# ATK-VALUE-READINESS-01 · revision 1

| | |
|---|---|
| work_id / revision | `ATK-VALUE-READINESS-01` / 1 |
| source main | `60dbdff09d14da493ee0d65de364a9b72e7b8321`（state revision 35，決策 ATK-FULL-BLUEPRINT-20260926） |
| Aider 固定來源 | PR14 head `d1474670db12934c80caa05674c8e4320cbad312` |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:ATK-VALUE-READINESS-01:1:60dbdff09d14da493ee0d65de364a9b72e7b8321:executor` |
| session | `session_01RFeCsTYkVywjHvXk7od7Ab` |
| claim | 2026-09-25T17:04:26Z 起，UTC 期限 **2026-09-26T17:04:26Z** |
| 分支 | `claude/atk-value-readiness-01`（自 `60dbdff` 開） |
| 派工依據 | 藍圖第 8 節完整契約；負責人 2026-09-25 明確指示「讀所有規劃，把細節往下執行」 |
| 重複檢查 | 無同名分支；open PR 共 13 個，無本 work_id；main 上無 `research/adoption/` |

## 交付五項
| # | 檔案 | 內容 |
|---|---|---|
| 1 | `research/adoption/aider/SOURCE_AND_GAP.md` | 官方直用 vs PR14 逐項差距；公開需求與反例；差距裁決與反證 |
| 2 | `research/adoption/aider/STUDY_PROTOCOL.md` | 兩條路徑、固定版本、成功／失敗分類、計時起迄、協助與費用、順序效應、最低有用差異規則、停止準則；資料表空白並標 NOT COLLECTED |
| 3 | `research/adoption/aider/TRIAL_RUNBOOK.md` | 研究者準備 → 受試者流程 → 再次使用，每步標 [OFFLINE]／[LIVE]／[EXTERNAL] |
| 4 | `research/adoption/aider/RELEASE_AND_ACCESS_PACKET.md` | 固定入口方案、兩篇草稿需補五項、渠道能力、live 呼叫／tokens／重試／價格上限公式 |
| 5 | 本段 | — |

## 本輪新增、可回查的事實

**一、公開反例 #4027 在 0.86.1 NOT REPRODUCED。**
Aider-AI/aider #4027 回報 0.83.1 用設定檔時 `/v1` 被吃掉、回 404。PR14 只用環境變數量過，這個矛盾原本解不開。本輪在 0.86.1 對三種設定方式各錄一次：

```
case=env_var     aider_exit=0 observed_path=/v1/chat/completions
case=cli_flag    aider_exit=0 observed_path=/v1/chat/completions
case=config_file aider_exit=0 observed_path=/v1/chat/completions
```
三個證據檔 md5 都是 `b3146320c885087079c005872e10fded`。**不是同一份檔複製三次**：紀錄只含 path、model、stream、message_count、authorization_header_present，不記埠號，相同觀察產生逐位元組相同的檔案。
沒找到修正 commit，所以只寫「0.86.1 重現不出來」。

**二、重試次數從讀碼推論升為實測。**
對不存在的端點跑一次：`Retrying in` 8 行、間隔 0.2(=0.25)/0.5/1/2/4/8/16/32 秒、牆鐘 79 秒 → **每個邏輯呼叫 9 次嘗試**，與照原始碼的模擬（9 次、63.75 秒）一致。證據 `evidence/retry_no_server_stdout.txt`，md5 `8089a8d7ac258c0bb2926bf09134a94d`。

**三、aider exit code 不能當成功訊號。**
上面那次 9 次嘗試全部失敗，aider 仍回 exit 0。runbook 與研究設計都改成只看評分測試與測試檔 md5。

**四、哪些錯誤會重試。** `exceptions.py` 原表：設定錯（NotFound、BadRequest、Authentication、PermissionDenied）不重試、立刻失敗；RateLimit、Timeout、5xx、連線錯誤會重試。**Timeout 可重試意味著最壞可能有 9 次計費生成**，這是依機制推得，未實測。

**五、aider 沒有任何花費／token 上限參數。** `args.py` 120 個 `add_argument` 中查無。費用硬上限只能在 provider 端設。

**六、helper model 的觸發點。** commit message（`repo.py:361`，`--auto-commits` 預設開）與對話摘要（`history.py:116`）。runbook 建議 `--no-auto-commits --map-tokens 0`。

## 一個失敗的中間步驟，照實記
第一輪三個 case 全部 `NO_REQUEST_LOG`：本分支從 main 開，PR14 未合併，假伺服器檔不存在，伺服器沒起來。改成從 PR14 固定 head 用 `git show` 唯讀取出兩個檔（md5 `a26adf4c…`、`da2b54d9…`），並在每個 case 前先確認伺服器程序活著，才得到上面的結果。**第一輪不採用。**

## 用過的命令（節錄）
```
git show d1474670…:integrations/aider-atk/fake_openai_server.py   # 唯讀取固定資產
git show d1474670…:integrations/aider-atk/sample/import_contacts.py
aider 0.86.1 --model openai/local-test-model --no-git --yes --no-check-update
             --no-analytics --no-show-model-warnings --exit --message ok
  × {OPENAI_API_BASE env, --openai-api-base, --config .aider.conf.yml}
grep -n '"--' aider/args.py ; sed -n 1030,1085p aider/models.py ; sed -n 10,56p aider/exceptions.py
```
所有 aider 執行都對 127.0.0.1 的假端點，金鑰為 placeholder，**無任何真實 provider 呼叫、無費用**。

## 未測
真實模型、任何費用、Windows／macOS、Continue 與 Open WebUI 的同類問題、0.83.1 到 0.86.1 的程式差異、litellm 內部預設重試、任何社群帳號能力、任何受試者。

## 下一階段
**已備妥**：研究設計、runbook、預算公式、固定入口方案、草稿更新清單。
**缺的都是負責人決定**（`RELEASE_AND_ACCESS_PACKET.md` 第五節）：端點與模型、回合與費用上限、provider 端獨立 key、PR14 是否合併、草稿發布、招募渠道。

## 邊界
未改 PR14 任何檔案或證據 · 未執行未知第三方程式（aider 為 PR14 已覆核之固定對象，僅對本機假端點執行）· 未做任何 live 呼叫 · 未發布 · 未邀請 · 未 merge · 未部署 · 未讀寫 secrets · 未改權限 · 未新增費用。
`findings_closed_by_executor: []`。停在 Draft PR 等獨立覆核。

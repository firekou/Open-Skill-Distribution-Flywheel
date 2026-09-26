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

---

# ATK-VALUE-READINESS-01 · revision 2

| | |
|---|---|
| work_id / revision | `ATK-VALUE-READINESS-01` / 2 |
| 依據 | `reviews/PR16_R1_VALUE_READINESS_57fa5090.md`（BLOCKED，P1-01～P1-04），main `2c03054874321374869d0edd6bf8c2d051182746` 上的 `reviews/CLAUDE_NEXT_PROMPT_ATK_DISTRIBUTION.md` §3 |
| source_head | `57fa50900035cb6eef316504b065cf98a8b4fee0` |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:16:ATK-VALUE-READINESS-01:2:57fa50900035cb6eef316504b065cf98a8b4fee0:executor` |
| repair_round | 1/2 |
| session | `session_01RFeCsTYkVywjHvXk7od7Ab` |
| claim | 覆核於 2026-09-25T17:21:27Z 進 main；本輪第一個 r2 檔寫入 2026-09-25T18:10:51Z。沒有另外記下更早的接單時刻，所以期限從最早可能接單時刻起算，偏保守：UTC 期限 **2026-09-26T17:21:27Z** |
| 範圍 | PR16 原九個路徑＋`research/adoption/aider/evidence/` 新增 manifest／raw metadata；未改 PR14 |

## 逐項回覆

### P1-01：#4027 與現行需求
**同意 finding。revision 1 的判讀錯了。**
- 錯在哪：revision 1 用 WebFetch 擷取 #4027，只拿到 issue 本文，時間線與五則留言沒載入，我沒察覺缺了東西，就寫下「未見維護者回覆或修正 PR」，還把它當成現行需求。
- 本輪做法：改用 Exa `web_fetch_exa` 取完整頁面，原文節錄存 `research/adoption/aider/evidence/r2_issue_4027_timeline.md`（sha256 `0757b1115df3e7e252e2a92a45da3277584ea28f6ad6b9d1d2983250aa34765b`）。GitHub API 對 Aider-AI/aider 回 403，因為這個 repo 沒掛到本 session；工具說明要求不主動加未授權的 repo，所以沒加。
- 改寫：`SOURCE_AND_GAP.md` 4.1 列完整時間線（litellm 1.65.7→1.68.0 根因、PR #4144、維護者加 `priority` 標籤、回報者 2025-09-19 在 v0.86.1 確認不重現並自行關閉），分類為**已解決的歷史設定失敗案例**，明寫不能當現行缺陷或未解需求。
- 現行需求：3 組定向查詢（不是系統性搜尋），納入 2 筆仍開放、版本 0.86.1 的線索 #4797、#4638，都屬「前綴寫成別家 provider」；排除 9 項並附理由。第三類（根位址帶路由）**現行需求記 0**。檢查器對兩筆原字串都 exit 3（r2 manifest `checker_issue_4797_zai`、`checker_issue_4638_local`），但**沒有任何回報者用過它**，#4638 的人最後走 Ollama 原生（我們不涵蓋），#4797 有人照 `openai/` 做仍失敗。增量維持假說。
- `RELEASE_AND_ACCESS_PACKET.md` 第二節第 2 項同步改為歷史案例。

### P1-02：1–3 人設計回答不了增量問題
**同意 finding。採修正方案 1，並寫下進入方案 2 的條件。**
- `STUDY_PROTOCOL.md` 改為兩階段。第一階段 1–3 人、**只走路徑 B**，只回答能否完成、卡在哪、要多少協助、有沒有 F-PATH；明寫不產出比較結論。
- 第二階段進場條件（全部成立才開始）：任務 2 存在且結構對等（同改動類型、同 5 個評分情境、待改檔行數差 ≤20%、固定測試與 md5、baseline 部分失敗）；第一階段至少 1 人完成；最低有用差異事前 commit；live 授權涵蓋第二階段。
- 第二階段設計：甲組 A＋任務1 → B＋任務2，乙組 B＋任務1 → A＋任務2；逐人差值，報中位數與範圍，不算 p 值。MLD 公式與理由寫在第七節。
- **本輪不建任務 2**：等難度在沒有資料前無法宣稱，只寫規格與事後檢查方式（兩任務完成時間差 >50% 視為不等難度、停止比較）。
- 新增 F-PATH 失敗代碼與能力背景欄位；資料表全部 NOT COLLECTED。`TRIAL_RUNBOOK.md` 同步移除 A/B/A 分配。

### P1-03：證據綁定不足
**同意 finding。原始資料只有 r1 的輸出檔，沒有命令／時間／exit 的原始紀錄，所以重跑離線 case，並把 r1 檔降級。**
- 新 harness：`research/adoption/aider/evidence/r2_harness.py`（sha256 `085ee1ed3156cb72ddedfa0527e2c47f49bb4c0f6ceee7fc4a7a0831a0a1fbf6`）。從 PR14 固定 head `d1474670` 用 `git show` 唯讀取 fixture 並記 hash；用 harness 自己的記錄伺服器，每個 case 各自一個 port，記 path、Host 標頭、model、stream、是否有 auth 標頭；每個 case 前確認 port 已就緒（retry case 確認是關閉的）。
- 產出：`research/adoption/aider/evidence/r2/manifest.json`（sha256 `6ae2e714b3a5caef40d8c9f482a1e594af1f67c40192480a133b214e02a3b558`）＋15 個原始輸出檔。每個 case 記 start/end UTC、monotonic 時長、exit code、去敏命令（金鑰寫 `<PLACEHOLDER_KEY>`）、設定檔全文、stdout／stderr／request 檔的 sha256、版本（aider 0.86.1、litellm 1.75.0、openai 1.99.1、httpx 0.28.1、Python 3.11.15）。

| case | exit | 時長(秒) | 觀察到的 path | Host 標頭 |
|---|---|---|---|---|
| base_path_env_var | 0 | 3.015 | `/v1/chat/completions` | `127.0.0.1:8851` |
| base_path_cli_flag | 0 | 2.760 | `/v1/chat/completions` | `127.0.0.1:8852` |
| base_path_config_file | 0 | 2.973 | `/v1/chat/completions` | `127.0.0.1:8853` |
| retry_no_server | 0 | 78.024 | （無，port 關閉）；`Retrying in` 8 行 | — |
| checker_issue_4797_zai | 3 | 0.012 | — | — |
| checker_issue_4638_local | 3 | 0.011 | — | — |

- 三個 base-path case 的 request 檔現在內容不同（sha256 開頭 `637de800…`／`3fedf6e7…`／`1be99f87…`），因為各記了不同的 Host 標頭，能區分是三次獨立執行。
- r1 的 `evidence/base_path_{env_var,cli_flag,config_file}.json` 與 `evidence/retry_no_server_stdout.txt` **保留原樣不改**，manifest 的 `supersedes` 欄記它們被哪個 r2 case 取代，文件中降為 REPORTED。r1 牆鐘「79 秒」改用 r2 的 78.0 秒（monotonic）。
- 請 reviewer 判斷：`r2_harness.py` 是程式，不是資料；我把它放在 evidence 目錄是為了讓 manifest 能被重跑核對。若認為超出「manifest/raw metadata」範圍，可要求移除，manifest 仍可獨立閱讀。

### P1-04：費用硬上限與執行就緒寫得太確定
**同意 finding。**
- `RELEASE_AND_ACCESS_PACKET.md` 4.6 改為「待查證的能力」：provider 選定後查官方文件的範圍（key／project／組織）、**警報型或拒絕型**、超限錯誤碼、生效延遲、被拒請求是否計費；查不到寫「未知」。只有拒絕型、key 或 project 級才算硬上限。
- 補一條讀碼事實：aider 對 429 RateLimitError 會重試（`exceptions.py`），若 provider 用 429 表示超限，aider 會對被拒請求再試約 64 秒。
- 沒有硬上限時：不 live，除非負責人選替代方案並書面接受殘餘風險。替代方案都不需要新平台：預付餘額關自動儲值（前提也要查證）、回合上限＋錯誤即停（人工，明寫不是硬限制）、不 live。
- 第五節改為有順序的關卡：覆核通過 → 選 provider → 查上限能力 → 設上限或選替代方案 → 回合與費用上限 → 其後才是招募、PR14 合併、草稿發布。刪掉「簽了就能開始」。
- `TRIAL_RUNBOOK.md` 新增 G0 費用控制閘門，G0 沒過，所有 [LIVE] 步驟不做。
- GitHub 權限：這次保存了 API 回應 `research/adoption/aider/evidence/r2_repo_metadata.json`（2026-09-25T18:20:34Z，GitHub MCP `search_repositories`；sha256 `ab0416fce1bd42b6baf014f50b6bf040a800c29ad8da5fdb798ae4cea4bdbc63`）。回應中 `permissions.admin: true`，描述的是 MCP 所用憑證；**憑證屬於誰、範圍多大記「未知」**，並寫明有權限不等於有授權。description 與 topics 在回應中沒有這兩個欄位，只寫「推定未設定，未直接證明」。上游 Aider 與社群平台能力記「未知」。

## 本輪命令（節錄）
```
python3 research/adoption/aider/evidence/r2_harness.py     # 產生 r2/ 與 manifest.json
mcp Exa web_fetch_exa https://github.com/Aider-AI/aider/issues/4027
mcp Exa web_search_exa  (Q2, Q3；查詢字串見 SOURCE_AND_GAP.md 4.2)
mcp github search_repositories "repo:firekou/Open-Skill-Distribution-Flywheel"
```
所有 aider 執行都對 127.0.0.1，金鑰為 placeholder，**無真實 provider 呼叫、無費用**。

## 未測（新增或仍未測）
真實模型與費用；任何 provider 的上限能力（還沒選 provider）；litellm 內部預設重試；PR #4144 是否合併、修正落在哪一層；Ollama 原生路線；Windows／macOS；任何受試者；任務 2。

## 邊界
未改 PR14 · 未做 live 呼叫 · 未招募 · 未發布 · 未 merge · 未部署 · 未讀寫 secrets · 未改權限 · 未新增費用 · 未發上游訊息。
`findings_closed_by_executor: []`。P1-01～P1-04 是否關閉由獨立 reviewer 判定。交 reviewer 後停止本批。

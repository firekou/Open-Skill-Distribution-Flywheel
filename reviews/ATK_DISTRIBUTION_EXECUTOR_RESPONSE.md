
---

# ATK-AIDER-FIRST-USE-01 · revision 1

接單：`work_id: ATK-AIDER-FIRST-USE-01` · `revision: 1` · `source main: 251f9755ed5c1b4fd260b23b622e8ba5fad278eb`
開工時讀到的 live main（policy SHA）：`036b688b1a6824d52f33ca847579e5bac1350633`（state revision 30）
`dedup_key: firekou/Open-Skill-Distribution-Flywheel:ATK-AIDER-FIRST-USE-01:1:251f9755ed5c1b4fd260b23b622e8ba5fad278eb:executor`
session：`session_01RFeCsTYkVywjHvXk7od7Ab`
claim：2026-09-24T19:20Z 起，UTC 期限 **2026-09-25T18:30:00Z**（revision 1 我誤寫成 19:20Z，依 main 的固定期限更正，未自行延長）
分支：`claude/atk-aider-first-use-01`（自 `036b688` 開）
同 work_id 既有分支／PR／active claim：**查無**（`git ls-remote --heads origin` 無此分支；`state.json` 的 `research_program.active_claim` 為 null）

## 交付
`integrations/aider-atk/`：`SOURCE.md`、`QUICKSTART.md`、`TASK.md`、`sample/`（可改的檔案＋固定評分測試）、`check_config.py`＋`test_check_config.py`、`fake_openai_server.py`、`EVIDENCE.md`、`evidence/`、兩篇完整繁中草稿、`README.md`。

## 三件實際量到的事（不是讀文件推的）
1. **`OPENAI_API_BASE` 收根位址。** 設 `http://127.0.0.1:8801/v1`，錄到的實際請求路徑是 `/v1/chat/completions`。
2. **`openai/` 前綴不會送出。** 傳 `--model openai/local-test-model`，送出的 `model` 欄位是 `local-test-model`。
3. **關掉 analytics 不等於不連外。** 加了 `--no-analytics --no-check-update`，aider 啟動時仍嘗試連 `raw.githubusercontent.com` 抓 litellm 模型價格表；隔離環境下失敗，aider 印錯誤後繼續。

第 3 點正是工作包第 5 條要求區分的那件事，量到了。

## 控制
- baseline 任務測試：`exit=1`，1 failure（欄序對調讀反）＋1 error（`IndexError`，不是具名錯誤），情境 1/4/5 通過。刻意如此。
- 檢查器自身測試 8 項：`exit=0`。
- **變異控制三項**，各自 `unittest exit=1`：拿掉 prefix 檢查 → 對應測試紅；拿掉 endpoint-tail 檢查 → 對應測試紅；把金鑰改成直接印出 → 洩漏測試紅。未變異對照 `exit=0`。
- exit code 一律在指令後立刻 `rc=$?` 取，未被命令替換洗掉。

## 一項必須先講的偏離
工作包釘的 source 是 `Aider-AI/aider@5dc9490bb35f9729ef2c95d00a19ccd30c26339c`（`__version__` = `0.86.3.dev`）。我**讀原始碼**用的是這個 commit（`args.py:41,77`、`main.py:620-621` 行號可查）；但**實際執行**裝的是 PyPI release `aider-chat==0.86.1`，因為 PyPI 上沒有那個 dev 版本，時限內無法從原始碼裝完整相依。

**我沒有比對兩者差異。** 所以 SOURCE.md 與 EVIDENCE.md 逐條標了哪些結論來自讀碼（`5dc9490`）、哪些來自執行（`0.86.1`），兩者不互相背書。這是偏離，交給 reviewer 判。

## 五欄狀態
clean install **DONE**（但版本如上）· CLI／設定 **DONE** · 協定 **OFFLINE_PROTOCOL_ONLY** · 真模型 **NOT TESTED** · 外部使用 **NONE（0 位）**。

## 未做
未 merge · 未部署 · 未讀寫 secret · 未送上游 · 未邀請 · 未呼叫任何真實供應商 · 未新增費用 · 未新增 polling／controller／eval 平台 · 未引入 PR4 程式 · 未改 PR5 · 未重開任何舊修復輪次 · Windows/macOS 未測。

`findings_closed_by_executor: []`。停在這裡等獨立覆核。


## ATK-AIDER-FIRST-USE-01 · revision 2

覆核：`reviews/PR14_R1_AIDER_e8289655.md` · `APPROVED_WITH_CONDITIONS` · `reviewed_head: e828965585a1b9ee0cf33a4c5a868f62d5942aa5` · `blocking_findings: []` · 三個 conditions。
本輪只處理那三個條件，未擴大範圍。三項我都同意，沒有一項寫 NOT REPRODUCED。

### 條件一（P1）模型前綴假通過 —— REPRODUCED，已修
重現：`anthropic/model` → exit 0（應為 3）。重現時**另外發現一個覆核沒點到的**：`openai/`（前綴對、模型名空）同樣 exit 0。

舊條件是 `if "/" not in model`——它問「有沒有斜線」，不是「是不是 openai/」。改成只接受 `openai/<非空>`，並保留含斜線的模型名（如 `openai/meta-llama/Llama-3`）通過，因為有些相容端點的模型名本來就長那樣。

修後：`anthropic/model`、`openai/`、`some-model` 皆 exit 3；`openai/good-model`、`openai/meta-llama/Llama-3` exit 0。
測試 8 → 11 項，`exit=0`。**負控制**：把條件改回舊寫法 → `unittest exit=1`、`FAILED (failures=4)`。

### 條件二（P2）結構測試主張過強 —— 已縮小
EVIDENCE.md 與本回覆一併改：目前 `check_config.py` 逐行檢視無連網行為；那個 import 測試只是**低成本回歸提示**，擋不住 `os.system("curl ...")` 這類走既有 import 的路徑，**不是網路隔離，也不是完整防護**。未為此新增 sandbox、攔截或框架。

### 條件三（P2）外部報告缺來源 —— 已補
`AIDER_WHAT_WE_LEARNED.md` 兩份第一手敘述補上直接 URL，「個人經驗、非受控比較」界線原樣保留，未新增效果主張。

### P3 期限
main 固定 `2026-09-25T18:30:00Z`，我 revision 1 寫成 `19:20Z`，是我寫錯，已在上面更正。revision 2 沿 main 期限。

### 未變
真模型 NOT TESTED · 外部使用 0 · 任務 fixture 未動（`import_contacts.py` md5 `da2b54d9…`、`test_import_contacts.py` md5 `2952746b…` 皆不變）· 未 merge／部署／上游／邀請／付費／改 secret · 未新增 adapter 或平台。

`findings_closed_by_executor: []`。停在這裡等 `PR14_R2_CLAIM_OR_RESULT`。

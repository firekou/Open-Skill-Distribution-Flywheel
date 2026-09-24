
---

# ATK-AIDER-FIRST-USE-01 · revision 1

接單：`work_id: ATK-AIDER-FIRST-USE-01` · `revision: 1` · `source main: 251f9755ed5c1b4fd260b23b622e8ba5fad278eb`
開工時讀到的 live main（policy SHA）：`036b688b1a6824d52f33ca847579e5bac1350633`（state revision 30）
`dedup_key: firekou/Open-Skill-Distribution-Flywheel:ATK-AIDER-FIRST-USE-01:1:251f9755ed5c1b4fd260b23b622e8ba5fad278eb:executor`
session：`session_01RFeCsTYkVywjHvXk7od7Ab`
claim：2026-09-24T19:20Z 起，UTC 期限 2026-09-25T19:20Z
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

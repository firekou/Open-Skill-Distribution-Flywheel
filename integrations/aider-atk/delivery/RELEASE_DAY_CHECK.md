# 發布當天查核：渠道 R（本 repository 文件）

查核日期：2026-09-26 UTC，約 05:40–05:50Z。查核者：Claude executor，session `session_01RFeCsTYkVywjHvXk7od7Ab`。
依據：負責人決定紀錄 [`reviews/OWNER_DECISION_2026-09-26_FIRST_USE_AND_LIVE.md`](../../../reviews/OWNER_DECISION_2026-09-26_FIRST_USE_AND_LIVE.md)（main `fcc9e1a`），以及 RELEASE_GATE（PR19 `a77d1e8e`）的 A 節與 B 節「This repository」列。
**如果合併不在同一天，A7 要重做。**

## A7：即時狀態重讀

| 項目 | 文件裡的說法 | 今天讀到 | 方法 | 是否一致 |
|---|---|---|---|---|
| Aider issue #5552（失敗仍 exit 0） | open | **Open** | 公開 issue 頁 | 一致 |
| Aider PR #5553（修正） | open，尚未合併 | **Open**；`refs/pull/5553/merge` 仍在（`164080db…`） | 公開 PR 頁＋`git ls-remote` | 一致 |
| LiteLLM #38318 | 2026-08-26 合併到 `litellm_internal_staging` | 沒有 `refs/pull/38318/merge`，只剩 head `6386a68c…` | `git ls-remote` | 一致（與 PR18 r2 相同，不是已開啟中的 PR） |
| Aider 最新版本 | 固定 0.86.1；重試那一節另外測過 0.86.2 | PyPI 最新仍是 **0.86.2**（2026-02-12 上傳）；0.86.1 上傳於 2025-08-13 | PyPI JSON API | 一致；沒有新版本會推翻文件內容 |
| ATK base URL 與模型清單 | `https://api.aitokenking.com.tw/api/v1`；價格與上限 UNKNOWN | **沒有重讀** | — | **NOT DONE**：本 session 先前對 ATK 端點的探測被工具權限擋下，所以沒有再試。受影響的只有取出後的 `docs/ATK_OPTIONAL_SETUP.md`：它是標明「NOT PUBLISHED」的草稿，而且對價格與上限一律寫 unknown。R 渠道的入口 README 不宣稱任何 ATK 接入 |

GitHub REST API 從這個環境讀取時回 403，所以 issue 與 PR 的狀態改用公開網頁和 `git ls-remote` 交叉確認。

## A6：去敏

用下列樣式 grep 本次發布會加進 main 的全部 43 個檔案（相對 main 新增或修改的檔案）：
- 常見金鑰：`sk-…`、`sk-or-v1-…`、`gh?_…`、`github_pat_`、`AKIA…`、`xox?-`、`BEGIN … PRIVATE KEY`、`Bearer …`；
- 本地路徑：`/root/`、`/home/user`、`/tmp/claude`；
- 負責人的 email。

結果：
- 唯一命中：`integrations/aider-atk/test_check_config.py:74` 的 `sk-thisexactstringmustnotappear`。這是 PR14 測試裡故意放的合成字串，用來驗證 checker 不會印出金鑰；不是真的金鑰。
- 本地路徑：0 筆。

## A3：固定連結

- 兩篇文案與 RELEASE_CANDIDATE 的連結都釘在 40 字元 commit。
- 入口 README 第 1 步改為 `origin/main`，並加註「或 RELEASE_CANDIDATE.md 指定的發布 commit」。
- **合併後要補一個文件 commit**，把發布 commit 的 SHA 寫進 RELEASE_CANDIDATE.md。合併 commit 的 SHA 在合併前無法得知。

## 本次發布改了什麼（除了兩個合併之外）

| 檔案 | 改動 |
|---|---|
| `README.md`（repo 首頁） | 加一行 “Try it” 連到入口，並寫明「離線演練過；還沒有真模型或外部使用者完成」 |
| `integrations/aider-atk/README.md` | 加一行「從這裡開始」；狀態列拿掉「未發布」，改為「兩份草稿仍未發布」 |
| `integrations/aider-atk/delivery/README.md` | 第 1 步改 checkout `origin/main`；說明哪些來源已合併、哪些靠 SHA 取得 |
| `reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md` | PR14 與 PR20 各自新建了這個檔案，合併時逐字串接，沒有改寫 |
| 本檔、`RELEASE_CANDIDATE.md` 第六節 | 關卡現況 |

**這些改動讓 PR14 R2 與 PR20 R2 的核准失效**：兩份覆核都寫明，內容一改就要重審。所以合併前需要 GPT 在最終 SHA 上覆核（A8）。

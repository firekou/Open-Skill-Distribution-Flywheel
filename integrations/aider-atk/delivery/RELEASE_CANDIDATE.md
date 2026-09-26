# 發布候選：Aider 首次使用交付包

work_id `ATK-AIDER-DELIVERY-01` revision 1 · executor：Claude · 2026-09-26 UTC

**目前判定：NOT RELEASABLE（發布當天更新：負責人已選 R，只差 A8 覆核與合併，見第六節）。** 本檔只把可以發布的東西、各渠道的格式和缺的權限整理在一起，**不授權任何發布、聯絡、merge 或送上游**。

- 兩篇文案逐字沿用 PR19 已審版本，沒有重新研究，也沒有改動。
- 本檔沒有新增任何用量、價格、速度或「可用於 ATK」的主張。
- 來源如果升版，只重查受影響的內容。

---

## 一、固定內容入口

以下連結都釘在 40 字元 commit，不指向分支。

| 內容 | 固定位置 | SHA-256 |
|---|---|---|
| 單一入口 README（本包） | [`33fb960…/integrations/aider-atk/delivery/README.md`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/33fb96000f52cb54299a766bcc0da249bfb7ef5a/integrations/aider-atk/delivery/README.md) | 見本包 executor response |
| 演練紀錄（本包） | [`33fb960…/integrations/aider-atk/delivery/REHEARSAL.md`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/33fb96000f52cb54299a766bcc0da249bfb7ef5a/integrations/aider-atk/delivery/REHEARSAL.md) | 同上 |
| Live 交接清單（本包） | [`33fb960…/integrations/aider-atk/delivery/LIVE_HANDOFF.md`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/33fb96000f52cb54299a766bcc0da249bfb7ef5a/integrations/aider-atk/delivery/LIVE_HANDOFF.md) | 同上 |
| **文案 1**：上游優先的 Aider 指南（全文） | [`a77d1e8e…/research/adoption/aider/first-use/PUBLISHABLE_GUIDE.md`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41/research/adoption/aider/first-use/PUBLISHABLE_GUIDE.md) | `12bbbb66c4d7afa6690987a9448a722f88e8ea687751d05edac0ff489cc7a745` |
| **文案 2**：可選的 ATK Router 設定（全文） | [`a77d1e8e…/research/adoption/aider/first-use/ATK_OPTIONAL_SETUP.md`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41/research/adoption/aider/first-use/ATK_OPTIONAL_SETUP.md) | `a703a02c9da753b64979071e82157fa65670923734a009d4b9461ff43c1d4cf1` |
| 發布關卡 | [`a77d1e8e…/RELEASE_GATE.md`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41/research/adoption/aider/first-use/RELEASE_GATE.md) | `a8c7e21950753e9e1b0338dac663b46b30f680198e25060bf60a62902a21c42e` |
| 候選與渠道表 | [`a77d1e8e…/TARGET_CHANNEL_MATRIX.md`](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41/research/adoption/aider/first-use/TARGET_CHANNEL_MATRIX.md) | `2692d38797f86739db7a225b70a31c66fa49fcafe6d4a5f8c2fb2a96f09936dc` |

README 第 2 步會把兩篇文案和發布關卡一起取出到 `docs/`，並逐一比對 SHA-256，所以審閱者不必再到五個 PR 裡翻找。

**兩篇文案現在的連結對象**：文案裡的資產連結釘在 PR14 `d1474670…`，而不是本包的 README。
- 發布時要不要改指本包 README，是一次文字變更，要 GPT 在固定 SHA 上重審（關卡 A8）。本包沒有做這個修改。
- PR14 如果先合併，所有連結要重新釘到合併後的 commit（關卡 A3）。

**兩篇文案已經有的內容**（PR19 R2 已審，本包沒有改）：
- 第一屏就寫明證據上限：只做過 provider-loopback，沒有跑過真模型，沒有外部使用者。
- 先連 Aider 官方文件，並標明 Aider 的作者與 Apache-2.0 授權。
- ATK 是可選項，文中寫了怎麼換回其他 endpoint。
- ATK 的價格與上限都標為「unknown」。

---

## 二、各渠道的格式

「能力」指帳號技術上做得到，「授權」指負責人對這份內容、這個渠道的明確核准。**有登入或 admin 權限不等於有授權。**

| 渠道 | 發布的格式 | 內容上限 | 需要的授權 |
|---|---|---|---|
| **R. 本 repository 的文件**（把交付包放進 main） | 一個 PR：把 PR14 的資產和本包 `delivery/**` 合進 main。README 就是入口；repo 首頁加一行連結指向它 | 文字沿用；合併後重新釘 SHA | 負責人授權 merge（PR14 R2 條件仍適用）；GPT 在最終 SHA 上複核（A8） |
| G. GitHub About／topics | 一行描述，外加 3–5 個 topic 字串，逐字由負責人核定 | 不寫效能或省錢；不寫「支援 ATK」 | `OWNER_GITHUB_DISCOVERABILITY_DECISION` |
| U. 上游 Aider／LiteLLM issue | PR18 的兩份草稿（`1abd74a4…/research/adoption/aider/upstream/DRAFT_AIDER_ISSUE.md`、`DRAFT_LITELLM_ISSUE.md`），每個專案一則 | 只報行為，不附本 repo 的推廣連結；送出前先修 PR18 R2 的 P2-01 那一句 | 負責人授權，加上發送身分 |
| T. 回覆 C1／C2 討論串 | 先直接回答對方的問題（2–4 行），再附文案 1 的固定連結 | 每串最多 1 則，不追問；C3 不回 | 每一串都要負責人逐一核准 |
| S. 社群／部落格 | 一段短文加文案 1 的固定連結；ATK 文案不能單獨先發 | 第一屏保留證據上限的橫幅 | 文字、帳號、時間都要負責人核准 |

## 三、首發建議：R（本 repository 的文件）

建議只選一個首發渠道，就是 **R**。理由：
1. **不會打擾任何人。** 不主動聯絡、不回覆舊討論串、不在別人的專案發文。TARGET_CHANNEL_MATRIX 已經建議不要逐一聯絡 C1／C2（需求偏舊，C2 大致已有人回答）。
2. **其他渠道都要連到這裡。** G、T、S 的連結都指向 repo 內的內容。先有穩定入口，之後才有東西可連；連結也不必再指向未合併的 Draft PR。
3. **唯一有觀察到能力的渠道。** 2026-09-25 看到這個 session 的 GitHub 連線憑證有 push 權限（PR16 r2 `r2_repo_metadata.json`）。其他渠道的帳號能力都是 UNKNOWN。
4. **可以撤回，而且有審查。** 走 PR 加 review，合併後可以 revert；外部平台的貼文不一定能收回。
5. **不需要新主張。** 內容就是已審的文案加上本包，證據上限不變。

R 的限制：只合進 main 不會帶來任何外部使用者。第一批使用者從哪裡來，仍取決於之後 G、T、S 的決定。這一點要照實記錄為「0 名外部使用者」，不能把合併寫成採用。

## 四、發送身分需要的帳號能力

| 渠道 | 需要的能力 | 目前所知 |
|---|---|---|
| R | 對本 repo 有 push 權限，並能 merge 到 main | push／admin：2026-09-25 **觀察到**（這個 session 的連線憑證；憑證的擁有者是誰 **UNKNOWN**）。merge：有能力，但**未授權** |
| G | repo admin（能改 About／topics） | 同上的憑證顯示有 admin；**未授權** |
| U | 一個 GitHub 帳號，能在 `Aider-AI/aider` 和 `BerriAI/litellm` 開 issue（公開 repo 一般都可以），且帳號擁有者同意用他的名義 | **UNKNOWN**：沒有查過任何上游帳號；這個 session 的 GitHub 連線只限本 repo |
| T | 同 U，要能在 `Aider-AI/aider` 的 issue 留言 | **UNKNOWN** |
| S | 各平台帳號（X、Reddit、HN、dev.to、部落格…） | **UNKNOWN**；這個 session 沒有、也不應該有社群帳號憑證 |

任何渠道都還要負責人指定「由哪個帳號發、帳號擁有者已同意」（關卡 A2）。

## 五、發布後的回饋處理

1. **入口**：使用者照 README 第 8 步，從 `fixtures/valid_fail.json` 開始，只填允許的欄位，填成一筆去識別的紀錄。
   - 交回方式由負責人在發布時指定。本 repo 的 Issues 在 2026-09-25 是開啟的（`has_issues: true`），發布當天要再確認。
   - 不收姓名、金鑰、程式碼或原始 log。
2. **收件後**：
   - 用 `validate_feedback.py` 驗證，必須 exit 0。
   - 不合格的紀錄只回覆「哪個欄位、哪類錯誤」（驗證器本身就只輸出這兩樣），不轉貼內容。
3. **判讀**：
   - 成功只看紀錄中的測試結果：5/5，而且測試檔的 hash 不變。不看 Aider 的 exit code。
   - 所有人都計入分母，包括沒完成、中途退出、0 人。
   - 不從個案推算百分比或省下的費用。
4. **有人卡住時**：
   - 卡在 README 範圍內（設定形狀、路徑），先修 README，再請下一位使用者。
   - 卡在範圍外（例如 Ollama 原生路徑），就照實說不支援，並指向 Aider 官方文件。
5. **停止條件**：沿用 RELEASE_GATE 的 C 節。
   - 有人回報意外扣款、金鑰外洩或資料暴露。
   - 有維護者或社群表示內容不受歡迎或有錯。
   - 上游行為改變，使文中說法不再成立。
   - 負責人撤回授權。
   - 連續兩位使用者因同一個範圍內的原因失敗。
   - 需要的聯絡數超過授權。
   任一發生就停止，回報負責人。
6. **紀錄**：每一筆紀錄的處理結果（收件時間、驗證 exit、判讀結果）交給 `ATK-FIRST-USE-01` 批次，按那一批派工時指定的路徑保存。本包沒有預先建立收件目錄。

## 六、關卡現況（RELEASE_GATE A 節，2026-09-26 發布當天更新）

| # | 關卡 | 現況 |
|---|---|---|
| A1 | 負責人授權這份內容與渠道 | ☑ 已決定渠道 R、受眾是 repo 訪客、最多 0 次聯絡，見 [負責人決定紀錄](../../../reviews/OWNER_DECISION_2026-09-26_FIRST_USE_AND_LIVE.md)（main `fcc9e1a`）。**合併由負責人本人執行** |
| A2 | 發送身分與帳號擁有者同意 | ☑ `firekou`，由帳號擁有者本人選定 |
| A3 | 連結全部釘在 commit | ◐ 文案與本檔已釘住；合併後要補一個文件 commit，寫入發布 commit 的 SHA |
| A4 | 第一屏寫明證據上限 | ☑ 入口 README、repo 首頁那一行、兩篇文案都有 |
| A5 | 上游優先、標明 Aider 作者、ATK 為可選 | ☑ |
| A6 | 去敏 | ☑ 見 [`RELEASE_DAY_CHECK.md`](RELEASE_DAY_CHECK.md)。唯一命中是 PR14 測試裡刻意放的合成字串 |
| A7 | 發布當天重讀即時狀態 | ◐ Aider #5552／#5553、LiteLLM #38318、Aider 最新版本都已重讀，與文件一致；**ATK base URL 與模型沒有重讀**（原因見 RELEASE_DAY_CHECK）。合併若不在 2026-09-26，要重做 |
| A8 | GPT 在最終 SHA 上複核 | ☐ 等待。本發布 PR 的內容讓 PR14 R2 與 PR20 R2 的核准失效，需要重審 |
| B（This repository） | 負責人授權 merge；PR14 R2 條件仍成立；合併後重新釘連結 | ◐ 負責人已選 R，由 firekou 合併；等 A8 通過 |

**要真正合併，還欠三件事**：
1. GPT 在最終 SHA 上覆核（A8）；
2. 負責人用 `firekou` 按下合併；
3. 合併後補一個文件 commit，寫入發布 commit 的 SHA（A3）。

合併之後，對外只能說「離線演練過、可以照做」，**不能**說真模型可用、有外部使用者，或 ATK 已接入。真模型的結果要等 `ATK-AIDER-LIVE-01`（選項 C，上限 $2；金鑰注入前是 BLOCKED_ACCESS）。

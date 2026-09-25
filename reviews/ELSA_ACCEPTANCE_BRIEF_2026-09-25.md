# 給愛莎的接受判斷書：Open-Skill 分發飛輪
版本 2（2026-09-25，PR #15 合併後改寫）· 產出者：Claude（本線 executor）
可信 main：`3bdb1c218866bf8a43ecba301cc33fdee693fec1`（state revision 34）
用途：請愛莎決定「這條線現在的狀態是否接受、是否繼續、往哪走」。**這份文件本身不是任何批准。**

## 30 秒看懂
Open-Skill 這條線有兩個可自己驗證的成果，都已被獨立覆核通過；沒有外部使用者、沒有真實模型呼叫、沒有花錢。

但在上一版之後發生了一件事，它現在比技術進度更需要愛莎處理：**組織狀態 skill 被合進 main，而它的獨立覆核結論是 BLOCKED，內容一個字沒改。** 連帶把兩個問題帶進公開倉庫。

## 一、組織狀態 skill 的現況（本輪新增，最需要裁示）

| 事實 | 值 |
|---|---|
| main 路徑 | `.claude/skills/atk-org-status/SKILL.md` |
| 合併方式 | PR #15 squash → `252bf6dcd8de7bd3072ad044143fa4304bc7622f`（2026-09-25T05:39:02Z） |
| 檔案 blob | `cc4c98e85080e9f4bf6a3f97582b1a0e00ce9132` |
| 這個 blob 的獨立覆核結論 | **BLOCKED**（`reviews/PR15_R1_ORG_STATUS_2affb13f.md`） |
| 合併後有沒有修改 | **沒有。與被判 BLOCKED 的那份完全相同** |
| 合併後覆核 | `reviews/PR15_POST_MERGE_GOVERNANCE_252bf6dc.md` —— 維持 BLOCKED，明寫「出現在 main 是觀察到的事實，不是批准」 |
| main branch protection | **關閉**，必要檢查 **0** |

### 1a. 治理衝突現在活在 main 上
skill 寫 Open-Skill 線硬閘「**禁止 fork、上傳、對外邀請**」。同一個 main 的 `decisions.json` 有兩筆 approved：

- `ATK-OPEN-ADOPTION-20260922`：通過證據與帳號檢查後，**最多 3 則相關邀請**。
- `ATK-EXTERNAL-VALUE-CONTINUE-20260924`：核准**一條有界的 Aider 貢獻／整合路徑**。

兩邊不可能同時成立，而且現在兩邊都在同一個權威位置。我照嚴格的那一邊執行（不邀請、不上傳、不 fork），但這等於讓兩筆已批准決策實質失效。**該由愛莎明確裁定，不該由我默默選一邊。**

### 1b. 公開外露（這一項 GPT 的覆核沒有處理，是本線補的）
這個倉庫是公開的。我逐行盤過那份 skill：**沒有任何金鑰、token、私鑰或錢包地址。** 外露的是：

| 項目 | 內容 |
|---|---|
| 兩個線上服務網址 | DeFi Lab 唯讀看板、雜誌白話首屏 |
| 跨倉庫內部狀態 | PR #49 / #46 / #13 / #12 / #11 / #1，以及 `firekou/Arbitrage_prediction_market` 倉庫名 |
| 組織結構 | 各線主管、席位代號、愛莎為團隊主管、Frank 為最終負責人 |
| 商業情報 | 本週優先、首刊約 9/28、已停掉的兩件事、商務策略進度（#1–#5 完成、#6 等 Frank） |
| 未完成清單 | 「嘴型不會動、人設未定」「HeyGen 未核准」「不簽名、不廣播」—— 等於一份「還沒做好什麼」的地圖 |

**兩個網址實測都是 HTTP 200、不需登入**（看板 9,880 bytes；首屏 8,439 bytes，2026-09-25 量測）。看板本身唯讀、簽名與廣播關閉，危害因此有限，但流量與探勘是實際的。

**必須講清楚的一件事：從 main 刪掉不等於沒公開過。** `252bf6d` 已在 main 歷史裡，之後就算再推 commit 刪檔，任何人仍可用 `git show 252bf6d:.claude/skills/atk-org-status/SKILL.md` 讀到全文，PR #15 頁面也還在，而且可能已被搜尋索引或第三方爬走。刪檔只能減少之後被順手看到的機會，**不能當成撤回**。

### 1c. 本線建議（三項，按有效性排序）
1. **服務端優先。** 網址已流出，git 端做什麼都收不回。若看板不該公開，唯一有效的動作是 Railway 加驗證或**換域名**（換了舊網址即失效）。若本來就打算公開，那真正該在意的不是網址，而是上表後三列的商業情報。
2. **repo 端改寫成「只指向各 repo 正式帳本的索引」**，不寫具體網址、PR 編號、商業進度與未完成清單。這同時解決 GPT 指出的「平行權威」與本線發現的外露。
3. **開 main branch protection。** 目前 0 必要檢查，所以被判 BLOCKED 的東西可以一路合進來，沒有機制擋。若希望「BLOCKED 不該能合」，這要靠設定，不是靠 review 自律。

GPT 的合併後覆核也要求一筆補救決策，選項是：移出 agent 發現路徑／改成非權威索引／明確廢止衝突的決策並記錄後果。上面第 2 項對應它的第二個選項。

## 二、技術交付現況（與上一版相同，已通過獨立覆核）

| 可驗成果 | 對別人的好處 | 明確還不是什麼 |
|---|---|---|
| PR #14 Draft：Aider 原生設定資產（Quick Start、最小任務＋固定評分測試、離線設定檢查器、協定錄製）。head `d1474670`；GPT 獨立重跑 11/11 測試 exit 0、五個模型名反例逐一實測 | 想用 Aider 接自己端點的人，照一份文件就能開始，且分得清「設定錯」與「模型做錯」 | 沒跑過任何真實供應商、沒有速度或省錢數字、Windows/macOS 未測、外部使用者 0 |
| 三個量到的事實：`OPENAI_API_BASE` 收根位址（實際請求 `/v1/chat/completions`）、`openai/` 前綴不會送出、`--no-analytics --no-check-update` 仍會連 `raw.githubusercontent.com` | 三個都是第一次設定會卡住、而讀文件讀不出來的點 | 只在 aider 0.86.1、單一 `--message`、repo-map 關閉的條件下量到 |
| `research/EXTERNAL_VALUE_EVIDENCE_CARDS_2026-09-24.md`：三個外部工具的價值證據卡與增量裁決 | 避免重造別人已做好的東西（兩個結論是「直接用原作」） | GPT 判 NEEDS_INFORMATION，三項 P2 待修；後續未派工 |

## 三、六點回報

**1. 現況（大白話）**
離線該做的都做完並通過獨立覆核。再往前一步需要錢或需要對外聯繫，兩者都還沒授權。另外組織 skill 帶著 BLOCKED 狀態進了 main，把一個治理衝突和一批商業情報放到公開位置。

**2. 下一步與距目標多遠**
距「Open-Skill 要有可訂閱的價值」還差**有人真的用過**。技術資產到位，兩條路各差一個授權：真實 provider 測試（需憑證、端點、明確呼叫／費用上限）；找外部使用者跟做（需發送授權與對象，研究文件寫最多 3 位探索）。

**3. 問題**
上面第 1a（治理衝突）與 1b（公開外露）。兩項都不是技術問題，都需要人的決定。

**4. 整體階段規劃**
第一階段離線資產已完成並通過覆核。第二階段同任務配對比較，前提是憑證與費用上限。第三階段外部使用者實際跟做，前提是發送授權與對象。三階段不能跳。

**5. 需要愛莎決策或幫忙**
1. DeFi Lab 看板該不該公開？換域名、加驗證，還是就讓它公開。
2. 要不要做那份「只指向帳本的索引」改寫？要的話請給工作單（範圍、work_id），本線不自己開。
3. 治理衝突以哪邊為準：skill 的「禁止對外邀請」，或兩筆已批准決策。
4. 要不要開 main branch protection。
5. 若要進第二階段：誰提供端點與憑證、呼叫上限多少。
6. 若要進第三階段：邀請對象由誰指定（研究文件明訂不把被我們引用的作者自動當收件人）。

**6. 其他意見**
兩句我認為該記下來的。

一句是舊的：這條線前幾輪最大的浪費不是技術做錯，是**把「文件寫完」當成「有人用了」**。帳本上外部採用是 0，我建議就讓它顯示 0，直到真的有人用過。

一句是本輪新的：**PR #15 這件事證明目前的品質關卡是自願的。** 覆核判 BLOCKED，然後它還是合進了 main，而且內容一字未改。GPT 只能記錄，擋不住。要嘛接受這個狀態並承認覆核只是建議，要嘛把它變成機制（branch protection）。兩者都可以，但不該以為現在已經有擋的機制。

## 關於「接受」這件事的限制（與上一版相同）
我**不能**代愛莎記錄接受，也不能把「愛莎已准」寫進帳本。本 repo 已有三份獨立覆核（PR8 R4、PR12 R3／R4、PR13 R2）駁回過「分支自稱愛莎授權」，理由都是缺可追溯的指令來源。

要讓接受成立且擋得住覆核，需要其中一種痕跡：
- 愛莎或 Frank 在對應 PR 留言，或
- Frank 在 `governance/decisions.json` 新增一筆 approved 決策。

在那之前，本線狀態維持 `ATK_AIDER_REAL_PROVIDER_OR_EXTERNAL_USE_AUTHORIZATION`，不往前推。

## 已讀入的來源（本輪實際讀取）
- **main 上的** `.claude/skills/atk-org-status/SKILL.md`，blob `cc4c98e85080e9f4bf6a3f97582b1a0e00ce9132`（與被判 BLOCKED 的同一份）
- `.claude/skills/atk-goal-alignment/SKILL.md`、`.claude/skills/executive-review-gate/SKILL.md`
- `skills/AGENT_SKILL_CONTRACT.md`（證據階梯 REPORTED → OBSERVED → TESTED → VERIFIED → REPRODUCED；無角色可批准自己的下游閘）
- `organization/ORGANIZATION_V1.md`（舊版雜誌社席位表）
- `reviews/PR15_R1_ORG_STATUS_2affb13f.md`、`reviews/PR15_POST_MERGE_GOVERNANCE_252bf6dc.md`
- `governance/state.json` revision 34、`governance/decisions.json`

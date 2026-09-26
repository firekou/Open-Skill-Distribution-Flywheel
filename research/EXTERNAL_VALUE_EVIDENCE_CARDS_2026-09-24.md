# 外部價值證據卡與增量差距裁決
work_id：LAB-EXTERNAL-METHOD-01（延續）
checkpoint：EXTERNAL_VALUE_EVIDENCE_AND_INCREMENTAL_GAP
依據決策：LAB-EXTERNAL-CONTRIBUTIONS-20260924
查閱日期：2026-09-24（所有外部來源均為當日觀察）
狀態：三張證據卡與差距裁決已完成。**未安裝、未執行任何第三方程式，未送任何上游訊息。**

## 這份文件是什麼、不是什麼
是：依 `research/AI_LAB_EXTERNAL_CONTRIBUTIONS_2026-09-24.md` 末節指定的下一交付——先找外部已有需求與第三方使用證據的工具，逐一做證據卡，再選一個原作尚未覆蓋、我們能小幅改善的缺口。

不是：第三方重現、採用證明、上游貢獻，或任何效能比較。本輪沒有跑過任何被評估的程式。

## 選題的起點是一個真實問題，不是一份工具榜單
三個候選都在回答同一個使用者問題，這個問題本身有外部證據（見卡片內來源），不是我們自己想出來的：

> 我要在自己的機器上跑別人寫的 AI 工具／MCP server／skill。我無法判斷它到底能碰到什麼，也無法判斷我設的限制有沒有真的生效。

三個候選是三種不同的答法：**卡 A 用作業系統層強制隔離**、**卡 B 用靜態掃描工具描述**、**卡 C 用集中式 gateway 收斂供應商存取**。

## 方法與誠實限制
- 來源順序依研究文件規定：官方 code / release / issue 優先，其次第三方報導。凡是我只在第三方部落格看到、無法在一手來源確認的數字，卡片內一律標記「**未經一手確認**」，不納入判斷依據。
- 卡 A 我做了一手核對：`git clone --depth 1` 後**只讀原始碼**，固定 source SHA 與授權。未執行 `npm install`、未執行 `npm test`、未執行 `srt`。
- 卡 B、卡 C 只到官方文件與官方 issue 頁面層級，**沒有 clone、沒有讀原始碼**，因此卡 B、卡 C 的技術判斷比卡 A 弱一級，不能拿來下技術結論。
- GitHub REST API 在本環境以未認證方式取用回 403，issue 內容是透過網頁擷取讀到的；issue 編號與標題屬**單次擷取未二次驗證**，引用時已標明。
- 所有 star / fork 數字只作「值得查」的線索，不作價值證據，符合研究文件引用的 CHAOSS Awareness 原則。

---

# 證據卡 A：anthropics/sandbox-runtime（`srt`）

| 欄位 | 內容 |
|---|---|
| 受益者與問題 | 要在本機跑不可信程式（agent、MCP server、第三方 skill）的開發者與團隊：需要真的擋住檔案與網路，而不是靠對方自律 |
| 原作貢獻 | 不靠容器，直接用作業系統原生機制強制檔案／網路／Unix socket 限制：macOS `sandbox-exec` Seatbelt、Linux `bubblewrap` ＋ network namespace ＋ seccomp BPF、Windows 專用帳號＋WFP egress fence |
| 來源版本（一手、已固定） | `git clone --depth 1`；HEAD `ddbeb74711c4097014ef3056791efa83f553116c`，最後 commit 日期 2026-09-21，`package.json` version **0.0.77** |
| 授權（一手） | Apache-2.0（repo 內 `LICENSE`，檔頭已核） |
| 維護現況 | README 自稱 "research preview"：「As this is an early research preview, APIs and configuration formats may evolve.」Windows 標示 Alpha。**repo 內沒有 `CONTRIBUTING.md`**（`ls CONTRIBUTING*` 回 No such file） |
| 為何被關注（可觀察證據） | 不是靠宣傳：README 自己**逐項列出已知繞過與弱化選項**（domain fronting、`enableWeakerNestedSandbox`、`enableWeakerNetworkIsolation`、`allowAppleEvents` 會「removes code-execution isolation, not just weakens it」、`/var/run/docker.sock` 等於給出整台主機）。一個願意寫下自己哪裡擋不住的專案，比宣稱全面防護的專案更值得採信 |
| 正面報告 | 對我們最直接：這正是本 repo `GOV-R1-03` 卡住時缺的那個東西。我們當時本機只有 `unshare`，實測只擋得住網路，`host_fs_denied` 與 `source_readonly` 都做不到。srt 在這三項都有實作路徑 |
| 負面報告（官方 issue，單次擷取） | #576「macOS: a caller-supplied literal path containing `[…]` compiles to a non-matching regex, silently voiding denyRead」——使用者傳入含中括號的**字面路徑**，被當成 glob 編譯，`denyRead` **靜默失效**且不留紀錄。回報者原文：「Bug 1 is the security-relevant one: reads are allow-by-default, so a deny that matches the wrong path _is_ exposure, with nothing logged.」相關同類：#596（`/tmp` 規則永遠比不上 `/private/tmp`）、#582（filesystem violations 從未被收集）、#540 |
| 獨立程度 | 高。#576 由外部回報者提出，附自製 A/B 重現輸出；不是作者自述 |
| 原本的替代方案 | 自己寫容器、自己寫 seccomp、或什麼都不做。三者我們都試過或看過，都比採用 srt 差 |
| 實際效果與限制 | **未驗證**。我沒有執行它。README 的宣稱與 issue 的反例我都讀了，但兩者都不是我的觀察 |

---

# 證據卡 B：invariantlabs-ai/mcp-scan（現為 Snyk「Agent Scan」）

| 欄位 | 內容 |
|---|---|
| 受益者與問題 | 已經裝了一堆 MCP server／skill 的人：想知道哪一個的工具描述藏了 prompt injection、tool poisoning 或 rug pull |
| 原作貢獻 | 連上已設定的 MCP server、取回 tool descriptions，配合本地檢查與雲端 API 分析，做 15 項左右的風險偵測；另有 proxy 模式監看 MCP 流量 |
| 來源版本 | **未固定**。只讀官方 repo 頁面與文件，未 clone、未讀原始碼。文件顯示 v0.5.x 與 v0.6+ 檢測項目不同 |
| 授權 | Apache-2.0（頁面讀取，未以檔案核對） |
| 維護現況 | Invariant Labs 已於 2025-06 被 Snyk 併購，工具成為 Snyk Agent Scan 的基礎。官方頁面明寫：「**Agent Scan is closed to contributions at this time**」 |
| 為何被關注 | 外部對 MCP 供應鏈的疑慮有多方來源（見下方 MCP 需求證據），這是其中最常被指名的掃描器 |
| 正面報告 | 它處理的是「描述裡寫了什麼」，這一層確實需要有人做，而且他們做得比我們可能做的好 |
| 負面／限制 | 方法本質是**靜態＋遠端取描述**，官方說明「For MCP, it connects to servers and retrieves tool descriptions.」它不回答「這個 server 執行時實際碰到了什麼」。另外會把 MCP server 設定與 skill 內容送到 Snyk 的分析 API——這對不能外送設定的環境是硬限制 |
| 獨立程度 | 中。能力描述來自官方文件（利害關係人自述），未見我能核對的第三方重現 |
| 我們能引入什麼 | 直接當工具用。**不做替代品** |

## MCP 這一層的外部需求證據（用於卡 B、卡 A 的問題成立與否）
- Zuplo《State of MCP》調查（搜尋結果轉述：約 100 名 builder，2025-11～12）：50% 把安全／存取控制列為第一難題、38% 說安全疑慮正在阻擋擴大採用、24–25% 的 MCP server **完全沒有驗證機制**。**我無法在一手頁面確認**：`https://zuplo.com/mcp-report` 當日擷取只回到導覽列，沒有內文；`https://zuplo.com/blog/mcp-survey` 未再逐項核對。因此這些數字在本文件中只作**方向性線索**，不作論據。
- 「社群 MCP server 安裝失敗率 30–50%」：只在二手部落格看到，**找不到一手來源，不採用**。
- 可採信的一手層級證據反而是卡 A 的 issue：隔離規則會靜默失效，這件事有具體編號、具體重現。

---

# 證據卡 C：BerriAI/LiteLLM（LLM gateway／router）

| 欄位 | 內容 |
|---|---|
| 為何列入 | 它是離 ATK Router 最近的外部成熟方案。若不看它就談我們的 router 有價值，就是研究文件說的「先選工具再找需求」 |
| 受益者與問題 | 要在多家供應商之間統一呼叫、控管金鑰與預算的團隊 |
| 原作貢獻 | 統一 API、fallback、預算與金鑰管理的 proxy |
| 維護現況 | 高度活躍，且**有企業版**：階層預算、RBAC、SSO、audit log 等治理功能需商業授權（二手來源，未一手確認） |
| 負面報告（官方 issue，單次擷取） | #41357（開啟，2026-09-16）「Proxy leaks one SlackAlerting.periodic_flush task every 30s when general_settings.alerting is set (grows until restart)」；#37611（已關，2026-09-10）背景健康檢查把整張表載進每個 worker → 接近 OOM；#38193（已關，2026-09-03）OOM 重啟後記憶體持續成長 |
| 一手安全事件 | 官方公告 `docs.litellm.ai/blog/security-update-march-2026`：PyPI 上的 `litellm==1.82.7`、`1.82.8` 遭投毒，2026-03-24 10:39 UTC 起上架約 40 分鐘；payload 掃環境變數、SSH key、AWS/GCP/Azure 憑證、Kubernetes token、資料庫密碼並外傳。官方建議輪換全部密鑰、檢查 `litellm_init.pth`、釘回 v1.82.6 或更早 |
| 獨立程度 | 事件本身為專案自述（高可信，因為對己不利）；效能問題為外部回報 issue |
| 我們的增量 | **看不出來**。這是一個資源遠比我們多的專案，它的公開問題是規模與供應鏈，不是缺一個小 adapter |

---

# 差距裁決

| 候選 | 裁決 | 理由 |
|---|---|---|
| B：mcp-scan / Agent Scan | **直接採用原作** | 它已經把「描述層風險」做得比我們可能做的好；而且官方明寫不收貢獻，我們連回饋路徑都沒有。不做替代品 |
| C：LiteLLM | **不改造** | 唯一該帶走的是一條做法，不是一份程式：**釘住版本、把第三方套件當供應鏈看**。這是我們自己該遵守的紀律，不是可交付的技術貢獻 |
| A：sandbox-runtime | **薄接入，並保留一個上游回饋候選** | 見下 |

## 選定的缺口（只選一個）
**使用者自己寫的設定，有沒有真的擋住他以為擋住的東西——原作沒有提供一個面向使用者的檢查方式。**

我在一手原始碼核到的事實（HEAD `ddbeb747`）：
- `package.json` 的 `bin` 只有 `srt`；`src/cli.ts` 全檔只有兩個 `.command(...)`：`windows-install`、`windows-uninstall`。**沒有 `verify` / `check` / `probe` 之類的子命令。**
- `test/sandbox/` 下有 70 個測試檔，**而且確實有用對照組**（例如 `macos-apple-events.test.ts:73` 的 `baselineOpenWorks` 會先確認未隔離時該操作本來會成功，再決定要不要跑該組測試）。

**所以這裡要先更正我自己的第一個假設。** 我原本以為「原作沒有對照組觀念」，一讀原始碼就知道不成立——他們有。真正缺的比那窄得多：

> 那套對照組紀律活在**專案自己的 CI**裡，驗的是「實作符不符合作者的預期」。它沒有被包成一個**使用者可以拿自己的 settings 檔跑一遍**的東西。#576 正是這個縫隙：實作照自己的邏輯正確執行，使用者寫的 `denyRead` 卻靜默失效，而且**不留紀錄**——使用者沒有任何管道會發現。

## 增量假說與反證條件
**假說**：一個「拿使用者的 settings 檔，對每條規則各跑一次應當被拒的動作，並與未隔離基線配對比較」的一致性探針，能在使用者端抓到 #576／#596 這一類靜默失效。

**必須先講的減項**：#576 的回報者**自己已經手工做了配對比較**（他貼出的 `project / project[1] / proj*ect` 三列 enforced / BYPASSED / LOST 對照表就是）。所以方法不是我們的原創，我們能加的只有**打包成可重複執行、覆蓋全部規則**這件事。這讓增量比我原先設想的小很多，我照實記下來。

**反證條件（任一成立就撤回這個題目）**：
1. 上游已經有、或正在做同樣的東西——我只讀了 CLI 與 issue 標題，**沒有讀完 132 個開啟中的 PR**，這是本輪最大的未覆蓋範圍。
2. 探針抓不到 #576 那個設定（例如規則本身在編譯期就被改寫，探針看到的和實際生效的不是同一份）。
3. 只能在 macOS 成立、Linux 上做不出同樣的配對，那它就不是一個通用貢獻。

**停止條件**：若上述任一成立，結論就是「直接採用 srt，不做增量」，並把它當成我們 `GOV-R1-03` 的隔離後端候選——**這件事本身就已經有價值，與有沒有上游貢獻無關**。

## 對我們自己的直接影響（內部收益，不是社會價值）
`GOV-R1-03` 與 controller 的 retry gate 一直卡在「沒有可驗證的隔離環境」。srt 是目前找到最接近的現成答案，而且授權（Apache-2.0）允許使用。這是內部解鎖，**不能算作我們創造的外部價值**，兩者分開記。

## 本輪未做
未安裝、未執行任何第三方程式（含 `npm install` / `npm test` / `srt`）· 未讀 srt 的 132 個開啟 PR · 未固定卡 B 卡 C 的 source commit · 未送任何上游 issue 或 PR · 未 merge · 未部署 · 未改 secrets／權限 · 未新增費用 · 未建立 active claim · 兩個 live runner 維持停用 · 既有修復輪次維持 2/2，未重置。

新增外部採用證據：**0**。本輪產出的是選題與裁決，不是已交付的技術貢獻。

## 來源清單（2026-09-24 查閱）
- https://github.com/anthropics/sandbox-runtime （一手；已 clone 至 HEAD `ddbeb74711c4097014ef3056791efa83f553116c`，只讀）
- https://github.com/anthropics/sandbox-runtime/issues/576 、 /596 、 /582 、 /540
- https://github.com/invariantlabs-ai/mcp-scan
- https://invariantlabs.ai/blog/introducing-mcp-scan
- https://docs.litellm.ai/blog/security-update-march-2026 （一手官方事件公告）
- https://github.com/BerriAI/litellm/issues/41357 、 /37611 、 /38193
- https://zuplo.com/mcp-report （當日擷取無內文，數字未採用）

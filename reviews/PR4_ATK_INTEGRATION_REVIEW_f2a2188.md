# PR #4：官方接入確認與最小修正交接

日期：2026-09-18
審查 commit：f2a2188b9a42db11b3ab9c261678de3ddec78806
PR：https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/4
結論：APPROVED_WITH_CONDITIONS，僅認可方向與有限實作；以下必要修正完成前保持 Draft，不代表批准合併或發布。

## 負責人需要知道的事

官方入口已找到，並非需要另建 ATK 平台。官方模型清單以本次授權的憑證取得 HTTP 200，回傳 52 個模型。PR 的舊網址缺少 .tw 與 /api，不能繼續把它當作 ATK 是否上線的證據。機密未寫入此報告或 repository。

14 個本機 HTTP 測試獨立重跑通過。但原始碼未硬編碼 key 不等於執行時不會洩漏 key；錯誤輸出洩漏已用假憑證重現。

這個交付是獨立範例，尚未接入 headroom 或其他候選工具。可保留為輔助範例，但「每個接入都必須先寫共同 adapter」沒有證據。官方已提供原生 MCP 與 OpenAI 相容設定，下一個分享資產應優先用現成設定完成。

## 方向對齊五行

- 目標來源：負責人最新校正，技術分享、實用 skill／工具、透明可選的 ATK 接入與採用。
- 本輪交付：確認真實接入，審查小型範例，交付 Claude 可直接執行的修正。
- 主線連結：讓開發者能照 Quick Start 接入 ATK，並可切換回其他 provider。
- 必要驗證與停止點：官方 endpoint、最小連線、基本成功／錯誤行為、文件與憑證安全；修完即送有限複核。
- 範圍差異：不恢復 benchmark、不擴建 provider 框架、不要求所有供應商真實測試、不新增治理平台。

## 官方事實與 live 證據

來源：https://aitokenking.com.tw/assets/docs/zh-Hant/index.html#mcp-server
本次直接取得並閱讀官方 HTML。

| 用途 | 官方入口 | 驗證方式 |
|---|---|---|
| OpenAI 相容 API base URL | https://api.aitokenking.com.tw/api/v1 | Authorization: Bearer，由環境變數供應 |
| 模型清單 | GET /api/v1/models | TESTED：HTTP 200，52 個模型 |
| Chat Completions | POST /api/v1/chat/completions | 下方列本輪單次驗證結果 |
| MCP | https://api.aitokenking.com.tw/mcp | X-Aitokenking-Api-Key header；官方文件確認，尚未執行 MCP handshake |

MCP URL 不能當作 ATK_BASE_URL；兩種協定需分開寫。文件使用 AITOKENKING_API_KEY，PR 使用 ATK_API_KEY；負責人提供的變數標籤也不同。Claude 應選一個文件中的標準名稱並明列映射，不能要求使用者猜測。只提供 placeholder 與環境變數引用，不提交真實 key。

Chat live（TESTED）：直接使用此 PR 的 atk_provider.py，僅以環境設定改用官方 base URL，model=claude-sonnet-4.6，MAX_RETRIES=1，無 fallback，max_tokens=16。一次訊息 Reply with OK only. 成功回傳 OK，usage 為 12 input／4 output tokens；未回報美元成本，不能當成免費。這證明單次文字路徑可用，不代表 MCP、所有模型、其他 provider 或完整 CLI 均已 live 驗證。未取得帳務資料，未進行其他付費工作負載。

## 必要修正

### P4-01：錯誤本文可能洩漏憑證（REPRODUCED）

atk_provider.py 的 _post 把服務端錯誤 body 前 400 字直接納入 ProviderError，範例會印到 stderr。註解宣稱 key 在 header 因此不會出現在 body，這個推論不成立，服務端或代理可以回顯 header。

重現：本機 _Server 回應 HTTP 401，JSON error 為 invalid credential CANARY_SECRET；傳入同值的假 API key。捕捉 complete() 的例外後，'CANARY_SECRET' in str(exc) 為 True。未對真實服務刻意製造此錯誤。

修正：公開錯誤使用受控訊息，或可靠遮蔽本次使用的機密，再輸出；至少驗證 HTTP 401／代理錯誤與最終 fallback 彙整均不含 canary。保留 status 與 provider 等可診斷資訊。不要用「原始碼找不到 sk-」代替執行時測試。

### P4-02：沒有摘要也會被當作成功（REPRODUCED）

OpenAI 相容路徑收到 HTTP 200、choices[0].message.content = null 時，complete() 正常回傳 Completion(text=None)。範例會印 None 並 exit 0。對這個文字摘要資產而言沒有交付有效摘要。

重現：本機 _Server 回應上述 JSON，斷言 c.text is None，結果 True。

修正：為本範例的純文字能力明確檢查有效非空字串；不支援的 tool-only／null 回覆應清楚失敗，不能冒充摘要成功。驗正常非空文字成功、null／不符型別／空內容失敗即可，不需要扩建 tool calling。

### P4-03：Quick Start 與可檢視請求的說明不符實作（OBSERVED）

1. .env.example 的舊 ATK URL 不符合官方文件，README 只叫人填 key/model，照抄無法完成。
2. README 宣稱 dry-run 印出 exact request，但程式只印每個 message 前 300 字，且未印完整 wire payload。這是摘要預覽，不是完整請求。

修正官方 URL、環境變數映射與文件；dry-run 可以保留節錄但必須標明，或確實輸出完整無 header 的 payload。不要輸出 Authorization。

## 給 Claude 的下一步

1. Fetch main，讀本檔及 atk-goal-alignment skill，保留 PR #4 分支，不合併。
2. 修 P4-01～03；更新 VERIFICATION 與 executor response，保留歷史未驗證紀錄但標明時間，增加本輪 reviewer live 證據及限制。
3. 把官方 MCP 環境變數設定及 OpenAI 相容設定做成最小 Quick Start。引用現成官方接點，不自行實作 MCP server，也不把通用 adapter 包裝成必備基建。
4. 兩篇分享稿以讀者實際完成接入為中心；不聲稱已整合 headroom、不聲稱節省。既有工具如可配置 base URL 就用配置，勿先 fork。
5. 本輪獨立範例可以作第一份接入教學，明列原訂候選整合尚未完成；後續才從現有候選選一個實際工具接上，不以本 PR 虛報完成。
6. 回覆仍寫 reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md，列新完整 SHA、必要正負控制、文件變更、未驗證部分。測試完成送 review 即停止，不恢復 Lab 或治理 PoC。
7. 真實 key 不在 repository，也不應從報告取得。若 Claude 環境没有 secret，只完成不需 secret 的修正，引用本 reviewer 的 live 結果並標明測試者，不能稱自己跑過。

此文件是持久交接，不表示已啟動或通知另一個 Claude session。不得把 main 的審查文件推送視為程式 PR 合併授權。

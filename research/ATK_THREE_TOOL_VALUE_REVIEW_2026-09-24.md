# 三個外部工具的價值初評與接入取捨
日期：2026-09-24｜Planner 研究，非獨立 runtime review
本輪已完成：官方入口、授權、外部回報與既有本 repo PR 查重。未完成：第三方案例重現、ATK live、外部採用效果。

## 選擇結論
優先 Aider 的「小範圍程式修改與可跟做設定範例」。使用原生 OpenAI-compatible 設定，不再建共同 provider adapter。Continue 列候補；Open WebUI 暫不實作。
這是以本輪可取得證據與小交付成本選擇，並非全市場排名，也不宣稱三者的外部效益皆已充分證實。

| 候選 | 既有貢獻／使用情境 | 可查外部訊號及證據限制 | ATK 接點／開放情況 | 本輪取捨 |
|---|---|---|---|---|
| Aider | 終端中的既有程式修改、局部 diff 與 Git 工作流程 | dbatools 作者有具體遷移操作、成本與失敗紀錄；另一位開源維護者說明小 diff 與人工掌握程式的重要性。是使用者第一手敘述，非受控比較或我們重現 | 原生 OPENAI_API_BASE、OPENAI_API_KEY、openai/model；LICENSE.txt Apache-2.0 | 優先做可跟做設定與小任務；新增價值只是假說，不改上游核心 |
| Continue | 在 IDE 使用自訂模型完成 chat/edit 工作 | issue12896 回報自訂設定與預期不符，但其「模型自稱」不能證實路由錯誤；issue13231 有 Windows 路徑問題回報。本輪未找到充分獨立效益數據 | provider: openai、apiBase；特定模型可需 useResponsesApi:false；LICENSE Apache-2.0 | 保留；IDE版本、角色與endpoint差異讓首輪驗收面較大 |
| Open WebUI | 圖形介面連接多個模型服務 | issue26324 回報切到 llama.cpp 後看不到 token usage；是使用與瓶頸線索，未由我們重現，不能推導 ATK 同樣出錯 | 官方支持 OpenAI-compatible connection；現行 LICENSE 含品牌保留條件及例外，不視為無條件白牌 | 保留原品牌的教學可能有用；本輪不部署 UI、不改品牌、不擴多人帳號 |

## Aider 的價值證據卡
受益者：維護既有程式碼、只想做可審小改動的開源開發者與其 Agent。
原作價值：已提供修改檔案、上下文與 Git 整合；我們不能把這些算自己新增功能。
1. Chrissy LeMaire 的使用報告：2024-10-18 發表，頁面標2025-11-02更新；提供 Pester 遷移命令、失敗經驗與成本自述。它支持「真實維護工作曾用 Aider」，不支持當前模型、價格或 ATK 的效益。
2. Sem Sinchenko 2026-03-10：第一手說明小範圍 patch、人工 review 與程式 ownership 的價值。文中速度／token數是個人經驗，本輪不採為保證，也不採其廣泛正確率主張。
3. Aider issues5639、5713、5752 是其他服務的接入宣傳／提案。只證明有人提出配置配方，不能當獨立採用或 ATK 客戶需求。
4. 固定來源5dc9490bb35f9729ef2c95d00a19ccd30c26339c：已讀 args.py/main.py，確認原生API base映射；__init__.py含0.86.3.dev，這是source pin，不冒稱正式release。
5. CONTRIBUTING要求顯著變更先討論，小變更可PR，另有CLA。本輪只在自家repo備稿，不送上游或簽署任何協議。

預期增量：讓不熟悉 endpoint/model prefix 的使用者，用一份明確設定與任務就能開始，分清「設定正確」與「模型做對」，減少故障定位時間。此增量尚未測量。
反證：原生官方步驟同樣容易；我們增加檔案、維護或限制，卻沒有減少錯誤。若反證成立，推薦官方入口，停止自有包。

## 具體案例與比較設計
案例：合成的小型 Python CSV 匯入函式，目前要求 name/email 固定欄序；改為依欄名讀取，支援對調欄序，缺 email 欄給明確錯誤，保留空字串與Unicode。這是本地教學fixture，非外部使用者已驗證需求，更不是原Pester案例重現。
以測試定義既有行為、交換欄序、缺欄、空值、Unicode；只有匯入函式可改，評分測試固定不可改。
先做「原生官方設定」與「我們的設定指引」配對；未取得模型使用授權前，只驗設定、CLI與隔離中的協定測試。使用固定回應/假server時標OFFLINE_PROTOCOL_ONLY，不記模型成功。
live開放後再測同模型同輸入與同預算，記全部請求（含helper/重試）及結果。沒有live證據不寫接通。
外部使用者評估：先記第一次自行完成所需時間、設定錯誤與協助次數；再記是否願意再用、拒用原因。小樣本3位仅作探索且不是必須湊滿。招募或發送另依現有明確對象和權限，不把研究來源作者自動列收件人。

## 為何不重建 adapter
本repo PR4已有standalone provider例子，live head829c7e9d800b8aeb19ef13d20af9678511c72cb4，本輪只做查重，不批准它。Aider原生配置已能表達接點，故不引入PR4程式、不改PR5、不新增MCP或controller。PR8 live仍9ab2cbb09f44a94a0e52d8e8c4d6bbb9de2d6b34，舊2/2修復不重開。

## 來源與搜尋可追溯性
查閱日期2026-09-24；定向初評，不宣稱完整系統性搜尋、全分頁或所有最新專案。
官方：
- https://aider.chat/docs/llms/openai-compat.html
- https://github.com/Aider-AI/aider/blob/5dc9490bb35f9729ef2c95d00a19ccd30c26339c/aider/args.py
- https://github.com/Aider-AI/aider/blob/5dc9490bb35f9729ef2c95d00a19ccd30c26339c/aider/main.py
- https://github.com/Aider-AI/aider/blob/5dc9490bb35f9729ef2c95d00a19ccd30c26339c/CONTRIBUTING.md
- https://docs.continue.dev/customize/model-providers/top-level/openai
- https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/
- https://github.com/open-webui/open-webui/blob/main/LICENSE
外部：
- https://blog.netnerds.net/2024/10/aider-is-awesome/
- https://semyonsinchenko.github.io/ssinchenko/post/aider_2026_and_other_topics/
- https://github.com/continuedev/continue/issues/12896
- https://github.com/continuedev/continue/issues/13231
- https://github.com/open-webui/open-webui/issues/26324

GitHub定向查詢：
- repo:Aider-AI/aider "openai compatible"，top3：5639/5713/5752，均未採為獨立價值證據。
- repo:continuedev/continue "apiBase"，top3：13198/12896/13231；13198為provider提案，未採為獨立效益。
- repo:open-webui/open-webui "OpenAI" "connection"，top3：30510/30957/26324，僅採26324作明確使用障礙線索。
- repo:Aider-AI/aider is:issue "api_base" -PZERO -Bourse -HAL，top5無結果，不代表無問題。
- 本repo open PR列表12筆，另aider關鍵字PR/code搜尋無結果；索引無結果不是絕對不存在，executor開工仍須檢查樹與分支。

Web查詢包括官方相容設定，以及Aider的OpenAI/404與CONTRIBUTING。搜索引擎部分查詢回傳無關結果，已剔除。沒有採用未讀取全文的宣傳比較文作數值依据。
LICENSE blob觀察：Aider d645695673349e3947e8e5ae42332d0ac3164cd7；Continue c25dc1768217ba50d454fcc06290d66886512872；Open WebUI99f39e7feff29c93342877adad2d5c15e707444c。blob不是整個版本commit；實作時需釘完整依賴。

下一交付見 reviews/ATK_AIDER_FIRST_USE_PACKET.md。本報告無外部採用、無省費／省時數字，也無獨立批准。

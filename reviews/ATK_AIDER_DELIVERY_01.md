# ATK 下一階段執行工作包
日期：2026-09-26。負責人要求沿完整藍圖立即細化、執行並派工。
本包為 Planner 指令，不是實作完成或獨立驗收。

## 目標對照
目標來源：本輪負責人明確要求繼續執行，沿既有工具分享、可選 ATK 接入、實際採用藍圖。
本輪交付：第一次接觸專案的開發者可從單一入口取得既有 Aider 資產並完成離線跟做。
主線連結：消除成果分散在 PR14/16/17/18/19，使用者不知從何開始的實際交付問題。
必要驗證與停止點：乾淨目錄按公開命令完成取得、設定檢查、已知失敗任務與回饋驗證，交 Draft PR。
範圍差異：整合可用交付，不重選工具、不新增框架；外部動作的缺口只約束對應步驟。

## 當前狀態
PR14 離線資產 d1474670db12934c80caa05674c8e4320cbad312。
PR16 readiness 1dcd625df3bde48b13b91abb3b03eb7e19371558。
PR17 live 準備 6ea3cec9937e74de8ce77f47c5e92d3d1617c506。
PR18 upstream 備稿 1abd74a4b7f14d8b5e397d33afa2ace212841099。
PR19 first-use 準備 a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41。
以上依 main 最新 review，已審範圍不重新修第三輪。真實 ATK 模型與外部使用仍未證實。

## 本次立即派工契約
- work_id: ATK-AIDER-DELIVERY-01
- revision: 1
- source_main: bbb85b39001ece19a8f19e3f186c1c3eeb1805cb
- source_head: a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41
- branch: claude/atk-aider-delivery-01
- dedup_key: firekou/Open-Skill-Distribution-Flywheel:ATK-AIDER-DELIVERY-01:1:bbb85b39001ece19a8f19e3f186c1c3eeb1805cb:executor
- deadline: 2026-09-27T02:32:50Z
- 單批45分鐘；未完成交 partial、已交付檔案與精確恢復步驟。最多兩輪本包修復，舊 finding 次數不重置。
- 新增 API 費用上限：0。
- executor: Claude；reviewer: GPT 不同 run，從 GitHub 取證。
- 查既有同 work_id PR/claim；有 active claim 就續用，不另開。
- 先在 PR19 conversation 回 claim：session/run、work_id/revision、source_main/source_head、branch、scope、dedup、絕對期限。

## 允許路徑與命令
僅 integrations/aider-atk/delivery/**、research/adoption/aider/first-use/delivery/**、reviews/ATK_DISTRIBUTION_EXECUTOR_RESPONSE.md 追加。
新分支從上述 source main 建立；五個來源 commit 唯讀取得，不合併來源分支、不改作者原始證據、不把現有 Draft PR 標成 merged。
允許 git fetch/show/archive、read-only GitHub/官方文檔查核、隔離 tempdir/venv、固定版本依賴安装、Python unittest/jsonschema、SHA-256、工作分支 commit/push/Draft PR。
測試使用合成資料且不得帶真憑證或可寫 GitHub token。套件安裝網路與無 provider 呼叫分開說明；不要宣稱完整網路隔離。

## 依序執行的小步驟與具體檔案
1. delivery/README.md：一個入口，依序列「取得固定資產 → 安裝 → 無憑證設定檢查 → 最小 CSV 任務 → 如何判定結果 → 提交去敏回饋」。分清離線可立即執行與 live 待條件。明列 cwd、版本、完整命令及预期 exit。優先直接引用來源固定 SHA，不複製全部歷史報告。
2. delivery/SOURCE_MANIFEST.json：每個實際使用檔案的來源 commit、path、SHA-256、目標用途。以最小取得腳本或完整 git 命令讓上述入口真的可跟做；不可 curl|sh，不執行未核對腳本。來源檔保持 byte-for-byte；必要 wrapper 全放 delivery。
3. research/.../delivery/validate_feedback.py：真正可執行的紀錄驗證入口，使用 PR19 v1.1 schema 的固定來源。除了 schema，若 tests_total/tests_failed 都非 null，拒絕 failed > total。無效輸入 exit 非0；輸出只列欄位位置與錯誤類型，不回顯原始值或身份/keys。依賴固定版本。這是資料收集流程組裝，不修改 PR19 已批准 schema。
4. 同目錄 fixtures/ 與 test_validate_feedback.py：合成合法 pass、合法 fail、failed>total、false pass、錯誤來源 URL、內部冒外部、malformed JSON、合成秘密不回顯；確認正控制不被全部拒絕。內部 fixtures 不算使用者資料。
5. delivery/REHEARSAL.md 與 evidence/：在乾淨目錄親自照 README 跑一次。記環境、命令、時間、exit、檔案 hash。固定 CSV 原始缺陷預期測試失敗，不能把它寫成成功；可在演練複本加入明示人工參考修正驗證5項評分機制，不把人工修正歸因模型。無真模型呼叫。列實际遇到的阻礙及已改的入口，不複製舊測試數當新測試。
6. delivery/LIVE_HANDOFF.md：重用 PR17 命令，整理一份待填 endpoint/model、runtime、安全注入、key輪替確認、價格、token/請求/總費用上限與停止方式的具體執行清單。缺項標 NOT_RUN/BLOCKED_ACCESS，只停 live，繼續其他成果。不得讀取/印出/搬運秘密或假設預算。
7. delivery/RELEASE_CANDIDATE.md：重用 PR19 已審兩篇文案，不再重新研究。提供這個 Draft PR 固定內容的入口、兩篇全文/固定來源、每個建議渠道的格式、選一個首發建議及理由、發送身份所需帳號能力、發布後回饋處理步驟。未確認渠道權限標 UNKNOWN；用量/價格/真接入未測不添加行銷主張。來源升版才重查受影響內容。
8. executor response 追加：實際成果連結、所有來源與 result SHA、命令/exit、哪些離線已測、哪些 live 未做、下一批具體可用輸入。建立一個 Draft PR，回 PR19 conversation 結果 URL 與 SHA，交 GPT 覆核後停止本批。

## 驗收與否定條件
- 同一入口無需人工搬運五個 PR 報告即可完成離線跟做；來源可固定追查。
- 命令實跑，失敗基線/人工參考/真模型三者清楚，真模型未跑就明標。
- 回饋驗證器能拒絕不一致資料且不洩漏輸入；至少一個合法案例通過。
- 兩篇草稿可直接審閱，含來源、限制、可選 ATK/退出方式。
- 沒有新平台、SDK、controller、benchmark、重新選題或重作既有研究。
- 有來源/存取故障，交已完成部分與精確錯誤，不阻塞無依賴步驟。
- 不接受只回傳計畫或填空模板作整包完成。

## 後续全程工作與接续條件
|階段/負責|輸入與小動作|可驗收成果與停止點|
|---|---|---|
|現在 Claude：DELIVERY-01|上述8項操作，整合來源、寫小validator、親自跟做|一個可跟做 Draft PR + 原始演練結果，送GPT|
|GPT：交付驗收|取result SHA，跟做入口、核對關鍵負控制、比較來源|具體review；只修影響交付缺陷，最多2輪|
|Claude：ATK-AIDER-LIVE-01|對已選endpoint/model，確認注入與費用授權，按固定命令一個最小連通+CSV任務，保留失敗與usage|真模型輸出、5項測試、人工diff核對、實際費用或未知，送審；未具條件只停此列|
|Claude：ATK-FIRST-USE-01|資產驗收後，按具體獲授權渠道/身份發布或至多3位匹配非作者探索，先取得同意|全分母、成功/退出、配置卡點、支持分鐘；0人也如實回報，不擴發送|
|Claude：ATK-VALUE-DECISION-01|取得首次結果後，沿既有protocol分析；缺可比對照只報個案，記不同日期再用|保留/改善/推薦原作/退出，最多一個後續改善，不造百分比|
|Claude：ATK-UPSTREAM-01 發送階段|沿PR18既有草稿，修9請求的Aider歸因，送出前查重與貢獻規範；僅具授權才送|實際issue URL與維護者回覆；無回覆保持未知|
|Claude：ATK-SUSTAIN-01|首次使用起7日及30日窗口整理再用、失敗、維護/支持時間、可取得成本|投入與成果裁決；兩批無新需求/效果就縮減，不自動擴第二工具|

每列已有全程目的；達前置且已有授權，GPT立即派下一包，不再要求負責人重講方向。不具備的條件記該動作缺口，不把全專案標停止。後續 batch 的來源 SHA、期限、對象與額度須在派工時固定，不能用表格假裝已啟動。

## 界線
本輪明確授權規劃、離線整合實作、Draft PR與GitHub派工。沒有指定的merge、production部署、上游/社群發送、credential操作、新增支出仍不執行。舊授權若確實涵蓋特定動作沿用，不能杜撰已核准帳號/對象/成本。

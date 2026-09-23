# 當前交接狀態

## 2026-09-23：PR9 M1 隔離計畫獨立覆核

- PR #9 Draft/open/unmerged；精確 head `ba3f9ae3bce04d72f4afaa6f9e935c112661fca2`，只有 6 個 `reviews/` 計畫、狀態與 probe 檔，沒有產品程式變更。
- [R1 獨立覆核](PR9_R1_M1_PLAN_ba3f9ae3.md)：**NEEDS_INFORMATION**。PR #9 是 PLAN_ONLY／blocker evidence，不是 M1 replay 成果。
- VERIFIED：PR #5 live head 仍為 `304af885...`；計畫引用的 current／previous 共 6 個 Git blob SHA 均與精確 refs 相符；probe JSON 可解析。
- OBSERVED：PR #9 probe 顯示其環境無 Docker／Podman／bwrap／firejail，`unshare -n` 被拒，且 `pr_code_executed=false`。本 reviewer 環境也在 bwrap 建立 network namespace 時被 OS 拒絕，因此沒有執行 PR code。
- 執行前必要修正：Git blob header 必須用 NUL byte，不是字面 `\\0`；唯讀 evidence input 與可寫 result output 必須分離；作者本機 `/workspace/qa-plans` 改成固定 repository path；evidence level 依實際 run 擇一。
- Exact head 的 workflow runs、check runs、commit statuses、PR reviews 均為 0；PR 沒有 comment 或固定 executor response。這不提高 persistent launcher／executor 接線狀態。
- 下一 checkpoint：`M1_P5_R4_01_QUALIFYING_RUNTIME_AND_PRE_RUN_PLAN_CORRECTION`。真正權限缺口是具 network-none、唯讀來源、無 secrets／寫 token、pinned image 的獨立 runner。
- 完成前不發邀請、不套 PR5 patch；外部採用仍為 0。未 merge、部署、呼叫 provider、修改 secrets／權限或新增支出。


## 2026-09-23：PR8 revision 2 五項條件已關閉

- [R2 獨立覆核](PR8_R2_CONDITIONS_8161c6a3.md)：內容 SHA `8161c6a33251b06c44db9f5dbabc9431fa73b67d`，live/result head `b76fc7ba08deade6733f140d3a37aadfd201d51c`；結論 **APPROVED_WITH_CONDITIONS**。
- Claude session `session_01RFeCsTYkVywjHvXk7od7Ab` 的 revision 2 成果、work_id、source head、dedup key、content/result SHA 與 [result receipt](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/8#issuecomment-5783517419) 完整。
- VERIFIED：15.1% 已綁 MD5／0.37.0／PR5 SHA；外連與 telemetry 主張已縮到實際證據；六個入口固定到 immutable commit `fb47e31...`；validator schema 層與負控制獨立重跑成立；INT-02 四／五筆誤修正。
- `check_consistency.py` 24/24、正常 records、五負一正 fixtures、另建 11 項 schema matrix、immutable target existence 與 patch/AST 回歸均獨立通過。精確 content/live SHA 沒有 workflow run、commit status 或 PR review。
- 非阻擋 P3：`EVIDENCE_FORMAT.md` 仍寫四個負 fixture，實際為五個；列 merge／發布前 editorial backlog，不為一字差異派第二輪修復。
- 新留言沒有改 content head。獨立以 main `e65f66b...` 和 PR head `b76fc7ba...` 重跑 merge-tree 無衝突，GitHub REST 回報 `mergeable_state: clean`；先前一次 false 是重算暫態。未來真的進 merge gate 時仍須再查。
- 下一 checkpoint 是 M1／P5-R4-01 合格獨立隔離重放。完成前不發邀請、不套 PR5 patch；不再向 Claude 派這批條件修復。
- 外部採用仍為 0。未 merge、部署、發邀請、修改 settings/secrets/權限、送上游、呼叫 provider 或新增費用。


## 2026-09-23：PR8 revision 2 已接單

- Claude session `session_01RFeCsTYkVywjHvXk7od7Ab` 已對 `ATK-OPEN-ADOPTION-01` revision 2、stage `A-CONDITIONS` 回傳完整 claim：[接單證據](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/8#issuecomment-5783362399)。
- source/live head `77a8200533c80bc288186f58c1d8ecb6d25d121d`、reviewed content `c3637c4dcf7a0ab86e884dfb6ba07054c93d873d`、dedup key 與期限均符合限定修正包。
- 這是與 r1 不同的既有 Claude session；可將本 task 升為 EXECUTING，但仍不證明 comment 可啟動新 session 或 persistent launcher 已接通。
- PR live head 尚未改變，沒有 result SHA，因此不重審、不重派、不重複留言。下一 checkpoint 是 revision 2 的新 content/result SHA。
- 未發邀請、未套 PR5 patch、未 merge、部署、修改 settings/secrets/權限、送上游或新增費用。


## 2026-09-23：PR8 A package R1 獨立覆核

- PR #8 Draft/open/unmerged；內容 head `c3637c4dcf7a0ab86e884dfb6ba07054c93d873d`，live head `77a8200533c80bc288186f58c1d8ecb6d25d121d` 只追加 executor response。
- Claude receipt 已成立：`ATK-OPEN-ADOPTION-01` revision 1、`session_016YNgsSCC2eV5sicob2f56f`、固定來源 `304af885...` 與 dedup key；這是既有 session 的成果證據，不證明持久 launcher。
- [R1 review](PR8_R1_ATK_OPEN_ADOPTION_c3637c4d.md)：**APPROVED_WITH_CONDITIONS**。A1–A5 產物已齊，外部採用仍為 0。
- VERIFIED：PR5 doc patch 可套用；`ab_test.py` 去 docstring 後 AST 不變；JSON/manifest 可解析；GitHub search、Agent Skills、MCP Registry 與兩個候選討論的關鍵敘述獲獨立交叉核對。
- 條件：外部稿的 27% 應為 15.1%；一般 networked runtime 不可宣稱 nothing leaves loopback；branch/省略網址改 immutable 完整 URL；validator 補 schema 約束；INT-02 四/五筆誤。
- reviewer bwrap 隔離因 `NETLINK_ROUTE socket: Operation not permitted` 失敗，未執行 PR runtime。作者 44 tests/15.1%/負控制仍為 TESTED；M1 與 P5-R4-01 獨立重放 pending。
- 已傳送同 work_id revision 2 的一次 bounded condition packet：[PR comment](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/8#issuecomment-5782770702)。目前只到 SIGNAL_SENT，沒有新接單或成果 SHA。
- 條件關閉前不發邀請、不套 PR5 patch。未 merge、部署、改 settings/secrets/權限、送上游、呼叫 live provider 或新增支出。


唯一規則入口：[治理入口](../governance/OPERATING_RULES.md)。決策看 decisions.json；啟動查 live PR head，不沿用歷史快照當批准。


## 2026-09-22：新產品採用工作包已交付 main

- [完整工作包](ATK_OPEN_ADOPTION_EXECUTION_PACKAGE.md)：`ATK-OPEN-ADOPTION-01` revision 1，READY_FOR_EXECUTOR。
- 第一輪交付 A1-A5：統一入口、Agent 契約、分發方案、邀請候選/草稿、採用證據格式；分支 `claude/atk-open-adoption-01`，Draft PR 送審。
- 首批開源開發者與其 Agent；內部測試、受邀外部採用、公開發現採用分開記錄。尚無本包新接單/成果/外部採用證據。
- 下一 checkpoint：Claude 固定 work_id 的 session/run 接單與 A 包成果 SHA，GPT 獨立覆核；留言或文件存在不等於 launcher 已啟動。
- PR5 R9 NEEDS_INFORMATION 不變；舊 2/2 不重派。原文件 backlog 依新指示限定納入本包文件/docstring 整併；P5-R4-01 仍等獨立隔離重放。PR6 不阻塞無依賴採用工作。
- 以下為歷史快照，current task 與界線以最新 decisions/state 和完整包為準。

## 2026-09-21：PR5 R9 最後修復確認

- [R9 review](PR5_R9_CONFIRM_304af885.md)，head `304af885193245da7186cb6b9ab247ec2494bd86`，**NEEDS_INFORMATION**。
- VERIFIED：指定三入口四處 live 命令皆有 `--retry-max-attempts 1`，官方 0.37.0 CLI/retry loop 交叉核對通過；P5-R8-01 在指定入口 source-level 修復成立。
- 本 reviewer 的 bwrap 與 unshare 探測仍 exit 1 / Operation not permitted，未執行 PR code。作者 44 tests 與 mutants 仍為 TESTED，P5-R4-01 獨立重放保持 pending。
- work_id `ATK-PR5-R7-LIVE-GUARD` revision 2 已由既有 session 回傳 source/result SHA 與 dedup key；[接單/成果](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/5#issuecomment-5762403819)。不代表新 session 或持久 launcher 已接通。
- 2/2 修復結束，不派第三輪。free sample 舊命令與成功次數文案保留發布前 BACKLOG_NOT_DISPATCHED；受驗證安裝入口限定 README/TRY_IT 的 0.37.0，不將 free sample 當已驗收 live 入口。
- 下一 checkpoint：合格獨立隔離環境綁定現 head 重放既有 P5-R4-01 與受影響 tests；不要求作者重做同類證據。無依賴的 ATK 分發規劃繼續，不等待 controller ACTIVE。
- 新留言事件只對應同一份第二輪交付，已合併處理，沒有重複 review 或派工。PR open/Draft/unmerged；未使用 key、模型、費用、部署、權限修改或上游發送。

## 2026-09-21：PR5 R8 第一輪修復確認與最後修復包

- Claude 既有 session 已以固定 work_id `ATK-PR5-R7-LIVE-GUARD` revision 1、source head `f4d676b22a853f64b37f2c160cdb3d1f6bc47efc` 接單，回傳 result head `cde4e5c855096b1d7566d44680259851810aec99` 與 dedup key；這證明既有 GitHub conversation 到既有 session 的一次 round trip，不證明 comment／label 能啟動新的持久 Claude session。
- [R8 限定確認](PR5_R8_CONFIRM_cde4e5c.md)：**BLOCKED**。金鑰命令列範例、預設四次呼叫與未證實因果三項，在 app／文件層級已修正。
- 新 P1 `P5-R8-01`：釘選的 Headroom 0.37.0 預設 `retry_max_attempts=3`，會對 429／529／其他 5xx／transport failure 重試。現行 live 命令未覆寫，因此 mock 只證明兩個 client requests，不能證明 provider attempts 上限為 2。
- 已向 PR #5 傳送同一工作包 revision 2，也是 2／2 最後一輪；source head、dedup key、scope 與期限均已固定。修法限於 live 啟動加 `--retry-max-attempts 1`、對齊呼叫主張與聚焦離線測試。
- 新留言事件經 readback 確認只是 revision 2 工作包本身；live head 仍為 `cde4e5c8`，尚無新 session 接單或成果 SHA，不重複派工。
- Exact head 無 workflow runs、check runs 或 commit statuses；作者自報 40 tests 為 TESTED，本 reviewer 未在合格隔離 runtime 執行 PR code。
- `P5-R4-01` 繼續等待獨立隔離重放，不重派作者。第三方採用仍為 0；ATK 採用主線不等待 controller ACTIVE。
- PR #5 維持 Draft、未合併；本次 readback 顯示 mergeable false。未部署、未修改 secrets／權限、未呼叫模型、未新增費用、未送上游。



## 2026-09-21：PR6 第二輪限定修復覆核結案

- 方法：govern-github-agent-handoffs；授權 GOV-HANDOFF-TAKEOVER-20260921。review 仍依 REVIEW-MAIN 存 main。
- GPT reviewer webhook 已由 PR #6 的 synchronize 事件實際驗證，精確 live head e26aac4eed0696cefa45b19aac46e7fc9c3da6e8；這只證明 reviewer event path，不證明 Claude persistent launcher 或完整端到端接通。
- Claude 既有 session session_01RFeCsTYkVywjHvXk7od7Ab 已交付 work_id GOV-PR6-R2、revision 2。程式 head 25457fbd2ff02a900d55538eb4e2fa0893663c31；live head 其後只追加 executor response，沒有 controller 程式差異。
- [R4 獨立 review](PR6_R4_G4_REVIEW_25457fbd.md)：**BLOCKED**。CLI success envelope 與 guard ordering 在 source 層級關閉；lease-loss launch、effect binding、deadline launch gate 與 credentialed executor/reviewer isolation 仍阻擋。
- 作者自報 146 tests、50/51 mutants 與 replay／recovery／isolation evidence；本 reviewer 沒有合格隔離 runtime，因此不升格為獨立通過。精確程式與 live SHA 都沒有 commit status 或 workflow run。
- 同批限定修復已達兩輪上限，不再向 Claude 自動重派第三輪，也不改名規避。next checkpoint 改為 Planner scope reduction：保留 GitHub durable ledger、人工 bounded handoff 與已驗證 reviewer event；controller 維持 FOUNDATION_ONLY / 非 ACTIVE。
- Claude persistent launcher、executor 接線、真實隔離 runtime 與完整閉環仍為 NOT_VERIFIED。沒有因留言送出或舊 session 回覆而提高這些狀態。
- PR5 live 933446ab230e6fb8b41d79b596ef3c19b721fb7a 未變，P5-R4-01 繼續等待獨立隔離重放，不重派作者修復。PR7 只保留補充證據，不建立平行 controller。
- repo API 讀取及 main review／ledger 寫入已成功；未合併、未部署、未修改 Secrets／權限、未新增費用、未送上游。
- 產品主線仍是有用工具/skill、可選 ATK Router/API/MCP 接入、技術分享與實際採用；不以治理 ACTIVE 阻塞無依賴交付，不恢復 benchmark、Freeze 或框架試點。

## 2026-09-21：PR6 G4 獨立 review 與接續規劃（R2 歷史）

- 新完整報告已收到。程式 head `86421c903563a16ca888a4aed10bd614e223ca0e`，政策 `d92d082bfcee7002d737e2c3ee2914d2b1fa804c`。
- 審查時 live head `75976be1db636ef72d76206b387583fb3cc03443`；與程式 head 淨差異只有送審文件，無程式變更。
- [G4 review](PR6_R2_G4_REVIEW_86421c90.md)：**BLOCKED**。GOV-R2-01～05 與既有 GOV-R1-03 OPEN；runtime **FOUNDATION_ONLY**。
- REPRODUCED：兩個 live command 範本在標準字串展開時拋 KeyError。VERIFIED：controller 未呼叫續租與 intent API；其餘 crash／限額／policy 接線缺口以原始碼證據標示。
- 本 reviewer 的隔離工具被 OS 拒絕，未執行 PR tests/replay/mutation 或模型探針。作者自報 92 tests／26 mutants 不升格為獨立通過。
- [完整接續 Prompt](../governance/IMPLEMENTATION_PROMPT.md) 已補齊修復、C0/C1 修訂、G4 重審、G5 單次試行、C2/C3/G6 持久交接、C4 維運及 G7 使用者成果驗證。D1 分支與 D3 reviewer 定義依既有決策，不重問。
- 本次只寫 review／規劃／摘要，未啟動 runner、安裝 trigger、呼叫模型或合併 PR。PR5 與既有 reviewer trigger 本輪不變。

## 2026-09-19：PR5 最新獨立複核
- 精確 live head `933446ab230e6fb8b41d79b596ef3c19b721fb7a`，Draft、未合併。
- [GPT R6 review](PR5_R6_REVIEW_933446ab.md)：**NEEDS_INFORMATION**。新提交只含 executor 重放紀錄與回覆，0 產品程式變更，範圍不變。
- VERIFIED：R5 manifest 的五個 Git blob SHA 已由 reviewer 對 GitHub 精確 refs 交叉核對，全數一致。
- TESTED：executor 自報在 env-i、unshare-n 與唯讀輸入下通過 31 tests、五個 unknown controls、舊版負控制及既有控制；這不是獨立驗收，不能自行關閉 P5-R4-01。
- VERIFIED probe：本 reviewer 環境的 bwrap、unshare、user namespace 均被 OS 拒絕，Docker 不存在；依安全門檻未執行 PR code。見 [R6 隔離探測](evidence/pr5-r6/isolation_probe.json)。
- 下一步只需另一個可提供無秘密、無外網、唯讀來源、無寫入 token 的獨立 reviewer 重放既有 [R5 證據包](evidence/pr5-r5/README.md)。Claude 不需重寫修復或再補同類自跑證據。
- P5-R4-01 維持 `INDEPENDENT_RUNTIME_VERIFICATION_PENDING`。同一 head 無新獨立證據不重複 review、不寫空提交。
- 第三方採用 0、搜尋 T0 未執行仍為既有記錄；本輪未重測。1A／2A／3A 有效，上游仍未批准送出。
- PR6／GOV-BOOTSTRAP 不在本任務範圍，不更動其狀態。

## 持續檢查
- 已註冊「ATK PR5 提交複核」，PR #5 新 commit 事件可喚醒 GPT reviewer；沒有 5／10 分鐘輪詢，也沒有每小時替代排程。
- 本輪 webhook 已成功取得事件、查 live head、去重並形成綁定完整 SHA 的 review，表示 reviewer 事件路徑已有一次實際紀錄；不等於 executor 已接通或整套治理 ACTIVE。
- 報告／狀態寫 main，不用被審分支記帳 commit 撞掉 review。
- GOV-BOOTSTRAP 仍須驗證持久控制、實際 runtime 與停止／去重；不要再建重複 PR5 reviewer 排程，也不要把 reviewer 事件成功當完整閉環驗收。見[原導入交辦](../governance/IMPLEMENTATION_PROMPT.md)。

## 歷史
- [R5](PR5_R5_REVIEW_32ca53c.md) 對 `32ca53cd703efeb647ddb2d65168ba69f1e414d6` 的結論為 NEEDS_INFORMATION，原因是獨立隔離 runtime 不可用；R6 新增 executor 證據後結論未變。
- PR #4 的 829c7e9 已完成約定 review，見 [R3 及追加結案](PR4_R3_REVIEW_328a33b.md)。
- PR #1 benchmark 維持暫停，歷史 findings OPEN。

## 2026-09-21：PR6 R5 scope reduction

- Live head `7de3043938b4179f5011f82927aaeecc5b82cbd1` 相對 `e26aac4` 只有一份 171 行提案，`governance/controller/` 與 executor response 未變；R4 對程式 `25457fbd` 的 **BLOCKED** 結論維持。
- [Planner review](PR6_R5_SCOPE_REDUCTION_7de3043.md)：**APPROVED_WITH_CONDITIONS**，只接受拆包作為規劃輸入，不構成第三輪修復、merge、部署或 runtime 啟動授權。
- 包 A（R2-02／03／05 與兩項 P2）保存為 `BACKLOG_NOT_DISPATCHED`；包 B 等待可驗證的 trusted-wrapper／untrusted-source 隔離後端。原批兩輪上限不重置，不建立平行 controller。
- 隔離驗收須分開可信 orchestration 與未信任 PR source：PR code 不直接取得 credential；必要模型連線經可信、可稽核、最小權限 wrapper/broker；GitHub write 另行綁定 work_id/result head；所有 denial claim 需要可工作的 unwrapped baseline。
- Controller 維持 `FOUNDATION_ONLY`。主線 ATK 工具/skill、可選 Router／API／MCP 接入與實際採用不等待治理 ACTIVE；本輪沒有外部使用者成功證據。
- Exact head 無 workflow runs 或 commit statuses；未執行 controller 測試，因為本輪沒有 implementation diff。

## 2026-09-21：PR5 R7 採用準備覆核

- Live head `f4d676b22a853f64b37f2c160cdb3d1f6bc47efc` 相對 `e8a15d7d` 有一個新內容 commit，含 preflight 修正、3 個新測試、TRY_IT 與 executor response；不是 reviewer-only 或 main merge。
- [R7 review](PR5_R7_REVIEW_f4d676b.md)：**BLOCKED**。離線／live 外送邊界、最小試用入口及歷史資料標示有進展，但 live 指令仍有兩個 P1。
- VERIFIED：TRY_IT 宣稱首次 live 為一個任務、direct／proxy 各一次；實際 `ab_test.py` 會跑 summary 與 needle，合計四次 provider calls。TRY_IT 同時禁止命令列放 key，卻示範 `ATK_API_KEY=...`。
- VERIFIED：兩次 pass-through 只能證明觀察重複，`local_check.py` 仍將其解釋成 payload 沒有冗餘，與 executor「根因未建立」矛盾。
- 作者自報 34 tests 與 controls 為 TESTED；exact head 無 workflow run、check run 或 commit status。本 reviewer 沒有合格隔離 runtime，未執行 PR code。
- 已向 PR #5 留下一次限定修復包 `ATK-PR5-R7-LIVE-GUARD`，source head 與 dedup key 固定；目前僅為 `SIGNAL_SENT_NO_RECEIPT`，不代表 Claude session 已啟動。
- `P5-R4-01` 繼續等待獨立隔離重放，不重派作者、不因 R7 修復關閉。第三方採用仍為 0。
- 未 merge、未部署、未修改 secrets／權限、未呼叫模型、未新增費用、未送上游。

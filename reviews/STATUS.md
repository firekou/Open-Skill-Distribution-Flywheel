# 當前交接狀態

## 2026-09-23：PR12 A4 當日邀請 precheck 覆核

- PR #12 Draft/open/unmerged；精確 head `707dc26d15d8b0a2a6a34cb0364fd73f68e397d8`，只新增 precheck 與 branch STATUS，沒有送出邀請。
- [R1 獨立覆核](PR12_R1_A4_PRECHECK_707dc26d.md)：**BLOCKED**。三個 immutable commits 的 Quickstart blob 一致；C1/C2 仍為 Unanswered；C3 closed/completed、C4 open 但無可附重現，這些 live facts 已驗證。
- P1：C1 問 Command Code／9router request shape；C2 問 Anthropic `/v1/messages`；現有 Quickstart 只驗 OpenAI chat-completions 與 synthetic deploy log。現在的邀請無法直接完成兩位使用者的工作，不得把「可留言」當「適合邀請」。
- P2：A4 最多三次的有限邀請方向已由 ATK-OPEN-ADOPTION-20260922 授權，不應再重問是否要邀請；真正缺口是 exact sender login 與可回覆 Discussion 的 capability evidence。
- P2：pinned Quickstart §9 仍寫 independent replay pending，與 PR10 已關閉 M1 的 main 狀態不一致。下一版須建立新 immutable content URL，並保留只涵蓋 P5-R4-01 的窄界線。
- 已送出同 work_id revision 3、stage `A4-PRECHECK` 的最後 2/2 限定修正訊號：[PR #8 comment](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/8#issuecomment-5797105025)。目前只有 SIGNAL_SENT，尚無 Claude session/run 接單或 result SHA。
- 下一 checkpoint：`ATK_OPEN_ADOPTION_R3_CLAIM_OR_RESULT`。修正通過前不發邀請；外部採用仍為 0。
- 未 merge、部署、套 PR5 patch、修改 secrets／權限、呼叫 provider、送上游或新增支出；automation 維持 `FOUNDATION_ONLY`。

## 2026-09-23：PR10 M1 獨立隔離重放通過

- PR #10 Draft/open/unmerged；精確 head `cf37880bb90d6f646591588f39de91df67d7923c`，來源綁定 PR #5 `304af885193245da7186cb6b9ab247ec2494bd86`。
- [R1 獨立覆核](PR10_R1_M1_REPLAY_cf37880b.md)：**APPROVED**。M1／P5-R4-01 在限定範圍內關閉，PR #5 升為 **APPROVED_WITH_CONDITIONS**；這不是 merge、發布或 live provider 授權。
- 獨立 runner `bc-5b9148f9-3253-5b1a-8a1c-79147a5cb763` 使用 pinned image `python@sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9`，具 `--network none`、唯讀 root、唯讀來源與 evidence mount、drop capabilities、no-new-privileges 與資源上限。
- VERIFIED：來源／前版共 6 個 Git blob SHA 全部與精確 refs 相符；19/19 JSONL 可解析且無 `passed:false`；44/44 unit tests 通過；未知參數控制與舊版會回顯 synthetic secret 的負控制成立。
- 證據上限為 **REPRODUCED**，只涵蓋 P5-R4-01。它不證明 license、clean install、live provider、外部採用、發布或 persistent launcher/controller。
- Exact evidence head 的 workflow runs、check runs、commit statuses、PR reviews 均為 0；這不影響已直接審核的 evidence，但不提高持久自動化狀態。Controller 維持 `FOUNDATION_ONLY`。
- 外部採用仍為 0。下一 checkpoint：`PR8_DAY_OF_A4_INVITATION_PRECHECK`，只核對 recipient、channel、account permission 與 immutable URL；通過後才可依既有授權最多發 3 份邀請。
- 尚未 merge、部署、發送邀請、呼叫 provider、修改 secrets／權限、送上游或新增支出。

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
> **落地註記（2026-09-23）**
>
> 本檔為 **PLAN_ONLY**。截至 2026-09-23，`ISOLATION_RUNTIME` 尚未可用（品保探測結果：`ISOLATION_RUNTIME=NOT_AVAILABLE`）。隔離重放尚未執行。P5-R4-01 維持待獨立隔離重放。`independent_runtime_verified` 維持 false。`governance/state.json` 未修改。
>
> 文件用語（僅供人讀，未寫入 state）：`M1_P5_R4_01_PLAN_READY_AWAITING_ISOLATION_RUNTIME`。
>
> 目標對齊：來源是 2026-09-23 負責人要求把品保計畫落入 `reviews/`。交付是執行前檢查清單。主線是 ATK-OPEN-ADOPTION-01 的 M1 隔離重放準備；少了這份綁定 head／blob 的清單，下一席位無法按固定範圍重放。停止點是計畫落地；沒有隔離 runtime 就不跑 PR code、不發邀請、不套 PR5 patch、不 merge。範圍只含本計畫與 STATUS 指標。

# QA 一頁｜M1／P5-R4-01 合格隔離重放

**席位：** 品保（Open-Skill QA）  
**日期：** 2026-09-23（Asia/Taipei）  
**工單來源：** 飛輪長｜PR#8 下一關＝唯一關  
**性質：** 可執行計畫＋檢查清單（本輪**未**執行重放）  
**禁令：** 發邀請｜套 PR5 patch｜merge｜部署｜作者 session 代替獨立重放

---

## 0. 錨點（執行前必須再讀 live）

| 欄位 | 值 |
|---|---|
| Finding | `P5-R4-01`（unknown token／dash-leading 私密值不可回顯） |
| Milestone | `M1` ＝關閉 PR#8 附條件通過前的獨立隔離重放 |
| 綁定 PR#5 head | `304af885193245da7186cb6b9ab247ec2494bd86` |
| 負控制 baseline（pre-fix） | `d1930e4696f11cfb3cdae2f59d1b3692b68ee127` 的 `local_check.py` |
| PR#8 live（條件文件） | `b76fc7ba08deade6733f140d3a37aadfd201d51c` |
| 條件來源 | `reviews/PR8_R2_CONDITIONS_8161c6a3.md` |
| state.json | `tasks[ATK-OPEN-ADOPTION-01].next_checkpoint = M1_P5_R4_01_INDEPENDENT_ISOLATED_REPLAY` |
| PR5 任務狀態 | `NEEDS_INFORMATION`；`pending_evidence` 含本項 |
| 歷史腳本（不可直接當本輪 manifest） | `reviews/evidence/pr5-r5/` 綁的是舊 head `32ca53c…` |

**作廢條件：** PR#5 live head ≠ `304af885…`；或重放範圍檔案 blob 變更；或隔離證據失敗／無法建立。

---

## 1. 環境門檻（任一項不成立 → 不跑 PR code）

| # | 要求 | 通過準則 |
|---|---|---|
| E1 | 無 secrets | 無 `ATK_*`／`OPENAI_*`／`ANTHROPIC_*`／`GH_TOKEN`／雲端金鑰進容器；合成字串僅用固定假值 |
| E2 | 無外網 | `--network none`（或等價）；例外僅允許**事先**列出且為唯讀取 blob 的準備階段（執行重放本體必須離線） |
| E3 | 唯讀來源 | 輸入掛載 `readonly`；無 `.git`、無 host HOME、無 Docker socket |
| E4 | 無寫 token | 無 GitHub write／deploy／PAT；結果只寫到 reviewer 側 evidence 目錄 |
| E5 | 獨立身分 | 執行者 ≠ Claude executor／作者 session；須記錄 reviewer run id |
| E6 | 隔離能力 | Docker（`--pull=never` 本地 pinned 映像）或等價 bwrap／namespace；能力探測失敗則停止 |

**品保本機探測（2026-09-23）：** `docker` 無、`unshare -n` → Operation not permitted → **`ISOLATION_RUNTIME=NOT_AVAILABLE`**。故本輪只交計畫，不降級為無隔離執行。

---

## 2. 準備步驟（可在隔離外、唯讀 API 完成）

1. 再查 PR#5 live head；若 ≠ `304af885…` → **STOP**，更新計畫後再派。  
2. 自 GitHub 取精確 blob（勿用作者工作目錄拷貝）：

| 路徑 | Git blob SHA（於 `304af885…`） |
|---|---|
| `current/local_check.py` | `07f7fd15964da5cb363086327b05fa1d1f2b7153` |
| `current/test_local_check.py` | `4fe0411306d7e0fcae114575e460a4d768c2623f` |
| `current/ab_test.py` | `0927f51c2a2443117fa6942b29f32529f7557a1f` |
| `current/README.md` | `54c8f3bc056d76831db515f1f79236dc66f4b4e6` |
| `current/TRY_IT.md`（受影響文件，建議一併掛入） | `600f0d912311c32317622c26fd26c783097d87cf` |
| `previous/local_check.py`（`d1930e4…`） | `ec66c5ea914fe62d8ec24ab65c3a221f2aacab76` |

3. 新建本輪 evidence 目錄（建議）：`reviews/evidence/pr5-m1-304af885/`  
   - `manifest.json`：寫入上表＋`reviewed_head`／`comparison_head`  
   - 改編自 `pr5-r5/reviewer_checks.py`：  
     - **必須**改 `reviewed_head` 與 blob 對照  
     - **禁止**硬編碼 `Ran 31 tests`（該數已過期）；改為：suite `exit=0` 且 README 宣稱數＝`TestLoader.countTestCases()`（與套件內 `DocumentedCountsMatchReality` 同口徑）  
     - 保留：五種 unknown 無回顯、舊版 dash 負控制會回顯、`--help`、合法 `--needle=`、縮小／等長／膨脹／丟 needle、HTTP body 三態不洩漏  
4. SHA1 驗證：`sha1("blob {len}\\0{bytes}")` 必須等於 manifest。

---

## 3. 隔離執行（唯有 E1–E6 全過才執行）

參考（映像須預先本地 pinned，`--pull=never`）：

```sh
timeout 180 docker run --rm --pull=never --network none --read-only \
  --cap-drop ALL --security-opt no-new-privileges --user 65534:65534 \
  --pids-limit 64 --memory 512m --cpus 1 \
  --tmpfs /tmp:rw,nosuid,nodev,size=64m,mode=1777 \
  --mount type=bind,src="$INPUT",dst=/input,readonly \
  --mount type=bind,src="$EVIDENCE",dst=/evidence,readonly \
  --env HOME=/tmp --env PYTHONDONTWRITEBYTECODE=1 \
  --entrypoint python3 "$IMAGE" \
  /evidence/reviewer_checks.py /input /evidence/manifest.json
```

記錄：完整命令、exit、stdout／stderr、Python 版本、映像 digest、隔離旗標、reviewer 身分、精確 head。

---

## 4. 通過／失敗準則

| 檢查 | PASS | FAIL／STOP |
|---|---|---|
| G0 隔離 | E1–E6 成立且 probe 成功 | 任一失敗 → **不執行** PR code；P5-R4-01 維持 pending |
| G1 blob | 全部 SHA 吻合 | mismatch → STOP |
| G2 P5-R4-01 | 五種 unknown：`exit 2`、輸出無合成私密字串、無 `needlez`、含 `--help` | 任一回顯／錯誤 exit → FAIL |
| G3 負控制 | 舊版 `previous`：`--needlez -<secret>` **必須**回顯 secret（證明測試抓得到舊洞） | 不回顯 → 負控制失效 → FAIL |
| G4 合法路徑 | `--help` OK；`--needle=-secret` 仍可 parse | 破壞合法路徑 → FAIL |
| G5 suite | `test_local_check.py` exit 0；README 數＝實際 case 數 | 失敗或數值漂移 → FAIL |
| G6 回歸 | 縮小／等長／膨脹／丟 needle／HTTP body 控制符合腳本斷言 | 任一失敗 → FAIL |
| G7 邊界誠實 | 報告標明：mock process／network；**非**乾淨安裝、非 live provider、非採用證明 | 若誤升 VERIFIED／對外發布 → 違規 |

**關閉條件：** G0–G7 全 PASS，且關閉當下再查 live head 仍為 `304af885…` → 可將 `P5-R4-01` 標 **CLOSED（獨立 TESTED／REPRODUCED 依實際隔離強度標註）**。  
作者／executor 自報不得升格。

---

## 5. 證據欄位（交付物 schema）

寫入 `reviews/evidence/pr5-m1-304af885/RESULT.json`（建議）與 STATUS 追加段：

```yaml
work_id: M1_P5_R4_01
reviewed_head: "304af885193245da7186cb6b9ab247ec2494bd86"
comparison_head: "d1930e4696f11cfb3cdae2f59d1b3692b68ee127"
pr8_live_at_plan: "b76fc7ba08deade6733f140d3a37aadfd201d51c"
isolation:
  runtime: docker|bwrap|NONE
  network: none
  secrets: false
  github_write_token: false
  pr_code_executed: true|false
checks: { G0..G7: PASS|FAIL|NOT_RUN }
highest_evidence_allowed: TESTED   # 品保席位上限；獨立重放成功可標 REPRODUCED 僅限本 finding
decision: PASS|FAIL|BLOCKED_NO_RUNTIME
evidence_paths:
  - reviews/evidence/pr5-m1-304af885/manifest.json
  - reviews/evidence/pr5-m1-304af885/reviewer_checks.py
  - reviews/evidence/pr5-m1-304af885/stdout.txt
  - reviews/evidence/pr5-m1-304af885/isolation_probe.json
```

---

## 6. 與 STATUS／state.json 對齊的 next_checkpoint 語

**計畫完成（本輪）：**  
`next_checkpoint: M1_P5_R4_01_PLAN_READY_AWAITING_ISOLATION_RUNTIME`

**重放 PASS 後（執行席位／獨立 reviewer）：**  
`next_checkpoint: PR8_DAY_OF_A4_INVITATION_PRECHECK`  
（完成前仍：**不發邀請、不套 PR5 patch**；`EVIDENCE_FORMAT` 四／五筆誤仍為 merge 前非阻擋 backlog。）

**重放 FAIL：**  
`next_checkpoint: M1_P5_R4_01_FAIL_BOUNDED_REPAIR`（僅限失敗 finding；不自動重開已用盡的 2/2 修復輪）

**無 runtime（現況）：**  
`next_checkpoint: M1_P5_R4_01_INDEPENDENT_ISOLATED_REPLAY`（維持 state.json 原文；補註 `runtime_owner` 待指定）

---

## 7. 本輪品保結論

| 項目 | 狀態 |
|---|---|
| 可執行計畫＋檢查清單 | **DONE** |
| 隔離重放執行 | **NOT_RUN**（本機 `ISOLATION_RUNTIME=NOT_AVAILABLE`） |
| 證據路徑 | 計畫：`/workspace/qa-plans/M1_P5_R4_01_ISOLATED_REPLAY_QA_PLAN.md`；repo 落地待飛輪長指定寫入 `reviews/` |
| 可發布／邀請／patch | **否** |

```yaml
qa_gate:
  decision: PLAN_ONLY
  finding: P5-R4-01
  bound_head: "304af885193245da7186cb6b9ab247ec2494bd86"
  isolation_runtime: NOT_AVAILABLE
  next_checkpoint: "M1_P5_R4_01_INDEPENDENT_ISOLATED_REPLAY"
  blocking_for_pr8: true
  forbidden_actions_honored: [invite, apply_pr5_patch, merge, deploy]
```

# Runtime 假設一頁｜M1／P5-R4-01 主跑（品保）

**席位：** 品保＝主跑（愛莎裁定／飛輪長改派）  
**日期：** 2026-09-23 22:19 Asia/Taipei  
**性質：** 強制順序第 1 步——環境定義；**尚未**執行隔離重放  
**禁令：** 發邀請｜套 PR5 patch｜合 main｜部署｜作者 Claude session 代替獨立 runtime

---

## A. 合格隔離 runtime 定義（假設＝必須同時成立）

| ID | 假設 | 滿足方式 | 例外標法 |
|---|---|---|---|
| R1 無 secrets | 執行環境不帶真實 `ATK_*`／provider／`GH_TOKEN`／雲端金鑰；測試僅用固定合成字串 | 清空／不注入；manifest 列假值名稱 | 若必須帶名無值的占位 → 在 RESULT 標 `secret_names_present_values_empty` |
| R2 無外網 | 重放本體 **network none** | Docker `--network none` 或等價 namespace／bwrap | 準備階段唯讀取 Git blob 可有網；須與執行階段分開記錄。執行階段有網＝**不合格** |
| R3 唯讀來源 | 輸入樹 readonly；無 `.git`、無 host HOME、無 docker.sock | bind mount `readonly` | 無例外 |
| R4 無寫 token | 無 GitHub write／deploy／PAT；結果只寫 reviewer evidence | 不掛憑證；不用作者 session | 無例外 |
| R5 獨立身分 | 執行者 ≠ PR 作者／Claude executor session | 記錄 reviewer／agent id＋run id | 作者自報不得升格 |
| R6 可證明隔離 | 可出示隔離旗標（docker 命令列／bwrap argv／probe JSON） | 失敗則 STOP，不跑 PR code | 無例外 |

**不合格則：** 不執行 `local_check.py`／測試套件中的 PR 程式碼；不得標 PASS／CLOSED。

---

## B. 綁定 SHA（執行前再核對 live）

| 錨點 | SHA |
|---|---|
| PR#5 reviewed head | `304af885193245da7186cb6b9ab247ec2494bd86` |
| PR#8 live（條件文件） | `b76fc7ba08deade6733f140d3a37aadfd201d51c` |
| 負控制 baseline | `d1930e4696f11cfb3cdae2f59d1b3692b68ee127` → `previous/local_check.py` blob `ec66c5ea914fe62d8ec24ab65c3a221f2aacab76` |
| 條件文件 | `reviews/PR8_R2_CONDITIONS_8161c6a3.md` |

**範圍檔 blob（於 PR#5 head）：**

| 路徑 | blob |
|---|---|
| `current/local_check.py` | `07f7fd15964da5cb363086327b05fa1d1f2b7153` |
| `current/test_local_check.py` | `4fe0411306d7e0fcae114575e460a4d768c2623f` |
| `current/ab_test.py` | `0927f51c2a2443117fa6942b29f32529f7557a1f` |
| `current/README.md` | `54c8f3bc056d76831db515f1f79236dc66f4b4e6` |
| `current/TRY_IT.md`（建議） | `600f0d912311c32317622c26fd26c783097d87cf` |

作廢：live head ≠ 上表；或任一 blob 漂移。

---

## C. 通過／失敗準則（摘要）

| Gate | PASS | FAIL／STOP |
|---|---|---|
| G0 runtime | R1–R6 全真 | 任一假 → **BLOCKER／NOT_RUN**，不跑 PR code |
| G1 blob | SHA 全吻合 | mismatch → STOP |
| G2 P5-R4-01 | 五種 unknown：exit 2、無私密回顯、無 `needlez`、輸出含 `--help` | 回顯或錯誤 exit → FAIL |
| G3 負控制 | 舊版 dash-leading **必須**回顯 secret | 不回顯 → FAIL |
| G4 合法路徑 | `--help`；`--needle=-secret` 可 parse | 破壞 → FAIL |
| G5 suite | exit 0；README 數＝實際 case 數（禁止硬編碼 31） | 失敗／漂移 → FAIL |
| G6 回歸 | 縮小／等長／膨脹／丟 needle／HTTP body 控制 | 任一失敗 → FAIL |
| G7 誠實邊界 | 標 mock；不升 VERIFIED／不宣布可發布 | 違規 |

對照 PR#8 R2：本關關閉前 **不**發邀請、**不**套 PR5 patch。

---

## D. 證據路徑（約定）

| 產物 | 路徑 |
|---|---|
| 本假設一頁 | `/workspace/qa-plans/M1_P5_R4_01_RUNTIME_ASSUMPTIONS.md` |
| 隔離探測 | `/workspace/qa-plans/m1-runtime-probe-20260923-221947/probe.txt` |
| 探測 JSON | `/workspace/qa-plans/m1-runtime-probe-20260923-221947/isolation_probe.json` |
| 若可跑後的證據樹 | `reviews/evidence/pr5-m1-304af885/`（manifest／reviewer_checks／stdout／RESULT.json） |
| 詳細計畫（前序） | `/workspace/qa-plans/M1_P5_R4_01_ISOLATED_REPLAY_QA_PLAN.md` |

---

## E. 本機對照假設（主跑探測結果）

| 假設 | 本機 | 判定 |
|---|---|---|
| R1 無 secrets | 環境無 provider／GH token 名（僅 CURSOR_*） | 可滿足（若執行） |
| R2 無外網 | `enp0s3` UP；`unshare -n` → Operation not permitted | **不滿足** |
| R3 唯讀來源 | 無容器挂载工具 | **無法證明** |
| R4 無寫 token | 本席不持 write PAT 執行重放 | 意向可滿足；缺隔離載具 |
| R5 獨立身分 | 品保 agent（非作者 Claude session） | 身分 OK |
| R6 可證明隔離 | docker／podman／bwrap／firejail＝無；docker.sock＝無；CapEff＝0 | **不滿足** |

**總判定：`ISOLATION_RUNTIME=NOT_CAPABLE` → 進入強制順序第 2 步 BLOCKER，不執行重放。**

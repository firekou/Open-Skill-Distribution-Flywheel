# BLOCKER｜M1／P5-R4-01 合格隔離重放（品保主跑）

**時間：** 2026-09-23 22:19 Asia/Taipei  
**順序：** ① runtime 假設一頁已交 → ② 現有環境無法滿足 → **立刻 BLOCKER**  
**誠實標示：** `pr_code_executed: false`｜未假裝跑過｜未標 PASS

## 缺什麼（具體）

| 缺口 | 現況 | 需要 |
|---|---|---|
| 容器 runtime | `docker`／`podman` CLI＝無；`/var/run/docker.sock`＝無 | 可用 Docker（或 podman）＋本地 pinned 映像、`--pull=never`、`--network none` |
| 網路隔離 | `unshare -n` → Operation not permitted；`enp0s3` UP（預設有外網） | 能建立 **network-none** 的 namespace／容器；或由運維提供已 offline 的 runner |
| 使用者空間沙箱 | `bwrap`／`firejail`＝無 | 若不用 Docker，需等價 bwrap 配方 |
| Capabilities | CapPrm／CapEff＝0 | 不足以自建 network namespace |
| 映像 | 無本地 python 測試映像可掛 | 預先 pull 並 pin digest 的 python3 映像（或核准內部映像） |

**可滿足但不足以開跑：** 獨立身分（品保≠作者 session）；環境無 provider／GH write token 名。

## 探測證據

- `/workspace/qa-plans/m1-runtime-probe-20260923-221947/probe.txt`
- `/workspace/qa-plans/m1-runtime-probe-20260923-221947/isolation_probe.json`
- Runtime 假設：`/workspace/qa-plans/M1_P5_R4_01_RUNTIME_ASSUMPTIONS.md`

## 與條件對照（PR#8 R2）

- 獨立隔離重放：**尚未開始執行**（runtime 門檻未過）
- 禁令已守：未發邀請、未套 PR5 patch、未合 main、未部署、未用作者 Claude session

## 建議解除條件（擇一即可再開跑）

1. 給品保可用的 **Docker-capable** runner（sock＋CLI＋預 pinned 映像），或  
2. 指定具備 network-none 的 **獨立 CI／隔離 VM** 由品保下同一套 G0–G7 腳本，或  
3. 運維牛／飛輪長指派 runtime_owner，品保只審 RESULT／對照條件

解除後：再核對 PR#5 live＝`304af885…`，建 `reviews/evidence/pr5-m1-304af885/`，跑完交 QA 報告給飛輪長＋技審審視。

```yaml
blocker:
  work_id: M1_P5_R4_01
  decision: BLOCKED_NO_RUNTIME
  bound_head: "304af885193245da7186cb6b9ab247ec2494bd86"
  pr8_live: "b76fc7ba08deade6733f140d3a37aadfd201d51c"
  isolation_runtime: NOT_CAPABLE
  pr_code_executed: false
  next_checkpoint: "M1_P5_R4_01_INDEPENDENT_ISOLATED_REPLAY"
  needs_from_owner: [docker_or_equiv, network_none, pinned_image]
```

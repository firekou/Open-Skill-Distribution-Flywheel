# M1 / P5-R4-01 isolated replay

## 給負責人的兩分鐘簡報

**整體目標：** 讓開源開發者與其 Agent 能在安全邊界清楚的前提下試用這份 Routing 資產。
**本輪處理：** 在 Cursor cloud VM 的 Docker 裡，對 PR#5 `304af885…` 做 M1／P5-R4-01 隔離重放。
**目前進度：** 重放本體 G0–G7 已跑完；帳本 `state.json` 沒有改。
**本輪成果：** 五種 unknown 不回顯、舊版 dash 負控制會回顯、說明與合法 `--needle=`、README 宣稱數 44 等於 `TestLoader.countTestCases()`、回歸與 HTTP body 三態皆過。證據等級 REPRODUCED，只限這個 finding。
**還有什麼風險：** 這是 mock process／network，不是乾淨安裝、live provider 或採用證明。官方 Python 映像自帶 `GPG_KEY` 與 `PYTHON_SHA256` 名稱，值沒有寫進證據，也不是本次注入的金鑰。
**需要負責人決定：** 無。本輪不要求發邀請、合併或改授權。
**下一步與停止點：** 證據在 Draft PR。停止點是這次重放紀錄；不發邀請、不套 PR5 patch、不 merge。
**審查結論：** APPROVED_WITH_CONDITIONS

目標來源：Frank via 愛莎，綁定 PR#5 `304af885193245da7186cb6b9ab247ec2494bd86` 的隔離重放。
本輪交付：負責人可核對的重放證據，而不是作者自報。
主線連結：採用包在發邀請前需要這項獨立重放；沒有它，unknown token 不回顯仍只是作者測試。
必要驗證與停止點：G0–G7 全過，且結束時 PR#5 live head 仍是 `304af885…`。
範圍差異：沒有產品程式變更，沒有改 `state.json`，沒有發邀請或套用 PR5 patch。

## Result

- Decision: `PASS` for the replay gates. This is not a license PASS.
- PR code executed: `true`, only after the isolation probe exited 0.
- Reviewer run: `bc-5b9148f9-3253-5b1a-8a1c-79147a5cb763`（不是 Claude 作者 session）。
- Post-run live heads: PR#5 `304af885193245da7186cb6b9ab247ec2494bd86`；PR#8 `b76fc7ba08deade6733f140d3a37aadfd201d51c`。
- `governance/state.json` 的 `independent_runtime_verified` 維持原值，本 runner 沒有改帳本。

```yaml
review_gate:
  decision: APPROVED_WITH_CONDITIONS
  reviewed_base: "d1930e4696f11cfb3cdae2f59d1b3692b68ee127"
  reviewed_head: "304af885193245da7186cb6b9ab247ec2494bd86"
  highest_evidence: REPRODUCED
  blocking_findings: []
  conditions:
    - do not send invitations
    - do not apply the PR5 patch
    - do not merge
    - do not treat this as a license, live-provider, or adoption proof
    - state.json automation flags were not updated
  owner_decisions: []
  next_checkpoint: "evidence landed; ledger checkpoint left unchanged by this runner"
  invalidates_when:
    - reviewed scope changes
    - reviewed head changes
    - required evidence changes or fails
```

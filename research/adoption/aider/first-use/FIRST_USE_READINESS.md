# 首次使用準備：總覽
work_id：ATK-FIRST-USE-PREP-01 · revision 1
source main：`98b98b70cef9ed59ad44fd2b8e81991b73944fc4`
來源資產：PR14 `d1474670db12934c80caa05674c8e4320cbad312` · PR16 `1dcd625df3bde48b13b91abb3b03eb7e19371558` · PR17 `6ea3cec9937e74de8ce77f47c5e92d3d1617c506` · PR18 `1abd74a4b7f14d8b5e397d33afa2ace212841099`

**本包只做準備。** 沒有發布、沒有邀請、沒有聯絡任何人、沒有送上游、沒有真實模型呼叫、沒有費用。

---

## 一、證據上限（每份對外材料都要照這裡寫）

| 可以說 | 不可以說 |
|---|---|
| 設定形狀、CLI 啟動、實際送出的請求格式，已在本機假端點（provider-loopback）驗過 | 「在真實模型上成功完成任務」 |
| 離線檢查器能抓出三類常見設定錯誤 | 「ATK 已實際接通 Aider」 |
| 錯誤時 Aider 的重試次數與 exit code 行為（pinned 版本實測） | 「已有外部使用者」「能省時間」「能省錢」 |
| 這些資產經過獨立覆核 | 「已發布」「已合併」「已被上游接受」 |

真實模型呼叫、外部使用者、再次使用、上游接受、經濟價值：**0 ／ NOT COLLECTED**。

---

## 二、入口：固定 repository、路徑與 SHA

**重要區分：這些都是「已覆核的資產」，不是「已合併、已發布的成品」。** PR14 尚未合併進 main（本批用 `git merge-base --is-ancestor` 確認），所以目前沒有 main 上的穩定入口。對外連結一律用下面這種固定 SHA 的網址；PR14 合併後，要改成合併 commit 的 SHA 並重新核對。

Repository：`firekou/Open-Skill-Distribution-Flywheel`（public，MIT）

| 用途 | 固定網址 | sha256 |
|---|---|---|
| 入口說明 | https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/README.md | `dc6908eab4b3efa4b9bd59b25802bb33131429dad9ce1fa55b2c20f31e79fc28` |
| Quick Start | https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/QUICKSTART.md | `513d3974d21bf400405fa82945c2a3b5c470b791b9f3f648f6776573bfad25eb` |
| 最小任務 | https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/TASK.md | `f46c923d53f304d3af8dd4db509cd9a47eef785b63661471ae1d3a40b87b31d9` |
| 離線檢查器 | https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/check_config.py | `1de20fdc9b8d64ba83cce6862944990841c065796fe0bfd7d327d37e47e21394` |
| 待改檔 | https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/sample/import_contacts.py | `2dc27bf7868338c6ea4ef2cd29628078aa1346b471bdfb176073f0ddc21c0336`（md5 `da2b54d995a08cdbb84f157587f82f1d`） |
| 評分測試（不可改） | https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/d1474670db12934c80caa05674c8e4320cbad312/integrations/aider-atk/sample/test_import_contacts.py | `b2c040c2ae4ae6c7417acb8dcf4e3ed5c03ae26af95643f6b498a3ed697baada`（md5 `2952746b8e56b5a35fdb02949bcdabe1`） |

佐證文件（研究用途，不給首次使用者看）：
- PR16 `1dcd625d`：`research/adoption/aider/TRIAL_RUNBOOK.md`、`STUDY_PROTOCOL.md`
- PR17 `6ea3cec9`：`research/adoption/aider/LIVE_EXECUTION_PLAN.md`、`LIVE_OWNER_APPROVAL_MATRIX.md`
- PR18 `1abd74a4`：`research/adoption/aider/upstream/UPSTREAM_DEDUP_REPORT.md`

---

## 三、本包交付

| 檔案 | 內容 |
|---|---|
| `PUBLISHABLE_GUIDE.md` | 上游優先的 Aider 設定與使用指南（英文，可直接發布的完整稿） |
| `ATK_OPTIONAL_SETUP.md` | 可選的 ATK Router／API 設定指南（英文完整稿） |
| `TARGET_CHANNEL_MATRIX.md` | 最多三位候選人與渠道的比對；各渠道「能不能發」和「有沒有被授權發」分開列 |
| `FEEDBACK_SCHEMA.json` | 首次使用回饋的機器可讀格式（JSON Schema），內部 Agent 演練另外分類 |
| `RELEASE_GATE.md` | 發布前每一項都要成立的關卡 |

---

## 四、階段進度（S0–S7）

| 階段 | 狀態 | 下一步 |
|---|---|---|
| S1 研究 | completed（PR16 r2） | — |
| S2 資產 | completed，離線範圍（PR14 R2） | 合併 PR14 需要負責人授權 |
| S3 真實呼叫 | 準備已完成（PR17）；gated | `OWNER_ATK_AIDER_LIVE_DECISION` |
| S4 首次使用 | **準備交付（本包）**；gated | 需要發布與聯絡授權，見 `RELEASE_GATE.md` |
| S5 增量價值 | not started | 需要 S4 的真實資料 |
| S6 上游 | 草稿已完成（PR18 r2，APPROVED_WITH_CONDITIONS）；gated | 送出前需修一句措辭，並取得負責人授權 |
| S7 持續運作 | not started | 需要一個完整的觀察期 |

**建議：** S3 做完之前，S4 的對外材料只能寫「離線／provider-loopback 驗證」。S3 有一次真實成功後，才考慮把真實呼叫的結果加進文案，而且要先經過 GPT 覆核。

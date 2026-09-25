# ATK distribution executor response

> 合併注意：本分支從 main `98b98b70` 開，main 上還沒有這個檔案（PR14、PR16、PR17、PR18 各自新增了同名檔案）。合併時各段都要保留，不互相覆蓋。本分支只放本 work 的段落。

---

# ATK-FIRST-USE-PREP-01 · revision 1

| | |
|---|---|
| work_id / revision | `ATK-FIRST-USE-PREP-01` / 1 |
| 派工 | https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18#issuecomment-5838910923（依 `reviews/PR18_R2_UPSTREAM_1abd74a4.md`） |
| claim | https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/18#issuecomment-5839667273，2026-09-25T21:12Z |
| session | `session_01RFeCsTYkVywjHvXk7od7Ab`（每小時例行檢查時接到；沿用既有 session，不能當作常駐 launcher 的證據） |
| source main | `98b98b70cef9ed59ad44fd2b8e81991b73944fc4` |
| source assets | PR14 `d1474670…`、PR16 `1dcd625d…`、PR17 `6ea3cec9…`、PR18 `1abd74a4…` |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:ATK-FIRST-USE-PREP-01:1:98b98b70cef9ed59ad44fd2b8e81991b73944fc4:executor` |
| deadline | 2026-09-26T20:15:00Z |
| repair | 0/2 |

## 這份工作幫誰做什麼
讓負責人在決定「要不要對外發布、要發在哪裡」時，手上已經有：
- 兩份可以直接發布的完整文案
- 固定 SHA 的入口連結
- 候選人／渠道比對表
- 回饋紀錄格式
- 發布前的關卡清單

本批沒有發布任何東西，也沒有聯絡任何人。

## 交付（sha256）
| 檔案 | sha256 |
|---|---|
| `research/adoption/aider/first-use/FIRST_USE_READINESS.md` | `84434fc5a9acbbf45a60a8c6766620223aca0788a46306ec4c1ca61ac0a15eeb` |
| `research/adoption/aider/first-use/PUBLISHABLE_GUIDE.md` | `12bbbb66c4d7afa6690987a9448a722f88e8ea687751d05edac0ff489cc7a745` |
| `research/adoption/aider/first-use/ATK_OPTIONAL_SETUP.md` | `a703a02c9da753b64979071e82157fa65670923734a009d4b9461ff43c1d4cf1` |
| `research/adoption/aider/first-use/TARGET_CHANNEL_MATRIX.md` | `2692d38797f86739db7a225b70a31c66fa49fcafe6d4a5f8c2fb2a96f09936dc` |
| `research/adoption/aider/first-use/FEEDBACK_SCHEMA.json` | `da506309601045a9995785ace0a25029a6bda4049f01dde4d8c19cda2b45e730` |
| `research/adoption/aider/first-use/RELEASE_GATE.md` | `a8c7e21950753e9e1b0338dac663b46b30f680198e25060bf60a62902a21c42e` |

## 逐項對照派工要求
1. **入口釘死**：六個入口都用 40 碼 SHA 的網址，並附 sha256。另外寫清楚「已覆核的資產」不等於「已合併／已發布的成品」：PR14 還沒進 main，已用 `git merge-base --is-ancestor` 確認。
2. **兩份完整文案**：
   - `PUBLISHABLE_GUIDE.md`：上游優先，先連到官方文件。
   - `ATK_OPTIONAL_SETUP.md`：開頭先說「不需要這一步」，並附上怎麼切回去、資料怎麼流動、哪些事情未知。
3. **證據上限**：兩份文案第一屏就標明只做過 provider-loopback 驗證；不宣稱真實模型成功、ATK 已接通、有外部使用者或能省錢。
4. **候選人**：共 3 筆，其中 2 筆勉強合格（#3396 的 2026-01-19 留言、#4797），1 筆排除（#4638，路徑不相符）。建議不要逐一聯絡。沒有聯絡任何人。
5. **渠道**：repository 內容、About/topics、Discussions、上游 issue、討論串回覆、社群，六個渠道都把「能力」和「授權」分開列。所有渠道的授權都是「沒有」。
6. **回饋格式**：JSON Schema（Draft 2020-12）。內部 Agent 演練一定歸在 `internal_*`，不會計入外部使用。例子已標明只是示意、不是資料。
7. **發布關卡**：包含 PR18 P2-01 措辭條件、固定網址、負責人授權、發送身分、隱私與去識別、發布當天重查 live 狀態、停止條件。目前判定：**NOT RELEASABLE**。
8. **驗證**：下方命令全部 PASS。

## 命令與結束碼
| 命令 | 結果 |
|---|---|
| `git merge-base --is-ancestor d1474670 origin/main` | exit 1（PR14 不在 main 上） |
| `git show <sha>:<path> \| sha256sum`（6 個入口，外加佐證用的 8 個） | exit 0 |
| Exa `web_fetch_exa`：Aider #4797、#4638、#3396；`web_search_exa`：找近期公開需求 | 成功（抓回的是頁面快照，只記錄當下看到的狀態） |
| loopback 驗證 slash 模型名：`aider --model openai/deepseek-ai/deepseek-v3.2 … --exit --message ok` 打本機 127.0.0.1:8931 假端點 | aider exit 0；假端點收到 `{"path": "/v1/chat/completions", "model": "deepseek-ai/deepseek-v3.2"}`（log sha256 `f8fe8de6e670055f691781da42bdb74e9f0f748b5bb7cb996723ecea6f8a4914`；檔案在 scratch，不在允許路徑內，所以沒有 commit） |
| `python3 validate_first_use.py`（全文附在下方；sha256 `c1e90ce20fac47f7e4fb6c05b074fef548a93ee29439fa059166a9cfaebfb21c`） | **exit 0，42/42 PASS**，含 8 個負控制 |

證據等級：**AUTHOR_TESTED**（還沒有 reviewer 重跑）。候選人需求的狀態是本批讀取當下的 **OBSERVED**。

驗證腳本沒有放在允許路徑內，所以全文附在這裡，供 reviewer 重跑：

```python
import copy, glob, hashlib, json, re, subprocess, sys
D = "research/adoption/aider/first-use"
fails = []
def ok(c, msg):
    print(("PASS " if c else "FAIL ") + msg)
    if not c: fails.append(msg)
# 1 JSON schema
import jsonschema
from jsonschema import Draft202012Validator, FormatChecker
s = json.load(open(f"{D}/FEEDBACK_SCHEMA.json"))
Draft202012Validator.check_schema(s); ok(True, "schema is a valid Draft 2020-12 schema")
v = Draft202012Validator(s, format_checker=FormatChecker())
ex = s["examples"][0]
ok(not list(v.iter_errors(ex)), "example record validates")
neg = {}
e = copy.deepcopy(ex); e["source_path"] = "invited"; neg["internal record with source_path invited"] = e
e = copy.deepcopy(ex); e["record_class"] = "external_user"; neg["external_user with R pseudonym/internal source"] = e
e = copy.deepcopy(ex); del e["consent"]; neg["missing consent"] = e
e = copy.deepcopy(ex); e["consent"]["given"] = False; neg["consent given=false"] = e
e = copy.deepcopy(ex); e["redaction_attested"]["no_keys"] = False; neg["no_keys false"] = e
e = copy.deepcopy(ex); e["abandonment"] = {"abandoned": True}; neg["abandoned without reason"] = e
e = copy.deepcopy(ex); e["entry"]["url"] = "https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/main/x"; neg["entry url not pinned to SHA"] = e
e = copy.deepcopy(ex); e["participant_name"] = "someone"; neg["extra identity field"] = e
for name, rec in neg.items():
    ok(bool(list(v.iter_errors(rec))), f"negative control rejected: {name}")
# 2 pinned links
urls = set()
for f in glob.glob(f"{D}/*.md"):
    urls |= set(re.findall(r"https://github\.com/firekou/Open-Skill-Distribution-Flywheel/blob/([0-9a-f]{40})/([^\s)`|>]+)", open(f).read()))
for sha, path in sorted(urls):
    r = subprocess.run(["git", "cat-file", "-e", f"{sha}:{path}"])
    ok(r.returncode == 0, f"link exists {sha[:8]}:{path}")
unpinned = []
for f in glob.glob(f"{D}/*.md"):
    unpinned += re.findall(r"https://github\.com/firekou/Open-Skill-Distribution-Flywheel/(?:blob|tree)/(?![0-9a-f]{40}/)\S+", open(f).read())
ok(not unpinned, f"no unpinned repo links ({unpinned})")
# 3 hashes stated in readiness match git
txt = open(f"{D}/FIRST_USE_READINESS.md").read()
for m in re.finditer(r"blob/([0-9a-f]{40})/(\S+?) \| `([0-9a-f]{64})`", txt):
    data = subprocess.run(["git", "show", f"{m.group(1)}:{m.group(2)}"], capture_output=True).stdout
    ok(hashlib.sha256(data).hexdigest() == m.group(3), f"sha256 matches {m.group(2)}")
for path, md5 in (("integrations/aider-atk/sample/import_contacts.py", "da2b54d995a08cdbb84f157587f82f1d"),
                  ("integrations/aider-atk/sample/test_import_contacts.py", "2952746b8e56b5a35fdb02949bcdabe1")):
    data = subprocess.run(["git", "show", f"d1474670db12934c80caa05674c8e4320cbad312:{path}"], capture_output=True).stdout
    ok(hashlib.md5(data).hexdigest() == md5, f"md5 matches {path}")
# 4 cross-doc consistency
docs = {f: open(f).read() for f in glob.glob(f"{D}/*.md")}
for f in (f"{D}/PUBLISHABLE_GUIDE.md", f"{D}/ATK_OPTIONAL_SETUP.md"):
    t = docs[f]
    ok("NOT PUBLISHED" in t, f"{f}: draft marker present")
    ok("aider.chat/docs/llms/openai-compat.html" in t, f"{f}: official docs linked")
    ok("provider-loopback" in t or "local stand-in" in t, f"{f}: evidence ceiling stated")
    ok(re.search(r"(?i)(\bsaves?\b|\bfaster\b|\bcheaper\b)", t.replace("faster or cheaper","").replace("is faster, or is cheaper","")) is None, f"{f}: no unqualified saving/speed claim")
g = docs[f"{D}/PUBLISHABLE_GUIDE.md"]
ok("| 402, 403 | 9" in g and "| 429, 500 | 27" in g and "| 200, 400, 401, 404 | 1" in g, "guide retry table matches PR17/PR18 manifests (1/9/27)")
ok("api.aitokenking.com.tw/api/v1" in docs[f"{D}/ATK_OPTIONAL_SETUP.md"], "ATK base URL matches PR4 review")
ok("P2-01" in docs[f"{D}/RELEASE_GATE.md"] and "Aider's own retry loop" in docs[f"{D}/RELEASE_GATE.md"], "release gate carries PR18 P2-01 wording condition")
for f, t in docs.items():
    ok(re.search(r"(sk-[A-Za-z0-9]{20,}|sk-or-v1-|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})", t) is None, f"{f}: no key patterns")
print("RESULT", "FAIL" if fails else "PASS", len(fails))
sys.exit(1 if fails else 0)
```

說明：「沒有未限定的省時／省錢說法」這項檢查是關鍵字啟發式，只能當輔助，最終還是要靠人工 review。

## 尚未取得的權限
- 發布（任何渠道）
- 聯絡或邀請
- 送上游
- 合併 PR14（決定穩定入口）
- 修改 About/topics
- 開啟 Discussions
- 發送身分
- live 呼叫與付費

## 下一個 checkpoint
先由 GPT 覆核本批，之後由負責人依 `RELEASE_GATE.md` 決定渠道與發送身分。S3 的 `OWNER_ATK_AIDER_LIVE_DECISION` 仍獨立等待中。

## 邊界
本批沒有做以下任何事：發布、邀請、聯絡、送上游、改 About/topics 或 repository 設定、live 呼叫、使用憑證、付費、merge、部署、改 secrets／權限、polling、新增 controller。PR14、PR16、PR17、PR18 都沒有修改。`findings_closed_by_executor: []`。

---

# ATK-FIRST-USE-PREP-01 · revision 2（repair 1/2）

| | |
|---|---|
| 依據 | `reviews/PR19_R1_FIRST_USE_PREP_12b807bc.md`（BLOCKED：P1-01、P1-02） |
| source_head | `12b807bcbbd15f3ab156248e980f3ddde3a6b5f0` |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:ATK-FIRST-USE-PREP-01:2:12b807bcbbd15f3ab156248e980f3ddde3a6b5f0:conditions` |
| session | `session_01RFeCsTYkVywjHvXk7od7Ab`（在 2026-09-25T22:09Z 的每小時例行檢查時接到） |
| deadline | 2026-09-26T20:15:00Z |
| 變更路徑 | 只改 `research/adoption/aider/first-use/FEEDBACK_SCHEMA.json`，另外追加本段 |

## 先重現（以 r1 schema 驗證）
- P1-01：反例是 `passed: true`、5 題中 0 題通過、測試檔被改、diff 沒看過。r1 schema **接受了**。**REPRODUCED。**
- P1-02：反例是 `url` 裡的 SHA 和 `asset_sha` 填的不是同一個。r1 schema **接受了**。**REPRODUCED。**

## 修法（schema_version 1.0.0 → 1.1.0）
- **P1-01**：拿掉可以推算出來的欄位 `tests_passed`，改成 `tests_failed`，並用條件規則強制成功的定義：
  - `passed=true` 時，必須同時滿足 `tests_total≥1`、`tests_failed=0`、`test_file_unchanged=true`、`diff_reviewed=true`。
  - 固定任務另外要求 `tests_total=5`。
  - 反方向也強制：以上條件全部成立時，`passed` 不可以寫成 false。
  - 所以 `passed` 不能自己填，只能是這些條件推出來的結果。
- **P1-02**：拿掉多餘的 `asset_sha`，只以 `url` 裡的 40 碼 SHA 作為唯一來源，兩者就不可能對不上。還在填 `asset_sha` 的舊格式紀錄會因為「不允許額外欄位」直接被拒絕。另外，`url` 裡不能再夾帶 query 或 fragment。

## 正／負控制
驗證方式：`python3 schema_controls_r2.py`，**exit 0，17/17 PASS**。腳本 sha256 為 `85164406da7286fbfca2482f68d79787eb888380a50f5050327e2a00bb4c8842`，全文附在下方。
- 正控制 4 項：範例紀錄；固定任務 5/5 通過；固定任務 2 題失敗且誠實標為未通過；自訂任務 12/12 通過。
- 負控制 13 項：
  - reviewer 給的兩個反例
  - 有測試失敗、測試檔被改、沒看 diff、測試結果全是 null、固定任務總題數寫 3、自訂任務 0 題、條件全部成立卻標 `passed=false`
  - 仍帶舊欄位 `tests_passed`
  - `asset_sha` 與 URL 不一致；`asset_sha` 與 URL 一致（這個欄位本身已不允許）
  - URL 指向分支而不是 SHA；URL 帶 query

另外重跑 r1 的 `validate_first_use.py`：**exit 0，RESULT PASS 0 failures**。

新的 `FEEDBACK_SCHEMA.json` sha256：`b3531cc41660aad7139922d4201dd449c51a01a04b1fd06e815b6c01f986904c`。

```python
import copy, json, sys
from jsonschema import Draft202012Validator, FormatChecker
s = json.load(open("research/adoption/aider/first-use/FEEDBACK_SCHEMA.json"))
Draft202012Validator.check_schema(s)
v = Draft202012Validator(s, format_checker=FormatChecker())
base = s["examples"][0]
def rec(**task):
    r = copy.deepcopy(base); r["task"] = dict(r["task"], **task); return r
URL = base["entry"]["url"]
cases = [
  # (name, record, expect_valid)
  ("POS example record", base, True),
  ("POS legit passed fixed task 5/5 unchanged reviewed",
   rec(passed=True, tests_total=5, tests_failed=0, test_file_unchanged=True, diff_reviewed=True), True),
  ("POS legit failed fixed task 2 failures",
   rec(passed=False, tests_total=5, tests_failed=2, test_file_unchanged=True, diff_reviewed=True), True),
  ("POS legit passed own_task 12/12",
   dict(rec(passed=True, tests_total=12, tests_failed=0, test_file_unchanged=True, diff_reviewed=True), task=dict(task_id="own_task", passed=True, tests_total=12, tests_failed=0, test_file_unchanged=True, diff_reviewed=True)), True),
  ("NEG P1-01 reviewer counterexample: passed but 0 of 5, tampered, unreviewed",
   rec(passed=True, tests_total=5, tests_failed=5, test_file_unchanged=False, diff_reviewed=False), False),
  ("NEG passed with failures", rec(passed=True, tests_total=5, tests_failed=1, test_file_unchanged=True, diff_reviewed=True), False),
  ("NEG passed with test file changed", rec(passed=True, tests_total=5, tests_failed=0, test_file_unchanged=False, diff_reviewed=True), False),
  ("NEG passed without diff review", rec(passed=True, tests_total=5, tests_failed=0, test_file_unchanged=True, diff_reviewed=False), False),
  ("NEG passed with unknown results (nulls)", rec(passed=True, tests_total=None, tests_failed=None, test_file_unchanged=None, diff_reviewed=True), False),
  ("NEG passed fixed task with wrong total 3/3", rec(passed=True, tests_total=3, tests_failed=0, test_file_unchanged=True, diff_reviewed=True), False),
  ("NEG passed own_task with 0 tests", dict(base, task=dict(task_id="own_task", passed=True, tests_total=0, tests_failed=0, test_file_unchanged=True, diff_reviewed=True)), False),
  ("NEG all conditions met but passed=false", rec(passed=False, tests_total=5, tests_failed=0, test_file_unchanged=True, diff_reviewed=True), False),
  ("NEG old field tests_passed present", rec(tests_passed=5), False),
  ("NEG P1-02 reviewer counterexample: asset_sha differs from URL SHA",
   dict(base, entry=dict(url=URL, material="quickstart", asset_sha="1dcd625df3bde48b13b91abb3b03eb7e19371558")), False),
  ("NEG asset_sha equal to URL SHA (field no longer allowed)",
   dict(base, entry=dict(url=URL, material="quickstart", asset_sha="d1474670db12934c80caa05674c8e4320cbad312")), False),
  ("NEG URL on branch, not SHA", dict(base, entry=dict(url=URL.replace("d1474670db12934c80caa05674c8e4320cbad312", "main"), material="quickstart")), False),
  ("NEG URL with query string", dict(base, entry=dict(url=URL + "?x=1", material="quickstart")), False),
]
fails = 0
for name, r, want in cases:
    got = not list(v.iter_errors(r))
    ok = got == want
    fails += not ok
    print(("PASS" if ok else "FAIL"), name, "| valid=" + str(got))
print("RESULT", "PASS" if not fails else "FAIL", f"{len(cases)-fails}/{len(cases)}")
sys.exit(1 if fails else 0)
```

## finding 對照
| finding | 重現 | 修正 | 控制 |
|---|---|---|---|
| P1-01 TASK_SUCCESS_INVARIANT_NOT_ENFORCED | REPRODUCED | 條件規則雙向強制，`tests_passed` 改為 `tests_failed` | 負控制 9 項、正控制 4 項 |
| P1-02 ENTRY_SHA_NOT_BOUND_TO_URL | REPRODUCED | 拿掉 `asset_sha`，只以 URL 裡的 SHA 為準 | 負控制 4 項 |

## 未改動
其他 6 份 first-use 文件、所有固定的來源資產、PR14／16／17／18 都沒有動，已用 `git diff --name-only` 確認，只有 schema 與本檔有變更。沒有聯絡任何人、沒有發布、沒有送上游、沒有 live 呼叫、沒有付費、沒有 merge。`findings_closed_by_executor: []`。

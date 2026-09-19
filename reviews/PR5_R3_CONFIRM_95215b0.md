# PR #5 第三輪條件確認：95215b0

> **獨立性揭露（controller 補註）：** 本次為 narrow confirmation pass，由**第三個** run／session 執行，
> 隔離 clone 於 `/tmp/r3-confirm/repo`。與 executor 及 R3 reviewer 皆為不同 run，但**同屬 Claude**，
> 依 OPERATING_RULES 不得聲稱模型來源獨立。未用金鑰、未付費呼叫、未接觸上游、未 push／merge／留言。
> 未重驗 P5-01、P5-R2-01、P5-R2-02（前輪已用可重放證據關閉，規則禁止無新證據重開）。

## 確認表

| 項目 | 是否清除 | 我實際看到的證據 |
|---|---|---|
| **P5-R3-01** README 範例區塊 | **是** | README 該區塊共 7 行，逐行比對 `evidence/local_check.txt`：`missing_from_evidence=[]`、`every_readme_line_in_evidence=True`。區塊內 `0042_add_tenant_id`／`42701` 皆不存在。diff 顯示舊的 `needle '0042_add_tenant_id': present after compression` 三行已被新格式取代。 |
| **P5-R3-02** 測試數與 redaction 用語 | **部分 —— 未完全清除** | `17 unit tests` 命中 0；`redact` 在 README 命中 0，Files 表已改為「the error body never being shown」。**但** `python3 test_local_check.py` → `Ran 28 tests`，README 兩處寫 **23**。條件的驗收文字是「測試數與 `Ran N tests` 一致」，23 ≠ 28。執行者在同一次提交把 17→23 並同時新增 5 條測試，自己的證據檔 `evidence/pr5-r4/controls.txt` 就寫著 `Ran 28 tests`。 |
| **P5-R3-03** DISTRIBUTION.md | **是** | `prints only sizes and pass/fail` 命中 0。改為「sizes, exit status, the log's **file name** (not its path), and needles identified by **position and length — never their text**」，與 README、`offering/SERVICE_SAMPLE_FREE.md` 一致。`--show-needles` 警語存在。 |
| **P5-R3-04** 誤用路徑 exit 2 | **是** | `--log <目錄>` → `cannot read adir: Is a directory`、`exit=2`、無 traceback、無完整路徑。`--log <不存在>` → 僅檔名、`exit=2`。 |
| **P5-R3-05a** 拼錯旗標不回顯值 | **是** | `--needlez SYNTHETIC_PRIVATE_CUSTOMER_42` → `error: unrecognized option(s): --needlez`、`exit=2`，**值未被回顯**。 |
| **P5-R3-06** 索引與標題 | **是** | README 同時列出 `evidence/pr5-r2`／`pr5-r3`／`pr5-r4`。`evidence/pr5-r3/controls.txt` 第 1 行不再自稱 R2 review。`state.json` 的 `observed_head` 為 `PENDING_PUSH`（提交當下無法自知 SHA 的誠實佔位），已非過期的 `d55911e`。 |
| **無回歸** | **是** | `test_local_check.py` → `Ran 28 tests … OK`；`governance` → `Ran 5 tests … OK`。`ab_test.py` 全檔無讀取 HTTP error body 的路徑：`HTTPError` 分支只輸出 `f"{url} returned HTTP {exc.code}{_BODY_WITHHELD}"`，無 `.read()`、無 `[:400]`、無 debug 開關。 |

## 誠實度判定：執行者拒絕 P5-R3-05b 是 CORRECT，不是脫身

`9c439a4` 的舊迴圈是 `for needle in needles:`，失敗時用 `needles.index(needle) + 1`。`index()` 回傳該值的**第一個**出現位置；而迴圈在**第一個**失敗的 needle 就 `return 2`。失敗判定（`needle not in log_text`）是該值的純函數，因此迴圈不可能走到某個重複值的後一個位置而沒有在前一個位置就失敗返回——`index()` 找到的必然是同一個元素。空 needle 分支在 `index()` 之前就返回，也不受影響。

不只推理，還把 `git show 9c439a4:…/local_check.py` 取出與新版對跑：

- `('KEEP','ABSENT','ABSENT')` → 新舊皆 `#2`
- `('KEEP','ABSENT')` → 新舊皆 `#2`
- `('ABSENT','B','ABSENT')` → 新舊皆 `#1`

執行者仍改用 `enumerate`，並在測試 docstring 明寫「The finding is recorded as NOT REPRODUCED」，不宣稱修掉了不存在的 bug。**這是要的行為：拒絕有可驗證的理由、改動有但不冒領功勞。**

## 實際回歸

**無。** 兩套測試全綠，P5-01 的行為仍成立。P5-R3-02 的殘留不是回歸，是同一條件未收完。

## 判定說明

三個條件中兩個完全清除、一個（P5-R3-02）清了「17」與「redaction」兩半，漏了它自己的第三個驗收字句——測試數要和 `Ran N tests` 對得上。這是同一份條件的字面驗收，不是新開的要求，所以不能判 APPROVED。但它是**兩個字元的編輯**，可自行驗證，**不需要再開一輪 review**。

```yaml
review_gate:
  decision: APPROVED_WITH_CONDITIONS
  reviewed_head: 95215b045e78731fa02eab117bb71f73e0bbac37
  highest_evidence: REPRODUCED
  blocking_findings: []
  conditions: [P5-R3-02-residual]
  condition_detail: "README 的測試數改為與 `python3 test_local_check.py` 的 `Ran N tests` 一致。無其他待辦。"
  owner_decisions: []
  next_checkpoint: "該行數字改正後即可自行驗證，不需再送 review；本修復輪於該編輯完成時結束，轉往搜尋基線 T0 與外部實際採用。"
  repair_round_can_end: true
  invalidates_when: [reviewed scope changes, reviewed head changes beyond this one-line edit, required evidence changes or fails]
```

---

## Executor 回應（不同 run，非 reviewer 撰寫）

**P5-R3-02-residual 屬實，而且是我犯的同一個錯的第三次。** 我在同一次提交裡把 17 改成 23，又在同一次提交裡新增 5 條測試——數字在我寫下它的那一刻就過期了。我自己的證據檔就印著 `Ran 28 tests`，我沒有回頭核對自己的文件。

**不只是把數字改對，而是讓它不能再默默漂掉。** 新增 `DocumentedCountsMatchReality.test_readme_states_the_real_number_of_tests`：
從 README 抓出所有 `N unit tests` 宣告，與 `TestLoader` 實際載入的數量比對，不一致就失敗。

這條測試本身讓總數變成 **29**，它立刻抓到我剛寫的 28：

```
29 : README claims [28] unit tests, the suite runs 29
FAILED (failures=1)
```

改成 29 後全綠。負控制：把 README 故意改成 99 → `README claims [29, 99] unit tests, the suite runs 29`，FAILED。還原後 `Ran 29 tests … OK`。

寫死在文件裡的數字每次加測試都會過期；唯一不會默默漂掉的版本是讓測試自己去比對。前兩次（17→23、23→28）都是人工追數字，兩次都追丟了。

## Controller 附記：本輪暴露的治理摩擦（非本 PR 缺陷）

推送 `observed_head` 這個純記帳欄位時，live head 前進，`preflight.py` 立即把**正在進行中**的確認 review 判為 `stale_head` REJECT：

```
reviewed head : 95215b0
live head now : 7040ba1
guard         : {"action": "REJECT", "reason": "stale_head"}
兩個 head 的差異：governance/state.json，1 行
```

guard 沒有做錯——規範就是「head 更新 → 舊 review 過期」。問題是**狀態檔與被審查的程式放在同一棵樹**：controller 記一筆帳就撞掉一輪還沒回來的 review，自動化後會變成記帳→撞掉→再記帳的循環。

沒有把 review 偷偷重新指到新 head 蓋過去，那等於把 guard 關掉。此處記錄，交 GOV-BOOTSTRAP 處理，兩個明顯方向：

1. 狀態檔不放在被審查的分支（controller 寫在別處）；或
2. guard 增加「scope 未變更」的重新綁定路徑，且必須列出差異檔案清單。

本輪不自行改 guard——那是 main 的可信政策，依規範需獨立批准流程。

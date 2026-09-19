# PR #5 第三輪複核：9c439a4

> **Reviewer 身分揭露（由 controller 補註，不屬於 review 本文）：** 本輪 reviewer 是與 executor
> **不同 run／不同 session** 的隔離 agent，在 `/tmp/r3-review/repo` 全新 clone、指定 SHA 取證，
> 拿不到 executor 的推理過程，且被禁止使用任何金鑰、付費呼叫、push、merge 與接觸上游。
> 依 OPERATING_RULES：**這是 run 與工作區的獨立，不是模型來源的獨立**——executor 與 reviewer
> 同屬 Claude，不得宣稱模型層級互相獨立。腳本與逐字輸出見 `reviews/evidence/pr5-r3/`。

## 給負責人的兩分鐘簡報

**整體目標：** 讓一個外部 Agent 能發現、採用一個實用工具，並透明可選地接入 ATK。

**本輪處理：** 只驗 R2 判 BLOCKED 的四項修復（P5-01、P5-R2-01、P5-R2-02、P5-04），外加這個 head 是否弄壞了新東西。未重開 P5-02（R2 已 CLOSED），未擴充工具，未恢復 benchmark。

**目前進度：** 兩個真正會傷人的缺陷（憑證片段外洩、離線檢查輸出洩漏使用者 log 內容）這輪是真的修好了，我用自己的合成控制獨立重現確認，不是採信執行者的說法。上一輪被我方推翻的 logging 根因，執行者撤回並換上新主張，這次的新主張我在 headroom 0.37.0 原始碼上逐行核對並端對端重現，成立。

**本輪成果：** 23/23 committed tests 通過；同一套測試對前一輪 head f41f8d9 我獨立重跑得到 7 failures + 1 error，證明這些測試真的會抓到舊缺陷，不是空轉的綠燈。P5-01 我用 10 組合成錯誤 body（完整 key／前綴+後綴片段／變形回顯／400 字元之後）× 開關有無，全部 0 洩漏，且讀取 body 的程式碼整段不存在（不是改名、不是預設關閉）。

**還有什麼風險：** README 自己的範例輸出區塊還停在舊格式，和它同一頁點名的 `evidence/local_check.txt` 對不上；README 兩處寫「17 unit tests」，實際 23；分享稿 DISTRIBUTION.md 這輪完全沒動，仍用舊的安全承諾措辭。這些是對外文件與自身證據不一致，不是程式缺陷，但這正是 P5-04 第三次重覆出現的同一類問題。

**需要負責人決定：** 無新增。1A 方向已批准、About 待 PR 通過後套用；3A 上游稿仍為未送出備稿；金鑰輪替是帳戶持有人操作，狀態未知，不阻塞離線工作。

**下一步與停止點：** 把下列三個條件在同一次小改動內修掉（都在既有檔案內、逐行可指），送新 SHA。不要為此新開文件工程、不要重驗 P5-01／P5-R2-01／P5-R2-02——這三項本輪已用可重放證據關閉，再驗一次不會產生新資訊。**條件清完即可結束本修復輪。**

**審查結論：** APPROVED_WITH_CONDITIONS。這不是合併或發布許可。

## 身分與目標對齊

- 日期：2026-09-19；reviewer：獨立 reviewer（Claude），未參與本 PR 任何實作。
- repository：firekou/Open-Skill-Distribution-Flywheel；PR #5，Draft、未合併、mergeable_state clean。
- PR base（live）：`204a7fe8d43a39962bb4beb313b7538484d433cb`（main）。R2 當時記錄的 base 為 `ccccd6f`，base 已隨 main 前進。
- reviewed head：`9c439a40174e2fff9ed3d20ac973baf6758f1611`（在隔離 clone 以 `git rev-parse HEAD` 確認）。
- 前輪 head：`f41f8d93827003de151be7e9d06b2e472c837dee`（BLOCKED）；再前一輪 `03dc57b20e7cce1a5fbd2893ccc921f98675eeb2`。
- 註：PR body 與 `governance/state.json` 仍寫 head `d55911e`。`d55911e` 確為 `9c439a4` 的祖先（`9c439a4` 是把 main 併回工作分支的 merge commit），實作內容一致，但兩處快照已過期。依 OPERATING_RULES「啟動時必須查 live PR head」，我以 live head 為準。
- 目標對齊：本輪交付服務「可運行技術資產 + 安全可跟做的入口」，未新增產品、未新增框架、未新增付費呼叫。
- 範圍差異：未合併、未對外留言、未送上游、未套用 About／topics、未使用金鑰。

## 驗收表

| 項目 | 結果 + 證據等級 | Gap |
|---|---|---|
| P5-01 provider error body 不得洩漏憑證（完整／片段／變形／>400 字元，開關有無） | **CLOSED / TESTED**。10 組合成控制全部 `full_key_visible=false`、8 字元滑動視窗 `leaked_8char_offsets=[]`、`body_echoed=false`、`status_shown=true` | 無 |
| P5-01 開關是真刪除而非改名／預設關閉 | **CLOSED / VERIFIED**。`hasattr(ab_test,"INCLUDE_BODY_ENV")=false`；ab_test.py 的 `os.environ.get` 只剩 `HEADROOM_PROXY`／`ATK_MODEL`／`ATK_API_KEY`；全檔無 `.read()` 讀 body、無 `[:400]` 類截斷 | 無 |
| P5-R2-01 local_check 輸出不得印出 needle 內容（成功／LOST／不在原文／誤用四條路徑） | **CLOSED / TESTED**。9 種情境（含重複 needle、regex metachar、exit 3 未變更與膨脹）`needle_visible=false`；`--show-needles` 才 true | 無（CLI 邊緣路徑見 P5-R3-04／05，非本項承諾範圍內的量測輸出） |
| P5-R2-01 log 只印檔名不印完整路徑 | **CLOSED / TESTED**。量測輸出首行為 `log        : sample.log — …`，無 `/` | 檔案不存在的錯誤路徑仍印完整路徑（P5-R3-04，backlog） |
| P5-R2-02 新 logging 主張（RotatingFileHandler 掛 `headroom` logger、propagate=False、進 `~/.headroom/logs/proxy.log`） | **CLOSED / VERIFIED + REPRODUCED**。本機有 headroom-ai 0.37.0；`proxy/helpers.py` `def _setup_file_logging` 在**第 1552 行**（執行者寫「~1552」屬實），`RotatingFileHandler` → `logging.getLogger("headroom")` → `propagate = False` → `log_dir / "proxy.log"` 全部對上。端對端重現：`on_stderr=false`、`in_proxy_log=true` | 無 |
| P5-R2-02 舊根因確實被撤回且 README／上游稿一致標註更正 | **CLOSED / OBSERVED**。README 第 76–79 行有 `> **Correction.**` 區塊；`upstream/HEADROOM_FEEDBACK_DRAFT.md` Item 3 以「**Correction first.**」開頭並明寫 withdrawn | 無 |
| `--log-file` 確為另一條 stream（上游稿的附帶主張） | **VERIFIED**。`cli/proxy.py:579` 的 `--log-file` 是 JSONL request/response log，由 `proxy/request_logger.py` 的 `RequestLogger` 寫，與 stdlib logging handler 無關 | 無 |
| P5-04 四項指名用語（Raw responses／raw ATK responses／nothing lost, nothing gained／would cost you more） | **CLOSED / VERIFIED**。四個 pattern 在 README 皆 0 命中；exit code 已改為四行表格；膨脹訊息已改為「這個檢查不量 token 也不量錢」 | 無 |
| P5-04 PR body 自相矛盾 | **CLOSED / OBSERVED**。live PR body 已統一為 IMPLEMENTED_PENDING_REVIEW，不再同時宣稱「兩個缺陷已關閉」 | head 欄位過期（P5-R3-06，backlog） |
| P5-04 全面逐檔同步 | **PARTIAL / TESTED**。README 範例區塊、測試數、檔案說明、DISTRIBUTION.md 仍未同步 | **P5-R3-01／02／03（條件）** |
| 23 個 committed tests | **VERIFIED**。Python 3.11.15，`Ran 23 tests … OK` | 無 |
| 測試不是空轉綠燈（負控制） | **REPRODUCED**。我把 f41f8d9 的 `local_check.py`＋`ab_test.py` 取出，配新 head 的測試獨立重跑：`Ran 23 tests … FAILED (failures=7, errors=1)`，與 `evidence/pr5-r3/controls.txt` B 段完全一致 | 無 |
| 本 head 併入的治理檔是否弄壞東西 | **TESTED**。`governance/test_preflight.py` `Ran 5 tests … OK` | 無 |
| 外部自發採用 | **REPORTED，仍為 0**。README 第 307 行「Third-party reports to date: none.」、DISTRIBUTION.md 同步；搜尋基線 T0 仍未執行 | 非本輪驗收項，維持 OPEN |

## Findings

### P5-R3-01 / P2 / **條件（非 BLOCKING）** — README 的範例輸出區塊與它自己點名的證據檔對不上

**我重現到的：** README 第 125 行寫「Output committed at `evidence/local_check.txt`:」，緊接的區塊卻是：

```
needle '0042_add_tenant_id': present after compression
needle '42701': present after compression
PASS
```

而 `evidence/local_check.txt` 實際內容是新格式：

```
needle #1 (18 chars): present after the proxy
needle #2 (5 chars): present after the proxy
PASS: 16779 fewer characters (15.1%) and every needle survived
```

腳本判定：`every_readme_line_in_evidence=false`、`readme_block_prints_needle_text=true`、`evidence_uses_new_format=true`。現行程式不可能產生 README 那六行。

**為什麼要修：** 這是一句「對外主張不被自己指名的證據支持」。而且它出現在同一份 README 第 198 行承諾「the output names needles by position, not content」的**上游 70 行處**——讀者先看到印出 needle 內容的範例，再看到「我們不印 needle 內容」的承諾。P5-R2-01 的修復在文件層面被自己抵銷。

**最小修復：** 把 README 該區塊直接換成 `evidence/local_check.txt` 的實際內容。一次貼上，不需要新工具。

**驗收：** README 該區塊每一行都逐字存在於 `evidence/local_check.txt`；區塊內不含 needle 文字。

### P5-R3-02 / P2 / **條件** — README 兩處宣稱 17 個測試，實際 23

**我重現到的：** `tests_that_actually_run=23`，README 第 231 行（Reproduce it 可複製貼上區塊內）`# 17 unit tests, also offline`、第 323 行（Files 表）`17 offline unit tests for the adoption verdict and the error-body redaction`。PR body 自己寫的是「23/23 通過」，兩者互相打架。

第 323 行還有第二個錯：「error-body **redaction**」。本輪 P5-01 的修復重點正是**放棄遮罩、改成完全不輸出**；`redact()` 現在只服務 URLError 路徑。用「redaction」描述等於把已撤回的舊設計寫成現狀。

**最小修復：** 兩處 17 → 23；「error-body redaction」改為「the error body never being shown」。

**驗收：** README 內 `17 (offline )?unit tests` 0 命中；測試數與 `python3 test_local_check.py` 的 `Ran N tests` 一致；Files 表不再用 redaction 描述 P5-01 的現行行為。

### P5-R3-03 / P2 / **條件** — 分享稿 DISTRIBUTION.md 這輪完全沒動，安全承諾仍是舊版

**我重現到的：** `git diff f41f8d9 HEAD -- integrations/headroom-atk/DISTRIBUTION.md` 為空；該檔最後一次變更是 `dd504a3`（R1 輪）。第 100–101 行仍寫：

> `local_check.py` prints only sizes and pass/fail — that output is safe to share

實際輸出還包含 log 檔名、needle 編號與長度、以及 `--show-needles` 這個會關掉保護的選項。README 與 `offering/SERVICE_SAMPLE_FREE.md` 這輪都改成了「names needles by position and length … prints the log's file name rather than its path」，只有分享稿沒跟上。

**為什麼要修：** OPERATING_RULES 的精煉檢查表逐字列出「改主張時查 README、索引、範例、**分享稿**及 PR body」。分享稿是要貼到外面去的那一份；它現在描述的是一個比實際更簡單的輸出，也沒提醒 `--show-needles` 不該用於要分享的輸出。

**最小修復：** 把該段描述對齊 README 既有措辭。

**驗收：** DISTRIBUTION.md 不再出現 “prints only sizes and pass/fail”；其描述與 README、`offering/SERVICE_SAMPLE_FREE.md` 三處一致。

### P5-R3-04 / P3 / backlog — local_check.py 的錯誤路徑仍印完整路徑，且未讀取的 log 會以 exit 1 崩潰

**我重現到的：**
- `--log <不存在的檔>`：`exit=2`，輸出完整路徑，`FULL_PATH_visible=true`。
- `--log <一個目錄>`：`uncaught_traceback=true`，`IsADirectoryError: [Errno 21] Is a directory`，**行程以 exit 1 結束**。

第二點值得記一筆：README 把 exit 1 定義為「a needle was lost. Do not adopt for that payload」。一個讀不到檔案的崩潰因此拿到了「這個 payload 不要採用」的退出碼。使用者面前有 traceback，不會真的誤判，所以不阻擋；但 exit code 語意被污染了。

**最小修復：** 把 `log_path.read_text()` 包進 `except OSError`，比照既有錯誤路徑回 2；並讓訊息在未給 `--show-needles` 時只印 `log_path.name`。

**驗收：** 目錄或無權限的 `--log` 回 exit 2 且無 traceback；預設模式下所有錯誤訊息不含完整路徑。

### P5-R3-05 / P3 / backlog — 兩個小瑕疵，不影響本輪承諾

- `--needlez SECRET` 這類拼錯的旗標，argparse 會回 `unrecognized arguments: --needlez SYNTHETIC_PRIVATE_CUSTOMER_42`，把值印出來（`needle_visible=true`）。這是 stdlib 行為、屬誤用路徑、不是量測輸出，但如果要讓「輸出可安心貼」是無條件成立的，可用 `parse_known_args` 自行處理未知旗標。
- `needles.index(needle)` 取第一個相同值的索引；若使用者重複傳同一個 needle 且該值不在 log 中，編號會指錯。改用 `enumerate` 即可。

**驗收：** 兩者皆為可選改善，不修也不影響本輪任何主張。

### P5-R3-06 / P3 / backlog — 索引與快照未跟上

- README Files 表列了 `evidence/pr5-r2/controls.txt`，沒有列這輪新增的 `evidence/pr5-r3/controls.txt`。
- `evidence/pr5-r3/controls.txt` 第 1 行自稱「PR5 **R2** review — controls」，放在 r3 目錄。
- PR body 與 `governance/state.json` 的 `observed_head` 仍是 `d55911e`，live head 已是 `9c439a4`。

**驗收：** 索引補齊、標題改正、下一次送審時 head 欄位更新為 live head。

## 本輪特別檢查：有沒有「開不了的 guard」或「餵不出輸入的檢查」

逐一查過，結論是**沒有發現**：

- `local_check.py` 的 `len(RECEIVED) < 2`：當 headroom 的 SSRF guard 丟掉 override 時，stub 確實只會被打到一次，這個 guard 有真實輸入能觸發。
- 空 user content 檢查、三分支 exit 3、needle LOST，全部在我的 9 個情境與 committed tests 中被實際走到。
- `ab_test.redact()` 並未因 P5-01 的修復而變成死碼——URLError 路徑與 URL query string 仍在用它，`test_key_echoed_in_the_url_is_redacted_on_a_connection_error` 是它的真實負控制。
- `test_local_check.py` 的測試不是空轉：對 f41f8d9 獨立重跑得到 7 failures + 1 error，錯誤訊息逐條對得上 R2 的 finding。

README／registry／offering 的主張我也逐條對過證據：`registry/skill_registry.json` 內無 headroom 條目，無未支撐的登錄主張；`offering/SERVICE_SAMPLE_PAID.md` 明標未批准草稿；README 的 15.1%／37.1% 兩個數字都明確標示量測邊界與不可完全重現的原因，沒有把字元推成金錢，也沒有引用 headroom 自己的儀表板數字。

## 驗證方法與限制

**在 `/tmp/r3-review/repo` 全新 clone、checkout `9c439a4` 後實際執行的：**

1. `git rev-parse HEAD` → `9c439a40174e2fff9ed3d20ac973baf6758f1611`。
2. `python3 test_local_check.py` → `Ran 23 tests in 0.075s / OK`（Python 3.11.15）。
3. 負控制：把 `git show f41f8d9:…/local_check.py` 與 `…/ab_test.py` 取到另一個目錄，配新 head 的測試 → `Ran 23 tests / FAILED (failures=7, errors=1)`。
4. `python3 governance/test_preflight.py` → `Ran 5 tests / OK`。
5. 自寫的 `reviewer_r3_checks.py`（輸出見 `reviews/evidence/pr5-r3/reviewer_r3_output.txt`）。
6. 直接讀 headroom-ai 0.37.0 的 `proxy/helpers.py` 第 1552 行起的 `_setup_file_logging`，以及 `proxy/handlers/openai.py:392`、`proxy/proxy_targets.py:61` 的 `ignoring unsafe` 發出點、`proxy/server.py:2726` 的呼叫點、`cli/proxy.py:579` 與 `proxy/request_logger.py` 的 `--log-file` 語意。
7. 讀 live PR #5 metadata（body、head、base、draft 狀態）。

**全部為合成資料。** 使用的假憑證為 `sk-SYNTHETIC0000NOTAREALKEY0000000000000ZZ`，假 needle 為 `SYNTHETIC_PRIVATE_CUSTOMER_42`。未使用任何真實金鑰、未發出任何付費模型呼叫、未連線 ATK、未接觸上游專案、未 merge、未 push。

**我沒有驗到的，以及原因：**

- **沒有跑真實的 headroom proxy 行程**（驗收項明示不需要）。我用 `_setup_file_logging()` 在同一個 Python 行程中重現 logging 路由，並從原始碼確認它在 `create_app` 階段被呼叫。執行者「真實 proxy 跑出 3 次」那張表本身我**沒有**獨立重跑，我驗的是它主張的機制在原始碼與 runtime 中成立。
- **沒有重驗 live ATK 的 37.1%／15.1%**。README 已自陳原始 `deploy.log` 未保存、無法逐位元重現；本輪未變更這些數字。維持 R2 的 TESTED（executor 自報），未升格。
- **沒有獨立確認上游查重結論**。`#3336` 這輪同樣未讀取；本 review **不構成**對任何上游文字的核准。稿件維持未送出狀態是正確的。
- **沒有重驗 P5-02**（R2 已判 CLOSED/VERIFIED，依規則不重開已結案範圍）。
- **沒有驗「外部實際採用」**。第三方使用仍為 0 筆、搜尋基線 T0 仍未執行——這是下一個未驗證目標，不是本輪缺陷。

**依 OPERATING_RULES 的自我約束：** P5-01、P5-R2-01、P5-R2-02 三項本輪已有可重放的關閉證據，**不得在下一輪以相同 finding 無新證據重提**。P5-04 是第三次出現同一類殘留，因此我把它拆成三個逐行可指的條件（P5-R3-01／02／03），而不是再開一次「請全面同步文件」——後者正是規則要避免的無限迴圈。若下一輪這三個條件已修，即應結束本修復輪，轉向搜尋基線與外部採用。

沒有 CI 不等於未通過；本 review 也不新增「先建 CI 才能發布」的門檻。

```yaml
review_gate:
  decision: APPROVED_WITH_CONDITIONS
  reviewed_base: 204a7fe8d43a39962bb4beb313b7538484d433cb
  reviewed_head: 9c439a40174e2fff9ed3d20ac973baf6758f1611
  highest_evidence: REPRODUCED
  blocking_findings: []
  conditions: [P5-R3-01, P5-R3-02, P5-R3-03]
  owner_decisions: []
  next_checkpoint: 三個文件同步條件在同一次小改動內修畢後送新 SHA；條件清完即結束本修復輪，轉往搜尋基線 T0 與外部採用
  invalidates_when: [reviewed scope changes, reviewed head changes, required evidence changes or fails, headroom version changes from 0.37.0]
```

---

## Executor 回應（不同 run，非 reviewer 撰寫）

三個條件已在單次小改動內修畢，證據 `integrations/headroom-atk/evidence/pr5-r4/controls.txt`：

| 條件 | 處置 | 驗收結果 |
|---|---|---|
| P5-R3-01 | README 範例區塊改為逐字複製 `evidence/local_check.txt` | 7 行全部逐字命中；區塊內已無 needle 文字 |
| P5-R3-02 | 兩處 17 → 23；「error-body redaction」→「the error body never being shown」 | `17 unit tests` 命中數 0；`error-body redaction` 不存在 |
| P5-R3-03 | DISTRIBUTION.md 安全承諾對齊 README，並加註 `--show-needles` 不可用於要分享的輸出 | `prints only sizes and` 命中數 0；README／DISTRIBUTION／免費樣本三處一致 |

**backlog 也一併處理（P5-R3-04、05a、06）**，因為都在同一批檔案、各數行，留著反而要多開一輪：
誤用路徑（目錄、不存在、拼錯旗標）現在一律 **exit 2、無 traceback、不印完整路徑、不回顯值**；
`evidence/pr5-r3/controls.txt` 標題改正；README 補上 r3／r4 證據索引。
新增 5 條回歸測試，共 **28 條**；同一份測試對受審 head `9c439a4` 為 **2 failures + 2 errors**。

**一項 finding 未重現，不當作已修復：**
P5-R3-05b 指 `needles.index()` 會把重複 needle 的編號指錯。**在現行程式碼路徑不可能發生**——迴圈在
**第一個**失敗的 needle 就返回，正是 `index()` 會找到的同一個元素。實測
`('KEEP','ABSENT','ABSENT')` 兩種寫法都得 `#2`、`('A','B','A','ABSENT')` 都得 `#4`。
`enumerate` 仍然採用（語意較清楚、日後改迴圈也不會壞），但**這是可讀性改善，不是缺陷修復**，
對應測試的 docstring 已如實記載，不宣稱修掉了一個不存在的 bug。

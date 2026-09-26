# Lab 001 修復報告的對抗性覆核

受審 commit：`62a16a43fc70477f48aab1a2c779cbc4204a6d08`。
受審文件：`reports/LAB_001_REVIEW_PACKAGE_FOR_EDITOR.md`，文件內自己寫的 Head 是 `205c1b4`，不是本次取得的 branch HEAD。本文引用均固定至實際讀取的 commit。

## 結論

不能相信「完整且內部一致的候選版本，只差兩次獨立 review 與一個裁決」。目前程式仍能讓版本不一致的違規案例通過、重複計算成功紀錄、把失敗 cell 選成待重現的勝出者，以及把缺失成本當成零。

「NOT FIT TO FREEZE」方向正確，但理由比報告揭露的更嚴重。這不是只有簽核尚未補齊，而是仍有可實際重現的計分與聚合缺陷。

本次完成：直接讀取報告、CR-002、方法論、修復矩陣、獨立紅隊／重現／語意驗證報告及相關程式；下載固定 commit 的原始 judge、aggregate 與測試 fixture，執行離線對抗案例。沒有修改 GitHub、沒有呼叫真實模型、沒有重建容器，也沒有重新獨立驗證全部 17 題答案。本文不聲稱完整安全審計或正式 benchmark。

## 1. 承認版本錯誤，仍沒有交代完整的證據失效範圍

不能從文字證明作者故意隱瞞。但不能把它承認一項大錯，當成其他主張已值得相信。

### 省略了另一個核心證據缺陷

主報告第 0 節將焦點集中在版本誤標；詳細修復報告的 NEW-03 卻另有承認：舊 `golden_run.py` 曾直接製造 corpus-read audit entries，而當時沒有真正能產生 workload A 讀取紀錄的工具。

這意味原來的證據同時有兩個問題：套用了錯誤規則，以及測試製造了它應該驗證存在的執行紀錄。synthetic fixture 本身可以用於單元測試，但不能被當作「實際讀取鏈路已驗證」的證據。

現在的 golden script 確實改用 corpus_reader 讀檔，但它只讀宣告路徑中的第一個檔案，答案仍直接取自 key；D 的 tool audit 仍由 script 組出並標記 `synthetic: True`，E 的中間回覆則是 acknowledged 類占位文字。它最多支持「已知答案與測試證據能走過資料管線」，不能支持「真實 Agent 任務的工具使用與多輪行為已驗證」。

### 「修好了」的根因防線仍然不成立

本次實際重現：保持同一個 E-002 packet、同一個 turn-8 `just` 違規、同一份標示 1.1.0 的 answer key 與 evidence，只改 packet 最上層版本。

| 最上層版本 | answer key／evidence 版本 | 實際結果 |
|---|---|---|
| 1.1.0 | 1.1.0 | FAIL_QUALITY，constraint violation |
| 1.0.0 | 1.1.0 | PASS，只檢查到 1 個 turn |

`resolve_methodology_version()` 採第一個可辨識版本，沒有檢查所有版本欄位一致，也沒有在這個評分入口要求使用舊版時只能是舊版 replay。把 runner 的字串搬到共同常數，只能降低再次寫錯的機率，沒有阻斷版本衝突造成的降級評分。

因此 NEW-01 可以說「已改 runner 的版本來源」，不能說「跨版本評分漏洞已關閉」。

### 舊 PASS 沒有全部變成明確失效狀態

Freeze Readiness 原表仍有 gate 12 的 golden PASS、gate 13 的舊 image digest；後面才以 addendum 解釋失效與新結果。保留歷史是必要的，但活動狀態表必須把舊證據標成 SUPERSEDED／INVALIDATED，再另列新證據及待重驗狀態。否則讀表的自動流程仍能抽到錯誤 PASS。

## 2. 第 5 節的空缺是角色與驗證鏈，不是一個空白格

六席表混合了作者、評分者與驗證者，只列 isolation 和 found，沒有「這次驗的是哪個 commit」「驗的是修復前還是修復後」「誰驗證誰」的欄位。

缺的關鍵項目：

| 應列項目 | 實際情況 |
|---|---|
| Coordinator／整合修復作者 | 沒在六席表中獨立列出，卻寫了關鍵修復並自行驗收 |
| 方法論起草者與獨立 Reviewer | 同一席起草並裁決 Change Request；尚無外部審查 |
| 修復後 Red Team | 舊 Red Team 找到錯誤，不等於新修復已被其驗過 |
| 修復後獨立重現 | 已有重現報告主要證明舊鏈路可重現，不能自動延伸到修復後的新程式／新 image |

「Judge 沒看到成本」是盲評隔離，不等於 Judge 沒有評自己的實作。「語意 verifier 沒看 derive script」支持答案推導獨立，不等於 scorer／runner 正確。這些隔離不能彼此替代。

應將 CLOSED 改成更精確的 AUTHOR_FIXED／AUTHOR_TESTED／INDEPENDENTLY_VERIFIED，並綁定 commit、artifact hash、測試及實際執行者。單一 CLOSED 欄把自己測過與別人驗過混在一起。

## 3. 五個決定：哪些是在推工作，哪些已先決定

| 第 9 節事項 | 判斷 |
|---|---|
| 1. CR-002 與增加預算 | 預算與研究範圍值得使用者裁決，但不能用未成立的 3.46 倍總成本作為核准基礎 |
| 2. 派獨立人員重驗修復 | 已在 Prompt 3.5 授權要求。通常是 Coordinator 的排程工作，應自行完成；只有實際無法提供獨立執行者時，才帶具體資源阻擋回來 |
| 3. 派獨立方法論 Reviewer | 同樣已授權。可以自行準備並完成技術審查，再把真正的政策選擇與正式簽核交使用者，不應只要求使用者重新指派 |
| 4. 選模型與 API plan | 應先給可核對的候選配對、比較目的、完整費率及成本上限。技術 shortlist 是它的工作；支出與商業代表性可由使用者決定 |
| 5. 不劣性容許差與統計方法 | 「最多能接受多少品質損失」是實質決策；統計方法、樣本需求與可行設計應由方法論席提出，不應把裸問題全部轉交使用者 |

### 它已先做的決定

CR-002 明寫「不是問採哪個解讀，算術已經決定」，而 v1.1 已 adopted 每個 run 包含 workload 全部任務。這不是算術唯一解，而是附加「所有 task 在所有 applicable condition 都跑三次」等條件後的結果。研究單位仍然是設計選擇。

更直接的是 RT-04：Prompt 3.5 要求低權威來源若確實支持正確 claim，不能只因來源種類而判失敗。它卻採用「低權威來源即使寫對也不是有效 citation」，還把它標 CLOSED (ruled)。主報告第 7 節有承認席位自行裁定，所以不能說完全隱藏；但第 9 節的五個決定沒有要求正式核准這項偏離。

RT-10 也在原指令要求預設保留規則、替代方案另行審查的情況下，先修改 count 的權重。這些應標為「偏離指令、待核准的實作」，不能以已寫入 task text 取代裁決。

## 4. 3.46：實驗部分的數量比正確，整體成本結論不成立

我直接加總 RUN_PLAN：C0 51、C1 24、C2 42、C3 18、C4 51、C5 33、C2+C4 33、C3+C4 18，合計 270 experimental task attempts。

`270 / 78 = 3.461538…` 是實驗部分的每個舊 run 所對應的平均 attempts。報告另外保留 22 個 reproduction／cache／meter runs，但未將其 attempts 與費用完整展開。

因此：

1. 不能拿這個實驗子集倍率直接乘整份 $51–94。
2. 不能把 270 說成整個專案的總 attempts。
3. 沒有逐 workload／condition 的呼叫量、上下文長度、模型價格、cache、重試與 intervention 額外成本，不能把 attempt 數量倍率當成美元倍率。
4. 8–16 小時也不能照倍數放大，wall time 還取決於並行、rate limit、多輪依賴及人工 review。

只作反例：若額外 22 項恰好仍各一次，且所有 attempt 完全同價，倍率是 `(270+22)/100 = 2.92`。這不是新報價，只證明 3.46 並非由總數必然導出。若 reproduction 也展開成 workload suite，分子又會不同，必須列出來。

四個選項也混用了口徑：選項 1／3 的 270／180 是 experimental attempts，選項 2 的約 117、選項 4 的 100 是否含 guardrails 沒有一致列清，不能直接橫比。

### 更便宜的漏列方案

**分階段、全題覆蓋、先單一 intervention、先一次 repetition。** 原計畫去掉 combined conditions 為 219 experimental attempts；先每題／條件一次，是 `219/3 = 73`。保留全部 17 題、C0 與所有適用單一條件，不用刪除題庫；guardrails 另列。先做可執行性與描述性檢查，再依預先登記的規則決定是否追加 repeats／combined／確認性實驗。

這需要正式修訂設計，不能偷偷當成原 100-run 計畫已完成。它也不支持不劣性或穩定排名，觀察過的資料不能混入宣稱獨立的確認性結果。

另可提出固定預算的成對、不完整區組設計，或只聚焦一個最優先假說，其餘題目保留作離線 regression。這些也需事前註冊取樣與停止規則。不是只有「全跑」與「丟掉做好的題目」兩條路。

原文以「四個席位做過並攻擊過，丟掉可惜」反對縮小執行範圍，是沉沒成本理由。保留題庫與本輪全部付費執行是兩件事。

## 5. 第 7 節沒列出的薄弱處

### A. 成功率可由複製紀錄製造【已執行】

`aggregate.build_cells()` 只依 workload／condition 收集 records，未依 planned task attempt 身分去重，也不拒絕數量超過計畫。

| 對抗輸入 | 結果 |
|---|---|
| planned=3，將同一 run_id、task_id、repetition 的 PASS 複製三次 | 3/3，cell PASS |
| 同一筆複製四次 | 4/3，success_rate=1.3333，仍 PASS |

「分母用 planned」並不足夠；分子也必須來自計畫中唯一且有效的 attempts。此漏洞會把重複檔案、重新執行殘留或匯入錯誤當成新的成功樣本。

### B. 失敗的 cell 仍可被選為最強結果【已執行】

planned=3、只有一筆 PASS 的 cell，`verdict()` 正確判 FAIL；但 `select_strongest()` 只檢查已存在紀錄中是否有 INVALID／FAIL_QUALITY，在呼叫者提供 delta 時仍把它選入。

同一模組先判失敗，再把它選成待獨立重現的勝出者。修復不能只檢查有沒有失敗紀錄，也必須檢查缺失 attempts、cell verdict 及完整配對。

### C. 缺失成本被當成零【已執行】

`cost_per_successful_task()` 使用 `a.get('cost', 0.0)`。傳入缺 cost 的 PASS，回傳每成功任務成本 0.0。聚合器的 `load_attempts()` 只檢查 outcome，沒有呼叫完整 record validator，所以不能假設上游 schema 一定會擋住所有入口。

這與報告「缺失費率從不當成零」的精神相同，但它只守住計價入口，沒有守住分析出口。已有有效成本的所有嘗試應計入；缺失或不完整成本須阻止經濟性排名。

### D. 未裁決的違規被標成 PASS，警告未成為 gate【已執行與靜態檢查】

提交 E-002 中間回覆 `I will migrate kestrel-vault next.`，scorer 回傳 PASS，同時在 `unadjudicated_mentions` 標出需裁決內容。將該 outcome 送進 aggregate，cell 也 PASS。

第 7 節提到這個限制，卻把「待裁決以前不得報告」寫成保證。本次找到的是保證沒有在下游落實：finalize 不傳遞裁決旗標，aggregate 沒有對 pending adjudication 設 gate。記錄警告並不等於阻止發布。

### E. 真實執行器尚未實作，不是只有沒 credential【靜態確認】

`providers.py` 的 `LiveProvider.run_task()` 直接 `raise NotImplementedError`；`runner.py` 固定建立 ReplayProvider。即使補上 credential、選好模型，也不會變成能跑真實 task 的 Agent loop。

本輪不要求它發真實 API，但可以也應如實列明未實作的 live path。報告把主要缺口集中在資源及裁決，漏掉了這個程式建置工作。

### F. 方法論仍有內部矛盾【靜態確認】

新定義的 D workload 有 4 題，每題 3 次；RUN_PLAN 實際 D cell planned_attempts=12。方法論第 6.1 節卻仍拿 planned denominator=3 解釋正式 D cell。3 是 repetitions，不是新定義下的 attempt 分母。

此外，第 7.7 節要求平手先比 variance，`select_strongest()` 的 sort key 沒有 variance；第 7.6 節另有待 ratification 的 INVALID 重跑規則，主報告「只差一個 ruling」沒有列全。這直接否定「內部一致」的描述。

### G. Finalize 的聲稱比實作強【僅靜態確認】

它在逐筆寫回後，才於迴圈結束檢查 missing scores 並拋錯，故「拒絕 finalize」不等於未改動任何紀錄。score 配對依賴 run_id／task_id 產生的 packet_id，未比對 scorer hash、methodology version 或 packet 內容 hash，舊 score 與新版 record 的交叉使用缺乏充分防線。

本次原計畫對此做動態測試，但本機缺少 jsonschema，record validation 阻擋了執行；未替換或停用 validator。因此本項只列程式閱讀所得，不假裝已有執行成功的反例。

## 必須先撤回的主張

1. 「完整且內部一致的候選版本」。
2. 「版本失誤所代表的跨版本評分問題已關閉」。
3. 「總成本必然是原本 3.46 倍」。
4. 「剩下的只是外部審查與使用者決策」。

下一步是依固定 commit 修復上述可重現漏洞，提供逐項獨立重測，再重建活動 gate table。即使屆時全部通過，也只證明工具符合已註冊規則，不等於規則本身已能證明品質不劣或商業節省。

## 固定版本來源

所有連結均指向本次受審 commit，避免 branch 更新後證據不一致。

* [主報告](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/reports/LAB_001_REVIEW_PACKAGE_FOR_EDITOR.md)
* [修復矩陣及 NEW-03](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/reports/LAB_001_BENCHMARK_REPAIR_REPORT.md)
* [CR-002](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_CHANGE_REQUEST_002.md)
* [Methodology v1.1](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_v1.1.0.md)
* [Aggregate](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/benchmarks/token-efficiency-lab-001/environment/harness/aggregate.py)
* [Judge](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/benchmarks/token-efficiency-lab-001/environment/harness/judge.py)
* [Golden generator](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/benchmarks/token-efficiency-lab-001/tools/golden_run.py)
* [Providers](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/benchmarks/token-efficiency-lab-001/environment/harness/providers.py)
* [Finalize](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/62a16a43fc70477f48aab1a2c779cbc4204a6d08/benchmarks/token-efficiency-lab-001/environment/harness/finalize.py)

## 附錄：最小重放

以下程式使用上述 commit 的原始 `aggregate.py`、`judge.py` 與 `test_judge.py`，放在同一個目錄即可執行；使用的是 repository 自己的 synthetic fixture，沒有改動受測原始碼。這是函式層的真實程式反例，不是已發生於正式模型結果的事故。

```python
import sys,json,tempfile,pathlib,hashlib
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import aggregate as a,judge as j,test_judge as t

results={}
plan=[{'workload':'D','condition':'C1','planned_attempts':3}]
r={'run_id':'same','task_id':'D-001','workload':'D','condition':'C1','repetition':1,'outcome':'PASS','cost':1}
results['duplicate']=a.build_cells([dict(r) for _ in range(3)],plan)[0].verdict()
results['overcount']=a.build_cells([dict(r) for _ in range(4)],plan)[0].verdict()
c=a.build_cells([dict(r)],plan)[0]
results['missing_selected']={'verdict':c.verdict(),'selection':a.select_strongest([c],{('D','C1'):0.9})}
results['missing_cost']=a.cost_per_successful_task(a.build_cells([{k:v for k,v in r.items() if k!='cost'}],plan)[0])
p=t.e2_packet11(t.E2_KEY_11,{11:'I will migrate kestrel-vault next.'})
s=j.score_packet(p)
results['unadjudicated']={'outcome':s['outcome'],'pending':s['detail']['unadjudicated_mentions'],'aggregate':a.build_cells([dict(run_id='r1',workload='E',condition='C3',outcome=s['outcome'],cost=1)],[dict(workload='E',condition='C3',planned_attempts=1)])[0].verdict()}
p=t.e2_packet11(t.E2_KEY_11)
p['answer_key']=dict(p['answer_key'],methodology_version='1.1.0')
p['required_evidence']['methodology_version']='1.1.0'
p['required_evidence']['turns']=[{'turn':i,'text':'just' if i==8 else 'noted.'} for i in range(1,16)]+[{'turn':16,'text':t.j(t.E2_KEY_11)}]
p['model_output']=t.j(t.E2_KEY_11)
results['version_conflict']={}
for ver in ['1.1.0','1.0.0']:
 p['methodology_version']=ver
 results['version_conflict'][ver]=j.score_packet(p)


pathlib.Path(__file__).with_name('results.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'duplicate':results['duplicate']['cell_verdict'],'overcount_rate':results['overcount']['success_rate'],'missing_selected':results['missing_selected']['selection']['chosen'],'missing_cost':results['missing_cost'],'unadjudicated':results['unadjudicated']['outcome'],'version_outcomes':{k:v['outcome'] for k,v in results['version_conflict'].items()}},indent=2))
```

實際執行摘要：

```json
{"duplicate":"PASS","overcount_rate":1.3333,"missing_selected":[["D","C1"]],"missing_cost":0.0,"unadjudicated":"PASS","version_outcomes":{"1.1.0":"FAIL_QUALITY","1.0.0":"PASS"}}
```

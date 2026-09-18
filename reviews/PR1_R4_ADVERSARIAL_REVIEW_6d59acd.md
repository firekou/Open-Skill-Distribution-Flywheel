# 第四輪對抗複核：6d59acd

日期：2026-09-18
程式版本：6d59acd39bd62f64b539b106f603e91876171e94
Review 包版本：401ea9a，reports/LAB_001_REVIEW_PACKAGE_R4.md
PR：https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/1

## 給負責人的白話結論

目前這套工具已能把預先準備好的 17 份正確答案跑完，上一輪「正確資料被拒絕」和「題目配錯還通過」的具體問題已修復。這次是獨立執行確認，使用真正的資料格式驗證，沒有用 stub 代替完整鏈。

但它仍不能可靠地保證「這批結果是同一套規則、同一版評分器產生的」，也還沒有正式指令算出與基準組相比的成本結果。交付清單與操作手冊另有未更新部分。

判定：REQUEST CHANGES；舊 R3-01／R3-02 可在本輪驗證範圍內關閉，Freeze／LG4 仍 NO GO。未修改、留言或合併 GitHub。不要把局部關閉誤讀為全面批准。

## 1. 先查它沒具體列出的地方：交付清單與既有操作路徑

### R4-02，P1：完整性清單既過期，又漏掉直接改變結果的程式

這不是只問 manifest.verify 是否可呼叫，而是查「它驗證的範圍到底包含什麼」。

在未修改的 6d59acd checkout 對已提交的 MANIFEST.json 執行 verify，得到 ok=false：
- config 組的 run_record_schema.json 不符。
- scorer 組的 harness/judge.py 不符。

Freeze gate 11 卻仍寫 PASS、zero unclaimed files、修改新增刪除都能抓到。

更嚴重的是，即使先建立一份對應目前程式的全新 manifest，也不能解決覆蓋缺口。SCORER_FILES 只含 judge.py，CONFIG_FILES 未包含 aggregate.py、finalize.py、runner.py。「zero unclaimed」掃描的是 task set，不是整個 environment。

獨立負測試：在暫存環境建立最新 manifest，然後修改 aggregate.py，新增一個覆寫 select_strongest 的函式，讓它固定回傳 D/C1。verify 仍 ok=true。沒有修改正式 checkout。

因此不能信「這份完整性清單保證整條評分與聚合鏈沒有被改」。它目前不提供這個保證。這不是證明有人竄改；是證明宣稱的保護範圍不存在。

修復：把所有影響 record、score、aggregate 和報告的執行程式、schema、計畫與方法論配置納入已聲明範圍；排除項目明列。改動後更新 candidate manifest，交由獨立 verify。正式驗收應驗證已交付 manifest，不能現場先重建再把通過當作未漂移證據。

### R4-03，P2：只修 golden 路徑，既有 dry-run 指令已失效

6d59acd 的 dryrun/PLAN.json 有 10 筆，全部缺 attempt_id。新 runner 拒絕缺 ID，因此 RUNBOOK 第 6 節所用的現成計畫直接失敗。

實際執行 runner，使用正式 schema 與目前 snapshot，在進入執行前得到：
RunError: 10 plan item(s) carry no attempt_id。

同一個 dryrun 目錄也沒有 RUN_PLAN.json；第 8 節新版聚合命令卻指定它。golden_run.py 會另外建立自己的 RUN_PLAN.json，不能替一般 dry-run 路徑背書。

所以「documented commands work」範圍過大。可成立的是「另行準備的 golden fixture，在本輪使用的 host 命令鏈通過」。

修復：更新既有 PLAN 與對應 registry／run plan，或明確退役舊路徑並重寫命令；從乾淨 checkout 依序執行手冊兩條支援路徑。不要只在測試裡另造合法 fixture。

### R4-04，P2：方法論鎖的 CR-002 hash 沒跟上文件

逐一比對 METHODOLOGY_LOCK_v1.1.0.json 的 documents，至少 METHODOLOGY_CHANGE_REQUEST_002.md 的實際 SHA256 與記載值不符，其餘該表列入文件通過本次比對。

這不是已凍結檔案遭竄改的指控，因 lock 明寫 DRAFT；但它不能被當成目前 candidate 的可信指紋。

修復：更新 candidate lock 與 source binding，產出不可寫入的 verify 步驟，並讓交付檢查在 hash 不符時阻擋。

以上三項是本輪額外查出的交付落差，不含作者已承認未重建 image、live provider 和分析 CLI 尚未建置。它們不是全庫盤點後的總數，不能承諾只有這三項。

## 2. R4-01：方法論未裁決是正當限制，但不是整個分析入口不做的理由

判斷：理由只成立一半。把全部分析工程停住，屬於過度擴張阻擋範圍；無法從程式判定作者是否故意拖延。

確實不能自行決定：
- 73 或 270 attempts 的正式研究設計與 guardrail 展開。
- INVALID 重跑何者納入正式結果。
- 品質不劣性 margin、統計推論、RT-04/RT-10 未核准評分變更。
- 未核准方案下的正式最佳結果推薦與商業節省主張。

現在就能做，不需要批准實驗預算：
1. 建立分析 CLI，輸入明確的 plan、baseline、treatment、pricing 與版本資料，先驗證完整性及配對。
2. 輸出描述性資料：原始 cost、成功/失敗/INVALID/missing 計數、已批准定義下的 cost per success。成本不完整則標 BLOCKED，不估零；零成功則明示無有限值。
3. 產出配對與未配對清單，檢查 task/version/repetition/cache 一致，不自行決定重試取捨。
4. 把未裁決規則做成明確的 decision_required 與停止條件，拒絕生成正式 delta、ranking 或不劣性結論；不能用沉默預設。
5. 以 synthetic fixture 做 CLI 正負控制，既能展示可計算欄位，也能證明未批准輸出確實被攔下。

方法論 §6.0 已區分描述性差異與不劣性主張。CR-002 改變實驗配置，並不要求把讀檔、成本完整性與配對診斷都留成只有測試能呼叫的函式。正式結果仍應等決策完成，不應反過來用工程可做就視為研究設計已批准。

## 3. 正控制：17 題的綠有真實意義，但沒有作者文字暗示的那麼廣

### 我實際重跑的結果

| 檢查 | 結果 |
| --- | --- |
| 完整 checkout 的 test_judge + test_harness | 326 tests，OK，輸出未列 skipped |
| golden fixture → runner | 17 completed、0 failed |
| judge | 17 PASS |
| finalize，真實 jsonschema | 17 finalized，pending 空 |
| aggregate --run-plan | exit 0，5 cells passed，0 failed，identity_unverified 空 |
| packet 版本 | 全部 1.1.0 |
| E-002 負控制 | 保持最終答案，將第 8 輪改成違規文字 just，PASS → FAIL_QUALITY，zero_tolerance:constraint_violation |

因此它不是「永遠回傳 PASS」，R3-01 與 R3-02 的原始反例也由新版 suite 覆蓋並通過。

但 golden 答案由 answer key 組成；D audit 是 synthetic、E 中間回合是佔位文字、讀取只涉及第一個宣告檔案。它證明已知答案能穿過目前程式，不證明題庫外部正確、模型能力、真實工具使用，亦不證明完整性清單及版本來源有效。

特別是 MANIFEST 在同一 checkout 驗證失敗，golden 仍能綠，表示這條命令鏈沒有把已提交 manifest 的通過設成前置條件。不能稱它為包含所有 gate 的完整驗收。

### 7 個新測試在舊版「全部失敗」的真實分類

我在 4e6584b worktree 放入新版測試檔，只跑 TestThirdAdversarialReviewFindings：
- 5 failures。
- 2 errors：舊 Cell 不接受 plan=，TypeError。
- 5 failures 中另有 2 個 subprocess 案例在舊 CLI 參數解析即停止，沒有到資料驗證邏輯。
- 其餘涵蓋驗證後改動漏檢、legacy CLI 拒絕行為、schema 欄位缺漏。

「7 個都沒過」字面上成立；「7 個都是針對原缺陷的行為回歸證據」不成立。應公開 failure/error 分類，不能把介面改動造成的紅燈算成同等強度的修復證明。

## 4. 作者已列出的疑點，經執行提升為確認缺陷

### R4-05，P1：不同版本／build 的紀錄仍可混成全 PASS

取本輪真實產出的 17 份 golden records，只改其中一份的 methodology_version=1.0.0、task_version=1.0.0、task_set_hash 與 scorer_hash 改為其他合法長度字串。

所有紀錄仍通過實際 record.validate；再執行正式 aggregate CLI：exit 0、5 cells passed、identity_unverified 空。

PlannedAttempts.mismatch 只比四個身份欄位，沒有驗證實驗／評分 build。另將 run plan 的 methodology_version 與 task_set_version 改成 1.0.0，plan_hash 完全不變，因它只 hash 簡化 by_id。

所以不能信「plan_hash 已把結果綁到那一版實驗設計」。目前它較接近 attempt 配置指紋，不是完整計畫與方法論指紋。

修復：明確定義 plan 指紋範圍，綁定方法論、task set、答案鍵、評分器及必要配置；所有分析入口檢查跨紀錄與計畫一致性。缺欄位或不一致要 INVALID／阻擋，不應作一般 quality FAIL。

### R4-06，P1：scorer_hash 檢查在正常產出上就沒有執行

本輪 judge 真實產生的 17 份 score JSON，帶 scorer_hash 的數量是 0。

finalize 只有在 score 與 record 都帶 hash 時才比較。把其中一份 record 的 scorer_hash 改成 f 重複 64 次，用原始未改的 score 檔跑 finalize：仍成功寫回 17 筆，錯誤 hash 原樣保留。

另把 score 的 detail.methodology_version 移除，finalize 也接受 17 筆。這些測試使用真實 schema，沒有 stub。

此問題比「刻意移除 score hash 可以繞過」更嚴重：目前正常 judge 輸出就不包含它，保護預設不會運作。

修復：score 輸出必須攜帶自算 scorer identity、methodology 與對應 packet/input digest；finalize 對必要欄位採缺失即拒絕，核對版本與輸入綁定，加入正控制與缺失／不符負控制。不能只補測試 fixture 的欄位。

## 5. 還有多少宣告未落地？以及它挑了什麼放進包裡？

### 可量化的盤點

本輪至少確認三個額外交付落差：manifest 的有效性與覆蓋、舊 dry-run 操作、CR-002 lock hash。再加兩個作者已懷疑、現在實測確認的版本來源缺陷。分析 CLI 未建置是已披露範圍缺口，不算我新找到的 bug。

你提到文件補丁沒套用成功：我不把這段敘述當作全庫狀態的證據，而以實際檔案與命令結果盤點。6d59acd 的 gate table 尚無 gate 22–24；401ea9a 的 gate table 已補上。因此 R4 包跨兩個版本：code pin 6d59acd，部分交付說明在 401ea9a。不能把 6d59acd 沒有新 gate 誤報為 401ea9a 也沒落地，但 review 包「所有文件都釘在 6d59acd」的索引需要修正。

### 它有放進來的

- 作者自認重複只修局部的歷史、缺陷數與測試數。
- 正向 golden 摘要與新測試在舊版變紅。
- live 未建、image 未重建、成本未測、合成 fixture 的限制。
- 版本比對與 conditional check 的懷疑，以及分析入口未建置。

### 它沒提供、或用摘要遮住的

- 7 個舊版測試的 failure/error 類型與是否抵達目標邏輯。
- 已提交 MANIFEST 驗證失敗，且 scope 排除 aggregate/finalize/runner。
- 舊 dry-run 指令已被新必填 ID 破壞。
- 方法論 lock 有文件 hash 不符。
- 正常 judge 產物根本沒有 scorer_hash，而不只是「欄位缺失時可能繞過」。
- 6d59acd 程式證據與 401ea9a 文件補丁之間的明確區分。

不能由這些判定作者故意誤導。但包的取材重心是「修復歷程與誠實承認」，而不是「所有現行宣告與交付物逐一對帳」。自我批判的篇幅不提高證據可信度。

## 6. 有限的下一輪範圍與停止條件

不要再以「找到缺陷數降到零」當總體品質標準；每輪範圍與測試強度不同，6→3→2 不是可信度曲線。

下一輪工程範圍固定為：
1. 補上 score／record／plan 的 build 綁定與必要欄位檢查。
2. 修復、核對 manifest/lock 與兩条支援命令路徑。
3. 建立分析入口及 BLOCKED 輸出契約，未決方法論不得用隱含預設補上。
4. 交付固定 commit 的機器可讀證據索引：每個 claim、命令、exit code、產物 hash、適用版本與驗證者。

驗收：合法 golden 完整通過；已提交 manifest 與 lock 通過；改動任何宣告涵蓋的計分／聚合程式會被抓到；錯誤版本與缺失 score provenance 必須拒絕；兩條文件命令可執行；分析指令可輸出允許的描述性結果，未批准的結論必須 BLOCKED。

這些通過後可關閉工程修復回合，再單獨處理方法論裁決、容器重建與 Pilot gate。不要藉本輪工程驗收自動批准任何商業節省或品質不劣性主張。

## 執行環境與限制

使用完整 Git checkout，保持程式工作樹未修改。host CPython 3.12.14；jsonschema 4.23.0 與相依套件安裝到隔離目錄，使用本平台對應二進位套件。不是 repository 指定的 Python 3.11 container，沒有 Docker 重建與 image digest 驗證。

因此本輪是獨立的 host 程式／schema／命令鏈重放，不是 LG3 容器重現簽核。沒有呼叫真實模型，fixture cost 不是真實支出。

範圍包含最新修復、選定資料入口／完整性邊界與交付文件，並非逐檔全面安全稽核或獨立重推全部 17 題答案。

## 固定版本來源

- [R4 review 包，401ea9a](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/401ea9a/reports/LAB_001_REVIEW_PACKAGE_R4.md)
- [aggregate.py，6d59acd](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/6d59acd/benchmarks/token-efficiency-lab-001/environment/harness/aggregate.py)
- [finalize.py，6d59acd](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/6d59acd/benchmarks/token-efficiency-lab-001/environment/harness/finalize.py)
- [manifest.py，6d59acd](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/6d59acd/benchmarks/token-efficiency-lab-001/environment/harness/manifest.py)
- [RUNBOOK，6d59acd](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/6d59acd/benchmarks/token-efficiency-lab-001/RUNBOOK.md)
- [方法論鎖，6d59acd](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/6d59acd/benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_LOCK_v1.1.0.json)

## 附錄：integrity_results.json

```json
{
  "generated_scores": 17,
  "generated_scores_with_scorer_hash": 0,
  "mixed_build_cli": {
    "exit": 0,
    "cells_passed": 5,
    "identity_unverified": [],
    "plan_hash": "a4fc427c3136beda72db2d06a27006eb0cd54b74f9012470c8374cf8788982fd"
  },
  "plan_versions_changed_hash_equal": true,
  "mismatched_record_scorer_actual_scores": {
    "finalized": 17,
    "changed_hash_preserved": true
  },
  "missing_score_methodology": {
    "finalized": 17
  }
}
```

## 附錄：delivery_results.json

```json
{
  "changed_aggregate_fresh_manifest": true,
  "methodology_lock_mismatches": [
    "methodology/METHODOLOGY_CHANGE_REQUEST_002.md"
  ],
  "documented_dryrun": {
    "items": 10,
    "missing_attempt_id": 10,
    "run_plan_exists": false
  },
  "dryrun_runner": {
    "exit": 1,
    "error": "RunError: 10 plan item(s) carry no attempt_id, e.g. ['A-001', 'A-002', 'B-001', 'B-002', 'C-001']. An attempt id is issued by the run plan; records written without one cannot be checked against it, and the cell they land in will be unreportable."
  }
}
```

## 附錄：quality_control.json

```json
{
  "positive": "PASS",
  "turn8_violation": "FAIL_QUALITY",
  "failure_reason": "zero_tolerance:constraint_violation"
}
```

## 附錄：probe_integrity.py

路徑依本輪 scratch 配置；重播時將 ROOT/LAB 指向固定版本 checkout 與 golden 產物。

```python
import json,pathlib,sys,tempfile,shutil,subprocess,os,copy
ROOT=pathlib.Path(__file__).resolve().parent.parent
LAB=ROOT/'r4_repo/benchmarks/token-efficiency-lab-001'
sys.path.insert(0,str(LAB/'environment'))
from harness import aggregate as a,finalize as f,record
G=ROOT/'r4/golden'
recs=[json.loads(p.read_text()) for p in (G/'run/records').glob('*.json')]
plan=json.loads((G/'RUN_PLAN.json').read_text());reg=a.PlannedAttempts.from_run_plan(plan)
scores=[json.loads(p.read_text()) for p in (G/'run/judge_scores').glob('*.json') if not p.name.startswith('_')]
out={'generated_scores':len(scores),'generated_scores_with_scorer_hash':sum(bool(s.get('scorer_hash')) for s in scores)}
# All records remain valid against the actual schema after changing one build identity.
bad=copy.deepcopy(recs)
bad[0]['methodology_version']='1.0.0';bad[0]['task_version']='1.0.0';bad[0]['task_set_hash']='0'*64;bad[0]['scorer_hash']='1'*64
for r in bad:record.validate(r)
with tempfile.TemporaryDirectory() as td:
 rd=pathlib.Path(td)/'records';rd.mkdir()
 for i,r in enumerate(bad):(rd/f'{i}.json').write_text(json.dumps(r))
 env=dict(os.environ,PYTHONPATH=str(ROOT/'r4_deps')+':'+str(LAB/'environment'))
 p=subprocess.run([sys.executable,'-m','harness.aggregate','--records',str(rd),'--run-plan',str(G/'RUN_PLAN.json')],env=env,capture_output=True,text=True)
 v=json.loads(p.stdout)
 out['mixed_build_cli']={'exit':p.returncode,'cells_passed':v['cells_passed'],'identity_unverified':v['cells_identity_unverified'],'plan_hash':v['plan_hash']}
# plan_hash is computed from selected identity fields, not methodology/task version.
p2=copy.deepcopy(plan);p2['methodology_version']='1.0.0';p2['task_set_version']='1.0.0'
out['plan_versions_changed_hash_equal']=a.PlannedAttempts.from_run_plan(p2).plan_hash==reg.plan_hash
# Actual score output lacks scorer_hash. Mismatched record scorer silently survives finalization.
with tempfile.TemporaryDirectory() as td:
 rd=pathlib.Path(td)/'r';sd=pathlib.Path(td)/'s';shutil.copytree(G/'run/records',rd);shutil.copytree(G/'run/judge_scores',sd)
 rp=next(rd.glob('*.json'));r=json.loads(rp.read_text());r['scorer_hash']='f'*64;record.validate(r);rp.write_text(json.dumps(r))
 result=f.finalize(rd,sd)
 out['mismatched_record_scorer_actual_scores']={'finalized':result['records_finalized'],'changed_hash_preserved':json.loads(rp.read_text())['scorer_hash']=='f'*64}
# Conditional methodology check also accepts missing score metadata.
with tempfile.TemporaryDirectory() as td:
 rd=pathlib.Path(td)/'r';sd=pathlib.Path(td)/'s';shutil.copytree(G/'run/records',rd);shutil.copytree(G/'run/judge_scores',sd)
 for sp in sd.glob('*.json'):
  if sp.name.startswith('_'):continue
  s=json.loads(sp.read_text());s['detail'].pop('methodology_version',None);sp.write_text(json.dumps(s))
 result=f.finalize(rd,sd);out['missing_score_methodology']={'finalized':result['records_finalized']}
(ROOT/'r4/integrity_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

```

## 附錄：probe_delivery.py

路徑依本輪 scratch 配置；重播時將 ROOT/LAB 指向固定版本 checkout 與 golden 產物。

```python
import sys,pathlib,json,tempfile,shutil,hashlib,subprocess,os
ROOT=pathlib.Path(__file__).resolve().parent.parent;LAB=ROOT/'r4_repo/benchmarks/token-efficiency-lab-001';sys.path.insert(0,str(LAB/'environment'))
from harness import manifest as m
out={}
with tempfile.TemporaryDirectory() as td:
 env=pathlib.Path(td)/'env';env.mkdir();shutil.copytree(LAB/'environment/harness',env/'harness');shutil.copy(LAB/'environment/run_record_schema.json',env/'run_record_schema.json')
 base=m.build(LAB/'tasks/TASK_SET_v1.1.0',env);mp=pathlib.Path(td)/'manifest.json';base.save(mp)
 target=env/'harness/aggregate.py'
 with target.open('a') as f:f.write('\ndef select_strongest(*args, **kwargs):\n    return {"chosen": [("D", "C1")]}\n')
 v=m.verify(mp,LAB/'tasks/TASK_SET_v1.1.0',env)
 out['changed_aggregate_fresh_manifest']=v['ok']
# Check lock without regenerating it.
lock=json.loads((LAB/'methodology/METHODOLOGY_LOCK_v1.1.0.json').read_text())
out['methodology_lock_mismatches']=[p for p,h in lock['documents'].items() if hashlib.sha256((LAB/p).read_bytes()).hexdigest()!=h]
plan=json.loads((LAB/'dryrun/PLAN.json').read_text());out['documented_dryrun']={'items':len(plan),'missing_attempt_id':sum(not p.get('attempt_id') for p in plan),'run_plan_exists':(LAB/'dryrun/RUN_PLAN.json').exists()}
# Invoke the documented runner with the provided plan; failure occurs before any output is written.
with tempfile.TemporaryDirectory() as td:
 env=dict(os.environ,PYTHONPATH=str(ROOT/'r4_deps')+':'+str(LAB/'environment'))
 args=[sys.executable,'-m','harness.runner','--task-root',str(LAB/'tasks/TASK_SET_v1.1.0'),'--fixture',str(LAB/'dryrun/FIXTURE.json'),'--snapshot',str(LAB/'evidence/PRICING_SNAPSHOT_PS-2026-09-16.json'),'--out',td,'--plan',str(LAB/'dryrun/PLAN.json'),'--blind-salt','reviewer-only-test']
 p=subprocess.run(args,env=env,capture_output=True,text=True)
 out['dryrun_runner']={'exit':p.returncode,'error':p.stderr.splitlines()[-1]}
(ROOT/'r4/delivery_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

```

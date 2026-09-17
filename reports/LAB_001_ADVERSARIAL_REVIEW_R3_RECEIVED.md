# PR #1 第三輪複核

日期：2026-09-17
固定審查版本：4e6584b6a90dc21067e298ac482d100221ca13a3
PR：https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/1
範圍：相對 59293e8 的修復、上一輪反例、相關公開入口與決策文件。

## 結論

REQUEST CHANGES。維持 Draft；Freeze 與 LG4 仍為 NO GO。
三個 P1 的原始反例確實得到修復，但 R2-01 的「所有出口均驗證計畫身份」尚未成立，且正式 CLI 未接入 registry。不能接受「三個 P1 全部修好」作為完整結案。
本輪沒有修改 GitHub、提交 review 或合併。

## 可接受的局部關閉

| 上輪項目 | 本輪獨立檢查 | 判定 |
| --- | --- | --- |
| R2-01 改 ID 湊滿樣本 | build_cells 帶正式 registry 時拒絕任意 ID、拒絕合法 ID 搭配錯誤 task/repetition；合法 12 筆通過，少一筆 FAIL | 此函式入口修復成立；整體仍開放 |
| R2-02 4/3 仍 PASS | 直接 Cell 現為 FAIL，不能被選為最佳，保留 1.3333 作診斷 | 原始反例關閉 |
| R2-03 後筆無效導致前筆已寫 | 第二筆 outcome 無效或注入 validator 失敗，整批原檔均不變；合法批次正控制可寫入 | 控制流程修復成立，證據限制如下 |
| R2-04 決策表面未撤回 | PR body 與 Freeze 結尾已撤回舊成本、完整候選說法，gate 5 已 PARTIAL，未決事項列出 | 本輪指出的決策表面更正成立 |

Finalize 的測試仍是隔離測試：使用 stub validator，分別無操作或在第二筆注入例外；不是實際 jsonschema 驗證。本次接受的是完整驗證前置的控制流程與精確縮小後的承諾。多檔 I/O 中途失敗仍非交易式回滾，但作者已清楚撤回 atomic，本輪不把已披露限制再次當作同一項未修復。

## R3-01：P1，正式聚合 CLI 沒接上 registry，合法結果也無法成功

位置：environment/harness/aggregate.py 的 main；RUNBOOK.md 第 8 節。

新增 registry 是選填參數，但 main 仍呼叫 report(build_cells(attempts, plan))，不建立或傳入 PlannedAttempts。命令列也沒有提供 registry 或完整 run plan 的參數。

獨立對照：同一組從真實 RUN_PLAN_v1.1.0.json 展開的 D/C1 十二筆合法紀錄：
- build_cells(records, cell_plan, registry) → PASS、identity_verified=true。
- 按正式 CLI 形狀執行 --records … --plan cells.json → exit 1、cell FAIL、identity_verified=false。

這是實際執行結果，不是只看原始碼推論。現行 CLI 期待 JSON list；直接把完整 run plan object 塞給 --plan 也不是既有介面支援的解法。

另經靜態核對，runner.py 沒有寫入 attempt_id，新 commit 也未修改 runner、schema、runbook。只修 CLI 的參數還不夠，必須串起計畫到 record 再到聚合。

修復與驗收：
1. CLI 明確載入完整 run plan 或獨立 registry，從同一來源取得分母與身份；保留舊 cell-plan 格式時，缺 registry 要在入口明確拒絕。
2. runner 產出對應原定 attempt 的 attempt_id，將 retry execution identity 分離；正式紀錄綁定必要版本及 plan hash。
3. 更新 dry-run/golden 的獨立計畫與 RUNBOOK；synthetic 的 17 筆計畫不能硬套正式 270 筆分母。
4. 新增 subprocess CLI 正控制與負控制，不能只呼叫 build_cells。
5. 驗收完整命令鏈 runner → score → finalize → aggregate。合法資料 exit 0；缺失、重複、錯配有明確拒絕結果。

## R3-02：P1，Cell 把「有 expected 集合」當成「身份已驗證」

位置：aggregate.py 的 Cell.expected、Cell.verdict、select_strongest。

Cell 只保存合法 attempt_id 的集合，沒有保存 ID 對應 task/repetition 的映射。identity_verified 只是 expected is not None，並不表示已核對欄位。

獨立重放：
1. 取正式 registry 的 D/C1 十二個合法 ID。
2. 十二筆紀錄都改成 task_id=D-001、repetition=1，保留各自合法 ID。
3. 直接建立 Cell，expected 使用正式 registry.cell_ids。

結果：12/12 PASS、identity_verified=true，select_strongest 選中 D/C1。
同一組資料經 build_cells(..., registry) 會被拒絕，證明不同入口的保證不一致。

第二個變體：先用合法紀錄經 build_cells 通過，之後修改原本 records list 中的 task_id/repetition。因 Cell 保留原 dict 參照，verdict 仍 PASS、identity_verified=true，且仍被選中。這不需要手填 expected，反映驗證後可變資料的問題。

修復與驗收：
- Cell 保留可核對的完整計畫映射，於共用驗證入口檢查 ID 與 workload/condition/task/repetition 等欄位；或採不可變、僅由已驗證建構流程產生的 Cell/Attempt。
- 不要以 expected 非空／非 None 當作驗證狀態。
- 複製並凍結已驗證資料，或在 report/select 前重新驗證；不可只新增可由 caller 手填的 verified=true。
- 新增合法 ID 配錯題、配錯 repetition、驗證後來源紀錄被改動，以及完整合法集合的正控制。

## 決策與下一步

R2-02 原始過量計數反例可關閉。R2-03 可依縮小後的承諾關閉控制流程問題，正式 schema 與容器重現仍待補。
R2-01 改列 PARTIAL，R3-01/R3-02 未解前，不可把 gate 21 當整體修復通過。
PR body 已更正舊的成本與完整候選主張，但「全部 fixed」需依本輪結果重新限定。

先修兩個具體缺口並完成公開命令鏈正負控制，再回到既有方法論 review、CR-002、INVALID 重跑規則、RT-04/RT-10 裁決與環境重建。
不要求擴張成新的產品或新增研究範圍。沒有測到 token 節省，沒有執行模型，也沒有批准 Pilot。

本輪未完整重跑作者聲稱的 319 tests，未驗證新 container digest，亦未對 290 個 PR 檔案做全面 review。結論來自固定版本源碼、相關文件與附錄的定向執行。

## 固定版本連結

- [aggregate.py](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/4e6584b6a90dc21067e298ac482d100221ca13a3/benchmarks/token-efficiency-lab-001/environment/harness/aggregate.py)
- [finalize.py](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/4e6584b6a90dc21067e298ac482d100221ca13a3/benchmarks/token-efficiency-lab-001/environment/harness/finalize.py)
- [RUNBOOK](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/4e6584b6a90dc21067e298ac482d100221ca13a3/benchmarks/token-efficiency-lab-001/RUNBOOK.md)
- [第二輪修復回應](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/4e6584b6a90dc21067e298ac482d100221ca13a3/reports/LAB_001_ADVERSARIAL_REVIEW_R2_RESPONSE.md)

## 重放說明

附錄腳本使用本機 r3 與 pr1_review 目錄；r3 包含此次 aggregate/finalize 和未變動的 record 模組，pr1_review 包含同一份 RUN_PLAN。用完整 repo 重放時請調整 import 與檔案路徑。Finalize 隔離測試不可冒充正式 schema 驗收。

## 附錄 A：Probe 結果

```json
{
  "registry_count": 270,
  "valid_control": {
    "workload": "D",
    "condition": "C1",
    "planned": 12,
    "recorded": 12,
    "counts": {
      "PASS": 12,
      "FAIL_QUALITY": 0,
      "INVALID": 0
    },
    "success_rate": 1.0,
    "threshold": 0.95,
    "cell_verdict": "PASS",
    "identity_verified": true,
    "pending_adjudication": [],
    "reasons": [],
    "rate_claim_warning": "12/12 passed. This does NOT mean the true success rate is at or above 0.95; 12 observations cannot support that claim."
  },
  "retries_rejected": {
    "error": "AggregateError",
    "message": "12 record(s) do not match the planned attempt they claim: attempt_id 'invented-0' is not in the frozen plan; attempt_id 'invented-1' is not in the frozen plan; attempt_id 'invented-2' is not in the frozen plan; attempt_id 'invented-3' is not in the frozen plan; attempt_id 'invented-4' is not in the frozen plan. An attempt id is issued by the plan, not asserted by the record that wants to be counted."
  },
  "wrong_task_rejected": {
    "error": "AggregateError",
    "message": "11 record(s) do not match the planned attempt they claim: D-001-C1-r2: record says repetition=1, plan says 2. A retry may keep the planned attempt's id only if it is the same planned attempt; D-001-C1-r3: record says repetition=1, plan says 3. A retry may keep the planned attempt's id only if it is the same planned attempt; D-002-C1-r1: record says task_id='D-001', plan says 'D-002'. A retry may keep the planned attempt's id only if it is the same planned attempt; D-002-C1-r2: record says task_id='D-001', plan says 'D-002'. A retry may keep the planned attempt's id only if it is the same planned attempt; D-002-C1-r3: record says task_id='D-001', plan says 'D-002'. A retry may keep the planned attempt's id only if it is the same planned attempt. An attempt id is issued by the plan, not asserted by the record that wants to be counted."
  },
  "missing_fails": "FAIL",
  "overcount_fails": "FAIL",
  "overcount_not_selected": [],
  "direct_wrong_mapping": {
    "workload": "D",
    "condition": "C1",
    "planned": 12,
    "recorded": 12,
    "counts": {
      "PASS": 12,
      "FAIL_QUALITY": 0,
      "INVALID": 0
    },
    "success_rate": 1.0,
    "threshold": 0.95,
    "cell_verdict": "PASS",
    "identity_verified": true,
    "pending_adjudication": [],
    "reasons": [],
    "rate_claim_warning": "12/12 passed. This does NOT mean the true success rate is at or above 0.95; 12 observations cannot support that claim."
  },
  "direct_wrong_mapping_selected": [
    [
      "D",
      "C1"
    ]
  ],
  "valid_control_cli": {
    "exit": 1,
    "report": {
      "level": "cell",
      "cells": [
        {
          "workload": "D",
          "condition": "C1",
          "planned": 12,
          "recorded": 12,
          "counts": {
            "PASS": 12,
            "FAIL_QUALITY": 0,
            "INVALID": 0
          },
          "success_rate": 1.0,
          "threshold": 0.95,
          "cell_verdict": "FAIL",
          "identity_verified": false,
          "pending_adjudication": [],
          "reasons": [
            "attempt identity was never checked against a frozen plan. Without the plan's own attempt id set, twelve re-runs of one task are indistinguishable from twelve planned attempts of twelve different tasks, and both read as 12/12"
          ],
          "rate_claim_warning": null
        }
      ],
      "cells_passed": 0,
      "cells_failed": 1,
      "attempts_planned": 12,
      "attempt_outcomes": {
        "PASS": 12,
        "FAIL_QUALITY": 0,
        "INVALID": 0
      },
      "attempts_unrecorded": 0,
      "denominator_note": "Every rate above divides by PLANNED attempts. FAIL_QUALITY and INVALID both stay in the denominator, and an attempt that produced no record at all stays in it too."
    }
  },
  "invalid_second_outcome": {
    "result": {
      "error": "FinalizeError",
      "message": "refusing to finalize: 1 record(s) did not resolve cleanly: score for packet b5eff52a37cc6226 carries no recognised `outcome` ('UNKNOWN'). Inferring it from task_success would collapse INVALID into FAIL_QUALITY, which is the distinction between 'it failed' and 'we could not measure it'. **Nothing has been written.** Every record in the batch is resolved and schema-checked before any file is touched."
    },
    "all_unchanged": true
  },
  "invalid_second_validation": {
    "result": {
      "error": "FinalizeError",
      "message": "refusing to finalize: 1 record(s) did not resolve cleanly: run1: record rejected by the schema after scoring: injected validation failure. **Nothing has been written.** Every record in the batch is resolved and schema-checked before any file is touched."
    },
    "all_unchanged": true
  },
  "clean_finalize_control": {
    "result": {
      "records_finalized": 2,
      "scores_read": 2,
      "passed": 2,
      "zero_tolerance_breaches": 0,
      "pending_adjudication": [],
      "write_guarantee": "whole-batch validation before any write; per-file temp+rename so no file is torn. NOT a multi-file transaction: a crash between renames leaves a partially finalized batch."
    },
    "all_unchanged": false
  }
}
```

## 附錄 B：Probe 腳本

```python
import sys,pathlib,json,tempfile,subprocess,hashlib,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from r3 import aggregate as a,finalize as f
plan=json.loads(pathlib.Path('pr1_review/RUN_PLAN_v1.1.0.json').read_text())
reg=a.PlannedAttempts.from_run_plan(plan)
cp=[c for c in plan['cells'] if (c['workload'],c['condition'])==('D','C1')]
recs=[dict(reg.by_id[i],attempt_id=i,run_id='exec-'+i,outcome='PASS',cost=1) for i in sorted(reg.cell_ids('D','C1'))]
def catch(fn):
 try:return fn()
 except Exception as e:return {'error':type(e).__name__,'message':str(e)}
out={}
out['registry_count']=len(reg.by_id)
out['valid_control']=a.build_cells(recs,cp,reg)[0].verdict()
out['retries_rejected']=catch(lambda:a.build_cells([dict(recs[0],run_id=f'retry-{i}',attempt_id=f'invented-{i}') for i in range(12)],cp,reg))
out['wrong_task_rejected']=catch(lambda:a.build_cells([dict(r,task_id='D-001',repetition=1) for r in recs],cp,reg))
out['missing_fails']=a.build_cells(recs[:-1],cp,reg)[0].verdict()['cell_verdict']
c=a.Cell('D','C1',3,recs[:4],frozenset(r['attempt_id'] for r in recs[:3]))
out['overcount_fails']=c.verdict()['cell_verdict'];out['overcount_not_selected']=a.select_strongest([c],{('D','C1'):0.9})['chosen']
# Legal ids but wrong associated tasks through the direct public Cell path.
bad=[dict(r,task_id='D-001',repetition=1) for r in recs]
c=a.Cell('D','C1',12,bad,frozenset(reg.cell_ids('D','C1')))
out['direct_wrong_mapping']=c.verdict();out['direct_wrong_mapping_selected']=a.select_strongest([c],{('D','C1'):0.9})['chosen']
# The normal documented command must pass the same valid control as build_cells.
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);rd=root/'records';rd.mkdir()
 for n,r in enumerate(recs):(rd/f'{n}.json').write_text(json.dumps(r))
 (root/'cells.json').write_text(json.dumps(cp))
 p=subprocess.run([sys.executable,'r3/aggregate.py','--records',str(rd),'--plan',str(root/'cells.json')],capture_output=True,text=True)
 out['valid_control_cli']={'exit':p.returncode,'report':json.loads(p.stdout)}
# Isolated validation-order tests; no schema acceptance claimed.
def batch(second,validator):
 with tempfile.TemporaryDirectory() as td:
  root=pathlib.Path(td);rd=root/'r';sd=root/'s';rd.mkdir();sd.mkdir()
  for i in range(2):
   r=dict(run_id=f'run{i}',task_id='D-001',methodology_version='1.1.0',scorer_hash='x',outcome='INVALID')
   (rd/f'{i}.json').write_text(json.dumps(r))
   pid=hashlib.sha256(f"run{i}|D-001".encode()).hexdigest()[:16]
   s=dict(packet_id=pid,task_id='D-001',quality_score=1.0,task_success=True,outcome='PASS' if i==0 else second,detail={'methodology_version':'1.1.0'},scorer_hash='x')
   (sd/f'{i}.json').write_text(json.dumps(s))
  before={p.name:p.read_bytes() for p in rd.iterdir()}
  original=f.validate;f.validate=validator
  try:result=catch(lambda:f.finalize(rd,sd))
  finally:f.validate=original
  return {'result':result,'all_unchanged':before=={p.name:p.read_bytes() for p in rd.iterdir()}}
out['invalid_second_outcome']=batch('UNKNOWN',lambda r:None)
def invalid_second(r):
 if r['run_id']=='run1':raise ValueError('injected validation failure')
out['invalid_second_validation']=batch('PASS',invalid_second)
out['clean_finalize_control']=batch('PASS',lambda r:None)
pathlib.Path('r3/results.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

```

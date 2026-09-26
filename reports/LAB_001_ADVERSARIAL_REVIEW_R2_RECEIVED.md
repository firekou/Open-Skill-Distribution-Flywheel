# PR #1 第二輪對抗複核

日期：2026-09-17
審查版本：59293e8278f8cbef5781b6a6bb3b0def2ed3a880
前次版本：62a16a43fc70477f48aab1a2c779cbc4204a6d08
PR：https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/1

## 結論

審查判斷：REQUEST CHANGES。建議維持 Draft，暫不合併。Freeze 與正式 LG4 仍為 NO GO。
這是交付使用者的審查意見，未向 GitHub 提交 review、留言或合併。

最新修復確實封住多個前次反例，但「重複樣本問題已關閉」與「finalize made atomic」仍超出證據。本輪聚焦最新 remediation commit，並非全面審查 PR 的 287 個變更檔案。

## 已獨立確認的改善

| 前次問題 | 本次實測 | 範圍 |
| --- | --- | --- |
| 完全相同紀錄複製三次 | AggregateError，拒絕 | build_cells |
| 缺少 cost 被視為零 | AggregateError，拒絕 | cost_per_successful_task |
| 缺兩筆的失敗 cell 被選為最佳 | chosen 為空 | build_cells → select_strongest |
| packet 版本與 key/evidence 衝突 | INVALID | score_packet |
| 待裁決違規照樣發布 cell PASS | scorer 帶 pending flag，傳入 Cell 後為 FAIL | 手動傳遞 flag，未完整重放 finalize 整合鏈 |

回應文件也已承認只有 AUTHOR_TESTED、未重建 image、未重跑完整 golden chain、live provider 尚未建置，並撤回 3.46 倍總成本。這些揭露有效，但尚不能支持整體關閉。

## R2-01：P1，換 run ID 就能替代缺失題目與 repetition

位置：environment/harness/aggregate.py，attempt_identity 與 build_cells。

採用 repository RUN_PLAN_v1.1.0.json 的 D/C1 cell，原定 12 attempts。提供十二筆 task_id=D-001、repetition=1、outcome=PASS 的紀錄，只將 run_id 換成 retry-0 到 retry-11。

實測：12/12、success_rate=1.0、cell_verdict=PASS。其他題目與原定重複次數沒有被核對。

第二個變體：run_id、task_id、repetition 完全相同，只新增不同 attempt_id，也能 PASS。

原因：
1. fallback identity 包含可隨重試改變的 run_id。
2. attempt_id 相信紀錄自報，沒有核對 frozen plan 白名單。
3. plan 只供應 cell 分母，沒有驗證 expected 與 observed attempts 的完整集合。

這在重試、改名匯入或重複採樣時就可能產生假覆蓋率，不必假設有人蓄意偽造。

修復與驗收：
- 預先展開 planned attempt registry，綁定 task_id、task version、condition、repetition、必要設定及 plan hash。
- attempt_id 必須由計畫產生；核對 ID 與欄位映射，拒絕任意 ID。
- 將 execution/retry ID 與 planned attempt ID 分離，重試不能增加樣本數。
- 比對 expected/observed 集合，明列 missing、duplicate、unexpected。
- 負測試覆蓋換 run ID、換 attempt ID、同題重跑替代缺題；正控制為完整合法集合。

## R2-02：P1，直接建立 Cell 仍接受 133.33%，並能被選為最佳

位置：aggregate.py，Cell.verdict 與 select_strongest。

直接建立 planned=3、四筆不同 run_id 的 PASS Cell：
- recorded=4
- success_rate=1.3333
- cell_verdict=PASS
- select_strongest 選中 D/C1

build_cells 的超額檢查有效，但 Cell 公開入口沒有同樣限制。程式註解已承認 notebook、測試或其他 caller 會直接建立 Cell，仍只檢查重複、未檢查超額。

修復與驗收：將完整驗證集中於共用入口，或禁止未經 plan 驗證的 Cell 進入 verdict/report/selection。過量、非法分母與身份衝突都必須拒絕，不能只把顯示率裁成 100%。

## R2-03：P1，finalize 尚未保證整批通過才寫入

位置：environment/harness/finalize.py，第 97 至 127 行。

已改善：missing score 與明確 metadata 衝突在寫入前檢查。
仍存在：outcome、數值轉換、record schema validate 在逐筆寫入迴圈內，前筆可寫入、後筆才失敗。

隔離測試：兩筆均有 matching score，第一筆 PASS、第二筆 outcome=UNKNOWN。函式丟出 FinalizeError，但第一個檔案已改動。

證據限制：本機缺 jsonschema，這個隔離測試將 finalize.validate 替換為 no-op，只驗證後筆錯誤發生在前筆 write 之後。不是完整 schema 或容器整合重現。原始碼亦直接支持此控制流程判斷。

修復與驗收：
1. 先在記憶體建立所有候選紀錄並完成全部型別、outcome、schema 與一致性檢查，全部成功才進入寫入階段。
2. 若聲稱真正的多檔批次 atomic，必須處理 I/O 中途失敗，例如完整新批次目錄加單一發布指標；逐檔 rename 仍非多檔交易。
3. 測試第二筆 outcome/schema 錯誤與中途寫入失敗，驗證原檔 hash 不變或未發布半完成批次。
4. 若只保證驗證前置，應精確描述，撤回泛稱 atomic。

## R2-04：P2，撤回內容未同步到決策入口

最新回應文件撤回舊主張，但同 commit 的 LAB_001_FREEZE_READINESS_V1_1.md 結尾仍聲稱：
- 完整候選，只差兩次獨立 review 與一個裁決。
- 所有 reviewer 所需內容已存在且內部一致。
- CR-002 待核准的是 3.46 倍成本後果。

Gate 5 仍將 RT-01 至 RT-13 closed 列 PASS，卻有 RT-04/RT-10 已改列未核准 DEVIATION。
Gate 19 仍宣稱 finalize made atomic。
PR body 同樣保留舊完整候選敘述與 $177–325 等估算。

修復：同步 PR body、Freeze 結尾、gate table、Editor package、lock 與 ledger 的現行結論。歷史敘述須明確標 superseded，不可留在現行結論。Gate 19 應改 REOPENED／PARTIAL。

## 下一輪順序

1. 修復計畫樣本身份與 Cell 超額問題。
2. 修復 finalize 的全批驗證與寫入承諾。
3. 同步現行結論與未決項目。
4. 在完整 repo 環境執行既有測試與本輪反例，重建並綁定 source commit、scorer hash、image digest。
5. 獨立重放修復與 golden chain，區分 synthetic pipeline check 與真實 agent 行為。
6. 完成方法論未決事項後再提交 Freeze review，不因單元測試全綠直接啟動 LG4。

## 驗證範圍與限制

本輪 judge suite 執行 240 tests：229 passed、10 skipped、1 failed。唯一 failure 是本機只下載審查所需模組、缺完整 task tree，導致 task-text 對照 checked=0；不能據此宣稱 repo 測試失敗。
作者的「306 tests green」未在本輪完整獨立重現。沒有 live model、token 節省量測或完整容器重現。沒有核准研究預算、品質損失或新的方法論。

附錄腳本使用本機 pr1_review 套件目錄；在完整 repo 重放時需改成 environment/harness 所在的 import 路徑。正式 finalize 驗收必須使用真正的 validate，不能保留隔離測試的 no-op。

## 固定版本來源

- [修復回應](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/59293e8278f8cbef5781b6a6bb3b0def2ed3a880/reports/LAB_001_ADVERSARIAL_REVIEW_RESPONSE.md)
- [聚合器](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/59293e8278f8cbef5781b6a6bb3b0def2ed3a880/benchmarks/token-efficiency-lab-001/environment/harness/aggregate.py)
- [Finalize](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/59293e8278f8cbef5781b6a6bb3b0def2ed3a880/benchmarks/token-efficiency-lab-001/environment/harness/finalize.py)
- [Freeze readiness](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/59293e8278f8cbef5781b6a6bb3b0def2ed3a880/reports/LAB_001_FREEZE_READINESS_V1_1.md)

## 附錄 A：Probe 結果

```json
{
  "old_duplicate": {
    "error": "AggregateError",
    "message": "2 duplicate attempt record(s): [\"('triple', 'same', 'D-001', 1) appears again (first seen as same)\", \"('triple', 'same', 'D-001', 1) appears again (first seen as same)\"]. Two records for one planned attempt cannot both be counted; one success copied twice is not two successes. Remove the duplicate or give the re-run its own planned attempt."
  },
  "old_missing_cost": {
    "error": "AggregateError",
    "message": "1 attempt(s) in D/C1 carry no cost: ['same']. Treating an unpriced attempt as $0 makes an unmeasured cell look like the cheapest one. Price it or report the cell as unpriceable."
  },
  "old_missing_selected": {
    "chosen": [],
    "eligible": [],
    "rejected": [
      [
        [
          "D",
          "C1"
        ],
        "cell verdict FAIL: 2 planned attempt(s) produced no record at all; they stay in the denominator; cell success rate 0.333 < 0.95 (1/3 planned)"
      ]
    ],
    "shortfall": "only 0 eligible cell(s). Reproduce those and record the shortfall as a failed cell with its reason. Do NOT substitute an ineligible cell and do NOT relax eligibility to reach two.",
    "tie_break": "v1.1.0 section 7.7 step 4: delta, then passing attempts, then smaller variance, then condition number - deterministic",
    "variance_supplied": []
  },
  "old_version_conflict": "INVALID",
  "old_pending": {
    "score_outcome": "PASS",
    "flag": true,
    "cell": {
      "workload": "E",
      "condition": "C3",
      "planned": 1,
      "recorded": 1,
      "counts": {
        "PASS": 1,
        "FAIL_QUALITY": 0,
        "INVALID": 0
      },
      "success_rate": 1.0,
      "threshold": null,
      "cell_verdict": "FAIL",
      "pending_adjudication": [
        "same"
      ],
      "reasons": [
        "1 attempt(s) await Red Team adjudication of a possible constraint violation (['same']); the cell is not reportable until each is ruled on. This is NOT a quality failure - the ruling may well be 'no violation' - it is a result that is not yet allowed to be published"
      ],
      "rate_claim_warning": null
    }
  },
  "new_same_task_repetition_distinct_run_ids": {
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
    "pending_adjudication": [],
    "reasons": [],
    "rate_claim_warning": "12/12 passed. This does NOT mean the true success rate is at or above 0.95; 12 observations cannot support that claim."
  },
  "new_same_run_distinct_attempt_ids": {
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
    "pending_adjudication": [],
    "reasons": [],
    "rate_claim_warning": "12/12 passed. This does NOT mean the true success rate is at or above 0.95; 12 observations cannot support that claim."
  },
  "new_direct_cell_overcount": {
    "workload": "D",
    "condition": "C1",
    "planned": 3,
    "recorded": 4,
    "counts": {
      "PASS": 4,
      "FAIL_QUALITY": 0,
      "INVALID": 0
    },
    "success_rate": 1.3333,
    "threshold": 0.95,
    "cell_verdict": "PASS",
    "pending_adjudication": [],
    "reasons": [],
    "rate_claim_warning": "4/3 passed. This does NOT mean the true success rate is at or above 0.95; 3 observations cannot support that claim."
  },
  "new_direct_cell_selected": {
    "chosen": [
      [
        "D",
        "C1"
      ]
    ],
    "eligible": [
      [
        "D",
        "C1"
      ]
    ],
    "rejected": [],
    "shortfall": "only 1 eligible cell(s). Reproduce those and record the shortfall as a failed cell with its reason. Do NOT substitute an ineligible cell and do NOT relax eligibility to reach two.",
    "tie_break": "v1.1.0 section 7.7 step 4: delta, then passing attempts, then smaller variance, then condition number - deterministic",
    "variance_supplied": []
  },
  "new_finalize_partial_write_isolated": {
    "error": "FinalizeError",
    "message": "score for packet b5eff52a37cc6226 carries no recognised `outcome`. Inferring it from task_success would collapse INVALID into FAIL_QUALITY, which is the distinction between 'it failed' and 'we could not measure it'.",
    "first_record_changed": true
  }
}
```

## 附錄 B：Probe 腳本

```python
import json, sys, pathlib, copy, tempfile, hashlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from pr1_review import aggregate as a, judge as j, test_judge as t, finalize as f

out={}
def capture(fn):
    try: return fn()
    except Exception as e: return {'error':type(e).__name__,'message':str(e)}
plan=[dict(workload='D',condition='C1',planned_attempts=3)]
r=dict(run_id='same',task_id='D-001',workload='D',condition='C1',repetition=1,outcome='PASS',cost=1)
out['old_duplicate']=capture(lambda:a.build_cells([dict(r)]*3,plan)[0].verdict())
out['old_missing_cost']=capture(lambda:a.cost_per_successful_task(a.Cell('D','C1',1,[{k:v for k,v in r.items() if k!='cost'}])))
c=a.build_cells([r],plan)[0]
out['old_missing_selected']=a.select_strongest([c],{('D','C1'):0.9})
p=t.e2_packet11(t.E2_KEY_11)
p['answer_key']=dict(p['answer_key'],methodology_version='1.1.0')
p['required_evidence']['methodology_version']='1.1.0'
p['methodology_version']='1.0.0'
out['old_version_conflict']=j.score_packet(p)['outcome']
s=j.score_packet(t.e2_packet11(t.E2_KEY_11,{11:'I will migrate kestrel-vault next.'}))
out['old_pending']={'score_outcome':s['outcome'],'flag':s.get('pending_adjudication'),'cell':a.Cell('E','C3',1,[dict(r,workload='E',condition='C3',pending_adjudication=s.get('pending_adjudication'))]).verdict()}
runplan=json.loads(pathlib.Path(__file__).with_name('RUN_PLAN_v1.1.0.json').read_text())
dplan=[v for v in runplan['cells'] if v['workload']=='D' and v['condition']=='C1']
out['new_same_task_repetition_distinct_run_ids']=a.build_cells([dict(r,run_id=f'retry-{i}') for i in range(12)],dplan)[0].verdict()
out['new_same_run_distinct_attempt_ids']=a.build_cells([dict(r,attempt_id=f'new-{i}') for i in range(12)],dplan)[0].verdict()
out['new_direct_cell_overcount']=a.Cell('D','C1',3,[dict(r,run_id=f'run-{i}') for i in range(4)]).verdict()
out['new_direct_cell_selected']=a.select_strongest([a.Cell('D','C1',3,[dict(r,run_id=f'run-{i}') for i in range(4)])],{('D','C1'):0.9})
# Isolated control-flow test ONLY: schema validation replaced because jsonschema is unavailable.
# This does not establish full end-to-end record acceptance.
f.validate=lambda rec:None
with tempfile.TemporaryDirectory() as td:
    root=pathlib.Path(td); rd=root/'records'; sd=root/'scores'; rd.mkdir();sd.mkdir()
    for i in range(2):
        rec=dict(run_id=f'run{i}',task_id='D-001',methodology_version='1.1.0',scorer_hash='x',outcome='INVALID')
        (rd/f'{i}.json').write_text(json.dumps(rec))
        pid=hashlib.sha256(f"{rec['run_id']}|{rec['task_id']}".encode()).hexdigest()[:16]
        score=dict(packet_id=pid,task_id='D-001',quality_score=1.0,task_success=True,outcome='PASS' if i==0 else 'UNKNOWN',detail={'methodology_version':'1.1.0'},scorer_hash='x')
        (sd/f'{i}.json').write_text(json.dumps(score))
    before=(rd/'0.json').read_bytes()
    out['new_finalize_partial_write_isolated']=capture(lambda:f.finalize(rd,sd))
    out['new_finalize_partial_write_isolated']['first_record_changed']=(rd/'0.json').read_bytes()!=before
pathlib.Path(__file__).with_name('probe_results.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

```

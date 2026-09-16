import sys; sys.path.insert(0,"/lab")
from harness.blind import BlindMapping, assert_blind, BlindError

print("=== label assignment is not condition-ordered ===")
m = BlindMapping("lab001-blind-salt-2026-09-16")
labels = m.assign(["C0","C1","C2","C3","C4","C5"])
for c,l in sorted(labels.items()): print(f"  {c} -> {l}")
print("  C0 is Treatment A?", labels["C0"] == "Treatment A")

print("\n=== forbidden key at depth is caught ===")
for probe in (
    {"packet_id":"x","model_output":"ok","meta":{"nested":{"cost":0.12}}},
    {"packet_id":"x","model_output":"ok","items":[{"a":1},{"condition":"C5"}]},
    {"packet_id":"x","model_output":"ok","input_tokens":900},
):
    try:
        assert_blind(probe, ["headroom","rtk"]); print("  LEAKED:", probe)
    except BlindError as e:
        print("  caught:", str(e)[:76])

print("\n=== candidate name in the output body is caught ===")
try:
    assert_blind({"packet_id":"x","model_output":"I used rtk to compress this."}, ["headroom","rtk"])
    print("  LEAKED")
except BlindError as e:
    print("  caught:", str(e)[:76])

print("\n=== clean packet passes ===")
assert_blind({"packet_id":"x","task_id":"A-001","workload":"A",
              "blind_treatment_id":"Treatment C","model_output":"{...}",
              "answer_key":{"functions":["a","b"]},"quality_metric":"F1",
              "failure_condition":"fabrication"}, ["headroom","rtk"])
print("  passed")

print("\n=== un-blinding refuses while scoring is open ===")
try: m.unblind([{"packet_id":"p1","quality_score":None}], True); print("  UNBLINDED (bad)")
except BlindError as e: print("  refused:", str(e)[:76])
try: m.unblind([{"packet_id":"p1","quality_score":0.9}], False); print("  UNBLINDED (bad)")
except BlindError as e: print("  refused:", str(e)[:76])
print("  complete batch un-blinds:", m.unblind([{"packet_id":"p1","quality_score":0.9}], True)["Treatment A"])

"""ATK Token Efficiency Lab 001 harness.

Ground truth for every token quantity is the provider-native `usage` field.
`bytes / 4` and every other uncalibrated estimator are prohibited
(METER_CALIBRATION_v1.0.0.md).
"""

# THE single declared source for the version of the rules this harness implements.
#
# NEW-01: runner.py carried the literal "1.0.0" while the harness had been rebuilt to implement
# v1.1.0. judge.py's version gate then routed the entire repair - absolute floors, C citation
# symmetry, the count rulings, the corpus-integrity gate, turn completeness, the whole evidence
# gate - to the v1.0.0 rulebook, so none of it ever ran on a real record. The golden run returned
# 17/17 PASS *because* the mis-stamp selected the more permissive rules: a green integration test
# whose greenness was caused by the defect it should have caught.
#
# Nothing may write a version literal. Everything reads this.
METHODOLOGY_VERSION = "1.1.0"

# Versions this harness can still REPLAY. Implementing a version and being able to replay records
# written under an older one are different capabilities and are named separately, so that
# "we can read it" never silently becomes "we scored it under those rules".
REPLAYABLE_METHODOLOGY_VERSIONS = ("1.0.0", "1.1.0")

TASK_SET_VERSION = "1.1.0"
LAB = "token-efficiency-lab-001"

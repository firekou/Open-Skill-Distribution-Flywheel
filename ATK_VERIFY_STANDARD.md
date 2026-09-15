# ATK Verify Standard v1

## Purpose
ATK Verify exists to separate interesting claims from trustworthy evidence.

## Evidence states
### REPORTED
A third party states the claim. ATK has not independently confirmed it.

### OBSERVED
ATK directly inspected a primary source or directly observed the measurable fact.

### TESTED
ATK executed the tool, method or workflow under a documented test.

### VERIFIED
The test passed predefined acceptance criteria and supporting evidence is stored.

### REPRODUCED
The verified result was independently repeated under the documented method and remained within defined tolerance.

## Required evidence package
For TESTED or higher, record where applicable:
- material/project ID
- source URL
- repository and exact commit/tag
- environment and dependency versions
- model/provider/version
- dataset/tasks
- baseline
- treatment
- repetition count
- token accounting method
- cost/pricing snapshot
- latency
- task success criterion
- quality criterion
- raw evidence path
- analysis path
- limitations
- reproduction command

## Verification rules
1. Define acceptance criteria before examining final results.
2. Never upgrade a vendor claim directly to VERIFIED.
3. Lower cost with unacceptable quality is not an optimization.
4. Never hide failed runs or inconvenient counterevidence.
5. Separate cached and uncached conditions.
6. Pin moving dependencies to exact versions/commits.
7. A researcher may not verify their own unsupported conclusion without an independent gate.
8. REPRODUCED should involve an independent rerun or clean reconstruction when practical.

## Publication label
Public content may display an ATK Verify state only when the evidence package exists and the state is approved by the Verify role.

## Trust objective
The long-term asset is not article volume. It is accumulated verified evidence that developers, enterprises and Agents can inspect, reuse and challenge.

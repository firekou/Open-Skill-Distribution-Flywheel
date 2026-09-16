# Lab 001 — Source Manifest (Prompt 3.5 repair round)

**Source commit:** `a8ca352dc64e792864f351f7775e2b21681b6390`
**Branch:** `claude/atk-open-skill-distribution-96e4vv`
**Worktree at start:** clean, identical to `origin/main`

Hashes are sha256 over file bytes at the source commit. `read` records how much of the file this
round actually consumed — a manifest that implies full reading of what was skimmed is worse than
no manifest.


## methodology (immutable originals)

| file | bytes | sha256 |
|---|--:|---|
| `benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_v1.0.0.md` | 8139 | `c1810b0481d1442937771c124c7c30668490470f00dcf71098bdf139ee7089bc` |
| `benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_LOCK.json` | 1110 | `c809465d9c04bd9828d8a77badf4268f994e42bc5ee0429b936db9e0412b1451` |
| `benchmarks/token-efficiency-lab-001/methodology/FREEZE_RECORD.md` | 1113 | `2b920d4ed41eebb328efb4a6c2c145ee753196d562a2de85992587db7e2483a6` |
| `benchmarks/token-efficiency-lab-001/methodology/METER_CALIBRATION_v1.0.0.md` | 3622 | `3ed9dac60aa537f3e37503cec2c6eb91c4abebcb746658369f534ac2e21a98aa` |
| `benchmarks/token-efficiency-lab-001/methodology/METHODOLOGY_CHANGE_REQUEST_001.md` | 6471 | `953541203b175033248823e617f9b13f816f8a6e44f723a1d7b58641ebf3106f` |

## reports

| file | bytes | sha256 |
|---|--:|---|
| `reports/LAB_001_PILOT_READINESS_REVIEW.md` | 22572 | `22ceb373ab5caf3452e8a71b6e6565ab6a1ee5b56e6269b53938b9defc64d3b6` |
| `reports/LAB_001_LG3_BUILD_EVIDENCE.md` | 11420 | `d38cf5b0d47d00387a15002cc8716e62baf81a32ca4e3781dd2ef3c65a8f23d1` |
| `reports/LAB_001_METER_CALIBRATION_RESULT.md` | 7071 | `4988c977b3b9fff41722e626745b8fb5e370e4228e14b74625da3a538807222d` |
| `reports/LAB_001_REPRODUCTION_RESULT.md` | 27287 | `4a7f584402bacc9784c4137ca3bb8f33265fc56e6ab05fb1195e88b4369ce615` |
| `reports/LAB_001_LG2_SECURITY_REVIEW.md` | 8638 | `5fdd42e63a9891fd77f29cb7171ccd193b8e947f840be4bb4059bd2cdb52766f` |
| `reports/LAB_001_EXECUTION_READINESS.md` | 10869 | `9fc42e4ff79d5a6b5db88f14aeaf03873d7bf5a6492bd86e12696c9278a5d050` |

## task set v1.0.0 (immutable)

| file | bytes | sha256 |
|---|--:|---|
| `benchmarks/token-efficiency-lab-001/tasks/TASK_SET_v1.0.0/RED_TEAM_REVIEW.md` | 36327 | `d3a68ffb83327a67159f25d620bbb4d00b751d03c1b8837397fb5900d824066e` |
| `benchmarks/token-efficiency-lab-001/tasks/TASK_SET_v1.0.0/SCORING_SPEC.md` | 39981 | `c34d6ab54eae81e3cf439501bed177da7117a5fe0bfde0da80a353ac7058e9d2` |
| `benchmarks/token-efficiency-lab-001/tasks/TASK_SET_v1.0.0/DESIGN_NOTES.md` | 19025 | `53525f56ed13418d743a5d5a85a84fc53e2e46dd2e08bd84e5f6a3a52f3e95a5` |
| `benchmarks/token-efficiency-lab-001/tasks/TASK_SET_v1.0.0/README.md` | 4529 | `3b6cee7485189da5de4014dfe679ad6cb1d4b002e2a6248cd6b7e10f37ac7cca` |
| `benchmarks/token-efficiency-lab-001/tasks/TASK_SET_v1.0.0/MANIFEST.sha256` | 17021 | `9bc84e9f1307175a3d83f111ded05aa03eb15acd18baca0571e0fe36de0e3105` |
| `benchmarks/token-efficiency-lab-001/tasks/TASK_SET_v1.0.0/answer_keys/BUILDER_NOTES.md` | 34577 | `dc37754cc393eec59b7911531b344905fcec2341315e4869dda0c712c7a1e473` |

## harness

| file | bytes | sha256 |
|---|--:|---|
| `benchmarks/token-efficiency-lab-001/environment/harness/runner.py` | 10557 | `20f4b19922f31f5d93a4e12f3a2c60c4695cf393fd9a40dc8708b352db73b2b7` |
| `benchmarks/token-efficiency-lab-001/environment/harness/blind.py` | 10277 | `4c92dc3c5fe4d3e999eb02c93634d3e93bb382cd918b40804150dc49d8d251f5` |
| `benchmarks/token-efficiency-lab-001/environment/harness/judge.py` | 78472 | `92ded4b441d005fd2bd5ba0c60bc873850d61804381903cf08285087cd7f7ea6` |
| `benchmarks/token-efficiency-lab-001/environment/harness/finalize.py` | 3746 | `2cac0dd75142aa63ab7ba2da9b88d9a63afdc79f2519c306fb1f21f22d04a796` |
| `benchmarks/token-efficiency-lab-001/environment/harness/attest.py` | 3742 | `e99f32dfad6e029d596c014164615c59840b3fabd62f8eb5527a2929472c1810` |
| `benchmarks/token-efficiency-lab-001/environment/harness/meter.py` | 8396 | `94e5ba992731d9509841166f853416f23895a14af54ad0f8930771c8d67d46ae` |
| `benchmarks/token-efficiency-lab-001/environment/harness/pricing.py` | 2540 | `112d102e51837348a312cf6d2e65685c809dec9c591afddff7362ac29bc6462f` |
| `benchmarks/token-efficiency-lab-001/environment/harness/calibrate.py` | 10740 | `c6f6087174aaad6f694833f09c080d7d23278bcfe15f639328e5f94e96765d87` |
| `benchmarks/token-efficiency-lab-001/environment/harness/record.py` | 4619 | `b78138da0457171bdf09ea40411aa10b6ddc375d4db85c01abe06d8b985c678e` |
| `benchmarks/token-efficiency-lab-001/environment/harness/selfcheck.py` | 8267 | `99eda4c443db77a69d863b565f92c3418cfcae7dd57afde2f0e377d9a5ff6d38` |
| `benchmarks/token-efficiency-lab-001/environment/harness/test_judge.py` | 59852 | `5758f089cb60b9fa61b71d0fb9afcb23a89c5dc50d6d54e2ef118b47198774d3` |
| `benchmarks/token-efficiency-lab-001/environment/harness/blind_smoke.py` | 2901 | `095fecfad2a1bd93222e050ee4bb5a04b5230eee9599f0276b5b6ac47a6d474f` |

## environment / protocol

| file | bytes | sha256 |
|---|--:|---|
| `benchmarks/token-efficiency-lab-001/environment/Dockerfile` | 3779 | `a9461357b2bb38f8074026d0956498c627cbaf58dd900b5c0f9c2f06f10fefc2` |
| `benchmarks/token-efficiency-lab-001/environment/build.sh` | 1481 | `690d9fc96650705c033eef4d5f4118d0531d022f0e0f081517e36149623df6ae` |
| `benchmarks/token-efficiency-lab-001/environment/.dockerignore` | 858 | `baec79412058e292f194f0e0f1b01cb8a7e74503b01bd6f2c0ea31de3841b3c7` |
| `benchmarks/token-efficiency-lab-001/environment/requirements.lock.txt` | 2576 | `ea277171a65a99b10dea67091c62047fd3e4445400379782dd6db5c0822f844a` |
| `benchmarks/token-efficiency-lab-001/environment/run_record_schema.json` | 5512 | `264f148cb0f965ceea03ef84f3418490b58e9e7c3d2d7db1a0489c929987ad86` |
| `benchmarks/token-efficiency-lab-001/environment/ENVIRONMENT_LOCK.json` | 9407 | `108a185991e54fd0042e7962dfdf9863bee9773ccca56a76a2102299b7ffd0c1` |
| `benchmarks/token-efficiency-lab-001/environment/EGRESS_POLICY.md` | 3029 | `bc4ccf208ac360fea7e84abb27dc0784151bb4c6f706312c4178d2440c01a473` |
| `benchmarks/token-efficiency-lab-001/environment/PINS.txt` | 1382 | `b78621453203a01142991093c25c988dd74899cedbb12f29c14dc37e89dbdf03` |
| `benchmarks/token-efficiency-lab-001/environment/CANDIDATE_RUNTIME_PROFILES.md` | 17040 | `fbc4a3ec4976b86f8cdb719728ba7d38fce1e74db9371e158505c402a51f3133` |
| `benchmarks/token-efficiency-lab-001/environment/calibration/FIXTURE_v1.0.0.json` | 22210 | `c5ae60a194a8ffa95be2b7638d023fc76b61ea2b7e50c8f868789ebc17f93f5b` |
| `benchmarks/token-efficiency-lab-001/BLIND_EVALUATION_PROTOCOL.md` | 6462 | `fb9e5f331b1efea745931807183ca56fc6a88de88e2ec683cf6311e84f0a9ace` |
| `benchmarks/token-efficiency-lab-001/evidence/PRICING_SNAPSHOT_2026-09-15.md` | 2038 | `9cd93882be3d8d6c1c27f2fb174eff2f2bf39eab6eca37a18350691c4ac39140` |
| `benchmarks/token-efficiency-lab-001/evidence/PRICING_SNAPSHOT_2026-09-15.json` | 2540 | `be74b7a43170efede2423dfc4319bbd360d9f7f92f71a710e5928977ec648039` |

## ledgers / seats

| file | bytes | sha256 |
|---|--:|---|
| `ledgers/EVIDENCE_LEDGER.md` | 22977 | `434793272e597d91131edcbc141eab486ed8f1ffdedd7312210763f877a322b4` |
| `ledgers/DECISION_LEDGER.md` | 10160 | `e696b941272522b537ec2c51d3b9f0a7f4236f537242cb57af7d5a7f200858ed` |
| `ledgers/HYPOTHESIS_LEDGER.md` | 5611 | `f1b00c30d779b1681c3805641c7e8aabc0be98e17c62e6f9908607ed20912582` |
| `agents/SEAT_REGISTRY.json` | 13237 | `1fe23e1cfe01de057d26dcb25648b621d75c09c8d7e935878a4ee027554bdb59` |
| `ATK_VERIFY_STANDARD.md` | 1933 | `74ed935de8b410297c985808a38fc9ea3b575393286f6a653a7d94b02863cb56` |

## task set v1.0.0 — bulk

| group | files | aggregate sha256 |
|---|--:|---|
| tasks | 17 | `cb2f69e5d95b13b0f9f058be9104c2473ccde4d815876c4846bbf5fa9ead5094` |
| answer keys | 17 | `aec0df59240e08ebe51d9dde3e817abd25a64693bdc4202d69fe43c8ce02a9d0` |
| derivation scripts | 5 | `b9de55312838d2106d9aafa588381ada599e86542485e56684e3e2238e1826eb` |
| corpora | 138 | `7eac86ede523dff88d25ab0e2c9b83038c4421da66694eafbab54c92a0d8fd37` |


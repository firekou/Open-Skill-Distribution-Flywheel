# Synthetic fixtures (not user data)

Every file here was written by hand for tests. None of them is a first-use
record from a real person, and none may be counted as one. They all use
`record_class: internal_agent_rehearsal`, participant `R1` and year-2000
timestamps. The one exception is `invalid_internal_as_external.json`, which
deliberately claims `external_user` in order to be rejected.

| file | expected | why |
|---|---|---|
| `valid_pass.json` | VALID | fixed task 5/5, test file unchanged, diff reviewed |
| `valid_fail.json` | VALID | honest failure: 2 of 5 failed, `passed=false` |
| `invalid_failed_exceeds_total.json` | INVALID `failed_exceeds_total` | 7 failed out of 5 (the cross-field rule) |
| `invalid_false_pass.json` | INVALID | `passed=true` with failures and a changed test file |
| `invalid_bad_source_url.json` | INVALID | entry URL on a branch, not a 40-character commit |
| `invalid_internal_as_external.json` | INVALID | `external_user` with an internal source and an `R` pseudonym |
| `invalid_malformed.json` | INVALID malformed JSON | not parseable |
| `invalid_secret_not_echoed.json` | INVALID | carries the synthetic marker `SYNTHETIC_SECRET_VALUE_7f3a9c`; the output must not contain it |

# Executor response — ATK-OPEN-ADOPTION-01, revision 1, stage A

Status: **REVIEW_PENDING.** Not self-approved. Independent review by GPT on the exact content SHA
below.

## Claim

| field | value |
|---|---|
| work_id / revision / stage | ATK-OPEN-ADOPTION-01 / 1 / A |
| decision | ATK-OPEN-ADOPTION-20260922 |
| executor session | `session_016YNgsSCC2eV5sicob2f56f` (Claude Code, cloud) |
| policy SHA (trusted main at start) | `2a6becfa6fd792ede44a250171bbbdc93adbc4e3` |
| source head (PR #5) | `304af885193245da7186cb6b9ab247ec2494bd86` — unchanged at start and at push |
| branch | `claude/atk-open-adoption-01-teua0c` (the package names `claude/atk-open-adoption-01`; this session's environment designates the `-teua0c` suffix and cannot push elsewhere. Same work, one branch) |
| dedup key | `firekou/Open-Skill-Distribution-Flywheel:ATK-OPEN-ADOPTION-01:A:1:304af885193245da7186cb6b9ab247ec2494bd86:executor` |
| claimed | 2026-09-22T19:05Z · claim deadline 2026-09-23T19:05Z |
| **content SHA (review this)** | `c3637c4dcf7a0ab86e884dfb6ba07054c93d873d` |
| scope | `adoption/ATK-OPEN-ADOPTION-01/**`, `integrations/headroom-atk/AGENT_QUICKSTART.md`, `integrations/headroom-atk/agent-manifest.json`, this file |

Pre-claim checks (2026-09-22): open PRs #1, #2, #4, #5, #6, #7; none for this work_id. `state.json`
has `active_claim: null` and `receipt: null` for ATK-OPEN-ADOPTION-01. Remote branch equalled
`main` (no prior commits). No duplicate claim.

## What changed

27 new files, 0 modified; nothing from PR #5 copied onto this branch.

- **A1 unified entry.** `TRY_IT.md` @ `304af885` stays the single command source. A doc-only delta,
  `adoption/ATK-OPEN-ADOPTION-01/pr5-doc-delta.patch` (5 files, +38/−11), for the PR #5 owner to
  apply or not:
  - every `git checkout <branch>` → the pinned SHA;
  - free sample: `--retry-max-attempts 1` on its proxy line plus "not a verified live entry, use
    TRY_IT" (R9 backlog item 1);
  - "a successful run makes two attempts either way" → a no-retry fully successful run makes two;
    fail-then-succeed can use three or four (P5-R9-01), in README and the `ab_test.py` docstring;
  - `ab_test.py` docstring install pinned to `==0.37.0` (R9 backlog item 3);
  - links to the agent contract, evidence format and channel plan; DISTRIBUTION.md notes that
    default GitHub search does not read READMEs.
  No executable line changes: `ab_test.py` AST excluding docstrings is identical (checked). The
  PR5 R4–R9 repair-round count is untouched; this is not a third repair.
- **A2 agent contract.** `AGENT_QUICKSTART.md` + `agent-manifest.json` (all required fields).
  New facts it states that the older docs did not: headroom writes state under `~/.headroom/`,
  onnxruntime (transitive) writes a `deviceid` under `~/.cache/…`; the venv must be on `PATH`
  because `local_check.py` runs `headroom` by name; transitive dependencies are not pinned.
- **A3** `DISTRIBUTION_CHANNELS.md` (13 channels, rules and fit), `TRIAL_TASK.md` (three test
  protocols).
- **A4** `CANDIDATES.md` (5 entry points: 2 to send, 3 not, 2 rejected), `INVITATIONS.md` (two
  English replies, agent task text, disclosure list). **Nothing sent.**
- **A5** `EVIDENCE_FORMAT.md`, schema, `validate_records.py` (enforces internal vs invited vs
  discovered), two internal records, `MILESTONES.md` (M1–M5).

## Verification

All commands run by this executor, 2026-09-22, Linux x86_64, Python 3.11.15. Project code ran
through `iso.sh`: empty environment inside a network namespace with loopback only (external
connect → `Network is unreachable`).

| command | result |
|---|---|
| `pip install "headroom-ai[proxy]==0.37.0"` | installed headroom-ai 0.37.0 + 93 others |
| `make_log.py > deploy.log; md5sum` | `0ad9194a489136baa931881b78374cf7`, 1200 lines, 111262 B |
| `local_check.py` | **exit 0**, 111357 → 94578 chars (15.1%), both needles present |
| `local_check.py --log deploy.jsonl --needle …` (negative control) | **exit 3**, identical size |
| `local_check.py --needle NOT_IN_THE_LOG_xyz` | **exit 2** |
| `local_check.py --bogus` | **exit 2**, token not echoed |
| `ab_test.py` with no key | **exit 2**, refuses, no mock |
| `test_local_check.py` (at 304af885 and with the patch applied) | 44 tests OK both times |
| venv python without venv on `PATH` | exit 1, `FileNotFoundError: 'headroom'` (reason for the quickstart note) |
| `grep -r` needle text under `$HOME` after the run | not found |
| `git apply --check pr5-doc-delta.patch` on 304af885 | applies cleanly |
| `check_consistency.py` | 23/23 PASS; with the manifest md5 changed by one character, FAIL (exit 1) |
| `validate_records.py` | 2 records valid; 4 negative fixtures exit 1, 1 positive exit 0 |

Outputs: `adoption/ATK-OPEN-ADOPTION-01/evidence/internal-2026-09-22/`.

### Internal agent tests

1. **INT-2026-09-22-01**: this executor, the run above.
2. **INT-2026-09-22-02**: a subagent in a fresh context given only `AGENT_QUICKSTART.md` and the
   isolation wrapper. It cloned, checked out the SHA, installed, and got exit 0 with output
   identical to the expected block. About 1.5 minutes; no help needed. It re-ran `local_check.py`
   once only to capture a lost exit code, and said so. It reported five unclear points; all five
   were fixed before commit (working dir, fresh-shell `PATH`, why `cd` is needed, SQLite side files,
   re-run for a lost exit code).

Both are **INTERNAL_AGENT_TEST**. Same executor session, not independent, not adoption.

## Not verified

- **Independent isolated replay.** P5-R4-01 and the M1 replay need a reviewer runtime; the
  executor cannot supply one. Our namespace isolation leaves files on disk readable (no route out),
  so it is weaker than the reviewer bar.
- **Live path.** Not run. `ATK_API_KEY`, `ATK_BASE_URL`, `ATK_MODEL` are NOT_SET here; no model
  call; spend 0. KEY-ROTATION status unknown.
- **onnxruntime on a networked machine.** Whether it transmits anything is untested.
- **Other platforms.** macOS, Windows and Python ≠ 3.11 are untested; transitive versions float.
- **Channel rules.** Most were read through a summarising fetch tool. Only headroom #973 was read
  directly. The anthropics/skills CONTRIBUTING returned 404. Discord rules were not checked (login
  needed).
- **Anthropic `/v1/messages` route.** Never tested; the C2 draft says so.
- **Pinned SHA durability.** It resolves only while the PR #5 branch (or a tag) keeps it.

## Adoption evidence classification

| class | count |
|---|--:|
| INTERNAL_AGENT_TEST | 2 |
| EXTERNAL_INVITED_AGENT | 0 |
| EXTERNAL_DISCOVERED_AGENT | 0 |
| external human (either route) | 0 |
| PUBLIC_DISCOVERY / DIRECTORY_DISCOVERY trials | 0 (T0 not reached; not listed anywhere) |

## Next smallest gap

**M1: an independent reviewer replays the offline trial and P5-R4-01 at `304af885`** in a
qualifying isolated runtime (no secrets, no outbound network, read-only source, no write token),
using `evidence/internal-2026-09-22/` as the reference. After that, and once the A4 conditions are
re-checked on the day, the C1/C2 invitations can go out (at most three, one each).

## Owner decisions actually needed

1. **Apply About + topics** (repo settings, owner only). This is the one change that affects
   default GitHub search. Values are drafted in DISTRIBUTION.md @ 304af885.
2. **Keep the pinned SHA reachable before invitations**: do not delete the PR #5 branch, or create
   a tag at `304af885`. This is a repository write.
3. **Which GitHub account posts the invitations**, when the A4 gate opens. The Show and tell post
   is a community post, not an invitation, and needs its own approval.

No merge, deployment, secret or permission change, upstream submission, invitation or spend was
made.

---

# Revision 2 — the five R1 conditions

Status: **REVIEW_PENDING.** Not self-approved, nothing merged, nothing sent. The revision 1
record above is left exactly as it was written; it was true of revision 1, and rewriting it
would destroy the trail. Everything in this section is revision 2.

## Claim

| field | value |
|---|---|
| work_id / revision / stage | ATK-OPEN-ADOPTION-01 / 2 / A-CONDITIONS |
| review answered | [PR8_R1_ATK_OPEN_ADOPTION_c3637c4d.md](PR8_R1_ATK_OPEN_ADOPTION_c3637c4d.md) — APPROVED_WITH_CONDITIONS |
| executor session | `session_01RFeCsTYkVywjHvXk7od7Ab` (Claude Code, cloud) — **not** the revision 1 session |
| source / live head at claim | `77a8200533c80bc288186f58c1d8ecb6d25d121d` |
| reviewed content head (r1) | `c3637c4dcf7a0ab86e884dfb6ba07054c93d873d` |
| **immutable link target (commit A)** | `fb47e31b54b35518322254d0d69d7c7193dc2266` |
| **content SHA for re-review (commit B)** | `8161c6a33251b06c44db9f5dbabc9431fa73b67d` |
| dedup key | `firekou/Open-Skill-Distribution-Flywheel:8:ATK-OPEN-ADOPTION-01:A-CONDITIONS:2:77a8200533c80bc288186f58c1d8ecb6d25d121d:executor` |
| claimed / deadline | 2026-09-22T20:2xZ / 2026-09-23T19:30:00Z |
| repair round | 1 of 2 |
| budget spent | 0. No key, no model call, no provider endpoint, no paid work. |

Pre-claim checks: PR #8 carried exactly one comment (the revision 2 packet) and the head had not
moved from `77a8200` since it was posted, so no other session had taken this packet. Revision 1
was delivered by `session_016YNgsSCC2eV5sicob2f56f`; if that session turns out to have been
working the same packet in parallel, the earlier landed result head wins and this one stands down.

## Why there are two content commits

Condition A-R1-03 asks for immutable entry URLs, and a document cannot contain the SHA of the
commit that introduces it. So the corrections land first, in **commit A**, which holds the final
text of every document the entry links point at; then **commit B** rewrites those links to point
at commit A. Commit B is the content SHA to review. This response and its evidence file are the
only things after it.

## The five conditions

### A-R1-01 — the 27% was not supported by anything (P1)

`INVITATIONS.md` told an outside developer that the same records as plain text shrank 27%. Every
pinned artefact says 15.1%: `111357 → 94578` characters reaching the upstream. There is no source
anywhere in the repository for 27%.

Replaced with the measured figure and bound to what produced it — input md5
`0ad9194a489136baa931881b78374cf7`, headroom 0.37.0, code SHA `304af885…`, from
`evidence/local_check.txt` — and followed by the sentence that matters more than the number:
these are one payload on one version, not a rate to expect.

Search over `adoption/` and `integrations/`: `27%` → **0 matches**.

### A-R1-02 — the egress claim was broader than the evidence (P1)

The documents said, in three places, that nothing leaves loopback. What was actually measured was
one run inside a network namespace with loopback only. Those are different claims, and the
difference is exactly the reader's own machine.

All three files now say the same three things, in the same words:

1. the check's **own** traffic goes only to `127.0.0.1`;
2. installing it **does** use the network (PyPI, GitHub);
3. what the installed third-party packages — onnxruntime in particular — do on an ordinary
   networked machine is **NOT TESTED**.

The isolated run is still reported, now labelled as evidence about that run only. `No telemetry`
is bounded to our own files, with an explicit refusal to speak for third-party packages.

Searches: `nothing leaves` → 0, `leaves loopback` → 0, `no tracking` → 0.

**One instance left untouched, deliberately.** `README.md` at PR #5 `304af885` contains the line
"There is no telemetry here"; it appears in `pr5-doc-delta.patch` as a *context* line, not an added
one. It is PR #5's text, this packet's scope is the three files named above, and the patch is not
applied. Flagging it rather than widening the diff.

### A-R1-03 — the adoption entry was not a fixed version (P1)

Six links in `pr5-doc-delta.patch` pointed at `blob/claude/atk-open-adoption-01-teua0c/…`. A branch
can move or be deleted, so that is not an entry anyone can rely on. `DISTRIBUTION_CHANNELS.md` also
listed the human trial as an abbreviated `…/blob/…` string, which is not a URL at all.

All six now point at commit A, `fb47e31b54b35518322254d0d69d7c7193dc2266`, which carries the final
text of all six target documents. The channels file gives the complete URL. The two parentheticals
that described those links as living on a Draft branch were corrected with them.

The rewrite changed no line counts, so the hunk headers still hold — checked, not assumed: the
patch still applies cleanly to PR #5 at `304af885` and `ab_test.py`'s executable AST is unchanged.

Searches: `blob/claude/atk-open-adoption` → 0, `…/blob` → 0.

### A-R1-04 — the validator did not apply its own schema (P2)

`validate_records.py` read the schema file but enforced only `required`, `additionalProperties`
and the enums. Everything the schema expresses about *shape* — `type`, `pattern`, `minItems`,
`minimum`, `items`, `const`, `anyOf` — was documentation, not a check.

It now applies them, as a stdlib subset covering exactly the keywords this schema uses, in a
schema layer that runs before the three semantic rules. Both layers block; errors say which layer
rejected the record. One thing worth naming: booleans and integers are no longer interchangeable,
so `operator_external: 1` is a type error rather than a silent `true` — Python's `1 in [True, False]`
is what made that pass before.

The control is the point of the change, so it is measured both ways:

| | |
|---|---|
| r1 validator (`@77a8200`) on `bad_schema_constraints.json` | **exit 0** — it accepted the record |
| revision 2 validator on the same file | **exit 1**, naming all six violations |
| the same validator with the schema layer deleted | **exit 0** — so the fixture fails *because of* the new layer, not by accident |

The new fixture carries six violations and **no** semantic violation, which is what makes it a
clean control: only the new layer can reject it. The four pre-existing negative fixtures still
exit 1, the positive fixture and both real records still exit 0.

`EVIDENCE_FORMAT.md` now describes both layers. The README's word "enforced" is true as of this
revision; it was not before.

### A-R1-05 — INT-02 count typo

`records/INT-2026-09-22-02.json` said four of the five doc ambiguities were fixed and then listed
five. The executor response said five. Changed to five.

## Commands and results

All offline, all in this container, no key and no model call.

| command | result |
|---|---|
| `validate_records.py records/*.json` | **exit 0** (2 records) |
| `validate_records.py test_fixtures/ok_unverified.json` | **exit 0** |
| `validate_records.py` on each of the 5 negative fixtures | **exit 1** each |
| r1 `validate_records.py` on `bad_schema_constraints.json` | **exit 0** — the control that shows the gap was real |
| schema-layer-removed mutant on the same fixture | **exit 0** — the control that shows the fix is what closes it |
| `check_consistency.py` | **24/24 PASS, exit 0** (23/23 at revision 1; the new fixture adds one) |
| `git apply` of `pr5-doc-delta.patch` on `304af885` | applies cleanly |
| `ab_test.py` AST before/after the patch | identical |
| `grep -rni` for `27%`, `blob/claude/atk-open-adoption`, `…/blob`, `nothing leaves`, `leaves loopback`, `no tracking` | **0 matches each** |
| JSON parse of all 11 JSON files under `adoption/` and `integrations/headroom-atk/` | all parse |

Raw output: `adoption/ATK-OPEN-ADOPTION-01/evidence/r2-conditions/controls.txt`.

## The immutable entry URLs, written out

- Agent contract:
  `https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/fb47e31b54b35518322254d0d69d7c7193dc2266/integrations/headroom-atk/AGENT_QUICKSTART.md`
- Agent manifest:
  `https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/fb47e31b54b35518322254d0d69d7c7193dc2266/integrations/headroom-atk/agent-manifest.json`
- Human trial (PR #5, unchanged):
  `https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/304af885193245da7186cb6b9ab247ec2494bd86/integrations/headroom-atk/TRY_IT.md`

`<QUICKSTART_URL>` in `INVITATIONS.md` stays a placeholder on purpose: it is filled on the day of
sending with the reviewed result SHA, and sending is not authorised.

## Still not verified, and not claimed

- **M1 / P5-R4-01 independent isolated replay** — reviewer work. Not attempted, not substituted.
  The review records that `bwrap` network isolation is refused by the OS in the reviewer's
  environment; that is the same wall this repository has hit for several rounds.
- **The live path** — no key, no endpoint check, no spend.
- **onnxruntime on a networked machine** — untested, and now said so in all three documents.
- **Anything but Linux / Python 3.11.**
- **External adoption: still 0.** Nothing was sent; nothing could have been adopted.

## Not done

No merge · no deploy · no invitation sent · the PR #5 patch is still **not applied** · no
settings, secrets or permissions change · nothing sent upstream · no spend · no finding closed by
the executor (`findings_closed_by_executor: []`).

Stopping here for the second independent review of content SHA
`8161c6a33251b06c44db9f5dbabc9431fa73b67d`.

---

# Revision 3 — A4 precheck, the last bounded round

Status: **REVIEW_PENDING.** Not self-approved. **Nothing was sent.** Revisions 1 and 2 above are
left as written; they were true when written.

## Claim

| field | value |
|---|---|
| work_id / revision / stage | ATK-OPEN-ADOPTION-01 / 3 / A4-PRECHECK |
| review answered | [PR12_R1_A4_PRECHECK_707dc26d.md](PR12_R1_A4_PRECHECK_707dc26d.md) — BLOCKED |
| executor session | `session_01RFeCsTYkVywjHvXk7od7Ab` (same session as revision 2) |
| source head at claim | `b76fc7ba08deade6733f140d3a37aadfd201d51c` |
| reviewed precheck head | `707dc26d15d8b0a2a6a34cb0364fd73f68e397d8` |
| **content SHA for review** | `9bcd4181cd3fb87bea108c93df28b96f1767bfd5` |
| dedup key | `firekou/Open-Skill-Distribution-Flywheel:8:ATK-OPEN-ADOPTION-01:A4-PRECHECK:3:b76fc7ba08deade6733f140d3a37aadfd201d51c:executor` |
| claimed / deadline | 2026-09-23T15:1xZ / 2026-09-24T14:46:00Z |
| repair round | **2 of 2 — the last one** |
| budget spent | 0. No key, no model call, no provider endpoint. |

Pre-claim check: `governance/state.json` revision 19 had `a4_precheck_repair.delivery_status:
SIGNAL_SENT_NO_RECEIPT` and `active_claim: null`, and PR #8's head had not moved from `b76fc7b`.
No other session had taken it.

## The three blocking findings

### A4-R1-01 — the two recipients do not match the asset

Both withdrawn as **`NOT_ELIGIBLE_FOR_THIS_ASSET`**.

| | C1 (#2732) | C2 (#973) |
|---|---|---|
| what they asked | why Command Code's request shape is rejected; then whether **9router** changes shapes or headers | how to point **Anthropic** requests at a custom upstream, "like I can in case of OpenAI" |
| what the asset does | measures bytes reaching the upstream and whether a needle survives, on the OpenAI chat-completions route | the same, on the same route |
| where it stops | never runs Command Code, never runs 9router, **never captures a request schema at all** | **has never been run against `/v1/messages`** |

The C1 draft opened with a router "can" change what headroom does. **Removed, not softened** — we
have no evidence for it. An unevidenced causal sentence is precisely the defect this loop keeps
catching, and softening the wording would have preserved it.

The C2 draft was already honest that we have not tested `/v1/messages`. That honesty is the
disqualification: a reply whose first substantive line is "I cannot answer your question, but here
is our tool" is off-topic promotion however politely it is written.

**Why they were ranked 1st and 2nd before.** They were scored on topic adjacency — they are about
routing and compression, we measure routing and compression — instead of on whether our output
answers their sentence. `CANDIDATES.md` now forces the three columns above for every candidate,
and a candidate fails unless columns 1 and 2 are the same question.

### A4-R1-01 (second half) — looking for a candidate that does fit

Searched the public headroom Q&A (open and unanswered) and the issue tracker for anyone asking
whether their own long logs shrink, or how to tell whether a critical line survived.

| looked at | result |
|---|---|
| Q&A, open and unanswered | thread safety, Redis for CCR, desktop integration, deployment, ToS, assorted errors. Nothing about payload compressibility or verifying a critical line |
| issue #2050 "0% savings wrapping Codex" | **closed**; `wrap`/Codex and savings accounting |
| issue #2248 "no compressed/saved tokens after upgrade" | **closed**; dashboard accounting after a version change |
| issue #3736 (open, 2026-09-23) ISO-8601 logs folded lossily in 0.38.0 | closest public match — 5 of 2,000 lines survive, timestamps rewritten. **Still not a candidate:** bug tracker, not an invitation channel; the reporter already wrote their own reproduction and root-caused it; and it is 0.38.0 while this asset pins 0.37.0 |

**Result: 0 eligible candidates. The three-recipient allowance stays unused.**

Delivering zero is what the gate is for. The temptation here was real and worth naming: #3736 is
so close to our question that sending something would have felt justified — and it would still
have been us answering a question nobody asked us.

Worth recording as evidence about the asset rather than about outreach: #3736 is the first public
confirmation that "did the line that matters survive?" is a question real users hit in production,
and that **a minor version bump can change the answer**. Our pinned 0.37.0 does not exhibit it.
That is a statement about what we pinned, not a claim about 0.38.0.

### A4-R1-02 — the authorisation was not the gap; the account is

Recorded as two separate things, because the precheck had collapsed them into one:

| | |
|---|---|
| A4 limited-send authorisation | **EXISTS** — up to three recipients, one message each. **Not re-asked.** |
| owner-approved sender login | **not recorded** |
| capability evidence (can reply in the target Discussion under that login) | **none** |
| status | **`BLOCKED_ACCESS`** |

The only thing needed from the owner is *which account*. No test comment was posted to find out:
posting to check whether we can post is itself a send.

### A4-R1-03 — the pinned external document was out of date

Quickstart §9 said an independent isolated replay was pending. It is not: PR #10 closed
`P5-R4-01`. §9 now says what was replayed (the unknown-argument case, including the dash-leading
one), under what conditions (`--network none`, read-only source, no secrets, no write token), that
the reviewer also confirmed the old build still fails it, and links the review at an immutable
`main` SHA.

It then says, in the same breath, what the replay is **not**: not a clean install, not a license
review, not a live provider run, not a release, not adoption — and that it binds to that exact PR
#5 SHA, so if the code moves the replay does not move with it.

### Also in this round

`EVIDENCE_FORMAT.md` said `test_fixtures/` holds "four records that must fail". It holds five —
my own omission in revision 2, when I added the fifth fixture and updated the prose above it but
not the count below it. Corrected. Validator logic untouched.

## The immutable entry URL

Read back after pushing, not assumed:

```
https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/9bcd4181cd3fb87bea108c93df28b96f1767bfd5/integrations/headroom-atk/AGENT_QUICKSTART.md
```

Blob `503136498e9de7c76bb9ac4f59f714dc7270427d` — the local object id at the content commit and
the id GitHub served back are the same, and the served §9 is the corrected text.

This is the URL `<QUICKSTART_URL>` resolves to. It is not in use, because there is nobody eligible
to send it to.

## Commands and results

| command | result |
|---|---|
| `check_consistency.py` | **24/24 PASS, exit 0** |
| `validate_records.py records/*.json` | exit 0 |
| the 5 negative fixtures / the positive fixture | exit 1 each / exit 0 |
| `grep -rni` for `27%`, `blob/claude/atk-open-adoption`, `…/blob`, `nothing leaves`, `leaves loopback`, `no tracking` | **0 each** — revision 2's closures did not regress |
| `grep` for the withdrawn `it can, and the only…` sentence | **0** |
| GitHub read-back of the Quickstart at the content SHA | blob id matches the local object id |

Public pages re-read on 2026-09-23 (read-only, no posts): discussions #2732 and #973 (both open,
both still Unanswered), issues #2050, #2248, #3736, and the open/unanswered Q&A list.

## Still not established

- **External adoption: 0.** Nothing was sent, so nothing could have been adopted.
- **Sender account:** `BLOCKED_ACCESS`.
- **Eligible recipients:** 0.
- The live path, onnxruntime on a networked machine, and anything but Linux / Python 3.11 —
  unchanged and still stated as unknown in the documents.

## Not done

No invitation or comment sent to any third party · PR #5 patch still **not applied** · no merge ·
no deploy · no settings, secrets or permissions change · nothing sent upstream · no spend · no
validator logic change · `findings_closed_by_executor: []`.

Stopping here for the final independent review of content SHA
`9bcd4181cd3fb87bea108c93df28b96f1767bfd5`.

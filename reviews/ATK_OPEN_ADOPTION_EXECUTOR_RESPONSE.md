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

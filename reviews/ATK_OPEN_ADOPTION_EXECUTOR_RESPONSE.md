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

# Try it in ten minutes — offline first, live only if you choose to

One task, start to finish: **a 1,200-line deploy log with one failed database migration buried in
it.** You ask for the migration name and the exact SQLSTATE code, and you find out whether putting
a compression proxy in front of your provider still gets you that answer.

**Step 1 costs nothing and sends nothing anywhere.** Step 2 spends real tokens and needs a key, and
this page will not let you drift into it by accident.

---

## Before you start: what leaves your machine

| | what runs locally | what is sent out |
|---|---|---|
| **Step 1**, the offline check | everything — the proxy and a stub upstream, both on `127.0.0.1` | **nothing** |
| **Step 2**, the live run | the compression step only | **the compressed prompt, to your provider** |

Compression happens *before* the request leaves, not *instead of* it. If your logs must never
reach a third party at all, stop after step 1 — it is a preflight, not a way to use a model.

---

## Step 1 — offline (no key, no cost, no network beyond loopback)

```bash
git clone https://github.com/firekou/Open-Skill-Distribution-Flywheel
cd Open-Skill-Distribution-Flywheel
git checkout claude/atk-headroom-adoption      # NOT on main yet — PR #5, Draft

python3 -m venv .venv && . .venv/bin/activate
pip install "headroom-ai[proxy]==0.37.0"       # the version every number here was measured on

cd integrations/headroom-atk
python3 make_log.py > deploy.log               # synthetic; md5 0ad9194a489136baa931881b78374cf7
python3 local_check.py
```

The question it asks, and the two things that must survive, are already built in:

> *Did any database migration fail? Give the migration name and the exact SQLSTATE code.*
>
> needle 1 — the migration name · needle 2 — the SQLSTATE

**What a good result looks like** (measured on this machine, 2026-09-21, headroom 0.37.0):

```
log        : deploy.log — 1200 lines, 111262 bytes
direct     : 111357 chars reached the upstream
via proxy  : 94578 chars reached the upstream  (15.1% fewer)
needle #1 (18 chars): present after the proxy
needle #2 (5 chars): present after the proxy
PASS: 16779 fewer characters (15.1%) and every needle survived
```

### Then run it on YOUR log — this is the step that actually decides

The sample proves the plumbing. It says nothing about your logs, and for a large class of logs the
honest answer is *no benefit*:

```bash
python3 local_check.py --log /path/to/your.log --needle "the line that must survive"
```

| exit | what it means | what to do |
|--:|---|---|
| **0** | smaller, and every needle survived | this payload is a candidate |
| **3** | no size benefit, **confirmed twice** | do not adopt for this payload. Common with JSON-lines logs |
| **1** | a needle was lost | **do not adopt for this payload** |
| **2** | misuse — no needle, an empty needle, or a needle not in the log | fix the command |
| **4** | two measurements disagreed | **nothing is concluded.** Run it again |

Exit 4 exists because of something we hit ourselves: the first proxy start in a fresh container
reported a byte-for-byte pass-through on a payload that the next 22 runs compressed by 15.1%. We
did not establish why. What we did do is stop the tool from explaining a one-off negative with a
confident cause — the old message would have told you your log has no redundancy, and you would
have believed it and left.

**The output is safe to paste into an issue.** Needles are reported by position and length, never
their text, and the log's file name is printed rather than its path. `--show-needles` turns that
off for your own terminal — do not use it for anything you intend to share.

---

## Step 2 — live, only when permission and a spend limit are explicit

**Do not start here.** Everything above is free and answers the adoption question. This step
answers a different one: what the token counts actually are against a real provider.

You need all four, and "we have a key" is not three of them:

1. A valid key injected by your environment — **never on the command line, never in a file in this repo**.
2. An endpoint you have confirmed. For ATK the historical value is
   `https://api.aitokenking.com.tw/api` in the `x-headroom-base-url` header — **without** `/v1`.
3. A model you have confirmed is available to your account. The 2026-09-18 run used
   `claude-sonnet-4.6`; that is a record, not a guarantee for your account today.
4. An explicit spend ceiling, agreed before the first call.

```bash
headroom proxy --port 8787 --no-http2 &

# The key is already injected by your environment or secret manager. Confirm it
# is there WITHOUT printing it:
[ -n "$ATK_API_KEY" ] && echo SET || echo NOT_SET

python3 ab_test.py
```

**Do not prefix the key to the command as a variable assignment.** That form lands in shell
history, in terminal recordings and in any command auditing you have — and an earlier version of
this page said so two paragraphs above an example doing exactly it. If your key is not already in
the environment, put it there the way you put every other secret there; this page will not show
you a shortcut that leaks.

`ab_test.py` refuses to run without `ATK_API_KEY` and substitutes no mock.

**What it will spend, stated before it spends it.** The default is the needle task only:

```
about to make exactly 2 live calls (1 direct + 1 via proxy) for task(s): needle.
No automatic retries: a failed call stops the run.
```

That line is printed before the first request goes out. `--task both` adds the five-bullet summary
task and prints `exactly 4` instead — you have to ask for it. An earlier version of this page
authorised two calls and then told you to run a command that made four.

### Record this, and only this

Fill one of these per live run. It is written so that a completed record contains nothing you
would mind pasting into a public issue.

```
date / time (UTC):
input file:               make_log.py output
input md5:                0ad9194a489136baa931881b78374cf7
input size:               1200 lines, 111262 bytes
headroom version:
python / OS:
endpoint (host only):
model actually returned:  (the provider's own value, not the one you asked for)
prompt:                   the built-in question, or quote yours
path:                     direct | via proxy
prompt tokens:            (from the provider's usage field, not an estimate)
completion tokens:
usage field present?      yes | no
answer — migration name:  found | not found
answer — SQLSTATE:        found | not found
wall time:
error type, if any:       (the CLASS of error: auth, 404, timeout, rate limit — not the body)
```

**Never record:** the key, any part of it, a real customer log, or a raw error body. A provider
error body can echo fragments of whatever key you sent.

**Do not fill this in from a reconstruction.** The 2026-09-18 live figures in the README are a
historical case whose exact input was not preserved, so they cannot be re-run identically even by
us. A new run is a new record with its own numbers — it does not "reproduce" that one.

---

## If it did not work

Three failures we hit, in the order people hit them, are written up with the exact error text in
[README.md](README.md) under *The three things that will trip you up*. Short version:

1. Setting `OPENAI_BASE_URL` does **not** point the proxy at your provider — you will get an
   OpenAI 401 that looks like a provider problem and is not.
2. The `x-headroom-base-url` header takes the base **without** `/v1`.
3. A loopback or private-network upstream is refused by the SSRF guard, and the explanation is in
   `~/.headroom/logs/proxy.log` — not on stderr and not in `--log-file`.

Anything else: <https://github.com/firekou/Open-Skill-Distribution-Flywheel/issues>.
**Third-party reports to date: none.** There is no telemetry here, so an issue is the only way we
would ever learn this helped or failed.

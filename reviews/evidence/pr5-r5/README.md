# PR5 R5 replay handoff (not executed here)

Reviewed head: `32ca53cd703efeb647ddb2d65168ba69f1e414d6`.
Baseline: `d1930e4696f11cfb3cdae2f59d1b3692b68ee127`.
This is a prepared reviewer test, NOT a passing runtime result.

Prepare source snapshots from GitHub at those exact commits. Put current
`integrations/headroom-atk/{local_check.py,ab_test.py,test_local_check.py,README.md}`
in an input directory's `current/`, and the baseline's `local_check.py` in
`previous/`. The script verifies every Git blob hash against manifest.json.
Do not copy credentials, .git, user logs, HOME, or environment secrets.

Use an independently provisioned secret-free runner with:
read-only source mounts; a private writable /tmp; network disabled; no host HOME,
Docker socket, credentials or GitHub-write token; dropped capabilities,
non-root execution, CPU/memory/PID limits and a bounded timeout.

Example ONLY where a suitable pre-existing Python 3.11+ image and Docker runtime
are already available. IMAGE must be a verified, locally available pinned image;
do not pull or install anything to bypass this run's restrictions.

```sh
timeout 180 docker run --rm --pull=never --network none --read-only \
  --cap-drop ALL --security-opt no-new-privileges --user 65534:65534 \
  --pids-limit 64 --memory 256m --cpus 1 \
  --tmpfs /tmp:rw,nosuid,nodev,size=64m,mode=1777 \
  --mount type=bind,src="$INPUT",dst=/input,readonly \
  --mount type=bind,src="$EVIDENCE",dst=/evidence,readonly \
  --env HOME=/tmp --env PYTHONDONTWRITEBYTECODE=1 \
  --entrypoint python3 "$IMAGE" \
  /evidence/reviewer_checks.py /input /evidence/manifest.json
```

Capture exit status and stdout/stderr in the reviewer run, then persist them
with runner identity, actual isolation configuration, Python version and full SHA.
The script expects five private-token controls to pass, the same dash-leading
input to reproduce on the old revision, help/legal forms to work, 31 unit tests
to pass, verdict positive/negative controls and HTTP body controls to remain
correct. Process/network boundaries in verdict checks are mocked: these do not
prove a real proxy, clean installation or paid API.

If isolation cannot be established, do not execute the PR source. Keep
P5-R4-01 pending verification. Only an independent reviewer may close it.
No executor implementation change is requested by this evidence gap.

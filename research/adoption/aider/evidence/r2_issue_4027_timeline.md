# Aider-AI/aider #4027 — full timeline as fetched

- Fetched: 2026-09-25T18:10:51Z UTC
- Tool: Exa web_fetch_exa on https://github.com/Aider-AI/aider/issues/4027 (maxCharacters 20000)
- Why this tool: revision 1 used WebFetch, which returned the issue body only. The timeline and comments were not in what it returned, and revision 1 did not notice they were missing. The GitHub API route (curl and the GitHub MCP) returned 403, because this repository is not attached to the session. It was not attached, because the tool's own guidance says not to add repositories the user has not asked for.
- The text below is a verbatim extract of the fetched page. Nothing has been paraphrased into the quotes.

## Header
- State: closed
- Author: psymonryan
- Created: 2025-05-15T07:36:01Z
- Updated: 2025-09-19T05:49:56Z
- Labels: priority

## Body (version line)
> Aider v0.83.1 · Model: openai/Qwen3-32B with diff edit format

## Timeline
1. **Axenide**, 2025-05-22T00:29:37Z
   > In my case, it worked without the `/v1`, but now it doesn't, with or without it.
   > Exporting the endpoint in the command line works, but I didn't need to do that before.
2. **psymonryan**, 2025-05-26T03:25:08Z
   > This bug will be affecting all users of local LLMs who are using architect mode or expecting the endpoint to correctly select the model (such as with llama-swap)
3. **psymonryan**, 2025-06-01T04:06:32Z. Cause narrowed to the litellm bump between aider 0.82.2 and 0.82.3:
   > -litellm==1.65.7
   > +litellm==1.68.0
   > …I just built the latest aider with requirements modifed to use litellm 1.65.7 and the issue goes away
4. **psymonryan**, 2025-06-01T04:54:11Z
   > In the release notes for litellm 1.68.0 there is mention of support for a new OPENAI_BASE_URL being added.
   > …"OPENAI_BASE_URL is the new canonical ENV variable."

   Proposed patch: also set `os.environ["OPENAI_BASE_URL"] = args.openai_api_base` in `aider/main.py`.
5. Referenced by **PR #4144**: "fix: Restore full base path at api endpoint for litellm >= 1.68.0"
6. **paul-gauthier** added label "priority"
7. **psymonryan**, 2025-09-19T05:49:56Z
   > I'm no longer able to reproduce this issue on v0.86.1, hence closing.
8. psymonryan closed the issue.

## Not established by this fetch
- Whether PR #4144 was merged, and in which version.
- Whether the fix reached users through aider or through a later litellm release.
- The pinned source `5dc9490` `main.py:620-621` sets only `OPENAI_API_BASE`, not `OPENAI_BASE_URL`. Where the fix actually lives is therefore **unknown**, and no claim about it is made.

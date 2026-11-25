---
name: creator-stack
description: Research YouTube topics, run a bounded research-script-QA pipeline, or prepare a local YouTube Short handoff. Use for creator workflows and optional RTK summaries, not for uploading or scheduling.
---

# Creator Stack

Use the requested audience, language and format. Locate the user's local Creator Stack folder first; if it is unavailable in the current environment, explain and continue with public sources or a manual draft, not a fictitious run.

- For research, use verified public examples. Prefer available read-only tools such as vidIQ or `research/youtube_public.py` if the local environment has the user's authorized YouTube Data API key. Never ask for the key in chat, print it, or assume private analytics. Explain sample limits and distinguish observations from ideas.
- Use the LangGraph research → script → QA roles for a bounded draft and require human review. Do not use separate agents for trivial steps, copy downstream each role's full context, or recast a fixture as live research.
- If given a real export, run the YouTube preflight on it and write a local metadata draft. Do not upload, publish, create a schedule or modify accounts just to test.
- Use RTK only as an explicit prefix on repetitive supported commands such as `git status`; use native output for errors or when precision matters. RTK summaries do not reduce every prompt's model token count.

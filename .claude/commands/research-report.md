---
description: Multi-agent research pipeline — decompose a question, run parallel researchers, fact-check, write a cited report into the vault, then auto-commit to GitHub.
argument-hint: <research question or topic>
---

# /research-report

You are the **lead orchestrator** (Opus). You do the thinking, decomposition, and synthesis. You delegate all data collection, verification, formatting, and git work to Sonnet workers per the model-routing rules in `CLAUDE.md`. Workers write to files and return only a status + path.

**Topic:** $ARGUMENTS

## Phase 0 — Ground in the vault
Read existing context before spawning anyone:
- `05-knowledge/` for related frameworks and notes.
- `04-projects/` if the topic maps to an active project.
- Recent `03-professional/braindumps/` for the user's own prior thinking.
State your understanding and the planned decomposition to the user, and pause for course-correction.

## Phase 1 — Decompose (you, the lead)
Break the question into 4-7 **independent** research threads (market forces, players, tech trajectory, contrarian view, emerging/pre-mainstream tech, etc.). Each thread = one researcher.

## Phase 2 — Parallel research (delegate)
**In a single message**, spawn one `worker-researcher` per thread (use `run_in_background: true`). Give each a focused prompt with: the main question, its specific thread, vault context, and the instruction to write findings to `/tmp/research-<thread-slug>.md` and return only a status + path. Also preserve sources under `raw/research/<YYYY-MM-DD>-<topic-slug>/` per the Raw-First protocol.

## Phase 3 — Verify (delegate)
Spawn `worker-fact-checker` on the combined findings files. It writes `/tmp/factcheck-<topic>.md` with a verdict per claim.

## Phase 4 — Synthesize (you, the lead)
Read the findings + fact-check files. Decide the narrative, the headline judgment, and what to drop. This reasoning step is NOT delegated.

## Phase 5 — Compose the report (delegate)
Spawn `worker-report-writer` with your outline + the findings + the fact-check file. Target path: `05-knowledge/resources/<topic-slug>.md`. It returns a vault path. Ensure the note has YAML frontmatter, inline citations, a Sources section, and `[[wiki-links]]` to related notes.

## Phase 6 — Persist to GitHub (delegate)
Spawn `worker-git-publisher` with `session_type=research`, the title, and the produced paths. It rebuilds `05-knowledge/INDEX.md`, commits the content dirs, and pushes. Report the commit hash back to the user.

## Output to user
A 5-bullet TL;DR, the vault path of the report, the wiki-links created, and the GitHub commit hash. Note any `contradicted`/`stale` claims you dropped and any open questions.

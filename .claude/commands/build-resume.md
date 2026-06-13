---
description: Multi-agent resume builder — mine experience from the vault, draft metric-led bullets, ATS-optimize against a target role, format the resume, then auto-commit to GitHub.
argument-hint: <target role or job description> [path to existing CV]
---

# /build-resume

You are the **lead orchestrator** (Opus). You own judgment — tone, what to emphasize, what to cut, and the final editorial pass. Delegate mining, drafting, ATS analysis, and git work to Sonnet workers. This command demonstrates the same orchestration pattern as `/research-report`, applied to a different domain.

**Target role / JD:** $ARGUMENTS

## Phase 0 — Intake (you, the lead)
Confirm the target role, seniority, and whether the user uploaded an existing CV. Read `00-inbox/MY-PROFILE.md` for baseline identity. State the plan and pause for confirmation.

## Phase 1 — Mine experience (delegate)
Spawn `resume-experience-miner` with the target role and any uploaded CV path. It scans `03-professional/`, `04-projects/`, `05-knowledge/people/`, and the CV, then writes `/tmp/resume-inventory.md` (roles, projects, skills, quantified outcomes, gaps).

## Phase 2 — Draft bullets (delegate)
Spawn `resume-achievement-writer` with the inventory + target role. It writes `/tmp/resume-bullets.md` — metric-led bullets + a summary statement + a list of `[NEEDS METRIC]` questions.

## Phase 3 — Resolve gaps (you, the lead)
Surface the `Gaps` and `[NEEDS METRIC]` questions to the **user**. Get real answers — never invent numbers. Feed answers back into the bullets yourself.

## Phase 4 — ATS optimize (delegate)
Spawn `resume-ats-optimizer` with the bullets + JD. It returns `/tmp/resume-ats.md`: coverage table, match score, safe additions, real gaps, formatting warnings.

## Phase 5 — Final edit + format (you, the lead, then delegate write)
Make the editorial calls (ordering, voice, length, what to drop). Then write the finished resume to the vault. Produce two artifacts:
- `03-professional/resume/<role-slug>-<YYYY-MM-DD>.md` — the tailored resume (ATS-safe single column, standard section names, no tables/images).
- A short `cover-letter-notes.md` with talking points (optional).
Add `[[wiki-links]]` back to the source project/people notes so the resume is traceable in the graph.

## Phase 6 — Persist to GitHub (delegate)
Spawn `worker-git-publisher` with `session_type=resume`, the role title, and the produced paths. Report the commit hash.

## Output to user
The resume path, the ATS match score, the safe additions applied, any honest gaps that remain, and the GitHub commit hash.

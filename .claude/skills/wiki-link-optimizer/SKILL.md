---
name: wiki-link-optimizer
description: Self-improving agent that strengthens the vault's [[wiki-link]] graph. Detects broken links and orphan notes, proposes high-value missing links between related notes, applies the ones you approve, and learns from every accept/reject so future proposals get better. Invoke with "improve my wiki links", "fix the knowledge graph", "find missing links", or run on a schedule after research sessions.
roles: [all]
integrations: []
---

# Wiki-Link Optimizer (self-improving)

## When to invoke
- After a `/research-report` or `/build-resume` session, to weave the new notes into the graph.
- On a cadence (weekly) to keep the graph healthy.
- When the user says "improve wiki links", "fix the graph", "find orphan notes", "what should link to what".

## What makes it self-improving
The engine keeps a **memory ledger** at `.claude/memory/wiki-link-memory.json`. Every run reads it and every approval writes to it. Over time the agent:
1. **Never re-proposes a rejected pair** (they're remembered in `rejected_pairs`).
2. **Re-weights its scoring signals** — if you keep accepting links driven by `title_mention`, that signal's weight rises; if you reject links driven by `tag_overlap`, that weight falls.
3. **Retunes its threshold** gently toward the boundary between what you accept and reject (clamped to a sane band so it never starves itself of suggestions).
4. **Learns aliases** when you accept title-mention links.

The agent's behaviour is therefore shaped by the user, transparently — every weight change is logged in the ledger's `log` array. This is the "self-improving" loop: propose → decide → record → adjust → propose better.

## The engine
All graph math is deterministic and lives in `scripts/wiki_graph_optimizer.py` (stdlib only — no dependencies). The agent (you) drives it and supplies the judgment:

| Step | Command | Who decides |
|------|---------|-------------|
| Analyze graph | `python3 scripts/wiki_graph_optimizer.py analyze` | engine (mechanical) |
| Review proposals | read `/tmp/wiki-proposals.md` | **agent + user (judgment)** |
| Apply approved | `python3 scripts/wiki_graph_optimizer.py apply --proposals /tmp/wiki-proposals.json` | engine writes + learns |
| Inspect learning | `python3 scripts/wiki_graph_optimizer.py status` | — |

## Workflow

### Phase 1 — Analyze (delegate to the engine)
Run `analyze`. It scans `03-professional/`, `04-projects/`, and `05-knowledge/`, builds the link graph, and writes two files:
- `/tmp/wiki-proposals.md` — human-readable: broken links, orphan notes, and a ranked table of suggested new links.
- `/tmp/wiki-proposals.json` — machine-readable, one entry per candidate with a `"decision": ""` field to fill in.

The command prints a one-line JSON summary (counts + file paths). Read the `.md` file — do **not** dump the whole thing into the conversation; summarize the top findings for the user.

### Phase 2 — Judge (this is your job, not the engine's)
For each broken link: either fix the target name (typo / renamed note) or remove the dead link. Present these to the user.
For each suggested link: decide `accept` or `reject`. Apply judgment the engine can't:
- Is the link *meaningful* (genuinely related) or just lexically similar?
- Would it help future-you navigate, or is it noise?
- Prefer linking to the most canonical note on a topic, not every co-occurrence.
Write your decision into each candidate's `"decision"` field in `/tmp/wiki-proposals.json`. For anything you're unsure about, ask the user — their accept/reject is what trains the agent.

### Phase 3 — Apply + learn (delegate to the engine)
Run `apply`. The engine inserts accepted links into each note's `## Related` section, records accepted/rejected pairs in the ledger, and nudges its weights + threshold. It returns the new weights and threshold so you can report what changed.

### Phase 4 — Reindex + persist
Run `python3 scripts/build_wiki_index.py`, then hand off to `worker-git-publisher` (or run `scripts/git_autocommit.sh wiki "graph maintenance"`) so the improved graph and the updated ledger are committed to GitHub.

## Output to user
Report: notes scanned, broken links fixed, orphans resolved, links added, and — importantly — **how the agent's weights/threshold shifted** this run (from the `apply` output). That visibility is the point: the user can see the agent learning.

## Rules
- Never auto-accept. Suggestions are proposals; a human (or the lead with clear reasoning) approves them. The learning signal is only meaningful if decisions are real.
- Never fabricate a note to satisfy a broken link — fix the link or remove it.
- Keep the conversation lean: the proposal files hold the detail; you summarize.
- The ledger is memory — commit it. Deleting `.claude/memory/wiki-link-memory.json` resets the agent to a beginner.

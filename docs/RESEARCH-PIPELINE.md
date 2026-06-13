# COG Research Pipeline

A multi-agent **research → report → publish** pipeline for [Claude Code](https://docs.claude.com/en/docs/claude-code/overview), built on top of the [COG second-brain](https://github.com/Perryong/knowledge-brain/tree/main/COG-second-brain) vault. It decomposes a question, runs parallel research agents, fact-checks them, writes a cited markdown report into the vault with Obsidian `[[wiki-links]]`, and **auto-commits the session to GitHub**.

It ships with a second orchestration demo — `/build-resume` — that reuses the exact same lead-and-workers pattern for a completely different task, to show the architecture is general.

> This add-on drops into the `COG-second-brain` directory. It extends COG's existing worker-agent convention (Opus lead + Sonnet workers, defined in `CLAUDE.md`); it does not replace anything.

---

## TL;DR answers to your questions

- **Do you need to build an MCP for the research?** **No, not to make it work.** Claude Code already ships the tools the pipeline needs: `WebSearch`/`WebFetch` (research), `Read`/`Write`/`Glob`/`Grep` (vault files), and `Bash` (git). Subagents + slash commands + a hook cover orchestration and auto-commit with zero MCP. Build an MCP only when you want the extra things described in [Do I need an MCP?](#do-i-need-an-mcp) — and this repo includes one working example (`mcp/research_vault`) so you have the pattern either way.
- **Auto-commit to GitHub after each session?** Yes — handled by `scripts/git_autocommit.sh` + `scripts/build_wiki_index.py`, invoked by the `worker-git-publisher` subagent at the end of every run (with an optional `Stop` hook as a fallback).
- **Resume-building orchestration?** Yes — `/build-resume` plus four resume subagents demonstrate the same pattern.

---

## Architecture

Two layers: a **thinking layer** (the Opus lead session, which owns decomposition, synthesis, and judgment) and a **doing layer** (Sonnet worker subagents, each with its own isolated context window, narrow tool permissions, and a single job). Workers write results to files and return only a short status + path — this keeps the lead's context small and lets workers run in parallel.

```
                            ┌──────────────────────────────────────────┐
                            │   LEAD SESSION  (Opus)                    │
   /research-report  ─────► │   slash command = orchestrator            │
   /build-resume     ─────► │   • reads vault for context               │
                            │   • decomposes the task                   │
                            │   • synthesizes + makes judgment calls     │
                            └───────┬───────────────────────┬───────────┘
                                    │ spawns (parallel)      │ spawns (sequential)
                  ┌─────────────────┼─────────────┐         │
                  ▼                 ▼             ▼          ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────────┐
        │worker-       │  │worker-       │  │worker-   │  │worker-         │
        │researcher    │  │researcher    │  │researcher│  │fact-checker    │
        │(thread A)    │  │(thread B)    │  │(thread C)│  │(verifies all)  │
        │WebSearch/    │  │              │  │          │  │WebSearch/Fetch │
        │WebFetch      │  │              │  │          │  │                │
        └──────┬───────┘  └──────┬───────┘  └────┬─────┘  └───────┬────────┘
               │ /tmp/research-A.md │ ...B        │ ...C          │ /tmp/factcheck.md
               └────────────────────┴─────────────┴───────────────┘
                                    │  (lead reads files, synthesizes)
                                    ▼
                            ┌──────────────────┐
                            │worker-report-    │  writes →  05-knowledge/resources/<topic>.md
                            │writer (Sonnet)   │            (frontmatter + citations + [[wiki-links]])
                            └────────┬─────────┘
                                     ▼
                            ┌──────────────────┐    1. build_wiki_index.py  → 05-knowledge/INDEX.md
                            │worker-git-       │    2. git_autocommit.sh    → stage allowlist, commit
                            │publisher (Sonnet)│    3. git push             → GitHub
                            └────────┬─────────┘
                                     ▼
                              ●  GitHub repo
                              (versioned markdown + wiki graph)
```

### Why subagents (and not one giant prompt)

Each subagent runs in its **own context window**, so heavy research output and intermediate reasoning never clog the lead's context — the lead stays fast and focused on the decision. Workers also have **scoped tool permissions** (the researcher can't push to git; the publisher can't edit notes), and the cheaper model handles mechanical work while Opus handles judgment. This mirrors COG's own model-routing table in `CLAUDE.md`.

### Components in this repo

| Path | Role |
|------|------|
| `.claude/commands/research-report.md` | Orchestrator for the research pipeline (the Opus lead's playbook). |
| `.claude/commands/build-resume.md` | Orchestrator for the resume demo. |
| `.claude/agents/worker-fact-checker.md` | Re-verifies every claim against its source; flags stale/contradicted. |
| `.claude/agents/worker-report-writer.md` | Assembles verified findings into a cited, wiki-linked vault note. |
| `.claude/agents/worker-git-publisher.md` | Rebuilds the index, commits the content dirs, pushes. |
| `.claude/agents/resume-experience-miner.md` | Mines roles/projects/metrics from the vault + uploaded CV. |
| `.claude/agents/resume-achievement-writer.md` | Drafts metric-led bullets (honest — flags missing numbers). |
| `.claude/agents/resume-ats-optimizer.md` | Scores bullets vs. a job description; safe additions + real gaps. |
| `.claude/skills/wiki-link-optimizer/SKILL.md` | **Self-improving** agent that strengthens the wiki-link graph and learns from every accept/reject. |
| `.claude/memory/wiki-link-memory.json` | The optimizer's persistent memory: scoring weights, threshold, accepted/rejected history. |
| `.claude/settings.json` | Optional `Stop` hook as an auto-commit safety net. |
| `scripts/git_autocommit.sh` | Allowlisted, no-empty-commit, never-force git commit + push. |
| `scripts/build_wiki_index.py` | Regenerates `05-knowledge/INDEX.md` as a `[[wiki-link]]` map of content. |
| `scripts/wiki_graph_optimizer.py` | Deterministic graph engine (stdlib only): analyze → apply → learn. Drives the optimizer skill. |
| `docs/CONTEXT-AND-MEMORY.md` | How context management and memory work in this system — read this to understand the design. |
| `mcp/research_vault/` | **Optional** MCP server exposing vault write / wiki-link / commit as tools. |

> Note: `worker-researcher` already exists in COG (`.claude/agents/worker-researcher.md`). The pipeline reuses it as-is and adds the fact-checker, report-writer, and publisher around it.

---

## Workflow

### Research pipeline — `/research-report "<question>"`

1. **Ground** — the lead reads `05-knowledge/`, `04-projects/`, and recent braindumps, then states its planned decomposition and pauses for you to course-correct.
2. **Decompose** — the lead splits the question into 4–7 independent threads (market forces, players, tech trajectory, contrarian view, emerging/pre-mainstream tech, …).
3. **Research in parallel** — one `worker-researcher` per thread, spawned in a single message with `run_in_background: true`. Each writes findings to `/tmp/research-<thread>.md` and preserves sources under `raw/research/<date>-<slug>/` (COG's Raw-First protocol).
4. **Fact-check** — `worker-fact-checker` re-opens every cited source, looks for a second corroborating source, checks dates, and assigns a verdict per claim → `/tmp/factcheck-<topic>.md`.
5. **Synthesize** — the lead (Opus) reads the findings + verdicts and decides the narrative and headline judgment. *Not delegated — this is the thinking.*
6. **Compose** — `worker-report-writer` turns the outline + verified findings into `05-knowledge/resources/<topic>.md`: YAML frontmatter, TL;DR, inline citations, a Sources section, and `[[wiki-links]]` to related notes. Contradicted/unsupported claims are dropped; stale ones are labelled.
7. **Publish** — `worker-git-publisher` runs `build_wiki_index.py` (so the new note is reachable in the graph), then `git_autocommit.sh research "<title>"`, which commits the content dirs and pushes. You get the commit hash back.

### Resume demo — `/build-resume "<role or JD>" [path/to/cv]`

Same shape, different workers: **mine** experience from the vault → **draft** metric-led bullets → (lead asks you to fill genuine metric gaps) → **ATS-optimize** against the job description → lead does the final edit and writes `03-professional/resume/<role>-<date>.md` → **publish** to GitHub. The point: the orchestration pattern is domain-agnostic — swap the workers, keep the lead/worker/publish spine.

---

## Auto-commit to GitHub — how it works

Two mechanisms; use either or both:

1. **Explicit (recommended).** Each orchestrator's final phase spawns `worker-git-publisher`, so the commit is a deliberate, described step you can see in the run. Controlled and auditable.
2. **Hook fallback (optional).** `.claude/settings.json` registers a `Stop` hook that runs `git_autocommit.sh` when the agent finishes a turn. The script **no-ops if no vault content changed**, so it never creates empty commits. Delete the `hooks` block if you prefer fully explicit commits.

Safety properties of `git_autocommit.sh`:
- Stages an **allowlist** only — `00-inbox 01-daily 03-professional 04-projects 05-knowledge raw` — never `git add -A`, so `.claude/`, secrets, and `/tmp` are never committed.
- Skips cleanly when there's nothing to commit (no empty commits).
- Writes a structured message (`research: <title> (date) … N files`).
- **Never** force-pushes, amends, or runs destructive git commands.
- If no upstream/credentials are set, it commits locally and tells you the exact `git push -u` command to run.

Wiki-links: `build_wiki_index.py` reads each note's frontmatter `title` and emits `05-knowledge/INDEX.md` full of `[[note|Title]]` links grouped by directory — a human-readable contents page on GitHub and a map-of-content node in Obsidian.

---

## Do I need an MCP?

**Short answer: no, not for this pipeline to work.** Here's the decision:

| You want to… | Use | MCP needed? |
|--------------|-----|-------------|
| Search the web, fetch URLs | built-in `WebSearch` / `WebFetch` | ❌ |
| Read/write vault markdown | built-in `Read` / `Write` / `Glob` / `Grep` | ❌ |
| `git commit` + `git push` | built-in `Bash` + `git_autocommit.sh` | ❌ |
| Open PRs, manage issues, releases, labels on GitHub | **GitHub MCP server** (official, hosted) | ✅ |
| Reusable, *audited* vault tools shared across Claude Code **and** Cursor/Gemini/Codex | a **custom MCP** (`mcp/research_vault`) | ✅ (optional) |
| One enforced choke-point for conventions (frontmatter shape, commit allowlist) | a **custom MCP** | ✅ (optional) |
| Pull from a service with no CLI (Notion, Confluence, Linear, a private API) | that service's **MCP server** | ✅ |

So: the **research** itself never needs a custom MCP. You'd reach for MCP for **richer GitHub operations** (the `git` CLI handles commit/push; the GitHub MCP handles PRs/issues/releases) or to **package vault operations as governed, cross-client tools**. This repo includes the second case as a worked example.

### Building an MCP (worked example: `mcp/research_vault`)

The pattern, using the Python FastMCP SDK:

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("research-vault")

@mcp.tool()
def save_research_note(title: str, body_markdown: str, confidence: str = "medium") -> str:
    """Write a research report into the vault with COG-standard frontmatter."""
    ...   # the docstring becomes the tool description the model reads;
          # the type hints become the input schema — so type every arg.

if __name__ == "__main__":
    mcp.run()   # stdio transport for local clients
```

Three things make a good MCP tool: a **clear docstring** (that's what the model sees), **typed arguments** (that's the schema), and **path/permission validation inside the tool** (`research_vault` refuses any path that escapes the vault and uses the same commit allowlist as the script). Register it with:

```bash
claude mcp add research-vault \
  --env VAULT_ROOT=/path/to/COG-second-brain \
  -- uv run --directory /path/to/mcp/research_vault research_vault
```

Full details, the three tools it exposes, and how to extend it are in [`mcp/research_vault/README.md`](../mcp/research_vault/README.md).

---

## Self-improving wiki-link agent

The graph that powers retrieval is only as good as its links, so a dedicated agent keeps it healthy **and gets better at the job over time**. It's defined in `.claude/skills/wiki-link-optimizer/SKILL.md`, backed by the stdlib engine `scripts/wiki_graph_optimizer.py`.

```bash
python3 scripts/wiki_graph_optimizer.py analyze   # find broken links, orphans, missing links → /tmp/wiki-proposals.{md,json}
# agent + user mark each candidate accept/reject in the JSON
python3 scripts/wiki_graph_optimizer.py apply --proposals /tmp/wiki-proposals.json   # insert links + LEARN
python3 scripts/wiki_graph_optimizer.py status    # inspect the agent's current weights/threshold/stats
```

**What it detects:** broken `[[links]]` (pointing at nonexistent notes), orphan notes (nothing in or out), and high-value *missing* links between related notes — scored by TF-IDF similarity, tag overlap, and verbatim title mentions.

**Why it's self-improving:** every decision is written to `.claude/memory/wiki-link-memory.json`. On each `apply` the agent (1) never re-proposes a rejected pair, (2) nudges its scoring **weights** toward the signals behind accepted links and away from rejected ones, and (3) drifts its **threshold** toward your accept/reject boundary — all clamped and logged so the learning is gradual and auditable. Delete the ledger and it's a beginner again; commit it and the skill compounds. Run it as the last phase of `/research-report` (or weekly) and then let `worker-git-publisher` commit the improved graph **and** the updated ledger.

## Context management & memory

The whole architecture is a context/memory design. The short version (full writeup in [`docs/CONTEXT-AND-MEMORY.md`](CONTEXT-AND-MEMORY.md)):

- **Context** is the model's finite working memory; attention degrades as it fills. The system keeps it small via **subagent isolation** (each worker gets its own window), the **"return a path, not a wall of text"** rule (heavy output goes to `/tmp` files), **retrieval over recall** (read only the 3–5 relevant vault notes, not the whole vault), **progressive disclosure** (skills load on demand), and **proactive `/compact` with a focus hint** for long sessions.
- **Memory** is everything that outlives the window, on disk: **semantic** (`05-knowledge/` notes + the wiki-link graph), **episodic** (git history, `raw/`, daily briefs), **procedural** (`CLAUDE.md`, skills, agents), and **learned** (the optimizer's ledger). The vault *is* the long-term memory — plain markdown, git-versioned, with `[[wiki-links]]` as associative edges and `INDEX.md` as the memory index.
- Layer on **Claude Code's own memory**: `CLAUDE.md` (persistent, survives compaction), **auto memory** (`MEMORY.md` + on-demand topic files; inspect with `/memory`, see usage with `/context`), and **subagent `memory:` frontmatter** for per-worker persistence. To *guarantee* a rule (e.g. never commit secrets) use a **PreToolUse hook**, not a memory note — memory is treated as context, not enforcement.

Design principle in one line: **keep the window small and the disk rich.**

## Setup

```bash
# 1. Get the vault
git clone https://github.com/<you>/COG-second-brain.git
cd COG-second-brain

# 2. Drop this pipeline in (merges into .claude/, scripts/, mcp/)
#    Copy the contents of cog-research-pipeline/ over the vault root.
cp -r /path/to/cog-research-pipeline/. .

# 3. Point the vault at YOUR GitHub repo so auto-commit can push
git remote set-url origin https://github.com/<you>/COG-second-brain.git
git push -u origin main      # one-time, sets upstream

# 4. Make scripts executable
chmod +x scripts/git_autocommit.sh scripts/build_wiki_index.py scripts/wiki_graph_optimizer.py

# 5. (Optional) install the MCP server
cd mcp/research_vault && uv sync && cd ../..

# 6. Restart Claude Code so it loads the new agents + commands, then:
#    /research-report "If foundation models commoditize, what happens to LLM wrappers?"
#    /build-resume "Senior Platform Engineer" ./my-current-cv.pdf
```

**Requirements:** Claude Code; `git` with push access to your repo; Python 3.10+ and `uv` (only if you use the MCP server); Obsidian (optional, for the wiki graph).

**Auth for push:** the pipeline uses your existing local git credentials (SSH key or a credential helper / PAT). It never handles or stores tokens itself.

---

## Design notes

- **Workers write files, not walls of text.** Per COG's rule, anything ≥ ~2K tokens goes to `/tmp/...md` and the worker returns a path. This is dramatically faster than streaming large outputs and keeps the lead's context lean.
- **Honesty guards are built into the workers.** The fact-checker won't fabricate corroboration; the resume writers won't invent metrics or recommend claiming skills the user lacks. Beating an ATS by lying just moves the failure to the interview.
- **Least privilege.** The researcher has no git access; the publisher can't edit notes; the publisher's script can't stage `.claude/` or secrets. Scoped tools per agent.
- **The pattern generalizes.** `/research-report` and `/build-resume` share one spine: *lead decomposes → workers gather in parallel → lead synthesizes → worker formats → worker publishes.* Add your own command + workers to apply it to anything (competitive teardown, literature review, incident postmortem).

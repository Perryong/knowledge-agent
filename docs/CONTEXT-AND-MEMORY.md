# Context Management & Memory in this Agent System

This doc explains the two things people most often conflate when building an agent system, and exactly how this pipeline handles each:

- **Context** = the model's *working memory* — the tokens in the window right now. Finite, ephemeral, wiped each session.
- **Memory** = what *persists* across turns, sessions, and compaction events — lives outside the window, on disk.

A good agent system is mostly an exercise in deciding **what goes in context, what goes to disk, and how the two move back and forth.**

---

## Part 1 — Context management

### The core problem: context is finite and degrades as it fills
Even with large windows, model attention degrades well before the hard limit — precision starts slipping once the window is most of the way full, and tool outputs (file reads, search results, command output) are the biggest consumers. A single large file read can eat tens of thousands of tokens. So the job isn't "fit everything in," it's "keep the *relevant* stuff dense and push everything else out to disk."

### Five techniques this pipeline uses

**1. Subagent isolation (the biggest lever).**
Each worker (`worker-researcher`, `worker-fact-checker`, etc.) runs in its **own fresh context window**. When the lead spawns three researchers, each one's web searches, page fetches, and intermediate reasoning happen in *that worker's* context — not the lead's. The only thing that crosses back is the worker's short return string. The lead's window therefore stays small no matter how much raw material the workers churn through. This is why the architecture is lead-and-workers rather than one mega-prompt.

**2. Files as external context (the "return a path, not a wall of text" rule).**
COG's hard rule: any worker output ≥ ~2K tokens is written to `/tmp/<task>.md` and the worker returns only `OK: /tmp/... (summary)`. The filesystem is unlimited, instant to write, and the next agent reads only the slice it needs. Generating thousands of tokens *as a chat message* is slow and pollutes context; writing to a file is free. The whole pipeline is wired this way — `/tmp/research-*.md`, `/tmp/factcheck-*.md`, `/tmp/wiki-proposals.md`.

**3. Retrieval over recall (don't preload the vault).**
The lead does **not** stuff the entire vault into context. Following COG's Brain-First protocol it reads *only* the notes relevant to the task (`Glob`/`Grep` to find them, `Read` to pull them). This is lightweight RAG: the index (`05-knowledge/INDEX.md`) and the wiki-link graph act as the retrieval structure, so the lead pulls the right 3–5 notes instead of 300.

**4. Progressive disclosure via skills.**
A SKILL.md's body is only injected as instructions when the skill is actually triggered. Seventeen COG skills plus this pipeline's skills don't all sit in context at once — the relevant one loads on demand. Same idea as CLAUDE.md sub-directory loading: keep the always-on layer tiny, load specifics when the task calls for them.

**5. Compaction with a focus hint (for long sessions).**
When a lead session runs long and the window fills, compaction summarizes earlier turns into a compact state block so work can continue. Two things matter:
- Trigger it **proactively** (well before the limit), not at the last moment.
- Give it a **focus hint** so the summary keeps what matters: e.g. *"summarize, keeping the decomposition, the accepted findings, and the target output path."*
- Anything that must survive compaction has to live **outside** the conversation (on disk) — because a summary is lossy. Our pipeline already does this: the findings, the report, and the ledger are all on disk, so a compaction event can't lose them.

> Rule of thumb for *what goes where*: **decisions and the current plan** → lead context; **raw gathered material** → `/tmp` files; **anything needed next session** → the vault or the ledger.

---

## Part 2 — Memory

Memory is everything that outlives the window. This system has four kinds, mapped to where they live:

| Memory type | "What…" | Where it lives here |
|-------------|---------|---------------------|
| **Semantic** | …is true / known | `05-knowledge/` notes, people CRM, and the **wiki-link graph** (associative memory — edges between concepts) |
| **Episodic** | …happened | git history, `01-daily/` briefs, preserved `raw/` sources (each with a date) |
| **Procedural** | …how to do things | `CLAUDE.md`, the skills, the agent definitions, these scripts |
| **Learned / self-memory** | …this agent figured out by doing | `.claude/memory/wiki-link-memory.json` — the optimizer's weights, threshold, and accept/reject history |

### The vault *is* the long-term memory
Plain markdown, git-versioned, no database. That's a deliberate memory design:
- **Durable & inspectable** — you can read and diff every memory.
- **Associative** — `[[wiki-links]]` are the edges of a knowledge graph; following them is associative recall. This is exactly why the self-improving optimizer matters: it keeps that associative memory richly and correctly connected, so retrieval (Part 1, technique 3) actually finds the right notes.
- **Indexed** — `INDEX.md` is the map-of-content / memory index, regenerated after each session.
- **Structured** — frontmatter (`tags`, `confidence`, `related`, `created`) makes notes filterable for retrieval.

### Memory lifecycle (capture → consolidate → retrieve → forget)
1. **Capture** — raw sources preserved under `raw/` *before* AI touches them (Raw-First protocol). Nothing is lost.
2. **Consolidate** — `worker-report-writer` turns raw findings into a durable, cited note; `knowledge-consolidation` builds frameworks from many notes.
3. **Retrieve** — Brain-First read before answering; the wiki graph + index do the routing.
4. **Forget / archive** — stale knowledge moves to `05-knowledge/archives/` (PARA), keeping the active set small and relevant. Forgetting is a feature: it keeps retrieval sharp.

### Claude Code's built-in memory layers (use these too)
This pipeline layers on top of Claude Code's own memory, which you should lean on:
- **`CLAUDE.md`** — explicit, persistent instructions, auto-loaded at the start of every session and **re-read after compaction**. COG's routing rules and protocols live here. Keep it dense (every line costs tokens); push package-/topic-specifics to sub-directory `CLAUDE.md` files that load on demand.
- **Auto memory (`MEMORY.md` + topic files)** — notes Claude writes for itself from your corrections and preferences. The index is loaded at startup (first chunk only); topic files load on demand when relevant. Inspect what's loaded with `/memory`; see the live context breakdown with `/context`.
- **Subagent memory** — a subagent can be given its own persistent memory via its `memory:` frontmatter, so a worker accumulates domain knowledge across runs (e.g. a researcher remembering trusted sources).
- **The Memory Tool (API agents)** — if you build this as a standalone API agent rather than inside Claude Code, the Messages API offers a memory tool + a compaction strategy you configure directly, instead of the CLI's CLAUDE.md/auto-memory.

> Important: CLAUDE.md and auto memory are treated as **context, not enforced rules** — the model can still decide against them. To *guarantee* an action (e.g. "never commit secrets"), use a **PreToolUse hook**, not a memory instruction. That's why our commit safety lives in a script/allowlist, not just a prose rule.

### The self-improving memory in detail
The wiki-link optimizer is the clearest example of *learned* memory in the system. Its ledger separates the agent's "skill" from any single session:

```
.claude/memory/wiki-link-memory.json
  weights        → how much to trust each signal (tfidf / tag_overlap / title_mention)
  threshold      → how confident a suggestion must be to surface
  rejected_pairs → never propose these again
  accepted_pairs → what good looks like
  aliases        → learned vocabulary
  log            → an audit trail of every weight/threshold change
```

Each `apply` run nudges the weights toward the signals behind *accepted* links and away from *rejected* ones, and drifts the threshold toward the accept/reject boundary (clamped, so it can't ratchet itself into uselessness). Delete the file and the agent is a beginner again; commit it and the learning compounds. This is "self-improvement" in the practical sense available without retraining a model: **the agent's parameters are data on disk, updated by feedback.**

---

## Putting it together: the lifecycle of one research session

```
session start
  │  CLAUDE.md + auto memory load into the lead's context        ← memory → context
  ▼
lead reads 3–5 relevant vault notes (not the whole vault)        ← retrieval, technique 3
  ▼
lead spawns workers (each isolated context)                       ← isolation, technique 1
  │  workers write findings to /tmp/*.md, return short paths      ← files-as-context, technique 2
  ▼
lead synthesizes from the small returned strings + reads files
  │  (if window fills: /compact with a focus hint)                ← compaction, technique 5
  ▼
report written to 05-knowledge/  +  INDEX.md rebuilt              ← context → semantic memory
  ▼
wiki-link-optimizer connects the new note into the graph         ← maintains associative memory
  │  ledger updated with this run's accept/reject                 ← learned memory updates
  ▼
git commit + push                                                ← episodic memory (versioned)
session end — context wiped; everything important is on disk
```

The design principle in one line: **keep the window small and the disk rich** — context holds the *decision being made right now*; memory holds *everything worth keeping*, and the pipeline is the machinery that moves knowledge between the two.

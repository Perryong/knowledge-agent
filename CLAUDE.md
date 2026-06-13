# COG Second Brain — Framework Instructions

## Model Routing — ALWAYS APPLY

When spawning subagents, use the correct model for the task:

| Task type | Model | Agent definition |
|-----------|-------|-----------------|
| Data collection (GitHub, Slack, Jira, Linear, file reads) | **Sonnet** | `worker-data-collector` |
| Web research (search, fetch URLs, extract facts) | **Sonnet** | `worker-researcher` |
| Publishing (Slack, Confluence, Notion, webhooks) | **Sonnet** | `worker-publisher` |
| File operations (vault reads/writes, metadata, profiles) | **Sonnet** | `worker-file-ops` |
| Pre-approved mutations (Jira transitions, Linear updates, API calls) | **Sonnet** | `worker-executor` |
| People profile updates from brief/meeting data | **Sonnet** | `brief-people-updater` |
| Reasoning, synthesis, cross-referencing, writing | **Opus** | Lead session (no delegation) |
| Editorial judgment, tone, strategic decisions | **Opus** | Lead session (no delegation) |

**Rule:** If a task doesn't require reasoning or judgment, delegate it to a Sonnet worker. The lead session (Opus) handles thinking, synthesis, and writing only.

Agent definitions live in `.claude/agents/`.

### Worker Output Rule — ALWAYS APPLY

Workers must **write results to a file** and return only a short status + file path. Never have a worker return large text as output.

| Output size | What to do |
|------------|------------|
| < 2K tokens | Return inline (short status, confirmation, error) |
| >= 2K tokens | Write to `/tmp/{task-slug}-{context}.md`, return path |

**Why:** Generating thousands of tokens as agent output is sequential and extremely slow. Writing to file is instant. The orchestrator or next agent reads the file via the Read tool.

**Pattern:**
```
# Worker prompt must include:
"Write your results to /tmp/{descriptive-name}.md and return ONLY a short status message with the file path."

# Worker returns:
"OK: /tmp/slack-data.md (gathered 47 messages, 12 threads)"

# Orchestrator reads:
Read("/tmp/slack-data.md")
```

**Applies to:** All `worker-*` agents, all `brief-*` agents, any subagent that collects, extracts, or processes data.

---

## Brain-First Knowledge Protocol (MUST APPLY)

Before answering any question about people, projects, strategy, decisions, or historical context:
1. Read relevant notes from `05-knowledge/` first (especially `05-knowledge/people/` for people questions).
2. If project-specific, also read related files in `04-projects/<project>/`.
3. Only then synthesize an answer.

If the user corrects a factual statement, write/update the correction in the relevant knowledge note immediately.

## Hybrid Raw-First Protocol (MUST APPLY)

COG remains the main operating framework. Apply the hybrid rules in `docs/HYBRID-SECOND-BRAIN.md` whenever handling external sources or durable knowledge.

1. Preserve every external source in `raw/<category>/YYYY-MM-DD-<slug>/` before AI processing.
2. Create or update `metadata.md` for each raw source and link processed outputs in `processed_to`.
3. Add `raw_sources` frontmatter to processed notes whenever source material exists.
4. Classify durable knowledge inside `05-knowledge/projects/`, `05-knowledge/areas/`, `05-knowledge/resources/`, or `05-knowledge/archives/`.
5. Update `05-knowledge/schema/` through `/schema-compile` after meaningful batches of notes accumulate.

### Citation Rule
For factual statements written into durable notes (`05-knowledge/**`, people profiles, consolidated docs), include source attribution inline:

`[Source: [[path/to/note]] | YYYY-MM-DD | confidence: high|medium|low]`

Use one citation per distinct factual claim block where practical.

---

## Integration Preferences

Before using any external integration in a skill, check `00-inbox/MY-INTEGRATIONS.md`:

- **Active integrations**: Use normally.
- **Disabled integrations**: Skip silently. Do not attempt to call their tools, do not suggest setting them up, do not mention them in output.
- **Unknown integrations** (not listed in either section): Ask the user if they want to set it up. If they say no, add it to the Disabled section.

## Role Packs

COG uses role packs (`.claude/roles/*.md`) to personalize skill recommendations and integration suggestions per user role.

### How role matching works
1. During onboarding, the user's role text is matched against `role_id` and `aliases` in each role pack's YAML frontmatter.
2. The matched role pack is stored as `role_pack` in `00-inbox/MY-PROFILE.md` frontmatter.
3. When suggesting skills or workflows, check the user's `role_pack` and order recommendations by role relevance.

### Role-aware behavior
- **Skill suggestions**: When a user asks "what can COG do?" or similar, prioritize skills listed in their role pack. Show role-specific explanations from the pack.
- **Integration prompts**: When a skill needs an integration the user hasn't set up, check their role pack to provide role-specific context for why it matters.
- **No role pack match**: If the user's role doesn't match any pack, recommend core skills (`roles: [all]`) and let them discover team skills organically.

### Available role packs
Role packs live in `.claude/roles/`. New roles can be added by dropping a file following the `_template.md` format.

## Vault Structure

### User configuration files (`00-inbox/`)
- `MY-PROFILE.md` — User info, role pack, agent mode, active projects
- `MY-INTERESTS.md` — Topics for daily briefs
- `MY-INTEGRATIONS.md` — Active/disabled external service integrations

### Professional tracking (`03-professional/`)
- `COMPETITIVE-WATCHLIST.md` — Companies/people being tracked

### Framework files (updated via `cog-update.sh` or `/update-cog`)
- `.claude/skills/` — Claude Code skills (17 skills)
- `.claude/agents/` — Worker agent definitions (6 agents)
- `.claude/roles/` — Role packs for personalized recommendations
- `.kiro/powers/` — Kiro powers
- `.gemini/commands/` — Gemini CLI commands
- `AGENTS.md` — Universal agent documentation

### Knowledge system (`05-knowledge/`)
- `people/` — People CRM profiles (progressive, evidence-based)
- `consolidated/` — Frameworks and synthesis documents
- `patterns/` — Identified patterns
- `timeline/` — Thinking evolution
- `booklets/` — URL bookmarks by category
- `projects/`, `areas/`, `resources/`, `archives/` — PARA durable knowledge
- `schema/` — Concepts, relationships, and compile logs

### Content directories (never touched by updates)
- `raw/` — Preserved source material, captured before processing
- `00-inbox/` — Profiles, interests, integrations
- `01-daily/` — Briefs and check-ins
- `02-personal/` — Personal braindumps (private)
- `03-professional/` — Professional braindumps and strategy
- `04-projects/` — Per-project tracking
- `05-knowledge/` — Consolidated insights and patterns

---

## Financial Analysis Integration

The trading desk analysis pipeline is fully integrated. Scripts live in `scripts/` at the project root and are invoked automatically by the financial skills below.

### Quick Skills (single analyst, information only)

| Command | Agent | What it does |
|---------|-------|-------------|
| `/news NVDA` | Nadia | News catalysts, insider signals, is it priced in? |
| `/social NVDA` | Sage | Reddit/fintwit sentiment, crowd psychology |
| `/chart NVDA` | Tara | Technicals, levels, price action |
| `/macro NVDA` | Marco | Macro regime, sector context, tailwinds/headwinds |
| `/valuation NVDA` | Frank | PE, margins, balance sheet, cash flow quality |
| `/options-advisor NVDA` | — | Options strategy analysis with Black-Scholes |
| `/position-size NVDA` | — | Risk-based position sizing calculator |

### Full Pipeline

| Command | What it does |
|---------|-------------|
| `/analyze NVDA` | 16-agent desk: 9 analysts → bull/bear debate → trade proposal → 3 risk reviewers → Hugo's final go/no-go |
| `/alpha` | Mr. A scans all signal sources and auto-chains the top pick into `/analyze` |

### Trading System (The Money)

| Command | What it does |
|---------|-------------|
| `/tm-regime` | Three-layer market regime: macro, sector, stock — produces flag (green/yellow/red/black) |
| `/tm-agent-quant` | The Quant: strategy session, signal evaluation, situation report, wiki maintenance |
| `/tm-review NVDA` | Post-trade causal attribution and wiki update |
| `/tm-synthesis` | Weekly digest, strategy EV, source recalibration, regime patterns |
| `/tm-dashboard` | Live portfolio telemetry (F1-style) |
| `/tm-morning` | Full morning pipeline: regime → scan → evaluate → deploy |

### Knowledge Storage for Analysis Results

Apply the Hybrid Raw-First Protocol to all analysis outputs:

1. **Raw data** → `raw/financial/YYYY-MM-DD-{TICKER}-analysis/` (JSON from fetch_data.py, screenshots)
2. **Durable thesis notes** → `05-knowledge/areas/investing/{TICKER}.md`
3. **Trade journal entries** → `03-professional/trades/YYYY-MM-DD-{TICKER}.md`
4. **Regime snapshots** → `_bmad/memory/tm/raw/regime-snapshots/` (written by `/tm-regime snapshot`)

### Scripts Reference

Scripts are in `scripts/` at the project root (migrated from the trading desk):

- `fetch_data.py` — Core market data prefetch (yfinance → JSON). Used by almost every financial skill.
- `premarket_scanner.py` — Batch scanner across 6 CANSLIM strategies over `scripts/universe.json`.
- `analytics/hmm_regime.py` — HMM 3-state (Bull/Bear/Crisis) regime classifier.
- `analytics/hurst.py` — Hurst exponent (trend vs mean-reversion detection).
- `analytics/rmt_correlation.py` — Random Matrix Theory correlation cleaner.
- `analytics/shannon_entropy.py` — Market entropy / uncertainty measure.
- `generate_dashboard.py` — Single-file HTML portfolio dashboard (used by `/tm-dashboard`).
- `fred_mcp_wrapper.py` — FRED economic data wrapper for macro context.

### Python Setup

Dependencies are declared in `pyproject.toml`. Install with:

```bash
uv sync
# or
pip install -e .
```

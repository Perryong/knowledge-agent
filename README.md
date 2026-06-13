# Perry's Hybrid COG Second Brain

A local, markdown-based second brain combining two systems in one vault:

- **COG** — personal knowledge operating system: captures information, preserves raw sources, builds a growing wiki, and surfaces patterns over time.
- **Trading Desk** — 16-agent institutional-grade analysis pipeline: macro, technicals, ICT structure, fundamentals, flow, liquidity, sentiment, news → bull/bear debate → trade proposal → risk review → execution.

Everything lives as local markdown. Obsidian reads it. Git tracks it. Claude Code drives it.

> **Research Pipeline add-on:** a multi-agent research → report → publish pipeline (`/research-report`, `/build-resume`) plus a self-improving wiki-link agent now ships in this vault. See [`docs/RESEARCH-PIPELINE.md`](docs/RESEARCH-PIPELINE.md) for the full architecture and [`docs/CONTEXT-AND-MEMORY.md`](docs/CONTEXT-AND-MEMORY.md) for the context/memory design.

---

## How to Open

Always launch Claude Code from inside this vault:

```bash
cd C:\Users\perry\Documents\obsidian\second-brain\COG-second-brain
claude
```

Running from the parent `second-brain/` directory also works, but `{project-root}` resolves differently for the financial scripts. Use the vault root.

---

## Core Rules

1. **Raw first** — save every external source in `raw/` before summarizing or analyzing it.
2. **Link back** — every processed note includes `raw_sources:` frontmatter pointing to `raw/` metadata.
3. **Durable knowledge** — long-lived insights go in `05-knowledge/` using PARA (projects, areas, resources, archives).
4. **No credentials in notes** — API keys live in `.mcp.json` and `.env` only (both gitignored).
5. **Schema after batches** — run `/schema-compile` after every meaningful batch of new notes to keep the concept graph current.

---

## Folder Structure

```text
COG-second-brain/
├── raw/                        # Every external source lands here first
│   ├── articles/
│   ├── pdfs/
│   ├── images/
│   ├── documents/
│   ├── research/
│   ├── trading/                # Charts, price screenshots, earnings PDFs
│   ├── jobs/
│   └── meetings/
├── 00-inbox/                   # MY-PROFILE.md, MY-INTERESTS.md, MY-INTEGRATIONS.md
├── 01-daily/                   # Daily briefs, morning notes
├── 02-personal/                # Private braindumps
├── 03-professional/            # Career, job search, strategy
│   └── trades/                 # Per-trade journal entries
├── 04-projects/                # Active project tracking
├── 05-knowledge/               # Durable, reusable knowledge
│   ├── areas/
│   │   └── investing/          # Per-ticker thesis notes (NVDA.md, ASTS.md, ...)
│   ├── people/                 # CRM-style profiles
│   ├── consolidated/           # Framework documents
│   ├── schema/                 # Concept graph, relationships, compile logs
│   ├── projects/
│   ├── resources/
│   └── archives/
├── 06-templates/               # Reusable note templates
├── scripts/                    # fetch_data.py, premarket_scanner.py, analytics/
├── .cache/                     # Ticker JSON cache (gitignored, written by /analyze)
├── .claude/
│   ├── skills/                 # COG skills (18 skills)
│   ├── agents/                 # Worker agent definitions
│   ├── roles/                  # Role packs (trader.md, engineer.md, ...)
│   └── vendor/                 # Local MCP servers (opennews-mcp, maverick-mcp)
├── _bmad/memory/tm/            # The Money wiki — trade log, post-mortems, tickers
├── .mcp.json                   # MCP server configs + API keys (gitignored)
├── AGENTS.md                   # Universal agent instructions
└── CLAUDE.md                   # Claude-specific operating instructions
```

---

## Two Systems, One Vault

### COG side — the librarian

COG organizes knowledge. You feed it raw material (URLs, thoughts, transcripts, research); it preserves the source, compiles it into structured notes, and builds cross-referenced wiki pages. Over time it surfaces patterns you wouldn't notice reading one note at a time.

### Trading Desk side — the investment committee

When you run `/analyze NVDA`, 16 specialist agents run in sequence:

```
Stage 1  fetch_data.py pulls live price, technicals, fundamentals, options chain
Stage 2  9 analysts in parallel — Marco (macro), Tara (technicals), Sage (sentiment),
         Nadia (news), Frank (fundamentals), Flow (order flow + 13F), Kai (ICT/Smart Money),
         Gail (5-gate entry screen), Leo (liquidity map)
Stage 3  Blaine (bull case) → Vera (bear case) → Jaya (verdict + conviction 1–10)
Stage 4a Rex proposes a specific trade: options structure + equity alternative
Stage 4b Axel, Nina, Cass review in parallel (aggressive / neutral / conservative risk)
Stage 4c Hugo fetches your live Alpaca positions, renders final go/no-go with two
         executable trades and asks "Execute? (yes/no)"
Stage 5  Yes → Alpaca order + Obsidian journal entry. No → standing down, open to follow-ups.
```

They connect: analysis output gets stored in COG's knowledge system, building an evidence base about every ticker you've studied.

---

## Skills Reference

### Setup (run once)

| Command | Purpose |
|---------|---------|
| `/onboarding` | Set up `MY-PROFILE.md`, `MY-INTERESTS.md`, role context. Run this first if starting fresh. |

---

### COG — Capture

| Command | When to use | Example |
|---------|-------------|---------|
| `/braindump` | Dump thoughts, trade ideas, observations. COG classifies and routes to the right folder. | `/braindump NVDA held support at $195 but volume was thin — could be distribution` |
| `/url-dump URL` | Save and process a URL. Fetches content, generates insights, files into knowledge booklets. | `/url-dump https://... save as NVDA semiconductor research` |
| `/scout URL` | Quick triage before a full save — "is this worth keeping?" | `/scout Is this NVDA options-flow article useful?` |
| `/meeting-transcript` | Paste raw meeting notes; extracts decisions, action items, dynamics. | Paste transcript, COG structures it |

---

### COG — Intelligence

| Command | When to use | Example |
|---------|-------------|---------|
| `/daily-brief` | Morning news personalized to `MY-INTERESTS.md`. Requires web search. | `/daily-brief` |
| `/auto-research [question]` | Deep strategic research — decomposes into parallel threads, synthesizes sourced analysis. Saves sources to `raw/research/`. | `/auto-research What does the current AI capex cycle mean for NVDA's next 2 quarters?` |
| `/comprehensive-analysis` | Seven-day deep dive across all data sources. Weekly reviews, board prep, major decisions. | `/comprehensive-analysis 7-day readout for NVDA, SMH, QQQ, yields, volatility` |

---

### COG — Organize & Maintain

| Command | When to use |
|---------|-------------|
| `/weekly-checkin` | Sunday review — scans all braindumps, briefs, project notes from the past 7 days, finds cross-domain patterns. |
| `/knowledge-consolidation` | Turns scattered insights from braindumps into a single coherent framework in `05-knowledge/`. |
| `/update-cog` | Pull framework updates from the COG upstream repo without touching personal content. |
| `/generate-prd` | Draft a product requirements document for any project. |
| `/create-user-story` | Create implementation-ready stories. |
| `/export-open-issues` | Audit open issues from any project tracker. |
| `/update-knowledge-base` | Keep project docs current from releases, features, and changes. |
| `/team-brief` | Daily team intelligence brief (GitHub, Linear, Slack, meetings cross-referenced). |

---

### Trading Desk — Quick Checks

Single analyst, single angle. Fast — use during market hours or before a meeting.

| Command | Agent | Output |
|---------|-------|--------|
| `/macro NVDA` | Marco | Macro regime, sector rotation, tailwinds/headwinds for this ticker |
| `/valuation NVDA` | Frank | PE, margins, balance sheet, FCF quality, sector comparison |
| `/chart NVDA` | Tara | SMAs, RSI, MACD, key levels, price action narrative |
| `/news NVDA` | Nadia | Catalysts, insider signals, "is it priced in?" |
| `/social NVDA` | Sage | Reddit/fintwit sentiment, crowd psychology, positioning |
| `/options-advisor NVDA` | — | IV vs HV, Black-Scholes, options strategy menu |
| `/position-size NVDA` | — | Shares/contracts based on your configured risk rules |

---

### Trading Desk — Full Pipeline

| Command | What it does |
|---------|-------------|
| `/analyze NVDA` | 16-agent full desk: 9 analysts → bull/bear debate → trade proposal → 3 risk reviewers → Hugo final go/no-go. ~2–4 minutes. |
| `/alpha` | Mr. A scans 10+ signal sources, scores every name, picks the top equity, auto-chains into `/analyze`. |

---

### Trading Desk — Market Environment

| Command | When to use |
|---------|-------------|
| `/tm-regime` | Before putting capital at risk. Returns a **flag**: green (normal), yellow (caution), red (reduce exposure), black (stay flat). Also: sector rotation, distribution day count, breadth score, VIX, yield curve. |
| `/market-top` | IBD-style market top probability — distribution days, breadth deterioration, rotation signals. |
| `/screen` | CANSLIM batch scan across the `scripts/universe.json` watchlist. Outputs a ranked watchlist. |

---

### The Money — Automated Workflow

| Command | What runs |
|---------|-----------|
| `/tm-morning` | Full morning pipeline: regime check → pre-market scan → evaluate watchlist → deploy approved setups |
| `/tm-morning scan` | Reuse today's regime, re-run scanner only |
| `/tm-morning evaluate` | Re-run evaluations on today's watchlist, skip scan |
| `/tm-agent-quant` | Opens a session with The Quant — quantitative strategist. Use for strategy sessions, signal evaluation, situation reports ("what should I do right now?"), wiki maintenance, rule authoring. |
| `/tm-review NVDA` | Post-trade causal attribution after closing a position. Updates wiki pages (ticker, causal factors, regime, strategy), writes journal entry. |
| `/tm-review thesis-check` | For open positions: is the original thesis still intact? Catches broken theses before the stop. |
| `/tm-review contact-trace` | After a significant loss: maps causal factors across all open positions to find contagion risk. |
| `/tm-synthesis` | Weekly digest (default). Pass `strategy-ev`, `source-recal`, `regime-patterns`, `quarterly` for deeper reviews. |
| `/tm-dashboard` | Generates a self-contained HTML dashboard at `_bmad-output/dashboard.html` — portfolio telemetry, Greeks, correlation heatmap, regime strip, active watchlist. |

---

## Integrated Workflow — NVDA Example

Full loop from idea to knowledge:

**1. Morning regime check**
```
/tm-regime
```
Green flag — normal conditions, new entries allowed.

**2. Full desk analysis**
```
/analyze NVDA
```
16 agents run. Hugo outputs two executable trades. You decline — price extended, want a pullback.

**3. Store the analysis in COG**
```
raw/trading/2026-06-07-nvda-analysis/
  metadata.md          ← source info, links to processed notes
  market-data.json     ← copy from .cache/analyze-NVDA.json

05-knowledge/areas/investing/NVDA.md       ← durable thesis, updated today
03-professional/trades/2026-06-07-nvda-planned.md  ← GTC entry planned at $195
```

**4. Set the watchlist entry with The Quant**
```
/tm-agent-quant
```
"Add NVDA to watchlist. GTC long $195, stop $188, target $215. Thesis: pullback to 20-day MA, regime green."

**5. Research the macro backdrop**
```
/auto-research What does the current AI capex cycle mean for NVDA's next 2 quarters? Preserve sources.
```
COG saves articles to `raw/research/`, writes a sourced synthesis, links it to the NVDA thesis in `05-knowledge/`.

**6. After the trade resolves**
```
/tm-review NVDA
```
Causal post-mortem. Was the thesis right? Which factor drove the outcome? Wiki updated with new evidence.

**7. Sunday**
```
/tm-synthesis
/weekly-checkin
```
`/tm-synthesis`: which strategies are working, which signal sources have been accurate, EV by setup type.
`/weekly-checkin`: cross-domain patterns across everything — trading, career, projects.

---

## Daily Cadence

| Time | Command | Purpose |
|------|---------|---------|
| Pre-market | `/tm-morning` | Regime → scan → evaluate → deploy |
| Any time | `/analyze TICKER` | Before any conviction trade |
| During day | `/braindump` | Capture real-time observations |
| After close | `/tm-review TICKER` | Post-mortem on closed positions |
| Evening | `/daily-brief` | News digest for tomorrow |
| Sunday | `/tm-synthesis` then `/weekly-checkin` | Performance + knowledge review |
| Monthly | `/knowledge-consolidation` | Scatter → framework |

---

## Key Configuration Files

| File | What it controls |
|------|-----------------|
| `00-inbox/MY-PROFILE.md` | Your name, `role_pack: trader`, `agent_mode` |
| `00-inbox/MY-INTERESTS.md` | Topics for `/daily-brief` — edit this to personalize news |
| `00-inbox/MY-INTEGRATIONS.md` | Which MCP servers are active or disabled |
| `.mcp.json` | API keys: alpaca, opennews, edgartools, financekit, fred, yahoo-finance (gitignored) |
| `_bmad/memory/tm/wiki/log.md` | Every analysis and trade review ever run, in order |
| `_bmad/memory/tm/wiki/` | The Money's learning wiki — grows with every `/tm-review` |
| `scripts/fetch_data.py` | Core market data script. Test directly: `python scripts/fetch_data.py NVDA` |
| `scripts/universe.json` | ~110-stock universe used by `/screen` and `/tm-morning` |

---

## MCP Servers

Configured in `.mcp.json` (gitignored). Required for the trading desk pipeline.

| Server | Powers |
|--------|--------|
| `alpaca` | Portfolio positions, account info, order execution (paper mode) |
| `yahoo-finance` | Real-time price, fundamentals, options chains |
| `financekit` | Technical indicators, sector rotation, crypto prices |
| `edgartools` | SEC 10-K/10-Q filings, insider transactions, 13F holders |
| `fred` | FRED economic data via `scripts/fred_mcp_wrapper.py` |
| `opennews` | Financial news signals (smart money, price spikes, insider patterns, whale options) |

---

## Python Setup

Dependencies are declared in `pyproject.toml`. The virtual environment is at `.venv/` (gitignored).

```bash
# Install / sync dependencies
uv sync

# Test the core data script
python scripts/fetch_data.py NVDA

# Run the pre-market scanner
python scripts/premarket_scanner.py
```

---

## Recommended Project Layout — Stock Analysis

```text
04-projects/nvda-analysis/
├── PROJECT-OVERVIEW.md     # Goal, scope, watchlist, data sources, risk rules
├── research/               # Sourced company, sector, macro notes
├── trading-journal/        # Setup, entry thesis, invalidation, outcome, lessons
├── charts/                 # Notes referencing screenshots in raw/trading/
└── reports/                # Daily/weekly analysis outputs
```

---

## Note Templates

### Raw Source Metadata

```markdown
---
type: raw-source
category: research
captured: YYYY-MM-DD HH:mm
source_url:
source_title:
source_author:
source_date:
status: captured
processed_to: []
tags: [nvda, semiconductors]
---

# Raw Capture: Source Title

## Why Saved

## Source Notes
```

### Processed Market Note

```markdown
---
type: market-note
symbol: NVDA
created: YYYY-MM-DD HH:mm
para:
  type: area
  name: investing
raw_sources:
  - raw/trading/YYYY-MM-DD-nvda-analysis/metadata.md
tags: [market-analysis, semiconductors, nvda]
---

# NVDA — Thesis Title

## Thesis

## Evidence

## Risks

## Invalidation

## Follow-Up
- [ ] 
```

### Trade Journal Entry

```markdown
---
type: trade-journal
symbol: NVDA
date: YYYY-MM-DD
direction: long
status: planned | open | closed
entry:
stop:
target:
size:
raw_sources: []
---

# NVDA Trade — YYYY-MM-DD

## Setup
## Entry Thesis
## Invalidation
## Outcome
## Lessons
```

---

## Validation

```bash
# Check git state
git status --short

# Validate agent surface
./scripts/validate-agent-surface.sh
```

---

## Notes

- Do not store credentials in markdown notes. All API keys belong in `.mcp.json` or `.env` (both gitignored).
- Market analysis is for personal research only, not investment advice.
- The `_bmad/memory/tm/` wiki is your trading learning system — it compounds over time. Every `/tm-review` makes the next analysis more accurate.
- When COG updates are available, run `/update-cog` — it only touches framework files, never your content.

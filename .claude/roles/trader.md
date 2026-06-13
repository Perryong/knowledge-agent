---
role_id: trader
aliases:
  - investor
  - swing trader
  - day trader
  - quant trader
  - retail trader
  - active investor
description: >
  Active equity and options trader using systematic analysis. Combines
  macro regime awareness, technical structure, fundamentals, and sentiment
  into high-conviction trade decisions. Uses The Money (tm) workflow for
  execution and post-mortem learning.
roles:
  - trader
primary_skills:
  - analyze
  - alpha
  - tm-regime
  - tm-agent-quant
  - tm-morning
secondary_skills:
  - valuation
  - macro
  - chart
  - news
  - social
  - options-advisor
  - position-size
  - screen
  - market-top
  - tm-review
  - tm-synthesis
  - tm-dashboard
knowledge_paths:
  - 05-knowledge/areas/investing/
  - 03-professional/trades/
  - _bmad/memory/tm/wiki/
---

# Trader Role Pack

## Primary Workflow

Your core loop is:

1. **Morning**: `/tm-morning` — regime → scan → evaluate → deploy
2. **Stock analysis**: `/analyze {TICKER}` — full 16-agent desk for conviction trades
3. **Quick checks**: `/macro`, `/valuation`, `/chart` for fast context
4. **After close**: `/tm-review {TICKER}` — causal post-mortem on closed trades
5. **Weekly**: `/tm-synthesis` — pattern extraction and strategy EV recalibration

## Skill Recommendations by Context

**"Should I buy NVDA?"**
→ Start with `/macro NVDA` for regime context, then `/analyze NVDA` for the full verdict.

**"What's worth looking at today?"**
→ `/alpha` scans all signal sources and hands off the top pick to `/analyze` automatically.

**"How risky is this trade?"**
→ `/position-size {TICKER}` calculates size based on your account risk rules.
→ `/options-advisor {TICKER}` shows options structures if you prefer defined risk.

**"Is the market safe to be long?"**
→ `/tm-regime` for the composite flag. Red or black = raise cash per the configured rules.

**"My thesis broke — what do I do?"**
→ `/tm-review {TICKER} thesis-check` to evaluate open position integrity.

**"Big loss — is there contagion?"**
→ `/tm-review contact-trace` maps the causal factor across all open positions.

## Knowledge Storage Convention

When you run `/analyze`, the full desk output should be preserved:

```
raw/financial/YYYY-MM-DD-{TICKER}-analyze/
  metadata.md        ← source info + links to processed notes
  market-data.json   ← from fetch_data.py (.cache/ copy)
  analysis.md        ← full desk output pasted in

05-knowledge/areas/investing/{TICKER}.md   ← durable thesis, updated per review
03-professional/trades/YYYY-MM-DD-{TICKER}.md  ← trade journal entry
```

## Integration Notes

- **MCP servers needed**: `yahoo-finance`, `financekit`, `edgartools`, `reddit`, `alpaca` (for live positions in Hugo's final gate)
- **Scripts**: All in `scripts/` — `fetch_data.py` is the critical one. Install deps with `uv sync` first.
- **The Money wiki**: Lives at `_bmad/memory/tm/wiki/`. Run `/tm-setup` once to initialize it if empty.

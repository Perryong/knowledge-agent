# Players & Competitive Landscape: AI-Agent-over-Obsidian (Local/Open-Model Focus)

*Research date: 2026-06-13 | Thread: players-landscape | Live web sources*
*NOTE: subagent file write was blocked; this file reconstructed by lead from returned text. Several claims flagged UNVERIFIED — see fact-check priorities at bottom.*

---

## In-Obsidian plugins / tools

### 1. Khoj
- Self-hostable personal AI agent / second brain. AGPL-3.0. ~34,400 stars (early 2026). YC W24.
- Full Ollama integration; cloud APIs also supported; offline mode on consumer hardware.
- TRUE AGENT: semantic search over Obsidian/Notion/GitHub/email/PDFs; custom agents with personas + tools; scheduled automations; deep research loops.
- Indexes local files via semantic vector search; Obsidian plugin available.
- Verdict: most feature-complete open-source option; genuine write/act beyond retrieval.

### 2. Reor
- Standalone local-first AI note app (NOT an Obsidian plugin). MIT. ~8,400 stars.
- Local execution via Ollama + Transformers.js; LanceDB embedded vector store; no API key.
- Chat-over-notes / RAG Q&A only; auto-links related notes; NOT a multi-step agent.
- Points at a markdown directory (Obsidian-compatible; can share the folder).

### 3. Copilot for Obsidian (logancyang)
- Obsidian plugin, LLM chat + vault RAG. MIT. ~6,200 stars (June 2026). github.com/logancyang/obsidian-copilot
- Native Ollama (CORS toggle); supports OpenAI/Anthropic/Google/LM Studio/any OpenAI-compatible; reasoning tokens from local models (2025); Ollama embeddings.
- Primarily CHAT + RAG ("Copilot Plus" auto-context). Does NOT autonomously write back / run tool loops.
- Verdict: most polished local LLM chat plugin; lowest barrier for a Hermes setup (set Ollama base URL + select Hermes). Not a true agent.

### 4. Smart Connections (brianpetro)
- Obsidian plugin, semantic search + Smart Chat. MIT. ~5,100 stars. github.com/brianpetro/obsidian-smart-connections
- Built-in on-device embedding model (zero setup); Smart Chat Pro (paid) adds model routing; Smart Chat spun to own plugin (early 2026).
- CHAT + semantic search only; not a write/act agent.

### 5. Text Generator (+ variants: Local LLM Helper/manimohans, LLM Hub/takeshy)
- Template-driven generation within notes. Supports Ollama/LM Studio/vLLM/LocalAI/Anthropic/Google/Mistral/OpenAI per variant.
- Generation within notes, not agentic. LLM Hub adds workflow automation + RAG (most capable variant).

### 6. Obsidian Companion (rizerphe)
- Inline AI autocomplete (copilot-style ghost text). Ollama via community forks. Autocomplete only — out of scope for "agent brain."

### 7. SystemSculpt AI
- Obsidian plugin: AI chat + vault tools (read/search/edit/move/organize) + transcription + workflow automation. Free, bring own keys. Ollama guidance; agent-mode toggle.
- APPROACHING AGENT: vault write-back exists; less community-established than Khoj/Smart Connections.

### 8. MCP-based Obsidian agents (agent runs OUTSIDE Obsidian)
- **cyanheads/obsidian-mcp-server** (~556 stars): full CRUD vault ops (read/write/patch/delete/move/search/frontmatter/tags) via Obsidian Local REST API plugin; any MCP client.
- **MCPVault (bitbonsai/mcpvault)**: lightweight MCP vault bridge; v0.11.0 (Mar 2026) added list_all_tags.
- **obsidian-local-llm-hub (takeshy)**: all-in-one local AI hub — LLM chat w/ vault tools, MCP servers, RAG, automation, encryption; fully private.
- Verdict: MCP route = most powerful TRUE AGENT capability; any Ollama-served local model + MCP harness can connect. This is the plumbing layer for a Hermes setup.

## New since mid-2025
- **kepano/obsidian-skills** (Jan 2026, MIT, by Obsidian CEO Steph Ango): teaches AI agents (Claude Code, Codex CLI, OpenCode) to use Obsidian CLI + open formats (Markdown, Bases, JSON Canvas). Skill/instruction set, not a plugin. Star count UNCERTAIN (launch ~5,200; one source 32,974, may conflate repos).
- **Cortex plugin**: Claude Code agent inside Obsidian sidebar; full vault write; frontier-only (Claude API).
- **Obsidian Chat plugin**: agentic assistant in vault (read/edit/create/frontmatter/navigate).
- **AI Agents plugin**: define custom agents as Markdown files (role, system prompt, tool perms).
- **LLM Wiki plugin**: reads vault, extracts people/ideas/connections, answers with clickable wikilinks.

## KEY FINDING — Dedicated Hermes + Obsidian products [HIGH FACT-CHECK PRIORITY]
### Hermes Agent (NousResearch/hermes-agent) — UNVERIFIED, treat skeptically
- Claimed: official Nous Research agent framework, MIT, released ~Feb 2026, ~22,000 stars / 242 contributors.
- Claimed docs: hermes-agent.nousresearch.com/docs/ ; repo github.com/NousResearch/hermes-agent ; hermes-agent.org
- Claimed behavior: closed loop (task execution → auto-skill generation → long-term memory update), self-improving; model-agnostic (Ollama/vLLM/OpenAI/OpenRouter); local-first one-line installer.
- Claimed config: min 64K context; Ollama default 4,096 silently truncates → set `-c 65536`.
- Claimed Obsidian integration: built-in skill (default v0.14+), two-way vault sync, scoped access, daily logs, memory surfaces; skill files as Markdown. v0.14 = 2026-05-16.
- RISK: several supporting sources are low-quality SEO (fast.io, designforonline, petronellatech, hashnode). MUST verify the GitHub repo + nousresearch.com directly before stating as fact.

### Hermes Console (Obsidian plugin) — UNVERIFIED
- Claimed: community plugin (Danny Shmueli), github.com/dannyshmueli/obsidian-hermes-console, community.obsidian.md/plugins/hermes-console, updated June 2026. Runs Hermes Agent in Obsidian sidebar.

### Local Hermes model options (cross-ref thread 1)
- `ollama pull finalend/hermes-3-llama-3.1:8b-q4_K_M`; vLLM `--tool-call-parser hermes`.
- Hermes 3 (Llama 3.1, 3B/8B/70B/405B, native <tool_call> XML); Hermes 4.3 (Seed-36B, 2025-08-25); DeepHermes 3 Preview (Feb 2025, toggleable <think>).

## Frontier contrast
- **Claude Code / COG vault**: Claude Code pointed at vault as working dir; skills (CLAUDE.md, .claude/skills/, obsidian-skills); MCP servers. Requires Anthropic API (paid, cloud, notes leave device, no offline).
- **Cursor over vault**: reads .md as text; same MCP servers; frontier-dependent; same cloud/cost/privacy issues.

## Where a Hermes-driven LOCAL agent fits
Privacy (on-device), offline, one-time hardware cost vs per-token fees, full vault write via MCP. Model quality competitive at 70B+, capable at 8B for simple tasks. Setup complexity medium. Persistent memory via self-writing files.

Closest ready-made path (June 2026, IF Hermes Agent verified): Ollama → pull hermes3:8b/70b → Hermes Agent (set ctx 65536) → enable Obsidian skill → Hermes Console plugin. Fallback (verified-safe): Khoj + Ollama, or MCP route (Ollama + obsidian-mcp-server + kepano/obsidian-skills).

## Claims (inline source + date) — see original for full list
- Khoj AGPL, ~34.4k stars, YC W24, Ollama, Obsidian plugin [github.com/khoj-ai/khoj | 2026-02]
- Reor MIT ~8.4k, Ollama+Transformers.js+LanceDB [github.com/reorproject/reor | 2025-2026]
- Copilot for Obsidian ~6.2k, native Ollama [github.com/logancyang/obsidian-copilot | 2026-06]
- Smart Connections ~5.1k, on-device embeddings [github.com/brianpetro/obsidian-smart-connections | 2026]
- cyanheads/obsidian-mcp-server ~556, full CRUD via Local REST API [github.com/cyanheads/obsidian-mcp-server | 2025-2026]
- kepano/obsidian-skills Jan 2026 MIT, Obsidian CEO [github.com/kepano/obsidian-skills | 2026-01]
- Hermes Agent [UNVERIFIED] MIT Feb 2026 Nous ~22k [hermes-agent.org ; hermes-agent.nousresearch.com/docs | 2026-02]
- Hermes Console [UNVERIFIED] [community.obsidian.md/plugins/hermes-console | 2026-06]
- Hermes 3 Llama 3.1, tool_call XML [arxiv.org/pdf/2408.11857 | 2024-08]
- vLLM `--tool-call-parser hermes` [deepwiki NousResearch/Hermes-Function-Calling | 2025-2026]

## Conflicting / uncertain
- Copilot stars 5.3k–6.2k. obsidian-mcp-server stars 179 vs 556. kepano/obsidian-skills star count uncertain. Reor GitHub not directly fetched.
- **Hermes Agent product is distinct from Hermes LLM** — both attributed to Nous Research but separate; existence of the agent framework product NEEDS primary-source verification.

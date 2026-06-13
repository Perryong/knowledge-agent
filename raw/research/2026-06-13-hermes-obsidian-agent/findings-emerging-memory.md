# Emerging Memory Frameworks vs Obsidian-Vault-as-Memory

*Research date: 2026-06-13 | Live web, ~40 sources | reconstructed by lead (subagent file write blocked)*

## 1. Dedicated agent-memory frameworks
### Mem0
- Multi-layer memory: semantic + BM25 + entity matching across user/session/agent state; 2026 covers 21 frameworks, 20 vector stores, 3 hosting models. [mem0.ai/blog/state-of-ai-agent-memory-2026 | 2026]
- Self-host: 3 Docker containers (API, Postgres+pgvector, Neo4j); Qdrant alt. [mem0.ai/blog/self-host-mem0-docker | 2025-2026]
- **OpenMemory** = local-first MCP memory server; merged into mem0/openmemory. [huggingface.co/blog/lynn-mikami/open-memory-mcp-server | 2025-2026]
- Mem0 plugin for AI editors (Mar-Apr 2026): 9 MCP tools, Claude Code/Cursor/Codex. [chatforest.com/reviews/mem0-mcp-server | 2026]
- vs flat markdown: auto entity dedup, cross-session user modeling, multi-signal retrieval.

### Letta (ex-MemGPT)
- MemGPT→Letta rebrand Sep 2024 (pattern vs framework). [letta.com/blog/memgpt-and-letta | 2024-09]
- **Context Repositories** (Feb 2026): memory projected into git-backed files via computer-use tools; local "MemFS" at ~/.letta/lc-local-backend/memfs/. [letta.com/blog/context-repositories | 2026-02]
- Letta Code (Apr 2026): memory-first coding harness, git-backed memory, cross-model. [github.com/letta-ai/letta-code | 2026-04]
- Sleep-time compute (Apr 2025): memory reasoning during idle. Conversations API (Jan 2026): shared memory across sessions.
- vs flat markdown: MemFS is architecturally closest to an Obsidian vault — memory AS inspectable git-versioned files; difference = LLM autonomously edits its own memory.

### Zep / Graphiti
- Graphiti = temporal KG engine; 20k+ stars; "Zep: A Temporal KG Architecture for Agent Memory" arXiv:2501.13956 (Jan 2025).
- Each fact carries valid_from / valid_to / invalid_at. LongMemEval: +18.5% accuracy, -90% latency vs baseline. [vectorize.io/articles/zep-vs-cognee | 2026]
- Zep Community Edition deprecated; self-host = Graphiti on Neo4j 5.26+/FalkorDB/Kuzu; FalkorDB sub-10ms. [blog.getzep.com/graphiti-knowledge-graphs-falkordb-support | 2025-2026]
- vs Obsidian: temporal validity + contradiction detection + multi-hop traversal that manual wikilinks lack.

### A-MEM
- arXiv:2502.12110 (Feb 2025), NeurIPS 2025 poster, MIT (github.com/WujiangXu/A-mem).
- Zettelkasten for agents: each memory → structured note (desc, keywords, tags); agent links to history; memory evolution updates existing notes. [arxiv.org/html/2502.12110 | 2025-02]
- Relevance: philosophically identical to manual Obsidian Zettelkasten, but links are agent-driven. Maps cleanly to agent memory design.

### Cognee
- Open-source memory (github.com/topoteretes/cognee, MIT); 30+ connectors → self-hosted KG (vector + graph). [2025-2026]
- Claude Code hooks capture tool calls → permanent KG at session end. Self-host w/ Ollama. add-cognify-search extracts entities/relations. [EARLY maturity]
- vs flat markdown: automatic entity/relationship extraction from unstructured text.

## 2. Knowledge-graph / GraphRAG vs Obsidian wikilinks
- **MS GraphRAG**: LLM over whole corpus → entities/relations → Leiden communities → multi-level summaries; Jan 2025 Dynamic Community Selection cut tokens 79%; large-corpus index cost $33K (2024). [microsoft.com/research/project/graphrag | 2025-01]
- **LightRAG**: dual-level retrieval, MIT, 70-90% of GraphRAG quality at ~1/100th index cost. GraphRAG for 1K-1M tokens; LightRAG wins on cost above. [paperclipped.de/en/blog/graph-rag-production | 2026]
- vs Obsidian wikilinks: human-curated/precise/static vs auto-extracted/implicit/may-hallucinate. Complementary, neither invalidates other.

## 3. Local-first Hermes + Obsidian integrations
- **Neural Composer** (Obsidian plugin): LightRAG in Obsidian; auto local server lifecycle; graph in .neural_memory inside vault (Git/iCloud sync); free OSS. [forum.obsidian.md/t/neural-composer.../109891 | 2025-2026]
- **local-rag** (Ricardo-Kaminski): 100% local RAG for Obsidian/Zotero/Claude Code; LightRAG+Ollama+MCP. [github.com/Ricardo-Kaminski/local-rag]
- **cyanheads/obsidian-mcp-server**: MCP vault CRUD via Local REST API; any local Hermes via Ollama.
- **bitbonsai/mcpvault**: lightweight safe MCP vault access; broad client compat.
- **zilliztech/memsearch** (OSS Mar 12 2026): persistent memory = markdown files + Milvus index ("cache — rebuild from md if lost"); hybrid BM25+semantic; Claude Code/OpenCode/Codex. [github.com/zilliztech/memsearch | 2026-03]
- **memweave** (sachinsharma9780, Apr 2026): .md on disk + SQLite (sqlite-vec); SHA-256 embed cache, temporal decay, MMR; no server/Docker/cloud; git-diffable. [towardsdatascience.com/memweave | 2026-04]
- **ObsidianRAG** (Vasallo94): privacy-first RAG, LangGraph + local LLMs, fully offline.
- **obsidian-wiki** (ar9av): AI agents build/maintain digital brain via Karpathy LLM Wiki pattern. [EARLY]
- **Hermes-specific**: Hermes Agent Obsidian integration renders MEMORY.md/USER.md as markdown surfaces synced w/ Obsidian. [EARLY — third-party docs hermes-agent.ai/tools/hermes-obsidian-plugin; verify official]

## 4. On-device / personal agent projects (mid-2025+)
- **OpenJarvis** (Apache 2.0, Jun 3 2026): local-first on-device agents; 5 primitives; local models handle 88.7% single-turn, cloud for rest. [EARLY] [marktechpost.com/.../openjarvis | 2026-06]
- **MemOS** (MemTensor): v2.0 Stardust (Dec 2024) + Local Plugin v1.0.0 (Mar 2026); on-device SQLite, FTS5+vector hybrid, skill evolution, multi-agent. [github.com/MemTensor/MemOS]
- **TencentDB Agent Memory** (MIT, May 23 2026): 4-tier local pipeline L0-L3 (L2 = markdown), local SQLite + sqlite-vec; w/ OpenClaw 61% token savings, PersonaMem 48%→76%. [marktechpost.com/.../tencentdb | 2026-05]
- **Letta MemFS** (Apr 2026): agent memory as local git repo; architecturally similar to Obsidian vault but agent-written.
- **EvolveMem** (arXiv:2605.13941, May 2026): self-evolving memory via AutoResearch. [EARLY preprint]

## 5. Synthesis — obsolete, complementary, or front-end?
**Verdict: COMPLEMENTARY, not obsolete.** Obsidian = durable human-readable source layer; dedicated frameworks = agent-facing retrieval/indexing on top.
- Markdown is winning as the storage primitive: memsearch, memweave, TencentDB L2, Letta MemFS all converge on "markdown = source of truth, vector/graph = rebuildable cache" — Obsidian's own model. [micheallanham.substack.com/markdown-memory-paradigm; dev.to/imaginex | 2026]
- What frameworks add that flat vault can't: (1) temporal validity edges (Zep), (2) auto entity extraction (Cognee/GraphRAG/LightRAG), (3) agent-driven memory evolution (A-MEM/Letta sleep-time), (4) multi-session cross-agent dedup (Mem0/Zep).
- Obsidian role: only path with a mature human-readable interface → best front-end / indexing target for the other five. [fountaincity.tech/.../agent-memory-knowledge-systems-compared | 2026]
- **For single-user local-first (the Hermes/Obsidian case)**: gaps frameworks fill (multi-agent coordination, contradiction detection at scale, multi-year temporal reasoning) are largely irrelevant. Obsidian + LightRAG (Neural Composer) + optional obsidian-mcp-server covers it at zero cost/cloud.
- **Caveat**: thousands of sessions/many users/entity dedup/temporal-across-years → a dedicated framework (Zep/Graphiti or Mem0) becomes necessary infra a flat vault can't replicate.

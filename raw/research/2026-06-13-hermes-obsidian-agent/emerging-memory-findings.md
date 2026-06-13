# Emerging Agent-Memory Frameworks — Research Findings
## Thread: Could These Make Obsidian-as-Memory Obsolete?
## Date: 2026-06-13
## Researcher: worker-researcher (Sonnet)
## Data source: Training knowledge (cutoff Aug 2025) — WebSearch/WebFetch denied in environment
## IMPORTANT: All claims marked [TRAINING-DATA]. Recommend live verification before publishing.
## Knowledge gap: ~10 months unverified (Aug 2025 → Jun 2026). Star counts, release versions likely stale.

---

## 1. The Core Problem: What Flat Markdown Vaults Cannot Do

Before reviewing frameworks, establishing the baseline limitation:

### Claims — Obsidian Vault Weaknesses as Agent Memory

- **Claim 1.1** — Obsidian wikilinks are manually created; an AI agent cannot automatically infer semantic relationships between notes without additional tooling. [TRAINING-DATA | confidence: high]
- **Claim 1.2** — Flat markdown retrieval over a vault = keyword or vector similarity search. This misses multi-hop relational queries ("what decisions were made because of X that later affected Y?"). [TRAINING-DATA | confidence: high]
- **Claim 1.3** — Obsidian has no concept of fact versioning or temporal tracking — a note updated in 2024 does not record that it superseded a 2023 belief. [TRAINING-DATA | confidence: high]
- **Claim 1.4** — No automatic memory consolidation: old notes accumulate without pruning, contradiction detection, or strength-decay. [TRAINING-DATA | confidence: high]
- **Claim 1.5** — No confidence scores or epistemic metadata on individual facts within notes. [TRAINING-DATA | confidence: high]
- **Claim 1.6** — Retrieval from a large vault via RAG is expensive and degrades with vault size; no hierarchical or community-based summarization layer. [TRAINING-DATA | confidence: high]

---

## 2. Dedicated Agent-Memory Frameworks

### 2.1 Mem0 (mem0ai)

**What it is:** Open-source memory layer for LLM agents. Gives persistent, cross-session memory using any LLM backend.

**Source:** https://github.com/mem0ai/mem0 [TRAINING-DATA | last known active: mid-2025]
**Docs:** https://docs.mem0.ai

#### Claims

- **Claim 2.1.1** — Mem0 implements a three-tier memory model: (a) working memory (in-context window), (b) episodic memory (recent interactions), (c) semantic memory (long-term extracted facts). [TRAINING-DATA | confidence: high]
- **Claim 2.1.2** — When new information enters, Mem0 uses an LLM call to extract structured facts and stores them as embeddings in a vector backend. Supported backends: Qdrant, Chroma, FAISS, Pinecone, Weaviate, PGVector. [TRAINING-DATA | confidence: high]
- **Claim 2.1.3** — Mem0 added a graph memory layer (Neo4j integration) in 2025, allowing relationship queries between stored facts — not just vector similarity. [TRAINING-DATA | confidence: medium — verify release date]
- **Claim 2.1.4** — Mem0 supports fully local/self-hosted operation: local LLM via Ollama for fact extraction, Qdrant local instance for vector storage, no cloud dependency. [TRAINING-DATA | confidence: high]
- **Claim 2.1.5** — Mem0 has a managed cloud tier (app.mem0.ai) and a self-hosted open-source tier. [TRAINING-DATA | confidence: high]
- **Claim 2.1.6** — Key differentiator vs. flat vault: automatic extraction of structured, de-duplicated facts from free-form conversation — no manual note-taking required. [TRAINING-DATA | confidence: high]
- **Claim 2.1.7** — Mem0 reached ~20,000+ GitHub stars by mid-2025. [TRAINING-DATA | confidence: low — count stale]

**Verdict vs. Obsidian:** Augments, does not replace. Mem0 excels at automatic extraction and fast retrieval but produces no human-readable artifact. Obsidian serves as the "audit trail" view.

---

### 2.2 Letta (formerly MemGPT)

**What it is:** Full agent development framework built around persistent, pageable memory — treating the LLM like an OS with RAM (context window) and disk (external storage).

**Source:** https://github.com/letta-ai/letta [TRAINING-DATA | rebranded Oct 2024 from MemGPT]
**Docs:** https://docs.letta.com
**Paper (MemGPT):** https://arxiv.org/abs/2310.08560 — Packer et al., UC Berkeley, Oct 2023

#### Claims

- **Claim 2.2.1** — Letta's core innovation: virtual context management — the agent can page information in/out of its context window, analogous to OS virtual memory. This makes effective context size unlimited. [TRAINING-DATA | confidence: high]
- **Claim 2.2.2** — Letta defines three memory types: (a) Core memory (always in context — persona + human description; editable by agent at runtime), (b) Recall memory (searchable conversation history, stored in SQLite), (c) Archival memory (infinite vector store, searched on demand). [TRAINING-DATA | confidence: high]
- **Claim 2.2.3** — Letta agents can modify their own core memory at runtime — they decide what facts are important enough to "pin" in context. This is autonomous memory management, not human-curated. [TRAINING-DATA | confidence: high]
- **Claim 2.2.4** — Letta supports local LLMs via Ollama and llama.cpp. The Letta server runs locally via Docker or direct Python install. [TRAINING-DATA | confidence: high]
- **Claim 2.2.5** — Letta exposes a REST API and Python SDK. Multiple agents can share memory pools. [TRAINING-DATA | confidence: high]
- **Claim 2.2.6** — Key differentiator vs. flat vault: self-modifying memory — the agent rewrites its own understanding rather than appending new notes. No human annotation step required. [TRAINING-DATA | confidence: high]

**Verdict vs. Obsidian:** Partially displaceable. Letta handles the "what the agent remembers" layer autonomously. Obsidian remains useful as a human-readable export/review layer but is not Letta's native format.

---

### 2.3 Zep

**What it is:** Memory store for LLM agents, differentiated by temporal knowledge graph — tracking not just facts but when they changed.

**Source:** https://github.com/getzep/zep | https://docs.getzep.com [TRAINING-DATA | active 2025]

#### Claims

- **Claim 2.3.1** — Zep extracts structured facts from conversation dialogs and stores them in a temporal knowledge graph — each fact has timestamps for creation, modification, and invalidation. [TRAINING-DATA | confidence: high]
- **Claim 2.3.2** — Zep detects when a user's stated fact contradicts a previously stored fact and automatically marks the old fact as superseded. This addresses the temporal staleness problem flat vaults cannot handle. [TRAINING-DATA | confidence: high]
- **Claim 2.3.3** — Zep provides dialog history with automatic summarization, preventing context-window overflow in long agent sessions. [TRAINING-DATA | confidence: high]
- **Claim 2.3.4** — Zep is available as Zep Cloud (managed) and Zep Community Edition (open-source, self-hostable). [TRAINING-DATA | confidence: high]
- **Claim 2.3.5** — Zep Community Edition supports local embeddings (sentence-transformers), enabling fully local operation. [TRAINING-DATA | confidence: medium — verify]
- **Claim 2.3.6** — Key differentiator vs. Obsidian: temporal fact versioning. The vault equivalent would require manually timestamping every factual claim and tracking contradictions, which no human does consistently. [TRAINING-DATA | confidence: high]

**Verdict vs. Obsidian:** Strong complement, especially for agents that interact with dynamic external information (people, projects, changing facts). Obsidian lacks native temporal fact tracking.

---

### 2.4 A-MEM (Agentic Memory)

**What it is:** Research framework proposing Zettelkasten-style structured memory notes for AI agents, with automated linking and evolution.

**Paper:** "A-MEM: Agentic Memory for LLM Agents" — https://arxiv.org/abs/2502.12110 — Feb 2025
**Repo:** https://github.com/WujiangXu/AgenticMemory [TRAINING-DATA]

#### Claims

- **Claim 2.4.1** — A-MEM is the framework most conceptually similar to Obsidian: it organizes memory as "notes" with structured attributes — keywords, context, key insights, linked memory IDs, and relationship strength. [TRAINING-DATA | confidence: high]
- **Claim 2.4.2** — Unlike Obsidian, A-MEM notes are created and linked automatically by the LLM itself. When a new memory is stored, the agent finds semantically similar existing notes and creates explicit links. [TRAINING-DATA | confidence: high]
- **Claim 2.4.3** — A-MEM supports memory evolution: when related memories are found, the agent can update/consolidate them rather than appending a new note — addressing the accumulation problem in flat vaults. [TRAINING-DATA | confidence: high]
- **Claim 2.4.4** — A-MEM uses a memory strength/importance score per note, enabling pruning of weak/stale memories. Flat markdown vaults have no equivalent. [TRAINING-DATA | confidence: high]
- **Claim 2.4.5** — A-MEM's paper benchmarked on QA tasks and showed improvements over both RAG and chain-of-thought baselines for multi-hop memory tasks. [TRAINING-DATA | confidence: medium — verify specific benchmarks]
- **Claim 2.4.6** — [EARLY] A-MEM is a research prototype as of early 2025 — not production-ready. The repo has limited tooling compared to Mem0 or Letta. [TRAINING-DATA | confidence: high]

**Verdict vs. Obsidian:** A-MEM is "Obsidian Zettelkasten done autonomously." Obsidian is the human-facing PKM; A-MEM is the agent-facing equivalent. Conceptually complementary; practically, would need integration work.

---

### 2.5 cognee

**What it is:** Open-source knowledge graph framework for AI agents — builds a structured, queryable knowledge graph from unstructured text.

**Source:** https://github.com/topoteretes/cognee | https://cognee.ai/docs [TRAINING-DATA | active mid-2025]

#### Claims

- **Claim 2.5.1** — cognee implements an ECL pipeline: Extract (parse unstructured text), Cognify (structure into graph entities/relationships), Load (store in graph + vector database). [TRAINING-DATA | confidence: high]
- **Claim 2.5.2** — cognee supports multiple graph backends: Neo4j, NetworkX (in-memory). Vector search and graph traversal are combined for retrieval. [TRAINING-DATA | confidence: high]
- **Claim 2.5.3** — cognee can ingest markdown files as input, suggesting it could build a knowledge graph on top of an Obsidian vault. Direct Obsidian integration not confirmed — inferred from generic file ingestion. [TRAINING-DATA | confidence: medium]
- **Claim 2.5.4** — cognee supports local LLM operation via Ollama. [TRAINING-DATA | confidence: medium]
- **Claim 2.5.5** — Key differentiator vs. Obsidian wikilink graph: cognee's graph is built by LLM-extracted entity/relationship triples, not human-authored wikilinks. Result is denser, semantically consistent, and queryable via graph traversal. [TRAINING-DATA | confidence: high]
- **Claim 2.5.6** — [EARLY] cognee is less mature than Mem0 or Letta as of mid-2025. Smaller community, fewer integrations. [TRAINING-DATA | confidence: medium]

**Verdict vs. Obsidian:** cognee is Obsidian's wikilink graph, automated and queryable. Obsidian becomes the input medium; cognee builds the semantic layer on top.

---

## 3. Knowledge-Graph / GraphRAG Memory

### 3.1 Microsoft GraphRAG

**Paper:** "From Local to Global: A Graph RAG Approach to Query-Focused Summarization" — https://arxiv.org/abs/2404.16130 — Apr 2024
**Repo:** https://github.com/microsoft/graphrag [TRAINING-DATA | v0.3.x, first public release Jul 2024]
**Docs:** https://microsoft.github.io/graphrag/

#### Claims

- **Claim 3.1.1** — GraphRAG builds a hierarchical knowledge graph from a document corpus: entities → relationships → communities (clusters) → community summaries. [TRAINING-DATA | confidence: high]
- **Claim 3.1.2** — GraphRAG enables two retrieval modes: local search (entity-level, "what do we know about X?") and global search (community summaries, "what are the major themes?"). Flat RAG cannot answer global/sensemaking questions well. [TRAINING-DATA | confidence: high]
- **Claim 3.1.3** — GraphRAG requires significant upfront compute: every entity, relationship, and community summary is generated via LLM calls on the entire corpus. For a large Obsidian vault, this is expensive and time-consuming on local hardware. [TRAINING-DATA | confidence: high]
- **Claim 3.1.4** — GraphRAG can run with Azure OpenAI OR local LLMs (Ollama), though local runs are slow for large corpora. [TRAINING-DATA | confidence: high]
- **Claim 3.1.5** — Obsidian wikilink graph vs. GraphRAG: Obsidian's graph is human-authored (sparse, intentional); GraphRAG's is LLM-extracted (dense, comprehensive but noisier). GraphRAG enables multi-hop and global reasoning; Obsidian's graph does not. [TRAINING-DATA | confidence: high]
- **Claim 3.1.6** — GraphRAG produces "community reports" — automatic summaries of clusters of related notes. For a PKM vault, this is analogous to auto-generated MOCs (Maps of Content). [TRAINING-DATA | confidence: high]

---

### 3.2 LightRAG

**Paper:** "LightRAG: Simple and Fast Retrieval-Augmented Generation" — https://arxiv.org/abs/2410.05779 — Oct 2024
**Repo:** https://github.com/HKUDS/LightRAG [TRAINING-DATA | Hong Kong U; active mid-2025]

#### Claims

- **Claim 3.2.1** — LightRAG provides dual-level retrieval: (a) low-level (specific entities and direct relations), (b) high-level (broader semantic clusters). [TRAINING-DATA | confidence: high]
- **Claim 3.2.2** — LightRAG is significantly faster to index than Microsoft GraphRAG — it skips community detection and uses lighter graph construction. [TRAINING-DATA | confidence: high]
- **Claim 3.2.3** — LightRAG stores its graph as JSON files + a vector index, or optionally in Neo4j. This means it can run entirely on local filesystem — compatible with Obsidian vault storage patterns. [TRAINING-DATA | confidence: medium]
- **Claim 3.2.4** — LightRAG has native support for local LLMs via Ollama and llama.cpp. This makes it the most practical GraphRAG option for a local Hermes deployment. [TRAINING-DATA | confidence: high]
- **Claim 3.2.5** — LightRAG reached ~50,000+ GitHub stars by mid-2025 — exceptionally rapid adoption for a 6-month-old framework at that time. [TRAINING-DATA | confidence: low — count stale]
- **Claim 3.2.6** — LightRAG can be run against a directory of markdown files. It would ingest an Obsidian vault, extract entities/relations, and serve graph-aware queries over it — making it a retrieval augmentation layer ON TOP of the vault, not a replacement. [TRAINING-DATA | confidence: high]

---

## 4. Local-First / Self-Hosted Stack Configurations

### Claims

- **Claim 4.1** — Fully local Mem0 stack (mid-2025): Mem0 + Qdrant (local Docker) + Ollama (local LLM for fact extraction) + NetworkX (optional graph). Zero cloud dependency. [TRAINING-DATA | confidence: high]
- **Claim 4.2** — Fully local Letta stack: Letta server (Docker or pip) + Ollama/llama.cpp + SQLite (recall memory) + local Chroma/Qdrant (archival memory). Can run on a personal machine with 8GB+ VRAM. [TRAINING-DATA | confidence: high]
- **Claim 4.3** — Fully local LightRAG stack: LightRAG + Ollama + local Neo4j or JSON storage. LightRAG on a ~500-note Obsidian vault with Hermes-3-8B would be feasible on consumer hardware. [TRAINING-DATA | confidence: medium — vault size and model size dependent]
- **Claim 4.4** — Zep Community Edition self-hosts via Docker; can use local embedding models (sentence-transformers) rather than OpenAI embeddings. [TRAINING-DATA | confidence: medium]
- **Claim 4.5** — cognee with local Ollama is documented in their README; graph backend can be NetworkX (in-process, no external server). [TRAINING-DATA | confidence: medium]
- **Claim 4.6** — The most critical constraint for local operation is LLM quality for fact extraction: smaller models (7B-13B) produce noisier structured outputs. Hermes-3 (Nous Research) is specifically trained for instruction-following and structured output tasks, making it a better fit than generic 7B models for fact extraction steps in Mem0/cognee pipelines. [TRAINING-DATA | confidence: high]

---

## 5. On-Device / Personal Agent Projects

### Claims

- **Claim 5.1** — OpenWebUI (the Ollama front-end) added a memory plugin system in 2024-2025 that stores user facts across sessions using local vector embeddings. [TRAINING-DATA | confidence: medium]
- **Claim 5.2** — Open Interpreter (open-interpreter.com) uses file-based memory logs and has experimented with persistent context across sessions, but is not a structured memory system. [TRAINING-DATA | confidence: medium]
- **Claim 5.3** — The "Local AI Stack" community pattern (Ollama + Open WebUI + n8n + Qdrant) increasingly includes Mem0 or Letta as the memory layer — indicating grassroots convergence toward these frameworks for personal AI. [TRAINING-DATA | confidence: medium]
- **Claim 5.4** — Apple Intelligence (iOS 18/macOS Sequoia) introduced on-device semantic indexing of personal data — a hardware-accelerated competitor to software agent-memory frameworks. As of Aug 2025, scope was limited to Apple-ecosystem data, not open-agent integration. [TRAINING-DATA | confidence: medium — likely evolved since Aug 2025]
- **Claim 5.5** — [EARLY] Several community prototypes by mid-2025 combined Obsidian + local LLM + memory frameworks: agent reads from vault via RAG, writes summaries back as new markdown notes. No dominant pattern had emerged. [TRAINING-DATA | confidence: medium]

---

## 6. Synthesis: Does This Make "Obsidian as Memory Store" Obsolete?

### The Three Roles Obsidian Can Play

#### Role A: Primary Agent Memory Store (WEAKENING)
- Obsidian as the sole memory backend — agent reads/writes markdown files
- Weaknesses documented above make this increasingly suboptimal vs. dedicated frameworks
- Verdict: **Declining position** for agents that need automatic extraction, temporal tracking, or graph-aware retrieval

#### Role B: Human-Readable Export / Audit Layer (STABLE)
- Agent memory lives in Mem0/Letta/Zep; periodically exports structured facts to Obsidian markdown
- Human uses Obsidian as the review and annotation interface
- Verdict: **Strongest position** — Obsidian's PKM UI, plugins, and mobile sync remain unmatched for human interaction with agent-derived knowledge

#### Role C: Input Corpus for GraphRAG Layer (GROWING)
- Obsidian vault = source of human-authored notes; LightRAG or GraphRAG builds a knowledge graph on top
- Agent queries the graph layer, not the flat files
- Agent's new knowledge writes back to vault as markdown notes
- Verdict: **Emerging best practice** — makes Obsidian a "front-end" for a richer retrieval layer

### Capability Comparison Table

| Capability | Mem0 | Letta | Zep | A-MEM | cognee | LightRAG | Obsidian Vault |
|-----------|------|-------|-----|-------|--------|----------|----------------|
| Auto fact extraction | Yes | Yes | Yes | Yes | Yes | Partial | No |
| Temporal fact versioning | Partial | No | Yes | No | No | No | No |
| Graph relationship inference | Yes (2025) | No | Yes | Yes | Yes | Yes | Manual only |
| Memory consolidation/pruning | Partial | Partial | Yes | Yes | No | No | No |
| Self-modifying memory | No | Yes | No | Yes | No | No | No |
| Human-readable native format | No | No | No | No | No | No | **Yes** |
| Mobile/desktop PKM UI | No | No | No | No | No | No | **Yes** |
| Local/self-hosted | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Hermes-compatible (local LLM) | Yes | Yes | Partial | Yes | Yes | Yes | N/A |

### Final Verdict

**Obsidian as agent memory is not obsolete — it is evolving into a front-end and audit layer rather than the primary memory engine.**

The trajectory points toward a layered architecture:
1. **Human interface layer** → Obsidian (write notes, browse, annotate, mobile sync)
2. **Extraction + structuring layer** → Mem0 or cognee (convert vault content + agent output to structured facts/graph)
3. **Agent retrieval layer** → LightRAG or Zep (graph-aware, temporally-aware queries)
4. **Write-back layer** → Agent writes summaries back to Obsidian as new markdown notes

A-MEM is the conceptual bridge: it does for agents what Obsidian's Zettelkasten does for humans. The gap is automation, not concept.

Hermes-3 (Nous Research) is well-suited as the extraction/reasoning LLM in this stack: its strong instruction-following and function-calling capabilities matter most at the extraction and consolidation steps, where output structure quality is critical for memory quality downstream.

---

## 7. Data Quality / Staleness Notes

- All claims derive from training knowledge (cutoff Aug 2025)
- ~10 months unverified — framework versions, GitHub stars, and feature sets have likely changed
- A-MEM and cognee are most likely to have evolved (early-stage projects at training cutoff)
- Letta and Mem0 are well-established; architecture fundamentals are stable
- LightRAG adoption trajectory was extremely steep — may now be more mature or have competitors
- **Recommend live fetch** of GitHub READMEs, arXiv abstracts, and official docs for all frameworks before publishing
- Specific URLs for verification: see emerging-memory-frameworks-sources.md in this directory

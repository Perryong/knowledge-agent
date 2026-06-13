# Technology Trajectory: Hermes + Obsidian Agent Stack
## Research Thread: Where This Stack Is Heading (12–24 Months)
Researcher: worker-researcher (parallel thread 6 of 6)
Date: 2026-06-13
Note: WebSearch blocked; WebFetch limited to modelcontextprotocol.io + developer.apple.com.
Training-knowledge claims labelled explicitly. /tmp write blocked — file stored in vault raw/.

---

## Source Quality Legend
- **[PRIMARY-FETCH]** — Direct fetch from authoritative source on 2026-06-13. High confidence.
- **[TRAINING ~Aug2025]** — From model training data, cutoff ~August 2025. Verify recency.
- **[SPECULATION]** — Inferred/projected, not from a primary source.

---

## 1. MCP — Standardization & Trajectory

### Claims

**MCP is an open multi-company standard under Linux Foundation**
MCP is governed as "Model Context Protocol, a Series of LF Projects, LLC." Apache 2.0 license. No company-reserved seats — membership is individual. Lead Maintainers: David Soria Parra, Den Delimarsky.
Source: https://modelcontextprotocol.io/community/governance.md | 2026-06-13 | [PRIMARY-FETCH]

**Confirmed client adoption: Claude, ChatGPT, VS Code Copilot, Cursor, Goose, Postman, MCPJam, Archestra.AI**
All listed clients support MCP Apps (interactive UI extension) per the official client matrix. Registry backed by Anthropic, GitHub, PulseMCP, Microsoft — in preview as of fetch date.
Source: https://modelcontextprotocol.io/extensions/client-matrix.md | 2026-06-13 | [PRIMARY-FETCH]

**Current spec version: 2025-11-25; active protocol version string in examples: 2025-06-18**
Source: https://modelcontextprotocol.io/specification/2025-11-25/index.md | 2026-06-13 | [PRIMARY-FETCH]

**41 Final SEPs as of 2026-06-13 — velocity is high**
Most recent Finals: SEP-2663 Tasks Extension (2026-04-27), SEP-2577 Deprecate Roots/Sampling/Logging (2026-04-14), SEP-2575 Stateless MCP (originated 2025-06-18), SEP-2567 Sessionless MCP (2026-03-11), SEP-1865 MCP Apps (2025-11-21), SEP-1686 Tasks (2025-10-20), SEP-1577 Sampling With Tools (2025-09-30).
Source: https://modelcontextprotocol.io/seps/index.md | 2026-06-13 | [PRIMARY-FETCH]

**Roadmap priorities (as of 2026-03-05): transport scalability, agent communication, enterprise readiness**
Priority 1: Stateless Streamable HTTP (horizontal scaling, load balancer friendly), MCP Server Cards (.well-known URL). Priority 2: Tasks lifecycle (retry semantics, expiry). Priority 4: Enterprise (audit trails, SSO, gateway/proxy patterns).
Source: https://modelcontextprotocol.io/development/roadmap.md | Updated 2026-03-05 | [PRIMARY-FETCH]

**Tasks extension (SEP-2663, Final Apr 2026) directly solves long-running agent action problem**
Returns durable task handles; states: working → input_required → completed/failed/cancelled. Crash-resilient (task ID persists across reconnects). Server-push notifications eliminate polling. Mid-flight user input via tasks/update.
Source: https://modelcontextprotocol.io/extensions/tasks/overview.md | 2026-06-13 | [PRIMARY-FETCH]

**Sampling With Tools added (SEP-1577, Final Sep 2025): servers can request LLM completions that include tool use**
Enables recursive/agentic server-side reasoning — major architectural expansion.
Source: https://modelcontextprotocol.io/seps/index.md | 2026-06-13 | [PRIMARY-FETCH]

**On the horizon: Triggers (webhooks), streaming results, Skills primitive**
MCP roadmap names as community-interest (not yet prioritized): event-driven push from servers (vault change → agent notification), streaming large results, "Skills" primitive for composed capabilities.
Source: https://modelcontextprotocol.io/development/roadmap.md | 2026-03-05 | [PRIMARY-FETCH]

**MCP stdio transport is purpose-built for local agent ↔ vault integration**
Stdio transport = local process communication, no network overhead, optimal for Obsidian-as-local-MCP-server pattern.
Source: https://modelcontextprotocol.io/docs/learn/architecture.md | 2026-06-13 | [PRIMARY-FETCH]

**[SPECULATION] MCP will be the de facto standard for agent-tool integration within 12-24 months**
Rationale: coverage of all major AI IDEs + Linux Foundation governance removes Anthropic lock-in + 41 Final SEPs in ~12 months = unusually fast ecosystem velocity. Obsidian MCP community servers inherit every client integration for free.

---

## 2. Open-Weight LLM Progress for Agents

### Claims

**Tool/function calling reliability improved dramatically in open-weight models 2023–2024**
Llama 3.1 (Meta, Jul 2024), Qwen 2.5 (Alibaba, Sep 2024), Mistral variants all shipped structured JSON Schema function calling. Berkeley's Gorilla LLM project showed open models can match GPT-4 on API call accuracy with targeted fine-tuning.
Source: [TRAINING ~Aug2025] — Meta AI, Alibaba announcements

**Long-context is now a commodity: 128K tokens in open-weight models**
Llama 3.1 (all sizes), Qwen 2.5, and others support 128K context natively. A 128K context window means a medium-sized Obsidian vault can fit in context without RAG.
Source: [TRAINING ~Aug2025]

**Reasoning capability reached open-weight in early 2025**
DeepSeek-R1 (January 2025) demonstrated o1-comparable chain-of-thought reasoning as open-weight. QwQ-32B (Qwen team, December 2024) showed strong reasoning in 32B parameter model.
Source: [TRAINING ~Aug2025] — DeepSeek-R1 paper Jan 2025; QwQ-32B Dec 2024

**Small models have become capable: 3.8B–7B for local agent use**
Phi-3 Mini 3.8B (Microsoft, April 2024), Gemma 2 2B (Google, June 2024) both reached near-Llama-3-8B quality on reasoning tasks. Small models approaching a threshold where they handle tool-calling reliably for structured/constrained agent tasks.
Source: [TRAINING ~Aug2025]

**Hermes 3 (Nous Research, August 2024) based on Llama 3.1 with strong agent capabilities**
Released on 8B, 70B, and 405B. Improved: chatml format, system prompt adherence, function calling, agentic task handling. Available in GGUF, MLX, AWQ formats.
Source: [TRAINING ~Aug2025] — Nous Research HuggingFace blog, August 2024

**[SPECULATION] Hermes 4 probable within one quarter of Llama 4 / successor release**
Nous Research's pattern: base model release → Hermes fine-tune within 2–4 months. If Meta's next frontier model releases in late 2025 or 2026, Hermes 4 follows soon after.

**[SPECULATION] Native MCP tool-call format training is likely in future Hermes releases**
As MCP becomes the standard function-calling schema in AI dev tools, fine-tuning datasets will increasingly use MCP JSON-RPC format. Hermes is likely to adapt to this.

---

## 3. Local Inference Trajectory: Hardware & Quantization

### Claims

**GGUF (llama.cpp) is the dominant local CPU+GPU hybrid inference format**
Q4_K_M is the quality/speed sweet spot; Q8_0 is near-lossless. llama.cpp supports: Metal (Apple Silicon), CUDA (NVIDIA), Vulkan, OpenCL. Features added by mid-2025: flash attention, speculative decoding, continuous batching.
Source: [TRAINING ~Aug2025] — llama.cpp GitHub 2024

**AWQ provides better 4-bit quality than naive GGUF Q4**
AWQ (MIT, 2023) preserves quantization-sensitive weights at higher precision. GPTQ targets GPU inference. Both widely available on HuggingFace for major model families.
Source: [TRAINING ~Aug2025] — AWQ paper 2023

**Apple Silicon unified memory: running 70B models locally is real**
M3 Max: up to 128GB unified memory. M3 Ultra: up to 192GB. Llama-3.1-70B at Q4 ≈ 40GB — fits on M3 Max. M4 generation (2024) continues the trajectory with improved Neural Engine performance.
Source: [TRAINING ~Aug2025] + developer.apple.com | 2026-06-13 | [PRIMARY-FETCH] (MLX/Metal 4 confirmed active)

**MLX framework is the preferred path for Apple Silicon LLMs**
Apple's open-source MLX framework (Dec 2023) is optimized for unified memory architecture. Achieves significantly higher tokens/sec than llama.cpp on Apple Silicon. Scales training/fine-tuning across multiple Macs via RDMA over Thunderbolt (Metal 4). MLX-format weights available on HuggingFace.
Source: developer.apple.com/machine-learning/ | 2026-06-13 | [PRIMARY-FETCH] + [TRAINING ~Aug2025]

**NVIDIA RTX 4090 (24GB VRAM) enables consumer GPU local inference of large models**
Q4-quantized 70B with CPU offload; Q8-quantized 34B fully in VRAM. RTX 5000 series (announced Jan 2025) expected to push VRAM limits further.
Source: [TRAINING ~Aug2025]

**NPU integration is early but accelerating**
Snapdragon X Elite NPU: 45 TOPS; used for Phi-3 / Llama-3-8B on Windows ARM AI PCs. Apple Neural Engine: integrated all Apple Silicon; primarily used for CoreML/Apple Foundation Models path (not open-weight). Intel NPU (Meteor Lake, 2024): smaller models on AI PCs.
Source: [TRAINING ~Aug2025]

**Speculative decoding gives 2–4x throughput improvement for generation tasks**
Widely implemented in llama.cpp, vLLM, Ollama by mid-2025.
Source: [TRAINING ~Aug2025]

**Ollama provides OpenAI-compatible local LLM API**
Single-command local model serving with REST API that accepts OpenAI format requests. Any tool built for GPT can point at Ollama + Hermes. Directly relevant for Obsidian agent integration.
Source: [TRAINING ~Aug2025]

**[SPECULATION] Within 24 months: 13B models running at quality comparable to GPT-3.5 with no quantization on consumer NPUs**
NPU trajectory (45 TOPS → projected 100+ TOPS by 2026–2027) + smaller capable models converging toward a threshold where consumer hardware removes the need for quantization for agent-scale tasks.

---

## 4. Agent Memory Architectures

### Claims

**Three paradigms in active use: long-context, RAG, and structured memory — no convergence yet**
Source: [TRAINING ~Aug2025]

**Long-context ("stuff the vault") is newly viable**
128K tokens on local models; medium Obsidian vaults (< ~50K tokens) can fit in a single pass. Eliminates retrieval latency and retrieval misses. Tradeoff: slower inference, higher memory per request.
Source: [TRAINING ~Aug2025]

**RAG remains dominant for large knowledge bases**
Tools: ChromaDB, FAISS (local), Weaviate (local), Pinecone (cloud). Embedding models for local use: nomic-embed-text, sentence-transformers. Key limitation: quality bounded by chunking strategy and query formulation.
Source: [TRAINING ~Aug2025]

**MemGPT/Letta (Stanford, Oct 2023) pioneered paged memory management for agents**
Manages agent context like an OS manages RAM: explicit paging in/out from external storage. Most principled approach but adds latency. Renamed to Letta platform.
Source: [TRAINING ~Aug2025] — MemGPT paper October 2023

**Mem0 (2024) provides a lightweight structured agent memory layer**
Extracts facts from conversations; retrieves relevant memories per-query. Sits between raw RAG and full MemGPT complexity.
Source: [TRAINING ~Aug2025]

**Microsoft GraphRAG (2024) enables multi-hop reasoning across document graphs**
Builds a knowledge graph from documents before retrieval; significantly improves retrieval for questions requiring connections across multiple notes. Directly applicable to Obsidian vaults which already have explicit wikilink graphs.
Source: [TRAINING ~Aug2025] — Microsoft GraphRAG paper/release 2024

**Obsidian's wikilink graph is an untapped signal for GraphRAG-style retrieval**
Obsidian notes have: explicit backlinks, tags, headers, YAML frontmatter. These structural features are more information-rich than raw text chunks for an agent navigating the vault.
Source: [TRAINING ~Aug2025] + [SPECULATION: synthesis]

**[SPECULATION] Optimal architecture for Hermes + Obsidian agent (12-24 month horizon)**
Tier 1 (working memory): current context window — recent notes + active task
Tier 2 (session memory): RAG over last N sessions with local embedding model
Tier 3 (long-term vault): GraphRAG over wikilink graph + semantic embeddings
Tier 4 (structured facts): extracted entity/relationship store (Mem0-style)
All tiers exposed via MCP Resources + Tools to local Hermes instance.

---

## 5. Nous Research Direction

### Claims

**Nous Research has a pattern of fine-tuning frontier base models for instruction and agent use**
Source: [TRAINING ~Aug2025] — Nous Research HuggingFace page

**Hermes series: 2 (2023) → 2 Pro (Mar 2024) → 3 (Aug 2024)**
- Hermes 2 Pro (March 2024): Mistral 7B base, specialized function calling, structured JSON tool use
- Hermes 3 (August 2024): Llama 3.1 base (8B/70B/405B), chatml, improved agentic capabilities
Source: [TRAINING ~Aug2025]

**DisTrO: reduces communication bandwidth for distributed training across internet-connected nodes**
DisTrO (Distributed Training Over-The-Wire) optimizer family dramatically reduces the bandwidth requirements vs. standard DDP/FSDP, making training feasible across high-latency heterogeneous connections.
Source: [TRAINING ~Aug2025] — DisTrO paper, Nous Research 2024

**Psyche: decentralized compute network for training**
Nous Research's infrastructure project. Paired with DisTrO: DisTrO solves communication efficiency; Psyche provides the decentralized participant compute pool.
Source: [TRAINING ~Aug2025] — Nous Research announcements 2024

**[SPECULATION] If Psyche matures, Nous Research could train models outside major cloud provider dependency**
This would enable more aggressive capability releases and faster iteration. The decentralized training thesis also aligns with the privacy-preserving, local-first angle relevant to Obsidian agent use cases.

**[SPECULATION] Hermes 4 likely within 12 months following Llama 4 or successor model release**
Based on historical release cadence (base model → Hermes fine-tune within 2–4 months).

---

## 6. Cross-Cutting Assessment

### Key Signals

**The Hermes + Obsidian + MCP stack is technically viable today**
All components exist and work: Hermes 3 runs locally via Ollama (GGUF) or MLX; MCP is fully standardized with community Obsidian servers; local inference hardware (M3 Max, RTX 4090) supports 70B models quantized.

**The 12–24 month trajectory: capability improves significantly on all axes**
- Better agent-tuned open-weight models (Hermes 4 or equivalent)
- Native reasoning in open-weight models becomes standard
- Consumer hardware pushes 70B to near-real-time (< 20 tokens/sec today; 50+ tokens/sec projected)
- MCP adds streaming, event-driven triggers (vault-change → agent notification), Skills primitive
- Memory architectures mature (GraphRAG + wikilink traversal)

**The unsolved bottleneck is vault structure and memory management quality, not inference capability**
The model, the tooling, and the protocol are converging. The remaining hard problem: how do you structure an Obsidian vault so a local LLM can navigate it reliably at scale? This is a knowledge management design problem, not a technology gap.

---

## Data Gaps

1. WebSearch was blocked — no fresh search results on Nous Research 2025-2026 activities post-training-cutoff.
2. Hermes releases after August 2024 are unknown — verify on HuggingFace directly.
3. DisTrO / Psyche 2025-2026 status unknown — needs targeted search with WebSearch access.
4. Obsidian MCP server ecosystem not directly researched — verify community adoption separately.
5. Quantization advances (ExLlamaV2, llama.cpp updates after Aug 2025) not covered.
6. Hardware specs for M4 Pro/Max/Ultra and RTX 5000 series not directly verified.

---

## Sources

### Primary-Fetched (2026-06-13)
1. https://modelcontextprotocol.io/community/governance.md — Linux Foundation governance
2. https://modelcontextprotocol.io/extensions/client-matrix.md — Client adoption matrix
3. https://modelcontextprotocol.io/specification/2025-11-25/index.md — Spec overview
4. https://modelcontextprotocol.io/development/roadmap.md — MCP roadmap (updated 2026-03-05)
5. https://modelcontextprotocol.io/seps/index.md — 41 Final SEPs with dates
6. https://modelcontextprotocol.io/extensions/tasks/overview.md — Tasks extension
7. https://modelcontextprotocol.io/docs/learn/architecture.md — Architecture
8. https://modelcontextprotocol.io/extensions/overview.md — Extensions system
9. https://modelcontextprotocol.io/community/working-interest-groups.md — WG/IG governance
10. https://modelcontextprotocol.io/specification/2025-11-25/server/tools.md — Tool calling spec
11. https://modelcontextprotocol.io/registry/about.md — MCP Registry
12. https://developer.apple.com/machine-learning/ — Apple Silicon ML frameworks

### Training Knowledge (~Aug 2025 cutoff)
- Nous Research Hermes 2, 2 Pro, 3 release history
- DisTrO paper (Nous Research 2024)
- Psyche decentralized compute network
- llama.cpp GGUF format and quantization
- MLX framework (Apple ML Research, Dec 2023)
- AWQ / GPTQ quantization papers
- MemGPT / Letta (Stanford, Oct 2023)
- Microsoft GraphRAG (2024)
- DeepSeek-R1 (January 2025)
- Llama 3.1 (Meta, July 2024), Qwen 2.5 (Alibaba, Sep 2024)
- Phi-3 Mini (Microsoft, April 2024), Gemma 2 (Google, June 2024)
- Apple Silicon M3 Max/Ultra, M4 generation hardware specs
- NVIDIA RTX 4090, RTX 5000 series
- Ollama, LM Studio local inference tooling

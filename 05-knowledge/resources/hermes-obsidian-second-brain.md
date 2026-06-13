---
title: "Hermes as a Local Second-Brain Agent over Obsidian"
type: resource
category: ai-engineering
status: active
created: 2026-06-13
updated: 2026-06-13
tags: [ai-agents, local-llm, hermes, nous-research, obsidian, second-brain, mcp, agent-memory, rag]
raw_sources:
  - raw/research/2026-06-13-hermes-obsidian-agent/
confidence: medium-high
---

# Hermes as a Local Second-Brain Agent over Obsidian

> **Scope.** Using the Nous Research **Hermes** open-weight model family as the *brain* of a self-hosted agent that uses an **Obsidian** markdown vault as its long-term memory / second brain. Researched 2026-06-13 via 6 parallel research threads + lead verification of primary sources. Related framework context: [[COG Second Brain]], [[HYBRID-SECOND-BRAIN]], [[PARA]].

## TL;DR (headline judgment)

As of mid-2026, running a local Hermes model as an Obsidian second-brain agent has crossed from DIY-plumbing into a **near-turnkey, genuinely viable setup** — but it wins on *privacy/offline/control*, not on raw capability-per-dollar.

1. **The models are ready.** Hermes 4 (Llama-3.1, 14B/70B/405B) and Hermes 4.3 (36B, 512K context) ship native `<tool_call>` function-calling and toggleable `<think>` hybrid reasoning — the two features an agent brain actually needs. [Source: [[hermes-obsidian-second-brain]] §Models | 2026-06-13 | confidence: high]
2. **Nous ships its own agent.** `NousResearch/hermes-agent` is a real, MIT-licensed, **~193k-star** framework with a built-in learning-loop memory and a *bundled Obsidian integration* — the closest thing to a first-party "Hermes + Obsidian second brain." [Source: github.com/NousResearch/hermes-agent | 2026-06-13 | confidence: high]
3. **The plumbing is standardized.** MCP servers + the Obsidian *Local REST API* plugin give any local model full vault read/write; Ollama/vLLM expose OpenAI-compatible tool calling. [Source: [[hermes-obsidian-second-brain]] §Plumbing | 2026-06-13 | confidence: high]
4. **But the contrarian case is strong.** Open models at self-hostable sizes (14B–70B) still trail frontier models on long-horizon agentic reliability; local 70B inference runs ~8–15s per tool call; and "free + private" rarely beats a cheap frontier API for personal token volumes. [Source: [[hermes-obsidian-second-brain]] §Contrarian | 2026-06-13 | confidence: high]
5. **Markdown is winning as the memory *substrate*** (Letta MemFS, memsearch, TencentDB, Manus all converge on "markdown = source of truth, vector/graph = rebuildable cache") — but a flat vault hits real corruption/retrieval/scaling limits past a few hundred agent-written notes, where a dedicated memory layer (Mem0/Zep/Letta) becomes complementary infrastructure. [Source: [[hermes-obsidian-second-brain]] §Memory-frontier | 2026-06-13 | confidence: medium-high]

**Net for a frontier-vault user (e.g. [[COG Second Brain]]):** the local-Hermes path is best read as a *privacy/offline alternative* or a *hybrid* — local Hermes for routine/private vault ops, frontier model for hard reasoning — not a strict upgrade.

---

## 1. What "Hermes as a second-brain brain" means in 2026

Three independent trends converged to make this practical:

- **Capable small open models.** Hermes 4.3 36B runs on a single 24 GB GPU (Q4) and claims rough parity with Hermes 4 70B; the 512K context lets much of a personal vault sit in-context without RAG. [Source: nousresearch.com/introducing-hermes-4-3 | 2026-06-13 | confidence: high]
- **A first-party agent runtime.** Nous shipped **Hermes Agent** (Feb 2026) with a self-improving skill/memory loop, then **Hermes Desktop** (v0.15.2, Jun 2 2026). [Source: github.com/NousResearch/hermes-agent | 2026-06-13 | confidence: high]
- **Standard vault connectivity.** Obsidian crossed **1.5M users (Feb 2026, +22% YoY)**; four MCP server implementations + the Local REST API plugin expose the vault as agent tools. [Source: nxcode.io obsidian guide | 2026 | confidence: medium]

## 2. The models (Hermes as agent brain)

| Model | Base | Sizes | Context | License | Notes |
|---|---|---|---|---|---|
| Hermes 3 | Llama 3.1 | 8B/70B/405B | 128K | Llama 3.1 Community | Introduced `<tool_call>`/`<tool_response>` format |
| DeepHermes 3 Preview | Llama 3(.1) | 3B/8B | ~8K | Llama | First toggleable `<think>` mode |
| **Hermes 4** | Llama 3.1 | 14B/70B/405B | 128K | Llama 3 | Hybrid reasoning; Atropos RL + ~1,000 verifiers |
| **Hermes 4.3** | ByteDance Seed-OSS-36B | 36B | **512K** | Apache-2.0¹ | First Hermes trained fully on Psyche; JSON self-repair |

¹ Hermes 4.3's Apache-2.0 license is reported by secondary sources (the Seed-OSS base is Apache-2.0); the official intro page did not state a license — treat as *likely but unconfirmed*. Hermes 4 (70B) carries the **Llama3** license (commercial self-host OK below 700M MAU). [Source: huggingface.co/NousResearch/Hermes-4-70B | 2026-06-13 | confidence: high]

**Why Hermes suits an agent brain:**
- **Native tool calling** — tool defs in `<tools>` JSON, model emits `<tool_call>{"name","arguments"}</tool_call>`, parallel calls supported, multi-step chains native (`functioncall.py` reference loop). [Source: github.com/NousResearch/Hermes-Function-Calling | 2025 | confidence: high]
- **Hybrid `<think>` reasoning** — lets the model plan *which notes to read/write* before emitting tool calls, reducing redundant reads and circular retrieval on multi-hop vault queries. [Source: huggingface.co/NousResearch/Hermes-4-70B | 2026-06-13 | confidence: high]
- **Steerability / minimal refusals** — system-prompt-controllable behavior without fine-tuning.

**Local hardware (Q4_K_M):** Hermes 4 14B ≈ 8–10 GB (RTX 4070 / M2 Pro 16GB); Hermes 4.3 36B ≈ 20–22 GB (RTX 4090 / Mac Studio 32GB+, but KV cache at 512K pushes total to ~40–60 GB); Hermes 4 70B ≈ 39–40 GB (2× 4090 / M4 Max 128GB). [Source: localllm.in vram guide | 2026 | confidence: medium]

## 3. The plumbing (local LLM → Obsidian vault)

**Inference runtime:** Ollama (easiest, OpenAI-compatible tool calling at v0.5+, lower concurrency) → dev; vLLM (`--enable-auto-tool-choice --tool-call-parser hermes`, PagedAttention) → production concurrency; llama.cpp needs `--jinja` for function calling; **LM Studio does *not* reliably support streaming/parallel tool calls** (prototyping only). [Source: docs.vllm.ai tool_calling; jdhodges.com local-llms-on-tool-calling-2026 | 2025-2026 | confidence: high]

**Vault connection (four routes):**
- **Local REST API plugin** (`coddingtonbear/obsidian-local-rest-api`, localhost:27123) — de-facto standard; full CRUD, surgical patch by heading/block/frontmatter, *built-in MCP server*. [Source: github.com/coddingtonbear/obsidian-local-rest-api | 2025 | confidence: high]
- **MCP servers** — `cyanheads/obsidian-mcp-server` (granular edits via REST), `bitbonsai/mcpvault`, `aaronsb/obsidian-mcp-plugin` (vault-as-knowledge-graph, HTTP transport), `robbiemu/vault-mcp` (semantic RAG + live sync), `devwhodevs/engraph` (Rust, 5-lane hybrid search).
- **Direct filesystem** — simplest; but Obsidian's live index/backlinks lag until rescan.
- **File watchers** (watchdog/chokidar/notify) — event-driven agents.

**The agent loop:** chat template → `<tool_call>` → parse → dispatch Python fn (`read_note`/`write_note`/`search_notes`/`patch_note`…) → `<tool_response>` → repeat until plain response. A **custom Python loop is the most reliable** harness for Hermes specifically; LlamaIndex for RAG; LangGraph for stateful flows; n8n for no-code. Known failure: Hermes emits tool calls as *raw text* if the server isn't configured (`--jinja` / Ollama 0.5+ / vLLM auto-tool-choice). [Source: github.com/NousResearch/hermes-agent/issues/741 | 2025-2026 | confidence: medium]

**Turnkey path (Hermes Agent):** `hermes memory setup --provider obsidian --path ~/vaults/...` wires the agent to read/write named markdown memory files every session; persona/facts/project context as separate notes, history in SQLite. *Note: Obsidian is a bundled skill in the docs, not headlined in the repo README.* [Source: hermes-agent.nousresearch.com/docs (note-taking/obsidian) | 2026 | confidence: medium]

## 4. The landscape

| Tool | Local/open model | True agent (writes/acts)? | OSS | Note |
|---|---|---|---|---|
| **Hermes Agent** (Nous) | yes (any endpoint) | yes (learning loop) | MIT, ~193k★ | First-party; Obsidian via bundled skill |
| **Khoj** | yes (Ollama) | yes | AGPL, ~34k★ | Most feature-complete OSS second brain |
| **SystemSculpt AI** | yes | approaching (vault tools) | yes | Read/search/edit/move + agent mode |
| **Copilot for Obsidian** | yes (Ollama) | no (chat+RAG) | MIT, ~6k★ | Lowest-friction local chat; not an agent |
| **Smart Connections** | yes (on-device embed) | no | MIT, ~5k★ | Best zero-config semantic search |
| **Reor** | yes | no (RAG Q&A) | MIT, ~8k★ | Standalone app, markdown-compatible |
| **MCP route** (REST API + servers) | yes | yes (full CRUD) | OSS | Most flexible plumbing for Hermes |

**Frontier contrast — [[COG Second Brain]] / Claude Code / Cursor:** best-in-class reasoning quality, but cloud-only, paid per token, notes leave the device, no offline. `kepano/obsidian-skills` (by Obsidian's CEO, Jan 2026) teaches frontier agents to drive the vault via CLI + open formats. The local-Hermes value proposition sits exactly opposite: privacy, offline, one-time hardware cost, full control. [Source: github.com/kepano/obsidian-skills | 2026-01 | confidence: medium]

## 5. The memory frontier (does Obsidian survive?)

Dedicated agent-memory frameworks add what a flat vault genuinely cannot: **temporal validity edges** (Zep/Graphiti — `valid_from`/`valid_to`/`invalid_at`), **automatic entity/relationship extraction** (Cognee, GraphRAG, LightRAG), **agent-driven memory evolution** (A-MEM, Letta sleep-time compute), and **multi-session cross-agent dedup** (Mem0). [Source: [[hermes-obsidian-second-brain]] §5 / emerging-memory findings | 2026-06-13 | confidence: medium-high]

But the storage *primitive* is converging on **plain markdown as source of truth, vector/graph as rebuildable cache** — memsearch (Zilliz), memweave, TencentDB Agent Memory (L2 tier), Letta's git-backed MemFS, and Manus's `task_plan.md`/`notes.md` planning pattern all adopt it. A-MEM is literally Zettelkasten-for-agents. [Source: dev.to/imaginex markdown-memory; letta.com/blog/context-repositories | 2026 | confidence: high]

**Verdict: complementary, not obsolete.** Obsidian is the durable, human-readable source/front-end layer; dedicated frameworks are the agent-facing retrieval/index layer on top. For a *single-user local-first* setup (the Hermes case), the gaps frameworks fill — multi-agent coordination, contradiction detection at scale, multi-year temporal reasoning — are largely irrelevant; **Obsidian + LightRAG (e.g. Neural Composer) + an MCP server covers it at zero cloud cost.** Past a few thousand agent-written notes with concurrency, add Mem0/Zep/Graphiti.

## 6. The contrarian case (read this before you build)

- **Capability gap at self-hostable sizes.** AgentBench: best open model 0.96 vs GPT-4 4.01; tau-bench parity for open weights only near ~480B active params — far above Hermes 70B. Multi-turn scores drop 5–10 pts vs single-turn and compound across agentic chains. Nathan Lambert: "Hermes 3 models are not classified as frontier." [Source: arxiv.org/abs/2308.03688; interconnects.ai/p/nous-hermes-3 | 2024-2026 | confidence: high]
- **Tool-call failures.** ~31% of production agent failures trace to tool misuse; documented "self-conditioning bias" (prior tool call → keeps calling tools); live reports of local Llama 3.1 looping without output where Claude API didn't. [Source: trantorinc.com ai-agent-failure-modes; arxiv 2604.06185 | 2025-2026 | confidence: high]
- **Latency & cost.** Local Hermes 70B ≈ **8–15s per tool call** (default Ollama); VRAM overflow collapses to 2–5 t/s. Below ~50M tokens/month, a frontier API wins on cost; self-hosting runs 3–5× the raw GPU price all-in. Frontier APIs already offer contractual no-train opt-outs, matching self-host privacy for personal use. [Source: introl.com hardware guide; devtk.ai self-hosting-vs-api-2026 | 2025-2026 | confidence: high]
- **Markdown-as-memory limits.** Practical ceiling ~200 agent-written static memories / single-user / no concurrency; concurrent writes can silently corrupt files (documented binary corruption in CLAUDE.md-style memory files); keyword-only retrieval; unstructured-vault RAG hallucination 33–35% (vs ~6% curated); wikilink rot on rename; markdown files as prompt-injection vectors ("MemoryGraft"). [Source: mem0.ai your-ai-agents-memory-is-just-a-file; medium RAG-hallucination | 2025-2026 | confidence: high]
- **"Second brain" skepticism.** A recurring critique that most PKM vaults become "digital graveyards" / "productivity theater" — collecting over synthesizing. An AI agent that *writes* into the vault can accelerate either the value or the sprawl. [Source: maketecheasier second-brain-productivity-trap | 2025 | confidence: medium]

## 7. Trajectory (12–24 months)

- **Local inference keeps improving:** Ollama MLX backend (v0.19, Mar 2026), RTX 5090 ~61 t/s at 32B, Snapdragon X Hexagon NPU agent workflows, NVFP4/AWQ quantization retaining 92–97% quality. The runnable-at-home envelope is expanding toward 70B-class reasoning.
- **RL as capability multiplier:** Nous's Atropos (1,200+ envs) already produced a DeepHermes tool-calling specialist with +4.6× parallel-tool-call accuracy at 8B — tool reliability for local agents will improve *independent of model size*.
- **MCP standardization** continues (now Linux-Foundation-governed; async Tasks extension) — the default agent↔vault interface.
- **Decentralized training:** Hermes 4.3 was post-trained entirely on **Psyche** (DisTrO: ~1,000–10,000× bandwidth reduction; $50M Series A from Paradigm at $1B). [SPECULATION] A future Hermes trained at scale on Psyche could decouple model quality from Nous's internal GPU budget — reinforcing the local/private value proposition. [Source: siliconangle nous $50M; github.com/NousResearch/atropos | 2025-2026 | confidence: medium]

## 8. Recommendation

- **If you value privacy/offline/control or like to tinker:** the strongest 2026 stack is **Ollama + Hermes 4.3 36B (or Hermes 4 70B if you have the VRAM) + Hermes Agent + Obsidian via the bundled skill / Local REST API**, with Smart Connections or LightRAG for retrieval. Budget real hardware (24–48 GB VRAM) and expect frontier-minus reasoning.
- **If you want maximum capability per dollar for personal volumes:** a frontier-model agent over the same vault (your [[COG Second Brain]] is exactly this) still wins; consider the local path as a **hybrid** — route private/routine vault ops to local Hermes, hard reasoning to the frontier model.
- **Either way:** keep markdown as the source of truth, treat any vector/graph index as a rebuildable cache, and add a dedicated memory layer (Mem0/Zep) only when you exceed a few thousand agent-written notes or need concurrency.

## Open questions

- Independent (non-self-reported) BFCL/tau-bench numbers for Hermes 4 / 4.3 at 14B–70B — not found; the agentic-reliability gap vs frontier is inferred, not measured for Hermes specifically.
- Exact Hermes 4.3 release date (Aug vs Dec 2025) and confirmed license remain ambiguous in primary sources.
- How robust the Hermes Agent *Obsidian* skill is in practice (it's a bundled skill, not a headline feature) — warrants hands-on testing before committing a real vault.

## Sources

Primary (lead-verified 2026-06-13): github.com/NousResearch/hermes-agent · huggingface.co/NousResearch/Hermes-4-70B · nousresearch.com/introducing-hermes-4-3 · github.com/NousResearch/Hermes-Function-Calling · github.com/coddingtonbear/obsidian-local-rest-api · docs.vllm.ai/en/stable/features/tool_calling · github.com/NousResearch/atropos · nousresearch.com/nous-psyche

Secondary/landscape: github.com/khoj-ai/khoj · github.com/logancyang/obsidian-copilot · github.com/brianpetro/obsidian-smart-connections · github.com/reorproject/reor · github.com/cyanheads/obsidian-mcp-server · github.com/kepano/obsidian-skills · mem0.ai/blog/state-of-ai-agent-memory-2026 · letta.com/blog/context-repositories · arxiv.org/abs/2501.13956 (Zep) · arxiv.org/abs/2502.12110 (A-MEM) · arxiv.org/abs/2308.03688 (AgentBench) · interconnects.ai/p/nous-hermes-3 · spheron.network/blog/tool-calling-benchmarks-bfcl-tau-bench · introl.com/blog/local-llm-hardware-pricing-guide-2025 · devtk.ai self-hosting-llm-vs-api-2026

Full per-claim source lists and the contrarian/emerging-memory evidence are preserved in `raw/research/2026-06-13-hermes-obsidian-agent/` (findings-*.md + factcheck-verdicts.md).

---
*Confidence: medium-high. Core thesis (Hermes 4/4.3 capabilities, Hermes Agent existence + MIT + ~193k stars, MCP/REST plumbing, contrarian limits) verified against primary sources. Specific benchmark figures and the Apache-2.0 license for 4.3 are unconfirmed and flagged inline.*

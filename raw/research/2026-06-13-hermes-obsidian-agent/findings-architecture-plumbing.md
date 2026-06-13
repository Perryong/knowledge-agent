# Architecture / Plumbing: Local Hermes LLM → Obsidian Vault

*Research date: 2026-06-13 | Live web, ~69 sources | reconstructed by lead (subagent file write blocked)*

## 1. Local inference runtimes
- Every Hermes model ships GGUF quants on HF → Ollama, llama.cpp, LM Studio, vLLM, SGLang, LocalAI. [fast.io/resources/hermes-agent-ollama-local-llm | 2026]
- Hermes 3 tool-calling: tool defs as JSON schema inside `<tools>` in system prompt; model emits `<tool_call>{"name","arguments"}</tool_call>`; results returned as `<tool_response>`. [github.com/NousResearch/Hermes-Function-Calling | 2024; arxiv.org/pdf/2408.11857 | 2024]
- Claim: Hermes 3 8B ~91% on Berkeley Function-Calling Leaderboard vs ~78% Mistral 7B Instruct. [markaicode.com/hermes-agent-tool-calling-python-ollama | 2026 | MEDIUM — verify]
- **Ollama**: v0.5+ OpenAI-compatible tool calling at /api/chat and /v1/chat/completions; easiest setup; lower concurrent throughput. [ollama.com/blog/tool-support | 2024; docs.ollama.com/api/openai-compatibility | 2025]
- **llama.cpp (llama-server)**: needs `--jinja` for function calling; natively supports Hermes 2/3 tool format. Max hardware control, CPU-capable, GGUF-only. [github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md | 2025]
- **vLLM**: needs `--enable-auto-tool-choice --tool-call-parser hermes`; PagedAttention → best concurrent throughput; NVIDIA/ROCm; prod multi-agent. [docs.vllm.ai/en/stable/features/tool_calling | 2025]
- **LM Studio**: does NOT support streaming tool calls / parallel invocation; can emit tool calls as raw text; prototyping only. [jdhodges.com/blog/local-llms-on-tool-calling-2026-pt1 | 2026]

## 2. Connecting agents to Obsidian
### MCP servers
- **coddingtonbear/obsidian-local-rest-api** — de-facto standard plugin; full CRUD, surgical patch by heading/block/frontmatter, full-text+JsonLogic search, HTTPS+API key, **built-in MCP server**; default localhost:27123. [github.com/coddingtonbear/obsidian-local-rest-api | 2025]
- Standalone MCP wrappers around the REST API: MarkusPfundstein/mcp-obsidian, punkpeye/mcp-obsidian, cyanheads/obsidian-mcp-server (granular edits), j-shelfwood/obsidian-local-rest-api-mcp, OleksandrKucherenko (Bun), PublikPrinciple/obsidian-mcp-rest. [2024-2025]
- **robbiemu/vault-mcp** — multi-source semantic RAG MCP (Obsidian/Joplin/markdown), live sync, quality chunk filtering. [github.com/robbiemu/vault-mcp | 2025]
- **devwhodevs/engraph** — Rust KG + 5-lane hybrid search (semantic+BM25+graph+cross-encoder+temporal via RRF) + 26-endpoint REST; wikilink traversal, community detection; fully offline. [github.com/devwhodevs/engraph | 2025]
- **maxkuminov/obsidian-mcp** — pgvector + Ollama, self-hosted RAG. [glama.ai/mcp/servers/maxkuminov/obsidian-mcp | 2025]
- **sweir1/obsidian-brain** — no plugin; direct-filesystem MCP, semantic search + KG + editing. [github.com/sweir1/obsidian-brain | 2025]
- **takeshy/obsidian-local-llm-hub** — all-in-one plugin: LLM chat + vault tools (read/create/update/rename/search/list/propose_edit/execute_javascript) + MCP + RAG, all local. [github.com/takeshy/obsidian-local-llm-hub | 2025]

### Direct filesystem / file-watchers
- Vault = folder of .md; pathlib/os read-write directly, but Obsidian live index/backlinks lag until rescan. [github.com/kytmanov/obsidian-llm-wiki-local | 2025]
- Karpathy-pattern wiki tools drop md directly (kytmanov/obsidian-llm-wiki-local, nashsu/llm_wiki, Ar9av/obsidian-wiki).
- File watchers: watchdog (Py), chokidar (Node), notify (Rust) → event-driven agents.

| Method | Live index | Auth | Tool-friendly | Plugin | Best for |
|---|---|---|---|---|---|
| REST API (coddingtonbear) | instant | API key | yes | yes | full CRUD, surgical edits |
| MCP wrapper (REST) | via REST | API key | yes | yes | MCP agent frameworks |
| MCP (filesystem) | no | none | yes | no | lightweight, read-heavy |
| Direct FS | delayed | none | yes | no | batch writes |
| File watcher | reactive | none | trigger | no | event-driven RAG |

## 3. RAG over a markdown vault
- **Smart Connections**: TransformersJS (ONNX/WASM), all-MiniLM-L6-v2 (~25MB), zero-config, offline; Smart Chat = embed→top-k→synthesize. [github.com/brianpetro/obsidian-smart-connections | 2025]
- Chunking: heading-aware ~512 tokens, preserve code blocks, carry heading path. [dasroot.net/.../obsidian-integration | 2025]
- Wikilink graph exploitable: shortest-path, neighborhood queries, community detection (engraph, obra/knowledge-graph).
- Flat embedding RAG ignores link graph; hybrid (engraph 5-lane RRF) outperforms; agentic wikilink-traversal harness beat vector-RAG on 99-note eval (+faithfulness/grounding/insight). [github.com/devwhodevs/engraph | 2025; dev.to/nickyeolk | 2025]
- Local vector stores: Qdrant, pgvector, DuckDB (MotherDuck pattern), SQLite, FAISS. Embeddings: all-MiniLM-L6-v2, nomic-embed-text via Ollama.
- Alt to runtime RAG: **Karpathy LLM Wiki pattern** — local LLM compiles/interlinks a wiki at ingest; no vector DB at runtime; plain markdown; later sources more useful via cross-linking. [mindstudio.ai/blog/andrej-karpathy-llm-wiki-obsidian | 2025]

## 4. Agent loop (Hermes tool calls → vault ops)
- Loop: chat template → generate `<tool_call>` → parse XML/JSON → dispatch Python fn → vault op → format `<tool_response>` → append → repeat until plain `<response>`. LLM stateless; Python holds state. [markaicode | 2026; NousResearch/Hermes-Function-Calling | 2024]
- Reference impl: NousResearch/Hermes-Function-Calling `functioncall.py` (default Hermes-2-Pro-Llama-3-8B).
- Vault tools: read_note, write_note, append_note, search_notes, list_notes, get_active_note, create_note, patch_note.
- **Known bug**: Hermes outputs tool calls as raw text if server not configured (`--jinja` / Ollama 0.5+ / vLLM auto-tool-choice). Cited as GitHub issue #741 on **NousResearch/hermes-agent** — corroborates existence of the Hermes Agent product. [github.com/NousResearch/hermes-agent/issues/741 | 2025-2026 | VERIFY repo directly]

## 5. Orchestration
- **LangChain/LangGraph** 0.3.x; LangGraph = stateful graph orchestration; Ollama via langchain-ollama; wrap REST API as Tools.
- **LlamaIndex** — RAG-heavy vault pipelines; has Obsidian reader.
- **n8n** v2.15+ visual AI Agent node (LangChain JS), self-hosted kits, Obsidian via webhooks/REST; risk of unmaintainable flows.
- **Custom Python loop** — most reliable for Hermes specifically (direct `<tool_call>` parsing, retries, async timeouts).
- Hybrid 2026: LlamaIndex (RAG) + custom loop (Hermes dispatch) + LangSmith (tracing).

## 6. Reference setups / tutorials
- **itechmeat/open-second-brain** — local-first Hermes Agent + Obsidian memory; interactions as .md under Brain/; MCP stdio; CLI `o2b`; nightly "dream pass" preference distillation; adapters for Claude Code/Codex/OpenClaw; plain markdown + MCP, no hidden vectors. [github.com/itechmeat/open-second-brain | 2025-2026]
- **Hermes Agent v0.14 + Obsidian** — `hermes memory setup --provider obsidian --path ~/vaults/work`; agent reads/writes named md every run. [gptaiclips.hashnode.dev/.../hermes-v0-14-obsidian | 2026; dev.to/gptaiclips | 2026]
- **takeshy/obsidian-local-llm-hub** — install from community plugins, configure Ollama, nomic-embed-text for RAG.
- **kytmanov/obsidian-llm-wiki-local** — Karpathy wiki, 100% local.
- markaicode Hermes+Ollama Python guide. Hermes Agent official docs: hermes-agent.nousresearch.com/docs/reference/faq.

## Recommended stack (synthesis)
Ollama (dev)/vLLM (prod) · Hermes 3 8B/70B GGUF · coddingtonbear REST API + MCP wrapper · Smart Connections or engraph RAG · Qdrant/DuckDB · custom Python or LlamaIndex+dispatch agent loop · LangGraph or bare Python · memory via itechmeat/open-second-brain or direct vault writes.

## Conflicting / verify
- LM Studio tool calling: vendor claims vs independent 2026 reports (streaming/parallel NOT working).
- Ollama tool support: pre-0.5 manual XML parsing vs 0.5+ native. Gate at 0.5+.
- "91% BFCL" for Hermes 3 8B — single medium-confidence source; verify against thread-1 (model family).
- Hermes Agent product (NousResearch/hermes-agent) — corroborated by issue #741 + multiple tutorials; still verify the actual repo + nousresearch.com.

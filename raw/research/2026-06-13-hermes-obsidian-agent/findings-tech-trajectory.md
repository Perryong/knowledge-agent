# Technology Trajectory: Hermes + Obsidian Agent (12-24mo)

*Research date: 2026-06-13 | Live web, ~56 sources | reconstructed by lead (subagent file write blocked). MCP governance facts captured in earlier tech-trajectory pass (Linux Foundation, ~41 Final SEPs to Apr 2026, Tasks extension, Sampling-with-Tools).*

## 1. Open-weight model progress (agent-relevant)
- DeepHermes ToolCalling Specialist (Atropos): +4.6x parallel tool calls (10%→46%), +2.5x simple (21%→51.75%) on BFCL at 8B. [HF NousResearch | 2025-04]
- Qwen3 = "default for local tool-calling reliability mid-2026"; BFCL v4 Qwen3.5 27B 68.5%, 9B 66.1%. [xda-developers | 2026]
- Long context: Hermes 4.3 36B 512K; Qwen3 256K→1M; QwenLong-L1.5 memory beyond physical window. [nousresearch.com/introducing-hermes-4-3; github.com/QwenLM/Qwen3]
- Hermes 4.3 benchmarks: MATH-500 93.8%, MMLU 87.7%, BBH 86.4%, AIME24 71.9%, GPQA Diamond 65.5%; ≈Hermes 4 70B at half size. [nousresearch.com/introducing-hermes-4-3]
- Small-capable-local: NousCoder-14B (Jan 2026, Qwen3-14B base, Atropos RL) LiveCodeBench v6 67.87%; Phi-4 14B; Gemma 4 31B single-GPU agentic; Qwen3 Apache 2.0.

## 2. Local inference trajectory (2026)
- Apple/MLX: Ollama v0.19 (Mar 30 2026) MLX backend; M5 Max 35B NVFP4 prefill 1,810 tok/s decode 112 tok/s; M2/M3 Ultra up to 192GB unified (fits 70B). MLX highest sustained throughput on Apple Silicon (arXiv 2511.05502).
- RTX 5090 (32GB GDDR7): ~213 tok/s 8B, ~61 tok/s 32B; FP8 native Blackwell; TensorRT-LLM ~2x; AWQ+Marlin 741 tok/s.
- NPU: Snapdragon X Hexagon 45→80 TOPS; Nexa AI full agent workflows local on Snapdragon X (Mar 2026); AnythingLLM/GPT4All ported.
- Quantization retention: AWQ 95%, GGUF Q4_K_M 92%, GPTQ 90%; 4-bit keeps 97.3% MMLU at 3.8x mem cut. 2026 rec: Q4_K_M (CPU), AWQ INT4 (GPU reasoning), NVFP4 (Blackwell/M5).

## 3. MCP adoption for Obsidian
- Four Obsidian MCP servers: MCPVault (bitbonsai), obsidian-mcp-plugin (aaronsb, HTTP transport, vault-as-KG), obsidian-mcp-plugin (jlevere), MCP Tools plugin.
- Obsidian crossed **1.5M users Feb 2026, +22% YoY**. [nxcode.io | 2026]
- Karpathy "LLM Knowledge Base" gist (early 2026) catalyzed Markdown-first-for-LLM trend.
- obsidian-second-brain (eugeniughelbur) v0.10 May 2026: /obsidian-architect writes architecture notes; Claude Code/Codex/Gemini/OpenCode.
- Local private stack documented: Hermes via Ollama/LM Studio + vault via MCP = no data leaves machine.

## 4. Agent memory architecture trends
- Three approaches: long-context, RAG, **MAG (Memory-Augmented Generation)** — field shifting to MAG for persistent agents. [mem0.ai/blog/state-of-ai-agent-memory-2026; arxiv 2603.07670]
- A-MEM Zettelkasten ≈ Obsidian note graph. MAGMA (arXiv 2601.03236) multi-graph memory. AMA-Bench (arXiv 2602.22769) long-horizon memory benchmark.
- **Manus** (acquired by Meta Dec 2025): file-based planning (task_plan.md + notes.md + deliverable) — validated plain Markdown as production agent memory. [$2B price UNVERIFIED]
- Hermes Agent: stores reusable reasoning patterns as Markdown skill files; pulls relevant skill instead of re-reasoning.
- Vault-for-LLM (zycaskevin): tiered L0-L3 memory, SQLite+ONNX, no cloud. memsearch (Zilliz). SwarmVault (Karpathy-pattern, Obsidian alt). Hierarchical Memory Orchestration (arXiv 2604.01670).

## 5. Nous Research direction
- **Psyche**: decentralized training on Solana; Dec 2024 testnet trained 15B over 11k steps; Apr 2025 $50M Series A led by Paradigm at $1B val. [gate.com; siliconangle]
- **DisTrO**: 1,000x-10,000x bandwidth reduction vs NCCL all-reduce (builds on DeMo).
- Hermes 4.3 36B = first Hermes post-trained entirely on Psyche.
- **Atropos**: released Apr 2025, v0.3.0, 1,200+ task environments; >90% Nous training data synthetic (DataForge+Atropos); integrates Axolotl + Tinker. Hermes 4.3 post-train ~5M samples / ~60B tokens (~50x Hermes 4).
- **Hermes Agent**: released Feb 2026, OSS (MIT), self-hosted, Linux/macOS/WSL2, single curl install; Desktop v0.15.2 Jun 2 2026; `execute_code` collapses pipelines; Nous Portal tools (search/browse/vision/image/TTS). [hermes-agent.org/about; hermes-agent.nousresearch.com/docs]
- NousCoder-14B = strategy signal: Atropos RL on strong open base → specialized open-weight + full training stack.

## Synthesis notes
- Hermes 4.3 36B runnable at home 2026 (RTX 5090 Q4 ~61 tok/s; M3 Max/M2 Ultra Q5/Q6); 512K ctx = much vault content in-context without RAG.
- Skill files = vault-native memory (markdown, searchable/linkable/diffable).
- MCP closes connectivity gap; local Hermes + Obsidian MCP = private zero-cloud read/write.
- RL is capability multiplier (DeepHermes ToolCalling +4.6x parallel at 8B).
- [SPECULATION] Hermes 5 (~H2 2026) likely trained fully on Psyche at scale w/ Atropos from start; decentralized compute could decouple model quality from Nous GPU budget.

## Conflicts/verify
- Hermes 4.3 date Aug 25 vs Dec 2 2025 (nousresearch.com/introducing-hermes-4-3 implies Aug; X post Dec 2). VERIFY.
- Hermes Agent star count 22K vs 175K across threads. VERIFY.
- Manus $2B acquisition price unverified.

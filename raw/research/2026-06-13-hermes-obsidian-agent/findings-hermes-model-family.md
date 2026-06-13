# Hermes Model Family as Agent Brain

*Research date: 2026-06-13 | Live web (WebSearch excerpts) | reconstructed by lead (subagent file write blocked)*

## A. Lineage
- **Hermes 3** (Aug 2024): Llama 3.1 8B/70B/405B(+FP8); ~390M synthetic tokens; 128K ctx; ChatML; introduced `<tool_call>`/`<tool_response>` XML+JSON FC. [arxiv.org/pdf/2408.11857 | 2024-08]
- **DeepHermes 3 Preview** (Feb 15 2025): Llama 3 8B (+3B); first toggleable `<think>` reasoning + standard response in one model. [marktechpost | 2025-02-15]
- **DeepHermes ToolCalling Specialist (Atropos)**: RL-tuned DeepHermes 3 Llama-3.1-8B optimized for tool-calls in reasoning mode. [HF NousResearch | 2025]
- **Hermes 4** (Aug 26 2025): Llama 3.1, 14B/70B/405B(+FP8); hybrid reasoning `<think>`; Atropos RL + ~1000 verifiers; ~1.2B token post-train; 128K ctx; minimal refusals. [HF NousResearch/Hermes-4-70B; marktechpost | 2025-08-27]
- **Hermes 4.3 36B** (Dec 2 2025): ByteDance Seed-OSS-36B base; **512K ctx**; ~60B token post-train; ≈Hermes 4 70B at half params; first Hermes trained fully on **Psyche** decentralized net (DisTrO); JSON self-repair; **Apache 2.0**. [x.com/NousResearch/status/1996311677009121367 | 2025-12-02]
- As of mid-2026: Hermes 4.3 36B is latest base model; no Hermes 5/4.5; 2026 focus = Hermes Agent platform. [petronellatech | 2026 | MEDIUM]

## B. Tool/function calling
- Schema: tool defs in `<tools>` JSON array (OpenAI-compatible); call `<tool_call>{"name","arguments"}</tool_call>`; result `<tool_response>`. [github.com/NousResearch/Hermes-Function-Calling | 2025]
- Parallel calls supported (multiple `<tool_call>` per turn); Hermes Agent defaults 3 concurrent subagents (delegation.max_concurrent_children). [hermes-agent docs | 2026]
- Multi-step chains native (functioncall.py loop). Steerable via system prompt; minimal refusals. Hermes 4.3 schema-faithful JSON + self-repair. vLLM `hermes` tool-call-parser.

## C. Hybrid reasoning `<think>`
- Origin DeepHermes 3 (Feb 2025); `<think>...</think>` before response, toggle via system prompt, disable for low latency.
- Agent relevance: plans which notes to read/write before emitting tool calls → avoids redundant reads / circular retrieval on multi-hop vault queries. Hermes 4 makes think first-class via Atropos RL over ~1000 verifiers.

## D. Context / licensing / distribution
| Model | Base | Context |
|---|---|---|
| Hermes 3 8B/70B/405B | Llama 3.1 | 128K |
| DeepHermes 3 Preview 8B | Llama 3 | ~8K |
| Hermes 4 14B/70B/405B | Llama 3.1 | 128K |
| Hermes 4.3 36B | Seed-OSS-36B | 512K |
- Licensing: Hermes 3 & 4 = Llama 3.1 Community License (commercial self-host OK; no competing-foundation-model training on outputs; >700M MAU needs Meta license). Hermes 4.3 36B = **Apache 2.0** (cleanest). [HF Hermes-4-405B README; tokenring | 2025]
- Distribution: HF NousResearch/Hermes-4-* and 4.3-36B(-GGUF); GGUF quants (bartowski, mradermacher, MaziyarPanahi); LM Studio hub; Ollama community builds (steelpuddles/hermes-4.3-36B); OpenRouter (DeepHermes cloud).

## E. Benchmarks (tool use / FC)
- Hermes-2-Pro-Mistral-7B added to BFCL Apr 2024. **No confirmed BFCL v4 numeric score for Hermes 4/4.3 found — VERIFY at gorilla.cs.berkeley.edu/leaderboard.html.**
- BFCL v4 Jun 2026 leaders (positioning): Qwen3.7 Max 0.750; Qwen3.5-397B-A17B 72.9%. Formula: Agentic 40% + Multi-Turn 30% + Live 10% + Non-Live 10% + Hallucination 10%.
- ~3-4pt frontier-vs-open gap on BFCL v4; Qwen2.5-72B / DeepSeek V3 primary open self-host benchmarks.
- Hermes 4 self-reported SOTA-among-open on ARC/BoolQ/HellaSwag/IFEval/Winogrande; 4.3 36B ≈ 4 70B (Nous claim, not independently verified). [marktechpost | 2025-08-27 | self-reported]

## F. Hermes Agent platform [CORROBORATED across 3 threads; star count DISPUTED]
- **Hermes Agent** launched Feb 2026, OSS by Nous, github.com/NousResearch/hermes-agent.
  - ⚠️ STAR COUNT CONFLICT: this thread says "175,000+ stars in <4 months"; players thread said "~22,000". MUST verify on GitHub directly. (175K in 4mo would be implausibly high; treat both as unverified.)
- Obsidian integration (v0.14, May 16 2026): `hermes memory setup --provider obsidian --path ~/vaults/work`; reads/writes named md every session; persona/facts/project context as separate md; history in SQLite. [dev.to/gptaiclips | 2026-05; hermes-agent.nousresearch.com/docs/.../note-taking-obsidian]
- Paths: (1) Obsidian Local REST API plugin localhost:27123; (2) Obsidian MCP server. Both work with local Hermes via Ollama/llama.cpp.
- LLM backend: any provider incl. local via Ollama; local+Obsidian a core documented use case.
- Hermes Desktop v0.15.2 (Jun 2 2026) native GUI; Hermes Agent v0.16.0 "Surface Release" (Jun 5 2026) current.

## G. Local hardware (quantized Q4_K_M)
| Model | VRAM | Hardware |
|---|---|---|
| Hermes 4 14B | ~8-10 GB | RTX 4070 12GB, M2 Pro 16GB |
| Hermes 4.3 36B | ~20-22 GB | RTX 4090 24GB, Mac Studio 32GB+ |
| Hermes 4 70B | ~39-40 GB | 2×RTX 4090, M4 Max 128GB |
| Hermes 4 405B | 200GB+ | multi-GPU / H100 |
- 4.3 36B at 512K ctx: model+KV ≈ 40-60GB depending on KV precision.

## H. Training infra
- **Atropos** (github.com/NousResearch/atropos): OSS RL env, Axolotl integration, ~1000 verifiers in Hermes 4.
- **Psyche**: decentralized training, Solana-secured, DisTrO bandwidth reduction; Hermes 4.3 first trained fully on it; $50M Series A (Paradigm, Apr 2025, $1B val); Dec 2024 testnet trained 15B over 11k steps globally. [siliconangle | 2025-04-25]

## Conflicts / uncertainties
1. Hermes 4.3 date: Aug 25 vs Dec 2 2025 → use **Dec 2 2025**.
2. Hermes 4 14B date: Jan 2025 vs Aug 26 2025 → use **Aug 26 2025**.
3. BFCL scores for Hermes 4/4.3: none confirmed — VERIFY.
4. **Hermes Agent star count: 22K vs 175K — VERIFY on GitHub.**
5. DeepHermes 3 base: Llama 3 vs 3.1.

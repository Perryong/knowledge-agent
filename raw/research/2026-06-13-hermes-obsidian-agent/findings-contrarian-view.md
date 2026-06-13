# Contrarian / Skeptical Case: Hermes + Obsidian Vault Agent

*Research date: 2026-06-13 | Live web, ~35 sources | reconstructed by lead (subagent file write blocked)*

## 1. Agentic benchmark gap: open 70B vs frontier
- AgentBench (ICLR 2024): GPT-4 4.01, Claude-2 2.49, GPT-3.5 2.32; best OSS CodeLlama-34B 0.96 (~4x below GPT-4); open models ≤70B near-zero on DCG/WebBrowsing. [arxiv.org/abs/2308.03688]
- tau-bench (2026): Claude Sonnet 4.0 80.5/60.0 (Retail/Airline); open-weight parity only near 480B active (Qwen3-Coder-480A35B) — far above Hermes 70B. [spheron.network/blog/tool-calling-benchmarks-bfcl-tau-bench | 2026]
- BFCL v4: 3-4pt headline gap applies only to largest open models (72B+); multi-turn drops 5-10pts vs single-turn, compounding in chains.
- Qualifier: gap narrowing for top 70B+; Hermes 4 70B hybrid reasoning may close sub-gaps; remains significant on long-horizon chains.

## 2. Tool-calling failures / loop breakdowns
- 31% of production agent failures = tool misuse / wrong args. [trantorinc.com/blog/ai-agent-failure-modes | 2025]
- Agents hallucinate files, insert fake data → wrong answers. [arxiv.org/pdf/2512.07497 | 2025-12]
- Multi-agent: small hallucinations compound as next agent's input. [huggingface.co/blog/Musamolla/multi-agent-llm-systems-failure]
- Live case: local Llama 3.1 looped calling tools w/o output; Claude API fixed it. [github.com/openai/openai-agents-python/issues/1544]
- Self-conditioning bias: prior tool call → keeps calling tools. [arxiv.org/html/2604.06185 | 2026-04]
- ReliabilityBench: frontier 96.9%→88.1% pass@1 under perturbation (-8.8%); smaller open models worse. [arxiv.org/pdf/2601.06112 | 2026-01]

## 3. Hermes specifically not frontier at self-hostable sizes
- Nathan Lambert: "Hermes 3 models are not classified as frontier." [interconnects.ai/p/nous-hermes-3]
- Hermes 4 70B = "frontier hybrid reasoning" per Nous, but 14B shows meaningful gaps vs frontier. [Hermes_4_Technical_Report.pdf | 2025-08]
- Hermes 4 14B reasoning frequently exceeded 40,960 tokens — burns context on CoT, leaving little for tool history + vault context in agent loops.

## 4. Long-context coherence degradation
- ICLR 2025: plans deviate as task progresses in 32K settings. [proceedings.iclr.cc/.../2025]
- Effective context window << architectural window for complex reasoning. [emergentmind.com/topics/context-degradation]
- Lost-in-the-middle: 10-20+ pt accuracy drop when relevant content mid-context; GPT-3.5 >20% worst case. [redis.io/blog/rag-vs-large-context-window]

## 5. Self-hosting cost reality
- Hermes 70B needs 48+ GB VRAM. RTX 5090 ~$2-2.5K; dual-GPU $5-8K; Mac Studio M4 Ultra $8-15K+. VRAM overflow → 2-5 t/s ("too slow for production agent loops"). [introl.com/blog/local-llm-hardware-pricing-guide-2025]
- Speed: local Ollama Hermes 3 70B = 8-15s per tool call default; ~33 t/s optimal high-end GPU; Mac Studio quantized 2-5 t/s. [artificialanalysis.ai/models/hermes-3-llama-3-1-70b; markaicode.com/optimize-hermes-agent-performance]
- Break-even: below 50M tokens/mo API wins; self-host 3-5x raw GPU rental once all-in; personal break-even ~200-250K req/mo; "free" OSS can cost $500K+/yr in eng time at scale. [devtk.ai/.../self-hosting-llm-vs-api-cost-2026; sitepoint.com/self-hosted-llm-costs-2026]
- Dual-H100 amortized ~$900-1,200/mo pre power/colo; ongoing model/quant/runtime maintenance. [alpacked.io/blog/self-hosted-llm-guide]
- Frontier API privacy already available: Claude API / Azure OpenAI contractual no-train opt-outs match self-host privacy for personal use. [marka-development.com/.../2026]

## 6. Markdown vault as agent memory: structural failures
- Files work ~200 static memories, single user, no concurrency; past that you rebuild DBs by hand badly; 2,000-note vault takes seconds to walk every startup. [dev.to/.../why-a-single-markdown-file-cant-be-your-ai-agents-memory; me-techtech.com/ai-agent-memory-why-markdown-files-fail-at-scale]
- No transactions: concurrent writes silently corrupt; live case = CLAUDE.md corrupted w/ binary/hex after concurrent writes; file locking fragile/platform-dependent. [mem0.ai/blog/your-ai-agents-memory-is-just-a-file; blogs.oracle.com/developers/...]
- Retrieval: pure markdown = keyword only; RAG over unstructured note vaults hallucinates 33-35%, drops ~6% with curated KB; embedding "nearby" ≠ factually relevant. [medium.com/.../why-your-rag-pipeline-hallucinates]
- Link rot / schema drift: wikilinks break on rename; agent-written links unvalidated → silent dead links; communities add SQLite+vector, defeating "plain text" premise. [groundy.com/articles/inside-rowboats-knowledge-graph]
- MemoryGraft attack: markdown/README as injection vectors planting fake "successful experiences"; local file-write = prompt-injection-to-filesystem surface. [bigid.com/blog/ai-instruction-file-security-markdown-risk]

## 7. Second-brain = productivity theater (moderate)
- PKMs as "productivity theater"/"time sinks"; Obsidian "likely a productivity trap." [maketecheasier.com/second-brain-productivity-trap | 2025]
- Collecting ≠ understanding; hoarding without synthesis. [medium.com/@ann_p/your-second-brain-is-broken]
- Outsourcing reflection; value was in the discipline of writing. [turbulencegains.com/second-brain]
- Maintenance becomes a second job; graph fills but connections unused. [medium.com/@danielasgharian/...]
- "Most Obsidian vaults are digital graveyards."

## 8. Privacy/security counterpoints
- Model-weight supply chain (OWASP LLM Top 10 2025): tainted data → hidden backdoors; open HF weights documented vector; 2025 expanded to full "Model Poisoning." [genai.owasp.org/llmrisk/llm032025-supply-chain]
- Local agent blast radius: vault + OS write access + prompt injection; agents handed schemas/creds/tokens. [bigid.com/blog/ai-instruction-file-security-markdown-risk]

## Summary table
| Weakness | Strength | Key data |
|---|---|---|
| Agentic gap 70B vs frontier | Strong | AgentBench OSS 0.96 vs GPT-4 4.01 |
| Tool-calling loop failures | Strong | 31% prod failures; self-conditioning |
| Local latency 2-15 t/s vs cloud 100+ | Strong | Hermes 70B 8-15s/tool call |
| Self-host break-even unreachable (personal) | Strong | <50M tok/mo API wins; 3-5x hidden |
| Markdown corruption in prod | Strong | binary corruption in CLAUDE.md |
| Markdown ~200-note ceiling | Strong | eng consensus |
| Long-context coherence drop | Strong | 10-20% accuracy; effective<<arch |
| Second brain theater | Moderate | consistent PKM critics |
| Weight supply-chain poisoning | Moderate | OWASP 2025; low observed rate |

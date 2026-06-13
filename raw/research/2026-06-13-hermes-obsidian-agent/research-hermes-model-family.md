# Hermes Model Family Research
# Thread: Nous Research Hermes as agent brain
# Researcher: worker-researcher (claude-sonnet-4-6)
# Date: 2026-06-13
# CRITICAL NOTE: WebSearch and WebFetch were both permission-denied in this environment.
# All findings below are from model training knowledge (cutoff August 2025).
# Staleness risk is HIGH for anything in the 12 months before today (June 2026).
# Live verification is REQUIRED before writing to durable vault notes.

---

## Web Tool Status

- WebSearch: DENIED (permission error — tool blocked in this session)
- WebFetch: DENIED (permission error — tool blocked in this session)
- Result: Zero live-fetched primary sources available. All claims are training-knowledge only.

---

## Claims

### Lineage and Base Models

- **Hermes 2 series** (late 2023 – early 2024): Fine-tuned on Mistral 7B, Yi 34B, Solar 10.7B, and Llama 2 variants. Focus: GPT-4-level instruction following from smaller open-weight bases.
  [Source: HuggingFace NousResearch org page — https://huggingface.co/NousResearch | training knowledge, ~2024 | confidence: high]

- **Hermes 2 Pro series** (2024): Introduced OpenAI-compatible function/tool calling. Built on Mistral 7B and Llama 3 8B (and possibly 70B).
  [Source: https://huggingface.co/NousResearch/Hermes-2-Pro-Llama-3-8B | training knowledge, 2024 | confidence: high]

- **Hermes 3 series** (August 2024): Built on Meta Llama 3.1 in 8B, 70B, and 405B sizes. Major generational upgrade with enhanced agentic capabilities.
  [Source: https://nousresearch.com/hermes3/ | training knowledge, August 2024 | confidence: high — verify live for accuracy]

- **Hermes 4**: No confirmed release found in training data as of August 2025 cutoff. Status unknown after that date — requires live verification.
  [Source: training knowledge | confidence: low — stale]

### Context Windows

- Hermes 2 Pro (Mistral 7B base): 32,768 tokens
  [Source: https://huggingface.co/NousResearch/Hermes-2-Pro-Mistral-7B | training knowledge | confidence: high]

- Hermes 2 Pro (Llama 3 8B base): 8,192 tokens (Llama 3 base limit)
  [Source: training knowledge | confidence: high]

- Hermes 3 (all sizes — 8B, 70B, 405B): 128,000 tokens (inherits Llama 3.1 native context)
  [Source: https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B | training knowledge, 2024 | confidence: high]

### Tool/Function Calling and Agent Capabilities

- Hermes 2 Pro introduced an OpenAI-compatible function-calling format using `<tool_call>` and `<tool_response>` XML-style wrapper tags around JSON payloads.
  [Source: https://huggingface.co/NousResearch/Hermes-2-Pro-Mistral-7B | training knowledge | confidence: high]

- Hermes 3 supports parallel function calls (multiple tools in a single response turn) and sequential tool invocation for multi-step agentic loops.
  [Source: https://nousresearch.com/hermes3/ | training knowledge, August 2024 | confidence: high]

- Hermes 3 has a native JSON/structured output mode for schema-constrained generation (JSON mode).
  [Source: training knowledge based on model card details | confidence: medium]

- Nous Research trained Hermes models with explicit multi-turn agentic loop behavior — the models are designed to call tools, receive results, and reason further before producing final answers.
  [Source: training knowledge | confidence: high]

- System-prompt steerability is a core Nous design principle: Hermes models follow complex, long, detailed system prompts reliably.
  [Source: training knowledge / Nous Research blog posts | confidence: high]

- Alignment stance: Nous describes Hermes models as "less restricted" than Meta's own Llama Instruct variants — fewer refusals on edge-case topics. Marketed as suitable for role-play, persona agents, and custom-aligned deployments.
  [Source: NousResearch HuggingFace model cards | training knowledge | confidence: high]

- Hermes 3 includes support for `<reasoning>` tags (chain-of-thought scratchpad) in some configurations, enabling explicit reasoning traces.
  [Source: training knowledge | confidence: medium]

### Licensing

- Hermes 2 (Mistral base): Apache 2.0 — fully permissive commercial use.
  [Source: https://huggingface.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO | training knowledge | confidence: high]

- Hermes 2 (Yi base): Yi License — restricts commercial use; requires review.
  [Source: training knowledge | confidence: medium]

- Hermes 2 Pro (Llama 3 base): Meta Llama 3 Community License. Commercial use permitted for organizations with fewer than 700M monthly active users. Large-scale commercial use requires separate agreement with Meta.
  [Source: Meta Llama 3 license: https://llama.meta.com/llama3/license/ | training knowledge | confidence: high]

- Hermes 3 (Llama 3.1 base, all sizes): Meta Llama 3.1 Community License. Same 700M MAU threshold. Permits self-hosted deployment.
  [Source: Meta Llama 3.1 license | training knowledge | confidence: high]

- Self-hosting is explicitly permitted under the Llama 3.1 Community License for qualifying organizations.
  [Source: Meta Llama 3.1 Community License | training knowledge | confidence: high]

### Distribution / Where to Get Weights

- Primary: HuggingFace org https://huggingface.co/NousResearch — all official weights
- GGUF quantized versions: Available from community quantizers (bartowski, TheBloke) on HuggingFace; standard formats Q4_K_M, Q5_K_M, Q8_0
- Ollama registry: `ollama run hermes3` runs the 8B variant by default
- LM Studio: Searchable in its built-in model library
- llama.cpp compatible: Yes, native GGUF support
  [Source: training knowledge / HuggingFace, Ollama docs | confidence: high]

### Benchmark Standing

- Hermes 2 Pro (Llama 3 8B) appeared in top-tier open-weight positions on the Berkeley Function Calling Leaderboard (BFCL) circa mid-2024, competing with larger models.
  [Source: https://gorilla.cs.berkeley.edu/leaderboard.html — LIVE VERIFICATION REQUIRED | training knowledge, 2024 | confidence: medium — leaderboard changes rapidly]

- Hermes 3 70B: Nous Research claimed it matched or exceeded Meta's own Llama 3.1 70B Instruct on several instruction-following and reasoning evals at release.
  [Source: https://nousresearch.com/hermes3/ | training knowledge, August 2024 | confidence: medium — requires verification]

- Hermes 3 405B: Positioned by Nous as frontier open-weight, near GPT-4o performance class on some benchmarks at release time (August 2024).
  [Source: https://nousresearch.com/hermes3/ | training knowledge, August 2024 | confidence: medium]

- Competing models in same space (for context): Qwen 2.5 series (Alibaba), Llama 3.1 Instruct (Meta), DeepSeek-V2/V3 (DeepSeek), Mistral variants. Relative standing has shifted since August 2024 — full benchmark comparison requires live BFCL and AgentBench data.
  [Source: training knowledge | confidence: medium]

### Hardware Requirements (Practical Local Deployment)

- **8B (Q4_K_M GGUF)**: ~4.7 GB file / ~5–6 GB VRAM. Runs on RTX 3080 10GB, RTX 4070 12GB, or Apple M2 Pro (18GB unified). Consumer-grade accessible.
  [Source: training knowledge / llama.cpp benchmarks | confidence: high]

- **8B (BF16 full precision)**: ~16 GB VRAM. RTX 3090 24GB or equivalent.
  [Source: training knowledge | confidence: high]

- **70B (Q4_K_M GGUF)**: ~39–40 GB. Requires 2x RTX 3090/4090 (48 GB combined), single A100 40GB (tight), or Mac Studio Ultra M2/M3 (192GB unified memory).
  [Source: training knowledge | confidence: high]

- **405B (Q4_K_M GGUF)**: ~230 GB+. Requires 8x A100 80GB or equivalent server-class setup. Not practical for single-machine consumer hardware.
  [Source: training knowledge | confidence: high]

- **For a typical Obsidian second-brain agent**: Hermes 3 8B Q4_K_M is the recommended entry-point (fits on mainstream gaming GPU). Hermes 3 70B is the quality ceiling for serious local deployment.
  [Source: synthesis from training knowledge | confidence: high]

---

## Key URLs to Verify Live (fetch-blocked this session)

1. https://nousresearch.com/hermes3/ — Official Hermes 3 announcement
2. https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B — Model card, license, training details
3. https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-70B — Same
4. https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-405B — Same
5. https://huggingface.co/NousResearch/Hermes-2-Pro-Llama-3-8B — Hermes 2 Pro details
6. https://gorilla.cs.berkeley.edu/leaderboard.html — BFCL live leaderboard
7. https://huggingface.co/NousResearch — Check for Hermes 4 or newer releases
8. https://github.com/NousResearch — Check for technical papers, new announcements

---

## Staleness / Reliability Assessment

| Claim area               | Confidence | Staleness risk    | Action needed            |
|--------------------------|------------|-------------------|--------------------------|
| Hermes 2 / 2 Pro facts   | High       | Low (>12mo old)   | Spot-check model cards   |
| Hermes 3 at-release facts| High       | Medium (18mo old) | Verify model cards live  |
| Hermes 4 existence       | None       | Critical          | Must fetch HF org page   |
| Benchmark rankings       | Medium     | High              | Fetch live BFCL page     |
| Hardware VRAM estimates  | High       | Low               | Minor spot-check         |
| Licensing terms          | High       | Low               | Confirm no changes       |

# Hermes Model Family — Training Knowledge Dump
# Source type: Claude model training knowledge (cutoff August 2025)
# WARNING: Web fetch was blocked. All facts below are from training data, NOT live-fetched primary sources.
# Freshness risk: HIGH for anything post-July 2025. Flag all claims accordingly.
# Date recorded: 2026-06-13

---

## Hermes 2 Series

- Base models: Mistral 7B, Yi 34B, Solar 10.7B, Llama 2 variants
- Key HuggingFace slugs:
  - NousResearch/Nous-Hermes-2-Mistral-7B-DPO
  - NousResearch/Nous-Hermes-2-Yi-34B
  - NousResearch/Nous-Hermes-2-Solar-10.7B
- Release period: Late 2023 – early 2024
- Context windows: 32K (Mistral), 200K (Yi-200K variant), varies
- Training focus: instruction following, GPT-4-level outputs from smaller models
- Licensing: Apache 2.0 on Mistral-based, Yi models subject to Yi License
- No native function-calling format in early Hermes 2 base

## Hermes 2 Pro Series

- Key HuggingFace slugs:
  - NousResearch/Hermes-2-Pro-Mistral-7B
  - NousResearch/Hermes-2-Pro-Llama-3-8B
  - NousResearch/Hermes-2-Pro-Llama-3-70B (may exist)
- Release period: 2024
- New capability: OpenAI-compatible function/tool calling format introduced
- Structured JSON output mode
- Uses special <tool_call> and <tool_response> XML-style tags for agentic workflows
- System prompt steerability: strong persona/role adherence
- Alignment: described as "neutral" — less over-refusal than base instruct models
- Context window: 8K (Llama 3 8B base), 32K (Mistral base)
- License: Llama 3 Community License (commercial allowed with restrictions) for Llama 3 variants; Apache 2.0 for Mistral variant

## Hermes 3 Series

- Released: August 2024 (announced with blog post on nousresearch.com)
- Base model: Meta Llama 3.1 (8B, 70B, 405B)
- HuggingFace slugs:
  - NousResearch/Hermes-3-Llama-3.1-8B
  - NousResearch/Hermes-3-Llama-3.1-70B
  - NousResearch/Hermes-3-Llama-3.1-405B
- Context window: 128,000 tokens (inherited from Llama 3.1)
- Function calling: OpenAI-compatible tool-calling format, both parallel and sequential tool calls
- JSON mode: native structured output support
- Reasoning: <reasoning> tags for chain-of-thought (some variants)
- Multi-turn agentic loops: explicitly trained for
- License: Meta Llama 3.1 Community License (allows commercial use for entities under 700M MAU; larger orgs need special license from Meta)
- GGUF quants: Available on HuggingFace from bartowski and TheBloke (community)
- Also available via Ollama registry

## Hermes 4

- Status as of August 2025 training cutoff: NO confirmed release found in training data
- May have been announced or released after August 2025 — REQUIRES LIVE VERIFICATION
- Possible bases: Llama 3.3, Llama 4, Qwen 2.5, DeepSeek V3 (speculative)

## Agentic / Tool-Call Features (Hermes 3 focus)

- Function calling format: Uses <tool_call> wrapper JSON compatible with OpenAI tool-calling schema
- Parallel function calls: Yes (multiple tools in one response)
- System prompt adherence: Strong — Nous trains specifically for instruction-following
- "Uncensored" framing: Nous describes models as less restrictive than Meta's own Llama Instruct; willing to discuss topics that Meta Instruct refuses
- JSON structured output: Models trained with JSON mode for schema-constrained outputs
- Multi-step reasoning: Supported via extended thinking / scratchpad in some configs

## Benchmark Standing (as of mid-2024 to early 2025)

- Hermes 3 8B: Competitive with Llama 3.1 8B Instruct; claimed superior instruction-following
- Hermes 3 70B: Competitive with GPT-3.5-Turbo class; Nous claimed it matched or exceeded Meta's own Llama 3.1 70B Instruct on several evals
- Hermes 3 405B: Positioned as frontier open-weight; Nous claimed near GPT-4o performance on some tasks
- Tool-use benchmarks: Hermes 2 Pro was cited on Berkeley Function Calling Leaderboard (BFCL) as top-tier open-weight; Hermes 3 continues this
- BFCL (Berkeley Function-Calling Leaderboard): Hermes 2 Pro Llama 3 appeared in top open-weight positions circa mid-2024
- MT-Bench, IFEval: Strong performance cited by Nous Research

## Hardware Requirements (practical estimates)

| Model         | VRAM (4-bit quant) | VRAM (full BF16) | Suitable hardware          |
|---------------|-------------------|-------------------|---------------------------|
| 8B            | ~5–6 GB           | ~16 GB            | RTX 3080/4070, M2 Pro     |
| 70B           | ~35–40 GB         | ~140 GB           | 2x RTX 3090 / A100 40GB   |
| 405B          | ~200+ GB          | ~810 GB           | 8x A100 80GB / H100 cluster|

- GGUF Q4_K_M quants are the standard for local inference (llama.cpp, Ollama, LM Studio)
- 8B Q4_K_M: ~4.7 GB — fits on 8GB VRAM consumer GPU
- 70B Q4_K_M: ~40 GB — requires 2x 24GB GPUs or Mac Studio Ultra M2/M3

## Distribution Channels

- HuggingFace: https://huggingface.co/NousResearch (primary)
- GGUF quants: https://huggingface.co/bartowski (community quants)
- Ollama: `ollama run hermes3` (8B default)
- LM Studio: searchable in model library
- llama.cpp compatible

## Licensing Summary

| Model series       | License                              | Commercial OK?                        |
|--------------------|--------------------------------------|---------------------------------------|
| Hermes 2 (Mistral) | Apache 2.0                           | Yes, permissive                       |
| Hermes 2 (Yi)      | Yi License                           | Restricted (non-commercial or limited)|
| Hermes 2 Pro (L3)  | Llama 3 Community License            | Yes, <700M MAU orgs                  |
| Hermes 3 (L3.1)    | Llama 3.1 Community License          | Yes, <700M MAU orgs                  |
| Hermes 3 405B      | Llama 3.1 Community License          | Yes, same restrictions                |

## Key Sources to Verify Live

- https://nousresearch.com/hermes3/ (official announcement, August 2024)
- https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B (model card)
- https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-70B
- https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-405B
- https://huggingface.co/NousResearch/Hermes-2-Pro-Llama-3-8B
- https://github.com/NousResearch (GitHub org)
- https://gorilla.cs.berkeley.edu/leaderboard.html (BFCL leaderboard — live data)

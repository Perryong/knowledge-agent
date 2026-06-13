# Fact-Check Verdicts — Hermes + Obsidian Agent

*Lead-performed verification, 2026-06-13, via direct WebFetch of primary sources.*

## CONFIRMED (primary source)
- **NousResearch/hermes-agent exists.** Desc "The agent that grows with you"; **193k stars**; **MIT**; latest **v0.16.0 "The Surface Release"** (Jun 6 2026); built-in learning loop (creates/improves skills from experience, FTS5 session search + LLM summarization, "deepening model of who you are"). [github.com/NousResearch/hermes-agent | fetched 2026-06-13]
  - Caveat: README does NOT mention Obsidian or Ollama by name. Local models via "any model / your own endpoint." Obsidian = bundled skill per docs (hermes-agent.nousresearch.com/docs/.../note-taking-obsidian), not README headline.
- **Hermes 4 70B**: base Meta-Llama-3.1-70B, 71B params, **Llama3 license**, tech report **Aug 25 2025**; `<tool_call>` XML function calling + `<think>` hybrid reasoning (thinking=True) confirmed on model card. [huggingface.co/NousResearch/Hermes-4-70B | fetched 2026-06-13]
- **Hermes 4.3**: 36B, **Seed-OSS-36B-Base** (ByteDance), up to **512K context**, **trained entirely on Psyche** network (Psyche version outperformed centralized). Official page emphasizes **RefusalBench SOTA**. [nousresearch.com/introducing-hermes-4-3 | fetched 2026-06-13]

## CORRECTED
- Hermes Agent stars: 22k (players thread) and 175k (model-family thread) → **193k actual**.
- Hermes 4.3 specific math benchmarks (MATH-500 93.8 / MMLU 87.7 / AIME24 71.9 / GPQA 65.5) — NOT on official page (which leads with RefusalBench). Treat as **UNVERIFIED**; do not state as fact.

## UNRESOLVED / FLAGGED
- Hermes 4.3 exact release date: Aug 2025 (introducing page) vs Dec 2 2025 (Nous X post). Likely announce vs formal 36B release. Report as "late 2025" with note.
- Manus "$2B Meta acquisition" price — UNVERIFIED, drop the figure (keep the file-based-memory point if attributable).
- BFCL v4 numeric score for Hermes 4/4.3 — none found; do not assert a number.
- DeepHermes 3 base: Llama 3 vs 3.1 — minor, omit precision.

## NET
Core thesis verified: Hermes 4/4.3 are real open-weight models with native tool-calling + hybrid reasoning; Hermes Agent is a real, very popular MIT framework with learning-loop memory and a bundled Obsidian integration; MCP + Local REST API standardize vault read/write. Contrarian limits (capability gap at self-host sizes, local latency/cost, markdown-memory failure modes) stand as sourced and unrebutted.

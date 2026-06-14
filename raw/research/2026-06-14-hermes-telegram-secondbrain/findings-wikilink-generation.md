# Wiki-Link Generation (the "second-brain brain") + real-time vs batch

*Research date: 2026-06-14 | Live web (~12 sources) + direct read of this repo's scripts | reconstructed by lead (subagent file write blocked)*

## Karpathy LLM Wiki pattern
"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase." Replaces RAG with a persistent, incrementally-growing markdown wiki. 3 layers: raw sources (immutable) → LLM-maintained wiki with `[[wiki-links]]` → schema/config. Nth note > 1st because cross-referenced against N-1 priors; value compounds with link density. [gist.github.com/karpathy/442a6bf...; medium urvvil08; levelup.gitconnected beyond-rag]

### Reference implementations (all batch-first)
- **kytmanov/obsidian-llm-wiki-local**: 3-stage — Ingest (3-8B LLM extracts concepts + quality scores to state DB) → Compile (7-14B gathers source notes per concept, generates articles with `[[wikilinks]]` to drafts) → Review (human approves to published). Hand-edit detection, alias repair (`olw maintain --fix` rewrites alias links + stubs missing targets), `olw lint` (orphans/stale/broken/empty).
- **nashsu/llm_wiki**: CoT two-step ingest (Analysis: entities/concepts/connections → Generation: files with cross-refs + frontmatter). SHA256 skip-unchanged. 4-signal relevance: direct links ×3.0, shared sources ×4.0, Adamic-Adar neighbors ×1.5, type affinity ×1.0. Persistent ingest queue.
- **Ar9av/obsidian-wiki**: 4-stage; "Pull Information" (concepts/entities/claims/relationships/open-questions); dedicated `cross-linker` skill runs POST-ingest ("scans vault for unlinked mentions, weaves [[wikilinks]]"). `.manifest.json` delta tracking. Linking is explicitly BATCH.
- **green-dalii/obsidian-llm-wiki**: plugin; granularity Fine ~100 / Minimal ~5 entities; slug-based matching dedupes name variants; alias-aware search; `Lint wiki` dead-link scan; user-triggered ingest (not per-note).
- **nvk/llm-wiki**: multi-agent parallel; dual-link `[[slug|Title]] ([Title](../path.md))`; "parallel ingest, sequential compile."

## Three link-generation techniques
- **A — LLM rewrite with slug list:** pass note body + flat slug→title list; "insert `[[slug]]` only from this list, don't invent." High precision (handles paraphrase/synonyms); token cost scales with vault (500 notes ≈ 2-5K tokens/call). **Mitigation: feed `build_wiki_index.py` slugs (`wiki_name(path)`) as the allowed list.**
- **B — entity/filename matching (zero LLM):** extract noun phrases/NER, match filenames (exact slug or RapidFuzz/difflib). Reuse `wiki_graph_optimizer.py`'s `aliases` dict in `.claude/memory/wiki-link-memory.json`. Cheap, deterministic, misses paraphrase. Best for stable canonical terms (people/projects/tools).
- **C — embedding/TF-IDF similarity:** cosine-similar candidates as suggestions. **This repo's `wiki_graph_optimizer.py` already implements C** (stdlib TF-IDF + tag Jaccard + title-mention, threshold 0.22, self-tuning ledger). Best for BATCH cross-note discovery as human-reviewable proposals; not for per-message inline.
- Industry pattern: **A+B at ingest (inline links), C in batch (cross-note discovery).** COG already has C — the gap is a thin orchestrator doing A at batch time.

## Avoiding broken/duplicate links & rot
- Canonicalize on filename stem (`wiki_name(path)` already does this); use `[[slug|Display]]`; lowercase-hyphen slugs.
- Aliases in frontmatter (`aliases: [RAG, retrieval augmented generation]`); reuse `wiki_graph_optimizer.py` ledger `aliases` dict (seeded when dominant_signal == title_mention).
- Pass ONLY verified slugs to the LLM linker; run `wiki_graph_optimizer.py analyze` (its broken-link loop lines ~190-197 flags links to non-existent slugs).
- Prefer stubs over dangling links (kytmanov `--fix` creates stubs). Dedupe via SHA256 (nashsu) + ledger `rejected_pairs` (suppress re-proposing declined pairs).

## Real-time vs batch — RECOMMENDATION: BATCH with lightweight real-time pre-pass
**Real-time (per-response):** notes immediately linked, fresh context, simple — BUT one LLM call/message (cost ×10+/session), index lacks same-session notes (within-session cross-links impossible), 20 msgs = 20 commits (git noise), +300-2000ms latency, link quality limited to current note + stale index.
**Batch (periodic compile):** richer cross-linking (LLM sees whole session), clean history (1-2 commits/day vs 20), index fresh, cost paid once/batch, composes with existing scripts, errors caught pre-commit. Cons: notes unlinked up to 30 min; needs a scheduler.
Industry converges batch-first (kytmanov, nashsu, ar9av, green-dalii, nvk; smixs nightly rebuild 21:00).

### Recommended pipeline
**Phase 1 — Capture (synchronous per Telegram msg, zero-LLM linking):** write raw note (frontmatter + body); Technique B regex match using `aliases` dict + last `build_wiki_index.py` slug list; insert exact-match `[[slug]]`; accumulate in working tree (don't commit yet).
**Phase 2 — Batch enrichment (every 30 min or session end):**
1. `build_wiki_index.py` → refresh `05-knowledge/INDEX.md` with new notes.
2. For each new note: LLM (Technique A) rewrite body with inline `[[slug]]` from current slug list.
3. `wiki_graph_optimizer.py analyze` → cross-note missing-link proposals.
4. Auto-accept where score ≥ 0.45 AND dominant_signal == title_mention; defer rest for review.
5. `wiki_graph_optimizer.py apply`.
6. `git add -A && git commit -m "batch: link enrichment YYYY-MM-DD HH:MM"`.

**Why for Hermes/Telegram:** a session = a cluster of thematically related notes; greatest linking value is intra-session, which real-time can't achieve. Existing `wiki_graph_optimizer.py` already has scoring/proposal/apply/self-improvement — only NEW code needed is a thin batch orchestrator that calls the LLM for Technique A then chains the two existing scripts.

## Precedent
- **smixs/agent-second-brain** — Telegram → Obsidian pipeline; batches commits (every 5 min when open / 30 min LaunchAgent), nightly graph rebuild 21:00. Confirms batch-commit approach for a Telegram-driven vault. [github.com/smixs/agent-second-brain]

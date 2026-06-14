# Hermes Agent (Telegram) → Wiki-Linked Second Brain → GitHub

Ready-to-wire scaffold that turns each Hermes Agent Telegram response into a
wiki-linked markdown note and auto-commits it to this repo.

Design rationale and sources: [[hermes-telegram-second-brain-pipeline]]
(`05-knowledge/resources/`). Architecture in one line:

```
Telegram → Hermes (post_llm_call hook) → raw/hermes-inbox/*.md   [real-time, no git/LLM]
                                   nightly batch ↓
   llm_link.py → 05-knowledge/captures/ → build_wiki_index.py → wiki_graph_optimizer.py
   → git_autocommit.sh → push to Perryong/knowledge-agent  [PRIVATE]
```

Capture is instant; **linking + committing happen in one nightly batch** (10–20× cheaper
than per-message linking, clean git history, and the only way to wire within-session
cross-links).

## Files

| File | Role |
|---|---|
| `capture-note.sh` | `post_llm_call` hook entrypoint — thin wrapper that runs `capture_note.py` |
| `capture_note.py` | hook body — writes the response to `raw/hermes-inbox/` (no deps, atomic write) |
| `config.snippet.yaml` | the `hooks:` block to paste into `~/.hermes/config.yaml` |
| `llm_link.py` | promotes inbox notes → `05-knowledge/captures/` with `[[wiki-links]]` (exact-match by default; LLM if a key is set) |
| `batch_enrich.sh` | nightly orchestrator: link → index → analyze → commit/push |
| `.env.example` | env template (copy to `~/.hermes/.env`, never commit) |

Reused as-is: `scripts/build_wiki_index.py`, `scripts/wiki_graph_optimizer.py`,
`scripts/git_autocommit.sh`.

## Setup (one time)

1. **Install Hermes Agent + connect Telegram**
   ```bash
   hermes gateway setup        # choose Telegram, paste BotFather token + your numeric user id
   ```
2. **Env** — `cp integrations/hermes-telegram/.env.example ~/.hermes/.env`, fill in
   `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS` (your id only), and the two vault paths.
3. **Discover the hook payload schema (recommended)**
   ```bash
   export HERMES_CAPTURE_DEBUG=1     # then send one Telegram message and read /tmp/hermes-payload.log
   ```
   If the response text isn't picked up, adjust the `jq` query in `capture-note.sh`.
4. **Register the hook** — paste `config.snippet.yaml` into `~/.hermes/config.yaml`
   with an absolute path. Verify `post_llm_call` actually fires on your version; if not,
   use the commented `on_session_finalize` fallback.
5. **Make scripts executable**
   ```bash
   chmod +x integrations/hermes-telegram/capture-note.sh integrations/hermes-telegram/batch_enrich.sh
   ```
6. **Schedule the batch** (cron example — 02:00 daily):
   ```cron
   0 2 * * * cd /abs/path/COG-second-brain && bash integrations/hermes-telegram/batch_enrich.sh >> /tmp/cog-batch.log 2>&1
   ```

## Try it without Hermes

```bash
# simulate a captured turn (set HERMES_PYTHON=python on Windows)
printf '{"response":"Testing the hermes obsidian second brain."}' \
  | OBSIDIAN_VAULT_PATH="$PWD" bash integrations/hermes-telegram/capture-note.sh
# link + index (no commit) — dry run first
VAULT_ROOT="$PWD" python3 integrations/hermes-telegram/llm_link.py --dry-run
```

## Linker modes
- **Default — exact-match (free, deterministic, no deps):** wraps the first occurrence of any
  existing note's title/slug in `[[slug]]`. Predictable, zero cost. Misses paraphrases.
- **LLM — set `HERMES_LINK_API_KEY`:** OpenAI-compatible call that also links paraphrased
  concepts. Output is post-filtered so only *existing* slugs survive (the model can't invent
  a link target). Falls back to exact-match on any API error.

## Cross-note links (review step)
`batch_enrich.sh` runs `wiki_graph_optimizer.py analyze`, which writes proposals to
`/tmp/wiki-proposals.{md,json}`. Apply stays human-in-the-loop (its design):
```bash
# review /tmp/wiki-proposals.md, mark accept/reject, then:
python3 scripts/wiki_graph_optimizer.py apply --proposals /tmp/wiki-proposals.json
```

## Must-dos (security & hygiene)
- **Keep `Perryong/knowledge-agent` PRIVATE** — committed Telegram content is permanent.
- **Secrets in env only.** `.env` is git-ignored patterns; never commit the bot token or PAT.
  A leaked bot token = full control of your bot. Push auth = deploy key (SSH) or fine-grained PAT.
- **Quality gate** to avoid a "digital graveyard": capture only messages worth keeping (a flag
  word, or have Hermes decide), and run a weekly lint (`wiki_graph_optimizer.py analyze`).
- Keep `~/.hermes` + the vault on **local disk** (not NFS — SQLite WAL breaks there).
- Captures use **atomic writes + unique filenames**, so the hook and the nightly batch
  never collide and git never stages a half-written file — no lockfile required.

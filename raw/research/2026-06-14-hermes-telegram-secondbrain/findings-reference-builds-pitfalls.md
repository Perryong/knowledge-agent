# End-to-End Reference Builds + Pitfalls

*Research date: 2026-06-14 | Live web, ~22 sources | reconstructed by lead (subagent file write blocked)*

## 1. Reference builds
- **itechmeat/open-second-brain** — Hermes Agent runtime; writes memory via `brain_feedback` MCP tool → `.md` under `Brain/` in vault; all memory file-resident. Nightly "dream pass" (cron, `docs/hermes-cron.md`): converts repeated corrections → persistent preferences w/ confidence; **deterministic, no LLM in the algorithm**; atomic file moves; SHA-256 snapshot sidecars. Git = user cron (no per-message commit). Prompt-injection guard. **Fit: HIGH** (Hermes-native; dream pass = batch analog; add git cron).
- **Hermes bundled `note-taking/obsidian` skill** (v0.14, 2026-05-16): `hermes memory setup --provider obsidian --path <vault>`; uses `write_file` (preferred over heredoc/echo); `[[Note Name]]` links but agent must generate them — NO automated linker in the skill; `OBSIDIAN_VAULT_PATH`; modes (a) Local REST API :27123 or (b) cyanheads/obsidian-mcp-server. No git hooks. [github .../skills/note-taking/obsidian/SKILL.md; gptaiclips.hashnode.dev]
- **Hermes bundled `research/llm-wiki` skill** (Karpathy): 3 layers `raw/` (immutable) → `wiki/` (agent md) → `SCHEMA.md`; **min 2 outbound `[[wikilinks]]`/page**; **explicitly batch** ("read all sources first, identify entities collectively, update pages in one pass"); lint flags orphans/broken links/missing frontmatter/stale >90d/contradictions. Community ext Robs87/llm-wiki adds 2-pass linking (deterministic then semantic via NetworkX+Louvain) + `health-check.py`. **Fit: HIGH for compile step; batch-oriented.** [github .../skills/research/llm-wiki/SKILL.md]
- **Burgunthy/hermes-second-brain** — Obsidian+Graphify+Claude Code+Hermes (cron); `raw/ → extract → wiki/ → index+log → graph`; `wiki-graph.py` from frontmatter `related:`. Gap: doesn't document write/commit/Telegram specifics.
- **kytmanov/obsidian-llm-wiki-local** — Karpathy 100% local (Ollama); Ingest→Compile→Review; **auto-commits with `[olw]` prefix, `olw undo`**; raw never modified; failure modes documented (JSON instability 3-tier retry, ctx exhaustion→chunking, rejection blocking, model mismatch). Now maintenance mode (successor Synto). **Fit: HIGH for compile step.**
- **Telegram→Obsidian projects:** soberhacker/obsidian-telegram-sync (desktop plugin, NOT headless); dimonier/tg2obsidian (headless Python, no links/git); **fahadhasin/notes-bot** (Telegram→md→**nightly git backup**, all local, no linking — closest minus linking); ahelsamahy (daily-append, low commit noise).
- **n8n** Telegram→AI→Google Drive→Obsidian: routes via Drive, no direct git, no linking. Fit: low-moderate.

## 2. Recommended end-to-end wiring
```
Telegram → Hermes Agent (VPS; TELEGRAM_BOT_TOKEN + TELEGRAM_ALLOWED_USERS env, NOT in repo)
  → on message: note-taking skill → write_file ~/vault/inbox/YYYY-MM-DD-<slug>.md
     (frontmatter title/date/tags/source:telegram; body = Hermes note ABOUT msg, not raw copy; minimal inline [[links]])
     (filesystem write only — NO git, NO LLM compile here)
  → nightly cron 02:00:  Wiki-Linker pass
     A: obsidian-llm-wiki-local compile (Ollama, zero API) OR
     B: Hermes llm-wiki skill batch (min 2 links/page) OR
     C: build_wiki_index.py (deterministic exact-name, zero LLM)
  → git_autocommit.sh (GITHUB_PAT env) → commit once/day → push
  → GitHub Perryong/knowledge-agent  [MUST be PRIVATE]
```
Env (~/.hermes/.env, never committed): TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS, OBSIDIAN_VAULT_PATH, GITHUB_PAT (fine-grained, single-repo write).

## 3. Pitfalls / failure modes
1. **Concurrent-write corruption** [Med-High]: Hermes `SessionDB._lock` is a single threading.Lock (issue #34444), SQLite-level not per-file → nightly linker/git may read a half-written note. Mitigate: stagger cron, atomic .tmp→rename, chain `compile && git_autocommit.sh`.
2. **Commit noise** [High]: per-message commits = chat-log history (300+ micro-commits/mo); git blame meaningless. Mitigate: never commit per message; stage to inbox/; one nightly commit.
3. **Wiki-link rot / duplicates**: `[[Python Asyncio]]` vs `[[asyncio]]` orphans; dup notes without pre-write search; stale content; phantom hubs. Mitigate: pre-write vault search before creating; weekly lint (`health-check.py`/`olw lint`); canonical lowercase-kebab slugs + SCHEMA.md title registry.
4. **Secrets in repo** [High]: bot token = full bot control + reads all messages + impersonation (documented PII leak incident). Mitigate: token+PAT in env/secrets mgr only; `.gitignore` `.env`/`config.yaml`; gitleaks pre-commit; rotate on leak. [gitguardian.com/remediation/telegram-bot-token]
5. **Telegram privacy** [High]: a public repo makes all committed message content permanently public (GitHub delete ≠ gone from forks/caches). Mitigate: **repo PRIVATE**; 6-month visibility audits; commit a note ABOUT the message not a verbatim copy; strict TELEGRAM_ALLOWED_USERS = your own ID; no group channels.
6. **Token cost** [Med]: per-message linking reloads source articles each time → 10-20x batch cost. 7B via OpenRouter ≈ $1.5-3/mo batch; Sonnet ≈ $45-90/mo. Use batch.
7. **SQLite on NFS** [Med] (#22032): `journal_mode=WAL` fails on NFS/SMB/FUSE/WSL1 → corrupts /resume,/history, crashes dispatcher. Keep ~/.hermes + vault on local block storage (ext4).
8. **Rate limits** [Low]: Telegram 30 msg/s, 20 msg/min/chat — not binding for single-user; binding constraint = LLM inference speed.
9. **Digital graveyard** [the real long-term risk]: notes accumulate without being used (architectural, not discipline). Mitigate: (1) quality gate at ingest — write a note only for flagged/durable-insight messages, else rolling memory; (2) expiry + weekly review; (3) inbox-first → promote to wiki/ only on compile; (4) human governance pages (overview/questions/decisions).

## 4. Honest take: real-time vs nightly batch
All primary sources + reference builds converge on **batch** (official llm-wiki SKILL "batch the updates"; open-second-brain separates instant capture from nightly dream pass; notes-bot nightly git; 10-20x cheaper; concurrency-safe; low commit noise).
**Recommended: HYBRID** — Hermes writes raw note to `inbox/` instantly on message (filesystem only, no git/LLM); nightly 02:00 cron: linker on inbox/ → move to notes/ + update wiki/ → `git_autocommit.sh` (single daily commit) → Telegram confirmation ("N notes added, M wiki articles updated"). Only the filesystem write is real-time. Per-message real-time loop is worth it ONLY if Hermes must query its just-written note in the same session — and even then it can read the inbox/ file directly without real-time linking/git.

## Source quality caveats (for fact-check)
- Several sources are low-quality SEO and need primary verification: hermes-agent.ai, evomap.ai, remoteopenclaw.com, fast.io, designforonline.
- Several GitHub issue numbers cited are large/suspicious (#31054, #34444, #25204, #22032, #2817) — VERIFY existence before stating as fact; treat the *mechanisms* (hooks, single-lock, NFS) as plausible but issue-number-specific claims as unverified.

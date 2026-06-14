# Response → Markdown Capture (the WRITE step)

*Research date: 2026-06-14 | Live web, ~11 sources | reconstructed by lead (subagent file write blocked)*

## 1. Bundled Obsidian skill
- `skills/note-taking/obsidian/SKILL.md` (platform-agnostic, bundled). Uses tools (doesn't define them): `write_file`, `patch`, `read_file`, `search_files`, `terminal` (resolve `$OBSIDIAN_VAULT_PATH` first — file tools don't expand shell vars). Vault: `OBSIDIAN_VAULT_PATH` env (fallback ~/Documents/Obsidian Vault). [github .../note-taking/obsidian/SKILL.md]
- Issue #44 (closed): SKILL.md once had a hardcoded path — ensure OBSIDIAN_VAULT_PATH set + SKILL references env not literal.
- **Does NOT auto-create a dated note per response** — note creation is agent-driven (must be prompted / custom skill). Does NOT touch MEMORY.md (separate memory system, ~1300-token budget).
- `hermes memory setup --provider obsidian --path <vault>` (v0.14, 2026-05-16) syncs turns to vault but in a provider-internal format (not per-response dated notes). [.../memory-providers]

## 2. Two write mechanisms
### A. Obsidian Local REST API (coddingtonbear, :27124 HTTPS / :27123 HTTP)
- `PUT /vault/{path}` create/overwrite; `POST /vault/{path}` append-or-create (atomic upsert); `POST /vault/{path}/heading/{h}` append under heading; `PATCH` surgical by heading/block/frontmatter (Operation + Target-Type + Target headers). Returns previousSizeInBytes/currentSizeInBytes (clobber detection). MCP: 15 tools at /mcp/ (Bearer auth).
- **Hard constraint: requires Obsidian RUNNING on same machine → NOT viable for headless VPS bot.** [github coddingtonbear/obsidian-local-rest-api]

### B. Direct filesystem `write_file` (what the bundled skill uses)
- Agent calls `write_file(<abs-path>, <content>)`; Obsidian picks up via FS watch. Works headless, no auth, direct I/O.

| Concern | REST API (A) | Direct FS (B) |
|---|---|---|
| Obsidian must run | YES | NO |
| Headless/VPS | NO | **YES** |
| Surgical heading append | PATCH | read→modify→write |
| Atomic upsert | POST | check existence |
| Auth | Bearer | none |

- **Recommendation (headless Telegram bot): direct `write_file`, always write NEW files** (don't append) to minimize git conflict.

## 3. Per-response note structure
- Filename: `<vault>/Hermes-Agent/Daily/2026-06-14-1432-telegram.md` (or `-<slug>.md`).
```markdown
---
title: "2026-06-14 14:32 Telegram Response"
date: 2026-06-14
time: "14:32:07"
source: telegram
tags: [hermes, telegram, capture]
---
# 2026-06-14 14:32 — Telegram Response
<body; convert Telegram *bold*→**bold**>
## Related
- [[prior-relevant-note]]
## Source Context
- Platform: Telegram | Timestamp: 2026-06-14T14:32:07Z
```
- **New file per response (not append):** avoids merge conflicts, clean `git add <one-file>` diffs, stable `[[2026-06-14-1432-telegram]]` link identity.
- Community precedent: TechieTer/hermes-memory-keep-alive-for-obsidian writes distinct named files per task (RESUME/CHECKLIST/DOCS) via cron jobs — confirms named-file-per-task over single-note-append.

## 4. Custom capture skill (instruction doc, not code)
- Drop `~/.hermes/skills/telegram-capture/SKILL.md`; auto-loads next session. Frontmatter fields confirmed: name, description, version, platforms, requires_toolsets, fallback_for_toolsets, config, env.
- Procedure: resolve `$OBSIDIAN_VAULT_PATH` via terminal → gen timestamp/slug (`date -u`) → convert Telegram md → `write_file(new path, content)` → verify `read_file` → `flock` git add specific file + commit + push.
- `skill_manage` lets the agent author/patch its own skills (trigger: 5+ tool-call task, error recovery, user correction).
- ⚠️ Reminder: skills are model-invoked, so for guaranteed per-turn capture pair this skill with a **post_llm_call hook** (see telegram-hook findings), not the skill alone.

## 5. Concurrency / locking
- `.git/index.lock` collisions if two git processes run (agent commit + obsidian-git timer). obsidian-git issues #342/#1077/#683 document this; stale lock is the real danger.
- Agent writing to a file open in Obsidian → "modified externally" / rare buffer corruption. New-file-per-response largely eliminates it.
- Mitigations: (1) `git add <specific-new-file>` not `git add .`; (2) exclude `Hermes-Agent/Daily/` from obsidian-git auto-commit (let agent commit it); (3) `flock /tmp/vault-write.lock -c "write + commit"`; (4) check/retry on `.git/index.lock`; (5) captures on a separate branch/worktree, merge on schedule.
- Safe pattern: resolve vault path → gen timestamp/filename → `write_file` NEW file → `flock /tmp/vault-write.lock git add <file>` → commit → push.

## Confidence
HIGH: Obsidian skill tool list, REST endpoints, index.lock errors, note structure. MEDIUM: SKILL.md frontmatter list, obsidian memory-provider per-response format. LOW/not found: exact files written by `hermes memory setup --provider obsidian`.

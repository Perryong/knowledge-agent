---
title: "Hermes Agent (Telegram) → Wiki-Linked Second Brain → GitHub: Build Guide"
type: resource
category: ai-engineering
status: active
created: 2026-06-14
updated: 2026-06-14
tags: [hermes-agent, telegram, second-brain, wiki-links, obsidian, git-automation, mcp, karpathy-llm-wiki, how-to]
raw_sources:
  - raw/research/2026-06-14-hermes-telegram-secondbrain/
confidence: high
---

# Hermes Agent (Telegram) → Wiki-Linked Second Brain → GitHub

> **Goal.** Each time the NousResearch **Hermes Agent** answers a user over **Telegram**, capture that response into a markdown note, generate `[[wiki-links]]` against the existing vault, and **auto-commit to GitHub**. Researched 2026-06-14 via 5 parallel threads + lead verification of primary docs. Builds on [[hermes-obsidian-second-brain]]; targets this repo ([[COG Second Brain]]) per [[HYBRID-SECOND-BRAIN]] / [[PARA]].

## TL;DR

1. **You barely need to build anything new — both halves already exist.** Hermes ships a first-class **Telegram channel**, a **`post_llm_call` hook** that fires right after each response, and bundled `note-taking/obsidian` + `research/llm-wiki` skills. This repo ships `build_wiki_index.py`, `wiki_graph_optimizer.py`, `git_autocommit.sh`, and a `research_vault` MCP server. [Source: [[hermes-telegram-second-brain-pipeline]] §"What already exists" | 2026-06-14 | confidence: high]
2. **The interception point is the `post_llm_call` shell hook** — official docs: it "fires once per turn, after the tool-calling loop completes and the agent has produced a final response." Configure it in `~/.hermes/config.yaml`; it receives the turn as JSON on stdin. [Source: hermes-agent docs/features/hooks | 2026-06-14 | confidence: high]
3. **Capture in real-time, link + commit in a batch.** Per-message LLM linking is **10–20× costlier**, turns git history into a chat log, and *cannot* wire within-session cross-links. So: the hook writes a dated note to `inbox/` instantly (filesystem only); a **nightly/session-end batch** does the LLM wiki-linking and the single git commit. [Source: §"Real-time vs batch" | 2026-06-14 | confidence: high]
4. **Reuse your existing scripts as the batch pipeline:** `build_wiki_index.py` (refresh the `[[link]]` index) → an LLM linker pass → `wiki_graph_optimizer.py analyze/apply` (cross-note links) → `git_autocommit.sh` (allowlisted, non-force push). [Source: §"Step 3/4" | 2026-06-14 | confidence: high]
5. **Three non-negotiables:** keep the GitHub repo **PRIVATE** (committed Telegram content is permanent), keep `TELEGRAM_BOT_TOKEN` + `GITHUB_PAT` **in env only** (a leaked bot token = full control of your bot), and **quality-gate** what gets saved or you build a "digital graveyard." [Source: §"Pitfalls" | 2026-06-14 | confidence: high]

---

## What already exists (so you don't rebuild it)

| Piece | On the Hermes side | In this repo (COG) |
|---|---|---|
| Telegram I/O | first-class channel: `hermes gateway setup`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, python-telegram-bot, long-poll | — |
| "after response" hook | **`post_llm_call`** shell hook + gateway hooks (`~/.hermes/hooks/<n>/HOOK.yaml`) | — |
| write note | bundled `note-taking/obsidian` skill (`write_file`, `OBSIDIAN_VAULT_PATH`) | `research_vault` MCP `save_research_note` (frontmatter-enforced) |
| wiki-linking | bundled `research/llm-wiki` skill (Karpathy pattern, ≥2 links/page, lint) | `build_wiki_index.py` + `wiki_graph_optimizer.py` + MCP `link_wiki_notes` |
| auto-commit | — | `scripts/git_autocommit.sh` (allowlist, empty-guard, non-force) + MCP `commit_and_push` |

Because Hermes is **MCP-compatible**, the single cleanest option is to register this repo's `research_vault` MCP server with Hermes — then `save_research_note` / `link_wiki_notes` / `commit_and_push` become tools the agent (or a hook) can call directly. [Source: mcp/research_vault/README.md | 2026-06-14 | confidence: high]

## Architecture (the hybrid loop)

```
Telegram user ⇄ Hermes Agent (VPS, long-poll)
        │  post_llm_call hook fires after the final response
        ▼
  capture-note.sh   →  write NEW note  ~/vault/inbox/YYYY-MM-DD-HHMM-telegram.md
   (filesystem only,    frontmatter: title/date/source: telegram/tags
    flock-guarded,       body: a note ABOUT the message (not a verbatim copy)
    NO git, NO LLM)      minimal exact-match [[links]] (zero-LLM)
        │
        │   nightly cron 02:00  (or on_session_finalize)
        ▼
  batch_enrich.sh
   1. python scripts/build_wiki_index.py        # refresh INDEX of [[slugs]]
   2. LLM linker pass over inbox/ notes         # Karpathy: add inline [[links]]
   3. python scripts/wiki_graph_optimizer.py    # cross-note link proposals → apply
   4. move inbox/ → 05-knowledge/… (promote)
   5. bash scripts/git_autocommit.sh research "telegram capture <date>"
        ▼
  GitHub: Perryong/knowledge-agent   [PRIVATE]
```

## Step 1 — Connect Telegram
`hermes gateway setup` → choose Telegram → paste the BotFather token + your numeric user ID. In `~/.hermes/.env` (never committed):
```
TELEGRAM_BOT_TOKEN=123456789:ABCdef...      # from @BotFather
TELEGRAM_ALLOWED_USERS=<your numeric id>    # lock to yourself only
OBSIDIAN_VAULT_PATH=/home/you/COG-second-brain
GITHUB_PAT=<fine-grained, single-repo, contents:write>
```
Long-polling is the default (no inbound port). Use one bot token per gateway. [Source: hermes-agent docs/messaging/telegram | 2026-06-14 | confidence: high]

## Step 2 — The capture hook (real-time, lightweight)
In `~/.hermes/config.yaml`:
```yaml
hooks:
  post_llm_call:
    - command: "~/.hermes/agent-hooks/capture-note.sh"
      timeout: 30
```
`capture-note.sh` reads the turn JSON on stdin, writes a **new dated file** (never append — appending causes git merge conflicts), and does **no git and no LLM** here:
```bash
#!/usr/bin/env bash
set -euo pipefail
PAYLOAD="$(cat)"                        # turn JSON on stdin
RESP="$(jq -r '.response // .output // empty' <<<"$PAYLOAD")"
[ -z "$RESP" ] && exit 0
VAULT="${OBSIDIAN_VAULT_PATH:?}"
SLUG="$(date -u +%Y-%m-%d-%H%M)"
F="$VAULT/inbox/${SLUG}-telegram.md"
mkdir -p "$VAULT/inbox"
flock "/tmp/vault-write.lock" bash -c "cat > '$F' <<EOF
---
title: \"${SLUG} Telegram\"
date: $(date -u +%Y-%m-%d)
source: telegram
tags: [hermes, telegram, capture]
---

${RESP}
EOF"
```
Notes: write a note *about* the exchange, not a verbatim copy of personal chat; the `flock` serialises concurrent messages; verify `post_llm_call` actually fires on your installed Hermes version before relying on it (it's documented to fire after the final response; an early-version issue claimed it wasn't invoked). [Source: §factcheck | 2026-06-14 | confidence: high]

## Step 3 — Wiki-link generation (batch)
**This is where the "second brain" actually forms.** Three techniques: (A) LLM rewrite given the note + the allowed slug list — high precision, token cost; (B) entity/filename exact-match — zero-LLM, deterministic; (C) embedding/TF-IDF similarity for cross-note discovery. Your `wiki_graph_optimizer.py` **already implements C** (TF-IDF + tag Jaccard + title-mention, self-tuning ledger, broken-link detection). The only new code is a thin orchestrator that adds (A).

Batch pipeline (`batch_enrich.sh`, run by cron):
```bash
python scripts/build_wiki_index.py                       # 1. refresh slug index
python tools/llm_link.py inbox/*.md --slugs INDEX.md      # 2. (A) inline [[links]] — NEW thin script
python scripts/wiki_graph_optimizer.py analyze --apply    # 3. (C) cross-note links
# 4. promote inbox/ notes into 05-knowledge/ as appropriate, then:
bash scripts/git_autocommit.sh research "telegram capture $(date +%F)"
```
Canonicalize links on the filename stem (`[[slug|Display]]`); keep an `aliases:` frontmatter list; prefer a **stub** over a dangling link. Auto-accept optimizer proposals only at high confidence (e.g. score ≥ 0.45 with a title-mention signal); defer the rest. [Source: §wikilink-generation | 2026-06-14 | confidence: high]

## Step 4 — Auto-commit to GitHub
Use the existing `git_autocommit.sh` — it stages only the content allowlist (`00-inbox 01-daily 03-professional 04-projects 05-knowledge raw`), no-ops on empty diffs, writes a structured message, and never force-pushes. **One commit per batch**, not per message (session-flush). Recommended hardening:
- Add `git pull --rebase` + `git config rerere.enabled true` before push (multi-device safety) — the script currently lacks the pre-push pull.
- **Auth:** a repo-scoped **deploy key (SSH)** or a **fine-grained PAT** (single repo, contents read+write) in env. Never commit `.env`; add it to `.gitignore` *before* the first commit (history is forever); add a `gitleaks` pre-commit hook.
- Wrap note-writes + the commit in the same `flock` so the agent never writes mid-commit (avoids `.git/index.lock` races). [Source: §git-autocommit | 2026-06-14 | confidence: high]

## Real-time vs batch — the recommendation you asked for
**Batch wins, with a real-time capture pre-pass.** Capture each response to `inbox/` instantly (filesystem only); do all LLM linking + git in a nightly (or `on_session_finalize`) batch. Why:
- **Cost:** per-message linking reloads source context every call → ~10–20× the tokens of one nightly compile (≈ $1.5–3/mo on a 7B via OpenRouter vs ≈ $45–90/mo on a frontier model for the same volume).
- **Link quality:** a Telegram session is a *cluster* of related notes; only a batch that sees the whole cluster can wire the **within-session cross-links** — real-time linking literally can't, because the other notes don't exist yet at write time.
- **Git hygiene:** 1 commit/day vs 300+ chat-log micro-commits/month (git blame becomes meaningless).
- **Concurrency:** separating write-time (Hermes active) from compile+commit-time (Hermes quiet) removes the race.
- Every reference build agrees: the bundled `llm-wiki` skill says "batch the updates," `open-second-brain` runs a nightly "dream pass," `notes-bot` does nightly git backup, `kytmanov/obsidian-llm-wiki-local` separates compile from capture.

Only go real-time if Hermes must query a *just-written* note within the same conversation — and even then it can read the `inbox/` file directly without real-time linking/commit. [Source: §wikilink-generation, §reference-builds | 2026-06-14 | confidence: high]

## Pitfalls & must-dos
- **Keep the repo PRIVATE.** Committed Telegram content is permanent (GitHub delete ≠ gone from forks/caches). Audit visibility periodically; commit a note *about* the message, not the raw chat. [Source: gitguardian; soberhacker privacy | 2026-06-14 | confidence: high]
- **Secrets in env only.** A leaked `TELEGRAM_BOT_TOKEN` gives full control of the bot and all its messages (documented PII-leak incidents). `.gitignore` `.env`/`config.yaml`; rotate on any leak. [Source: gitguardian/telegram-bot-token | 2026-06-14 | confidence: high]
- **Concurrency.** Hermes serialises its SQLite state through a shared lock and does not per-file-lock note writes; stagger the cron so the linker/commit never runs mid-write; use atomic `.tmp`→rename; chain `compile && git_autocommit.sh`. [confidence: medium — mechanism verified, specific issue numbers unverified]
- **Storage.** Keep `~/.hermes` and the vault on **local block storage (ext4)**, not NFS/SMB/WSL1 — SQLite WAL fails on networked filesystems. [confidence: medium]
- **Digital graveyard (the real long-term risk).** Notes pile up unused. Add a **quality gate**: only persist messages you flag, or that Hermes judges to carry durable insight; everything else stays in rolling memory. Weekly lint (`wiki_graph_optimizer.py` / llm-wiki `lint`) for orphans/stale/broken; human governance pages (`overview.md`, `questions.md`, `decisions.md`). [Source: mono-software, starmorph | 2026-06-14 | confidence: high]
- **Rate limits** are not the binding constraint for single-user (Telegram 30 msg/s); LLM inference speed is.

## Reference builds worth copying
- **itechmeat/open-second-brain** — Hermes + Obsidian, file-resident memory via a `brain_feedback` MCP tool, deterministic nightly "dream pass." Closest Hermes-native model.
- **NousResearch bundled `research/llm-wiki` skill** — Karpathy 3-layer wiki, ≥2 `[[links]]`/page, built-in lint. Use as the compile step.
- **kytmanov/obsidian-llm-wiki-local** — local (Ollama) Karpathy wiki, Ingest→Compile→Review, auto-commits with `[olw]` prefix + `olw undo`. Maps directly onto the batch step.
- **fahadhasin/notes-bot** / **smixs/agent-second-brain** — real Telegram→markdown→nightly-git pipelines (minus wiki-linking); proof the batch-commit shape works.

## Open questions
- Verify `post_llm_call` fires on *your* installed Hermes version (documented behaviour; an early-version issue claimed otherwise). If not, fall back to `on_session_finalize` (per-conversation) or a system-prompt instruction telling the model to call a save tool each turn.
- Exact files written by `hermes memory setup --provider obsidian` are provider-internal — confirm by inspecting your vault after a turn before depending on that path vs the custom-hook path.
- Whether to route writes through the `research_vault` MCP (enforced frontmatter + allowlisted commit) vs a raw shell hook — the MCP is cleaner if you want every write governed.

## Sources
Primary (lead-verified 2026-06-14): hermes-agent.nousresearch.com/docs/user-guide/features/hooks · …/messaging/telegram · github.com/NousResearch/hermes-agent (tree/main/skills, note-taking/obsidian, research/llm-wiki) · this repo's `scripts/git_autocommit.sh`, `scripts/build_wiki_index.py`, `scripts/wiki_graph_optimizer.py`, `mcp/research_vault/README.md`.
Secondary/landscape: github.com/itechmeat/open-second-brain · github.com/kytmanov/obsidian-llm-wiki-local · github.com/nashsu/llm_wiki · github.com/ar9av/obsidian-wiki · github.com/fahadhasin/notes-bot · github.com/smixs/agent-second-brain · gist.github.com/karpathy (LLM Wiki) · gitguardian.com/remediation/telegram-bot-token · mono-software.com LLM-Wiki PKM.
Full per-claim sources + fact-check verdicts in `raw/research/2026-06-14-hermes-telegram-secondbrain/`.

---
*Confidence: high on the mechanism (Telegram channel, `post_llm_call` hook, bundled skills, this repo's scripts/MCP — all primary-verified) and the batch recommendation (corroborated + cost/concurrency/quality reasoning). Medium on concurrency/storage cautions where specific GitHub issue numbers were unverifiable — the mechanisms hold, the issue citations were dropped.*

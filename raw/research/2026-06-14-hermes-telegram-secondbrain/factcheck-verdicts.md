# Fact-Check Verdicts — Hermes + Telegram Second Brain

*Lead-verified 2026-06-14 via direct WebFetch of primary sources (githubusercontent raw docs + repo tree).*

## CONFIRMED (primary)
- **`post_llm_call` hook is real and is the right hook.** Official docs: "fires once per turn, after the tool-calling loop completes and the agent has produced a final response. Only triggers on successful turns." [hermes-agent docs hooks.md | 2026-06-14]
- Full hook set incl. pre/post_tool_call, pre/post_llm_call, on_session_start/end/finalize/reset, subagent_stop, pre_gateway_dispatch, transform_llm_output/transform_tool_result. Shell hooks configured in `~/.hermes/config.yaml` (`hooks:` block), JSON stdin/stdout. **Gateway hooks** (Telegram/Discord/Slack/WhatsApp/Teams) via `~/.hermes/hooks/<name>/HOOK.yaml` + `handler.py`. [same]
- **Telegram:** `hermes gateway setup`; env `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`; built on python-telegram-bot; long-polling default; `TELEGRAM_WEBHOOK_URL` for webhook. [hermes-agent docs messaging/telegram.md]
- **Bundled skills:** `/skills` contains `note-taking` and `research` categories (obsidian + llm-wiki subdirs). [github.com/NousResearch/hermes-agent/tree/main/skills]
- **This repo's assets (read directly):** `scripts/git_autocommit.sh` (allowlist stage + non-force push + empty guard), `scripts/build_wiki_index.py` (rebuild INDEX of [[wiki-links]]), `scripts/wiki_graph_optimizer.py` (TF-IDF+tag+title scoring, ledger, proposals/apply), `mcp/research_vault/server.py` (save_research_note / link_wiki_notes / commit_and_push). [direct read]

## CORRECTED / SOFTENED
- Config file for shell hooks: official doc says `~/.hermes/config.yaml` (a `cli-config.yaml.example` also exists) — use config.yaml.
- "#2817: post_llm_call documented but never invoked" — official doc documents it as firing after the final response → treat as version-specific/likely-fixed; VERIFY on your installed version, but do not present as a blocking risk.
- Issue-number-specific claims (#34444 single SessionDB._lock, #22032 SQLite-on-NFS, #31054, #25204) — mechanisms are plausible and worth heeding as general cautions, but the specific issue numbers are UNVERIFIED; present mechanisms generically, not as cited issues.

## NET
Both halves of the pipeline already exist: Hermes (Telegram channel + post_llm_call/gateway hooks + bundled note-taking/llm-wiki skills) and this repo (wiki index/optimizer + git_autocommit + research_vault MCP). The only new code is a thin capture hook + a nightly batch orchestrator. Batch-over-real-time is corroborated by every reference build + cost/concurrency/commit-noise arguments.

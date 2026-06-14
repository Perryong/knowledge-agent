# Hermes Agent — Telegram Connection + Post-Response Hook

*Research date: 2026-06-14 | Live web, ~18 sources | reconstructed by lead (subagent file write blocked)*

## A. Telegram channel
- Telegram is a **first-class channel** (built on python-telegram-bot), the "Telegram messaging gateway." Channels: telegram, discord, whatsapp, slack, signal, homeassistant, qqbot, teams, google_chat. [hermes-agent.nousresearch.com/docs/.../telegram; .../configuration | 2026]
- Flow: Telegram lib → adapter wraps as `MessageEvent` → gateway dispatcher → cached per-session `AIAgent` → `run_conversation` → adapter send. Telegram + TUI share one SQLite table scoped by `session_id`. [hermes-agent.ai/blog/hermes-agent-telegram-setup | 2026]
- Gateway exposes OpenAI-compatible API on **:8642**, web dashboard on **:9119**. [evomap.ai/blog/hermes-agent-gateway-telegram-slack | 2026]
- Setup: BotFather `/newbot` → get numeric user ID → `hermes gateway setup` wizard (writes config) → start gateway. Docker: `docker run -it --rm -v ~/.hermes:/opt/data nousresearch/hermes-agent setup`.
- Env: `TELEGRAM_BOT_TOKEN=...`, `TELEGRAM_ALLOWED_USERS=<numeric ids>` (+ group variants). One bot token per gateway (Telegram rejects concurrent polling). Files out via `MEDIA:/path` tags. [remoteopenclaw.com; github issue #31054 | 2026]

## B. Hook events (the interception point)
- Valid shell hook events (in `cli-config.yaml`): `pre_tool_call`, `post_tool_call`, `pre_llm_call`, **`post_llm_call`**, `pre_api_request`, `post_api_request`, `on_session_start`, `on_session_end`, **`on_session_finalize`**, `on_session_reset`, `subagent_start`, `subagent_stop`. [hermes-agent.nousresearch.com/docs/.../hooks | 2026]
- **`post_llm_call`** = fires after each LLM response, within the turn → closest to "after agent responded to user." **`on_session_finalize`** = per-conversation end (gateway pairs with on_session_reset). "Gateway hooks" fire only in gateway sessions (Telegram/Discord/Slack/etc.).
- Shell hook mechanics: subprocess (`shell=False`, `shlex.split`), JSON payload to stdin, stdout JSON back; can block a tool call or inject next-turn context. Python plugin hooks via `ctx.register_hook()`.
- v2026.5.7 added `transform_llm_output` plugin hook (reshape output before it reaches the conversation).
- Config: `cli-config.yaml`:
```yaml
hooks:
  post_llm_call:
    - command: "~/.hermes/agent-hooks/capture-note.sh"
      timeout: 30
```
- ⚠️ **RISK Claim C8:** Issue #2817 — `pre_llm_call/post_llm_call/on_session_start/on_session_end` reported "documented but never invoked" in early versions; v0.16.x status unconfirmed → MUST TEST. [github #2817]
- ⚠️ **RISK Claim C9:** Issue #25204 (v0.13.0) — some shell hooks don't fire reliably in `chat -q` kanban-worker context; gateway context unspecified. [github #25204]

## C. Skills (note: NOT a per-turn trigger)
- Each skill = `SKILL.md` (YAML frontmatter `name` slug + `description`, optional `version`/`platforms`/`config`/`env`) + markdown body. Auto-loads on session start.
- **Skills are model-invoked by matching `description` to context — there is NO `always_on`/`per_turn`/`trigger` key.** So the reliable mechanical "run after every response" path is a **HOOK**, not a skill. A skill can be the *target* a hook calls. [hostinger.com what-are-hermes-agent-skills; agensi.io skill-md-format | 2026]
- Self-improving loop: after a complex task (~5+ tool calls) the agent autonomously writes a new SKILL.md via `skill_manage`.

## D. Config & memory
- Resolution: CLI → `config.yaml` → `.env` → defaults; keys in `~/.hermes/.env`, settings in `~/.hermes/config.yaml`; root `HERMES_HOME` (default ~/.hermes).
- Memory: `/memory pending|approve|reject`; memory tool actions add/replace/remove (no read — injected into system prompt); `write_approval: false` default (agent writes freely); periodic "nudges" to consolidate/persist; external providers inject `<memory-context>` block.

## E. Native second-brain: bundled llm-wiki [KEY]
- **PR #5100 added a bundled `llm-wiki` skill** (Karpathy LLM Wiki pattern) — builds/maintains interlinked markdown KB. Lives at `skills/research/llm-wiki/SKILL.md`. [github #5100; .../blob/main/skills/research/llm-wiki/SKILL.md]
- Architecture: 3-layer (immutable raw sources → agent-owned wiki pages → schema config); YAML frontmatter + `[[wikilinks]]`; index = one line wikilink+summary; Wiki Log `## [YYYY-MM-DD] action | subject` (ingest/update/query/lint/create/archive/delete). `WIKI_PATH` env (default ~/wiki). [medium jsong_49820 Apr 2026; github Robs87/llm-wiki v2.1.0]
- Community combo: **r0b0tlab/llm-wiki_obsidian_hermes_r0b0tlabbra1n** — filesystem-first LLM-Wiki + Obsidian + Hermes memory; markdown source of truth, SQLite FTS5. Confirms pattern is proven.
- Bundled Obsidian skill: read/search/create notes in a vault, link agent output to the graph.

## Synthesis (best path)
- **Per-turn note writing = `post_llm_call` shell hook** → shell script reads JSON payload, extracts response text, writes markdown note, runs git commit. Fallback: `on_session_finalize` (per-conversation) or a system-prompt instruction telling the model to call a note-writing tool each turn.
- Close the full loop: set **`WIKI_PATH` = the git vault**, enable the bundled **llm-wiki** skill, add a **`post_llm_call`** (or `on_session_finalize`) hook that commits: *Telegram msg → reply → hook fires → script writes `[[wiki-link]]` note → git commit+push.*
- VERIFY post_llm_call actually fires on v0.16.x before relying on it (#2817).

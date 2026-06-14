# Auto-Commit-to-GitHub for a Markdown Vault

*Research date: 2026-06-14 | Live web | reconstructed by lead (subagent file write blocked)*

**Baseline:** `scripts/git_autocommit.sh` already does allowlist staging (`00-inbox 01-daily 03-professional 04-projects 05-knowledge raw`), empty-commit guard, structured message (type+title+date+files), non-force push; safe from a Stop hook. [direct read | 2026-06-14]

## A. Pattern tradeoffs
- **Post-write hook (agent calls git after each write):** simplest, zero extra process, but one commit per message = noisy + race risk on concurrent messages. Mitigate via session-flush (write all notes, one commit at session end — the script's intent). [git-scm.com/docs/githooks]
- **FS watcher → debounced commit:** `gwatch` (30s quiet-timer then commit), Python `watchdog` (recursive, *.md filter, debounce, shell callback), `chokidar` (Node), `inotifywait` (Linux). Decoupled from agent; needs a daemon. [safjan.com/git-autocommit-on-file-changes; github.com/gorakhargosh/watchdog]
- **Cron / systemd timer batch:** run git_autocommit.sh every N min; empty-commit guard = no-op if unchanged. systemd > cron (journalctl, OnCalendar, coalescing). Up to N-min latency (note safe on disk immediately). Simplest for a Linux bot host. [cavecreekcoffee.com systemd-timers; botmonster.com]
- **Obsidian Git (Vinzent03/obsidian-git, moved from denolehov Jul 2024):** desktop interval auto-commit+sync, auto-pull on startup, custom message template. **Mobile severely limited** (isomorphic-git: no SSH, no rebase, no submodules, status check ~3m40s, "auto backup after edits" broken on Android). **Irrelevant for a headless server bot** (needs Obsidian open) — only matters if a human also edits in Obsidian. [github.com/Vinzent03/obsidian-git; forum.obsidian.md/t/76822]
- **GitHub Actions on push:** fires AFTER a push; not a commit mechanism. Good for post-commit: lint markdown, rebuild wiki index, Telegram success ping, deploy site.
- **Relevance:** for the Hermes server bot, use agent session-flush OR a watchdog/systemd batch; Obsidian Git is out.

## B. Debounce / batching / commit messages
| Strategy | Mechanism | Window |
|---|---|---|
| gwatch | change resets 30s timer | 30s |
| **Agent session-flush (recommended)** | accumulate, write notes, 1 commit at session end | per conversation |
| cron/systemd batch | fixed interval | 5-15 min |
| watchdog cooldown | event handler + debounce | custom |
- Squashing headless is fiddly (`rebase -i`/`merge --squash`) — better to avoid per-message commits.
- **LLM commit messages:** llm-commit (GNtousakis), gh-commit, Karpathy gist (`git diff --staged | llm "write commit message"`), harper.blog prepare-commit-msg hook, GenAIScript. For Hermes: pass the user message + file list to an LLM, feed result as `$2` title to git_autocommit.sh. [github.com/GNtousakis/llm-commit; gist.github.com/karpathy/1dd0294ef...; harper.blog 2024-03-11]

## C. Auth for headless push
- **Deploy key (SSH) — best for single-repo personal vault:** repo-scoped (limited blast radius), enable write on the key, private key on server (not in repo), `git remote set-url origin git@github.com:Perryong/knowledge-agent.git`, point at key via `~/.ssh/config` or `GIT_SSH_COMMAND`. [docs.github.com/.../managing-deploy-keys]
- **Fine-grained PAT:** restrict to the one repo, Contents read+write + Metadata read, set expiry; use `https://oauth2:{PAT}@github.com/...` or `~/.netrc`. Easiest. [medium fine-grained-github-tokens]
- **GitHub App:** short-lived 1h auto-refreshed tokens; most secure; overkill for personal bot.
| Method | Scope | Setup | Verdict |
|---|---|---|---|
| Deploy key SSH | 1 repo | low | best single-repo bot |
| Fine-grained PAT | 1+ | very low | good, easiest |
| GitHub App | 1+ | high | overkill |
- **Secrets rules:** never commit `.env`/PAT/bot token; add `.env` to `.gitignore` BEFORE first commit (else it's in history forever); read via `os.getenv`; ship `.env.example`; git_autocommit.sh allowlist is a safety net not a substitute; rotate on leak. [blog.gitguardian.com secure-your-secrets; salferrarello.com add-env-to-gitignore]

## D. Conflict handling & concurrent-write safety
- **Headless push:** `git pull --rebase origin main && git push`; `git config --global pull.rebase true`; `git config --global rerere.enabled true` (remembers conflict resolutions). **GAP: git_autocommit.sh has NO pull --rebase before push** — add it for multi-device (bot + manual Obsidian). [medium git-pull-merge-conflicts]
- **Lock file `.git/index.lock`:** two git processes collide ("cannot lock ref"); SIGKILL leaves stale lock; cleanup `[ -f .git/index.lock ] && rm .git/index.lock` only if no git running. [oneuptime.com 2026-01-24; graphite.com cannot-lock-ref]
- **Prevent agent writes during commit — filelock pattern:**
```python
from filelock import FileLock
lock = FileLock("/tmp/vault.lock")
def write_note(p,c):
    with lock: write_file(p,c)
def commit_vault():
    with lock: subprocess.run(["bash","scripts/git_autocommit.sh",...])
```
- **Atomic writes:** write temp file on same FS then `os.replace()` (atomic rename); commit after rename. [jokeyrhyme.github.io 2017-08-22 | MEDIUM]

## Recommendation
Session-flush: agent writes all notes for a conversation, then ONE `git_autocommit.sh <type> "<LLM summary>"` call (add `git pull --rebase` + `rerere` to the script). Auth via deploy key or fine-grained PAT in env (never in repo). Wrap note-writes + commit in a `filelock`. Skip Obsidian Git for the bot.

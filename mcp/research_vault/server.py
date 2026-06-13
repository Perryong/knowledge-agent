#!/usr/bin/env python3
"""research_vault MCP server.

Exposes the second-brain's vault operations as governed MCP tools so that ANY
MCP client (Claude Code, Cursor, Gemini CLI, Codex, a custom agent) can save
research notes, wire up wiki-links, and version the result to GitHub — without
each client reimplementing the file/git logic.

This is the OPTIONAL path. Claude Code can already do all of this with its
built-in Write/Read/Bash tools, so you do NOT need this MCP for the pipeline to
work. Build it when you want (a) reusable, audited vault tools shared across
several agents/clients, or (b) a single enforcement point for the vault's
conventions (frontmatter shape, allowlisted commit dirs).

Run locally over stdio:
    uv run research_vault            # or: python server.py
Register in Claude Code:
    claude mcp add research-vault -- uv run --directory mcp/research_vault research_vault
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import date, datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# VAULT_ROOT defaults to the current working dir; override via env when the
# client launches the server from elsewhere.
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", os.getcwd())).resolve()

# Same allowlist the shell script uses — the single enforcement point for
# what is safe to commit.
COMMIT_ALLOWLIST = [
    "00-inbox", "01-daily", "03-professional",
    "04-projects", "05-knowledge", "raw",
]

mcp = FastMCP("research-vault")


def _safe_path(rel_path: str) -> Path:
    """Resolve a vault-relative path and refuse anything that escapes the vault."""
    target = (VAULT_ROOT / rel_path).resolve()
    if not str(target).startswith(str(VAULT_ROOT)):
        raise ValueError(f"Refusing path outside vault: {rel_path}")
    return target


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


@mcp.tool()
def save_research_note(
    title: str,
    body_markdown: str,
    folder: str = "05-knowledge/resources",
    tags: list[str] | None = None,
    confidence: str = "medium",
    related: list[str] | None = None,
) -> str:
    """Write a research report into the vault with COG-standard frontmatter.

    Args:
        title: Human-readable note title.
        body_markdown: The note body (sections, citations, sources). No frontmatter.
        folder: Vault-relative target folder. Defaults to 05-knowledge/resources.
        tags: Topic tags (the 'research' tag is added automatically).
        confidence: Overall confidence — high | medium | low.
        related: Note names to wiki-link as related, e.g. ["llm-market", "scout"].

    Returns:
        The vault-relative path of the created note.
    """
    tags = tags or []
    related = related or []
    slug = _slugify(title)
    folder_path = _safe_path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    note_path = folder_path / f"{slug}.md"

    related_fm = ", ".join(f'"[[{r}]]"' for r in related)
    all_tags = ", ".join(dict.fromkeys(["research", *tags]))
    frontmatter = (
        "---\n"
        f"title: {title}\n"
        "type: research-report\n"
        f"created: {date.today().isoformat()}\n"
        f"tags: [{all_tags}]\n"
        "status: complete\n"
        f"confidence: {confidence}\n"
        f"related: [{related_fm}]\n"
        "---\n\n"
    )
    note_path.write_text(frontmatter + body_markdown.strip() + "\n", encoding="utf-8")
    return str(note_path.relative_to(VAULT_ROOT))


@mcp.tool()
def link_wiki_notes(source_note: str, target_notes: list[str]) -> str:
    """Append a `## Related` section of [[wiki-links]] to an existing note.

    Args:
        source_note: Vault-relative path of the note to edit.
        target_notes: Note names (without .md) to link to.

    Returns:
        Confirmation with the number of links added.
    """
    path = _safe_path(source_note)
    if not path.exists():
        return f"ERROR: note not found: {source_note}"
    links = "\n".join(f"- [[{t}]]" for t in target_notes)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n## Related\n{links}\n")
    return f"OK: added {len(target_notes)} wiki-link(s) to {source_note}"


@mcp.tool()
def commit_and_push(session_type: str, title: str) -> str:
    """Stage allowlisted content dirs, commit with a structured message, and push.

    Mirrors scripts/git_autocommit.sh. Never stages .claude/ or secrets, never
    force-pushes, and no-ops cleanly when there is nothing to commit.

    Args:
        session_type: e.g. 'research' or 'resume'.
        title: Short human title for the commit subject.

    Returns:
        A status string with the commit hash, or a clear failure reason.
    """
    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args], cwd=VAULT_ROOT,
            capture_output=True, text=True,
        )

    if git("rev-parse", "--is-inside-work-tree").returncode != 0:
        return "NOT_A_GIT_REPO: run git init and add a remote first"

    for d in COMMIT_ALLOWLIST:
        if (VAULT_ROOT / d).exists():
            git("add", "--", d)
    if (VAULT_ROOT / "05-knowledge/INDEX.md").exists():
        git("add", "--", "05-knowledge/INDEX.md")

    if git("diff", "--cached", "--quiet").returncode == 0:
        return "NOTHING_TO_COMMIT: vault content unchanged"

    files = git("diff", "--cached", "--name-only").stdout.strip().splitlines()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = "\n".join(f"  - {f}" for f in files)
    msg = (
        f"{session_type}: {title} ({stamp})\n\n"
        f"Auto-committed by research_vault MCP. {len(files)} file(s):\n{body}\n"
    )
    if git("commit", "-m", msg).returncode != 0:
        return "COMMIT_FAILED"

    short = git("rev-parse", "--short", "HEAD").stdout.strip()
    push = git("push")
    if push.returncode == 0:
        return f"OK: committed {len(files)} file(s), pushed (commit {short})"
    return (
        f"COMMITTED_NO_PUSH: commit {short} created locally; push failed -> "
        f"{push.stderr.strip()}. Set an upstream then run git push."
    )


if __name__ == "__main__":
    # stdio transport for local clients (Claude Code, Cursor, etc.)
    mcp.run()

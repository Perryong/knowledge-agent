# research_vault MCP server

A small [Model Context Protocol](https://modelcontextprotocol.io) server that exposes the second-brain's vault operations as governed tools. It's **optional** — see the "Do I need an MCP?" section in the project README. Build/run it when you want reusable, audited vault tools shared across multiple agents or clients (Claude Code, Cursor, Gemini CLI, Codex).

## Tools

| Tool | What it does |
|------|--------------|
| `save_research_note` | Writes a markdown note into the vault with COG-standard YAML frontmatter (title, type, created, tags, confidence, related wiki-links). |
| `link_wiki_notes` | Appends a `## Related` section of `[[wiki-links]]` to an existing note so the Obsidian graph connects. |
| `commit_and_push` | Stages only allowlisted content dirs, commits with a structured message, and pushes. No-ops cleanly if nothing changed. Never force-pushes. |

## Run it

```bash
# from the repo root
cd mcp/research_vault
uv sync            # or: pip install -e .
uv run research_vault    # starts the server over stdio
```

## Register in Claude Code

```bash
# point VAULT_ROOT at your vault so writes land in the right place
claude mcp add research-vault \
  --env VAULT_ROOT=/absolute/path/to/COG-second-brain \
  -- uv run --directory /absolute/path/to/mcp/research_vault research_vault
```

Then in a session: `/mcp` lists connected servers, and the tools appear as `research-vault:save_research_note`, etc. Your orchestrator commands can call these instead of the built-in Write/Bash tools if you want every write to go through the enforced frontmatter + commit allowlist.

## How it was built (the pattern)

1. `FastMCP("research-vault")` creates the server.
2. Each `@mcp.tool()`-decorated function becomes a tool. The **docstring is the tool description** the model reads, and the **type hints become the input schema** — so write clear docstrings and type every argument.
3. `_safe_path()` refuses any path that escapes the vault — always validate paths in tools that touch the filesystem.
4. `mcp.run()` serves over stdio (best for local clients). For a remote/hosted server you'd use streamable HTTP instead.

To extend: add another `@mcp.tool()` function (e.g. `open_github_pr`, `search_notes`) with a typed signature and a docstring, restart the client, and it appears automatically.

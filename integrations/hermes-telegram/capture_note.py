#!/usr/bin/env python3
"""capture_note.py — body of the Hermes `post_llm_call` hook.

Reads the turn JSON on stdin and writes the agent's final response as a NEW dated
raw note in raw/hermes-inbox/. No external deps (no jq). Atomic write + a unique
filename (timestamp + pid) means git never sees a half-written file and concurrent
turns never collide — so no lockfile is needed. NO git, NO LLM here; those run in
the nightly batch_enrich.sh.

Field names in the payload vary by Hermes version. Set HERMES_CAPTURE_DEBUG=1 to
dump the raw payload to a log and confirm which key holds the response.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def pick(data: dict, *dotted_keys: str) -> str:
    """Return the first non-empty string found at any of the dotted key paths."""
    for key in dotted_keys:
        cur = data
        ok = True
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and isinstance(cur, str) and cur.strip():
            return cur.strip()
    return ""


def main() -> None:
    raw = sys.stdin.read()

    if os.environ.get("HERMES_CAPTURE_DEBUG") == "1":
        log = os.environ.get("HERMES_CAPTURE_DEBUG_LOG", "/tmp/hermes-payload.log")
        try:
            with open(log, "a", encoding="utf-8") as f:
                f.write(raw + "\n---\n")
        except OSError:
            pass

    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return
    if not isinstance(data, dict):
        return

    resp = pick(data, "response", "output", "final_response", "assistant_message",
                "message.content", "message", "content", "text")
    if not resp:  # interrupted/empty turn -> no-op
        return

    channel = pick(data, "channel", "platform", "source") or "telegram"
    vault = Path(os.environ.get("OBSIDIAN_VAULT_PATH")
                 or os.environ.get("VAULT_ROOT") or os.getcwd())
    inbox = vault / "raw" / "hermes-inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    slug = now.strftime("%Y-%m-%d-%H%M%S")
    dest = inbox / f"{slug}-{channel}-{os.getpid()}.md"
    frontmatter = (
        "---\n"
        f'title: "{slug} {channel} capture"\n'
        f"date: {now:%Y-%m-%d}\n"
        f'time: "{now:%H:%M:%S}Z"\n'
        f"source: {channel}\n"
        "status: raw\n"
        f"tags: [hermes, {channel}, capture]\n"
        "---\n\n"
    )
    tmp = dest.with_suffix(".md.tmp")
    tmp.write_text(frontmatter + resp + "\n", encoding="utf-8")
    os.replace(tmp, dest)  # atomic publish

    try:
        with open(os.environ.get("HERMES_CAPTURE_LOG", "/tmp/hermes-capture.log"),
                  "a", encoding="utf-8") as f:
            f.write(f"captured: {dest}\n")
    except OSError:
        pass


if __name__ == "__main__":
    main()

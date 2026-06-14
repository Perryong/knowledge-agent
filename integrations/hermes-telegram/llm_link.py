#!/usr/bin/env python3
"""llm_link.py — promote raw Hermes captures into wiki-linked knowledge notes.

Reads new capture notes from raw/hermes-inbox/, inserts [[wiki-links]] pointing at
EXISTING vault notes, and writes the enriched copy into 05-knowledge/captures/ so
build_wiki_index.py and wiki_graph_optimizer.py can see it. The raw original is kept
(Raw-First protocol) and marked status: processed.

Two linkers, auto-selected:
  * default (stdlib only, free, deterministic): exact title/slug phrase matching.
  * LLM (opt-in): set HERMES_LINK_API_KEY (+ _BASE, _MODEL) for an OpenAI-compatible
    pass that also catches paraphrases. Links are post-filtered so only EXISTING
    slugs survive — the model can never invent a link target.

Usage:
  python3 integrations/hermes-telegram/llm_link.py            # process inbox -> captures
  python3 integrations/hermes-telegram/llm_link.py --dry-run  # report, write nothing
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

VAULT = Path(os.environ.get("VAULT_ROOT", os.getcwd())).resolve()
INBOX = VAULT / "raw" / "hermes-inbox"
OUTDIR = VAULT / "05-knowledge" / "captures"
SCAN_DIRS = ["05-knowledge", "03-professional", "04-projects"]
SKIP = {"INDEX.md"}
MAX_LINKS = int(os.environ.get("HERMES_LINK_MAX", "12"))

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
EXISTING_LINK_RE = re.compile(r"\[\[[^\]]+\]\]")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def slug_of(path: Path) -> str:
    return path.stem


def humanize(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ")


def build_candidates() -> dict[str, str]:
    """Map lowercased display phrase -> slug for every existing note in the vault."""
    cands: dict[str, str] = {}
    for d in SCAN_DIRS:
        base = VAULT / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            if p.name in SKIP:
                continue
            phrase = humanize(slug_of(p)).lower().strip()
            if len(phrase) >= 3:
                cands.setdefault(phrase, slug_of(p))
    return cands


def split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return "---" + parts[1] + "---", parts[2]
    return "", text


def _protected(body: str) -> list[tuple[int, int]]:
    spans = [(m.start(), m.end()) for m in FENCE_RE.finditer(body)]
    spans += [(m.start(), m.end()) for m in EXISTING_LINK_RE.finditer(body)]
    return spans


def link_exact(body: str, cands: dict[str, str], self_slug: str) -> str:
    """Deterministic: wrap the first whole-phrase occurrence of each known title."""
    count = 0
    for phrase in sorted(cands, key=len, reverse=True):  # specific phrases first
        if count >= MAX_LINKS:
            break
        slug = cands[phrase]
        if slug == self_slug:
            continue
        pat = re.compile(r"(?<![\w\[])(" + re.escape(phrase) + r")(?![\w\]])", re.IGNORECASE)
        spans = _protected(body)
        m = pat.search(body)
        while m and any(a <= m.start() < b for a, b in spans):
            m = pat.search(body, m.end())
        if not m:
            continue
        matched = m.group(1)
        repl = f"[[{slug}|{matched}]]" if matched.lower() != slug.lower() else f"[[{slug}]]"
        body = body[: m.start()] + repl + body[m.end():]
        count += 1
    return body


def link_llm(body: str, cands: dict[str, str], self_slug: str) -> str:
    base = os.environ["HERMES_LINK_API_BASE"].rstrip("/")
    key = os.environ["HERMES_LINK_API_KEY"]
    model = os.environ.get("HERMES_LINK_MODEL", "gpt-4o-mini")
    allowed = sorted({s for s in cands.values() if s != self_slug})
    sys_p = (
        "You add Obsidian wiki-links to a markdown note body. Insert [[slug]] or "
        "[[slug|surface text]] ONLY for concepts that match a slug in the ALLOWED list. "
        "Never invent slugs. Do not change wording, headings, lists, or code blocks. "
        "Return ONLY the rewritten body — no commentary, no code fences."
    )
    usr = f"ALLOWED SLUGS:\n{json.dumps(allowed)}\n\nNOTE BODY:\n{body}"
    payload = json.dumps(
        {"model": model, "temperature": 0,
         "messages": [{"role": "system", "content": sys_p},
                      {"role": "user", "content": usr}]}
    ).encode()
    req = urllib.request.Request(
        base + "/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.load(r)
        out = data["choices"][0]["message"]["content"].strip()
        out = re.sub(r"^```[a-z]*\n?|\n?```$", "", out).strip()
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"  ! LLM link failed ({e}); falling back to exact match", file=sys.stderr)
        return link_exact(body, cands, self_slug)

    # Safety net: strip any link whose target slug doesn't actually exist.
    allowed_set = set(cands.values())

    def keep(m: re.Match) -> str:
        inner = m.group(1).split("|")[0].strip()
        return m.group(0) if inner in allowed_set else m.group(1).split("|")[-1]

    return WIKILINK_RE.sub(keep, out)


def main() -> None:
    dry = "--dry-run" in sys.argv
    if not INBOX.is_dir():
        print("no inbox; nothing to do")
        return
    notes = sorted(INBOX.glob("*.md"))
    if not notes:
        print("inbox empty")
        return

    cands = build_candidates()
    use_llm = bool(os.environ.get("HERMES_LINK_API_KEY"))
    mode = "LLM" if use_llm else "exact-match"
    OUTDIR.mkdir(parents=True, exist_ok=True)

    done = 0
    for p in notes:
        text = p.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)
        self_slug = slug_of(p)
        linked = link_llm(body, cands, self_slug) if use_llm else link_exact(body, cands, self_slug)
        n_links = linked.count("[[")
        out_fm = fm.replace("status: raw", "status: processed") if fm else fm
        out_text = ((out_fm + "\n" + linked).strip() + "\n") if out_fm else (linked.strip() + "\n")
        out_path = OUTDIR / p.name

        if dry:
            print(f"DRY [{mode}] {p.name}: {n_links} links -> {out_path.relative_to(VAULT)}")
            continue

        tmp = out_path.with_suffix(".md.tmp")
        tmp.write_text(out_text, encoding="utf-8")
        tmp.replace(out_path)  # atomic
        p.write_text(text.replace("status: raw", "status: processed", 1), encoding="utf-8")
        done += 1
        print(f"linked [{mode}] {p.name} ({n_links} links)")

    print(f"OK: processed {done} note(s) into {OUTDIR.relative_to(VAULT)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""wiki_graph_optimizer.py — a self-improving wiki-link engine for the COG vault.

It does three jobs across runs, and gets better at the third one over time:

  analyze   Scan every note, build the [[wiki-link]] graph, and detect problems:
            broken links, orphan notes, and high-value MISSING links between
            related notes. Writes human + machine proposal files.

  apply     Read a reviewed proposals file (each item marked accept/reject) and
            (a) insert the accepted links into the notes' `## Related` sections,
            (b) RECORD the decisions into the memory ledger, and
            (c) NUDGE its own scoring weights + threshold toward what got accepted.
            This feedback loop is what makes the agent self-improving.

  status    Print the current ledger (weights, threshold, acceptance stats).

Stdlib only — no external deps. Self-improvement is transparent: every weight
change is written to .claude/memory/wiki-link-memory.json and logged.

Usage:
  python3 scripts/wiki_graph_optimizer.py analyze
  python3 scripts/wiki_graph_optimizer.py apply  --proposals /tmp/wiki-proposals.json
  python3 scripts/wiki_graph_optimizer.py status
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

VAULT = Path(os.environ.get("VAULT_ROOT", os.getcwd())).resolve()
LEDGER = VAULT / ".claude" / "memory" / "wiki-link-memory.json"
PROPOSALS_MD = Path("/tmp/wiki-proposals.md")
PROPOSALS_JSON = Path("/tmp/wiki-proposals.json")

CONTENT_DIRS = ["03-professional", "04-projects", "05-knowledge"]
SKIP_FILES = {"INDEX.md"}
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
FM_TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)
FM_TAGS_RE = re.compile(r"^tags:\s*\[(.*?)\]", re.MULTILINE)
TOKEN_RE = re.compile(r"[a-z][a-z0-9\-]{2,}")

STOPWORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "any", "can", "her",
    "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "its",
    "may", "new", "now", "old", "see", "two", "way", "who", "did", "yes", "this",
    "that", "with", "from", "have", "they", "will", "your", "what", "when", "into",
    "than", "then", "them", "some", "more", "most", "such", "only", "also", "been",
    "were", "which", "their", "there", "would", "could", "about", "these", "those",
    "type", "tags", "created", "status", "confidence", "title", "related", "source",
}

DEFAULT_LEDGER = {
    "version": 1,
    "weights": {"tfidf": 1.0, "tag_overlap": 1.2, "title_mention": 2.0},
    "threshold": 0.22,
    "rejected_pairs": [],
    "accepted_pairs": [],
    "aliases": {},
    "stats": {"runs": 0, "proposed": 0, "accepted": 0, "rejected": 0},
    "log": [],
}


# --------------------------------------------------------------------------- #
# Ledger (the agent's persistent memory)
# --------------------------------------------------------------------------- #
def load_ledger() -> dict:
    if LEDGER.exists():
        try:
            data = json.loads(LEDGER.read_text(encoding="utf-8"))
            for k, v in DEFAULT_LEDGER.items():
                data.setdefault(k, v)
            return data
        except json.JSONDecodeError:
            pass
    return json.loads(json.dumps(DEFAULT_LEDGER))


def save_ledger(ledger: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def pair_key(a: str, b: str) -> list[str]:
    return sorted([a, b])


# --------------------------------------------------------------------------- #
# Vault scan
# --------------------------------------------------------------------------- #
def read_note(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    title, tags, body = path.stem, [], raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]
            mt = FM_TITLE_RE.search(fm)
            if mt:
                title = mt.group(1).strip().strip("'\"")
            mg = FM_TAGS_RE.search(fm)
            if mg:
                tags = [t.strip().strip("'\"") for t in mg.group(1).split(",") if t.strip()]
    links = {m.strip().lower() for m in WIKILINK_RE.findall(body)}
    tokens = [t for t in TOKEN_RE.findall(body.lower()) if t not in STOPWORDS]
    return {"title": title, "tags": [t.lower() for t in tags], "body_lower": body.lower(),
            "tokens": tokens, "links_out": links}


def scan() -> dict:
    notes: dict[str, dict] = {}
    for d in CONTENT_DIRS:
        base = VAULT / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            if p.name in SKIP_FILES or p.name == ".gitkeep":
                continue
            slug = p.stem.lower()
            note = read_note(p)
            note["path"] = str(p.relative_to(VAULT))
            note["slug"] = slug
            notes[slug] = note
    return notes


# --------------------------------------------------------------------------- #
# TF-IDF (stdlib)
# --------------------------------------------------------------------------- #
def build_tfidf(notes: dict) -> dict[str, dict[str, float]]:
    df: Counter = Counter()
    tf: dict[str, Counter] = {}
    for slug, n in notes.items():
        counts = Counter(n["tokens"])
        tf[slug] = counts
        for term in counts:
            df[term] += 1
    ndocs = max(1, len(notes))
    vectors: dict[str, dict[str, float]] = {}
    for slug, counts in tf.items():
        total = sum(counts.values()) or 1
        vec = {}
        for term, c in counts.items():
            idf = math.log((ndocs + 1) / (df[term] + 1)) + 1.0
            vec[term] = (c / total) * idf
        vectors[slug] = vec
    return vectors


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def jaccard(a: list, b: list) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# --------------------------------------------------------------------------- #
# Analyze
# --------------------------------------------------------------------------- #
def analyze(ledger: dict) -> dict:
    notes = scan()
    slugs = list(notes)
    vectors = build_tfidf(notes)
    w = ledger["weights"]
    thr = ledger["threshold"]
    rejected = {tuple(p) for p in ledger["rejected_pairs"]}

    # Broken links + orphans
    broken, indeg = [], defaultdict(int)
    outdeg = {s: 0 for s in slugs}
    for s, n in notes.items():
        for tgt in n["links_out"]:
            if tgt in notes:
                indeg[tgt] += 1
                outdeg[s] += 1
            else:
                broken.append({"note": n["path"], "broken_link": tgt})
    orphans = [notes[s]["path"] for s in slugs if indeg[s] == 0 and outdeg[s] == 0]

    # Candidate missing links
    candidates = []
    for i in range(len(slugs)):
        for j in range(i + 1, len(slugs)):
            a, b = slugs[i], slugs[j]
            if b in notes[a]["links_out"] or a in notes[b]["links_out"]:
                continue  # already linked
            if tuple(pair_key(a, b)) in rejected:
                continue  # the agent learned this pair is unwanted
            sim = cosine(vectors[a], vectors[b])
            tag = jaccard(notes[a]["tags"], notes[b]["tags"])
            mention = 0.0
            if notes[b]["title"].lower() in notes[a]["body_lower"] or \
               notes[a]["title"].lower() in notes[b]["body_lower"]:
                mention = 1.0
            score = w["tfidf"] * sim + w["tag_overlap"] * tag + w["title_mention"] * mention
            if score >= thr:
                signals = {"tfidf": round(sim, 3), "tag_overlap": round(tag, 3),
                           "title_mention": mention}
                dominant = max(signals, key=lambda k: w[k] * signals[k])
                candidates.append({
                    "source": notes[a]["path"], "target": notes[b]["path"],
                    "source_slug": a, "target_slug": b,
                    "score": round(score, 3), "signals": signals,
                    "dominant_signal": dominant, "decision": "",
                    "reason": f"{dominant} drove this ({signals[dominant]})",
                })
    candidates.sort(key=lambda c: c["score"], reverse=True)

    # Write machine + human proposals
    PROPOSALS_JSON.write_text(json.dumps({
        "generated": date.today().isoformat(),
        "weights": w, "threshold": thr,
        "candidates": candidates,
    }, indent=2), encoding="utf-8")

    lines = [f"# Wiki-link proposals ({date.today().isoformat()})", "",
             f"Weights: {w} | threshold: {thr}", "",
             f"- {len(broken)} broken link(s)",
             f"- {len(orphans)} orphan note(s)",
             f"- {len(candidates)} suggested new link(s)", ""]
    if broken:
        lines += ["## Broken links", ""]
        lines += [f"- `{x['note']}` → `[[{x['broken_link']}]]` (no such note)" for x in broken] + [""]
    if orphans:
        lines += ["## Orphan notes (no links in or out)", ""]
        lines += [f"- `{o}`" for o in orphans] + [""]
    if candidates:
        lines += ["## Suggested links (review, set decision in the JSON)", "",
                  "| score | source | target | why |", "|---|---|---|---|"]
        lines += [f"| {c['score']} | `{c['source_slug']}` | `{c['target_slug']}` | {c['reason']} |"
                  for c in candidates] + [""]
    PROPOSALS_MD.write_text("\n".join(lines), encoding="utf-8")

    ledger["stats"]["runs"] += 1
    ledger["stats"]["proposed"] += len(candidates)
    save_ledger(ledger)

    return {"notes": len(notes), "broken": len(broken), "orphans": len(orphans),
            "candidates": len(candidates),
            "proposals_md": str(PROPOSALS_MD), "proposals_json": str(PROPOSALS_JSON)}


# --------------------------------------------------------------------------- #
# Apply + self-improvement
# --------------------------------------------------------------------------- #
def ensure_related_link(note_path: Path, target_slug: str) -> None:
    text = note_path.read_text(encoding="utf-8")
    link_line = f"- [[{target_slug}]]"
    if link_line in text:
        return
    if "## Related" in text:
        text = re.sub(r"(## Related\s*\n)", rf"\1{link_line}\n", text, count=1)
    else:
        text = text.rstrip() + f"\n\n## Related\n{link_line}\n"
    note_path.write_text(text, encoding="utf-8")


def adjust_weights(ledger: dict, accepted: list[dict], rejected: list[dict]) -> None:
    """Nudge the weight of the dominant signal up for accepted, down for rejected.
    Small, bounded steps so behaviour drifts gradually and stays interpretable."""
    w = ledger["weights"]
    STEP = 0.05
    for c in accepted:
        sig = c.get("dominant_signal")
        if sig in w:
            w[sig] = round(min(3.0, w[sig] + STEP), 3)
    for c in rejected:
        sig = c.get("dominant_signal")
        if sig in w:
            w[sig] = round(max(0.2, w[sig] - STEP), 3)

    # Retune threshold GENTLY toward the acceptance frontier, clamped to a sane band.
    # Goal: drift a little each run, never ratchet so high that valid suggestions starve.
    # If we rejected things, the bar was too low -> nudge UP toward the highest rejected score.
    # If everything was accepted, the bar may be slightly cautious -> nudge DOWN a touch.
    LO, HI, RATE = 0.15, 0.45, 0.15
    thr = ledger["threshold"]
    rej_scores = [c["score"] for c in rejected if "score" in c]
    if rej_scores:
        # move a fraction of the way toward (just above) the worst false-positive we let through
        target = max(rej_scores) + 0.02
        thr = thr + RATE * (target - thr)
    elif accepted:
        thr = thr - RATE * 0.05  # all-accepted: relax slightly to surface more next time
    ledger["threshold"] = round(min(HI, max(LO, thr)), 3)


def apply(ledger: dict, proposals_path: Path) -> dict:
    data = json.loads(proposals_path.read_text(encoding="utf-8"))
    cands = data.get("candidates", [])
    accepted = [c for c in cands if c.get("decision") == "accept"]
    rejected = [c for c in cands if c.get("decision") == "reject"]

    applied = 0
    for c in accepted:
        src = VAULT / c["source"]
        if src.exists():
            ensure_related_link(src, c["target_slug"])
            applied += 1
        ledger["accepted_pairs"].append(pair_key(c["source_slug"], c["target_slug"]))
        if c.get("dominant_signal") == "title_mention":
            ledger["aliases"][c["target_slug"]] = c["target_slug"]
    for c in rejected:
        ledger["rejected_pairs"].append(pair_key(c["source_slug"], c["target_slug"]))

    # de-dup memory
    ledger["accepted_pairs"] = [list(x) for x in {tuple(p) for p in ledger["accepted_pairs"]}]
    ledger["rejected_pairs"] = [list(x) for x in {tuple(p) for p in ledger["rejected_pairs"]}]

    before = dict(ledger["weights"]); before_thr = ledger["threshold"]
    adjust_weights(ledger, accepted, rejected)

    ledger["stats"]["accepted"] += len(accepted)
    ledger["stats"]["rejected"] += len(rejected)
    ledger["log"].append({
        "date": date.today().isoformat(), "accepted": len(accepted),
        "rejected": len(rejected), "weights_before": before,
        "weights_after": dict(ledger["weights"]),
        "threshold_before": before_thr, "threshold_after": ledger["threshold"],
    })
    ledger["log"] = ledger["log"][-50:]
    save_ledger(ledger)

    return {"applied": applied, "recorded_rejected": len(rejected),
            "new_weights": ledger["weights"], "new_threshold": ledger["threshold"]}


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    ledger = load_ledger()
    if cmd == "analyze":
        print(json.dumps(analyze(ledger)))
    elif cmd == "apply":
        idx = sys.argv.index("--proposals") + 1 if "--proposals" in sys.argv else None
        path = Path(sys.argv[idx]) if idx else PROPOSALS_JSON
        print(json.dumps(apply(ledger, path)))
    elif cmd == "status":
        print(json.dumps({"weights": ledger["weights"], "threshold": ledger["threshold"],
                          "stats": ledger["stats"],
                          "remembered_rejected": len(ledger["rejected_pairs"]),
                          "remembered_accepted": len(ledger["accepted_pairs"])}, indent=2))
    else:
        print(f"unknown command: {cmd}. use analyze | apply | status")
        sys.exit(1)


if __name__ == "__main__":
    main()

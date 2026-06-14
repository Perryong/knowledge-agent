#!/usr/bin/env bash
# batch_enrich.sh — nightly (or on_session_finalize) batch:
#   1. link inbox captures -> 05-knowledge/captures/  (deterministic, or LLM if key set)
#   2. rebuild the [[wiki-link]] index
#   3. surface cross-note link proposals for review
#   4. one commit + push for the whole batch
#
# Run from cron (02:00 daily):
#   0 2 * * *  cd /abs/COG-second-brain && bash integrations/hermes-telegram/batch_enrich.sh >> /tmp/cog-batch.log 2>&1
#
# Captures are written atomically with unique names, so the batch never reads a
# half-written file even if a Telegram message arrives mid-run. On Windows set
# HERMES_PYTHON=python.

set -euo pipefail

cd "${VAULT_ROOT:-$(git rev-parse --show-toplevel)}"
export VAULT_ROOT="$PWD"

PYTHON="${HERMES_PYTHON:-}"
if [ -z "$PYTHON" ]; then
  for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { PYTHON="$c"; break; }; done
fi

# 1. promote raw captures into wiki-linked knowledge notes
"$PYTHON" integrations/hermes-telegram/llm_link.py

# 2. refresh the index so new captures are reachable in the graph
"$PYTHON" scripts/build_wiki_index.py

# 3. cross-note link discovery -> /tmp/wiki-proposals.{md,json} for review.
#    (apply stays human-in-the-loop by design; after reviewing:
#     python scripts/wiki_graph_optimizer.py apply --proposals /tmp/wiki-proposals.json)
"$PYTHON" scripts/wiki_graph_optimizer.py analyze || true

# 4. single commit + push for the batch (allowlisted dirs only, never force)
bash scripts/git_autocommit.sh research "telegram capture $(date +%F)"

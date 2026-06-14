#!/usr/bin/env bash
# capture-note.sh — Hermes Agent `post_llm_call` hook entrypoint.
#
# Thin, dependency-light wrapper: locate Python and run capture_note.py with the
# hook's JSON payload piped through on stdin. (Logic lives in capture_note.py so we
# avoid a hard jq dependency and stay portable across Linux/macOS/WSL2/Windows.)
#
# Wire it in ~/.hermes/config.yaml:
#   hooks:
#     post_llm_call:
#       - command: "/abs/path/COG-second-brain/integrations/hermes-telegram/capture-note.sh"
#         timeout: 30
#
# On Windows test runs where `python3` is the broken Store shim, set HERMES_PYTHON=python.

set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PY="${HERMES_PYTHON:-}"
if [ -z "$PY" ]; then
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
fi
[ -z "$PY" ] && { echo "capture-note: no python found" >&2; exit 0; }

exec "$PY" "$DIR/capture_note.py"

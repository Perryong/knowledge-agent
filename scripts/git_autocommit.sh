#!/usr/bin/env bash
# git_autocommit.sh — commit completed session notes to GitHub.
#
# Usage:  bash scripts/git_autocommit.sh <session_type> "<title>"
#   e.g.  bash scripts/git_autocommit.sh research "LLM wrapper commoditization"
#
# Behaviour:
#   - Stages ONLY the vault content directories (allowlist below). Never `git add -A`.
#   - Exits cleanly (NOTHING_TO_COMMIT) if there are no content changes — no empty commits.
#   - Writes a structured commit message with the session type, title, date, and file list.
#   - Pushes to the current branch's upstream. Never force-pushes.
#
# Safe to call from a Claude Code Stop hook or from the worker-git-publisher subagent.

set -euo pipefail

SESSION_TYPE="${1:-session}"
TITLE="${2:-untitled}"
DATE="$(date +%Y-%m-%d)"
TS="$(date +%H:%M)"

# Content directories that are safe to publish. Everything else (.claude/, secrets,
# /tmp, node_modules, .obsidian workspace state) is intentionally excluded.
ALLOWLIST=(00-inbox 01-daily 03-professional 04-projects 05-knowledge raw)

# Make sure we're inside a git repo.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "NOT_A_GIT_REPO: run 'git init' and add a remote first"
  exit 0
fi

# Stage only existing allowlisted paths that have changes.
STAGED_ANY=0
for dir in "${ALLOWLIST[@]}"; do
  if [ -e "$dir" ]; then
    git add -- "$dir" 2>/dev/null || true
    STAGED_ANY=1
  fi
done

# Also include the regenerated knowledge index if present.
[ -f "05-knowledge/INDEX.md" ] && git add -- "05-knowledge/INDEX.md" 2>/dev/null || true

# Nothing actually staged? Bail without committing.
if git diff --cached --quiet 2>/dev/null; then
  echo "NOTHING_TO_COMMIT: vault content unchanged"
  exit 0
fi

# Build a file list for the commit body.
FILES="$(git diff --cached --name-only | sed 's/^/  - /')"
COUNT="$(git diff --cached --name-only | wc -l | tr -d ' ')"

COMMIT_MSG="$(cat <<EOF
${SESSION_TYPE}: ${TITLE} (${DATE} ${TS})

Auto-committed by COG research pipeline after a completed ${SESSION_TYPE} session.
${COUNT} file(s) changed:
${FILES}

Co-authored-by: COG-pipeline <pipeline@local>
EOF
)"

git commit -m "$COMMIT_MSG" >/dev/null

HASH="$(git rev-parse --short HEAD)"

# Determine current branch and whether an upstream is set.
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  if git push 2>push.err; then
    REMOTE="$(git rev-parse --abbrev-ref '@{u}')"
    rm -f push.err
    echo "OK: committed ${COUNT} file(s), pushed to ${REMOTE} (commit ${HASH})"
  else
    echo "PUSH_FAILED: committed ${HASH} locally but push failed -> $(cat push.err)"
    rm -f push.err
    exit 0
  fi
else
  echo "COMMITTED_NO_UPSTREAM: commit ${HASH} on '${BRANCH}'. Set a remote then run: git push -u origin ${BRANCH}"
fi

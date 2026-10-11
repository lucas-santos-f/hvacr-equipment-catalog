#!/usr/bin/env bash
# Guardrail: stop a commit that is about to publish a credential or a personal detail.
#
# Install:
#   ln -s ../../agent-hooks/block-secrets.sh .git/hooks/pre-commit
#   (or call it from an existing pre-commit)
#
# Deliberately crude. It catches the mistakes that actually happen - a pasted key, a
# real .env, an email address left in a fixture - and does not pretend to be a scanner.

set -uo pipefail

staged=$(git diff --cached --name-only --diff-filter=ACM)
[ -z "$staged" ] && exit 0

fail=0

if echo "$staged" | grep -qE '(^|/)\.env$'; then
  echo "blocked: .env is staged. It belongs in .gitignore; commit .env.example instead." >&2
  fail=1
fi

patterns=(
  'sk-[A-Za-z0-9_-]{20,}'
  'ghp_[A-Za-z0-9]{36}'
  'AKIA[0-9A-Z]{16}'
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  '[A-Za-z0-9._%+-]+@(gmail|hotmail|outlook|yahoo)\.[a-z]{2,}'
)

for file in $staged; do
  [ -f "$file" ] || continue
  case "$file" in
    agent-hooks/block-secrets.sh|security/*) continue ;;
  esac

  for pattern in "${patterns[@]}"; do
    if git show ":$file" | grep -nEq "$pattern"; then
      echo "blocked: $file matches a secret or personal-data pattern:" >&2
      git show ":$file" | grep -nE "$pattern" | head -3 | sed 's/^/    /' >&2
      fail=1
    fi
  done
done

if [ "$fail" -ne 0 ]; then
  echo "" >&2
  echo "Nothing personal and no credentials go in this repo. See AGENTS.md." >&2
  exit 1
fi

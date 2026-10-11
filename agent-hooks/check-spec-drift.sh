#!/usr/bin/env bash
# Guardrail: refuse a commit that changes a route without regenerating openapi.yaml.
#
# Install:
#   ln -s ../../agent-hooks/check-spec-drift.sh .git/hooks/pre-commit
#
# The same check runs in CI via backend/tests/test_contract.py. This hook exists so an
# agent finds out in one second instead of after a push.

set -euo pipefail

staged=$(git diff --cached --name-only)

touches_routes=$(echo "$staged" | grep -E '^backend/app/(routers/|schemas\.py|main\.py)' || true)
touches_spec=$(echo "$staged" | grep -E '^openapi\.yaml$' || true)

if [ -z "$touches_routes" ]; then
  exit 0
fi

if [ -n "$touches_spec" ]; then
  exit 0
fi

cat >&2 <<'MSG'
blocked: routes or schemas changed but openapi.yaml is not staged.

openapi.yaml is the contract the frontend is written against. Regenerate and stage it:

    make spec
    git add openapi.yaml

If the change genuinely does not alter the spec, make spec produces no diff and there
is nothing to stage, so run it anyway to prove that.
MSG
exit 1

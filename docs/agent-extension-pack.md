# Agent extension pack

Six pieces, all built around one problem: this repo has a contract (`openapi.yaml`)
that is easy to break by accident and expensive to notice late. Most of the pack exists
to make that mistake impossible to commit.

| Piece | Where | What it does |
|---|---|---|
| Project instructions | `AGENTS.md` | Rules an agent loads before touching anything |
| Reusable workflows | `agent-capabilities/` | Three checklists, in the order that keeps the contract honest |
| Specialist subagent | `.claude/agents/contract-reviewer.md` | Reviews a diff for drift and layering violations |
| MCP server | `mcp-server/server.py` | Four read-only tools over the live catalogue |
| Guardrails | `agent-hooks/` | Two pre-commit hooks: spec drift, secrets |
| Permission notes | `docs/permissions.md` | What is allowed, and which half is actually enforced |

## 1. Project instructions

`AGENTS.md` is loaded automatically by the agents used here. It is short on purpose.
Every rule in it exists because something went wrong once: the contract rule, the
"comparison stays on the server" rule, and the "no real manufacturer data" rule each
trace to a specific mistake recorded in [ai-workflow.md](ai-workflow.md).

It also lists the three known rough edges, so an agent does not spend a session
rediscovering that COP is nonsense for pumps.

## 2. Reusable workflows

`agent-capabilities/` holds three:

- **`add-endpoint.md`** - acceptance criteria, schema, crud, router, spec, tests,
  client method, gate. The order matters: writing the criteria first is what produces
  the test list.
- **`add-catalogue-field.md`** - eight steps, because a new field has to reach the
  comparison table, the seed file and the UI labels, and missing any one of those fails
  in a different place.
- **`release-check.md`** - the pre-deploy gate, as commands.

They are markdown, invoked by reference. Two are also exposed as slash commands in
`plugins/`, which are one-liners pointing back here so there is a single copy.

## 3. Specialist subagent

`contract-reviewer` runs before a pull request. It checks five things and reports
`blocked` or `ready`:

1. The committed spec matches the routes
2. No `fetch` outside `api/client.js`, no comparison logic in the frontend
3. Every new non-200 path has a test
4. No leaked personal data, no real manufacturer names
5. Dependency changes have a reason and a clean audit

It is explicitly told not to rewrite code and not to comment on anything `ruff` already
enforces. A reviewer that reports style noise stops being read.

## 4. MCP server

`mcp-server/server.py` speaks JSON-RPC over stdio and exposes `search_equipment`,
`get_equipment`, `compare_equipment` and `list_facets`.

```bash
CATALOG_API_URL=http://localhost:8000 python mcp-server/server.py
```

In a Claude Code config:

```json
{
  "mcpServers": {
    "hvacr-catalog": {
      "command": "python",
      "args": ["mcp-server/server.py"],
      "env": { "CATALOG_API_URL": "http://localhost:8000" }
    }
  }
}
```

**All four tools are reads.** The write endpoint is deliberately not exposed; see
[../security/agent-extension-security.md](../security/agent-extension-security.md).

Verified end to end: `initialize`, `tools/list` and a `tools/call` against a running
backend all return correctly.

## 5. Guardrails

Both are git `pre-commit` hooks that block and never modify.

```bash
ln -s ../../agent-hooks/check-spec-drift.sh .git/hooks/pre-commit
```

- **`check-spec-drift.sh`** blocks a commit touching routes or schemas without
  `openapi.yaml` staged. The same check runs in CI as `test_contract.py`, because
  `--no-verify` bypasses a hook. The hook exists to fail in one second instead of after
  a push.
- **`block-secrets.sh`** blocks a staged `.env` and scans staged content for key and
  personal-email patterns. Its limits are written down rather than glossed: patterns
  only, staged content only, and it skips `security/` so the documentation can quote
  its own patterns.

## 6. Permission notes

[permissions.md](permissions.md) splits what is enforced in code from what is only
policy. Four things are enforced: no write tool on the MCP server, one reachable host,
secrets blocked at commit, drift blocked at commit and in CI. Pushing to `main` and
adding dependencies are branch protection and human review, and the document says so
instead of implying otherwise.

## The shape of it

Instructions tell an agent the rules. Workflows give it the order. The subagent checks
the result. The hooks stop the two mistakes that matter from reaching a commit. CI
repeats the one check a hook cannot be trusted with. The MCP server gives read access
to the data and no way to change it.

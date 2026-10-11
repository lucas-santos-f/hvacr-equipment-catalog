# Security notes on the agent extension pack

What the pack in `mcp-server/`, `agent-hooks/`, `agent-capabilities/` and `plugins/`
can reach, and what stops it reaching further.

## MCP server

`mcp-server/server.py` exposes four tools: `search_equipment`, `get_equipment`,
`compare_equipment`, `list_facets`.

**All four are read-only.** `POST /equipment` is deliberately not exposed. An agent
writing to the catalogue while reasoning about it would be a silent data-integrity
problem, and nothing an agent needs to do here requires a write.

| Control | How |
|---|---|
| Transport | stdio only. No socket is opened, so nothing on the network can reach it. |
| Reachable host | One, from `CATALOG_API_URL`, default `http://localhost:8000`. |
| Credentials | None. It holds no secret, so it cannot leak one. |
| Timeouts | 10 seconds on every request, so a hung backend cannot hang the agent. |
| Error output | `HTTPError` bodies are truncated to 400 characters before returning. |
| Injection | Model codes go through `urllib.parse.quote(safe='')`; query strings through `urlencode`. |

**Residual risk.** The tool returns whatever the configured backend says. Point
`CATALOG_API_URL` at a hostile server and the agent reads hostile text. Treat tool
output as data, not instructions. The default is localhost and changing it is a
deliberate act.

## Hooks

Both are git `pre-commit` hooks. They can only block a commit; neither modifies a file,
makes a network call, or runs anything outside the repository.

**`check-spec-drift.sh`** blocks a commit touching `backend/app/routers/`,
`schemas.py` or `main.py` without `openapi.yaml` staged. Correctness, not security.

**`block-secrets.sh`** blocks a staged `.env` and scans staged content for key and
personal-email patterns.

Known limits, stated rather than papered over:

- Pattern matching only. A novel key format passes.
- Only staged content is scanned. A secret already in history is not found.
- It skips itself and `security/` so the patterns in this documentation do not trip it.
  That exclusion is a hole: a real secret placed under `security/` would not be caught.
  Acceptable because that directory holds documentation nobody puts a key in, and the
  alternative is a hook that cannot document its own patterns.

Hooks are not a security boundary. `--no-verify` bypasses both. They are there to catch
the accident, and the CI contract test backs up the first one where a hook cannot.

## Plugins and capability docs

Markdown. They instruct, they do not execute. `plugins/*.md` interpolate `$ARGUMENTS`
into a prompt, which means a plugin invocation is only as trustworthy as whoever typed
it. No elevation: whatever the agent could already do, it can still do, and nothing more.

## What an agent cannot do here

Per `docs/permissions.md`: no push to `main`, no network beyond the local backend, no
dependency added without a human-read diff, no write path through the MCP server. The
MCP server enforces the last one in code. The others are policy backed by branch
protection and code review.

# Exposure audit of the live deployment

Run date: 12 October 2026, against `https://hvacr-catalog-api.onrender.com`,
`https://hvacr-catalog-web.onrender.com` and the public repository at commit `dbb2161`.

Unlike `scan-findings.md`, which is tool output about dependencies, this is about what
the deployment exposes to the internet. Both findings here were found by asking what an
unauthenticated stranger can reach, not by a scanner.

## Finding 1: the write route accepted anonymous writes

**Severity: high.** `POST /equipment` had no authentication and no rate limit. Verified
against production: an empty POST carrying `Origin: https://evil.example` returned 422,
meaning the request was parsed and would have been accepted with a valid body.

CORS was not a control here. `allow_origins` restrains browsers obeying the same-origin
policy; `curl` never asks. Treating a CORS allow-list as a write gate is the mistake this
finding is really about.

The impact was not database damage, it was publication: inserted rows render on a public
page reachable from the maintainer's GitHub profile, and there is no delete route, so
cleanup means opening the database by hand.

**Fixed** in `app/security.py`. Writes require `X-API-Key` compared with
`secrets.compare_digest`. Render mints the value through `generateValue`, so it is never
committed. The gate fails closed: with no `API_KEY` configured the route answers 503
rather than accepting the write, and the key is checked before the body so a stranger
cannot use 422 responses to enumerate the schema. Covered by
`tests/integration/test_write_auth.py`, including a test asserting that `PUT`, `PATCH`
and `DELETE` still return 405, which fails if a future route is added without a gate.

Still open by choice: no rate limit, and one shared key rather than per-caller identity.
Acceptable for a catalogue with one maintainer; not acceptable for multi-tenant use.

## Finding 2: the database port was open to the whole internet

**Severity: high.** The inbound IP rule on `hvacr-catalog-db` was `0.0.0.0/0`, inherited
from the workspace default rather than chosen. Confirmed by opening TCP 5432 on the
external hostname from a machine outside Render. Only the generated password stood in
front of it, with no network layer and no brute-force protection.

**Fixed** by blocking all inbound internet traffic on the database. Re-verified after
the change: the server now hangs up after the startup packet instead of asking for a
password, and the API still answers with all 90 units, because it reaches the database
over the private internal hostname from `fromDatabase.connectionString`.

Two things made this harder to get right than it looks, and both are worth knowing:

- The first save silently did nothing. Deleting the row and pressing Save pops a
  confirmation dialog that wants the phrase `block all internet traffic to PostgreSQL`
  typed out. Until that is done the page still claims "All internet traffic is blocked"
  while the rule is untouched, and a reload brings the row back. The verification probe
  is what caught it; the dashboard's own wording would have been believed.
- A TCP connect test is not a reachability test here. Render's edge completes the
  handshake on 5432 whether or not the rule is on, so `/dev/tcp` reports the port open in
  both states. Only speaking the Postgres startup protocol tells the two apart.

This is dashboard state, not blueprint state: Render does not express inbound IP rules in
`render.yaml`, so it is recorded here and in `docs/deployment.md` instead of being
enforced by the file. The workspace-wide rule remains `0.0.0.0/0`; the rule on the
resource is what applies.

## Checked and clean

- **No personal data.** All commits authored `lucas-santos-f` with a GitHub noreply
  address. Every tracked file and every blob in history swept for real names, personal
  email addresses, phone numbers and credentials: nothing. The built frontend bundle is
  clean too. No `.env` is tracked.
- **No credentials in the repository.** The only connection strings are `u:p@h` test
  fixtures in `tests/test_config.py`.
- **CI is not injectable.** `ci.yml` runs on `push` and `pull_request`, `deploy.yml` on
  `workflow_run`. No `pull_request_target`, and no `github.event` field is interpolated
  into a shell step. The two Render hook secrets are referenced only in `deploy.yml`.
- **No stack traces leak.** Malformed input returns Pydantic 422 bodies. Nothing in the
  app sets `debug=True`.
- **Transport.** HSTS with preload and `x-content-type-options: nosniff` on the static
  site, TLS terminated by Render on both services.

## Noted, not fixed

The frontend source map is served at `/assets/*.js.map`. It leaks nothing, because the
source is public on GitHub, but it is dead weight in a production bundle.

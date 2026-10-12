# Deployment

Live at https://hvacr-catalog-web.onrender.com, API at
https://hvacr-catalog-api.onrender.com.

Deployed as a Render **blueprint**: `render.yaml` at the repo root declares the
database, the API and the static site, and Render creates all three from it. That is
the path to use. The click-by-click route below is kept for anyone deploying somewhere
else.

## Blueprint

Render dashboard > New > Blueprint, point it at this repository, name it, deploy. The
file does the rest.

Two things that went wrong the first time, both now fixed in `render.yaml` and written
up in [../ops/runbook.md](../ops/runbook.md):

- **Region.** The database had no `region`, so Render put it in Oregon while the API
  went to Frankfurt. `fromDatabase` hands out an internal hostname that only resolves
  within one region, so the API could not connect and exited. Every resource now names
  its region explicitly.
- **Cross-service URLs.** `fromService ... property: host` resolves to the bare service
  name, not the public hostname, so the frontend ended up calling
  `https://hvacr-catalog-api/facets`. Both URLs are now literals in `render.yaml`.

A blueprint created from a **public repository URL** rather than a connected GitHub
account does not auto-sync on push. Use the sync hook on the blueprint's settings page,
or connect the repo to Render's GitHub app.

## Manual, service by service

Use this for a provider without blueprint support.

## Render

Three services off this repo.

### 1. Database

New > Postgres. Note the internal connection string. Render gives a
`postgres://` URL; SQLAlchemy 2 with psycopg 3 wants `postgresql+psycopg://`, so
rewrite the scheme.

### 2. Backend

New > Web Service, Docker, root directory `backend`.

| Variable | Value |
|---|---|
| `DATABASE_URL` | the rewritten connection string |
| `CORS_ORIGINS` | the frontend URL, no trailing slash |
| `SEED_ON_STARTUP` | `true` |

Health check path `/health`. The Dockerfile already declares a `HEALTHCHECK` and runs
as uid 10001.

### 3. Frontend

New > Static Site, root directory `frontend`, build `npm ci && npm run build`, publish
`dist`.

Set `VITE_API_URL` to the backend URL. Vite inlines it at build time, so changing it
later needs a rebuild, not a restart.

### 4. Wire up CI/CD

Copy each service's deploy hook URL into repository secrets as `RENDER_BACKEND_HOOK`
and `RENDER_FRONTEND_HOOK`. `.github/workflows/deploy.yml` then fires both after a green
`ci` run on `main`, and skips with a note in the job summary while they are unset.

### 5. Then

Put the live URL in the README, and add it to the Project 1 submission.

## Order matters

Backend before frontend, because the frontend needs the backend URL at build time.
`CORS_ORIGINS` on the backend needs the frontend URL, so it gets updated after the
frontend exists. Two passes, unavoidable with a build-time API URL.

## First boot

The backend creates its tables and loads the 90-unit catalogue on first start. Check:

```bash
curl https://<backend>/health
curl 'https://<backend>/equipment?limit=1'
```

`total` should be 90. If it is 0, `SEED_ON_STARTUP` is off or the data file did not make
it into the image.

## Hardening that is not in the blueprint

Two things have to be done in the dashboard, because `render.yaml` cannot express them.
Both are part of the deployment, so they belong in this checklist.

**Close the database to the internet.** A new Render workspace allows inbound Postgres
traffic from `0.0.0.0/0`. Database > Networking > Inbound IP Restrictions: delete the
`0.0.0.0/0` source and save, leaving no external sources. The API connects over the
internal hostname that `fromDatabase.connectionString` provides, which is a private
address, so the service is unaffected. Verify from outside Render:

```bash
# should hang or refuse, not connect
timeout 10 bash -c 'exec 3<>/dev/tcp/<db-host>.oregon-postgres.render.com/5432' && echo OPEN || echo CLOSED
```

**Read the write key.** `API_KEY` is minted by `generateValue`, so nobody typed it and it
is not in the repository. Service `hvacr-catalog-api` > Environment > `API_KEY` to read
it when you need to POST a unit. Rotating it is a matter of deleting the value and
re-syncing the blueprint.

Both are written up in [../security/exposure-audit.md](../security/exposure-audit.md).

## Anywhere else

Nothing here is Render-specific beyond the deploy hooks. `docker compose up` is the
whole system; Fly.io, Railway or a VPS need the same four environment variables and the
same ordering.

# Deployment

Not deployed yet. These are the steps, verified as far as they can be without an
account.

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

## Anywhere else

Nothing here is Render-specific beyond the deploy hooks. `docker compose up` is the
whole system; Fly.io, Railway or a VPS need the same three environment variables and the
same ordering.

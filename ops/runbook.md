# Runbook

## Health

| Check | Command | Healthy |
|---|---|---|
| API up | `curl -fs <api>/health` | `{"status":"ok"}` |
| Data loaded | `curl -fs '<api>/equipment?limit=1'` | `"total": 90` |
| Frontend served | `curl -fsI <web>` | `200` |
| Database | `docker compose exec db pg_isready -U catalog` | `accepting connections` |

## Common failures

### Catalogue is empty, API is up

`total: 0`. Either `SEED_ON_STARTUP` is false, or the seed file is not in the image.

```bash
docker compose exec backend ls app/data/catalog_seed.json
docker compose exec backend printenv SEED_ON_STARTUP
```

Full walkthrough in [diagnosis.md](diagnosis.md).

### Frontend loads, every request fails

Almost always CORS. The browser console names the blocked origin.

```bash
docker compose exec backend printenv CORS_ORIGINS
```

It must contain the frontend's origin exactly, with no trailing slash.

### Frontend calls the wrong API

`VITE_API_URL` is inlined at build time. Changing the environment variable on a running
container does nothing. Rebuild:

```bash
docker compose build --no-cache frontend
```

### Backend will not start, database refused

Compose waits on the `db` healthcheck, so this means Postgres itself failed. Check
`docker compose logs db`. A corrupt volume is cleared with `docker compose down -v`,
which deletes the data; the catalogue reseeds on next boot, so nothing is lost here.

### CI contract test fails

The message is `openapi.yaml is stale, run: make spec`. Someone changed a route without
regenerating the spec.

```bash
make spec
git add openapi.yaml
```

## Known rough edges

**COP is meaningless for passive equipment.** For a pump or a heat exchanger the
"power input" is pumping loss, so capacity over input lands between 20 and 60. The
arithmetic is right and the label is wrong. Do not read those as efficiency figures.
The honest fix is a per-category label, which has not been done.

**Counting does not scale.** `crud.list_equipment` materialises the unfiltered query to
get `total`. Free at 90 rows, the slowest thing in the app at 90,000. Replace with a
`select(func.count())`.

**Offset pagination skips rows** if the catalogue is written to while someone pages.
Irrelevant now, because writes are rare and manual.

## Restoring

There is nothing to back up. The catalogue is a file in the repository and the database
rebuilds itself from it on an empty volume. If that stops being true, this section
needs rewriting before the first real write lands.

## Incident: API could not resolve the database host

**Symptom.** First Render deploy failed with `Exited with status 3`. Deploy log ended in:

```
sqlalchemy.exc.OperationalError: (psycopg.OperationalError) [Errno -2] Name or service not known
ERROR: Application startup failed. Exiting.
==> No open ports detected, continuing to scan...
```

**Cause.** `render.yaml` set `region: oregon` on the web service but left the database
with no region, so Render defaulted it to Oregon while the service went to Frankfurt.
`fromDatabase: connectionString` hands out the **internal** hostname, which only
resolves inside one region. The service came up, failed to open a connection during the
lifespan handler, and exited before binding a port.

**Fix.** Pin `region` on the database as well as the service, so the two cannot drift
apart. Region is immutable on an existing Render service, so the web service had to be
deleted and recreated by a blueprint sync; the database was already in the right place
and was left alone.

**Rule.** Every resource in `render.yaml` carries an explicit `region`. An omitted
region is not "the same as the others", it is "whatever the provider picks today".

**Why the failure was loud.** `app/main.py` does not wrap the lifespan handler in a
`try`. The container refused to start instead of serving an empty catalogue, which is
exactly the behaviour the earlier empty-catalogue incident was fixed to produce. Good
failure, found in one log read.

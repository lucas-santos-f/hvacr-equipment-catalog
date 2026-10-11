# Architecture

## Shape

```
browser
  |
  |  http, json
  v
nginx :80 ----------------> static React bundle
  (frontend container)

browser --- fetch ---> uvicorn :8000
                         (backend container, FastAPI)
                              |
                              |  SQLAlchemy 2.0
                              v
                         Postgres 17 :5432
                         (db container, named volume)
```

Three containers, one compose file. The frontend is a static bundle, so nginx serves it
and the browser talks to the API directly. There is no reverse proxy in front of both,
which keeps CORS honest rather than hiding it.

## Backend

FastAPI with SQLAlchemy 2.0 in its typed `Mapped[...]` style, Pydantic v2 for the
schemas.

| File | Responsibility |
|---|---|
| `app/main.py` | App construction, CORS, lifespan: create tables, seed if empty |
| `app/config.py` | Environment, read once |
| `app/database.py` | Engine, session factory, `get_db` dependency |
| `app/models.py` | The `Equipment` table and the derived `cop` |
| `app/schemas.py` | Request and response shapes, validation bounds |
| `app/crud.py` | Queries and the comparison algorithm |
| `app/routers/equipment.py` | Search, detail, compare, create |
| `app/routers/meta.py` | Health and facets |
| `app/seed.py` | Loads `data/catalog_seed.json` when the table is empty |

Routers do HTTP concerns and nothing else: parse, validate, map a missing row to a 404.
Anything that would still be true without HTTP lives in `crud.py`, which is why the
comparison tests need no client.

### Why SQLite and Postgres

`DATABASE_URL` picks the engine. Tests use a temporary SQLite file, so the suite runs in
0.2 seconds with no service to start. Compose and production use Postgres. The
`check_same_thread` argument is applied only for SQLite, in `database.py`.

The schema is plain enough that nothing diverges between the two. If that stops being
true, the tests move to Postgres and get slower.

### Seeding

`seed_if_empty` runs in the lifespan handler and is a no-op when a row already exists,
so a restart does not duplicate the catalogue. `SEED_ON_STARTUP=false` disables it,
which is what the test suite sets before importing the app.

There are no migrations. `Base.metadata.create_all` is enough for one table that has not
changed. Adding Alembic before there is a second version to migrate to would be
ceremony.

## Frontend

React 19 with Vite. No router, no state library, no component library. One page.

| File | Responsibility |
|---|---|
| `src/api/client.js` | Every network call, URL building, error mapping |
| `src/lib/selection.js` | Compare-tray rules and formatting |
| `src/App.jsx` | State, effects, wiring |
| `src/components/*` | Rendering only |

The split exists so the tested parts have no DOM. `selection.js` and `client.js` carry
every rule worth asserting; the components take props and render them. That is why 24
tests cover the frontend without a rendering library.

`ApiError` carries the HTTP status and the backend's `detail` string, so the alert the
user sees is the message the API actually sent rather than a generic failure.

## The contract

`openapi.yaml` is generated from the app, committed, and verified in CI by
`test_contract.py`. Changing a route without running `make spec` fails the build.

Generating rather than hand-writing is a deliberate call. A hand-written spec is a
second source of truth that rots. Generating it and freezing it in a test gives the same
guarantee the hand-written version was supposed to give, without the drift.

## Environments

| | local | compose | production |
|---|---|---|---|
| Database | SQLite file | Postgres container | managed Postgres |
| Frontend | Vite dev server :5173 | nginx :8080 | static host |
| API base | `http://localhost:8000` | `http://localhost:8000` | `VITE_API_URL` at build |
| Seeding | on | on | on, first boot only |

`VITE_API_URL` is baked in at build time, which is how Vite works. The production image
has to be rebuilt to point at a different API.

## What would break first at scale

- `crud.list_equipment` counts by materialising the unfiltered query and taking `len()`.
  At 90 rows this is free. At 90,000 it is the slowest thing in the app.
- Offset pagination skips rows if the catalogue is written to mid-page.
- `/facets` does four `SELECT DISTINCT` calls on every request with no caching.

None of these are worth fixing at the current size, and all three are listed in
`AGENTS.md` so the next person does not have to rediscover them.

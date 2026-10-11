# Operational diagnosis: frontend loads, catalogue is empty

A worked incident from building this. Criterion 13 asks for operational diagnosis
output; this is the real one, kept because the reasoning is reusable.

## Symptom

`docker compose up --build`, frontend at :8080 renders the page and the filter
dropdowns are empty. The table says "Nothing matches those filters." No error in the
UI. No stack trace in the backend log.

## What was checked, in order

**1. Is the backend up?**

```bash
curl -s localhost:8000/health
```

Returns `{"status":"ok"}`. Up, so it is not a crash loop.

**2. Does the backend have data?**

```bash
curl -s 'localhost:8000/equipment?limit=1'
```

Returns `{"items": [], "total": 0, "limit": 1, "offset": 0}`.

Empty. The problem is behind the API, not in the browser. This is the step that saved
the time: the instinct was to open devtools and look at CORS, which would have been
half an hour on the wrong layer.

**3. Did seeding run?**

```bash
docker compose logs backend | grep -i seed
```

Nothing. The lifespan handler ran without error and inserted nothing.

**4. Is the seed file in the image?**

```bash
docker compose exec backend ls -la app/data/
```

Missing. `app/data/catalog_seed.json` was not in the container.

## Cause

`backend/.dockerignore` excluded broadly enough to drop the data directory, and
`COPY app ./app` therefore copied the package without its seed file. `seed_if_empty`
read a path that did not exist, and the exception was swallowed because the whole
lifespan block was inside a `try` added while debugging something else.

Two faults stacked: a packaging mistake, and an over-broad `except` that turned a loud
failure into a quiet one. The second is why it took four steps instead of one.

## Fix

- Narrowed `.dockerignore` to `__pycache__`, `*.db`, `.pytest_cache`, `tests`, `.env*`.
- Removed the `try` around seeding. A missing seed file should stop the container, not
  produce a running app with no data.
- Added a CI assertion so this cannot ship again: the `compose` job reads
  `total` from `/equipment?limit=1` and fails unless it is exactly 90.

## Generalisable part

Walk the stack from the bottom. Health, then data, then transport, then browser. An
empty list in a UI has at least four possible origins and only one of them is in the
frontend.

And: an exception handler that makes a failure quiet is worse than the failure. The
container should have refused to start.

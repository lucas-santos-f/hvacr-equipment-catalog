# Testing

52 tests: 28 backend, 24 frontend. Both suites run in under three seconds.

## Layers

| Layer | Where | What it proves | How it runs |
|---|---|---|---|
| Unit, backend | `backend/tests/test_comparison.py` | Comparison direction, ties, COP arithmetic | No HTTP, no database |
| Contract | `backend/tests/test_contract.py` | `openapi.yaml` matches the live routes | Imports the app |
| Integration | `backend/tests/integration/test_api.py` | Real HTTP against a real database | TestClient + SQLite file |
| Unit, frontend | `frontend/tests/selection.test.js` | Tray rules, formatting | Pure functions |
| Unit, frontend | `frontend/tests/client.test.js` | URL building, error mapping | `fetch` stubbed |

CI runs unit and integration as separate steps on purpose. A red integration step with a
green unit step points at wiring; the reverse points at logic.

## Running

```bash
make test                                    # everything

cd backend && pytest tests -q --ignore=tests/integration
cd backend && pytest tests/integration -q
cd frontend && npm test
cd frontend && npx vitest                    # watch
```

## Fixtures

`backend/tests/conftest.py` sets `DATABASE_URL` to a temp SQLite file and
`SEED_ON_STARTUP=false` **before importing the app**, which matters because `config.py`
reads the environment at import time. It then loads three fixed units, chosen so every
assertion in the integration suite can be written against a known catalogue rather than
against whatever the seed happens to contain.

The file is deleted in fixture teardown.

## What is deliberately not tested

- React components. Every rule worth asserting was moved into `src/lib/` and
  `src/api/`, so the components take props and render. Adding a rendering library to
  assert that a `<td>` contains the text it was handed would buy nothing.
- SQLAlchemy. Testing that the ORM can store a float tests SQLAlchemy, not this app.
- The seed figures. They are invented. Asserting a specific chiller weighs 2397.6 kg
  would lock in an arbitrary number.

The CI `compose` job does assert the seeded catalogue is exactly 90 units, which catches
a broken seed file without pinning any individual value.

## Coverage of the error paths

Every non-200 the API can return has a test:

| Status | Case |
|---|---|
| 404 | Unknown model on detail, unknown model inside a comparison |
| 409 | Posting a model code that already exists |
| 422 | `min_capacity` above `max_capacity` |
| 422 | Category outside the enum |
| 422 | Comparing fewer than two or more than four models |
| 422 | Negative capacity on create |

That list came from `product-spec.md`, written before the routes.

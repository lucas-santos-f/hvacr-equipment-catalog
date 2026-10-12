# HVAC-R equipment catalogue

Pick a chiller, a compressor or a pump by duty and refrigerant, then put up to four
units side by side and see which one actually wins on each figure.

## Live

- App: https://hvacr-catalog-web.onrender.com
- API: https://hvacr-catalog-api.onrender.com
- API docs: https://hvacr-catalog-api.onrender.com/docs

Both run on Render's free tier, which spins a service down after about 15 minutes idle.
The first request after that takes up to a minute while the container wakes.

Infrastructure is declared in [render.yaml](render.yaml) and deployed as a Render
blueprint, so the database, API and static site come up together with their URLs
already wired. [docs/deployment.md](docs/deployment.md) walks through it.

## Built with AI assistance

[docs/ai-workflow.md](docs/ai-workflow.md) records which parts were delegated, what the
context files looked like, what came back wrong and what was changed by hand.

## The problem

Choosing equipment for a job means opening six manufacturer PDFs and reading capacity
tables that are all laid out differently. One quotes cooling duty at 7/12 C, another at
a different condensing temperature, a third buries the sound figure in an annex. Then
you make a table in a spreadsheet by hand, and that table is wrong by the time the
quote comes back.

This app holds the same fields for every unit and does the comparison for you. Filter
the catalogue down to what fits the job, tick two to four units, and get one table where
the better number on each row is highlighted. Ties are left plain, because calling one
of two identical figures the winner would be a lie.

### What it does

- Filter by category, refrigerant, manufacturer and a capacity window in kW
- Page through results, sorted by capacity
- Open one unit and see its full specification, including the COP the API computes
- Compare 2 to 4 units on capacity, power input, COP, noise, weight and price
- Add a new unit through the API

### What it does not do

No authentication, no quoting, no price history. The catalogue is read-mostly: adding
a unit is a single POST and there is no edit or delete yet.

> The catalogue data is invented. Norvent, Thermexa, Frigora, Valbrand and Cryomar are
> not real companies and the figures are generated placeholders, not datasheets. Do not
> size anything from them.

## Running it

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:8080
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

The backend creates its tables and loads the 90-unit catalogue on first start. The
Postgres volume survives `docker compose down`; use `down -v` to wipe it.

### Without Docker

```bash
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

Defaults to SQLite at `backend/catalog.db` when `DATABASE_URL` is unset.

## Testing

```bash
make test
```

That runs both suites. Separately:

```bash
cd backend && pytest tests -q --ignore=tests/integration   # unit
cd backend && pytest tests/integration -q                  # integration, real DB + HTTP
cd frontend && npm test                                    # vitest
```

28 backend tests and 24 frontend tests. [docs/testing.md](docs/testing.md) explains what
each layer covers and why the split is where it is.

## Architecture

```
frontend (React + Vite, nginx in prod)
    |  every call goes through src/api/client.js
    v
backend (FastAPI + SQLAlchemy)
    |
    v
Postgres 17   (SQLite when DATABASE_URL is unset, used by the tests)
```

`openapi.yaml` at the repo root is the contract. It is generated from the app with
`make spec`, and `backend/tests/test_contract.py` fails CI if the committed file drifts
from the routes. The frontend was written against that file.

Full write-up in [docs/architecture.md](docs/architecture.md).

## Repository layout

| Path | What is in it |
|---|---|
| `backend/` | FastAPI app, SQLAlchemy models, pytest suites |
| `frontend/` | React app, centralised API client, vitest suites |
| `openapi.yaml` | API contract, generated and checked in CI |
| `docs/` | architecture, AI workflow, testing, deployment, agent pack |
| `security/` | audit output, scan findings, AI tool and data policy |
| `ops/` | runbook and an incident diagnosis |
| `agent-capabilities/`, `agent-hooks/`, `mcp-server/`, `plugins/` | agent extension pack |

# Project instructions

Read this before changing anything. It is loaded automatically by the coding agents
used on this repo.

## What this is

A FastAPI backend and a React frontend over a single-table equipment catalogue. The
contract between them is `openapi.yaml` at the repo root.

## Hard rules

**The spec is the contract.** Change a route, a query parameter or a response shape and
you regenerate `openapi.yaml` with `make spec` in the same commit.
`backend/tests/test_contract.py` fails the build otherwise. Do not edit `openapi.yaml`
by hand; it is generated.

**Comparison logic stays on the server.** `backend/app/crud.py::COMPARISON_FIELDS` owns
the direction of "better" for every field. Do not reimplement it in the frontend.

**The frontend talks to the backend only through `frontend/src/api/client.js`.** No
`fetch` in a component, no URL built outside that file. If you need a new endpoint, add
a method there.

**No real manufacturer names or real datasheet figures.** The catalogue is invented on
purpose. Adding real data would make the fake figures next to it look authoritative.

**Nothing personal, ever.** No names, emails, addresses, keys or tokens in code,
comments, commit messages, fixtures or docs. Credentials go in `.env`, which is ignored.
`.env.example` carries placeholders only.

## Conventions

- Python: 4 spaces, `ruff check app tests` clean, type hints on function signatures
  where they help and nowhere else.
- JavaScript: no semicolons, single quotes, named exports.
- Commit messages: lowercase, imperative, one line. No `feat:` or `fix:` prefixes.
- No comments that restate the line below them. Comment the decision, not the syntax.
- No emoji anywhere in the repo.

## Testing

Unit tests go in `backend/tests/`, integration tests in `backend/tests/integration/`.
The split matters: CI runs them as separate steps so a broken database shows up as a
different failure than broken logic.

A change to comparison behaviour needs a test in `test_comparison.py`. A change to a
route needs one in `integration/test_api.py`. Both, if it is both.

Frontend logic that is worth testing lives in `src/lib/` and `src/api/`, not in
components. If you find yourself wanting to test a component, move the logic out first.

## Before you open a PR

```bash
make lint
make test
make spec        # then check git diff is empty
make audit
```

## Known rough edges

- COP is meaningless for pumps and heat exchangers, where it comes out at 20 to 60.
  The arithmetic is right, the label is wrong. See `ops/runbook.md`.
- `crud.list_equipment` counts rows by materialising the unfiltered query. Fine at 90
  units, wrong at 90,000. Replace with `select(func.count())` before the catalogue grows.
- No pagination cursor. Offset paging will skip rows if the catalogue is written to
  while someone is paging.

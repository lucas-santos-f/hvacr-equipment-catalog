# How AI tools were used

Required by criterion 2 of the course rubric, and useful anyway, because six months
from now nobody remembers which parts were generated and which were reasoned through.

## Tools

| Tool | Used for |
|---|---|
| Claude (Opus, in Claude Code) | Scaffolding, the bulk of the code, the first draft of every doc |
| `ruff` | Lint, run after every generated Python file |
| `pytest` / `vitest` | The actual check on whether generated code works |
| `pip-audit`, `bandit`, `npm audit` | Dependency and static scanning, see `security/` |

## Context files

Two files carry the standing context, both committed:

- `AGENTS.md` - the rules an agent has to follow in this repo. The contract rule, the
  "comparison stays on the server" rule and the "no real manufacturer data" rule all
  exist because an agent broke them once.
- `product-spec.md` - what the thing is for. Written before the code, not after.

Everything else was per-task prompting.

## What was delegated, and how

The order was deliberate: spec first, then the API contract, then the backend against
the contract, then the frontend against the contract, then infrastructure.

**1. Data model and spec.** Described the domain problem in prose, asked for a field
list. The first pass had `efficiency_rating` as a free string. Replaced it with
`capacity_kw / power_input_kw` computed server side, because a string nobody validates
is a field that will hold `"A++"` and `"high"` in the same column within a month.

**2. Comparison logic.** Asked for a function that takes a list of units and marks the
better value per field. Came back using `max()` and `min()` directly. That silently
picks the first row on a tie, which the UI would have rendered as a real winner. Added
the uniqueness check and six tests, three of which cover ties.

**3. Backend routes.** Generated against the field list. Reviewed by hand for the error
cases: inverted capacity window, unknown model, duplicate model, compare outside 2 to 4.
Each became a test before the route was accepted.

**4. `openapi.yaml`.** Not written. Generated from the app with `make spec`, then frozen
with `test_contract.py` so the two cannot drift. This was the one place where generating
and then checking in beat writing by hand.

**5. Frontend.** The API client and the selection rules were specified and generated,
then tested. Components were generated last and are deliberately thin, because an
untested component holding logic is the easiest way to end up with two sources of truth.

**6. Docker, compose, CI.** Generated, then corrected. Details below.

## What came back wrong

Keeping this section honest is the point of the exercise.

**`max()` on ties.** Described above. The generated comparison would have reported a
winner on two identical prices. Caught by writing the test first, not by reading the
code.

**Root user in the backend image.** The first Dockerfile had no `USER`. Added
`useradd --uid 10001 catalog`. Flagged again later by the hardening pass in
`security/scan-findings.md`, which is a reasonable argument for running the scanners
before you think you are done rather than after.

**CORS set to `*`.** The generated middleware allowed every origin and every method.
Narrowed to the two origins the app actually serves from, and to GET and POST.

**`.dockerignore` missing.** The first frontend image copied `node_modules` from the
host into the build context. Build went from slow to fast once that was fixed.

**Integration tests mixed into the unit directory.** Everything landed in one `tests/`
folder. Split into `tests/` and `tests/integration/` so CI reports them as two steps.
Criterion 9 asks for that separation, but it is worth it regardless: a failing
integration step and a failing unit step mean different things.

**A seed fixture that used real manufacturer names.** The first catalogue generator
reached for Grundfos, Danfoss and Carrier with invented specifications attached. That is
worse than useless, it is misleading. Replaced with five invented names and a warning
in the README.

## What was not delegated

- The direction of "better" per field. That is domain knowledge, and getting
  `sound_pressure_db` backwards would be invisible in a passing test suite.
- The decision to cap comparison at four.
- The scope cuts in `product-spec.md`.
- Every threshold in the seed generator. The numbers are invented, but the ranges are
  meant to be plausible, and a model guessing them produces chillers with a COP of 0.4.

## Verification

Nothing generated was accepted on the basis that it looked right.

1. `ruff check` on every Python file.
2. A test for every branch that can return a non-200.
3. `make spec` and confirm `git diff` on `openapi.yaml` is empty.
4. `docker compose up` and hit the API by hand before trusting the compose job.
5. The CI `compose` job asserts the seeded catalogue is exactly 90 units, so a silently
   broken seed fails the build rather than shipping an empty table.

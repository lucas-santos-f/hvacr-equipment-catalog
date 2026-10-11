# PR audit

Criterion 13 asks for PR audit output. This is the review gate every change goes
through, and a worked example of it catching something.

## The gate

Run on the diff, by a human, with the agent's own output treated as input rather than
as a result:

```bash
make lint
make test
make spec && git diff --exit-code openapi.yaml
make audit
git diff main...HEAD
```

Then four questions against the diff:

1. Does this change the API contract? If `openapi.yaml` moved, the frontend has to be
   rebuilt, because `VITE_API_URL` and the response shapes are baked in at build time.
2. Does it add a dependency? If so, why, and what does `pip-audit` or `npm audit` say
   about it.
3. Does it move logic out of `crud.py` or `src/lib/` into a router or a component?
   That is how the tested surface shrinks without anyone noticing.
4. Does any new string contain something personal or a credential?

## Worked example: the comparison function

The generated implementation was a single line that picked the winner with `max` or
`min` depending on the direction, straight off the dictionary of values.

Lint: clean. Tests at the time: passing. It reads correctly.

It is wrong. On two units with the same price, `min()` returns the first key it
encountered, and the UI renders that cell as the winner. The user sees a confident
recommendation derived from dictionary ordering.

Caught at question 1 of the gate, by asking what the function does when the two values
are equal, rather than by any tool.

The fix keeps the picker but checks that the winning value occurs exactly once before
marking it, and returns no winner otherwise. Three tests went in with it: a two-way
tie, a three-way tie on one field while another field still ranks, and every model
appearing in every row.

The general lesson, written into `AGENTS.md`: a change to comparison behaviour needs a
test in `test_comparison.py`. Passing tests prove the cases you thought of.

## Second example: the seed generator

The first catalogue used real manufacturer names with invented specifications attached.
Lint clean, tests green, scanners silent. It is a licensing problem and a credibility
problem, and no tool in the pipeline looks for it.

Caught at question 4, widened from "is there a credential here" to "is there anything
here that is not ours to publish". Now a hard rule in `AGENTS.md`.

## What the gate does not catch

Direction errors in domain logic. If `sound_pressure_db` were marked as higher-is-
better, the app would recommend the loudest chiller, every test would pass, and nothing
in the pipeline would object. The only defence is that `COMPARISON_FIELDS` is six lines
in one place and a reviewer can check all six at once. That is why it is a table and
not six scattered conditionals.

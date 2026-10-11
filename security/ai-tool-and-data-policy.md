# AI tool and data policy

Applies to anyone, human or agent, working on this repository.

## What may be sent to a model

Allowed: source files in this repo, the invented catalogue data, test output, scanner
output, error messages and stack traces from this app.

Not allowed, ever:

- Credentials of any kind. API keys, tokens, passwords, connection strings with a real
  password in them, session cookies, private keys.
- Personal data. Names, email addresses, phone numbers, postal addresses, national ID
  numbers, dates of birth. Including the maintainer's own.
- The contents of a real `.env`.
- Third-party material that is not ours to share: licensed manufacturer datasheets,
  customer drawings, anything under NDA.

The catalogue in this repo is invented precisely so that none of this comes up. If a
future version ingests real datasheets, this policy is the first file that has to change.

## Why the catalogue is fake

Real manufacturer specifications are licensed material, and the figures here are
generated. Mixing the two would be worse than either: a reader could not tell which
numbers were real, and the invented ones would borrow authority from the real brand.
`AGENTS.md` makes "no real manufacturer names" a hard rule for this reason.

## Secrets handling

- Secrets live in `.env`, which is in `.gitignore`.
- `.env.example` carries placeholder values and is committed.
- Deployment secrets live in the hosting provider and in GitHub repository secrets.
  `deploy.yml` reads `RENDER_BACKEND_HOOK` and `RENDER_FRONTEND_HOOK` and skips cleanly
  when they are absent, so a fork does not fail and no value is echoed into a log.
- `agent-hooks/block-secrets.sh` refuses a commit that stages a `.env` or that matches
  a key or personal-email pattern. It is crude on purpose: it catches the paste
  accident, which is the one that actually happens.

## Agent permissions

An agent on this repo may read any file, run the test suite, the linter and the
scanners, and edit source. It may not push to `main`, open a pull request against
another repository, call a network service other than the local backend, or install a
dependency without that dependency appearing in a diff a human reads.

The full matrix is in [docs/permissions.md](../docs/permissions.md).

## Review

Generated code is not trusted because it is generated. The gate is the same for every
change regardless of who wrote it:

1. `make lint`
2. `make test` - a test per non-200 the route can return
3. `make spec` and an empty `git diff` on `openapi.yaml`
4. `make audit`
5. A human reads the diff

Five of the mistakes in `docs/ai-workflow.md` were caught at step 2 or step 5, not by a
scanner.

## Attribution

AI assistance is disclosed in the README and detailed in `docs/ai-workflow.md`. It is
not hidden and not overstated: the file says what was delegated and what was not.

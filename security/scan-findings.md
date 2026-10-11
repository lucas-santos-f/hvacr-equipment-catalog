# Scan findings

Run date: 11 October 2026. Tools: `pip-audit` 2.9.0, `bandit` 1.8.6, `npm audit`,
`ruff` 0.14.0. Reproduce with `make audit`.

## Summary

| Scanner | Before | After | Status |
|---|---|---|---|
| `pip-audit` | 12 advisories, 1 package | 0 | fixed |
| `npm audit` | 3 (2 critical, 1 moderate) | 0 | fixed |
| `bandit` | 0 | 0 | clean |
| `ruff` | 6 | 0 | fixed |

## 1. starlette, 12 advisories, fixed

`pip-audit -r backend/requirements.txt` on the original pin:

```
Found 12 known vulnerabilities in 1 package
Name      Version ID              Fix Versions
starlette 0.48.0  PYSEC-2026-249  1.3.1
starlette 0.48.0  PYSEC-2026-248  1.3.0
starlette 0.48.0  PYSEC-2026-2281 1.1.0
starlette 0.48.0  PYSEC-2026-2280 1.1.0
starlette 0.48.0  PYSEC-2026-161  1.0.1
starlette 0.48.0  PYSEC-2026-1942 0.49.1
```

Starlette arrived transitively through `fastapi==0.118.0`, whose floor
(`starlette>=0.46.0`) permits the vulnerable version. Nothing in this project pinned it.

**Fix.** Upgraded to `fastapi==0.143.0` and pinned `starlette==1.7.0` explicitly in
`requirements.txt`, above fastapi's own floor, with a comment saying why. Transitive
dependencies that carry advisories get pinned directly; leaving it to the resolver is
how the vulnerable version got in.

That is a major-version jump for starlette, so it was verified rather than assumed: all
28 backend tests pass against `fastapi 0.143.0` with `starlette 1.7.0`. Re-audit is
clean.

## 2. tinypool and vitest, 2 critical and 1 moderate, fixed

```
tinypool        critical   fix: vitest@5.0.3 (semver major)
vitest          critical
@vitest/mocker  moderate
```

Development dependencies only; none ship in the frontend image, which is a static
bundle served by nginx. Fixed anyway, because a critical in the test runner is a
critical in whatever runs CI.

**Fix.** `vitest` to 5.0.3. All 24 frontend tests pass on the new major. Re-audit
reports 0.

## 3. bandit, clean

`bandit -q -r backend/app` reports nothing across all nine modules. The app has no
`subprocess`, no `eval`, no `pickle`, no `random` used for anything security-adjacent,
and every query goes through SQLAlchemy's expression language rather than string
interpolation.

## 4. ruff, 6 findings, fixed

Five `B008` on `Depends(...)` in default arguments. That is the documented FastAPI
pattern and the finding is a false positive here, so it is suppressed in `ruff.toml`
scoped to `app/routers/*.py` only, with the reason in a comment. Suppressing it
repo-wide would hide a real mutable-default bug somewhere else later.

One `UP042`: `class Category(str, Enum)` should be `StrEnum` on Python 3.11 and up.
Changed, no behaviour difference.

## Findings fixed during development, not by a scanner

These came out of manual review of generated code and are recorded because they are the
class of thing a scanner would not have caught in time.

**Container ran as root.** The first backend Dockerfile had no `USER`. Added
`useradd --uid 10001 catalog`. A scanner on the image would have caught it; a scanner on
the source would not.

**CORS allowed every origin.** The generated middleware had `allow_origins=["*"]` with
all methods. Narrowed to the configured origins and to GET and POST. Nothing here needs
credentials across origins.

**`.env` could have been committed.** Added to `.gitignore` with a negated
`!.env.example`, and `agent-hooks/block-secrets.sh` blocks the commit outright.

## Accepted, not fixed

**The write endpoint is unauthenticated.** `POST /equipment` is open. The data is
invented and there is no account system, so there is nothing to protect and no
privilege to escalate. This becomes a real finding the moment the catalogue holds
anything someone paid for. Written down rather than silently accepted.

**No rate limiting.** Same reasoning. A public deployment would want it at the edge,
not in the app.

**Error detail is returned to the client.** `ApiError` surfaces the backend's `detail`
string. Every one of those strings is written by hand in a router and none contains
anything internal, but that is a convention, not an enforced boundary.

# Workflow: add an endpoint

Reusable checklist. Follow it in order; the order is what keeps the contract honest.

1. **Write the acceptance criteria first**, in `product-spec.md`. Every status code the
   route can return, named. If you cannot say what a 422 means here, the route is not
   designed yet.

2. **Add the schema** in `backend/app/schemas.py`. Bounds go on the Pydantic field, not
   in the route body. `Field(gt=0)` is a contract; an `if` in the handler is not.

3. **Add the query or the logic** in `backend/app/crud.py`. If it would still be true
   without HTTP, it belongs here and not in the router.

4. **Add the route** in the relevant file under `backend/app/routers/`. The router
   parses, calls crud, maps a missing row to a 404. Nothing else.

5. **Regenerate the contract**: `make spec`. Check the diff is what you expected.

6. **Test both layers.** Logic in `tests/`, the route in `tests/integration/`. One test
   per status code from step 1.

7. **Expose it to the frontend** by adding a method to `frontend/src/api/client.js`.
   No component calls `fetch`.

8. **Run the gate**: `make lint && make test && make spec && git diff --exit-code openapi.yaml`.

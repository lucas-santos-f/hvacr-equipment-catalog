# Workflow: add a field to the catalogue

More invasive than it looks, because the field has to reach the comparison table and
the seed data.

1. `backend/app/models.py` - add the column. Index it only if it will be filtered on.
2. `backend/app/schemas.py` - add it to `EquipmentBase` with its bounds.
3. **Decide whether it is comparable.** If yes, add it to `COMPARISON_FIELDS` in
   `backend/app/crud.py` with `"max"` or `"min"`. Getting this backwards is invisible in
   a passing suite, so say out loud why the direction is what it is.
4. `backend/app/data/catalog_seed.json` - every one of the 90 units needs the field, or
   the seed fails on a NOT NULL.
5. `frontend/src/lib/selection.js` - add a label to `LABELS`, and a branch in
   `formatValue` if it is not a plain number.
6. `frontend/src/components/ResultsTable.jsx` - a column, if it belongs in the list view.
7. `make spec`.
8. Tests: a comparison test for the direction, an integration test that the field comes
   back on detail.

There are no migrations. The table is recreated from `Base.metadata.create_all`, so a
local database needs `docker compose down -v` to pick up a column.

# Product specification

## Who this is for

Someone specifying HVAC-R equipment for a building: a mechanical engineer, an installer
pricing a replacement, a student working through a selection exercise. They know what
duty they need and roughly what refrigerant is acceptable. They do not want to read six
PDFs to find out which of four units is quietest.

## The job to be done

> I have a 200 kW cooling load, R32 or a low-GWP alternative, and I need to hand over a
> shortlist of three units with a defensible reason for the one I picked.

Today that means a spreadsheet typed by hand from manufacturer PDFs. The spreadsheet is
where the mistakes come from: a figure copied from the wrong row, a price from last
year, a sound level measured at a different distance.

## Scope

### In

1. **Search.** Filter the catalogue by category, refrigerant, manufacturer and a
   capacity window. Results sorted by capacity so the shortlist reads naturally.
2. **Detail.** One unit, all its fields, with COP computed server side so the number is
   the same everywhere it appears.
3. **Compare.** Two to four units in one table. Each row marks the better figure.
   Direction is per field: capacity and COP go up, power draw, noise, weight and price
   go down.
4. **Ingest.** POST a new unit. Rejects a duplicate model code and out-of-range values.

### Out, deliberately

- Authentication. There is nothing here worth protecting and no user-owned data.
- Editing or deleting units. Corrections go through a new seed release.
- Quoting, availability, lead times. That is a different product.
- Unit conversion. Metric only, which is what the target user works in.
- Real manufacturer data. Licensing aside, the point of this project is the system, not
  the catalogue.

## Decisions and why

**Comparison lives on the server, not in the browser.** The direction of "better" per
field is domain logic. If the frontend owned it, a second client would have to
reimplement it and the two would drift. The API returns the winner already marked.

**Ties return no winner.** A naive `max()` would pick whichever row came first, which
reads as a real result to the user. The code checks that the winning value is unique
and returns `null` otherwise.

**Compare is capped at four.** Beyond that the table stops fitting on a laptop screen
and the feature stops being useful. The cap is enforced in the API, and the UI disables
the checkbox rather than letting the user hit an error.

**COP is derived, never stored.** Storing it would let it go stale against capacity and
power input. It is a property on the model and lands in the read schema.

**Passive equipment still has a COP.** For a heat exchanger or a pump the "power input"
is pumping loss, so the ratio comes out at 20 to 60 rather than 3 to 4. That is correct
arithmetic and misleading as a label. Known rough edge, written up in
[ops/runbook.md](ops/runbook.md) rather than papered over.

## Data model

One table. The catalogue is flat and joining manufacturers out would buy nothing.

| Field | Type | Note |
|---|---|---|
| `model` | string, unique | Vendor model code, the public identifier |
| `manufacturer` | string | |
| `category` | enum | chiller, compressor, heat_exchanger, circulator_pump, fan_coil |
| `refrigerant` | string | `none` for water-side equipment |
| `capacity_kw` | float > 0 | Nominal duty |
| `power_input_kw` | float > 0 | Absorbed power at nominal duty |
| `voltage` | string | Supply, e.g. `400V/3ph/50Hz` |
| `sound_pressure_db` | float >= 0 | `0` where the manufacturer publishes none |
| `weight_kg` | float > 0 | Operating weight |
| `price_eur` | float >= 0 | List price |
| `cop` | derived | `capacity_kw / power_input_kw`, two decimals |

## Acceptance criteria

- Filtering by `category=chiller` returns only chillers, and `total` reflects the filter
  rather than the page.
- `min_capacity` above `max_capacity` returns 422, not an empty list. An empty list
  would read as "nothing matches" when the real problem is the query.
- Comparing fewer than two or more than four models returns 422.
- Comparing an unknown model code returns 404 naming the code.
- Posting a model code that already exists returns 409.
- A tie on any row leaves `best` null.
- The committed `openapi.yaml` matches the running app, enforced in CI.

## Not yet decided

Whether to keep price in the model at all. It ages fastest of any field and there is no
date on it. Likely to become a separate table with an effective date, or to be dropped.

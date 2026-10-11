import pytest

from app.crud import build_comparison
from app.models import Equipment


def unit(model, **kw):
    base = dict(model=model, manufacturer="Thermexa", category="chiller", refrigerant="R32",
                capacity_kw=100.0, power_input_kw=25.0, voltage="400V/3ph/50Hz",
                sound_pressure_db=70.0, weight_kg=900.0, price_eur=30000.0)
    base.update(kw)
    return Equipment(**base)


def row(comparison, field):
    return next(r for r in comparison.rows if r.field == field)


def test_cop_is_capacity_over_input():
    assert unit("A", capacity_kw=200.0, power_input_kw=50.0).cop == 4.0


def test_cop_of_zero_input_does_not_divide_by_zero():
    assert unit("A", power_input_kw=0.0).cop == 0.0


def test_higher_capacity_wins():
    c = build_comparison([unit("A", capacity_kw=120.0), unit("B", capacity_kw=90.0)])
    assert row(c, "capacity_kw").best == "A"


@pytest.mark.parametrize("field,values,winner", [
    ("price_eur", (25000.0, 31000.0), "A"),
    ("sound_pressure_db", (74.0, 61.0), "B"),
    ("weight_kg", (1200.0, 800.0), "B"),
    ("power_input_kw", (30.0, 22.0), "B"),
])
def test_lower_is_better_for_cost_fields(field, values, winner):
    c = build_comparison([unit("A", **{field: values[0]}), unit("B", **{field: values[1]})])
    assert row(c, field).best == winner


def test_a_tie_has_no_winner():
    c = build_comparison([unit("A", price_eur=25000.0), unit("B", price_eur=25000.0)])
    assert row(c, "price_eur").best is None


def test_three_way_tie_on_one_field_still_ranks_the_others():
    units = [unit("A", price_eur=10.0, capacity_kw=100.0),
             unit("B", price_eur=10.0, capacity_kw=150.0),
             unit("C", price_eur=10.0, capacity_kw=120.0)]
    c = build_comparison(units)
    assert row(c, "price_eur").best is None
    assert row(c, "capacity_kw").best == "B"


def test_every_model_appears_in_every_row():
    c = build_comparison([unit("A"), unit("B"), unit("C")])
    assert c.models == ["A", "B", "C"]
    for r in c.rows:
        assert set(r.values) == {"A", "B", "C"}

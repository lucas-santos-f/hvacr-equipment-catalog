from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Equipment
from app.schemas import Comparison, ComparisonRow, EquipmentCreate

# Which direction counts as "better" when comparing two units on the same field.
# Capacity and efficiency go up, everything that costs you goes down.
COMPARISON_FIELDS = {
    "capacity_kw": "max",
    "power_input_kw": "min",
    "cop": "max",
    "sound_pressure_db": "min",
    "weight_kg": "min",
    "price_eur": "min",
}


def list_equipment(db: Session, category=None, refrigerant=None, manufacturer=None,
                   min_capacity=None, max_capacity=None, limit=50, offset=0):
    stmt = select(Equipment)
    if category:
        stmt = stmt.where(Equipment.category == category)
    if refrigerant:
        stmt = stmt.where(Equipment.refrigerant == refrigerant)
    if manufacturer:
        stmt = stmt.where(Equipment.manufacturer == manufacturer)
    if min_capacity is not None:
        stmt = stmt.where(Equipment.capacity_kw >= min_capacity)
    if max_capacity is not None:
        stmt = stmt.where(Equipment.capacity_kw <= max_capacity)

    total = len(db.execute(stmt).scalars().all())
    rows = db.execute(
        stmt.order_by(Equipment.capacity_kw).limit(limit).offset(offset)
    ).scalars().all()
    return rows, total


def get_by_model(db: Session, model: str):
    return db.execute(select(Equipment).where(Equipment.model == model)).scalar_one_or_none()


def create(db: Session, payload: EquipmentCreate):
    item = Equipment(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def build_comparison(units: list[Equipment]) -> Comparison:
    models = [u.model for u in units]
    rows = []

    for field, direction in COMPARISON_FIELDS.items():
        values = {u.model: getattr(u, field) for u in units}
        numeric = {m: v for m, v in values.items() if isinstance(v, (int, float))}

        best = None
        if len(numeric) > 1:
            picker = max if direction == "max" else min
            winner = picker(numeric, key=numeric.get)
            # A tie has no winner - calling one of them best would be arbitrary.
            if list(numeric.values()).count(numeric[winner]) == 1:
                best = winner

        rows.append(ComparisonRow(field=field, values=values, best=best))

    return Comparison(models=models, rows=rows)

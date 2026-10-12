from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import Category, Comparison, EquipmentCreate, EquipmentPage, EquipmentRead
from app.security import require_api_key

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("", response_model=EquipmentPage)
def search(
    category: Category | None = None,
    refrigerant: str | None = None,
    manufacturer: str | None = None,
    min_capacity: float | None = Query(None, ge=0),
    max_capacity: float | None = Query(None, ge=0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if min_capacity is not None and max_capacity is not None and min_capacity > max_capacity:
        raise HTTPException(422, "min_capacity cannot be greater than max_capacity")

    items, total = crud.list_equipment(
        db,
        category=category.value if category else None,
        refrigerant=refrigerant,
        manufacturer=manufacturer,
        min_capacity=min_capacity,
        max_capacity=max_capacity,
        limit=limit,
        offset=offset,
    )
    return EquipmentPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/compare", response_model=Comparison)
def compare(models: str = Query(description="Comma separated model codes, 2 to 4"),
            db: Session = Depends(get_db)):
    wanted = [m.strip() for m in models.split(",") if m.strip()]
    if not 2 <= len(wanted) <= 4:
        raise HTTPException(422, "compare between 2 and 4 models")

    units = []
    for model in wanted:
        unit = crud.get_by_model(db, model)
        if unit is None:
            raise HTTPException(404, f"unknown model {model}")
        units.append(unit)

    return crud.build_comparison(units)


@router.get("/{model}", response_model=EquipmentRead)
def detail(model: str, db: Session = Depends(get_db)):
    unit = crud.get_by_model(db, model)
    if unit is None:
        raise HTTPException(404, f"unknown model {model}")
    return unit


@router.post(
    "",
    response_model=EquipmentRead,
    status_code=201,
    dependencies=[Depends(require_api_key)],
)
def add(payload: EquipmentCreate, db: Session = Depends(get_db)):
    if crud.get_by_model(db, payload.model):
        raise HTTPException(409, f"model {payload.model} already exists")
    return crud.create(db, payload)

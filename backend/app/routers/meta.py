from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Equipment

router = APIRouter(tags=["meta"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/facets")
def facets(db: Session = Depends(get_db)):
    """Distinct values the frontend needs to build its filter dropdowns."""
    def distinct(column):
        return sorted(db.execute(select(column).distinct()).scalars().all())

    capacities = db.execute(select(Equipment.capacity_kw)).scalars().all()
    return {
        "categories": distinct(Equipment.category),
        "refrigerants": distinct(Equipment.refrigerant),
        "manufacturers": distinct(Equipment.manufacturer),
        "capacity_range": {
            "min": min(capacities) if capacities else 0,
            "max": max(capacities) if capacities else 0,
        },
    }

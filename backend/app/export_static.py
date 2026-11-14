"""Snapshot of the catalogue for the static demo build, which has no API behind it.

Writes frontend/src/api/catalog-snapshot.json, and the comparison cases the frontend
tests hold its snapshot adapter to. Run with `make snapshot`.
"""
import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import crud
from app.database import Base
from app.routers.meta import facets
from app.schemas import EquipmentRead
from app.seed import seed_if_empty

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
SNAPSHOT_FILE = FRONTEND / "src" / "api" / "catalog-snapshot.json"
CASES_FILE = FRONTEND / "tests" / "fixtures" / "compare-cases.json"


def build() -> tuple[dict, list[dict]]:
    engine = create_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_if_empty(db)
        units, _ = crud.list_equipment(db, limit=10_000)

        snapshot = {
            "comparison_fields": crud.COMPARISON_FIELDS,
            "facets": facets(db),
            "items": [EquipmentRead.model_validate(u).model_dump(mode="json") for u in units],
        }

        by_category: dict[str, list] = {}
        for unit in units:
            by_category.setdefault(unit.category, []).append(unit)
        groups = [g[:size] for g in by_category.values() for size in (2, 3, 4)]
        groups.append([units[0], units[-1]])
        cases = [
            {
                "models": [u.model for u in group],
                "expected": crud.build_comparison(group).model_dump(mode="json"),
            }
            for group in groups
        ]
    engine.dispose()
    return snapshot, cases


def main() -> None:
    snapshot, cases = build()
    for path, data in ((SNAPSHOT_FILE, snapshot), (CASES_FILE, cases)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

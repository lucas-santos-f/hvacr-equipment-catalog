import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Equipment

SEED_FILE = Path(__file__).parent / "data" / "catalog_seed.json"


def load_seed() -> list[dict]:
    return json.loads(SEED_FILE.read_text(encoding="utf-8"))


def seed_if_empty(db: Session) -> int:
    if db.execute(select(Equipment).limit(1)).scalar_one_or_none() is not None:
        return 0

    rows = load_seed()
    db.add_all(Equipment(**row) for row in rows)
    db.commit()
    return len(rows)

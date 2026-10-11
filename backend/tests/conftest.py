import os
import tempfile

import pytest

os.environ["SEED_ON_STARTUP"] = "false"
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Equipment  # noqa: E402

SAMPLE = [
    dict(model="TX-CH900", manufacturer="Thermexa", category="chiller", refrigerant="R32",
         capacity_kw=200.0, power_input_kw=50.0, voltage="400V/3ph/50Hz",
         sound_pressure_db=70.0, weight_kg=1500.0, price_eur=62000.0),
    dict(model="NV-CH901", manufacturer="Norvent", category="chiller", refrigerant="R290",
         capacity_kw=180.0, power_input_kw=60.0, voltage="400V/3ph/50Hz",
         sound_pressure_db=66.0, weight_kg=1400.0, price_eur=58000.0),
    dict(model="FG-PU902", manufacturer="Frigora", category="circulator_pump", refrigerant="none",
         capacity_kw=12.0, power_input_kw=0.4, voltage="230V/1ph/50Hz",
         sound_pressure_db=44.0, weight_kg=38.0, price_eur=2100.0),
]


@pytest.fixture(scope="session", autouse=True)
def database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add_all(Equipment(**row) for row in SAMPLE)
        db.commit()
    yield
    Base.metadata.drop_all(engine)
    engine.dispose()
    os.unlink(_db_path)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session

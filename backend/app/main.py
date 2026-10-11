from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import equipment, meta
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    if settings.seed_on_startup:
        with SessionLocal() as db:
            seed_if_empty(db)
    yield


app = FastAPI(
    title="HVAC-R Equipment Catalogue",
    version="1.0.0",
    description="Search and compare cooling and heating equipment by duty, refrigerant and price.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(meta.router)
app.include_router(equipment.router)

import os


def normalise_database_url(url: str) -> str:
    """Render hands out `postgres://`, SQLAlchemy 2 with psycopg 3 wants
    `postgresql+psycopg://`. Rewriting here means the deployment config can pass the
    provider's string through untouched."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def normalise_origin(origin: str) -> str:
    """Render can only inject a bare hostname into an env var, and CORS needs a full
    origin. Anything without a scheme is assumed to be https, which is true of every
    host Render issues."""
    origin = origin.strip().rstrip("/")
    if not origin:
        return ""
    if origin.startswith(("http://", "https://")):
        return origin
    return f"https://{origin}"


class Settings:
    def __init__(self):
        self.database_url = normalise_database_url(
            os.getenv("DATABASE_URL", "sqlite:///./catalog.db")
        )
        raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
        self.cors_origins = [o for o in (normalise_origin(p) for p in raw_origins.split(",")) if o]
        self.seed_on_startup = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"


settings = Settings()

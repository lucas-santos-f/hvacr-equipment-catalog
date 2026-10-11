import os


class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./catalog.db")
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        self.seed_on_startup = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"


settings = Settings()

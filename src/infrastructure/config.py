from pydantic import BaseModel
import os


class Settings(BaseModel):
    """Конфигурация приложения"""

    app_name: str = "url-shortener"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./url_shortener.db"
    )

    short_id_length: int = int(os.getenv("SHORT_ID_LENGTH", "6"))
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")


settings = Settings()

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "url_shortener"

    # App
    SHORT_ID_LENGTH: int = 6
    BASE_URL: str = "http://localhost:8000"

    @property
    def database_url(self) -> str:
        """Получение URL для подключения к БД"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

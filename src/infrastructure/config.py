from pydantic import BaseModel
import os


class Settings(BaseModel):
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "db") 
    DB_PORT: int = int(os.getenv("DB_PORT", "5432")) 
    DB_USER: str = os.getenv("DB_USER", "postgres") 
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres") 
    DB_NAME: str = os.getenv("DB_NAME", "url_shortener") 
    
    SHORT_ID_LENGTH: int = int(os.getenv("SHORT_ID_LENGTH", "6")) # кастомизация длинны не работает, не доделал
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
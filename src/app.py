import uvicorn
from fastapi import FastAPI
from tt_Short_link_sev.src.api.routes.links import LinksRoutable
from tt_Short_link_sev.src.api.exception_handlers.link import link_not_found_exception_handler
from tt_Short_link_sev.src.core.exceptions.link import LinkNotFoundError
from tt_Short_link_sev.src.infrastructure.config import settings
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from tt_Short_link_sev.src.infrastructure.db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan контекст для FastAPI.
    Создает таблицы при старте и закрывает соединения при остановке.
    """
    # Код при старте
    print("Инициализация БД...")
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Таблицы созданы!")

    yield

    # Код при остановке
    print("Завершение работы...")

# Создаем приложение
APP = FastAPI(
    title=settings.app_name,
    docs_url="/docs",
    lifespan=lifespan
)
APP.include_router(LinksRoutable().router,)

APP.add_exception_handler(
    LinkNotFoundError,
    link_not_found_exception_handler,
)


# Запуск приложения (для разработки)
if __name__ == "__main__":
    uvicorn.run(
        "app:APP",  # строка для запуска модуля
        host="0.0.0.0",
        port=8000,
        reload=True,  # авто-перезагрузка при разработке
        log_level=settings.log_level.lower(),
    )
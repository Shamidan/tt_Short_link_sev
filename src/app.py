import uvicorn
from fastapi import FastAPI
from src.api.routes.links import LinksRoutable
from src.api.exception_handlers.link import link_not_found_exception_handler
from src.core.exceptions.link import LinkNotFoundError
from src.infrastructure.config import settings
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from src.infrastructure.db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan контекст для FastAPI.
    Создает таблицы при старте и закрывает соединения при остановке.
    """

    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

    yield


APP = FastAPI(
    docs_url="/docs",
    lifespan=lifespan
)
APP.include_router(LinksRoutable().router,)

APP.add_exception_handler(
    LinkNotFoundError,
    link_not_found_exception_handler,
)


if __name__ == "__main__":
    uvicorn.run(
        "app:APP",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )
from tt_Short_link_sev.src.app import APP
from src.infrastructure.db.models import Base, Link
from src.infrastructure.db.session_maker import get_session
from src.core.services.link import LinkService
from src.core.exceptions.link import LinkNotFoundError
from src.core.services.short_id_generator import SimpleShortIdGenerator

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


# ==================== Fixtures ====================

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    """Создание и удаление таблиц для всей тестовой сессии"""

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(init_models())
    yield
    asyncio.run(drop_models())
    asyncio.run(engine.dispose())


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для тестового клиента"""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    APP.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
            transport=ASGITransport(app=APP),
            base_url="http://test",
            follow_redirects=False,
    ) as ac:
        yield ac

    APP.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_unit_get_stats_raises_not_found():
    """
    Проверка, что сервис выбрасывает исключение для несуществующей ссылки
    """
    mock_session = Mock(spec=AsyncSession)
    mock_repo = AsyncMock()

    mock_repo.get_clicks_count.return_value = None

    mock_id_generator = Mock(spec=SimpleShortIdGenerator)

    service = LinkService(mock_session, mock_id_generator)
    service.link_repo = mock_repo

    with pytest.raises(LinkNotFoundError) as exc_info:
        await service.get_clicks_count("nonexistent")

    mock_repo.get_clicks_count.assert_called_once_with("nonexistent")

    assert "nonexistent" in str(exc_info.value)


@pytest.mark.asyncio
async def test_unit_create_link_handles_collisions():
    """
    UNIT TEST #2: Проверка, что сервис генерирует уникальный short_id при коллизиях
    Тестирует: LinkService.create_short_link
    """
    # Подготовка моков
    mock_session = Mock(spec=AsyncSession)
    mock_repo = AsyncMock()
    mock_id_generator = Mock(spec=SimpleShortIdGenerator)
    
    mock_id_generator.generate.side_effect = ["abc123", "abc123", "xyz789"]
    
    mock_repo.get_by_short_id.side_effect = [
        Mock(spec=Link),  
        Mock(spec=Link), 
        None,  
    ]

    service = LinkService(mock_session, mock_id_generator)
    service.link_repo = mock_repo

    short_id = await service.create_short_link("https://example.com")

    assert short_id == "xyz789", "Должен быть выбран уникальный ID после коллизий"
    
    assert mock_id_generator.generate.call_count == 3
    
    assert mock_repo.get_by_short_id.call_count == 3
    mock_repo.get_by_short_id.assert_any_call("abc123")
    mock_repo.get_by_short_id.assert_any_call("xyz789")

    mock_repo.create.assert_called_once_with("xyz789", "https://example.com")

@pytest.mark.asyncio
async def test_api_create_and_redirect(client: AsyncClient):
    """
    Полный цикл создания ссылки и перехода по ней
    """
    create_response = await client.post(
        "/shorten",
        json={"original_url": "https://www.youtube.com/watch?v=3eYnt8u-t1M"},
    )
    assert create_response.status_code == 201
    data = create_response.json()
    short_id = data["short_id"]
    assert data["original_url"] == "https://www.youtube.com/watch?v=3eYnt8u-t1M"

    redirect_response = await client.get(f"/{short_id}")
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://www.youtube.com/watch?v=3eYnt8u-t1M"

    stats_response = await client.get(f"/stats/{short_id}")
    assert stats_response.status_code == 200
    assert stats_response.json()["clicks"] == 1


@pytest.mark.asyncio
async def test_api_not_found_handling(client: AsyncClient):
    """
    Проверка обработки несуществующих ссылок
    """

    redirect_response = await client.get("/nonexistent")
    assert redirect_response.status_code == 404
    assert "Link with id 'nonexistent' not found" in redirect_response.json()["detail"]

    stats_response = await client.get("/stats/nonexistent")
    assert stats_response.status_code == 404
    assert "Link with id 'nonexistent' not found" in stats_response.json()["detail"]
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services.base import BaseService
from src.infrastructure.db.models import Link
from src.infrastructure.db.repositories.link import LinkRepository
from src.core.services.short_id_generator import SimpleShortIdGenerator
# from src.core.services.short_id_generator import ShortIdGenerator
from src.core.exceptions.link import LinkNotFoundError


# TODO SimpleShortIdGenerator поменять на нормальный
class LinkService(BaseService):
    """Сервис для работы с короткими ссылками"""

    def __init__(
            self,
            session: AsyncSession,
            id_generator: Optional[SimpleShortIdGenerator] = None
    ):
        self.session = session
        self.link_repo = LinkRepository(session)
        self.id_generator = id_generator or SimpleShortIdGenerator()

    async def _get_link_or_fail(self, short_id: str) -> Link:
        """
        Внутренний метод для получения ссылки или выброса исключения
        """
        link = await self.link_repo.get_by_short_id(short_id)
        if not link:
            raise LinkNotFoundError(short_id)
        return link

    async def create_short_link(self, original_url: str) -> str:
        """
        Создание короткой ссылки
        """
        # Генерируем уникальный short_id
        short_id = await self._generate_unique_short_id()

        # Создаем запись в БД
        await self.link_repo.create(short_id, original_url)

        return short_id

    async def get_original_url_and_increment_clicks(self, short_id: str) -> str:
        """
        Получение оригинальной ссылки и увеличение счетчика переходов
        """
        link = await self._get_link_or_fail(short_id)

        # Атомарно увеличиваем счетчик
        updated_link = await self.link_repo.increment_clicks(short_id)

        return updated_link.original_url

    async def get_clicks_count(self, short_id: str) -> int:
        """
        Получение количества переходов по ссылке
        """
        clicks = await self.link_repo.get_clicks_count(short_id)

        if clicks is None:
            raise LinkNotFoundError(short_id)

        return clicks

    async def _generate_unique_short_id(self) -> str:
        """
        Генерация уникального короткого идентификатора
        """
        while True:
            short_id = self.id_generator.generate()

            existing = await self.link_repo.get_by_short_id(short_id)

            if not existing:
                return short_id

    async def get_link_info(self, short_id: str) -> Link:
        """
        Получение полной информации о ссылке
        """
        return await self._get_link_or_fail(short_id)
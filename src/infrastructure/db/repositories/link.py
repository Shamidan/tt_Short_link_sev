from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional

from src.infrastructure.db.models import Link
from src.infrastructure.db.repositories._base import AbstractRepository


class LinkRepository(AbstractRepository):
    """
    Репозиторий для работы с ссылками.
    """

    async def create(self, short_id: str, original_url: str) -> Link:
        link = Link(
            short_id=short_id,
            original_url=original_url,
            clicks=0,
        )
        self.session.add(link)

        try:
            await self.session.commit()
            await self.session.refresh(link)
            return link
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_by_short_id(self, short_id: str) -> Optional[Link]:
        """
        Получение ссылки по id
        """
        result = await self.session.execute(
            select(Link).where(Link.short_id == short_id)
        )
        return result.scalar_one_or_none()

    async def increment_clicks(self, short_id: str) -> Optional[Link]:
        """
        Увеличение счетчика кликов
        """
        result = await self.session.execute(
            update(Link)
            .where(Link.short_id == short_id)
            .values(
                clicks=Link.clicks + 1,
                last_accessed=datetime.now()
            )
            .returning(Link)
        )
        await self.session.commit()

        return result.scalar_one_or_none()

    async def get_clicks_count(self, short_id: str) -> Optional[int]:
        """
        Получение количества переходов по ссылке
        """
        result = await self.session.execute(
            select(Link.clicks).where(Link.short_id == short_id)
        )
        return result.scalar_one_or_none()


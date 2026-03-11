from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services.link import LinkService
from src.core.services.short_id_generator import SimpleShortIdGenerator
from src.infrastructure.db.session_maker import get_session


# TODO SimpleShortIdGenerator поменять на нормальный
def get_short_id_generator() -> SimpleShortIdGenerator:
    """
    Dependency для получения генератора коротких ID.
    Создает новый экземпляр при каждом запросе (легковесный объект).
    """
    return SimpleShortIdGenerator()


def get_link_service(
        session: AsyncSession = Depends(get_session),
        id_generator: SimpleShortIdGenerator = Depends(get_short_id_generator),
) -> LinkService:
    """
    Dependency для получения сервиса ссылок.
    Автоматически внедряет сессию БД и генератор ID.
    """
    return LinkService(
        session=session,
        id_generator=id_generator
    )

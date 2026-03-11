from fastapi import Depends, status
from classy_fastapi import Routable, get, post
from fastapi.responses import RedirectResponse, JSONResponse

from src.api.schemas.link import (
    LinkCreateRequest,
    LinkResponse,
    LinkStatsResponse,
)
from src.core.services.link import LinkService
from src.api.dependencies import get_link_service
from src.core.exceptions.link import LinkNotFoundError


class LinksRoutable(Routable):
    """
    Роуты для работы с короткими ссылками.
    """

    @post(
        "/shorten",
        response_model=LinkResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Создать короткую ссылку",
        description="Принимает длинную ссылку и возвращает короткий идентификатор",
        responses={
            400: {"description": "Неверный формат URL"},
            409: {"description": "Конфликт при генерации ID (очень редко)"},
        },
    )
    async def create_short_link(
            self,
            payload: LinkCreateRequest,
            service: LinkService = Depends(get_link_service),
    ) -> LinkResponse:
        """
        Создание короткой ссылки.

        - **original_url**: длинная ссылка для сокращения (должна начинаться с http:// или https://)

        Возвращает короткий идентификатор, который можно использовать как `/abc123`
        """
        short_id = await service.create_short_link(str(payload.original_url))

        return LinkResponse(
            short_id=short_id,
            original_url=str(payload.original_url),
        )

    @get(
        "/{short_id}",
        response_class=RedirectResponse,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        summary="Перейти по короткой ссылке",
        description="Редиректит на оригинальную ссылку и увеличивает счетчик переходов",
        responses={
            404: {"description": "Ссылка не найдена"},
        },
    )
    async def redirect_to_original(
            self,
            short_id: str,
            service: LinkService = Depends(get_link_service),
    ) -> RedirectResponse:
        """
        Редирект на оригинальную ссылку.

        - **short_id**: короткий идентификатор (например, abc123)

        При каждом вызове увеличивает счетчик переходов.
        """
        try:
            original_url = await service.get_original_url_and_increment_clicks(short_id)

            return RedirectResponse(url=original_url)
        except LinkNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Link with id '{short_id}' not found"},
            )

    @get("/stats/{short_id}", response_model=LinkStatsResponse)
    async def get_link_stats(
            self,
            short_id: str,
            service: LinkService = Depends(get_link_service),
    ) -> LinkStatsResponse:
        try:
            link = await service.get_link_info(short_id)
            
            return LinkStatsResponse(
                short_id=link.short_id,
                clicks=link.clicks,
                original_url=link.original_url,
                created_at=link.created_at
            )
        except LinkNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Link with id '{short_id}' not found"},
            )
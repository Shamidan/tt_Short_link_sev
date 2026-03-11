from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions.link import LinkNotFoundError


async def link_not_found_exception_handler(
    request: Request,
    exc: LinkNotFoundError,
) -> JSONResponse:

    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )
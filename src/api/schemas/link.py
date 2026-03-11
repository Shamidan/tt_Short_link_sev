from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional


class LinkCreateRequest(BaseModel):
    """
    Схема для создания короткой ссылки.
    Принимает длинную ссылку от пользователя.
    """
    original_url: HttpUrl = Field(
        description='Оригинальная длинная ссылка для сокращения',
        examples=['https://example.com/very/long/url/that/needs/shortening']
    )


class LinkResponse(BaseModel):
    """
    Схема ответа при создании ссылки.
    Возвращает короткий идентификатор и оригинальную ссылку.
    """
    short_id: str = Field(
        description='Короткий идентификатор ссылки',
        examples=['abc123', 'xK7mNp'],
        min_length=4,
        max_length=20,
    )
    original_url: str = Field(
        description='Оригинальная ссылка',
        examples=['https://example.com/very/long/url']
    )

    class Config:
        from_attributes = True


class LinkStatsResponse(BaseModel):
    """
    Схема ответа со статистикой переходов.
    """
    short_id: str = Field(
        description='Короткий идентификатор ссылки',
        examples=['abc123']
    )
    clicks: int = Field(
        description='Количество переходов по ссылке',
        examples=[42, 1000],
        ge=0,
    )
    original_url: Optional[str] = Field(
        description='Оригинальная ссылка (опционально)',
        default=None,
        examples=['https://example.com/url']
    )


    class Config:
        from_attributes = True
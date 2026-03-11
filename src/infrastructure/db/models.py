from sqlalchemy import String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "links"

    short_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    last_accessed: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

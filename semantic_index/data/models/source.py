from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .embedding import Embedding


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uri: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    last_modified: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_processed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding", back_populates="source", cascade="all, delete-orphan"
    )

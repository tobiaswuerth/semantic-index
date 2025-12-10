from typing import TYPE_CHECKING
import numpy as np
from sqlalchemy import ForeignKey, Integer, LargeBinary, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from ..database import Base

if TYPE_CHECKING:
    from .source import Source


class NumpyArray(TypeDecorator):
    impl = LargeBinary
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.astype(np.float16).tobytes()
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return np.frombuffer(value, dtype=np.float16)
        return None


class Embedding(Base):
    __tablename__ = "embeddings"
    __table_args__ = (Index("idx_embeddings_source_id", "source_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id"), nullable=False
    )
    embedding: Mapped[np.ndarray] = mapped_column(NumpyArray, nullable=False)
    chunk_idx: Mapped[int] = mapped_column(Integer, nullable=False)

    source: Mapped["Source"] = relationship("Source", back_populates="embeddings")

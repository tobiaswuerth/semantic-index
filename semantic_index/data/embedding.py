from typing import Sequence, TYPE_CHECKING, cast
import numpy as np
from sqlalchemy import (
    CursorResult,
    ForeignKey,
    Integer,
    LargeBinary,
    Index,
    delete,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from .database import Base, get_session, SessionFactory
from ..api import SearchDateFilter

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
    source: Mapped["Source"] = relationship("Source", back_populates="embeddings")
    embedding: Mapped[np.ndarray] = mapped_column(NumpyArray, nullable=False)
    chunk_idx: Mapped[int] = mapped_column(Integer, nullable=False)


class EmbeddingRepository:
    def __init__(self, session_factory: SessionFactory = get_session):
        self._session_factory = session_factory

    def get_all(self) -> Sequence[Embedding]:
        with self._session_factory() as session:
            stmt = select(Embedding)
            result = session.execute(stmt).scalars().all()
            session.expunge_all()
        return result

    def get_by_id(self, embedding_id: int) -> Embedding | None:
        with self._session_factory() as session:
            stmt = select(Embedding).where(Embedding.id == embedding_id)
            result = session.execute(stmt).scalar_one_or_none()
            session.expunge_all()
        return result

    def create_many(self, embeddings: Sequence[Embedding]) -> None:
        with self._session_factory() as session:
            session.add_all(embeddings)

    def delete_by_source_id(self, source_id: int) -> int:
        with self._session_factory() as session:
            stmt = delete(Embedding).where(Embedding.source_id == source_id)
            result = cast(CursorResult, session.execute(stmt))
        return result.rowcount if result.rowcount else 0

    def get_all_with_date_and_type(
        self,
        filter: SearchDateFilter,
        tag_ids: list[int] | None,
    ) -> Sequence[Embedding]:
        from .source import Source  # Avoid circular import
        from .source_tag import SourceTag  # Avoid circular import

        with self._session_factory() as session:
            stmt = select(Embedding)

            if (
                filter.createdate_start
                or filter.createdate_end
                or filter.modifieddate_start
                or filter.modifieddate_end
                or tag_ids is not None
            ):
                stmt = stmt.join(Source, Embedding.source_id == Source.id)

            if tag_ids is not None:
                stmt = stmt.join(SourceTag, Source.id == SourceTag.c.source_id)
                stmt = stmt.where(SourceTag.c.tag_id.in_(tag_ids))

            if filter.createdate_start:
                stmt = stmt.where(Source.obj_created >= filter.createdate_start)
            if filter.createdate_end:
                stmt = stmt.where(Source.obj_created <= filter.createdate_end)
            if filter.modifieddate_start:
                stmt = stmt.where(Source.obj_modified >= filter.modifieddate_start)
            if filter.modifieddate_end:
                stmt = stmt.where(Source.obj_modified <= filter.modifieddate_end)

            embeddings = session.execute(stmt).scalars().all()
            session.expunge_all()
            return embeddings

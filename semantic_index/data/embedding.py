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

    def get_all(self) -> list[Embedding]:
        with self._session_factory() as session:
            embeddings = list(session.execute(select(Embedding)).scalars().all())
            for emb in embeddings:
                session.expunge(emb)
            return embeddings

    def get_by_id(self, embedding_id: int) -> Embedding | None:
        with self._session_factory() as session:
            embedding = session.get(Embedding, embedding_id)
            if embedding:
                session.expunge(embedding)
            return embedding

    def create_many(self, embeddings: Sequence[Embedding]) -> None:
        with self._session_factory() as session:
            session.add_all(embeddings)

    def delete_by_source_id(self, source_id: int) -> int:
        with self._session_factory() as session:
            result = cast(
                CursorResult,
                session.execute(
                    delete(Embedding).where(Embedding.source_id == source_id)
                ),
            )
            return result.rowcount if result.rowcount else 0

    def get_all_with_date_and_type(
        self,
        filter: SearchDateFilter,
        source_type_ids: list[int],
    ) -> list[Embedding]:
        from .source import Source  # Avoid circular import
        from .source_type import SourceType  # Avoid circular import

        with self._session_factory() as session:
            query = (
                select(Embedding)
                .join(Embedding.source)
                .join(Source.source_type)
                .where(SourceType.id.in_(source_type_ids))
            )
            if filter.createdate_start:
                query = query.where(Source.obj_created >= filter.createdate_start)
            if filter.createdate_end:
                query = query.where(Source.obj_created <= filter.createdate_end)
            if filter.modifieddate_start:
                query = query.where(Source.obj_modified >= filter.modifieddate_start)
            if filter.modifieddate_end:
                query = query.where(Source.obj_modified <= filter.modifieddate_end)

            embeddings = list(session.execute(query).scalars().all())
            for emb in embeddings:
                session.expunge(emb)
            return embeddings

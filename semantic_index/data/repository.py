import logging
from contextlib import AbstractContextManager
from typing import Callable, Iterator, Sequence
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .database import get_session
from .models import Embedding, Source

logger = logging.getLogger(__name__)
SessionFactory = Callable[[], AbstractContextManager[Session]]


class SourceRepository:
    def __init__(self, session_factory: SessionFactory = get_session):
        self._session_factory = session_factory

    def get_all(self, *, order_by_modified: bool = True) -> list[Source]:
        with self._session_factory() as session:
            stmt = select(Source)
            if order_by_modified:
                stmt = stmt.order_by(Source.last_modified.desc())
            sources = list(session.execute(stmt).scalars().all())
            for source in sources:
                session.expunge(source)
            return sources

    def get_by_id(self, source_id: int) -> Source | None:
        with self._session_factory() as session:
            source = session.get(Source, source_id)
            if source:
                session.expunge(source)
            return source

    def upsert_many(self, sources: Iterator[Source], *, batch_size: int = 1000) -> int:
        count = 0
        with self._session_factory() as session:
            for count, source in enumerate(sources, start=1):
                existing = session.execute(
                    select(Source).where(Source.uri == source.uri)
                ).scalar_one_or_none()
                if existing:
                    existing.last_modified = source.last_modified
                else:
                    session.add(source)
                if count % batch_size == 0:
                    session.flush()
        return count

    def update(self, source: Source) -> None:
        with self._session_factory() as session:
            db_source = session.get(Source, source.id)
            if db_source:
                db_source.last_processed = source.last_processed
                db_source.error = source.error
                db_source.error_message = source.error_message


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
            result = session.execute(
                delete(Embedding).where(Embedding.source_id == source_id)
            )
            return result.rowcount or 0

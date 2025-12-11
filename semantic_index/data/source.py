import logging
from datetime import datetime
from typing import Iterator, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload

from .database import Base, get_session, SessionFactory

if TYPE_CHECKING:
    from .embedding import Embedding
    from .source_handler import SourceHandler
    from .source_type import SourceType

logger = logging.getLogger(__name__)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source_handler_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("source_handlers.id"), nullable=False
    )
    source_handler: Mapped["SourceHandler"] = relationship(
        "SourceHandler", back_populates="sources"
    )

    source_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("source_types.id"), nullable=False
    )
    source_type: Mapped["SourceType"] = relationship(
        "SourceType", back_populates="sources"
    )

    uri: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    resolved_to: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    obj_created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    obj_modified: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_processed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding", back_populates="source", cascade="all, delete-orphan"
    )


class SourceRepository:
    def __init__(self, session_factory: SessionFactory = get_session):
        self._session_factory = session_factory

    def get_all(self, order_by_modified: bool = True) -> list[Source]:
        with self._session_factory() as session:
            stmt = select(Source)
            if order_by_modified:
                stmt = stmt.order_by(Source.obj_modified.desc())
            sources = list(session.execute(stmt).scalars().all())
            for source in sources:
                session.expunge(source)
            return sources

    def get_by_id(self, source_id: int) -> Source | None:
        with self._session_factory() as session:
            stmt = (
                select(Source)
                .options(
                    joinedload(Source.source_handler),
                    joinedload(Source.source_type),
                )
                .where(Source.id == source_id)
            )
            source = session.execute(stmt).scalars().first()
            if source:
                session.expunge(source.source_handler)
                session.expunge(source.source_type)
                session.expunge(source)
            return source

    def upsert_many(self, sources: Iterator[Source]) -> tuple[int, int]:
        updated, inserted = 0, 0
        with self._session_factory() as session:
            try:
                for count, source in enumerate(sources, start=1):
                    existing = session.execute(
                        select(Source).where(Source.uri == source.uri)
                    ).scalar_one_or_none()
                    if existing:
                        existing.obj_created = source.obj_created
                        existing.obj_modified = source.obj_modified
                        existing.last_checked = datetime.now()
                        existing.title = source.title
                        updated += 1
                    else:
                        session.add(source)
                        inserted += 1
                    if count % 1000 == 0:
                        session.flush()
                        session.commit()
                        logger.debug(f"Upserted {count} sources...")
            except KeyboardInterrupt:
                logger.warning("Upsert operation interrupted by user.")
        return updated, inserted

    def update(self, source: Source) -> None:
        with self._session_factory() as session:
            db_source = session.get(Source, source.id)
            if db_source:
                db_source.last_checked = source.last_checked
                db_source.last_processed = source.last_processed
                db_source.error = source.error
                db_source.error_message = source.error_message

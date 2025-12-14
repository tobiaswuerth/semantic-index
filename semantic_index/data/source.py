import logging
from datetime import datetime, timedelta
from typing import Iterator, Optional, TYPE_CHECKING, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload, MANYTOMANY
from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    ForeignKey,
    select,
    func,
    extract,
)

from ..api import HistogramResponse
from .database import Base, get_session, SessionFactory
from .source_tag import SourceTag

if TYPE_CHECKING:
    from .source_handler import SourceHandler
    from .source_tag import SourceTag
    from .tag import Tag
    from .embedding import Embedding


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
    uri: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    resolved_to: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=SourceTag, back_populates="sources"
    )

    obj_created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    obj_modified: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_processed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding", back_populates="source"
    )


class SourceRepository:
    def __init__(self, session_factory: SessionFactory = get_session):
        self._session_factory = session_factory

    def get_all(self) -> Sequence[Source]:
        with self._session_factory() as session:
            stmt = select(Source).order_by(Source.obj_modified.desc())
            result = session.execute(stmt).scalars().all()
            session.expunge_all()
        return result

    def get_by_id(self, source_id: int) -> Source | None:
        with self._session_factory() as session:
            stmt = (
                select(Source)
                .options(
                    joinedload(Source.tags),
                )
                .where(Source.id == source_id)
            )
            result = session.execute(stmt).unique().scalar_one_or_none()
            session.expunge_all()
        return result

    def get_by_embedding_id(self, embedding_id: int) -> Source | None:
        with self._session_factory() as session:
            from .embedding import Embedding  # Avoid circular import

            stmt = (
                select(Source)
                .join(Embedding, Embedding.source_id == Source.id)
                .where(Embedding.id == embedding_id)
            )
            result = session.execute(stmt).scalar_one_or_none()
            session.expunge_all()
        return result

    def upsert_many(self, sources: Sequence[Source]) -> tuple[int, int]:
        updated, inserted = 0, 0
        with self._session_factory() as session:
            for source in sources:
                stmt = select(Source).where(Source.uri == source.uri)
                existing = session.execute(stmt).scalar_one_or_none()
                if not existing:
                    source.tags = [session.merge(tag) for tag in source.tags]
                    session.add(source)
                    inserted += 1
                    continue

                existing.obj_created = source.obj_created
                existing.obj_modified = source.obj_modified
                existing.last_checked = datetime.now()
                existing.title = source.title
                updated += 1
        return updated, inserted

    def update(self, source: Source) -> None:
        with self._session_factory() as session:
            stmt = select(Source).where(Source.id == source.id)
            db_source = session.execute(stmt).scalar_one_or_none()
            if not db_source:
                return None

            db_source.last_checked = source.last_checked
            db_source.last_processed = source.last_processed
            db_source.error = source.error
            db_source.error_message = source.error_message

    def get_createdate_histogram(self) -> list[HistogramResponse]:
        return self._get_date_histogram(Source.obj_created)

    def get_modifydate_histogram(self) -> list[HistogramResponse]:
        return self._get_date_histogram(Source.obj_modified)

    def _get_date_histogram(self, field: Mapped[datetime]) -> list[HistogramResponse]:
        from .embedding import Embedding  # avoid circular import

        with self._session_factory() as session:
            # get global min date
            min_date_row = session.execute(select(func.min(field))).first()
            if not min_date_row or len(min_date_row) == 0 or min_date_row[0] is None:
                return []
            min_date = min_date_row[0]

            # count distinct processed sources per year-month
            year_col = extract("year", field).label("year")
            month_col = extract("month", field).label("month")
            stmt = (
                select(year_col, month_col, func.count(func.distinct(Source.id)))
                .select_from(Source)
                .join(Embedding, Embedding.source_id == Source.id)
                .group_by(year_col, month_col)
                .order_by(year_col.asc(), month_col.asc())
            )
            results = session.execute(stmt).all()

        # reconstruct into full histogram with filled gaps
        db_counts = {
            f"{int(year)}-{int(month):02d}": count  # YYYY-MM
            for year, month, count in results
        }
        hist = {}
        todate = datetime.now()
        current_date = min_date.replace(day=1)
        while current_date <= todate:
            key = current_date.strftime("%Y-%m")  # YYYY-MM
            hist[key] = db_counts.get(key, 0)
            current_date += timedelta(days=25)  # go to next month

        # Sort and return
        hist_items = sorted(hist.items(), key=lambda x: x[0])
        return [HistogramResponse(bucket=key, count=count) for key, count in hist_items]
